import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "DEV 공모전 - 한국 개발자 공모전 모음",
  description:
    "대한민국의 개발자 관련 공모전, 해커톤, 프로그래밍 대회 정보를 한눈에 확인하세요.",
  openGraph: {
    title: "DEV 공모전 - 한국 개발자 공모전 모음",
    description:
      "대한민국의 개발자 관련 공모전, 해커톤, 프로그래밍 대회 정보를 한눈에 확인하세요.",
    locale: "ko_KR",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        <link
          rel="stylesheet"
          as="style"
          crossOrigin="anonymous"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"
        />
      </head>
      <body className="flex min-h-screen flex-col bg-gray-50 font-[Pretendard] text-gray-900 antialiased">
        <Navbar />
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
