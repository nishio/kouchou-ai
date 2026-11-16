#!/usr/bin/env python3
"""Azure Blob Storage接続テストと確認方法

このスクリプトはAzure Blob Storageへの接続をテストし、ファイルのアップロードと
ダウンロードが正常に動作するか確認します。続けて、API の起動時に復元する
status/report_status.json を読み戻し、JSON として読めることを確認します
（新しい環境でまだ無い場合は警告だけで通します）。

Azure の deploy（.github/workflows/azure-deploy.yml）が、デプロイ前の health check として
実行します。どれかの確認に失敗したら終了コード 1 で終わり、デプロイを止めます。
STORAGE_TYPE が azure_blob でない場合も、Blob を確認したことにならないので 1 で終わります。

実行方法:
    cd apps/api && rye run python scripts/test_storage.py

出力例:
2025-09-25 12:31:44 [info     ] Logger setup complete          [app] json_logs=False log_file=stdout log_level=INFO
STORAGE_TYPE: azure_blob
AZURE_BLOB_STORAGE_ACCOUNT_NAME: <BLOB_STORAGE_NAME>
AZURE_BLOB_STORAGE_CONTAINER_NAME: kouchou-reports
Azure Blob Storage Account URL: https://<BLOB_STORAGE_NAME>.blob.core.windows.net
2025-09-25 12:31:44 [info     ] AzureBlobStorageServiceを使用します。アカウント: <BLOB_STORAGE_NAME> コンテナ: kouchou-reports [app]
Storage service initialized: AzureBlobStorageService
2025-09-25 12:31:46 [info     ] ファイルをアップロードしました。パス: 'test_upload.txt' パス: 'test/test_upload.txt' [app]
✅ Upload successful to: test/test_upload.txt
2025-09-25 12:31:47 [info     ] ファイルをダウンロードしました。パス: 'test/test_upload.txt' ローカルパス: 'test_download.txt' [app]
✅ Download and content verification successful: test/test_upload.txt

Azure Storage内のファイル確認方法:

1. Azure CLI を使用した確認:
   # 全ファイルのリスト表示
   az storage blob list --account-name <BLOB_STORAGE_NAME> --container-name kouchou-reports --output table

   # 特定レポートのファイル確認
   az storage blob list --account-name <BLOB_STORAGE_NAME> --container-name kouchou-reports \\
       --prefix "outputs/[REPORT-ID]" --output table

   # ファイルのダウンロード
   az storage blob download --account-name <BLOB_STORAGE_NAME> --container-name kouchou-reports \\
       --name "outputs/[REPORT-ID]/hierarchical_result.json" --file ./downloaded.json

2. Azure Storage Explorer での確認:
   - ストレージアカウント: <BLOB_STORAGE_NAME>
   - コンテナ: kouchou-reports
   - 表示設定: 「すべてのBlobと現在のバージョンがないBlob」を選択

   スクリーンショット: https://gyazo.com/81698c6fdf2532005c5b1cd5d9ac2298

   ファイル構造:
   kouchou-reports/
   ├── outputs/[REPORT-ID]/     # レポート出力ファイル
   │   ├── hierarchical_result.json
   │   ├── hierarchical_overview.txt
   │   └── その他の結果ファイル
   ├── configs/[REPORT-ID].json # パイプライン設定
   └── inputs/[REPORT-ID].csv   # 入力データ

3. Python での確認（このスクリプトの拡張例）:
   storage_service = get_storage_service()
   # AzureBlobStorageService の場合、container_client を使用してリスト取得可能

環境変数の確認:
   - STORAGE_TYPE=azure_blob
   - AZURE_BLOB_STORAGE_ACCOUNT_NAME=<BLOB_STORAGE_NAME>
   - AZURE_BLOB_STORAGE_CONTAINER_NAME=kouchou-reports

注意事項:
   - LocalStorageService（STORAGE_TYPE=local）では実際の外部ストレージ保存は行われません
   - Azure Container Apps上で実行された場合、ローカル環境にはファイルが存在しません
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

# apps/api フォルダから実行する場合のパス設定
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import settings
from src.services.storage import AzureBlobStorageService, get_storage_service

# API の起動時に initialize_from_storage() が復元するステータスファイル（ReportSyncService と同じ場所）
REMOTE_STATUS_FILE_PATH = "status/report_status.json"


def cleanup_local_files(*paths: str) -> None:
    """Remove temporary local files if they exist."""
    for path in paths:
        if os.path.exists(path):
            os.remove(path)


def cleanup_remote_file(storage_service, remote_path: str) -> None:
    """Remove the uploaded test blob when running against Azure Blob Storage."""
    if not isinstance(storage_service, AzureBlobStorageService):
        return
    try:
        storage_service.container_client.delete_blob(remote_path, delete_snapshots="include")
        print(f"🧹 Deleted remote test blob: {remote_path}")
    except Exception as e:
        print(f"⚠️ Failed to delete remote test blob: {remote_path} ({e})")


def check_write_and_read(storage_service, work_dir: Path) -> bool:
    """テスト用の blob を書いて読み戻し、内容が一致するか確かめる。"""
    probe_id = uuid4().hex
    test_file_path = str(work_dir / f"test_upload_{probe_id}.txt")
    downloaded_file_path = str(work_dir / f"test_download_{probe_id}.txt")
    remote_path = f"test/test_upload_{probe_id}.txt"
    test_content = "Test upload to Azure Blob Storage"

    try:
        Path(test_file_path).write_text(test_content, encoding="utf-8")
        if not storage_service.upload_file(test_file_path, remote_path):
            print("❌ Upload failed")
            return False
        print(f"✅ Upload successful to: {remote_path}")

        if not storage_service.download_file(remote_path, downloaded_file_path):
            print(f"❌ Download failed: {remote_path}")
            return False
        if Path(downloaded_file_path).read_text(encoding="utf-8") != test_content:
            print(f"❌ Downloaded content mismatch: {remote_path}")
            return False
        print(f"✅ Download and content verification successful: {remote_path}")
        return True
    finally:
        cleanup_local_files(test_file_path, downloaded_file_path)
        cleanup_remote_file(storage_service, remote_path)


def check_report_status_readback(storage_service, work_dir: Path) -> bool:
    """status/report_status.json を読み戻し、JSON のオブジェクトとして読めるか確かめる。

    まだ一度もレポートを作っていない新しい環境には無いので、無いときは警告だけで通す。
    中身（レポートの一覧）は表示しない。
    """
    blob_client = storage_service.container_client.get_blob_client(REMOTE_STATUS_FILE_PATH)
    if not blob_client.exists():
        print(f"⚠️ {REMOTE_STATUS_FILE_PATH} is not in the container yet (new environment?); skipping read-back")
        return True

    local_path = work_dir / "report_status.json"
    try:
        if not storage_service.download_file(REMOTE_STATUS_FILE_PATH, str(local_path)):
            print(f"❌ Read-back failed: {REMOTE_STATUS_FILE_PATH}")
            return False
        try:
            report_status = json.loads(local_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            print(f"❌ {REMOTE_STATUS_FILE_PATH} is not valid JSON: {e}")
            return False
        if not isinstance(report_status, dict):
            print(f"❌ {REMOTE_STATUS_FILE_PATH} is not a JSON object (got {type(report_status).__name__})")
            return False
        print(f"✅ Read-back successful: {REMOTE_STATUS_FILE_PATH} ({len(report_status)} reports)")
        return True
    finally:
        cleanup_local_files(str(local_path))


def main() -> int:
    print(f"STORAGE_TYPE: {settings.STORAGE_TYPE}")
    print(f"AZURE_BLOB_STORAGE_ACCOUNT_NAME: {settings.AZURE_BLOB_STORAGE_ACCOUNT_NAME}")
    print(f"AZURE_BLOB_STORAGE_CONTAINER_NAME: {settings.AZURE_BLOB_STORAGE_CONTAINER_NAME}")
    print(f"Azure Blob Storage Account URL: {settings.azure_blob_storage_account_url}")

    try:
        storage_service = get_storage_service()
        print(f"Storage service initialized: {storage_service.__class__.__name__}")
        # local のままだと upload / download は何もしないので、Blob を確かめたことにならない
        if not isinstance(storage_service, AzureBlobStorageService):
            print("❌ STORAGE_TYPE is not azure_blob; this health check only verifies Azure Blob Storage")
            return 1

        with tempfile.TemporaryDirectory() as work_dir:
            if not check_write_and_read(storage_service, Path(work_dir)):
                return 1
            if not check_report_status_readback(storage_service, Path(work_dir)):
                return 1
    except Exception as e:
        # 例外で抜けたときも失敗として終わる（以前は終了コード 0 で抜け、deploy が進んでいた）
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
