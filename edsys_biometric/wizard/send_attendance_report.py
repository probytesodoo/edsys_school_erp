import odoo
from odoo import models, fields, api, _
# from odoo.osv import osv
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import datetime

class send_attendance_report(models.Model):
    _name = 'send.attendance.report'

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    
    @api.multi
    def send_attendance_report_button(self):
        context = self._context
        active_ids = context['active_ids']
        hr_employee_obj =self.env['hr.employee']
        hr_employee_recs = hr_employee_obj.browse(active_ids)
        for hr_employee_rec in hr_employee_recs :
            hr_employee_rec.attendance_report_from_date = self.from_date
            hr_employee_rec.attendance_report_to_date = self.to_date
            hr_attendance_obj =self.env['hr.attendance']
            hr_attendance_ids = hr_attendance_obj.search([('employee_id','=', hr_employee_rec.id),('name','>=', self.from_date),('name','<=', self.to_date)])
            #send mail
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])[0]
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_biometric', 'send_attendance_report_email_template')[1]
            template_rec = self.env['email.template'].browse(template_id)
            template_rec.write({'email_to' : hr_employee_rec.work_email,'email_from':email_sender.smtp_user})
            template_rec.send_mail(hr_employee_rec.id, force_send=True)
        #raise openerp.exceptions.AccessError(_("stop"))
        return True
            