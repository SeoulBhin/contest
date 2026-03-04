"""씽굿 (thinkcontest.com) 스크래퍼 - JS 렌더링, Selenium 사용"""

import re
from datetime import datetime
from .base import BaseScraper, ContestItem
from ..utils.date_parser import parse_korean_date

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False


class ThinkContestScraper(BaseScraper):
    SOURCE_NAME = "thinkcontest"
    BASE_URL = "https://www.thinkcontest.com"

    def _create_driver(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            f"user-agent={self._get_headers()['User-Agent']}"
        )
        return webdriver.Chrome(options=options)

    def scrape(self) -> list[ContestItem]:
        self.logger.info("ThinkContest 크롤링 시작")

        if not HAS_SELENIUM:
            self.logger.error("Selenium이 설치되지 않았습니다")
            return []

        contests = []
        driver = None

        try:
            driver = self._create_driver()
            # IT/SW 카테고리 페이지
            url = f"{self.BASE_URL}/Contest/CateField.php?str_cate=1&str_type=1"
            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".contest_list li, .list_wrap li, .cate_list li, table tbody tr"))
            )

            self._delay()

            # 목록 항목 추출
            items = driver.find_elements(By.CSS_SELECTOR, ".contest_list li, .list_wrap li, .cate_list li")

            if not items:
                # 테이블 형식 시도
                items = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

            self.logger.info(f"ThinkContest: {len(items)}개 항목 발견")

            for item in items:
                try:
                    contest = self._parse_selenium_item(item)
                    if contest:
                        contests.append(contest)
                except Exception as e:
                    self.logger.warning(f"ThinkContest 항목 파싱 실패: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"ThinkContest 크롤링 실패: {e}")
        finally:
            if driver:
                driver.quit()

        self.logger.info(f"ThinkContest: {len(contests)}개 수집 완료")
        return contests

    def _parse_selenium_item(self, item) -> ContestItem | None:
        try:
            link = item.find_element(By.CSS_SELECTOR, "a[href]")
        except Exception:
            return None

        href = link.get_attribute("href") or ""
        if not href:
            return None

        # ID 추출
        id_match = re.search(r"[?&]id=(\d+)", href)
        if not id_match:
            id_match = re.search(r"/(\d+)(?:\?|$|/)", href)
        contest_id = f"thinkcontest-{id_match.group(1)}" if id_match else None
        if not contest_id:
            return None

        url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

        # 제목
        title = ""
        for selector in [".tit", ".title", "h3", "h4", "td:nth-child(2)"]:
            try:
                el = item.find_element(By.CSS_SELECTOR, selector)
                title = el.text.strip()
                if title:
                    break
            except Exception:
                continue

        if not title:
            title = link.text.strip()
        if not title:
            return None

        # 주최자
        organizer = ""
        for selector in [".org", ".host", ".company", "td:nth-child(3)"]:
            try:
                el = item.find_element(By.CSS_SELECTOR, selector)
                organizer = el.text.strip()
                if organizer:
                    break
            except Exception:
                continue

        # 날짜
        deadline = None
        start_date = None
        for selector in [".date", ".period", ".day", "td:nth-child(4)"]:
            try:
                el = item.find_element(By.CSS_SELECTOR, selector)
                date_text = el.text.strip()
                if date_text:
                    parts = re.split(r"\s*[~～–]\s*", date_text)
                    if len(parts) >= 2:
                        start_date = parse_korean_date(parts[0])
                        deadline = parse_korean_date(parts[-1])
                    else:
                        deadline = parse_korean_date(date_text)
                    if deadline:
                        break
            except Exception:
                continue

        if not deadline:
            return None

        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")

        # 썸네일
        thumbnail = ""
        try:
            img = item.find_element(By.CSS_SELECTOR, "img")
            thumbnail = img.get_attribute("src") or ""
        except Exception:
            pass

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
                     "알고리즘", "오픈소스", "SW", "IT"]
        for kw in keywords:
            if kw.lower() in title.lower():
                tags.append(kw)
        return tags[:5]
