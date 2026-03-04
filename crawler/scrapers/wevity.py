"""위비티 (wevity.com) 스크래퍼 - 서버 렌더링 HTML"""

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from .base import BaseScraper, ContestItem


class WevityScraper(BaseScraper):
    SOURCE_NAME = "wevity"
    BASE_URL = "https://www.wevity.com"

    # 접수중인 CS/IT 관련 카테고리
    CATEGORY_PARAMS = [
        "?c=find&s=1&gub=1&cidx=20&mode=ing",  # 웹/모바일/IT
        "?c=find&s=1&gub=1&cidx=21&mode=ing",  # 게임/소프트웨어
        "?c=find&s=1&gub=1&cidx=22&mode=ing",  # 과학/공학
    ]

    def scrape(self) -> list[ContestItem]:
        self.logger.info("Wevity 크롤링 시작")
        contests = []
        seen_ids = set()

        for params in self.CATEGORY_PARAMS:
            try:
                url = f"{self.BASE_URL}/{params}"
                response = requests.get(
                    url,
                    headers=self._get_headers(),
                    timeout=15,
                )
                response.raise_for_status()
                response.encoding = "utf-8"
                soup = BeautifulSoup(response.text, "lxml")

                items = soup.select("ul.list > li")
                self.logger.info(f"Wevity ({params}): {len(items)}개 항목 발견")

                for item in items:
                    try:
                        contest = self._parse_item(item)
                        if contest and contest.id not in seen_ids:
                            seen_ids.add(contest.id)
                            contests.append(contest)
                    except Exception as e:
                        self.logger.warning(f"Wevity 항목 파싱 실패: {e}")
                        continue

                self._delay()

            except Exception as e:
                self.logger.error(f"Wevity 카테고리 크롤링 실패 ({params}): {e}")

        self.logger.info(f"Wevity: {len(contests)}개 수집 완료")
        return contests

    def _parse_item(self, item: BeautifulSoup) -> ContestItem | None:
        # 제목 링크 찾기
        tit_div = item.select_one("div.tit")
        if not tit_div:
            return None

        link_tag = tit_div.select_one("a")
        if not link_tag:
            return None

        href = link_tag.get("href", "")
        title = link_tag.get_text(strip=True)
        if not title or not href:
            return None

        # "신규", "IDEA" 등 배지 텍스트 제거
        title = re.sub(r"\b(신규|NEW|IDEA)\b", "", title).strip()

        # ID 추출 (ix 파라미터)
        ix_match = re.search(r"ix=(\d+)", href)
        if not ix_match:
            return None
        contest_id = f"wevity-{ix_match.group(1)}"

        url = f"{self.BASE_URL}/{href}" if not href.startswith("http") else href

        # 주최사
        organ_div = item.select_one("div.organ")
        organizer = organ_div.get_text(strip=True) if organ_div else ""

        # D-day에서 마감일 계산
        day_div = item.select_one("div.day")
        if not day_div:
            return None

        day_text = day_div.get_text(strip=True)

        # D+N (이미 마감)은 스킵
        if "D+" in day_text:
            return None

        # D-N에서 N 추출
        d_match = re.search(r"D-(\d+)", day_text)
        if not d_match:
            return None

        days_left = int(d_match.group(1))
        deadline_date = datetime.now() + timedelta(days=days_left)
        deadline = deadline_date.strftime("%Y-%m-%d")

        category = self._categorize(title)

        return ContestItem(
            id=contest_id,
            title=title,
            description="",
            organizer=organizer,
            deadline=deadline,
            startDate=datetime.now().strftime("%Y-%m-%d"),
            prize="",
            url=url,
            thumbnailUrl="",
            category=category,
            source=self.SOURCE_NAME,
            tags=self._extract_tags(title),
            scrapedAt=datetime.now().isoformat(),
        )

    def _extract_tags(self, title: str) -> list[str]:
        tags = []
        keywords = ["AI", "인공지능", "웹", "앱", "데이터", "보안", "해커톤",
                     "알고리즘", "오픈소스", "클라우드", "블록체인", "IoT", "로봇",
                     "SW", "IT", "코딩", "프로그래밍", "소프트웨어", "게임",
                     "과학", "공학", "모바일"]
        for kw in keywords:
            if kw.lower() in title.lower():
                tags.append(kw)
        return tags[:5]
