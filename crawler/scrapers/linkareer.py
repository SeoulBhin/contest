"""링커리어 (linkareer.com) 스크래퍼 - React SPA, Selenium 사용"""

import re
import json
from datetime import datetime
from .base import BaseScraper, ContestItem
from ..utils.date_parser import parse_korean_date

try:
    import requests as req_lib

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

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
    GRAPHQL_URL = "https://api.linkareer.com/graphql"

    def scrape(self) -> list[ContestItem]:
        self.logger.info("Linkareer 크롤링 시작")

        # GraphQL API 직접 호출 시도
        contests = self._try_graphql()
        if contests:
            return contests

        # Selenium 폴백
        if HAS_SELENIUM:
            return self._try_selenium()

        self.logger.error("Linkareer: GraphQL 및 Selenium 모두 사용 불가")
        return []

    def _try_graphql(self) -> list[ContestItem]:
        """GraphQL API 직접 호출"""
        if not HAS_REQUESTS:
            return []

        self.logger.info("Linkareer: GraphQL API 호출 시도")
        contests = []

        try:
            query = """
            query Activities($filterBy: ActivityFilterBy, $pageInfo: PageInfoInputType, $orderBy: ActivityOrderBy) {
              activities(filterBy: $filterBy, pageInfo: $pageInfo, orderBy: $orderBy) {
                nodes {
                  id
                  title
                  description
                  organization {
                    name
                  }
                  startAt
                  closeAt
                  thumbnail
                  activityTypeCategories
                  url
                  reward
                  tags {
                    name
                  }
                }
                totalCount
              }
            }
            """
            variables = {
                "filterBy": {
                    "activityTypeCategory": "CONTEST",
                    "categoryIDs": [],
                    "status": "OPEN",
                },
                "pageInfo": {"page": 1, "size": 30},
                "orderBy": {"field": "CLOSE_AT", "direction": "ASC"},
            }

            headers = {
                **self._get_headers(),
                "Content-Type": "application/json",
            }

            response = req_lib.post(
                self.GRAPHQL_URL,
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=15,
            )

            if response.status_code != 200:
                self.logger.warning(f"Linkareer GraphQL 응답 코드: {response.status_code}")
                return []

            data = response.json()
            nodes = (
                data.get("data", {}).get("activities", {}).get("nodes", [])
            )

            self.logger.info(f"Linkareer GraphQL: {len(nodes)}개 항목 발견")

            for node in nodes:
                try:
                    contest = self._parse_graphql_node(node)
                    if contest:
                        contests.append(contest)
                except Exception as e:
                    self.logger.warning(f"Linkareer GraphQL 노드 파싱 실패: {e}")

        except Exception as e:
            self.logger.warning(f"Linkareer GraphQL 실패: {e}")

        return contests

    def _parse_graphql_node(self, node: dict) -> ContestItem | None:
        node_id = str(node.get("id", ""))
        if not node_id:
            return None

        title = node.get("title", "").strip()
        if not title:
            return None

        org = node.get("organization", {})
        organizer = org.get("name", "") if org else ""

        close_at = node.get("closeAt", "")
        start_at = node.get("startAt", "")

        deadline = parse_korean_date(close_at) if close_at else None
        start_date = parse_korean_date(start_at) if start_at else None

        if not deadline:
            # ISO 형식 시도
            if close_at:
                try:
                    dt = datetime.fromisoformat(close_at.replace("Z", "+00:00"))
                    deadline = dt.strftime("%Y-%m-%d")
                except ValueError:
                    pass
        if not deadline:
            return None

        if not start_date and start_at:
            try:
                dt = datetime.fromisoformat(start_at.replace("Z", "+00:00"))
                start_date = dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")

        description = node.get("description", "") or ""
        thumbnail = node.get("thumbnail", "") or ""
        reward = node.get("reward", "") or ""
        url = node.get("url", "") or f"{self.BASE_URL}/activity/{node_id}"

        tags = [t.get("name", "") for t in (node.get("tags") or []) if t.get("name")]
        category = self._categorize(title, description)

        return ContestItem(
            id=f"linkareer-{node_id}",
            title=title,
            description=description[:500],
            organizer=organizer,
            deadline=deadline,
            startDate=start_date,
            prize=reward,
            url=url,
            thumbnailUrl=thumbnail,
            category=category,
            source=self.SOURCE_NAME,
            tags=tags[:5],
            scrapedAt=datetime.now().isoformat(),
        )

    def _try_selenium(self) -> list[ContestItem]:
        """Selenium으로 크롤링 (GraphQL 실패 시 폴백)"""
        self.logger.info("Linkareer: Selenium 폴백 시도")
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
            driver.get(f"{self.BASE_URL}/list/contest")

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[href*='/activity/']")
                )
            )
            self._delay()

            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/activity/']")
            self.logger.info(f"Linkareer Selenium: {len(links)}개 링크 발견")

            seen = set()
            for link in links:
                try:
                    href = link.get_attribute("href") or ""
                    id_match = re.search(r"/activity/(\d+)", href)
                    if not id_match:
                        continue
                    node_id = id_match.group(1)
                    if node_id in seen:
                        continue
                    seen.add(node_id)

                    title = link.text.strip()
                    if not title or len(title) < 3:
                        continue

                    contests.append(
                        ContestItem(
                            id=f"linkareer-{node_id}",
                            title=title,
                            description="",
                            organizer="",
                            deadline=datetime.now().strftime("%Y-%m-%d"),
                            startDate=datetime.now().strftime("%Y-%m-%d"),
                            prize="",
                            url=href,
                            thumbnailUrl="",
                            category=self._categorize(title),
                            source=self.SOURCE_NAME,
                            tags=[],
                            scrapedAt=datetime.now().isoformat(),
                        )
                    )
                except Exception as e:
                    self.logger.warning(f"Linkareer Selenium 항목 파싱 실패: {e}")

        except Exception as e:
            self.logger.error(f"Linkareer Selenium 크롤링 실패: {e}")
        finally:
            if driver:
                driver.quit()

        self.logger.info(f"Linkareer Selenium: {len(contests)}개 수집 완료")
        return contests
