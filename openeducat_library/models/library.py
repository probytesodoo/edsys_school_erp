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
from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class library_location(models.Model):
    
    _name = 'library.location'
    _description = 'Configure multiple libraries'

    #@api.depends('parent1_id')
    def get_librarian(self):
        """
        get librarian
        ------------------
        :return:
        """
        
        for library in self :
            
            self.env.cr.execute("select id from res_users where library_id =%s",(library.id,))
            user_ids = map(lambda x:x[0], self.env.cr.fetchall())
            if user_ids :
                library.user_ids = [(6,0,user_ids)]

    def get_total_book_unit(self):
        """
        get total book unit in library
        ------------------
        :return:
        """
        for library in self :
            self.env.cr.execute("select id from op_book_unit where library_id =%s",(library.id,))
            book_unit_ids = map(lambda x:x[0], self.env.cr.fetchall())
            if book_unit_ids :
                library.total_book_unit = len(book_unit_ids)             

    name = fields.Char('Name', size=256, required=True)
    code = fields.Char('Code', size=5, required=True)
    user_ids = fields.Many2many('res.users','user_id','library_id',string='Librarian', compute='get_librarian',copy=False)

    total_book_unit = fields.Integer('Total Books Unit', size=5, compute = 'get_total_book_unit')
    
    
    _sql_constraints = [
        ('code_uniq','unique(code)', 'The code of the Library must be unique !'),
        ('name_uniq','unique(name)', 'Library already exist !')
        
    ]

class OpLibraryCardType(models.Model):
    _name = 'op.library.card.type'
    _description = 'Library Card Type'

    name = fields.Char('Name', size=256, required=True)
    type = fields.Selection(
        [('student', 'Student'), ('faculty', 'Faculty')],
        'Type', required=True)
    allow_book = fields.Integer('No of Books Allowed', size=10, required=True)
    duration = fields.Float(
        'Duration', help='Duration in terms of Number of Lead Days',
        required=True)
    penalty_amt_per_day = fields.Float('Penalty Amount per Day', required=True)


class OpLibraryCard(models.Model):
    _name = 'op.library.card'
    _rec_name = 'number'
    _description = 'Library Card'

    partner_id = fields.Many2one(
        'res.partner', 'Student/Faculty')
    number = fields.Char('Number', size=256, required=True)
    library_card_type_id = fields.Many2one(
        'op.library.card.type', 'Card Type', required=True)
    issue_date = fields.Date('Issue Date', required=True)
    type = fields.Selection(
        [('student', 'Student'), ('faculty', 'Faculty')],
        'Type', default='student', required=True)
    #student_id = fields.Many2one('op.student', 'Student')
    student_id = fields.Many2one('res.partner', 'Student')
    faculty_id = fields.Many2one('op.faculty', 'Faculty')
    return_days = fields.Integer('Return Days', required=True)
    active = fields.Boolean('Active',default=True)
    
    @api.onchange('student_id')
    def onchange_student(self):
        library_card_id = self
        if library_card_id.student_id : 
            self.env.cr.execute('''select library_card_id from res_partner where id=%s ''',(library_card_id.student_id.id,))
            val = map(lambda x:x[0], self.env.cr.fetchall())
            if any(val) : 
                raise except_orm(_('Warning!'),_("Library card %s already assigned to %s.")\
                                 %(library_card_id.student_id.library_card_id.number,library_card_id.student_id.name))  
    
        
    @api.onchange('faculty_id')
    def onchange_faculty(self):
        library_card_id = self
        if library_card_id.faculty_id : 
            self.env.cr.execute('''select library_card_id from op_faculty where id=%s ''',(library_card_id.faculty_id.id,))
            val = map(lambda x:x[0], self.env.cr.fetchall())
            if any(val) : 
                raise except_orm(_('Warning!'),_("Library card %s already assigned to %s.")\
                                 %(library_card_id.faculty_id.library_card_id.number, library_card_id.faculty_id.name))  

    @api.onchange('library_card_type_id')
    def onchange_card_type(self):
        """
        Selects type on the basis of library card type
        """
        if self.library_card_type_id:
            if self.library_card_type_id.type == 'student':
                self.type = 'student'
            else:
                self.type = 'faculty'
        
    @api.multi
    def map_library_card(self,library_card_id):
        """
        Throw exception if user assign same partner for multiple library card
        """
        library_card_id.env.uid = SUPERUSER_ID
        
        if library_card_id.type =="student" : 
#             query = """select id from res_partner where library_card_id =%s """
#             params = (library_card_id.id,)

            #UPDATE QUERY
            query_udpate = """update res_partner set library_card_id =%s where id=%s"""
            params_update = (library_card_id.id,library_card_id.student_id.id)
            # REMOVE OLD CARD MAPPING FROM PARTNER FORM
            query_replace = """update res_partner set library_card_id =NULL where library_card_id =%s"""
            params_replace = (library_card_id.id, ) 
                                
        else :
#             query = """select id from op_faculty where library_card_id =%s """
#             params = (library_card_id.id,)

            #UPDATE QUERY
            query_udpate = """update op_faculty set library_card_id =%s where id=%s"""
            params_update = (library_card_id.id,library_card_id.faculty_id.id) 
            # REMOVE OLD CARD MAPPING FROM FACULTY FORM
            query_replace = """update op_faculty set library_card_id =NULL where library_card_id =%s"""
            params_replace = (library_card_id.id, )                        

#         self.env.cr.execute(query, params)
#         val = map(lambda x:x[0],self.env.cr.fetchall())
#         if val : 
#             library_card = self.sudo().browse(val[0])
#             raise except_orm(_('Warning!'),
#                 _("Library card already %s exist for student")%(library_card.number))
        
        # REMOVE EXISTING CARD MAAPPING FROM STUDENT/FACULTY
        self.env.cr.execute(query_replace, params_replace)        
        # MAP LIBRARY CARD TO STUDENT/FACULTY
        self.env.cr.execute(query_udpate, params_update)

        return True

    @api.model
    def create(self,vals):
        """
        Map library card auto on student form
        """
        if vals.get("type") == "student" :
            vals["faculty_id"] = False
        
        else :
            vals["student_id"] = False

        # Check if chosen library card type and type is same
        type_brw = self.env['op.library.card.type'].browse(vals['library_card_type_id'])
        if 'library_card_type_id' in vals and 'type' in vals:
            if vals['library_card_type_id'] and vals['type']:
                if type_brw.type == 'student' and vals['type'] != 'student':
                    raise except_orm(_('Warning!'), _("Library Card Type should be Student!"))
                elif type_brw.type == 'faculty' and vals['type'] != 'faculty':
                    raise except_orm(_('Warning!'), _("Library Card Type should be Faculty!"))


            
        res = super(OpLibraryCard,self).create(vals)
        # CHECK IF CARD ALREADY ASSIGNED TO PARTNER
        
        self.map_library_card(res)
        return res

    @api.multi
    def write(self,vals):
        """
        Map library card auto on student form
        """
        if self.type == "student" :
            vals["faculty_id"] = False
        
        else :
            vals["student_id"] = False     

        # Check if chosen library card type and type is same
        if 'library_card_type_id' in vals or 'type' in vals:
            if 'library_card_type_id' not in vals:
                vals['library_card_type_id'] = self.library_card_type_id.id
            if 'type' not in vals:
                vals['type'] = self.type

            if vals['library_card_type_id'] or vals['type']:
                type_brw = self.env['op.library.card.type'].browse(vals['library_card_type_id'])
                if type_brw.type == 'student' and vals['type'] != 'student':
                    raise except_orm(_('Warning!'), _("Library Card Type should be Student!"))
                elif type_brw.type == 'faculty' and vals['type'] != 'faculty':
                    raise except_orm(_('Warning!'), _("Library Card Type should be Faculty!"))
       
        # CHECK IF CARD ALREADY ASSIGNED TO PARTNER
        
        library_card_id = self
        # CALL TO MAP PDC ID IN JOURNAL ENTRY
        res = super(OpLibraryCard,self).write(vals)
        self.map_library_card(library_card_id )        

        return res    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
