import { NextResponse } from "next/server";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, x-api-key",
};

// 本番の API（apps/api/src/routers/spreadsheet.py の get_spreadsheet_data）と同じ形で返す。
// comment-id は id に、comment・source・url 以外の列は attribute_ を付けた属性になる。
const comments = [
  { id: "sheet-1", comment: "スプレッドシートの1件目のコメントです", attribute_年代: "20代" },
  { id: "sheet-2", comment: "スプレッドシートの2件目のコメントです", attribute_年代: "30代" },
  { id: "sheet-3", comment: "スプレッドシートの3件目のコメントです", attribute_年代: "40代" },
];

export async function GET(request: Request, context: { params: Promise<{ fileName: string }> }) {
  if (request.headers.get("x-api-key") !== process.env.ADMIN_API_KEY) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401, headers: corsHeaders });
  }
  const { fileName } = await context.params;
  return NextResponse.json(
    { status: "success", file_name: fileName, comments, total: comments.length },
    { headers: corsHeaders },
  );
}

export function OPTIONS() {
  return new Response(null, { headers: corsHeaders });
}
