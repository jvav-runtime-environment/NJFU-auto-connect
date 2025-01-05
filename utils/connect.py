"""负责与登录服务器沟通"""

import json
import requests
import logging

from utils import network
from utils import configManager

lg = logging.getLogger("登录")


def get_json_data(text: str):
    """获取text中大括号包括的内容"""
    start = text.find("{")
    end = text.rfind("}")
    lg.debug(f"解析后数据: {text[start : end + 1]}")
    return text[start : end + 1]


def login(username, password, platform):
    """登录的主要逻辑"""
    config = configManager.get_config()

    platform = config["platform"]  # 平台
    login_api = config["login_api"]  # 登录api

    data = {
        "callback": "dr1003",
        "login_method": "1",
        "user_account": ",0," + username + platform,
        "user_password": password,
        "wlan_user_ip": network.get_ip(),  # 该项非必要，防出错
        "wlan_user_ipv6": "",
        "wlan_user_mac": network.get_mac(),  # 该项非必要，防出错
        "wlan_ac_ip": "",
        "wlan_ac_name": "",
        "jsVersion": "4.2.2",
        "terminal_type": "1",
        "lang": "zh-cn",
        "v": "1111",
        "lang": "zh",
    }

    r = requests.get(login_api, params=data)
    lg.info(f"响应代码: {r.status_code}")
    lg.debug(f"原始响应:\n{r.text}")
    r.raise_for_status()

    r_json = json.loads(get_json_data(r.text))
    if r_json["result"]:
        return [True, ""]
    else:
        return [False, r_json["msg"]]


def is_connected():
    """检查是否已经登录"""
    config = configManager.get_config()
    check_url = config["check_url"]  # 检查url

    r = requests.get(check_url)
    lg.info(f"(检测)响应代码: {r.status_code}")
    lg.debug(f"(检测)原始响应:\n{r.text}")
    r.raise_for_status()

    if "上网登录页" in r.text:
        return False
    return True
