from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import time

class clear_cheque_wiz(models.TransientModel):

    _inherit = 'clear.cheque.wiz'
    
    label = fields.Char()
    clear_cheque_date_wizard = fields.Date('Date of clearing cheque')
    
    @api.multi
    def clear_cheque(self):
        pdc=self.env['pdc.detail']
        journal_obj=self.env['account.journal']
        account_move_obj = self.env['account.move']
        period_pool = self.env['account.period']
        jounral_dict1 = {}
        jounral_dict2 = {}
        active_ids=self._context['active_ids']
        for active_id in active_ids:
            chk=pdc.browse(active_id)
            chk.clear_cheque_date = self.clear_cheque_date_wizard
            #chk.write({'clear_cheque_date' : self.clear_cheque_date_wizard})
            partner_id=False
            if self.clear_cheque_date_wizard < chk.cheque_start_date :
                raise except_orm(_('Warning!'), _("Clearing cheque date should be greater than Cheque Date"))
            if self.clear_cheque_date_wizard > chk.cheque_expiry_date :
                raise except_orm(_('Warning!'), _("Clearing cheque date should be less than Cheque Expiry Date"))
            
            if chk.state!='posted':
                raise except_orm(_('Warning!'),
                    _("You can cleared only Submitted cheque"))
            if chk.chk_fee_type=='reg' and chk.journal_entry_id.state != 'posted':
                raise except_orm(_('Warning!'),
                    _("Cheque's journal entry is not Submitted.You can not clear this cheque"))
            if chk.chk_fee_type=='academic':  
                if chk.voucher_id and chk.voucher_id.move_id and chk.voucher_id.move_id.state!= 'posted':
                    raise except_orm(_('Warning!'),
                    _("Cheque's payment journal entry is not Submitted.You can not clear this cheque"))
                if chk.voucher_id.move_ids:
                    partner_id= chk.voucher_id.move_ids[0].partner_id  
            #===================================================================
            # journal=journal_obj.search([('name','=','Bank')], limit=1)
            # if not journal.id:
            #     raise except_orm(_('Warning!'),
            #         _("Bank Journal is not found."))
            #===================================================================
            
            #jounral_dict1 remove and call default bank
            pids = period_pool.find(self.clear_cheque_date_wizard)
            if partner_id : 
                if partner_id.customer : 
                    journal=journal_obj.search([ ('type','=','bank'), ('default_credit_account_id','=',chk.bank_payment_name.id)], limit=1)
                    if not journal.id:
                        raise except_orm(_('Warning!'), _("Bank Journal is not found."))
                    if chk.amount > 0 :
                        jounral_dict1.update({'name':chk.name,'debit':chk.amount,'partner_id':partner_id.id})
                        jounral_dict2.update({'name':chk.name,'credit':chk.amount,'account_id':chk.journal_id.default_credit_account_id.id,'partner_id':partner_id.id})
                    else : 
                        jounral_dict1.update({'name':chk.name,'credit':abs(chk.amount),'partner_id':partner_id.id})
                        jounral_dict2.update({'name':chk.name,'debit':abs(chk.amount),'account_id':chk.journal_id.default_credit_account_id.id,'partner_id':partner_id.id})
                elif partner_id.supplier :
                    journal=journal_obj.search([('default_debit_account_id','=',chk.bank_payment_name.id)], limit=1)
                    if not journal.id:
                        raise except_orm(_('Warning!'), _("Bank Journal is not found."))
                    if chk.amount > 0 :
                        jounral_dict1.update({'name':chk.name,'debit':chk.amount,'account_id':chk.journal_id.default_debit_account_id.id,'partner_id':partner_id.id})
                        jounral_dict2.update({'name':chk.name,'credit':chk.amount,'partner_id':partner_id.id})
                    else :
                        jounral_dict1.update({'name':chk.name,'credit':abs(chk.amount),'account_id':chk.journal_id.default_debit_account_id.id,'partner_id':partner_id.id})
                        jounral_dict2.update({'name':chk.name,'debit':abs(chk.amount),'partner_id':partner_id.id})
                jounral_data = {
                                    'journal_id':journal.id,
                                    'line_id':[(0,0,jounral_dict1),(0,0,jounral_dict2)],
                                    'ref': chk.name,
                                    'bank_name':chk.bank_name,
                                    'bank_payment_name':chk.bank_payment_name.id,
                                    'cheque_date':chk.cheque_start_date,
                                    'cheque_expiry_date':chk.cheque_expiry_date,
                                    'date' : self.clear_cheque_date_wizard,
                                    'period_id' : pids[0].id,
                                }  
                bank_jounral = account_move_obj.create(jounral_data)
                bank_jounral.button_validate()
                chk.state='cleared'
                chk.cleared_entry_id=bank_jounral.id
            else : 
                return super(clear_cheque_wiz, self).clear_cheque()
            #raise except_orm(_('Warning!'), _("stop for testing"))
        return True