# -*- coding: utf-8 -*-
"""
@author: Online ERP Hungary Kft.
"""

from odoo import api, SUPERUSER_ID


def translation_hu_postinit(cr, registry=None):
    env = api.Environment(cr, SUPERUSER_ID, {})

    env["base.language.install"].create({
        'overwrite': True,
        'lang_ids': [(6, 0, [env.ref('base.lang_hu').id])],
    }).lang_install()
