# utils/dummy-server
これはダミーサーバーです  
フロントエンドの開発時にのみ利用してください

## Environment variables
- `PUBLIC_API_KEY`
  - public-viewer からのリクエストを受け付けるためのAPIキー
  - /reports および /reports/:slug へアクセスする際に必要
  - (/ や /meta/** へのアクセスには不要)
- `ADMIN_API_KEY`
  - admin からのリクエストを受け付けるためのAPIキー
  - /admin/reports へアクセスする際に必要

## endpoints
- GET /
  - (ヘルスチェック用)
- GET /meta/metadata.json
  - レポート発行者情報
- GET /meta/reporter.png
  - レポート発行者画像
- GET /meta/icon.png
  - レポートアイコン
- GET /meta/ogp.png
  - OGP画像(1200x630推奨)
- GET /reports
  - レポート一覧
- GET /reports/:slug
  - レポート本体
- GET /admin/reports
  - レポート一覧(公開前含む)
- POST /admin/reports
  - レポート作成（202 を返す。`E2E_TEST=true` のときは受け取った本文をレポート ID ごとに控える）
- POST /admin/spreadsheet/import
  - スプレッドシートの取り込み（外部には取りに行かず、取り込んだことにする）
- GET /admin/spreadsheet/data/:fileName
  - 取り込んだスプレッドシートのデータ（固定の 3 件）
- DELETE /admin/inputs/:fileName
  - 取り込んだデータの削除
- GET /e2e/created-reports/:slug
  - E2E 用。POST /admin/reports で受け取った本文を読み戻す（`E2E_TEST=true` のときだけ）

## metadata
- reporter: string
  - レポート作成者名
- message: string
  - レポート作成者からのメッセージ
- webLink?: string
  - レポート作成者URL
- privacyLink?: string
  - プライバシーポリシーURL
- termsLink?: string
  - 利用規約URL
- brandColor?: string
  - ブランドカラー
