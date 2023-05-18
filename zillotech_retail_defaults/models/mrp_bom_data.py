from odoo import fields, models, api, _


class MrpProductInherited(models.Model):
    _inherit = "mrp.production"

    mrp_product_image = fields.Image(string="Image")
    print_mrp_product_image = fields.Boolean(string="Print Product Image")

    mrp_product_image_size = fields.Selection([
        ('sm', 'Small'),
        ('md', 'Medium'),
        ('lg', 'Large'),
    ], default='sm', string="Print Image Size")

    def _compute_mrp_product_image(self):
        for rec in self:
            rec.mrp_product_image = rec.product_id.image_128 if rec.product_id.image_128 else False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(MrpProductInherited, self)._onchange_product_id()
        for rec in self:
            rec.mrp_product_image = rec.product_id.image_128 if rec else False
        return res


class StockMoveInherited(models.Model):
    _inherit = "stock.move"

    stock_mv_product_img = fields.Image(
        string="Image", compute='_compute_stock_mv_product_img')

    def _compute_stock_mv_product_img(self):
        for rec in self:
            rec.stock_mv_product_img = rec.product_id.image_128 if rec.product_id.image_128 else False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(StockMoveInherited, self)._onchange_product_id()
        for rec in self:
            rec.stock_mv_product_img = rec.product_id.image_128 if rec else False
        return res


class MrpBomInherited(models.Model):
    _inherit = "mrp.bom"

    print_bom_product_image = fields.Boolean(string="Print Product Image")

    bom_product_image_size = fields.Selection([
        ('sm', 'Small'),
        ('md', 'Medium'),
        ('lg', 'Large'),
    ], default='sm', string="Print Image Size")


class BomLineInherited(models.Model):
    _inherit = "mrp.bom.line"

    bom_line_product_img = fields.Image(
        string="Image", compute='_compute_bom_line_product_img')

    def _compute_bom_line_product_img(self):
        for rec in self:
            rec.bom_line_product_img = rec.product_id.image_128 if rec else False

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(BomLineInherited, self).onchange_product_id()
        for rec in self:
            rec.bom_line_product_img = rec.product_id.image_128 if rec else False
        return res


class BomStructureReportInherited(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components = []
        total = 0
        for line in bom.bom_line_ids:
            line_quantity = (
                                    bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            price = line.product_id.uom_id._compute_price(
                line.product_id.standard_price, line.product_uom_id) * line_quantity
            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(
                    line_quantity, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_total = self._get_price(line.child_bom_id, factor)
            else:
                sub_total = price
            sub_total = self.env.user.company_id.currency_id.round(sub_total)
            print(line.bom_line_product_img)
            components.append({
                'prod_image': line.bom_line_product_img,
                'prod_id': line.product_id.id,
                'prod_name': line.product_id.display_name,
                'code': line.child_bom_id and self._get_bom_reference(line.child_bom_id) or '',
                'prod_qty': line_quantity,
                'prod_uom': line.product_uom_id.name,
                'prod_cost': self.env.user.company_id.currency_id.round(price),
                'parent_id': bom.id,
                'line_id': line.id,
                'level': level or 0,
                'total': sub_total,
                'child_bom': line.child_bom_id.id,
                'phantom_bom': line.child_bom_id and line.child_bom_id.type == 'phantom' or False,
                'attachments': self.env[
                    'mrp.document'
                ].search(['|', '&',
                          ('res_model', '=', 'product.product'),
                          ('res_id', '=', line.product_id.id), '&',
                          ('res_model', '=', 'product.template'),
                          ('res_id', '=', line.product_id.product_tmpl_id.id)]
                         ),

            })
            total += sub_total
        return components, total

    def _get_pdf_line(self, bom_id, product_id=False, qty=1, child_bom_ids=[], unfolded=False):

        data = self._get_bom(
            bom_id=bom_id, product_id=product_id, line_qty=qty)

        def get_sub_lines(bom, product_id, line_qty, line_id, level):
            data = self._get_bom(bom_id=bom.id, product_id=product_id,
                                 line_qty=line_qty, line_id=line_id, level=level)
            bom_lines = data['components']
            lines = []
            for bom_line in bom_lines:

                lines.append({
                    'prod_image': bom_line['prod_image'],
                    'name': bom_line['prod_name'],
                    'type': 'bom',
                    'quantity': bom_line['prod_qty'],
                    'uom': bom_line['prod_uom'],
                    'prod_cost': bom_line['prod_cost'],
                    'bom_cost': bom_line['total'],
                    'level': bom_line['level'],
                    'code': bom_line['code']
                })
                if bom_line['child_bom'] and (unfolded or bom_line['child_bom'] in child_bom_ids):
                    line = self.env['mrp.bom.line'].browse(bom_line['line_id'])
                    lines += (get_sub_lines(line.child_bom_id, line.product_id,
                                            line.product_qty * data['bom_qty'], line, level + 1))
            if data['operations']:
                lines.append({
                    'name': _('Operations'),
                    'type': 'operation',
                    'quantity': data['operations_time'],
                    'uom': _('minutes'),
                    'bom_cost': data['operations_cost'],
                    'level': level,
                })
                for operation in data['operations']:
                    if unfolded or 'operation-' + str(bom.id) in child_bom_ids:
                        lines.append({
                            'name': operation['name'],
                            'type': 'operation',
                            'quantity': operation['duration_expected'],
                            'uom': _('minutes'),
                            'bom_cost': operation['total'],
                            'level': level + 1,
                        })
            return lines

        bom = self.env['mrp.bom'].browse(bom_id)
        product = product_id or bom.product_id or bom.product_tmpl_id.product_variant_id
        pdf_lines = get_sub_lines(bom, product, qty, False, 1)
        data['components'] = []
        data['lines'] = pdf_lines
        return data
