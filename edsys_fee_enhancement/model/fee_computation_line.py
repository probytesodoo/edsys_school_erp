from odoo import models, fields, api, _

class fee_computation_line(models.Model):

    _name = 'fee.computation.line'
    
    name = fields.Many2one('product.product','Fee Computation')
    calculated_amount = fields.Float("Calculated Amount", help='Original amount')
    discount_percentage = fields.Float("Discount Percentage")
    discount_amount = fields.Float("Discount Amount", )
    payable_amount = fields.Float("Payable Amount", help='Amount - Discount Amount')
    fee_payment_type_id = fields.Many2one('fee.payment.type',string="Fee Payment type")
    fee_computation_id = fields.Many2one('fee.computation',string="Fee Computation")
