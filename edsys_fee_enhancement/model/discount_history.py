from odoo import models, fields, api, _

class discount_history(models.Model):

    _name = 'discount.history'
    
    sr_no = fields.Integer('Sr. No.')
    discount_category_id = fields.Many2one('discount.category','Discount Category')
    discount_category_code = fields.Char(related='discount_category_id.code')
    action_type = fields.Selection([('applied','Applied' ),('removed','Removed')],'Action')
    action_date = fields.Date("Action Date")
    applied_by = fields.Many2one('res.users', 'Applied By')
    applicable_from_date = fields.Date('Applicable From Date')
    academic_year_id = fields.Many2one('batch', 'Academic Year')
    is_applicable = fields.Boolean('Is Applicable')
    partner_id = fields.Many2one('res.partner',string="Student")
