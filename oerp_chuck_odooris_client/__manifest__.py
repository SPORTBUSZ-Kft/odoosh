# -*- coding: utf-8 -*-
{
    "name": "Chuck odooris client",
    "version": "16.0.0.0.0",
    "author": "Online ERP Hungary Kft.",
    "website": "https://online-erp.hu/",
    "category": "OERP",
    "description": "Send request install and success cron",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "data/cron.xml",
    ],
    "license": "Other proprietary",
    "installable": True,
    "auto_install": False,
    "application": False,
    "external_dependencies": {
        "python": [
            "GitPython",
        ]
    },
}
