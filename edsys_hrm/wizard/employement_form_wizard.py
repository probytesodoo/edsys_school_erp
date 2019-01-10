from odoo import models, fields, api, _
# from odoo.osv import osv

class employement_form_wizard(models.Model):
    _name = 'employement.form.wizard'

    @api.multi
    def send_employement_form(self):
        context = self._context
        active_ids = context['active_ids']
        active_model = context['active_model']
        hr_recs=self.env[active_model].browse(active_ids)
        for hr_rec in hr_recs :
            if hr_rec.active_employee : 
                if not hr_rec.work_email : 
                    raise osv.except_osv(_('Warning!'), _('Please specify work email of existing employee.'))
                else :
                    email_to = hr_rec.work_email
                
            else : 
                if not hr_rec.email_id : 
                    raise osv.except_osv(_('Warning!'), _('Please specify personal email of new employee.'))
                else :
                    email_to = hr_rec.email_id
            hr_rec.employment_application_form_link = '/employee/employment-form?employee=%s'%(hr_rec.id)
            
            # send mail to employee to fill the information
            if  hr_rec.employee_state != 'employee':
                raise osv.except_osv(_('Warning!'), _('For Candidate please use resend application form'))
                
            # send mail to employee to fill the information
                    
            if  hr_rec.employee_state == 'employee':
                email_server=self.env['ir.mail_server']
                email_sender=email_server.search([])[0]
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('edsys_hrm', 'email_template_for_existing_employee')[1]
                template_rec = self.env['mail.template'].browse(template_id)
                template_rec.write({'email_to' : email_to,'email_from':email_sender.smtp_user})
                template_rec.send_mail(hr_rec.id, force_send=True)
        return True
            