import { getLastUpdated } from "@/lib/contests";
import { formatLastUpdated } from "@/lib/dates";

export default function Footer() {
  const lastUpdated = getLastUpdated();

  return (
    <footer className="border-t border-gray-200 bg-gray-50">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className="flex flex-col items-center gap-2 text-sm text-gray-500">
          <p>
            마지막 업데이트: {formatLastUpdated(lastUpdated)}
          </p>
          <p>
            데이터 출처: 링커리어, 컨테스트코리아, 씽굿
          </p>
          <p className="mt-2 text-xs text-gray-400">
            본 사이트는 공모전 정보를 자동 수집하여 제공하며, 정확한 내용은 각
            공모전 공식 페이지를 확인해주세요.
          </p>
        </div>
      </div>
    </footer>
  );
}
