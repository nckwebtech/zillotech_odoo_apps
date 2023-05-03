from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_nck_usa_sale_tax_table = fields.Boolean(string="USA Sales Tax Table")

    @api.onchange('module_nck_usa_sale_tax_table')
    def _onchange_sale_table(self):
        if self.module_nck_usa_sale_tax_table is True:
            if self.group_sale_delivery_address is False or self.module_delivery is False:
                self.group_sale_delivery_address = True
                self.module_delivery = True
        else:
            self.group_sale_delivery_address = False
            self.module_delivery = False
