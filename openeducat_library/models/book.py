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
from odoo.exceptions import ValidationError
import re
from odoo.exceptions import except_orm, Warning, RedirectWarning


class OpBook(models.Model):
    _name = 'op.book'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Book"

    #     @api.constrains('ean', 'isbn')
#     def _check_digit_constraint(self):
#         p = re.compile('^\d{10}$')
#         if p.match(self.isbn) == None:
#             raise except_orm(_('Warning!'),
#                     _("Please Enter Valid ISBN13 Code: (%s)") % (self.isbn,))
# 
#         if p.match(self.ean) == None:
#             raise except_orm(_('Warning!'),
#                     _("Please Enter Valid EAN13 Code: (%s)") % (self.ean,))
#         return True

    name = fields.Char('Title', size=128, required=True)
    isbn = fields.Char('ISBN13 Code', size=16)
    ean = fields.Char('EAN10 Code', size=16)
    tags = fields.Many2many('op.tag', string='Tag(s)')
    author_ids = fields.Many2many(
        'op.author', string='Author(s)', required=True)
    edition = fields.Char('Edition')
    description = fields.Text('Description')
    publisher_ids = fields.Many2many(
        'op.publisher', string='Publisher(s)', required=True)
#     course_ids = fields.Many2many('op.course', string='Course', required=True)
    course_ids = fields.Many2many('course', string='Course', required=True)
    movement_line = fields.One2many('op.book.movement', 'book_id', 'Movements')
    subject_ids = fields.Many2many(
        'op.subject', string='Subjects', required=True)
    internal_code = fields.Char('Internal Code', size=64)
    queue_ids = fields.One2many('op.book.queue', 'book_id', 'Book Queue')
    unit_ids = fields.One2many('op.book.unit', 'book_id', 'Units')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
