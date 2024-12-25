"""负责管理开机自启动"""

import os
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


def create():
    if not startup.exists():
        startup.touch()
    if startup.read_text() != startup_cmd:
        startup.write_text(startup_cmd)
    lg.info(f"已创建启动项")
    lg.debug(f"启动项内容: {startup_cmd}")


def remove():
    if startup.exists():
        startup.unlink()
    lg.info("已移除启动项")
