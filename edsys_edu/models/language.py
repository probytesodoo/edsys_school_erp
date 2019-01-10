from odoo import models, fields, api, _
from datetime import date,datetime


class Language(models.Model):

    _inherit = 'res.lang'

    is_optional = fields.Boolean('Is Optional')
    iso_code = fields.Char('ISO code', size=16, help='This ISO code is the name of po files to use for translations',required=False)
    direction = fields  .Selection([('ltr', 'Left-to-Right'), ('rtl', 'Right-to-Left')], 'Direction',required=False)
    date_format = fields.Char('Date Format',required=False)
    time_format = fields.Char('Time Format',required=False)
    grouping = fields.Char('Separator Format',required=False, help="The Separator Format should be like [,n] where 0 < n :starting from Unit digit.-1 will end the separation. e.g. [3,2,-1] will represent 106500 to be 1,06,500;[1,2,-1] will represent it to be 106,50,0;[3] will represent it as 106,500. Provided ',' as the thousand separator in each case.")
    decimal_point = fields.Char('Decimal Separator',required=False)
    thousands_sep = fields.Char('Thousands Separator', required=False)
