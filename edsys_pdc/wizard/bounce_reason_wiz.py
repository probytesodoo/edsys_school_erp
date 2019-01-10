from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import time

class bounce_reason_wiz(models.TransientModel):

    _inherit = 'bounce.reason.wiz'
    
    #reason = fields.Char(string="Please mention reason for Reject cheque",size=126)
    reason=fields.Selection( [('cancelled','Cancelled'), ('bounced','Bounced'), ('returned','Returned') ],'Please mention reason for Reject cheque')
    bounce_date_wizard = fields.Date('Reject Check Date')
    
    @api.multi
    def bounce_cheque(self):
        pdc=self.env['pdc.detail']
        active_ids=self._context['active_ids']
        journal_obj=self.env['account.journal']
        jounral_dict1 = {}
        jounral_dict2 = {}
        partner_id = False
        account_move_obj = self.env['account.move']
        journal=journal_obj.search([('code','=','MISC')], limit=1)
        if not journal.id:
            raise except_orm(_('Warning!'),_("Miscellaneous Journal is not found."))
        if journal.default_debit_account_id  :
            raise except_orm(_('Warning!'),_("Miscellaneous Journal default debit account should be None."))
        if journal.default_credit_account_id : 
            raise except_orm(_('Warning!'),_("Miscellaneous Journal default credit account should be None."))
        
        for active_id in active_ids:
            move_lines_reverse = []
            pdc_obj=pdc.browse(active_id)
            pdc_obj.bounce_cheque_date = self.bounce_date_wizard
            if pdc_obj.state =='draft':
                raise except_orm(_('Warning!'),
                    _("You can not bounce Draft cheque"))
            
            pdc_obj.reason=self.reason
            if pdc_obj.chk_fee_type=='reg':
                
                #new code for JE
                for move_line in pdc_obj.journal_entry_id.line_id :
                    if move_line.credit > 0 :
                        debit_line  = {
                                        'name' : move_line.name,
                                        'debit' : move_line.credit,
                                        'credit' : move_line.debit,
                                        'account_id' : move_line.account_id.id,
                                        'partner_id' : move_line.partner_id.id,
                                        }
                        move_lines_reverse.append((0,0, debit_line))
                        
                    elif move_line.debit > 0 :
                        credit_line  = {
                                        'name' : move_line.name,
                                        'debit' : move_line.credit,
                                        'credit' : move_line.debit,
                                        'account_id' : move_line.account_id.id,
                                        'partner_id' : move_line.partner_id.id,
                                        }
                        move_lines_reverse.append((0,0, credit_line))
                jounral_data = {'journal_id':journal.id,
                                'line_id': move_lines_reverse, #[(0,0,debit_line),(0,0,credit_line)],
                                'ref':pdc_obj.journal_entry_id.ref,
                                'bank_name':pdc_obj.journal_entry_id.bank_name,
                                'date' : self.bounce_date_wizard,
                                }  
                bank_jounral = account_move_obj.create(jounral_data)
                bank_jounral.button_validate()
                pdc_obj.journal_entry_id=bank_jounral.id
                
                
                pdc_obj.state='bounced'
                #pdc_obj.journal_entry_id.button_cancel()
                
                
            elif pdc_obj.chk_fee_type=='academic':
                if pdc_obj.voucher_id:
                    #pdc_obj.voucher_id.cancel_voucher()
                    reconcile_obj = self.env['account.move.reconcile']
                    move_line_obj = self.env['account.move.line']
                    for line_cr_id in pdc_obj.voucher_id.line_cr_ids :
                        line_cr_id.reconcile = False
                        line_cr_id.amount = 0.00
                        
                    ############### code copied from default account_voucher module and method cancel_voucher()    
                    # refresh to make sure you don't unlink an already removed move
                    pdc_obj.voucher_id.refresh()
                    for line in pdc_obj.voucher_id.move_ids:
                        # refresh to make sure you don't unreconcile an already unreconciled entry
                        line.refresh()
                        if line.reconcile_id:
                            move_lines = [move_line.id for move_line in line.reconcile_id.line_id]
                            move_lines.remove(line.id)
                            line.reconcile_id.unlink()
                            if len(move_lines) >= 2:
                                move_lines_recs = move_line_obj.browse(move_lines)
                                move_lines_recs.reconcile_partial()
                        
                    for move_line in pdc_obj.voucher_id.move_id.line_id :
                        if move_line.credit > 0 :
                            debit_line  = {
                                            'name' : move_line.name,
                                            'debit' : move_line.credit,
                                            'credit' : move_line.debit,
                                            'account_id' : move_line.account_id.id,
                                            'partner_id' : move_line.partner_id.id,
                                            }
                            move_lines_reverse.append((0,0, debit_line))
                            
                        elif move_line.debit > 0 :
                            credit_line  = {
                                            'name' : move_line.name,
                                            'debit' : move_line.credit,
                                            'credit' : move_line.debit,
                                            'account_id' : move_line.account_id.id,
                                            'partner_id' : move_line.partner_id.id,
                                            }
                            move_lines_reverse.append((0,0, credit_line))
                    jounral_data = {'journal_id':journal.id,
                                    'line_id': move_lines_reverse, #[(0,0,debit_line),(0,0,credit_line)],
                                    'ref':pdc_obj.voucher_id.move_id.ref,
                                    'bank_name':pdc_obj.voucher_id.move_id.bank_name,
                                    'date' : self.bounce_date_wizard,
                                    }  
                    bank_jounral = account_move_obj.create(jounral_data)
                    bank_jounral.button_validate()
                    pdc_obj.journal_entry_id=bank_jounral.id
                    pdc_obj.state='bounced'
            else:
                pdc_obj.state='bounced'
                pdc_obj.journal_entry_id.button_cancel()
                if pdc_obj.journal_entry_id.pdc_id:
                    pdc_obj.journal_entry_id.pdc_id=False
            if pdc_obj.cleared_entry_id:
                pdc_obj.cleared_entry_id.button_cancel()
                pdc_obj.cleared_entry_id.unlink()

	    if pdc_obj:
                if pdc_obj.voucher_id:
                    re_reg_reference = pdc_obj.voucher_id.reference
                    if re_reg_reference:
                        re_reg_student_rec = re_reg_student.search([('code','=',re_reg_reference)])
                        if re_reg_student_rec:
                            re_reg_student_rec.state = 'awaiting_re_registration_fee'
                            re_reg_student_rec.fee_status = 're_unpaid'
                            re_reg_student_rec.total_paid_amount = 0.00
                            re_reg_parent = re_reg_student_rec.re_reg_parents
                            if re_reg_parent:
                                re_reg_parent.state = 'awaiting_re_registration_fee'

        #raise except_orm(_('Warning!'),_("stoppppp"))      
        return True
