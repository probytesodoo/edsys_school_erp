from odoo import models, fields, api

class FeeStructureUpdate(models.Model):

    _inherit = 'fees.line'

    @api.multi
    def update_fee_amount(self):
        """
        Update promoted fee structure when update Fee structure master
        --------------------------------------------------------------
        :return:
        """
        res = super(FeeStructureUpdate, self).update_fee_amount()
        promote_student_line_obj = self.env['promote.student.line']
        for promote_student in promote_student_line_obj.search([('new_acad_class','=',self.fees_id.course_id.id),
                                               ('new_acad_year', '=', self.fees_id.academic_year_id.id)]):
            print promote_student.promoted_fee_structure_confirm
            if promote_student.promoted_fee_structure_confirm != True:
                for fee_line in promote_student.fees_structure_lines.search([('promote_line_id','=',promote_student.id),
                                                                             ('name','=',self.name.id)]):
                    fee_line.amount = self.amount
        return res