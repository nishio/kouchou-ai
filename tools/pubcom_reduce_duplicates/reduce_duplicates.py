"""
パブリックコメント重複削減ツール

このスクリプトは、パブリックコメントに含まれる類似・重複コメントを識別し、
代表的なコメントを抽出するためのツールです。
埋め込みベクトルを使用して類似度を計算し、階層的クラスタリングによって
類似コメントをグループ化します。
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from openpyxl import Workbook
from typing import List, Dict, Any, Tuple, Optional
import json
from datetime import datetime


def reduce_duplicates(
    comments: List[Dict[str, Any]],
    output_dir: str,
    distance_threshold: float = 0.80,
    model_name: str = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2',
) -> Tuple[List[Dict[str, Any]], str]:
    """
    パブリックコメントの重複を削減し、各クラスタの代表的なコメントを抽出する

    Args:
        comments: コメントのリスト。各コメントは辞書で、少なくとも 'id' と 'comment' キーを含む必要がある
        output_dir: 結果を保存するディレクトリのパス
        distance_threshold: クラスタリングのための距離しきい値（0〜1の範囲、大きいほど類似度が低くても同じクラスタになる）
        model_name: 使用するSentenceTransformerのモデル名

    Returns:
        代表的なコメントのリストとExcelファイルへのパス
    """
    print(f"Processing {len(comments)} comments...")
    
    if not comments:
        print("No comments to process.")
        return [], ""
    
    comment_texts = [comment['comment'] for comment in comments]
    
    valid_indices = [i for i, text in enumerate(comment_texts) if text.strip()]
    if not valid_indices:
        print("No valid comments to process (all empty).")
        return [], ""
    
    valid_comments = [comments[i] for i in valid_indices]
    valid_texts = [comment_texts[i] for i in valid_indices]
    
    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    
    print("Calculating embeddings...")
    embeddings = model.encode(valid_texts)
    print(f"Embedding shape: {embeddings.shape}")
    
    print(f"Clustering with distance threshold: {distance_threshold}")
    cluster_model = AgglomerativeClustering(
        n_clusters=None,
        metric='cosine',
        linkage='complete',
        distance_threshold=distance_threshold,
        compute_full_tree=True
    )
    clusters = cluster_model.fit_predict(embeddings)
    num_clusters = len(set(clusters))
    print(f"Found {num_clusters} clusters")
    
    cluster_data = {}
    for i, cluster_id in enumerate(clusters):
        if cluster_id not in cluster_data:
            cluster_data[cluster_id] = []
        cluster_data[cluster_id].append(i)
    
    central_comments = []
    result_table = []
    
    for cluster_id, indices in cluster_data.items():
        cluster_embeddings = embeddings[indices]
        
        centroid = np.mean(cluster_embeddings, axis=0)
        
        min_dist = float('inf')
        center_idx = -1
        
        for i, idx in enumerate(indices):
            dist = cosine(centroid, embeddings[idx])
            if dist < min_dist:
                min_dist = dist
                center_idx = idx
        
        central_comment = valid_comments[center_idx]
        central_comments.append({
            'id': central_comment['id'],
            'comment': central_comment['comment'],
            'source': central_comment.get('source', None),
            'url': central_comment.get('url', None),
            'cluster_id': int(cluster_id),  # numpy.int64をPythonのintに変換
            'cluster_size': len(indices)
        })
        
        for idx in indices:
            dist_to_center = cosine(embeddings[idx], embeddings[center_idx])
            result_table.append({
                'id': valid_comments[idx]['id'],
                'cluster_id': int(cluster_id),  # numpy.int64をPythonのintに変換
                'distance_to_center': float(dist_to_center),  # numpy.float64をPythonのfloatに変換
                'comment': valid_comments[idx]['comment'],
                'is_center': bool(idx == center_idx)  # numpy.boolをPythonのboolに変換
            })
    
    central_comments = sorted(central_comments, key=lambda x: x['cluster_size'], reverse=True)
    
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = os.path.join(output_dir, f'pubcom_clustering_results_{timestamp}.xlsx')
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        summary_df = pd.DataFrame(central_comments)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        for cluster_id in sorted(set([item['cluster_id'] for item in result_table])):
            cluster_df = pd.DataFrame([item for item in result_table if item['cluster_id'] == cluster_id])
            
            cluster_df = cluster_df.sort_values('distance_to_center', ascending=True)
            
            cluster_df = cluster_df.reset_index(drop=True)
            
            sheet_name = f'Cluster_{cluster_id:04d}'
            if len(sheet_name) > 31:
                sheet_name = f'C_{cluster_id}'
            cluster_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"Results saved to: {excel_path}")
    return central_comments, excel_path


def load_comments_from_csv(csv_path: str, comment_col: str, id_col: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    CSVファイルからコメントデータを読み込む
    
    Args:
        csv_path: CSVファイルのパス
        comment_col: コメントが含まれる列名
        id_col: IDが含まれる列名（オプション）
    
    Returns:
        コメントデータのリスト
    """
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(csv_path, encoding='cp932')
        except:
            df = pd.read_csv(csv_path, encoding='utf-8', on_bad_lines='skip')
    
    if comment_col not in df.columns:
        raise ValueError(f"Column '{comment_col}' not found in CSV file. Available columns: {df.columns.tolist()}")
    
    comments = []
    for idx, row in df.iterrows():
        comment_data = {
            'comment': str(row[comment_col])
        }
        
        if id_col and id_col in df.columns:
            comment_data['id'] = str(row[id_col])
        else:
            comment_data['id'] = str(int(idx) + 1)
        
        comments.append(comment_data)
    
    return comments


def main():
    parser = argparse.ArgumentParser(description='パブリックコメント重複削減ツール')
    parser.add_argument('input_file', help='入力CSVファイルのパス')
    parser.add_argument('--comment-col', default='comment', help='コメントが含まれる列名（デフォルト: comment）')
    parser.add_argument('--id-col', help='IDが含まれる列名（オプション）')
    parser.add_argument('--output-dir', default='output', help='出力ディレクトリ（デフォルト: output）')
    parser.add_argument('--threshold', type=float, default=0.80, help='類似度閾値（0.75〜0.90、デフォルト: 0.80）')
    parser.add_argument('--model', default='sentence-transformers/paraphrase-multilingual-mpnet-base-v2', 
                        help='使用する埋め込みモデル（デフォルト: sentence-transformers/paraphrase-multilingual-mpnet-base-v2）')
    
    args = parser.parse_args()
    
    try:
        comments = load_comments_from_csv(args.input_file, args.comment_col, args.id_col)
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        sys.exit(1)
    
    reduced_comments, excel_path = reduce_duplicates(
        comments=comments,
        output_dir=args.output_dir,
        distance_threshold=args.threshold,
        model_name=args.model
    )
    
    print(f"\n重複削減結果: {len(comments)}件のコメントから{len(reduced_comments)}件の代表的なコメントを抽出しました。")
    print(f"重複削減率: {(1 - len(reduced_comments) / len(comments)) * 100:.1f}%")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(args.output_dir, f'reduced_comments_{timestamp}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(reduced_comments, f, ensure_ascii=False, indent=2)
    
    print(f"\n結果ファイル:")
    print(f"- Excel: {excel_path}")
    print(f"- JSON: {json_path}")


if __name__ == "__main__":
    main()
