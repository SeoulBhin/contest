"use client";

import { useEffect, useState } from "react";
import { getDDay } from "@/lib/dates";

export default function CountdownBadge({ deadline }: { deadline: string }) {
  const [dday, setDday] = useState<number | null>(null);

  useEffect(() => {
    setDday(getDDay(deadline));
  }, [deadline]);

  if (dday === null) return null;

  if (dday < 0) {
    return (
      <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
        마감
      </span>
    );
  }

  if (dday === 0) {
    return (
      <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-700 animate-pulse">
        D-Day
      </span>
    );
  }

  if (dday <= 7) {
    return (
      <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-700">
        D-{dday}
      </span>
    );
  }

  if (dday <= 30) {
    return (
      <span className="inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800">
        D-{dday}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">
      D-{dday}
    </span>
  );
}
