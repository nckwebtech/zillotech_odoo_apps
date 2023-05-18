{
    'name': 'Customer Statements & Customer Overdue Payments',
    'version': '16.0.1.0.1',
    'summary': """Customers/Suppliers Statement Report""",
    'description': """This app helps to Customer/Vendor Statements and Overdue Payments Reports with auto send feature .""",
    'category': 'Accounting',
    'author': 'Zillo Tech',
    'company': 'Zillo WebTech',
    'maintainer': 'Zillo WebTech',
    'website': 'https://www.nckwebtech.com/',
    'depends': ['base', 'account', 'contacts', 'mail', 'web', 'payment', 'portal'],
    'data': ['security/ir.model.access.csv',
             'wizards/outstanding_report.xml',
             'data/static_data.xml',
             'data/scheduled_actions.xml',
             'wizards/montly_weekly_pay_button.xml',
             'wizards/custom_wizard_view.xml',
             'reports/buyer_print_reports.xml',
             'reports/report_templates.xml',
             'reports/reports_weekly_monthly.xml',
             'views/res_partner_statements_view.xml',
             'views/res_partner_wizard_view.xml',
             'views/filter_buyer_statement_views.xml',
             'views/res_config_views.xml',
             'views/statement_templates.xml',
             'views/layout_inherit.xml',
             'wizards/sent_email_view.xml',
             'views/portal_invoice_payment_option.xml'
             ],
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 5,
    'price': 39.50,
    'currency': 'USD',
}
