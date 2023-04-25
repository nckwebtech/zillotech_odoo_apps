{
    'name': 'NCK Product Documents',
    'version': '15.0.1.0.0',
    'sequence': 10,
    'summary': 'Product Documents',
    'description': """This app help to set Product Documents and forward to sales and invoice.""",
    'author': 'Zillo Tech',
    'company': 'Zillo WebTech',
    'maintainer': 'Zillo WebTech',
    'website': 'https://www.nckwebtech.com/',
    'images': ['static/description/banner.png'],
    'depends': ['base', 'product', 'account', 'sale', 'sale_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/product_template_views.xml',
        'views/sale_documents.xml',],
    'assets': {
        'web.assets_backend': [
            'zillotech_product_documents/static/src/js/many_tags_link.js',
        ], },
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
