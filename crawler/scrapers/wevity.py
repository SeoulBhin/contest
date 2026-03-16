"""위비티 (wevity.com) 스크래퍼 - Selenium 사용 (Cloudflare 우회)"""

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

        if not HAS_SELENIUM:
            self.logger.error("Selenium이 설치되지 않았습니다")
            return []

        contests = []
        seen_ids = set()
        driver = None

        try:
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument(f"user-agent={self._get_headers()['User-Agent']}")

            driver = webdriver.Chrome(options=options)

            for params in self.CATEGORY_PARAMS:
                try:
                    url = f"{self.BASE_URL}/{params}"
                    driver.get(url)

                    try:
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "ul.list > li")
                            )
                        )
                    except Exception:
                        self.logger.warning(f"Wevity ({params}): 항목 로딩 실패 또는 결과 없음")
                        continue

                    self._delay()

                    items = driver.find_elements(By.CSS_SELECTOR, "ul.list > li")
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

                except Exception as e:
                    self.logger.error(f"Wevity 카테고리 크롤링 실패 ({params}): {e}")

        except Exception as e:
            self.logger.error(f"Wevity 크롤링 실패: {e}")
        finally:
            if driver:
                driver.quit()

        self.logger.info(f"Wevity: {len(contests)}개 수집 완료")
        return contests

    def _parse_item(self, item) -> ContestItem | None:
        # 제목 링크 찾기
        try:
            tit_div = item.find_element(By.CSS_SELECTOR, "div.tit")
        except Exception:
            return None

        try:
            link_tag = tit_div.find_element(By.CSS_SELECTOR, "a")
        except Exception:
            return None

        href = link_tag.get_attribute("href") or ""
        title = link_tag.text.strip()

        # 배지 텍스트 제거
        title = re.sub(r"\b(신규|NEW|IDEA|SPECIAL)\b", "", title).strip()

        if not title or not href:
            return None

        # ID 추출 (ix 파라미터)
        ix_match = re.search(r"ix=(\d+)", href)
        if not ix_match:
            return None
        contest_id = f"wevity-{ix_match.group(1)}"

        url = f"{self.BASE_URL}/{href}" if not href.startswith("http") else href

        # 주최사
        organizer = ""
        try:
            organ_div = item.find_element(By.CSS_SELECTOR, "div.organ")
            organizer = organ_div.text.strip()
        except Exception:
            pass

        # D-day에서 마감일 계산
        try:
            day_div = item.find_element(By.CSS_SELECTOR, "div.day")
        except Exception:
            return None

        day_text = day_div.text.strip()

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
