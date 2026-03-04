"use client";

import {
  ContestCategory,
  ContestSource,
  CATEGORY_LABELS,
  SOURCE_LABELS,
} from "@/types/contest";

interface FilterBarProps {
  selectedCategory: ContestCategory | "all";
  selectedSource: ContestSource | "all";
  onCategoryChange: (category: ContestCategory | "all") => void;
  onSourceChange: (source: ContestSource | "all") => void;
}

export default function FilterBar({
  selectedCategory,
  selectedSource,
  onCategoryChange,
  onSourceChange,
}: FilterBarProps) {
  const categories: (ContestCategory | "all")[] = [
    "all",
    ...Object.keys(CATEGORY_LABELS) as ContestCategory[],
  ];

  const sources: (ContestSource | "all")[] = [
    "all",
    ...Object.keys(SOURCE_LABELS) as ContestSource[],
  ];

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div className="flex flex-wrap gap-1.5">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => onCategoryChange(cat)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
              selectedCategory === cat
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {cat === "all" ? "전체" : CATEGORY_LABELS[cat]}
          </button>
        ))}
      </div>
      <div className="flex gap-1.5 sm:ml-auto">
        {sources.map((src) => (
          <button
            key={src}
            onClick={() => onSourceChange(src)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
              selectedSource === src
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {src === "all" ? "전체" : SOURCE_LABELS[src]}
          </button>
        ))}
      </div>
    </div>
  );
}
