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

### 前提条件

テストを実行する前に、対象のサーバーを起動してください：

**管理画面テスト（Admin）を実行する場合:**
```bash
# 別のターミナルで
cd client-admin
npm run dev
# port 4000 で起動
```

**Clientテスト（レポート表示）を実行する場合:**

Clientテストは2つのサーバーが必要です：
1. ダミーAPIサーバー（port 8002）
2. Clientアプリケーション（port 3000）

詳細は「Clientテスト（レポート表示画面）」セクションを参照してください。

**すべてのテストを実行する場合:**

管理画面テストとClientテストの両方を実行する場合、3つのサーバーを起動：
1. 管理画面（port 4000）
2. ダミーAPIサーバー（port 8002）
3. Client（port 3000、ダミーAPIサーバーを参照）

### テスト実行コマンド

すべてのテストを実行:
```bash
npm test
```

管理画面のテストのみ実行:
```bash
npx playwright test --project=admin
```

Clientのテストのみ実行:
```bash
npx playwright test --project=client
```

UIモードでテストを実行:
```bash
npm run test:ui
```

デバッグモードでテストを実行:
```bash
npm run test:debug
```

テストレポートを表示:
```bash
npm run report
```

## ディレクトリ構造とテストファイル

```
test/e2e/
├── tests/
│   ├── admin/
│   │   └── create-report.spec.ts  # 管理画面のレポート作成テスト
│   ├── client/
│   │   ├── reports.spec.ts        # Client レポート一覧テスト
│   │   └── report-detail.spec.ts  # Client レポート詳細テスト
│   ├── verify-dummy-server.spec.ts # ダミーサーバー検証テスト
│   ├── verify-environment.spec.ts  # 環境設定検証テスト
│   ├── simple.spec.ts             # シンプルな接続確認テスト（デバッグ用）
│   └── debug.spec.ts              # 要素確認テスト（デバッグ用）
├── seed.spec.ts                   # 基本的な環境確認テスト
├── fixtures/
│   ├── admin/                     # 管理画面用フィクスチャ
│   └── client/                    # Client用フィクスチャ（APIモック）
│       ├── metadata.json          # Meta情報
│       ├── reports.json           # レポート一覧
│       └── report-test-report-1.json  # レポート詳細
├── pages/                         # ページオブジェクトモデル（将来的に使用）
├── playwright.config.ts           # Playwright設定
├── TEST_PLAN.md                   # 管理画面テスト計画書
└── CLIENT_TEST_PLAN.md            # Clientテスト計画書
```

### テストファイルの説明

**本番テスト:**
- `tests/admin/create-report.spec.ts` - 管理画面（port 4000）の主要な機能テスト
- `tests/client/reports.spec.ts` - Client（port 3000）のレポート一覧テスト
- `tests/client/report-detail.spec.ts` - Client（port 3000）のレポート詳細テスト
- `seed.spec.ts` - 環境が正しく動作しているかの基本確認

**検証テスト（Clientテスト実行前に推奨）:**
- `tests/verify-dummy-server.spec.ts` - ダミーサーバーが期待通りにテストフィクスチャを返すことを確認
- `tests/verify-environment.spec.ts` - 必要なサーバーが正しい環境変数で起動していることを確認

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

### プロジェクトの分離

`playwright.config.ts` では3つのプロジェクトが定義されています：

- **verify**: 検証テスト（ダミーサーバーと環境設定の確認）
- **admin**: 管理画面テスト（port 4000）
- **client**: Clientテスト（port 3000）

各プロジェクトは独立して実行でき、それぞれ異なるbaseURLを使用します。

### 検証テストの重要性

Clientテストを実行する前に、検証テストを実行することを強く推奨します：

```bash
# ダミーサーバーの動作確認
npx playwright test tests/verify-dummy-server.spec.ts --project=verify

# 環境変数と設定の確認
npx playwright test tests/verify-environment.spec.ts --project=verify
```

**なぜ検証テストが重要か:**
1. **ダミーサーバーの検証** (`verify-dummy-server.spec.ts`)
   - ダミーサーバーが期待通りにテストフィクスチャを返しているか確認
   - `/meta/metadata.json`, `/reports`, `/reports/[slug]` のエンドポイントを個別にテスト
   - フィクスチャのデータ構造が正しいか検証

2. **環境設定の検証** (`verify-environment.spec.ts`)
   - clientサーバーがダミーサーバーを正しく参照しているか確認
   - 環境変数が正しく設定されているか確認
   - テストに必要なサーバーが起動しているか確認

これらの検証テストが失敗する場合、Clientテストも失敗するため、先に問題を特定できます。

## テストのデバッグ

テストが失敗する場合は、以下の順序でデバッグを行ってください：

### 0. 検証テスト（最優先）

```bash
# まず検証テストで基本的な環境を確認
npx playwright test tests/verify-dummy-server.spec.ts --project=verify
npx playwright test tests/verify-environment.spec.ts --project=verify
```

これらが失敗する場合、サーバーの起動状態や環境変数の設定を確認してください。

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

## 管理画面テスト（Admin）

詳細なテスト計画は `TEST_PLAN.md` を参照してください。

### 対象

- **URL**: http://localhost:4000（client-admin）
- **機能**: レポート作成、パイプライン設定

### テスト実行

```bash
# 事前に管理画面サーバーを起動
cd ../../client-admin && npm run dev

# 管理画面のテストのみ実行
npx playwright test --project=admin
# または
npx playwright test tests/admin/
```

## Clientテスト（レポート表示画面）

詳細なテスト計画は `CLIENT_TEST_PLAN.md` を参照してください。

### 対象

- **URL**: http://localhost:3000（client）
- **機能**: レポート一覧表示、レポート詳細表示

### テストの特徴

**ダミーAPIサーバーを使用:**
- `utils/dummy-server`（Next.js）がテストフィクスチャを返すAPIサーバーとして動作
- 実際のPython APIサーバー（port 8001）は不要
- テストデータは `fixtures/client/` に配置
- Next.js Server Componentsが実際にHTTPリクエストを行うため、真のE2Eテスト

### テスト実行

```bash
# ターミナル1: ダミーAPIサーバーを起動（port 8002）
cd utils/dummy-server && npm install
PUBLIC_API_KEY=public E2E_TEST=true npx next dev -p 8002

# ターミナル2: Clientサーバーを起動（port 3000、ダミーAPIサーバーを参照）
cd client
NEXT_PUBLIC_API_BASEPATH=http://localhost:8002 \
API_BASEPATH=http://localhost:8002 \
NEXT_PUBLIC_PUBLIC_API_KEY=public \
npm run dev

# ターミナル3: テストを実行
cd test/e2e

# 推奨: まず検証テストを実行して環境を確認
npx playwright test tests/verify-dummy-server.spec.ts --project=verify
npx playwright test tests/verify-environment.spec.ts --project=verify

# 検証が成功したら、Clientテストを実行
npx playwright test --project=client
# または個別のテストファイルを実行
npx playwright test tests/client/reports.spec.ts
npx playwright test tests/client/report-detail.spec.ts
```

**注意**:
- ダミーサーバーとclientサーバーの両方が起動している必要があります
- clientサーバーは環境変数でダミーサーバー(8002)を参照するように設定します
- テスト失敗時は、まず検証テストを実行してサーバーと環境変数が正しく設定されているか確認してください

### テストデータ（フィクスチャ）

Clientテストでは以下のフィクスチャを使用：

- `fixtures/client/metadata.json` - Meta情報（レポート作成者情報）
- `fixtures/client/reports.json` - レポート一覧（2件のテストレポート）
- `fixtures/client/report-test-report-1.json` - レポート詳細（**実際の本番データ**: `utils/dummy-server/app/reports/example/hierarchical_result.json` から取得したAIと著作権に関する意見データ）

これらのフィクスチャは `utils/dummy-server` が読み込み、HTTP APIとして提供します。

**重要:** `report-test-report-1.json` は実際のパイプライン処理結果をコピーした本番データ構造を使用しているため、テストが実際のデータ構造を正確に検証できます。

### テストコード例

```typescript
test("レポート一覧表示", async ({ page }) => {
  // ダミーAPIサーバーが自動的にテストフィクスチャを返す
  await page.goto("/");
  await page.waitForLoadState("networkidle");

  // テストフィクスチャのデータを検証
  await expect(page.getByText("テスト太郎")).toBeVisible();
  await expect(page.getByText("テストレポート1")).toBeVisible();
});
```

### ダミーサーバーの実装

ダミーサーバー（`utils/dummy-server`）は以下の機能を提供：

1. **環境変数 `E2E_TEST=true`** の時、テストフィクスチャを読み込み
2. **`/meta/metadata.json`**: middleware.tsがテストフィクスチャを返す
3. **`/reports`**: `app/reports/route.ts`がテストフィクスチャを返す
4. **`/reports/[slug]`**: `app/reports/[slug]/route.ts`がテストフィクスチャを返す

E2E_TEST環境変数が設定されていない場合は、通常のダミーデータを返します。
