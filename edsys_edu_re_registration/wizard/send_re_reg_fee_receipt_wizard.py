from openerp import models, fields, api, _
from openerp.osv import osv

class send_re_reg_fee_receipt_wizard(models.Model):
    _name = 'send.re.reg.fee.receipt.wizard'

    @api.multi
    def send_re_reg_fee_button(self):
        context = self._context
        active_ids = context['active_ids']
        active_model = context['active_model']
        for active_id in active_ids :
            parent_re_reg_obj = self.env['re.reg.waiting.responce.parents']
            parent_re_reg_rec = parent_re_reg_obj.browse(active_id)
            for student_re_reg_rec in parent_re_reg_rec.student_ids:
                if student_re_reg_rec.state == 're_registration_confirmed' :
                    student_data = '<table border="2"><tr><td><b>Student Name</b></td><td><b>Class-Sec</b></td><td><b>Re-Registration Confirm</b></td><td><b>Amount Received for Re-Registration</b></td></tr>'
                    student_data += '<tr><td>%s</td><td>%s</td><td>Yes</td><td>%s</td></tr></table>'%(
                        student_re_reg_rec.name.name,student_re_reg_rec.next_year_course_id.name,student_re_reg_rec.total_paid_amount)
                    
                    voucher_obj = self.env['account.voucher']
                    voucher_id = voucher_obj.search([('reference','=',student_re_reg_rec.code)])
                    # Send email for Payment Receipt
                    email_server = self.env['ir.mail_server']
                    email_sender = email_server.search([], limit=1)
                    ir_model_data = self.env['ir.model.data']
                    template_id = ir_model_data.get_object_reference('edsys_edu_re_registration','email_template_re_registration_fee_receipt_paid')[1]
                    template_rec = self.env['mail.template'].sudo().browse(template_id)
                    body_html = template_rec.body_html
                    body_dynamic_html = template_rec.body_html
                    body_dynamic_html += '%s'%(student_data)
                    template_rec.write({'email_to': student_re_reg_rec.name.parents1_id.parents_email,
                                        'email_from': email_sender.smtp_user,
                                        'email_cc': '',
                                        'body_html': body_dynamic_html})
		    # updated by swapnil on 25-apr-2017 amrita request
                    #template_rec.send_mail(voucher_id.id, force_send=True)
                    template_rec.body_html = body_html
        return True
            
