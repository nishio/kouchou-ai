import { test } from "@playwright/test";

test("要素を確認", async ({ page }) => {
  await page.goto("http://localhost:4000/create");

  // ネットワークアイドルとDOMContentLoadedを待つ
  await page.waitForLoadState("networkidle");
  await page.waitForLoadState("domcontentloaded");

  // 少し待ってReactのハイドレーションを待つ
  await page.waitForTimeout(1000);

  // ページのスナップショットを表示
  console.log("\n=== ページタイトル ===");
  console.log(await page.title());

  console.log("\n=== 全ての見出し ===");
  const headings = await page.locator("h1, h2, h3, h4, h5, h6").all();
  for (const h of headings) {
    console.log(`- ${await h.textContent()}`);
  }

  console.log("\n=== 全てのボタン ===");
  const buttons = await page.locator("button").all();
  for (const btn of buttons) {
    const text = await btn.textContent();
    if (text?.trim()) {
      console.log(`- "${text.trim()}"`);
    }
  }

  console.log("\n=== 全ての画像 ===");
  const images = await page.locator("img").all();
  for (const img of images) {
    const alt = await img.getAttribute("alt");
    const src = await img.getAttribute("src");
    console.log(`- alt="${alt}" src="${src}"`);
  }

  console.log("\n=== トップページを確認 ===");
  await page.goto("http://localhost:4000/");
  console.log("タイトル:", await page.title());

  const topImages = await page.locator("img").all();
  console.log("画像数:", topImages.length);
  for (const img of topImages) {
    const alt = await img.getAttribute("alt");
    console.log(`- alt="${alt}"`);
  }
});
