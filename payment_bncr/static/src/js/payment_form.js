/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

// Extender PaymentForm para manejar BNCR - Compatible con Odoo 18
export class BNCRPaymentForm extends Component {
    
    /**
     * Procesar el formulario de pago BNCR
     */
    async _processBNCRPayment(processingValues) {
        
        // Verificar que tenemos los datos necesarios
        if (!processingValues.modal_script_url) {
            this._displayError(
                _t("Configuration Error"),
                _t("BNCR modal script URL is not configured.")
            );
            return Promise.reject("Missing BNCR configuration");
        }
        
        try {
            // Cargar el script del modal de BNCR si no está cargado
            if (typeof window.AlignetVPOS2 === 'undefined') {
                await this._loadBNCRScript(processingValues.modal_script_url);
            }
            
            // Preparar el formulario para BNCR
            this._prepareBNCRForm(processingValues);
            
            // Abrir el modal de BNCR
            return this._openBNCRModal(processingValues.api_url);
            
        } catch (error) {
            console.error('BNCR: Error processing payment', error);
            this._displayError(
                _t("Payment Error"),
                _t("There was an error initializing the payment system. Please try again.")
            );
            return Promise.reject(error);
        }
    }
    
    /**
     * Cargar el script de BNCR
     * @private
     * @param {string} scriptUrl - URL del script
     * @returns {Promise}
     */
    async _loadBNCRScript(scriptUrl) {
        try {
            await loadJS(scriptUrl);
            
            // Verificar que el objeto AlignetVPOS2 esté disponible
            if (typeof window.AlignetVPOS2 === 'undefined') {
                throw new Error('AlignetVPOS2 object not found after loading script');
            }
            
            console.log('BNCR: Script loaded successfully');
        } catch (error) {
            console.error('BNCR: Failed to load script', error);
            throw new Error(`Failed to load BNCR script: ${error.message}`);
        }
    }
    
    /**
     * Preparar el formulario HTML para BNCR
     * @private
     * @param {Object} processingValues - Valores de procesamiento
     */
    _prepareBNCRForm(processingValues) {
        // Buscar o crear el formulario BNCR
        let form = document.getElementById('bncr_payment_form');
        
        if (!form) {
            form = document.createElement('form');
            form.id = 'bncr_payment_form';
            form.name = 'bncr_payment_form';
            form.method = 'post';
            form.className = 'alignet-form-vpos2';
            form.style.display = 'none';
            document.body.appendChild(form);
        } else {
            // Limpiar formulario existente
            form.innerHTML = '';
        }
        
        // Agregar campos del payment_data
        const paymentData = processingValues.payment_data;
        for (const [key, value] of Object.entries(paymentData)) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = value || '';
            form.appendChild(input);
        }
        
        console.log('BNCR: Form prepared with data', paymentData);
    }
    
    /**
     * Abrir el modal de BNCR
     * @private
     * @param {string} apiUrl - URL de la API
     * @returns {Promise}
     */
    _openBNCRModal(apiUrl) {
        return new Promise((resolve, reject) => {
            try {
                // Configurar callbacks para el modal
                this._setupBNCRCallbacks(resolve, reject);
                
                // Abrir el modal
                window.AlignetVPOS2.openModal(apiUrl);
                
                console.log('BNCR: Modal opened');
                
            } catch (error) {
                console.error('BNCR: Error opening modal', error);
                reject(error);
            }
        });
    }
    
    /**
     * Configurar callbacks para el modal de BNCR
     * @private
     * @param {Function} resolve - Función resolve de la Promise
     * @param {Function} reject - Función reject de la Promise
     */
    _setupBNCRCallbacks(resolve, reject) {
        
        // Timeout para evitar que se quede colgado
        const timeout = setTimeout(() => {
            this._displayError(
                _t("Payment Timeout"),
                _t("The payment process is taking too long. Please try again.")
            );
            reject(new Error('Payment timeout'));
        }, 300000); // 5 minutos
        
        // Cleanup function
        const cleanup = () => {
            clearTimeout(timeout);
        };
        
        // Escuchar mensajes del modal
        const messageHandler = (event) => {
            // Verificar origen del mensaje por seguridad
            if (!event.origin.includes('alignetsac.com')) {
                return;
            }
            
            try {
                const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
                
                if (data.type === 'bncr_success') {
                    cleanup();
                    window.removeEventListener('message', messageHandler);
                    resolve(data);
                } else if (data.type === 'bncr_error' || data.type === 'bncr_cancel') {
                    cleanup();
                    window.removeEventListener('message', messageHandler);
                    reject(new Error(data.message || 'Payment failed'));
                }
            } catch (e) {
                console.warn('BNCR: Invalid message format', event.data);
            }
        };
        
        window.addEventListener('message', messageHandler);
    }
    
    /**
     * Mostrar error al usuario
     * @private
     * @param {string} title - Título del error
     * @param {string} message - Mensaje del error
     */
    _displayError(title, message) {
        // Usar el sistema de notificaciones de Odoo 18
        if (this.env && this.env.services && this.env.services.notification) {
            this.env.services.notification.add(message, {
                title: title,
                type: 'danger',
                sticky: true,
            });
        } else {
            // Fallback para mostrar error
            console.error(`${title}: ${message}`);
            alert(`${title}: ${message}`);
        }
    }
}

// Registrar el componente para Odoo 18
registry.category("payment_form").add("bncr", BNCRPaymentForm);

// Funciones globales para compatibilidad con BNCR
window.bncrPaymentSuccess = function(data) {
    console.log('BNCR: Payment successful', data);
    window.postMessage({
        type: 'bncr_success',
        data: data
    }, window.location.origin);
};

window.bncrPaymentError = function(error) {
    console.error('BNCR: Payment error', error);
    window.postMessage({
        type: 'bncr_error',
        message: error.message || 'Payment failed'
    }, window.location.origin);
};

window.bncrPaymentCancel = function() {
    console.log('BNCR: Payment cancelled');
    window.postMessage({
        type: 'bncr_cancel',
        message: 'Payment cancelled by user'
    }, window.location.origin);
};