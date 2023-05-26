from odoo import models, _


class ResPartnerData(models.Model):
    _inherit = 'res.partner'

    def action_show_export_wizard(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Export Customer Pricelist'),
                'res_model': 'list.export.wizard',
                'target': 'new',
                'view_id': self.env.ref('nck_pricelist_export.wizard_form_list_export_wizard').id,
                'view_mode': 'form',
                'context': {'default_customer_ids': self.ids}
                }


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    def action_show_pricelist_export_wizard(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Export Pricelist'),
                'res_model': 'pricelist.export.wizard',
                'target': 'new',
                'view_id': self.env.ref('nck_pricelist_export.wizard_form_pricelist_export_wizard').id,
                'view_mode': 'form',
                'context': {'default_pricelist_ids': self.ids}
                }
