import contestsData from "../../data/contests.json";
import { Contest, ContestsData } from "@/types/contest";

export function getContestsData(): ContestsData {
  return contestsData as ContestsData;
}

export function getAllContests(): Contest[] {
  return getContestsData().contests;
}

export function getContestById(id: string): Contest | undefined {
  return getAllContests().find((c) => c.id === id);
}

export function getActiveContests(referenceDate?: Date): Contest[] {
  const now = referenceDate || new Date();
  const today = now.toISOString().split("T")[0];
  return getAllContests()
    .filter((c) => c.deadline >= today)
    .sort((a, b) => a.deadline.localeCompare(b.deadline));
}

export function getCompletedContests(referenceDate?: Date): Contest[] {
  const now = referenceDate || new Date();
  const today = now.toISOString().split("T")[0];
  return getAllContests()
    .filter((c) => c.deadline < today)
    .sort((a, b) => b.deadline.localeCompare(a.deadline));
}

export function getLastUpdated(): string {
  return getContestsData().lastUpdated;
}
