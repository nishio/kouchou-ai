import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { NextResponse } from "next/server";
import { createdReports } from "../../../lib/createdReports";

export async function GET(request: Request) {
  const requestApiKey = request.headers.get("x-api-key");
  const validApiKey = process.env.ADMIN_API_KEY;
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, x-api-key",
  };

  if (!requestApiKey || requestApiKey !== validApiKey) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401, headers: corsHeaders });
  }

  // E2E_TEST環境変数が設定されている場合はテストフィクスチャを使用
  if (process.env.E2E_TEST === "true") {
    const fixturePath = resolve(process.cwd(), "../../test/e2e/fixtures/client/reports.json");
    const fixtureJson = await readFile(fixturePath, "utf-8");
    const reports = JSON.parse(fixtureJson);
    return NextResponse.json(reports, { headers: corsHeaders });
  }

  // 通常のダミーデータ
  return NextResponse.json(
    [
      {
        id: "example",
        slug: "example",
        status: "ready",
        title: "[テスト]人類が人工知能を開発・展開する上で、最優先すべき課題は何でしょうか？",
        createdAt: new Date().toISOString(),
      },
    ],
    { headers: corsHeaders },
  );
}

// レポート作成。本番の API（apps/api/src/routers/admin_report.py の create_report）と同じく 202 を返す。
// E2E_TEST のときは受け取った本文を控え、テストが GET /e2e/created-reports/:slug で送信内容を確かめられるようにする
export async function POST(request: Request) {
  if (request.headers.get("x-api-key") !== process.env.ADMIN_API_KEY) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }
  const body = await request.json().catch(() => null);
  const input = typeof body?.input === "string" ? body.input : "";
  if (!input) {
    return NextResponse.json({ detail: "input is required" }, { status: 422 });
  }
  const store = createdReports();
  if (store.has(input)) {
    return NextResponse.json({ detail: "Report ID already exists" }, { status: 409 });
  }
  if (process.env.E2E_TEST === "true") {
    store.set(input, { body, hasUserApiKey: request.headers.has("x-user-api-key") });
  }
  return new Response(null, { status: 202 });
}

export async function OPTIONS() {
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, x-api-key",
    },
  });
}
