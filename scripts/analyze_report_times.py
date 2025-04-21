"""
レポート生成パイプラインの実行時間分析スクリプト

このスクリプトは完了したレポートの hierarchical_status.json ファイルを読み込み、
各ステップの実行時間データを抽出します。入力データ量（コメント数と平均コメント長）と
実行時間の関係を分析し、将来のレポート生成時間を予測するための基礎情報を提供します。
"""

import json
import pandas as pd
from pathlib import Path
import csv
from typing import Dict, Any

REPORT_DIR = Path(__file__).parent.parent / "server/broadlistening/pipeline/outputs"
INPUT_DIR = Path(__file__).parent.parent / "server/broadlistening/pipeline/inputs"

def analyze_comments_in_report(report_dir: Path) -> Dict[str, float]:
    """
    コメント数と平均コメント長を計算する
    
    Args:
        report_dir: レポートディレクトリのパス
        
    Returns:
        dict: コメント数と平均コメント長を含む辞書
    """
    report_slug = report_dir.name
    
    input_file = None
    potential_input = INPUT_DIR / f"{report_slug}.csv"
    
    if potential_input.exists():
        input_file = potential_input
    else:
        for file in report_dir.glob("*.csv"):
            if "input" in file.name.lower() or "comments" in file.name.lower():
                input_file = file
                break
    
    if input_file is None:
        print(f"レポート {report_slug} の入力ファイルが見つかりませんでした")
        return {"comment_count": 0, "avg_comment_length": 0}
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # ヘッダーをスキップ
            
            comments = [row[0] for row in reader if row and len(row) > 0]
            comment_count = len(comments)
            
            avg_length = sum(len(comment) for comment in comments) / comment_count if comment_count > 0 else 0
                
            return {
                "comment_count": comment_count,
                "avg_comment_length": avg_length
            }
    except Exception as e:
        print(f"レポート {report_slug} の入力ファイル読み込みエラー: {e}")
        return {"comment_count": 0, "avg_comment_length": 0}

def get_report_metadata(report_dir: Path) -> Dict[str, Any]:
    """
    レポートのメタデータを取得する
    
    Args:
        report_dir: レポートディレクトリのパス
        
    Returns:
        dict: スラグ、タイトル、作成時間を含むメタデータ
    """
    status_file = report_dir / "hierarchical_status.json"
    if not status_file.exists():
        return {}
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        return {
            "slug": report_dir.name,
            "title": status.get("question", "不明"),
            "created_at": status.get("start_time", "不明"),
            "status": status.get("status", "不明")
        }
    except Exception as e:
        print(f"レポート {report_dir.name} のステータスファイル読み込みエラー: {e}")
        return {}

def get_step_durations(report_dir: Path) -> Dict[str, float]:
    """
    各ステップの実行時間を取得する
    
    Args:
        report_dir: レポートディレクトリのパス
        
    Returns:
        dict: ステップ名と実行時間（秒）のマッピング
    """
    status_file = report_dir / "hierarchical_status.json"
    if not status_file.exists():
        return {}
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        durations = {}
        for job in status.get("completed_jobs", []):
            step = job.get("step")
            duration = job.get("duration")
            if step and duration is not None:
                durations[step] = duration
        
        return durations
    except Exception as e:
        print(f"レポート {report_dir.name} のステータスファイル読み込みエラー: {e}")
        return {}

def analyze_reports() -> pd.DataFrame:
    """
    すべてのレポートを分析し、時間データを収集する
    
    Returns:
        pd.DataFrame: レポートの時間データを含むDataFrame
    """
    report_data = []
    
    report_dirs = [d for d in REPORT_DIR.iterdir() if d.is_dir()]
    
    for report_dir in report_dirs:
        status_file = report_dir / "hierarchical_status.json"
        if not status_file.exists():
            continue
        
        metadata = get_report_metadata(report_dir)
        if not metadata or metadata.get("status") != "completed":
            continue
        
        comment_info = analyze_comments_in_report(report_dir)
        
        durations = get_step_durations(report_dir)
        if not durations:
            continue
        
        report_data.append({
            "slug": metadata.get("slug", "不明"),
            "title": metadata.get("title", "不明"),
            "created_at": metadata.get("created_at", "不明"),
            "comment_count": comment_info["comment_count"],
            "avg_comment_length": comment_info["avg_comment_length"],
            **durations
        })
    
    return pd.DataFrame(report_data) if report_data else pd.DataFrame()

def format_time(seconds: float) -> str:
    """
    秒を読みやすい時間形式に変換する
    
    Args:
        seconds: 秒数
        
    Returns:
        str: フォーマットされた時間文字列（例: "2分30秒"）
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}時間{minutes}分{seconds}秒"
    elif minutes > 0:
        return f"{minutes}分{seconds}秒"
    else:
        return f"{seconds}秒"

def display_report_data(df: pd.DataFrame) -> None:
    """
    レポートデータを表示する
    
    Args:
        df: レポートデータを含むDataFrame
    """
    avg_comment_count = df["comment_count"].mean()
    avg_comment_length = df["avg_comment_length"].mean()
    
    print(f"\n=== 全体の平均値 ===")
    print(f"平均コメント数: {avg_comment_count:.1f}")
    print(f"平均コメント長: {avg_comment_length:.1f} 文字")
    
    step_names = [col for col in df.columns if col not in ["slug", "title", "created_at", "comment_count", "avg_comment_length"]]
    
    print("\n=== 各ステップの平均実行時間 ===")
    total_avg_duration = 0
    for step in step_names:
        avg_duration = df[step].mean()
        total_avg_duration += avg_duration
        print(f"  - {step}: {format_time(avg_duration)}")
    
    print(f"\n合計平均実行時間: {format_time(total_avg_duration)}")

def display_individual_reports(df: pd.DataFrame) -> None:
    """
    個別レポートのデータを表示する
    
    Args:
        df: レポートデータを含むDataFrame
    """
    step_names = [col for col in df.columns if col not in ["slug", "title", "created_at", "comment_count", "avg_comment_length"]]
    
    print("\n=== 個別レポートデータ ===")
    for _, row in df.sort_values("comment_count").iterrows():
        print(f"\nレポート: {row['title']} ({row['slug']})")
        print(f"コメント: {row['comment_count']} (平均長: {row['avg_comment_length']:.1f} 文字)")
        
        # 各ステップの実行時間を表示
        report_total_duration = 0
        print("ステップ実行時間:")
        for step in step_names:
            duration = row[step]
            report_total_duration += duration
            print(f"  - {step}: {format_time(duration)}")
        
        print(f"合計実行時間: {format_time(report_total_duration)}")

def main():
    """メイン関数"""
    print("レポート実行時間データを分析しています...")
    
    df = analyze_reports()
    
    if df.empty:
        print("レポートデータが見つかりませんでした。")
        return
    
    print(f"{len(df)}件の完了したレポートが見つかりました。")
    
    display_report_data(df)
    
    display_individual_reports(df)
    
    output_file = Path(__file__).parent / "report_timing_analysis.csv"
    df.to_csv(output_file, index=False)
    print(f"\n詳細データを {output_file} に保存しました")
    
    print("\n分析完了!")

if __name__ == "__main__":
    main()
