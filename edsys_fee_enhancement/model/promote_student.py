from odoo import models, fields, api, _
from odoo.exceptions import except_orm
import datetime

class promote_student_line(models.Model):

    _inherit = 'promote.student.line'
    
    discount_applicable_date = fields.Date('Discount Applicable Date')
    fee_computation_ids = fields.One2many('fee.computation', 'promote_student_line_id' ,'Fee Computation')
    
    @api.multi
    def write(self, vals):
        if 'discount_applicable_date' in vals and vals['discount_applicable_date']:
            discount_applicable_date_formatted = datetime.datetime.strptime(vals['discount_applicable_date'], "%Y-%m-%d").date()
            current_date = datetime.date.today()
            acd_yr_start_date = self.new_acad_year.start_date
            acd_yr_start_date_formatted = datetime.datetime.strptime(acd_yr_start_date, "%Y-%m-%d").date()
            acd_yr_end_date = self.new_acad_year.end_date
            acd_yr_end_date_formatted = datetime.datetime.strptime(acd_yr_end_date, "%Y-%m-%d").date()
            if discount_applicable_date_formatted < acd_yr_start_date_formatted and discount_applicable_date_formatted > acd_yr_end_date_formatted:
                raise except_orm(_('Warning!'), _("Discount Applicable Date should between academic year start date and end date "))
        return super(promote_student_line, self).write(vals)
    
    @api.multi
    def confirm_done_promoted_fee_structure(self):
        res = super(promote_student_line, self).confirm_done_promoted_fee_structure()
        fee_computation_obj = self.env['fee.computation']
        self.student_id.write({ 'student_section_id': self.new_acad_section.id, 
                               'discount_on_fee' : self.discount_category.id,
                               'discount_applicable_date' : self.discount_applicable_date })
         
        if self.student_id.fee_computation_ids :
            #remove previous years fee computation lines
            for fee_computation_rec in self.student_id.fee_computation_ids :
                fee_computation_rec.unlink()
        #create new fee computation lines
        self.student_id.update_fee_structure()
        #create same lines to promotion fee computation
        if self.student_id.fee_computation_ids :
            for fee_computation_rec in self.student_id.fee_computation_ids :
                fee_computation_line_ids = []
                for fee_computation_line_rec in fee_computation_rec.fee_computation_line_ids :
                    fee_computation_line_vals = {
                                                    'name' : fee_computation_line_rec.name.id,
                                                    'calculated_amount' : fee_computation_line_rec.calculated_amount,
                                                    'discount_percentage' : fee_computation_line_rec.discount_percentage,
                                                    'discount_amount' : round(fee_computation_line_rec.discount_amount),
                                                    'payable_amount' : round(fee_computation_line_rec.payable_amount),
                                                    'fee_payment_type_id' : fee_computation_line_rec.fee_payment_type_id.id,
                                                }
                    fee_computation_line_ids.append((0,0,fee_computation_line_vals))
                fee_computation_vals = {
                                        'month_id' : fee_computation_rec.month_id.id,
                                        'fee_date' : fee_computation_rec.fee_date,
                                        'fee_computation_line_ids' : fee_computation_line_ids, #[ (6, 0, fee_computation_line_ids_list) ],
                                        'total_calculated_amount' : fee_computation_rec.total_calculated_amount,
                                        'total_discount_amount' : fee_computation_rec.total_discount_amount,
                                        'invoice_amount' : fee_computation_rec.invoice_amount,
                                        'discount_category_id' : fee_computation_rec.discount_category_id.id,
                                        'status' : fee_computation_rec.status,
                                        'promote_student_line_id' : self.id
                                    }
                fee_computation_id = fee_computation_obj.create(fee_computation_vals)
        
