from odoo import api, fields, models


class CustomContacts(models.Model):
    _inherit = "res.partner"

    sms_history = fields.One2many('aretx.sms.composer', 'partner_id', string="SMS History", domain="[('partner_id','=',id)]", readonly=True, ondelete='restrict')
    phone = fields.Char(string="Phone", required=True)


