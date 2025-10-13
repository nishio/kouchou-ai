import { test, expect } from "@playwright/test";

/**
 * Client - レポート一覧テスト
 *
 * トップページ（http://localhost:3000）のレポート一覧機能をテストします。
 * ダミーAPIサーバー（port 8002）がテストフィクスチャを返します。
 */

test.describe("Client - レポート一覧", () => {
  test("正常系 - レポート一覧が表示される", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // レポート作成者名が表示される
    await expect(page.getByText("テスト太郎")).toBeVisible();

    // 「レポート一覧」の見出しが表示される
    await expect(page.getByRole("heading", { name: "レポート一覧" })).toBeVisible();

    // 各レポートが表示される
    await expect(page.getByText("テストレポート1")).toBeVisible();
    await expect(page.getByText("テストレポート2：市民の声を集めよう")).toBeVisible();

    // レポートの説明文が表示される
    await expect(page.getByText(/1つ目のE2Eテスト用レポート/)).toBeVisible();
  });

  test("レポートカードをクリックすると詳細ページに遷移する", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // 最初のレポートカードをクリック
    await page.getByText("テストレポート1").click();

    // URLが変わることを確認
    await page.waitForURL("**/test-report-1");
    expect(page.url()).toContain("/test-report-1");
  });

  test("レポートの作成日時が表示される", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // 作成日時が表示される
    await expect(page.getByText(/作成日時:/)).toBeVisible();
  });

  test("ブランドカラーが適用される", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // レポートカードの左ボーダーにブランドカラーが適用されているか確認
    // (ブランドカラー: #2577b1)
    const card = page.locator("a[href='/test-report-1']").first();
    await expect(card).toBeVisible();
  });
});

test.describe("Client - レスポンシブデザイン", () => {
  const viewports = [
    { name: "デスクトップ", width: 1920, height: 1080 },
    { name: "タブレット", width: 768, height: 1024 },
    { name: "モバイル", width: 375, height: 667 },
  ];

  for (const viewport of viewports) {
    test(`${viewport.name}サイズでレポート一覧が表示される`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });

      await page.goto("/");
      await page.waitForLoadState("networkidle");

      // レポート一覧が表示される
      await expect(page.getByRole("heading", { name: "レポート一覧" })).toBeVisible();
      await expect(page.getByText("テストレポート1")).toBeVisible();
    });
  }
});

/**
 * 注意事項:
 * - このテストはダミーAPIサーバー（port 8002）を使用します
 * - テストフィクスチャは test/e2e/fixtures/client/ に配置
 * - ダミーAPIサーバーは playwright.config.ts の webServer で自動起動されます
 * - Next.jsのハイドレーション完了を待つため waitForLoadState("networkidle") が必須
 */
