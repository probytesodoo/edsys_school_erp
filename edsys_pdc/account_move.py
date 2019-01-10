# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date,datetime,timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import odoo.addons.decimal_precision as dp

class account_move(models.Model):
    _inherit='account.move'
    
    bank_payment_name = fields.Many2one('account.account', 'Bank Payment Name', domain=[('user_type.name','=','Bank')])
    
    
    @api.multi    
    def create_pdc_cheque(self):
        pdc_obj = self.env['pdc.detail']
        if self.amount <=0.0:
            raise except_orm(_('Warning!'),
                 _("Cheque Amount can not be zero !"))            
        vals={
            'name':self.chk_num,
            'amount':self.amount,
            'journal_id':self.journal_id.id or False,
            'journal_entry_id':self.id,
            'cheque_start_date':self.cheque_date,
            'cheque_expiry_date':self.cheque_expiry_date,
            'bank_name':self.bank_name,
            'bank_payment_name':self.bank_payment_name.id,
            'party_name':self.party_name,
            'period_id':self.period_id and self.period_id.id or False ,
            'state':'draft',

                }
        pdc_rec=pdc_obj.create(vals)
        self.pdc_id=pdc_rec.id
        
        return True
