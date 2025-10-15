import { test, expect } from "@playwright/test";

/**
 * ダミーサーバー動作確認テスト
 *
 * E2Eテストを実行する前に、ダミーサーバーが正しく動作していることを確認します。
 *
 * 前提条件:
 * - ダミーサーバーが port 8002 で起動していること
 * - 環境変数 E2E_TEST=true が設定されていること
 */

test.describe("ダミーサーバー動作確認", () => {
  test("metadata エンドポイントがテストフィクスチャを返す", async ({ request }) => {
    const response = await request.get("http://localhost:8002/meta/metadata.json");
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.reporter).toBe("テスト太郎");
    expect(data.message).toBe("これはE2Eテスト用のメッセージです。");
    expect(data.brandColor).toBe("#2577b1");
  });

  test("reports エンドポイントがテストフィクスチャを返す", async ({ request }) => {
    const response = await request.get("http://localhost:8002/reports", {
      headers: {
        "x-api-key": "public",
      },
    });
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(Array.isArray(data)).toBeTruthy();
    expect(data.length).toBe(2);
    expect(data[0].slug).toBe("test-report-1");
    expect(data[0].title).toBe("テストレポート1");
  });

  test("report detail エンドポイントがテストフィクスチャを返す", async ({ request }) => {
    const response = await request.get("http://localhost:8002/reports/test-report-1", {
      headers: {
        "x-api-key": "public",
      },
    });
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.config.question).toBe("AIと著作権について、どのような意見が寄せられているのか？");
    expect(data.clusters.length).toBeGreaterThan(100);
    expect(data.clusters[1].label).toContain("生成AIと著作権");
    expect(data.comment_num).toBe(100);
  });

  test("存在しないレポートで404を返す", async ({ request }) => {
    const response = await request.get("http://localhost:8002/reports/non-existent", {
      headers: {
        "x-api-key": "public",
      },
    });
    expect(response.status()).toBe(404);
  });
});
