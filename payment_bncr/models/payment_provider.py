# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import json
import hmac
import hashlib


import requests
from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.payment_bncr import const


_logger = logging.getLogger(__name__)


class Paymentprovider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('bncr', "BNCR Payment Gateway")], ondelete={'bncr': 'set default'}
    )
    bncr_acquirer_id = fields.Char(
        string="Id del adquiriente", 
        required_if_provider='bncr',
        help="Acquirer ID proporcionado por BNCR")

    bncr_commerce_id = fields.Char(
        string="Id del Comercio", 
        required_if_provider='bncr',
        help="Commerce ID proporcionado por BNCR")
    
    bncr_secret_key = fields.Char(
        string="Clave Secreta SHA-2",
        required_if_provider='bncr',
        help="Clave secreta SHA-2 proporcionada por BNCR")
    
    bncr_gateway_url = fields.Char(
        string="Gateway URL",
        required_if_provider='bncr',
        default="https://integracion.alignetsac.com/",
        help="URL base del gateway BNCR")

    bncr_modal_script_url = fields.Char(
        string="Modal Script URL",
        default="https://integracion.alignetsac.com/VPOS2/js/modalcomercio.js",
        help="URL del script JavaScript del modal de BNCR")

    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'bncr').update({
            'support_refund': 'partial',
            'support_tokenization': False,  # BNCR doesn't support tokenization
            'support_manual_capture': False,  # BNCR processes immediately
        })    
    
    def _bncr_calculate_signature(self, acquirer_id, commerce_id, operation_number, amount, currency_code):
        """ Compute the SHA-512 signature for BNCR according to their documentation.
        
        :param str acquirer_id: ID del adquiriente
        :param str commerce_id: ID del comercio
        :param str operation_number: Número de operación de compra
        :param str amount: Monto en centavos
        :param str currency_code: Código de moneda
        :return: The calculated signature.
        :rtype: str
        """
        self.ensure_one()
        
        # Concatenar valores según documentación BNCR
        signature_string = (
            str(acquirer_id) + 
            str(commerce_id) + 
            str(operation_number) + 
            str(amount) + 
            str(currency_code) + 
            str(self.bncr_secret_key)
        )
        
        # Generar hash SHA-512
        signature = hashlib.sha512(signature_string.encode('utf-8')).hexdigest()
        
        _logger.info("BNCR: Signature string: %s", signature_string)
        _logger.info("BNCR: Generated signature: %s", signature)
        
        return signature

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'bncr':
            return default_codes
        return const.DEFAULT_PAYMENT_METHOD_CODES

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """ Override to filter BNCR providers based on currency support. """
        providers = super()._get_compatible_providers(*args, currency_id=currency_id, **kwargs)
        
        # BNCR típicamente soporta USD (840) y puede soportar otras monedas
        # Filtrar según las monedas soportadas por tu configuración
        if currency_id:
            currency = self.env['res.currency'].browse(currency_id)
            bncr_providers = providers.filtered(lambda p: p.code == 'bncr')
            
            # Definir monedas soportadas (ajustar según tu configuración)
            supported_currencies = ['USD', 'CRC', 'EUR']  # Ejemplo
            
            if currency.name not in supported_currencies:
                providers = providers - bncr_providers
                
        return providers