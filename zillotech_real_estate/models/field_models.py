from odoo import fields, models


class RealEstateFieldFeatureModels(models.Model):
    _name = 'lot.feature'
    _rec_name = 'feature_name'
    _description = "Lot"

    feature_name = fields.Char('Lot Feature')


class RealEstateFieldHCModels(models.Model):
    _name = 'heating.cooling'
    _rec_name = 'heating_cooling_type'
    _description = "heating"

    heating_cooling_type = fields.Char('Heating and Cooling')


class RealEstateFieldIAModels(models.Model):
    _name = 'indoor.amenities'
    _rec_name = 'indoor_amenities_type'
    _description = "indoor"

    indoor_amenities_type = fields.Char('Indoor Amenities')


class RealEstateFieldOAModels(models.Model):
    _name = 'outdoor.amenities'
    _rec_name = 'outdoor_amenities_type'
    _description = "outdoor"

    outdoor_amenities_type = fields.Char('Outdoor Amenities')
