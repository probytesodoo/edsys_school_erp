# -*- coding: utf-8 -*-
##############################################################################
#
#    base_workingdays module for OpenERP, Manage working days
#    Copyright (C) 2016 SYLEAM Info Services (<http://www.syleam.fr>)
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of base_workingdays
#
#    base_workingdays is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    base_workingdays is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api, fields
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, rruleset, DAILY, MO, TU, WE, TH, FR, SA, SU
from datetime import datetime, timedelta
from pytz import utc, timezone
# from odoo.osv import osv
from odoo.tools.translate import _


class ResCompany(models.Model):
    _inherit = 'res.company'

    workingday_monday = fields.Boolean(string='Monday', default=True, help='Checked if employees of this company works on monday')
    workingday_tuesday = fields.Boolean(string='Tuesday', default=True, help='Checked if employees of this company works on tuesday')
    workingday_wednesday = fields.Boolean(string='Wednesday', default=True, help='Checked if employees of this company works on wednesday')
    workingday_thursday = fields.Boolean(string='Thursday', default=True, help='Checked if employees of this company works on thursday')
    workingday_friday = fields.Boolean(string='Friday', default=True, help='Checked if employees of this company works on friday')
    workingday_saturday = fields.Boolean(string='Saturday', default=False, help='Checked if employees of this company works on saturday')
    workingday_sunday = fields.Boolean(string='Sunday', default=False, help='Checked if employees of this company works on sunday')
    days_validation_ids = fields.One2many('res.company.day.validation','company_id', string='Days Validation', help='lines of fields to check on write')
    specific_working_date_ids = fields.One2many('res.company.workdate', 'company_id', string='Specific Working Date', help='list of dates worked, to bypass not worked dates')
    
    public_holiday_ids = fields.One2many('hr.public.holiday', 'company_id', string='Public Holiday')
    

    @api.model
    def verify_valid_date(self, date, delay=0):
        """
        Searches the first available date before or after 'date' argument
        Available dates are checked days, limited to work days from country
        """
        res_country_workdates_obj = self.env['res.country.workdates']
            
        # Check if the field 'date' is date or datetime format
        if len(date) == 10:
            date = datetime.strptime(date, '%Y-%m-%d')
            is_date = True
        else:
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            is_date = False
            # We will calculate datetime based on the timezone of the user if set
            if self.env.context.get('tz'):
                date = utc.localize(date, is_dst=True).astimezone(timezone(self.env.context['tz']))
                # Remove TZ in datetime
                date = date.strftime('%Y-%m-%d %H:%M:%S')
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            date = date.date()
                
        hr_public_holiday_obj = self.env['hr.public.holiday']
        hr_public_holiday_ids = hr_public_holiday_obj.search([])
        
        holiday_list = []
        #=======================================================================
        # for hr_public_holiday_id in hr_public_holiday_ids :
        #     public_holiday_from = datetime.strptime(hr_public_holiday_id.date_from, '%Y-%m-%d %H:%M:%S')
        #     public_holiday_to = datetime.strptime(hr_public_holiday_id.date_to, '%Y-%m-%d %H:%M:%S')
        #     #dates between two dates
        #     delta = public_holiday_to - public_holiday_from
        #     for i in range(delta.days + 1):
        #         holiday = public_holiday_from + timedelta(days=i)
        #         holiday_list.append(holiday)
        #=======================================================================
                
            #===================================================================
            # if date.date() >= public_holiday_from.date() and date.date() <= public_holiday_to.date():
            #     raise osv.except_osv(_('Warning!'), _('%s to %s is a Public Holiday.' %(public_holiday_from.date(), public_holiday_to.date())))
            #===================================================================
            
        # Initialize return value
        valid_dates = {}

        # Search all date between from and to date
        one_year = relativedelta(months=1)
#         if before:
#             start_date = date - one_year
#             end_date = date
#         else:
        start_date = date
        end_date = date + one_year
        company = self
        #for company in self:
        # List available weekdays
        available_weekdays = []
        if company.workingday_monday:
            available_weekdays.append(MO)
        if company.workingday_tuesday:
            available_weekdays.append(TU)
        if company.workingday_wednesday:
            available_weekdays.append(WE)
        if company.workingday_thursday:
            available_weekdays.append(TH)
        if company.workingday_friday:
            available_weekdays.append(FR)
        if company.workingday_saturday:
            available_weekdays.append(SA)
        if company.workingday_sunday:
            available_weekdays.append(SU)

        # List all possible days
        diff_day = rruleset()
        diff_day.rrule(rrule(DAILY, byweekday=available_weekdays, dtstart=start_date, until=end_date))
        
        # Exclude not worked days from list
        dates_list = list(diff_day)
        for hr_public_holiday_id in hr_public_holiday_ids :
            public_holiday_from = datetime.strptime(hr_public_holiday_id.date_from, '%Y-%m-%d')
            public_holiday_to = datetime.strptime(hr_public_holiday_id.date_to, '%Y-%m-%d')
            print 'public_holiday_from : ',public_holiday_from
            print 'public_holiday_to : ',public_holiday_to
            #dates between two dates
            delta = public_holiday_to - public_holiday_from
            print 'delta : ', delta
            for i in range(delta.days + 1):
                print 'iiiiiiiii', i
                print 'timedelta(days=i) : ',timedelta(days=i)
                holiday = public_holiday_from + timedelta(days=i)
                print 'holiday : ', holiday
                for d in dates_list :
                    if d.date() == holiday.date():
                        diff_day.exdate(holiday)
        diff_day = sorted(list(diff_day))
        # Deletes the not working days for the selected country
        if company.country_id:
            diff_day = res_country_workdates_obj.not_worked(company.country_id.id, diff_day, dates_list[0], dates_list[-1])
        
        # Add specific dates
        for spec in company.specific_working_date_ids:
            spec_date = datetime.strptime(spec.date, '%Y-%m-%d')
            if start_date.date() <= spec_date.date() and spec_date.date() <= end_date.date():
                diff_day.rdate(spec_date)

        # Choose the good day
        diff_day = sorted(list(diff_day))
        chosen_day = diff_day[delay]
        if chosen_day.date() != date :
            raise osv.except_osv(_('Warning!'), _('%s declared as a holiday.' %(date)))

        # Add the chosen day in return dict
        if is_date:
            valid_dates[company.id] = chosen_day.strftime('%Y-%m-%d')
        else:
            # We convert the date without timezone of user
            if self.env.context.get('tz'):
                chosen_day = timezone(self.env.context['tz']).localize(chosen_day, is_dst=True).astimezone(utc)
            valid_dates[company.id] = chosen_day.strftime('%Y-%m-%d %H:%M:%S')
        return valid_dates

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
