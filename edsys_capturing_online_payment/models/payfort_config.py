# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date

class InheritPayfortConfig(models.Model):

    _inherit = 'payfort.config'

    bank_service_charge = fields.Float(string='Bank Service Charge(%)',default=2.1)
    payfort_history_ids = fields.One2many('payfort.history','payfort_config_id', string='Payfort History')

    @api.multi
    def write(self,vals):
        """
        inherit write method for capture
        payfort history,
        ---------------------------------
        :param vals: dictonary
        :return:
        """
        payfort_history_obj = self.env['payfort.history']
        for rec in self:
            if rec.id:
                payfort_history_data = {
                    'name' : self.name,
                    'access_code' : self.access_code,
                    'charge' : self.charge,
                    'active' : self.active,
                    'transaction_charg_amount' : self.transaction_charg_amount,
                    'payfort_type' : self.payfort_type,
                    'payfort_url' : self.payfort_url,
#                     'merchant_identifier' : self.merchant_identifier,
                    'journal_id' : self.journal_id.id,
                    'bank_service_charge' : self.bank_service_charge,
                    'change_date' : date.today(),
                    'user' : self._uid,
                    'payfort_config_id' : rec.id,
                }
                payfort_history_obj.create(payfort_history_data)
        return super(InheritPayfortConfig,self).write(vals)

class PayfortHistory(models.Model):

    _name = 'payfort.history'

    name = fields.Char(string="Name",size=126)
    access_code = fields.Char(string="Acess Code",size=126)
    charge = fields.Float(string='Charge(%)')
    active = fields.Boolean(string="Active")
    transaction_charg_amount = fields.Float('Transaction Charges')
    payfort_type = fields.Selection([('test','Test'),('production','Production')],string='Payfort Type')
    payfort_url = fields.Char(string='Payfort Url',store=True)
    psp_id = fields.Char('PSP ID')
    journal_id = fields.Many2one('account.journal','Payment Method')
    bank_service_charge = fields.Float(string='Bank Service Charge(%)')
    change_date = fields.Datetime('Update Date')
    user = fields.Many2one('res.users', string="User")
    payfort_config_id = fields.Many2one('payfort.config', string="Current User")