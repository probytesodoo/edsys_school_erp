# -*- coding: utf-8 -*-
from odoo import http

# class SalesForecastingArima(http.Controller):
#     @http.route('/sales_forecasting_arima/sales_forecasting_arima/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_forecasting_arima/sales_forecasting_arima/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_forecasting_arima.listing', {
#             'root': '/sales_forecasting_arima/sales_forecasting_arima',
#             'objects': http.request.env['sales_forecasting_arima.sales_forecasting_arima'].search([]),
#         })

#     @http.route('/sales_forecasting_arima/sales_forecasting_arima/objects/<model("sales_forecasting_arima.sales_forecasting_arima"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_forecasting_arima.object', {
#             'object': obj
#         })