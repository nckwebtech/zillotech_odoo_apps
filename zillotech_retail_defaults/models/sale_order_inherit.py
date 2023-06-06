from odoo import fields, models, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    third_party_billing = fields.Boolean('3rd Party Billing', default=False)


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _default_warehouse_id(self):
        print('_default_warehouse_id')
        # !!! Any change to the default value may have to be repercuted
        # on _init_column() below.
        return self.env.user._get_default_warehouse_id()

    third_party_billing = fields.Boolean(related='partner_id.third_party_billing', string='3rd Party Billing')
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id, check_company=True)


class PurchaseOrderLineRetail(models.Model):
    _inherit = "purchase.order.line"

    pl_product_image = fields.Image(string="Image", compute='_compute_purchase_product_image')

    def _compute_purchase_product_image(self):
        for rec in self:
            rec.pl_product_image = rec.product_id.image_128 if rec.product_id.image_128 else False

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLineRetail, self).onchange_product_id()
        for rec in self:
            rec.pl_product_image = rec.product_id.image_128 if rec else False
        return res


class PurchaseOrderRetail(models.Model):
    _inherit = "purchase.order"

    print_purchase_product_image = fields.Boolean(string="Print Product Image")

    purchase_product_image_size = fields.Selection([
        ('sm', 'Small'),
        ('md', 'Medium'),
        ('lg', 'Large'),
    ], default='sm', string="Print Image Size")
