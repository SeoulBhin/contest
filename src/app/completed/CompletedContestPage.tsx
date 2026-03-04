"use client";

import { Contest } from "@/types/contest";
import { useContestSplit } from "@/hooks/useContestSplit";
import ContestGrid from "@/components/ContestGrid";

export default function CompletedContestPage({
  contests,
}: {
  contests: Contest[];
}) {
  const { completed, isReady } = useContestSplit(contests);

  if (!isReady) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">완료된 공모전</h1>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-64 animate-pulse rounded-xl border border-gray-200 bg-gray-100"
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">완료된 공모전</h1>
      <ContestGrid
        contests={completed}
        emptyMessage="완료된 공모전이 없습니다."
      />
    </div>
  );
}
