import Link from "next/link";
import { Contest, CATEGORY_LABELS, SOURCE_LABELS } from "@/types/contest";
import { formatDate } from "@/lib/dates";
import CountdownBadge from "./CountdownBadge";

export default function ContestCard({ contest }: { contest: Contest }) {
  return (
    <Link
      href={`/contest/${contest.id}`}
      className="group flex flex-col rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition-all hover:border-blue-300 hover:shadow-md"
    >
      <div className="mb-3 flex items-start justify-between gap-2">
        <span className="rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
          {CATEGORY_LABELS[contest.category]}
        </span>
        <CountdownBadge deadline={contest.deadline} />
      </div>

      <h3 className="mb-2 text-lg font-semibold text-gray-900 group-hover:text-blue-600 line-clamp-2">
        {contest.title}
      </h3>

      <p className="mb-4 text-sm text-gray-500 line-clamp-2">
        {contest.description}
      </p>

      <div className="mt-auto flex flex-col gap-2 text-sm text-gray-600">
        <div className="flex items-center gap-1.5">
          <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3H21m-3.75 3H21" />
          </svg>
          <span className="truncate">{contest.organizer}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
          </svg>
          <span>마감: {formatDate(contest.deadline)}</span>
        </div>
        {contest.prize && (
          <div className="flex items-center gap-1.5">
            <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.996.044-1.573.959-1.573 1.96C3.677 7.587 5.254 9 7.205 9h9.59c1.95 0 3.528-1.413 3.528-2.804 0-1.001-.577-1.916-1.573-1.96A3 3 0 0015.75 3a3.001 3.001 0 00-3 .75A3 3 0 009.75 3a3.002 3.002 0 00-3 1.236z" />
            </svg>
            <span className="truncate">{contest.prize}</span>
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between border-t border-gray-100 pt-3">
        <span className="text-xs text-gray-400">
          {SOURCE_LABELS[contest.source]}
        </span>
        <div className="flex flex-wrap gap-1">
          {contest.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-500"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </Link>
  );
}
