// E2E 用: POST /admin/reports で受け取った本文を、レポート ID（input）ごとに控える。
// 管理画面の作成は Server Action から送られ、ブラウザの page.route では捕まえられないため、
// テストは GET /e2e/created-reports/:slug で送られた内容を読み戻して確かめる。
// next dev ではルートごとにモジュールが読み直されることがあるので、globalThis に置いて共有する。

export type CreatedReportRecord = {
  body: Record<string, unknown>;
  hasUserApiKey: boolean;
};

const globalStore = globalThis as typeof globalThis & {
  __e2eCreatedReports?: Map<string, CreatedReportRecord>;
};

export function createdReports(): Map<string, CreatedReportRecord> {
  if (!globalStore.__e2eCreatedReports) {
    globalStore.__e2eCreatedReports = new Map();
  }
  return globalStore.__e2eCreatedReports;
}
