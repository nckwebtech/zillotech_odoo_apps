from odoo import fields, models


class CommissionCustomerHistory(models.Model):
    _name = 'commission.customer.line.history'

    partner_id = fields.Many2one('res.partner', string='Customer')
    company_name = fields.Char('Company Name', related='partner_id.name')
    commission = fields.Float('Commission (%)', required=True)
    wizard_id = fields.Many2one('account.commission.wizard.history')


class DeductForProductHistory(models.Model):
    _name = 'product.commission.deduct.history'

    product_id = fields.Many2one('product.product', 'Product')
    wizard_id = fields.Many2one('account.commission.wizard.history')
    deduct_amount = fields.Float('Amount')


class ProductCommissionReportHistory(models.Model):
    _name = 'account.commission.wizard.history'

    report_name = fields.Char('Report Name')
    wizard_id = fields.Integer()
    date_from_filter = fields.Date(string='Date From')
    date_to_filter = fields.Date(string='Date To')
    commission_value = fields.Float('Commission ( % )', default=0.0)
    add_report_product_ids = fields.Many2many('product.product')
    commission_customer_line_ids = fields.One2many('commission.customer.line.history', 'wizard_id')
    deduct_product_line_ids = fields.One2many('product.commission.deduct.history', 'wizard_id')
