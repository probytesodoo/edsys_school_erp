# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import time
from datetime import datetime, date
from odoo.exceptions import except_orm


class RegistrationInherit(models.Model):

    _inherit = 'registration'

    @api.multi
    def confirm_payment(self):
        library_obj = self.env['op.library.card']
        card_obj = self.env['op.library.card.type']

        res = super(RegistrationInherit, self).confirm_payment()
        student_type_card = card_obj.search([('type', '=', 'student')])
        if not student_type_card:
            raise except_orm(_('Warning!'), _("Please create library card type of STUDENT!!"))
        else:
            library_obj.sudo().create({'number': self.student_id.student_id,
                                       'issue_date': self.admission_date,
                                       'library_card_type_id': student_type_card.id,
                                       'type': 'student',
                                       'student_id': self.student_id.id,
                                       'active': True,
                                       'return_days': 0,
                                   })
        return res


class TransferCertificateInherit(models.Model):

    _inherit = 'trensfer.certificate'

    @api.multi
    def send_mail_return_library_book(self):
        """
        send mail saying return library books.
        -------------------------------------
        :return:
        """
        for tc_student_rec in self:
            flag = False
            data = ''
            for book_line in self.name.book_movement_lines:
                if book_line.state == 'issue':
                    author = ''
                    for auth in book_line.book_id.author_ids:
                        author += auth.name + ', '
                    author = author[:-2]
                    data += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (book_line.book_id.name, author, book_line.issued_date, book_line.return_date or '')
                    flag = True

            if flag:
                email_server = self.env['ir.mail_server']
                email_sender = email_server.search([], limit=1)
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('openeducat_library', 'email_template_return_library_books')[1]
                template_rec = self.env['mail.template'].sudo().browse(template_id)
                body_html = template_rec.body_html
                body_dynamic_html = template_rec.body_html
                body_dynamic_html += '<p>Student Name: %s</p>' % (tc_student_rec.name.name)
                body_dynamic_html += '<p>Grade: %s</p>' % (tc_student_rec.name.course_id.name)
                body_dynamic_html += '<p>Section:%s </p>' % (tc_student_rec.name.student_section_id.name or '')
                body_dynamic_html += '<table border=1 width=100% align=center>'
                body_dynamic_html += '<tr><td><b>Book Name</b></td><td><b>Author</b></td><td><b>Issued On</b></td><td><b>Due Date</b></td></tr></tr>%s</table>'%(data)
                template_rec.sudo().write({'email_to': tc_student_rec.name.parents1_id.parents_email,
                                           'email_from': email_sender.smtp_user,
                                           'email_cc': '',
                                           'body_html': body_dynamic_html})
                template_rec.send_mail(self.id)
                template_rec.body_html = body_html
        return True

    @api.multi
    def come_to_ministry_approval(self):
        flag = False
        books = ''
        # without returning library books, you cannot proceed further
        for book_line in self.name.book_movement_lines:
            if book_line.state == 'issue':
                books += book_line.book_unit_id.name + ', '
                flag = True

        if flag:
            books = books[:-2]
            raise except_orm(_('Warning!'), _("%s need to return library books %s to proceed further!!")
                             % (self.name.name, books))

        # Deactivate the library card
        self.env.cr.execute("select id from op_library_card where student_id =%s", (self.name.id,))
        library_card = map(lambda x: x[0], self.env.cr.fetchall())

        if not library_card:
            raise except_orm(_('Warning!'), _("Library Card is not available for %s!!") % self.name.name)
        elif len(library_card) > 1:
            raise except_orm(_('Warning!'), _("There are %s library cards available for %s." + '\n' +
            "There should be only one library card for individual!!") % (len(library_card), self.name.name))
        else:
            library = self.env['op.library.card'].sudo().search([('id', '=', library_card[0])])
            library.active = False
        res = super(TransferCertificateInherit, self).come_to_ministry_approval()
        return res

    @api.multi
    def confirm_tc_calculation(self):
        res = super(TransferCertificateInherit, self).confirm_tc_calculation()
        # send mail for library books return
        self.send_mail_return_library_book()
        return res

