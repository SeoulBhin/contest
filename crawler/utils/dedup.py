"""공모전 중복 제거 유틸리티"""

import re


def normalize_title(title: str) -> str:
    """제목 정규화: 공백/특수문자 제거, 소문자 변환"""
    title = re.sub(r"[^\w가-힣]", "", title)
    return title.lower()


def deduplicate_contests(contests: list[dict]) -> list[dict]:
    """ID와 제목 유사도 기반 중복 제거

    같은 ID가 있으면 최신 scrapedAt 기준으로 유지.
    다른 소스에서 동일 공모전이 있으면 제목 유사도로 판단.
    """
    seen_ids: dict[str, dict] = {}
    seen_titles: dict[str, dict] = {}
    result = []

    for contest in contests:
        cid = contest["id"]

        # ID 기반 중복 체크
        if cid in seen_ids:
            existing = seen_ids[cid]
            if contest.get("scrapedAt", "") > existing.get("scrapedAt", ""):
                seen_ids[cid] = contest
                result = [c for c in result if c["id"] != cid]
                result.append(contest)
            continue

        # 제목 유사도 기반 중복 체크 (다른 소스 간)
        norm_title = normalize_title(contest.get("title", ""))
        if norm_title in seen_titles:
            existing = seen_titles[norm_title]
            if contest.get("scrapedAt", "") > existing.get("scrapedAt", ""):
                seen_titles[norm_title] = contest
                result = [
                    c
                    for c in result
                    if normalize_title(c.get("title", "")) != norm_title
                ]
                result.append(contest)
            continue

        seen_ids[cid] = contest
        seen_titles[norm_title] = contest
        result.append(contest)

    return result
