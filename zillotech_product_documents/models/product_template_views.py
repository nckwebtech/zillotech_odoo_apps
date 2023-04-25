from odoo import models, fields, api


class ProductDocumentTree(models.Model):
    _name = 'product.documents'
    _rec_name = 'doc_category'
    _description = "Product Document"

    doc_category = fields.Char('Document Category', required=True)
    attachment_ids = fields.Many2many('ir.attachment', 'product_document_attachment_rel', 'product_document_id',
                                      'attachment_id', 'Upload Documents',
                                      help="You may attach files to this template")
    compute_field = fields.Boolean(string="check field", compute='_compute_get_user')

    def _compute_get_user(self):
        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('zillotech_product_documents.group_users_access') and not res_user.has_group(
                'zillotech_product_documents.group_admin_access'):
            self.compute_field = True
        else:
            self.compute_field = False


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    product_document_only_ids = fields.Many2many('product.documents', 'product_document_rel', 'product_template_id',
                                                 'doc_category_id', string='Document Category')
    page_product_doc_hide = fields.Boolean(compute='_compute_page_invoice_product_hide', string='Page Field')
    compute_field = fields.Boolean(string="check field", compute='_compute_get_template_user')

    @api.onchange('purchase_ok')
    def _compute_get_template_user(self):
        """compute for product documents in product page"""
        if not self.page_product_doc_hide:
            res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
            if res_user.has_group('zillotech_product_documents.group_users_access') and not res_user.has_group(
                    'zillotech_product_documents.group_admin_access'):
                self.compute_field = True
            else:
                self.compute_field = False
        else:
            self.compute_field = False

    @api.onchange('purchase_ok')
    def _compute_page_invoice_product_hide(self):
        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if not res_user.has_group('zillotech_product_documents.group_users_access') and not res_user.has_group(
                'zillotech_product_documents.group_admin_access'):
            self.page_product_doc_hide = True
        else:
            self.page_product_doc_hide = False
