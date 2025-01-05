""" 负责管理配置项"""

import copy
import json
import logging
from utils.pathManager import config_path

lg = logging.getLogger("配置")


def get_default():
    """返回默认配置"""
    return copy.deepcopy(basic_config)


def get_config():
    """返回已解析的配置"""
    return config


def get_raw_config():
    """返回未解析的原始设置"""
    return raw_config


def load_config():
    """读取配置文件"""
    lg.info("读取配置文件")
    global config, raw_config

    try:
        raw_config = json.loads(config_path.read_text())
        config = copy.deepcopy(raw_config)
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
        lg.warning("配置文件损坏, 重置配置文件")
        lg.warning("错误信息\n", exc_info=True)

        # 解析默认配置
        raw_config = get_default()
        config = copy.deepcopy(raw_config)
        config["login_api"] = config["login_api"].format(serverip=config["serverip"])
        config["check_url"] = config["check_url"].format(serverip=config["serverip"])
        return config

    lg.info("读取完成")


def save_config(config):
    # 保存配置文件
    lg.info("保存配置文件")
    config_path.write_text(json.dumps(config))
    load_config()  # 重新加载配置文件


config = None
raw_config = None

basic_config = {  # 默认配置
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
    lg.warning("配置文件不存在, 创建默认配置文件")
    config_path.touch()
    config_path.write_text(json.dumps(basic_config))

load_config()
