from odoo import models, api


class SaleOrderLineInheritKansas(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id')
    def _compute_tax_id(self):
        """override the existing function to recompute the tax"""
        if not self.order_id.partner_shipping_id.exclude_sales_tax:
            for rec in self:
                if rec.product_id:
                    if not rec.product_id.exclude_sales_tax:
                        data = self.env['tax.table'].search(
                            [('state_id', '=', self.order_id.partner_shipping_id.state_id.id)], limit=1)
                        if data.live_tax_id:
                            rec.tax_id = data.live_tax_id
                        else:
                            rec.tax_id = data.sales_tax_id
                    else:
                        rec.tax_id = False
        else:
            for rec in self:
                rec.tax_id = False
