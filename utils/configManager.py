""" 负责管理配置项"""

import copy
import json
import traceback
import logging as lg
from utils.pathManager import config_path

inited = False
if not inited:  # 防止多次加载导致覆盖
    config_path = config_path
    basic_config = {
        "username": "",
        "password": "",
        "serverip": "10.51.2.20",
        "login_api": "http://{serverip}:801/eportal/portal/login",
        "check_url": "http://{serverip}",
        "wifiname": "CMCC-EDU",
        "platform": "@cmcc",
        "interval": 10,
        "startup": False,
    }

    if not config_path.exists():
        config_path.touch()
        config_path.write_text(json.dumps(basic_config))
        lg.info("未找到配置文件, 使用默认配置")

    inited = True


def get_default():
    return copy.deepcopy(basic_config)


def get_raw_config():
    # 返回未解析的原始设置
    return json.loads(config_path.read_text())


def get_config():
    try:
        config = json.loads(config_path.read_text())
        config["login_api"] = config["login_api"].format(serverip=config["serverip"])
        config["check_url"] = config["check_url"].format(serverip=config["serverip"])

        # 保证配置项完整
        assert "username" in config
        assert "password" in config
        assert "serverip" in config
        assert "login_api" in config
        assert "check_url" in config
        assert "wifiname" in config
        assert "platform" in config
        assert "interval" in config
        assert "startup" in config

    except (KeyError, json.JSONDecodeError, AssertionError):
        lg.warning(f"配置文件损坏, 使用默认配置。错误信息: {traceback.format_exc()}")

        # 解析默认配置
        config = get_default()
        config["login_api"] = config["login_api"].format(serverip=config["serverip"])
        config["check_url"] = config["check_url"].format(serverip=config["serverip"])
        return config

    return config


def save_config(config):
    json.dump(config, open(config_path, "w", encoding="utf-8"))
