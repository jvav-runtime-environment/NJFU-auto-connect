inited = False
if not inited:
    import pathlib
    import sys

    temp_dir = pathlib.Path(__file__).parent.parent
    current_dir = pathlib.Path(sys.argv[0]).parent

    icon_path = temp_dir / "icon.png"
    log_path = current_dir / "log.txt"
    config_path = current_dir / "config.json"
