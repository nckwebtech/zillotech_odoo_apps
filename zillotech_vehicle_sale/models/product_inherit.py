from odoo import fields, models, api

FUEL_TYPES = [
    ('diesel', 'Diesel'),
    ('gasoline', 'Gasoline'),
    ('hybrid', 'Hybrid Diesel'),
    ('full_hybrid_gasoline', 'Hybrid Gasoline'),
    ('plug_in_hybrid_diesel', 'Plug-in Hybrid Diesel'),
    ('plug_in_hybrid_gasoline', 'Plug-in Hybrid Gasoline'),
    ('cng', 'CNG'),
    ('lpg', 'LPG'),
    ('hydrogen', 'Hydrogen'),
    ('electric', 'Electric'),
]


class UsedVehicleAdd(models.Model):
    _inherit = 'product.template'

    detailed_type = fields.Selection(selection_add=[('vehicle', 'Vehicle')], tracking=True,
                                     ondelete={'vehicle': 'set consu'})
    type = fields.Selection(selection_add=[
        ('vehicle', 'Vehicle')
    ], ondelete={'vehicle': 'set consu'})
    down_payment_amount = fields.Float(
        'Down Payment Amount', digits='Down Payment Amount',
        default=0, help="Down payment amount as an advance.",
    )
    brand_id = fields.Many2one('used.vehicle.model.brand', 'Manufacturer',
                               help='Manufacturer of the vehicle')
    vehicle_type = fields.Many2one('used.vehicle.type', 'Type')
    vehicle_condition = fields.Many2one('used.vehicle.condition', string='Condition')
    transmission = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic')], 'Transmission',
                                    help='Transmission Used by the vehicle')
    model_year = fields.Char()
    seats = fields.Integer(string='Seats Number')
    doors = fields.Integer(string='Doors Number')
    default_co2 = fields.Integer('CO2 Emissions')
    default_mileage = fields.Char('Mileage')
    vin_code = fields.Char('VIN Code')

    start_date = fields.Date('Start Date')
    vehicle_features = fields.Html('Vehicle Features')
    co2_standard = fields.Char()
    default_fuel_type = fields.Selection(FUEL_TYPES, 'Fuel Type', default='diesel')
    power = fields.Integer('Power')
    horsepower = fields.Integer()
    horsepower_tax = fields.Integer('Horsepower Taxation')
    title_status = fields.Char('Title Status')
    engine = fields.Char('Engine')
    drivetrain = fields.Char('Drivetrain')
    exterior_color = fields.Many2many('used.vehicle.exterior.color')
    interior_color = fields.Many2many('used.vehicle.interior.color')

    def _detailed_type_mapping(self):
        type_mapping = super()._detailed_type_mapping()
        type_mapping['vehicle'] = 'product'
        return type_mapping

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        if self.brand_id:
            self.image_1920 = self.brand_id.image_128

    def action_print_catalog(self):
        return self.env.ref('zillotech_vehicle_sale.action_inventory_product_report').report_action(self)


class UsedVehicleAdd(models.Model):
    _inherit = 'sale.order'

    down_payment_amount = fields.Float()
    balance_amount = fields.Float()
