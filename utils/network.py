"""负责检查网络状态"""

import uuid
import socket
import subprocess
import logging as lg


def get_wifi_info():
    """获取wifi信息"""
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

    # 去除额外字符
    info = list(map(str.strip, info))

    # 去除空字符串
    for i in range(info.count("")):
        info.remove("")
    info = info[1:]

    # 替换中文冒号
    info = [i.replace("：", ":") for i in info]

    lg.debug(f"网络状态 -> 信息:\n{info}")

    dic = {}
    for i in info:
        try:
            key, value = i.split(":", 1)
            dic[key] = value
        except ValueError:
            lg.warning(f"网络状态 -> 信息格式错误:\n{i}")

    return dic


def get_mac():
    """获取MAC地址"""
    mac = hex(uuid.getnode())[2:]
    lg.debug(f"网络状态 -> MAC地址:\n{mac}")
    return mac


def get_ip():
    """获取IP地址"""
    ip = socket.gethostbyname(socket.gethostname())
    lg.debug(f"网络状态 -> IP地址:\n{ip}")
    return ip
