import { test, expect } from "@playwright/test";

test("シンプルな接続テスト - Admin", async ({ page }) => {
  // 管理画面（port 4000）の接続確認
  const response = await page.goto("http://localhost:4000/create");

  console.log("Status:", response?.status());
  console.log("URL:", page.url());

  // ページの内容を取得
  const content = await page.content();
  console.log("Page length:", content.length);

  // 何か表示されているか確認
  expect(response?.status()).toBe(200);
});

test("シンプルな接続テスト - Client", async ({ page }) => {
  // Client（port 3000）の接続確認
  const response = await page.goto("http://localhost:3000");

  console.log("Status:", response?.status());
  console.log("URL:", page.url());

  // ページの内容を取得
  const content = await page.content();
  console.log("Page length:", content.length);

  // 何か表示されているか確認
  expect(response?.status()).toBe(200);
});
