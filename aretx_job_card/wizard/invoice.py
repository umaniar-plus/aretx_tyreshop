import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InvoiceWizard(models.TransientModel):
    _name = "invoice.wizard"
    _description = "Invoice Wizard"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def default_get(self, fields):
        res = super(InvoiceWizard, self).default_get(fields)
        res['invoice_date'] = datetime.date.today()
        if self.env.context.get('active_id'):
            res['job_id'] = self.env.context.get('active_id')
        return res

    job_id = fields.Many2one('job.card', string='Invoice')

    # reason = fields.Text(string='Reason', default='Test Reason....')
    invoice_date = fields.Date(string='Invoice Date')

    def action_invoice(self):
        if self.job_id.job_card_date == fields.Date.today():
            raise ValidationError(_("Invoiced Generated!!"))
        self.job_id.state = 'invoiced'
        return

    # def send_and_print_action(self):
    #     a1=self.env['account.invoice.send']
    #     a1.send_and_print_action({})

    # def create_invoice(self):
    #     invoice = self.env['job.card'].create({
    #         'type': 'out_invoice',
    #         'journal_id': job.id,
    #         'partner_id': product_id.id,
    #         'invoice_date': date_invoice,
    #         'date': date_invoice,
    #         'invoice_line_ids': [(0, 0, {
    #             'product_id': product_id.id,
    #             'quantity': 40.0,
    #             'name': 'product test 1',
    #             'discount': 10.00,
    #             'price_unit': 2.27,
    #         })]
    #     })
    # @api.onchange('job_id')
    # def onchange_job_id(self):
    #     self.ref = self.job_id.ref
