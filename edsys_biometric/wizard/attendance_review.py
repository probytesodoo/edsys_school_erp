from odoo import models, fields, api, _
from odoo import models

class attendance_review_wizard(models.Model):
    """
        A wizard to manage the change of users' passwords
    """

    _name = "attendance.review.wizard"
    _description = "Attendance Review Wizard"
    

    attendance_review_ids = fields.One2many('attendance.review', 'wizard_id', string='Attendance Review')
    

    def _default_attendance_review_ids(self, cr, uid, context=None):
        attendance_list = []
        if context is None:
            context = {}
        attendance_model = self.pool['hr.attendance']
        attendance_ids = context.get('active_model') == 'hr.attendance' and context.get('active_ids') or []
        for attendance in attendance_model.browse(cr, uid, attendance_ids, context=context) :
            if attendance.attendance_state == 'draft' : 
                attendance_vals = {'justification' : attendance.justification,'attendance_id': attendance.id, 'action_time': attendance.name, 'action' : attendance.action, 'employee_id' : attendance.employee_id}
                attendance_list.append( (0, 0, attendance_vals))
        return attendance_list

    _defaults = {
        'attendance_review_ids': _default_attendance_review_ids,
    }

    def submit_attendance_review_button(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids, context=context)[0]
        line_ids = [attendance_review_id.id for attendance_review_id in wizard.attendance_review_ids]
        self.pool.get('attendance.review').submit_attendance_review_button(cr, uid, line_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

class attendance_review(models.Model):
    """
        A model to configure users in the change password wizard
    """

    _name = 'attendance.review'
    _description = 'Attendance Review'
    
    wizard_id = fields.Many2one('attendance.review.wizard', string='Wizard')
    attendance_id = fields.Many2one('hr.attendance', string='Employee Attendance')
    action = fields.Selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('action','Action')], 'Action')
    employee_id = fields.Many2one('hr.employee', "Employee")
    action_time = fields.Datetime('User Login')
    justification = fields.Char('Justification')
    

    def submit_attendance_review_button(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.justification :
                line.attendance_id.write({'review_tags' : 'corrected','justification': line.justification, 'attendance_state': 'seek_review'})
        
        
