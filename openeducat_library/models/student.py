# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields
from openerp import models, fields, api, _

class Student(models.Model):

    _inherit = 'res.partner'

    library_card_id = fields.Many2one('op.library.card', 'Library Card')
    book_movement_lines = fields.One2many(
        'op.book.movement', 'student_id', 'Movements')   
    
    
    @api.multi
    def open_report(self):
        '''print library catd of student '''
      
        value = {
            'type': 'ir.actions.report.xml',
            'report_name': 'openeducat_library.report_student_library_card',
            'datas': {
                'model': 'res.partner',
                'id': self.id,
                'ids': [self.id],
                'report_type': 'pdf',
                'report_file': 'openeducat_library.report_student_library_card'
            },
            'nodestroy': True
        
        }
        return value

class OpStudent(models.Model):
    _inherit = 'op.student'

    library_card_id = fields.Many2one('op.library.card', 'Library Card')
    book_movement_lines = fields.One2many(
        'op.book.movement', 'student_id', 'Movements')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
