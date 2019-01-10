# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Public Holidays",
    'images': [],
    'summary': """Manage public holidays""",
    'author': "Edsys",
    'website': "http://www.redbytes.in",
    'category': 'Human Resources',
    'version': '1.0',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_public_holiday_security.xml',
        'data/hr_holidays_status.xml',
        'views/hr_public_holiday.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
