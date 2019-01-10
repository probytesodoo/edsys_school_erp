from odoo import models, fields, api, _

class fee_computation(models.Model):

    _name = 'fee.computation'
    
    List_Of_Month = [
        (1,'January'),
        (2,'February'),
        (3,'March'),
        (4,'April'),
        (5,'May'),
        (6,'June'),
        (7,'July'),
        (8,'August'),
        (9,'September'),
        (10,'October'),
        (11,'November'),
        (12,'December'),
        ]
    
    name = fields.Many2one('product.product','Name')
    month_id = fields.Many2one('fee.month','Month')
    month = fields.Selection(List_Of_Month, string='Month', related='month_id.name')
    fee_date = fields.Date('Date')
    total_calculated_amount = fields.Float("Calculated Amount", help="Original amount : without discount")
    total_discount_amount = fields.Float("Total Discount Amount", help="Calculated amount - Invoice Amount")
    invoice_amount = fields.Float("Invoice Amount", help="Calculated amount - Discount Amount")
    status = fields.Selection([('invoice_raised','Invoice Raised' ),('invoice_not_raised','Invoice Not Raised')],'Status', default='invoice_not_raised')
    discount_category_id = fields.Many2one('discount.category',string="Discount Name")
    
    fee_computation_line_ids = fields.One2many('fee.computation.line','fee_computation_id', string="fee Computation Lines")
    partner_id = fields.Many2one('res.partner',string="Student")
    registration_id = fields.Many2one('registration', string="Registration")
    promote_student_line_id = fields.Many2one('promote.student.line', string="Promote Student")
