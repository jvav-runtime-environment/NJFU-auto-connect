import sys
from utils import lock

if not lock.can_create():
    sys.exit(0)

from utils import logManager
from utils import update


import tray
import logging
import traceback
from tkinter import messagebox

lg = logging.getLogger("主程序")

try:
    lg.info("启动")
    update.check_and_apply_update()

    tray.run()
    lg.info("结束")
except Exception:
    lg.critical("未知错误")
    lg.critical("错误信息:\n", exc_info=True)
    messagebox.showerror("未知的内部错误:\n", traceback.format_exc())
