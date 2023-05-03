from odoo import models, fields, api


class InvoiceInheritData(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(InvoiceInheritData, self)._onchange_partner_id()
        if self.partner_id:
            self.partner_shipping_id = self.partner_id
            self._onchange_partner_shipping_id()
        return res

    @api.onchange('partner_shipping_id')
    def _onchange_partner_shipping_id(self):
        res = super(InvoiceInheritData, self)._onchange_partner_shipping_id()
        self.partner_shipping_id.live_tax_history_id = False
        if not self.partner_shipping_id.exclude_sales_tax:
            if self.invoice_line_ids:
                data = self.env['tax.table'].search([('state_id', '=', self.partner_shipping_id.state_id.id)], limit=1)
                if data:
                    for line in self.invoice_line_ids:
                        if not line.product_id.exclude_sales_tax:
                            if not self.partner_shipping_id.live_tax_invoice_id:
                                line.with_context(check_move_validity=False).write({'tax_ids': data.sales_tax_id})
                            else:
                                line.with_context(check_move_validity=False).write(
                                    {'tax_ids': self.partner_shipping_id.live_tax_invoice_id})
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

        if self.partner_shipping_id:
            data = self.env['tax.table'].search_read([('state_id', '=', self.partner_shipping_id.state_id.id)],
                                                     ['destination_tax'], limit=1)
            if data and data[0]['destination_tax'] == 'yes':
                if self.partner_shipping_id and self._origin.partner_shipping_id != self.partner_shipping_id:
                    self.show_kansas_tax_button_invoice = True
                else:
                    self.show_kansas_tax_button_invoice = False
            else:
                self.show_kansas_tax_button_invoice = False

        return res

    def update_destination_tax_invoice(self):
        if self.partner_shipping_id:
            data = self.env['tax.table'].search([('state_id', '=', self.partner_shipping_id.state_id.id)], limit=1)
            if data.destination_tax == 'yes':
                values = dict(
                    address='%s %s' % (
                        self.partner_shipping_id.street if self.partner_shipping_id.street else '',
                        self.partner_shipping_id.street2 if self.partner_shipping_id.street2 else ''),
                    state=self.partner_shipping_id.state_id.name if self.partner_shipping_id.state_id.name else None,
                    city=self.partner_shipping_id.city if self.partner_shipping_id.city else None,
                    zip=self.partner_shipping_id.zip if self.partner_shipping_id.zip else None)
                tax_rate = self.env['sale.order'].fetch_tax_datas(values)
                if tax_rate:
                    tax_rate_data = self.env['account.tax'].search([('name', 'ilike', '%s' % (
                        float(tax_rate['totalTax'])) + ' % ' + '%s' % data.state_id.name + ' Sales Tax'),
                                                                    ('amount', '=',
                                                                     round(float(tax_rate['totalTax']), 2))])
                    if not tax_rate_data:
                        tax_rate_data = self.env['account.tax'].create({'name': '%s' % (
                            float(tax_rate['totalTax'])) + ' % ' + '%s' % data.state_id.name + ' Sales Tax',
                                                                        'amount': round(float(tax_rate['totalTax']),

                                                                                        2)})
                        self.partner_shipping_id.live_tax_invoice_id = tax_rate_data
                        self.partner_shipping_id.live_tax_history_id = tax_rate_data

                        if self.partner_shipping_id.live_tax_invoice_id:
                            for line in self.invoice_line_ids:
                                if not line.product_id.exclude_sales_tax:
                                    if not self.partner_shipping_id.live_tax_invoice_id:
                                        line.with_context(check_move_validity=False).write(
                                            {'tax_ids': data.sales_tax_id})
                                    else:
                                        line.with_context(check_move_validity=False).write(
                                            {'tax_ids': self.partner_shipping_id.live_tax_invoice_id})
                                else:
                                    line.with_context(check_move_validity=False).write({'tax_ids': False})
                            self.partner_shipping_id.live_tax_invoice_id = False

                    else:

                        self.partner_shipping_id.live_tax_invoice_id = tax_rate_data
                        self.partner_shipping_id.live_tax_history_id = tax_rate_data

                        if self.partner_shipping_id.live_tax_invoice_id:
                            for line in self.invoice_line_ids:
                                if not line.product_id.exclude_sales_tax:
                                    if not self.partner_shipping_id.live_tax_invoice_id:
                                        line.with_context(check_move_validity=False).write(
                                            {'tax_ids': data.sales_tax_id})
                                    else:
                                        line.with_context(check_move_validity=False).write(
                                            {'tax_ids': self.partner_shipping_id.live_tax_invoice_id})
                                else:
                                    line.with_context(check_move_validity=False).write({'tax_ids': False})
                            self.partner_shipping_id.live_tax_invoice_id = False

    show_kansas_tax_button_invoice = fields.Boolean('Show Kansas tax', default=False)


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    def _get_computed_taxes(self):
        self.ensure_one()
        if not self.move_id.partner_shipping_id.exclude_sales_tax:
            if self.product_id:
                if not self.product_id.exclude_sales_tax:
                    data = self.env['tax.table'].search(
                        [('state_id', '=', self.move_id.partner_shipping_id.state_id.id)], limit=1)
                    if not self.move_id.partner_shipping_id.live_tax_history_id:
                        self.tax_ids = data.sales_tax_id
                        tax_ids = self.tax_ids
                        return tax_ids
                    else:
                        self.tax_ids = self.move_id.partner_shipping_id.live_tax_history_id
                        tax_ids = self.tax_ids
                        return tax_ids
