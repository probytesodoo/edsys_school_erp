from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import except_orm, Warning, RedirectWarning

class SendRequestTransferCertificate(models.TransientModel):

    _name = 'tc.form.request.wiz'

    student_ids = fields.Many2many('res.partner', 'tc_student_tbl', 'tc_id', 'student_id', 'Student')

    @api.multi
    def send_tc_form_request(self):
        """
        This method is use to select multiple student and create record for TC Process,
        also send mail for TC Form
        ------------------------------------------------------------------------------
        :return:
        """
        tc_obj = self.env['trensfer.certificate']
        for student_rec in self.student_ids:
            tc_ex_rec = tc_obj.search([('name', '=', student_rec.id)])
            if tc_ex_rec.id:
                raise except_orm(_('Warning!'),
                        _("The TC process has already been initiated for %s!")%(student_rec.name))
            tc_data = {
                'student_id': student_rec.student_id,
                'name': student_rec.id,
                'reg_no': student_rec.reg_no,
                'batch_id': student_rec.batch_id.id,
                'course_id': student_rec.course_id.id,
                'student_section_id': student_rec.student_section_id.id,
                'state': 'tc_requested'
            }
            tc_rec = tc_obj.create(tc_data)
            tc_rec.send_mail_for_tc_form()