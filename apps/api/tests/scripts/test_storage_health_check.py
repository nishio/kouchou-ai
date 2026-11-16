"""scripts/test_storage.py（Azure deploy 前の Blob Storage health check）のテスト（#973）。

以前は例外で抜けても終了コード 0 で終わり、STORAGE_TYPE が local（upload / download が何もしない）
でも deploy が進んでいた。Blob への読み書きと status/report_status.json の読み戻しを確かめ、
どれかに失敗したら 1 で終わることを、Azure に接続しない偽の storage で確かめる。
"""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from src.services.storage import AzureBlobStorageService, LocalStorageService

API_DIR = Path(__file__).resolve().parents[2]
SCRIPT = API_DIR / "scripts" / "test_storage.py"


def _load():
    spec = importlib.util.spec_from_file_location("storage_health_check", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


health = _load()


class _FakeBlobClient:
    def __init__(self, blobs, path):
        self.blobs = blobs
        self.path = path

    def exists(self):
        return self.path in self.blobs


class _FakeContainerClient:
    def __init__(self, blobs):
        self.blobs = blobs
        self.deleted = []

    def get_blob_client(self, path):
        return _FakeBlobClient(self.blobs, path)

    def delete_blob(self, path, delete_snapshots=None):
        self.deleted.append(path)
        self.blobs.pop(path, None)


class FakeAzureStorage(AzureBlobStorageService):
    """Azure に接続しない AzureBlobStorageService。blob はメモリの dict に持つ。"""

    def __init__(self, blobs=None, fail_download=False, corrupt_download=False):
        self.blobs = dict(blobs or {})
        self.container_client = _FakeContainerClient(self.blobs)
        self.fail_download = fail_download
        self.corrupt_download = corrupt_download

    def upload_file(self, local_path, remote_path):
        self.blobs[remote_path] = Path(local_path).read_bytes()
        return True

    def download_file(self, remote_blob_path, local_file_path):
        if self.fail_download or remote_blob_path not in self.blobs:
            return False
        data = b"corrupted" if self.corrupt_download else self.blobs[remote_blob_path]
        Path(local_file_path).write_bytes(data)
        return True


def _status(value) -> dict:
    return {health.REMOTE_STATUS_FILE_PATH: json.dumps(value).encode("utf-8")}


@pytest.fixture
def run_with(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    def run(storage):
        monkeypatch.setattr(health, "get_storage_service", lambda: storage)
        return health.main()

    return run


def test_healthy_storage_with_report_status_passes(run_with, capsys, tmp_path):
    storage = FakeAzureStorage(_status({"report-a": {"status": "ready"}, "report-b": {"status": "error"}}))

    assert run_with(storage) == 0

    out = capsys.readouterr().out
    assert "Read-back successful: status/report_status.json (2 reports)" in out
    # レポートの中身（slug など）は表示しない
    assert "report-a" not in out
    # テスト用の blob は消し、ステータスファイルは残す。カレントディレクトリに一時ファイルを残さない
    assert [p for p in storage.blobs if p.startswith("test/")] == []
    assert health.REMOTE_STATUS_FILE_PATH in storage.blobs
    assert list(tmp_path.iterdir()) == []


def test_missing_report_status_is_a_warning_on_a_new_environment(run_with, capsys):
    assert run_with(FakeAzureStorage()) == 0
    assert "skipping read-back" in capsys.readouterr().out


@pytest.mark.parametrize(
    "blobs",
    [
        pytest.param({health.REMOTE_STATUS_FILE_PATH: b"{not json"}, id="invalid-json"),
        pytest.param(_status(["report-a"]), id="not-an-object"),
        pytest.param({health.REMOTE_STATUS_FILE_PATH: b"\xff\xfe\x00"}, id="not-utf8"),
    ],
)
def test_unreadable_report_status_fails(run_with, blobs):
    assert run_with(FakeAzureStorage(blobs)) == 1


def test_download_failure_fails(run_with):
    assert run_with(FakeAzureStorage(_status({}), fail_download=True)) == 1


def test_content_mismatch_fails_and_cleans_up(run_with):
    storage = FakeAzureStorage(_status({}), corrupt_download=True)
    assert run_with(storage) == 1
    assert [p for p in storage.blobs if p.startswith("test/")] == []


def test_local_storage_is_not_a_blob_health_check(run_with, capsys):
    """local の upload / download は何もしないので、通したら何も確かめずに deploy が進む"""
    assert run_with(LocalStorageService()) == 1
    assert "STORAGE_TYPE is not azure_blob" in capsys.readouterr().out


def test_exception_fails(run_with, monkeypatch):
    def broken():
        raise RuntimeError("DefaultAzureCredential failed to retrieve a token")

    monkeypatch.setattr(health, "get_storage_service", broken)
    assert health.main() == 1


def test_script_exit_code_is_nonzero_when_storage_is_local(tmp_path):
    """deploy の step はスクリプトの終了コードで止まるので、プロセスとして 1 で終わることを確かめる"""
    env = {
        **os.environ,
        "STORAGE_TYPE": "local",
        "ENV_FILE": str(tmp_path / "no.env"),
        "ADMIN_API_KEY": "dummy",
        "PUBLIC_API_KEY": "dummy",
        "OPENAI_API_KEY": "dummy",
    }
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=API_DIR, env=env, capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "STORAGE_TYPE is not azure_blob" in result.stdout
