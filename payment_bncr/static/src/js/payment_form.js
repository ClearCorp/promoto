/* global AlignetVPOS2 */

import { loadJS } from '@web/core/assets';
import paymentForm from '@payment/js/payment_form';

paymentForm.include({
    bncrData: undefined,

    // #=== MANIPULACIÓN DEL DOM ===#

    /**
     * Oculta el contenedor del botón de BNCR si se expande otro proveedor.
     * @override
     */
    async _expandInlineForm(radio) {
        const providerCode = this._getProviderCode(radio);
        if (providerCode !== 'bncr') {
            document.getElementById('o_bncr_button_container')?.classList.add('d-none');
        }
        this._super(...arguments);
    },

    /**
     * Prepara el formulario inline para BNCR.
     * Carga el script del modal de BNCR y prepara el botón de pago.
     * @override
     */
    async _prepareInlineForm(providerId, providerCode, paymentOptionId) {
        if (providerCode !== 'bncr') {
            this._super(...arguments);
            return;
        }

        this._hideInputs();
        this._setPaymentFlow('direct');
        document.getElementById('o_bncr_loading').classList.remove('d-none');

        this.bncrData ??= {};
        this.bncrData[paymentOptionId] ??= {};

        // Carga el SDK de BNCR solo una vez.
        if (!this.bncrData[paymentOptionId].isSdkLoaded) {
            const radio = document.querySelector(`input[name="o_payment_radio"][data-payment-option-id="${paymentOptionId}"]`);
            const inlineFormValues = JSON.parse(radio.dataset['bncrInlineFormValues']);
            
            this.bncrData[paymentOptionId].inlineFormValues = inlineFormValues;

            // La URL del script se obtiene desde la configuración del proveedor en Odoo.
            await loadJS(inlineFormValues.modal_script_url);
            this.bncrData[paymentOptionId].isSdkLoaded = true;

            const payButton = document.getElementById('o_bncr_pay_button');
            payButton.addEventListener('click', this._bncrOnClick.bind(this));
        }

        document.getElementById('o_bncr_loading').classList.add('d-none');
        document.getElementById('o_bncr_button_container').classList.remove('d-none');
    },

    // #=== FLUJO DE PAGO ===#

    /**
     * Inicia el flujo de pago al hacer clic en el botón.
     * Llama al backend de Odoo para crear la transacción y obtener los datos firmados.
     * @private
     */
    async _bncrOnClick() {
        this._disableButton();
        // Llama a _submitForm, lo que activará _get_specific_rendering_values en el backend
        // y el resultado se pasará a _processDirectFlow.
        await this._submitForm(new Event("BncrClickEvent"));
    },

    /**
     * Procesa los datos recibidos del backend, construye el formulario para BNCR y abre el modal.
     * @override
     */
    _processDirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode !== 'bncr') {
            this._super(...arguments);
            return;
        }

        const { gateway_url } = this.bncrData[paymentOptionId].inlineFormValues;
        const paymentData = processingValues.payment_data;

        // Elimina cualquier formulario antiguo para evitar conflictos.
        const oldForm = document.getElementById('f1_bncr');
        if (oldForm) {
            oldForm.remove();
        }

        // Crea dinámicamente el formulario que Alignet/BNCR VPOS2 necesita.
        const form = document.createElement('form');
        form.setAttribute('name', 'f1');
        form.setAttribute('id', 'f1_bncr'); // Usamos un ID único
        form.setAttribute('method', 'post');
        
        // El backend ya nos dio un diccionario 'payment_data' con todos los campos necesarios.
        for (const [key, value] of Object.entries(paymentData)) {
            const input = document.createElement('input');
            input.setAttribute('type', 'hidden');
            input.setAttribute('name', key);
            input.setAttribute('value', value);
            form.appendChild(input);
        }
        document.body.appendChild(form);
        
        // Abre el modal de BNCR. El script cargado (AlignetVPOS2) se encarga del resto.
        // Nota: Asumimos que el script de BNCR expone el objeto global AlignetVPOS2.
        AlignetVPOS2.openModal(gateway_url);
    },
});