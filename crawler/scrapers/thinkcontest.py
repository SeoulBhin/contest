"""씽굿 (thinkcontest.com) 스크래퍼 - JSON API 사용"""

import re
import requests
from datetime import datetime
from .base import BaseScraper, ContestItem
from ..utils.date_parser import parse_korean_date


# IT/SW 관련 카테고리 키워드 (contest_field_nm에 부분 매칭)
IT_KEYWORDS = ["게임", "소프트웨어", "과학"]


class ThinkContestScraper(BaseScraper):
    SOURCE_NAME = "thinkcontest"
    BASE_URL = "https://www.thinkcontest.com"
    API_URL = "https://www.thinkcontest.com/thinkgood/user/contest/subList.do"

    def scrape(self) -> list[ContestItem]:
        self.logger.info("ThinkContest 크롤링 시작")
        contests = []

        try:
            payload = {
                "pageIndex": 1,
                "pageSize": 50,
                "sort_type": "REG_DT",
                "sort_order": "DESC",
                "search_status": "접수중",
            }
            headers = {
                **self._get_headers(),
                "Content-Type": "application/json",
            }

            response = requests.post(
                self.API_URL,
                json=payload,
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            items = data.get("listJsonData", [])
            self.logger.info(f"ThinkContest API: {len(items)}개 항목 발견")

            for item in items:
                try:
                    contest = self._parse_api_item(item)
                    if contest:
                        contests.append(contest)
                except Exception as e:
                    self.logger.warning(f"ThinkContest 항목 파싱 실패: {e}")

        except Exception as e:
            self.logger.error(f"ThinkContest 크롤링 실패: {e}")

        self.logger.info(f"ThinkContest: {len(contests)}개 수집 완료")
        return contests

    def _parse_api_item(self, item: dict) -> ContestItem | None:
        # IT/SW 관련 카테고리만 필터링
        field_nm = item.get("contest_field_nm", "")
        if not any(kw in field_nm for kw in IT_KEYWORDS):
            return None

        contest_pk = str(item.get("contest_pk", ""))
        if not contest_pk:
            return None

        title = item.get("program_nm", "").strip()
        if not title:
            return None

        organizer = item.get("host_company", "") or ""
        prize = item.get("prize_money", "") or ""

        # 날짜 파싱
        finish_dt = item.get("finish_dt", "")
        accept_dt = item.get("accept_dt", "")

        deadline = self._parse_api_date(finish_dt)
        start_date = self._parse_api_date(accept_dt)

        if not deadline:
            # receive_period 에서 추출 시도 ("2026-03-02 ~ 2026-04-02")
            period = item.get("receive_period", "")
            if period:
                parts = re.split(r"\s*~\s*", period)
                if len(parts) == 2:
                    start_date = start_date or parse_korean_date(parts[0].strip())
                    deadline = parse_korean_date(parts[1].strip())

        if not deadline:
            return None
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")

        # URL
        url = f"{self.BASE_URL}/thinkgood/user/contest/view.do?contest_pk={contest_pk}"

        # 썸네일
        poster_name = item.get("poster_name", "")
        poster_path = item.get("poster_path", "")
        thumbnail = ""
        if poster_name and poster_path:
            thumbnail = f"{self.BASE_URL}/_attach/thinkgood/{poster_path}{poster_name}"

        category = self._categorize(title)

        return ContestItem(
            id=f"thinkcontest-{contest_pk}",
            title=title,
            description="",
            organizer=organizer,
            deadline=deadline,
            startDate=start_date,
            prize=prize,
            url=url,
            thumbnailUrl=thumbnail,
            category=category,
            source=self.SOURCE_NAME,
            tags=self._extract_tags(title),
            scrapedAt=datetime.now().isoformat(),
        )

    @staticmethod
    def _parse_api_date(dt_str: str) -> str | None:
        """API 날짜 문자열 ('2026-03-02 00:00:00.0') -> 'YYYY-MM-DD'"""
        if not dt_str:
            return None
        m = re.match(r"(\d{4}-\d{2}-\d{2})", dt_str)
        return m.group(1) if m else None

    def _extract_tags(self, title: str) -> list[str]:
        tags = []
        keywords = ["AI", "인공지능", "웹", "앱", "데이터", "보안", "해커톤",
                     "알고리즘", "오픈소스", "SW", "IT", "코딩", "게임",
                     "소프트웨어", "프로그래밍"]
        for kw in keywords:
            if kw.lower() in title.lower():
                tags.append(kw)
        return tags[:5]
