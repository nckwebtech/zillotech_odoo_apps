from odoo import fields, models


class CommissionCustomer(models.TransientModel):
    _name = 'commission.customer.line'

    partner_id = fields.Many2one('res.partner', string='Customer')
    company_name = fields.Char('Company Name', related='partner_id.name')
    commission = fields.Float('Commission (%)', required=True)
    wizard_id = fields.Many2one('account.commission.wizard')


class DeductForProduct(models.TransientModel):
    _name = 'product.commission.deduct'

    product_id = fields.Many2one('product.product', 'Product')
    wizard_id = fields.Many2one('account.commission.wizard')
    deduct_amount = fields.Float('Amount')

