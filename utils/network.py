"""负责检查网络状态"""

import uuid
import socket
import subprocess
import logging as lg


def get_wifi_info():
    result = subprocess.Popen(
        ["netsh", "wlan", "show", "interfaces"], stdout=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW, encoding="utf-8"
    )
    info = result.stdout.read().replace(" ", "").split("\n")
    lg.debug(f"获取到的网络信息: {info}")

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
    lg.info(f"本机MAC地址: {mac}")
    return mac


def get_ip():
    ip = socket.gethostbyname(socket.gethostname())
    lg.info(f"本机IP地址: {ip}")
    return ip
