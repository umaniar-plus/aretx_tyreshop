from odoo import api, fields, models
from odoo.osv.expression import AND


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tyre_message_km = fields.Integer(
        string="Send Message Every (KM)",
        config_parameter='tyreshop.tyre_message_km',
        help="Send reminder message every given kilometers."
    )
    tyre_message_months = fields.Integer(
        string="Send Message Every (Months)",
        config_parameter='tyreshop.tyre_message_months',
        help="Send reminder message every given months."
    )


class VehicleMaster(models.Model):
    _name = "vehicle.master.model"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vehicle Master"
    _rec_name = 'x_vehicle_number_id'

    partner_id = fields.Many2one('res.partner', string="Customer")

    x_brand_id = fields.Many2one('vehicle.brand.model', string="Brand Name", ondelete='restrict')
    x_model_id = fields.Many2one('vehicle.model.model', string="Model Name", domain="[('brand_id','=',x_brand_id)]",
                                 ondelete='restrict')
    x_vehicle_number_id = fields.Char(string="Vehicle Number", required=True, tracking=True, ondelete='restrict')
    x_color_id = fields.Many2one('vehicle.color.model', string="Vehicle Color", ondelete='restrict')
    x_avg_km = fields.Integer(
        string="Avg Monthly (KM)",
        help="Avg monthly given kilometers."
    )
    x_customer_id = fields.Many2many('res.partner', 'res_partner_vehicle_master_model_rel', string="Customers",
                                     required=True, tracking=True)

    last_message_date = fields.Date(
        string="Last Message Date",
        default=lambda self: fields.Date.today(),  # sets today's date at creation
    )

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string="Priority")  # priority widget

    @api.model
    def default_get(self, fields_list):
        res = super(VehicleMaster, self).default_get(fields_list)
        print("Context received in default_get:", self.env.context)

        context = dict(self.env.context or {})
        print('context:', context)

        if context.get('default_name'):
            res['x_vehicle_number_id'] = context['default_name']

        if context.get('default_partner_id'):
            partner = self.env['res.partner'].browse(context['default_partner_id'])  # Fetch partner record
            res['x_customer_id'] = [(6, 0, [partner.id])]  # Correctly assign Many2many field

        return res

    def name_get(self):
        result = []
        for record in self:
            add = ''
            if record.x_brand_id and record.x_model_id:
                add = '(' + ' ' + record.x_brand_id.name + ' ' + record.x_model_id.name + ' )'
            name = record.x_vehicle_number_id + ' ' + add
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):
        if 'x_vehicle_number_id' in vals:
            vehicle_search = self.env['vehicle.master.model'].search(
                [('x_vehicle_number_id', '=', vals['x_vehicle_number_id'])])
            if vehicle_search:
                x_customer_id = 'x_customer_id'
                if 'tally_mapper_name' in vals:
                    x_customer_id = 'tally_mapper_name'
                if len(vals[x_customer_id][0][2]) > 1:
                    x_c_ids = tuple(vals[x_customer_id][0][2])
                else:
                    x_c_ids = '(' + str(vals[x_customer_id][0][2][0]) + ')'
                self._cr.execute(
                    '''SELECT res_partner_id FROM res_partner_vehicle_master_model_rel WHERE vehicle_master_model_id = %s AND res_partner_id IN %s''' % (
                        vehicle_search.id, x_c_ids))
                mapper_exist_ids = self._cr.fetchall()
                for rec in vals[x_customer_id][0][2]:
                    if len(mapper_exist_ids) == 0:
                        # create
                        self._cr.execute(
                            '''INSERT INTO res_partner_vehicle_master_model_rel(vehicle_master_model_id,res_partner_id) VALUES(%s,%s)''' % (
                                vehicle_search.id, rec))
                    elif rec not in mapper_exist_ids[0]:
                        # create
                        self._cr.execute(
                            '''INSERT INTO res_partner_vehicle_master_model_rel(vehicle_master_model_id,res_partner_id) VALUES(%s,%s)''' % (
                                vehicle_search.id, rec))

                return vehicle_search
            else:
                res = super(VehicleMaster, self).create(vals)
                return res
        else:
            res = super(VehicleMaster, self).create(vals)
            return res

    def view_in_invoice(self):
        return {
            'name': self.x_vehicle_number_id,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'domain': [('vehicle_number', '=', self.x_vehicle_number_id)],
            'target': 'list'
        }

    def view_in_sale(self):
        return {
            'name': self.x_vehicle_number_id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'domain': [('x_vehicle_number_id', '=', self.x_vehicle_number_id)],
            'target': 'list'
        }
