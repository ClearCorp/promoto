/** @odoo-module **/

import paymentButton from '@payment/js/payment_button';

paymentButton.include({

    /**
     * Habilita el botón de pago de BNCR.
     * @override
     */
    _setEnabled() {
        if (!this.paymentButton.dataset.isBncr) {
            this._super();
            return;
        }
        this.paymentButton.querySelector('#o_bncr_pay_button').removeAttribute('disabled');
    },

    /**
     * Deshabilita el botón de pago de BNCR.
     * @override
     */
    _disable() {
        if (!this.paymentButton.dataset.isBncr) {
            this._super();
            return;
        }
        this.paymentButton.querySelector('#o_bncr_pay_button').setAttribute('disabled', 'disabled');
    },

    /**
     * Previene que la lógica genérica oculte el contenedor del botón de BNCR.
     * @override
     */
    _hide() {
        if (!this.paymentButton.dataset.isBncr) {
            this._super();
        }
    },

    /**
     * Previene que la lógica genérica muestre el contenedor del botón de BNCR.
     * @override
     */
    _show() {
        if (!this.paymentButton.dataset.isBncr) {
            this._super();
        }
    },
});