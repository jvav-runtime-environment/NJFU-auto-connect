"""管理自动更新"""

import sys
import time
import requests
import subprocess
import logging as lg

from utils import pathManager
from utils.createStartUp import is_exe


CURRENT_VERSION = "v1.1.2"
CHECK_UPDATE_URL = "https://api.github.com/repos/jvav-runtime-environment/NJFU-auto-connect/releases/latest"
PROXY = ["", "https://ghproxy.cc/"]  # 加速代理

update_path = pathManager.current_dir / "update"
update_file = update_path / "connect.exe"

update_bat_file = pathManager.current_dir / "update.bat"

update_cmd = f"""@echo off
echo start updating in 5 seconds...
timeout /t 5 /nobreak
move /y "{update_file}" "{pathManager.current_dir}"
echo completed! start program in 2s...
timeout /t 2 /nobreak
start "{pathManager.exe_path}"
exit
"""

percent = 0


def get_download_percent():
    """获取下载进度"""
    return percent


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


def download(file_info):
    """下载最新版本"""
    global update_path, percent

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

                        # 每10秒输出一次下载进度
                        t2 = time.time()
                        if t2 - t1 > 10:
                            lg.info(f"更新 -> 下载进度: {percent:.2f}%")
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

    if success:
        lg.info("更新 -> 结束, 下载完成")
        return True
    else:
        lg.info("更新 -> 结束, 全部失败")
        return False


def check_and_apply_update():
    """检查更新并更新"""
    if not is_exe:  # 更新只在exe版本启动
        return

    have_update, data = check_update()

    # 如果存在update_bat表示已经执行过更新
    if not have_update:
        lg.info("更新 -> 已更新")
        lg.info("更新 -> 移除更新文件")
        update_bat_file.unlink(missing_ok=True)
        update_file.unlink(missing_ok=True)

    elif update_file.exists() and update_file.stat().st_size == data["assets"][0]["size"]:
        lg.info("更新 -> 检测到更新文件")
        update_bat_file.touch()
        update_bat_file.write_text(update_cmd)
        subprocess.Popen(f'"{update_bat_file}"', shell=True)
        lg.info("更新 -> 即将执行更新, 结束程序")
        sys.exit(0)
