"""管理路径(exe路径与py路径不同)"""

import sys
import pathlib
import logging as lg

inited = False
if not inited:
    temp_dir = pathlib.Path(__file__).parent.parent
    current_dir = pathlib.Path(sys.argv[0]).parent

    icon_path = temp_dir / "icon.png"
    log_path = current_dir / "log.txt"
    config_path = current_dir / "config.json"

    lg.debug(f"当前路径: {current_dir}")
    lg.debug(f"临时路径: {temp_dir}")
