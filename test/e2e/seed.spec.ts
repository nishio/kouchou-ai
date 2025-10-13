import { test } from '@playwright/test';
// 最低限：トップを開ける状態に

test('seed', async ({ page }) => {
  await page.goto('/');    // baseURL に依存
  // ここでログイン/初期化が必要なら実装（cookie 設定や API での準備など）
});
