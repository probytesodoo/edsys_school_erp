from odoo import models, fields, api, _

class reject_reason_wiz(models.TransientModel):

    _name='reject.reason.wiz'
    
    reason = fields.Char(string="Please mention reason to reject this record",size=126)
    
    @api.multi
    def reject_state(self):
        active_ids=self.env.context['active_ids']
        reg_obj=self.env['registration'].browse(active_ids)
        for reg_rec in reg_obj:
            if reg_rec.state == 'awaiting_fee':
                reg_rec.student_id.active=False

            if reg_rec.state == 'pending':
                reg_rec.state_dropdown = reg_rec.state
                reg_rec.decision_reject_state()
            else:
                reg_rec.write({'state_hide_ids':[(0,0, {'reg_id': reg_rec.id,'state_name':reg_rec.state})],
                               'state_hide':reg_rec.state})
                reg_rec.state_dropdown = reg_rec.state
                reg_rec.state_dropdown = reg_rec.state
                
            email_server=self.env['ir.mail_server']
            email_sender=email_server.search([])
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_edu',
                                                             'email_template_student_reject')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            template_rec.write({'email_to' : reg_rec.email,'email_from':email_sender.smtp_user,
                                'email_cc': ''})
            #template_rec.send_mail(reg_rec.id, force_send=True)
            
            reg_rec.state = 'rejected'
            reg_rec.reject_reason=self.reason
