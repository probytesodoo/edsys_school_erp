# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import base64
import time
from datetime import datetime, date
import hashlib


class TransferCertificate(models.Model):
    _name = 'trensfer.certificate'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Transfer Certificate"


    currency_id = fields.Many2one('res.currency',
        string='Currency', readonly=True, default=lambda self: self._get_currency())
   


    # @api.model
    # def _default_journal(self):
    #     voucher_type = self._context.get('voucher_type', 'sale')
    #     company_id = self._context.get('company_id', self.env.user.company_id.id)
    #     domain = [
    #         ('type', '=', voucher_type),
    #         ('company_id', '=', company_id),
    #     ]
    #     return self.env['account.journal'].search(domain, limit=1)

    @api.one
    @api.depends('journal_id', 'company_id')
    def _get_journal_currency(self):
        self.currency_id = self.journal_id.currency_id.id or self.company_id.currency_id.id

    @api.depends('credit','parent_credit')
    def genarate_payfort_payment_link(self):
        """
        payfort Payment link genarate and
        display form front end,
        -----------------------------------
        :return:
        """
        for record in self:
            amount = record.credit + record.parent_credit
            payfort_link = ''
            if amount > 0.00:
                payfort_link = record._get_payfort_payment_link(amount=amount, order_id=self.transfer_certificate_number)
            else:
                payfort_link = ''
            record.tc_payment_link = payfort_link
            
    @api.multi
    def write(self, vals):
        ir_attachment = self.env['ir.attachment']
        upload_tc_certificate = None
        if 'upload_tc_certificate' in vals:
                upload_tc_certificate = vals['upload_tc_certificate']
        if upload_tc_certificate :
            upload_tc_certificate_ids = ir_attachment.sudo().search([('name','=','Tc Attachment'), ('res_id','=',self.id)])
            if upload_tc_certificate_ids :
                upload_tc_certificate_ids.sudo().write(  {
                                                          'name': 'Tc Attachment',
                                                           'res_model':  'trensfer.certificate',
                                                           'res_id': self.id,
                                                           'datas': base64.b64encode(upload_tc_certificate),
                                                           'type': 'url'
                                                            }  )
            else : 
                ir_attachment.sudo().create({
                                                    'name': 'Tc Attachment',
                                                   'res_model':  'trensfer.certificate',
                                                   'res_id': self.id,
                                                   'datas': base64.b64encode(upload_tc_certificate),
                                                   'type': 'url'
                                                   })
        res = super(TransferCertificate, self).write(vals)
        return res

    @api.depends('actual_receivables_invoice')
    def compute_total_receivables_amount(self):
        # print '-------------compute_total_receivables_amount---------------'
        """
        this method is compute total receivables amount of student,
        ------------------------------------------------------------
        :return:
        """
        for record in self:
            total_receivables_amount = 0.00
            for receivables_inv_rec in record.actual_receivables_invoice:
                total_receivables_amount += receivables_inv_rec.residual
            record.total_receivables_amount = total_receivables_amount
            # print record.total_receivables_amount,'----------------------------------record.total_receivables_amount'

    @api.depends('actual_paid_invoice')
    def compute_total_paid_amount(self):
        # print '------------compute_total_paid_amount---------------'
        """
        This method is use to compute total paid amount of student,
        :return:
        """
        for record in self:
            # print record,'========================record'
            total_paid_amount = 0.00
            for paid_inv_rec in record.actual_paid_invoice:
                # print paid_inv_rec,'======================paid_inv_rec'
                total_paid_amount += paid_inv_rec.residual
            record.total_paid_amount = total_paid_amount
            # print record.total_paid_amount,'====================record.total_paid_amount'

    code = fields.Char('Code')
    student_id = fields.Char('Student Id')
    name = fields.Many2one('res.partner', 'Name')
    reg_no = fields.Char('Registration')
    batch_id = fields.Many2one("batch", "Current Academic Year")
    course_id = fields.Many2one('course', 'Current Admission To Class')
    student_section_id = fields.Many2one('section', 'Current Admission To Section')
    state = fields.Selection([('tc_requested', 'TC requested'),
                              ('fee_balance_review', 'Fee Balance Review'),
                              ('final_fee_awaited', 'Fee Clearance'),
                              ('tc_complete', 'TC Process Completed'),
                              ('tc_cancel', 'TC Withdrawn'),
                              ], 'State', track_visibility='onchange')
    cancel_state = fields.Selection([('tc_requested', 'TC Requested'),
                                     ('fee_balance_review', 'Fee Balance Review'),
                                     ('final_fee_awaited', 'Fee Clearance'),
                                     ('tc_cancel', 'TC Withdrawn')], track_visibility='onchange')
    tc_form_filled  = fields.Boolean('TC Form Filled')
    last_date_of_tc_request_form = fields.Date('Date of TC Request Form Send')
    new_school_name = fields.Char('New School Name')
    tc_type = fields.Selection([('within_uae', 'Different Emirate'),
                                ('outside_uae','Outside UAE'),
                                ('within_dubai', 'Within Same Emirate')], track_visibility='onchange')
    reason_for_leaving = fields.Char('Reason for Leaving')
    tc_form_fill_link = fields.Char('Link for TC Form fill up')
    last_date_for_accounting = fields.Date('Last date for Accounting')
    actual_paid_invoice = fields.Many2many('account.invoice', 'tc_paid_invoice_tbl', 'tc_id', 'inv_id')
    actual_receivables_invoice = fields.Many2many('account.invoice', 'tc_receivables_invoice_tbl', 'tc_id', 'inv_id')
    total_receivables_amount = fields.Float(compute='compute_total_receivables_amount')
    total_paid_amount = fields.Float(compute='compute_total_paid_amount')
    tc_fee_stucture = fields.Many2many('tc.fees.line', 'tbl_tc_fee', 'tc_id', 'fee_line_id')
    credit = fields.Monetary(related='name.credit')
    advance_total_recivable = fields.Float(related='name.advance_total_recivable')
    re_reg_total_recivable = fields.Float(related='name.re_reg_total_recivable')
    parent_credit = fields.Monetary(related='name.parents1_id.credit')
    parent_advance_total_recivable = fields.Float(related='name.parents1_id.advance_total_recivable')
    parent_re_reg_total_recivable = fields.Float(related='name.parents1_id.re_reg_total_recivable')
    cal_total_due = fields.Boolean('Final Total Due')
    reason = fields.Char(string="Please mention reason to Cancel this TC application", size=126)
    tc_payment_link = fields.Char(stirng='Payfort Payment Link', compute='genarate_payfort_payment_link')
    khda_reference_number = fields.Char('KHDA Reference No')
    grade = fields.Many2one(related ='name.class_id')
    section = fields.Many2one(related='name.student_section_id')
    khada_sis_number = fields.Char(related='name.khada_sis')
    last_attendance_date = fields.Date(related='name.last_attendance_date')
    upload_tc_certificate =fields.Binary(string='File Name')
    res_partner_id = fields.Many2one('res.partner')
    transfer_certificate_number = fields.Char('Transfer Certificate Number',readolny=True)
    
#     
    
    

    @api.multi
    def ministry_approval_confirm(self):
        """
        final approval by ministry,
        --------------------------------
        :return:
        """
        email_server = self.env['ir.mail_server']
        email_sender = email_server.search([])
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_transfer_certificate', 'email_template_tc_issuance_email')[1]
        template_rec = self.env['mail.template'].browse(template_id)
        template_rec.write({'email_to': self.name.parents1_id.parents_email,
                            'email_from': email_sender.smtp_user,
                            'email_cc': ''})
        template_rec.send_mail(self.id)
        self.state = 'tc_complete'
        self.name.active = False

    @api.multi
    def come_to_ministry_approval(self):
        """
        --------------------------------
        :return:
        """
        self.state = 'tc_complete'

    @api.multi
    def tc_fee_pay_mannual_wizard(self):
        """

        :return:
        """
        view = self.env.ref('edsys_transfer_certificate.tc_fee_pay_manually_wizard')
        ctx = dict(self.env.context)
        return {
            'name': _('Manual Payment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tc.fee.pay.manually.wiz',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def send_fee_receipt_mail(self,voucher_rec):
        """
        ---------------------------
        :return:
        """
        email_server = self.env['ir.mail_server']
        email_sender = email_server.sudo().search([],limit=1)
        template_id = self.env['ir.model.data'].get_object_reference('edsys_transfer_certificate',
                                                                     'email_template_tc_fee_receipt_paid',)[1]
        template_rec = self.env['mail.template'].sudo().browse(template_id)
        template_rec.write({'email_to': voucher_rec.partner_id.parents1_id.parents_email,
                            'email_from': email_sender.smtp_user,
                            'email_cc': ''})
        template_rec.send_mail(voucher_rec.id, force_send=True)

    @api.model
    def _make_journal_search(self,ttype):
        """
        ---------------------------------
        :param ttype:
        :return:
        """
        journal_pool = self.env['account.journal']
        return journal_pool.search([('type', '=', ttype)])

    @api.model
    def _get_journal(self):
        """
        -------------------
        :return:
        """
        if self._context is None: self._context = {}
        invoice_pool = self.env['account.invoice']
        journal_pool = self.env['account.journal']
        if self._context.get('invoice_id', False):
            invoice = invoice_pool.browse(self._context['invoice_id'])
            journal_id = journal_pool.search([('currency', '=', invoice.currency_id.id),
                                            ('company_id', '=', invoice.company_id.id)],
                                             limit=1)
            return journal_id and journal_id[0] or False
        if self._context.get('journal_id', False):
            return self._context.get('journal_id')
        if not self._context.get('journal_id', False) and self._context.get('search_default_journal_id', False):
            return self._context.get('search_default_journal_id')

        ttype = self._context.get('type', 'bank')
        if ttype in ('payment', 'receipt'):
            ttype = 'bank'
        res = self._make_journal_search(ttype)
        return res and res[0] or False

    @api.model
    def _get_period(self):
        # print '=======================get period============'
        """
        ------------------
        :return:
        """
        if self._context is None: context = {}
        if self._context.get('period_id', False):
            return self._context.get('period_id')
        periods = self.env['account.period'].search([])
        return periods and periods[0] or False

    @api.model
    def _get_currency(self):
        if self._context is None: self._context = {}
        journal_pool = self.env['account.journal']
        journal_id = self._context.get('journal_id', False)
        if journal_id:
            if isinstance(journal_id, (list, tuple)):
                # sometimes journal_id is a pair (id, display_name)
                journal_id = journal_id[0]
            journal = journal_pool.browse(journal_id)
            if journal.currency:
                return journal.currency.id
        return self.env['res.users'].browse(self._uid).company_id.currency_id.id

    @api.one
    def confirm_tc_calculation(self):
        print '===============confirm_tc_calculation-------------'
        """
        ------------------------------------------------
        :return:
        """
        account_payment_obj = self.env['account.payment']
        account_voucher_obj = self.env['account.voucher']
        voucher_line_obj = self.env['account.voucher.line']
        date = time.strftime('%Y-%m-%d')
        for student_rec in self:
            # For Actual Paid Invoice
            #student_rec.calculate_total_due()
            for actual_paid_invoice_rec in self.actual_paid_invoice:
                if actual_paid_invoice_rec.state == 'paid':
                    account_invoice_refund_obj = self.env['account.invoice.refund']
                    journal_rec = self._get_journal()
                    account_invoice_refund_rec = account_invoice_refund_obj.create({
                            'filter_refund': 'refund',
                            'description': 'TC Fee Refund',
                            'journal_id': journal_rec.id,
                            'date': time.strftime('%Y-%m-%d')
                        })
                    refund_inv_rec = account_invoice_refund_rec.with_context({'invoice_rec':actual_paid_invoice_rec}).compute_refund(mode='refund')
                    refund_inv_rec.is_tc_refund = True
                    refund_inv_rec.action_invoice_open()
                    # print refund_inv_rec,'====================refund'
                elif actual_paid_invoice_rec.state == 'open':
#                     actual_paid_invoice_rec.signal_workflow('invoice_cancel')
                    actual_paid_invoice_rec.action_invoice_cancel()

            # For Actual Receivable Invoice
            if student_rec.credit == 0.00 and student_rec.parent_credit == 0.00:
                for actual_receivables_inv_rec in self.actual_receivables_invoice:
                    if actual_receivables_inv_rec.state == 'open':
                        if actual_receivables_inv_rec.residual > 0.00:
                            period_rec = self._get_period()
                            journal_rec = self._get_journal()
                            curency_id = self._get_currency()
#                             voucher_data = {
#                                 'period_id': period_rec.id,
#                                 'journal_id': journal_rec.id,
#                                 'account_id': journal_rec.default_debit_account_id.id,
#                                 'partner_id': student_rec.id,
#                                 'currency_id': curency_id,
#                                 'reference': student_rec.name,
#                                 'amount': 0.0,
#                                 'type': 'receipt' or 'payment',
#                                 'state': 'draft',
#                                 'name': '',
#                                 'date': time.strftime('%Y-%m-%d'),
#                                 'company_id': 1,
#                                 'tax_id': False,
#                                 'payment_option': 'without_writeoff',
#                                 'comment': _('Write-Off'),
#                                 'payfort_type': True,
#                                 }
#                             voucher_rec = account_voucher_obj.create(voucher_data)

                            payment_vals ={
                               'partner_type' : 'customer',
                               'partner_id' : actual_receivables_inv_rec.partner_id.id,
                               'journal_id' : journal_rec.id,
                               'account_id': journal_rec.default_debit_account_id.id,
                               'reference': student_rec.name,
                               'amount' : 0.0,
                               'payment_method_id' : 1,
                               'payment_type' : 'inbound',
                               }
                            payment_rec = account_payment_obj.create(payment_vals)
                            payment_rec.post()

#                             res = voucher_rec.onchange_partner_id(voucher_rec.partner_id.id, journal_rec.id,
#                                                                   float(actual_receivables_inv_rec.residual),
#                                                                    voucher_rec.currency_id.id,
#                                                                   voucher_rec.type, date)
#                             for line_data in res['value']['line_cr_ids']:
#                                 voucher_lines = {
#                                     'move_line_id': line_data['move_line_id'],
#                                     'amount': line_data['amount_original'] or line_data['amount'],
#                                     'name': line_data['name'],
#                                     'amount_unreconciled': line_data['amount_unreconciled'],
#                                     'type': line_data['type'],
#                                     'amount_original': line_data['amount_original'],
#                                     'account_id': line_data['account_id'],
#                                     'voucher_id': voucher_rec.id,
#                                     'reconcile': True
#                                 }
#                                 voucher_line_obj.sudo().create(voucher_lines)
# 
#                             for line_data in res['value']['line_dr_ids']:
#                                 voucher_lines = {
#                                     'move_line_id': line_data['move_line_id'],
#                                     'amount': line_data['amount_original'],
#                                     'name': line_data['name'],
#                                     'amount_unreconciled': line_data['amount_unreconciled'],
#                                     'type': line_data['type'],
#                                     'amount_original': line_data['amount_original'],
#                                     'account_id': line_data['account_id'],
#                                     'voucher_id': voucher_rec.id,
#                                 }
# 
#                                 voucher_line_obj.sudo().create(voucher_lines)
# 
#                             # Validate voucher (Add Journal Entries)
#                             voucher_rec.proforma_voucher()
            elif student_rec.credit < 0.00 or student_rec.parent_credit < 0.00:
                for actual_receivables_inv_rec in self.actual_receivables_invoice:
                    if actual_receivables_inv_rec.state == 'open':
                        if actual_receivables_inv_rec.residual > 0.00:
                            amount = actual_receivables_inv_rec.residual
                            journal_id = self._get_journal()
                            payment_vals ={
#                                'period_id': actual_receivables_inv_rec.period_id.id,
                               'partner_type' : 'customer',
                               'partner_id' : actual_receivables_inv_rec.partner_id.id,
                               'journal_id' : journal_id.id,
                               'account_id': journal_id.default_debit_account_id.id,
                               'reference': actual_receivables_inv_rec.name,
                               'amount' : amount,
                               'payment_method_id' : 1,
                               'payment_type' : 'inbound',
                               }
                            payment_rec = account_payment_obj.create(payment_vals)
                            payment_rec.post()

#                             voucher_rec = account_voucher_obj.create(voucher_data)
#                             date = time.strftime('%Y-%m-%d')
#                             if voucher_rec.id:
#                                 res = voucher_rec.onchange_partner_id(actual_receivables_inv_rec.partner_id.id, journal_id.id, actual_receivables_inv_rec.residual,
#                                                                       actual_receivables_inv_rec.currency_id.id,actual_receivables_inv_rec.type, date)
#                                 # Loop through each document and Pay only selected documents and create a single receipt
#                                 for line_data in res['value']['line_cr_ids']:
#                                     if not line_data['amount']:
#                                         continue
#                                     name = line_data['name']
# 
#                                     if line_data['name'] in [actual_receivables_inv_rec.number]:
#                                         if not line_data['amount']:
#                                             continue
#                                         voucher_lines = {
#                                             'move_line_id': line_data['move_line_id'],
#                                             'amount': amount,
#                                             'name': line_data['name'],
#                                             'amount_unreconciled': line_data['amount_unreconciled'],
#                                             'type': line_data['type'],
#                                             'amount_original': line_data['amount_original'],
#                                             'account_id': line_data['account_id'],
#                                             'voucher_id': voucher_rec.id,
#                                             'reconcile': True
#                                         }
#                                         voucher_line_obj.create(voucher_lines)
# 
#                                 for line_data in res['value']['line_dr_ids']:
#                                     if amount > 0:
#                                         set_amount = line_data['amount_original']
#                                         if amount <= set_amount:
#                                             set_amount = amount
#                                         reconcile = False
#                                         voucher_lines = {
#                                             'move_line_id': line_data['move_line_id'],
#                                             'name': line_data['name'],
#                                             'amount_unreconciled': line_data['amount_unreconciled'],
#                                             'type': line_data['type'],
#                                             'amount_original': line_data['amount_original'],
#                                             'account_id': line_data['account_id'],
#                                             'voucher_id': voucher_rec.id,
#                                         }
#                                     voucher_line_rec = voucher_line_obj.sudo().create(voucher_lines)
#                                     reconsile_vals = voucher_line_rec.onchange_amount(line_data['amount_original'],set_amount)
#                                     voucher_line_rec.reconcile = reconsile_vals['value']['reconcile']
#                                     if voucher_line_rec.reconcile:
#                                         amount_vals = voucher_line_rec.onchange_reconcile()
#                                         voucher_line_rec.amount = amount_vals['value']['amount']
#                                     else:
#                                         voucher_line_rec.amount = set_amount
#                                     # a = 10 / 0
#                                     amount -= set_amount
# 
#                                 # Add Journal Entries
#                                 voucher_rec.proforma_voucher()
# 
#                                 # Validate voucher (Add Journal Entries)
#                                 voucher_rec.proforma_voucher()
        self.state = 'final_fee_awaited'
        self.send_mail_payfort_payment_link()

    @api.model
    def create(self, vals):
        """
        This method use for generate unique code,
        -----------------------------------------
        :param vals:dictonary
        :return:
        """
        transfer_certificate_number = ''
        obj_ir_sequence = self.env['ir.sequence']
        ir_sequence_ids = obj_ir_sequence.sudo().search([('name','=','Transfer Certificate Number Sequence')])
        if ir_sequence_ids:
            transfer_certificate_number = obj_ir_sequence.next_by_code('trensfer.certificate')
        else:
            sequence_vals = {
                                'name' : 'Transfer Certificate Number Sequence',
                                'prefix' : 26,
                                'padding' : 7,
                                'number_next_actual' : 1,
                                'number_increment' : 1,
                                'implementation_standard' : 'standard',
                             }
            ir_sequence_ids = obj_ir_sequence.create(sequence_vals)
            transfer_certificate_number = obj_ir_sequence.next_by_code('trensfer.certificate')
#         dyanamic_registration_number = random.randrange(1000, 1000000, 1)
#         dyanamic_order_number = random.randrange(1000, 1000000, 1)
        vals['transfer_certificate_number'] = transfer_certificate_number
        
        vals['code'] = self.env['ir.sequence'].get('trensfer.certificate.form') or '/'
        res = super(TransferCertificate, self).create(vals)
        return res

    @api.multi
    def unlink(self):
        return super(TransferCertificate, self).unlink()

    @api.multi
    def come_to_cancle(self):
        """
        able to “Cancel TC application” at any stage before moving to Alumni
        --------------------------------------------------------------------
        :return:
        """
        if self.state == 'final_fee_awaited':
            for receivable_invoice in self.actual_receivables_invoice:
                if receivable_invoice.is_tc_invoice == True and receivable_invoice.state == 'open':
                    receivable_invoice.signal_workflow('invoice_cancel')
            for paid_invoice in self.actual_paid_invoice:
                paid_invoice.action_cancel_draft()
                paid_invoice.action_invoice_open()

        self.cancel_state, self.state = self.state, 'tc_cancel'

    @api.multi
    def back_from_cancel(self):
        """
        able to back from cancle state to current state,
        ------------------------------------------------
        :return:
        """
        if self.cancel_state == 'final_fee_awaited':
            for receivable_invoice in self.actual_receivables_invoice:
                if receivable_invoice.is_tc_invoice == True and receivable_invoice.state == 'cancel':
                    receivable_invoice.action_cancel_draft()
                    receivable_invoice.action_invoice_open()

            for paid_invoice in self.actual_paid_invoice:
                paid_invoice.signal_workflow('invoice_cancel')
        self.state = self.cancel_state

    @api.one
    def come_to_fee_balance_review(self):
        """
        This method use to change state from tc requested to
        fee balance review.
        -----------------------------------------------------
        :return:
        """
        if self.tc_form_filled != True:
            raise except_orm(_('Warning!'),
                    _("Please Fill TC Form !"))
        else:
            for tc_fee_structure in self.env['tc.fees.structure'].search([]):
                tc_fee_structure_line = tc_fee_structure.tc_fees_line_ids.search([
                                                                    ('tc_fees_structure_id', '=', tc_fee_structure.id),
                                                                    ('tc_type', '=', self.tc_type)])
                if len(tc_fee_structure_line) == 1:
                    self.tc_fee_stucture = [(4, tc_fee_structure_line.id)]
            self.state = 'fee_balance_review'

    @api.model
    def check_remaining_month_invoice(self, batch_id, month, year, student_rec):
        # print '==================check remianing month invoice==========='
        """
        -------------------------------------------------------------------------
        :param batch_id:
        :param month:
        :param year:
        :return:
        """
        fee_payment_obj = self.env['fee.payment']
        month_rec = batch_id.month_ids.search([('batch_id', '=', batch_id.id),
                                               ('name', '=', month),
                                               ('year', '=', year)], limit=1)
        if month_rec.id:
            fee_status = student_rec.payment_status.search([('student_id', '=', student_rec.id),
                                                            ('month_id', '=', month_rec.id)], limit=1)
            if len(fee_status) == 0:
                ctx = {'student_rec' : student_rec,'month_rec': month_rec}
                fee_payment_rec = fee_payment_obj.search([('month', '=', month_rec.id),
                                        ('academic_year_id', '=', student_rec.batch_id.id),
                                        ('course_id', '=', student_rec.course_id.id)], limit=1)
                if not fee_payment_rec.id:
                    fee_payment_detail = {}
                    name = str(student_rec.course_id.name) + '/' +\
                           str(month_rec.name)+ '/' + \
                           str(month_rec.year)+ '/' + ' Fee Calculation'
                    fee_payment_data = {
                        'name': name,
                        'code': name,
                        'course_id': student_rec.course_id.id,
                        'academic_year_id': student_rec.batch_id.id,
                        'month': month_rec.id,
                        'year': month_rec.year
                    }
                    fee_payment_rec = fee_payment_obj.create(fee_payment_data)
                if fee_payment_rec.id:
                    fee_payment_rec.with_context(ctx).generate_fee_payment()

    @api.multi
    def invoice_for_transfer_certificate_fee(self):
        # print '===============invoice_for_transfer_certificate_fee================'
        """
        -------------------------------------------
        :return:
        """
        invoice_obj = self.env['account.invoice']
        already_invoice_exist = invoice_obj.search([('partner_id', '=', self.name.id),('is_tc_invoice', '=', True)])
        if not already_invoice_exist.id:
            tc_fee_line_list = []
            for fee_line_rec in self.tc_fee_stucture:
                invoice_line_data = {
                    'product_id': fee_line_rec.name.id,
                    'account_id': fee_line_rec.name.property_account_income_id.id,
                    'name': fee_line_rec.name.name,
                    'quantity': 1,
                    'price_unit': fee_line_rec.amount,
                    'rem_amount': fee_line_rec.amount,
                    'parent_id': self.name.parents1_id.id,
                    'priority': fee_line_rec.sequence,
                    }
                tc_fee_line_list.append((0, 0, invoice_line_data))
            if len(tc_fee_line_list) > 0:
                invoice_vals={
                            'partner_id': self.name.id,
                            'account_id': self.name.property_account_receivable_id.id,
                            'invoice_line_ids': tc_fee_line_list,
                            'batch_id': self.name.batch_id.id,
                            'is_tc_invoice': True,
                            }
                invoice_rec = invoice_obj.create(invoice_vals)
                if invoice_rec.id:
#                     invoice_rec.signal_workflow('invoice_open')
                    invoice_rec.action_invoice_open()

    @api.one
    def calculate_total_due(self):
        # print'===================calculated total dueee==='
        """
        This method use to calculate total due base on last
        date of accounting.
        -----------------------------------------------------,
        :return:
        """

        if not self.last_date_for_accounting:
            raise except_orm(_('Warning!'),
                    _("Please Fill Last Date For Accounting !"))
        account_invoice_obj = self.env['account.invoice']
        last_date_for_accounting = datetime.strptime(self.last_date_for_accounting, "%Y-%m-%d")
        # remove noice for actual receivable
        for receivables_inv_rec in self.actual_receivables_invoice:
            self.actual_receivables_invoice = [(2, receivables_inv_rec.id)]

        # remove noice for actual payble
        for paid_invoice_rec in self.actual_paid_invoice:
            self.actual_paid_invoice = [(2,paid_invoice_rec.id)]

        # Last Date For Accounting is must be in between Academic start and End date
        batch_start_date = datetime.strptime(self.batch_id.start_date, "%Y-%m-%d")
        batch_end_date = datetime.strptime(self.batch_id.end_date, "%Y-%m-%d")
        if not batch_start_date <= last_date_for_accounting <= batch_end_date:
            raise except_orm(_('Warning!'),
                    _("Last Date For Accounting must be in between Academic Start Date and End date !"))

        # check and genarate invoice for remaining month if needed.
        self.check_remaining_month_invoice(batch_id = self.batch_id,
                                          month = last_date_for_accounting.month,
                                          year = last_date_for_accounting.year,
                                          student_rec = self.name)

        # create invoice for Transfer Certificate fee
        self.invoice_for_transfer_certificate_fee()

        # Already invoiced beyond his Last accounting date but unpaid – Fee de post to calculate balance.
        for receivables_invoice_rec in account_invoice_obj.search([('partner_id','=',self.name.id),
                                                                   ('state','=','open'),
                                                                   ('type','=','out_invoice')]):
            # print receivables_invoice_rec,'------------------------receivables_invoice_rec'
            invoice_date = datetime.strptime(receivables_invoice_rec.date_invoice,"%Y-%m-%d")
            if invoice_date <= last_date_for_accounting:
                self.actual_receivables_invoice = [(4,receivables_invoice_rec.id)]
            elif receivables_invoice_rec.is_tc_invoice:
                self.actual_receivables_invoice = [(4,receivables_invoice_rec.id)]

        for paid_invoice_rec in account_invoice_obj.search([('partner_id','=',self.name.id),
                                                            ('state','in',['open','paid']),
                                                            ('type','=','out_invoice')]):
            # print paid_invoice_rec,'=====================paid_invoice_rec'
            invoice_date = datetime.strptime(paid_invoice_rec.date_invoice,"%Y-%m-%d")
            if invoice_date > last_date_for_accounting:
                if paid_invoice_rec.is_tc_invoice == False:
                    self.actual_paid_invoice = [(4,paid_invoice_rec.id)]

        self.write({
            'cal_total_due' : True,
            # 'state' : 'final_fee_awaited',
            })
        self.name.write({'ministry_approved': False})
#         raise except_orm(_("Warning!"), _('stop'))

    @api.model
    def _get_payfort_payment_link(self,amount,order_id):
        """
        Get Payfort Detail from Payfort Master
        --------------------------------------
        :return:
        """
        active_payforts = self.env['payfort.config'].search([('active', '=', 'True')])

        if not active_payforts:
            raise except_orm(_('Warning!'),
                             _("Please create Payfort Details First!"))
        elif len(active_payforts) > 1:
            raise except_orm(_('Warning!'),
                             _("There should be only one payfort record!"))
            
        link = '/redirect/payment?AMOUNT=%s&ORDERID=%s'%(amount,order_id)
        return link

    @api.multi
    def send_mail_payfort_payment_link(self):
        # print'==========send mail payfort payment link============ tcc'
        """
        send mail to tc payfort payment link.
        -------------------------------------
        :return:
        """
        for tc_student_rec in self:
            # Payment Link For no balance
            tc_fee_amount = 0.00
            other_fee_amount = 0.00
            for tc_invoice_rec in tc_student_rec.actual_receivables_invoice:
                if tc_invoice_rec.is_tc_invoice and tc_invoice_rec.state == 'open':
                    tc_fee_amount += tc_invoice_rec.residual
            for other_invoice_rec in tc_student_rec.actual_receivables_invoice:
                if not other_invoice_rec.is_tc_invoice and other_invoice_rec.state == 'open':
                    other_fee_amount += other_invoice_rec.residual

            if tc_student_rec.credit == tc_fee_amount \
                    and tc_student_rec.parent_credit == 0.00\
                    and other_fee_amount == 0.00:
                link = tc_student_rec._get_payfort_payment_link(amount=tc_fee_amount, order_id=tc_student_rec.transfer_certificate_number)

                email_server = self.env['ir.mail_server']
                email_sender = email_server.search([], limit=1)
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('edsys_transfer_certificate', 'email_template_payment_link_no_balance_email')[1]
                template_rec = self.env['mail.template'].browse(template_id)
                body_html = template_rec.body_html
                body_dynamic_html = template_rec.body_html + '<p>TC Request Number : %s.</p>'%(tc_student_rec.code)
                body_dynamic_html += '<table border=1 width=100% align=center>'
                body_dynamic_html += '<tr><td><b>Name</b></td><td><b>Amount</b></td></tr><tr><td>Certificate Fee</td><td>%s</td></tr><tr><td>Out Standing Balance</td><td>%s</td></tr></table>'%(tc_fee_amount,other_fee_amount)
                body_dynamic_html += '<p>Total outstanding amount is AED %s</p>'%(tc_fee_amount)
                body_dynamic_html += '<p><a href=%s><button>Click here</button>to pay Certificate fee</a></p></div>'%(link)
                template_rec.write({'email_to': tc_student_rec.name.parents1_id.parents_email,
                                    'email_from': email_sender.smtp_user,
                                    'email_cc': '',
                                    'body_html': body_dynamic_html})
                template_rec.send_mail(self.id)
                template_rec.body_html = body_html
                return True

            # Payment Link For Outstanding Fees
            total_credit_amount = tc_student_rec.credit + tc_student_rec.parent_credit
            if total_credit_amount > 0.00 and tc_fee_amount > 0.00 and other_fee_amount > 0.00:

                link = tc_student_rec._get_payfort_payment_link(amount=total_credit_amount, order_id=tc_student_rec.transfer_certificate_number)

                email_server = self.env['ir.mail_server']
                email_sender = email_server.search([], limit=1)
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('edsys_transfer_certificate', 'email_template_payment_link_outstanding_fees')[1]
                template_rec = self.env['mail.template'].browse(template_id)
                body_html = template_rec.body_html
                body_dynamic_html = template_rec.body_html + '<p>TC Request Number : %s.</p>'%(tc_student_rec.code)
                body_dynamic_html += '<table border=1 width=100% align=center>'
                body_dynamic_html += '<tr><td><b>Name</b></td><td><b>Amount</b></td></tr><tr><td>Certificate Fee</td><td>%s</td></tr><tr><td>Out Standing Balance</td><td>%s</td></tr></table>'%(tc_fee_amount,other_fee_amount)
                body_dynamic_html += '<p>Please note you have an outstanding fee amount of %s pending.</p>'%(total_credit_amount)
                body_dynamic_html += '<p><a href=%s><button>Click here</button>to pay the Outstanding Fees (plus applicable online transaction charges)</a></p></div>'%(link)
                template_rec.write({'email_to': tc_student_rec.name.parents1_id.parents_email,
                                    'email_from': email_sender.smtp_user,
                                    'email_cc': '',
                                    'body_html': body_dynamic_html})
                template_rec.send_mail(self.id)
                template_rec.body_html = body_html
                return True

            # Advance Payment
            if total_credit_amount <= 0.00 or tc_fee_amount == 0.00:
                tc_fee = 0.00
                for tc_invoice_rec in tc_student_rec.actual_receivables_invoice:
                    if tc_invoice_rec.is_tc_invoice:
                        tc_fee += tc_invoice_rec.amount_total

                email_server = self.env['ir.mail_server']
                email_sender = email_server.search([], limit=1)
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('edsys_transfer_certificate', 'email_template_payment_link_refund')[1]
                template_rec = self.env['mail.template'].browse(template_id)
                body_html = template_rec.body_html
                body_dynamic_html = template_rec.body_html + '<p>TC Request Number : %s.</p>'%(tc_student_rec.code)
                body_dynamic_html += '<table border=1 width=100% align=center>'
                body_dynamic_html += '<tr><td><b>Name</b></td><td><b>Amount</b></td></tr><tr><td>Certificate Fee</td><td>%s</td></tr><tr><td>Current Advance</td><td>%s</td></tr></table>'%(tc_fee,abs(total_credit_amount))
                body_dynamic_html += '<p>You are entitled to receive a refund of AED %s</p>'%(abs(total_credit_amount))
                body_dynamic_html += '<p>Please contact the school accounts team to get this processed at the earliest</p></div>'
                template_rec.write({'email_to': tc_student_rec.name.parents1_id.parents_email,
                                    'email_from': email_sender.smtp_user,
                                    'email_cc': '',
                                    'body_html': body_dynamic_html})
                #template_rec.send_mail(self.id)
                template_rec.body_html = body_html
                return True

    @api.multi
    def send_mail_for_tc_form(self):
        # print '==============send mail for tc form============='
        """
        This method is used to send mail for tc Form,
        ---------------------------------------------
        :return:
        """
        tc_fee_structure_obj = self.env['tc.fees.structure']
        tc_fee_str_rec = tc_fee_structure_obj.search([])
        if len(tc_fee_str_rec) < 1:
            raise except_orm(_('Warning!'),
                _("Please Define Transfer Certificate Fee Structure !"))
        if len(tc_fee_str_rec) > 1:
            raise except_orm(_('Warning!'),
                _("More than One Record contain in Transfer Certificate Fee Structure !"))
        if len(tc_fee_str_rec) == 1:
            tc_fee_str_line_rec = tc_fee_str_rec.tc_fees_line_ids.search([('tc_fees_structure_id', '=', tc_fee_str_rec.id)])
            if len(tc_fee_str_line_rec) != 3:
                raise except_orm(_('Warning!'),
                _("Transfer Certificate Fee Structure Line Contain wrong Data !"))
            tc_fee_str_line_rec_uae = tc_fee_str_rec.tc_fees_line_ids.search([
                                                                ('tc_fees_structure_id', '=', tc_fee_str_rec.id),
                                                                ('tc_type', '=', 'within_uae')])
            if len(tc_fee_str_line_rec_uae) != 1:
                raise except_orm(_('Warning!'),
                _("Transfer Certificate Fee Structure Line Contain wrong Data !"))
            tc_fee_str_line_rec_dubai = tc_fee_str_rec.tc_fees_line_ids.search([
                                                                ('tc_fees_structure_id', '=', tc_fee_str_rec.id),
                                                                ('tc_type', '=', 'outside_uae')])
            if len(tc_fee_str_line_rec_dubai) != 1:
                raise except_orm(_('Warning!'),
                _("Transfer Certificate Fee Structure Line Contain wrong Data !"))

            tc_fee_str_line_rec_within_dubai = tc_fee_str_rec.tc_fees_line_ids.search([
                                                                ('tc_fees_structure_id', '=', tc_fee_str_rec.id),
                                                                ('tc_type', '=', 'within_dubai')])
            if len(tc_fee_str_line_rec_within_dubai) != 1:
                raise except_orm(_('Warning!'),
                _("Transfer Certificate Fee Structure Line Contain wrong Data !"))

        for tc_student_rec in self:
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            encoded_data = base64.b64encode(tc_student_rec.code)
            c_link = base_url + '/student/tc/request?TCCODE=%s'%(encoded_data)
            tc_student_rec.write({
                    'tc_form_fill_link': c_link,
                    'last_date_of_tc_request_form': datetime.now(),
                })
            email_server = self.env['ir.mail_server']
            email_sender = email_server.search([])
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('edsys_transfer_certificate', 'email_template_tc_form_email')[1]
            template_rec = self.env['mail.template'].browse(template_id)
            template_rec.write({'email_to': self.name.parents1_id.parents_email,
                                'email_from': email_sender.smtp_user,
                                'email_cc': '',})
            template_rec.send_mail(self.id)

class AccountInvoiceInherit(models.Model):

    _inherit = 'account.invoice'

    is_tc_invoice = fields.Boolean("Is TC Invoice")
    is_tc_refund = fields.Boolean("Is TC Refund Invoice")
    
    period_id = fields.Many2one('account.period','Force Period')

class AccountInvoiceRefundInherit(models.TransientModel):

    _inherit = 'account.invoice.refund'
    
#     journal_id = fields.May2one('account.journal','Refund Journal') 
    journal_id = fields.Many2one('account.journal', 'Refund Journal', help='You can select here the journal to use for the credit note that will be created. If you leave that field empty, it will use the same journal as the current invoice.')
    period = fields.Many2one('account.period','Force Period')

    @api.multi
    def compute_refund(self, mode='refund'):
        # print self,'===========================self'
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account invoice refund’s ID or list of IDs
        -----------------------------------------------------------
        :param mode:
        :return:
        """

        if 'invoice_rec' in self._context and self._context['invoice_rec']:
            inv_obj = self.env['account.invoice']
            reconcile_obj = self.env['account.move.reconcile']
            account_m_line_obj = self.env['account.move.line']
            mod_obj = self.env['ir.model.data']
            act_obj = self.env['ir.actions.act_window']
            inv_tax_obj = self.env['account.invoice.tax']
            inv_line_obj = self.env['account.invoice.line']
            res_users_obj = self.env['res.users']

            for form in self:
                print '=============================form',form,self._context['invoice_rec']
                date = False
                period = False
                description = False
                company = res_users_obj.browse(self._uid).company_id
                journal_id = form.journal_id.id
                for inv in self._context['invoice_rec']:
                    if inv.state in ['draft', 'proforma2', 'cancel']:
                        raise except_orm(_('Error!'), _('Cannot %s draft/proforma/cancel invoice.') % (mode))
                    if inv.reconciled and mode in ('cancel', 'modify'):
                        raise except_orm(_('Error!'), _('Cannot %s invoice which is already reconciled, invoice should be unreconciled first. You can only refund this invoice.') % (mode))
                    if form.period.id:
                        period = form.period.id
                    else:
                        period = inv.period_id and inv.period_id.id or False

                    if not journal_id:
                        journal_id = inv.journal_id.id

                    if form.date:
                        date = form.date
                        if not form.period.id:
                                self._cr.execute("select name from ir_model_fields \
                                                where model = 'account.period' \
                                                and name = 'company_id'")
                                result_query = self._cr.fetchone()
                                if result_query:
                                    self._cr.execute("""select p.id from account_fiscalyear y, account_period p where y.id=p.fiscalyear_id \
                                        and date(%s) between p.date_start AND p.date_stop and y.company_id = %s limit 1""", (date, company.id,))
                                else:
                                    self._cr.execute("""SELECT id
                                            from account_period where date(%s)
                                            between date_start AND  date_stop  \
                                            limit 1 """, (date,))
                                res = self._cr.fetchone()
                                if res:
                                    period = res[0]
                    else:
                        date = inv.date_invoice
                    if form.description:
                        description = form.description
                    else:
                        description = inv.name

                    if not period:
                        raise except_orm(_('Insufficient Data!'),
                                                _('No period found on the invoice.'))
                    period_id = self.env['account.period'].browse([period])
                    refund_inv = inv.refund(date, period_id.date_stop, description, journal_id)
                    refund_inv.write({'date_due': date})
                                # 'check_total': inv.check_total})
                    # refund_inv.button_compute()
                return refund_inv
        else:
            res = super(AccountInvoiceRefundInherit,self).compute_refund(mode='refund')
            return res

class ReRegistrationResponceStudentInherit(models.Model):

    _inherit = 're.reg.waiting.responce.student'

    tc_form_send = fields.Boolean('Tc Form Send')

    @api.multi
    def re_reg_send__tc_form_request(self):
        """
        -----------------------------------
        :return:
        """
        tc_obj = self.env['trensfer.certificate']
        tc_ex_rec = tc_obj.search([('name','=',self.name.id)])
        if tc_ex_rec.id:
            raise except_orm(_('Warning!'),
                    _("The TC process has already been initiated for %s !") % self.name.name)
        tc_data = {
            'name': self.name.id,
            'reg_no': self.reg_no,
            'batch_id': self.batch_id.id,
            'course_id': self.course_id.id,
            'state': 'tc_requested'
        }
        tc_rec = tc_obj.create(tc_data)
        self.tc_form_send = True
        tc_rec.send_mail_for_tc_form()

class FeePaymentInherit(models.Model):

    _inherit = 'fee.payment'

    @api.model
    def first_day_of_month(self,month,year):
        """
        getting first date of month
        -----------------------------------
        :param month:
        :param year:
        :return: first date of invoice
        """
        return date(year, month, 1)

    @api.model
    def send_payforts_link(self, student_total_receivable,parent_total_receivable,student_rec, invoice_rec):
        """
        During TC fee calculation time payment link not send sepretaly,
        ---------------------------------------------------------------
        :param student_rec: record set of student
        :param invoice_rec: record set student invoice
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
        else:
            res = super(FeePaymentInherit, self).send_payforts_link(student_total_receivable,parent_total_receivable,student_rec, invoice_rec)
            return res

    @api.multi
    def generate_fee_payment_old_8july2016(self):
        """
        ---------------------------
        :return:
        """
        if 'month_rec' in self._context and 'student_rec' in self._context:
            context = self._context
            student_record = context['student_rec']
            main_month_diff = self.academic_year_id.month_ids.search_count([('batch_id', '=', self.academic_year_id.id),
                                                                   ('leave_month', '=', False)])
            leave_month = []
            for l_month in self.academic_year_id.month_ids.search([('batch_id', '=', self.academic_year_id.id),
                                                                   ('leave_month', '=', True)]):
                leave_month.append((int(l_month.name), int(l_month.year)))
            invoice_obj = self.env['account.invoice']
            student_obj = self.env['res.partner']
            month_year_obj = self.month
            if self.month.leave_month == True:
                # get worning if try to calculate fee for leave month
                raise except_orm(_("Warning!"), _("You can not calculate Fee for Leave month.\n Please Select other month."))

            self.fields_readonly=True
            parents_list = []
            parents_advance_change = []
            if month_year_obj.id:
                for stud_id in student_record:
                    month_diff = main_month_diff
                    joining_date = datetime.strptime(stud_id.admission_date, "%Y-%m-%d").date()
                    start_date = datetime.strptime(self.academic_year_id.start_date, "%Y-%m-%d").date()
                    end_date = datetime.strptime(self.academic_year_id.end_date, "%Y-%m-%d").date()
                    get_unpaid_diff = self.get_person_age(start_date, joining_date)
                    month_in_stj = self.months_between(start_date, joining_date)
                    student_total_receivable = stud_id.credit
                    parent_total_receivable = 0.00
                    if stud_id.parents1_id.id:
                        parent_total_receivable = stud_id.parents1_id.credit
                        for parent_advance_dict in parents_advance_change:
                            if stud_id.parents1_id.id in parent_advance_dict:
                                parent_total_receivable = parent_advance_dict[stud_id.parents1_id.id]

                    unpaid_month = 0
                    if get_unpaid_diff.get('months') > 0:
                        unpaid_month = get_unpaid_diff.get('months')
                        if len(month_in_stj) > 0 and len(leave_month) > 0:
                            for leave_month_year in leave_month:
                                if leave_month_year in month_in_stj:
                                    unpaid_month -= 1

                    month_diff -= unpaid_month
                    month_in_joining_end = self.months_between(joining_date, end_date)
                    months = self.striked_off_months(stud_id, self.academic_year_id, month_year_obj, month_in_joining_end)
                    for month in months:
                        fee_month_amount = 0.00
                        total_discount = 0.00
                        fee_line_lst = []
                        invoice_dic = {}
                        for fee_amount in stud_id.student_fee_line:
                            per_month_year_fee = 0.0
                            dis_amount = 0.00
                            if fee_amount.fee_pay_type.name == 'year':
                                exist_month = stud_id.payment_status.search_count([('student_id', '=', stud_id.id),('month_id.batch_id','=',self.academic_year_id.id)])
                                if exist_month == 0:
                                    all_amount = stud_id.student_fee_line.search([('name', '=', fee_amount.name.id),
                                                                                  ('stud_id', '=', stud_id.id)], limit=1)
                                    per_month_year_fee = all_amount.amount
                                    if fee_amount.discount > 0:
                                        dis_amount = (per_month_year_fee * fee_amount.discount)/100
                                    fee_line_lst.append((0, 0,
                                        {
                                            'product_id': fee_amount.name.id,
                                            'account_id': fee_amount.name.property_account_income_id.id,
                                            'name': fee_amount.name.name,
                                            'quantity': 1,
                                            'price_unit': round(per_month_year_fee, 2),
                                            'parent_id': stud_id.parents1_id.id,
                                            'rem_amount': round(per_month_year_fee, 2),
                                            'priority': fee_amount.sequence,
                                        }))
                                    # student fee detail update
                                    exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                          ('student_id', '=', stud_id.id)], limit=1)
                                    if exist_qtr_pay_detail.id:
                                        # if exist_qtr_pay_detail.month_id.id != month.id:
                                            exist_qtr_pay_detail.write({'cal_amount': per_month_year_fee,
                                                                        'discount_amount': dis_amount,
                                                                        'month_id': month.id})
                                    else:
                                        fee_year_pay_value = {
                                                    'name': fee_amount.name.id,
                                                    'student_id': stud_id.id,
                                                    'month_id': month.id,
                                                    'fee_pay_type': fee_amount.fee_pay_type,
                                                    'cal_amount': per_month_year_fee,
                                                    'total_amount': fee_amount.amount,
                                                    'discount_amount': dis_amount,
                                                }
                                        stud_id.payble_fee_ids = [(0, 0, fee_year_pay_value)]

                                fee_month_amount += per_month_year_fee

                            elif fee_amount.fee_pay_type.name == 'quater':
                                if month.qtr_month == True:
                                    all_amount = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                ('student_id', '=', stud_id.id)], limit=1, order="id desc")
                                    per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
                                    count_month = 0
                                    for total_month_id in self.academic_year_id.month_ids.search([('qtr_month', '=', True),
                                                                                                  ('batch_id', '=', self.academic_year_id.id),
                                                                                                  ('leave_month', '=', False)]):
                                        exist_month = stud_id.payment_status.search([('month_id', '=', total_month_id.id),
                                                                                     ('student_id', '=', stud_id.id)])
                                        if exist_month.id:
                                            count_month += 1

                                    if count_month != 0:
                                        new_per_month_qtr_fee = per_month_qtr_fee * count_month
                                        if all_amount.cal_amount <= new_per_month_qtr_fee:
                                            cal_alt_new = new_per_month_qtr_fee - all_amount.cal_amount
                                            if cal_alt_new > 0:
                                                per_month_qtr_fee = per_month_qtr_fee + cal_alt_new
                                            else:
                                                per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
                                    else:
                                        per_month_qtr_fee = all_amount.total_amount/(month_diff/3)

                                    fee_month_amount += per_month_qtr_fee

                                    # discount calculation for quater month
                                    fee_paid_line = stud_id.payment_status.search_count([('month_id', '=', total_month_id.id),
                                                                                     ('student_id', '=', stud_id.id)])
                                    if fee_amount.discount > 0:
                                        if fee_paid_line > 0:
                                            if amount_above.discount_amount > 0.0:
                                                alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                                current_month_disamount = (per_month_qtr_fee * fee_amount.discount)/100
                                                if alredy_permonth_discount == current_month_disamount:
                                                    dis_amount = current_month_disamount
                                                elif alredy_permonth_discount < current_month_disamount:
                                                    difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                                    difference_discount = difference_discount_per_month * fee_paid_line
                                                    dis_amount = current_month_disamount + difference_discount
                                                elif alredy_permonth_discount > current_month_disamount:
                                                    difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                                    difference_discount = difference_discount_per_month * fee_paid_line
                                                    dis_amount = current_month_disamount - difference_discount
                                            else:
                                                dis_amount_quater = (per_month_qtr_fee * fee_amount.discount)/100
                                                dis_amount = dis_amount_quater + (dis_amount_quater * fee_paid_line)
                                        else:
                                            dis_amount = (per_month_qtr_fee * fee_amount.discount)/100
                                    total_discount += dis_amount

                                    fee_line_lst.append((0, 0,
                                            {
                                                'product_id': fee_amount.name.id,
                                                'account_id': fee_amount.name.property_account_income_id.id,
                                                'name': fee_amount.name.name,
                                                'quantity': 1,
                                                'price_unit': round(per_month_qtr_fee,2),
                                                'parent_id': stud_id.parents1_id.id,
                                                'rem_amount': round(per_month_qtr_fee,2),
                                                'priority': fee_amount.sequence,
                                            }))
                                    # student fee detail update
                                    exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                          ('student_id','=',stud_id.id)], limit=1)
                                    if exist_qtr_pay_detail.id:
                                        # if exist_qtr_pay_detail.month_id.id != month.id:
                                            exist_qtr_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                                        'discount_amount' : all_amount.discount_amount + dis_amount,
                                                                        'month_id': month.id,})
                                    else:
                                        fee_qtr_pay_value =\
                                                {
                                                    'name': fee_amount.name.id,
                                                    'student_id': stud_id.id,
                                                    'month_id': month.id,
                                                    'fee_pay_type': fee_amount.fee_pay_type,
                                                    'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                    'total_amount' : fee_amount.amount,
                                                    'discount_amount' : all_amount.discount_amount + dis_amount
                                                }
                                        stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]

                            if fee_amount.fee_pay_type.name == 'half_year':
                                if month.quater_month == True:
                                    all_amount = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                ('student_id', '=', stud_id.id)], limit=1, order="id desc")
                                    per_month_qtr_fee = all_amount.total_amount/2
                                    count_month = 0
                                    for total_month_id in self.academic_year_id.month_ids.search([('quater_month', '=', True),
                                                                                                  ('batch_id', '=', self.academic_year_id.id),
                                                                                                  ('leave_month', '=', False)]):
                                        exist_month = stud_id.payment_status.search([('month_id', '=', total_month_id.id),
                                                                                     ('student_id', '=', stud_id.id)])
                                        if exist_month.id:
                                            count_month += 1
                                    if count_month != 0:
                                        new_per_month_qtr_fee = per_month_qtr_fee * count_month

                                        if all_amount.cal_amount <= new_per_month_qtr_fee:
                                            cal_alt_new = new_per_month_qtr_fee - all_amount.cal_amount
                                            if cal_alt_new > 0:
                                                per_month_qtr_fee = per_month_qtr_fee + cal_alt_new
                                            else:
                                                per_month_qtr_fee = all_amount.total_amount/2
                                    else:
                                        per_month_qtr_fee = all_amount.total_amount/2

                                    fee_month_amount += per_month_qtr_fee

                                    #discount calculation for half year
                                    fee_paid_line = stud_id.payment_status.search_count([('month_id', '=', total_month_id.id),
                                                                                     ('student_id', '=', stud_id.id)])
                                    if fee_amount.discount > 0:
                                        if fee_paid_line > 0:
                                            if amount_above.discount_amount > 0.0:
                                                alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                                current_month_disamount = (per_month_qtr_fee * fee_amount.discount)/100
                                                if alredy_permonth_discount == current_month_disamount:
                                                    dis_amount = current_month_disamount
                                                elif alredy_permonth_discount < current_month_disamount:
                                                    difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                                    difference_discount = difference_discount_per_month * fee_paid_line
                                                    dis_amount = current_month_disamount + difference_discount
                                                elif alredy_permonth_discount > current_month_disamount:
                                                    difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                                    difference_discount = difference_discount_per_month * fee_paid_line
                                                    dis_amount = current_month_disamount - difference_discount
                                            else:
                                                dis_amount_half_month = (per_month_qtr_fee * fee_amount.discount)/100
                                                dis_amount = dis_amount_half_month + (dis_amount_half_month * fee_paid_line)
                                        else:
                                            dis_amount = (per_month_qtr_fee * fee_amount.discount)/100

                                    total_discount += dis_amount

                                    fee_line_lst.append((0, 0,
                                            {
                                                'product_id': fee_amount.name.id,
                                                'account_id': fee_amount.name.property_account_income_id.id,
                                                'name': fee_amount.name.name,
                                                'quantity': 1,
                                                'parent_id': stud_id.parents1_id.id,
                                                'price_unit': round(per_month_qtr_fee, 2),
                                                'rem_amount': round(per_month_qtr_fee, 2),
                                                'priority': fee_amount.sequence,
                                            }))
                                    # Student fee detail update
                                    exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                          ('student_id', '=', stud_id.id)], limit=1)
                                    if exist_qtr_pay_detail.id:
                                        # if exist_qtr_pay_detail.month_id.id != month.id:
                                            exist_qtr_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                                        'discount_amount': all_amount.discount_amount + dis_amount,
                                                                        'month_id': month.id,})
                                    else:
                                        fee_qtr_pay_value =\
                                                {
                                                    'name': fee_amount.name.id,
                                                    'student_id': stud_id.id,
                                                    'month_id': month.id,
                                                    'fee_pay_type': fee_amount.fee_pay_type,
                                                    'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                    'total_amount': fee_amount.amount,
                                                    'discount_amount': all_amount.discount_amount + dis_amount
                                                }

                                        stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]

                            elif fee_amount.fee_pay_type.name == 'alt_month':
                                if month.alt_month == True:
                                    all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                ('student_id','=',stud_id.id)], limit=1, order="id desc")
                                    per_month_alt_fee = all_amount.total_amount/(month_diff/2)
                                    count_month = 0
                                    for total_month_id in self.academic_year_id.month_ids.search([('alt_month', '=', True),
                                                                                                  ('batch_id', '=', self.academic_year_id.id),
                                                                                                  ('leave_month', '=', False)]):
                                        exist_month = stud_id.payment_status.search([('month_id', '=', total_month_id.id),
                                                                                     ('student_id', '=', stud_id.id)])
                                        if exist_month.id:
                                            count_month += 1
                                    if count_month != 0:
                                        new_per_month_alt_fee = per_month_alt_fee * count_month
                                        if all_amount.cal_amount <= new_per_month_alt_fee:
                                            cal_alt_new = new_per_month_alt_fee - all_amount.cal_amount
                                            if cal_alt_new > 0:
                                                per_month_alt_fee = per_month_alt_fee + cal_alt_new
                                            else:
                                                per_month_alt_fee = all_amount.total_amount/(month_diff/2)
                                    else:
                                        per_month_alt_fee = all_amount.total_amount/(month_diff/2)

                                    fee_month_amount += per_month_alt_fee

                                    # discount calculation for alt month
                                    fee_paid_line = stud_id.payment_status.search_count([('month_id', '=', total_month_id.id),
                                                                                     ('student_id', '=', stud_id.id)])
                                    if fee_amount.discount > 0:
                                        if fee_paid_line > 0:
                                            if amount_above.discount_amount > 0.0:
                                                alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                                current_month_disamount = (per_month_alt_fee * fee_amount.discount)/100
                                                if alredy_permonth_discount == current_month_disamount:
                                                    dis_amount = current_month_disamount
                                                elif alredy_permonth_discount < current_month_disamount:
                                                    difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                                    difference_discount = difference_discount_per_month * fee_paid_line
                                                    dis_amount = current_month_disamount + difference_discount
                                                elif alredy_permonth_discount > current_month_disamount:
                                                    difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                                    difference_discount = difference_discount_per_month * fee_paid_line
                                                    dis_amount = current_month_disamount - difference_discount
                                            else:
                                                dis_amount_alt_month = (per_month_alt_fee * fee_amount.discount)/100
                                                dis_amount = dis_amount_alt_month + (dis_amount_alt_month * fee_paid_line)
                                        else:
                                            dis_amount = (per_month_alt_fee * fee_amount.discount)/100

                                    total_discount += dis_amount

                                    fee_line_lst.append((0,0,
                                            {
                                                'product_id' : fee_amount.name.id,
                                                'account_id' : fee_amount.name.property_account_income_id.id,
                                                'name' : fee_amount.name.name,
                                                'quantity' : 1,
                                                'price_unit' : round(per_month_alt_fee,2),
                                                'parent_id' : stud_id.parents1_id.id,
                                                'rem_amount' : round(per_month_alt_fee,2),
                                                'priority' : fee_amount.sequence,
                                            }))
                                    # student fee detail update
                                    exist_alt_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                          ('student_id', '=', stud_id.id)], limit=1)
                                    if exist_alt_pay_detail.id:
                                        # if exist_alt_pay_detail.month_id.id != month.id:
                                            exist_alt_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_alt_fee,
                                                                        'discount_amount': all_amount.discount_amount + dis_amount,
                                                                        'month_id': month.id,})
                                    else:
                                        fee_alt_pay_value =\
                                                {
                                                    'name': fee_amount.name.id,
                                                    'student_id': stud_id.id,
                                                    'month_id': month.id,
                                                    'fee_pay_type': fee_amount.fee_pay_type,
                                                    'cal_amount': all_amount.cal_amount + round(per_month_alt_fee, 2),
                                                    'total_amount': fee_amount.amount,
                                                    'discount_amount': all_amount.discount_amount + dis_amount
                                                }
                                        stud_id.payble_fee_ids = [(0, 0, fee_alt_pay_value)]

                            elif fee_amount.fee_pay_type.name == 'month':
                                amount_above = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                              ('student_id', '=', stud_id.id)], limit=1)
                                # per month fee calculation
                                per_month_fee = amount_above.total_amount/(month_diff)
                                # already fee paided month
                                fee_paid_line = stud_id.payment_status.search_count([('student_id', '=', stud_id.id),
                                                                                     ('month_id.batch_id','=',self.academic_year_id.id)])
                                if fee_paid_line > 0:
                                    new_rem_amount = per_month_fee * fee_paid_line
                                    if amount_above.cal_amount <= new_rem_amount:
                                        cal_new = new_rem_amount - amount_above.cal_amount
                                        if cal_new > 0:
                                            per_month_fee = cal_new + per_month_fee
                                        else:
                                            per_month_fee = amount_above.total_amount/(month_diff)
                                else:
                                    per_month_fee = amount_above.total_amount/(month_diff)
                                fee_month_amount += per_month_fee
                                # discount calculation for per month
                                if fee_amount.discount > 0:
                                    if fee_paid_line > 0:
                                        if amount_above.discount_amount > 0.0:
                                            alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                            current_month_disamount = (per_month_fee * fee_amount.discount)/100
                                            if alredy_permonth_discount == current_month_disamount:
                                                dis_amount = current_month_disamount
                                            elif alredy_permonth_discount < current_month_disamount:
                                                difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                                difference_discount = difference_discount_per_month * fee_paid_line
                                                dis_amount = current_month_disamount + difference_discount
                                            elif alredy_permonth_discount > current_month_disamount:
                                                difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                                difference_discount = difference_discount_per_month * fee_paid_line
                                                dis_amount = current_month_disamount - difference_discount
                                        else:
                                            dis_amount_month = (per_month_fee * fee_amount.discount)/100
                                            dis_amount = dis_amount_month + (dis_amount_month * fee_paid_line)
                                    else:
                                        dis_amount = (per_month_fee * fee_amount.discount)/100
                                total_discount += dis_amount
                                fee_line_lst.append((0, 0,
                                    {
                                        'product_id': fee_amount.name.id,
                                        'account_id': fee_amount.name.property_account_income_id.id,
                                        'name': fee_amount.name.name,
                                        'quantity': 1,
                                        'price_unit': round(per_month_fee,2),
                                        'parent_id': stud_id.parents1_id.id,
                                        'rem_amount': round(per_month_fee,2),
                                        'priority': fee_amount.sequence,
                                    }))
                                # Student Fee Detail Update
                                exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                       ('student_id', '=', stud_id.id)], limit=1)
                                if exist_stud_pay_detail.id:
                                    # if exist_stud_pay_detail.month_id.id != month.id:
                                        exist_stud_pay_detail.write({'cal_amount': amount_above.cal_amount + per_month_fee,
                                                                     'discount_amount': amount_above.discount_amount + dis_amount,
                                                                     'month_id': month.id})
                                else:
                                    fee_pay_value =\
                                        {
                                            'name': fee_amount.name.id,
                                            'student_id': stud_id.id,
                                            'month_id': month.id,
                                            'fee_pay_type': fee_amount.fee_pay_type,
                                            'cal_amount': amount_above.cal_amount + per_month_fee,
                                            'total_amount': fee_amount.amount,
                                            'discount_amount': amount_above.discount_amount + dis_amount
                                        }

                                    stud_id.payble_fee_ids = [(0, 0, fee_pay_value)]

                            # Term wise Fee Calculation
                            elif fee_amount.fee_pay_type.name == 'term':
                                paid_term_obj = self.env['paid.term.history']
                                terms=self.env['acd.term'].search([('batch_id','=',self.academic_year_id.id)])
                                amount_above = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                              ('student_id','=',stud_id.id)])
                                current_term=amount_above.next_term
                                exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                       ('student_id','=',stud_id.id)])

                                per_month_fee=0
                                term_id=False
                                prev_term_seq=exist_stud_pay_detail.next_term.id

                                if prev_term_seq:
                                    same_seq_terms=self.env['acd.term'].search([('id','>',prev_term_seq)])

                                next_term=exist_stud_pay_detail.next_term.id
                                invoice_dic={}
                                if current_term.id:
                                    start_date = datetime.strptime(current_term.start_date, "%Y-%m-%d")
                                    end_date = datetime.strptime(current_term.end_date, "%Y-%m-%d")
                                    if start_date.month == month.name:
                                        if int(start_date.year) == int(month.year):
                                            term_month = self.months_between(start_date,end_date)
                                            per_month_fee = (fee_amount.amount / month_diff) * len(term_month)
                                            term_id=amount_above.next_term.id
                                            prev_paid_rec=paid_term_obj.search([('student_id','=',stud_id.id),('term_id','=',term_id),('batch_id','=',self.academic_year_id.id)])
                                            if not prev_paid_rec:
                                                paid_term_obj.create({'student_id':stud_id.id,'term_id':term_id,'batch_id':self.academic_year_id.id})
                                            if same_seq_terms.ids:
                                                list=[]
                                                for each in same_seq_terms:
                                                    if each in terms:
                                                        list.append(each.id)
    #                                                    next_term=each.id

                                                if list:
                                                    list=sorted(list)
                                                    next_term=list[0]
                                        else:
                                            per_month_fee=0
                                            term_id=False
                                # discount calculation
                                if fee_amount.discount > 0:
                                    pre_dis = 0.00
                                    if amount_above.cal_amount > 0.00:
                                        pre_dis = (amount_above.cal_amount * fee_amount.discount) / 100
                                        if pre_dis != amount_above.discount_amount:
                                            if pre_dis < amount_above.discount_amount:
                                                pre_dis = pre_dis - amount_above.discount_amount
                                            else:
                                                pre_dis = pre_dis - amount_above.discount_amount
                                    dis_amount = (per_month_fee * fee_amount.discount) / 100
                                    dis_amount + pre_dis

                                total_discount += dis_amount
                                fee_month_amount += per_month_fee

                                fee_line_lst.append((0,0,
                                        {
                                            'product_id' : fee_amount.name.id,
                                            'account_id' : fee_amount.name.property_account_income_id.id,
                                            'name' : fee_amount.name.name,
                                            'quantity' : 1.00,
                                            'price_unit' : round(per_month_fee,2),
                                            'rem_amount' : round(per_month_fee,2),
                                            'parent_id' : stud_id.parents1_id.id,
                                            'priority' : fee_amount.sequence,
                                        }))

                                fee_pay_value =\
                                            {
                                                'name': fee_amount.name.id,
                                                'student_id': stud_id.id,
                                                'month_id': month.id,
                                                'fee_pay_type': fee_amount.fee_pay_type.name,
                                                'cal_amount': amount_above.cal_amount + per_month_fee,
                                                'total_amount' : fee_amount.amount,
                                                'next_term':next_term,
                                                'discount_amount' : amount_above.discount_amount + dis_amount,
                                            }
                                invoice_dic.update({'term_id':term_id or "",})
                                if not exist_stud_pay_detail.id:
                                    stud_id.payble_fee_ids = [(0, 0, fee_pay_value)]
                                else:
                                    for val in exist_stud_pay_detail:
                                        val.cal_amount=amount_above.cal_amount + per_month_fee
                                        val.next_term=next_term
                                        val.discount_amount = amount_above.discount_amount + dis_amount

                            if fee_amount.discount > 0.00 and dis_amount != 0.00:
                                if not fee_amount.name.fees_discount:
                                    raise except_orm(_("Warning!"), _('Please define Discount Fee For %s.')%(fee_amount.name.name))
                                else:
                                    if not fee_amount.name.fees_discount.property_account_income_id.id:
                                        raise except_orm(_("Warning!"), _('Please define account Income for %s.')%(fee_amount.name.fees_discount.name))
                                    else:
                                        fee_line_lst.append((0,0,{
                                            'product_id' : fee_amount.name.fees_discount.id,
                                            'account_id' : fee_amount.name.fees_discount.property_account_income_id.id,
                                            'name' : fee_amount.name.fees_discount.name,
                                            'quantity' : 1.00,
                                            'parent_id' : stud_id.parents1_id.id,
                                            'price_unit' : -round(dis_amount,2),
                                            'rem_amount' : -round(dis_amount,2),
                                            'priority' : 0,
                                            }))

                        # Monthaly Fee Pyment Generate Line
                        exist_fee_line = self.fee_payment_line_ids.search([('student_id','=',stud_id.id),
                                                                            ('month_id','=',self.month.id),
                                                                            ('year','=',self.year),
                                                                            ('fee_payment_id','=',self.id)])
                        if not exist_fee_line.id:
                            self.fee_payment_line_ids.create({
                                'student_id': stud_id.id,
                                'total_fee': fee_month_amount-total_discount,
                                'month_id': month.id,
                                'month': month.name,
                                'year': month.year,
                                'fee_payment_id' : self.id,
                                })
                        # else:
                        #     exist_fee_line.write({
                        #         'total_fee': fee_month_amount-total_discount,
                        #     })

                        # Invoice Create
                        exist_invoice = invoice_obj.search_count([('partner_id','=',stud_id.id),('month_id','=',month.id)])
                        if exist_invoice == 0 and len(fee_line_lst) > 0:
                            invoice_date = self.first_day_of_month(int(month.name), int(month.year))
                            invoice_vals = {
                                'partner_id' : stud_id.id,
                                'month_id' : month.id,
                                'account_id' : stud_id.property_account_receivable.id,
                                'invoice_line_ids' : fee_line_lst,
                                'month' : month.name,
                                'year' : month.year,
                                'batch_id' : self.academic_year_id.id,
                                'date_invoice' : invoice_date,
                            }
                            invoice_id = invoice_obj.create(invoice_vals)

                            if invoice_dic:
                                invoice_id.write(invoice_dic)

                            # Invoice validate
                            invoice_id.action_invoice_open()
                            # invoice_id.action_date_assign()
                            # invoice_id.action_move_create()
                            # invoice_id.action_number()
                            # invoice_id.invoice_validate()

                            # send payfort link for online fee payment
                            if invoice_id.id:
                                parent_rem_advance = self.with_context({'send_mail':False}).send_payforts_link(student_total_receivable=student_total_receivable,
                                                        parent_total_receivable=parent_total_receivable,
                                                        student_rec=stud_id,
                                                        invoice_rec=invoice_id)
                                if stud_id.parents1_id.id:
                                    if stud_id.parents1_id.id not in parents_list:
                                        parents_list.append(stud_id.parents1_id.id)
                                        parents_advance_change.append({stud_id.parents1_id.id:parent_rem_advance})

                        fee_status = stud_id.payment_status.search([('month_id','=',month.id),
                                                                    ('student_id','=',stud_id.id)])
                        if not fee_status.id:
                            status_val = {
                                'month_id': month.id,
                                'paid': False,
                            }
                            stud_id.payment_status = [(0,0,status_val)]
                self.state = 'genarated'
            else:
                raise except_orm(_('Warning !'),
                        _("your selected year %s and month %s does not match as per academic start date %s to end date %s. !")
                                 % (self.year,self.month.id,self.academic_year_id.start_date,self.academic_year_id.end_date))
        else:
            return super(FeePaymentInherit, self).generate_fee_payment()



    @api.multi
    def generate_fee_payment(self):
        # print '================generate fee paument-----------'
        """
        ---------------------------
        :return:
        """
        if 'month_rec' in self._context and 'student_rec' in self._context:
            context = self._context
            student_record = context['student_rec']
            main_month_diff = self.academic_year_id.month_ids.search_count([('batch_id', '=', self.academic_year_id.id),
                                                                   ('leave_month', '=', False)])
            leave_month = []
            for l_month in self.academic_year_id.month_ids.search([('batch_id', '=', self.academic_year_id.id),
                                                                   ('leave_month', '=', True)]):
                leave_month.append((int(l_month.name), int(l_month.year)))
            invoice_obj = self.env['account.invoice']
            student_obj = self.env['res.partner']
            month_year_obj = self.month
            if self.month.leave_month == True:
                # get worning if try to calculate fee for leave month
                raise except_orm(_("Warning!"), _("You can not calculate Fee for Leave month.\n Please Select other month."))

            self.fields_readonly=True
            parents_list = []
            parents_advance_change = []
            if month_year_obj.id:
                for stud_id in student_record:
                    month_diff = main_month_diff
                    joining_date = datetime.strptime(stud_id.admission_date, "%Y-%m-%d").date()
                    start_date = datetime.strptime(self.academic_year_id.start_date, "%Y-%m-%d").date()
                    end_date = datetime.strptime(self.academic_year_id.end_date, "%Y-%m-%d").date()
                    if start_date <= joining_date <= end_date:
                        cal_date = joining_date
                    else:
                        cal_date = start_date
                    get_unpaid_diff = self.get_person_age(start_date, cal_date)
                    month_in_stj = self.months_between(start_date, cal_date)
                    student_total_receivable = stud_id.credit
                    parent_total_receivable = 0.00
                    if stud_id.parents1_id.id:
                        parent_total_receivable = stud_id.parents1_id.credit
                        for parent_advance_dict in parents_advance_change:
                            if stud_id.parents1_id.id in parent_advance_dict:
                                parent_total_receivable = parent_advance_dict[stud_id.parents1_id.id]
    
                    unpaid_month = 0
                    if get_unpaid_diff.get('months') > 0:
                        unpaid_month = get_unpaid_diff.get('months')
                        if len(month_in_stj) > 0 and len(leave_month) > 0:
                            for leave_month_year in leave_month:
                                if leave_month_year in month_in_stj:
                                    unpaid_month -= 1
    
                    month_diff -= unpaid_month
                    first_date_of_month = self.first_day_of_month(int(month_year_obj.name), int(month_year_obj.year))
                    last_date_of_month = self.last_day_of_month(first_date_of_month)
                    if joining_date > last_date_of_month:
                        continue
                    if month_diff <= 0:
                        continue
                    # month_in_joining_end = self.months_between(joining_date, end_date)
                    months = self.striked_off_months(joining_date,start_date,end_date,last_date_of_month,month_year_obj)
                    for month in months:
                        alredy_month_exist = stud_id.payment_status.search([('student_id', '=', stud_id.id),
                                                                            ('month_id','=',month.id)])
                        if alredy_month_exist.id:
                            continue
                        fee_month_amount = 0.00
                        total_discount = 0.00
                        fee_line_lst = []
                        invoice_dic = {}
                        for fee_amount in stud_id.student_fee_line:
                            per_month_year_fee = 0.0
                            dis_amount = 0.00
                            if fee_amount.fee_pay_type.name == 'year':
                                exist_month = stud_id.payment_status.search_count([('student_id', '=', stud_id.id),('month_id.batch_id','=',self.academic_year_id.id)])
                                if exist_month == 0:
                                    all_amount = stud_id.student_fee_line.search([('name', '=', fee_amount.name.id),
                                                                                  ('stud_id', '=', stud_id.id)], limit=1)
                                    per_month_year_fee = all_amount.amount
                                    if fee_amount.discount > 0:
                                        dis_amount = (per_month_year_fee * fee_amount.discount)/100
                                    fee_line_lst.append((0, 0,
                                        {
                                            'product_id': fee_amount.name.id,
                                            'account_id': fee_amount.name.property_account_income_id.id,
                                            'name': fee_amount.name.name,
                                            'quantity': 1,
                                            'price_unit': round(per_month_year_fee, 2),
                                            'parent_id': stud_id.parents1_id.id,
                                            'rem_amount': round(per_month_year_fee, 2),
                                            'priority': fee_amount.sequence,
                                        }))
                                    # student fee detail update
                                    exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                          ('student_id', '=', stud_id.id)], limit=1)
                                    if exist_qtr_pay_detail.id:
                                        # if exist_qtr_pay_detail.month_id.id != month.id:
                                            exist_qtr_pay_detail.write({'cal_amount': per_month_year_fee,
                                                                        'discount_amount': dis_amount,
                                                                        'month_id': month.id})
                                    else:
                                        fee_year_pay_value = {
                                                    'name': fee_amount.name.id,
                                                    'student_id': stud_id.id,
                                                    'month_id': month.id,
                                                    'fee_pay_type': fee_amount.fee_pay_type,
                                                    'cal_amount': per_month_year_fee,
                                                    'total_amount': fee_amount.amount,
                                                    'discount_amount': dis_amount,
                                                }
                                        stud_id.payble_fee_ids = [(0, 0, fee_year_pay_value)]
    
                                fee_month_amount += per_month_year_fee
    
                            elif fee_amount.fee_pay_type.name == 'quater':
                                if month.qtr_month == True:
                                    all_amount = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                ('student_id', '=', stud_id.id)], limit=1, order="id desc")
                                    per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
                                    count_month = 0
                                    for total_month_id in self.academic_year_id.month_ids.search([('qtr_month', '=', True),
                                                                                                  ('batch_id', '=', self.academic_year_id.id),
                                                                                                  ('leave_month', '=', False)]):
                                        exist_month = stud_id.payment_status.search([('month_id', '=', total_month_id.id),
                                                                                     ('student_id', '=', stud_id.id)])
                                        if exist_month.id:
                                            count_month += 1
    
                                    if count_month != 0:
                                        new_per_month_qtr_fee = per_month_qtr_fee * count_month
                                        if all_amount.cal_amount <= new_per_month_qtr_fee:
                                            cal_alt_new = new_per_month_qtr_fee - all_amount.cal_amount
                                            if cal_alt_new > 0:
                                                per_month_qtr_fee = per_month_qtr_fee + cal_alt_new
                                            else:
                                                per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
                                    else:
                                        per_month_qtr_fee = all_amount.total_amount/(month_diff/3)
    
                                    fee_month_amount += per_month_qtr_fee
    
                                    # discount calculation for quater month
                                    fee_paid_line = stud_id.payment_status.search_count([('month_id', '=', total_month_id.id),
                                                                                     ('student_id', '=', stud_id.id)])
                                    if fee_amount.discount > 0:
                                        if fee_paid_line > 0:
                                            if amount_above.discount_amount > 0.0:
                                                alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                                current_month_disamount = (per_month_qtr_fee * fee_amount.discount)/100
                                                if alredy_permonth_discount == current_month_disamount:
                                                    dis_amount = current_month_disamount
                                                elif alredy_permonth_discount < current_month_disamount:
                                                    difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                                    difference_discount = difference_discount_per_month * fee_paid_line
                                                    dis_amount = current_month_disamount + difference_discount
                                                elif alredy_permonth_discount > current_month_disamount:
                                                    difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                                    difference_discount = difference_discount_per_month * fee_paid_line
                                                    dis_amount = current_month_disamount - difference_discount
                                            else:
                                                dis_amount_quater = (per_month_qtr_fee * fee_amount.discount)/100
                                                dis_amount = dis_amount_quater + (dis_amount_quater * fee_paid_line)
                                        else:
                                            dis_amount = (per_month_qtr_fee * fee_amount.discount)/100
                                    total_discount += dis_amount
    
                                    fee_line_lst.append((0, 0,
                                            {
                                                'product_id': fee_amount.name.id,
                                                'account_id': fee_amount.name.property_account_income_id.id,
                                                'name': fee_amount.name.name,
                                                'quantity': 1,
                                                'price_unit': round(per_month_qtr_fee,2),
                                                'parent_id': stud_id.parents1_id.id,
                                                'rem_amount': round(per_month_qtr_fee,2),
                                                'priority': fee_amount.sequence,
                                            }))
                                    # student fee detail update
                                    exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                          ('student_id','=',stud_id.id)], limit=1)
                                    if exist_qtr_pay_detail.id:
                                        # if exist_qtr_pay_detail.month_id.id != month.id:
                                            exist_qtr_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                                        'discount_amount' : all_amount.discount_amount + dis_amount,
                                                                        'month_id': month.id,})
                                    else:
                                        fee_qtr_pay_value =\
                                                {
                                                    'name': fee_amount.name.id,
                                                    'student_id': stud_id.id,
                                                    'month_id': month.id,
                                                    'fee_pay_type': fee_amount.fee_pay_type,
                                                    'cal_amount': all_amount.cal_amount + per_month_qtr_fee,
                                                    'total_amount' : fee_amount.amount,
                                                    'discount_amount' : all_amount.discount_amount + dis_amount
                                                }
                                        stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]
    
                            if fee_amount.fee_pay_type.name == 'half_year':
                                if month.quater_month == True:
                                    fee_details_rec = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                ('student_id', '=', stud_id.id)], limit=1,
                                                                                    order="id desc")
                                    amount_above = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                              ('student_id','=',stud_id.id)])
                                    per_month_half_fee = 0.00
                                    joining_date = datetime.strptime(stud_id.admission_date, "%Y-%m-%d").date()
                                    total_month = self.academic_year_id.month_ids.search_count([('batch_id','=',self.academic_year_id.id),
                                                                                     ('leave_month','=',False)])
                                    batch_start_date = datetime.strptime(self.academic_year_id.start_date, "%Y-%m-%d")
                                    unpaid_month_dic = self.get_person_age(batch_start_date,joining_date)
                                    total_month_rec = total_month - unpaid_month_dic.get('months') or 0
                                    half_month_rec = self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),
                                                                                     ('leave_month','=',False),
                                                                                     ('quater_month','=',True)])
                                    is_next_half_year = True
                                    if len(half_month_rec) == 2:
                                        first_date_of_half = self.first_day_of_month(int(half_month_rec[0].name),
                                                                                      int(half_month_rec[0].year))
                                        second_date_of_half = self.first_day_of_month(int(half_month_rec[1].name),
                                                                                      int(half_month_rec[1].year))
                                        last_date_of_half = datetime.strptime(self.academic_year_id.end_date,"%Y-%m-%d").date()
                                        if fee_details_rec.is_next_half_year:
                                            if second_date_of_half > joining_date:
                                                month_count = self.months_between(second_date_of_half,last_date_of_half)
                                                is_next_half_year = False
                                            else:
                                                month_count = []
                                        else:
                                            if first_date_of_half <= joining_date < second_date_of_half:
                                                month_count = self.months_between(joining_date,second_date_of_half)
                                            elif second_date_of_half <= joining_date < last_date_of_half:
                                                month_count = self.months_between(joining_date,last_date_of_half)
                                        leave_month = []
                                        for l_month in self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),
                                                                                       ('leave_month','=',True)]):
                                            leave_month.append((int(l_month.name),int(l_month.year)))
                                        count_month = []
                                        for month_year in month_count:
                                            if month_year not in leave_month:
                                                count_month.append(month_year)
                                        if total_month_rec > 0 and len(count_month) > 0:
                                            par_month_amount = fee_amount.amount / total_month_rec
                                            per_month_half_fee = par_month_amount * len(count_month)

                                        t_month_count = []
                                        if fee_details_rec.is_next_half_year:
                                            if first_date_of_half <= joining_date < second_date_of_half:
                                                t_month_count = self.months_between(joining_date,second_date_of_half)
                                            elif second_date_of_half <= joining_date < last_date_of_half:
                                                t_month_count = self.months_between(joining_date,last_date_of_half)
                                        t_leave_month = []
                                        for l_month in self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),
                                                                                       ('leave_month','=',True)]):
                                            t_leave_month.append((int(l_month.name),int(l_month.year)))

                                        t_count_month = []
                                        for month_year in t_month_count:
                                            if month_year not in t_leave_month:
                                                t_count_month.append(month_year)
                                        first_month_half_fee = 0.00
                                        if total_month_rec > 0 and len(t_count_month) > 0:
                                            par_month_amount = fee_amount.amount / total_month_rec
                                            first_month_half_fee = par_month_amount * len(t_count_month)
                                        diff_half_amount = first_month_half_fee - amount_above.cal_amount
                                        per_month_half_fee += diff_half_amount
                                    fee_month_amount += per_month_half_fee
                                    #discount calculation for half year
                                    dis_amount = (per_month_half_fee * fee_amount.discount)/100

                                    total_discount += dis_amount

                                    fee_line_lst.append((0, 0,
                                            {
                                                'product_id': fee_amount.name.id,
                                                'account_id': fee_amount.name.property_account_income_id.id,
                                                'name': fee_amount.name.name,
                                                'quantity': 1,
                                                'parent_id': stud_id.parents1_id.id,
                                                'price_unit': round(per_month_half_fee, 2),
                                                'rem_amount': round(per_month_half_fee, 2),
                                                'priority': fee_amount.sequence,
                                            }))
                                    # Student fee detail update
                                    exist_qtr_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                          ('student_id', '=', stud_id.id)], limit=1)
                                    if exist_qtr_pay_detail.id:
                                        # if exist_qtr_pay_detail.month_id.id != month.id:
                                            exist_qtr_pay_detail.write({'cal_amount': fee_details_rec.cal_amount + per_month_half_fee,
                                                                        'discount_amount': fee_details_rec.discount_amount + dis_amount,
                                                                        'month_id': month.id,
                                                                        'is_next_half_year':is_next_half_year})
                                    else:
                                        fee_qtr_pay_value =\
                                                {
                                                    'name': fee_amount.name.id,
                                                    'student_id': stud_id.id,
                                                    'month_id': month.id,
                                                    'fee_pay_type': fee_amount.fee_pay_type,
                                                    'cal_amount': fee_details_rec.cal_amount + per_month_half_fee,
                                                    'total_amount': fee_amount.amount,
                                                    'discount_amount': fee_details_rec.discount_amount + dis_amount,
                                                    'is_next_half_year':is_next_half_year,
                                                }
                                        stud_id.payble_fee_ids = [(0, 0, fee_qtr_pay_value)]
    
                            elif fee_amount.fee_pay_type.name == 'alt_month':
                                if month.alt_month == True:
                                    all_amount = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                ('student_id','=',stud_id.id)], limit=1, order="id desc")
                                    per_month_alt_fee = all_amount.total_amount/(month_diff/2)
                                    count_month = 0
                                    for total_month_id in self.academic_year_id.month_ids.search([('alt_month', '=', True),
                                                                                                  ('batch_id', '=', self.academic_year_id.id),
                                                                                                  ('leave_month', '=', False)]):
                                        exist_month = stud_id.payment_status.search([('month_id', '=', total_month_id.id),
                                                                                     ('student_id', '=', stud_id.id)])
                                        if exist_month.id:
                                            count_month += 1
                                    if count_month != 0:
                                        new_per_month_alt_fee = per_month_alt_fee * count_month
                                        if all_amount.cal_amount <= new_per_month_alt_fee:
                                            cal_alt_new = new_per_month_alt_fee - all_amount.cal_amount
                                            if cal_alt_new > 0:
                                                per_month_alt_fee = per_month_alt_fee + cal_alt_new
                                            else:
                                                per_month_alt_fee = all_amount.total_amount/(month_diff/2)
                                    else:
                                        per_month_alt_fee = all_amount.total_amount/(month_diff/2)
    
                                    fee_month_amount += per_month_alt_fee
    
                                    # discount calculation for alt month
                                    fee_paid_line = stud_id.payment_status.search_count([('month_id', '=', total_month_id.id),
                                                                                     ('student_id', '=', stud_id.id)])
                                    if fee_amount.discount > 0:
                                        if fee_paid_line > 0:
                                            if amount_above.discount_amount > 0.0:
                                                alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                                current_month_disamount = (per_month_alt_fee * fee_amount.discount)/100
                                                if alredy_permonth_discount == current_month_disamount:
                                                    dis_amount = current_month_disamount
                                                elif alredy_permonth_discount < current_month_disamount:
                                                    difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                                    difference_discount = difference_discount_per_month * fee_paid_line
                                                    dis_amount = current_month_disamount + difference_discount
                                                elif alredy_permonth_discount > current_month_disamount:
                                                    difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                                    difference_discount = difference_discount_per_month * fee_paid_line
                                                    dis_amount = current_month_disamount - difference_discount
                                            else:
                                                dis_amount_alt_month = (per_month_alt_fee * fee_amount.discount)/100
                                                dis_amount = dis_amount_alt_month + (dis_amount_alt_month * fee_paid_line)
                                        else:
                                            dis_amount = (per_month_alt_fee * fee_amount.discount)/100
    
                                    total_discount += dis_amount
    
                                    fee_line_lst.append((0,0,
                                            {
                                                'product_id' : fee_amount.name.id,
                                                'account_id' : fee_amount.name.property_account_income_id.id,
                                                'name' : fee_amount.name.name,
                                                'quantity' : 1,
                                                'price_unit' : round(per_month_alt_fee,2),
                                                'parent_id' : stud_id.parents1_id.id,
                                                'rem_amount' : round(per_month_alt_fee,2),
                                                'priority' : fee_amount.sequence,
                                            }))
                                    # student fee detail update
                                    exist_alt_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                          ('student_id', '=', stud_id.id)], limit=1)
                                    if exist_alt_pay_detail.id:
                                        # if exist_alt_pay_detail.month_id.id != month.id:
                                            exist_alt_pay_detail.write({'cal_amount': all_amount.cal_amount + per_month_alt_fee,
                                                                        'discount_amount': all_amount.discount_amount + dis_amount,
                                                                        'month_id': month.id,})
                                    else:
                                        fee_alt_pay_value =\
                                                {
                                                    'name': fee_amount.name.id,
                                                    'student_id': stud_id.id,
                                                    'month_id': month.id,
                                                    'fee_pay_type': fee_amount.fee_pay_type,
                                                    'cal_amount': all_amount.cal_amount + round(per_month_alt_fee, 2),
                                                    'total_amount': fee_amount.amount,
                                                    'discount_amount': all_amount.discount_amount + dis_amount
                                                }
                                        stud_id.payble_fee_ids = [(0, 0, fee_alt_pay_value)]
    
                            elif fee_amount.fee_pay_type.name == 'month':
                                amount_above = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                              ('student_id', '=', stud_id.id)], limit=1)
                                # per month fee calculation
                                per_month_fee = amount_above.total_amount/(month_diff)
                                # already fee paided month
                                fee_paid_line = stud_id.payment_status.search_count([('student_id', '=', stud_id.id),
                                                                                     ('month_id.batch_id','=',self.academic_year_id.id)])
                                if fee_paid_line > 0:
                                    new_rem_amount = per_month_fee * fee_paid_line
                                    if amount_above.cal_amount <= new_rem_amount:
                                        cal_new = new_rem_amount - amount_above.cal_amount
                                        if cal_new > 0:
                                            per_month_fee = cal_new + per_month_fee
                                        else:
                                            per_month_fee = amount_above.total_amount/(month_diff)
                                else:
                                    per_month_fee = amount_above.total_amount/(month_diff)
                                fee_month_amount += per_month_fee
                                # discount calculation for per month
                                if fee_amount.discount > 0:
                                    if fee_paid_line > 0:
                                        if amount_above.discount_amount > 0.0:
                                            alredy_permonth_discount = amount_above.discount_amount/fee_paid_line
                                            current_month_disamount = (per_month_fee * fee_amount.discount)/100
                                            if alredy_permonth_discount == current_month_disamount:
                                                dis_amount = current_month_disamount
                                            elif alredy_permonth_discount < current_month_disamount:
                                                difference_discount_per_month = current_month_disamount - alredy_permonth_discount
                                                difference_discount = difference_discount_per_month * fee_paid_line
                                                dis_amount = current_month_disamount + difference_discount
                                            elif alredy_permonth_discount > current_month_disamount:
                                                difference_discount_per_month = alredy_permonth_discount - current_month_disamount
                                                difference_discount = difference_discount_per_month * fee_paid_line
                                                dis_amount = current_month_disamount - difference_discount
                                        else:
                                            dis_amount_month = (per_month_fee * fee_amount.discount)/100
                                            dis_amount = dis_amount_month + (dis_amount_month * fee_paid_line)
                                    else:
                                        dis_amount = (per_month_fee * fee_amount.discount)/100
                                total_discount += dis_amount
                                fee_line_lst.append((0, 0,
                                    {
                                        'product_id': fee_amount.name.id,
                                        'account_id': fee_amount.name.property_account_income_id.id,
                                        'name': fee_amount.name.name,
                                        'quantity': 1,
                                        'price_unit': round(per_month_fee,2),
                                        'parent_id': stud_id.parents1_id.id,
                                        'rem_amount': round(per_month_fee,2),
                                        'priority': fee_amount.sequence,
                                    }))
                                # Student Fee Detail Update
                                exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name', '=', fee_amount.name.id),
                                                                                       ('student_id', '=', stud_id.id)], limit=1)
                                if exist_stud_pay_detail.id:
                                    # if exist_stud_pay_detail.month_id.id != month.id:
                                        exist_stud_pay_detail.write({'cal_amount': amount_above.cal_amount + per_month_fee,
                                                                     'discount_amount': amount_above.discount_amount + dis_amount,
                                                                     'month_id': month.id})
                                else:
                                    fee_pay_value =\
                                        {
                                            'name': fee_amount.name.id,
                                            'student_id': stud_id.id,
                                            'month_id': month.id,
                                            'fee_pay_type': fee_amount.fee_pay_type,
                                            'cal_amount': amount_above.cal_amount + per_month_fee,
                                            'total_amount': fee_amount.amount,
                                            'discount_amount': amount_above.discount_amount + dis_amount
                                        }
    
                                    stud_id.payble_fee_ids = [(0, 0, fee_pay_value)]
                            # Term Wise Fee Calculations
                            elif fee_amount.fee_pay_type.name == 'term':
                                paid_term_obj = self.env['paid.term.history']
                                terms=self.env['acd.term'].search([('batch_id','=',self.academic_year_id.id)])
                                amount_above = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                              ('student_id','=',stud_id.id)])
                                current_term=amount_above.next_term
                                exist_stud_pay_detail = stud_id.payble_fee_ids.search([('name','=',fee_amount.name.id),
                                                                                       ('student_id','=',stud_id.id)])

                                per_month_fee=0
                                dis_amount = 0
                                term_id=False
                                prev_term_seq=exist_stud_pay_detail.next_term.id

                                if prev_term_seq:
                                    same_seq_terms=self.env['acd.term'].search([('id','>',prev_term_seq)])
                                next_term=exist_stud_pay_detail.next_term.id
                                invoice_dic={}
                                if current_term.id:
                                    start_date = datetime.strptime(current_term.start_date, "%Y-%m-%d")
                                    end_date = datetime.strptime(current_term.end_date, "%Y-%m-%d")
                                    difference_amount = 0.00
                                    if start_date.month == month.name:
                                        if int(start_date.year) == int(month.year):
                                            term_month = self.months_between(start_date,end_date)
                                            total_month_diff = self.academic_year_id.month_ids.search_count([('batch_id', '=', self.academic_year_id.id),
                                                                            ('leave_month', '=', False)])
                                            batch_start_date = datetime.strptime(self.academic_year_id.start_date, "%Y-%m-%d")
                                            joining_date = datetime.strptime(stud_id.admission_date, "%Y-%m-%d").date()
                                            unpaid_month_dic = self.get_person_age(batch_start_date,joining_date)
                                            t_month_diff = total_month_diff - unpaid_month_dic.get('months') or 0
                                            per_month_fee = (fee_amount.amount / t_month_diff) * len(term_month)
                                            term_id=amount_above.next_term.id
                                            prev_paid_rec=paid_term_obj.search([('student_id','=',stud_id.id),('term_id','=',term_id),('batch_id','=',self.academic_year_id.id)])
                                            if not prev_paid_rec:
                                                paid_term_obj.create({'student_id':stud_id.id,'term_id':term_id,'batch_id':self.academic_year_id.id})
                                            if same_seq_terms.ids:
                                                list=[]
                                                for each in same_seq_terms:
                                                    if each in terms:
                                                        list.append(each.id)
    #                                                    next_term=each.id
                                                if list:
                                                    list=sorted(list)
                                                    next_term=list[0]

                                            term_in_batch = self.env['acd.term'].search([('batch_id','=',self.academic_year_id.id)])
                                            total_term_cal = 0.00
                                            for term_rec in term_in_batch:
                                                if term_rec.id == current_term.id:
                                                    break
                                                term_start_date = datetime.strptime(term_rec.start_date, "%Y-%m-%d").date()
                                                term_end_date = datetime.strptime(term_rec.end_date, "%Y-%m-%d").date()
                                                # start with joining date in
                                                if term_start_date <= joining_date <= term_end_date:
                                                    term_month = self.months_between(joining_date,term_end_date)
                                                    total_term_cal += (fee_amount.amount / t_month_diff) * len(term_month)
                                                elif joining_date <= term_end_date:
                                                    term_month = self.months_between(term_start_date,term_end_date)
                                                    total_term_cal += (fee_amount.amount / t_month_diff) * len(term_month)
                                            if total_term_cal > 0.00 and amount_above.cal_amount > 0.00:
                                                difference_amount = total_term_cal - amount_above.cal_amount

                                            per_month_fee += difference_amount

                                            # discount calculation
                                            if fee_amount.discount > 0:
                                                pre_dis = 0.00
                                                if amount_above.cal_amount > 0.00:
                                                    pre_dis = (amount_above.cal_amount * fee_amount.discount) / 100
                                                    if pre_dis != amount_above.discount_amount:
                                                        if pre_dis < amount_above.discount_amount:
                                                            pre_dis = pre_dis - amount_above.discount_amount
                                                        else:
                                                            pre_dis = pre_dis - amount_above.discount_amount
                                                dis_amount = (per_month_fee * fee_amount.discount) / 100
                                                #dis_amount += pre_dis
                                        else:
                                            per_month_fee=0
                                            term_id=False

                                total_discount += dis_amount
                                fee_month_amount += per_month_fee
                                if per_month_fee > 0.00:
                                    fee_line_lst.append((0,0,
                                            {
                                                'product_id' : fee_amount.name.id,
                                                'account_id' : fee_amount.name.property_account_income_id.id,
                                                'name' : fee_amount.name.name,
                                                'quantity' : 1.00,
                                                'price_unit' : round(per_month_fee,2),
                                                'rem_amount' : round(per_month_fee,2),
                                                'parent_id' : stud_id.parents1_id.id,
                                                'priority' : fee_amount.sequence,
                                            }))

                                fee_pay_value =\
                                            {
                                                'name': fee_amount.name.id,
                                                'student_id': stud_id.id,
                                                'month_id': month.id,
                                                'fee_pay_type': fee_amount.fee_pay_type.name,
                                                'cal_amount': amount_above.cal_amount + per_month_fee,
                                                'total_amount' : fee_amount.amount,
                                                'next_term':next_term,
                                                'discount_amount' : amount_above.discount_amount + dis_amount,
                                            }
                                invoice_dic.update({'term_id':term_id or "",})
                                if not exist_stud_pay_detail.id:
                                    stud_id.payble_fee_ids = [(0, 0, fee_pay_value)]
                                else:
                                    for val in exist_stud_pay_detail:
                                        val.cal_amount=amount_above.cal_amount + per_month_fee
                                        val.next_term=next_term
                                        val.discount_amount = amount_above.discount_amount + dis_amount

                            if fee_amount.discount > 0.00 and dis_amount != 0.00:
                                if not fee_amount.name.fees_discount:
                                    raise except_orm(_("Warning!"), _('Please define Discount Fee For %s.')%(fee_amount.name.name))
                                else:
                                    if not fee_amount.name.fees_discount.property_account_income_id.id:
                                        raise except_orm(_("Warning!"), _('Please define account Income for %s.')%(fee_amount.name.fees_discount.name))
                                    else:
                                        fee_line_lst.append((0,0,{
                                            'product_id' : fee_amount.name.fees_discount.id,
                                            'account_id' : fee_amount.name.fees_discount.property_account_income_id.id,
                                            'name' : fee_amount.name.fees_discount.name,
                                            'quantity' : 1.00,
                                            'parent_id' : stud_id.parents1_id.id,
                                            'price_unit' : -round(dis_amount,2),
                                            'rem_amount' : -round(dis_amount,2),
                                            'priority' : 0,
                                            }))
                        # Monthly Fee Payment Generate Line
                        exist_month_rec = self.search([('course_id', '=', self.course_id.id),
                                                       ('academic_year_id', '=', self.academic_year_id.id),
                                                       ('month', '=', month.id)])
                        if len(exist_month_rec)> 0:
                            exist_fee_line = exist_month_rec.fee_payment_line_ids.search([('student_id', '=', stud_id.id),
                                                                            ('month_id', '=', self.month.id),
                                                                            ('year', '=', self.year)])
                            if not exist_fee_line.id:
                                exist_month_rec.fee_payment_line_ids.create({
                                    'student_id': stud_id.id,
                                    'total_fee': fee_month_amount-total_discount,
                                    'month_id': month.id,
                                    'month': month.name,
                                    'year': month.year,
                                    'fee_payment_id': exist_month_rec.id,
                                    })
                        else:
                            create_month_rec = self.create({
                                'name': str(self.course_id.name)+'/' + str(month.name)+'/'+str(month.year)+'Fee Calculation',
                                'code': str(self.course_id.name)+'/'+str(month.name)+'/'+str(month.year)+' Fee Calculation',
                                'course_id': self.course_id.id,
                                'academic_year_id': self.academic_year_id.id,
                                'month': month.id,
                            })
                            create_month_rec.fee_payment_line_ids.create({
                                'student_id': stud_id.id,
                                'total_fee': fee_month_amount-total_discount,
                                'month_id': month.id,
                                'month': month.name,
                                'year': month.year,
                                'fee_payment_id': create_month_rec.id,
                                })
    
                        # Invoice Create
                        exist_invoice = invoice_obj.search_count([('partner_id','=',stud_id.id),('month_id','=',month.id)])
                        if exist_invoice == 0 and len(fee_line_lst) > 0:
                            invoice_date = self.first_day_of_month(int(month.name), int(month.year))
                            invoice_vals = {
                                    'partner_id' : stud_id.id,
                                    'month_id' : month.id,
                                    'account_id' : stud_id.property_account_receivable_id.id,
                                    'invoice_line_ids' : fee_line_lst,
                                    'month' : month.name,
                                    'year' : month.year,
                                    'batch_id' : self.academic_year_id.id,
                                    'date_invoice' : invoice_date,
                                }
                            invoice_id = invoice_obj.create(invoice_vals)

                            if invoice_dic:
                                invoice_id.write(invoice_dic)

                            # Invoice validate
                            invoice_id.action_invoice_open()
                            # invoice_id.action_date_assign()
                            # invoice_id.action_move_create()
                            # invoice_id.action_number()
                            # invoice_id.invoice_validate()

                            # send payfort link for online fee payment
                            if invoice_id.id:
                                parent_rem_advance = self.with_context({'send_mail':False}).send_payforts_link(student_total_receivable=student_total_receivable,
                                                        parent_total_receivable=parent_total_receivable,
                                                        student_rec=stud_id,
                                                        invoice_rec=invoice_id)

                                if stud_id.parents1_id.id:
                                    if stud_id.parents1_id.id not in parents_list:
                                        parents_list.append(stud_id.parents1_id.id)
                                        parents_advance_change.append({stud_id.parents1_id.id:parent_rem_advance})

                        fee_status = stud_id.payment_status.search([('month_id','=',month.id),
                                                                    ('student_id','=',stud_id.id)])
                        if not fee_status.id:
                            status_val = {
                                'student_id':stud_id.id,
                                'month_id': month.id,
                                'paid': False,
                            }
                            stud_id.payment_status.create(status_val)
                self.state = 'genarated'
            else:
                raise except_orm(_('Warning !'),
                        _("your selected year %s and month %s does not match as per academic start date %s to end date %s. !")
                                 % (self.year,self.month.id,self.academic_year_id.start_date,self.academic_year_id.end_date))
        else:
            return super(FeePaymentInherit, self).generate_fee_payment()
        
class res_partner(models.Model):
    
    _inherit = 'res.partner'
     
    transfer_id = fields.One2many('trensfer.certificate', 'name', 'Transfer Certificate')
