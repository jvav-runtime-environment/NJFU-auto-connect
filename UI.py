import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import logging as lg

from utils import configManager
from utils import createStartUp
from utils import update
from utils.pathManager import icon_path

# 匹配分辨率
import ctypes
import threading

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)


class MainUI:
    """设置UI"""

    def __init__(self, config):
        self.window = tk.Tk()
        self.window.iconphoto(True, tk.PhotoImage(file=icon_path))
        self.window.tk.call("tk", "scaling", ScaleFactor / 75)
        self.window.title("配置设置-校园网自动登录 " + update.get_version())

        # 默认配置项
        self.config = config

        # 创建基本设置部分
        self.create_basic_settings()

        # 创建高级设置部分
        self.create_advanced_settings()

        # 创建保存设置和恢复默认按钮
        self.create_action_buttons()

    def create_basic_settings(self):
        """创建基本设置项"""
        frame = ttk.Frame(self.window)
        frame.pack(padx=20, pady=10, fill="x")

        # 用户名
        ttk.Label(frame, text="用户名:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.username_var = tk.StringVar(value=self.config["username"])
        ttk.Entry(frame, textvariable=self.username_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        # 密码
        ttk.Label(frame, text="密码:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.password_var = tk.StringVar(value=self.config["password"])
        ttk.Entry(frame, textvariable=self.password_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        # WiFi 名称
        ttk.Label(frame, text="WiFi 名称:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.wifiname_var = tk.StringVar(value=self.config["wifiname"])
        self.wifiname_combobox = ttk.Combobox(frame, textvariable=self.wifiname_var, values=["CMCC-EDU", "@f-Yang"])
        self.wifiname_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.wifiname_combobox.bind("<<ComboboxSelected>>", self.on_wifi_name_change)

        # 平台
        ttk.Label(frame, text="平台:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.platform_var = tk.StringVar(value=self.config["platform"])
        ttk.Entry(frame, textvariable=self.platform_var, width=30).grid(row=3, column=1, padx=5, pady=5)

        # 定时刷新间隔
        ttk.Label(frame, text="间隔时间(分钟):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.interval_var = tk.IntVar(value=self.config["interval"])
        ttk.Entry(frame, textvariable=self.interval_var, width=30).grid(row=4, column=1, padx=5, pady=5)

        # 启动时运行
        ttk.Label(frame, text="开机自启:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.startup_button = ttk.Button(frame, text="移除启动项" if self.config["startup"] else "创建启动项", command=self.create_startup)
        self.startup_button.grid(row=5, column=1, padx=5, pady=5)

    def create_advanced_settings(self):
        """创建高级设置项"""
        self.advanced_frame = ttk.Frame(self.window)
        self.advanced_frame.pack(padx=20, pady=10, fill="x")
        self.advanced_frame.pack_forget()  # 初始隐藏

        # 服务器 IP
        ttk.Label(self.advanced_frame, text="服务器 IP:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.serverip_var = tk.StringVar(value=self.config["serverip"])
        ttk.Entry(self.advanced_frame, textvariable=self.serverip_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        # 登录 API
        ttk.Label(self.advanced_frame, text="登录 API:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.login_api_var = tk.StringVar(value=self.config["login_api"])
        ttk.Entry(self.advanced_frame, textvariable=self.login_api_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        # 检查 URL
        ttk.Label(self.advanced_frame, text="检查 URL:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.check_url_var = tk.StringVar(value=self.config["check_url"])
        ttk.Entry(self.advanced_frame, textvariable=self.check_url_var, width=30).grid(row=2, column=1, padx=5, pady=5)

    def create_startup(self):
        """切换开机自启状态"""
        self.config["startup"] = not self.config["startup"]

        if self.config["startup"]:
            createStartUp.create()
            self.startup_button.config(text="移除启动项")
        else:
            createStartUp.remove()
            self.startup_button.config(text="创建启动项")

    def on_wifi_name_change(self, event):
        """WiFi 名称改变时的处理"""
        if self.wifiname_var.get() == "CMCC-EDU":
            self.platform_var.set("@cmcc")
        elif self.wifiname_var.get() == "@f-Yang":
            self.platform_var.set("@njxy")

    def create_action_buttons(self):
        """创建保存设置和恢复默认按钮"""
        action_frame = ttk.Frame(self.window)
        action_frame.pack(padx=20, pady=20, side="bottom")

        # 高级设置按钮
        self.advanced_button = ttk.Button(action_frame, text="高级设置", command=self.toggle_advanced_settings)
        self.advanced_button.grid(row=0, columnspan=2, padx=10, pady=10)

        # 保存设置按钮
        self.save_button = ttk.Button(action_frame, text="保存设置", command=self.save_config)
        self.save_button.grid(row=1, column=0, padx=10)

        # 恢复默认按钮
        self.restore_button = ttk.Button(action_frame, text="恢复默认", command=self.restore_default)
        self.restore_button.grid(row=1, column=1, padx=10)

    def toggle_advanced_settings(self):
        """切换高级设置的显示与隐藏"""
        if self.advanced_frame.winfo_ismapped():
            self.advanced_frame.pack_forget()
            self.advanced_button.config(text="高级设置")
        else:
            self.advanced_frame.pack(padx=20, pady=10, fill="x")
            self.advanced_button.config(text="收起高级设置")

    def save_config(self):
        """保存配置"""
        if messagebox.askokcancel("保存设置", "确定保存设置吗?"):
            # 更新配置字典
            self.config["username"] = self.username_var.get()
            self.config["password"] = self.password_var.get()
            self.config["serverip"] = self.serverip_var.get()
            self.config["login_api"] = self.login_api_var.get()
            self.config["check_url"] = self.check_url_var.get()
            self.config["wifiname"] = self.wifiname_var.get()
            self.config["platform"] = self.platform_var.get()
            self.config["interval"] = self.interval_var.get()

            configManager.save_config(self.config)
            messagebox.showinfo("保存设置", "设置已保存")

    def restore_default(self):
        """恢复默认设置"""
        if messagebox.askokcancel("恢复默认", "确定恢复默认设置吗?"):
            self.config = configManager.get_default()

            # 更新界面上的值
            self.username_var.set(self.config["username"])
            self.password_var.set(self.config["password"])
            self.serverip_var.set(self.config["serverip"])
            self.login_api_var.set(self.config["login_api"])
            self.check_url_var.set(self.config["check_url"])
            self.wifiname_var.set(self.config["wifiname"])
            self.platform_var.set(self.config["platform"])
            self.interval_var.set(self.config["interval"])
            self.startup_button.config(text="创建启动项" if not self.config["startup"] else "移除启动项")

            configManager.save_config(self.config)
            messagebox.showinfo("恢复默认", "设置已恢复默认")

    def show(self):
        """显示窗口"""
        self.window.mainloop()


class DownloadUI:
    """下载进度条"""

    def create(self):
        self.window = tk.Tk()
        self.window.iconphoto(True, tk.PhotoImage(file=icon_path))
        self.window.title("下载更新-校园网自动登录")

        # 创建下载进度条
        self.create_progressbar()

    def create_progressbar(self):
        """创建下载进度条"""
        frame = ttk.Frame(self.window)
        frame.pack(padx=20, pady=10, fill="x")

        # 进度条
        self.progressbar = ttk.Progressbar(frame, length=300, mode="determinate")
        self.progressbar.pack(padx=5, pady=5)

        # 进度文本
        self.progress_label = ttk.Label(frame, text="0%")
        self.progress_label.pack(padx=5, pady=5)

    def update_progress(self):
        """更新下载进度"""
        percent = update.get_download_percent()

        self.progressbar["value"] = percent
        self.progressbar.update()
        self.progress_label.config(text=f"{percent:.2f}%")

        # 定时调用
        self.window.after(100, self.update_progress)

    def start_download_thread(self, file_info):
        """启动下载线程"""

        def update_proc():
            try:
                success = update.download(file_info)
                if success:
                    messagebox.showinfo("更新", "更新完成, 重启程序后完成更新")
                else:
                    messagebox.showerror("更新", "更新失败, 检查网络后重试")

                self.window.after(0, self.window.destroy)  # 防止不同线程调用
                lg.info("更新(下载) -> 结束")

            except Exception:
                lg.error("更新(下载) -> 未知错误")
                lg.error("更新(下载) -> 错误信息:\n", exc_info=True)

        update_thread = threading.Thread(target=update_proc)
        update_thread.daemon = True
        lg.info("更新(下载) -> 启动")
        update_thread.start()

    def check_and_ask_for_update(self):
        """检查更新并询问是否更新"""
        have_update, data = update.check_update()
        if have_update:
            if messagebox.askyesno("检查更新", f"发现新版本, 是否更新?({update.CURRENT_VERSION} -> {data['tag_name']})"):
                self.start_download_thread(data)
                self.create()
                return True
            else:
                lg.info("更新 -> 取消更新")
        else:
            messagebox.showinfo("检查更新", "当前已是最新版本")
        return False

    def show(self):
        """显示窗口"""
        if self.check_and_ask_for_update():  # 仅在进行更新的时候运行窗口
            self.update_progress()
            self.window.mainloop()
