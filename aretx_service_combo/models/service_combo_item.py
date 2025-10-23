from odoo import api, fields, models


class ComboCreate(models.Model):
    _name = "service.combo.item"
    _description = "service combo item"

    service_combo_id = fields.Many2one('product.template',string='service combo')
    service_id=fields.Many2one('product.template',string='service',domain="[('detailed_type','=','service'),('is_service_combo','=',False)]")
    no_of_items=fields.Integer(string='Quantity')







