# -*- coding: utf-8 -*-
"""
@author: Online ERP Hungary Kft.
"""

import os
from contextlib import closing
from .config import oerp_send_information, DEMO_KEY_HASH, oerp_get_actual_branch

from odoo import models, api, sql_db
from odoo.tools import config
import hashlib

from logging import getLogger

_logger = getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    @api.model
    def _oerp_get_registration_information(self):
        """Regisztrációs adatok szótár összeállítása, hogy el tudja küldeni a szervernek"""

        users_tbl = self.env["res.users"].sudo()
        modules_tbl = self.env["ir.module.module"]
        ICP = self.env["ir.config_parameter"].sudo()

        key_type = "other"
        eecode = ICP.get_param("database.enterprise_code")
        if eecode and hashlib.sha512(eecode.encode("utf-8")).hexdigest() == DEMO_KEY_HASH:
            key_type = "demo"
        enterprise_code_hash = ICP.get_param("database.enterprise_code.hash")

        # Összeálítom az aktív cégek adatait
        active_companies = dict()
        for company in self.env["res.company"].search([]):

            company_state = None
            if company.state_id:
                company_state = company.state_id.name

            active_companies[company.id] = {
                "name": company.name,
                "zip": company.zip,
                "street": company.street,
                "street2": company.street2,
                "city": company.city,
                "state": company_state,
                "country": company.country_id.name,
                "phone": company.phone,
                "email": company.email,
                "website": company.website,
                "vat": company.vat,
            }

        res = {
            "event": "periodic_update",
            "db": self.env.registry._db.dbname,
            "expire_date": ICP.get_param("database.expiration_date"),
            "expire_reason": ICP.get_param("database.expiration_reason", "trial"),
            "start_date": ICP.get_param("database.create_date"),
            "key_type": key_type,
            "enterprise_code": eecode,
            "enterprise_code_hash": enterprise_code_hash,
            "uuid": ICP.get_param("database.uuid"),
            "active_users": len(
                users_tbl.search([("active", "=", False)]).filtered(
                    lambda user: not user.has_group("base.group_portal") and not user.has_group("base.group_public")
                )
            ),
            "active_portal_users": len(
                users_tbl.search(
                    [
                        ("active", "=", False),
                    ]
                ).filtered(lambda user: user.has_group("base.group_portal") and not user.has_group("base.group_public"))
            ),
            "all_users": users_tbl.search_count(
                [
                    "|",
                    ("active", "=", False),
                    ("active", "=", True),
                ]
            ),
            "active_modules": [
                line.name
                for line in modules_tbl.search(
                    [
                        ("state", "in", ("installed", "to upgrade")),
                    ]
                )
            ],
            "active_companies": active_companies,
            # TODO: egyéb adatok, pl. base_url, stb.
            "db_storage": self._oerp_get_db_size(),
            "file_storage": self._oerp_get_storage_size(),
            "actual_branch": oerp_get_actual_branch(self.env),
        }
        return res

    @api.model
    def oerp_send_cron_info(self):
        """Cron működésének tesztelése és az Online ERP szerverére adatok küldése"""
        ICP = self.env["ir.config_parameter"].sudo()

        modules = oerp_send_information(
            "db/event",
            {
                "db": self.env.registry._db.dbname,
                "enterprise_code": ICP.get_param("database.enterprise_code"),
                "event": "get_modules",
                "username": self.env.user.name,
                "uid": self.env.user.id,
            },
        )
        _logger.debug("response of get_modules: %s", modules)
        res = modules.get("result")
        _logger.debug("result=%s", res)
        if isinstance(res, (list, tuple)):
            # TODO: modullista frissítése ha kapunk utasítást telepítésre

            # modulok telepítése
            uninstalled_modules = self.env["ir.module.module"].search(
                [("name", "in", res), ("state", "!=", "installed")]
            )
            if uninstalled_modules:
                uninstalled_modules.button_immediate_install()
                self.env.cr.commit()

        response = oerp_send_information("db/event", self._oerp_get_registration_information())
        _logger.debug("response of periodic_update: %s", response)
        # check whether we got the hash of the enterprise_code
        enterprise_code_hash = response.get("result", dict()).get("enterprise_code_hash")
        _logger.debug("enterprise_code_hash=%s", enterprise_code_hash)
        if enterprise_code_hash:
            ICP.set_param("database.enterprise_code.hash", enterprise_code_hash)

    @api.model
    def _oerp_get_storage_size(self):
        total_size = 0
        os_path_join = os.path.join
        os_getsize = os.path.getsize
        for storage_data in os.walk(os.path.join(config["data_dir"], "filestore", self.env.registry._db.dbname)):
            for f in storage_data[2]:
                fp = os_path_join(storage_data[0], f)
                total_size += os_getsize(fp)
        return total_size

    @api.model
    def _oerp_get_db_size(self):
        with closing(sql_db.db_connect(self.env.registry._db.dbname).cursor()) as cr:
            cr.execute("SELECT pg_database_size(%s)", (self.env.registry._db.dbname,))
            return cr.fetchone()[0]
