from odoo import models, fields, api, _
# from odoo.osv import osv
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import datetime

class extend_probation_wizard(models.Model):
    _name = 'extend.probation.wizard'

    extend_probation_days = fields.Integer('Extend Probation Period In Days')
    
    @api.multi
    def extend_probation_button(self):
        context = self._context
        active_ids = context['active_ids']
        active_model = context['active_model']
        hr_recs=self.env[active_model].browse(active_ids)
        for hr_rec in hr_recs :
            probation_period = int(hr_rec.probation_period)
            if self.extend_probation_days < probation_period :
                raise osv.except_osv('Warning', 'Employee %s already has probation more than %s ' %(hr_rec.name, self.extend_probation_days))
            elif self.extend_probation_days == probation_period :
                raise osv.except_osv('Warning', 'Employee %s already has probation %s ' %(hr_rec.name, self.extend_probation_days))
            
            hr_rec.probation_period = self.extend_probation_days
            
            first_day_office = datetime.datetime.strptime(hr_rec.first_day_office, DATE_FORMAT)
            probation_completion_date = first_day_office + datetime.timedelta(days= self.extend_probation_days)
            hr_rec.probation_completion_date = probation_completion_date
            # send mail to employee to fill the information
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])[0]
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_hrm', 'probation_extend_email_template_edi')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            email_to = hr_rec.work_email +','+hr_rec.email_id
            template_rec.write({'email_to' : email_to,'email_from':email_sender.smtp_user})
            template_rec.send_mail(hr_rec.id, force_send=True)
#             template_rec.write({'email_to' : hr_rec.email_id,'email_from':email_sender.smtp_user})
#             template_rec.send_mail(hr_rec.id, force_send=True)
             
        return True
            