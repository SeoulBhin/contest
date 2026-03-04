"""한국어 날짜 형식을 YYYY-MM-DD로 파싱"""

import re
from datetime import datetime, timedelta
from typing import Optional


def parse_korean_date(text: str) -> Optional[str]:
    """다양한 한국어 날짜 형식을 YYYY-MM-DD로 변환

    지원 형식:
    - 2026.03.15 / 2026-03-15 / 2026/03/15
    - 2026년 3월 15일
    - 03.15(토) / 03.15 (마감일만 있을 때 올해로 추정)
    - D-14 형식 (현재 날짜 기준 계산)
    """
    if not text:
        return None

    text = text.strip()

    # YYYY.MM.DD or YYYY-MM-DD or YYYY/MM/DD
    m = re.search(r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})", text)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

    # YYYY년 M월 D일
    m = re.search(r"(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일", text)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

    # MM.DD or MM/DD (올해로 추정)
    m = re.search(r"(?<!\d)(\d{1,2})[.\-/](\d{1,2})(?!\d)", text)
    if m:
        year = datetime.now().year
        month = int(m.group(1))
        day = int(m.group(2))
        if 1 <= month <= 12 and 1 <= day <= 31:
            return f"{year}-{month:02d}-{day:02d}"

    # D-숫자
    m = re.search(r"D[--](\d+)", text)
    if m:
        days = int(m.group(1))
        target = datetime.now() + timedelta(days=days)
        return target.strftime("%Y-%m-%d")

    return None


def extract_date_range(text: str) -> tuple[Optional[str], Optional[str]]:
    """텍스트에서 시작일~마감일 추출

    예: '2026.03.01 ~ 2026.04.15'
        '2026년 3월 1일 ~ 2026년 4월 15일'
    """
    parts = re.split(r"\s*[~～–-]\s*", text, maxsplit=1)
    if len(parts) == 2:
        start = parse_korean_date(parts[0])
        end = parse_korean_date(parts[1])
        return start, end

    single = parse_korean_date(text)
    return None, single
