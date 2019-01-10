from odoo import models, fields, api




class ir_sequence_type(models.Model):
    _name = 'ir.sequence.type'
    _order = 'name'
    
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', size=32, required=True)
   

    _sql_constraints = [
        ('code_unique', 'unique(code)', '`code` must be unique.')
    ]