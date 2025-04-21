"""
36.0文字問題のデバッグスクリプト

このスクリプトは、平均コメント長が36.0文字と誤って計算される
特定のケースを特定するためのものです。
"""

import csv
import os
from pathlib import Path
import sys

def test_csv_file(file_path, debug=True):
    """
    CSVファイルを読み込み、コメント数と平均コメント長を計算する
    
    Args:
        file_path: CSVファイルのパス
        debug: デバッグ情報を表示するかどうか
    
    Returns:
        dict: コメント数と平均コメント長を含む辞書
    """
    if debug:
        print(f"\n=== ファイル: {file_path.name} ===")
    
    if not file_path.exists() or file_path.stat().st_size == 0:
        if debug:
            print(f"ファイルが存在しないか空です: {file_path}")
        return {"comment_count": 0, "avg_comment_length": 0}
    
    comments = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if debug:
                first_line = f.readline().strip()
                print(f"最初の行: {first_line}")
                f.seek(0)
            
            reader = csv.reader(f, quotechar='"', doublequote=True, 
                               skipinitialspace=True)
            headers = next(reader, None)  # ヘッダー行を取得
            
            if headers:
                if debug:
                    print(f"ヘッダー: {headers}")
                
                comment_col_idx = 0  # デフォルトは最初の列
                for i, header in enumerate(headers):
                    if header and header.lower() in ['comment-body', 'comment', 'body', 'text', 'コメント']:
                        comment_col_idx = i
                        if debug:
                            print(f"コメント列を特定: '{header}' (インデックス {i})")
                        break
                
                for row in reader:
                    if row and len(row) > comment_col_idx:
                        comment = row[comment_col_idx].strip()
                        if comment:  # 空のコメントは除外
                            if comment.startswith('"') and comment.endswith('"'):
                                comment = comment[1:-1]
                            comments.append(comment)
    except Exception as e:
        if debug:
            print(f"標準CSV形式での読み込みエラー: {e}")
    
    if not comments:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                is_header = first_line.lower() in ['comment', 'コメント']
                
                f.seek(0)
                
                if is_header:
                    next(f)
                
                for line in f:
                    line = line.strip()
                    if line:
                        if line.startswith('"') and line.endswith('"'):
                            line = line[1:-1]
                        if line:  # 空でない場合のみ追加
                            comments.append(line)
            if debug and comments:
                print(f"単一列形式で {len(comments)} 件のコメントを読み込みました")
        except Exception as e:
            if debug:
                print(f"単一列形式での読み込みエラー: {e}")
    
    if not comments:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                
                for line in f:
                    line = line.strip()
                    if line:
                        comments.append(line)
            if debug and comments:
                print(f"非CSV形式で {len(comments)} 件のコメントを読み込みました")
        except Exception as e:
            if debug:
                print(f"非CSV形式での読み込みエラー: {e}")
    
    if not comments:
        try:
            with open(file_path, 'rb') as f:
                content = f.read(100)  # 最初の100バイトだけ読む
                if debug:
                    print(f"バイナリ内容の先頭: {content}")
                
                file_size = file_path.stat().st_size
                if file_size == 36:
                    if debug:
                        print(f"*** 特定のケースを検出: ファイルサイズが36バイト ***")
                    return {"comment_count": 1, "avg_comment_length": 36.0}
        except Exception as e:
            if debug:
                print(f"バイナリ読み込みエラー: {e}")
    
    comment_count = len(comments)
    
    if comment_count > 0:
        total_chars = sum(len(comment) for comment in comments)
        avg_length = total_chars / comment_count
        
        if debug:
            print(f"コメント数: {comment_count}")
            print(f"合計文字数: {total_chars}")
            print(f"平均長: {avg_length:.1f} 文字")
            
            if comments:
                print(f"最初のコメント例: '{comments[0][:50]}...' (長さ: {len(comments[0])}文字)")
                print(f"最後のコメント例: '{comments[-1][:50]}...' (長さ: {len(comments[-1])}文字)")
                
                lengths = [len(c) for c in comments]
                print(f"最短コメント: {min(lengths)} 文字")
                print(f"最長コメント: {max(lengths)} 文字")
                
                count_36 = sum(1 for l in lengths if l == 36)
                if count_36 > 0:
                    print(f"36文字のコメント数: {count_36}")
                    print("36文字のコメント例:")
                    for i, c in enumerate(comments):
                        if len(c) == 36:
                            print(f"  - '{c}'")
                            if i >= 2:  # 最大3つまで表示
                                break
                
                if 35.9 <= avg_length <= 36.1:
                    print("*** 平均長が36.0文字に近い値です ***")
        
        return {
            "comment_count": comment_count,
            "avg_comment_length": avg_length
        }
    else:
        if debug:
            print("コメントが見つかりませんでした")
        return {"comment_count": 0, "avg_comment_length": 0}

def scan_directory(directory_path):
    """
    指定されたディレクトリ内のCSVファイルをスキャンし、
    平均コメント長が36.0文字に近いファイルを特定する
    
    Args:
        directory_path: スキャンするディレクトリのパス
    """
    print(f"\n=== ディレクトリのスキャン: {directory_path} ===")
    
    csv_files = list(directory_path.glob("**/*.csv"))
    print(f"{len(csv_files)}件のCSVファイルが見つかりました")
    
    suspicious_files = []
    
    for file_path in csv_files:
        result = test_csv_file(file_path, debug=False)
        avg_length = result["avg_comment_length"]
        
        if 35.9 <= avg_length <= 36.1:
            suspicious_files.append((file_path, result))
            print(f"平均長が36.0に近いファイル: {file_path} (平均: {avg_length:.1f}文字)")
    
    empty_files = []
    for file_path in csv_files:
        if file_path.stat().st_size == 0:
            empty_files.append(file_path)
    
    if empty_files:
        print(f"\n{len(empty_files)}件の空のCSVファイルが見つかりました:")
        for file_path in empty_files:
            print(f"  - {file_path}")
    
    size_36_files = []
    for file_path in directory_path.glob("**/*"):
        if file_path.is_file() and file_path.stat().st_size == 36:
            size_36_files.append(file_path)
    
    if size_36_files:
        print(f"\n{len(size_36_files)}件のファイルサイズが36バイトのファイルが見つかりました:")
        for file_path in size_36_files:
            print(f"  - {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"    内容: '{content}'")
            except:
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        print(f"    バイナリ内容: {content}")
                except Exception as e:
                    print(f"    読み込みエラー: {e}")
    
    return suspicious_files

def main():
    """メイン関数"""
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        if file_path.exists():
            test_csv_file(file_path)
        else:
            print(f"ファイルが見つかりません: {file_path}")
    else:
        repo_root = Path(__file__).parent.parent
        
        sample_file = repo_root / "client-admin/public/sample_comments.csv"
        if sample_file.exists():
            test_csv_file(sample_file)
        
        directories = [
            repo_root / "server/broadlistening/pipeline/inputs",
            repo_root / "server/broadlistening/pipeline/outputs",
            repo_root / "client-admin/public"
        ]
        
        for directory in directories:
            if directory.exists():
                scan_directory(directory)
            else:
                print(f"ディレクトリが見つかりません: {directory}")

if __name__ == "__main__":
    main()
