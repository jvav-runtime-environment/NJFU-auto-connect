import urllib.request
import requests
import logging as lg
import pathManager

CURRENT_VERSION = "v1.1.2"
CHECK_UPDATE_URL = "https://api.github.com/repos/jvav-runtime-environment/NJFU-auto-connect/releases/latest"

update_path = pathManager.current_dir.parent / "update"
update_file = update_path / "connect.exe"


def check_update():
    """检查更新"""
    global CURRENT_VERSION, CHECK_UPDATE_URL

    try:
        response = requests.get(CHECK_UPDATE_URL)
        response.raise_for_status()

        data = response.json()
        latest_version = data["tag_name"]
        lg.info(f"更新 -> 当前版本: {CURRENT_VERSION}")
        lg.info(f"更新 -> 最新版本: {latest_version}")

        if latest_version > CURRENT_VERSION:
            return (latest_version, data["assets"][0]["browser_download_url"])
        return None

    except requests.RequestException:
        lg.warning("更新 -> 检查更新失败")
        return None


def download_latest(url):
    """下载最新版本"""
    global update_path

    update_path.mkdir(parents=True, exist_ok=True)

    lg.info("更新 -> 开始下载最新版本")

    r = requests.get(url, verify=False, stream=True)
    with open(update_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    lg.info("更新 -> 下载完成")


if __name__ == "__main__":
    update = check_update()
    if update:
        download_latest(update[1])
    else:
        lg.info("更新 -> 当前已是最新版本")
