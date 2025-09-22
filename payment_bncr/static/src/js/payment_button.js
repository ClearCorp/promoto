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
        document.getElementById('o_bncr_disabled_button').classList.add('d-none');
        document.getElementById('o_bncr_enabled_button').classList.remove('d-none');
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
        document.getElementById('o_bncr_disabled_button').classList.remove('d-none');
        document.getElementById('o_bncr_enabled_button').classList.add('d-none');
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