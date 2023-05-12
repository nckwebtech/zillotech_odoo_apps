from odoo import fields, api, models


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    page_purchase_product_hide = fields.Boolean(compute='_compute_page_purchase_product_hide', string='Page Field')
    product_purchase_compute_field = fields.Boolean(compute='_compute_get_user_product_purchase', string="check field")
    purchase_order_product_document_ids = fields.Many2many('product.documents', 'purchase_product_document_rel',
                                                           'purchase_product_template_id',
                                                           'doc_category_id', string='Document Category',
                                                           domain="[('id', '=', False)]",
                                                           compute='_compute_product_document_purchase')

    @api.onchange('partner_id')
    def _compute_page_purchase_product_hide(self):
        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if not res_user.has_group('zillotech_product_documents.group_users_access') and not res_user.has_group(
                'zillotech_product_documents.group_admin_access'):
            self.page_purchase_product_hide = True
        else:
            self.page_purchase_product_hide = False

    @api.onchange('partner_id')
    def _compute_get_user_product_purchase(self):
        if not self.page_purchase_product_hide:
            res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
            if res_user.has_group('zillotech_product_documents.group_users_access') and not res_user.has_group(
                    'zillotech_product_documents.group_admin_access'):
                self.product_purchase_compute_field = True
            else:
                self.product_purchase_compute_field = False
        else:
            self.product_purchase_compute_field = False

    @api.onchange('order_line')
    def _compute_product_document_purchase(self):
        """compute for product documents in purchase page"""
        if not self.page_purchase_product_hide:
            lines = []
            if self.order_line:
                for rec in self.order_line:
                    for line in rec.product_id.product_document_only_ids:
                        lines.append(line.id)
                self.purchase_order_product_document_ids = self.env['product.documents'].browse(lines)
        else:
            self.purchase_order_product_document_ids = False