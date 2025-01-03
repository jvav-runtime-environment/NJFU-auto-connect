import time
import requests
import logging as lg
import pathManager


CURRENT_VERSION = "v1.1.2"
CHECK_UPDATE_URL = "https://api.github.com/repos/jvav-runtime-environment/NJFU-auto-connect/releases/latest"
PROXY = ["", "https://ghproxy.cc/"]

update_path = pathManager.current_dir.parent / "update"
update_file = update_path / "connect.exe"

percent = 0


def check_update():
    """检查更新"""
    global CURRENT_VERSION, CHECK_UPDATE_URL

    try:
        lg.info("更新 -> 检查更新中")
        response = requests.get(CHECK_UPDATE_URL)
        response.raise_for_status()

        data = response.json()
        latest_version = data["tag_name"]
        lg.info(f"更新 -> 当前版本: {CURRENT_VERSION}")
        lg.info(f"更新 -> 最新版本: {latest_version}")

        if latest_version > CURRENT_VERSION:
            return (latest_version, data)
        return None

    except requests.RequestException:
        lg.warning("更新 -> 检查更新失败")
        return None


def download_latest(file_info):
    """下载最新版本"""
    global update_path, percent

    size = file_info["assets"][0]["size"]
    url = file_info["assets"][0]["browser_download_url"]
    update_path.mkdir(parents=True, exist_ok=True)
    update_file.unlink(missing_ok=True)

    lg.info("更新 -> 开始下载最新版本")
    lg.info(f"更新 -> 文件大小: {size / 1024 / 1024:.2f} MB")

    # 每个代理尝试下载一次
    success = False
    for proxy in PROXY:
        if proxy:
            lg.info(f"更新 -> 使用代理: {proxy}")
        else:
            lg.info(f"更新 -> 未使用代理")

        download_url = proxy + url

        try:
            r = requests.get(download_url, stream=True)
            with open(update_file, "wb") as f:

                r_size = 0  # 已下载大小
                t1 = t2 = time.time()  # 计时器

                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

                        # 计算下载进度
                        r_size += len(chunk)
                        percent = r_size / size * 100

                        # 每10秒输出一次下载进度
                        t2 = time.time()
                        if t2 - t1 > 10:
                            lg.info(f"更新 -> 下载进度: {percent:.2f}%")
                            t1 = t2

            success = True
            break

        except requests.RequestException:
            lg.warning("更新 -> 下载失败")
            lg.warning("更新 -> 错误信息\n", exc_info=True)
            update_file.unlink()

        except Exception:
            lg.warning("更新 -> 未知错误")
            lg.warning("更新 -> 错误信息\n", exc_info=True)
            update_file.unlink()

    if success:
        lg.info("更新 -> 结束, 下载完成")
        return True
    else:
        lg.info("更新 -> 结束, 全部失败")
        return False


if __name__ == "__main__":
    lg.basicConfig(
        filename=pathManager.log_path,
        filemode="a",
        level=lg.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        encoding="utf-8",
    )

    update, data = check_update()
    if update:
        download_latest(data)
    else:
        lg.info("更新 -> 当前已是最新版本")
