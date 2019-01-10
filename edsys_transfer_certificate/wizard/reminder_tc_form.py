from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import except_orm
import base64

class SendReminderTransferCertificate(models.TransientModel):

    _name = 'send.reminder.tc.form.wiz'

    @api.multi
    def resend_tc_form_link(self):
        """
        this method is use to resend request for
        TC form link.
        :return:
        """
        active_ids = self._context['active_ids']
        tc_obj = self.env['trensfer.certificate']
        for tc_student_rec in tc_obj.browse(active_ids):
            if tc_student_rec.tc_form_filled == True:
                raise except_orm(_("Warning!"), _(' Already Transfer Certificate form is filled by the student %s.')
                                 %(tc_student_rec.name.name))
            if tc_student_rec.tc_form_filled != True:
                email_server=self.env['ir.mail_server']
                email_sender=email_server.search([])
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('edsys_transfer_certificate', 'email_template_resend_tc_form_email')[1]
                template_rec = self.env['mail.template'].browse(template_id)
                template_rec.write({'email_to' : tc_student_rec.name.parents1_id.parents_email,'email_from':email_sender.smtp_user, 'email_cc': ''})
                template_rec.send_mail(tc_student_rec.id, force_send=True)
                tc_student_rec.write({'last_date_of_tc_request_form':datetime.now(),})
