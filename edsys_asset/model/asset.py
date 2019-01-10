# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _
from odoo import models, fields, api, _


class account_asset_asset(models.Model):
    _inherit = 'account.asset.asset'
    
    def _compute_board_undone_dotation_nb(self, cr, uid, asset, depreciation_date, total_days, context=None):
        undone_dotation_number = asset.method_number
        if asset.method_time == 'end':
            end_date = datetime.strptime(asset.method_end, '%Y-%m-%d').date()
            undone_dotation_number = 0
            while depreciation_date <= end_date:
                depreciation_date = (datetime(depreciation_date.year, depreciation_date.month, depreciation_date.day) + relativedelta(months=+asset.method_period))
		depreciation_date = depreciation_date.date()
                undone_dotation_number += 1
        if asset.prorata:
            undone_dotation_number += 1
        return undone_dotation_number
    



    def _compute_board_amount(self, cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=None):
        #by default amount = 0
        account_fiscal_year_obj = self.pool.get('account.fiscalyear')
        amount = 0
        if i == undone_dotation_number:
            amount = residual_amount
        else:
            if asset.method == 'linear':
                prorata_days = 0
                days = total_days - float(depreciation_date.strftime('%j'))
			
	        prorata_days = 0
                account_fiscal_year_ids = account_fiscal_year_obj.search(cr, uid, [])
                for account_fiscal_year_id in account_fiscal_year_ids:
                    account_fiscal_year_rec = account_fiscal_year_obj.browse(cr,uid,account_fiscal_year_id)
                    
                    fiscal_year_start_datetime = datetime.strptime(account_fiscal_year_rec.date_start, "%Y-%m-%d")
                    fiscal_year_stop_datetime = datetime.strptime(account_fiscal_year_rec.date_stop, "%Y-%m-%d")
                    
                    fiscal_year_start_date = fiscal_year_start_datetime.date()
                    fiscal_year_stop_date = fiscal_year_stop_datetime.date()
                    cal_days = fiscal_year_stop_date -  fiscal_year_start_date 
                    prorata_days = cal_days.days + 1


                amount = (amount_to_depr / asset.method_number) / total_days * prorata_days
                if asset.prorata:
                    purchase_datetime = datetime.strptime(asset.purchase_date, '%Y-%m-%d')
                    account_fiscal_year_ids = account_fiscal_year_obj.search(cr, uid, [])
                    for account_fiscal_year_id in account_fiscal_year_ids:
                        account_fiscal_year_rec = account_fiscal_year_obj.browse(cr,uid,account_fiscal_year_id)
                        
                        fiscal_year_start_datetime = datetime.strptime(account_fiscal_year_rec.date_start, "%Y-%m-%d")
                        fiscal_year_stop_datetime = datetime.strptime(account_fiscal_year_rec.date_stop, "%Y-%m-%d")
                        
                        purchase_date = purchase_datetime.date()
                        fiscal_year_start_date = fiscal_year_start_datetime.date()
                        fiscal_year_stop_date = fiscal_year_stop_datetime.date()
                        if  purchase_date >= fiscal_year_start_date and purchase_date <= fiscal_year_stop_date:
                            cal_days = fiscal_year_stop_date -  purchase_date 
                            prorata_days = cal_days.days + 1
                    amount = amount_to_depr / asset.method_number
                    if i == 1:
                        amount = (amount_to_depr / asset.method_number) / total_days * prorata_days
                    elif i == undone_dotation_number:
                        amount = (amount_to_depr / asset.method_number) / total_days * (total_days - days)
            elif asset.method == 'degressive':
	        prorata_days = 0
		amount = residual_amount * asset.method_progress_factor
                if asset.prorata:
                    account_fiscal_year_ids = account_fiscal_year_obj.search(cr, uid, [])
                    for account_fiscal_year_id in account_fiscal_year_ids:
                        account_fiscal_year_rec = account_fiscal_year_obj.browse(cr,uid,account_fiscal_year_id)
                        
                        fiscal_year_start_datetime = datetime.strptime(account_fiscal_year_rec.date_start, "%Y-%m-%d")
                        fiscal_year_stop_datetime = datetime.strptime(account_fiscal_year_rec.date_stop, "%Y-%m-%d")
                        
                        depreciation_date_updated = depreciation_date.date()
                        fiscal_year_start_date = fiscal_year_start_datetime.date()
                        fiscal_year_stop_date = fiscal_year_stop_datetime.date()
                        
                        if  depreciation_date_updated >= fiscal_year_start_date and depreciation_date_updated <= fiscal_year_stop_date:
                            cal_days = fiscal_year_stop_date -  depreciation_date_updated 
                            prorata_days = cal_days.days + 1
                    days = total_days - float(depreciation_date.strftime('%j'))
                    
                    
                    if i == 1:
                        amount = (residual_amount * asset.method_progress_factor) / total_days * prorata_days
                    elif i == undone_dotation_number:
                        amount = (residual_amount * asset.method_progress_factor) / total_days * (total_days - days)
        return amount


    def compute_depreciation_board(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        account_fiscal_year_obj = self.pool.get('account.fiscalyear')
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.value_residual == 0.0:
                continue
            posted_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_check', '=', True)],order='depreciation_date desc')
            old_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
            
            if old_depreciation_line_ids:
                depreciation_lin_obj.unlink(cr, uid, old_depreciation_line_ids, context=context)

            amount_to_depr = residual_amount = asset.value_residual
            if asset.prorata:
                depreciation_date = datetime.strptime(self._get_last_depreciation_date(cr, uid, [asset.id], context)[asset.id], '%Y-%m-%d')
            else:
                purchase_datetime = datetime.strptime(asset.purchase_date, '%Y-%m-%d')
                   
                #if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
                if (len(posted_depreciation_line_ids)>0):
                    last_depreciation_date = datetime.strptime(depreciation_lin_obj.browse(cr,uid,posted_depreciation_line_ids[0],context=context).depreciation_date, '%Y-%m-%d')
                    depreciation_date = (last_depreciation_date+relativedelta(months=+asset.method_period))
                else:
                    account_fiscal_year_ids = account_fiscal_year_obj.search(cr, uid, [])
                    for account_fiscal_year_id in account_fiscal_year_ids:
                        account_fiscal_year_rec = account_fiscal_year_obj.browse(cr,uid,account_fiscal_year_id)
                        
                        fiscal_year_start_datetime = datetime.strptime(account_fiscal_year_rec.date_start, "%Y-%m-%d")
                        fiscal_year_stop_datetime = datetime.strptime(account_fiscal_year_rec.date_stop, "%Y-%m-%d")
                        
                        purchase_date = purchase_datetime.date()
                        fiscal_year_start_date = fiscal_year_start_datetime.date()
                        fiscal_year_stop_date = fiscal_year_stop_datetime.date()
                        
                        if  purchase_date >= fiscal_year_start_date and purchase_date <= fiscal_year_stop_date:
                            depreciation_date = fiscal_year_start_date
                            
            if depreciation_date:   
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
                total_days = (year % 4) and 365 or 366
                
    
                undone_dotation_number = self._compute_board_undone_dotation_nb(cr, uid, asset, depreciation_date, total_days, context=context)
                for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                    i = x + 1
                    amount = self._compute_board_amount(cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=context)
                    residual_amount -= amount
                    vals = {
                         'amount': amount,
                         'asset_id': asset.id,
                         'sequence': i,
                         'name': str(asset.id) +'/' + str(i),
                         'remaining_value': residual_amount,
                         'depreciated_value': (asset.purchase_value - asset.salvage_value) - (residual_amount + amount),
                         'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                    }
                    depreciation_lin_obj.create(cr, uid, vals, context=context)
                    # Considering Depr. Period as months
                    depreciation_date = (datetime(year, month, day) + relativedelta(months=+asset.method_period))
                    day = depreciation_date.day
                    month = depreciation_date.month
                    year = depreciation_date.year
        return True

