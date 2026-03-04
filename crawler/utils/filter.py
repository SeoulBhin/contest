"""IT/컴퓨터공학 관련 공모전 키워드 화이트리스트 필터"""

import logging

logger = logging.getLogger(__name__)

# fmt: off
CS_KEYWORDS: set[str] = {
    # 프로그래밍 / 개발 일반
    "프로그래밍", "프로그래머", "코딩", "개발자", "개발", "소프트웨어", "sw",
    "오픈소스", "opensource", "github", "깃허브", "api", "sdk",
    "알고리즘", "자료구조", "코딩테스트", "코딩 테스트", "프로그래밍 대회",

    # 웹 / 앱 / 프론트엔드 / 백엔드
    "웹", "web", "앱", "app", "모바일", "mobile", "프론트엔드", "frontend",
    "백엔드", "backend", "풀스택", "fullstack", "react", "vue", "angular",
    "node", "django", "flask", "spring", "ios", "android",
    "html", "css", "javascript", "typescript",

    # AI / 머신러닝 / 딥러닝
    "ai", "인공지능", "머신러닝", "machine learning", "딥러닝", "deep learning",
    "자연어처리", "nlp", "컴퓨터비전", "computer vision", "생성형",
    "llm", "gpt", "챗봇", "chatbot", "신경망", "tensorflow", "pytorch",
    "강화학습", "추천시스템",

    # 데이터
    "데이터", "data", "빅데이터", "big data", "데이터분석", "데이터사이언스",
    "data science", "데이터엔지니어", "etl", "sql", "nosql", "데이터베이스",
    "database", "db", "시각화", "visualization", "통계", "분석",

    # 클라우드 / 인프라 / DevOps
    "클라우드", "cloud", "aws", "azure", "gcp", "docker", "쿠버네티스",
    "kubernetes", "devops", "ci/cd", "서버", "server", "리눅스", "linux",
    "네트워크", "network", "인프라", "infra",

    # 보안
    "보안", "security", "ctf", "해킹", "hacking", "사이버", "cyber",
    "취약점", "암호", "침투", "pentest", "정보보호",

    # 게임 / 그래픽스
    "게임", "game", "유니티", "unity", "언리얼", "unreal",
    "그래픽스", "graphics", "3d", "렌더링",

    # IoT / 임베디드 / 하드웨어
    "iot", "사물인터넷", "임베디드", "embedded", "아두이노", "arduino",
    "라즈베리파이", "raspberry", "센서", "마이크로컨트롤러", "펌웨어", "firmware",
    "로봇", "robot", "자율주행", "드론",

    # 블록체인 / 핀테크
    "블록체인", "blockchain", "스마트컨트랙트", "smart contract", "web3",
    "nft", "defi", "핀테크", "fintech", "암호화폐",

    # AR/VR / 메타버스
    "ar", "vr", "xr", "메타버스", "metaverse", "증강현실", "가상현실",

    # UX/UI 디지털 디자인
    "ux", "ui", "figma", "디지털디자인",

    # 해커톤 / IT 대회
    "해커톤", "hackathon", "it", "ict", "sw중심", "디지털", "digital",
    "테크", "tech", "컴퓨터", "computer", "정보", "스타트업", "startup",
    "디지털 전환", "dx",

    # 컴퓨터공학 학문
    "컴퓨터공학", "컴퓨터과학", "전산", "정보통신", "전자공학",
    "computer science", "computer engineering",
}
# fmt: on


def is_cs_related(contest: dict) -> bool:
    """제목, 설명, 태그에 CS 키워드가 하나라도 있으면 True"""
    text = " ".join([
        contest.get("title", ""),
        contest.get("description", ""),
        " ".join(contest.get("tags", [])),
    ]).lower()

    return any(kw in text for kw in CS_KEYWORDS)


def filter_cs_contests(contests: list[dict]) -> list[dict]:
    """IT/컴퓨터공학 관련 공모전만 필터링"""
    before = len(contests)
    filtered = [c for c in contests if is_cs_related(c)]
    removed = before - len(filtered)
    if removed > 0:
        logger.info(f"비IT 공모전 {removed}개 제외 ({before} → {len(filtered)})")
    return filtered
