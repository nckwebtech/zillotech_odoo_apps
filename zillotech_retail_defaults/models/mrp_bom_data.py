from odoo import fields, models, api, _


class MrpProductInherited(models.Model):
    _inherit = "mrp.production"

    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', readonly=False)
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

    @api.model
    def _get_bom_array_lines(self, data, level, unfolded_ids, unfolded, parent_unfolded=True):
        bom_lines = data['components']
        lines = []
        for bom_line in bom_lines:
            line_unfolded = ('bom_' + str(bom_line['index'])) in unfolded_ids
            line_visible = level == 1 or unfolded or parent_unfolded
            lines.append({
                'bom_id': bom_line['bom_id'],
                'name': bom_line['name'],
                'type': bom_line['type'],
                'quantity': bom_line['quantity'],
                'quantity_available': bom_line['quantity_available'],
                'quantity_on_hand': bom_line['quantity_on_hand'],
                'producible_qty': bom_line.get('producible_qty', False),
                'uom': bom_line['uom_name'],
                'prod_cost': bom_line['prod_cost'],
                'bom_cost': bom_line['bom_cost'],
                'route_name': bom_line['route_name'],
                'route_detail': bom_line['route_detail'],
                'lead_time': bom_line['lead_time'],
                'level': bom_line['level'],
                'code': bom_line['code'],
                'availability_state': bom_line['availability_state'],
                'availability_display': bom_line['availability_display'],
                'visible': line_visible,
                'prod_image': bom_line['product'].image_128,
            })
            if bom_line.get('components'):
                lines += self._get_bom_array_lines(bom_line, level + 1, unfolded_ids, unfolded, line_visible and line_unfolded)

        if data['operations']:
            lines.append({
                'name': _('Operations'),
                'type': 'operation',
                'quantity': data['operations_time'],
                'uom': _('minutes'),
                'bom_cost': data['operations_cost'],
                'level': level,
                'visible': parent_unfolded,
            })
            operations_unfolded = unfolded or (parent_unfolded and ('operations_' + str(data['index'])) in unfolded_ids)
            for operation in data['operations']:
                lines.append({
                    'name': operation['name'],
                    'type': 'operation',
                    'quantity': operation['quantity'],
                    'uom': _('minutes'),
                    'bom_cost': operation['bom_cost'],
                    'level': level + 1,
                    'visible': operations_unfolded,
                })
        if data['byproducts']:
            lines.append({
                'name': _('Byproducts'),
                'type': 'byproduct',
                'uom': False,
                'quantity': data['byproducts_total'],
                'bom_cost': data['byproducts_cost'],
                'level': level,
                'visible': parent_unfolded,
            })
            byproducts_unfolded = unfolded or (parent_unfolded and ('byproducts_' + str(data['index'])) in unfolded_ids)
            for byproduct in data['byproducts']:
                lines.append({
                    'name': byproduct['name'],
                    'type': 'byproduct',
                    'quantity': byproduct['quantity'],
                    'uom': byproduct['uom_name'],
                    'prod_cost': byproduct['prod_cost'],
                    'bom_cost': byproduct['bom_cost'],
                    'level': level + 1,
                    'visible': byproducts_unfolded,
                })
        return lines
