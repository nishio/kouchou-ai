"""Azure の接続できない・見つからない（404）失敗に、確かめる設定の案内を付ける（#592）。

自治体のセットアップで、AZURE_CHATCOMPLETION_VERSION に API バージョンではなくモデルのバージョンを
書いてしまい、404 の原因の特定に時間が掛かった。例外の型は変えずに（送り直しと失敗の分類が型を見る）、
分析ログと、抽出を中断するときのエラー文に案内を出す。外部には接続せず、httpx.MockTransport で応答する。
"""

import importlib
import logging

try:  # openai 2.x までは httpx を使う
    import httpx
except ModuleNotFoundError:  # 新しめの openai は httpx2 を同梱する
    import httpx2 as httpx

import openai
import pytest
from openai import AzureOpenAI

from analysis_core.services import llm

extraction = importlib.import_module("analysis_core.steps.extraction")

MESSAGES = [{"role": "user", "content": "hello"}]


@pytest.fixture
def azure(monkeypatch):
    """AzureOpenAI の通信先を差し替え、handler の応答（または例外）を返す"""
    state = {"handler": None}

    def make_client(**kwargs):
        kwargs.pop("http_client", None)
        transport = httpx.MockTransport(lambda request: state["handler"](request))
        return AzureOpenAI(**kwargs, http_client=httpx.Client(transport=transport), max_retries=0)

    monkeypatch.setattr(llm, "AzureOpenAI", make_client)
    monkeypatch.setenv("AZURE_CHATCOMPLETION_ENDPOINT", "https://example.invalid")
    monkeypatch.setenv("AZURE_CHATCOMPLETION_API_KEY", "dummy-secret-key-592")
    # API バージョンの欄にモデルのバージョンを書いてしまった設定
    monkeypatch.setenv("AZURE_CHATCOMPLETION_VERSION", "2024-08-06")
    monkeypatch.setenv("AZURE_CHATCOMPLETION_DEPLOYMENT_NAME", "kouchou-chat")
    return state


def _not_found(request):
    return httpx.Response(404, json={"error": {"code": "404", "message": "Resource not found"}})


def _connection_refused(request):
    raise httpx.ConnectError("connection refused", request=request)


def _timeout(request):
    raise httpx.ReadTimeout("timed out", request=request)


@pytest.mark.parametrize(
    ("handler", "error_type"),
    [
        pytest.param(_not_found, openai.NotFoundError, id="404"),
        pytest.param(_connection_refused, openai.APIConnectionError, id="connection"),
    ],
)
def test_azure_not_found_or_connection_error_logs_settings_to_check(azure, caplog, handler, error_type):
    azure["handler"] = handler
    with caplog.at_level(logging.ERROR), pytest.raises(error_type):
        llm.request_to_azure_chatcompletion(MESSAGES)

    assert "AZURE_CHATCOMPLETION_VERSION にはモデルのバージョンではなく API バージョン" in caplog.text
    assert "今の値: 2024-08-06" in caplog.text
    assert "kouchou-chat" in caplog.text
    assert "dummy-secret-key-592" not in caplog.text


def test_azure_timeout_is_not_blamed_on_settings(azure, caplog):
    """タイムアウトは APIConnectionError の子だが、設定の誤りではないので案内を出さない"""
    azure["handler"] = _timeout
    with caplog.at_level(logging.ERROR), pytest.raises(openai.APITimeoutError):
        llm.request_to_azure_chatcompletion(MESSAGES)

    assert "AZURE_CHATCOMPLETION_VERSION" not in caplog.text


@pytest.mark.parametrize("failure", ["NotFoundError", "APIConnectionError"])
def test_extraction_error_on_azure_explains_settings_to_check(failure):
    message = str(extraction.ExtractionBatchError({0: failure}, ["c1"], provider="azure"))
    assert "AZURE_CHATCOMPLETION_VERSION にはモデルのバージョン（例: 2024-08-06）ではなく API バージョン" in message
    assert "AZURE_CHATCOMPLETION_ENDPOINT" in message
    assert "c1" in message


@pytest.mark.parametrize(
    ("failures", "provider"),
    [
        pytest.param({0: "NotFoundError"}, "openai", id="openai-404"),
        pytest.param({0: "NotFoundError"}, None, id="unknown-provider"),
        pytest.param({0: "AuthenticationError"}, "azure", id="azure-auth"),
    ],
)
def test_settings_hint_only_for_azure_connection_and_not_found(failures, provider):
    message = str(extraction.ExtractionBatchError(failures, ["c1"], provider=provider))
    assert "AZURE_CHATCOMPLETION_VERSION" not in message


def test_extract_batch_passes_provider_to_the_error(monkeypatch):
    def extract(text, *args):
        raise openai.NotFoundError(
            "Resource not found",
            response=httpx.Response(404, request=httpx.Request("POST", "https://example.invalid")),
            body=None,
        )

    monkeypatch.setattr(extraction, "extract_arguments", extract)
    with pytest.raises(extraction.ExtractionBatchError, match="AZURE_CHATCOMPLETION_VERSION"):
        extraction.extract_batch(["x"], "p", "m", 1, provider="azure", comment_ids=["c1"])
