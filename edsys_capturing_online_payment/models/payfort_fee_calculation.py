from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp
import time,re
import base64

class FeePaymentInheritPayfort(models.Model):

    _inherit = 'fee.payment'

    @api.model
    def send_payforts_link(self, student_total_receivable,parent_total_receivable,student_rec, invoice_rec):
        """
        this method is use to send payfort link for online pay fee using payfort payment getway.
        ---------------------------------------------------------------------------------------
        :param student_total_receivable: student credit
        :param parent_total_receivable: parent credit
        :param student_rec: student record set
        :param invoice_rec: invoice record set
        :return:
        """
        if self._context and 'send_mail' in self._context and not self._context['send_mail']:
            advance_paid_amount = 0.00
            if student_total_receivable < 0.00:
                advance_paid_amount += abs(student_total_receivable)
            return_parent = abs(parent_total_receivable)
            if parent_total_receivable < 0.00:
                if student_total_receivable > 0.00:
                    if abs(parent_total_receivable) >= abs(student_total_receivable):
                        return_parent = return_parent - abs(student_total_receivable)
                    else:
                        parent_total_receivable = 0.00
                advance_paid_amount += return_parent
            return parent_total_receivable
        month_value = str(dict(self.env['account.invoice'].fields_get(allfields=['month'])['month']['selection'])[invoice_rec.month])
        advance_paid_amount = 0.00
        if student_total_receivable < 0.00:
            advance_paid_amount += abs(student_total_receivable)
        return_parent = abs(parent_total_receivable)
        if parent_total_receivable < 0.00:
            if student_total_receivable > 0.00:
                if abs(parent_total_receivable) >= abs(student_total_receivable):
                    return_parent = return_parent - abs(student_total_receivable)
                else:
                    parent_total_receivable = 0.00
            advance_paid_amount += return_parent
        active_payforts = self.env['payfort.config'].search([('active', '=', 'True')])

        if len(active_payforts) > 1:
            raise except_orm(_('Warning!'), _("There should be only one payfort record!"))

        if not active_payforts.id:
            raise except_orm(_('Warning!'), _("Please create Payfort Details First!"))

        payfort_amount = invoice_rec.residual
        if payfort_amount > 0.00:
            # if payfort amount greter then advance payment then mail send for payment
            # payfort_amount -= advance_paid_amount   //removed -it was deducting the advance twice from the invoiced amt aftr bulk reconciliation
            payable_amount = payfort_amount
            link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(payfort_amount,invoice_rec.invoice_number)
            # send mail to every student whos pay fee this month
            attachment_obj = self.env['ir.attachment']
            result = False
            for record in invoice_rec:
                ir_actions_report = self.env['ir.actions.report.xml']
                matching_report = ir_actions_report.search([('name', '=', 'Invoices Attachment')])
                if matching_report:
                    result, format = openerp.report.render_report(self._cr, self._uid, [record.id],
                                                                  matching_report.report_name, {'model': 'account.invoice'})
                    eval_context = {'time': time, 'object': record}
                    if matching_report.attachment or not eval(matching_report.attachment, eval_context):
                        result = base64.b64encode(result)
                        file_name = record.name_get()[0][1]
                        file_name = re.sub(r'[^a-zA-Z0-9 ]', '_', file_name)
                        file_name += ".pdf"
                        attachment_id = attachment_obj.create({
                            'name': file_name,
                            'datas': result,
                            'datas_fname': file_name,
                            'res_model': invoice_rec._name,
                            'res_id': invoice_rec.id,
                            'type': 'binary'
                        })

            email_server = self.env['ir.mail_server']
            email_sender = email_server.search([], limit=1)
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_monthly_fee_calculation')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            body_html = template_rec.body_html
            body_dynamic_html = template_rec.body_html + '<p>The total fee amount for the month of %s is AED %s.'%(month_value,invoice_rec.amount_total)
            body_dynamic_html += 'After adjusting your advances, the amount you have to pay is AED %s.'%(payable_amount)
            body_dynamic_html += ' The fee details are listed in the invoice attached </p>'
            body_dynamic_html += '<a href=%s><button>Click Here</button>For Online Payment</a></div>'%(link)
            template_rec.write({'email_to': student_rec.parents1_id.parents_email,
                                'email_from': email_sender.smtp_user,
                                'email_cc': '',
                                'body_html': body_dynamic_html})
	    # template_rec.send_mail(invoice_rec.id, force_send=True)
            # Stop Email
            # template_rec.send_mail(invoice_rec.id, force_send=True)
            template_rec.body_html = body_html
        return parent_total_receivable
