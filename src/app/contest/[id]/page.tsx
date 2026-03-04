import Link from "next/link";
import { getAllContests, getContestById } from "@/lib/contests";
import { formatDate } from "@/lib/dates";
import { CATEGORY_LABELS, SOURCE_LABELS } from "@/types/contest";
import CountdownBadge from "@/components/CountdownBadge";

export function generateStaticParams() {
  return getAllContests().map((c) => ({ id: c.id }));
}

export default async function ContestDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const contest = getContestById(id);

  if (!contest) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <h1 className="text-2xl font-bold text-gray-900">
          공모전을 찾을 수 없습니다
        </h1>
        <Link
          href="/"
          className="mt-4 text-blue-600 hover:text-blue-700"
        >
          홈으로 돌아가기
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl">
      <Link
        href="/"
        className="mb-6 inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
        목록으로
      </Link>

      <article className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <span className="rounded-md bg-blue-50 px-2.5 py-1 text-sm font-medium text-blue-700">
            {CATEGORY_LABELS[contest.category]}
          </span>
          <span className="rounded-md bg-gray-100 px-2.5 py-1 text-sm text-gray-600">
            {SOURCE_LABELS[contest.source]}
          </span>
          <CountdownBadge deadline={contest.deadline} />
        </div>

        <h1 className="mb-4 text-2xl font-bold text-gray-900 sm:text-3xl">
          {contest.title}
        </h1>

        <div className="mb-6 grid gap-3 rounded-lg bg-gray-50 p-4 text-sm sm:grid-cols-2">
          <div>
            <span className="font-medium text-gray-500">주최</span>
            <p className="text-gray-900">{contest.organizer}</p>
          </div>
          <div>
            <span className="font-medium text-gray-500">접수 기간</span>
            <p className="text-gray-900">
              {formatDate(contest.startDate)} ~ {formatDate(contest.deadline)}
            </p>
          </div>
          {contest.prize && (
            <div>
              <span className="font-medium text-gray-500">상금/혜택</span>
              <p className="text-gray-900">{contest.prize}</p>
            </div>
          )}
        </div>

        <div className="mb-6">
          <h2 className="mb-2 text-lg font-semibold text-gray-900">상세 내용</h2>
          <p className="whitespace-pre-line leading-relaxed text-gray-700">
            {contest.description}
          </p>
        </div>

        {contest.tags.length > 0 && (
          <div className="mb-6 flex flex-wrap gap-2">
            {contest.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        <a
          href={contest.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          공식 페이지에서 보기
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
          </svg>
        </a>
      </article>
    </div>
  );
}
