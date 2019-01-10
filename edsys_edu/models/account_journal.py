from odoo import models, fields, api, _
from datetime import date,datetime

class account_journal(models.Model):
    _inherit = "account.journal"
    
    is_cheque=fields.Boolean('Is Cheque Journal')
    online_payment = fields.Boolean(string='Online Payment')
    advance_reconcillation_journal = fields.Boolean(string='Advance Reconcillation')

