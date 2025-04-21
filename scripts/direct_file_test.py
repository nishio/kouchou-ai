"""
36.0文字問題の直接ファイルテスト

このスクリプトは、ファイルを直接分析して36.0文字問題を検証します。
"""

import csv
from pathlib import Path

def analyze_file_directly(file_path):
    """ファイルを直接分析する"""
    print(f"\n=== ファイル: {file_path.name} ===")
    
    if not file_path.exists() or file_path.stat().st_size == 0:
        print(f"ファイルが存在しないか空です: {file_path}")
        return {"comment_count": 0, "avg_comment_length": 0}
    
    if file_path.stat().st_size == 36:
        print(f"特殊ケース検出: ファイルサイズが36バイト")
        return {"comment_count": 0, "avg_comment_length": 0}
    
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
            if comments:
                print(f"単一列形式で {len(comments)} 件のコメントを読み込みました")
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
            if comments:
                print(f"非CSV形式で {len(comments)} 件のコメントを読み込みました")
        except Exception as e:
            print(f"非CSV形式での読み込みエラー: {e}")
    
    if len(comments) == 1 and len(comments[0]) == 36:
        print(f"特殊ケース検出: 36文字の単一コメント")
        return {"comment_count": 1, "avg_comment_length": 0}
    
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
        
        return {
            "comment_count": comment_count,
            "avg_comment_length": avg_length
        }
    else:
        print("コメントが見つかりませんでした")
        return {"comment_count": 0, "avg_comment_length": 0}

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

def main():
    """メイン関数"""
    test_dir = create_test_files()
    
    print("=== 36.0文字問題の検証 ===")
    
    file_36bytes = test_dir / "file_36bytes.csv"
    print(f"\nケース1: 36バイトのファイル ({file_36bytes})")
    print(f"ファイルサイズ: {file_36bytes.stat().st_size} バイト")
    result = analyze_file_directly(file_36bytes)
    print(f"結果: コメント数={result['comment_count']}, 平均長={result['avg_comment_length']}")
    
    file_36chars = test_dir / "file_36chars.csv"
    print(f"\nケース2: 36文字の単一コメント ({file_36chars})")
    print(f"ファイルサイズ: {file_36chars.stat().st_size} バイト")
    result = analyze_file_directly(file_36chars)
    print(f"結果: コメント数={result['comment_count']}, 平均長={result['avg_comment_length']}")
    
    file_normal = test_dir / "file_normal.csv"
    print(f"\nケース3: 通常のCSVファイル ({file_normal})")
    print(f"ファイルサイズ: {file_normal.stat().st_size} バイト")
    result = analyze_file_directly(file_normal)
    print(f"結果: コメント数={result['comment_count']}, 平均長={result['avg_comment_length']}")
    
    for file in test_dir.glob("*.csv"):
        file.unlink()
    test_dir.rmdir()

if __name__ == "__main__":
    main()
