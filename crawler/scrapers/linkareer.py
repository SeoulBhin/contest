"""링커리어 (linkareer.com) 스크래퍼 - Selenium 사용"""

import re
from datetime import datetime, timedelta
from .base import BaseScraper, ContestItem

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False


class LinkareerScraper(BaseScraper):
    SOURCE_NAME = "linkareer"
    BASE_URL = "https://linkareer.com"

    # 과학/공학 카테고리 필터 적용
    LIST_URL = "https://linkareer.com/list/contest?filterBy_categoryIDs=SCIENCE_ENGINEERING&filterBy_status=OPEN&orderBy_direction=DESC&orderBy_field=CREATED_AT"

    def scrape(self) -> list[ContestItem]:
        self.logger.info("Linkareer 크롤링 시작")

        if not HAS_SELENIUM:
            self.logger.error("Selenium이 설치되지 않았습니다")
            return []

        return self._scrape_with_selenium()

    def _scrape_with_selenium(self) -> list[ContestItem]:
        """Selenium으로 크롤링"""
        contests = []
        driver = None

        try:
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument(f"user-agent={self._get_headers()['User-Agent']}")

            driver = webdriver.Chrome(options=options)
            driver.get(self.LIST_URL)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[href*='/activity/']")
                )
            )
            self._delay()

            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/activity/']")
            self.logger.info(f"Linkareer: {len(links)}개 링크 발견")

            seen = set()
            for link in links:
                try:
                    href = link.get_attribute("href") or ""
                    id_match = re.search(r"/activity/(\d+)", href)
                    if not id_match:
                        continue

                    node_id = id_match.group(1)

                    # 제목 추출 - h5 안의 텍스트 또는 링크 텍스트
                    title = ""
                    try:
                        h5 = link.find_element(By.TAG_NAME, "h5")
                        title = h5.text.strip()
                    except Exception:
                        title = link.text.strip()

                    # "추천" 프리픽스 제거
                    title = re.sub(r"^추천\s*", "", title)

                    if not title or len(title) < 3:
                        continue

                    # 제목이 있는 링크만 처리 (이미지 링크 스킵)
                    if node_id in seen:
                        continue
                    seen.add(node_id)

                    # D-day 추출 시도 (형제 요소에서)
                    deadline = datetime.now().strftime("%Y-%m-%d")
                    organizer = ""
                    try:
                        card = link.find_element(By.XPATH, "./ancestor::div[contains(@class,'')]/../..")
                        dday_el = card.find_element(By.XPATH, ".//*[starts-with(text(),'D-')]")
                        dday_text = dday_el.text.strip()
                        dday_match = re.search(r"D-(\d+)", dday_text)
                        if dday_match:
                            days = int(dday_match.group(1))
                            deadline = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                    except Exception:
                        pass

                    contests.append(
                        ContestItem(
                            id=f"linkareer-{node_id}",
                            title=title,
                            description="",
                            organizer=organizer,
                            deadline=deadline,
                            startDate=datetime.now().strftime("%Y-%m-%d"),
                            prize="",
                            url=href,
                            thumbnailUrl="",
                            category=self._categorize(title),
                            source=self.SOURCE_NAME,
                            tags=self._extract_tags(title),
                            scrapedAt=datetime.now().isoformat(),
                        )
                    )
                except Exception as e:
                    self.logger.warning(f"Linkareer 항목 파싱 실패: {e}")

        except Exception as e:
            self.logger.error(f"Linkareer 크롤링 실패: {e}")
        finally:
            if driver:
                driver.quit()

        self.logger.info(f"Linkareer: {len(contests)}개 수집 완료")
        return contests

    def _extract_tags(self, title: str) -> list[str]:
        tags = []
        keywords = ["AI", "인공지능", "웹", "앱", "데이터", "보안", "해커톤",
                     "알고리즘", "오픈소스", "SW", "IT", "코딩", "게임",
                     "소프트웨어", "프로그래밍", "과학", "공학"]
        for kw in keywords:
            if kw.lower() in title.lower():
                tags.append(kw)
        return tags[:5]
