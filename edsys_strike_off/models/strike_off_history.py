# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
from openerp import _
from openerp import api
from openerp import fields
from openerp import models
from openerp.exceptions import except_orm, Warning, RedirectWarning


class Strike_off_History(models.Model):
    _name = 'strike.off.history'
    _rec_name = 'student_id'

    _order = "last_strike_off_date desc"

    # name = fields.Char('Strike of History')
    student_id = fields.Many2one('res.partner', 'Student')
    last_strike_off_date = fields.Date(string='Last Strike-off Date')
    strike_history_line_ids = fields.One2many('strike.off.history.line', 'strike_history_id', 'Strike Off History line')

    @api.multi
    def unlink(self):
        """It will not allow to delete the history"""
        if self:
            raise except_orm(_('Warning!'), _("You can not delete the student strike-off history!"))
        return super(Strike_off_History, self).unlink()
    
class Strike_off_History_Line(models.Model):
    _name = 'strike.off.history.line'

    strike_off_date = fields.Date(string='Strike-off Date')
    activate_date = fields.Date(string='Activate Date')
    remark = fields.Char(string='Strke-off Reason')
    strike_history_id = fields.Many2one('strike.off.history', string="Strike off History")
