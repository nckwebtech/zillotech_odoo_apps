from odoo import fields, models


class RealEstatePlace(models.Model):
    _inherit = 'product.template'

    def _default_country(self):
        return self.env['res.country'].search([('name', 'ilike', 'United States')])

    def _default_state(self):
        return self.env['res.country.state'].search([('name', 'ilike', 'Kansas'), ('code', 'ilike', 'KS')])

    detailed_type = fields.Selection(selection_add=[('real_estate', 'Real-Estate')], tracking=True,
                                     ondelete={'real_estate': 'set consu'})
    type = fields.Selection(selection_add=[
        ('real_estate', 'Real-Estate')
    ], ondelete={'real_estate': 'set consu'})

    owners_f_name = fields.Char('Owner First Name')
    owners_l_name = fields.Char('Owner Last Name')
    # address section
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]", default=_default_state)
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',
                                 default=_default_country)
    beds = fields.Integer('Beds')
    bath = fields.Integer('Baths')
    house_sq = fields.Char('House Sq Foot')
    lot_size = fields.Char('Lot Size')
    lot_features_ids = fields.Many2many('lot.feature', 'lot_feature_ref', string='Lot Features')
    property_type = fields.Char('Property Type')
    age_of_home = fields.Char('Age of Home')
    stories = fields.Char('Stories')
    garage = fields.Char('Garage')
    heating_cooling_ids = fields.Many2many('heating.cooling', 'heating_cooling_ref', string='Heating and Cooling')
    exterior_condition = fields.Char('Exterior Condition')
    roofing = fields.Char('Roofing')
    indor_amenities_ids = fields.Many2many('indoor.amenities', 'indoor_amenities_ref', string='Indoor Amenities')
    outdoor_amenities_ids = fields.Many2many('outdoor.amenities', 'outdoor_amenities_ref', string='Outdoor Amenities')
    listing_msg = fields.Char('Listing Message', size=250)
    main_img_ids = fields.Many2many('ir.attachment', 'main_img_attachment_rel', 'main_img_id',
                                    'attachment_id', 'Upload Images',
                                    help="You may attach files to this template")
    place_description = fields.Html('Description')

    def _detailed_type_mapping(self):
        type_mapping = super()._detailed_type_mapping()
        type_mapping['real_estate'] = 'product'
        return type_mapping

    def action_print_catalog_real(self):
        return self.env.ref('zillotech_real_estate.action_inventory_product_real_report').report_action(self)
