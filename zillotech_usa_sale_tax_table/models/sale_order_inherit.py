from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_shipping_id', 'partner_id')
    def _onchange_partner_shipping(self):
        """ Onchange function for tax computation in sale order """
        if self.partner_shipping_id:
            if not self.partner_id.exclude_sales_tax:
                if self.order_line:
                    data = self.env['tax.table'].search([('state_id', '=', self.partner_shipping_id.state_id.id)],
                                                        limit=1)
                    for line in self.order_line:
                        if not line.product_id.exclude_sales_tax:
                            line.write({'tax_id': data.sales_tax_id})
                        else:
                            line.write({'tax_id': False})
                        if data.tax_shipping == 'yes':
                            self.order_line[-1].write({'tax_id': data.sales_tax_id})
                        else:
                            if self.order_line[-1].product_id.detailed_type == 'service':
                                self.order_line[-1].write({'tax_id': False})
                            else:
                                self.order_line[-1].write({'tax_id': data.sales_tax_id})
            else:
                if self.order_line:
                    for line in self.order_line:
                        line.write({'tax_id': False})

    complete_address = fields.Char(related='partner_shipping_id.contact_address', string="")
    invoice_address = fields.Char(related='partner_invoice_id.contact_address', string="")

    def _create_delivery_line(self, carrier, price_unit):
        """Super method on delivery line to recompute the shipping cost tax ! """
        res = super(SaleOrder, self)._create_delivery_line(carrier, price_unit)
        if not self.partner_id.exclude_sales_tax:
            if self.order_line:
                data = self.env['tax.table'].search([('state_id', '=', self.partner_shipping_id.state_id.id)], limit=1)
                if data.tax_shipping == 'yes':
                    self.order_line[-1].write({'tax_id': data.sales_tax_id})
                else:
                    self.order_line[-1].write({'tax_id': False})
        else:
            self.order_line[-1].write({'tax_id': False})
        return res


class InvoiceInherit(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(InvoiceInherit, self)._onchange_partner_id()
        if self.partner_id:
            self.partner_shipping_id = self.partner_id
            self._onchange_partner_shipping_id()
        return res

    @api.onchange('partner_shipping_id')
    def _onchange_partner_shipping_id(self):
        res = super(InvoiceInherit, self)._onchange_partner_shipping_id()
        if not self.partner_shipping_id.exclude_sales_tax:
            if self.invoice_line_ids:
                data = self.env['tax.table'].search([('state_id', '=', self.partner_shipping_id.state_id.id)], limit=1)

                if data:
                    for line in self.invoice_line_ids:
                        if not line.product_id.exclude_sales_tax:
                            line.with_context(check_move_validity=False).write({'tax_ids': data.sales_tax_id})
                            print(data.sales_tax_id.name, 'qwertyuio')
                        else:
                            line.with_context(check_move_validity=False).write({'tax_ids': False})
                else:
                    for line in self.invoice_line_ids:
                        line.with_context(check_move_validity=False).write({'tax_ids': False})
            self._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
        else:
            if self.invoice_line_ids:
                for line in self.invoice_line_ids:
                    line.with_context(check_move_validity=False).write({'tax_ids': False})
            self._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
        return res

    complete_address = fields.Char(related='partner_shipping_id.contact_address', string="")


class SaleOrderLineInherit(models.Model):
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
                        rec.tax_id = data.sales_tax_id
                    else:
                        rec.tax_id = False
        else:
            for rec in self:
                rec.tax_id = False


class ProductInherit(models.Model):
    _inherit = 'product.template'

    exclude_sales_tax = fields.Boolean('Exclude Sales Tax',
                                       help='This helps to exclude the tax applied on the product !')


class CustomerInherit(models.Model):
    _inherit = 'res.partner'

    exclude_sales_tax = fields.Boolean('Sales Tax Exempt',
                                       help='This helps to exclude the tax applied on the product !')
