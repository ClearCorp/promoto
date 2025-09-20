# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import hashlib


from werkzeug import urls

from odoo import _, models, fields
from odoo.exceptions import ValidationError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_bncr.const import TRANSACTION_STATUS_MAPPING
from odoo.addons.payment_bncr.controllers.main import BNCRController


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # Campos específicos de BNCR
    bncr_acquirer_id = fields.Char(_('BNCR Id del adquirente'))
    bncr_commerce_id = fields.Char(_('BNCR Id del comercio'))
    bncr_purchase_operation_number = fields.Char(_('BNCR Número de operación'))
    bncr_purchase_amount = fields.Char(_('BNCR Monto'))
    bncr_purchase_currency_code = fields.Char(_('BNCR Código de moneda'))
    bncr_purchase_verification = fields.Char(_('BNCR Verificación'))
    bncr_language = fields.Char(_('BNCR Idioma'), default='SP')
    bncr_programming_language = fields.Char(_('BNCR Lenguaje programación'), default='PHP')
    
    # Campos de envío (shipping)
    bncr_shipping_first_name = fields.Char(_('BNCR Nombre'))
    bncr_shipping_last_name = fields.Char(_('BNCR Apellido'))
    bncr_shipping_email = fields.Char(_('BNCR Email'))
    bncr_shipping_address = fields.Char(_('BNCR Dirección'))
    bncr_shipping_zip = fields.Char(_('BNCR Código postal'))
    bncr_shipping_city = fields.Char(_('BNCR Ciudad'))
    bncr_shipping_state = fields.Char(_('BNCR Estado/Provincia'))
    bncr_shipping_country = fields.Char(_('BNCR País'))
    
    # Campos reservados
    bncr_reserved1 = fields.Char(_('BNCR Campo reservado 1'))
    bncr_reserved2 = fields.Char(_('BNCR Campo reservado 2'))
    bncr_reserved3 = fields.Char(_('BNCR Campo reservado 3'))

    def _get_specific_rendering_values(self, processing_values):
        """ Override of `payment` to return BNCR-specific rendering values.

        Note: self.ensure_one() from `_get_rendering_values`.

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values.
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'bncr':
            return res

        # Determinar código de moneda según BNCR
        currency_code_mapping = {
            'USD': '840',
            'CRC': '188',
            'EUR': '978',
            # Agregar más monedas según necesidad
        }
        currency_code = currency_code_mapping.get(self.currency_id.name, '840')
        
        # Convertir monto a centavos (entero)
        amount_cents = int(self.amount * 100)
        
        # Preparar datos de pago para BNCR
        payment_data = {
            'acquirerId': self.provider_id.bncr_acquirer_id,
            'idCommerce': self.provider_id.bncr_commerce_id,
            'purchaseOperationNumber': self.reference,
            'purchaseAmount': str(amount_cents),
            'purchaseCurrencyCode': currency_code,
            'language': 'SP',  # Español por defecto
            'programmingLanguage': 'PHP',
            
            # Datos del cliente/envío
            'shippingFirstName': self.partner_id.name.split(' ')[0] if self.partner_id.name else 'Cliente',
            'shippingLastName': ' '.join(self.partner_id.name.split(' ')[1:]) if self.partner_id.name and len(self.partner_id.name.split(' ')) > 1 else 'Usuario',
            'shippingEmail': self.partner_id.email or 'cliente@ejemplo.com',
            'shippingAddress': self.partner_id.street or 'Dirección no especificada',
            'shippingZIP': self.partner_id.zip or '00000',
            'shippingCity': self.partner_id.city or 'Ciudad',
            'shippingState': self.partner_id.state_id.name if self.partner_id.state_id else 'Estado',
            'shippingCountry': self.partner_id.country_id.code if self.partner_id.country_id else 'CR',
            
            # Campos reservados
            'reserved1': f"odoo_tx_{self.id}",
            'reserved2': self.partner_id.email or '',
            'reserved3': f"order_{self.reference}",
        }
        
        # Generar verificación/firma según documentación BNCR
        payment_data['purchaseVerification'] = self.provider_id._bncr_calculate_signature(
            payment_data['acquirerId'],
            payment_data['idCommerce'],
            payment_data['purchaseOperationNumber'],
            payment_data['purchaseAmount'],
            payment_data['purchaseCurrencyCode']
        )
        
        # Guardar algunos valores en la transacción para referencia
        self.bncr_acquirer_id = payment_data['acquirerId']
        self.bncr_commerce_id = payment_data['idCommerce']
        self.bncr_purchase_operation_number = payment_data['purchaseOperationNumber']
        self.bncr_purchase_amount = payment_data['purchaseAmount']
        self.bncr_purchase_currency_code = payment_data['purchaseCurrencyCode']
        self.bncr_purchase_verification = payment_data['purchaseVerification']
        self.bncr_reserved1 = payment_data['reserved1']
        
        rendering_values = {
            'api_url': self.provider_id.bncr_gateway_url,
            'modal_script_url': self.provider_id.bncr_modal_script_url,
            'payment_data': payment_data,
        }
        
        _logger.info("BNCR: Rendering values: %s", pprint.pformat(rendering_values))
        
        return rendering_values

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of `payment` to find the transaction based on BNCR data.

        :param str provider_code: The code of the provider that handled the transaction.
        :param dict notification_data: The notification data sent by the provider.
        :return: The transaction if found.
        :rtype: recordset of `payment.transaction`
        :raise ValidationError: If inconsistent data were received.
        :raise ValidationError: If the data match no transaction.
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'bncr' or len(tx) == 1:
            return tx

        # BNCR puede enviar el número de operación o referencia
        reference = notification_data.get('purchaseOperationNumber') or notification_data.get('reference')
        if not reference:
            raise ValidationError("BNCR: " + _("Received data with missing reference."))

        tx = self.search([
            ('reference', '=', reference), 
            ('provider_code', '=', 'bncr')
        ])
        
        if not tx:
            # Intentar buscar por bncr_purchase_operation_number si no se encuentra por reference
            tx = self.search([
                ('bncr_purchase_operation_number', '=', reference),
                ('provider_code', '=', 'bncr')
            ])
            
        if not tx:
            raise ValidationError(
                "BNCR: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of `payment` to process the transaction based on BNCR data.

        Note: self.ensure_one() from `_process_notification_data`

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data were received.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'bncr':
            return

        # Validar la respuesta de BNCR
        transaction_id = notification_data.get('transactionId')
        response_code = notification_data.get('responseCode')
        auth_code = notification_data.get('authorizationCode')
        
        # Actualizar campos de la transacción
        self.provider_reference = transaction_id
        
        # Guardar datos adicionales de BNCR
        for field_map in [
            ('purchaseOperationNumber', 'bncr_purchase_operation_number'),
            ('purchaseAmount', 'bncr_purchase_amount'),
            ('purchaseCurrencyCode', 'bncr_purchase_currency_code'),
            ('reserved1', 'bncr_reserved1'),
            ('reserved2', 'bncr_reserved2'),
            ('reserved3', 'bncr_reserved3'),
        ]:
            bncr_field, odoo_field = field_map
            if bncr_field in notification_data:
                setattr(self, odoo_field, notification_data[bncr_field])

        # Procesar estado de la transacción según códigos de respuesta de BNCR
        message = f"BNCR Transaction ID: {transaction_id}, Response Code: {response_code}"
        if auth_code:
            message += f", Authorization Code: {auth_code}"

        # Mapear códigos de respuesta de BNCR (ajustar según documentación)
        if response_code == '00':  # Aprobada
            self._set_done(state_message=message)
        elif response_code in ['01', '02', '03']:  # Pendiente/En proceso
            self._set_pending(state_message=message)
        elif response_code in ['05', '14', '54']:  # Rechazada
            self._set_canceled(state_message=message)
        else:  # Error o código no reconocido
            _logger.warning(
                "BNCR: Received data for transaction with reference %s with unknown response code: %s",
                self.reference, response_code
            )
            self._set_error(
                "BNCR: " + _("Received data with unknown response code: %s", response_code)
            )

    def _send_refund_request(self, amount_to_refund=None):
        """ Override to handle BNCR refunds if supported.
        
        Note: BNCR might not support programmatic refunds, 
        this would need to be implemented according to their API.
        """
        self.ensure_one()
        
        if self.provider_code != 'bncr':
            return super()._send_refund_request(amount_to_refund=amount_to_refund)
        
        # BNCR refund implementation would go here
        # For now, create a manual refund transaction
        refund_tx = super()._send_refund_request(amount_to_refund=amount_to_refund)
        
        # Mark as manual refund since BNCR might not support API refunds
        refund_tx.write({
            'state_message': _("Manual refund required through BNCR portal")
        })
        
        return refund_tx