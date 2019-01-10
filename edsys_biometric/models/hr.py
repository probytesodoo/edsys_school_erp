import odoo
from odoo import models, fields, api, _
# from odoo.osv import osv
import os
from datetime import datetime, timedelta

class hr_employee(models.Model):

    _inherit = "hr.employee"
    
    biometric_id = fields.Char('Biometric ID')
    attendance_ids = fields.One2many('hr.attendance','employee_id','Attendances' )
    attendance_report_from_date = fields.Date('Attendance Report From Date')
    attendance_report_to_date = fields.Date('Attendance Report To Date')

    @api.model
    def process_attendance_details(self, attendace_rec_list):
        hr_attendance = self.env['hr.attendance']
        logf = open("%s/../attendance_exception.log" %(os.path.dirname(os.path.abspath(__file__))), "w+")
        for attendace_rec in attendace_rec_list :
            try :
                employee_id = self.search([('biometric_id','=', attendace_rec['Emp_ID'])])
                attendace_in_vals = {}
                attendace_out_vals = {}
                if employee_id :
                        if attendace_rec['Status'] :
                            if attendace_rec['Status'] == 'P' :
                                status = 'present'
                            elif attendace_rec['Status'] == 'MS' :
                                status = 'missing_punch'
                            elif attendace_rec['Status'] == 'A' :
                                status = 'absent'

                        if attendace_rec['In_Punch'] :
                            format_In_Punch_strftime = datetime.strftime(attendace_rec['In_Punch'], "%Y-%m-%d %H:%M:%S")
                            attendace_in_vals = {
                                                 'employee_id' : employee_id.id,
                                                 'name' : format_In_Punch_strftime, #attendace_rec['In_Punch'] ,
                                                 'action' : 'sign_in',
                                                 'attendance_tag' : status
                                               }
                            hr_attendance__in_rec = hr_attendance.search([('attendance_tag', '=', status),('action', '=', 'sign_in'),('employee_id', '=', employee_id.id), ('name', '=', format_In_Punch_strftime)])
                            if not hr_attendance__in_rec :
                                hr_attendance.create(attendace_in_vals)
                                self.env.cr.commit()
                            else :
                                logf.write("Failed to import {0} because this record is already exists in Odoo \n".format(attendace_rec))

                        if attendace_rec['Out_Punch'] :
                            format_Out_Punch_strftime = datetime.strftime(attendace_rec['Out_Punch'], "%Y-%m-%d %H:%M:%S")
                            attendace_out_vals = {
                                                 'employee_id' : employee_id.id,
                                                 'name' : format_Out_Punch_strftime,
                                                 'action' : 'sign_out',
                                                 'attendance_tag' : status
                                               }
                            hr_attendance_out_rec = hr_attendance.search([('attendance_tag', '=', status),('action', '=', 'sign_out'),('employee_id', '=', employee_id.id), ('name', '=', format_Out_Punch_strftime)])
                            if not hr_attendance_out_rec :
                                hr_attendance.create(attendace_out_vals)
                                self.env.cr.commit()
                            else :
                                logf.write("Failed to import {0} because this record is already exists in Odoo \n".format(attendace_rec))
                else :
                    logf.write("Failed to import {0} because employee not exists in Odoo \n".format(attendace_rec))
            except Exception as e:     # most generic exception you can catch
                 logf.write("Failed to import {0}: {1} \n".format(attendace_rec, str(e)))
            finally:
                 # optional clean up code
                 pass
        return True


class hr_attendance(models.Model):

    _inherit = "hr.attendance"

    name = fields.Datetime('Date', required=True, select=1)
    attendance_tag = fields.Selection([('present','Present' ),('late','Late'),('left_early','Left Early'),('missing_punch','Missing Punch'),('absent','Absent')],'Attendance Tags')
    seek_review_wizard_id = fields.Many2one('attendance.review')
    justification = fields.Char('Justification')
    reject_reason = fields.Char('Rejection Reason')
    attendance_state = fields.Selection([('draft','Draft' ),('seek_review', 'Seek Review'),('confirmed', 'Confirmed'),('approved_by_reporting_manager','Approved By Reporting Manager'),('rejected_by_reporting_manager','Rejected By Reporting Manager'),('approved_by_hr_manager','Approved By HR Manager'),('rejected_by_hr_manager','Rejected By HR Manager'),('final','Final')],'Attendance State',default='draft')
    review_tags = fields.Selection([('corrected','Corrected' ),('excused', 'Excused')],'Review Tags')
    dubai_punch_date_format = fields.Char('Punch date', compute='get_dubai_punch_date_format')

    _defaults = {
        'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                }

    @api.one
    def get_dubai_punch_date_format(self):
        if self.name : 
            converted_date = datetime.strptime(self.name, "%Y-%m-%d %H:%M:%S")
#             print 'converted_date :::: ', converted_date, type(converted_date)
#             added_hour_date = str(converted_date + timedelta(hours=4))
#             print 'added_hour_date ::: ', added_hour_date
#             date_now = added_hour_date.split(" ")[0]
#             print 'date_now :::: ', date_now
#             time_now = datetime.strptime(added_hour_date.split(" ")[1], "%H:%M:%S").strftime("%I:%M %p")
#             print 'time_now :::: ', time_now
            self.dubai_punch_date_format = str(converted_date)#str(date_now) + " " + str(time_now)
            
    @api.model
    def _altern_si_so(self, ids):
        return True

    @api.multi
    def get_current_user(self):
        user_obj = self.env['res.users']
        user_value = user_obj.browse(self.env.user.id)
        for employee_id in self:
            employee_id.current_user = user_value.id

    action = fields.Selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('action','Action')], 'Action', required=True)
    current_user =fields.Char('User', compute='get_current_user')

    _constraints = [(_altern_si_so, 'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]

    @api.multi
    def approve_attendance_reporting_manager(self):
        reporting_manager = self.employee_id.parent_id
        if self.env.uid != 1 :
            if reporting_manager:
                if reporting_manager.user_id :
                    if reporting_manager.user_id.id ==  self.env.uid  :
                        # send email
                        email_server=self.env['ir.mail_server']
                        email_sender=email_server.search([])[0]
                        ir_model_data = self.env['ir.model.data']
                        template_id = ir_model_data.get_object_reference('edsys_biometric', 'attendance_approved_by_reporting_manager_email_template')[1]
                        template_rec = self.env['email.template'].browse(template_id)
                        template_rec.write({'email_to' : self.employee_id.work_email,'email_from':email_sender.smtp_user})
                        template_rec.send_mail(self.id, force_send=True)
                        self.attendance_state = 'approved_by_reporting_manager'
                        self.review_tags = 'excused'

                    else :
                        raise openerp.exceptions.AccessError(_("Respective Reporting Manager can Approve the attendance"))
                else :
                    raise openerp.exceptions.AccessError(_("Please assign Related User to Reporting Manager"))
            else :
                raise openerp.exceptions.AccessError(_("Please assign Reporting Manager to employee"))

        else :
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])[0]
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_biometric', 'attendance_approved_by_reporting_manager_email_template')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            template_rec.write({'email_to' : self.employee_id.work_email,'email_from':email_sender.smtp_user})
            template_rec.send_mail(self.id, force_send=True)
            self.attendance_state = 'approved_by_reporting_manager'
            self.review_tags = 'excused'

    @api.multi
    def approve_attendance_hr_manager(self):
        hr_manager = self.employee_id.hr_person
        if self.env.uid != 1 :
            if hr_manager:
                if hr_manager.user_id :
                    if hr_manager.user_id.id ==  self.env.uid  :
                        # send email
                        email_server=self.env['ir.mail_server']
                        email_sender=email_server.search([])[0]
                        ir_model_data = self.env['ir.model.data']
                        template_id = ir_model_data.get_object_reference('edsys_biometric', 'attendance_approved_by_hr_manager_email_template')[1]
                        template_rec = self.env['email.template'].browse(template_id)
                        template_rec.write({'email_to' : self.employee_id.work_email,'email_from':email_sender.smtp_user})
                        template_rec.send_mail(self.id, force_send=True)
                        self.attendance_state = 'approved_by_hr_manager'
                        self.review_tags = 'excused'

                    else :
                        raise openerp.exceptions.AccessError(_("Respective HR can Approve the attendance"))
                else :
                    raise openerp.exceptions.AccessError(_("Please assign Related User to HR Manager"))
            else :
                    raise openerp.exceptions.AccessError(_("Please assign HR Manager to employee"))

        else :
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])[0]
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_biometric', 'attendance_approved_by_hr_manager_email_template')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            template_rec.write({'email_to' : self.employee_id.work_email,'email_from':email_sender.smtp_user})
            template_rec.send_mail(self.id, force_send=True)
            self.attendance_state = 'approved_by_hr_manager'
            self.review_tags = 'excused'

    @api.multi
    def confirm_attendance(self):
        self.attendance_state = 'confirmed'

    @api.multi
    def reject_attendance_reporting_manager(self):
        reporting_manager = self.employee_id.parent_id
        if self.env.uid != 1 :
            if reporting_manager:
                if reporting_manager.user_id :
                    if reporting_manager.user_id.id ==  self.env.uid  :
                        if not self.reject_reason :
                            raise openerp.exceptions.AccessError(_("Please mention Rejection Reason"))
                        # send email
                        email_server=self.env['ir.mail_server']
                        email_sender=email_server.search([])[0]
                        ir_model_data = self.env['ir.model.data']
                        template_id = ir_model_data.get_object_reference('edsys_biometric', 'attendance_rejected_by_reporting_manager_email_template')[1]
                        template_rec = self.env['mail.template'].browse(template_id)
                        template_rec.write({'email_to' : self.employee_id.work_email,'email_from':email_sender.smtp_user})
                        template_rec.send_mail(self.id, force_send=True)
                        self.attendance_state = 'rejected_by_reporting_manager'
                        self.review_tags = 'excused'
                    else :
                        raise openerp.exceptions.AccessError(_("Respective Reporting can Approve the attendance"))
                else :
                    raise openerp.exceptions.AccessError(_("Please assign Related User to Reporting Manager"))
            else :
                raise openerp.exceptions.AccessError(_("Please assign Reporting Manager to employee"))

        else :
            if not self.reject_reason :
                raise openerp.exceptions.AccessError(_("Please mention Rejection Reason"))
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])[0]
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_biometric', 'attendance_rejected_by_reporting_manager_email_template')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            template_rec.write({'email_to' : self.employee_id.work_email,'email_from':email_sender.smtp_user})
            template_rec.send_mail(self.id, force_send=True)
            self.attendance_state = 'rejected_by_reporting_manager'
            self.review_tags = 'excused'


    @api.multi
    def reject_attendance_hr_manager(self):
        hr_manager = self.employee_id.hr_person
        if self.env.uid != 1 :
            if hr_manager:
                if hr_manager.user_id :
                    if hr_manager.user_id.id ==  self.env.uid  :
                        if not self.reject_reason :
                            raise openerp.exceptions.AccessError(_("Please mention Rejection Reason"))
                        # send email
                        email_server=self.env['ir.mail_server']
                        email_sender=email_server.search([])[0]
                        ir_model_data = self.env['ir.model.data']
                        template_id = ir_model_data.get_object_reference('edsys_biometric', 'attendance_rejected_by_hr_manager_email_template')[1]
                        template_rec = self.env['email.template'].browse(template_id)
                        template_rec.write({'email_to' : self.employee_id.work_email,'email_from':email_sender.smtp_user})
                        template_rec.send_mail(self.id, force_send=True)
                        self.attendance_state = 'rejected_by_hr_manager'
                        self.review_tags = 'excused'

                    else :
                        raise openerp.exceptions.AccessError(_("Respective HR can Approve the attendance"))
                else :
                    raise openerp.exceptions.AccessError(_("Please assign Related User to HR Manager"))
            else :
                raise openerp.exceptions.AccessError(_("Please assign HR Manager to employee"))
        else :
            if not self.reject_reason :
                raise openerp.exceptions.AccessError(_("Please mention Rejection Reason"))
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])[0]
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_biometric', 'attendance_rejected_by_hr_manager_email_template')[1]
            template_rec = self.env['email.template'].browse(template_id)
            template_rec.write({'email_to' : self.employee_id.work_email,'email_from':email_sender.smtp_user})
            template_rec.send_mail(self.id, force_send=True)
            self.attendance_state = 'rejected_by_hr_manager'
            self.review_tags = 'excused'
