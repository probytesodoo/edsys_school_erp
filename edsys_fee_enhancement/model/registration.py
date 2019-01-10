from odoo import models, fields, api, _
import datetime
from odoo.exceptions import except_orm
import base64

class Registration(models.Model):

    _inherit = 'registration'
    
    discount_applicable_date = fields.Date('Discount Applicable Date')
    fee_computation_ids = fields.One2many('fee.computation', 'registration_id' ,'Fee Computation')
    
    @api.multi
    def write(self, vals):
        if 'discount_applicable_date' in vals and vals['discount_applicable_date']:
            discount_applicable_date_formatted = datetime.datetime.strptime(vals['discount_applicable_date'], "%Y-%m-%d").date()
            current_date = datetime.date.today()
            acd_yr_start_date = self.batch_id.start_date
            acd_yr_end_date = self.batch_id.end_date
            acd_yr_start_date_formatted = datetime.datetime.strptime(acd_yr_start_date, "%Y-%m-%d").date()
            acd_yr_end_date_formatted = datetime.datetime.strptime(acd_yr_end_date, "%Y-%m-%d").date()
            if discount_applicable_date_formatted < acd_yr_start_date_formatted and discount_applicable_date_formatted > acd_yr_end_date_formatted:
                raise except_orm(_('Warning!'), _("Discount Applicable Date should between academic year start date and end date "))
        return super(Registration, self).write(vals)
    

    
    @api.multi
    def generate_payable_fee_recs(self,flag):
        """
        this method used when student pay Academy fee manualy.
        after fee pay fee status will be changed as
        academy fee unpaid to fee paid.
        ------------------------------------------
        @param self : object pointer
        """
        sequence = 1
        if self.fee_structure_confirm!=True:
             raise except_orm(_("Warning!"), _('Please Confirm the fee structure before paying fee'))
        stud_payble_obj = self.env['student.payble.fee']

        if self.student_id:
            stud_payble_val = {}
            if self.fee_computation_ids :
                for fee_computation_line_rec in self.fee_computation_ids[0].fee_computation_line_ids:
                    if not fee_computation_line_rec.name.property_account_income_id.id:
                        raise except_orm(_("Warning!"), _('Please define property income account for fees %s') % fee_computation_line_rec.name.name)
                    stud_payble_rec = stud_payble_obj.search_count([('month_id','=',self.fee_computation_ids[0].month_id.id),
                                                                    ('name','=',fee_computation_line_rec.name.id),
                                                                    ('fee_pay_type','=',fee_computation_line_rec.fee_payment_type_id.id),
                                                                    ('student_id','=',self.student_id.id)])
                    if stud_payble_rec == 0:
                        stud_payble_val = {
                                'name': fee_computation_line_rec.name.id,
                                'student_id': self.student_id.id,
                                'month_id' : self.fee_computation_ids[0].month_id.id,
                                'fee_pay_type' : fee_computation_line_rec.fee_payment_type_id.id,
                                'cal_amount' : 0,
                                'total_amount' : fee_computation_line_rec.payable_amount,
                                'discount_amount' : 0,
                                }
                        stud_payble_obj.create(stud_payble_val)
            else :
                raise except_orm(_("Warning!"), _('Fee computation does not exists'))
                    
        else:
             raise except_orm(_("Warning!"), _('Student Not Found'))
        #raise except_orm(_("Warning!"), _('stop'))

    
    
    @api.multi
    def send_payfort_acd_for_next_year_computation(self):
        """
        This method is use when enquiry for next year.
        --------------------------------------------
        :return: It return record set.
        """
        next_year_advance_fee_obj = self.env['next.year.advance.fee']
        sequence = 1
        stud_payble_obj = self.env['student.payble.fee']
        next_year_advance_fee_line_data = []
        if not self.student_id.property_account_customer_advance.id:
            raise except_orm(_('Warning!'),
                    _("Please define student Advance Payment Account!"))

        for fee_computation_line_rec in self.student_id.fee_computation_ids[0].fee_computation_line_ids:
            next_year_advance_fee_line_data.append((0,0,{
                'name' : fee_computation_line_rec.name.id,
                'description' : fee_computation_line_rec.name.name,
                'account_id' : self.student_id.property_account_customer_advance.id,
                'priority' : sequence,
                'amount' : fee_computation_line_rec.calculated_amount,
                'rem_amount' : fee_computation_line_rec.calculated_amount,
            }))
            sequence += 1
            if fee_computation_line_rec.discount_percentage > 0.00 or fee_computation_line_rec.discount_amount > 0.00:
                if not fee_computation_line_rec.name.fees_discount:
                    raise except_orm(_("Warning!"), _('Please define Discount Fees for %s.')%(fee_computation_line_rec.name.name))
                else:
                    if not fee_computation_line_rec.name.fees_discount.property_account_income.id:
                        raise except_orm(_("Warning!"), _('Please define account Income for %s.')%(fee_computation_line_rec.name.fees_discount.name))
                    else:
                        next_year_advance_fee_line_data.append((0,0,{
                            'name' : fee_computation_line_rec.name.fees_discount.id,
                            'description' : fee_computation_line_rec.name.fees_discount.name,
                            'account_id' : self.student_id.property_account_customer_advance.id,
                            'priority' : 0,
                            'amount' : -(fee_computation_line_rec.discount_amount),
                            'rem_amount' : -(fee_computation_line_rec.discount_amount),
                        }))

        #check if NYAF already exists and state in unpaid or partially paid... if yes then update else create new
        #next_year_advance_fee_id = next_year_advance_fee_obj.search([('partner_id','=', self.student_id.id),('reg_id', '=', self.id),('batch_id', '=', self.batch_id.id),('state','in', ('fee_unpaid','fee_partial_paid'))])
        next_year_advance_fee_id = next_year_advance_fee_obj.search([('partner_id','=', self.student_id.id),('reg_id', '=', self.id),('batch_id', '=', self.batch_id.id),('state','in', ('fee_unpaid','fee_partial_paid','fee_paid'))])
        if next_year_advance_fee_id :
            for next_year_advance_fee_line_id in next_year_advance_fee_id.next_year_advance_fee_line_ids :
                if next_year_advance_fee_line_id.amount < 0:
                    next_year_advance_fee_line_id.unlink()
                else :
                    for next_year_advance_fee_line in next_year_advance_fee_line_data :
                        if next_year_advance_fee_line_id.name.id == next_year_advance_fee_line[2]['name'] :
                                next_year_advance_fee_line_id.amount = next_year_advance_fee_line[2]['amount']
                                next_year_advance_fee_line_id.rem_amount = next_year_advance_fee_line[2]['rem_amount']
                
            for next_year_advance_fee_line in next_year_advance_fee_line_data :
                if next_year_advance_fee_line[2]['amount'] < 0 :
                    next_year_advance_fee_id.write({'next_year_advance_fee_line_ids' : [next_year_advance_fee_line]})
            return next_year_advance_fee_id
        else : 
            next_year_advance_fee_data = {
                'partner_id' : self.student_id.id,
                'reg_id' : self.id,
                'enq_date' : self.application_date,
                'order_id' : '/',
                'batch_id' : self.batch_id.id,
                'state' : 'fee_unpaid',
                'next_year_advance_fee_line_ids' : next_year_advance_fee_line_data,
            }
            new_obj = next_year_advance_fee_obj.create(next_year_advance_fee_data)
            return new_obj



    
    @api.multi
    def send_payfort_acd_pay_link_computation(self):
        """
        this method used to send payfort link for
        online payment of student acd fee.
        ------------------------------------------
        @param self : object pointer
        @net_amount : calculated amount
        @dis_amount : discount amount on calculated amount
        @total_net_amount : total calculated amount - total discount
        """
        amount_on_link = 0.00
        if self._context.has_key('flag') and self._context.get('flag') == True:
            if self.fee_structure_confirm != True:
                raise except_orm(_("Warning!"), _('Please Confirm the fee structure before sending payment link.'))
            if self.invoice_id:
                order_id = self.invoice_id.invoice_number
                amount_on_link = self.invoice_id.residual
            elif self.next_year_advance_fee_id:
                order_id = self.next_year_advance_fee_id.order_id
                amount_on_link = self.next_year_advance_fee_id.residual
        else:
            if self.batch_id.current_academic != True:
                # create NYAF if not current academic year
                get_record = self.send_payfort_acd_for_next_year_computation()
                self.next_year_advance_fee_id = get_record.id
                order_id = get_record.order_id
            # generate payble fee records
            payable_fee_recs = self.generate_payable_fee_recs(True)

    @api.multi
    def compute_fee_structure(self):
        fee_computation_obj = self.env['fee.computation']
        fee_computation_line_obj = self.env['fee.computation.line']
        
        if self.student_id.fee_computation_ids :
            #remove previous years fee computation lines
            if self.student_id.fee_computation_ids :
                for fee_computation_rec in self.student_id.fee_computation_ids :
                    fee_computation_rec.unlink()
        #create new fee computation lines
        self.student_id.update_fee_structure()
        #create same lines to registration fee computation
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
                                        'registration_id' : self.id
                                    }
                fee_computation_id = fee_computation_obj.create(fee_computation_vals)
    
    
    @api.multi   
    def confirm_done_fee_structure_computation(self):
        self.compute_fee_structure()
        ###### Start : from confirm_done_fee_structure of edsys_edu/models/registration
        self.fee_structure_confirm = True
        # send mail for link to pay acd fee online
        # self.send_payfort_acd_pay_link()---------- old code
        self.send_payfort_acd_pay_link_computation()
        self.current_date_for_link = base64.b64encode(str(datetime.date.today()))
        # send mail for extra form fillup and genarate link for same,
        self.send_mail_for_extra_form_fillup()
        dumy_date = base64.b64encode('0000-00-00')
        self.remaining_form_link = '/student/verification?ENQUIRY=%s&DATE=%s'%(self.enquiry_no,dumy_date)
        self.confirm_fee_date = datetime.datetime.now()
        ###### End : from confirm_done_fee_structure of edsys_edu/models/registration
        #raise except_orm(_("Warning!"), _('stop'))
        
    @api.multi   
    def confirm_fee_structure(self):
        if self.student_id.fee_computation_ids :
            #remove previous years fee computation lines
            for fee_computation_rec in self.student_id.fee_computation_ids :
                fee_computation_rec.unlink()
        if self.fee_computation_ids :
            #remove previous years fee computation lines from registration
            for fee_computation_rec in self.fee_computation_ids :
                fee_computation_rec.unlink()
                
        res = super(Registration, self).confirm_fee_structure()
        if self.discount_applicable_date :
            discount_applicable_date_formatted = datetime.datetime.strptime(self.discount_applicable_date, "%Y-%m-%d").date()
            self.student_id.discount_applicable_date = discount_applicable_date_formatted
        
