import fs from "fs";
import path from "path";

export async function GET(request: Request) {
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

  // E2E_TEST環境変数が設定されている場合はテストフィクスチャを使用
  let data;
  if (process.env.E2E_TEST === "true") {
    const fixtureDir = path.join(process.cwd(), "../../test/e2e/fixtures/client");
    const fixturesPath = path.join(fixtureDir, "reports.json");
    const fileContent = fs.readFileSync(fixturesPath, "utf8");
    data = JSON.parse(fileContent);
  } else {
    // 通常のダミーデータ
    data = [
      {
        slug: "example",
        status: "ready",
        title: "[テスト]人類が人工知能を開発・展開する上で、最優先すべき課題は何でしょうか？",
        description:
          "あのイーハトーヴォのすきとおった風、夏でも底に冷たさをもつ青いそら、うつくしい森で飾られたモリーオ市、郊外のぎらぎらひかる草の波。",
        isPubcom: true,
      },
    ];
  }

  return new Response(JSON.stringify(data), {
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
