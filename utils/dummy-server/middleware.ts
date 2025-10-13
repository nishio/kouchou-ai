import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// テストフィクスチャ（ビルド時にインポート）
const testMetadata = {
  isDefault: false,
  reporter: "テスト太郎",
  message: "これはE2Eテスト用のメッセージです。",
  webLink: "https://example.com",
  brandColor: "#2577b1",
};

export function middleware(request: NextRequest) {
  // E2Eテストモードの時のみ、metadataをテストフィクスチャで上書き
  if (process.env.E2E_TEST === "true" && request.nextUrl.pathname === "/meta/metadata.json") {
    return NextResponse.json(testMetadata, {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }

  return NextResponse.next();
}

export const config = {
  matcher: "/meta/:path*",
};
