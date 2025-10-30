from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ClaimReport(models.Model):
    _name = "claim.report"
    _description = "Claim Report"
    _order = "date desc, id desc"

    name = fields.Char(string="Claim Number", required=True, readonly=True, copy=False, default="New")
    partner_id = fields.Many2one("res.partner", string="Customer", required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today)
    note = fields.Text(string="Internal Note")
    line_ids = fields.One2many("claim.report.line", "claim_id", string="Claim Lines")
    state = fields.Selection([
        ("pending", "Pending"),
        ("pass", "Pass"),
        ("fail", "Failed"),
        # ("cancelled", "Cancelled"),
    ], default="pending", string="Status")


    def action_cancel(self):
        self.write({"state": "fail"})

    def action_done(self):
        self.write({"state": "pass"})

    def action_print_report(self):
        return self.env.ref("adv_features.action_report_claim_report").report_action(self)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("claim.report") or "New"
        return super().create(vals_list)


class ClaimReportLine(models.Model):
    _name = "claim.report.line"
    _description = "Claim Report Line"

    claim_id = fields.Many2one("claim.report", string="Claim Report", ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Product", required=True)
    description = fields.Char(string="Description")
    qty = fields.Float(string="Quantity", default=1.0)