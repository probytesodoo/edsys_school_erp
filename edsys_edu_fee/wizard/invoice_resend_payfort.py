from odoo import models, fields, api, _
from odoo.exceptions import except_orm
import hashlib

class ResendPayfortLink(models.TransientModel):

    _name='invoice.resend.payfort'

    @api.multi
    def resend_payfort_link(self):
        print '=============resend payfort link------------name===='
        invoice_obj = self.env['account.invoice']
        active_ids=self._context['active_ids']

        for invoice_rec in invoice_obj.browse(active_ids):
            if invoice_rec.state == 'open':
                # send payfort link
                active_payforts=self.env['payfort.config'].search([('active','=','True')])

                if len(active_payforts) > 1:
                    raise except_orm(_('Warning!'),_("There should be only one payfort record!"))

                if not active_payforts.id:
                    raise except_orm(_('Warning!'),_("Please create Payfort Details First!"))

                payfort_amount = invoice_rec.residual
                advance_amount = 0.00
                if invoice_rec.partner_id.credit < 0.00:
                    advance_amount += abs(invoice_rec.partner_id.credit)
                if invoice_rec.partner_id.parents1_id.id:
                    if invoice_rec.partner_id.parents1_id.credit < 0.00:
                        advance_amount += abs(invoice_rec.partner_id.parents1_id.credit)
                payfort_amount -= advance_amount
                payable_amount = 0.00
                if payfort_amount > 0.00:
                    payable_amount = payfort_amount
                    
                    link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(payable_amount,invoice_rec.invoice_number)
                    table_data = ''
                    table_data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                                      %(invoice_rec.partner_id.name,invoice_rec.number,invoice_rec.date_invoice,invoice_rec.amount_total,invoice_rec.residual)
                    total_advance_amt = 0.0
                    #student advance amount
                    student_advance_received = 0.0
                    if invoice_rec.partner_id.advance_total_recivable == False:
                        student_advance_received = 0.0
                    elif invoice_rec.partner_id.advance_total_recivable > 0.0:
                        student_advance_received = invoice_rec.partner_id.advance_total_recivable
                    total_advance_amt += student_advance_received

                    #parent advance amount
                    parent_advance_received = 0.0
                    if invoice_rec.partner_id.parents1_id.advance_total_recivable == False:
                        parent_advance_received = 0.0
                    elif invoice_rec.partner_id.parents1_id.advance_total_recivable > 0.0:
                        parent_advance_received = invoice_rec.partner_id.parents1_id.advance_total_recivable
                    total_advance_amt += parent_advance_received

                    # resend mail to the parent
                    if invoice_rec.partner_id.is_parent == False:
                        email_server = self.env['ir.mail_server']
                        email_sender = email_server.search([], limit=1)
                        ir_model_data = self.env['ir.model.data']
                        template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_resend_academic_fee_payment_link')[1]
                        template_rec = self.env['mail.template'].browse(template_id)
                        body_html = template_rec.body_html
                        body_dynamic_html = template_rec.body_html + '<p>Pending Invoice Details:</p>'
                        body_dynamic_html += '<table border=%s>'%(2)
                        body_dynamic_html += '<tr><td><b>Child Name</b></td><td><b>Invoice number</b></td><td><b>Invoice date</b></td><td><b>Invoice amount</b></td><td><b>Pending amount</b></td></tr>%s'%(table_data)
                        body_dynamic_html += '<tr><td><b>Total</b></td><td></td><td></td><td></td><td><b>%s</b></td></tr></table><br/>'%(invoice_rec.residual)
                        body_dynamic_html += 'Total advances (if any):<br/>'
                        body_dynamic_html += '<table border=%s>'%(2)
                        body_dynamic_html += '<tr><td><b>Parent Code</b></td><td><b>Student</b></td><td><b>Advance Value</b></td></tr>'
                        body_dynamic_html += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>'%(invoice_rec.partner_id.parents1_id.parent1_id,invoice_rec.partner_id.name,student_advance_received)
                        body_dynamic_html += '<tr><td>%s</td><td></td><td>%s</td></tr>'%(invoice_rec.partner_id.parents1_id.parent1_id,parent_advance_received)
                        body_dynamic_html += '<tr><td><b>Total advances</b></td><td></td><td><b>%s</b></td></tr></table>'%(total_advance_amt)
                        body_dynamic_html += '<p>Total outstanding payment is AED %s</p></div>'%(payable_amount)
                        body_dynamic_html += '<p><a href=%s><button>Click Here</button>to pay Fee</a></p></div>'%(link)
                        template_rec.write({'email_from': email_sender.smtp_user,
                                            'email_to': invoice_rec.partner_id.parents1_id.parents_email,
                                            'email_cc': '',
                                            'body_html': body_dynamic_html})
                        raise except_orm(_("Warning!"), _('stop'))
                        template_rec.send_mail(invoice_rec.id,force_send=True)
                        template_rec.body_html = body_html

