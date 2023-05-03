from odoo import models, fields


class SaleTaxTable(models.Model):
    _name = 'tax.table'
    _description = 'Sale Tax Table'
    _rec_name = 'state_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state_id = fields.Many2one('res.country.state', 'State', help='Here you can choose state !',
                               domain=[('country_id', '=', 233)], required=True, ondelete='cascade')
    sales_tax_id = fields.Many2one('account.tax', string="Sales Tax", help='Add your Sale Tax here !',
                                   ondelete='cascade')
    tax_shipping = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Tax Shipping', default='no',
                                    required=True, help='Choose whether you want to add tax for shipping !')

