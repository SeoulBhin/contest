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
                "int_gbn": "1",       # 공모전
                "Ession": "10005",    # IT/소프트웨어/콘텐츠
                "order": "1",         # 접수중
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

            items = soup.select("ul.list_style2 > li")
            if not items:
                items = soup.select("div.list_area li")
            if not items:
                items = soup.select(".contest_list li, .list_wrap li")

            self.logger.info(f"ContestKorea: {len(items)}개 항목 발견")

            for item in items:
                try:
                    contest = self._parse_item(item)
                    if contest:
                        contests.append(contest)
                except Exception as e:
                    self.logger.warning(f"ContestKorea 항목 파싱 실패: {e}")
                    continue

                self._delay()

        except Exception as e:
            self.logger.error(f"ContestKorea 크롤링 실패: {e}")

        self.logger.info(f"ContestKorea: {len(contests)}개 수집 완료")
        return contests

    def _parse_item(self, item: BeautifulSoup) -> ContestItem | None:
        link_tag = item.select_one("a[href]")
        if not link_tag:
            return None

        href = link_tag.get("href", "")
        if not href:
            return None

        # ID 추출
        id_match = re.search(r"[?&]id=(\d+)", href)
        contest_id = f"contestkorea-{id_match.group(1)}" if id_match else None
        if not contest_id:
            return None

        url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

        # 제목
        title_tag = item.select_one(".txt, .title, h3, h4, .tit")
        title = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
        if not title:
            return None

        # 주최자
        org_tag = item.select_one(".org, .company, .host")
        organizer = org_tag.get_text(strip=True) if org_tag else ""

        # 날짜
        date_tag = item.select_one(".date, .period, .day")
        deadline = None
        start_date = None
        if date_tag:
            date_text = date_tag.get_text(strip=True)
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
        img_tag = item.select_one("img")
        thumbnail = ""
        if img_tag:
            thumbnail = img_tag.get("src", "")
            if thumbnail and not thumbnail.startswith("http"):
                thumbnail = f"{self.BASE_URL}{thumbnail}"

        # 설명
        desc_tag = item.select_one(".desc, .info, p")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        category = self._categorize(title, description)

        return ContestItem(
            id=contest_id,
            title=title,
            description=description,
            organizer=organizer,
            deadline=deadline,
            startDate=start_date,
            prize="",
            url=url,
            thumbnailUrl=thumbnail,
            category=category,
            source=self.SOURCE_NAME,
            tags=self._extract_tags(title, description),
            scrapedAt=datetime.now().isoformat(),
        )

    def _extract_tags(self, title: str, description: str) -> list[str]:
        tags = []
        text = title + " " + description
        keywords = ["AI", "인공지능", "웹", "앱", "데이터", "보안", "해커톤",
                     "알고리즘", "오픈소스", "클라우드", "블록체인", "IoT", "로봇"]
        for kw in keywords:
            if kw.lower() in text.lower():
                tags.append(kw)
        return tags[:5]
