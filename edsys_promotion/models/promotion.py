# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import except_orm


class promote_student(models.Model):
    _name = "promote.student"

    name = fields.Char(default='Student')
    class_id = fields.Many2one('course', string="Class")
    batch_id = fields.Many2one('batch', string="Academic Year")
    student_section_ids = fields.Many2many('section', string='Section')
    promote_to_class = fields.Many2one('course', string="Promote To Class")
    promote_to_batch = fields.Many2one('batch', string="Promote To Academic Year")
    promote_to_section = fields.Many2one('section', string='Promote To Section')
    student_list = fields.Boolean('Student List')
    student_line = fields.One2many('promote.student.line', 'promote_student_id', 'Promote Student')
    # state = fields.Selection([('draft', 'Draft'), ('promote', 'Promoted')], string='State', default='draft')
    
    @api.onchange('class_id')
    def onchange_class(self):
        course_obj = self.env['course']
        if self.class_id:
            if self.class_id.is_last_course:
                raise except_orm(_('Warning!'), _("You cannot proceed with promotion process for %s!")
                                 %self.class_id.name)
            if not self.class_id.is_last_course and not self.class_id.next_course:
                raise except_orm(_('Warning!'), _("Next course is not defined!"))
            self.promote_to_class = self.class_id.next_course.id
            
    @api.onchange('batch_id')
    def onchange_batch(self):
        batch_obj = self.env['batch']
        if self.batch_id:
            if not self.batch_id.next_batch:
                raise except_orm(_('Warning!'), _("Next batch is not defined!"))
            self.promote_to_batch = self.batch_id.next_batch.id

    @api.onchange('promote_to_batch')
    def onchange_promote_batch(self):
        fees_obj = self.env['fees.structure']
        if self.promote_to_batch:
            fees_data = fees_obj.search([('type', '=', 'academic'), ('course_id', '=', self.promote_to_class.id),
                                        ('academic_year_id', '=', self.promote_to_batch.id)])
            if not fees_data:
                raise except_orm(_('Warning!'),
                                 _("Fee Structure is not defined for class %s and academic year %s!")
                                 % (self.promote_to_class.name, self.promote_to_batch.name))
            
    @api.model
    def create(self, vals):
        course_obj = self.env['course']
        batch_obj = self.env['batch']
        course_brw = course_obj.browse(vals['class_id'])
        batch_brw = batch_obj.browse(vals['batch_id'])

        records = self.search([('class_id', '=', vals['class_id']), ('batch_id', '=', vals['batch_id'])])
        for rec in records:
            if len(list(rec.student_section_ids)) == 0:
                raise except_orm(_('Warning!'),
                            _("Record is already exist for same!"))
            elif rec.student_section_ids in vals['section_ids'][0][2]:
                raise except_orm(_('Warning!'),
                    _("Record is already exist for same!"))

        if 'class_id' in vals and 'promote_to_class' in vals:
            if vals['class_id'] and vals['promote_to_class']:
                if course_brw.is_last_course:
                    raise except_orm(_('Warning!'), _("You cannot proceed with promotion process for %s!")%course_brw.name)
                if not course_brw.next_course:
                    raise except_orm(_('Warning!'), _("Next course is not defined!"))
                if course_obj.browse(vals['promote_to_class']).id != course_brw.next_course.id:
                    raise except_orm(_('Warning!'),
                        _("promote to class can not be equal to or lower than current class!!"))
                
        if 'batch_id' in vals and 'promote_to_batch' in vals:
            if vals['batch_id'] and vals['promote_to_batch']:
                if not batch_brw.next_batch:
                    raise except_orm(_('Warning!'), _("Next batch is not defined!"))
                if batch_obj.browse(vals['promote_to_batch']).id != batch_brw.next_batch.id:
                    raise except_orm(_('Warning!'), 
                        _("promote to batch can not be equal to or lower than current batch!!"))
        return super(promote_student, self).create(vals)
    
    @api.multi
    def write(self, vals):
        course_obj = self.env['course']
        batch_obj = self.env['batch']

        if 'class_id' in vals or 'promote_to_class' in vals:
            if 'class_id' not in vals:  
                vals['class_id']=self.class_id.id
            if 'promote_to_class'not in vals:
                vals['promote_to_class'] = self.promote_to_class.id
                
            if vals['class_id'] or vals['promote_to_class']:
                course_brw = course_obj.browse(vals['class_id'])
                if course_brw.is_last_course:
                    raise except_orm(_('Warning!'), _("You cannot proceed with promotion process for %s!") % course_brw.name)
                if not course_brw.next_course:
                    raise except_orm(_('Warning!'), _("Next course is not defined!"))
                if course_obj.browse(vals['promote_to_class']).name != course_brw.next_course:
                    raise except_orm(_('Warning!'), _("Promote to class can not be equal to or lower than current class!!"))
                
        if 'batch_id' in vals or 'promote_to_batch' in vals:
            if 'batch_id' not in vals:  
                vals['batch_id']=self.batch_id.id
            if 'promote_to_batch'not in vals:
                vals['promote_to_batch']=self.promote_to_batch.id
                
            if vals['batch_id'] and vals['promote_to_batch']:
                batch_brw = batch_obj.browse(vals['batch_id'])
                if not batch_brw.next_batch:
                    raise except_orm(_('Warning!'), _("Next batch is not defined!"))
                if batch_obj.browse(vals['promote_to_batch']).name != batch_brw.next_batch:
                    raise except_orm(_('Warning!'), _("Promote to batch can not be equal to or lower than current batch!!"))
        return super(promote_student, self).write(vals)
    
    @api.multi
    def show_student_list(self):
        student_obj = self.env['res.partner']
        promote_obj = self.env['promote.student.line']
        fees_obj = self.env['fees.structure']
        self.student_list = False
        if not self.batch_id.promotion_start_date or not self.batch_id.promotion_end_date:
            raise except_orm(_('Warning!'), _("Promotion process period is not defined!"))
        start_date = datetime.strptime(self.batch_id.promotion_start_date, "%Y-%m-%d").date() 
        end_date = datetime.strptime(self.batch_id.promotion_end_date, "%Y-%m-%d").date()
        current_date = datetime.today().date()
        if ((current_date<start_date) or (current_date>end_date)):
            raise except_orm(_('Warning!'),
            _("Promotion process might not be started or already ended!"))

        if self.promote_to_batch:
            fees_data = fees_obj.search([('type', '=', 'academic'), ('course_id', '=', self.promote_to_class.id),
                                        ('academic_year_id', '=', self.promote_to_batch.id)])
            if not fees_data:
                raise except_orm(_('Warning!'), _("Fee Structure is not defined for class %s and academic year %s!")%
                                 (self.promote_to_class.name, self.promote_to_batch.name))

        if not self.student_section_ids:
            student_data = student_obj.search([('is_student', '=', True),
                                               ('promoted', '=', False),
                                               ('course_id', '=', self.class_id.id),
                                               ('batch_id', '=', self.batch_id.id)])
        else:
            student_data = student_obj.search([('is_student', '=', True),
                                               ('promoted', '=', False),
                                               ('course_id', '=', self.class_id.id),
                                               ('batch_id', '=', self.batch_id.id),
                                               ('student_section_id', 'in', self.student_section_ids.ids)])
        if len(student_data) > 0:
            for student in student_data:
                promote_student_rec = promote_obj.search([('student_id', '=', student.id),('current_academic_year', '=', self.batch_id.id)])
                if not promote_student_rec:
                    if not self.promote_to_section:
                        lines = {
                            'promote_student_id': self.ids[0],
                            'student_id': student.id,
                            'current_academic_year': student.batch_id.id,
                            'current_academic_class': student.course_id.id,
                            'current_academic_section': student.student_section_id.id,
                            'new_acad_year': self.promote_to_batch.id,
                            'new_acad_class': self.promote_to_class.id,
                            'new_acad_section': student.student_section_id.id
                            }
                    elif self.promote_to_section:
                        lines = {
                            'promote_student_id': self.ids[0],
                            'student_id': student.id,
                            'current_academic_year': student.batch_id.id,
                            'current_academic_class': student.course_id.id,
                            'current_academic_section': student.student_section_id.id,
                            'new_acad_year': self.promote_to_batch.id,
                            'new_acad_class': self.promote_to_class.id,
                            'new_acad_section': self.promote_to_section.id
                            }
                    promote_obj.create(lines)
                    self.student_list = True
        if self.student_list != True:
            raise except_orm(_('Warning!'), _("There is no any student to promote."))

    # @api.multi
    # def student_promotion(self):
    #     fees_obj = self.env['fees.structure']
    #     fees_data = fees_obj.search([('type', '=', 'academic'), ('course_id', '=', self.promote_to_class.id),
    #                                  ('academic_year_id', '=', self.promote_to_batch.id)])
    #     fee_lst = []
    #     for student in self.student_line:
    #         if student.state == 'draft':
    #             for fees in fees_data.fee_line_ids:
    #                 if not fees.name.is_admission_fee:
    #                     fees_lines = {
    #                             'promote_lines_id': student.id,
    #                             'sequence': fees.sequence,
    #                             'name': fees.name,
    #                             'amount': int(fees.amount),
    #                             'type': fees.type,
    #                             'fee_pay_type': fees.fee_pay_type.id
    #                             }
    #                     fee_lst.append((0, 0, fees_lines))
    #             student.fees_structure_lines = fee_lst
    #             student.student_id.promoted = True
    #             fee_lst = []
    #             student.state = 'promote'
    #     self.state = 'promote'


class promote_student_line(models.Model):

    _name = "promote.student.line"

    student_id = fields.Many2one('res.partner', 'Student')
    current_academic_year = fields.Many2one('batch', 'Current Academic Year')
    current_academic_class = fields.Many2one('course', 'Current Class')
    current_academic_section = fields.Many2one('section', 'Current Section')
    new_acad_year = fields.Many2one('batch', 'New Academic Year')
    new_acad_class = fields.Many2one('course', 'New Class')
    new_acad_section = fields.Many2one('section', 'Assign To Section')
    promote_student_id = fields.Many2one('promote.student', 'Student Reference')
    state = fields.Selection([('draft', 'Draft'), ('promote', 'Promoted'), ('fee_confirmed', 'Fee Confirmed')],
                             string='State', default='draft')

    @api.multi
    def unlink(self):
        for student in self:
            if student.state == 'draft':
                continue
            elif student.state == 'promote':
                student.student_id.promoted = False
                continue
            else:
                raise except_orm(_('Warning!'),_("You can not delete this record"))
        return super(promote_student_line, self).unlink()

class student_promotion(models.Model):
    _inherit = 'res.partner'

    promoted = fields.Boolean(string='Promoted')
    student_fees_history = fields.One2many('student.fee.history', 'fee_history', 'Fee History')
    
    
class CourseInherit(models.Model):
    _inherit = 'course'

    next_course = fields.Many2one('course', 'Next Course')
    is_last_course = fields.Boolean('Last Course')


class BatchInherit(models.Model):

    _inherit = 'batch'

    next_batch = fields.Many2one('batch', 'Next Batch')

    @api.onchange('next_batch')
    def onchange_next_batch(self):
        """
        --------------------------
        :return:
        """
        if self.next_batch:
            if self.end_date > self.next_batch.start_date:
                self.next_batch = False
                warning = {
                    'title': _('Warning!'),
                    'message': _('Next batch can not be lower than current batch!')
                }
                return {'warning': warning}

