# -*- coding: utf-8 -*-
"""
@author: Online ERP Hungary Kft.
"""

from .config import oerp_send_information

from odoo import models
from odoo.addons.base.models.ir_module import assert_log_admin_access

from logging import getLogger

_logger = getLogger(__name__)


class Module(models.Model):
    _inherit = "ir.module.module"

    @assert_log_admin_access
    def button_install(self):
        deps = self.upstream_dependencies(exclude_states=("uninstalled"))
        res = super(Module, self).button_install()
        (deps | self)._chuck_odooris_sync("module_install")
        return res

    @assert_log_admin_access
    def button_uninstall(self):
        deps = self.downstream_dependencies()
        res = super(Module, self).button_uninstall()
        (deps | self)._chuck_odooris_sync("module_uninstall")
        return res

    def _chuck_odooris_sync(self, action):
        data = {
            "db": self.env.registry._db.dbname,
            "event": action,
            "enterprise_code": self.env["ir.config_parameter"].sudo().get_param("database.enterprise_code"),
            "enterprise_code_hash": self.env["ir.config_parameter"].sudo().get_param("database.enterprise_code.hash"),
            "module_name": self.mapped("name"),
            "username": self.env.user.name,
            "uid": self.env.user.id,
        }
        return oerp_send_information("db/event", data)
