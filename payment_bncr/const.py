# Part of Odoo. See LICENSE file for full copyright and licensing details.

# BNCR supported payment method codes
DEFAULT_PAYMENT_METHOD_CODES = [
    'bncr',
]

# Mapeo de códigos de respuesta de BNCR a estados de transacción de Odoo
BNCR_RESPONSE_CODE_MAPPING = {
    # Transacciones aprobadas
    'done': ['00'],  # Aprobada
    
    # Transacciones pendientes (pueden requerir verificación adicional)
    'pending': [
        '01',  # Referir al emisor
        '02',  # Referir al emisor especial
        '03',  # Comercio inválido
    ],
    
    # Transacciones canceladas/rechazadas
    'canceled': [
        '05',  # No aprobar
        '14',  # Número de tarjeta inválido
        '54',  # Tarjeta vencida
        '61',  # Excede límite de monto
        '62',  # Tarjeta restringida
        '65',  # Excede límite de frecuencia
    ],
    
    # Errores del sistema
    'error': [
        '96',  # Error del sistema
        '91',  # Emisor o switch inoperativo
    ]
}

# Mapeo de monedas ISO a códigos de BNCR
CURRENCY_CODE_MAPPING = {
    'USD': '840',  # Dólar estadounidense
    'CRC': '188',  # Colón costarricense
    'EUR': '978',  # Euro
    'CAD': '124',  # Dólar canadiense
    'GBP': '826',  # Libra esterlina
    'JPY': '392',  # Yen japonés
}

# Códigos de país soportados (ISO 3166-1 alpha-2)
SUPPORTED_COUNTRY_CODES = [
    'CR',  # Costa Rica
    'US',  # Estados Unidos
    'CA',  # Canadá
    'MX',  # México
    'PA',  # Panamá
    'GT',  # Guatemala
    'NI',  # Nicaragua
    'HN',  # Honduras
    'SV',  # El Salvador
    'BZ',  # Belice
]

# Configuración de URLs por ambiente
GATEWAY_URLS = {
    'test': 'https://integracion.alignetsac.com/',
    'production': 'https://vpos2.alignetsac.com/',  # URL de producción (verificar)
}

# URLs de scripts JavaScript
MODAL_SCRIPT_URLS = {
    'test': 'https://integracion.alignetsac.com/VPOS2/js/modalcomercio.js',
    'production': 'https://vpos2.alignetsac.com/VPOS2/js/modalcomercio.js',  # URL de producción (verificar)
}

# Configuraciones por defecto
DEFAULT_LANGUAGE = 'SP'  # Español
DEFAULT_PROGRAMMING_LANGUAGE = 'PHP'
DEFAULT_COUNTRY = 'CR'  # Costa Rica

# Timeout para requests (en segundos)
REQUEST_TIMEOUT = 30

# Estados de transacción según la documentación de BNCR
TRANSACTION_STATUS_MAPPING = {
    'pending': ['PENDING', 'PROCESSING', 'INITIATED'],
    'done': ['COMPLETED', 'APPROVED', 'SUCCESS'],
    'canceled': ['CANCELLED', 'REJECTED', 'DECLINED', 'FAILED'],
    'error': ['ERROR', 'TIMEOUT', 'SYSTEM_ERROR']
}