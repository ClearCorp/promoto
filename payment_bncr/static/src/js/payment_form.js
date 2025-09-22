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
            const bncrContainer = document.getElementById('o_bncr_button_container');
            if (bncrContainer) {
                bncrContainer.classList.add('d-none');
            }
            // Mostrar botón original de Odoo
            const originalButton = document.getElementById('o_payment_submit_button');
            if (originalButton) {
                originalButton.style.display = 'block';
                originalButton.setAttribute('data-is-bncr', 'false');
            }
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
        
        // Mostrar loading
        const loadingElement = document.getElementById('o_bncr_loading');
        if (loadingElement) {
            loadingElement.classList.remove('d-none');
        }

        // Ocultar botón original de Odoo y mostrar contenedor BNCR
        const originalButton = document.getElementById('o_payment_submit_button');
        if (originalButton) {
            originalButton.style.display = 'none';
            originalButton.setAttribute('data-is-bncr', 'true');
        }

        this.bncrData ??= {};
        this.bncrData[paymentOptionId] ??= {};

        // Carga el SDK de BNCR solo una vez.
        if (!this.bncrData[paymentOptionId].isSdkLoaded) {
            const radio = document.querySelector(`input[name="o_payment_radio"][data-payment-option-id="${paymentOptionId}"]`);
            if (!radio || !radio.dataset['bncrInlineFormValues']) {
                console.error('BNCR: No se encontraron los valores del formulario inline');
                return;
            }
            
            const inlineFormValues = JSON.parse(radio.dataset['bncrInlineFormValues']);
            this.bncrData[paymentOptionId].inlineFormValues = inlineFormValues;

            try {
                // La URL del script se obtiene desde la configuración del proveedor en Odoo.
                await loadJS(inlineFormValues.modal_script_url);
                this.bncrData[paymentOptionId].isSdkLoaded = true;

                // Agregar event listener al botón habilitado de BNCR
                const bncrEnabledButton = document.getElementById('o_bncr_enabled_button');
                if (bncrEnabledButton) {
                    // Remover listeners previos para evitar duplicados
                    bncrEnabledButton.removeEventListener('click', this._bncrOnClick.bind(this));
                    bncrEnabledButton.addEventListener('click', this._bncrOnClick.bind(this));
                }
            } catch (error) {
                console.error('BNCR: Error cargando el script:', error);
                this._showError('Error cargando el sistema de pagos BNCR');
                return;
            }
        }

        // Ocultar loading y mostrar botón container
        if (loadingElement) {
            loadingElement.classList.add('d-none');
        }
        const bncrContainer = document.getElementById('o_bncr_button_container');
        if (bncrContainer) {
            bncrContainer.classList.remove('d-none');
        }
    },

    // #=== FLUJO DE PAGO ===#

    /**
     * Inicia el flujo de pago al hacer clic en el botón BNCR.
     * Llama al backend de Odoo para crear la transacción y obtener los datos firmados.
     * @private
     */
    async _bncrOnClick(event) {
        event.preventDefault();
        event.stopPropagation();
        
        this._bncrDisableButton();
        
        try {
            // Llama a _submitForm, lo que activará _get_specific_rendering_values en el backend
            // y el resultado se pasará a _processDirectFlow.
            await this._submitForm(event);
        } catch (error) {
            console.error('BNCR: Error en el proceso de pago:', error);
            this._bncrEnableButton();
            this._showError('Error procesando el pago. Intente nuevamente.');
        }
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

        try {
            const { gateway_url } = this.bncrData[paymentOptionId].inlineFormValues;
            const paymentData = processingValues.payment_data;

            if (!paymentData) {
                throw new Error('No se recibieron datos de pago del servidor');
            }

            // Elimina cualquier formulario antiguo para evitar conflictos.
            const oldForm = document.getElementById('f1_bncr');
            if (oldForm) {
                oldForm.remove();
            }

            // Crea dinámicamente el formulario que Alignet/BNCR VPOS2 necesita.
            const form = document.createElement('form');
            form.setAttribute('name', 'f1');
            form.setAttribute('id', 'f1_bncr');
            form.setAttribute('method', 'post');
            
            // El backend ya nos dio un diccionario 'payment_data' con todos los campos necesarios.
            for (const [key, value] of Object.entries(paymentData)) {
                const input = document.createElement('input');
                input.setAttribute('type', 'hidden');
                input.setAttribute('name', key);
                input.setAttribute('value', value || '');
                form.appendChild(input);
            }
            document.body.appendChild(form);
            
            // Verificar que el objeto AlignetVPOS2 esté disponible
            if (typeof AlignetVPOS2 === 'undefined') {
                throw new Error('El script de BNCR no se cargó correctamente');
            }
            
            // Abre el modal de BNCR. El script cargado (AlignetVPOS2) se encarga del resto.
            AlignetVPOS2.openModal(gateway_url);
            
        } catch (error) {
            console.error('BNCR: Error procesando flujo directo:', error);
            this._bncrEnableButton();
            this._showError(`Error abriendo el modal de pago: ${error.message}`);
        }
    },

    // #=== MÉTODOS DE UTILIDAD ===#

    /**
     * Deshabilita el botón de BNCR
     * @private
     */
    _bncrDisableButton() {
        const enabledButton = document.getElementById('o_bncr_enabled_button');
        const disabledButton = document.getElementById('o_bncr_disabled_button');
        
        if (enabledButton) enabledButton.classList.add('d-none');
        if (disabledButton) disabledButton.classList.remove('d-none');
    },

    /**
     * Habilita el botón de BNCR
     * @private
     */
    _bncrEnableButton() {
        const enabledButton = document.getElementById('o_bncr_enabled_button');
        const disabledButton = document.getElementById('o_bncr_disabled_button');
        
        if (disabledButton) disabledButton.classList.add('d-none');
        if (enabledButton) enabledButton.classList.remove('d-none');
    },

    /**
     * Muestra un mensaje de error
     * @private
     */
    _showError(message) {
        // Implementar según tu sistema de notificaciones de Odoo
        console.error(message);
        // Opcional: mostrar notificación toast o alert
        if (this.call && this.call('notification', 'add')) {
            this.call('notification', 'add', message, {
                type: 'danger',
            });
        }
    },
});