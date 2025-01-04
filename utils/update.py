"""管理自动更新"""

import sys
import time
import requests
import threading
import subprocess
import logging as lg

from utils import pathManager
from utils.createStartUp import is_exe
from tkinter import messagebox
from tkinter import messagebox


CURRENT_VERSION = "v1.1.2"
CHECK_UPDATE_URL = "https://api.github.com/repos/jvav-runtime-environment/NJFU-auto-connect/releases/latest"
PROXY = ["", "https://ghproxy.cc/"]  # 加速代理

update_path = pathManager.current_dir / "update"
update_file = update_path / "connect.exe"

update_bat_file = pathManager.current_dir / "update.bat"

update_cmd = f"""@echo off
cd /d {pathManager.current_dir}
echo start updating in 3s...
timeout /t 3 /nobreak >nul
move /y "{update_file}" "{pathManager.current_dir}"
start "" "{pathManager.exe_path}"
exit
"""


def get_version():
    """获取当前版本"""
    return CURRENT_VERSION


def check_update():
    """检查更新"""
    global CURRENT_VERSION, CHECK_UPDATE_URL

    try:
        lg.info("更新 -> 检查更新中")
        response = requests.get(CHECK_UPDATE_URL)
        response.raise_for_status()

        data = response.json()
        latest_version = data["tag_name"]
        lg.info(f"更新 -> 当前版本: {CURRENT_VERSION}")
        lg.info(f"更新 -> 最新版本: {latest_version}")

        if latest_version > CURRENT_VERSION:
            return (True, data)
        return (False, None)

    except requests.RequestException:
        lg.warning("更新 -> 检查更新失败")
        return (False, None)


def download(file_info, stats_callback=lambda finished, success, progress: None):
    """下载最新版本"""
    global update_path

    size = file_info["assets"][0]["size"]
    url = file_info["assets"][0]["browser_download_url"]
    update_path.mkdir(parents=True, exist_ok=True)
    update_file.unlink(missing_ok=True)

    lg.info("更新 -> 开始下载最新版本")
    lg.info(f"更新 -> 文件大小: {size / 1024 / 1024:.2f} MB")

    # 每个代理尝试下载一次
    success = False
    for proxy in PROXY:
        if proxy:
            lg.info(f"更新 -> 使用代理: {proxy}")
        else:
            lg.info(f"更新 -> 未使用代理")

        download_url = proxy + url
        percent = 0

        try:
            r = requests.get(download_url, stream=True)
            with open(update_file, "wb") as f:

                r_size = 0  # 已下载大小
                t1 = t2 = time.time()  # 计时器

                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

                        # 计算下载进度
                        r_size += len(chunk)
                        percent = r_size / size * 100

                        # 每秒更新一次下载进度
                        t2 = time.time()
                        if t2 - t1 > 1:
                            stats_callback(False, False, percent)  # 调用回调函数
                            t1 = t2

            success = True
            break

        except requests.RequestException:
            lg.warning("更新 -> 下载失败")
            lg.warning("更新 -> 错误信息\n", exc_info=True)
            update_file.unlink(missing_ok=True)

        except Exception:
            lg.warning("更新 -> 未知错误")
            lg.warning("更新 -> 错误信息\n", exc_info=True)
            update_file.unlink(missing_ok=True)

    # 结束时调用回调函数通知完成
    stats_callback(True, success, 100)

    if success:
        lg.info("更新 -> 结束, 下载完成")
        return True
    else:
        lg.info("更新 -> 结束, 全部失败")
        return False


def start_download_thread(file_info, status_callback=lambda finished, success, progress: None):
    download_thread = threading.Thread(target=download, args=(file_info, status_callback))
    download_thread.daemon = True
    lg.info("更新 -> 下载线程启动")
    download_thread.start()


def check_and_apply_update():
    """检查更新并更新"""
    if not is_exe:  # 更新只在exe版本启动
        return

    have_update, data = check_update()

    # 是否有更新
    if not have_update:
        lg.info("更新 -> 已更新")
        lg.info("更新 -> 移除更新文件")
        update_bat_file.unlink(missing_ok=True)
        update_file.unlink(missing_ok=True)

    elif update_file.exists() and update_file.stat().st_size == data["assets"][0]["size"]:
        lg.info("更新 -> 检测到更新文件")
        update_bat_file.touch()
        update_bat_file.write_text(update_cmd)

        subprocess.Popen(f'start "updating..." "{update_bat_file}"', shell=True)

        lg.info("更新 -> 即将执行更新, 结束程序")
        sys.exit(0)


def check_and_ask_for_update():
    """检查更新并询问是否更新"""
    have_update, data = check_update()
    if have_update:
        if messagebox.askyesno("检查更新", f"发现新版本, 是否更新?({CURRENT_VERSION} -> {data['tag_name']})"):
            return (True, data)
    else:
        messagebox.showinfo("检查更新", "当前已是最新版本")

    return (False, None)
