"""
CSVファイル解析のテストスクリプト

このスクリプトは、様々な形式のCSVファイルを読み込み、
コメント数と平均コメント長を正確に計算できるかテストします。
"""

import csv
from pathlib import Path

def test_csv_file(file_path):
    """
    CSVファイルを読み込み、コメント数と平均コメント長を計算する
    
    Args:
        file_path: CSVファイルのパス
    """
    print(f"\n=== ファイル: {file_path.name} ===")
    
    comments = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            print(f"最初の行: {first_line}")
            
            f.seek(0)
            
            reader = csv.reader(f, quotechar='"', doublequote=True, 
                               skipinitialspace=True)
            headers = next(reader, None)  # ヘッダー行を取得
            
            if headers:
                print(f"ヘッダー: {headers}")
                
                comment_col_idx = 0  # デフォルトは最初の列
                for i, header in enumerate(headers):
                    if header and header.lower() in ['comment-body', 'comment', 'body', 'text', 'コメント']:
                        comment_col_idx = i
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
        except Exception as e:
            print(f"単一列形式での読み込みエラー: {e}")
    
    if not comments:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                
                for line in f:
                    line = line.strip()
                    if line:
                        comments.append(line)
        except Exception as e:
            print(f"非CSV形式での読み込みエラー: {e}")
    
    comment_count = len(comments)
    
    if comment_count > 0:
        total_chars = sum(len(comment) for comment in comments)
        avg_length = total_chars / comment_count
        
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
    else:
        print("コメントが見つかりませんでした")

def main():
    """メイン関数"""
    test_files = [
        Path("/home/ubuntu/repos/kouchou-ai/client-admin/public/sample_comments.csv"),
        Path("/home/ubuntu/repos/kouchou-ai/server/broadlistening/pipeline/inputs/example-polis.csv"),
        Path("/home/ubuntu/repos/kouchou-ai/server/broadlistening/pipeline/inputs/dummy-comments-japan.csv")
    ]
    
    for file_path in test_files:
        if file_path.exists():
            test_csv_file(file_path)
        else:
            print(f"\n=== ファイル: {file_path.name} ===")
            print(f"ファイルが見つかりません: {file_path}")

if __name__ == "__main__":
    main()
