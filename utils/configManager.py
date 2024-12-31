""" 负责管理配置项"""

import copy
import json
import logging as lg
from utils.pathManager import config_path


def get_default():
    # 返回默认配置
    return copy.deepcopy(basic_config)


def get_config():
    # 返回已解析的配置
    return config


def get_raw_config():
    # 返回未解析的原始设置
    return json.loads(config_path.read_text())


def load_config():
    # 读取配置文件
    lg.info("配置管理器 -> 读取配置文件")
    global config
    global raw_config

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
        lg.warning("配置管理器 -> 配置文件损坏, 重置配置文件")
        lg.warning("配置管理器 -> 错误信息\n", exc_info=True)

        # 解析默认配置
        config = get_default()
        config["login_api"] = config["login_api"].format(serverip=config["serverip"])
        config["check_url"] = config["check_url"].format(serverip=config["serverip"])
        return config

    lg.info("配置管理器 -> 读取完成")
    return config


def save_config(config):
    # 保存配置文件
    lg.info("配置管理器 -> 保存配置文件")
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config, f)
        json.dump(config, f)
    lg.info("配置管理器 -> 保存完成")


config = None
raw_config = None

lg.info("配置管理器 -> 初始化")
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
    lg.warning("配置管理器 -> 配置文件不存在, 创建默认配置文件")
    config_path.touch()
    config_path.write_text(json.dumps(basic_config))

config = load_config()
lg.info("配置管理器 -> 初始化完成")
