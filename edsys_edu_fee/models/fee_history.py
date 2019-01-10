from odoo import models, fields, api, _

# class FeeHistory(models.Model):
#
#     _name = 'fee.history'
#
#     name = fields.Char(string='Name')
#     code = fields.Char(string='Code')
#     course_id = fields.Many2one('course', string='Class')
#     academic_year_id=fields.Many2one('batch','Academic Year')
#     fe_history_line = fields.One2many('fee.history.line','fee_history_id', string='Fee History line')

class FeeHistoryLine(models.Model):

    _name = 'fee.history.line'

    date = fields.Date('Date')
    name = fields.Many2one('product.product','Name')
    sequence  = fields.Integer(string='Sequence ')
    new_amount = fields.Float(string='New Amount')
    old_amount = fields.Float(string='Old Amount')
    # fee_history_id = fields.Many2one('fee.history', string='Fee History')
    fee_structure_id = fields.Many2one('fees.structure',string='Fee Structure')