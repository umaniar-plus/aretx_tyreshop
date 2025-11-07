from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.addons.phone_validation.tools import phone_validation


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            partners = self.search([
                                       '|', '|', '|', '|', '|',
                                       ('name', operator, name),
                                       ('email', operator, name),
                                       ('ref', operator, name),
                                       ('vat', operator, name),
                                       ('phone', operator, name),
                                       ('mobile', operator, name)
                                   ] + args, limit=limit)
        else:
            partners = self.search(args, limit=limit)
        return partners.name_get()


class InheritInvoiceLine(models.Model):
    _inherit = "account.move.line"
    # _inherit = ['account.move.line', 'mail.thread', 'mail.activity.mixin']

    expiry_date = fields.Date(string='Expiry Date')
    # expiry_date = fields.Date(string='Expiry Date', default=fields.Date.context_today)
    check = fields.Boolean(string='check', default=False)
    vehicle_id = fields.Char(string="Vehicle", stored=True)
    phone = fields.Char(related='partner_id.phone', store=False, string='Customer Phone', index=True)
    mobile = fields.Char(related='partner_id.mobile', store=False, string='Customer Mobile', index=True)
    # sms_data = fields.Many2one('aretx.sms.composer', domain="[('res_model', '=', 'account.move.line'), ('res_id', '=', id)]", store=False, string='Is SMS Sent?', index=True)
    is_sms_sent = fields.Boolean(string='Is SMS Sent?', compute='_compute_is_sms_sent', compute_sudo=False,
                                 default=False, store=False)
    x_vehicle_number_ids = fields.Many2many(related='partner_id.x_vehicle_number_ids', store=False, string='Vehicles',
                                            index=True)

    def _compute_is_sms_sent(self):
        for rec in self:
            print('sms_data')
            if 'aretx.sms.composer' in self.env:
                sms_data = self.env['aretx.sms.composer'].search(
                    [('res_model', '=', 'account.move.line'), ('res_id', '=', rec.id)])
                print(sms_data)
                if sms_data:
                    rec.is_sms_sent = True
                else:
                    rec.is_sms_sent = False
                # print(rec.sms_data)
                print('sms_data')
            else:
                rec.is_sms_sent = False
            # rec.is_sms_sent = False
        # pass

    def _sms_get_partner_fields(self):
        """ This method returns the fields to use to find the contact to link
        whensending an SMS. Having partner is not necessary, having only phone
        number fields is possible. However it gives more flexibility to
        notifications management when having partners. """
        fields = []
        if hasattr(self, 'partner_id'):
            fields.append('partner_id')
        if hasattr(self, 'partner_id'):
            fields.append('partner_id')
        if hasattr(self, 'partner_ids'):
            fields.append('partner_ids')
        return fields

    def _sms_get_default_partners(self):
        """ This method will likely need to be overridden by inherited models.
               :returns partners: recordset of res.partner
        """
        partners = self.env['res.partner']
        for fname in self._sms_get_partner_fields():
            partners = partners.union(*self.mapped(fname))  # ensure ordering
        return partners

    def _sms_get_number_fields(self):
        """ This method returns the fields to use to find the number to use to
        send an SMS on a record. """
        if 'mobile' in self:
            return ['mobile']
        return []

    def _sms_get_recipients_info(self, force_field=False, partner_fallback=True):
        """" Get SMS recipient information on current record set. This method
        checks for numbers and sanitation in order to centralize computation.

        Example of use cases

          * click on a field -> number is actually forced from field, find customer
            linked to record, force its number to field or fallback on customer fields;
          * contact -> find numbers from all possible phone fields on record, find
            customer, force its number to found field number or fallback on customer fields;

        :param force_field: either give a specific field to find phone number, either
            generic heuristic is used to find one based on ``_sms_get_number_fields``;
        :param partner_fallback: if no value found in the record, check its customer
            values based on ``_sms_get_default_partners``;

        :return dict: record.id: {
            'partner': a res.partner recordset that is the customer (void or singleton)
                linked to the recipient. See ``_sms_get_default_partners``;
            'sanitized': sanitized number to use (coming from record's field or partner's
                phone fields). Set to False is number impossible to parse and format;
            'number': original number before sanitation;
            'partner_store': whether the number comes from the customer phone fields. If
                False it means number comes from the record itself, even if linked to a
                customer;
            'field_store': field in which the number has been found (generally mobile or
                phone, see ``_sms_get_number_fields``);
        } for each record in self
        """
        result = dict.fromkeys(self.ids, False)
        tocheck_fields = [force_field] if force_field else self._sms_get_number_fields()
        for record in self:
            all_numbers = [record[fname] for fname in tocheck_fields if fname in record]
            all_partners = record._sms_get_default_partners()

            valid_number = False
            for fname in [f for f in tocheck_fields if f in record]:
                valid_number = phone_validation.phone_sanitize_numbers_w_record([record[fname]], record)[record[fname]][
                    'sanitized']
                if valid_number:
                    break

            if valid_number:
                result[record.id] = {
                    'partner': all_partners[0] if all_partners else self.env['res.partner'],
                    'sanitized': valid_number,
                    'number': record[fname],
                    'partner_store': False,
                    'field_store': fname,
                }
            elif all_partners and partner_fallback:
                partner = self.env['res.partner']
                for partner in all_partners:
                    for fname in self.env['res.partner']._sms_get_number_fields():
                        valid_number = \
                            phone_validation.phone_sanitize_numbers_w_record([partner[fname]], record)[partner[fname]][
                                'sanitized']
                        if valid_number:
                            break

                if not valid_number:
                    fname = 'mobile' if partner.mobile else ('phone' if partner.phone else 'mobile')

                result[record.id] = {
                    'partner': partner,
                    'sanitized': valid_number if valid_number else False,
                    'number': partner[fname],
                    'partner_store': True,
                    'field_store': fname,
                }
            else:
                # did not find any sanitized number -> take first set value as fallback;
                # if none, just assign False to the first available number field
                value, fname = next(
                    ((value, fname) for value, fname in zip(all_numbers, tocheck_fields) if value),
                    (False, tocheck_fields[0] if tocheck_fields else False)
                )
                result[record.id] = {
                    'partner': self.env['res.partner'],
                    'sanitized': False,
                    'number': value,
                    'partner_store': False,
                    'field_store': fname
                }
        return result

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            if rec.product_id.product_tmpl_id:
                demo = rec.move_id.vehicle_number.x_vehicle_number_id
                rec.update({'vehicle_id': demo})
                print("vehicle,", rec.vehicle_id)
                # if rec.product_id.product_tmpl_id.is_service_combo == True:
                #     rec.check = True
                #     my_date_months = rec.expiry_date + relativedelta(
                #         months=rec.product_id.product_tmpl_id.contract_duration)
                #     rec.expiry_date = my_date_months
                #     rec.update({'check': True, 'expiry_date': my_date_months})

    @api.onchange('product_id')
    def _onchange_product_id_set_expiry(self):
        """Set expiry_date only when Service Combo is selected."""
        if self.product_id:
            if self.product_id.product_tmpl_id.is_service_combo:
                # Set today's date if it's a Service Combo
                self.expiry_date = fields.Date.context_today(self)
            else:
                # Clear expiry date for non-Service Combo products
                self.expiry_date = False

    def unlink(self):
        # self.service_combo_unlink(res)
        for rec in self:
            if rec.move_id.move_type == 'out_invoice':
                task1_search = self.env['service.combo.tracker'].search([('account_move_line_id', '=', rec.id), (
                    'service_combo_id', '=',
                    rec.product_id.product_tmpl_id.id)])  # call create method of tasks.manager model
                if task1_search:
                    # update
                    for task1_delete in task1_search:
                        task1_delete.unlink()
        res = super(InheritInvoiceLine, self).unlink()
        return res

    # def write(self, vals):
    #     res = super(InheritInvoiceLine, self).write(vals)
    #     if 'expiry_date' in vals and self.move_id.move_type == 'out_invoice':
    #         self.service_combo_write(res)
    #     return res

    def create(self, vals):
        res = super(InheritInvoiceLine, self).create(vals)
        for rec in res:
            if rec.product_id.product_tmpl_id:
                # print("---",rec.product_id.product_tmpl_id,"----")
                # print("vahivale", rec.move_id.vehicle_number)
                demo = rec.move_id.vehicle_number.x_vehicle_number_id
                # rec.vehicle_id = demo
                rec.update({'vehicle_id': demo})
                print("vehicle,", rec.vehicle_id)
                if rec.product_id.product_tmpl_id.is_service_combo:
                    if not rec.expiry_date:  # only assign once
                        rec.check = True
                        my_date_months = date.today() + relativedelta(
                            months=rec.product_id.product_tmpl_id.contract_duration
                        )
                        rec.update({'check': True, 'expiry_date': my_date_months})

        if res.move_id.move_type == 'out_invoice':
            print('times for calling a function service combo')
            self.service_combo(res)
        return res

    def service_combo_write(self, res):
        print("hello i am service_bombo action...................service_combo_write")
        print(res)
        move_id = self  # self.env['account.move.line'].search([])[-1]
        services = self.env['service.combo.item'].search([])
        print("Order id", move_id)
        print("sale_combo_id", move_id.product_id.product_tmpl_id.id)
        order_combo_id = move_id.product_id.product_tmpl_id.id
        print("services", services)
        print("services_combo_id", services.service_combo_id)
        for combo in services:
            if combo.service_combo_id.id == order_combo_id:
                print("yes this is success.......")
                print("combo_id", combo.service_combo_id.id)
                print("service_id", combo.service_id.id)
                print("qunatity", combo.no_of_items)
                if combo.no_of_items == False or combo.no_of_items == 0:
                    # infinite service
                    task1_search = self.env['service.combo.tracker'].search([('account_move_line_id', '=', move_id.id),
                                                                             ('service_combo_id', '=',
                                                                              combo.service_combo_id.id), (
                                                                                 'service_id', '=',
                                                                                 combo.service_id.id)])  # call create method of tasks.manager model
                    if task1_search:
                        # update
                        for task1_update in task1_search:
                            task1_update.write({'is_infinite': True, 'expiry_date': move_id.expiry_date,
                                                'account_move_line_id': move_id.id,
                                                'service_combo_id': combo.service_combo_id.id,
                                                'service_id': combo.service_id.id, 'state': 'draft'})
                    else:
                        task1 = self.env['service.combo.tracker']  # call create method of tasks.manager model
                        task1.create({'is_infinite': True, 'expiry_date': move_id.expiry_date,
                                      'account_move_line_id': move_id.id, 'service_combo_id': combo.service_combo_id.id,
                                      'service_id': combo.service_id.id, 'state': 'draft'})
                else:
                    task1_search = self.env['service.combo.tracker'].search([('account_move_line_id', '=', move_id.id),
                                                                             ('service_combo_id', '=',
                                                                              combo.service_combo_id.id),
                                                                             ('service_id', '=', combo.service_id.id)])
                    if task1_search:
                        # update
                        for task1_update in task1_search:
                            task1_update.write({'expiry_date': move_id.expiry_date, 'account_move_line_id': move_id.id,
                                                'service_combo_id': combo.service_combo_id.id,
                                                'service_id': combo.service_id.id, 'state': 'draft'})
                    else:
                        for i in range(combo.no_of_items):
                            task1 = self.env['service.combo.tracker']  # call create method of tasks.manager model
                            task1.create({'expiry_date': move_id.expiry_date, 'account_move_line_id': move_id.id,
                                          'service_combo_id': combo.service_combo_id.id,
                                          'service_id': combo.service_id.id, 'state': 'draft'})

    def service_combo(self, res):

        # print("hello i am service_bombo action...................service_combo")
        # print(res)
        # move_id = res#self.env['account.move.line'].search([])[-1]
        for move_id in res:
            services = self.env['service.combo.item'].search([])
            # print("Order id",move_id)
            # print("sale_combo_id",move_id.product_id.product_tmpl_id.id)
            order_combo_id = move_id.product_id.product_tmpl_id.id
            # print("services",services)
            # print("services_combo_id",services.service_combo_id)
            for combo in services:
                if combo.service_combo_id.id == order_combo_id:
                    # print("yes this is success.......")
                    # print("combo_id",combo.service_combo_id.id)
                    # print("service_id",combo.service_id.id)
                    # print("qunatity",combo.no_of_items)
                    # print('combo.no_of_items',combo.no_of_items)

                    if combo.no_of_items == False or combo.no_of_items == 0:
                        # infinite service
                        task1 = self.env['service.combo.tracker']  # call create method of tasks.manager model
                        task1.create({'is_infinite': True, 'expiry_date': move_id.expiry_date,
                                      'account_move_line_id': move_id.id, 'service_combo_id': combo.service_combo_id.id,
                                      'service_id': combo.service_id.id, 'state': 'draft'})
                    else:
                        for i in range(combo.no_of_items):
                            # print('first time',i)
                            task1 = self.env['service.combo.tracker']  # call create method of tasks.manager model
                            # print('first time',i)
                            task1.create({'expiry_date': move_id.expiry_date, 'account_move_line_id': move_id.id,
                                          'service_combo_id': combo.service_combo_id.id,
                                          'service_id': combo.service_id.id, 'state': 'draft'})
                            # print('first time', i)
