{
    'name': "BNCR Payment Gateway",
    'version': '18.0.0.1',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "BNCR Payment Gateway Plugin allows merchants to accept Visa and Mastercard",
    'author': 'Daniel Avila',
    'website': 'www.promotoglobal.com',
    'depends': ['payment'],
    'data': [
        'views/payment_form_templates.xml',
        'views/payment_provider_views.xml',
        'views/bncr_templates.xml',
		'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_bncr/static/src/**/*',
        ],
    },
    'application': True,
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
