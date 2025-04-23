import json
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import settings
from src.schemas.admin_report import ReportInput
from src.services.report_status import add_new_report_to_status, set_status
from src.services.report_sync import ReportSyncService
from src.utils.logger import setup_logger

logger = setup_logger()

PIPELINE_STEPS = [
    "extraction",
    "embedding",
    "hierarchical_clustering",
    "hierarchical_initial_labelling",
    "hierarchical_merge_labelling",
    "hierarchical_overview",
    "hierarchical_aggregation",
    "hierarchical_visualization",
]

STEP_OUTPUT_FILES = {
    "extraction": ["extraction.json"],
    "embedding": ["embedding.json", "embedding.npy"],
    "hierarchical_clustering": ["hierarchical_clustering.json"],
    "hierarchical_initial_labelling": ["hierarchical_initial_labelling.json"],
    "hierarchical_merge_labelling": ["hierarchical_merge_labelling.json"],
    "hierarchical_overview": ["hierarchical_overview.json"],
    "hierarchical_aggregation": ["hierarchical_aggregation.json"],
    "hierarchical_visualization": ["hierarchical_visualization.json", "hierarchical_visualization.html"],
}


def _build_config(report_input: ReportInput) -> dict[str, Any]:
    comment_num = len(report_input.comments)

    config = {
        "name": report_input.input,
        "input": report_input.input,
        "question": report_input.question,
        "intro": report_input.intro,
        "model": report_input.model,
        "is_pubcom": report_input.is_pubcom,
        "extraction": {
            "prompt": report_input.prompt.extraction,
            "workers": report_input.workers,
            "limit": comment_num,
        },
        "hierarchical_clustering": {
            "cluster_nums": report_input.cluster,
        },
        "hierarchical_initial_labelling": {
            "prompt": report_input.prompt.initial_labelling,
            "sampling_num": 30,
            "workers": report_input.workers,
        },
        "hierarchical_merge_labelling": {
            "prompt": report_input.prompt.merge_labelling,
            "sampling_num": 30,
            "workers": report_input.workers,
        },
        "hierarchical_overview": {"prompt": report_input.prompt.overview},
        "hierarchical_aggregation": {
            "sampling_num": report_input.workers,
        },
    }

    if report_input.duplication_options and report_input.duplication_options.source_slug:
        config["source_slug"] = report_input.duplication_options.source_slug
        config["reuse_intermediate_results"] = report_input.duplication_options.reuse_intermediate_results

    return config


def save_config_file(report_input: ReportInput) -> Path:
    config = _build_config(report_input)
    config_path = settings.CONFIG_DIR / f"{report_input.input}.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    return config_path


def save_input_file(report_input: ReportInput) -> Path:
    """
    入力データをCSVファイルとして保存する

    Args:
        report_input: レポート生成の入力データ

    Returns:
        Path: 保存されたCSVファイルのパス
    """
    comments = [
        {
            "comment-id": comment.id,
            "comment-body": comment.comment,
            "source": comment.source,
            "url": comment.url,
        }
        for comment in report_input.comments
    ]
    input_path = settings.INPUT_DIR / f"{report_input.input}.csv"
    df = pd.DataFrame(comments)
    df.to_csv(input_path, index=False)
    return input_path


def copy_intermediate_results(source_slug: str, target_slug: str) -> None:
    """
    既存レポートの中間結果ファイルを新しいレポートディレクトリにコピーする

    Args:
        source_slug: コピー元のレポートスラッグ
        target_slug: コピー先のレポートスラッグ
    """
    source_dir = settings.REPORT_DIR / source_slug
    target_dir = settings.REPORT_DIR / target_slug

    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)

    for _step, files in STEP_OUTPUT_FILES.items():
        for file in files:
            source_file = source_dir / file
            if source_file.exists():
                target_file = target_dir / file
                logger.info(f"Copying {source_file} to {target_file}")
                shutil.copy2(source_file, target_file)

    source_status_file = source_dir / "hierarchical_status.json"
    if source_status_file.exists():
        target_status_file = target_dir / "hierarchical_status.json"

        # ステータスファイルの内容を読み込み、必要な情報を更新
        with open(source_status_file) as f:
            status_data = json.load(f)

        status_data["name"] = target_slug
        status_data["input"] = target_slug
        status_data["output_dir"] = target_slug
        status_data["status"] = "completed"  # 中間結果を再利用する場合は完了状態とする

        with open(target_status_file, "w") as f:
            json.dump(status_data, f, indent=4, ensure_ascii=False)

    logger.info(f"Intermediate results copied from {source_slug} to {target_slug}")


def _monitor_process(process: subprocess.Popen, slug: str) -> None:
    """
    サブプロセスの実行を監視し、完了時にステータスを更新する

    Args:
        process: 監視対象のサブプロセス
        slug: レポートのスラッグ
    """
    retcode = process.wait()
    if retcode == 0:
        # レポート生成成功時、ステータスを更新
        set_status(slug, "ready")

        logger.info(f"Syncing files for {slug} to storage")
        report_sync_service = ReportSyncService()
        # レポートファイルをストレージに同期し、JSONファイル以外を削除
        report_sync_service.sync_report_files_to_storage(slug)
        # 入力ファイルをストレージに同期し、ローカルファイルを削除
        report_sync_service.sync_input_file_to_storage(slug)
        # 設定ファイルをストレージに同期
        report_sync_service.sync_config_file_to_storage(slug)
        # ステータスファイルをストレージに同期
        report_sync_service.sync_status_file_to_storage()

    else:
        set_status(slug, "error")


def launch_report_generation(report_input: ReportInput) -> None:
    """
    外部ツールの main.py を subprocess で呼び出してレポート生成処理を開始する関数。
    中間結果の再利用オプションがある場合は、既存レポートの中間結果をコピーする。
    """
    try:
        add_new_report_to_status(report_input)
        config_path = save_config_file(report_input)

        if (
            report_input.duplication_options
            and report_input.duplication_options.reuse_intermediate_results
            and report_input.duplication_options.source_slug
        ):
            source_slug = report_input.duplication_options.source_slug
            target_slug = report_input.input
            
            source_input_path = settings.INPUT_DIR / f"{source_slug}.csv"
            target_input_path = settings.INPUT_DIR / f"{target_slug}.csv"
            if source_input_path.exists():
                shutil.copy2(source_input_path, target_input_path)
                logger.info(f"Copied input file from {source_input_path} to {target_input_path}")
            else:
                save_input_file(report_input)
                logger.warning(f"Source input file {source_input_path} not found, creating new input file")

            copy_intermediate_results(source_slug, target_slug)

            set_status(target_slug, "ready")

            logger.info(f"Syncing files for {target_slug} to storage")
            report_sync_service = ReportSyncService()
            report_sync_service.sync_report_files_to_storage(target_slug)
            report_sync_service.sync_input_file_to_storage(target_slug)
            report_sync_service.sync_config_file_to_storage(target_slug)
            report_sync_service.sync_status_file_to_storage()

        else:
            save_input_file(report_input)
            cmd = ["python", "hierarchical_main.py", config_path, "--skip-interaction", "--without-html"]
            execution_dir = settings.TOOL_DIR / "pipeline"
            process = subprocess.Popen(cmd, cwd=execution_dir)
            threading.Thread(target=_monitor_process, args=(process, report_input.input), daemon=True).start()

    except Exception as e:
        set_status(report_input.input, "error")
        logger.error(f"Error launching report generation: {e}")
        raise e
