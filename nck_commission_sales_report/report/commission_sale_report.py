from odoo import api, models, _


class CommissionSales(models.AbstractModel):
    _name = 'report.nck_commission_sales_report.commission_sales'

    @api.model
    def _get_report_values(self, docids, data=None):
        if self.env.context.get('commission_sales_pdf_report'):
            if data.get('report_data'):
                data.update(
                    {'account_data': data.get('report_data')['product_report_lines'][0],
                     'company': self.env.company,
                     'wizard_data': data.get('report_data')['wizard_data'],
                     'all_total': data.get('report_data')['product_report_lines'][2],
                     })

        return data
