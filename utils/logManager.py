"""负责管理日志"""

import logging as lg
from utils import pathManager

# 清理log文件
MAX_LOG_SIZE = 50 * 1024
if pathManager.log_path.exists() and pathManager.log_path.stat().st_size > MAX_LOG_SIZE:
    pathManager.log_path.unlink()


lg.basicConfig(
    filename=pathManager.log_path,
    filemode="a",
    level=lg.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
