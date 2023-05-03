import urllib.parse
from odoo import models, fields, api
import requests
import datetime
import xml.etree.ElementTree as ET


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def fetch_tax_datas(self, values):
        Returndata = {
            "Title": "Kansas Sales Tax Lookup",
            "calculationresult": 0,
            "abc1": "Kansas Sales Tax Lookup"
        }

        defaultSalesTaxRate = 7.3
        dtPaymentDate = datetime.date.today().strftime('%m/%d/%y')  # "#DateFormat(now(),"mm/dd/yyyy")#";
        encodedAddress = urllib.parse.urlencode({'strAddress': values['address']})
        intZipPlus = "5555"
        taxUrl = "https://wsdl.kssst.kdor.ks.gov/jurisdictionlookup.asmx/GetFIPSByAddress2?" + encodedAddress + "&strCityName=" + \
                 values['city'] + "&intZipCode=" + values[
                     'zip'] + "&intZipPlus=" + intZipPlus + "&dtPaymentDate=" + dtPaymentDate
        response = requests.get(taxUrl)
        defaultSalesTax = 1
        if response.status_code == 200:
            data = response.content
            Formated_XML = ET.fromstring(data)
            if Formated_XML[0].text != '3':
                if Formated_XML[0].text == '2':
                    Returndata["strReturnShortDesc"] = "Zipcode does not match, So using default zipcode"
                defaultSalesTax = 0
                taxRate = defaultSalesTax
                TLookUpResults = Formated_XML.findall('FIPSRecordList/TFIPSRecord')
                for item in TLookUpResults:
                    taxRate = taxRate + float(item.find("strGeneralTaxRateIntrastate").text)
                Returndata["taxRateDetailing"] = TLookUpResults
                Returndata["totalTax"] = taxRate
        Returndata["address"] = values['address']
        Returndata["city"] = values["city"]
        Returndata["state"] = values["state"]
        Returndata["zip"] = values["zip"]
        Returndata["defaultSalesTaxRate"] = defaultSalesTaxRate
        Returndata["defaultSalesTax"] = defaultSalesTax
        Returndata["calculation_result"] = 1
        return Returndata

    @api.onchange('partner_shipping_id')
    def _onchange_partner_destination_address(self):
        data = self.env['tax.table'].search([('state_id', '=', self.partner_shipping_id.state_id.id)], limit=1)
        if data.live_tax_id:
            data.live_tax_id = False
        if self.partner_shipping_id:
            data = self.env['tax.table'].search_read([('state_id', '=', self.partner_shipping_id.state_id.id)],
                                                     ['destination_tax'], limit=1)
            if data and data[0]['destination_tax'] == 'yes':
                if self.partner_shipping_id and self._origin.partner_shipping_id != self.partner_shipping_id:
                    self.show_kansas_tax_button = True
                else:
                    self.show_kansas_tax_button = False
            else:
                self.show_kansas_tax_button = False

    def update_destination_tax(self):
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
                tax_rate = self.fetch_tax_datas(values)
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
                        temp_data = data.tax
                        data.sales_tax_id = tax_rate_data
                        data.live_tax_id = tax_rate_data
                        self._onchange_partner_shipping()
                        data.sales_tax_id = self.env['account.tax'].browse(temp_data)
                    else:
                        temp_data = data.tax
                        data.sales_tax_id = tax_rate_data
                        data.live_tax_id = tax_rate_data
                        self._onchange_partner_shipping()
                        data.sales_tax_id = self.env['account.tax'].browse(temp_data)

    show_kansas_tax_button = fields.Boolean('Show Kansas tax', default=False)


class TaxTableInherit(models.Model):
    _inherit = "tax.table"

    destination_tax = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Use Kansas Destination Sales Tax',
                                       default='no',
                                       required=True)

    live_tax_id = fields.Many2one('account.tax', string="Sales Tax", help='Add your Sale Tax here !',
                                  ondelete='cascade')

    live_tax_invoice_id = fields.Many2one('account.tax', string="Invoice Tax", help='Invoice Tax !',
                                          ondelete='cascade')

    tax = fields.Integer(related='sales_tax_id.id')


class LiveTaxForCustomer(models.Model):
    _inherit = 'res.partner'

    live_tax_invoice_id = fields.Many2one('account.tax', string="Invoice Tax", help='Invoice Tax !', ondelete='cascade')

    live_tax_history_id = fields.Many2one('account.tax', string="History Tax", help='Invoice Tax !', ondelete='cascade')
