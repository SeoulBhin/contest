"use client";

import { useState, useMemo } from "react";
import { Contest, ContestCategory, ContestSource } from "@/types/contest";
import { filterContests } from "@/lib/filters";
import ContestCard from "./ContestCard";
import SearchBar from "./SearchBar";
import FilterBar from "./FilterBar";

interface ContestGridProps {
  contests: Contest[];
  emptyMessage?: string;
}

export default function ContestGrid({
  contests,
  emptyMessage = "공모전이 없습니다.",
}: ContestGridProps) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<ContestCategory | "all">("all");
  const [source, setSource] = useState<ContestSource | "all">("all");

  const filtered = useMemo(
    () => filterContests(contests, { category, source, search }),
    [contests, category, source, search]
  );

  return (
    <div className="space-y-6">
      <SearchBar value={search} onChange={setSearch} />
      <FilterBar
        selectedCategory={category}
        selectedSource={source}
        onCategoryChange={setCategory}
        onSourceChange={setSource}
      />

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-200 py-16">
          <svg className="mb-4 h-12 w-12 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m5.231 13.481L15 17.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v16.5c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9zm3.75 11.625a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
          </svg>
          <p className="text-gray-500">{emptyMessage}</p>
          {(search || category !== "all" || source !== "all") && (
            <button
              onClick={() => {
                setSearch("");
                setCategory("all");
                setSource("all");
              }}
              className="mt-3 text-sm text-blue-600 hover:text-blue-700"
            >
              필터 초기화
            </button>
          )}
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-500">
            {filtered.length}개의 공모전
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((contest) => (
              <ContestCard key={contest.id} contest={contest} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
