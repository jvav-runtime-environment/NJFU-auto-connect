"""负责管理开机自启动"""

import os
import winreg
import logging as lg
from pathlib import Path

try:
    if __nuitka_binary_dir is not None:  # type: ignore
        is_exe = True
except NameError:
    is_exe = False


startup = Path(f"{os.environ.get('APPDATA')}\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\conn.bat")
current_dir = Path(".").absolute()

# 判断是否为打包的程序
# 释放自启动bat
if is_exe:
    startup_cmd = f"cd /d {current_dir}\nstart connect.exe"
else:
    startup_cmd = f"cd /d {current_dir}\nstart pythonw main.py"

lg.info(f"当前运行为 {'打包'if is_exe else '源代码'} 版本")


def create_bat():
    if not startup.exists():
        startup.touch()
    if startup.read_text() != startup_cmd:
        startup.write_text(startup_cmd)
    lg.info(f"已创建启动项")
    lg.debug(f"启动项内容: {startup_cmd}")


def remove_bat():
    if startup.exists():
        startup.unlink()
    lg.info("已移除启动项")


def create_regesitry():
    try:
        key = winreg.HKEY_CURRENT_USER
        sub_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, "NJFU-auto-connect", 0, winreg.REG_SZ, f'"{current_dir}\\connect.exe"')
        lg.info(f"已创建注册表启动项")

    except Exception:
        lg.error(f"创建注册表启动项失败: ", exc_info=True)


def remove_regesitry():
    try:
        key = winreg.HKEY_CURRENT_USER
        sub_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_WRITE) as key:
            winreg.DeleteValue(key, "NJFU-auto-connect")
        lg.info(f"已移除注册表启动项")

    except Exception:
        lg.error(f"移除注册表启动项失败: ", exc_info=True)


def create():
    if is_exe:
        create_regesitry()
    else:
        create_bat()


def remove():
    if is_exe:
        remove_regesitry()
    else:
        remove_bat()


if __name__ == "__main__":
    create_regesitry()
    input()
    remove_regesitry()
