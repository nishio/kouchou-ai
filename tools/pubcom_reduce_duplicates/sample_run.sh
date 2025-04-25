
echo "=== パブリックコメント重複削減ツールのサンプル実行 ==="
echo "サンプルデータを使用して重複削減を実行します..."

cd "$(dirname "$0")"

if ! pip list | grep -q sentence-transformers; then
  echo "必要なパッケージをインストールしています..."
  pip install -r requirements.txt
fi

python reduce_duplicates.py sample_data/sample_comments.csv --comment-col comment --id-col id

echo ""
echo "=== 実行完了 ==="
echo "出力ディレクトリ(output)に結果ファイルが生成されています。"
