import time
import random
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ContestItem:
    id: str
    title: str
    description: str
    organizer: str
    deadline: str  # YYYY-MM-DD
    startDate: str  # YYYY-MM-DD
    prize: str
    url: str
    thumbnailUrl: str
    category: str
    source: str
    tags: list[str] = field(default_factory=list)
    scrapedAt: str = ""
    status: str = "active"

    def to_dict(self) -> dict:
        return asdict(self)


class BaseScraper(ABC):
    """모든 스크래퍼의 추상 베이스 클래스"""

    SOURCE_NAME: str = ""
    BASE_URL: str = ""
    MIN_DELAY: float = 2.0
    MAX_DELAY: float = 5.0

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _delay(self):
        """요청 간 랜덤 딜레이"""
        delay = random.uniform(self.MIN_DELAY, self.MAX_DELAY)
        time.sleep(delay)

    def _get_headers(self) -> dict:
        return {
            "User-Agent": "DevContestKR-Bot/1.0 (https://github.com/SeoulBhin/contest; educational project)",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
        }

    def _categorize(self, title: str, description: str = "") -> str:
        """제목과 설명으로 카테고리 추론"""
        text = (title + " " + description).lower()

        if any(kw in text for kw in ["알고리즘", "코딩테스트", "코딩 테스트", "프로그래밍 대회"]):
            return "algorithm"
        if any(kw in text for kw in ["해커톤", "hackathon"]):
            return "hackathon"
        if any(kw in text for kw in ["ai", "인공지능", "머신러닝", "딥러닝", "machine learning"]):
            return "ai_ml"
        if any(kw in text for kw in ["웹", "앱", "모바일", "프론트엔드", "백엔드", "web", "app"]):
            return "web_mobile"
        if any(kw in text for kw in ["게임", "game", "유니티", "언리얼"]):
            return "game"
        if any(kw in text for kw in ["보안", "security", "ctf", "해킹"]):
            return "security"
        if any(kw in text for kw in ["데이터", "data", "빅데이터"]):
            return "data"
        if any(kw in text for kw in ["iot", "사물인터넷", "임베디드", "로봇"]):
            return "iot"
        if any(kw in text for kw in ["소프트웨어", "sw", "개발", "오픈소스"]):
            return "sw_general"
        return "other"

    @abstractmethod
    def scrape(self) -> list[ContestItem]:
        """공모전 목록을 크롤링하여 반환"""
        pass
