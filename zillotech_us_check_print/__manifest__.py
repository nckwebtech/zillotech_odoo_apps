{
    'name': 'Check Print Pro',
    'version': '15.0.1.0.0',
    'summary': """""",
    'description': """""",
    'category': 'Accounting',
    "author": "Zillo Tech",
    "company": "Zillo WebTech",
    "maintainer": "Zillo WebTech",
    "website": "https://www.nckwebtech.com/",
    'depends': ['account', 'account_check_printing', 'base', 'website'],
    'data': ['security/ir.model.access.csv',
             'data/data.xml',
             'reports/print_report_actions.xml',
             'reports/page_details_templates.xml',
             'reports/check_templates_top.xml',
             'reports/check_templates_middle.xml',
             'reports/check_templates_bottom.xml',
             'views/check_config_views.xml',
             'views/inherit_views.xml'

             ],
    'assets': {
        'web.report_assets_common': [
            'zillotech_us_check_print/static/**/*',
        ]
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 70.00,
    'currency': 'USD',
}
