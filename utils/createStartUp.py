"""负责管理开机自启动"""

import sys
import winreg
import logging as lg
from utils.pathManager import current_dir

try:
    if __nuitka_binary_dir is not None:  # type: ignore
        is_exe = True
except NameError:
    is_exe = False


# 判断是否为打包的程序
# 释放自启动bat
if is_exe:
    startup_cmd = f'"{current_dir}\\connect.exe"'
else:
    startup_cmd = f'"{sys.executable}" "{current_dir}\\main.py"'

lg.info(f"启动项 -> 版本: {'打包'if is_exe else '源代码'}")


def create():
    try:
        key = winreg.HKEY_CURRENT_USER
        sub_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.SetValueEx(key, "NJFUAutoConnect", 0, winreg.REG_SZ, startup_cmd)
        lg.info("启动项 -> 已创建")

    except Exception:
        lg.error("启动项 -> 创建失败")
        lg.error(f"启动项 -> 错误信息:\n", exc_info=True)


def remove():
    try:
        key = winreg.HKEY_CURRENT_USER
        sub_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.DeleteValue(key, "NJFUAutoConnect")
        lg.info("启动项 -> 已移除")

    except FileNotFoundError:
        lg.warning(f"启动项 -> 移除中未找到键值")

    except Exception:
        lg.error("启动项 -> 移除失败")
        lg.error(f"启动项 -> 错误信息:\n", exc_info=True)
