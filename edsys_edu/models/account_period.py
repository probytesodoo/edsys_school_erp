from odoo import models, fields, api, _
from datetime import date,datetime




class account_invoice_inherit(models.Model):
    _inherit = "account.invoice"


    # period_id_id = fields.Char(string='Force Period')
    period_id = fields.Many2one('account.period', string='Force Period',
        domain=[('state', '!=', 'done')], copy=False,
        help="Keep empty to use the period of the validation(invoice) date.",
        readonly=True, states={'draft': [('readonly', False)]})
        


