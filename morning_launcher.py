"""
morning_launcher.py
====================================================
平日 08:30 に指定サイトを Chrome / Edge で自動起動
====================================================
作者  : Python先生 (Claude)
環境  : Ubuntu + VSCode + Python 3.8+
"""

import schedule
import time
import datetime
import json
import os
import logging
from pathlib import Path

# ── Selenium ────────────────────────────────────────
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service   import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options   import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# ══════════════════════════════════════════════════════
#  🔧 設定ファイル読み込み (sites_config.json)
# ══════════════════════════════════════════════════════

CONFIG_FILE = Path(__file__).parent / "sites_config.json"

DEFAULT_CONFIG = {
    "launch_time": "08:30",
    "browser": "chrome",          # "chrome" / "edge" / "both"
    "sites": [
        "https://www.google.com",
        "https://github.com",
        "https://qiita.com"
    ],
    "headless": False              # True にするとウィンドウ非表示
}

def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        logging.info(f"✅ 設定ファイルを読み込みました: {CONFIG_FILE}")
        return cfg
    else:
        # 初回：デフォルト設定を書き出す
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        logging.info(f"📝 デフォルト設定を作成しました: {CONFIG_FILE}")
        return DEFAULT_CONFIG

# ══════════════════════════════════════════════════════
#  🌐 ブラウザ起動関数
# ══════════════════════════════════════════════════════

def build_chrome_driver(headless: bool) -> webdriver.Chrome:
    opts = ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--start-maximized")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)


def build_edge_driver(headless: bool) -> webdriver.Edge:
    opts = EdgeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--start-maximized")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    service = EdgeService(EdgeChromiumDriverManager().install())
    return webdriver.Edge(service=service, options=opts)


def open_sites(driver: webdriver.Remote, sites: list[str]) -> None:
    """最初のサイトを開き、残りはタブで追加"""
    driver.get(sites[0])
    for url in sites[1:]:
        driver.execute_script(f"window.open('{url}', '_blank');")
    logging.info(f"🌐 {len(sites)} サイトを開きました")

# ══════════════════════════════════════════════════════
#  ⏰ メイン処理
# ══════════════════════════════════════════════════════

def is_weekday() -> bool:
    """月〜金 → True"""
    return datetime.datetime.now().weekday() < 5  # 0=月 … 4=金


def morning_job():
    if not is_weekday():
        logging.info("📅 今日は週末のためスキップします")
        return

    cfg     = load_config()
    sites   = cfg.get("sites", [])
    browser = cfg.get("browser", "chrome").lower()
    headless= cfg.get("headless", False)

    logging.info(f"🚀 朝のルーティン開始！ブラウザ: {browser}  サイト数: {len(sites)}")

    drivers = []
    try:
        if browser in ("chrome", "both"):
            drv = build_chrome_driver(headless)
            open_sites(drv, sites)
            drivers.append(drv)

        if browser in ("edge", "both"):
            drv = build_edge_driver(headless)
            open_sites(drv, sites)
            drivers.append(drv)

    except Exception as e:
        logging.error(f"❌ エラーが発生しました: {e}")
        for d in drivers:
            try:
                d.quit()
            except Exception:
                pass


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("morning_launcher.log", encoding="utf-8"),
        ],
    )

    cfg          = load_config()
    launch_time  = cfg.get("launch_time", "08:30")

    logging.info(f"⏰ スケジュール登録: 平日 {launch_time} に起動します")
    schedule.every().day.at(launch_time).do(morning_job)

    # 起動直後にすぐ実行したい場合は下の行のコメントを外す
    # morning_job()

    while True:
        schedule.run_pending()
        time.sleep(30)   # 30秒ごとにチェック


if __name__ == "__main__":
    main()
