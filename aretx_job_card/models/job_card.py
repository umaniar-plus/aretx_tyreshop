from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import html_keep_url
from odoo.tools.misc import formatLang
import json


class sale_order(models.Model):
    _inherit = "sale.order"
    _description = "Sale Order Inherit "

    # @api.model
    # def create(self, vals):
    #     print('heloooooooooooooo')
    #     print('heloooooooooooooo')
    #     vals['partner_id'] = 7
    #     vals['partner_invoice_id'] = 7
    #     print(self)
    #     print(vals)
    #     print('heloooooooooooooo')
    #     print('heloooooooooooooo')
    #     insert_sale_order = super(sale_order, self).create(vals)
    #     return insert_sale_order

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()

        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._search_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).', self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'user_id': self.user_id.id,
            'invoice_user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': self.fiscal_position_id or False,
            'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'currency_id': self.company_id.currency_id.id,
            'vehicle_kms': self.vehicle_kms,
            'vehicle_number': self.x_vehicle_number_id.id,
        }
        return invoice_vals

    @api.model
    def get_sale_types(self, include_receipts=False):
        return ['out_invoice', 'out_refund'] + (include_receipts and ['out_receipt'] or [])

    @api.model
    def get_purchase_types(self, include_receipts=False):
        return ['in_invoice', 'in_refund'] + (include_receipts and ['in_receipt'] or [])


class JobCard(models.Model):
    _name = "job.card"
    _inherits = {'sale.order': 'order_id'}
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "JobCard Entry"
    _order = 'job_card_date desc, id desc'
    rec_name = 'name'

    # name = fields.Char("Invoice No")
    name = fields.Char(string='Job Card Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    # order_id = fields.Many2one('sale.order', required=True, string='Order Id', store=True, ondelete='cascade')
    order_id = fields.Many2one(
        comodel_name='sale.order',copy=False,
        auto_join=True,
        string='Order Id', required=True, readonly=True, ondelete='cascade',
        check_company=True)

    partner_id = fields.Many2one('res.partner', required=True, readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)]}, string='Customer Name', store=True, ondelete='cascade')
    # partner_id = fields.Many2one('res.partner', ondelete='cascade',  string='Customer Name', store=True, required=True)
    # partner_id = fields.Many2one(related='order_id.partner_id', store=True, string='Customer Name', readonly=False, tracking=True, required=True)
    # invoice_count = fields.Integer(related='order_id.invoice_count', store=True, string='Invoice Count', readonly=False, tracking=True)
    invoice_count = fields.Integer(string='Invoice Count', compute='_get_invoiced')
    invoice_ids = fields.Many2many("account.move", string='Invoices', compute="_get_invoiced", copy=False,search="_search_invoice_ids")
    # amount_remain = fields.Float(string='Total Amount Paid To Invoice', compute='_get_invoiced')


    picking_ids = fields.One2many('stock.picking', 'sale_id', string='Transfers')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')
    # invoice_count_compute = fields.Integer(compute='invoice_check', string='Invoice Count')

    # partner_invoice_id = fields.Many2one(related='order_id.partner_invoice_id', store=True, string='Customer Name', readonly=False, tracking=True, required=True)

    # partner_id = fields.Many2one('sale.order', required=True, string='Order Id', ondelete='cascade')
    # partner_id = fields.One2many('sale.order', 'partner_id', string="Customer Name", tracking=True, required=True,)
    # partner_id = fields.Many2one('res.partner', required=True, string="Customer Name", tracking=True)
    # partner_job_id = fields.Many2one('res.partner', required=True, string="Customer Name", tracking=True)
    # partner_id = fields.Many2one('sale.order', related="order_id.partner_id", default='partner_job_id.id', required=True, string="Customer Name", tracking=True)
    # partner_invoice_id = fields.Many2one('sale.order', related="order_id.partner_invoice_id", default='partner_job_id.id', required=True, string="Customer Name", tracking=True)
    vehicle = fields.Many2one('vehicle.master.model', required=True, tracking=True, string="Vehicle", domain="[('x_customer_id', '=', partner_id)]", ondelete='restrict')
    job_card_date = fields.Datetime('JobCard Date', required=True, tracking=True, default=fields.Datetime.now)  # readonly=True
    # state = fields.Selection([
    #     ('open', 'Open'), ('work_in_progress', 'Work In Progress'), ('waiting_for_material', 'Waiting For Material'),
    #     ('completed', 'Completed'), ('invoiced', 'Invoiced')],
    #     string='JobCard Satus', default='open', group_expand='_group_expand_states')

    state = fields.Selection([
        ('open', 'Open'), ('draft', 'Draft'), ('confirm', 'Confirm'), ('completed', 'Completed'), ('done', 'Done')],
        string='JobCard Satus', default='open', group_expand='_group_expand_states')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,default=lambda self: self.env.company)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', store=True, check_company=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )

    vehicle_kms = fields.Char(string='Vehicle KMS', store=True)
    advance_payment_invisible = fields.Boolean(string='Advance Payment Invisible', compute="_advance_payment_invisible", default=True)

    # state = fields.Selection(selection_add=[
    #     ('open', 'Open'),
    #     ('work_in_progress', 'Work In Progress'),
    #     ('waiting_for_material', 'Waiting For Material'),
    #     ('completed', 'Completed'),
    #     ('sale', 'Invoiced'),
    # ], string='JobCard Status', readonly=True, index=True)
    total = fields.Float(string="Total")
    total_compute = fields.Float(string="Total", compute="_get_total_amount")
    # total = fields.Integer(string="Total", compute="_get_subtotal_amount", store=True)
    confirmed_user_id = fields.Many2one('res.users', string='Confirmed User')
    total_advance = fields.Float(
        compute="_get_advance_payment", string="Total Paid", )
    total_refund = fields.Float(compute="_get_advance_payment", string="Total Refund", )
    balance = fields.Char(compute="_get_balance", string="Balance", )

    @api.model
    def _default_note_url(self):
        return self.env.company.get_base_url()

    @api.model
    def _default_note(self):
        use_invoice_terms = self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')
        if use_invoice_terms and self.env.company.terms_type == "html":
            baseurl = html_keep_url(self._default_note_url() + '/terms')
            return _('Terms & Conditions: %s', baseurl)
        return use_invoice_terms and self.env.company.invoice_terms or ''

    note = fields.Html('Terms and conditions', default=_default_note)




    @api.depends('partner_id')
    def _get_balance(self):
        balance = 0.00
        for rec in self:
            currency = rec.currency_id or rec.company_id.currency_id
            balance_format = formatLang(self.env, 0.00, currency_obj=currency, digits=2)
            cr_dr = ''
            if rec.partner_id.id:
                # // DEBIT
                self._cr.execute(
                    '''SELECT 
    SUM(aml.balance) AS total_balance
FROM 
    public.account_move_line aml
INNER JOIN 
    public.account_account aa 
    ON aml.account_id = aa.id
WHERE 
    aml.parent_state = 'posted' 
    AND aml.balance > 0 
    AND aa.account_type IN ('asset_receivable', 'liability_payable') 
    AND aml.partner_id = %s;
''', [rec.partner_id.id]
                )
                fetched_dr = self._cr.fetchone()
                dr = 0.00
                if len(fetched_dr) > 0 and None not in fetched_dr:
                    dr = fetched_dr[0]

                self._cr.execute(
                    '''SELECT 
    SUM(aml.balance) AS total_balance
FROM 
    public.account_move_line aml
INNER JOIN 
    public.account_account aa 
    ON aml.account_id = aa.id
WHERE 
    aml.parent_state = 'posted' 
    AND aml.balance < 0 
    AND aa.account_type IN ('asset_receivable', 'liability_payable') 
    AND aml.partner_id = %s;
''', [rec.partner_id.id]
                )
                fetched_cr = self._cr.fetchone()
                cr = 0.00
                if len(fetched_cr) > 0 and None not in fetched_cr:
                    cr = fetched_cr[0]
                balance = abs(dr) - abs(cr)
                balance_format = formatLang(self.env, abs(abs(dr) - abs(cr)), currency_obj=currency,digits=2)
                cr_dr = 'CR'
                if balance == 0:
                    cr_dr = ''
                elif balance > 0:
                    cr_dr = 'DR'
            rec.balance = balance_format+' '+cr_dr



    remaining_amt = fields.Float(compute="_get_advance_payment", string="Total Remaining Amount", )
    # refund_remaining_amt = fields.Float(compute="_get_advance_payment", string="Total Amount To Refund", )

    account_move_ids = fields.Many2many('account.move', 'job_sale_account_move_rel', 'job_id', 'move_id', "Payment Details", readonly="1")
    refund_account_move_ids = fields.Many2many('account.move', 'job_refund_sale_account_move_rel', 'job_id', 'move_id', "Refund Payment Details", readonly="1")

    # @api.ondelete(at_uninstall=True)
    # def _unlink(self):
    #     rem_seq = self.env['ir.sequence'].search([('code', '=', 'job.card')])
    #     for rem in rem_seq:
    #         rem.unlink()
    #
    # def init(self):
    #     return self.env['ir.sequence'].create({
    #         'name': 'Job Card',
    #         'code': 'job.card',
    #         'prefix': 'JC', 'padding': 5,
    #         # 'company_id': wh.company_id.id,
    #         # 'implementation': 'no_gap',
    #     })

    def _advance_payment_invisible(self):
        for rec in self:
            if rec.state in ['draft', 'confirm', 'completed']:
                if not rec.order_id:
                    rec.advance_payment_invisible = True
                else:
                    if rec.state in ['completed']:
                        not_paid_invoices = rec.order_id.order_line.invoice_lines.move_id.filtered(
                            lambda r: r.payment_state not in ('paid'))
                        print('not_paid_invoices')
                        print(not_paid_invoices)
                        print('not_paid_invoices')
                        if len(not_paid_invoices) > 0:
                            rec.advance_payment_invisible = False
                        else:
                            rec.advance_payment_invisible = True
                    else:
                        rec.advance_payment_invisible = False
            else:
                rec.advance_payment_invisible = True

    def action_view_delivery(self):
        return self.order_id.action_view_delivery()

    def advance_payment(self):
        job = self
        res_id = job
        # data_obj = self.env['ir.model.data'].sudo().search(
        #     [('name', '=', 'advance_payment_wizard1')])
        data_obj = self.env['ir.model.data'].sudo().search(
            [('name', '=', 'job_advance_payment_wizard1')]) #xml-view_id
        data_id = data_obj.id
        view_id1 = False
        if self._context is None:
            self._context = {}
        ctx = dict(self._context)
        ctx['active_ids'] = [job.id]
        ctx['job_id'] = res_id.id
        if data_id:
            view_id1 = data_obj.browse(data_id).res_id
        value = {
            'name': _('Deposit amount entry'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'job.advance.payment.wizard',
            'view_id': False,
            'context': ctx,
            'views': [(view_id1, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True
        }
        return value


    def refund_payment(self):
        job = self
        res_id = job
        # data_obj = self.env['ir.model.data'].sudo().search(
        #     [('name', '=', 'refund_payment_wizard1')])
        data_obj = self.env['ir.model.data'].sudo().search(
            [('name', '=', 'job_refund_payment_wizard1')]) #xml-view_id
        data_id = data_obj.id
        view_id1 = False
        if self._context is None:
            self._context = {}
        ctx = dict(self._context)
        ctx['active_ids'] = [job.id]
        ctx['job_id'] = res_id.id
        ctx['default_amt'] = abs(res_id.remaining_amt)
        # ctx['default_amt'] = abs(res_id.refund_remaining_amt)
        if data_id:
            view_id1 = data_obj.browse(data_id).res_id
        value = {
            'name': _('Refund amount entry'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'job.refund.payment.wizard',
            'view_id': False,
            'context': ctx,
            'views': [(view_id1, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True
        }
        return value

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for order in self:
            order.delivery_count = len(order.order_id.picking_ids)

    @api.depends('total', 'total_compute')
    def _get_advance_payment(self):

        sum = 0.00
        remaining = 0.00
        for obj in self:
            obj.update({
                'total_advance': 0.0,
                'total_refund': 0.0,
                'remaining_amt': 0.0,
                # 'refund_remaining_amt': 0.0,
            })
            sum = 0
            refund_sum = 0
            paid_invoiced = 0

            for line in obj.account_move_ids:
                move_lines = self.env['account.move.line'].search(
                    [('move_id', '=', line.id)])
                if move_lines:
                    for mv in move_lines:
                        sum = sum + mv.debit

            #calculate invoice partial payment and increment sum of advance
            # for inv_id in obj.invoice_ids:
            #     sum = sum + inv_id.amount_remain

                # line_ids
                # account_payment_register = self.env['account.payment.register'].search([])
                # list_account_payment_register = []
                # for pay_rec in account_payment_register:
                #     print('pay_rec')
                #     print(pay_rec)
                #     print('pay_rec')
                #     for pay_line in pay_rec.line_ids:
                #         list_account_payment_register.append(pay_line.id)
                #
                # if inv_line_id in account_payment_register.line_ids:
                #     print('account_payment_register')
                #     print(account_payment_register)
                #     print(account_payment_register.line_ids.index(inv_line_id))
                #     print(account_payment_register.line_ids)
                #     print(obj.invoice_ids.line_ids)
                #     print('account_payment_register')
                # for pay_rec in account_payment_register:
                #     print('pay_rec')
                #     print(pay_rec)
                #     print('pay_rec')
                #     # pay_rec.line_ids
                #     # paid_amt = pay_rec.line_ids.filtered(lambda r: r.payment_state not in ('paid'))
                #     # for pay_line in pay_rec.line_ids:
                #     #     print('pay_line')
                #     #     print(pay_line)
                #     #     print(inv_line_id)
                #     #     print('pay_line')
                #     #     if pay_line.id == inv_line_id.id:
                #     #         print('inv_line')
                #     #         print(inv_line_id)
                #     #         print(pay_rec.amount)
                #     #         # print(pay_rec.amount)
                #     #
                #     #         print('inv_line')
                #     #         sum = sum + pay_rec.amount


            for line2 in obj.refund_account_move_ids:
                move_lines2 = self.env['account.move.line'].search(
                    [('move_id', '=', line2.id)])
                if move_lines2:
                    for mv2 in move_lines2:
                        refund_sum = refund_sum + mv2.debit

            paid_invoices = obj.order_id.order_line.invoice_lines.move_id.filtered(lambda r: r.payment_state in ('paid'))
            paid_invoiced = 0.00
            if paid_invoices:
                for mv in paid_invoices:
                    paid_invoiced += mv.amount_total
                # paid_invoiced = sum(mv.mapped(mv.amount_currency) for mv in paid_invoices)

            if sum < paid_invoiced:
                total = obj.amount_total - paid_invoiced
            else:
                total = (obj.amount_total - sum) + refund_sum

            # total = obj.amount_total - obj.amount_remain
            # total = obj.amount_remain
            # remain = sum - refund_sum
            # remain = (total - sum) + refund_sum
            # remain = (obj.amount_total - sum) + refund_sum
            obj.update({
                'total_advance': sum,
                'total_refund': refund_sum,
                'remaining_amt': total,#obj.amount_total - sum
                # 'refund_remaining_amt': remain#obj.amount_total - sum
            })

    @api.depends('order_id.order_line.invoice_lines')
    def _get_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            invoices = order.order_id.order_line.invoice_lines.move_id.filtered(
                lambda r: r.move_type in ('out_invoice', 'out_refund'))

            # invoices2 = order.order_id.order_line.invoice_lines.filtered(
            #     lambda r: r.reconciled == True)
            # print('invoices2')
            # print(invoices2)
            # print('invoices2')
            # if len(invoices2) == 0:
            #     total = order.amount_total
            #     sum = 0
            #
            #     for line in order.account_move_ids:
            #         move_lines = self.env['account.move.line'].search(
            #             [('move_id', '=', line.id)])
            #         if move_lines:
            #             for mv in move_lines:
            #                 sum = sum + mv.debit
            #     total = total - sum
            #     order.amount_remain = total
            # else:
            #     order.amount_remain = sum(mv.amount_currency for mv in invoices2)

            # order.amount_remain = sum(mv.amount_currency for mv in invoices2)
            # order.amount_remain = sum(mv.amount_remain for mv in invoices)
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)
            if order.order_id is not False and order.invoice_count == 0 and order.state in ['completed', 'done']:
                order.state = 'confirm'

    def _search_invoice_ids(self, operator, value):
        return self.order_id._search_invoice_ids(self, operator, value)


    def action_view_invoice(self):
        return self.order_id.action_view_invoice()

    # @api.depends('invoice_count')
    # @api.onchange('invoice_count')
    # def onchange_invoice_count(self):
    #     print('heloooo')
    #     print('heloooo')
    #     print('heloooo')
    #     print(self)
    #     print(self.invoice_count)
    #     print('heloooo')
    #     print('heloooo')
    #     print('heloooo')
        # for rec in self:
        #     if rec.order_id is not False and rec.invoice_count == 0 and rec.state in ['completed', 'done']:
        #         rec.state = 'confirm'

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None, ):
        raise UserError(_('You can not duplicate job card, please create new.'))
    #     context = self._context or {}
    #     default = dict(default or {}, name=_("%s (Copy)") % self.name)
    #     context_wo_lang = dict(context or {})
    #     context_wo_lang.pop('lang', None)
    #     context = context_wo_lang
    #     job = self.browse(self._ids)
    #     if context.get('variant'):
    #         # if we copy a variant or create one, we keep the same template
    #         default['order_id'] = job.order_id.id
    #     elif 'name' not in default:
    #         # seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(job_card_date']))
    #         # valsdefault['name'] = self.env['ir.sequence'].next_by_code('job.card', sequence_date=seq_date) or _('New')
    #         default['name'] = _("%s (copy)") % (job.name,)
    #
    #     items = []
    #     for item in job.x_job_card_ids:
    #         items.append(item.copy())
    #
    #     print('items')
    #     print('items')
    #     print('items')
    #     print(items)
    #     print('items')
    #     print('items')
    #     print('items')
    #     # default['x_job_card_ids'] = job.x_job_card_ids.copy()
    #     # default['x_job_card_ids'] = for item in items
    #
    #     # print('default')
    #     # print(default)
    #     # print(job)
    #     # print('default')
    #     return super(JobCard, self).copy(default=default)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self._get_balance()
        if self.partner_id:
            if self.vehicle not in self.partner_id.x_vehicle_number_ids:
                self.vehicle = ''
        if self.ids:
            return self.order_id.onchange_partner_id()


    #     print('change')
    #     print('change')
    #     print('change')
    #     if self.partner_id:
    #         print('change2')
    #         print('change2')
    #         print(self.order_id)
    #         print(self.order_id.name)
    #         print(self.partner_id)
    #         self.order_id.partner_id = self.partner_id
    #         self.order_id.partner_invoice_id = self.partner_id
    #         print(self.order_id.partner_id)
    #         print('change2')
    #         return self.order_id.partner_id.id#self.order_id.onchange_partner_id()
            # return self.order_id.onchange_partner_id()
    # def create_invoices(self):
    #     return {
    #         # 'name': self.x_vehicle_number_id,  # 'account.move.view',
    #         'res_model': 'account.move',
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'tree,form',
    #         'view_mode': 'tree,form',
    #         # 'view_mode': 'tree,form',
    #         # 'view_id': self.env.ref('sale.view_sale_advance_payment_inv').id
    #         # 'view_id': self.env.ref('base.view_partner_form').id
    #         # 'view_id': self.env.ref('account.view_out_invoice_tree').id,
    #         # 'domain': [('vehicle_number', '=', self.x_vehicle_number_id)],
    #         # 'target': 'list'
    #         # 'target': 'new'
    #
    #     }

    # def _create_invoices(self, grouped=False, final=False, date=None):
    #     print("invoiced print..................................")
    #
    #     invoice_vals = super(JobCard, self)._create_invoice()
    #     invoice_vals['vehicle_number'] = self.x_vehicle_number_id.id
    #     print("invoice vals", invoice_vals)
    #     return invoice_vals

    def invoice_report(self):
        return self.env.ref('job_card.action_report_job_card').report_action(self)

    def print_report(self):
        return self.env.ref('job_card.action_report_job_card').report_action(self)

    def _group_expand_states(self, state, domain, order):
        return [key for
                key, val in type(self).state.selection]

    # def action_draft(self):
    #     for rec in self:
    #         if rec.state == "confirm":
    #             # rec.order_id.action_confirm()
    #             rec.order_id.write({'state': 'draft'})
    #             rec.state = 'draft'

    def create_invoices(self):
        for rec in self:
            # self.env.context.set('active_id', rec.order_id.id)
            # self.env.context.set('active_model', 'sale.order')
            for st in rec.order_id.picking_ids:
                # st.with_context(active_id=st.id, active_model='stock.picking').action_set_quantities_to_reservation()
                st.with_context(active_id=st.id, active_model='stock.picking').button_validate()
            rec.order_id.with_context(active_id=rec.order_id.id, active_model='sale.order')._create_invoices()
            rec.state = 'completed'
            # if not rec.order_id and rec.order_id.invoice_status != 'to invoice':
            #     raise UserError(_("The selected Sales Order should contain something to invoice."))
            # rec.order_id._amount_all()
            # action = rec.env["ir.actions.actions"]._for_xml_id("sale.action_view_sale_advance_payment_inv")
            # action['context'] = {
            #     'active_ids': rec.order_id.ids
            # }
            # return action


    def action_done(self):
        for rec in self:
            if rec.state == "completed":
                if rec.order_id is not False and rec.invoice_count == 0 and rec.state in ['completed', 'done']:
                    rec.state = 'confirm'
                else:
                    rec.order_id.write({'state': 'done'})
                    # rec.order_id.action_done()
                    rec.state = 'done'

    def action_completed(self):
        for rec in self:
            rec.state = 'completed'

    def action_waiting_for_material(self):
        for rec in self:
            rec.state = 'waiting_for_material'

    def action_confirm(self):
        for rec in self:
            if rec.state == "draft":
                # rec.order_id.write({'state': 'sale'})
                rec.order_id.action_confirm()
                rec.state = 'confirm'

    # inherited fields
    # x_job_card_ids = fields.One2many('job.card.line', 'job_id', string="job Card")
    x_job_card_ids = fields.One2many('job.card.line', 'job_id', 'Job Card Line', states={'completed': [('readonly', True)], 'done': [('readonly', True)]}, copy=False, auto_join=True)
    # x_product_ids = fields.One2many('job.card.line', 'x_product_id', string="Product Name")
    x_quantity = fields.One2many('job.card.line', 'quantity', string="Quantity")
    x_uom = fields.One2many('job.card.line', 'product_uom_id', string="UoM")
    x_price = fields.One2many('job.card.line', 'price', string="Price")
    x_discount = fields.One2many('job.card.line', 'discount', string="Discount")
    # x_taxes = fields.One2many('job.card.line', 'tax_ids', string="Taxes")
    x_subtotal = fields.One2many('job.card.line', 'subtotal', string="Subtotal")
    # untaxed_amt = fields.Float(compute="_get_subtotal_amount", string="Untaxed Amount")
    # total_tax = fields.Float(string="Taxes", compute="_get_total_tax")
    untaxed_amt = fields.Float(string="Untaxed Amount")
    total_tax = fields.Float(string="Taxes")
    untaxed_amt_compute = fields.Float(string="Untaxed Amount", compute="_get_subtotal_amount")
    total_tax_compute = fields.Float(string="Taxes", compute="_get_total_tax")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,default=lambda self: self.env.user.company_id.currency_id.id)
    # amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')

    # @api.onchange('x_job_card_ids','x_quantity','x_price','x_discount','x_subtotal')
    @api.depends('x_job_card_ids','x_quantity','x_price','x_discount','x_subtotal')
    def _get_total_amount(self):
        val1 = 0.0
        total1 = 0.0
        grand_total = 0.0
        for obj in self:
            for line in obj.x_job_card_ids:
                total1 += line.subtotal
                val1 += self._amount_line_tax(line)
            grand_total = total1 + val1
            if obj.currency_id:
                obj.update({
                    'total': obj.currency_id.round(grand_total),#obj.currency_id.round(val1),
                    'total_compute': obj.currency_id.round(grand_total),#obj.currency_id.round(val1),
                })
            # print('obj.total')
            # print(obj.total)
            # print('obj.total')
            # obj.total = grand_total

    @api.onchange('x_job_card_ids', 'x_quantity', 'x_price', 'x_discount', 'x_subtotal')
    def _get_subtotal_amount(self):
        total = 0.0
        for obj in self:
            for line in obj.x_job_card_ids:
                total += line.subtotal
                # print('Line Subtotal : ', line.subtotal)
            obj.update({
                'untaxed_amt': obj.currency_id.round(total),
                'untaxed_amt_compute': obj.currency_id.round(total),
            })

    @api.onchange('x_job_card_ids', 'x_quantity', 'x_price', 'x_discount', 'x_subtotal')
    def _get_total_tax(self):
        # get total tax on the room
        val1 = 0.0
        total1 = 0.0
        for obj in self:
            for line in obj.x_job_card_ids:
                total1 += line.subtotal
                val1 += self._amount_line_tax(line)
            if obj.currency_id:
                obj.update({
                    'total_tax': obj.currency_id.round(val1),
                    'total_tax_compute': obj.currency_id.round(val1),
                })

    def _amount_line_tax(self, line):
        val = 0.0
        taxes = line.tax_ids.compute_all(
            line.price * (1 - (line.discount or 0.0) / 100.0), quantity=line.quantity)
        val = taxes['total_included'] - taxes['total_excluded']
        return val

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                                  [(state, view)
                                   for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        # context = {
        #     'default_type': 'out_invoice',
        # }
        context = {}
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or
                                                   self.env['account.move'].default_get(
                                                       ['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.mapped('name'),
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action


    @api.model
    def create(self, vals):
        print(vals)
        job = self.env['sale.order'].create({
            'partner_id': vals['partner_id'],#self.partner_id.id,
            'partner_invoice_id': vals['partner_id'],#self.partner_id.id,
            'amount_untaxed': vals['untaxed_amt'],
            'amount_tax': vals['total_tax'],
            'amount_total': vals['total'],
            'date_order': vals['job_card_date'],
            'x_vehicle_number_id': vals['vehicle'],
            'vehicle_kms': vals['vehicle_kms'],
            'note': vals['note'],
            'payment_term_id': vals['payment_term_id'],
            # 'is_enabled_roundoff': vals['is_enabled_roundoff'],
            # 'amount_round_off': vals['amount_round_off'],
            # 'state': 'done'
            # 'date_order': reservation.date_order,
            # 'shop_id': reservation.shop_id.id,
            # 'pricelist_id': reservation.pricelist_id.id,
            # 'vehicle':self.vehicle,
            # 'job_card_date':self.job_card_date
            # 'partner_shipping_id': reservation.partner_id.id,

            #                 'checkin_date': line.checkin,
            #                 'checkout_date': line.checkout,
            # 'reservation_id': reservation.id,
            # 'duration': line1.number_of_days,
            # 'note': reservation.note,
            # 'service_lines': reservation.other_items_ids,
        })
        vals['order_id'] = job.id
        vals['state'] = 'draft'
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'job_card_date' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['job_card_date']))
            vals['name'] = self.env['ir.sequence'].next_by_code('job.card', sequence_date=seq_date) or _('New')
        job_id = super(JobCard, self).create(vals)
        return job_id#super(JobCard, self).write({'partner_id':7})
        # tmp_job_card_lines = vals.get('x_job_card_ids', [])
        # if "job_id" not in vals:
        #     vals.update({'x_job_card_ids': []})
        #     job_id = super(JobCard, self).create(vals)
        #     for line in tmp_job_card_lines:
        #         line[2].update({'job_id': job_id})
        #     vals.update(
        #         {'x_job_card_ids': tmp_job_card_lines})
        #     super(JobCard, self).write(vals)
        #
        # else:
        #     job_id = super(JobCard, self).create(vals)
        # return job_id

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'open'):
                raise UserError(_('You can not delete job card after processed.'))
            if rec.order_id:
                rec.order_id.unlink()
        job_id = super(JobCard, self).unlink()
        return job_id

    # @api.model
    def write(self, vals):
        # print('11111111sdhajskdhasjkdhasjkdhak')
        # print('111111111sdhajskdhasjkdhasjkdhak')
        # print(self)
        # # print(id)
        # print(vals)
        if vals:
            job_master = self
            update_vals = {}
            if 'partner_id' in vals:
                update_vals['partner_id'] = vals['partner_id']
                update_vals['partner_invoice_id'] = vals['partner_id']
            if 'untaxed_amt' in vals:
                update_vals['amount_untaxed'] = vals['untaxed_amt']
            if 'total_tax' in vals:
                update_vals['amount_tax'] = vals['total_tax']
            if 'total' in vals:
                update_vals['amount_total'] = vals['total']
            if 'job_card_date' in vals:
                update_vals['date_order'] = vals['job_card_date']
            if 'vehicle' in vals:
                update_vals['x_vehicle_number_id'] = vals['vehicle']
            if 'vehicle_kms' in vals:
                update_vals['vehicle_kms'] = vals['vehicle_kms']
            if 'payment_term_id' in vals:
                update_vals['payment_term_id'] = vals['payment_term_id']
            if 'note' in vals:
                update_vals['note'] = vals['note']
            # if 'is_enabled_roundoff' in vals:
            #     update_vals['is_enabled_roundoff'] = vals['is_enabled_roundoff']
            # if 'amount_round_off' in vals:
            #     update_vals['amount_round_off'] = vals['amount_round_off']
            job_master.order_id.write(update_vals)
            vals['order_id'] = job_master.order_id

        job_id = super(JobCard, self).write(vals)
        return job_id
        # print('sdhajskdhasjkdhasjkdhak')
        # return True
        # if 'partner_id' in vals:
        #     pass
        # job = self.env['sale.order'].create({
        #     'partner_id': vals['partner_id'],  # self.partner_id.id,
        #     'partner_invoice_id': vals['partner_id'],  # self.partner_id.id,
        #     'amount_untaxed': vals['untaxed_amt'],
        #     'amount_tax': vals['total_tax'],
        #     'amount_total': vals['total'],
        #     'date_order': vals['job_card_date'],
        #     'x_vehicle_number_id': vals['vehicle'],
        #     # 'state': 'done'
        #     # 'date_order': reservation.date_order,
        #     # 'shop_id': reservation.shop_id.id,
        #     # 'pricelist_id': reservation.pricelist_id.id,
        #     # 'vehicle':self.vehicle,
        #     # 'job_card_date':self.job_card_date
        #     # 'partner_shipping_id': reservation.partner_id.id,
        #
        #     #                 'checkin_date': line.checkin,
        #     #                 'checkout_date': line.checkout,
        #     # 'reservation_id': reservation.id,
        #     # 'duration': line1.number_of_days,
        #     # 'note': reservation.note,
        #     # 'service_lines': reservation.other_items_ids,
        # })
        # vals['order_id'] = job.id
        # job_id = super(JobCard, self).create(vals)
        # return job_id

        # return self.order_id.onchange_partner_id()


class JobCardLine(models.Model):
    _name = "job.card.line"
    _description = "Job Card Line"
    _inherits = {'sale.order.line': 'order_line_id'}
    _check_company_auto = True

    name = fields.Text(string='Description', required=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(string='Sequence', default=10)
    order_line_id = fields.Many2one('sale.order.line', copy=False, string='order_line_id', ondelete='cascade', required=True, )
    job_id = fields.Many2one('job.card', string='Job Card Entry', ondelete='cascade')
    currency_id = fields.Many2one(related='job_id.currency_id', store=True, string='Currency', readonly=True)
    x_product_id = fields.Many2one('product.template', string="Product Name")
    quantity = fields.Float('Quantity',default=1.0)
    product_uom_id = fields.Many2one('uom.uom', related='x_product_id.uom_id', readonly=True)
    qty_invoiced = fields.Float(
        compute='_compute_qty_invoiced', string='Invoiced Quantity', store=True,
        digits='Product Unit of Measure')
    # product_updatable = fields.Many2one(related='order_line_id.product_updatable')
    # product_uom_readonly = fields.Many2one(related='order_line_id.product_uom_readonly')

    # product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure',
    #                                  domain="[('category_id','=',product_uom_id)]")

    price = fields.Float('Price')
    discount = fields.Float('Discount (%)', digits=(16, 2))
    # price = fields.Float(string="Price", related='x_product_id.price')
    tax_ids = fields.Many2many('account.tax', 'job_card_taxes_rel', 'job_card_line_id', 'tax_id', 'Taxes', domain=[
        ('type_tax_use', 'in', ['sale', 'all'])])
    # tax_ids = fields.Many2one(comodel_name='account.tax', string="Taxes")
    subtotal = fields.Float('Subtotal', compute='count_subtotal', store="True")
    # subtotal = fields.Float('Subtotal', compute='_compute_total')
    # g_total = fields.Integer(string='Grand Total')

    @api.depends('order_line_id.invoice_lines.move_id.state', 'order_line_id.invoice_lines.quantity', 'order_line_id.untaxed_amount_to_invoice')
    def _compute_qty_invoiced(self):
        """
        Compute the quantity invoiced. If case of a refund, the quantity invoiced is decreased. Note
        that this is the case only if the refund is generated from the SO and that is intentional: if
        a refund made would automatically decrease the invoiced quantity, then there is a risk of reinvoicing
        it automatically, which may not be wanted at all. That's why the refund has to be created from the SO
        """
        for line in self.order_line_id:
            qty_invoiced = 0.0
            for invoice_line in line._get_invoice_lines():
                if invoice_line.move_id.state != 'cancel':
                    if invoice_line.move_id.move_type == 'out_invoice':
                        qty_invoiced += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
                                                                                      line.product_uom)
                    elif invoice_line.move_id.move_type == 'out_refund':
                        qty_invoiced -= invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
                                                                                      line.product_uom)
            line.qty_invoiced = qty_invoiced

    @api.onchange('x_product_id')
    def _change_price(self):
        self.price = self.x_product_id.list_price
        for line in self:
            line.tax_ids = line.x_product_id.taxes_id
            line.name = line.x_product_id.name
        # self.product_uom_id = self.x_product_id.product_uom_id

    # contract_end_date = "29/2/2022"

    @api.depends('quantity', 'discount', 'price', 'tax_ids')
    def count_subtotal(self):
        for line in self:
            tax_amount = 0
            price = line.price * (1 - (line.discount or 0.0) / 100.0)
            product_product_master = self.env['product.product'].search(
                [('product_tmpl_id', '=', line.x_product_id.id)])
            if product_product_master:

                taxes = line.tax_ids.compute_all(price, line.job_id.currency_id, line.quantity,
                                              product=product_product_master[0],
                                              partner=line.job_id.order_id.partner_id)

                for tax in taxes['taxes']:
                    tax_amount = tax_amount + tax['amount']

                line.update({
                    'subtotal': taxes['total_excluded'],
                })

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id
            # product_browse = self.product_id
            # pricelist = self.folio_id.pricelist_id.id

            # ctx = self._context and self._context.copy() or {}
            # ctx.update({'date': self.checkin_date})

            price = self.product_id.price

            self.price_unit = price
            self.name = self.product_id.description_sale

    @api.model
    def create(self, vals):
        product_master = self.env['product.template'].browse(vals['x_product_id'])
        product_product_master = self.env['product.product'].search([('product_tmpl_id', '=', vals['x_product_id'])])
        job_master = self.env['job.card'].browse(vals['job_id'])
        # print('asdhaskdhasjkdhasjk')
        # print('asdhaskdhasjkdhasjk')
        # print('asdhaskdhasjkdhasjk')
        # print(self)
        # print(vals)
        # print('asdhaskdhasjkdhasjk')
        # print('asdhaskdhasjkdhasjk')
        # print('asdhaskdhasjkdhasjk')
        if product_product_master:
            sale_order_line_vals = {
                'order_id': job_master.order_id.id,
                'product_id': product_product_master[0].id,#product_master.id,
                # 'name': product_master.name,
                'name': vals['name'],
                'product_uom': product_master.uom_id.id,
                'price_unit': vals['price'],
                'product_uom_qty': vals['quantity'],
                'discount': vals['discount'],
                'tax_id': vals['tax_ids'],
            }
        else:
            sale_order_line_vals = {
                'order_id': job_master.order_id.id,
                'display_type': vals['display_type'],
                'product_id': False,
                'name': vals['name'],
                'product_uom': False,
                'customer_lead': 0,
                'price_unit': 0,
                'product_uom_qty': 0,
                'discount': vals['discount'],
                'tax_id': vals['tax_ids'],
            }

        if 'expiry_date' in vals:
            sale_order_line_vals['expiry_date'] = vals['expiry_date']
        if 'check' in vals:
            sale_order_line_vals['check'] = vals['check']
        if 'vehicle_id' in vals:
            sale_order_line_vals['vehicle_id'] = vals['vehicle_id']
        # job_line = self.env['sale.order.line'].create({
        #     'order_id': job_master.order_id.id,
        #     'product_id': product_master.id,
        #     'name': product_master.name,
        #     'product_uom': product_master.uom_id.id,
        #     'price_unit': vals['price'],
        #     'product_uom_qty': vals['quantity'],
        #     'discount': vals['discount'],
        #     'tax_id': vals['tax_ids'],
        # })
        job_line = self.env['sale.order.line'].create(sale_order_line_vals)
        vals['order_line_id'] = job_line.id
        # job_line_id = super(JobCardLine, self).create(vals)
        job_line_id = super().create(vals)
        return job_line_id  # super(JobCard, self).write({'partner_id':7})
        # tmp_job_card_lines = vals.get('x_job_card_ids', [])
        # if "job_id" not in vals:
        #     vals.update({'x_job_card_ids': []})
        #     job_id = super(JobCard, self).create(vals)
        #     for line in tmp_job_card_lines:
        #         line[2].update({'job_id': job_id})
        #     vals.update(
        #         {'x_job_card_ids': tmp_job_card_lines})
        #     super(JobCard, self).write(vals)
        #
        # else:
        #     job_id = super(JobCard, self).create(vals)
        # return job_id

        # @api.model

    def unlink(self):
        for rec in self:
            if rec.order_line_id:
                rec.order_line_id.unlink()
        job_line_id = super(JobCardLine, self).unlink()
        return job_line_id

    def write(self, vals):
        # print('sdhajskdhasjkdhasjkdhak')
        # print('sdhajskdhasjkdhasjkdhak')
        # print(self)
        # # print(id)
        # print(vals)
        # print(self.order_line_id)
        #
        if vals:
            update_vals = {}
            for rec in self:
                job_line_master = rec#self
                job_master = self.env['job.card'].browse(job_line_master.job_id.id)
                if 'order_id' in vals:
                    update_vals['order_id'] = vals['order_id']#job_master.order_id.id
                if 'x_product_id' in vals:
                    product_master = self.env['product.template'].browse(vals['x_product_id'])
                    update_vals['product_id'] =  product_master.id
                    # update_vals['name'] = product_master.name
                    update_vals['product_uom'] = product_master.uom_id.id
                if 'name' in vals:
                    update_vals['name'] = vals['name']
                if 'price' in vals:
                    update_vals['price_unit'] = vals['price']
                if 'quantity' in vals:
                    update_vals['product_uom_qty'] = vals['quantity']
                if 'discount' in vals:
                    update_vals['discount'] = vals['discount']
                if 'tax_ids' in vals:
                    update_vals['tax_id'] = vals['tax_ids']
                if 'expiry_date' in vals:
                    update_vals['expiry_date'] = vals['expiry_date']
                if 'check' in vals:
                    update_vals['check'] = vals['check']
                if 'vehicle_id' in vals:
                    update_vals['vehicle_id'] = vals['vehicle_id']

                print(update_vals)
                # job_master.order_id.write({'order_line':update_vals})
                # job_line_master.order_line_id.write({'price_unit':7800})
                job_line_master.order_line_id.write(update_vals)
                vals['order_line_id'] = job_line_master.order_line_id.id

        job_line_id = super(JobCardLine, self).write(vals)
        return job_line_id
        # print('sdhajskdhasjkdhasjkdhak')
        # return True
        # if 'partner_id' in vals:
        #     pass
        # job = self.env['sale.order'].create({
        #     'partner_id': vals['partner_id'],  # self.partner_id.id,
        #     'partner_invoice_id': vals['partner_id'],  # self.partner_id.id,
        #     'amount_untaxed': vals['untaxed_amt'],
        #     'amount_tax': vals['total_tax'],
        #     'amount_total': vals['total'],
        #     'date_order': vals['job_card_date'],
        #     'x_vehicle_number_id': vals['vehicle'],
        #     # 'state': 'done'
        #     # 'date_order': reservation.date_order,
        #     # 'shop_id': reservation.shop_id.id,
        #     # 'pricelist_id': reservation.pricelist_id.id,
        #     # 'vehicle':self.vehicle,
        #     # 'job_card_date':self.job_card_date
        #     # 'partner_shipping_id': reservation.partner_id.id,
        #
        #     #                 'checkin_date': line.checkin,
        #     #                 'checkout_date': line.checkout,
        #     # 'reservation_id': reservation.id,
        #     # 'duration': line1.number_of_days,
        #     # 'note': reservation.note,
        #     # 'service_lines': reservation.other_items_ids,
        # })
        # vals['order_id'] = job.id
        # job_id = super(JobCard, self).create(vals)
        # return job_id

        # return self.order_id.onchange_partner_id()

    # @api.model
    # def create(self, vals):
    #     if not self._context:
    #         self._context = {}
    #     if "job_id" in vals:
    #         job = self.env["job.card"].browse([vals['job_id']])[0]
    #         # self.env["product.product"].browse(
    #         #     vals['product_id']).write({'state': 'sellable'})
    #         vals.update({'order_id': job.order_id.id})
    #         # print("sssssssssssssssss",self._context.get('active_ids'))
    #
    #     jobline = super(JobCardLine, self).create(vals)
    #
    #     return jobline

    @api.depends('quantity', 'price')
    def _compute_total(self):

        check = 0
        for rec in self:

            if rec.quantity:
                rec.subtotal = rec.price * rec.quantity
                check = check + rec.subtotal
                print("total", rec.subtotal)
                print("job_id",rec.job_id.id)
                # rec.total = rec.total + rec.subtotal
            else:
                rec.quantity = 0
        # print("subtotal", rec.subtotal)
        self.g_total = check
        for rec in self:
            if rec.job_id.id:
                print("good bye")
                print("job_id",rec.job_id.id)

                total = self.env['job.card'].search([('id', '=', rec.job_id.id)])

                total.total = check

        print("check", check)
        # print("Main Total", rec.g_total)
        # print("rec_total", rec.g_total)


class CustomerJobCard(models.Model):
    _inherit = 'res.partner'

    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
    #     args = args or []
    #     domain = []
    #     if name:
    #         # domain = ['|', ('name', operator, name), ('phone', operator, name), ('x_vehicle_number_ids', operator, name)]
    #         domain = ['|', '|', ('name', operator, name), ('phone', operator, name), ('x_vehicle_number_ids', operator, name)]
    #     return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

# class Sale_Job_Card(models.Model):
#     _inherit = 'job.card'
#     _inherits = {'sale.order': 'order_id'}
#     order_id = fields.Many2one(
#         comodel_name='sale.order',
#         auto_join=True,
#         string='Order Id', required=True, readonly=True, ondelete='cascade',
#         check_company=True)