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

from odoo import models, fields, api, _


class IssueReturnBook(models.TransientModel):

    """ Issue Return Book Wizard """
    _name = 'issue.return.book'

    type = fields.Selection(
        [('student', 'Student'), ('faculty', 'Faculty')], 'Student/Faculty')
    student_id = fields.Many2one('res.partner', 'Student')
    faculty_id = fields.Many2one('op.faculty', 'Faculty')
    state = fields.Selection([('issue', 'Issue'), ('return', 'Return')])
    movement_ids = fields.Many2many('op.book.movement', 'book_issue_return_movement_rel', 'issue_return_id', 'movement_id')
    book_unit_ids = fields.Many2many('op.book.unit', 'book_issue_return_unit_rel', 'issue_return_id', 'book_unit_id')
    book_unit_id = fields.Many2one('op.book.unit', 'Book')
    barcode = fields.Char('Barcode', size=20)
    isbn = fields.Char('ISBN13 Code', size=16)
    ean = fields.Char('EAN10 Code', size=16)
    author_ids = fields.Many2many(
        'op.author', string='Author(s)')

    @api.onchange('barcode', 'isbn', 'ean', 'author_ids', 'book_unit_id')
    def onchange_issue(self):
        op_book_unit_obj = self.env['op.book.unit']

        if self.barcode:
            rec_op_book_unit = op_book_unit_obj.search([('barcode', 'ilike', self.barcode),
                                                        ('state', '=', 'available')])
            self.book_unit_ids = [(6, 0, list(set(rec_op_book_unit.ids + self.book_unit_ids.ids)))]

        if self.isbn:
            rec_op_book = self.env['op.book'].search([('isbn', 'ilike', self.isbn)])
            rec_op_book_unit = op_book_unit_obj.search([('book_id', 'in', rec_op_book.ids),
                                                        ('state', '=', 'available')])
            self.book_unit_ids = [(6, 0, list(set(rec_op_book_unit.ids + self.book_unit_ids.ids)))]

        if self.ean:
            rec_op_book = self.env['op.book'].search([('ean', 'ilike', self.ean)])
            rec_op_book_unit = op_book_unit_obj.search([('book_id', 'in', rec_op_book.ids),
                                                        ('state', '=', 'available')])
            self.book_unit_ids = [(6, 0, list(set(rec_op_book_unit.ids + self.book_unit_ids.ids)))]

        if self.author_ids:
            rec_op_book_unit = op_book_unit_obj.search([('book_id.author_ids', 'in', self.author_ids.ids),
                                                        ('state', '=', 'available')])
            self.book_unit_ids = [(6, 0, list(set(rec_op_book_unit.ids + self.book_unit_ids.ids)))]

        if self.book_unit_id:
            self.book_unit_ids = [(6, 0, list(set(self.book_unit_id.ids + self.book_unit_ids.ids)))]

    @api.onchange('state', 'type', 'student_id', 'faculty_id')
    def onchange_return(self):
        if self.state == 'return':
            if self.type == 'student':
                rec_op_book_mov = self.env['op.book.movement'].search([('state', '=', 'issue'),
                                                                   ('type', '=', self.type),
                                                                   ('student_id', '=', self.student_id.id)])
                self.movement_ids = [(6, 0, rec_op_book_mov.ids)]
            else:
                rec_op_book_mov = self.env['op.book.movement'].search([('state', '=', 'issue'),
                                                                   ('type', '=', self.type),
                                                                   ('faculty_id', '=', self.faculty_id.id)])
                self.movement_ids = [(6, 0, rec_op_book_mov.ids)]

