from odoo import fields, api, models


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    page_sale_product_hide = fields.Boolean(compute='_compute_page_sale_product_hide', string='Page Field')
    product_sale_compute_field = fields.Boolean(compute='_compute_get_user_product', string="check field")
    sale_order_product_document_ids = fields.Many2many('product.documents', 'sale_product_document_rel',
                                                       'sale_product_template_id',
                                                       'doc_category_id', string='Document Category',
                                                       compute='_compute_product_document_sale')

    @api.onchange('partner_id')
    def _compute_page_sale_product_hide(self):
        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if not res_user.has_group('zillotech_product_documents.group_users_access') and not res_user.has_group(
                'zillotech_product_documents.group_admin_access'):
            self.page_sale_product_hide = True
        else:
            self.page_sale_product_hide = False

    @api.onchange('partner_id')
    def _compute_get_user_product(self):
        if not self.page_sale_product_hide:
            res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
            if res_user.has_group('zillotech_product_documents.group_users_access') and not res_user.has_group(
                    'zillotech_product_documents.group_admin_access'):
                self.product_sale_compute_field = True
            else:
                self.product_sale_compute_field = False
        else:
            self.product_sale_compute_field = False

    @api.onchange('order_line')
    def _compute_product_document_sale(self):
        """compute for product documents in sales page"""
        if not self.page_sale_product_hide:
            lines = []
            if self.order_line:
                for rec in self.order_line:
                    for line in rec.product_id.product_document_only_ids:
                        lines.append(line.id)
                self.sale_order_product_document_ids = self.env['product.documents'].browse(lines)
            else:
                self.sale_order_product_document_ids = False
        else:
            self.sale_order_product_document_ids = False


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    product_invoice_compute_field = fields.Boolean(compute='_compute_get_user_invoice', string="check field")
    page_invoice_product_hide = fields.Boolean(compute='_compute_page_invoice_product_hide', string='Page Field')
    invoice_line_product_document_ids = fields.Many2many('product.documents', 'account_move_product_document_rel',
                                                         'account_move_product_template_id',
                                                         'doc_category_id', string='Document Category',
                                                         compute='_compute_product_document_account')

    @api.onchange('partner_id')
    def _compute_get_user_invoice(self):
        if not self.page_invoice_product_hide:
            res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
            if res_user.has_group('zillotech_product_documents.group_users_access') and not res_user.has_group(
                    'zillotech_product_documents.group_admin_access'):
                self.product_invoice_compute_field = True
            else:
                self.product_invoice_compute_field = False
        else:
            self.product_invoice_compute_field = False

    @api.onchange('partner_id')
    def _compute_page_invoice_product_hide(self):
        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if not res_user.has_group('zillotech_product_documents.group_users_access') and not res_user.has_group(
                'zillotech_product_documents.group_admin_access'):
            self.page_invoice_product_hide = True
        else:
            self.page_invoice_product_hide = False

    @api.onchange('invoice_line_ids')
    def _compute_product_document_account(self):
        """compute for product documents in invoice page"""
        if not self.page_invoice_product_hide:
            lines = []
            if self.invoice_line_ids:
                for rec in self.invoice_line_ids:
                    for line in rec.product_id.product_document_only_ids:
                        lines.append(line.id)
                self.invoice_line_product_document_ids = self.env['product.documents'].browse(lines)
            else:
                self.invoice_line_product_document_ids = False
        else:
            self.invoice_line_product_document_ids = False
