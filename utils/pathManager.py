"""管理路径(exe路径与py路径不同)"""

import sys
import pathlib


temp_dir = pathlib.Path(__file__).parent.parent
current_dir = pathlib.Path(sys.argv[0]).parent

exe_path = pathlib.Path(sys.argv[0])

icon_path = temp_dir / "icon.png"
log_path = current_dir / "log.txt"
config_path = current_dir / "config.json"
