# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import datetime as d
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning

class Batch(models.Model):

    _name = 'batch'
    _inherit = 'batch'
    code= fields.Char(size=8, string='Code', required=True)
    name= fields.Char(size=32, string='Name', required=True)
    start_date= fields.Date(string='Start Date', required=True)
    end_date= fields.Date(string='End Date', required=True)
    course_ids = fields.Many2many('course', 'batch_name', 'course_name',string="Classes")
    month_ids = fields.One2many('fee.month','batch_id',string='Month')
    effective_date = fields.Date(string="Effective Date")
    term_ids = fields.One2many('acd.term','batch_id',string="Academic Terms")
    current_academic = fields.Boolean('Current Academic Year',compute='compute_current_year')
    advance_payment_reconcile_date = fields.Date('Advance Payment Reconcile Date')


    @api.multi
    def compute_current_year(self):
        """
        this method is use to make current academic year
        base on current date.
        -----------------------------------------
        :return :
        """
        for record in self:
            s_date = datetime.strptime(record.start_date,"%Y-%m-%d").date()
            e_date = datetime.strptime(record.end_date,"%Y-%m-%d").date()
            c_date = d.date.today()
            if s_date <= c_date <= e_date:
                record.current_academic = True
            else:
                record.current_academic = False

       
    @api.model
    def create(self,vals):
        """
        add validation on record creation time.
        ---------------------------------------
        :param vals:
        :return:
        """
        prev_records=self.search(['|','&',('start_date','<=',vals['start_date']),('end_date','>=',vals['start_date']),'&',('start_date','<=',vals['end_date']),('end_date','>=',vals['end_date'])])
        if len(prev_records)!=0:
            raise except_orm(_("Warning...You are selecting a wrong duration!"), _('This duration is already comes under another academic year'))
        return super(Batch,self).create(vals)

    @api.multi
    def write(self,vals):
        """
        override write method and
        add validation on write record.
        -------------------------------
        :param vals: dictonary
        :return:
        """
        if 'start_date' not in vals:
            vals['start_date']=self.start_date
        if 'end_date' not in vals:
            vals['end_date']=self.end_date
        prev_records=self.search(['|','&',('start_date','<=',vals['start_date']),('end_date','>=',vals['start_date']),'&',('start_date','<=',vals['end_date']),('end_date','>=',vals['end_date'])])
        for each in prev_records:
            if each.id != self.id:
                raise except_orm(_("Warning...You are selecting a wrong duration!"), _('This duration is already comes under another academic year'))
        return super(Batch,self).write(vals)


    @api.model
    def months_between(self,start_date,end_date):
        months = []
        years = []
        month_year = []
        cursor = start_date
        while cursor <= end_date:
            tpl = (int(cursor.month),int(cursor.year))
            if cursor.month not in months or tpl not in month_year:
                if cursor.month not in months:
                    months.append(cursor.month)
                month_year.append(tpl)
            cursor += timedelta(weeks=1)
        return month_year

    @api.onchange('start_date','end_date')
    def _compute_month_of_batch(self):
        """
        - this method used to compute months record,
          based on start date and end date.
        - month record use for fee calculation,
        --------------------------------------------
        @param self : object pointer
        @worning : if start date greter then end date
        """
        if self.start_date and self.end_date:
            st_date = datetime.strptime(self.start_date , '%Y-%m-%d')
            en_date = datetime.strptime(self.end_date , '%Y-%m-%d')
            if st_date < en_date:
                s_date = datetime.strptime(self.start_date,"%Y-%m-%d").date()
                e_date = datetime.strptime(self.end_date,"%Y-%m-%d").date()
                month_in_between = self.months_between(s_date, e_date)
                total_month = len(month_in_between)
                if total_month % 2 == 0:
                    qter_month = total_month / 2
                else:
                    total_month += 1
                    qter_month = total_month / 2
                count = 0
                month_data_list = []
                for month_bet in month_in_between:
                    count += 1
                    if count % 2 == 0:
                        alt = False
                    else:
                        alt = True
                    if count % 3 == 1:
                        qtr_month = True
                    else:
                        qtr_month = False
                    if count in [1,qter_month+1]:
                        qtr = True
                    else:
                        qtr = False
                    month_chk_rec = self.month_ids.search([('name','=',month_bet[0]),('year','=',month_bet[1])])
                    if month_chk_rec.id:
                        month_dict = {
                            'code': count,
                            'name': month_bet[0],
                            'year': month_bet[1],
                            'alt_month': alt,
                            'quater_month': qtr,
                            'qtr_month': qtr_month,
                            }
                        month_data_list.append((4,month_chk_rec.id))
                        month_data_list.append((1,month_chk_rec.id,month_dict))
                    else:
                        month_data_list.append((0,0,{
                            'code': count,
                            'name': month_bet[0],
                            'year': month_bet[1],
                            'alt_month': alt,
                            'quater_month': qtr,
                            'qtr_month': qtr_month,
                            }))
                self.month_ids = month_data_list
            else:
                raise except_orm(_('Warning!'),
                    _("end date should be greater than start date !"))