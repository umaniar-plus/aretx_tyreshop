from odoo import api, fields, models


class CustomSale(models.Model):
    _inherit = ["sale.order"]

    x_vehicle_number_id = fields.Many2one('vehicle.master.model', string='Vehicle number',
                                          domain="[('x_customer_id','=',partner_id)]")

    # vehicle_number = fields.Char(string="vehicle_number")
    # vehicle_kms = fields.Char(string='Vehicle KMS')

    def _create_invoice(self):
        invoice_vals = super(CustomSale, self)._create_invoice()
        invoice_vals['vehicle_number'] = self.x_vehicle_number_id.id
        print("invoice vals", invoice_vals)
        return invoice_vals
