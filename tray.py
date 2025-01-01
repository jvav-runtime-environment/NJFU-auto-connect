import time
import requests
import threading
import traceback
import logging as lg
from tkinter import messagebox

from utils import configManager, network, connect, pathManager
import UI


config = configManager.get_config()


def connect_instant():
    """立即进行一次连接"""
    global config

    username = config["username"]
    password = config["password"]
    platform = config["platform"]

    success, msg = connect.login(username, password, platform)
    if success:
        notify("连接成功", "成功连接到校园网")
    else:
        notify("连接失败", "原因: " + msg)


def login_proc():
    """登录方法"""
    global config, stop_event

    username = config["username"]
    password = config["password"]
    platform = config["platform"]
    wifiname = config["wifiname"]
    interval = config["interval"]

    while not stop_event.is_set():
        try:
            # 未连接
            if not network.is_connected():
                stop_event.wait(5)
                continue

            # 检查wifi名称
            if not network.is_the_wifi(wifiname):
                stop_event.wait(60)
                continue

            # 登录
            if not connect.is_connected():
                success, msg = connect.login(username, password, platform)
                if success:
                    notify("连接成功", "成功连接到校园网")
                else:
                    notify("连接失败", "原因: " + msg)

            stop_event.wait(int(interval * 60))

        except (requests.ConnectionError, requests.HTTPError):
            lg.warning("登录线程 -> 连接错误")
            lg.warning("登录线程 -> 错误信息:\n", exc_info=True)

            # 询问是否重试
            if not messagebox.askretrycancel("连接失败", f"无法连接到服务器:\n{traceback.format_exc()}"):
                break

        except Exception:
            lg.error("登录线程 -> 未知错误")
            lg.error("登录线程 -> 错误信息:\n", exc_info=True)
            messagebox.showerror("未知的内部错误:\n", traceback.format_exc())
            break


from pystray import Icon, Menu, MenuItem
from PIL import Image

stop_event = threading.Event()
main_thread = threading.Thread(target=login_proc)


def create_work_thread():
    """创建主任务线程"""
    global main_thread

    main_thread = threading.Thread(target=login_proc)
    main_thread.daemon = True
    main_thread.start()


def run_work_thread():
    """启动主任务"""
    global stop_event, main_thread
    stop_event.clear()

    if not main_thread.is_alive():
        create_work_thread()

        tray.menu = running_menu
        tray.update_menu()
        lg.info("主任务 -> 启动")


def stop_work_thread():
    """停止主任务"""
    global stop_event
    stop_event.set()

    tray.menu = stopped_menu
    tray.update_menu()
    lg.info("主任务 -> 结束")


def notify(title, message):
    """通知"""

    def notify_proc():
        try:
            tray.notify(title=title, message=message)
            time.sleep(5)
            tray.remove_notification()
        except Exception:
            lg.error("通知线程 -> 未知错误")
            lg.error("通知线程 -> 错误信息:\n", exc_info=True)

    notify_thread = threading.Thread(target=notify_proc)
    notify_thread.daemon = True
    notify_thread.start()


def stop_tray():
    """结束程序"""
    tray.stop()
    lg.info("主程序 -> 结束")


def start_ui_thread():
    """启动UI线程"""

    def ui_proc():
        try:
            ui = UI.UI(configManager.get_raw_config())
            ui.window.mainloop()
            lg.info("UI线程 -> 结束")
        except Exception:
            lg.error("UI线程 -> 未知错误")
            lg.error("UI线程 -> 错误信息:\n", exc_info=True)

    ui_thread = threading.Thread(target=ui_proc)
    ui_thread.daemon = True
    ui_thread.start()
    lg.info("UI线程 -> 启动")


def run():
    """启动主程序"""
    global tray

    icon = Image.open(pathManager.icon_path)
    tray = Icon(name="NJFUAutoConnect", title="校园网自动登录", icon=icon, menu=running_menu)
    run_work_thread()
    tray.run()


tray = None
running_menu = Menu(
    MenuItem("运行", run_work_thread, enabled=False),
    MenuItem("停止", stop_work_thread),
    Menu.SEPARATOR,
    MenuItem("立即连接", connect_instant),
    MenuItem("设置", start_ui_thread),
    MenuItem("退出", stop_tray),
)
stopped_menu = Menu(
    MenuItem("运行", run_work_thread),
    MenuItem("停止", stop_work_thread, enabled=False),
    Menu.SEPARATOR,
    MenuItem("立即连接", connect_instant),
    MenuItem("设置", start_ui_thread),
    MenuItem("退出", stop_tray),
)
