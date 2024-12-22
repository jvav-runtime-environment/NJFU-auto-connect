import time
import sys
import requests
import threading
import traceback
import logging as lg
from pathlib import Path
from tkinter import messagebox

current_dir = Path(__file__).parent

# 清理log文件
log_path = current_dir / "log.txt"
if log_path.exists() and log_path.stat().st_size > 50 * 1024:
    log_path.unlink()


lg.basicConfig(
    filename="log.txt",
    filemode="a",
    level=lg.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


from utils import lock, configManager, createStartUp, network, connect
import UI


if not lock.can_create():
    lg.info("已有其他实例在运行, 程序退出")
    sys.exit(0)


config = configManager.get_config()
startup = config["startup"]


def connect_instant():
    # 立即进行一次连接
    global config

    username = config["username"]
    password = config["password"]
    platform = config["platform"]

    success, msg = connect.login(username, password, platform)
    if success:
        notify("连接成功", "成功连接到校园网")
    else:
        notify("连接失败", "原因: " + msg)


def set_startup(bool):
    # 设置启动项
    global config

    if config["startup"] != bool:
        config["startup"] = bool

        if bool:
            createStartUp.create()
        else:
            createStartUp.remove()


def login_proc():
    # 登录方法
    global config, running

    username = config["username"]
    password = config["password"]
    platform = config["platform"]
    wifiname = config["wifiname"]

    interval = config["interval"]

    while running:
        try:
            # 未连接
            if not network.is_connected():
                time.sleep(5)
                continue

            # 检查wifi名称
            if not network.is_the_wifi(wifiname):
                time.sleep(60)
                continue

            # 登录
            if not connect.is_connected():
                success, msg = connect.login(username, password, platform)
                if success:
                    notify("连接成功", "成功连接到校园网")
                else:
                    notify("连接失败", "原因: " + msg)

            time.sleep(int(interval * 60))

        except requests.ConnectionError:
            lg.warning(f"[登录线程] 连接错误: {traceback.format_exc()}")

            # 询问是否重试
            if not messagebox.askretrycancel("连接失败", f"无法连接到服务器: \n{e}"):
                break

        except Exception:
            e = traceback.format_exc()
            lg.error(f"[登录线程] 未知错误: {e}")
            messagebox.showerror("未知的内部错误\n", e)
            break


from pystray import Icon, Menu, MenuItem
from PIL import Image

running = True
main_thread = threading.Thread(target=login_proc)


def create_main_thread():
    global main_thread
    main_thread = threading.Thread(target=login_proc)
    main_thread.daemon = True
    main_thread.start()


def run_main_thread():
    global running, main_thread
    running = True

    if not main_thread.is_alive():
        create_main_thread()

        tray.menu = running_menu
        tray.update_menu()

    lg.info("任务线程启动")


def stop_main_thread():
    global running
    running = False

    tray.menu = stopped_menu
    tray.update_menu()
    lg.info("任务线程结束")


def notify(title, message):
    def notify_proc():
        try:
            tray.notify(title=title, message=message)
            time.sleep(5)
            tray.remove_notification()
        except Exception:
            lg.error(f"[通知线程] 未知错误: {traceback.format_exc()}")

    notify_thread = threading.Thread(target=notify_proc)
    notify_thread.daemon = True
    notify_thread.start()


def stop_tray():
    tray.stop()
    lg.info("程序已结束")


def start_ui_thread():

    def ui_proc():
        try:
            ui = UI.UI(configManager.get_raw_config())
            ui.window.mainloop()
            lg.info("[UI线程] UI线程已结束")
        except Exception:
            e = traceback.format_exc()
            lg.error(f"[UI线程] 未知错误: {e}")

    ui_thread = threading.Thread(target=ui_proc)
    ui_thread.daemon = True
    ui_thread.start()
    lg.info("[UI线程] UI线程已启动")


# 运行入口(主循环)
try:
    icon = Image.open(current_dir / "icon.png")
    running_menu = Menu(
        MenuItem("运行", run_main_thread, enabled=False),
        MenuItem("停止", stop_main_thread),
        MenuItem("立即连接", connect_instant),
        MenuItem("设置", start_ui_thread),
        MenuItem("退出", stop_tray),
    )
    stopped_menu = Menu(
        MenuItem("运行", run_main_thread),
        MenuItem("停止", stop_main_thread, enabled=False),
        MenuItem("立即连接", connect_instant),
        MenuItem("设置", start_ui_thread),
        MenuItem("退出", stop_tray),
    )

    tray = Icon("linking", icon=icon, menu=running_menu, title="校园网自动连接")

    create_main_thread()
    tray.run()

except Exception:
    e = traceback.format_exc()
    lg.error(f"未知错误: {e}")
    messagebox.showerror("未知的内部错误\n", e)
