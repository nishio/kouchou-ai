import { NextResponse } from "next/server";
import { createdReports } from "../../../../lib/createdReports";

// E2E 用: POST /admin/reports で受け取った本文を読み戻す（E2E_TEST のときだけ）
export async function GET(_request: Request, context: { params: Promise<{ slug: string }> }) {
  if (process.env.E2E_TEST !== "true") {
    return NextResponse.json({ detail: "Not Found" }, { status: 404 });
  }
  const { slug } = await context.params;
  const record = createdReports().get(slug);
  if (!record) {
    return NextResponse.json({ detail: `レポート ${slug} は作成されていません` }, { status: 404 });
  }
  return NextResponse.json(record);
}
