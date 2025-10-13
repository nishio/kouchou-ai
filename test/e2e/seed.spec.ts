import { test, expect } from "@playwright/test";

/**
 * Seed テスト - 最低限の動作確認
 *
 * このテストは管理画面が起動して基本的なページが表示されることを確認します。
 * 他のテストが実行される前に、環境が正しく設定されているかをチェックします。
 */

test.describe("Seed - 環境確認", () => {
  test("管理画面のトップページが開ける", async ({ page }) => {
    // baseURL (http://localhost:4000) に依存
    await page.goto("/");

    // ページが正常に読み込まれることを確認
    await expect(page).toHaveTitle(/広聴AI|Kouchou|Admin/);

    // ヘッダーのロゴが表示されることを確認
    await expect(page.getByRole("img", { name: "広聴AI" })).toBeVisible();
  });

  test("レポート作成ページが開ける", async ({ page }) => {
    await page.goto("/create");

    // レポート作成ページの見出しが表示される
    await expect(page.getByRole("heading", { name: "新しいレポートを作成する" })).toBeVisible();
  });
});
