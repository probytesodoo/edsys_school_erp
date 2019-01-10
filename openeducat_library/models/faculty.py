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

from openerp import models, fields, api


class OpFaculty(models.Model):
    _inherit = 'op.faculty'

    library_card_id = fields.Many2one('op.library.card', 'Library Card')
    book_movement_lines = fields.One2many(
        'op.book.movement', 'faculty_id', 'Movements')

    @api.multi
    def name_get(self):
        res = []
        for faculty in self:
            name = faculty.name
            if faculty.middle_name:
                name = name+' '+faculty.middle_name
            if faculty.last_name:
                name = name+' '+faculty.last_name
            res.append((faculty.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        ''' Faculty can searth with first name, middle name, last name and employee code '''
        args = args or []
        domain = ['|', '|', ('name', operator, name),
                            ('middle_name', operator, name),
                            ('last_name', operator, name)]

        rec_employee = self.env['hr.employee'].search([('code', operator, name)], limit=limit)
        if rec_employee:
            domain = ['|'] + domain + [('emp_id', 'in', rec_employee.ids)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
