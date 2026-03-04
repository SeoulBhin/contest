"""크롤러 오케스트레이터 - 모든 스크래퍼를 실행하고 결과를 병합"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

from .scrapers import ContestKoreaScraper, ThinkContestScraper, LinkareerScraper, WevityScraper, DaconScraper
from .utils.dedup import deduplicate_contests
from .utils.filter import filter_cs_contests

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

DATA_DIR = Path(__file__).parent.parent / "data"
CONTESTS_FILE = DATA_DIR / "contests.json"
METADATA_FILE = DATA_DIR / "metadata.json"

# 완료된 공모전 보관 기간 (일)
RETENTION_DAYS = 90


def load_existing_contests() -> list[dict]:
    """기존 contests.json 로드"""
    if CONTESTS_FILE.exists():
        try:
            with open(CONTESTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("contests", [])
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"기존 데이터 로드 실패: {e}")
    return []


def cleanup_old_contests(contests: list[dict]) -> list[dict]:
    """보관 기간이 지난 완료 공모전 제거"""
    cutoff = (datetime.now() - timedelta(days=RETENTION_DAYS)).strftime("%Y-%m-%d")
    before = len(contests)
    contests = [c for c in contests if c.get("deadline", "9999-99-99") >= cutoff]
    removed = before - len(contests)
    if removed > 0:
        logger.info(f"{removed}개의 오래된 공모전 정리")
    return contests


def run_scraper(scraper_class, metadata: dict) -> list[dict]:
    """개별 스크래퍼 실행 (에러 시 빈 리스트 반환)"""
    name = scraper_class.SOURCE_NAME if hasattr(scraper_class, "SOURCE_NAME") else scraper_class.__name__
    try:
        scraper = scraper_class()
        items = scraper.scrape()
        contests = [item.to_dict() for item in items]

        metadata["sources"][scraper.SOURCE_NAME] = {
            "lastSuccess": datetime.now().isoformat(),
            "count": len(contests),
            "errors": [],
        }

        logger.info(f"{name}: {len(contests)}개 수집 성공")
        return contests

    except Exception as e:
        error_msg = str(e)
        logger.error(f"{name} 실행 실패: {error_msg}")

        source_name = scraper_class.SOURCE_NAME if hasattr(scraper_class, "SOURCE_NAME") else name
        if source_name not in metadata["sources"]:
            metadata["sources"][source_name] = {}
        metadata["sources"][source_name]["errors"] = [
            {"time": datetime.now().isoformat(), "message": error_msg}
        ]
        return []


def main():
    logger.info("=== 크롤링 시작 ===")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    metadata: dict = {
        "lastCrawl": datetime.now().isoformat(),
        "sources": {},
    }

    # 기존 데이터 로드
    existing = load_existing_contests()
    logger.info(f"기존 데이터: {len(existing)}개")

    # 각 스크래퍼 실행
    scrapers = [ContestKoreaScraper, ThinkContestScraper, LinkareerScraper, WevityScraper, DaconScraper]
    new_contests: list[dict] = []
    success_count = 0

    for scraper_class in scrapers:
        results = run_scraper(scraper_class, metadata)
        if results:
            new_contests.extend(results)
            success_count += 1

    if success_count == 0:
        logger.error("모든 스크래퍼가 실패했습니다!")
        # 기존 데이터 유지하면서 메타데이터만 업데이트
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        sys.exit(1)

    logger.info(f"새로 수집: {len(new_contests)}개 (성공 소스: {success_count}/{len(scrapers)})")

    # 기존 데이터와 병합
    # 새 데이터에 있는 소스의 기존 데이터는 교체, 실패한 소스의 기존 데이터는 유지
    succeeded_sources = {s.SOURCE_NAME for s in scrapers if
                         metadata["sources"].get(s.SOURCE_NAME, {}).get("count", 0) > 0 or
                         not metadata["sources"].get(s.SOURCE_NAME, {}).get("errors")}

    # 실패한 소스의 기존 데이터 유지
    retained = [c for c in existing if c.get("source") not in succeeded_sources]
    all_contests = new_contests + retained

    # 중복 제거
    all_contests = deduplicate_contests(all_contests)

    # IT/컴퓨터공학 관련 공모전만 필터링
    all_contests = filter_cs_contests(all_contests)

    # 마감된 공모전 status 갱신
    today = datetime.now().strftime("%Y-%m-%d")
    for c in all_contests:
        if c.get("deadline", "9999-99-99") < today:
            c["status"] = "completed"
        else:
            c.setdefault("status", "active")

    # 오래된 공모전 정리
    all_contests = cleanup_old_contests(all_contests)

    # 마감일순 정렬
    all_contests.sort(key=lambda c: c.get("deadline", "9999-99-99"))

    logger.info(f"최종 공모전 수: {len(all_contests)}개")

    # 결과 저장
    output = {
        "lastUpdated": datetime.now().isoformat(),
        "totalCount": len(all_contests),
        "contests": all_contests,
    }

    with open(CONTESTS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    logger.info("=== 크롤링 완료 ===")


if __name__ == "__main__":
    main()
