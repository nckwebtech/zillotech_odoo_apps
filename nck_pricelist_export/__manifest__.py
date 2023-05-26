{
    'name': "Pricelist Export",
    'version': "15.0.1.0,0",
    'category': 'Sales',
    'summary': """Export customer related pricelist !""",
    'description': """1. Export customer related pricelist.
                      2. Export selected pricelist directly from wizard.
                      3. Reports are available both in Excel and PDF Format.""",
    'author': 'Zillo Tech',
    'company': 'Zillo WebTech',
    'maintainer': 'Zillo WebTech',
    'website': 'https://www.nckwebtech.com/',
    'depends': ['contacts', 'product', 'base', 'sale_management', 'sale'],
    'data': ['security/ir.model.access.csv',
             'reports/pdf_pricelist_export.xml',
             'reports/export_only_pricelist.xml',
             'wizards/wizard_view.xml',
             'wizards/pricelist_wizard_view.xml'],
    'assets': {
        'web.assets_backend': [],
        'web.assets_qweb': [],
    },
    'images': ['static/description/banner.png'],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
    'price': 78.50,
    'currency': 'USD',
}
