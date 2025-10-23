from.import models
from.import wizard


from odoo import api, SUPERUSER_ID

def _create_seq(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.sequence'].create({
        'name': 'Job Card',
        'code': 'job.card',
        'prefix': 'JC', 'padding': 5,
        # 'company_id': wh.company_id.id,
        # 'implementation': 'no_gap',
    })

def _uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rem_seq = env['ir.sequence'].search([('code', '=', 'job.card')])
    for rem in rem_seq:
        rem.unlink()

