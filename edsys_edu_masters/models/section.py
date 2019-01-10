# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class Section(models.Model):

    _name = 'section'

    code= fields.Char(size=8, string='Code', required=True)
    name=fields.Char(size=32, string='Name', required=True)
    course_id = fields.Many2many('course','section_course','student_section_id','course_id',string='Course')
