from odoo import models


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    def _get_computed_taxes(self):
        self.ensure_one()
        if not self.move_id.partner_shipping_id.exclude_sales_tax:
            if self.product_id:
                if not self.product_id.exclude_sales_tax:
                    data = self.env['tax.table'].search(
                        [('state_id', '=', self.move_id.partner_shipping_id.state_id.id)], limit=1)
                    self.tax_ids = data.sales_tax_id
                    tax_ids = self.tax_ids
                    return tax_ids
