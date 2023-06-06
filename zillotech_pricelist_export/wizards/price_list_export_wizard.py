import base64
import os
import xlsxwriter
from odoo import fields, models, http
from datetime import datetime

from odoo.http import request, content_disposition


class PriceListExport(models.TransientModel):
    _name = "list.export.wizard"
    _description = "Price List Export"

    customer_ids = fields.Many2many('res.partner', string='Customers', readonly=True)
    attachment_id = fields.Many2one('ir.attachment', string='Attachment')

    def _price_list_pdf(self, customer_ids):
        return self.env.ref('zillotech_pricelist_export.action_pdf_pricelist_report').report_action(self, data={
            'customer_ids': customer_ids})

    def action_print_price_list(self):
        if self._context.get('type') == 'pdf':
            report = self._price_list_pdf(self._context.get('default_customer_ids'))
            return report
        else:
            customer_list = self.compute_list_data(self._context.get('default_customer_ids'))
            attachment_id = self._pricelist_excel_report(customer_list)
            self.attachment_id = attachment_id
            return {'type': 'ir.actions.act_url',
                    'url': '/web/binary/pricelist_report?rec_id=%s' % self.id,
                    'target': 'self',
                    'res_id': self.id,
                    }

    def compute_list_data(self, data):

        def _compute_price(product):
            return product.with_context(pricelist=price_list.id, quantity=max(min_qty), date=date_today,
                                        uom=product.uom_id.id).price

        def _compute_discount(product):
            price = product.list_price
            discount = price - (price - (price * line.percent_price / 100))
            return round(discount, 2)

        product_records = self.env['product.product'].search([])
        date_today = datetime.today()
        customer_list = []
        for customer in data:
            customer_dict = {}
            customer = self.env['res.partner'].browse(customer)
            price_list = customer.property_product_pricelist
            customer_dict['customer'] = customer
            customer_dict['pricelist_name'] = price_list.name
            price_rule_list = []
            if price_list.item_ids:
                for line in price_list.item_ids:
                    min_qty = [line.min_quantity]
                    rule_dict = {'rule_name': line.name}
                    if line.compute_price == 'percentage' and line.percent_price and line.applied_on == '3_global':
                        product_list = [dict(product=product, price=_compute_price(product),
                                             discount=line.percent_price or 0,
                                             discount_amount=_compute_discount(product)) for product in product_records]
                        rule_dict['product_list'] = product_list
                    elif line.compute_price == 'percentage' and line.percent_price and line.applied_on == '2_product_category':
                        product_list = []
                        for product in product_records:
                            if product.categ_id.id == line.categ_id.id:
                                product_dict = dict(product=product, price=_compute_price(product),
                                                    discount=line.percent_price or 0,
                                                    discount_amount=_compute_discount(product))
                                product_list.append(product_dict)
                            else:
                                product_dict = dict(product=product, price=_compute_price(product),
                                                    discount=0,
                                                    discount_amount=0.0)
                                product_list.append(product_dict)
                        rule_dict['product_list'] = product_list
                    elif line.compute_price == 'percentage' and line.percent_price and line.applied_on == '1_product':
                        product_list = []
                        for product in product_records:
                            if product.product_tmpl_id.id == line.product_tmpl_id.id:
                                product_dict = dict(product=product, price=_compute_price(product),
                                                    discount=line.percent_price or 0,
                                                    discount_amount=_compute_discount(product))
                                product_list.append(product_dict)
                            else:
                                product_dict = dict(product=product, price=_compute_price(product),
                                                    discount=0,
                                                    discount_amount=0.0)
                                product_list.append(product_dict)
                        rule_dict['product_list'] = product_list
                    else:
                        product_list = []
                        for product in product_records:
                            if product.id == line.product_id.id:
                                product_dict = dict(product=product, price=_compute_price(product),
                                                    discount=line.percent_price or 0,
                                                    discount_amount=_compute_discount(product))
                                product_list.append(product_dict)
                            else:
                                product_dict = dict(product=product, price=_compute_price(product),
                                                    discount=0,
                                                    discount_amount=0.0)
                                product_list.append(product_dict)
                        rule_dict['product_list'] = product_list
                    price_rule_list.append(rule_dict)
            else:
                product_list = []
                min_qty = [1]
                rule_dict = {'rule_name': False}
                for product in product_records:
                    product_dict = dict(product=product, price=_compute_price(product),
                                        discount=0,
                                        discount_amount=0)
                    print('eee', product_dict)
                    product_list.append(product_dict)
                rule_dict['product_list'] = product_list
                price_rule_list.append(rule_dict)

            customer_dict['price_rule_list'] = price_rule_list
            customer_list.append(customer_dict)
        return customer_list

    def _pricelist_excel_report(self, customer_list):
        destination_folder = os.path.dirname(__file__) + "/odoo_xlsx"
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        file_name = 'Pricelist Report of Customers.xlsx'
        file_content_name = os.path.join(destination_folder, file_name)
        workbook = xlsxwriter.Workbook(file_content_name)
        cell_format = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px',
             'border': 1,
             'border_color': 'black'})
        for r_rec in customer_list:
            sheet = workbook.add_worksheet('%s' % r_rec['customer'].name)
            txt = workbook.add_format({'font_size': '10px', 'border': 1})
            sub_heading_sub = workbook.add_format({'align': 'center', 'bold': True,
                                                   'border': 1
                                                   }
                                                  )
            date_head = workbook.add_format({'align': 'center', 'bold': True,
                                             'font_size': '10px'})

            sheet.merge_range('A3:B3', ' Partner: ' + r_rec['customer'].name,
                              date_head)

            sheet.merge_range('E3:F3', 'Price List: ' + r_rec['pricelist_name'],
                              date_head)
            row = 4
            col = 0
            sheet.set_column(0, 0, 25)
            sheet.set_column(1, 1, 25)
            sheet.set_column(2, 2, 15)
            sheet.set_column(3, 3, 15)
            sheet.set_column(4, 4, 15)
            sheet.set_column(5, 5, 15)

            for rule_rec in r_rec['price_rule_list']:
                row += 1
                if rule_rec['rule_name']:
                    sheet.merge_range(row, col + 0, row, col + 5, 'Price Rule : ' + rule_rec['rule_name'],
                                      sub_heading_sub)
                    row += 1
                sheet.write(row, col + 0, 'Name', cell_format)
                sheet.write(row, col + 1, 'Internal Reference', cell_format)
                sheet.write(row, col + 2, 'Sales Price', cell_format)
                sheet.write(row, col + 3, 'Pricelist Price', cell_format)
                sheet.write(row, col + 4, 'Discount(%)', cell_format)
                sheet.write(row, col + 5, 'Discount Amount', cell_format)

                for product_rec in rule_rec['product_list']:
                    row += 1
                    sheet.write(row, col + 0, product_rec['product'].name, txt)
                    sheet.write(row, col + 1, product_rec['product'].default_code, txt)
                    sheet.write(row, col + 2, product_rec['product'].list_price, txt)
                    sheet.write(row, col + 3, product_rec['price'], txt)
                    sheet.write(row, col + 4, product_rec['discount'], txt)
                    sheet.write(row, col + 5, product_rec['discount_amount'], txt)
        workbook.close()
        files = base64.b64encode(open(file_content_name, 'rb').read())
        attachment_id = self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': files,
        })
        os.remove(file_content_name)
        return attachment_id


class BinaryZipReport(http.Controller):
    @http.route('/web/binary/pricelist_report', type='http', auth="public")
    def download_function_pricelist_report(self, **kwargs):
        rec_id = int(kwargs.get('rec_id'))
        data = request.env['list.export.wizard'].browse(rec_id)
        if data.attachment_id:
            file_content = base64.b64decode(data.attachment_id.datas)
            file_name = data.attachment_id.name if data.attachment_id.name else 'pricelist_report.xlsx'
            unlink_attachments = [(2, line.id) for line in data.attachment_id]
            data.write({'attachment_id': unlink_attachments})
            if not file_content:
                return request.not_found()
            else:
                if file_name:
                    return request.make_response(file_content,
                                                 [('Content-Type', 'application/octet-stream'),
                                                  ('Content-Disposition', content_disposition(file_name))])
