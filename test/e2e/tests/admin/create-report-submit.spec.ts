import path from "node:path";
import { type APIRequestContext, expect, test } from "@playwright/test";

/**
 * 作成を開始したときに API へ送られる内容の検証（#395）
 *
 * レポートの作成は Server Action（apps/admin/app/create/api/createReport.ts）から送られるので、
 * ブラウザの page.route では捕まえられない。ダミーサーバーの POST /admin/reports が受け取った本文を
 * レポート ID ごとに控え、GET /e2e/created-reports/:slug で読み戻して確かめる。
 */

const dummyApiBasePath = process.env.E2E_DUMMY_API_BASEPATH ?? "http://localhost:8002";

type CreatedReport = {
  body: {
    input: string;
    inputType: string;
    comments: Record<string, string | null>[];
    model: string;
    workers: number;
    is_pubcom: boolean;
    prompt: { extraction: string; initialLabelling: string; mergeLabelling: string; overview: string };
  };
  hasUserApiKey: boolean;
};

// 並列に走る他のテストと ID が重ならないようにする（英小文字・数字・ハイフンのみ）
function uniqueReportId(prefix: string): string {
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

async function fetchCreatedReport(request: APIRequestContext, slug: string): Promise<CreatedReport> {
  let record: CreatedReport | undefined;
  await expect
    .poll(async () => {
      const response = await request.get(`${dummyApiBasePath}/e2e/created-reports/${slug}`);
      if (!response.ok()) return response.status();
      record = (await response.json()) as CreatedReport;
      return 200;
    })
    .toBe(200);
  if (!record) throw new Error(`レポート ${slug} の送信内容を読み戻せませんでした`);
  return record;
}

test.describe("管理画面 - 作成の送信内容", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/create");
    await page.waitForLoadState("networkidle");
  });

  test("スプレッドシートを取得し、選んだコメント列と属性列で作成を開始できる", async ({ page, request }) => {
    const reportId = uniqueReportId("e2e-sheet");
    await page.getByLabel("ID", { exact: true }).fill(reportId);

    await page.getByRole("tab", { name: "Googleスプレッドシート" }).click();
    const fetchButton = page.getByRole("button", { name: "データを取得" });
    await expect(fetchButton).toBeDisabled();
    await page
      .getByPlaceholder("https://docs.google.com/spreadsheets/d/xxxxxxxxxxxx/edit")
      .fill("https://docs.google.com/spreadsheets/d/e2e-sample/edit");
    await fetchButton.click();

    await expect(page.getByText("スプレッドシートのデータ 3 件を取得しました").first()).toBeVisible();
    await expect(page.getByRole("button", { name: "取得済み" })).toBeDisabled();
    await expect(page.getByRole("combobox", { name: "コメントカラム選択" })).toHaveValue("comment");
    // CSV タブも同じ id の属性チェックボックスを（非表示で）持つので、表示中のスプレッドシートのタブの中で選ぶ
    const sheetPanel = page.getByRole("tabpanel", { name: "Googleスプレッドシート" });
    const attributeCheckbox = sheetPanel.locator('input[type="checkbox"]');
    await expect(attributeCheckbox).toHaveCount(1);
    await expect(sheetPanel.locator("label", { hasText: "attribute_年代" })).toBeVisible();
    await attributeCheckbox.check();

    await page.getByRole("button", { name: "作成前の確認へ" }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog.getByText("コメント件数：3件（非空：3件）")).toBeVisible();
    await dialog.getByRole("button", { name: "未確認のまま作成を開始" }).click();
    await page.waitForURL(/\/$/);

    const { body } = await fetchCreatedReport(request, reportId);
    expect(body.input).toBe(reportId);
    expect(body.inputType).toBe("spreadsheet");
    expect(body.comments).toEqual([
      {
        id: "sheet-1",
        comment: "スプレッドシートの1件目のコメントです",
        source: null,
        url: null,
        attribute_年代: "20代",
      },
      {
        id: "sheet-2",
        comment: "スプレッドシートの2件目のコメントです",
        source: null,
        url: null,
        attribute_年代: "30代",
      },
      {
        id: "sheet-3",
        comment: "スプレッドシートの3件目のコメントです",
        source: null,
        url: null,
        attribute_年代: "40代",
      },
    ]);
  });

  test("AI詳細設定で変えたモデル・並列実行数・プロンプトが送信内容に入る", async ({ page, request }) => {
    const reportId = uniqueReportId("e2e-settings");
    await page.getByLabel("ID", { exact: true }).fill(reportId);
    await page.locator('input[type="file"]').setInputFiles(path.resolve(__dirname, "../../fixtures/sample.csv"));
    await expect(page.getByRole("combobox", { name: "コメントカラム選択" })).toHaveValue("comment");

    await page.getByRole("button", { name: "レポート生成設定" }).click();
    const modelSelect = page.getByRole("combobox", { name: "AIモデル" });
    await expect(modelSelect).toHaveValue("gpt-4o-mini");
    await modelSelect.selectOption("gpt-4o");
    await page.getByLabel("並列実行数").fill("12");
    await page.getByLabel("抽出プロンプト").fill("E2E 抽出プロンプト");
    await page.getByLabel("初期ラベリングプロンプト").fill("E2E 初期ラベリングプロンプト");
    await page.getByLabel("統合ラベリングプロンプト").fill("E2E 統合ラベリングプロンプト");
    await page.getByLabel("要約プロンプト").fill("E2E 要約プロンプト");

    await page.getByRole("button", { name: "作成前の確認へ" }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog.getByText("コメント件数：3件（非空：3件）")).toBeVisible();
    await dialog.getByRole("button", { name: "未確認のまま作成を開始" }).click();
    await page.waitForURL(/\/$/);

    const { body, hasUserApiKey } = await fetchCreatedReport(request, reportId);
    expect(body.inputType).toBe("file");
    expect(body.comments.map((comment) => comment.comment)).toEqual([
      "これはテスト用のコメントです",
      "別のテスト用コメントです",
      "サンプルコメント3です",
    ]);
    expect(body.model).toBe("gpt-4o");
    expect(body.workers).toBe(12);
    expect(body.prompt).toEqual({
      extraction: "E2E 抽出プロンプト",
      initialLabelling: "E2E 初期ラベリングプロンプト",
      mergeLabelling: "E2E 統合ラベリングプロンプト",
      overview: "E2E 要約プロンプト",
    });
    // 「csv出力モード」（パブコメモード）に触らなければ既定値の true で送られる
    expect(body.is_pubcom).toBe(true);
    // APIキー欄を空にしたときは、利用者のキーを送らずサーバー設定を使う
    expect(hasUserApiKey).toBe(false);
  });

  test("「csv出力モード」を外すと is_pubcom: false で送られる", async ({ page, request }) => {
    const reportId = uniqueReportId("e2e-pubcom");
    await page.getByLabel("ID", { exact: true }).fill(reportId);
    await page.locator('input[type="file"]').setInputFiles(path.resolve(__dirname, "../../fixtures/sample.csv"));
    await expect(page.getByRole("combobox", { name: "コメントカラム選択" })).toHaveValue("comment");

    // パブコメモード（isPubcomMode）の切り替えは、画面では「csv出力モード」という名前で出ている
    await page.getByRole("button", { name: "レポート生成設定" }).click();
    const pubcomCheckbox = page.getByRole("checkbox", { name: "csv出力モード" });
    await expect(pubcomCheckbox).toBeChecked();
    // Chakra の Checkbox は input を見えなくしているので、uncheck() ではなくラベルを押して切り替える
    await page.locator("label", { hasText: "csv出力モード" }).click();
    await expect(pubcomCheckbox).not.toBeChecked();

    await page.getByRole("button", { name: "作成前の確認へ" }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog.getByText("コメント件数：3件（非空：3件）")).toBeVisible();
    await dialog.getByRole("button", { name: "未確認のまま作成を開始" }).click();
    await page.waitForURL(/\/$/);

    const { body } = await fetchCreatedReport(request, reportId);
    expect(body.input).toBe(reportId);
    expect(body.is_pubcom).toBe(false);
  });
});
