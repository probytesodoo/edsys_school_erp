from openerp import models, fields, api, _
from openerp.exceptions import except_orm

class ResendPayfortLinkInherit(models.TransientModel):

    _inherit = 'invoice.resend.payfort'

    @api.multi
    def resend_payfort_link(self):
        print '============resend payfort link -------invoice resend .payfort==='
        """
        Resend payfort payment link for particular invoice.
        ---------------------------------------------------
        @overide method : resend_payfort_link (edsys_edu_re_registration)
        :return:
        """
        invoice_obj = self.env['account.invoice']
        obj_ir_sequence = self.env['ir.sequence']
        active_ids=self._context['active_ids']
        for invoice_rec in invoice_obj.browse(active_ids):
            if invoice_rec.state == 'open':
                ir_sequence_ids = obj_ir_sequence.sudo().search([('name','=','Invoice Number Sequence')])
                if ir_sequence_ids:
                    invoice_number = obj_ir_sequence.next_by_code(ir_sequence_ids.id)
                    invoice_rec.invoice_number = invoice_number
                # send payfort link
                active_payforts=self.env['payfort.config'].search([('active','=','True')])

                if len(active_payforts) > 1:
                    raise except_orm(_('Warning!'),_("There should be only one payfort record!"))

                if not active_payforts.id:
                    raise except_orm(_('Warning!'),_("Please create Payfort Details First!"))

                payfort_amount = invoice_rec.residual
                advance_amount = 0.00
                if invoice_rec.partner_id.advance_total_recivable > 0.00:
                    advance_amount += invoice_rec.partner_id.advance_total_recivable
                if invoice_rec.partner_id.re_reg_total_recivable > 0.00:
                    advance_amount += invoice_rec.partner_id.re_reg_total_recivable
                if invoice_rec.partner_id.parents1_id.id:
                    if invoice_rec.partner_id.parents1_id.advance_total_recivable > 0.00:
                        advance_amount += invoice_rec.partner_id.parents1_id.advance_total_recivable
                    if invoice_rec.partner_id.parents1_id.re_reg_total_recivable > 0.00:
                        advance_amount += invoice_rec.partner_id.parents1_id.re_reg_total_recivable
                payfort_amount -= advance_amount
                payable_amount = 0.00
                if payfort_amount > 0.00:
                    payable_amount = payfort_amount
                    link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(payfort_amount,invoice_rec.invoice_number)
                    table_data = ''
                    table_data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' \
                                                      %(invoice_rec.partner_id.name,invoice_rec.number,invoice_rec.date_invoice,invoice_rec.amount_total,invoice_rec.residual)

                    total_advance_amt = 0.0
                    #student advance amount
                    student_advance_received = 0.0
                    if invoice_rec.partner_id.advance_total_recivable == False and invoice_rec.partner_id.re_reg_total_recivable == False:
                        student_advance_received = 0.0
                    elif invoice_rec.partner_id.advance_total_recivable > 0.0 or invoice_rec.partner_id.re_reg_total_recivable > 0.0:
                        student_advance_received = invoice_rec.partner_id.advance_total_recivable + invoice_rec.partner_id.re_reg_total_recivable
                    total_advance_amt += student_advance_received

                    #parent advance amount
                    parent_advance_received = 0.0
                    if invoice_rec.partner_id.parents1_id.advance_total_recivable == False and invoice_rec.partner_id.parents1_id.re_reg_total_recivable == False:
                        parent_advance_received = 0.0
                    elif invoice_rec.partner_id.parents1_id.advance_total_recivable > 0.0 or invoice_rec.partner_id.parents1_id.re_reg_total_recivable > 0.0:
                        parent_advance_received = invoice_rec.partner_id.parents1_id.advance_total_recivable +invoice_rec.partner_id.parents1_id.re_reg_total_recivable
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
                        template_rec.send_mail(invoice_rec.id,force_send=True)
                        template_rec.body_html = body_html

class ResendPayfortWizinheritPayfort(models.Model):

    _inherit='resend.payfort.wiz'

    @api.model
    def resend_mail_for_payfort_payment(self,parent,total_amount,order_id,table_date,advance_table,\
                                        voucher,advance_amt,invoice_amt):
        print '=============resend_mail_for_payfort_payment ----inherit-------------'
        """
        send mail to parent for all student fee with payfort payment link,
        also show invoice detail and advance payment detail as well.
        ------------------------------------------------------------------
        :param parent: parent record set
        :param total_amount: total amount have to pay
        :param order_id: Reference number
        :param table_date: student invoice table data
        :param advance_table: student advance table data
        :param voucher: voucher record set
        :param advance_amt: student advance amount
        :param invoice_amt: total invoice amount
        :return:
        """


        charge = 0.0
        payable_amount = total_amount
        obj_ir_sequence = self.env['ir.sequence']
        #PARENTS ADVANCE AMOUNT
        # advance_amt += parent.advance_total_recivable or 0.00 + parent.re_reg_total_recivable or 0.00
        if voucher:
            ir_sequence_ids = obj_ir_sequence.sudo().search([('name','=','Voucher Number Sequence')])
            if ir_sequence_ids:
                voucher_number = obj_ir_sequence.next_by_code(ir_sequence_ids.id)
                voucher.voucher_number = voucher_number
        parent_total_recivable = 0.0
        if parent.advance_total_recivable == False and parent.re_reg_total_recivable == False:
            parent_total_recivable = 0.0
        elif parent.advance_total_recivable > 0.0 or parent.re_reg_total_recivable > 0.0:
            parent_total_recivable = parent.advance_total_recivable or 0.00 + parent.re_reg_total_recivable or 0.00
            advance_amt += parent_total_recivable
        link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(total_amount,voucher.voucher_number)
        email_server = self.env['ir.mail_server']
        email_sender = email_server.search([], limit=1)
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_edu_fee', 'email_template_academic_fee_payment_reminder')[1]
        template_rec = self.env['mail.template'].browse(template_id)
        body_html = template_rec.body_html
        body_dynamic_html = template_rec.body_html + '<p>Pending Invoice Details:</p>'
        body_dynamic_html += '<table border=%s>'%(2)
        body_dynamic_html += '<tr><td><b>Child Name</b></td><td><b>Invoice number</b></td><td><b>Invoice date</b></td><td><b>Invoice amount</b></td><td><b>Pending amount</b></td></tr>%s'%(table_date)
        body_dynamic_html += '<tr><td><b>Total</b></td><td></td><td></td><td></td><td><b>%s</b></td></tr></table><br/>'%(invoice_amt)
        body_dynamic_html += 'Total advances (if any):<br/>'
        body_dynamic_html += '<table border=%s>'%(2)
        body_dynamic_html += '<tr><td><b>Parent Code</b></td><td><b>Student</b></td><td><b>Advance Value</b></td></tr>%s'%(advance_table)
        body_dynamic_html += '<tr><td>%s</td><td></td><td>%s</td></tr>'%(parent.parent1_id,parent_total_recivable)
        body_dynamic_html += '<tr><td><b>Total advances</b></td><td></td><td><b>%s</b></td></tr></table>'%(advance_amt)
        body_dynamic_html += '<p>Total outstanding payment is AED %s</p></div>'%(payable_amount)
        body_dynamic_html += '<p><a href=%s><button>Click Here</button>to pay Fee</a></p></div>'%(link)
        template_rec.write({'email_from': email_sender.smtp_user,
                            'email_to': parent.parents_email,
                            'email_cc': '',
                            'body_html': body_dynamic_html})
        template_rec.send_mail(voucher.id, force_send=True)
        template_rec.body_html = body_html
