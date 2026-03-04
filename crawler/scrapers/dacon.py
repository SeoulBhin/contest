"""데이콘 (dacon.io) 스크래퍼 - __NUXT__ JSON 파싱"""

import re
import json
import requests
from datetime import datetime
from .base import BaseScraper, ContestItem


class DaconScraper(BaseScraper):
    SOURCE_NAME = "dacon"
    BASE_URL = "https://dacon.io"
    LIST_URL = "https://dacon.io/competitions/"

    def scrape(self) -> list[ContestItem]:
        self.logger.info("Dacon 크롤링 시작")
        contests = []

        try:
            response = requests.get(
                self.LIST_URL,
                headers=self._get_headers(),
                timeout=15,
            )
            response.raise_for_status()
            response.encoding = "utf-8"

            # __NUXT__ JSON 추출
            comp_data = self._extract_nuxt_data(response.text)
            if not comp_data:
                self.logger.warning("Dacon: __NUXT__ 데이터를 찾을 수 없습니다")
                return contests

            self.logger.info(f"Dacon: {len(comp_data)}개 대회 발견")

            for item in comp_data:
                try:
                    contest = self._parse_item(item)
                    if contest:
                        contests.append(contest)
                except Exception as e:
                    self.logger.warning(f"Dacon 항목 파싱 실패: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Dacon 크롤링 실패: {e}")

        self.logger.info(f"Dacon: {len(contests)}개 수집 완료")
        return contests

    def _extract_nuxt_data(self, html: str) -> list[dict] | None:
        """HTML에서 window.__NUXT__ IIFE 데이터의 compData 추출

        Nuxt는 데이터를 IIFE로 직렬화함:
        (function(a,b,c,...){return {...}})(val1, val2, ...)
        변수 참조를 실제 값으로 치환한 뒤 JSON 파싱.
        """
        match = re.search(r"window\.__NUXT__\s*=\s*(.+?);\s*</script>", html, re.DOTALL)
        if not match:
            return None

        raw = match.group(1).strip()

        try:
            # 1) 먼저 순수 JSON인지 시도
            nuxt_data = json.loads(raw)
            return self._find_comp_data(nuxt_data)
        except (json.JSONDecodeError, ValueError):
            pass

        try:
            return self._parse_nuxt_iife(raw)
        except Exception as e:
            self.logger.warning(f"Dacon __NUXT__ 파싱 실패: {e}")

        return None

    def _find_comp_data(self, nuxt_data: dict) -> list[dict] | None:
        """파싱된 __NUXT__ dict에서 compData 배열 탐색"""
        data_list = nuxt_data.get("data", [])
        if data_list and isinstance(data_list, list):
            for data_item in data_list:
                if isinstance(data_item, dict) and "compData" in data_item:
                    return data_item["compData"]
        return None

    def _parse_nuxt_iife(self, raw: str) -> list[dict] | None:
        """Nuxt IIFE 파싱

        형태: (function(a,b,...){return {...}}(v1,v2,...))
        함수 본문 닫는 '}' 뒤의 '(' 와 마지막 '))' 사이가 인자.
        """
        # 파라미터 이름 추출
        param_match = re.match(r"\(?\s*function\s*\(([^)]*)\)", raw)
        if not param_match:
            return None

        param_names = [p.strip() for p in param_match.group(1).split(",")]

        # '}(' 패턴으로 인자 시작점 찾기 (함수 본문 끝 + 인자 시작)
        # 뒤쪽 절반에서 검색하여 본문 내부의 }( 와 혼동 방지
        half = len(raw) // 2
        arg_boundary = re.search(r"\}\s*\(", raw[half:])
        if not arg_boundary:
            return None

        arg_start = half + arg_boundary.end()  # '(' 다음 위치

        # 인자는 마지막 '))' 앞까지
        if raw.rstrip().endswith("))"):
            arg_end = raw.rstrip().rfind(")") - 1
            # rfind가 마지막 )를 찾으므로, 그 앞의 )가 인자 닫기
            arg_end = len(raw.rstrip()) - 2
        else:
            arg_end = raw.rstrip().rfind(")")

        args_str = raw[arg_start:arg_end]
        arg_values = self._tokenize_args(args_str)

        if len(arg_values) != len(param_names):
            self.logger.warning(
                f"Dacon IIFE: 파라미터 수({len(param_names)}) != 인자 수({len(arg_values)})"
            )
            # 짧은 쪽에 맞춤
            count = min(len(param_names), len(arg_values))
            param_names = param_names[:count]
            arg_values = arg_values[:count]

        # 치환 맵 생성
        var_map = dict(zip(param_names, arg_values))

        # 함수 본문에서 return 뒤의 객체 추출
        body_match = re.search(r"\breturn\s+(\{.+\})\s*\}", raw, re.DOTALL)
        if not body_match:
            return None

        body = body_match.group(1)

        # JS → JSON 변환: 변수 참조를 실제 값으로 치환
        # 키 이름(프로퍼티)과 값을 구분해서 값 위치의 변수만 치환
        def replace_var(m):
            name = m.group(0)
            if name in var_map:
                return var_map[name]
            return name

        # JS 객체를 JSON으로: 따옴표 없는 키에 따옴표 추가, 변수 참조 치환
        # 1) void 0 → null
        body = re.sub(r"\bvoid\s+0\b", "null", body)

        # 2) 변수 참조를 값으로 치환 (프로퍼티 값 위치)
        # 패턴: 콜론 뒤의 단독 식별자 (키가 아닌 값 위치)
        body = re.sub(
            r"(?<=:)\s*([a-zA-Z_]\w*)\s*(?=[,}\]])",
            lambda m: (
                var_map.get(m.group(1), m.group(1))
                if m.group(1) not in ("true", "false", "null")
                else m.group(0)
            ),
            body,
        )

        # 배열 내부의 변수 참조도 치환
        body = re.sub(
            r"(?<=[\[,])\s*([a-zA-Z_]\w*)\s*(?=[,\]])",
            lambda m: (
                var_map.get(m.group(1), m.group(1))
                if m.group(1) not in ("true", "false", "null")
                else m.group(0)
            ),
            body,
        )

        # 3) 따옴표 없는 키에 따옴표 추가
        body = re.sub(r"(?<=[{,])\s*([a-zA-Z_]\w*)\s*:", r'"\1":', body)

        # 4) 후행 쉼표 제거
        body = re.sub(r",\s*([}\]])", r"\1", body)

        nuxt_data = json.loads(body)
        return self._find_comp_data(nuxt_data)

    def _tokenize_args(self, args_str: str) -> list[str]:
        """IIFE 인자 문자열을 개별 값 토큰 리스트로 분리

        예: '0,1,false,"hello",null' → ['0', '1', 'false', '"hello"', 'null']
        문자열 내부의 쉼표와 중첩 괄호를 올바르게 처리.
        """
        tokens = []
        current = []
        depth = 0  # 괄호/대괄호/중괄호 깊이
        in_string = False
        string_char = None
        i = 0

        while i < len(args_str):
            ch = args_str[i]

            if in_string:
                current.append(ch)
                if ch == "\\" and i + 1 < len(args_str):
                    current.append(args_str[i + 1])
                    i += 2
                    continue
                if ch == string_char:
                    in_string = False
            elif ch in ('"', "'"):
                in_string = True
                string_char = ch
                current.append(ch)
            elif ch in ("(", "[", "{"):
                depth += 1
                current.append(ch)
            elif ch in (")", "]", "}"):
                depth -= 1
                current.append(ch)
            elif ch == "," and depth == 0:
                token = "".join(current).strip()
                if token:
                    # void 0 → null
                    if token == "void 0":
                        token = "null"
                    tokens.append(token)
                current = []
            else:
                current.append(ch)

            i += 1

        # 마지막 토큰
        token = "".join(current).strip()
        if token:
            if token == "void 0":
                token = "null"
            tokens.append(token)

        return tokens

    def _parse_item(self, item: dict) -> ContestItem | None:
        cpt_id = item.get("cpt_id")
        name = item.get("name", "").strip()
        if not cpt_id or not name:
            return None

        contest_id = f"dacon-{cpt_id}"
        url = f"{self.BASE_URL}/competitions/official/{cpt_id}/overview"

        # 마감일
        period_end = item.get("period_end", "")
        deadline = self._parse_datetime(period_end)
        if not deadline:
            return None

        # 시작일
        period_start = item.get("period_start", "")
        start_date = self._parse_datetime(period_start) or datetime.now().strftime("%Y-%m-%d")

        # 주최사
        organizer = item.get("sponsor", "") or ""

        # 상금 (만원 단위, "0"이면 빈 문자열)
        prize_raw = str(item.get("prize", "0"))
        prize = ""
        if prize_raw and prize_raw != "0":
            prize = f"{prize_raw}만원"

        # 태그 (keyword 필드를 | 로 split)
        keyword = item.get("keyword", "")
        tags = [t.strip() for t in keyword.split("|") if t.strip()] if keyword else []
        tags = tags[:5]

        category = self._categorize(name, keyword)

        return ContestItem(
            id=contest_id,
            title=name,
            description="",
            organizer=organizer,
            deadline=deadline,
            startDate=start_date,
            prize=prize,
            url=url,
            thumbnailUrl="",
            category=category,
            source=self.SOURCE_NAME,
            tags=tags,
            scrapedAt=datetime.now().isoformat(),
        )

    def _parse_datetime(self, dt_str: str) -> str | None:
        """'2026-03-30 09:59:59' 형식에서 'YYYY-MM-DD' 추출"""
        if not dt_str:
            return None
        match = re.match(r"(\d{4}-\d{2}-\d{2})", dt_str)
        return match.group(1) if match else None
