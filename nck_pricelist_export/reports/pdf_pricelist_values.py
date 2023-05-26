from odoo import models, api


class CustomerPricelist(models.AbstractModel):
    _name = 'report.nck_pricelist_export.pdf_pricelist_report'
    _description = 'PDF pricelist report'

    @api.model
    def _get_report_values(self, docids, data=None):
        customer_list = self.env['list.export.wizard'].compute_list_data(data['customer_ids'])
        return {
            'customer_list': customer_list
        }


class PricelistExport(models.AbstractModel):
    _name = 'report.nck_pricelist_export.export_pdf_pricelist_report'
    _description = 'Export pricelist report'

    @api.model
    def _get_report_values(self, docids, data=None):
        pricelist_ids = self.env['pricelist.export.wizard'].compute_list_data(data['pricelist_ids'])
        return {
            'pricelist_ids': pricelist_ids
        }
