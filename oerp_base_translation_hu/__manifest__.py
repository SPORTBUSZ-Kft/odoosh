# -*- coding: utf-8 -*-
# © 2011-2022 Online ERP Hungary Kft.

{
    "name": "Magyar nyelv",
    "version": "2.0.0",
    "category": "Online ERP/Translation",
    "license": "Other proprietary",
    "summary": "Valódi magyarítás az Online ERP által",
    "author": "Online ERP Hungary Kft.",
    "website": "https://online-erp.hu",
    "depends": ["base", "web"],
    "assets": {
        "web.assets_backend": [
            "oerp_base_translation_hu/static/src/scss/mail_chatter_fix.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": True,
    "post_init_hook": "translation_hu_postinit",
}
