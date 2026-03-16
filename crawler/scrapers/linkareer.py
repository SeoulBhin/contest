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

    # 접수중인 공모전 (카테고리 필터 없이 전체 조회 후 코드에서 IT 필터링)
    LIST_URL = "https://linkareer.com/list/contest?filterBy_status=OPEN&orderBy_direction=DESC&orderBy_field=CREATED_AT"

    # IT/SW 관련 키워드 필터
    IT_KEYWORDS = [
        "ai", "인공지능", "sw", "소프트웨어", "코딩", "프로그래밍",
        "해커톤", "hackathon", "데이터", "블록체인", "ict", "it",
        "앱", "웹", "개발", "알고리즘", "로봇", "디지털",
        "메타버스", "클라우드", "사이버", "보안", "게임",
        "iot", "빅데이터", "머신러닝", "딥러닝", "gpt", "llm",
        "과학", "공학", "테크", "tech", "컴퓨터", "전자",
    ]

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

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "a[href*='/activity/']")
                    )
                )
            except Exception:
                self.logger.warning("Linkareer: 페이지 로딩 타임아웃 또는 결과 없음")
                return []
            self._delay()

            # 카드 컨테이너를 기준으로 탐색 (사이트 구조 변경에 유연하게 대응)
            cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/activity/']")
            self.logger.info(f"Linkareer: {len(cards)}개 링크 발견")

            seen = set()
            for card in cards:
                try:
                    href = card.get_attribute("href") or ""
                    id_match = re.search(r"/activity/(\d+)", href)
                    if not id_match:
                        continue

                    node_id = id_match.group(1)
                    if node_id in seen:
                        continue

                    # 제목 추출 - 다양한 셀렉터 시도
                    title = ""
                    for selector in ["h5", "h4", "h3", "h6", "[class*='title']", "[class*='Title']", "strong", "span"]:
                        try:
                            el = card.find_element(By.CSS_SELECTOR, selector)
                            text = el.text.strip()
                            if text and len(text) >= 3:
                                title = text
                                break
                        except Exception:
                            continue

                    # 셀렉터로 못 찾으면 전체 텍스트에서 추출
                    if not title:
                        full_text = card.text.strip()
                        # 여러 줄에서 가장 긴 줄을 제목으로 사용
                        lines = [l.strip() for l in full_text.split("\n") if len(l.strip()) >= 3]
                        if lines:
                            title = max(lines, key=len)

                    # "추천" 프리픽스 제거
                    title = re.sub(r"^추천\s*", "", title)

                    if not title or len(title) < 3:
                        self.logger.debug(f"Linkareer 제목 추출 실패: href={href}, text='{card.text.strip()[:50]}'")
                        continue

                    # IT/SW 관련 키워드 필터링
                    if not any(kw in title.lower() for kw in self.IT_KEYWORDS):
                        continue

                    seen.add(node_id)

                    # 주최사 추출 시도
                    organizer = ""
                    try:
                        org_el = card.find_element(By.CSS_SELECTOR, "p[class*='organization']")
                        organizer = org_el.text.strip()
                    except Exception:
                        pass

                    # D-day 추출 시도
                    deadline = datetime.now().strftime("%Y-%m-%d")
                    card_text = card.text
                    dday_match = re.search(r"D-(\d+)", card_text)
                    if dday_match:
                        days = int(dday_match.group(1))
                        deadline = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

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
