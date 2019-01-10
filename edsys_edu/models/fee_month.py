# # -*- coding: utf-8 -*-
# from datetime import timedelta
# from openerp import models, fields, api, _
#
# class fee_month(models.Model):
#
#     _name = 'fee.month'
#
#     List_Of_Month = [
#         (1,'January'),
#         (2,'February'),
#         (3,'March'),
#         (4,'April'),
#         (5,'May'),
#         (6,'June'),
#         (7,'July'),
#         (8,'August'),
#         (9,'September'),
#         (10,'October'),
#         (11,'November'),
#         (12,'December'),
#         ]
#
#     code= fields.Char(string='Code')
#     name= fields.Selection(List_Of_Month,string='Month')
#     year = fields.Char(string="Year")
#     batch_id = fields.Many2one('batch',string='Batch')
#     alt_month = fields.Boolean('Alternate Month')
#     quater_month = fields.Boolean('Half Month')
#     qtr_month = fields.Boolean('Quater Month')