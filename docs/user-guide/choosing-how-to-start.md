# 広聴AI の始め方（どの方法で使うか）

広聴AI は、目的によって使い方が変わります。まず「何をしたいか」で選び、次に「どの構成で動かすか」を決めます。環境構築で迷ったら、**最初の分岐は OS ではなく「誰が・何台で使うか」**です。

## まず、何をしたいか

| やりたいこと | 方法 | 参照 |
| --- | --- | --- |
| 渡されたレポートを**読む / 見せる** | 環境構築は不要。ブラウザで開くだけ | [レポートの読み方](report-reading-guide.md) |
| **自分のデータで**レポートを作る | 分析を実行する環境が必要（下記参照） | [導入を検討する方へ](adoption-guide.md) |
| **CLI・分析コア**で分析・研究する | Python パッケージを使う | [CLI クイックスタート](cli-quickstart.md) |
| **Web UI・本体を開発**する | ローカル開発環境を構築 | [開発者向けガイド](../development/contributing.md) |

## レポートを作る：どの構成にするか

自分のデータでレポートを作るには、分析を実行する環境が必要です。次から選びます。

| 選択肢 | 向いている人 | 補足 |
| --- | --- | --- |
| **自分で環境を建てる（セルフホスト）** | 技術的な準備ができる人・組織 | 下記「環境構築の決定フロー」へ |
| **ブラウザで動く serverless 版** | まず手軽に試したい人 | 別プロジェクト。機能・運用は本体と別（[serverless 版](https://github.com/tokoroten/kouchou-ai-serverless)） |
| **建ててくれる人に相談する** | 自分では建てない人 | 組織内の担当者・支援者・コミュニティへ |
| **誰かが運用するサービス（managed）** | — | **現状提供されていません**（将来の余地あり） |

費用・個人情報（データの送信先）・相談先の詳しい判断材料は [導入を検討する方へ](adoption-guide.md) を参照してください。

## 環境構築の決定フロー（自分で建てる場合）

**最初に決めるのは OS ではなく「使い方」です。**

1. **まず試す・非技術者が 1 台で動かす** → GUI 中心のセットアップ（下記 OS 別ガイド）
2. **開発・本格運用・複数人で使う** → Docker Compose で起動（[クイックスタート](../self-hosting/quickstart.md)）

どちらも Docker を使います。Docker Desktop を使えない場合は、下の「[Docker Desktop を使えない場合](#docker-desktop-を使えない場合)」を見てください。

OS 別のセットアップガイド:

- [Windows セットアップ](../self-hosting/windows-setup.md)
- [Mac セットアップ](../self-hosting/mac-setup.md)
- [Linux セットアップ](../self-hosting/linux-setup.md)

### Docker Desktop を使えない場合

組織の利用条件・ライセンス・インストール権限などで Docker Desktop を入れられない場合は、次から選びます。組織の PC では、権限や利用条件を回避して進めず、IT 管理者に確認してください。

| 経路 | 必要なソフト | API キーの置き場所 | できること・注意 |
| --- | --- | --- | --- |
| **CLI（分析コア）** | Python 3.12 以上 | シェルの環境変数、または実行するディレクトリの `.env` | Docker を使わずに分析し、`report.html` を出せます。管理画面・閲覧画面はありません。[CLI クイックスタート](cli-quickstart.md) |
| **API と管理画面を Docker なしで起動** | Python（rye）・Node.js（pnpm） | `apps/api/.env` と `apps/admin/.env` | [クイックスタート](../self-hosting/quickstart.md)の「ローカル開発（Dockerを使わずに起動）」。開発者向けの手順で、閲覧画面（public-viewer）は含みません |
| **Linux の Docker Engine** | Docker Engine・Docker Compose v2 | リポジトリ直下の `.env` | Docker Desktop ではなく Docker Engine を使う手順です。[Linux セットアップ](../self-hosting/linux-setup.md) |
| **ブラウザで動く serverless 版** | ブラウザ | serverless 版の画面で入力 | 別プロジェクトで、本体と同じ機能・設定を保証しません。キーとデータの扱いはリンク先の説明を確認してください。[serverless 版](https://github.com/tokoroten/kouchou-ai-serverless) |

Windows の WSL2 上に Docker Engine を入れる経路や、Podman の compose 互換で起動する経路は、まだ動作を確かめていません（[#496](https://github.com/digitaldemocracy2030/kouchou-ai/issues/496) で確認中）。この案内では動作を保証しません。

どの経路でも、入力したコメントは選んだ LLM のプロバイダへ送られます。送信先と、外部に送らない構成（ローカル LLM）の条件は [導入を検討する方へ](adoption-guide.md) の 1 章を参照してください。

## 起動のしかた別のつまずきやすい点

設定ファイルの置き場所と、設定を変えた後にやることは、起動のしかたによって違います。

| 起動のしかた | 設定の置き場所 | 設定を変えた後 | ほかに気をつけること |
| --- | --- | --- | --- |
| **セットアップスクリプト**（`setup_win.bat` / `setup_mac.sh` / `setup_linux.sh`） | リポジトリ直下の `.env`（スクリプトが作る） | スクリプトをもう一度実行する（作り直しと起動まで行う）。`start_*` はイメージを作り直さないので、`.env` を手で直しても `NEXT_PUBLIC_` で始まる値などは反映されません | スクリプトを再実行すると、既存の `.env` は上書きされます。手で足した設定は控えておいてください |
| **Docker Compose**（[クイックスタート](../self-hosting/quickstart.md)） | リポジトリ直下の `.env` | `docker compose up -d --build` で作り直す。`NEXT_PUBLIC_` で始まる値などはイメージのビルド時に埋め込まれるため、`--build` が要ります | `docker compose restart` では `.env` を読み直しません |
| **Docker を使わずに起動**（API と管理画面） | API は `apps/api/.env`（API を起動するディレクトリからの相対パス。環境変数 `ENV_FILE` で別のファイルを指せる）、管理画面は `apps/admin/.env` | API（`make run`）と管理画面（`pnpm dev`）を起動し直す | `packages/analysis-core` を editable install しないと `No module named analysis_core` で失敗します。`apps/admin/.env` の `NEXT_PUBLIC_ADMIN_API_KEY` は API の `ADMIN_API_KEY` と同じ値にします |
| **CLI**（[CLI クイックスタート](cli-quickstart.md)） | シェルの環境変数、または実行するディレクトリ（か、その親）の `.env` | 次の実行から反映されます | シェルで `export` した値があると、`.env` の値より優先されます。古いキーが残っていないか確認してください |

## 関連ページ

- [導入を検討する方へ](adoption-guide.md) — 費用・個人情報・相談先
- [レポートの読み方](report-reading-guide.md) — 出力（散布図・クラスタ）の読み方
- [CLI クイックスタート](cli-quickstart.md) — 分析者・研究者向け
