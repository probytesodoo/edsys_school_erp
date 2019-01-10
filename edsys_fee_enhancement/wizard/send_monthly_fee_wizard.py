from odoo import models, fields, api, _
# from odoo.osv import osv

class send_monthly_fee_wizard(models.Model):
    _name = 'send.monthly.fee.wizard'

    @api.multi
    def send_monthly_fee_button(self):
        context = self._context
        active_ids = context['active_ids']
        active_model = context['active_model']
        
        for fee_active_id in active_ids :
            fee_payment_obj = self.env['fee.payment']
            fee_payment_rec = fee_payment_obj.browse(fee_active_id)
            if fee_payment_rec.fee_payment_line_ids :
                invoice_obj = self.env['account.invoice']
                invoice_recs = invoice_obj.search([('batch_id','=',fee_payment_rec.academic_year_id.id), ('month_id','=',fee_payment_rec.month.id)])
                for invoice_rec in invoice_recs :
                    if invoice_rec.partner_id.class_id == fee_payment_rec.course_id :
                        payfort_amount = invoice_rec.residual
                        if payfort_amount > 0.00:
                            if invoice_rec.fee_calculation_mail_sent == False :
                                payable_amount = payfort_amount
                                link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(payfort_amount,invoice_rec.invoice_number)
                                if invoice_rec.partner_id.parents1_id :
                                    student_rec = invoice_rec.partner_id
                                
                                month_value = str(dict(invoice_obj.fields_get(allfields=['month'])['month']['selection'])[invoice_rec.month])
                                email_server = self.env['ir.mail_server']
                                email_sender = email_server.search([], limit=1)
                                ir_model_data = self.env['ir.model.data']
                                template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_monthly_fee_calculation')[1]
                                template_rec = self.env['email.template'].browse(template_id)
                                body_html = template_rec.body_html
                                body_dynamic_html = template_rec.body_html + '<p>The total fee amount for the month of %s is AED %s.'%(month_value,invoice_rec.amount_total)
                                body_dynamic_html += 'After adjusting your advances, the amount you have to pay is AED %s.'%(payable_amount)
                                body_dynamic_html += ' The fee details are listed in the invoice attached </p>'
                                body_dynamic_html += '<a href=%s><button>Click Here</button>For Online Payment</a></div>'%(link)
                                template_rec.write({'email_to': student_rec.parents1_id.parents_email,
                                                    'email_from': email_sender.smtp_user,
                                                    'email_cc': '',
                                                    #'email_cc': 'scbagdebackup1@gmail.com',
                                                    'body_html': body_dynamic_html})
                                template_rec.send_mail(invoice_rec.id, force_send=False)
                                # Stop Email
                                # template_rec.send_mail(invoice_rec.id)
                                template_rec.body_html = body_html
                                invoice_rec.fee_calculation_mail_sent = True
        return True
            
