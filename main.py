import sys
from utils import lock

if not lock.can_create():
    sys.exit(0)

from utils import logManager
from utils import update


import tray
import traceback
import logging as lg
from tkinter import messagebox


try:
    update.check_and_apply_update()

    lg.info("主程序 -> 启动")
    tray.run()
except Exception:
    lg.critical("主程序 -> 未知错误")
    lg.critical("主程序 -> 错误信息:\n", exc_info=True)
    messagebox.showerror("未知的内部错误:\n", traceback.format_exc())
