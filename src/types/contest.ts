export type ContestCategory =
  | "algorithm"
  | "hackathon"
  | "ai_ml"
  | "web_mobile"
  | "game"
  | "security"
  | "data"
  | "iot"
  | "sw_general"
  | "other";

export type ContestSource = "linkareer" | "contestkorea" | "thinkcontest" | "wevity" | "dacon";

export type ContestStatus = "active" | "completed";

export interface Contest {
  id: string;
  title: string;
  description: string;
  organizer: string;
  deadline: string;
  startDate: string;
  prize: string;
  url: string;
  thumbnailUrl: string;
  category: ContestCategory;
  source: ContestSource;
  tags: string[];
  scrapedAt: string;
  status: ContestStatus;
}

export interface ContestsData {
  lastUpdated: string;
  totalCount: number;
  contests: Contest[];
}

export const CATEGORY_LABELS: Record<ContestCategory, string> = {
  algorithm: "알고리즘",
  hackathon: "해커톤",
  ai_ml: "AI/ML",
  web_mobile: "웹/모바일",
  game: "게임",
  security: "보안",
  data: "데이터",
  iot: "IoT",
  sw_general: "SW 일반",
  other: "기타",
};

export const SOURCE_LABELS: Record<ContestSource, string> = {
  linkareer: "링커리어",
  contestkorea: "컨테스트코리아",
  thinkcontest: "씽굿",
  wevity: "위비티",
  dacon: "데이콘",
};
