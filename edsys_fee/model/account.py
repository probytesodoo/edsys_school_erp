from odoo import models, fields, api, _
from datetime import date,datetime

class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    fee_calculation_mail_sent =fields.Boolean('Fee Calculation Mail Sent')
