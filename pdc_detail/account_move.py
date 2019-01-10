# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date,datetime,timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import odoo.addons.decimal_precision as dp

class account_move(models.Model):
    _inherit='account.move'
    
    is_manual=fields.Boolean('Manual Entry', readonly=True)
    pdc_id= fields.Many2one('pdc.detail','PDC Cheque',readonly=True)
    party_name = fields.Char('Party Name')
    chk_num = fields.Char('Cheque Number')
    #student_name = fields.Char(string="Student Reference", related='line_id.name')
    student_name = fields.Char(string="Student Reference")
    
    @api.onchange('journal_id')
    def onchange_journal_id(self):
        self.cheque_pay= self.journal_id.is_cheque
    
    @api.model    
    def create(self,vals):
        result = super(account_move, self).create(vals)
        
        if 'cheque_expiry_date' in vals and vals['cheque_expiry_date']:
            current_date=date.today()
            current_date=datetime.strptime(str(current_date), "%Y-%m-%d")
            comp_date= datetime.strptime(vals['cheque_expiry_date'], "%Y-%m-%d")
            chk_date= datetime.strptime(vals['cheque_date'], "%Y-%m-%d")
            if comp_date < current_date:
                raise except_orm(_('Warning!'),
                        _("Cheque Expiry Date should be after current date!"))
            if chk_date > comp_date:
                raise except_orm(_('Warning!'),
                        _("Cheque Expiry Date should be after cheque date!"))
                
        return result    
    
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
            'party_name':self.party_name,
            'period_id':self.period_id and self.period_id.id or False ,
            'state':'draft',

                }
        pdc_rec=pdc_obj.create(vals)
        self.pdc_id=pdc_rec.id
        
        return True
