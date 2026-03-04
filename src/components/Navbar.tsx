"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const basePath = "/contest";

export default function Navbar() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    const fullPath = basePath + path;
    if (path === "/") {
      return pathname === fullPath || pathname === fullPath + "/";
    }
    return pathname?.startsWith(fullPath);
  };

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link
          href="/"
          className="text-xl font-bold text-gray-900"
        >
          <span className="text-blue-600">DEV</span> 공모전
        </Link>
        <div className="flex gap-1">
          <Link
            href="/"
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              isActive("/")
                ? "bg-blue-50 text-blue-700"
                : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
            }`}
          >
            진행중
          </Link>
          <Link
            href="/completed"
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              isActive("/completed")
                ? "bg-blue-50 text-blue-700"
                : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
            }`}
          >
            완료
          </Link>
        </div>
      </div>
    </nav>
  );
}
