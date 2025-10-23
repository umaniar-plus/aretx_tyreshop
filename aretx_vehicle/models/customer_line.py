from odoo import api, fields, models


class CustomContacts(models.Model):
    _inherit = "res.partner"
    x_brand_ids = fields.Many2many('vehicle.master.model', 'x_brand_id', string="Brand Name",ondelete='restrict')
    x_model_ids = fields.One2many('vehicle.master.model', 'x_model_id', string="Model Name",ondelete='restrict')
    # x_customer_ids = fields.One2many('vehicle.mapper.master.model', 'x_customer_id', string="Customer Details",ondelete='restrict')

    x_vehicle_number_ids = fields.Many2many('vehicle.master.model',string="Brand Name", ondelete='restrict')
    # x_vehicle_number_ids = fields.Many2many('vehicle.master.model','res_partner_vehicle_master_model_rel','tally_mapper_name','x_vehicle_number_ids',string="Brand Name", ondelete='restrict')

    # x_customer_ids = fields.One2one('vehicle.master.model', 'x_customer_id', string="Vehicle Details",ondelete='restrict')
    # x_vehicle_number_ids=fields.One2many('vehicle.master.model', 'x_vehicle_number_id', string="Vehicle Details",ondelete='restrict')
    # x_vehicle_number_ids=fields.One2many('vehicle.mapper.master.model', 'vehicle_id', string="Vehicle Details",ondelete='restrict')
    # x_customer_ids = fields.One2many('vehicle.master.model', 'x_customer_id', string="Vehicle Details",ondelete='restrict')
    # x_vehicle_number_ids=fields.One2many('vehicle.master.model', 'x_vehicle_number_id', string="Vehicle Details",ondelete='restrict')
    x_color_ids = fields.One2many('vehicle.master.model', 'x_color_id', string="Vehicle Details",ondelete='restrict')

    # @api

