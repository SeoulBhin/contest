"""Discord Webhook으로 새 공모전 알림 전송"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("notify")

DATA_DIR = Path(__file__).parent.parent / "data"
CONTESTS_FILE = DATA_DIR / "contests.json"
NOTIFIED_FILE = DATA_DIR / "notified.json"

CATEGORY_COLORS = {
    "algorithm": 0x3498DB,
    "hackathon": 0xE74C3C,
    "ai_ml": 0x9B59B6,
    "web_mobile": 0x2ECC71,
    "game": 0xF39C12,
    "security": 0x1ABC9C,
    "data": 0x34495E,
    "iot": 0xE67E22,
    "sw_general": 0x2980B9,
    "other": 0x95A5A6,
}

CATEGORY_LABELS = {
    "algorithm": "알고리즘",
    "hackathon": "해커톤",
    "ai_ml": "AI/ML",
    "web_mobile": "웹/모바일",
    "game": "게임",
    "security": "보안",
    "data": "데이터",
    "iot": "IoT",
    "sw_general": "SW 일반",
    "other": "기타",
}


def load_notified_ids() -> set[str]:
    if NOTIFIED_FILE.exists():
        try:
            with open(NOTIFIED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, TypeError):
            pass
    return set()


def save_notified_ids(ids: set[str]):
    with open(NOTIFIED_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(ids), f, ensure_ascii=False, indent=2)


def calc_dday(deadline: str) -> str:
    try:
        d = datetime.strptime(deadline, "%Y-%m-%d")
        diff = (d - datetime.now()).days
        if diff < 0:
            return f"D+{abs(diff)}"
        if diff == 0:
            return "D-Day"
        return f"D-{diff}"
    except ValueError:
        return ""


def build_embed(contest: dict) -> dict:
    category = contest.get("category", "other")
    dday = calc_dday(contest.get("deadline", ""))
    deadline_display = contest.get("deadline", "미정")
    if dday:
        deadline_display = f"{deadline_display} ({dday})"

    embed = {
        "title": contest.get("title", "제목 없음"),
        "url": contest.get("url", ""),
        "color": CATEGORY_COLORS.get(category, 0x95A5A6),
        "fields": [
            {"name": "주최", "value": contest.get("organizer", "-"), "inline": True},
            {"name": "마감일", "value": deadline_display, "inline": True},
            {"name": "카테고리", "value": CATEGORY_LABELS.get(category, "기타"), "inline": True},
        ],
    }

    if contest.get("thumbnailUrl"):
        embed["thumbnail"] = {"url": contest["thumbnailUrl"]}

    return embed


def send_webhook(webhook_url: str, embeds: list[dict]):
    # Discord는 한 번에 최대 10개 embed
    for i in range(0, len(embeds), 10):
        batch = embeds[i:i + 10]
        payload = json.dumps({
            "username": "공모전 알리미",
            "content": f"**새로운 공모전 {len(batch)}개가 등록되었습니다!**" if i == 0 else None,
            "embeds": batch,
        }).encode("utf-8")

        req = Request(webhook_url, data=payload, headers={
            "Content-Type": "application/json",
            "User-Agent": "DevContestKR-Bot/1.0",
        })
        try:
            with urlopen(req) as resp:
                logger.info(f"Webhook 전송 성공 (batch {i // 10 + 1}, status {resp.status})")
        except URLError as e:
            logger.error(f"Webhook 전송 실패: {e}")


def main():
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        logger.info("DISCORD_WEBHOOK_URL이 설정되지 않아 알림을 건너뜁니다.")
        return

    if not CONTESTS_FILE.exists():
        logger.warning("contests.json이 없습니다.")
        return

    with open(CONTESTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    contests = data.get("contests", [])
    active = [c for c in contests if c.get("status") == "active"]

    notified_ids = load_notified_ids()
    new_contests = [c for c in active if c["id"] not in notified_ids]

    if not new_contests:
        logger.info("새로운 공모전이 없습니다.")
        return

    logger.info(f"새 공모전 {len(new_contests)}개 알림 전송")

    embeds = [build_embed(c) for c in new_contests]
    send_webhook(webhook_url, embeds)

    # 알림 완료된 ID 저장
    notified_ids.update(c["id"] for c in new_contests)
    save_notified_ids(notified_ids)

    logger.info("알림 처리 완료")


if __name__ == "__main__":
    main()
