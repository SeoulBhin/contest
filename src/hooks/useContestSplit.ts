"use client";

import { useState, useEffect } from "react";
import { Contest } from "@/types/contest";

export function useContestSplit(contests: Contest[]) {
  const [active, setActive] = useState<Contest[]>([]);
  const [completed, setCompleted] = useState<Contest[]>([]);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const today = new Date().toISOString().split("T")[0];
    setActive(
      contests
        .filter((c) => c.deadline >= today)
        .sort((a, b) => a.deadline.localeCompare(b.deadline))
    );
    setCompleted(
      contests
        .filter((c) => c.deadline < today)
        .sort((a, b) => b.deadline.localeCompare(a.deadline))
    );
    setIsReady(true);
  }, [contests]);

  return { active, completed, isReady };
}
