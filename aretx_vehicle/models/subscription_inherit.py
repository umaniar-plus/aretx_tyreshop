from odoo import api, fields, models


class CustomSubscriptionPackage(models.Model):
    _inherit = "subscription.package"

    #x_vehicle_number_id = fields.Many2one('vehicle.master.model',string='Vehicle number',domain="[('x_customer_id','=',partner_id)]")

    # vehicle_number_sub = fields.Many2one('vehicle.master.model', string='Vehicle number',domain="[('x_customer_id','=',partner_id)]")
    vehicle_number_sub = fields.Many2one('vehicle.mapper.master.model', string='Vehicle number',domain="[('x_customer_id','=',partner_id)]")

    # vehicle_number = fields.Char(string="vehicle_number")

    # def _prepare_invoice(self):
    #     invoice_vals=super(CustomSale, self)._prepare_invoice()
    #     invoice_vals['vehicle_number']=self.x_vehicle_number_id.id
    #     print("invoice vals",invoice_vals)
    #     return invoice_vals
