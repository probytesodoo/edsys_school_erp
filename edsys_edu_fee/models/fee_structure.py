import time
from odoo import models, fields, api, _
from datetime import date,datetime,timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
import math

class Fees_Line(models.Model):
    """
    Fees Lines
    """
    _name = 'fees.line'
    _description = 'Fees Line'

    name = fields.Many2one('product.product','Name',required=True)
    sequence = fields.Integer('Priority')
    amount = fields.Float('Amount',required=True)
    reg_id = fields.Many2one('registration', string='Registrations', invisible=True)
    reg_form_id = fields.Many2one('registration', string='Registrations Form', invisible=True)
    type=fields.Selection([('required','Required'),('optional','optional')])
    fees_id=fields.Many2one('fees.structure','Fees')
    fee_pay_type = fields.Many2one('fee.payment.type',string="Fee Payment Type")
    stud_id = fields.Many2one('res.partner','Student id')
    next_term = fields.Many2one('acd.term',string="Next Term")
    update_amount = fields.Float(string='Update Amount')
    discount = fields.Float(string="Discount(%)")
    discount_amount = fields.Float(string='Discount Amount')
    amount_from_percentage = fields.Float(string='Update Amount In Percentage(%)')

    @api.onchange('name')
    def on_addimition_fee(self):
        if self.name.is_admission_fee == True:
            one_type = self.env['fee.payment.type'].search([('name','=','one')])
            if one_type.id:
                self.fee_pay_type = one_type.id

    @api.onchange('update_amount')
    def get_update_percentage(self):
        if self.update_amount > 0 and self.amount > 0 :
            self.amount_from_percentage = (self.update_amount/self.amount)*100

            print 'hghfkkkkkkk'
    
#     @api.onchange('amount_from_percentage')
#     def get_update_amount(self):
#         # if self.amount_from_percentage >= 0 and self.amount_from_percentage <= 100:
#         if self.amount_from_percentage > 0:
#             self.update_amount = (self.amount*self.amount_from_percentage)/100
        

    @api.onchange('amount_from_percentage')
    def get_update_amount(self):
        # if self.amount_from_percentage >= 0 and self.amount_from_percentage <= 100:
        if self.amount_from_percentage > 0:
            pass
 
#             self.update_amount = round((self.amount*(self.amount_from_percentage))/100)
 
            print "vhhgjghhhhhhh"
        # else:
        #     raise except_orm(_('Warning!'),_("please enter valid Update Percentage(%)."))

    @api.onchange('discount')
    def onchange_discount(self):
        if self.discount > 100.0 or self.discount < 0.0:
            self.discount = 0.00
            raise except_orm(_('Warning!'),_("please enter valid discount(%)."))

    @api.model
    def create(self,vals):
        if 'discount' in vals:
            if vals['discount'] > 100.0 or vals['discount'] < 0.0:
                raise except_orm(_('Warning!'),_("please enter valid discount(%)."))
        return super(Fees_Line, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'update_amount' not in vals and 'amount' in vals:
            vals['amount'] = self.amount
            raise except_orm(_('Warning!'),
                    _("You can not update amount directly from hear !, please use Update Amount and Update button"))

        # discount change then discount amount calculation
        if 'discount' in vals:
            if vals['discount'] > 100.0 or vals['discount'] < 0.0:
                raise except_orm(_('Warning!'),_("please enter valid discount(%)."))
            else:
                if self.amount > 0.0 and 'discount_amount' not in vals:
                    vals['discount_amount'] = (self.amount * vals['discount'])/100

        # discount amount change then discount calculation
        if 'discount_amount' in vals and vals['discount_amount'] >= 0.0:
            if self.amount > 0.0 and 'discount' not in vals:
                vals['discount'] = (vals['discount_amount']*100)/self.amount

        return super(Fees_Line, self).write(vals)

    @api.model
    def default_get(self, fields):
        """
        this method is use for default set value when create new record.
        :param fields:
        :return:
        """
        res = super(Fees_Line, self).default_get(fields)
        # record update only when student_id get from Context
        if 'student_id' in self._context and self._context['student_id']:
            res.update({'stud_id': self._context['student_id']})
        return res

    @api.multi
    def unlink(self):
        """
        This Method is call, when we delete record.
        ------------------------------------------
        :return:
        """
        # add validation for record delation time
        for each in self:
            if each.type=='required' and each.reg_form_id:
                raise except_orm(_('Warning!'),
                    _("You cant delete the required fees lines!"))
        res=super(Fees_Line,self).unlink()
        return res

    @api.model
    def get_month_difference(self,start_date, date_today):
        """
        """
        years_diff = date_today.year - start_date.year

        months_diff = 0
        if date_today.month >= start_date.month:
            months_diff = date_today.month - start_date.month
        else:
            years_diff -= 1
            months_diff = 12 + (date_today.month - start_date.month)

        days_diff = 0
        if date_today.day >= start_date.day:
            days_diff = date_today.day - start_date.day
        else:
            months_diff -= 1
            days_diff = 31 + (date_today.day - start_date.day)

        if months_diff < 0:
            months_diff = 11
            years_diff -= 1

        age = years_diff
        month_dict = {
            'years' : years_diff,
            'months' : months_diff,
            'days' : days_diff
        }
        return month_dict

    @api.model
    def months_between(self,start_date,end_date):
        months = []
        month_year = []
        cursor = start_date

        while cursor <= end_date:
            if cursor.month not in months:
                months.append(cursor.month)
                month_year.append((int(cursor.month),int(cursor.year)))
            cursor += timedelta(weeks=1)
        return month_year

    @api.multi
    def update_fee_amount(self):
        """
        this method use to update student fee,
        --> update old fee amount with new fee amount,
        --> when fee update then generate history,
        --> update fee amount in student structure,
        --> update remaining fee amount in student fee paid detail,
        --> again calculation of fee as per new fee structure,
        --------------------------------------------------------
        @param self : object pointer
        """
        student_obj = self.env['res.partner']
        if self.update_amount == 0.00:
            raise except_orm(_('Warning!'),
                    _("please mention update amount value : (%s)") % (self.update_amount))
        else:
            if self.amount == self.update_amount:
                raise except_orm(_('No Update!'),
                    _("Fee amount %s and Update fee amount %s are same.") % (self.amount,self.update_amount))

            # genarate fees history
            sequence = self.fees_id.fee_history_line.search_count([('fee_structure_id','=',self.fees_id.id)])

            fee_history_line = {
                'sequence': sequence + 1,
                'name' : self.name.id,
                'old_amount': self.amount,
                'new_amount': self.update_amount,
                'date': date.today(),
                'fee_structure_id' : self.fees_id.id,
                }
            self.fees_id.fee_history_line = [(0, 0, fee_history_line)]

            # update student fee structure
            unpaid_diff = {}
            for stud_rec in student_obj.search([('is_parent', '=', False), ('course_id', '=', self.fees_id.course_id.id),
                                               ('batch_id', '=', self.fees_id.academic_year_id.id)]):
                if stud_rec.admission_date:
                    joining_date = datetime.strptime(stud_rec.admission_date,"%Y-%m-%d").date()
                    start_date = datetime.strptime(self.fees_id.academic_year_id.start_date,"%Y-%m-%d").date()
                    # end_date= datetime.strptime(self.fees_id.academic_year_id.end_date,"%Y-%m-%d").date()
                    # total_diff = self.get_month_difference(start_date,end_date)
                    total_month = self.fees_id.academic_year_id.month_ids.search_count([('batch_id','=',self.fees_id.academic_year_id.id),
                                                                                        ('leave_month','=',False)])
                    leave_month = []
                    for l_month in self.fees_id.academic_year_id.month_ids.search([('batch_id','=',self.fees_id.academic_year_id.id),
                                                                                        ('leave_month','=',True)]):
                        leave_month.append((int(l_month.name),int(l_month.year)))
                    month_in_stj = self.months_between(start_date,joining_date)
                    unpaid_diff = self.get_month_difference(start_date,joining_date)

                for fee_structure_rec in stud_rec.student_fee_line.search([('stud_id','=',stud_rec.id),
                                                                           ('name','=',self.name.id)],limit=1):
                    new_amount = self.update_amount
                    if fee_structure_rec.fee_pay_type.name not in ['one']:
                        if unpaid_diff and (unpaid_diff.get('months') > 0 or unpaid_diff.get('days') > 0):
                            unpaid_month = float(unpaid_diff.get('months'))
                            # if unpaid_diff.get('days') > 0:
                            #     unpaid_month += 1
                            if len(month_in_stj) > 0 and len(leave_month) > 0:
                                for leave_month_year in leave_month:
                                    if leave_month_year in month_in_stj:
                                        unpaid_month -= 1
                            if unpaid_month > 0.00 and total_month > 0.00:
                                unpaid_amount = (new_amount * unpaid_month) / total_month
                                new_amount -= unpaid_amount
                    if fee_structure_rec.id:
                        fee_structure_rec.write({'update_amount' : 0.00,'amount' : round(new_amount,2)})
                for fee_detail in stud_rec.payble_fee_ids.search([('name','=',self.name.id),
                                                                  ('student_id','=',stud_rec.id)]):
                    if fee_detail.id:
                        fee_detail.total_amount = round(new_amount,2)
                stud_rec.update_fee_structure()
            # update on Fee master line
            val = {
                    'update_amount' : 0.00,
                    'amount_from_percentage':0.0,
                    'amount' : self.update_amount,
                 }
            self.write(val)
        return True

#    @api.model
#    def create(self, vals):
#        if 'fees_id' in vals:
#            fees_id=vals['fees_id']
#            fees_obj=self.env['fees.structure'].browse(fees_id)
#            start_date=fees_obj.academic_year_id.start_date
#            end_date=fees_obj.academic_year_id.end_date
#
#            if vals['fee_pay_type']:
#
#                type=self.env['fee.payment.type'].browse(vals['fee_pay_type'])
#
#                if type.name=='term':
#                    if ((type.start_date>=start_date) and (type.start_date<=end_date) and (type.end_date>=start_date) and (type.end_date<=end_date)):
#                    else:
#                        raise except_orm(_('Warning!'),
#                        _("Term Start Date and End Date should be inbetween of Acadamic Year Start Date and End Date!"))
#
#        return super(Fees_Line, self).create(vals)

class Fees_Structure(models.Model):
    """
    Fees structure
    """
    _name = 'fees.structure'
    _description = 'Fees Structure'
    
    name = fields.Char('Name',required=True)
    code = fields.Char('Code',required=True)
    course_id= fields.Many2one('course', string='Class', required=True)
    academic_year_id=fields.Many2one('batch','Academic Year')
    fee_line_ids = fields.One2many('fees.line','fees_id','Fees Lines')
    type=fields.Selection([('reg','Registration'),('academic','Academic')])
    fee_history_line = fields.One2many('fee.history.line','fee_structure_id',string="Fee History")

    _sql_constraints = [
        ('code_uniq','unique(code)', 'The code of the Fees Structure must be unique !')
    ]

    @api.onchange('type','course_id','academic_year_id')
    def name_code_generate(self):
        name = ''
        if self.course_id and self.academic_year_id and self.type:
            name = self.type.upper() + '/' +\
                   self.course_id.name+ '/' + \
                   self.academic_year_id.name
        self.name = name
        self.code = name
    
    @api.model
    def create(self,vals):
        old_rec=self.search([('type','=',vals['type']),('course_id','=',vals['course_id']),('academic_year_id','=',vals['academic_year_id'])])

        if len(old_rec) != 0:
           raise except_orm(_('Warning!'),
                _("Fee structute already exist"))

        return super(Fees_Structure,self).create(vals)

    @api.multi
    def write(self,vals):
        if ('type' in vals) or ('course_id' in vals) or ('academic_year_id' in vals):
            if ('type' in vals):
                type=vals['type']
            else:
                type=self.type
            if ('course_id' in vals):
                course_id=vals['course_id']
            else:
                course_id=self.course_id.id
            if ('academic_year_id' in vals):
                academic_year_id=vals['academic_year_id']
            else:
                academic_year_id=self.academic_year_id.id
            old_rec=self.search([('type','=',type),('course_id','=',course_id),('academic_year_id','=',academic_year_id)])
            if len(old_rec) != 0:
                raise except_orm(_('Warning!'),
                _("Fee structute already exist"))
        return super(Fees_Structure,self).write(vals)

class fee_payment_type(models.Model):
    """
    Fee Payment Type
    """
    _name = 'fee.payment.type'
    _description = 'Fee Payment Type'
    
    name = fields.Selection([
            ('month', 'Monthly'),
            ('alt_month', 'Alternate Month'),
            ('quater', 'Quarterly'),
            ('year', 'Yearly'),
            ('one', 'One Time'),
            ('half_year','Half Year'),
            ('term','Term'),
        ],string="Name")
    code = fields.Char('Code')

    @api.multi
    def name_get(self):
        res = []
        def get_patment_type(type):
            val = {
                'month' : 'Monthly',
                'alt_month' : 'Alternate Month',
                'quater' : 'Quarterly',
                'year' : 'Yearly',
                'one' : 'One Time',
                'half_year' : 'Half Year',
                'term' : 'Term',
            }
            if val[type]:
                return val[type]

        for record in self:
            name = get_patment_type(record.name)
            res.append((record.id, name))
        return res

    @api.model
    def create(self,vals):
        vals['code']=vals['name']
        if vals['name']:
            old_rec=self.search([('name','=',vals['name'])])
            if len(old_rec) != 0:
               raise except_orm(_('Warning!'),
                    _("Payment Type %s is already exist") % (vals['name']))
        return super(fee_payment_type,self).create(vals)

    @api.multi
    def write(self,vals):
        if 'name' in vals:
            old_rec=self.search([('name','=',vals['name'])])
            if len(old_rec) != 0:
                raise except_orm(_('Warning!'),
                    _("Payment Type %s is already exist") % (vals['name']))
        
        return super(fee_payment_type,self).write(vals)
