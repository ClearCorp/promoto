/** @odoo-module **/

import paymentButton from '@payment/js/payment_button';

paymentButton.include({

    /**
     * Habilita el botón de pago de BNCR.
     * @override
     */
    _setEnabled() {
        const isBncr = this.paymentButton.dataset.isBncr === 'true';
        
        if (!isBncr) {
            this._super();
            return;
        }

        const disabledButton = document.getElementById('o_bncr_disabled_button');
        const enabledButton = document.getElementById('o_bncr_enabled_button');
        
        if (disabledButton) disabledButton.classList.add('d-none');
        if (enabledButton) enabledButton.classList.remove('d-none');
    },

    /**
     * Deshabilita el botón de pago de BNCR.
     * @override
     */
    _disable() {
        const isBncr = this.paymentButton.dataset.isBncr === 'true';
        
        if (!isBncr) {
            this._super();
            return;
        }

        const disabledButton = document.getElementById('o_bncr_disabled_button');
        const enabledButton = document.getElementById('o_bncr_enabled_button');
        
        if (enabledButton) enabledButton.classList.add('d-none');
        if (disabledButton) disabledButton.classList.remove('d-none');
    },

    /**
     * Previene que la lógica genérica oculte el contenedor del botón de BNCR.
     * @override
     */
    _hide() {
        const isBncr = this.paymentButton.dataset.isBncr === 'true';
        
        if (!isBncr) {
            this._super();
        }
        // Para BNCR, no ocultamos el botón ya que manejamos la visibilidad internamente
    },

    /**
     * Previene que la lógica genérica muestre el contenedor del botón de BNCR.
     * @override
     */
    _show() {
        const isBncr = this.paymentButton.dataset.isBncr === 'true';
        
        if (!isBncr) {
            this._super();
        }
        // Para BNCR, no mostramos el botón ya que manejamos la visibilidad internamente
    },
});