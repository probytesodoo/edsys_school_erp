from odoo import models, fields, api, _
import datetime
from odoo.exceptions import except_orm
import time

class fee_payment(models.Model):
    """
    Fee Payment
    """
    _inherit = 'fee.payment'
    _description = 'Fee Payment'
    
    @api.multi
    def generate_invoices(self):
        print'==============generate invoice=================='
        if self.month.leave_month == True:
            raise except_orm(_("Warning!"), _("You can not calculate Fee for Leave month.\n Please Select other month."))
        
        student_obj = self.env['res.partner']
        course_obj = self.env['course']
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        registration_obj = self.env['registration']
        nyaf_obj = self.env['next.year.advance.fee']
        
        section_id_list = []
        
        month_diff = self.academic_year_id.month_ids.search_count([('batch_id','=',self.academic_year_id.id),
                                                                   ('leave_month','=',False)])
        leave_month = []
        parents_list = []
        parents_advance_change = []
        
        if self.month.id:
            acd_yr_start_date = datetime.datetime.strptime(self.academic_year_id.start_date, "%Y-%m-%d").date()
            acd_yr_end_date = datetime.datetime.strptime(self.academic_year_id.end_date, "%Y-%m-%d").date()
            first_date_of_month = self.first_day_of_month(int(self.month.name), int(self.month.year))
            last_date_of_month = self.last_day_of_month(first_date_of_month)
            
            for l_month in self.academic_year_id.month_ids.search([('batch_id','=',self.academic_year_id.id),('leave_month','=',True)]):
                leave_month.append((int(l_month.name),int(l_month.year)))
                
            
            if self.section_ids :
                for section_id in self.section_ids :
                     section_id_list.append(section_id.id)
            else :
                section_id_list.append(False)
                for section in self.course_id.section :
                    section_id_list.append(section.id)
            
            student_recs = student_obj.search([('is_parent', '=', False),
                                               ('is_student', '=', True),
                                               ('active', '=', True),
                                               ('student_section_id', 'in', section_id_list),
                                               ('course_id', '=', self.course_id.id),
                                               ('batch_id', '=', self.academic_year_id.id)])
            for student_rec in student_recs :
                generate_invoice = False
                reg_rec = registration_obj.search([('enquiry_no','=',student_rec.reg_no)])
                if reg_rec :
                    if reg_rec.fee_status in ['academy_fee_partial_pay', 'academy_fee_pay']:
                        generate_invoice =  True
                else :
                    generate_invoice = True
                if generate_invoice :
                    student_total_receivable = student_rec.credit
                    parent_total_receivable = 0.00
                    if student_rec.parents1_id.id:
                        parent_total_receivable = student_rec.parents1_id.credit
                        for parent_advance_dict in parents_advance_change:
                            if student_rec.parents1_id.id in parent_advance_dict:
                                parent_total_receivable = parent_advance_dict[student_rec.parents1_id.id]
                    admission_date = datetime.datetime.strptime(student_rec.admission_date, "%Y-%m-%d").date()
                    months = self.striked_off_months(admission_date, acd_yr_start_date, acd_yr_end_date, last_date_of_month, self.month)
                    for month in months:
                        priority = 1
                        invoice_line_list = []
                        if student_rec.fee_computation_ids :
                            for fee_computation_rec in student_rec.fee_computation_ids :
                                if fee_computation_rec.month_id == month and  fee_computation_rec.status == 'invoice_not_raised' :
                                    for fee_computation_line_rec in fee_computation_rec.fee_computation_line_ids :
                                        invoice_lines = {
                                                            'product_id': fee_computation_line_rec.name.id,
                                                            'account_id': fee_computation_line_rec.name.property_account_income_id.id,
                                                            'name': fee_computation_line_rec.name.name,
                                                            'quantity': 1,
                                                            'price_unit': fee_computation_line_rec.calculated_amount,
                                                            'parent_id': student_rec.parents1_id.id,
                                                            'rem_amount': fee_computation_line_rec.calculated_amount,
                                                            'priority': priority,
                                                         }
                                        invoice_lines_rec = invoice_line_obj.create(invoice_lines)
                                        priority += 1
                                        invoice_line_list.append(invoice_lines_rec.id)
                                        if fee_computation_line_rec.discount_amount > 0.00 or fee_computation_line_rec.discount_percentage > 0.00 :
                                            discount_invoice_lines = {
                                                            'product_id': fee_computation_line_rec.name.fees_discount.id,
                                                            'account_id':fee_computation_line_rec.name.fees_discount.property_account_income_id.id,
                                                            'name': fee_computation_line_rec.name.fees_discount.name,
                                                            'quantity': 1,
                                                            'price_unit': -(fee_computation_line_rec.discount_amount),
                                                            'parent_id': student_rec.parents1_id.id,
                                                            'rem_amount': -(fee_computation_line_rec.discount_amount),
                                                            'priority':  priority,
                                                         }
                                            discount_invoice_lines_rec = invoice_line_obj.create(discount_invoice_lines)
                                            invoice_line_list.append(discount_invoice_lines_rec.id)
                                            priority += 1
                                        
                                        # student fee detail update
                                        exist_pay_detail = student_rec.payble_fee_ids.search([('name', '=', fee_computation_line_rec.name.id),
                                                                                              ('student_id', '=', student_rec.id)], limit=1)
                                        if exist_pay_detail.id:
                                            # if exist_pay_detail.month_id.id != month.id:
                                                exist_pay_detail.write({'cal_amount': fee_computation_line_rec.calculated_amount,
                                                                            'discount_amount': fee_computation_line_rec.discount_amount,
                                                                            'month_id': month.id})
                                        else:
                                            student_fee_line = student_rec.student_fee_line.search([('stud_id','=', student_rec.id), ('name','=', fee_computation_line_rec.name.id)])
                                            fee_year_pay_value = {
                                                        'name': fee_computation_line_rec.name.id,
                                                        'student_id': student_rec.id,
                                                        'month_id': month.id,
                                                        'fee_pay_type': fee_computation_line_rec.fee_payment_type_id.id,
                                                        'cal_amount': fee_computation_line_rec.calculated_amount,
                                                        'total_amount': round(student_fee_line.amount),
                                                        'discount_amount': fee_computation_line_rec.discount_amount,
                                                        'student_id' : student_rec.id
                                                    }
                                            exist_pay_detail.create(fee_year_pay_value)
                            
                                    # Monthly Fee Payment Generate Line
                                    exist_month_rec = self.search([('course_id', '=', self.course_id.id),
                                                                   ('academic_year_id', '=', self.academic_year_id.id),
                                                                   ('month', '=', month.id)])
                                    if len(exist_month_rec)> 0:
                                        exist_fee_line = exist_month_rec.fee_payment_line_ids.search([('student_id', '=', student_rec.id),
                                                                                        ('month_id', '=', month.id),
                                                                                        ('year', '=', self.year)])
                                        if not exist_fee_line.id:
                                            fee_payment_line_vals = {
                                                                        'student_id': student_rec.id,
                                                                        'total_fee': fee_computation_rec.invoice_amount,#fee_month_amount-total_discount,
                                                                        'month_id': month.id,
                                                                        'month': month.name,
                                                                        'year': month.year,
                                                                        'fee_payment_id': exist_month_rec.id,
                                                                    }
                                            exist_month_rec.fee_payment_line_ids.create(fee_payment_line_vals)
                                    else:
                                        create_month_rec = self.create({
                                            'name': str(self.course_id.name)+'/' + str(month.name)+'/'+str(month.year)+'Fee Calculation',
                                            'code': str(self.course_id.name)+'/'+str(month.name)+'/'+str(month.year)+' Fee Calculation',
                                            'course_id': self.course_id.id,
                                            'academic_year_id': self.academic_year_id.id,
                                            'month': month.id,
                                        })
                                        fee_payment_line_vals = {
                                                                    'student_id': student_rec.id,
                                                                    'total_fee': fee_computation_rec.invoice_amount, #fee_month_amount-total_discount,
                                                                    'month_id': month.id,
                                                                    'month': month.name,
                                                                    'year': month.year,
                                                                    'fee_payment_id': create_month_rec.id,
                                                                }
                                        create_month_rec.fee_payment_line_ids.create( fee_payment_line_vals )
#                                     fee_computation_rec.status = 'invoice_raised'
                                    # Invoice Create
                                    exist_invoice = invoice_obj.search_count([('partner_id','=',student_rec.id),('month_id','=',month.id)])
                                    if exist_invoice == 0 and len(invoice_line_list) > 0:
                                        invoice_date = self.first_day_of_month(int(month.name), int(month.year))
                                        invoice_vals = {
                                            'partner_id' : student_rec.id,
                                            'month_id' : month.id,
                                            'account_id' : student_rec.property_account_receivable_id.id,
                                            'invoice_line_ids' : [(6, 0, invoice_line_list)],
                                            'month' :  month.name,
                                            'year' : month.year,
                                            'batch_id' : self.academic_year_id.id,
                                            'date_invoice' : fee_computation_rec.fee_date,
                                        }
                                        invoice_rec = invoice_obj.create(invoice_vals)
                
                                        # Invoice validate
#                                         invoice_rec.signal_workflow('invoice_open')
                                        invoice_rec.action_invoice_open()
#                                         invoice_rec._get_outstanding_info_JSON()
#                                         invoice_rec.action_invoice_paid()
                                        
                                        nyaf_rec = nyaf_obj.search([ ('is_reconciled', '=', False),('partner_id', '=', student_rec.id),('batch_id', '=', self.academic_year_id.id), ('state','in',('fee_paid', 'fee_partial_paid') )])
                                        if nyaf_rec :
                                            nyaf_rec.reconcile_nyaf(invoice_rec)
                                            nyaf_rec.is_reconciled = True
                                            reg_rec.invoice_id=invoice_rec.id
                
                                        # send payfort link for online fee payment
                                        if invoice_rec.id:
                                            parent_rem_advance = self.send_payforts_link(student_total_receivable = student_total_receivable,
                                                                    parent_total_receivable = parent_total_receivable,
                                                                    student_rec = student_rec,
                                                                    invoice_rec = invoice_rec)
                                            if student_rec.parents1_id.id:
                                                if student_rec.parents1_id.id not in parents_list:
                                                    parents_list.append(student_rec.parents1_id.id)
                                                    parents_advance_change.append({student_rec.parents1_id.id:parent_rem_advance})
            
                                    fee_status = student_rec.payment_status.search([('month_id','=',month.id),
                                                                                ('student_id','=',student_rec.id)])
                                    if not fee_status.id:
                                        payment_status_val = {
                                            'student_id':student_rec.id,
                                            'month_id': month.id,
                                            'paid': False,
                                        }
                                        student_rec.payment_status.create(payment_status_val)
                                    fee_computation_rec.status = 'invoice_raised'
				    if reg_rec :
					if reg_rec.fee_computation_ids :
					    reg_rec.fee_computation_ids[0].status = 'invoice_raised'
                            
            self.state = 'genarated'
            print self.state,'------===223 fee payment===========generted'
#             raise except_orm(_("Warning!"), _('stop'))
        else:
            raise except_orm(_('Warning !'),
                    _("your selected year %s and month %s does not match as per academic start date %s to end date %s. !")
                             % (self.year,self.month.id,self.academic_year_id.start_date,self.academic_year_id.end_date))

