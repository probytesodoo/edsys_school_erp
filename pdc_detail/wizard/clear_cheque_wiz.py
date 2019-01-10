from openerp import models, fields, api, _
from datetime import datetime, timedelta
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time

class clear_cheque_wiz(models.TransientModel):

    _name='clear.cheque.wiz'
    
    label = fields.Char()
    
    @api.multi
    def clear_cheque(self):
        pdc=self.env['pdc.detail']
        journal_obj=self.env['account.journal']
        account_move_obj = self.env['account.move']
        jounral_dict1 = {}
        jounral_dict2 = {}
        active_ids=self._context['active_ids']
        for active_id in active_ids:
            chk=pdc.browse(active_id)
            partner_id=False
            if chk.state!='posted':
                raise except_orm(_('Warning!'),
                    _("You can cleared only posted cheque"))
            if chk.chk_fee_type=='reg' and chk.journal_entry_id.state != 'posted':
                raise except_orm(_('Warning!'),
                    _("Cheque's journal entry is not posted.You can not clear this cheque"))
            if chk.chk_fee_type=='academic':  
                if chk.voucher_id and chk.voucher_id.move_id and chk.voucher_id.move_id.state!= 'posted':
                    raise except_orm(_('Warning!'),
                    _("Cheque's payment journal entry is not posted.You can not clear this cheque"))
                if chk.voucher_id.move_ids:
                    partner_id= chk.voucher_id.move_ids[0].partner_id.id  
            journal=journal_obj.search([('type','=','bank')], limit=1)
            if not journal.id:
                raise except_orm(_('Warning!'),
                    _("Bank Journal is not found."))
            
            jounral_dict1.update({'name':chk.name,'debit':chk.amount,'partner_id':partner_id})
            jounral_dict2.update({'name':chk.name,'credit':chk.amount,'account_id':chk.journal_id.default_credit_account_id.id,'partner_id':partner_id})

            jounral_data = {'journal_id':journal.id,
                            'line_id':[(0,0,jounral_dict1),(0,0,jounral_dict2)],
                            'ref':'['+chk.name or '' + ']' + chk.party_name or '',
                            'bank_name':chk.bank_name,
                            'cheque_date':chk.cheque_start_date,
                            'cheque_expiry_date':chk.cheque_expiry_date,
                            
                            }  
            bank_jounral = account_move_obj.create(jounral_data)
            bank_jounral.button_validate()
            chk.state='cleared'
            chk.cleared_entry_id=bank_jounral.id
        return True
