# IIC マルチリージョン対応 セキュリティ記事 設計 (spec)

## Context

2026/7/29 に AWS IAM Identity Center (IIC) のマルチリージョンサポートが、Identity Center directory を
ID ソースとするインスタンスにも拡大された。従来は外部 IdP 接続時のみ利用可能だった機能。

この記事は「新機能の紹介」に留めず、**認証基盤の可用性はセキュリティ対策として必要である**という主張を
背骨に据える。可用性は CIA トライアドの "A" であり、ID・アクセス基盤が単一リージョンに依存していると、
そのリージョン障害時に AWS アカウントへのアクセス（インシデント対応を含む）ごと失う。マルチリージョン化は
運用改善ではなくレジリエンス設計の一部である、というメッセージを届ける。

対象: `articles/iic-multi-region-ssupport-for-security.md`（既存の空ファイル）

## 記事の主張（背骨）

- 可用性 = セキュリティ (CIA の A)
- 認証基盤の単一リージョン依存は現実的リスク（過去障害事例で裏付け）
- IIC マルチリージョン化は「試す新機能」ではなく「検討すべきセキュリティ設計」
- ただし前提条件（CMK 必須等）とコスト注意点も現実的に理解した上で導入判断する

トーン: 特定ベンダー批判にしない中立。Azure 事例は「単一リージョン依存の一般的リスク」の例として扱う。

## フロントマター

```yaml
title: "IAM Identity Center のマルチリージョン対応が Identity Center directory にも拡大 — 認証基盤の可用性はセキュリティ対策として必要という話"
emoji: "🌐"
type: "tech"
topics: ["aws", "security", "iam", "identitycenter", "organizations"]
published: false
publication_name: cscloud_blog
```

（タイトルは執筆時に微調整可）

## 構成

1. **イントロ** — `こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) ...` 自己紹介 + アップデート概要
   （2026/7/29、Identity Center directory 対応拡大、17 のデフォルト有効リージョン）。冒頭から
   「便利機能というより可用性=セキュリティ対策として捉えるべき」という論調を出す。
2. **`:::message` この記事の3行まとめ** — (1)何が変わったか (2)可用性はセキュリティ、単一リージョン依存はリスク
   (3)前提条件（組織インスタンス+マルチリージョン CMK）
3. **## なぜ認証基盤の可用性が「セキュリティ対策」なのか** ← 主張の土台
   - 可用性は CIA の A。認証基盤が落ちる = 全アクセス停止 = インシデント対応もできない
   - Break-Glass 記事をあっさり紹介（1〜2文 + URL 埋め込みカード）。2025/10 us-east-1 障害が背景。
     `https://zenn.dev/cscloud_blog/articles/idp-break-glass-access`
   - Azure DDoS 起因ポータル障害事例（2024/7/30、約8時間）を「単一リージョン依存の現実的リスク」として中立的に対比
   - 「だからこそ ID 基盤の多重化が要る」で本題へ橋渡し
4. **## 何がアップデートされたか** — 従来は外部 IdP のみ → Identity Center directory でも可能に。
   Active Directory は非対応、追加費用なし（KMS は別途）
5. **## マルチリージョンの仕組み**
   - プライマリ / 追加リージョン、非同期・結果整合性
   - レプリケーション対象の表（ユーザー・グループ・権限セット・割り当て・設定・アプリメタデータ・
     Trusted token issuer・セッション）
   - フェイルオーバー挙動（別リージョンのアクセスポータルに切替、CLI は各リージョンで個別認可）
6. **## セキュリティ対策としてどう効くか（主軸）**
   - プライマリ障害時も、事前にプロビジョニング済みの権限で別リージョンからアクセス継続
   - Break-Glass との「多層防御」— どちらか一方でなく併用推奨（AWS ドキュメントも break-glass 併用を推奨）
   - 締め: 「導入は運用改善ではなくレジリエンス設計の一部」という主張
7. **## 利用にあたっての前提と注意点**
   - 組織インスタンス限定（アカウントインスタンス不可）/ AD 非対応 / マルチリージョン CMK 必須
   - オプトインリージョン非対応 / リージョン数のクォータ
   - リージョン削除時: アプリ削除しないと課金継続、アプリアクセス喪失の注意
8. **## まとめ** — 「新機能だから試す」ではなく「セキュリティ設計として検討すべき」で締める

## Zenn 記法・規約

- 見出しは `##` から（`#` はタイトル予約）
- `:::message` / `:::message alert` / `:::details` を使用（HTML の details は使わない）
- 本文・見出しに絵文字を使わない（frontmatter の emoji のみ）
- UI 要素名はバックティックか「」で囲む
- URL は単独行で埋め込みカードにする
- 比較・要点は上部にも置き、末尾で重複させない

## 参考リンク（本文に埋め込む候補）

- What's New: https://aws.amazon.com/jp/about-aws/whats-new/2026/07/aws-iam-identity-center-extends-multi-region-support-to-identity-center-directory/
- ユーザーガイド (概要): https://docs.aws.amazon.com/singlesignon/latest/userguide/multi-region-iam-identity-center.html
- フェイルオーバー: https://docs.aws.amazon.com/singlesignon/latest/userguide/multi-region-failover.html
- Break-Glass 記事: https://zenn.dev/cscloud_blog/articles/idp-break-glass-access

## 執筆後の確認

- `/blog-review` スキルでレビュー（技術的正確性・炎上リスク・誤字・機微情報）
- `published: false` のまま納品（公開はユーザー判断）
- スクリーンショットは今回なし（解説中心）。図表は Markdown 表で対応
