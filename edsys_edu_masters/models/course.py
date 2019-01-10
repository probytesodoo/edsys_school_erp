# -*- coding: utf-8 -*-
from datetime import timedelta
from openerp import models, fields, api, _

class Course(models.Model):

    _name = 'course'

#    batch_id = fields.Many2one('batch',string='Batch')
    name = fields.Char(size=32, string='Name', required=True)
    code = fields.Char(size=8, string='Code', required=True)
    section = fields.Many2many('section','section_course','course_id','student_section_id',string='Section')
    evaluation_type = fields.Selection([('normal','Normal'),('GPA','GPA'),('CWA','CWA'),('CCE','CCE')], string='Evaluation Type', required=True)
    min_age = fields.Integer(string="Minimum Age")
    max_age = fields.Integer(string="Maximum Age")
#    effective_date = fields.Date(string="Effective Date")

    @api.multi
    def write(self,vals):
        if 'name' in vals and vals['name']:
            name=vals['name'].replace(' ','')
            vals['name']=name
        return super(Course,self).write(vals)

    @api.model
    def create(self,vals):
        if 'name' in vals and vals['name']:
            name=vals['name'].replace(' ','')
            vals['name']=name
        return super(Course,self).create(vals)
