"""컨테스트코리아 (contestkorea.com) 스크래퍼 - 서버 렌더링 HTML"""

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .base import BaseScraper, ContestItem
from ..utils.date_parser import parse_korean_date


class ContestKoreaScraper(BaseScraper):
    SOURCE_NAME = "contestkorea"
    BASE_URL = "https://www.contestkorea.com"
    LIST_URL = "https://www.contestkorea.com/sub/list.php"

    def scrape(self) -> list[ContestItem]:
        self.logger.info("ContestKorea 크롤링 시작")
        contests = []

        try:
            params = {
                "int_gbn": "1",
                "Txt_bcode": "030310001",  # 학문·과학·IT
            }
            response = requests.get(
                self.LIST_URL,
                params=params,
                headers=self._get_headers(),
                timeout=15,
            )
            response.raise_for_status()
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "lxml")

            # div.title 안에 view.php 링크가 있는 li를 찾는다
            items = []
            for title_div in soup.select("div.title"):
                link = title_div.select_one('a[href*="view.php"]')
                if link:
                    li = title_div.find_parent("li")
                    if li:
                        items.append(li)

            self.logger.info(f"ContestKorea: {len(items)}개 항목 발견")

            for item in items:
                try:
                    contest = self._parse_item(item)
                    if contest:
                        contests.append(contest)
                except Exception as e:
                    self.logger.warning(f"ContestKorea 항목 파싱 실패: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"ContestKorea 크롤링 실패: {e}")

        self.logger.info(f"ContestKorea: {len(contests)}개 수집 완료")
        return contests

    def _parse_item(self, item: BeautifulSoup) -> ContestItem | None:
        link_tag = item.select_one('div.title a[href*="view.php"]')
        if not link_tag:
            return None

        href = link_tag.get("href", "")
        if not href:
            return None

        # ID 추출 (str_no 파라미터)
        id_match = re.search(r"str_no=(\w+)", href)
        if not id_match:
            return None
        contest_id = f"contestkorea-{id_match.group(1)}"

        url = href if href.startswith("http") else f"{self.BASE_URL}/sub/{href}"

        # 제목 (span.txt)
        title_tag = item.select_one("span.txt")
        title = title_tag.get_text(strip=True) if title_tag else ""
        if not title:
            return None

        # 주최자 (ul.host li.icon_1 에서 "주최 ." 뒤의 텍스트)
        organizer = ""
        org_tag = item.select_one("ul.host li.icon_1")
        if org_tag:
            org_text = org_tag.get_text(strip=True)
            organizer = re.sub(r"^주최\s*[.·]\s*", "", org_text)

        # 날짜 (div.date-detail > span.step-1 의 접수 기간)
        deadline = None
        start_date = None
        step1 = item.select_one(".date-detail .step-1")
        if step1:
            date_text = step1.get_text(strip=True)
            date_text = re.sub(r"^접수\s*", "", date_text)
            parts = re.split(r"\s*[~～–]\s*", date_text)
            if len(parts) >= 2:
                start_date = parse_korean_date(parts[0])
                deadline = parse_korean_date(parts[-1])
            else:
                deadline = parse_korean_date(date_text)

        if not deadline:
            return None

        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")

        # 썸네일
        img_tag = item.select_one("div.title img")
        thumbnail = ""
        if img_tag:
            thumbnail = img_tag.get("src", "")
            if thumbnail and not thumbnail.startswith("http"):
                thumbnail = f"{self.BASE_URL}{thumbnail}"

        category = self._categorize(title)

        return ContestItem(
            id=contest_id,
            title=title,
            description="",
            organizer=organizer,
            deadline=deadline,
            startDate=start_date,
            prize="",
            url=url,
            thumbnailUrl=thumbnail,
            category=category,
            source=self.SOURCE_NAME,
            tags=self._extract_tags(title),
            scrapedAt=datetime.now().isoformat(),
        )

    def _extract_tags(self, title: str) -> list[str]:
        tags = []
        keywords = ["AI", "인공지능", "웹", "앱", "데이터", "보안", "해커톤",
                     "알고리즘", "오픈소스", "클라우드", "블록체인", "IoT", "로봇",
                     "SW", "IT", "코딩", "프로그래밍", "소프트웨어"]
        for kw in keywords:
            if kw.lower() in title.lower():
                tags.append(kw)
        return tags[:5]
