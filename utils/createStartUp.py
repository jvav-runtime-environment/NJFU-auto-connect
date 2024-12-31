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

lg.info(f"当前运行为 {'打包'if is_exe else '源代码'} 版本")


def create():
    try:
        key = winreg.HKEY_CURRENT_USER
        sub_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.SetValueEx(key, "NJFUAutoConnect", 0, winreg.REG_SZ, startup_cmd)
        lg.info(f"已创建注册表启动项")

    except Exception:
        lg.error(f"创建注册表启动项失败: ", exc_info=True)


def remove():
    try:
        key = winreg.HKEY_CURRENT_USER
        sub_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_ALL_ACCESS) as key:
            winreg.DeleteValue(key, "NJFUAutoConnect")
        lg.info(f"已移除注册表启动项")

    except FileNotFoundError:
        lg.info(f"未找到注册表启动项")

    except Exception:
        lg.error(f"移除注册表启动项失败: ", exc_info=True)


if __name__ == "__main__":
    create()
    input()
    remove()
