import odoo
from odoo import models, fields, api, _
# from odoo.osv import osv
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import datetime

class finalized_attendance(models.Model):
    _name = 'finalized.attendance'

   # @api.one
    def get_previous_date(self, cr, uid, context):
        search_ids = self.search(cr, uid, [])
        from_date = False
        last_id = False
        for search_id in search_ids :
            last_id = search_id
    	if last_id:
            	last_rec = self.browse(cr, uid, last_id)
            	last_rec_to_date = datetime.datetime.strptime(str(last_rec.to_date), "%Y-%m-%d")
            	from_date = last_rec_to_date + datetime.timedelta(days=1)
            	return from_date

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    tags_or_all = fields.Selection([('all','All Employees' ),('tags','Employee Tags')],'Employee tags or All Employee?', default='all')
    tag_ids = fields.Many2many('hr.employee.category', 'employee_tags', 'emp_id', 'tag_id', 'Employee Tags')


    _defaults = {
        'from_date': get_previous_date,
    }


    @api.multi
    def submit_finalized_attendance_button(self):
        context = self._context
        hr_attendance_obj =self.env['hr.attendance']
        hr_attendance_ids = hr_attendance_obj.search([('name','>=', self.from_date),('name','<=', self.to_date)])
        for hr_attendance_id in hr_attendance_ids :
            if self.tags_or_all == 'tags' :
                tag_list = []
                for category in hr_attendance_id.employee_id.category_ids :
                   tag_list.append(category.id)
                for tag in self.tag_ids :
                    for category in tag_list :
                        if tag.id == category :
                            if hr_attendance_id.attendance_state in ['draft','seek_review']:
                                raise openerp.exceptions.AccessError(_("%s needs to be completed prior to finalizing" %(hr_attendance_id.employee_id.name)))
                            else :
                                hr_attendance_id.attendance_state = 'final'
                        else :
                            raise openerp.exceptions.AccessError(_("%s needs to be completed prior to finalizing" %(hr_attendance_id.employee_id.name)))
            else :
                if hr_attendance_id.attendance_state in ['draft','seek_review']:
                    raise openerp.exceptions.AccessError(_("%s needs to be completed prior to finalizing." %(hr_attendance_id.employee_id.name)))
                else :
                    hr_attendance_id.attendance_state = 'final'
        return True
