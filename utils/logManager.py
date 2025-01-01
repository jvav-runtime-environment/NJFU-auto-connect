"""负责管理日志"""

import logging as lg
from utils.pathManager import log_path

# 清理log文件
MAX_LOG_SIZE = 50 * 1024
if log_path.exists() and log_path.stat().st_size > MAX_LOG_SIZE:
    log_path.unlink()


lg.basicConfig(
    filename=log_path,
    filemode="a",
    level=lg.DEBUG,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
