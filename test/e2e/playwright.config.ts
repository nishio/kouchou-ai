import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 30 * 1000,
  expect: {
    timeout: 5000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ["html", { outputFolder: "playwright-report" }],
    ["json", { outputFile: "playwright-report/results.json" }],
    ["list"],
  ],
  use: {
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "verify",
      testMatch: "**/verify-*.spec.ts",
      use: {
        ...devices["Desktop Chrome"],
      },
    },
    {
      name: "admin",
      testMatch: "**/admin/**/*.spec.ts",
      use: {
        ...devices["Desktop Chrome"],
        baseURL: "http://localhost:4000",
      },
    },
    {
      name: "client",
      testMatch: "**/client/**/*.spec.ts",
      use: {
        ...devices["Desktop Chrome"],
        baseURL: "http://localhost:3000",
      },
    },
    {
      name: "debug",
      testMatch: ["**/simple.spec.ts", "**/debug.spec.ts"],
      use: {
        ...devices["Desktop Chrome"],
      },
    },
  ],
  webServer: [
    // Clientテスト用: ダミーAPIサーバーを起動（テストフィクスチャを返す）
    {
      command: "cd ../../utils/dummy-server && PUBLIC_API_KEY=public E2E_TEST=true npm run dev -- --port 8002",
      port: 8002,
      timeout: 120 * 1000,
      reuseExistingServer: !process.env.CI,
      env: {
        E2E_TEST: "true",
        PUBLIC_API_KEY: "public",
      },
    },
    // Clientテスト用: フロントエンドサーバーを起動（ダミーAPIサーバーを参照）
    {
      command: "cd ../../client && NEXT_PUBLIC_API_BASEPATH=http://localhost:8002 API_BASEPATH=http://localhost:8002 npm run dev -- --port 3000",
      port: 3000,
      timeout: 120 * 1000,
      reuseExistingServer: !process.env.CI,
      env: {
        NEXT_PUBLIC_API_BASEPATH: "http://localhost:8002",
        API_BASEPATH: "http://localhost:8002",
        NEXT_PUBLIC_PUBLIC_API_KEY: "public",
      },
    },
  ],
  // Admin tests: cd ../../client-admin && npm run dev (手動起動が必要)
});
