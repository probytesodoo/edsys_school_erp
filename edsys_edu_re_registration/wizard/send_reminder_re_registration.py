from openerp import models, fields, api, _
import base64

class SendReminderReRegistrationParent(models.Model):

    _name = 'reminder.re.registration.parent'

    @api.multi
    def resend_re_reg_link_parent(self):
        """
        this method is use to resend request for
        re-registration process multiple parents.
        :return:
        """
        active_ids=self._context['active_ids']
        parent_rereg_obj = self.env['re.reg.waiting.responce.parents']
        for re_reg_rec in parent_rereg_obj.browse(active_ids):
            is_confirm = False
            for child_rec in re_reg_rec.student_ids:
                if child_rec.confirm == False:
                    is_confirm = True
                    
            if is_confirm == True:
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                encoded_data = base64.b64encode(re_reg_rec.code)
                c_link = base_url + '/student/re_registration/request?REREG=%s'%(encoded_data)
                # send mail

                email_server = self.env['ir.mail_server']
                email_sender = email_server.search([], limit=1)
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('edsys_edu_re_registration', 'email_template_resend_re_registration_request_parent')[1]
                template_rec = self.env['email.template'].browse(template_id)
                body_html = template_rec.body_html
                body_dynamic_html = template_rec.body_html
                body_dynamic_html += '<p><a href=%s><button>Click here</button>to complete the Re-registration form</a></p></div>'%(c_link)
                template_rec.write({'email_to': re_reg_rec.name.parents_email,
                                    'email_from': email_sender.smtp_user,
                                    'email_cc': '',
                                    'body_html': body_dynamic_html})
                template_rec.send_mail(re_reg_rec.id)
                template_rec.body_html = body_html

class SendPaymentReminderReRegistrationParent(models.Model):
    _name = 'payment.reminder.re.registration.parent'
    
    @api.multi
    def resend_re_reg_payment_link_parent(self):
        """
        this method is use to resend payment link for
        awaiting re-registration fee to multiple parents.
        :return:
        """
        active_ids=self._context['active_ids']
        parent_rereg_obj = self.env['re.reg.waiting.responce.parents']
        for parent_re_reg_rec in parent_rereg_obj.browse(active_ids):
            if parent_re_reg_rec.state == 'awaiting_re_registration_fee':
                if parent_re_reg_rec.residual > 0.00:
                    child_data_table = ''
                    for student_re_record in parent_re_reg_rec.student_ids:
                        child_data_table += '<tr>'
                        child_data_table += '<td>%s</td>'%(student_re_record.name.name)
                        child_data_table += '<td>%s</td>'%(student_re_record.next_year_course_id.name)
                        child_data_table += '<td>Yes</td>'
                        child_data_table += '<td>%s</td>'%(student_re_record.total_amount)
                        child_data_table += '</tr>'
                    parent_rereg_obj.send_re_registration_payment_link(parent_record = parent_re_reg_rec,
                                                       child_data_table = child_data_table)


class SendReminderReRegistrationStudent(models.Model):

    _name = 'reminder.re.registration.student'

    @api.multi
    def resend_re_reg_link_student(self):
        """
        this method is use to resend request for
        re-registration process to parent for particuler student wise.
        :return:
        """
        active_ids=self._context['active_ids']
        student_rereg_obj = self.env['re.reg.waiting.responce.student']
        for re_reg_rec in student_rereg_obj.browse(active_ids):
            if re_reg_rec.confirm == False:
                encoded_data = base64.b64encode(re_reg_rec.code)
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                c_link = base_url + '/student/re_registration/request?REREG=%s'%(encoded_data)
                # send mail

                email_server = self.env['ir.mail_server']
                email_sender = email_server.search([], limit=1)
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('edsys_edu_re_registration', 'email_template_resend_re_registration_request_student')[1]
                template_rec = self.env['mail.template'].browse(template_id)
                body_html = template_rec.body_html
                body_dynamic_html = template_rec.body_html
                body_dynamic_html += '<p><a href=%s><button>Click here</button>to complete the Re-registration form</a></p></div>'%(c_link)
                template_rec.write({'email_to': re_reg_rec.name.parents1_id.parents_email,
                                    'email_from': email_sender.smtp_user,
                                    'email_cc': '',
                                    'body_html': body_dynamic_html})
                template_rec.send_mail(re_reg_rec.id)
                template_rec.body_html = body_html

