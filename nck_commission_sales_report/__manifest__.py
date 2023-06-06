{
    'name': "Commission Sales Report",
    'version': "16.0.1.0,0",
    'summary': """""",
    'description': """""",
    'author': 'Zillo Tech',
    'company': 'Zillo WebTech',
    'maintainer': 'Zillo WebTech',
    'website': 'https://www.nckwebtech.com/',
    'category': 'Report',
    'depends': ['base', 'base_accounting_kit', 'account'],
    'data': ['security/ir.model.access.csv',
             'views/views.xml',
             'views/wizard_history.xml',
             'report/commission_sale_report.xml',
             'wizards/report_wizard.xml',
             'wizards/wizard_views.xml',

             ],
    'assets': {
        'web.assets_backend': [
            'nck_commission_sales_report/static/src/css/report.css',
            'nck_commission_sales_report/static/src/js/product_sale.js',
            'nck_commission_sales_report/static/src/xml/**/*',

        ],
    },
    'images': ['static/description/banner.png'],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
    'price': 78.50,
    'currency': 'USD',
}
