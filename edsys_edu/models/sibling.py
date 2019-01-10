# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, _

class sibling(models.Model):

    _name = 'sibling'

    sibling_name = fields.Char(size=256, string='Sibling Name')
    sibling_grade = fields.Char(size=256, string='Sibling Grade')
    reg_id = fields.Many2one('registration', string='Registrations', invisible=True)
    student_id = fields.Many2one('res.partner', string='Student', invisible=True)
