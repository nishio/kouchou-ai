# パブリックコメント重複削減ツール

このツールは、パブリックコメントに含まれる類似・重複コメントを識別し、代表的なコメントを抽出するためのものです。埋め込みベクトルを使用して類似度を計算し、階層的クラスタリングによって類似コメントをグループ化します。

## 機能概要

- SentenceTransformerを使用してコメントの埋め込みベクトルを生成
- コサイン類似度に基づく階層的クラスタリングで類似コメントをグループ化
- 各クラスタの中心に最も近いコメントを代表として抽出
- 詳細な分析結果をExcelファイルに出力

## インストール方法

1. 必要なPythonパッケージをインストールします：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本的な使い方

```bash
python reduce_duplicates.py input.csv --comment-col コメント --id-col ID
```

### オプション

```
usage: reduce_duplicates.py [-h] [--comment-col COMMENT_COL] [--id-col ID_COL]
                           [--output-dir OUTPUT_DIR] [--threshold THRESHOLD]
                           [--model MODEL]
                           input_file

パブリックコメント重複削減ツール

positional arguments:
  input_file            入力CSVファイルのパス

options:
  -h, --help            ヘルプメッセージを表示して終了
  --comment-col COMMENT_COL
                        コメントが含まれる列名（デフォルト: comment）
  --id-col ID_COL       IDが含まれる列名（オプション）
  --output-dir OUTPUT_DIR
                        出力ディレクトリ（デフォルト: output）
  --threshold THRESHOLD
                        類似度閾値（0.75〜0.90、デフォルト: 0.80）
  --model MODEL         使用する埋め込みモデル（デフォルト: sentence-transformers/paraphrase-multilingual-mpnet-base-v2）
```

## 出力結果

1. **Excelファイル** (`pubcom_clustering_results_YYYYMMDD_HHMMSS.xlsx`)
   - `Summary`シート：すべての代表的コメントとクラスタサイズ
   - `Cluster_XXXX`シート：各クラスタの詳細情報（中心からの距離順）

2. **JSONファイル** (`reduced_comments_YYYYMMDD_HHMMSS.json`)
   - 代表的なコメントのリスト（JSONフォーマット）

## 使用例

### 基本的な使用例

```bash
python reduce_duplicates.py pubcom_data.csv --comment-col "コメント本文" --id-col "番号"
```

### 類似度閾値を調整する例

```bash
python reduce_duplicates.py pubcom_data.csv --threshold 0.85
```

コメント数に応じて適切な `threshold` を選択することをお勧めします：

- コメント数が少ない場合（100件未満）：0.85〜0.90
- コメント数が中程度の場合（100〜1000件）：0.80〜0.85
- コメント数が多い場合（1000件以上）：0.75〜0.80

数値が小さいほど類似度の高いコメントのみがグループ化されます。

## 注意事項

- 大量のコメントを処理する場合は、十分なメモリを確保してください。
- 初回実行時は、埋め込みモデルのダウンロードに時間がかかる場合があります。
- 日本語のコメントに最適化されていますが、他の言語でも使用可能です。
