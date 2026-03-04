import { Contest, ContestCategory, ContestSource } from "@/types/contest";

export interface FilterOptions {
  category?: ContestCategory | "all";
  source?: ContestSource | "all";
  search?: string;
}

export function filterContests(
  contests: Contest[],
  options: FilterOptions
): Contest[] {
  let filtered = [...contests];

  if (options.category && options.category !== "all") {
    filtered = filtered.filter((c) => c.category === options.category);
  }

  if (options.source && options.source !== "all") {
    filtered = filtered.filter((c) => c.source === options.source);
  }

  if (options.search && options.search.trim()) {
    const query = options.search.trim().toLowerCase();
    filtered = filtered.filter(
      (c) =>
        c.title.toLowerCase().includes(query) ||
        c.organizer.toLowerCase().includes(query) ||
        c.description.toLowerCase().includes(query) ||
        c.tags.some((t) => t.toLowerCase().includes(query))
    );
  }

  return filtered;
}
