from odoo import api, fields, models


class BrandCreate(models.Model):
    _name = "vehicle.brand.model"
    _description = "Customer"
    # _rec_name = "vehicle_brand_name"

    name = fields.Char(string='Brand Name', required=True,ondelete='restrict')



