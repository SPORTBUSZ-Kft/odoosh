# -*- coding: utf-8 -*-
"""
@author: Online ERP Hungary Kft.
"""

from odoo.addons.base.models.ir_cron import ir_cron
from odoo import api, SUPERUSER_ID, sql_db, models
from .config import oerp_send_information, DEMO_KEY_HASH, oerp_get_actual_branch
import hashlib
from logging import getLogger

_logger = getLogger(__name__)


def _send_cron_run_info(env):
    # Összegyűjtöm az azonosításhoz szükséges információka
    key_type = "other"
    eecode = env["ir.config_parameter"].get_param("database.enterprise_code")
    if eecode and hashlib.sha512(eecode.encode("utf-8")).hexdigest() == DEMO_KEY_HASH:
        key_type = "demo"
    enterprise_code_hash = env["ir.config_parameter"].get_param("database.enterprise_code.hash")
    db_name = env.registry._db.dbname
    cron_data = {
        "db": db_name,
        "event": "cron_run",
        "enterprise_code": eecode,
        "key_type": key_type,
        "enterprise_code_hash": enterprise_code_hash,
        "actual_branch": oerp_get_actual_branch(env),
    }
    _logger.debug("cron_data=%s", cron_data)
    api_oerp = oerp_send_information("db/event", cron_data)
    _logger.debug("Signalling OnlineERP about successful cron run. db=%s return=%s", db_name, api_oerp)


class IrCron(models.Model):
    _inherit = "ir.cron"

    @api.model
    def _oerp_send_cron_run_info(self):
        _send_cron_run_info(self.env)


# this monkey patch does not work on Odoo.sh
# old_process_jobs = ir_cron._process_jobs


# @classmethod
# def _process_jobs(cls, db_name):
#     """Cron lefutásakor az Online ERP szerverére adatok küldése"""
#     res = old_process_jobs(db_name)
#     db = sql_db.db_connect(db_name)
#     with db.cursor() as cr:
#         with api.Environment.manage():
#             env = api.Environment(cr, SUPERUSER_ID, {})
#             _send_cron_run_info(env)
#     return res


# ir_cron._process_jobs = _process_jobs
