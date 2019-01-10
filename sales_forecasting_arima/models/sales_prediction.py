# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
import base64
import logging
import os
from tempfile import TemporaryFile
import itertools

import csv
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    
try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

import pandas as pd
import numpy as np
from statsmodels.tsa.arima_model import ARIMA

_logger = logging.getLogger(__name__)

class SalesPrediction(models.Model):
    _name = 'sales.prediction'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Sales Forecasting"
    _order = 'date_prediction desc, id desc'
    
    @api.multi
    def _check_pdq_value_range(self):
        for prediction in self:
            if self.state == 'data' and prediction.pdq_value < 1 or prediction.pdq_value > 10:
                return False
            return True
        
    @api.multi
    def _check_forecast_step_value(self):
        for prediction in self:
            if self.state == 'data' and self.forecast_steps <= 0:
                return False
        return True
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    date_prediction = fields.Datetime(string='Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Created By', index=True, track_visibility='onchange', 
                                readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('data', 'Data Fetched'),
        ('validate', 'Model Tested'),
        ('forecast', 'Forecast'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    data_file = fields.Binary(string='Sales File', required=True, help='Actual sales file broken down by either day, week, month, quarter or year.', readonly=True, states={'draft': [('readonly', False)]})
    data_filename = fields.Char("Filename")
    data_line = fields.One2many('sales.data.line', 'prediction_id', string='Data Lines')
    prediction_line = fields.One2many('sales.prediction.line', 'prediction_id', string='Prediction Lines')
    model_test_line = fields.One2many('model.test.line', 'prediction_id', string='Model Test Lines')
#    test_data_size = fields.Float("Test Data Size",default=20.0)
    pdq_value = fields.Integer("PDQ Value",default=1, states={'validate': [('readonly', True)], 'forecast': [('readonly', True)], 'done': [('readonly', True)]})
    forecast_steps = fields.Integer("Steps",default=1, states={'forecast': [('readonly', True)], 'done': [('readonly', True)]})
    p_value = fields.Integer("P",default=1, states={'forecast': [('readonly', True)], 'done': [('readonly', True)]})
    d_value = fields.Integer("D",default=1, states={'forecast': [('readonly', True)], 'done': [('readonly', True)]})
    q_value = fields.Integer("Q",default=1, states={'forecast': [('readonly', True)], 'done': [('readonly', True)]})
#    search_filter = fields.Selection([
#        ('all', 'All'),
#        ('category', 'Product Category'),
#        ('product', 'Product'),
#        ], string='Filter', )
    
    _constraints = [
        (_check_pdq_value_range, 'P,D, Q Value should be between 1 and 10', []),
        (_check_forecast_step_value, 'Periods to forecast should be greater than 0', []),
    ]
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sales.prediction') or 'New'

        result = super(SalesPrediction, self).create(vals)
        return result
    
    @api.multi
    def _read_file(self, csv_data, filename):
        with TemporaryFile('w+') as buf:
            try:
                buf.write(base64.decodestring(csv_data))
                buf.seek(0)
                fileformat = os.path.splitext(filename)[-1][1:].lower()
    #            if fileformat not in ('csv'):
    #                raise UserError(_('You can only import csv files.'))

    #            elif fileformat in ('xls','xlsx'):
    #                book = xlrd.open_workbook(file_contents=self.file)
                reader = csv.reader(buf, quotechar='"', delimiter=',')
                df_data = pd.DataFrame(data=[row for row in reader])
            except Exception as e:
                _logger.exception('File unsuccessfully imported, due to format mismatch.')
                raise UserError(_('File not imported due to format mismatch or a malformed file. (Valid format is  .csv)\n\nTechnical Details:\n%s') % tools.ustr(e))
            
            df_data = df_data.drop(df_data.index[0]) ### Drop first row as it contains column header

            ### Check if count of column is equal to 2
            if len(df_data.columns) != 2:
                raise UserError(_('You can have only 2 columns in the file: Period and Sales.'))

            ### Check if file contains null values
            if df_data.isnull().values.sum() > 0:
                raise UserError(_('File cannot contain null values.'))
            
            df_data.columns = ['Period','Sales']
            df_data['Sales'] = df_data['Sales'].astype('float64')
            ### Check if column is of type period
            try:
                df_data['Period'] = df_data['Period'].apply(lambda p: pd.Period(p))
            except  ValueError, e:
                raise UserError(_("Data not of type period in first column. \n %s" % e))
            return df_data
    
    @api.multi
    def fetch_data(self):
        df_sales_data = self._read_file(self.data_file, self.data_filename)
        self.data_line.unlink()
        sales_data = [(0 ,0, {'name': row['Period'], 'value': row['Sales']}) for index,row in df_sales_data.iterrows()]

        try:
            self.write({'data_line': sales_data})
        except  ValueError, e:
            raise UserError(_("Exception while fetching data. \n %s" % e))
        
        self.write({'state': 'data'})
        return True
    
    @api.multi
    def action_draft(self):
        self.data_line.unlink()
        self.model_test_line.unlink()
        self.write({'state': 'draft', 'pdq_value': 1})
        return True
    
    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True
    
    @api.multi
    def action_back_to_data(self):
        self.write({'state': 'data'})
        return True
    
    @api.multi
    def action_back_to_validate(self):
        self.prediction_line.unlink()
        self.write({'state': 'validate'})
        return True
    
    @api.multi
    def action_done(self):
        self.write({'state': 'done'})
        return True
    
    def _do_best_fit(self, df):
        range_value = self.pdq_value + 1
        p=d=q=range(0,int(range_value))
        pdq = list(itertools.product(p,d,q))
        
        best_aic_value = 99999
        best_param = ()
        best_index = 0
        vals = []
        index = 0
        for param in pdq:
            try:
                model_arima = ARIMA(df.values,order=param)
                model_arima_fit = model_arima.fit()
                aic_value = model_arima_fit.aic
                if np.isnan(aic_value):
                    continue
                    
                vals.append((0,0,{
                    'prediction_id': self.id,
                    'name': str(param),
                    'value': aic_value,
                    'sequence': 10,
                    'best_fit': False
                }))
                if model_arima_fit.aic < best_aic_value:
                    best_aic_value = aic_value
                    best_param = param
                    best_index = index
                index += 1
            except:
                continue
        vals[best_index][2]['best_fit'] = True
        vals[best_index][2]['sequence'] = 1

        self.model_test_line.unlink()
        self.write({'model_test_line': vals})

        print "best_aic_value: ", best_aic_value
        print "best_param: ", best_param
        return True

    
    @api.multi
    def action_validate(self):
        df_sales_data = self._read_file(self.data_file, self.data_filename)
        df_sales_data = df_sales_data.set_index('Period')
        
        return self._do_best_fit(df_sales_data)
    
    @api.multi
    def action_to_forecast(self):
        best_param = eval(self.model_test_line.filtered(lambda l: l.best_fit)[0].name)
        
        self.write({
            'state': 'validate', 
            'p_value': best_param[0],
            'd_value': best_param[1],
            'q_value': best_param[2]
        })
        return True
        
    @api.multi
    def action_forecast(self):
        df_sales_data = self._read_file(self.data_file, self.data_filename)
        df_sales_data = df_sales_data.set_index('Period')
        
        param = (self.p_value,self.d_value,self.q_value)
        
        model_arima = ARIMA(df_sales_data.values, order=param)
        model_arima_fit = model_arima.fit()
        predictions = model_arima_fit.forecast(steps=self.forecast_steps)[0]

        ### Generating future period
        freqstr = df_sales_data.index.freqstr
        last_period = str(df_sales_data.index[-1])

        future_period = pd.date_range(start=last_period, periods=self.forecast_steps + 1, freq=freqstr)
        future_period = future_period[1:]
        future_period = future_period.to_period(freqstr) ### Convert DateTimeIndex to PeriodIndex
        future_period = future_period.to_series().astype(str).tolist() ### Convert PeriodIndex to List

        self.prediction_line.unlink()
        predicted_data = [(0 ,0, {'name': each_prediction[0], 'value': each_prediction[1]}) for each_prediction in zip(future_period, predictions)]
        self.write({'prediction_line': predicted_data, 'state': 'forecast'})

        return True
    
class SalesDataLine(models.Model):
    _name = 'sales.data.line'
    _description = 'Sales Data Line'
    _order = 'prediction_id, sequence, id'
    
    prediction_id = fields.Many2one('sales.prediction', string='Forecast Reference', required=True, ondelete='cascade', index=True, copy=False)
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Period', required=True)
    value = fields.Float('Value', required=True, default=0.0)
    
class SalesPredictionLine(models.Model):
    _name = 'sales.prediction.line'
    _description = 'Sales Prediction Line'
    _order = 'prediction_id, sequence, id'
    
    prediction_id = fields.Many2one('sales.prediction', string='Forecast Reference', required=True, ondelete='cascade', index=True, copy=False)
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Char(string='Period', required=True)
    value = fields.Float('Value', required=True, default=0.0)

class ModelTestLine(models.Model):
    _name = 'model.test.line'
    _description = 'Model Test Line'
    _order = 'prediction_id, sequence, value'
    
    prediction_id = fields.Many2one('sales.prediction', string='Model Reference', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Char(string='P,D,Q', required=True)
    value = fields.Float('AIC Value', required=True, default=0.0)
    sequence = fields.Integer(string='Sequence', default=10)
    best_fit = fields.Boolean("Best Fit")