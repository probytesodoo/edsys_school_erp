# -*- coding: utf-8 -*-
from datetime import timedelta
from openerp import models, fields, api, _

class Religion(models.Model):
    _name = 'religion'

    name=fields.Char(size=256, string='Name', required=True)
    code=fields.Char(size=4, string='Code', required=True)
