from odoo import models, fields, api, _
import time
from odoo.exceptions import except_orm
import os

class ResendPayfortLinkVoucher(models.Model):
    _name = 'resend.payfort.link.voucher'

    voucher_date = fields.Date('Voucher Date',required=True)


    @api.model
    def resend_payfort_link_voucher_cron(self):
        print'=============resend payfort link voucher cron================='
        obj_ir_sequence = self.env['ir.sequence']
        account_invoice_obj = self.env['account.invoice']
        account_voucher_obj = self.env['account.voucher']
        current_date = time.strftime('%Y/%m/%d')
        logf = open("%s/../voucher_mail_cron.log" %(os.path.dirname(os.path.abspath(__file__))), "w+")
        account_voucher_record = account_voucher_obj.search([('date','=',current_date),('state','=','draft')])
        for account_voucher_rec in account_voucher_record:
            try :
                if account_voucher_rec:
                    if account_voucher_rec.voucher_number :
                        if account_voucher_rec.partner_id:
                                parent_rec = account_voucher_rec.partner_id
                                table_data = ''
                                student_id_list = []
                                stud_advance_table = ''
                                total_advance = 0.0
                                parent_cedit = 0.00
                                for child_rec in parent_rec.chield1_ids:
                                    if child_rec.active != False:
                                            student_id_list.append(child_rec.id)
                                stud_rec = self.env['res.partner'].browse(student_id_list)
                                if len(stud_rec) > 0:
                                    if parent_rec.credit :
                                        parent_cedit += parent_rec.credit
                                    total_amount_table = 0.00
                                    total_amount =0.0
                                    total_amount += parent_cedit                    
                
                                    for student_rec in stud_rec:
                                        invoice_residual_amount = 0
                                        total_advance += student_rec.advance_total_recivable + student_rec.re_reg_total_recivable
                                        advance_total_recivable = 0.0
                                        if student_rec.advance_total_recivable == False and student_rec.re_reg_total_recivable == False:
                                            advance_total_recivable = 0.0
                                        elif student_rec.advance_total_recivable > 0.0 or student_rec.re_reg_total_recivable > 0.0:
                                            advance_total_recivable = student_rec.advance_total_recivable + student_rec.re_reg_total_recivable
                                         
                                        stud_advance_table += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                                              %(parent_rec.parent1_id, student_rec.name, advance_total_recivable)
                                        
                                        
                                        for invoice_rec in account_invoice_obj.search([('partner_id','=',student_rec.id)]):
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
                
                                    if total_amount > 0.00:
                                        payable_amount = total_amount
                                        parent = parent_rec
                                        table_date = table_data
                                        advance_table = stud_advance_table
                                        voucher = account_voucher_rec
                                        advance_amt = total_advance
                                        invoice_amt = total_amount_table
                                        #if voucher:
                                        #    ir_sequence_ids = obj_ir_sequence.sudo().search([('name','=','Voucher Number Sequence')])
                                        #    if ir_sequence_ids:
                                        #        voucher_number = obj_ir_sequence.next_by_id(ir_sequence_ids.id)
                                        #        voucher.voucher_number = voucher_number
                                        parent_total_recivable = 0.0
                                        if parent.advance_total_recivable == False and parent.re_reg_total_recivable == False:
                                            parent_total_recivable = 0.0
                                        elif parent.advance_total_recivable > 0.0 or parent.re_reg_total_recivable > 0.0:
                                            parent_total_recivable = parent.advance_total_recivable or 0.00 + parent.re_reg_total_recivable or 0.00
                                            advance_amt += parent_total_recivable
                                        link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(total_amount,voucher.voucher_number)
                                        email_server = self.env['ir.mail_server']
                                        email_sender = email_server.search([], limit=1)
                                        ir_model_data = self.env['ir.model.data']
                                        template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_academic_fee_payment_reminder')[1]
                                        template_rec = self.env['mail.template'].browse(template_id)
                                        body_html = template_rec.body_html
                                        body_dynamic_html = template_rec.body_html + '<p>Pending Invoice Details:</p>'
                                        body_dynamic_html += '<table border=%s>'%(2)
                                        body_dynamic_html += '<tr><td><b>Child Name</b></td><td><b>Invoice number</b></td><td><b>Invoice date</b></td><td><b>Invoice amount</b></td><td><b>Pending amount</b></td></tr>%s'%(table_date)
                                        body_dynamic_html += '<tr><td><b>Total</b></td><td></td><td></td><td></td><td><b>%s</b></td></tr></table><br/>'%(invoice_amt)
                                        body_dynamic_html += 'Total advances (if any):<br/>'
                                        body_dynamic_html += '<table border=%s>'%(2)
                                        body_dynamic_html += '<tr><td><b>Parent Code</b></td><td><b>Student</b></td><td><b>Advance Value</b></td></tr>%s'%(advance_table)
                                        body_dynamic_html += '<tr><td>%s</td><td></td><td>%s</td></tr>'%(parent.parent1_id,parent_total_recivable)
                                        body_dynamic_html += '<tr><td><b>Total advances</b></td><td></td><td><b>%s</b></td></tr></table>'%(advance_amt)
                                        body_dynamic_html += '<p>Total outstanding payment is AED %s</p></div>'%(payable_amount)
                                        body_dynamic_html += '<p><a href=%s><button>Click Here</button>to pay Fee</a></p></div>'%(link)
                                        template_rec.write({'email_from': email_sender.smtp_user,
                                                            'email_to': parent.parents_email,
                                                            'email_cc': '',
                                                            'body_html': body_dynamic_html})
                                        mail_id = template_rec.send_mail(voucher.id, force_send=False)
                                        template_rec.body_html = body_html
                                        logf.write("Voucher mail sent {0}: and mail id is {1} \n".format(account_voucher_rec, str(mail_id)))
            except Exception as e:     # most generic exception you can catch
                logf.write("Failed to send mail {0}: {1} \n".format(account_voucher_rec, str(e)))                            
                                



    @api.multi
    def resend_payfort_link_voucher(self):
        print '========resend payfort =======link voucher======='
        active_ids = self._context['active_ids']
        obj_ir_sequence = self.env['ir.sequence']
        account_invoice_obj = self.env['account.invoice']
        account_voucher_obj = self.env['account.voucher']
        for account_voucher_rec in account_voucher_obj.browse(active_ids):
            if account_voucher_rec:
                if ((account_voucher_rec.voucher_number) and (account_voucher_rec.state=='draft') and (self.voucher_date == account_voucher_rec.date)):
                    if account_voucher_rec.partner_id:
                            parent_rec = account_voucher_rec.partner_id
                            table_data = ''
                            student_id_list = []
                            stud_advance_table = ''
                            total_advance = 0.0
                            parent_cedit = 0.00
                            for child_rec in parent_rec.chield1_ids:
                                if child_rec.active != False:
                                        student_id_list.append(child_rec.id)
                            stud_rec = self.env['res.partner'].browse(student_id_list)
                            if len(stud_rec) > 0:
                                if parent_rec.credit :
                                    parent_cedit += parent_rec.credit
                                total_amount_table = 0.00
                                total_amount =0.0
                                total_amount += parent_cedit                    
            
                                for student_rec in stud_rec:
                                    invoice_residual_amount = 0
                                    total_advance += student_rec.advance_total_recivable + student_rec.re_reg_total_recivable
                                    advance_total_recivable = 0.0
                                    if student_rec.advance_total_recivable == False and student_rec.re_reg_total_recivable == False:
                                        advance_total_recivable = 0.0
                                    elif student_rec.advance_total_recivable > 0.0 or student_rec.re_reg_total_recivable > 0.0:
                                        advance_total_recivable = student_rec.advance_total_recivable + student_rec.re_reg_total_recivable
                                     
                                    stud_advance_table += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                                          %(parent_rec.parent1_id, student_rec.name, advance_total_recivable)
                                    
                                    
                                    for invoice_rec in account_invoice_obj.search([('partner_id','=',student_rec.id)]):
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
            
                                if total_amount > 0.00:
                                    payable_amount = total_amount
                                    parent = parent_rec
                                    table_date = table_data
                                    advance_table = stud_advance_table
                                    voucher = account_voucher_rec
                                    advance_amt = total_advance
                                    invoice_amt = total_amount_table
                                    if voucher:
                                        ir_sequence_ids = obj_ir_sequence.sudo().search([('name','=','Voucher Number Sequence')])
                                        if ir_sequence_ids:
                                            voucher_number = obj_ir_sequence.next_by_code(ir_sequence_ids.id)
                                            voucher.voucher_number = voucher_number
                                    parent_total_recivable = 0.0
                                    if parent.advance_total_recivable == False and parent.re_reg_total_recivable == False:
                                        parent_total_recivable = 0.0
                                    elif parent.advance_total_recivable > 0.0 or parent.re_reg_total_recivable > 0.0:
                                        parent_total_recivable = parent.advance_total_recivable or 0.00 + parent.re_reg_total_recivable or 0.00
                                        advance_amt += parent_total_recivable
                                    link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(total_amount,voucher.voucher_number)
                                    email_server = self.env['ir.mail_server']
                                    email_sender = email_server.search([], limit=1)
                                    ir_model_data = self.env['ir.model.data']
                                    template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_academic_fee_payment_reminder')[1]
                                    template_rec = self.env['mail.template'].browse(template_id)
                                    body_html = template_rec.body_html
                                    body_dynamic_html = template_rec.body_html + '<p>Pending Invoice Details:</p>'
                                    body_dynamic_html += '<table border=%s>'%(2)
                                    body_dynamic_html += '<tr><td><b>Child Name</b></td><td><b>Invoice number</b></td><td><b>Invoice date</b></td><td><b>Invoice amount</b></td><td><b>Pending amount</b></td></tr>%s'%(table_date)
                                    body_dynamic_html += '<tr><td><b>Total</b></td><td></td><td></td><td></td><td><b>%s</b></td></tr></table><br/>'%(invoice_amt)
                                    body_dynamic_html += 'Total advances (if any):<br/>'
                                    body_dynamic_html += '<table border=%s>'%(2)
                                    body_dynamic_html += '<tr><td><b>Parent Code</b></td><td><b>Student</b></td><td><b>Advance Value</b></td></tr>%s'%(advance_table)
                                    body_dynamic_html += '<tr><td>%s</td><td></td><td>%s</td></tr>'%(parent.parent1_id,parent_total_recivable)
                                    body_dynamic_html += '<tr><td><b>Total advances</b></td><td></td><td><b>%s</b></td></tr></table>'%(advance_amt)
                                    body_dynamic_html += '<p>Total outstanding payment is AED %s</p></div>'%(payable_amount)
                                    body_dynamic_html += '<p><a href=%s><button>Click Here</button>to pay Fee</a></p></div>'%(link)
                                    template_rec.write({'email_from': email_sender.smtp_user,
                                                        'email_to': parent.parents_email,
                                                        'email_cc': '',
                                                        'body_html': body_dynamic_html})
                                    template_rec.send_mail(voucher.id, force_send=False)
                                    template_rec.body_html = body_html
                    
                                
                    
                    
                    
                    
                    
                    
                
