from openerp import models, fields, api, _
from datetime import date,datetime


class nationality(models.Model):

   _name = 'nationality'

   name = fields.Char(string="name",size=126)
   code = fields.Char(string ="code",size=126)
   country_id = fields.Many2one('res.country',string="Country")