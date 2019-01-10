from odoo import models, fields, api, _
import datetime
from odoo.exceptions import except_orm

class res_partner(models.Model):

    _inherit = 'res.partner'
    
    discount_applicable_date = fields.Date('Discount Applicable Date')
    fee_computation_ids = fields.One2many('fee.computation', 'partner_id' ,'Fee Computation')
    discount_history_ids = fields.One2many('discount.history' ,'partner_id' ,'Discount History')
    total_invoice_amount = fields.Float('Total Amount')
    
    @api.model
    def months_between(self,start_date,end_date):
        months = []
        month_year = []
        cursor = start_date

        while cursor <= end_date:
            if cursor.month not in months:
                months.append(cursor.month)
                month_year.append((int(cursor.month),int(cursor.year)))
            cursor += datetime.timedelta(weeks=1)
        return month_year
    
    
    @api.multi
    def get_fee_computation_line(self, partner):
        st_class = ''
        total_amount = 0.0
        student_id = ''
        name = ''
        year_id = ''
        class_id = ''
        student_section_id = ''
       
        parents1_id= ''
        parent_contact = ''
        parents_email = ''
       
        fee_computation_line =[]
        updated_fee_lines = []
        List_Of_Month = [
                                    [1,'January'],
                                    [2,'February'],
                                    [3,'March'],
                                    [4,'April'],
                                    [5,'May'],
                                    [6,'June'],
                                    [7,'July'],
                                    [8,'August'],
                                    [9,'September'],
                                    [10,'October'],
                                    [11,'November'],
                                    [12,'December'],
                                    ]
        
        status = {
                    'invoice_raised' : 'Invoice Raised',
                    'invoice_not_raised' : 'Invoice Not Raised',
                  }
                  
        
        invoice_lines = []
        obj_account_invoice = self.env['fee.computation']
        if partner:
            if partner.fee_computation_ids and len(partner.fee_computation_ids)>0:
                for fee_computation_id in partner.fee_computation_ids:
                
                    month_count = 0
                    month_date = 0
                    imvoice_count = 0
                    fee_computation_lines = []
                     
                    date = fee_computation_id.fee_date
                    
                    month_count = 0
                    month_date = 0
                    imvoice_count = 0
                    invoice_state_count = 0
                    student_di = 0
                    name_id = 0
                    year_di = 0
                    class_di = 0
                    student_section_di = 0
                    parent1_di = 0
                    parents1_di = 0
                    parent_contact_num = 0
                    parents_email_add = 0
                    
                    fee_computation_line = []
                    month = List_Of_Month[fee_computation_id.month_id.name - 1][1]
                    student_id = partner.student_id
                    name = partner.name
                    year_id = partner.year_id
                    class_id = partner.class_id 
                    student_section_id = partner.student_section_id
                    parents1_id = partner.parents1_id
                    parents1_id = partner.parents1_id
                    parent_contact = partner.parent_contact
                    parents_email = partner.parents_email
                    
                    for computed_invoice_line in fee_computation_id.fee_computation_line_ids:
                        invoice_line = []
                        fee_computation_lines = []
                        invoice_line.append(computed_invoice_line.name.name)
                        invoice_line.append(computed_invoice_line.calculated_amount)
                        invoice_line.append(fee_computation_id.discount_category_id.name)
                        invoice_line.append(computed_invoice_line.discount_percentage)
                        invoice_line.append(computed_invoice_line.discount_amount)
                        invoice_line.append(computed_invoice_line.payable_amount)
                       
                        amount = ''
                        discount_name = ''
                        discount = ''
                        dicount_percentage = ''
                        cal_amount = fee_computation_id.total_calculated_amount
                        invoice_amount = fee_computation_id.invoice_amount
                        invoice_status = status[fee_computation_id.status]
                        
                        fee_computation_lines.append(student_id)
                        fee_computation_lines.append(name)
                        fee_computation_lines.append(year_id.name)
                        fee_computation_lines.append(class_id.name)
                        fee_computation_lines.append(student_section_id.name)
                        fee_computation_lines.append(parents1_id.parent1_id)
                        fee_computation_lines.append(parents1_id.name)
                        fee_computation_lines.append(parents_email)
                        fee_computation_lines.append(parent_contact)
                        fee_computation_lines.append(date)
                        fee_computation_lines.append(month)
                        if bool(invoice_line):
                            fee_computation_lines.append(invoice_line)
                        fee_computation_lines.append(invoice_amount)
                        fee_computation_lines.append(invoice_status)
                        if bool(fee_computation_lines):
                            fee_computation_line.append(fee_computation_lines)
                        
                    if len(fee_computation_line)> 0:
                        for fee_computation_line_id in fee_computation_line:
                            if month == fee_computation_line_id[10]:
                                if month_count > 0:
                                    fee_computation_line_id[10] = ''
                                month_count += 1
                             
                            if date == fee_computation_line_id[9]:
                                if month_date > 0:
                                    fee_computation_line_id[9] = ''
                                month_date += 1
                                
                            #print fee_computation_line_id[12],'===========fee_computation_line_id[12]'
                            if invoice_amount == fee_computation_line_id[12]:
                                if imvoice_count > 0:
                                    fee_computation_line_id[12] = ''
                                if imvoice_count == 0:
                                    total_amount+= invoice_amount
                                imvoice_count += 1
                                
                            if invoice_status == fee_computation_line_id[13]:
                                if invoice_state_count > 0:
                                    fee_computation_line_id[13] = ''
                                invoice_state_count += 1
                            
                            if student_id == fee_computation_line_id[0]:
                                if student_di > 0:
                                    fee_computation_line_id[0] = ''
                                student_di += 1
                                
                            if name == fee_computation_line_id[1]:
                                if name_id > 0:
                                    fee_computation_line_id[1] = ''
                                name_id += 1
                            
                            if year_id.name == fee_computation_line_id[2]:
                                if year_di > 0:
                                    fee_computation_line_id[2] = ''
                                year_di += 1
                            
                            if class_id.name == fee_computation_line_id[3]:
                                if class_di > 0:
                                    fee_computation_line_id[3] = ''
                                class_di += 1
                            
                            if student_section_id.name == fee_computation_line_id[4]:
                                if student_section_di > 0:
                                    fee_computation_line_id[4] = ''
                                student_section_di += 1
                            
                            if parents1_id.parent1_id == fee_computation_line_id[5]:
                                if parent1_di > 0:
                                    fee_computation_line_id[5] = ''
                                parent1_di += 1
                            
                            if parents1_id.name == fee_computation_line_id[6]:
                                if parents1_di > 0:
                                    fee_computation_line_id[6] = ''
                                parents1_di += 1
                            
                            if parents_email == fee_computation_line_id[7]:
                                if parents_email_add > 0:
                                    fee_computation_line_id[7] = ''
                                parents_email_add += 1
                           
                            if parent_contact == fee_computation_line_id[8]:
                                if parent_contact_num > 0:
                                    fee_computation_line_id[8] = ''
                                parent_contact_num += 1
                                
                                
                            
                    if bool(fee_computation_line):
                        updated_fee_lines.append(fee_computation_line)
                self.total_invoice_amount = total_amount
        return updated_fee_lines

    @api.multi
    def write(self, vals):
        discount_history_obj = self.env['discount.history']
        current_date = datetime.date.today()
        discount_applicable_date_formatted =False
        if 'discount_applicable_date' in vals and vals['discount_applicable_date']:
            discount_applicable_date = vals['discount_applicable_date']
            discount_applicable_date_formatted = datetime.datetime.strptime(vals['discount_applicable_date'], "%Y-%m-%d").date()
            acd_yr_start_date = self.year_id.start_date
            acd_yr_start_date_formatted = datetime.datetime.strptime(str(acd_yr_start_date), "%Y-%m-%d").date()
            acd_yr_end_date = self.year_id.end_date
            acd_yr_end_date_formatted = datetime.datetime.strptime(str(acd_yr_end_date), "%Y-%m-%d").date()
            if discount_applicable_date_formatted <= acd_yr_start_date_formatted and discount_applicable_date_formatted >= acd_yr_end_date_formatted:
                raise except_orm(_('Warning!'), _("Discount Applicable Date should between academic year start date and end date "))
        elif self.discount_applicable_date :
            discount_applicable_date_formatted = datetime.datetime.strptime(self.discount_applicable_date, "%Y-%m-%d").date()
        
        if 'year_id' in vals and vals['year_id']:
            academic_year_id = vals['year_id']
        else :
            academic_year_id = self.year_id.id
        
        if 'discount_on_fee' in vals :
            discount_on_fee = vals['discount_on_fee']
            if discount_on_fee :
                action_type = 'applied'
            else :
                discount_on_fee = self.discount_on_fee.id
                action_type = 'removed'
            discount_history_vals = {
                                        'discount_category_id' : discount_on_fee,
                                        'action_type' : action_type,
                                        'action_date' : current_date,
                                        'applied_by' : self.env.uid,
                                        'applicable_from_date' : discount_applicable_date_formatted,
                                        'academic_year_id' : academic_year_id,
                                        'is_applicable' : False,
                                        'partner_id' : self.id
                                     }
            
            vals['discount_history_ids'] = [(0,0, discount_history_vals)]
        return super(res_partner, self).write(vals)
    

    @api.multi
    def calculate_monthly_fee(self, student_fee_line, fee_computation_rec_list):
        fee_computation_line_obj = self.env['fee.computation.line']
        total_prev_calculated_amount = 0
        for fee_computation_rec in fee_computation_rec_list :
            calculate_monthly =  False
            discount_amount = 0.00
            discount_percentage = 0.00
	    print len(fee_computation_rec_list),'==============len(fee_computation_rec_list)'
	    print student_fee_line.amount,'========================student_fee_line.amount'
            total_amt = student_fee_line.amount / len(fee_computation_rec_list)
	    print total_amt,'================total_amt'
            if fee_computation_rec.discount_category_id :
                discount_percentage = student_fee_line.discount
                discount_amount = (student_fee_line.discount_amount)/ len(fee_computation_rec_list)
            payable_amt = total_amt -  discount_amount
            if fee_computation_rec.fee_computation_line_ids :
                fee_computation_line_exists = fee_computation_rec.fee_computation_line_ids.search([('fee_computation_id','=',fee_computation_rec.id), ('name','=', student_fee_line.name.id)])
                if fee_computation_line_exists :
                    if fee_computation_rec.status == 'invoice_raised' :
                        #get diff amount
                        prev_calculated_amount = total_amt - fee_computation_line_exists.calculated_amount
                        total_prev_calculated_amount += prev_calculated_amount
                    else :
                        total_amt = total_amt + total_prev_calculated_amount
                        payable_amt = total_amt -  discount_amount
                        fee_computation_line_exists.calculated_amount = round(total_amt)
                        fee_computation_line_exists.discount_amount = round(discount_amount)
                        fee_computation_line_exists.payable_amount = round(payable_amt)
                        fee_computation_line_exists.discount_percentage = discount_percentage
                        total_prev_calculated_amount = 0
                else :
                    calculate_monthly = True
            else :
                calculate_monthly = True
            if calculate_monthly :
                monthly_vals = {
                                    'name' : student_fee_line.name.id,
                                    'calculated_amount' : round(total_amt),
                                    'discount_percentage' : discount_percentage,
                                    'discount_amount' : round(discount_amount),
                                    'payable_amount' : round(payable_amt),
                                    'fee_payment_type_id' : student_fee_line.fee_pay_type.id,
                                    'fee_computation_id' : fee_computation_rec.id
                                }
                fee_computation_line_obj.create(monthly_vals)
        
    @api.multi 
    def calculate_yearly_fee(self, student_fee_line, fee_computation_rec_list):
        fee_computation_line_obj = self.env['fee.computation.line']
        diff_calculated_amount = 0
        is_yearly_calculated =  False
        discount_amount = 0.00
        discount_percentage = 0.00
        if self.fee_computation_ids[0].fee_computation_line_ids :
            fee_computation_line_exists = self.fee_computation_ids[0].fee_computation_line_ids.search([('fee_computation_id','=',fee_computation_rec_list[0].id), ('name','=', student_fee_line.name.id)])
            if self.fee_computation_ids[0].discount_category_id :
                discount_percentage = student_fee_line.discount
                discount_amount = student_fee_line.discount_amount 
            payable_amount = student_fee_line.amount - discount_amount
            if fee_computation_line_exists :
                if self.fee_computation_ids[0].status == 'invoice_raised' :
                    diff_calculated_amount = student_fee_line.amount - fee_computation_line_exists.calculated_amount
                    if diff_calculated_amount != 0 :
                        is_yearly_calculated = False
                    else :
                        is_yearly_calculated = True
                else :
                    fee_computation_line_exists.calculated_amount = round(student_fee_line.amount)
                    fee_computation_line_exists.discount_amount = round(discount_amount)
                    fee_computation_line_exists.payable_amount = round(payable_amount)
                    is_yearly_calculated = True
        if not is_yearly_calculated :               
            invoice_not_raised_recs = self.fee_computation_ids.search([('status','=', 'invoice_not_raised'), ('partner_id','=', self.id)])
            if invoice_not_raised_recs :
                invoice_not_raised_rec = invoice_not_raised_recs[0]
                if invoice_not_raised_rec.discount_category_id :
                    discount_percentage = student_fee_line.discount
                    discount_amount = student_fee_line.discount_amount 
                if diff_calculated_amount != 0 :
                    payable_amount = diff_calculated_amount - discount_amount
                    calculated_amount = diff_calculated_amount
                else :
                    payable_amount = student_fee_line.amount - discount_amount 
                    calculated_amount = student_fee_line.amount
                yearly_vals = {
                                'name' : student_fee_line.name.id,
                                'calculated_amount' : round(calculated_amount),
                                'discount_percentage' : discount_percentage,
                                'discount_amount' : round(discount_amount ),
                                'payable_amount' : round(payable_amount),
                                'fee_payment_type_id' : student_fee_line.fee_pay_type.id,
                                'fee_computation_id' : invoice_not_raised_rec.id
                            }
                fee_computation_line_obj.create(yearly_vals)
    
    @api.multi 
    def calculate_termly_fee(self, student_fee_line, fee_computation_id_list):
        calculate_term_fee = False
        acd_term_obj = self.env['acd.term']
        fee_computation_line_obj = self.env['fee.computation.line']
        acd_term_list = []
        term_no_month = 0
        discount_percentage = 0
        discount_amount = 0
        total_prev_calculated_amount = 0
        acd_term_recs = acd_term_obj.search([('batch_id','=', self.year_id.id)])
        for acd_term_rec in acd_term_recs :
            acd_term_start_date = datetime.datetime.strptime(acd_term_rec.start_date, "%Y-%m-%d").date()
            acd_term_end_date = datetime.datetime.strptime(acd_term_rec.end_date, "%Y-%m-%d").date()
            fee_date = datetime.datetime.strptime(fee_computation_id_list[0].fee_date, "%Y-%m-%d").date()
            if acd_term_start_date <= fee_date <= acd_term_end_date:
                acd_term_start_date = fee_date
                term_no_month = len(self.months_between(fee_date, acd_term_end_date))
            elif acd_term_start_date >= fee_date:
                term_no_month = len(self.months_between(acd_term_start_date, acd_term_end_date))
            if term_no_month > 0 :
                for fee_computation_id in fee_computation_id_list :
                    fee_computation_term_rec = fee_computation_id.search([('partner_id','=', self.id), ('fee_date','=',acd_term_start_date )])
                if fee_computation_term_rec :
                    total_amt = (student_fee_line.amount / len(fee_computation_id_list) ) * term_no_month
                    if fee_computation_term_rec.discount_category_id :
                        discount_percentage = student_fee_line.discount
                        discount_amount = ((student_fee_line.discount_amount)/len(fee_computation_id_list) ) * term_no_month
                    payable_amt = total_amt - discount_amount
                    if fee_computation_term_rec.fee_computation_line_ids :
                        fee_computation_line_exists = fee_computation_term_rec.fee_computation_line_ids.search([('fee_computation_id','=',fee_computation_term_rec.id), ('name','=', student_fee_line.name.id)])
                        if fee_computation_line_exists :
                            if fee_computation_term_rec.status == 'invoice_raised' :
                                prev_calculated_amount = total_amt - fee_computation_line_exists.calculated_amount
                                total_prev_calculated_amount += prev_calculated_amount
                            else :
                                total_amt = total_amt + total_prev_calculated_amount
                                payable_amt = total_amt -  discount_amount
                                fee_computation_line_exists.calculated_amount = round(total_amt)
                                fee_computation_line_exists.discount_amount = round(discount_amount)
                                fee_computation_line_exists.payable_amount = round(payable_amt)
                                fee_computation_line_exists.discount_percentage = discount_percentage
                                total_prev_calculated_amount = 0
                        else :
                            calculate_term_fee = True
                    else :
                        calculate_term_fee = True
                    if calculate_term_fee :
                        termly_vals = {
                                            'name' : student_fee_line.name.id,
                                            'calculated_amount' : round(total_amt),
                                            'discount_percentage' : discount_percentage,
                                            'discount_amount' : round(discount_amount),
                                            'payable_amount' : round(payable_amt),
                                            'fee_payment_type_id' : student_fee_line.fee_pay_type.id,
                                            'fee_computation_id' : fee_computation_term_rec.id
                                        }
                        fee_computation_line_obj.create(termly_vals)
                        
    @api.multi 
    def calculate_half_yearly_fee(self, student_fee_line, fee_computation_id_list):
        first_half_month_list = []
        second_half_month_list = []
        leave_month_list = []
        first_fee_date = False
        second_fee_date = False
        calculate_half_yr_fee = False
        total_amt = 0
        discount_percentage = 0
        discount_amount = 0
        total_prev_calculated_amount = 0
        fee_computation_line_obj = self.env['fee.computation.line']
        half_month_recs = self.year_id.month_ids.search([('batch_id','=',self.year_id.id),
                                                    ('leave_month','=',False),
                                                    ('quater_month','=',True)])
        first_half_date = self.first_day_of_month(int(half_month_recs[0].name),int(half_month_recs[0].year))
        second_half_date = self.first_day_of_month(int(half_month_recs[1].name),int(half_month_recs[1].year))
        fee_date_first_month = datetime.datetime.strptime(fee_computation_id_list[0].fee_date, "%Y-%m-%d").date()
        acd_yr_end_date = datetime.datetime.strptime(self.year_id.end_date, "%Y-%m-%d").date()
        for l_month in self.year_id.month_ids.search([('batch_id', '=', self.year_id.id), ('leave_month', '=', True)]):
                leave_month_list.append((int(l_month.name), int(l_month.year)))   
        if first_half_date <= fee_date_first_month <= second_half_date :
            first_half_month_list = self.months_between(fee_date_first_month,second_half_date)
            first_fee_date = fee_date_first_month
        elif second_half_date <= fee_date_first_month < acd_yr_end_date:
            second_half_month_list = self.months_between(fee_date_first_month,acd_yr_end_date)
            second_fee_date = fee_date_first_month
        if first_half_month_list :
            second_half_month_list = self.months_between(second_half_date,acd_yr_end_date)
            second_fee_date = second_half_date
            if leave_month_list :
                for leave_month in leave_month_list :
                    if leave_month in first_half_month_list:
                        first_half_month_list.remove(leave_month)
        if second_half_month_list :
            for leave_month in second_half_month_list :
                if leave_month in first_half_month_list:
                    second_half_month_list.remove(leave_month)
        
        for fee_computation_rec in fee_computation_id_list :
            fee_rec = False
            half_yr_month_count = 0
            fee_date = datetime.datetime.strptime(fee_computation_rec.fee_date, "%Y-%m-%d").date()
            if first_fee_date :
                if fee_date == first_fee_date :
                    fee_rec = fee_computation_rec
                    half_yr_month_count = len(first_half_month_list)
            if second_fee_date :
                if fee_date == second_fee_date :
                    fee_rec = fee_computation_rec
                    half_yr_month_count = len(second_half_month_list)
            if half_yr_month_count > 0 and fee_rec :
                total_amt = (student_fee_line.amount / len(fee_computation_id_list)) * half_yr_month_count
                if fee_computation_rec.discount_category_id :
                    discount_percentage = student_fee_line.discount
                    discount_amount = ((student_fee_line.discount_amount)/len(fee_computation_id_list))* half_yr_month_count
                payable_amt = total_amt - discount_amount
                if fee_computation_rec.fee_computation_line_ids :
                    fee_computation_line_exists = fee_computation_rec.fee_computation_line_ids.search([('fee_computation_id','=', fee_rec.id), ('name','=', student_fee_line.name.id)])
                    if fee_computation_line_exists :
                        if fee_computation_rec.status == 'invoice_raised' :
                            prev_calculated_amount = total_amt - fee_computation_line_exists.calculated_amount
                            total_prev_calculated_amount += prev_calculated_amount
                        else :
                            total_amt = total_amt + total_prev_calculated_amount
                            payable_amt = total_amt -  discount_amount
                            fee_computation_line_exists.calculated_amount = round(total_amt)
                            fee_computation_line_exists.discount_amount = round(discount_amount)
                            fee_computation_line_exists.payable_amount = round(payable_amt)
                            fee_computation_line_exists.discount_percentage = discount_percentage
                            total_prev_calculated_amount = 0
                    else :
                        calculate_half_yr_fee = True
                else :
                    calculate_half_yr_fee = True
                if calculate_half_yr_fee :
                    half_yearly_vals = {
                                        'name' : student_fee_line.name.id,
                                        'calculated_amount' : round(total_amt),
                                        'discount_percentage' : discount_percentage,
                                        'discount_amount' : round(discount_amount),
                                        'payable_amount' : round(payable_amt),
                                        'fee_payment_type_id' : student_fee_line.fee_pay_type.id,
                                        'fee_computation_id' : fee_computation_rec.id
                                    }
                    fee_computation_line_obj.create(half_yearly_vals)
        
        #raise except_orm(_("Warning!"), _('stop'))
    
    
    @api.model
    def first_day_of_month(self,month,year):
        """
        getting first date of month
        -----------------------------------
        :param month:
        :param year:
        :return: first date of invoice
        """
        return datetime.date(year, month, 1)
    
    def get_person_age(self,date_birth, date_today):
        """
        At top level there are three possibilities : Age can be in days or months or years.
        For age to be in years there are two cases: Year difference is one or Year difference is more than 1
        For age to be in months there are two cases: Year difference is 0 or 1
        For age to be in days there are 4 possibilities: Year difference is 1(20-dec-2012 - 2-jan-2013),
        ----------------------------------------------------------------------------------------------------
        :param date_birth: Birth Date
        :param date_today: Current Date
        :return: Dictonary
        """
        years_diff = date_today.year - date_birth.year

        months_diff = 0
        if date_today.month >= date_birth.month:
            months_diff = date_today.month - date_birth.month
        else:
            years_diff -= 1
            months_diff = 12 + (date_today.month - date_birth.month)

        days_diff = 0
        if date_today.day >= date_birth.day:
            days_diff = date_today.day - date_birth.day
        else:
            months_diff -= 1
            days_diff = 31 + (date_today.day - date_birth.day)

        if months_diff < 0:
            months_diff = 11
            years_diff -= 1

        age = years_diff
        age_dict = {
            'years' : years_diff,
            'months' : months_diff,
            'days' : days_diff
        }
        return age_dict



    @api.multi
    def update_fee_structure(self):
        super(res_partner, self).update_fee_structure()
        fee_payment_obj = self.env['fee.payment']
        fee_month_obj = self.env['fee.month']
        acd_term_obj = self.env['acd.term']
        registration_obj = self.env['registration']
        fee_computation_obj = self.env['fee.computation']
        fee_computation_line_obj = self.env['fee.computation.line']
        discount_history_obj = self.env['discount.history']
        promote_student_line_obj = self.env['promote.student.line']
        
        is_calculate_term_fee =  False
        is_yearly_calculated = False
        is_first_half = True
        is_first_month_yearly = True
        is_first_month_termly = True
        is_first_half_calculated = False
        discount_applicable_date  = False
        is_discount_applicable = False
        discount_applicable_date_formatted = False
        exists_fee_computation_rec = False
        
        half_year_month_count = 0
        total_diff_calculated_amount = 0
        total_diff_discount_amount = 0.00
        total_diff_payable_amount = 0.00
        
        leave_month_list = []
        fee_computation_id_list = []
        fee_computation_id_student_list = []
        fee_computation_line_ids_list = []
        
        for l_month in self.year_id.month_ids.search([('batch_id', '=', self.year_id.id),
                                                               ('leave_month', '=', True)]):
            leave_month_list.append((int(l_month.name), int(l_month.year)))     
    	#print self.admission_date,'=================self.admission_date'
	
	#print type(self.admission_date),'=======type==========self.admission_date'    
        admission_date = datetime.datetime.strptime(str(self.admission_date), "%Y-%m-%d").date()
        acd_yr_start_date = datetime.datetime.strptime(str((self.year_id.start_date)), "%Y-%m-%d").date()
        acd_yr_end_date = datetime.datetime.strptime((self.year_id.end_date), "%Y-%m-%d").date()
        if acd_yr_start_date <= admission_date <= acd_yr_end_date:
            cal_date = admission_date
        else:
            cal_date = acd_yr_start_date
        get_unpaid_diff = self.get_person_age(cal_date, acd_yr_end_date)
        joining_to_end_months = self.months_between(cal_date, acd_yr_end_date)
        for leave_month in leave_month_list :
            if leave_month in joining_to_end_months:
                joining_to_end_months.remove(leave_month)
        if self.discount_applicable_date :
            if self.discount_history_ids :
                discount_applicable_date_formatted = datetime.datetime.strptime(self.discount_applicable_date, "%Y-%m-%d").date()
                self.discount_history_ids[-1].is_applicable = True
                self.discount_history_ids[-1].applicable_from_date = discount_applicable_date_formatted
                for discount_history_rec in self.discount_history_ids :
                    if discount_history_rec.is_applicable == False :
                        discount_history_rec.unlink()
                self.discount_history_ids[-1].sr_no = len(self.discount_history_ids )
            
        
        for joining_to_end_month in joining_to_end_months :
            discount_on_fee = False
            fee_computation_exists = False
            fee_computation_ids_exists =  False
            fee_month_rec = fee_month_obj.search([('name', '=', joining_to_end_month[0]),('year', '=', joining_to_end_month[1]), ('batch_id', '=', self.batch_id.id)])
            fee_date = self.first_day_of_month(int(fee_month_rec.name), int(fee_month_rec.year))
            if joining_to_end_month == joining_to_end_months[0] :
                if admission_date > fee_date :
                    fee_date = admission_date
            if discount_applicable_date_formatted :
		 print discount_applicable_date_formatted,'==============discount_applicable_date_formatted'
	         print fee_date,'=============fee_date'
                 if fee_date >= discount_applicable_date_formatted :
                    is_discount_applicable = True
            if is_discount_applicable :
                discount_on_fee = self.discount_on_fee.id
            if self.fee_computation_ids :
                fee_computation_exists = self.fee_computation_ids.search([('partner_id', '=', self.id), ('month_id','=', fee_month_rec.id )])
            if not fee_computation_exists :
                fee_computation_vals = {
                                           'month_id' : fee_month_rec.id,
                                           'fee_date' : fee_date,
                                           'discount_category_id' : discount_on_fee, 
                                           'status' : 'invoice_not_raised',
                                           'partner_id' : self.id,
                                       }
                fee_computation_id = fee_computation_obj.create(fee_computation_vals)
                fee_computation_id_list.append(fee_computation_id)
            else :
                if fee_computation_exists.status == 'invoice_not_raised' :
		    print '=============eror'
		    print fee_date,'===============1111111111==fee_date'
		    print discount_applicable_date_formatted,'====222====discount_applicable_date_formatted'
		    if fee_date and discount_applicable_date_formatted:
                    	if fee_date >= discount_applicable_date_formatted :
                        	fee_computation_exists.discount_category_id = discount_on_fee
                fee_computation_id_list.append(fee_computation_exists)
                
        for student_fee_line in self.student_fee_line :
            yearly_payable_amount = 0.00
            yearly_calculated_amount = 0.00
            if student_fee_line.fee_pay_type.name == 'month' :
                monthly_vals = self.calculate_monthly_fee(student_fee_line, fee_computation_id_list)
            if student_fee_line.fee_pay_type.name == 'year' or student_fee_line.fee_pay_type.name == 'one':
                yearly_vals = self.calculate_yearly_fee(student_fee_line, fee_computation_id_list)
            if student_fee_line.fee_pay_type.name == 'term' :
                termly_vals = self.calculate_termly_fee(student_fee_line, fee_computation_id_list)
            if student_fee_line.fee_pay_type.name == 'half_year' :
                half_yearly_vals = self.calculate_half_yearly_fee(student_fee_line, fee_computation_id_list)
        
        for fee_computation_rec in self.fee_computation_ids :
            fee_computation_rec.invoice_amount = 0.00
            fee_computation_rec.total_discount_amount = 0.00
            fee_computation_rec.total_calculated_amount = 0.00
            for fee_computation_line_rec in fee_computation_rec.fee_computation_line_ids :
                fee_computation_rec.total_calculated_amount += fee_computation_line_rec.calculated_amount
                fee_computation_rec.total_discount_amount += fee_computation_line_rec.discount_amount
                fee_computation_rec.invoice_amount += fee_computation_line_rec.payable_amount
                
        
