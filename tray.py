import time
import requests
import threading
import traceback
import logging as lg
from tkinter import messagebox

from utils import configManager, network, connect, pathManager
import UI


def connect_instant():
    """立即进行一次连接"""
    config = configManager.get_config()
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
    global stop_event

    config = configManager.get_config()
    username = config["username"]
    password = config["password"]
    platform = config["platform"]
    wifiname = config["wifiname"]
    interval = config["interval"]

    while not stop_event.is_set():
        try:
            wifi_info = network.get_wifi_info()

            if "SSID" in wifi_info:  # 连接到网络
                if wifi_info["SSID"] == wifiname:  # 连接到指定网络
                    if not connect.is_connected():  # 未连接到校园网
                        success, msg = connect.login(username, password, platform)
                        if success:
                            notify("连接成功", "成功连接到校园网")
                        else:
                            notify("连接失败", "原因: " + msg)
                else:
                    stop_event.wait(60)
                    continue
            else:
                stop_event.wait(5)
                continue

            stop_event.wait(int(interval * 60))

        except (requests.ConnectionError, requests.HTTPError) as e:
            lg.warning("登录线程 -> 连接错误")
            lg.warning("登录线程 -> 错误信息:\n", exc_info=True)

            # 询问是否重试
            if not messagebox.askretrycancel("连接失败", f"无法连接到服务器:\n{e}"):
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


class Traybutton:
    """自定义菜单按钮类"""

    def __init__(self, text, callback, enabled=True):
        self.text = text
        self.callback = callback
        self.enabled = enabled

    def get_item(self):
        """获取菜单项目"""
        if self.text == Menu.SEPARATOR:
            return Menu.SEPARATOR
        else:
            return MenuItem(self.text, self.callback, enabled=self.enabled)

    def enable(self, enabled=True):
        """启用按钮"""
        self.enabled = enabled


class Traymenu:
    """自定义菜单类"""

    def __init__(self):
        self.menu = [  # 菜单按钮列表
            Traybutton("运行", run_work_thread),
            Traybutton("停止", stop_work_thread),
            Traybutton("立即连接", connect_instant),
            Traybutton(Menu.SEPARATOR, None),
            Traybutton("设置", start_ui_thread),
            Traybutton("检查更新", lambda: None),
            Traybutton(Menu.SEPARATOR, None),
            Traybutton("退出", stop_tray),
        ]

    def get_menu(self):
        """获取菜单"""
        menu = []
        for button in self.menu:
            menu.append(button.get_item())

        return Menu(*menu)

    def update(self):
        """更新菜单"""
        tray.menu = self.get_menu()
        tray.update_menu()

    def enable_button(self, index, enable=True):
        """设置按钮状态"""
        self.menu[index].enable(enable)


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

        menu.enable_button(0, False)
        menu.enable_button(1, True)
        menu.update()
        lg.info("主任务 -> 启动")


def stop_work_thread():
    """停止主任务"""
    global stop_event
    stop_event.set()

    menu.enable_button(0, True)
    menu.enable_button(1, False)
    menu.update()
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
    tray = Icon(name="NJFUAutoConnect", title="校园网自动登录", icon=icon, menu=menu.get_menu())
    run_work_thread()
    tray.run()


tray = None
menu = Traymenu()
menu.enable_button(0, False)
