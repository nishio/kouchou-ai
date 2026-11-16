# GitHub Copilot 向けの指示（広聴AI / kouchou-ai）

このファイルは索引です。手順やルールの正本は下に挙げるファイルにあり、ここには写しません。内容が食い違うときは正本に従ってください。

## 回答の言語

- 説明・コメント・PR やコミットの文章は日本語で書いてください。コード中の識別子は既存のコードに合わせます。

## 読む順番

1. `CONTRIBUTING.md`：担当の割り当て、実装計画の共有、CLA、PR のルール（貢献ルールの正本）
2. `docs/development/ai-assistants.md`：AI エージェントで Issue から PR まで進める作業の流れと、作業ごとに追加で読むもの
3. `CLAUDE.md`：`skills/` の索引（Claude Code 向けだが、索引として他のエージェントにも使える）
4. 作業に合う skill：`skills/kouchou-ai-architecture/SKILL.md`（構造）、`skills/kouchou-ai-development/SKILL.md`（起動・設定・lint）、`skills/kouchou-ai-testing/SKILL.md`（テスト）。E2E を触るときは `test/e2e/CLAUDE.md` も読む

## 守ること

- 変更は Issue の範囲に絞り、変更した領域のテスト・lint・型検査を走らせてから PR にする
- PR の本文は `.github/PULL_REQUEST_TEMPLATE.md` に沿って書き、確かめたこと・確かめていないこと・実 API での確認の有無を分けて書く
- CLA への同意、人間による動作確認、レビュー依頼や Slack などへの連絡は、AI が代わりに済ませたことにしない（`docs/development/ai-assistants.md` の「人間の判断・attentionを使う操作」）
- API キー・個人情報・非公開データをコードや PR に含めない
