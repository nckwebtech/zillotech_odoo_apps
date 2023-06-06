import json
import time
import io
from datetime import date, timedelta

from odoo import fields, models, api, _
from odoo.tools import float_is_zero

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ProductSalesReport(models.TransientModel):
    _inherit = "account.common.report"
    _name = 'account.commission.sales'

    @api.model
    def view_report(self, option, params):
        if params.get('context'):
            context = params.get('context')
            wizard = self.env['account.commission.wizard'].search(
                [('id', '=', context['active_id'],)], order="id asc")
        else:
            wizard = self.env['account.commission.wizard'].search(
                [])[-1]
        first_day_of_current_month = date.today().replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

        data = {
            'model': self,
            'wizard_model': wizard,
            'product_ids': [x.id for x in wizard.add_report_product_ids if wizard.add_report_product_ids],
            'deduct_product_ids': [dict(id=x.product_id.id, amount=x.deduct_amount) for x in
                                   wizard.deduct_product_line_ids if
                                   wizard.deduct_product_line_ids],
            'date_from_filter': wizard.date_from_filter if wizard.date_from_filter else first_day_of_previous_month,
            'date_to_filter': wizard.date_to_filter if wizard.date_to_filter else last_day_of_previous_month,
            'product_records': [x.name for x in wizard.add_report_product_ids if wizard.add_report_product_ids],
            'company': self.env.company,
            'company_name': self.env.company.name,
        }

        records = self._get_report_values(data)

        currency = self._get_currency()

        return {
            'name': "Commission Sales Report",
            'type': 'ir.actions.client',
            'tag': 'p_c',
            'product_report_lines': records['Products'],
            'wizard_data': data,
            'currency': currency,

        }

    def _get_report_values(self, data):
        wizard_model = data['wizard_model']

        if wizard_model.commission_customer_line_ids:
            filtered_customers = wizard_model.commission_customer_line_ids
        else:
            filtered_customers = None

        if wizard_model.add_report_product_ids:
            filtered_product_data = wizard_model.add_report_product_ids
        else:
            filtered_product_data = None

        account_product_res = self._prepare_commission_lines(data, filtered_customers, filtered_product_data)

        return {
            'doc_ids': self.ids,
            'docs': wizard_model,
            'time': time,
            'Products': account_product_res,

        }

    @api.model
    def create(self, vals):
        vals['target_move'] = 'posted'
        res = super(ProductSalesReport, self).create(vals)
        return res

    def _prepare_commission_lines(self, data, filtered_customers, filtered_product_data):

        customer_line_amount = []
        res_data = []
        row = 0
        total_data = {}
        all_total_data = []

        line_all_total = 0.0
        all_qty_total = 0
        all_commission_total = 0.0
        currency = None
        symbol = None
        line_data = dict(
            (customer.partner_id.id or False, []) for customer in filtered_customers)
        if filtered_customers:
            customer_ids = [customer.partner_id.id for customer in filtered_customers]

            commission_data = dict(
                (customer.partner_id.id or False, customer.commission or False) for customer in filtered_customers)

            for customer in customer_ids:
                line_amount_total = 0.0
                total_qty_sold = 0
                commission_amount_total = 0.0
                total_list = []

                customer_invoices = self.env['account.move'].search(
                    [('state', '=', 'posted'), ('move_type', '=', 'out_invoice'),
                     ('invoice_date', '>=', data.get('date_from_filter')),
                     ('invoice_date', '<=', data.get('date_to_filter'))]).filtered(
                    lambda x: x.partner_id.id == customer)
                invoice_ids = customer_invoices.mapped('invoice_line_ids.product_id').filtered(
                    lambda x: x.id in data.get('product_ids'))
                product_ids = [x.id for x in invoice_ids]
                deduct_ids = [x['id'] for x in data.get('deduct_product_ids')]
                if customer_invoices:
                    for invoice in customer_invoices:
                        if invoice.invoice_line_ids:
                            for line in invoice.invoice_line_ids:
                                line_amount = 0.0
                                if line.product_id.id in product_ids and line.quantity > 0:
                                    partner_id = line.move_id.partner_id.name or False
                                    product_id = line.product_id
                                    product_name = line.product_id.name
                                    internal_reference = line.product_id.default_code
                                    move_id = line.move_id.id
                                    move_name = line.move_id.name
                                    invoice_date = line.move_id.invoice_date
                                    currency_id = line.company_id.currency_id.position
                                    currency_symbol = line.company_id.currency_id.symbol
                                    invoice_quantity = line.quantity
                                    total_qty_sold = int(total_qty_sold + line.quantity)
                                    if line.product_id.id in deduct_ids:
                                        for deduct in data.get('deduct_product_ids'):
                                            if deduct['id'] == line.product_id.id:
                                                line_amount = float(line.price_subtotal) - float(
                                                    deduct['amount'] * invoice_quantity)
                                    else:
                                        line_amount = float(line.price_subtotal)
                                    line_amount_total = float(line_amount_total + line_amount)

                                    commission_amount = float(
                                        float(line_amount) * float(commission_data[customer])) / float(100)
                                    commission_amount_total = commission_amount_total + commission_amount
                                    if customer:
                                        line_data[customer].append({
                                            'line': line,
                                            'product_id': product_id,
                                            'product_name': product_name,
                                            'partner_id': partner_id,
                                            'move': move_name,
                                            'currency': currency_id,
                                            'symbol': currency_symbol,
                                            'mov_id': move_id,
                                            'internal_reference': internal_reference,
                                            'invoice_quantity': invoice_quantity,
                                            'amount': round(line_amount, 2),
                                            'list_price': round(product_id.list_price, 2),
                                            'invoice_date': invoice_date,
                                            'commission_amount': round(commission_amount, 2),
                                        })
                    if customer and line_amount_total:
                        partner_record = self.env['res.partner'].browse(customer)
                        line_amount_dict = {'partner_id': customer,
                                            'partner_name': partner_record.name,
                                            'partner_record': partner_record,
                                            'line_amount_total': round(line_amount_total, 2),
                                            'total_qty_sold': total_qty_sold,
                                            'commission_amount_total': round(commission_amount_total, 2),
                                            'currency': line_data[customer][0]['currency'],
                                            'symbol': line_data[customer][0]['symbol'],
                                            }
                        total_list.append(line_amount_dict)
                        total_data[customer] = line_amount_dict
                        customer_line_amount.append(line_amount_dict)

            for customer in customer_line_amount:
                at_least_one_amount = False
                values = {}

                if customer['partner_id'] in customer_ids:
                    row = row + 1
                    values['row'] = row
                    values['partner_id'] = customer['partner_id']
                    partner_record = customer['partner_record']
                    values['partner_record'] = partner_record
                    values['partner_name'] = partner_record.name
                    product_all_total = customer['line_amount_total']
                    values['direction_amount'] = product_all_total
                    product_total_quantity = customer['total_qty_sold']
                    values['total_qty_sold'] = product_total_quantity

                for new in commission_data:
                    if customer['partner_id'] == new:
                        commission_percentage = commission_data[new]
                        values['commission_percentage'] = commission_percentage
                for rec in line_data:
                    if customer['partner_id'] == rec:
                        child_lines = line_data[rec]
                        child_lines_sorted = sorted(child_lines, key=lambda i: i['invoice_date'])
                        values['child_lines'] = child_lines_sorted
                for total in total_data:
                    if customer['partner_id'] == total:
                        total_lines = total_data[total]
                        values['total_lines'] = total_lines
                        line_all_total = line_all_total + float(total_lines['line_amount_total'])
                        all_qty_total = all_qty_total + float(total_lines['total_qty_sold'])
                        currency = total_lines['currency']
                        symbol = total_lines['symbol']
                        all_commission_total = all_commission_total + float(total_lines['commission_amount_total'])

                if not float_is_zero(values['direction_amount'],
                                     precision_rounding=self.env.company.currency_id.rounding):
                    at_least_one_amount = True

                if at_least_one_amount or (
                        self._context.get('include_nullified_amount') and line_data[customer['partner_id']]):
                    res_data.append(values)
            all_total = dict(line_all_total=round(line_all_total, 2), all_qty_total=round(all_qty_total, 2),
                             all_commission_total=round(all_commission_total, 2), currency=currency, symbol=symbol)
            all_total_data.append(all_total)
        return res_data, line_data, all_total_data

    @api.model
    def _get_currency(self):
        journal = self.env['account.journal'].browse(
            self.env.context.get('default_journal_id', False))
        if journal.currency_id:
            return journal.currency_id.id
        lang = self.env.user.lang
        if not lang:
            lang = 'en_US'
        lang = lang.replace("_", '-')
        currency_array = [self.env.company.currency_id.symbol,
                          self.env.company.currency_id.position, lang]
        return currency_array

    def get_dynamic_xlsx_report(self, response, report_data, wizard_data, dfr_data):
        report_data = json.loads(report_data)
        wizard_data = json.loads(wizard_data)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        cell_format = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px',
             'border': 1,
             'border_color': 'black'})
        sheet = workbook.add_worksheet()
        head = workbook.add_format({'align': 'center', 'bold': True,
                                    'font_size': '20px'})

        txt = workbook.add_format({'font_size': '10px', 'border': 1})
        sub_heading_sub = workbook.add_format({'align': 'center', 'bold': True,
                                               'border': 1
                                               }
                                              )
        sheet.merge_range('A1:H2',
                          wizard_data.get('company_name') + ':' + 'Commission Sales',
                          head)
        date_head = workbook.add_format({'align': 'center', 'bold': True,
                                         'font_size': '10px'})

        sheet.merge_range('A3:D3', ' Products: ' + ', '.join(
            [lt or '' for lt in
             wizard_data['product_records']]),
                          date_head)

        if wizard_data.get('date_from_filter') and wizard_data.get('date_to_filter'):
            sheet.merge_range('E3:F3', 'From: ' + wizard_data.get('date_from_filter'),
                              date_head)

            sheet.merge_range('G3:H3', 'To: ' + wizard_data.get('date_to_filter'),
                              date_head)

        sheet.merge_range('A5:E5', 'Company Name', sub_heading_sub)
        sheet.merge_range('F5:H5', 'Commission ( % )', sub_heading_sub)

        row = 4
        col = 0

        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 36)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)

        for report in report_data[0]:

            row += 1
            sheet.merge_range(row, col + 0, row, col + 4, report['partner_name'],
                              sub_heading_sub)
            sheet.merge_range(row, col + 5, row, col + 7, report['commission_percentage'], sub_heading_sub)
            row += 1
            sheet.write(row, col + 0, 'Entry Label', cell_format)
            sheet.write(row, col + 1, 'Invoice Date', cell_format)
            sheet.write(row, col + 2, 'IR', cell_format)
            sheet.write(row, col + 3, 'Product', cell_format)
            sheet.write(row, col + 4, 'QTY', cell_format)
            sheet.write(row, col + 5, 'Sales Price', cell_format)
            sheet.write(row, col + 6, 'Amount', cell_format)
            sheet.write(row, col + 7, 'Commission', cell_format)
            for r_rec in report['child_lines']:
                row += 1
                sheet.write(row, col + 0, r_rec['move'], txt)
                sheet.write(row, col + 1, r_rec['invoice_date'], txt)
                sheet.write(row, col + 2, r_rec['internal_reference'], txt)
                sheet.write(row, col + 3, r_rec['product_name'], txt)
                sheet.write(row, col + 4, r_rec['invoice_quantity'], txt)
                sheet.write(row, col + 5, r_rec['list_price'], txt)
                sheet.write(row, col + 6, r_rec['amount'], txt)
                sheet.write(row, col + 7, r_rec['commission_amount'], txt)
            if report['total_lines']:
                row += 1
                sheet.merge_range(row, col + 0, row, col + 3, 'Total Sales : ' + report['total_lines']['partner_name'],
                                  sub_heading_sub)
                sheet.write(row, col + 4, report['total_lines']['total_qty_sold'], sub_heading_sub)
                sheet.write(row, col + 5, '', sub_heading_sub)
                sheet.write(row, col + 6, report['total_lines']['line_amount_total'], sub_heading_sub)
                sheet.write(row, col + 7, report['total_lines']['commission_amount_total'], sub_heading_sub)

        if report_data[2]:
            row += 2
            sheet.merge_range(row, col + 0, row, col + 3, 'Total Sales : ',
                              sub_heading_sub)
            sheet.write(row, col + 4, report_data[2][0]['all_qty_total'], sub_heading_sub)
            sheet.write(row, col + 5, '', sub_heading_sub)
            sheet.write(row, col + 6, report_data[2][0]['line_all_total'], sub_heading_sub)
            sheet.write(row, col + 7, report_data[2][0]['all_commission_total'], sub_heading_sub)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


class ProductCommissionReport(models.TransientModel):
    _inherit = "account.common.report"
    _name = 'account.commission.wizard'

    def _default_customers(self):
        lines = [(5, 0, 0)]
        partner_ids = self.env['res.partner'].search([]).filtered(lambda x: x.company_type == 'company')
        for rec in partner_ids:
            vals = {'partner_id': rec}
            lines.append((0, 0, vals))
        return lines

    report_name = fields.Char('Report Name')

    date_from_filter = fields.Date(string='Date From')
    date_to_filter = fields.Date(string='Date To')
    commission_value = fields.Float('Commission ( % )', default=0.0)
    group_view = fields.Boolean()
    product_view = fields.Boolean()
    onchange_field = fields.Boolean()

    add_report_product_ids = fields.Many2many('product.product', required=True)

    commission_customer_line_ids = fields.One2many('commission.customer.line', 'wizard_id',
                                                   default=_default_customers)
    deduct_product_line_ids = fields.One2many('product.commission.deduct', 'wizard_id')

    def view_wizard(self):
        history_data = self._prepare_history_data()
        self.env['account.commission.wizard.history'].create(history_data)
        return {
            'name': "Commission Sales Report",
            'type': 'ir.actions.client',
            'tag': 'p_c',
        }

    def _prepare_move_line_default_vals(self):
        return [dict(partner_id=data.partner_id.id, company_name=data.company_name, commission=data.commission) for
                data in
                self.commission_customer_line_ids]

    def _prepare_deduct_line_vals(self):
        return [dict(product_id=data.product_id.id, deduct_amount=data.deduct_amount) for data in
                self.deduct_product_line_ids]

    def _prepare_history_data(self):
        history_data = {
            'report_name': self.report_name,
            'wizard_id': self.id,
            'date_from_filter': self.date_from_filter,
            'date_to_filter': self.date_to_filter,
            'commission_value': self.commission_value,
            'add_report_product_ids': self.add_report_product_ids,
            'commission_customer_line_ids': [(5, 0)] + [(0, 0, line_vals) for line_vals in
                                                        self._prepare_move_line_default_vals()],
            'deduct_product_line_ids': [(5, 0)] + [(0, 0, deduct_vals) for deduct_vals in
                                                   self._prepare_deduct_line_vals()],
        }
        return history_data

    @api.onchange('onchange_field')
    def _onchange_report_data(self):
        history = self.env['account.commission.wizard.history'].search([])[-1] if len(
            self.env['account.commission.wizard.history'].search([])) >= 1 else None
        if history:
            self.report_name = history.report_name
            self.date_from_filter = history.date_from_filter
            self.date_to_filter = history.date_to_filter
            self.commission_value = history.commission_value
            self.add_report_product_ids = history.add_report_product_ids
            if history.commission_customer_line_ids:
                commission_list = [
                    dict(partner_id=data.partner_id.id, company_name=data.company_name, commission=data.commission)
                    for
                    data in
                    history.commission_customer_line_ids]
                self.commission_customer_line_ids = [(5, 0)] + [(0, 0, line_vals) for line_vals in
                                                                commission_list]

            if history.deduct_product_line_ids:
                deduct_list = [dict(product_id=data.product_id.id, deduct_amount=data.deduct_amount) for data in
                               history.deduct_product_line_ids]

                self.deduct_product_line_ids = [(5, 0)] + [(0, 0, deduct_vals) for deduct_vals in
                                                           deduct_list]

    def edit_customer_lines(self):
        self.ensure_one()
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.commission.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': 'Dynamic Reports',
            'target': 'new',
        }

    def customer_update(self):
        if self.commission_value:
            for record in self.commission_customer_line_ids:
                record.write({'commission': self.commission_value})
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.commission.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': 'Dynamic Reports',
            'target': 'new',
        }

    def customer_edit(self):
        if not self.group_view:
            self.group_view = True

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.commission.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': 'Dynamic Reports',
            'target': 'new',
        }

    def customer_edit_back(self):
        if self.group_view:
            self.group_view = False
        if self.product_view:
            self.product_view = False

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.commission.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': 'Dynamic Reports',
            'target': 'new',
        }

    def product_edit(self):
        if not self.product_view:
            self.product_view = True

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.commission.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': 'Dynamic Reports',
            'target': 'new',
        }
