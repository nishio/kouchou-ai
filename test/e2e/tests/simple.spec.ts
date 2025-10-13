import { test, expect } from "@playwright/test";

test("シンプルな接続テスト", async ({ page }) => {
  // タイムアウトを確認するため、まずページにアクセスするだけ
  const response = await page.goto("http://localhost:4000/create");

  console.log("Status:", response?.status());
  console.log("URL:", page.url());

  // ページの内容を取得
  const content = await page.content();
  console.log("Page length:", content.length);

  // 何か表示されているか確認
  expect(response?.status()).toBe(200);
});
