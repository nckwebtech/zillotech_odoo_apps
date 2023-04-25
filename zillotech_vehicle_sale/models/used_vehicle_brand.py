from odoo import fields, models


class UsedVehicleModelBrand(models.Model):
    _name = 'used.vehicle.model.brand'
    _description = 'Brand of the vehicle'
    _order = 'name asc'

    name = fields.Char('Make', required=True)
    image_128 = fields.Image("Logo", max_width=128, max_height=128)


class UsedVehicleExteriorColor(models.Model):
    _name = 'used.vehicle.exterior.color'
    _description = 'Exterior Color of the Vehicle'
    _order = 'exterior_color asc'
    _rec_name = 'exterior_color'

    exterior_color = fields.Char('Exterior Color')


class UsedVehicleInteriorColor(models.Model):
    _name = 'used.vehicle.interior.color'
    _description = 'Interior Color of the Vehicle'
    _order = 'interior_color asc'
    _rec_name = 'interior_color'

    interior_color = fields.Char('Interior Color')


class UsedVehicleType(models.Model):
    _name = 'used.vehicle.type'
    _description = 'Type of the vehicle'
    _order = 'vehicle_type asc'
    _rec_name = 'vehicle_type'

    vehicle_type = fields.Char('Vehicle Type')


class UsedVehicleCondition(models.Model):
    _name = 'used.vehicle.condition'
    _description = 'Condition of the Vehicle'
    _order = 'vehicle_condition asc'
    _rec_name = 'vehicle_condition'

    vehicle_condition = fields.Char('Vehicle Condition')
