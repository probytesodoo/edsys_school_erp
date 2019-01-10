# # -*- coding: utf-8 -*-
# from datetime import timedelta
# from openerp import models, fields, api, _
#
# class Standard(models.Model):
#     _name = 'standard'
#     _order = 'sequence'
#
#     code= fields.Char(size=8, string='Code', required=True)
#     name= fields.Char(size=32, string='Name', required=True)
#     course_id= fields.Many2one('course', string='Course', required=True)
#     sequence=fields.Integer('Sequence')
#     division_ids=fields.Many2many('section', 'standard_division_rel', 'standard_id', 'student_section_id', 'Sections', )
# #    student_ids= fields.Many2many('student', 'student_standard_rel', 'student_id', 'standard_id', string='Student(s)')
# #    'class_ids': fields.many2many('op.gr.setup', 'op_class_setup_rel','op_standard_id', 'op_setup_id' , string='Class'),
