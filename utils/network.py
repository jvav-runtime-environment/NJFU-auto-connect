"""负责检查网络状态"""

import uuid
import socket
import subprocess
import logging as lg


def get_wifi_info():
    result = subprocess.Popen(
        ["netsh", "wlan", "show", "interfaces"],
        stdout=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    # 检测编码
    raw = result.stdout.read()
    try:
        raw.decode("utf-8")
        encoding = "utf-8"
    except UnicodeDecodeError:
        encoding = "gbk"

    # 格式化信息
    info = raw.decode(encoding).replace(" ", "").split("\n")
    lg.debug(f"网络状态 -> 信息:\n{info}")

    dic = {}
    for i in info:
        try:
            key, value = i.split(":")
            dic[key] = value
        except:
            pass

    return dic


def is_connected():
    result = get_wifi_info()
    if "SSID" in result:
        return True
    return False


def is_the_wifi(name):
    result = get_wifi_info()
    if result["SSID"] == name:
        return True
    return False


def get_mac():
    mac = hex(uuid.getnode())[2:]
    lg.debug(f"网络状态 -> MAC地址:\n{mac}")
    return mac


def get_ip():
    ip = socket.gethostbyname(socket.gethostname())
    lg.debug(f"网络状态 -> IP地址:\n{ip}")
    return ip
