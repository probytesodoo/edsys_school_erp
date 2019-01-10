from odoo import models, fields, api, _
# from odoo.osv import osv

class send_academic_fee_receipt_wizard(models.Model):
    _name = 'send.academic.fee.receipt.wizard'

    @api.multi
    def send_academic_fee_receipt_button(self):
        context = self._context
        active_ids = context['active_ids']
        active_model = context['active_model']
        for active_id in active_ids :
            reg_obj = self.env['registration']
            reg_rec = reg_obj.browse(active_id)
            if reg_rec.state == 'awaiting_fee' :
                voucher_obj = self.env['account.voucher']
                voucher_id = voucher_obj.search([('invoice_id', '=', reg_rec.invoice_id.id)])
                #send mail
                mail_obj=self.env['mail.mail']
                email_server=self.env['ir.mail_server']
                email_sender=email_server.search([])
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('edsys_edu', 'email_template_academic_fee_receipt_paid')[1]
                template_rec = self.env['mail.template'].browse(template_id)
                template_rec.write({'email_to' : reg_rec.email,'email_from':email_sender.smtp_user, 'email_cc': ''})
                template_rec.send_mail(voucher_id.id, force_send=True)
        return True
            
