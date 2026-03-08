import subprocess
import time
import datetime
import logging
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
LOG_FILE = SCRIPT_DIR / "scheduler.log"
UPDATE_SH = SCRIPT_DIR / "update.sh"

HOUR = 6          # 実行時刻（24時間表記）
MAX_RETRIES = 5   # 最大リトライ回数
RETRY_WAIT = 60   # リトライ間隔（秒）

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

NETWORK_ERRORS = (
    "could not resolve",
    "unable to connect",
    "connection timed out",
    "network is unreachable",
    "failed to connect",
    "no route to host",
    "ssl",
    "curl",
)

def is_network_error(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in NETWORK_ERRORS)

def run_update():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = subprocess.run(
                ["bash", str(UPDATE_SH)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                log.info("成功:\n%s", result.stdout.strip())
                return
            else:
                stderr = result.stderr.strip()
                log.warning("試行 %d/%d 失敗:\n%s", attempt, MAX_RETRIES, stderr)
                if not is_network_error(stderr):
                    log.error("ネットワーク以外のエラーのためリトライ中止")
                    return
        except subprocess.TimeoutExpired:
            log.warning("試行 %d/%d タイムアウト", attempt, MAX_RETRIES)
        except Exception as e:
            log.warning("試行 %d/%d 例外: %s", attempt, MAX_RETRIES, e)

        if attempt < MAX_RETRIES:
            log.info("%d秒後にリトライ...", RETRY_WAIT)
            time.sleep(RETRY_WAIT)

    log.error("全 %d 回の試行が失敗しました", MAX_RETRIES)

def main():
    log.info("スケジューラ起動（毎日 %02d:00 に実行）", HOUR)
    last_run_date = None

    while True:
        now = datetime.datetime.now()
        today = now.date()

        if now.hour == HOUR and last_run_date != today:
            log.info("=== 定時実行開始 ===")
            run_update()
            last_run_date = today

        time.sleep(30)

if __name__ == "__main__":
    main()
