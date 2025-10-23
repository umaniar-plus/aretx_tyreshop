from odoo import api, fields, models
from datetime import datetime

class ComboCreate(models.Model):
    _name = "service.combo.tracker"
    _description = "service combo tracker"

    # vehicle = fields.Many2one('vehicle.master.model', string='Vehicle', store=False)
    # customer = fields.Many2one('res.partner', string="Customer Name", related='vehicle.x_customer_id', store=False)
    # mobile = fields.Char(string="Mobile", related='customer.mobile', store=False)
    # brand = fields.Many2one('vehicle.brand.model', string="Brand Name", related='vehicle.x_brand_id', store=False)
    # model = fields.Many2one('vehicle.model.model', string="Model", related='vehicle.x_model_id', store=False)

    # saleorder_line_id = fields.Integer(string='saleorder id', readonly=True)
    account_move_line_id = fields.Many2one('account.move.line',string='invoice id',readonly=True, ondelete="cascade")
    saleorder_line_id = fields.Many2one('sale.order.line',string='saleorder id',readonly=True, ondelete="cascade")
    jobcard_line_id = fields.Many2one('job.card.line',string='jobcard id',readonly=True, ondelete="cascade")
    vehicle = fields.Char(string='Job Card Vehicle Number',related="jobcard_line_id.vehicle_id",readonly=True, store=True)
    vehicle_sale_order = fields.Char(string='Sale Order Vehicle Number',related="saleorder_line_id.vehicle_id",readonly=True, store=True)
    vehicle_invoice = fields.Char(string='Invoice Vehicle Number', related="account_move_line_id.vehicle_id",readonly=True, store=True)
    # vehicle = fields.Char(string='Vehicle Number',related="jobcard_line_id.vehicle_id",readonly=True)
    job_id = fields.Many2one(string='Job Card Customer',related="jobcard_line_id.job_id.partner_id",readonly=True,store=True)
    sale_order_id = fields.Many2one(string='Sale Order Customer',related="saleorder_line_id.order_id.partner_id",readonly=True,store=True)
    account_move_id = fields.Many2one(string='Invoice Customer', related="account_move_line_id.move_id.partner_id",readonly=True, store=True)

    expiry_date = fields.Date(string='Expiry Date', default=fields.Date.context_today,readonly=True)
    service_combo_id = fields.Many2one('product.template',string='service combo',readonly=True)
    service_id=fields.Many2one('product.template',string='service',readonly=True)

    # x_job_card_line_ids = fields.One2many('service.combo.tracker', 'jobcard_line_id', string="Job card line", store=False)

    # jobcard_line_id = fields.Many2one('job.card.line', string='jobcard id')
    # expiry_date = fields.Date(string='Expiry Date', default=fields.Date.context_today)
    # service_combo_id = fields.Many2one('product.template', string='service combo')
    # service_id = fields.Many2one('product.template', string='service')

    state = fields.Selection([
        ('draft', 'Pending'),
        ('cancle', 'Cancelled'),
        ('done', 'Done'), ], default='draft', string="Status")
    completed_date = fields.Date(string='Completed Date')
    description=fields.Char(string='Description')
    is_infinite = fields.Boolean(string='is infinite', default=False,readonly=True)

    def add_combo(self):
        task1 = self.env['service.combo.tracker']  # call create method of tasks.manager model
        if self._context['jobcard_line_id']:
            task1.create({'is_infinite': False, 'expiry_date': self._context['expiry_date'],'jobcard_line_id': self._context['jobcard_line_id'],'completed_date':datetime.today(),'service_combo_id': self._context['service_combo_id'],'service_id': self._context['service_id'], 'state': 'done'})
        if self._context['saleorder_line_id']:
            task1.create({'is_infinite': False, 'expiry_date': self._context['expiry_date'],'saleorder_line_id': self._context['saleorder_line_id'],'completed_date':datetime.today(),'service_combo_id': self._context['service_combo_id'],'service_id': self._context['service_id'], 'state': 'done'})
        if self._context['account_move_line_id']:
            task1.create({'is_infinite': False, 'expiry_date': self._context['expiry_date'],'account_move_line_id': self._context['account_move_line_id'],'completed_date':datetime.today(),'service_combo_id': self._context['service_combo_id'],'service_id': self._context['service_id'], 'state': 'done'})

    def view_partner(self):
        res_id = False
        if self.sale_order_id.id:
            res_id = self.sale_order_id.id
        elif self.account_move_id.id:
            res_id = self.account_move_id.id
        return {
            # 'name': self.x_vehicle_number_id,  # 'account.move.view',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            # 'view_type': 'tree,form',
            # 'view_type': 'tree',
            'view_mode': 'form',
            # 'view_id': self.env.ref('base.view_partner_form').id
            # 'view_id': self.env.ref('service_combo.service_combo_tracker_form_view').id,
            # 'domain': [('id', '=', self.id)],
            # 'target': 'list'
            # 'context':{'id':self.id},
            'res_id': res_id,
            # 'context': {'form_view_initial_mode': 'edit','no_create': True,'create':False},
            'context': {'create': False},
            # 'context': dict(self._context, create=False),
            # 'options':{'no_create': True},
            # 'flags': {'form': {'action_buttons': True}},
            # 'nodestroy': False,
            'nodestroy': True,
            'target': 'new'
        }
    def edit_combo(self):
        return {
            # 'name': self.x_vehicle_number_id,  # 'account.move.view',
            'res_model': 'service.combo.tracker',
            'type': 'ir.actions.act_window',
            # 'view_type': 'tree,form',
            # 'view_type': 'tree',
            'view_mode': 'form',
            # 'view_id': self.env.ref('base.view_partner_form').id
            # 'view_id': self.env.ref('service_combo.service_combo_tracker_form_view').id,
            # 'domain': [('id', '=', self.id)],
            # 'target': 'list'
            # 'context':{'id':self.id},
            'res_id': self.id,
            # 'context': {'form_view_initial_mode': 'edit','no_create': True,'create':False},
            'context': {'create':False},
            # 'context': dict(self._context, create=False),
            # 'options':{'no_create': True},
            # 'flags': {'form': {'action_buttons': True}},
            # 'nodestroy': False,
            'nodestroy': True,
            'target': 'new'
        }

    # @api.onchange('vehicle')
    # def _change_vehicle(self):
    #     print('vehicle_changed')
    #     print('vehicle_changed')
    #     print('vehicle_changed')
    #     for rec in self:
    #         job_card = self.env['job.card'].search(
    #             [('vehicle', '=', rec.vehicle.id), ('partner_id', '=', rec.vehicle.x_customer_id.id)])
    #         # print(dir(job_card.x_job_card_ids))
    #         ids = []
    #         for line in job_card.x_job_card_ids:
    #             ids.append(line.id)
    #         if len(ids) > 0:
    #             self.x_job_card_line_ids = self.env['service.combo.tracker'].search([('jobcard_line_id', 'in', ids)])
    #         else:
    #             self.x_job_card_line_ids = None
    #     print('asdasdasd')
    #     print('asdasdasd')
    #     print('asdasdasd')
    #     print(self.x_job_card_line_ids)
    #     print(dir(self.x_job_card_line_ids))
    #     print(self.x_job_card_line_ids.service_combo_id.name)
    #     print('asdasdasd')

        
