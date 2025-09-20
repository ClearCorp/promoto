# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import werkzeug

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import portal as payment_portal


_logger = logging.getLogger(__name__)


class BNCRController(http.Controller):
    _return_url = '/payment/bncr/return'
    _webhook_url = '/payment/bncr/webhook'
    _cancel_url = '/payment/bncr/cancel'

    @http.route(_return_url, type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def bncr_return_from_checkout(self, **data):
        """ Process the notification data sent by BNCR after redirection from checkout.

        :param dict data: The notification data (form data or query parameters)
        """
        _logger.info("BNCR: Handling return from checkout with data:\n%s", pprint.pformat(data))
        
        # Verificar que tengamos los datos mínimos necesarios
        if not data:
            _logger.warning("BNCR: Return from checkout without data")
            return request.render('payment.payment_process_error', {
                'error': 'No se recibieron datos del procesador de pagos'
            })

        try:
            # Buscar la transacción
            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                'bncr', data
            )
            
            # Procesar la notificación
            tx_sudo._process_notification_data(data)
            tx_sudo._execute_callback()

            # Redirigir al usuario según el estado
            return self._redirect_to_status_page(tx_sudo)

        except ValidationError as e:
            _logger.exception("BNCR: Error processing return data")
            return request.render('payment.payment_process_error', {
                'error': str(e)
            })

    @http.route(_webhook_url, type='http', auth='public', methods=['POST'], csrf=False)
    def bncr_webhook(self, **data):
        """ Process a webhook notification from BNCR.

        :param dict data: The webhook notification data
        """
        _logger.info("BNCR: Handling webhook with data:\n%s", pprint.pformat(data))
        
        try:
            # Buscar y procesar la transacción
            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                'bncr', data
            )
            tx_sudo._process_notification_data(data)
            tx_sudo._execute_callback()
            
            # BNCR puede esperar una respuesta específica
            return 'OK'

        except ValidationError as e:
            _logger.exception("BNCR: Error processing webhook data")
            return werkzeug.exceptions.BadRequest(str(e))

    @http.route(_cancel_url, type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def bncr_cancel_from_checkout(self, **data):
        """ Handle cancellation from BNCR checkout.

        :param dict data: The cancellation data
        """
        _logger.info("BNCR: Handling cancellation with data:\n%s", pprint.pformat(data))
        
        try:
            if data:
                tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                    'bncr', data
                )
                tx_sudo._set_canceled("Pago cancelado por el usuario")
                tx_sudo._execute_callback()
                
                return self._redirect_to_status_page(tx_sudo)
            else:
                # Cancelación sin datos específicos
                return request.redirect('/payment/status')

        except ValidationError as e:
            _logger.exception("BNCR: Error processing cancellation")
            return request.render('payment.payment_process_error', {
                'error': 'Error procesando la cancelación'
            })

    def _redirect_to_status_page(self, tx_sudo):
        """ Redirect to the appropriate status page based on transaction state.
        
        :param tx_sudo: The payment transaction
        :return: Redirect response
        """
        if tx_sudo.state == 'done':
            return request.redirect('/payment/status')
        elif tx_sudo.state in ['pending', 'authorized']:
            return request.redirect('/payment/status')
        else:
            return request.redirect('/payment/status')

    @http.route('/payment/bncr/simulate_return', type='http', auth='user', methods=['GET', 'POST'])
    def bncr_simulate_return(self, **data):
        """ Simulate a return from BNCR for testing purposes (only in debug mode). """
        if not request.env.user.has_group('base.group_system'):
            return request.not_found()
            
        # Datos de prueba para simular respuesta de BNCR
        test_data = {
            'acquirerId': '99',
            'idCommerce': '8056',
            'purchaseOperationNumber': data.get('ref', 'TEST123'),
            'purchaseAmount': data.get('amount', '10000'),
            'purchaseCurrencyCode': '840',
            'responseCode': data.get('response_code', '00'),
            'authorizationCode': data.get('auth_code', 'AUTH123'),
            'transactionId': data.get('transaction_id', 'TXN123456'),
            'reserved1': data.get('reserved1', ''),
        }
        
        return self.bncr_return_from_checkout(**test_data)


class PaymentPortal(payment_portal.PaymentPortal):
    """ Extend the payment portal to handle BNCR specific cases. """

    @http.route()
    def payment_pay(self, *args, reference=None, amount=None, currency_id=None,
                   partner_id=None, access_token=None, **kwargs):
        """ Override to add BNCR specific handling if needed. """
        
        # Llamar al método padre
        response = super().payment_pay(
            *args, reference=reference, amount=amount, currency_id=currency_id,
            partner_id=partner_id, access_token=access_token, **kwargs
        )
        
        # Agregar lógica específica para BNCR si es necesario
        if hasattr(response, 'qcontext'):
            qcontext = response.qcontext
            if qcontext and 'providers_sudo' in qcontext:
                # Filtrar proveedores BNCR según criterios específicos
                providers = qcontext['providers_sudo']
                bncr_providers = providers.filtered(lambda p: p.code == 'bncr')
                
                for provider in bncr_providers:
                    # Verificar configuración específica
                    if not all([provider.bncr_acquirer_id, provider.bncr_commerce_id, 
                              provider.bncr_secret_key]):
                        _logger.warning("BNCR provider %s has incomplete configuration", provider.name)
        
        return response