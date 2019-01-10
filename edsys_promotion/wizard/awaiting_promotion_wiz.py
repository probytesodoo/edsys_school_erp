from odoo import models, fields, api, _
from odoo.exceptions import except_orm

class awaiting_promotion_wiz(models.TransientModel):
    _name = 'awaiting.promotion.wiz'

    student_section_ids = fields.Many2one('section', string='Promote To Section')

    @api.multi
    def promote_students(self, context):
        fees_obj = self.env['fees.structure']
        promote_obj = self.env['promote.student.line']
        fee_confirm_list = []

        for student in context['active_ids']:
            awaiting_rec = promote_obj.browse(student)
            if awaiting_rec.state == 'draft':
                fees_data = fees_obj.search([('type', '=', 'academic'), ('course_id', '=', awaiting_rec.new_acad_class.id),
                                            ('academic_year_id', '=', awaiting_rec.new_acad_year.id)])

                if self.student_section_ids:
                    awaiting_rec.new_acad_section = self.student_section_ids.id

                for fees in fees_data.fee_line_ids:
                    if not fees.name.is_admission_fee:
                        fees_lines = {
                                'promote_lines_id': awaiting_rec.id,
                                'sequence': fees.sequence,
                                'name': fees.name,
                                'amount': int(fees.amount),
                                'type': fees.type,
                                'fee_pay_type': fees.fee_pay_type.id
                                }
                        fee_confirm_list.append((0, 0, fees_lines))
                awaiting_rec.fees_structure_lines = fee_confirm_list
                awaiting_rec.student_id.promoted = True
                fee_confirm_list = []
                awaiting_rec.state = 'promote'
            else:
                raise except_orm(_('Warning!'),_("You can promote student only in DRAFT state"))

