"""
実験的なembeddingベースの前処理スクリプト
extractionステップをスキップし、コメントに直接embeddingを適用して
階層的クラスタリングを行い、最も離れたサンプルを特定する
"""

import argparse
import os
import sys
import json
import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import pdist, squareform
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.llm import request_to_embed
from hierarchical_utils import initialization, update_status


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the embedding preprocessing experiment.")
    parser.add_argument("config", help="Path to config JSON file that defines the experiment.")
    return parser.parse_args()


def load_comments(config):
    """コメントデータを直接読み込む"""
    print("コメントデータを読み込み中...")
    comments = pd.read_csv(
        f"inputs/{config['input']}.csv", 
        usecols=["comment-id", "comment-body"]
    )
    limit = config["extraction"]["limit"]
    if limit and limit < len(comments):
        comments = comments.iloc[:limit]
    
    print(f"読み込んだコメント数: {len(comments)}")
    return comments


def generate_embeddings(comments, config):
    """コメントから直接埋め込みベクトルを生成"""
    print("埋め込みベクトルを生成中...")
    model = config["model"]
    
    embeddings = []
    batch_size = 20  # APIの制限を考慮したバッチサイズ
    
    for i in tqdm(range(0, len(comments), batch_size)):
        batch = comments["comment-body"].tolist()[i:i+batch_size]
        embeds = request_to_embed(batch, model)
        embeddings.extend(embeds)
    
    embedding_df = pd.DataFrame({
        "comment-id": comments["comment-id"].values,
        "comment-body": comments["comment-body"].values,
        "embedding": embeddings
    })
    
    output_dir = f"outputs/{config['output_dir']}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    embedding_df.to_pickle(f"{output_dir}/comment_embeddings.pkl")
    print(f"埋め込みベクトルを保存しました: {output_dir}/comment_embeddings.pkl")
    
    return embedding_df


def perform_hierarchical_clustering(embedding_df, config):
    """Ward法を使用した階層的クラスタリング"""
    print("階層的クラスタリングを実行中...")
    
    embeddings_array = np.array(embedding_df["embedding"].tolist())
    
    print("距離行列を計算中...")
    distances = pdist(embeddings_array, metric='euclidean')
    
    print("Ward法によるクラスタリングを実行中...")
    Z = sch.ward(distances)
    
    cluster_nums = config["hierarchical_clustering"]["cluster_nums"]
    
    results = {}
    for n_clusters in cluster_nums:
        print(f"クラスター数 {n_clusters} でラベル付け中...")
        labels = sch.fcluster(Z, t=n_clusters, criterion='maxclust')
        results[n_clusters] = labels
    
    result_df = embedding_df.copy()
    for n_clusters, labels in results.items():
        result_df[f"cluster_{n_clusters}"] = labels
    
    output_dir = f"outputs/{config['output_dir']}"
    result_df.to_csv(f"{output_dir}/clustering_results.csv", index=False)
    print(f"クラスタリング結果を保存しました: {output_dir}/clustering_results.csv")
    
    return result_df, Z


def find_distant_samples(result_df, Z, config):
    """各クラスター内で最も離れたサンプルペアを特定"""
    print("クラスター内の最遠サンプルを特定中...")
    
    embeddings_array = np.array(result_df["embedding"].tolist())
    
    distance_matrix = squareform(pdist(embeddings_array, metric='euclidean'))
    
    cluster_nums = config["hierarchical_clustering"]["cluster_nums"]
    distant_samples = []
    
    for n_clusters in cluster_nums:
        cluster_column = f"cluster_{n_clusters}"
        
        for cluster_id in range(1, n_clusters + 1):
            cluster_indices = result_df[result_df[cluster_column] == cluster_id].index.tolist()
            
            if len(cluster_indices) < 2:
                continue  # サンプルが1つしかない場合はスキップ
            
            max_distance = 0
            max_pair = (0, 0)
            
            for i in range(len(cluster_indices)):
                for j in range(i + 1, len(cluster_indices)):
                    idx1, idx2 = cluster_indices[i], cluster_indices[j]
                    distance = distance_matrix[idx1, idx2]
                    
                    if distance > max_distance:
                        max_distance = distance
                        max_pair = (idx1, idx2)
            
            if max_distance > 0:
                sample1 = result_df.iloc[max_pair[0]]
                sample2 = result_df.iloc[max_pair[1]]
                
                distant_samples.append({
                    "cluster_level": n_clusters,
                    "cluster_id": cluster_id,
                    "sample1_id": sample1["comment-id"],
                    "sample1_text": sample1["comment-body"],
                    "sample2_id": sample2["comment-id"],
                    "sample2_text": sample2["comment-body"],
                    "distance": max_distance,
                    "cluster_size": len(cluster_indices)
                })
    
    distant_df = pd.DataFrame(distant_samples)
    output_dir = f"outputs/{config['output_dir']}"
    distant_df.to_csv(f"{output_dir}/distant_samples.csv", index=False)
    print(f"最遠サンプルを保存しました: {output_dir}/distant_samples.csv")
    
    return distant_df


def estimate_reduction(distant_df):
    """最遠サンプルを統合した場合の項目数削減を見積もる"""
    print("項目数削減の見積もりを計算中...")
    
    for level in distant_df["cluster_level"].unique():
        level_df = distant_df[distant_df["cluster_level"] == level]
        total_clusters = level
        total_items = level_df["cluster_size"].sum()
        
        print(f"\nクラスターレベル {level} の分析:")
        print(f"  クラスター数: {total_clusters}")
        print(f"  総項目数: {total_items}")
        
        for _, row in level_df.iterrows():
            print(f"\nクラスター {row['cluster_id']} (サイズ: {row['cluster_size']}):")
            print(f"  サンプル1: {row['sample1_text'][:100]}...")
            print(f"  サンプル2: {row['sample2_text'][:100]}...")
            print(f"  距離: {row['distance']:.4f}")
            print(f"  これらを統合すると、クラスター内の項目数が {row['cluster_size']} から {row['cluster_size']-1} に減少します")
        
        total_reduction = len(level_df)
        reduction_percentage = (total_reduction / total_items) * 100
        print(f"\n全クラスターで最遠サンプルを統合した場合:")
        print(f"  削減される項目数: {total_reduction}")
        print(f"  削減率: {reduction_percentage:.2f}%")


def main():
    args = parse_arguments()
    
    with open(args.config) as f:
        config = json.load(f)
    
    config["output_dir"] = os.path.basename(args.config).split(".")[0]
    
    print(f"実験: {config['name']}")
    print(f"入力データ: {config['input']}")
    print(f"埋め込みモデル: {config['model']}")
    
    comments = load_comments(config)
    
    embedding_df = generate_embeddings(comments, config)
    
    result_df, Z = perform_hierarchical_clustering(embedding_df, config)
    
    distant_df = find_distant_samples(result_df, Z, config)
    
    estimate_reduction(distant_df)
    
    print("\n実験が完了しました。")


if __name__ == "__main__":
    main()
