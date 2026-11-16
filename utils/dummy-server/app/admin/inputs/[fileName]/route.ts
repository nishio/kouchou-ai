import { NextResponse } from "next/server";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, x-api-key",
};

// 取り込んだスプレッドシートのデータを消す（管理画面の「データをクリアして再入力」）。ダミーでは何も持っていない
export async function DELETE(request: Request, context: { params: Promise<{ fileName: string }> }) {
  if (request.headers.get("x-api-key") !== process.env.ADMIN_API_KEY) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401, headers: corsHeaders });
  }
  const { fileName } = await context.params;
  return NextResponse.json(
    { status: "success", message: `ファイル ${fileName}.csv を削除しました` },
    { headers: corsHeaders },
  );
}

export function OPTIONS() {
  return new Response(null, { headers: corsHeaders });
}
