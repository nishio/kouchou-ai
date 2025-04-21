"""
36.0文字問題の検証スクリプト

このスクリプトは、36.0文字問題を再現し、修正が正しく機能するかを検証します。
"""

import os
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from analyze_report_times import analyze_comments_in_report

def create_test_files():
    """テスト用のファイルを作成する"""
    test_dir = Path(__file__).parent / "test_files"
    test_dir.mkdir(exist_ok=True)
    
    file_36bytes = test_dir / "file_36bytes.csv"
    with open(file_36bytes, 'w', encoding='utf-8') as f:
        f.write("A" * 36)  # 36バイトのファイル
    
    file_36chars = test_dir / "file_36chars.csv"
    with open(file_36chars, 'w', encoding='utf-8') as f:
        f.write("comment\n")
        f.write('"' + "B" * 36 + '"')  # 36文字のコメント
    
    file_normal = test_dir / "file_normal.csv"
    with open(file_normal, 'w', encoding='utf-8') as f:
        f.write("comment\n")
        f.write('"コメント1"\n')
        f.write('"コメント2"\n')
        f.write('"コメント3"')
    
    return test_dir

def test_analyze_comments():
    """コメント分析関数をテストする"""
    test_dir = create_test_files()
    
    print("=== 36.0文字問題の検証 ===\n")
    
    file_36bytes = test_dir / "file_36bytes.csv"
    print(f"ケース1: 36バイトのファイル ({file_36bytes})")
    print(f"ファイルサイズ: {file_36bytes.stat().st_size} バイト")
    result = analyze_comments_in_report(file_36bytes.parent)
    print(f"結果: コメント数={result['comment_count']}, 平均長={result['avg_comment_length']}")
    print()
    
    file_36chars = test_dir / "file_36chars.csv"
    print(f"ケース2: 36文字の単一コメント ({file_36chars})")
    print(f"ファイルサイズ: {file_36chars.stat().st_size} バイト")
    result = analyze_comments_in_report(file_36chars.parent)
    print(f"結果: コメント数={result['comment_count']}, 平均長={result['avg_comment_length']}")
    print()
    
    file_normal = test_dir / "file_normal.csv"
    print(f"ケース3: 通常のCSVファイル ({file_normal})")
    print(f"ファイルサイズ: {file_normal.stat().st_size} バイト")
    result = analyze_comments_in_report(file_normal.parent)
    print(f"結果: コメント数={result['comment_count']}, 平均長={result['avg_comment_length']}")
    
    for file in test_dir.glob("*.csv"):
        file.unlink()
    test_dir.rmdir()

if __name__ == "__main__":
    test_analyze_comments()
