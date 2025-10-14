import { test, expect } from "@playwright/test";

/**
 * Seed テスト - 環境確認用テスト
 *
 * このテストは自動実行されるテストスイートではなく、テスト環境を整える上で
 * きちんと整えられているか確認することが目的です。
 *
 * 管理画面が起動して基本的なページが表示されることを確認し、
 * 他のテストを実行する前に環境が正しく設定されているかをチェックします。
 *
 * 実行方法:
 * ```
 * npx playwright test tests/seed.spec.ts --project=verify
 * ```
 *
 * 注意: このテストはverifyプロジェクト（playwright.config.ts）に含まれています。
 */

test.describe("Seed - 環境確認", () => {
  test("管理画面のトップページが開ける", async ({ page }) => {
    // baseURL (http://localhost:4000) に依存
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // ページが正常に読み込まれることを確認
    await expect(page).toHaveTitle(/広聴AI|Kouchou|Admin/);

    // ヘッダーのロゴが表示されることを確認
    await expect(page.getByRole("img", { name: "広聴AI" })).toBeVisible();
  });

  test("レポート作成ページが開ける", async ({ page }) => {
    await page.goto("/create");
    await page.waitForLoadState("networkidle");

    // レポート作成ページの見出しが表示される
    await expect(page.getByRole("heading", { name: "新しいレポートを作成する" })).toBeVisible();
  });
});
