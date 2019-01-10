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
from odoo.exceptions import except_orm,Warning

from ..models import book_unit
import datetime


class IssueBook(models.TransientModel):

    """ Issue Book """
    _name = 'issue.book'

    book_id = fields.Many2one('op.book', 'Book', required=True)
    book_unit_id = fields.Many2one('op.book.unit', 'Book Unit', required=True)
    isbn = fields.Char('ISBN13 Code', size=16)
    ean = fields.Char('EAN10 Code', size=16)
    barcode = fields.Char('Barcode', size=20)
    type = fields.Selection(
        [('student', 'Student'), ('faculty', 'Faculty')],
        'Type', required=True)
    #student_id = fields.Many2one('op.student', 'Student')
    student_id = fields.Many2one('res.partner', 'Student')
    class_id = fields.Many2one('course',string="Class")
    student_section_id = fields.Many2one('section', 'Admitted section')
    faculty_id = fields.Many2one('op.faculty', 'Faculty')
    library_card_id = fields.Many2one(
        'op.library.card', 'Library Card', required=True)
    issued_date = fields.Date('Issued Date', required=True, default=lambda self: fields.Date.today())
    return_date = fields.Date('Return Date', required=True)

    @api.onchange('library_card_id')
    def onchange_library_card_id(self):
        self.type = self.library_card_id.type
        if self.type == 'student':
            self.student_id = self.library_card_id.student_id.id
        self.return_date = datetime.datetime.now() + datetime.timedelta(self.library_card_id.return_days)
        self.faculty_id = self.library_card_id.faculty_id.id

    @api.onchange('book_id')
    def onchange_book_id(self):
        self.isbn = self.book_id.isbn
        self.ean = self.book_id.ean

    @api.onchange('book_unit_id')
    def onchange_book_unit_id(self):
        self.barcode = self.book_unit_id.barcode


    @api.onchange('student_id')
    def onchange_student_id(self):
        lib_card_obj= self.env['op.library.card']
        self.class_id = self.student_id.class_id.id
        self.student_section_id = self.student_id.student_section_id.id
        self.library_card_id = self.student_id.library_card_id.id
        if not self.student_id.library_card_id and self.type == 'student':
            warning = {
                    'title': _('Warning!'),
                    'message': _('No Library card found for this student!'),
                }
            return {'warning': warning}
        if self.type and not lib_card_obj.sudo().search([("student_id","=",self.student_id.id)]):
            warning = {
                    'title': _('Warning!'),
                    'message': _('Library card deactivated this student!'),
                }
            return {'warning': warning}

    @api.onchange('faculty_id')
    def onchange_faculty_id(self):
        
        lib_card_obj= self.env['op.library.card']
        self.library_card_id = self.faculty_id.library_card_id.id
        if not self.library_card_id and self.type == 'faculty':
            warning = {
                    'title': _('Warning!'),
                    'message': _('No Library card found for this faculty!'),
                }
        if self.type and not lib_card_obj.sudo().search([("faculty_id","=",self.faculty_id.id)]):
            warning = {
                    'title': _('Warning!'),
                    'message': _('Library card deactivated this faculty!'),
                }
            return {'warning': warning}



    @api.one
    def check_max_issue(self, student_id,faculty_id, library_card_id):
        if self.type=="student":
                
            book_movement_search = self.env["op.book.movement"].search(
                [('library_card_id', '=', library_card_id),
                 ('student_id', '=', student_id),
                 ('state', '=', 'issue')])
        else:
            book_movement_search = self.env["op.book.movement"].search(
                [('library_card_id', '=', library_card_id),
                 ('faculty_id', '=', faculty_id),
                 ('state', '=', 'issue')])            
        
        if len(book_movement_search) < self.env["op.library.card"].browse(
                library_card_id).library_card_type_id.allow_book:
            return True
        else:
            return False

    @api.one
    def do_issue(self):
        value = {}
    
        # CHECK IF LIBRRAY CARD DEACTIVATED
        lib_card_obj= self.env['op.library.card']
        if self.type=="student":
            if not lib_card_obj.sudo().search([("student_id","=",self.student_id.id)]):
                raise except_orm(_('Warning!'),
                        _("Library card deactivated this student!"))
        else:
            if not lib_card_obj.sudo().search([("faculty_id","=",self.faculty_id.id)]):
                raise except_orm(_('Warning!'),
                        _("Library card deactivated this faculty!"))            

    
        # CHECK ALLOWED BOOKS PER LIBRARY CARD
        #RETURN FALSE IF IT REACHES THE LIMIT
        
        if any(self.check_max_issue(self.student_id.id,self.faculty_id.id, self.library_card_id.id)):
            if self.book_unit_id.state and \
                    self.book_unit_id.state == 'available':
                
                book_movement_create = {
                    'book_id': self.book_id.id,
                    'book_unit_id': self.book_unit_id.id,
                    'type': self.type,
                    'student_id': self.student_id.id or False,
                    'faculty_id': self.faculty_id.id or False,
                    'library_card_id': self.library_card_id.id,
                    'issued_date': self.issued_date,
                    'return_date': self.return_date,
                    'library_id': self.env.context.get('library_id') or False,
                    'state': 'issue',
                }
                self.env['op.book.movement'].create(book_movement_create)
                self.book_unit_id.state = 'issue'
                value = {'type': 'ir.actions.act_window_close'}
            else:
                raise Warning(_('Error!'), _(
                    "Book Unit can not be issued because it's state is : %s") %
                    (dict(book_unit.unit_states).get(
                        self.book_unit_id.state)))
        else:
            if self.type =="student":
                
                partner_name = self.student_id.name
            else:
                partner_name = self.faculty_id.name
            
            raise Warning(_('Error!'), _(
                'Maximum Number of book allowed for %s is : %s') %
                (partner_name,
                 self.library_card_id.library_card_type_id.allow_book))
        return value

# class OpFaculty(models.Model):
#     _inherit = 'op.faculty'
#
#     @api.multi
#     def name_get(self):
#         result = []
#         for record in self:
#             result.append([record.id, "%s %s %s" % (record.name, record.middle_name, record.last_name)])
#         return  result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
