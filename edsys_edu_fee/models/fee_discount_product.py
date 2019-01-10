from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import date

class product_product(models.Model):

    _inherit='product.template'

    fees = fields.Boolean(string="Student Fees")
    is_fees_discount = fields.Boolean(string="Discount For Fees")
    fees_discount = fields.Many2one('product.template',string="Discount for Fees")
    is_admission_fee = fields.Boolean(string='For New Student Only')

class Product_Discount_Category(models.Model):

    _name = 'discount.category'

    name = fields.Char('Name')
    code = fields.Char('Code')
    discount_category_line = fields.One2many('discount.category.line', 'discount_category_id',string='Discount Line')
    discount_history_line = fields.One2many('discount.history.line','discount_category_id',string='Discount History Line')

class Discount_Category_line(models.Model):

    _name = 'discount.category.line'

    product_id = fields.Many2one('product.template',string='Discount for Fees')
    discount_type = fields.Selection([('amount','Amount'),('persentage','Persentage')],string='Discount Type')
    discount_amount = fields.Float(string='Discount Amount')
    discount_persentage = fields.Float('Discount Persentage')
    discount_category_id = fields.Many2one('discount.category',string='Discount Category')
    update_discount = fields.Float()

    @api.model
    def create(self,vals):
        if 'discount_type' in vals and vals['discount_type']:
            if vals['discount_type'] == 'amount':
                vals['discount_persentage'] = 0.00
            if vals['discount_type'] == 'persentage':
                vals['discount_amount'] = 0.00
        return super(Discount_Category_line,self).create(vals)

    @api.multi
    def write(self,vals):
        if 'discount_persentage' in vals and vals['discount_persentage']:
            if vals['discount_persentage'] > 100.0:
                raise except_orm(_('Warning!'),_("please enter valid discount(%)."))
        if 'discount_type' in vals and vals['discount_type']:
            if vals['discount_type'] == 'amount':
                vals['discount_persentage'] = 0.00
            if vals['discount_type'] == 'persentage':
                vals['discount_amount'] = 0.00
        if 'update_discount' not in vals:
            if 'discount_amount' in vals or 'discount_persentage' in vals:
                raise except_orm(_('Warning!'),_("You can not update discount direcaly from hear, use update button"))
        return super(Discount_Category_line,self).write(vals)

    @api.multi
    def discount_update(self):
        if self.update_discount >= 0.00:
            student_obj = self.env['registration']
            for stud_rec in student_obj.search([('discount_on_fee','=',self.discount_category_id.id),('fee_structure_confirm','=',True)]):
                for fee_line in stud_rec.student_fee_line:
                    if fee_line.name.fees_discount.id == self.product_id.id:
                        if self.discount_type == 'amount':
                           fee_line.discount_amount = self.update_discount
                        elif self.discount_type == 'persentage':
                            fee_line.discount = self.update_discount

            history_data = {
                'updated_discount_id' : self.product_id.id,
                'discount_type':self.discount_type,
                'discount_category_id':self.discount_category_id.id,
                'update_date': date.today(),
            }

            if self.discount_type == 'amount':
                history_data.update({
                    'old_discount_amount':self.discount_amount,
                    'new_discount_amount':self.update_discount,
                    })
                self.discount_category_id.discount_history_line = [(0,0,history_data)]
                self.write({
                    'discount_amount':self.update_discount,
                    'discount_persentage':0.00,
                    'update_discount':0.00,
                })

            elif self.discount_type == 'persentage':
                history_data.update({
                    'old_discount_persentage':self.discount_persentage,
                    'new_discount_persentage':self.update_discount,
                    })
                self.discount_category_id.discount_history_line = [(0,0,history_data)]
                self.write({
                    'discount_persentage':self.update_discount,
                    'discount_amount':0.00,
                    'update_discount':0.00,
                })

class Discount_history(models.Model):

    _name = 'discount.history.line'

    updated_discount_id = fields.Many2one('product.template',string='Discount Fees')
    discount_type = fields.Selection([('amount','Amount'),('persentage','Persentage')],string='Discount Type')
    old_discount_amount = fields.Float(string='Old Discount Amount')
    new_discount_amount = fields.Float(string='New Discount Amount')
    old_discount_persentage = fields.Float(string='Old Discount Persentage')
    new_discount_persentage = fields.Float(string='New Discount Persentage')
    discount_category_id = fields.Many2one('discount.category',string='Discount Category')
    update_date = fields.Date('Date')
