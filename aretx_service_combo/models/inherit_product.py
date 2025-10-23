from odoo import api, fields, models



class Custom_Invoice(models.Model):
    _inherit = "product.template"

    is_service_combo=fields.Boolean('Is Service Combo', default=False)
    contract_duration=fields.Integer(string='Contract Duration In Months')
    x_service_combo_ids = fields.One2many('service.combo.item', 'service_combo_id', string="service combo")
    x_service_ids = fields.One2many('service.combo.item', 'service_id', string="Service")
    x_quantity_ids=fields.One2many('service.combo.item', 'no_of_items', string="Quantity")

    @api.onchange('is_service_combo')
    def onchange_is_service_combo(self):
        for rec in self:
            print(rec)
            print(rec.is_service_combo)
            if rec.is_service_combo == True:
                print("true",rec.is_service_combo)
                service = self.env['product.template'].search([('id', '=',rec.ids)])
                print("id..",service)



    # @api.depends('x_service_ids')
    # def _compute_x_service_combo_ids(self):
    #     for rec in self:
    #         print(rec)

    # @api.depends('x_service_ids','x_service_combo_ids')
    # def _compute_service(self):
    #     for rec in self:
    #         print("combo_id", rec.service_combo_id.ids)
    #         print("service id", rec.service_id.id)
    #         if rec.service_id.id in rec.service_combo_id.ids:
    #             print("success")
                # self.service_id = None
            # print(rec.service_id)