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

from odoo import models, fields, api


class ReserveBook(models.TransientModel):

    """ Reserve Book """
    _name = 'reserve.book'

    partner_id = fields.Many2one('res.partner', required=True)

    @api.one
    def set_partner_old_10aug2016(self):
        #import ipdb;ipdb.set_trace()
        self.env['op.book.movement'].browse(
            self.env.context.get('active_ids', False)).write({
                'partner_id': self.partner_id.id,
                'reserver_name': self.partner_id.name,
                'state': 'reserve'
            })
            
    @api.one
    def set_partner(self):
        #import ipdb;ipdb.set_trace()
        book_movement_create = {
            'book_id': self.book_id.id,
            'book_unit_id': self.book_unit_id.id,
            'type': self.type,
            'student_id': self.student_id.id or False,
            'faculty_id': self.faculty_id.id or False,
            'library_card_id': self.library_card_id.id,
            'issued_date': self.issued_date,
            'return_date': self.return_date,
            'state': 'issue',
        }
        self.env['op.book.movement'].create(book_movement_create)
        self.book_unit_id.state = 'issue'
        value = {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
