# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo import models
from odoo.http import request

import odoo


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        res = super(Http, self).session_info()
        res.update({
            "config_id": user.pos_config.id if user.pos_config else 1,
        })
        return res
