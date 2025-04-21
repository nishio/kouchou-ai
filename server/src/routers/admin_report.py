import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.responses import FileResponse, ORJSONResponse
from fastapi.security.api_key import APIKeyHeader

from src.config import settings
from src.schemas.admin_report import Prompt, ReportInput
from src.schemas.report import Report, ReportStatus
from src.services.report_launcher import launch_report_generation
from src.services.report_status import (
    add_new_report_to_status,
    load_status_as_reports,
    set_status,
    toggle_report_public_state,
)
from src.utils.logger import setup_logger

slogger = setup_logger()
router = APIRouter()

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def verify_admin_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


@router.get("/admin/reports")
async def get_reports(api_key: str = Depends(verify_admin_api_key)) -> list[Report]:
    return load_status_as_reports()


@router.post("/admin/reports", status_code=202)
async def create_report(report: ReportInput, api_key: str = Depends(verify_admin_api_key)):
    try:
        launch_report_generation(report)
        return ORJSONResponse(
            content=None,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except ValueError as e:
        slogger.error(f"ValueError: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        slogger.error(f"Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/admin/comments/{slug}/csv")
async def download_comments_csv(slug: str, api_key: str = Depends(verify_admin_api_key)):
    csv_path = settings.REPORT_DIR / slug / "final_result_with_comments.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="CSV file not found")
    return FileResponse(path=str(csv_path), media_type="text/csv", filename=f"kouchou_{slug}.csv")


@router.get("/admin/reports/{slug}/status/step-json", dependencies=[Depends(verify_admin_api_key)])
async def get_current_step(slug: str):
    status_file = settings.REPORT_DIR / slug / "hierarchical_status.json"
    try:
        # ステータスファイルが存在しない場合は "loading" を返す
        if not status_file.exists():
            return {"current_step": "loading"}

        with open(status_file) as f:
            status = json.load(f)

        # error キーが存在する場合はエラーとみなす
        if "error" in status:
            return {"current_step": "error"}

        # 全体のステータスが "completed" なら、current_step も "completed" とする
        if status.get("status") == "completed":
            return {"current_step": "completed"}

        # current_job キーが存在しない場合も "loading" とみなす
        if "current_job" not in status:
            return {"current_step": "loading"}

        # current_job が空文字列の場合も "loading" とする
        if not status.get("current_job"):
            return {"current_step": "loading"}

        # 有効な current_job を返す
        return {"current_step": status.get("current_job", "unknown")}
    except Exception:
        return {"current_step": "error"}


@router.delete("/admin/reports/{slug}")
async def delete_report(slug: str, api_key: str = Depends(verify_admin_api_key)):
    try:
        set_status(slug, ReportStatus.DELETED.value)
        return ORJSONResponse(
            content={"message": f"Report {slug} marked as deleted"},
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except ValueError as e:
        slogger.error(f"ValueError: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        slogger.error(f"Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.patch("/admin/reports/{slug}/visibility")
async def update_report_visibility(slug: str, api_key: str = Depends(verify_admin_api_key)) -> dict:
    try:
        is_public = toggle_report_public_state(slug)

        return {"success": True, "isPublic": is_public}
    except ValueError as e:
        slogger.error(f"ValueError: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        slogger.error(f"Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/admin/reports/{slug}/duplicate")
async def duplicate_report(slug: str, api_key: str = Depends(verify_admin_api_key)) -> dict:
    """
    既存のレポートを複製して新しいレポートを作成するエンドポイント。
    設定ファイル（config）のみを複製し、中間結果は再利用しない。

    Args:
        slug: 複製元のレポートのスラッグ

    Returns:
        dict: 新しいレポートのスラッグを含む辞書
    """
    try:
        config_path = settings.CONFIG_DIR / f"{slug}.json"
        if not config_path.exists():
            raise ValueError(f"設定ファイルが見つかりません: {config_path}")

        with open(config_path) as f:
            config = json.load(f)

        new_slug = f"{slug}_copy_{uuid.uuid4().hex[:8]}"

        config["name"] = new_slug
        config["input"] = new_slug

        new_config_path = settings.CONFIG_DIR / f"{new_slug}.json"
        with open(new_config_path, "w") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        reports = load_status_as_reports(include_deleted=True)
        original_report = next((r for r in reports if r.slug == slug), None)
        
        if not original_report:
            raise ValueError(f"元のレポート情報が見つかりません: {slug}")

        
        report_input = ReportInput(
            input=new_slug,
            question=f"{original_report.title} (コピー)",
            intro=original_report.description,
            cluster=config.get("hierarchical_clustering", {}).get("cluster_nums", [5, 3]),
            model=config.get("model", "gpt-4"),
            workers=config.get("extraction", {}).get("workers", 5),
            prompt=Prompt(
                extraction=config.get("extraction", {}).get("prompt", ""),
                initial_labelling=config.get("hierarchical_initial_labelling", {}).get("prompt", ""),
                merge_labelling=config.get("hierarchical_merge_labelling", {}).get("prompt", ""),
                overview=config.get("hierarchical_overview", {}).get("prompt", ""),
            ),
            comments=[],  # 空のコメントリスト
            is_pubcom=original_report.is_pubcom,
        )
        
        add_new_report_to_status(report_input)
        set_status(new_slug, ReportStatus.READY.value)

        return {
            "success": True, 
            "slug": new_slug,
            "title": f"{original_report.title} (コピー)",
            "description": original_report.description
        }
    except ValueError as e:
        slogger.error(f"ValueError: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        slogger.error(f"Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e
