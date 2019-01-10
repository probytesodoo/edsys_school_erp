# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, _

class payfort_config(models.Model):

    _name = 'payfort.config'

    name = fields.Char(string="Name",size=126)
    access_code = fields.Char(string="Access Code",size=126)
    merchant_identifier = fields.Char('Merchant Identifier')
    sha_request_phase = fields.Char(string="SHA Request Phrase",size=126)
    return_url = fields.Char('Return URL',required=True)
    language = fields.Char('Language',required=True)
    charge = fields.Float(string='Charge(%)')
#    test = fields.Boolean(string="Is Test")
    active = fields.Boolean(string="Active")
    transaction_charg_amount = fields.Float('Transaction Charges')
    payfort_type = fields.Selection([('test','Test'),('production','Production')],string='Payfort Type')
    payfort_url = fields.Char(string='Payfort Url',store=True)
    
    journal_id = fields.Many2one('account.journal', string='Payment Method')

    @api.onchange('payfort_type')
    def onchange_payfort_url(self):
        if self.payfort_type == 'test':
            self.payfort_url = 'https://sbcheckout.payfort.com/FortAPI/paymentPage'
        elif self.payfort_type == 'production':
            self.payfort_url = 'https://checkout.payfort.com/FortAPI/paymentPage'
            
            
    @api.multi
    def write(self, vals):
        return super(payfort_config, self).write(vals)