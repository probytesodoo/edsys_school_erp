# -*- coding: utf-8 -*-
from datetime import timedelta
from openerp import models, fields, api, _

class Category(models.Model):
    _name = 'category'

    name= fields.Char(size=256, string='Name', required=True)
    code= fields.Char(size=4, string='Code', required=True)
