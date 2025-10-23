from odoo import api, fields, models


class CustomInvoice(models.Model):
    _inherit = "account.move"

    # vehicle_number = fields.Many2one('vehicle.master.model',string='Vehicle number',domain="[('x_customer_id','=',partner_id)]",ondelete='restrict')
    # brand_id = fields.Many2one('vehicle.brand.model', string="Brand Name")

    # vehicle_number = fields.Many2one('vehicle.master.model', string='Vehicle number',
    #                                domain="[('x_customer_id','=',partner_id)]")
    # tally_mapper_name = fields.One2many('vehicle.master.model','tally_mapper_name',string='Tally Mapper From Invoice',readonly=False)
    # tally_mapper_name = fields.One2many('vehicle.master.model','tally_mapper_name',string='Tally Mapper From Invoice',readonly=False)
    # vehicle_number = fields.Many2one('vehicle.mapper.master.model',string='Vehicle number',domain="[('x_customer_id','=',partner_id)]")
    vehicle_kms = fields.Char(string='Vehicle KMS')

    vehicle_number = fields.Many2one(
        'vehicle.master.model',
        string='Vehicle Number',
        domain="[('x_customer_id', '=', partner_id)]"
    )
