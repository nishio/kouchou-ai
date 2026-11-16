import { NextResponse } from "next/server";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, x-api-key",
};

// 本番の API（apps/api/src/routers/spreadsheet.py）は URL から CSV を取り込んで inputs/<file_name>.csv に置く。
// ダミーでは外部に取りに行かず、取り込んだことにして同じ形の応答を返す。
export async function POST(request: Request) {
  if (request.headers.get("x-api-key") !== process.env.ADMIN_API_KEY) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401, headers: corsHeaders });
  }
  const body = await request.json().catch(() => ({}));
  const url = typeof body?.url === "string" ? body.url : "";
  const fileName = typeof body?.file_name === "string" ? body.file_name : "";
  if (!url.startsWith("https://docs.google.com/spreadsheets/") || !fileName) {
    return NextResponse.json({ detail: "無効なスプレッドシートURLです" }, { status: 400, headers: corsHeaders });
  }
  return NextResponse.json(
    {
      status: "success",
      message: "スプレッドシートのインポートが完了しました",
      file_path: `inputs/${fileName}.csv`,
      file_name: fileName,
    },
    { headers: corsHeaders },
  );
}

export function OPTIONS() {
  return new Response(null, { headers: corsHeaders });
}
