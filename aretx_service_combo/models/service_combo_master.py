from odoo import api, fields, models

class ComboCreateMaster(models.Model):
    _name = "service.combo.master"
    # _inherit = "service.combo.tracker"
    _description = "service combo Master"

    # vehicle = fields.Many2one('vehicle.master.model', string='Vehicle',store=True)
    # customer = fields.Many2one('res.partner', string="Customer Name", related='vehicle.x_customer_id')
    # mobile=fields.Char(string="Mobile",related='customer.mobile')
    # brand = fields.Many2one('vehicle.brand.model', string="Brand Name",related='vehicle.x_brand_id')
    # model = fields.Many2one('vehicle.model.model',string="Model", related='vehicle.x_model_id')
    name = fields.Char(string="Name", store=True)
    vehicle = fields.Many2one('vehicle.master.model', string='Vehicle', tracking=True,store=True)
    # customer = fields.Char(string="Customer Name", store=True)
    # customer = fields.One2many('vehicle.master.model', 'id', string="Customer Name", store=True)
    # customer = fields.One2many('res.partner', 'id', string="Customer Name", store=True)
    # customer = fields.Many2many('res.partner', string="Customers", store=True)
    # mobile = fields.Char(string="Mobile", store=True)
    # vehicle_id = fields.One2many('res.partner.vehicle.master.model.rel', string='Customer', store=True)
    # vehicle_id = fields.One2many('res.partner.vehicle.master.model.rel', 'vehicle_master_model_id', string='Customer', store=True)
    # customer = fields.One2many('res.partner.vehicle.master.model.rel', 'res_partner_id', string='Customer', store=True)
    # customer = fields.One2many('vehicle.master.model', 'x_customer_id', string='Customer', store=True)
    # customer = fields.Many2one('res.partner', string="Customer Name", related='vehicle.x_customer_id', store=True)
    # customer = fields.Many2one('res.partner', string="Customer Name", related='vehicle.x_customer_id', store=True)
    # mobile = fields.Char(string="Mobile", related='customer.mobile', store=True)
    brand = fields.Many2one('vehicle.brand.model', string="Brand Name", related='vehicle.x_brand_id', store=True)
    model = fields.Many2one('vehicle.model.model', string="Model", related='vehicle.x_model_id', store=True)


    # x_job_card_item = fields.Many2one('job.card.line', string="Job card line", domain="[('vehicle_id','=',vehicle.x_vehicle_number_id)]")
    # x_job_card_line_ids = fields.Many2one('service.combo.tracker', string="Job card line",domain="[('jobcard_line_id','in',x_job_card_item)]")


    # x_job_card_line_ids = fields.One2many('service.combo.tracker', 'jobcard_line_id', string="Job card line")

    # x_job_card_item = fields.Many2one('job.card.line', string="Job card line",domain="[('vehicle_id','=',vehicle.x_vehicle_number_id)]",store=True)

    jobcard_line_id = fields.One2many('service.combo.tracker',string="Job card line",store=False)

    # x_service_combo_ids = fields.Many2one('service.combo.tracker', related="x_job_card_line_ids.service_combo_id", string="Service Combo id",store=False)
    # x_job_card_line_ids = fields.One2many('service.combo.tracker', 'jobcard_line_id', string="Job card line",store=False)

    # x_job_card_line_ids = fields.One2many('service.combo.tracker', 'jobcard_line_id', string="Job card line")
    # x_service_combo_ids = fields.One2many('service.combo.tracker', 'service_combo_id', string="Service Combo id")
    # x_state = fields.One2many('service.combo.tracker', 'state', string="State")
    # x_completed_date = fields.One2many('service.combo.tracker', 'completed_date', string="Completed Date")
    # x_description = fields.One2many('service.combo.tracker', 'description', string="Description")
    # x_service_ids = fields.One2many('service.combo.tracker', 'service_id', string="Service Id")

    @api.depends('vehicle')
    def _depends_vehicle(self):
        print('independs')
        print('independs')
        print('independs')

    @api.onchange('vehicle')
    def _change_vehicle(self):
        self.jobcard_line_id = None
        for rec in self:
            if rec.vehicle.x_customer_id is not False:
                print(rec.vehicle.x_customer_id)
                customer_ids = []
                for c_id in rec.vehicle.x_customer_id:
                    customer_ids.append(c_id.id)
                print(customer_ids)
                if len(customer_ids) > 0:
                    # self.customer = rec.vehicle.x_customer_id
                    # print([rec.vehicle.x_customer_id.id])
                    #job_card = self.env['job.card'].search([('vehicle', '=', rec.vehicle.id),('partner_id', 'in', customer_ids)])
                    sale_order = self.env['sale.order'].search([('x_vehicle_number_id', '=', rec.vehicle.id),('partner_id', 'in', customer_ids)])
                    invoice = self.env['account.move'].search([('vehicle_number', '=', rec.vehicle.id), ('partner_id', 'in', customer_ids)])
                    # print(dir(job_card.x_job_card_ids))
                    ids = []
                    #for line in job_card.x_job_card_ids:
                        # ids.append(str(line.id)+str(datetime.today()))
                        #ids.append(line.id)

                    sale_ids = []
                    invoice_ids = []
                    for sale_line in sale_order.order_line:
                        # ids.append(str(line.id)+str(datetime.today()))
                        sale_ids.append(sale_line.id)
                    for invoice in invoice.invoice_line_ids:
                        # ids.append(str(line.id)+str(datetime.today()))
                        invoice_ids.append(invoice.id)
                    if len(ids) > 0 or len(sale_ids) > 0 or len(invoice_ids) > 0:
                        # self.jobcard_line_id = self.env['service.combo.tracker'].search([('jobcard_line_id', 'in', ids)])
                        if len(ids) > 0 and len(sale_ids) > 0:
                            self.jobcard_line_id = self.env['service.combo.tracker'].search(['|', ('jobcard_line_id', 'in', ids), ('saleorder_line_id', 'in', sale_ids)])
                        elif len(ids) > 0:
                            self.jobcard_line_id = self.env['service.combo.tracker'].search([('jobcard_line_id', 'in', ids)])
                        elif len(invoice_ids) > 0 and len(sale_ids) > 0:
                            self.jobcard_line_id = self.env['service.combo.tracker'].search(['|', ('account_move_line_id', 'in', invoice_ids), ('saleorder_line_id', 'in', sale_ids)])
                        elif len(sale_ids) > 0:
                            self.jobcard_line_id = self.env['service.combo.tracker'].search([('saleorder_line_id', 'in', sale_ids)])
                        elif len(invoice_ids) > 0:
                            self.jobcard_line_id = self.env['service.combo.tracker'].search([('account_move_line_id', 'in', invoice_ids)])
                        # self.jobcard_line_id = self.env['service.combo.tracker'].search([('jobcard_line_id', 'in', ids)])

                    else:
                        self.jobcard_line_id = None

        # print('asdasdasd')
        # print('asdasdasd')
        # print('asdasdasd')
        # print(self.x_job_card_line_ids)
        # print(dir(self.x_job_card_line_ids))
        # print(self.x_job_card_line_ids.service_combo_id.name)
        # print('asdasdasd')

    @api.model
    def default_get(self, fields):
        rec = super(ComboCreateMaster, self).default_get(fields)
        # if conditions are met
        # res['vehicle'] = id_of_many2one_field
        # print('ressressressress')
        # print(res)
        # print(fields)
        # print(self)
        # print(self.vehicle)

        # for rec in self:
        #     job_card = self.env['job.card'].search([('vehicle', '=', rec.vehicle.id),('partner_id', '=', rec.vehicle.x_customer_id.id)])
        #     # print(dir(job_card.x_job_card_ids))
        #     print(job_card.x_job_card_ids)
        #     ids = []
        #     for line in job_card.x_job_card_ids:
        #         ids.append(line.id)
        #     if len(ids) > 0:
        #         rec.x_job_card_line_ids = self.env['service.combo.tracker'].search([('jobcard_line_id', 'in', ids)])
        #     else:
        #         rec.x_job_card_line_ids = None


        for rec in self:
            if rec.vehicle.x_customer_id is not False:
                print(rec.vehicle.x_customer_id)
                customer_ids = []
                for c_id in rec.vehicle.x_customer_id:
                    customer_ids.append(c_id.id)
                print(customer_ids)
                if len(customer_ids) > 0:
                    # self.customer = rec.vehicle.x_customer_id
                    # print([rec.vehicle.x_customer_id.id])
                    #job_card = self.env['job.card'].search([('vehicle', '=', rec.vehicle.id),('partner_id', 'in', customer_ids)])
                    sale_order = self.env['sale.order'].search([('x_vehicle_number_id', '=', rec.vehicle.id),('partner_id', 'in', customer_ids)])
                    # print(dir(job_card.x_job_card_ids))
                    ids = []
                    #for line in job_card.x_job_card_ids:
                        # ids.append(str(line.id)+str(datetime.today()))
                        #ids.append(line.id)

                    sale_ids = []
                    for sale_line in sale_order.order_line:
                        # ids.append(str(line.id)+str(datetime.today()))
                        sale_ids.append(sale_line.id)
                    if len(ids) > 0 or len(sale_ids) > 0:
                        # self.jobcard_line_id = self.env['service.combo.tracker'].search([('jobcard_line_id', 'in', ids)])
                        if len(ids) > 0 and len(sale_ids) > 0:
                            self.jobcard_line_id = self.env['service.combo.tracker'].search(['|', ('jobcard_line_id', 'in', ids), ('saleorder_line_id', 'in', sale_ids)])
                        elif len(ids) > 0:
                            self.jobcard_line_id = self.env['service.combo.tracker'].search([('jobcard_line_id', 'in', ids)])
                        elif len(sale_ids) > 0:
                            self.jobcard_line_id = self.env['service.combo.tracker'].search([('saleorder_line_id', 'in', sale_ids)])
                        # self.jobcard_line_id = self.env['service.combo.tracker'].search([('jobcard_line_id', 'in', ids)])

                    else:
                        self.jobcard_line_id = None
                # if len(customer_ids) > 0:
                #     # self.customer = rec.vehicle.x_customer_id
                #     # print([rec.vehicle.x_customer_id.id])
                #     job_card = self.env['job.card'].search([('vehicle', '=', rec.vehicle.id),('partner_id', 'in', customer_ids)])
                #     # print(dir(job_card.x_job_card_ids))
                #     ids = []
                #     for line in job_card.x_job_card_ids:
                #         # ids.append(str(line.id)+str(datetime.today()))
                #         ids.append(line.id)
                #     if len(ids) > 0:
                #         rec.jobcard_line_id = self.env['service.combo.tracker'].search([('jobcard_line_id', 'in', ids)])
                #
                #     else:
                #         rec.jobcard_line_id = None



        # print('ressressressress')
        return rec
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False,submenu=False):
    #     res = super(ComboCreateMaster, self).fields_view_get(
    #         view_id=view_id, view_type=view_type, toolbar=toolbar,
    #         submenu=submenu)
    #     # project_login = self.env['project.project'].search([])
    #     # managers_list = self.env.ref('project.group_project_manager')
    #     # for record in project_login:
    #     #     if (record.user_id.id == self.env.context.get('uid')) or (
    #     #             self.env.context.get('uid') in managers_list.users.ids):
    #     #         record.project_m_user = True
    #     #     else:
    #     #         record.project_m_user = False
    #     print('fields_view_get')
    #     print('fields_view_get')
    #     print('fields_view_get')
    #     print(self)
    #     print(view_id)
    #     print(view_type)
    #     print(toolbar)
    #     print(submenu)
    #     if 'params' in self._context:
    #         if 'id' in self._context['params']:
    #             combos = self.env['service.combo.master'].search([('id', '=', self._context['params']['id'])])
    #             if combos:
    #                 print(self._context['params']['id'])
    #                 print(combos.vehicle)
    #                 self.vehicle = combos.vehicle
    #                 self._change_vehicle()
    #     print('fields_view_get')
    #     print('fields_view_get')
    #     print('fields_view_get')
    #     # print(self.httprequest.referrer)
    #     # print(self.env.ref('service_combo.service_combo_master', 'id'))
    #     # print(res)
    #     self._change_vehicle()
    #     return res

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False,submenu=False):
    #     print('fields_view_get')
    #     print('fields_view_get')
    #     print('fields_view_get')
    #     print(self)

        # return self.x_job_card_line_ids

    # def write(self, vals):
    #     print('self')
    #     print(self)
    #     print('self')
    #     print('vals')
    #     print(vals)
    #     print('vals')
    #     res = super(ComboCreateMaster, self).write(vals)
    #     self._change_vehicle()
    #     return res
    # def save_combo(self):
    #     # print('hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    #     # print('hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    #     # print('hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    #     # print(self)
    #     # print('hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
    #     # return True
    #     return {
    #         # 'name': self.x_vehicle_number_id,  # 'account.move.view',
    #         'res_model': 'service.combo.tracker',
    #         'type': 'ir.actions.act_window',
    #         # 'view_type': 'tree,form',
    #         'view_type': 'tree',
    #         'view_mode': 'tree',
    #         # 'view_id': self.env.ref('base.view_partner_form').id
    #         # 'view_id': self.env.ref('service_combo.service_combo_tracker_form_view').id,
    #         # 'domain': [('id', '=', self.id)],
    #         # 'target': 'form'
    #         # 'target': 'new'
    #     }


    # @api.model
    # def create(self, vals):
    #     # res = super(ComboCreateMaster, self).create(vals)
    #     # # self.service_combo()
    #     # return res
    #     print('uyuuiyiuyiuyiuyuiy')
    #     print(self)
    #     print(vals)
    #     print('uyuuiyiuyiuyiuyuiy')
    #     print('uyuuiyiuyiuyiuyuiy')
    #     #pass combo_tracker id and update it
    #     # task1 = self.env['service.combo.tracker']  # call create method of tasks.manager model
    #     # task1.create({'expiry_date': job_card_id.expiry_date, 'jobcard_line_id': job_combo_id,
    #     #               'service_combo_id': combo.service_combo_id.id,
    #     #               'service_id': combo.service_id.id, 'state': 'draft'})
    #     # return self.id
    #     return True
    #     # res = super(ComboCreateMaster, self).create(vals)
    #     # # self.service_combo()
    #     # return self.service_combo()
    # 
    # def save_combo(self):
    #     return {
    #         # 'name': self.x_vehicle_number_id,  # 'account.move.view',
    #         'res_model': 'account.move',
    #         'type': 'ir.actions.act_window',
    #         # 'view_type': 'tree,form',
    #         'view_mode': 'tree,form',
    #         # 'view_id': self.env.ref('base.view_partner_form').id
    #         # 'view_id': self.env.ref('account.view_out_invoice_tree').id,
    #         # 'domain': [('vehicle_number', '=', self.x_vehicle_number_id)],
    #         'target': 'list'
    #         # 'target': 'new'
    #     }



