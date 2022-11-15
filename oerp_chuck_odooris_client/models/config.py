# -*- coding: utf-8 -*-
"""
@author: Online ERP Hungary Kft.
"""
import requests
import random
from logging import getLogger
import git


BASE_URL = "https://www.online-erp.hu"
BASE_DBNAME = "tsabi-odoo-sh-13-0-onlineerp-prod-990301"
CALL_TIMEOUT = 10.0
SESSION_TIMEOUT = 12.0

DEMO_KEY_HASH = "93d57520ba57afdaaa336e5ff4a5c5b82f8bed4ff1b15d5d6a0403e11b2fd60c841d2c2bc746bfcdfe2322cdeb69998c2d20a07fa7442a6ef29c60611386f19d"

try:
    # create custom_db_config.py file next to this to set own connection information
    from .custom_db_config import *
except ImportError:
    pass

_logger = getLogger(__name__)


def oerp_send_information(url, data):
    """Itt elküldi a megadott url-re a kívánt adatokat"""

    try:
        req_session = requests.get(f"{BASE_URL}/web/login?db={BASE_DBNAME}", timeout=SESSION_TIMEOUT)
        api_data = {
            "id": random.randint(1000, 50000),
            "jsonrpc": "2.0",
            "method": "call",
            "params": data,
        }
        call_oerp_api = requests.post(
            f"{BASE_URL}/chuck_odooris/{url}",
            json=api_data,
            cookies=req_session.cookies,
            timeout=CALL_TIMEOUT,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        _logger.info(f"API send data {BASE_URL}.")
        return call_oerp_api.json()
    except Exception as e:
        _logger.error("OnlineERP API connection error")
        _logger.error(e)
        return {}


def oerp_get_actual_branch(env, repo_path: str = "/home/odoo/src/user"):
    """Get actual branch in Odoo.sh."""
    repo = git.Repo(repo_path)
    for branch in repo.branches:
        if branch.name in env.registry._db.dbname:
            return branch.name
