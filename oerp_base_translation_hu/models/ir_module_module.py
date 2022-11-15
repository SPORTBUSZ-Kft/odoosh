# -*- coding: utf-8 -*-
"""
@author: Online ERP Hungary Kft.
"""


from odoo import models, tools, api
from odoo.modules import get_module_path, get_module_resource

import logging

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def _load_module_terms(self, modules, langs, overwrite=False):
        """Load PO files of the given modules for the given languages and
        the Hungarian from a custom location.
        """
        if "hu_HU" not in langs:
            return super()._load_module_terms(modules, langs, overwrite=overwrite)

        for lang in langs:

            if lang != "hu_HU":
                super()._load_module_terms(modules, [lang], overwrite=overwrite)

            else:

                for module_name in modules:
                    modpath = get_module_path(module_name)
                    if not modpath:
                        continue

                    need_load = True
                    for trans_file in (
                        get_module_resource(
                            "oerp_base_translation_hu", "data", "odoo-base", module_name, "i18n", "hu.po"
                        ),
                        get_module_resource(
                            "oerp_base_translation_hu", "data", "odoo-enterprise", module_name, "i18n", "hu.po"
                        ),
                        get_module_resource("oerp_base_translation_hu", "data", "other", module_name, "i18n", "hu.po"),
                    ):

                        if trans_file:
                            need_load = False
                            _logger.info("module %s: loading translation file (hu) for language hu_HU", module_name)
                            tools.trans_load(self._cr, trans_file, "hu_HU", verbose=False, overwrite=overwrite)

                            # quit from the loop
                            break

                    if need_load:
                        super()._load_module_terms([module_name], ["hu_HU"], overwrite=overwrite)

        return True
