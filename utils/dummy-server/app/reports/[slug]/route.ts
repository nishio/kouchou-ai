import fs from "fs";
import path from "path";

export async function GET(request: Request, context: { params: Promise<{ slug: string }> }) {
  const requestApiKey = request.headers.get("x-api-key");
  const validApiKey = process.env.PUBLIC_API_KEY;
  if (!requestApiKey || requestApiKey !== validApiKey) {
    return new Response(null, {
      status: 401,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }

  const { slug } = await context.params;

  // E2E_TEST環境変数が設定されている場合はテストフィクスチャを使用
  if (process.env.E2E_TEST === "true") {
    const fixtureDir = path.join(process.cwd(), "../../test/e2e/fixtures/client");
    const fixturePath = path.join(fixtureDir, `report-${slug}.json`);

    if (!fs.existsSync(fixturePath)) {
      return new Response(JSON.stringify({ error: "Not Found" }), {
        status: 404,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      });
    }

    const fileContent = fs.readFileSync(fixturePath, "utf8");
    const data = JSON.parse(fileContent);

    return new Response(JSON.stringify(data), {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }

  // 通常のダミーサーバーの動作: exampleの場合のみ
  if (slug === "example") {
    // ここで hierarchical_result.json を読み込む（既存のダミーデータ）
    const exampleData = await import("../example/hierarchical_result.json");
    return new Response(JSON.stringify(exampleData), {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }

  return new Response(JSON.stringify({ error: "Not Found" }), {
    status: 404,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

export async function OPTIONS() {
  return new Response(null, {
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, x-api-key",
    },
  });
}
