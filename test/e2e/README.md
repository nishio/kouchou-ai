# Kouchou AI E2Eテスト

このディレクトリにはPlaywrightを使用したKouchou AIアプリケーションのエンドツーエンドテストが含まれています。

## セットアップ

1. 依存関係のインストール:
   ```
   npm install
   ```

2. Playwrightブラウザのインストール:
   ```
   npx playwright install
   ```

3. 環境変数の設定:
   ```
   cp .env.example .env
   ```
   その後、`.env`ファイルを編集してテスト用の認証情報を追加します。

## テストの実行

すべてのテストを実行:
```
npm test
```

UIモードでテストを実行:
```
npm run test:ui
```

デバッグモードでテストを実行:
```
npm run test:debug
```

テストレポートを表示:
```
npm run report
```

## ディレクトリ構造とテストファイル

```
test/e2e/
├── tests/
│   ├── admin/
│   │   └── create-report.spec.ts  # 管理画面のレポート作成テスト
│   ├── simple.spec.ts              # シンプルな接続確認テスト（デバッグ用）
│   └── debug.spec.ts               # 要素確認テスト（デバッグ用）
├── seed.spec.ts                    # 基本的な環境確認テスト
├── pages/                          # ページオブジェクトモデル（将来的に使用）
├── fixtures/                       # テストフィクスチャ
├── playwright.config.ts            # Playwright設定
└── TEST_PLAN.md                    # 詳細なテスト計画書
```

### テストファイルの説明

**本番テスト:**
- `tests/admin/create-report.spec.ts` - 管理画面（port 4000）の主要な機能テスト
- `seed.spec.ts` - 環境が正しく動作しているかの基本確認

**デバッグ用テスト:**
- `tests/simple.spec.ts` - ページが正常にロードされるかをチェック（ステータスコード確認）
- `tests/debug.spec.ts` - ページ内の要素（見出し、ボタン、画像など）を表示して確認

## 新しいテストの追加

1. `tests/` または `tests/admin/` にテストファイルを追加
2. テスト内で **必ず `await page.waitForLoadState("networkidle")` を使用**
3. 複雑な操作には `pages/` にページオブジェクトを作成することを検討

## CI連携

テストは以下のタイミングで自動的に実行されます:
- 毎日0時(UTC)
- `e2e-test-required`ラベルが付いたPR

テスト結果はGitHub Actionsのアーティファクトとして利用できます。

## 重要な注意事項

### Next.jsのレンダリング待機

**必須:** すべてのテストで `await page.waitForLoadState("networkidle")` を使用してください。

```typescript
test("例", async ({ page }) => {
  await page.goto("http://localhost:4000/create");
  await page.waitForLoadState("networkidle");  // ← 必須！

  // この後に要素の検証
  await expect(page.getByRole("heading", { name: "..." })).toBeVisible();
});
```

**理由:** Next.jsはクライアントサイドでReactをハイドレーションするため、`goto`だけでは要素が表示される前にテストが実行されてタイムアウトします。

### webServerの自動起動

`playwright.config.ts` の `webServer` 設定により、テスト実行時に自動的に管理画面サーバー（port 4000）が起動します。

```typescript
webServer: {
  command: "npm run dev --prefix ../../client-admin",
  url: "http://localhost:4000",
  timeout: 120 * 1000,
  reuseExistingServer: !process.env.CI,
}
```

- テスト前に手動でサーバーを起動する必要は**ありません**
- ただし、`client-admin/node_modules` が存在することを確認してください
- 既にサーバーが起動している場合は再利用されます（`reuseExistingServer`）

## テストのデバッグ

テストが失敗する場合は、以下のデバッグ用テストを使用してください：

### 1. 接続確認

```bash
npx playwright test tests/simple.spec.ts
```

- ページが200 OKで返ってくるか確認
- ページのHTMLサイズを表示

### 2. 要素確認

```bash
npx playwright test tests/debug.spec.ts
```

- ページ内の全ての見出し、ボタン、画像を表示
- 要素が見つからない場合のデバッグに使用

### 3. ブラウザで確認

```bash
npx playwright test --headed --debug
```

- ブラウザを表示してステップ実行
- Playwrightインスペクターを使用

## 管理画面テスト

詳細なテスト計画は `TEST_PLAN.md` を参照してください。
