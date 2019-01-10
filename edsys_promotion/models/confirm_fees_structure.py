# -*- coding: utf-8 -*-
from odoo import _
from odoo import api
from odoo import fields
from odoo import models
from datetime import datetime
from odoo.exceptions import except_orm


class Fee_Confirmation(models.Model):
    _name = 'fee.confirmation'

    name = fields.Many2one('product.product', 'Name', required=True)
    sequence = fields.Integer('Priority')
    amount = fields.Float('Amount', required=True)
    type = fields.Selection([('required', 'Required'), ('optional', 'Optional')])
    fee_pay_type = fields.Many2one('fee.payment.type', string="Fee Payment Type")
    update_amount = fields.Float(string='Update Amount')
    discount = fields.Float(string="Discount(%)")
    discount_amount = fields.Float(string='Discount Amount')
    amount_from_percentage = fields.Float(string='Update Amount In Percentage(%)')
    promote_line_id = fields.Many2one('promote.student.line', string="Fee line")


class Student_Fee_History(models.Model):
    _name = 'student.fee.history'

    name = fields.Many2one('product.product', 'Name', required=True)
    sequence = fields.Integer('Priority')
    amount = fields.Float('Amount', required=True)
    type = fields.Selection([('required', 'Required'), ('optional', 'Optional')])
    fee_pay_type = fields.Many2one('fee.payment.type', string="Fee Payment Type")
    update_amount = fields.Float(string='Update Amount')
    discount = fields.Float(string="Discount(%)")
    discount_amount = fields.Float(string='Discount Amount')
    amount_from_percentage = fields.Float(string='Update Amount In Percentage(%)')
    academic_year_id = fields.Many2one('batch', 'Academic Year')
    class_id = fields.Many2one('course', 'Class')
    fee_history = fields.Many2one('res.partner', string="Student")


class confirm_fee_structure(models.Model):
    _inherit = 'promote.student.line'
    _rec_name = 'student_id'

    status = fields.Selection([('not_confirm', 'Not Confirmed'), ('confirm', 'Confirmed')],
                              string='Status', default='not_confirm')
    fees_structure_lines = fields.One2many('fee.confirmation', 'promote_line_id', string='Fee Structure')
    discount_category = fields.Many2one('discount.category', string='Fee Discount')
    promoted_fee_structure_confirm = fields.Boolean('Fee Structure Confirm')
    promoted_fee_structure_done = fields.Boolean('Fee Structure Done')


    @api.multi
    def update_fee_structure(self):
        """
        This method update the fee structure by adding mentioned discount.
        """
        # first all discount update with 0 value
        for feess in self.fees_structure_lines:
            feess.discount_amount = 0.0
            feess.discount = 0.0

        if self.discount_category:
            # apply discount on fee structure
            for discount_fee_line in self.discount_category.discount_category_line.search([
                                                                                        ('discount_category_id', '=', self.discount_category.id)]):
                for fees in self.fees_structure_lines:
                    if fees.name.fees_discount:
                        if fees.name.fees_discount == discount_fee_line.product_id:
                            if discount_fee_line.discount_type == 'amount':
                                if discount_fee_line.discount_amount > 0.00 and fees.amount > 0.00:
                                    fees.discount_amount = discount_fee_line.discount_amount


                            elif discount_fee_line.discount_type == 'persentage':
                                if discount_fee_line.discount_persentage > 0.00 and fees.amount > 0.00:
                                    fees.discount = discount_fee_line.discount_persentage
                                    fees.discount_amount = (discount_fee_line.discount_persentage * fees.amount)/100

    '''
    @api.multi
    def send_mail_for_promoted_fee_structure(self):
        email_server = self.env['ir.mail_server']
        email_sender = email_server.search([])
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_promotion', 'email_template1_promote_fee_structure')[1]
        template_rec = self.env['email.template'].browse(template_id)
        template_rec.write({'email_to': self.student_id.email, 'email_from': email_sender.smtp_user, 'email_cc': ''})
        template_rec.send_mail(self.id)
    '''

    @api.multi
    def send_mail_for_promoted_fee_structure(self):
        email_server = self.env['ir.mail_server']
        email_sender = email_server.search([])
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('edsys_promotion', 'email_template1_promote_fee_structure')[1]
        template_rec = self.env['mail.template'].browse(template_id)
        email_to = ''
        if self.student_id.email:
            student_mail = self.student_id.email
        if self.student_id.parents1_id.parents_email:
            parent_mail = self.student_id.parents1_id.parents_email
        
        email_to = student_mail + ',' + parent_mail
        template_rec.write({'email_to': email_to, 'email_from': email_sender.smtp_user, 'email_cc': ''})
        template_rec.send_mail(self.id)

    @api.multi
    def confirm_promoted_fee_structure(self):
        if self.promoted_fee_structure_done == True:
            raise except_orm(_('Warning!'), _("Fee structure Already confirm."))
        else:
            if self.discount_category.id:
                self.update_fee_structure()
            self.promoted_fee_structure_done = True

    @api.multi
    def reverse_promoted_fee_structure(self):
        """
        reverse the fee structure by updating the previous one i.e.
        fee structure without adding mentioned discount.
        """
        if self.promoted_fee_structure_done == False:
            raise except_orm(_('Warning!'), _("Fee structure Already Reversed."))
        else:
            fee_line_obj = self.env['fees.structure']
            for fees in fee_line_obj.search([
                    ('academic_year_id', '=', self.new_acad_year.id),
                    ('course_id', '=', self.new_acad_class.id),
                    ('type', '=', 'academic')]):
                for fee_line in fees.fee_line_ids:
                    for stud_fee in self.fees_structure_lines:
                        if stud_fee.name == fee_line.name:
                            stud_fee.write({'amount': fee_line.amount,
                                            'discount': 0.00,
                                            'discount_amount': 0.00})
            self.promoted_fee_structure_done = False

    @api.multi
    def confirm_done_promoted_fee_structure(self):
        """
        finally Done fee structure with all fee calculation,
        update the fee structure and also Academic year,Class and section with new one
        in student menu
        """
        fee_list = []
        self.write({'promoted_fee_structure_confirm': True, 'status': 'confirm', 'state': 'fee_confirmed'})
        self.student_id.write({'promoted': False, 'admission_date': self.new_acad_year.start_date,
                               'course_id': self.new_acad_class.id, 'class_id': self.new_acad_class.id,
                               'batch_id': self.new_acad_year.id, 'year_id': self.new_acad_year.id,
                               'student_section_id': self.new_acad_section.id, 'discount_on_fee': self.discount_category.id})
        
        for fee in self.student_id.student_fee_line:
            fee_line_data = {
                    'fee_history': self.student_id.id,
                    'academic_year_id': self.current_academic_year.id,
                    'class_id': self.current_academic_class.id,
                    'sequence': fee.sequence,
                    'name': fee.name,
                    'amount': int(fee.amount),
                    'discount': int(fee.discount),
                    'discount_amount': int(fee.discount_amount),
                    'type': fee.type,
                    'fee_pay_type': fee.fee_pay_type.id
                    }
            fee_list.append((0, 0, fee_line_data))
        self.student_id.student_fees_history = fee_list

        for fee_line_rec in self.student_id.student_fee_line:
            self.student_id.student_fee_line = [(2, fee_line_rec.id)]

        confirm_fee_list = []
        for confirm_fee_line_rec in self.fees_structure_lines:
            fee_dict = {
                'stud_id': self.student_id.id,
                'sequence': confirm_fee_line_rec.sequence,
                'name': confirm_fee_line_rec.name,
                'amount': int(confirm_fee_line_rec.amount),
                'discount': int(confirm_fee_line_rec.discount),
                'discount_amount': int(confirm_fee_line_rec.discount_amount),
                'type': confirm_fee_line_rec.type,
                'fee_pay_type': confirm_fee_line_rec.fee_pay_type.id
                }
            confirm_fee_list.append((0, 0, fee_dict))
        self.student_id.student_fee_line = confirm_fee_list

        payable_list = []
        start_date = datetime.strptime(self.new_acad_year.start_date, "%Y-%m-%d").date()
        month_rec = self.new_acad_year.month_ids.search([('name', '=', start_date.month), ('year', '=', str(start_date.year))], limit=1)
        for fee_structure_line_rec in self.fees_structure_lines:
            next_term = False
            if fee_structure_line_rec.fee_pay_type.name == 'term':
                print "self.new_acad_year==>",self.new_acad_year.name
                terms = self.env['acd.term'].search([('batch_id','=',self.new_acad_year.id)])
                if len(terms) == 0:
                    raise except_orm(_('Warning!'), _("Term not define for Academic year : %s"%(self.new_acad_year.name)))
                next_term = terms[0]
            fee_payable_data = {
                'name': fee_structure_line_rec.name.id,
                'month_id': month_rec.id,
                'fee_pay_type': fee_structure_line_rec.fee_pay_type.id,
                'total_amount': int(fee_structure_line_rec.amount),
                'discount_amount': 0.00,
                'cal_amount': 0.00,
                'cal_turm_amount': 0.00,
                'student_id': self.student_id.id,
                'next_term': next_term,
                'is_next_half_year':False,
                }
            payable_list.append((0, 0, fee_payable_data))
        if len(payable_list) == 0:
            raise except_orm(_('Warning!'), _(" Fee Payable Structure is Not Define !"))
        else:
            for fee_payable_line in self.student_id.payble_fee_ids:
                self.student_id.payble_fee_ids = [(2, fee_payable_line.id)]
            self.student_id.payble_fee_ids = payable_list

        self.send_mail_for_promoted_fee_structure()
