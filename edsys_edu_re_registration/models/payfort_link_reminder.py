from odoo import models, fields, api, _
from odoo.exceptions import except_orm
import hashlib
import time


class ResendPayfortLinkInherit(models.Model):

    _inherit = 'resend.payfort.wiz'


   

    @api.multi
    def resend_payfort_link(self):
        account_voucher_obj = self.env['account.voucher']
        account_invoice_obj = self.env['account.invoice']
        voucher_line_obj = self.env['account.voucher.line']
                                        
        if self.parent_ids:
            for parent_rec in self.parent_ids:
                table_data = ''
                student_id_list = []
                stud_advance_table = ''
                total_advance = 0.0
                parent_cedit = 0.00
                if self.class_id and self.student_section_id:
                    for child_rec in parent_rec.chield1_ids:
                        if self.class_id.id == child_rec.class_id.id and self.student_section_id.id == child_rec.student_section_id.id:
                            if child_rec.active != False:
                                student_id_list.append(child_rec.id)
                elif self.class_id and not self.student_section_id:
                    for child_rec in parent_rec.chield1_ids:
                        if self.class_id.id == child_rec.class_id.id:
                            if child_rec.active != False:
                                student_id_list.append(child_rec.id)
                    # stud_rec = parent_rec.chield1_ids.search([('class_id','=',self.class_id.id)])
                elif not self.class_id and self.student_section_id:
                    # stud_rec = parent_rec.chield1_ids.search([('student_section_id','=',self.student_section_id.id)])
                    for child_rec in parent_rec.chield1_ids:
                        if self.student_section_id.id == child_rec.student_section_id.id:
                            if child_rec.active != False:
                                student_id_list.append(child_rec.id)
                else:
                    # stud_rec = parent_rec.chield1_ids
                    for child_rec in parent_rec.chield1_ids:
                        if child_rec.active != False:
                            student_id_list.append(child_rec.id)
                stud_rec = self.env['res.partner'].browse(student_id_list)
                if len(stud_rec) > 0:
                    # check for parent advance payment#this is my logic
                    if parent_rec.credit :
                        parent_cedit += parent_rec.credit

                    total_amount_table = 0.00
                    total_amount =0.0
                    move_ids_list = []
                    stud_lst_invoice = []
                    stud_balance=0.0
                    total_amount += parent_cedit                    

                    for student_rec in stud_rec:
                        invoice_residual_amount = 0
                        
                        # COLLECT STUDENT ADVANCES
                        total_advance += student_rec.advance_total_recivable + student_rec.re_reg_total_recivable
                        advance_total_recivable = 0.0
                        if student_rec.advance_total_recivable == False and student_rec.re_reg_total_recivable == False:
                            advance_total_recivable = 0.0
                        elif student_rec.advance_total_recivable > 0.0 or student_rec.re_reg_total_recivable > 0.0:
                            advance_total_recivable = student_rec.advance_total_recivable + student_rec.re_reg_total_recivable
                         
                        stud_advance_table += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                              %(parent_rec.parent1_id, student_rec.name, advance_total_recivable)
                        
                        
                        for invoice_rec in account_invoice_obj.search([('partner_id','=',student_rec.id),('type','!=','out_refund')]):
                            #GET OPEN INVOICES
                            if invoice_rec.state == 'open' and invoice_rec.residual > 0.00:
                                
                                
                                # CHECK FOR NEGATIVE AMOUNT
                                if invoice_rec.amount_total < 0 : 
                                    invoice_residual_amount = -invoice_rec.residual
                                
                                else : 
                                    invoice_residual_amount = invoice_rec.residual
                                      
                                #total_amount_table += invoice_rec.residual    
                                total_amount_table += invoice_residual_amount
                                table_data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                              %(student_rec.name,invoice_rec.number,invoice_rec.date_invoice,invoice_rec.amount_total,invoice_residual_amount)
#                                                     
                        total_amount += student_rec.credit

                    period_rec = self._get_period()
                    journal_rec = self._get_journal()
                    curency_id = self._get_currency()
                    vouch_sequence = self.env['ir.sequence'].get('voucher.payfort') or '/'
                    account_config_settings_obj = self.env['account.config.settings']
                    account_config_settings_rec = account_config_settings_obj.search([])
		    if total_amount > 0.00:
			if total_amount >= account_config_settings_rec.amount_configurable:
		                voucher_data = {
		                    'period_id': period_rec.id,
		                    'journal_id': journal_rec.id,
		                    'account_id': journal_rec.default_debit_account_id.id,
		                    'partner_id': parent_rec.id,
		                    'currency_id': curency_id,
		                    'reference': parent_rec.name,
		                    'amount': 0.0,
		                    'type': 'receipt' or 'payment',
		                    'state': 'draft',
		                    'pay_now': 'pay_later',
		                    'name': '',
		                    'date': time.strftime('%Y-%m-%d'),
		                    'company_id': 1,
		                    'tax_id': False,
		                    'payment_option': 'without_writeoff',
		                    'comment': _('Write-Off'),
		                    'payfort_type': True,
		                    'payfort_link_order_id' : vouch_sequence,
				    'voucher_amount' : total_amount,
		                    # 'student_class' : self.class_id.id,
		                    # 'student_section' : self.student_section_id.id,
		                    }
		                voucher_rec = account_voucher_obj.create(voucher_data)

		                # SEND MAIL FOR PAY FORT
		                #self.resend_mail_for_payfort_payment(parent=parent_rec,total_amount=total_amount,order_id=vouch_sequence,\
		                #    table_date=table_data,advance_table=stud_advance_table,\
		                #    voucher=voucher_rec,advance_amt=total_advance,invoice_amt=total_amount_table)




class ResendPayfortLinkInheriInvoice(models.TransientModel):

    _inherit = 'invoice.resend.payfort'

    @api.multi
    def resend_payfort_link(self):
        invoice_obj = self.env['account.invoice']
        active_ids=self._context['active_ids']

        for invoice_rec in invoice_obj.browse(active_ids):
            if invoice_rec.state == 'open':
                # send payfort link
                active_payforts=self.env['payfort.config'].search([('active','=','True')])

                if len(active_payforts) > 1:
                    raise except_orm(_('Warning!'),_("There should be only one payfort record!"))

                if not active_payforts.id:
                    raise except_orm(_('Warning!'),_("Please create Payfort Details First!"))

                payfort_amount = invoice_rec.residual
                advance_amount = 0.00
                if invoice_rec.partner_id.advance_total_recivable > 0.00:
                    advance_amount += invoice_rec.partner_id.advance_total_recivable
                if invoice_rec.partner_id.re_reg_total_recivable > 0.00:
                    advance_amount += invoice_rec.partner_id.re_reg_total_recivable
                if invoice_rec.partner_id.parents1_id.id:
                    if invoice_rec.partner_id.parents1_id.advance_total_recivable > 0.00:
                        advance_amount += invoice_rec.partner_id.parents1_id.advance_total_recivable
                    if invoice_rec.partner_id.parents1_id.re_reg_total_recivable > 0.00:
                        advance_amount += invoice_rec.partner_id.parents1_id.re_reg_total_recivable
#                 payfort_amount -= advance_amount
#                 payable_amount = 0.00
                if payfort_amount > 0.00:
                    payable_amount = payfort_amount
                    link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(payable_amount,invoice_rec.invoice_number)
                    table_data = ''
                    table_data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                                      %(invoice_rec.partner_id.name,invoice_rec.number,invoice_rec.date_invoice,invoice_rec.amount_total,invoice_rec.residual)

                    total_advance_amt = 0.0
                    #student advance amount
                    student_advance_received = 0.0
                    if invoice_rec.partner_id.advance_total_recivable == False and invoice_rec.partner_id.re_reg_total_recivable == False:
                        student_advance_received = 0.0
                    elif invoice_rec.partner_id.advance_total_recivable > 0.0 or invoice_rec.partner_id.re_reg_total_recivable > 0.0:
                        student_advance_received = invoice_rec.partner_id.advance_total_recivable + invoice_rec.partner_id.re_reg_total_recivable
                    total_advance_amt += student_advance_received

                    #parent advance amount
                    parent_advance_received = 0.0
                    if invoice_rec.partner_id.parents1_id.advance_total_recivable == False and invoice_rec.partner_id.parents1_id.re_reg_total_recivable == False:
                        parent_advance_received = 0.0
                    elif invoice_rec.partner_id.parents1_id.advance_total_recivable > 0.0 or invoice_rec.partner_id.parents1_id.re_reg_total_recivable > 0.0:
                        parent_advance_received = invoice_rec.partner_id.parents1_id.advance_total_recivable +invoice_rec.partner_id.parents1_id.re_reg_total_recivable
                    total_advance_amt += parent_advance_received

                    # resend mail to the parent
                    if invoice_rec.partner_id.is_parent == False:
                        email_server = self.env['ir.mail_server']
                        email_sender = email_server.search([], limit=1)
                        ir_model_data = self.env['ir.model.data']
                        template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_resend_academic_fee_payment_link')[1]
                        template_rec = self.env['mail.template'].browse(template_id)
                        body_html = template_rec.body_html
                        body_dynamic_html = template_rec.body_html + '<p>Pending Invoice Details:</p>'
                        body_dynamic_html += '<table border=%s>'%(2)
                        body_dynamic_html += '<tr><td><b>Child Name</b></td><td><b>Invoice number</b></td><td><b>Invoice date</b></td><td><b>Invoice amount</b></td><td><b>Pending amount</b></td></tr>%s'%(table_data)
                        body_dynamic_html += '<tr><td><b>Total</b></td><td></td><td></td><td></td><td><b>%s</b></td></tr></table><br/>'%(invoice_rec.residual)
                        body_dynamic_html += 'Total advances (if any):<br/>'
                        body_dynamic_html += '<table border=%s>'%(2)
                        body_dynamic_html += '<tr><td><b>Parent Code</b></td><td><b>Student</b></td><td><b>Advance Value</b></td></tr>'
                        body_dynamic_html += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>'%(invoice_rec.partner_id.parents1_id.parent1_id,invoice_rec.partner_id.name,student_advance_received)
                        body_dynamic_html += '<tr><td>%s</td><td></td><td>%s</td></tr>'%(invoice_rec.partner_id.parents1_id.parent1_id,parent_advance_received)
                        body_dynamic_html += '<tr><td><b>Total advances</b></td><td></td><td><b>%s</b></td></tr></table>'%(total_advance_amt)
                        body_dynamic_html += '<p>Total outstanding payment is AED %s</p></div>'%(payable_amount)
                        body_dynamic_html += '<p><a href=%s><button>Click Here</button>to pay Fee</a></p></div>'%(link)
                        template_rec.write({'email_from': email_sender.smtp_user,
                                            'email_to': invoice_rec.partner_id.parents1_id.parents_email,
                                            'email_cc': '',
                                            'body_html': body_dynamic_html})
                        template_rec.send_mail(invoice_rec.id)
                        template_rec.body_html = body_html

