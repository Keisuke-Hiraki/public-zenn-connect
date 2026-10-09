---
title: "GuardDuty RDS 保護に RDS Data Activity Monitoring が増え、クエリの振る舞い検知が可能になりました"
emoji: "🗄️"
type: "tech"
topics: ["aws", "guardduty", "rds", "aurora", "security"]
published: false
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

皆さんは GuardDuty の RDS 保護（RDS Protection）を使用していますか？

これまで RDS 保護は、データベースへの **ログインアクティビティ** を分析し、不審なログインやブルートフォースを検知する機能でした。

そんな中、GuardDuty のコンソールを見ていたら、RDS 保護の設定に「RDS Data Activity Monitoring」という新しい項目が追加されていました。

![](/images/guardduty-rds-data-activity-monitoring_20261009-console.png)

今回はこの RDS Data Activity Monitoring で何ができるようになったのか、ドキュメントをもとに整理してみました。

:::message
この記事の 3 行まとめ

- RDS 保護に、クエリ（データプレーン）の振る舞いを分析する「RDS Data Activity Monitoring」が追加され、大量読み出し・削除・DROP などを検知できるようになりました
- 対象は Aurora PostgreSQL と RDS for PostgreSQL のみで、ログインアクティビティ監視が有効であることが前提です
- すでに RDS 保護を利用しているアカウントでも、データアクティビティ監視には **ログインアクティビティ監視とは別に 30 日間の無料トライアル** が適用されます
:::

従来のログインアクティビティ監視と、今回追加されたデータアクティビティ監視を比較すると以下のようになります。

| 項目 | ログインアクティビティ監視 | データアクティビティ監視（今回追加） |
| --- | --- | --- |
| 分析対象 | ログインの成功・失敗 | `SELECT` / `DELETE` / `DROP` などのクエリ傾向 |
| 主な検知内容 | 不審なログイン、ブルートフォース | 大量データの読み出し（持ち出し）、データ削除・破壊 |
| 対応エンジン | Aurora MySQL / Aurora PostgreSQL / RDS for PostgreSQL / RDS for MySQL / RDS for MariaDB / Aurora PostgreSQL Limitless | Aurora PostgreSQL / RDS for PostgreSQL |
| 前提条件 | なし | ログインアクティビティ監視の有効化 |
| 無料トライアル | RDS 保護の初回有効化時に 30 日 | データアクティビティ監視の初回有効化時に別途 30 日 |

## RDS Data Activity Monitoring とは

このセクションでは、RDS Data Activity Monitoring の概要と前提条件を整理します。

ドキュメントでは、データアクティビティ監視について以下のように説明されています。

> RDS Protection for data activity analyzes database query patterns on Amazon Aurora for PostgreSQL and RDS for PostgreSQL databases to detect potential data access and manipulation threats.

https://docs.aws.amazon.com/guardduty/latest/ug/rds-protection.html

つまり、これまでの「誰がどこからログインしたか」に加えて、**ログインした後に何をしたか** を GuardDuty が見てくれるようになった、という位置づけです。

具体例としては、以下のような振る舞いが挙げられています。

- そのデータベースやユーザーとしては通常よりも大幅に多い行を読み出している
- データを削除（`DELETE`）したり、テーブルなどを削除（`DROP`）したりしている
- 既知の悪意のある IP アドレスや Tor の IP アドレスからデータベースを操作している

### 前提条件と注意点

このセクションでは、有効化する前に押さえておきたい前提条件をまとめます。

コンソールにも記載されている通り、データアクティビティ監視を機能させるには **ログインアクティビティ監視（RDS 保護）が有効である必要があります。**

> RDS Protection for login activity is required for RDS Protection for data activity to function.

その他、ドキュメントから読み取れる注意点は以下の通りです。

- 有効化直後や DB インスタンスの新規作成直後は、通常の振る舞いを学習するために **最大 2 週間の学習期間** があり、その間は異常検知の Finding が出ない場合があります
- GuardDuty は分析に使ったデータアクティビティのログ自体はユーザーに提供しません
- 追加のインフラは不要で、データベースのパフォーマンスに影響しないように設計されているとされています

GuardDuty がログを提供しないため、Finding が出た後の調査にはデータベース側の監査ログが必要になります。pgaudit や、Aurora PostgreSQL であれば Database Activity Streams などをあらかじめ用意しておくとよさそうです。

### 対応しているデータベース

このセクションでは、データアクティビティ監視の対象となるエンジンとバージョンを整理します。

ログインアクティビティ監視は MySQL / MariaDB 系にも対応していますが、データアクティビティ監視は **PostgreSQL 系のみ** の対応です。

| DB エンジン | データアクティビティ監視の対応バージョン |
| --- | --- |
| Aurora PostgreSQL | 11.19 / 12.14 / 13.10 / 14.7 / 15.2 以降、およびそれ以降のメジャーバージョン |
| RDS for PostgreSQL | 11.20 / 12.15 / 13.11 / 14.8 / 15.3 以降、およびそれ以降のメジャーバージョン |
| Aurora MySQL | 非対応 |
| RDS for MySQL | 非対応 |
| RDS for MariaDB | 非対応 |
| Aurora PostgreSQL Limitless Database | 非対応 |

最新の対応状況は以下を参照してください。

https://docs.aws.amazon.com/guardduty/latest/ug/rds-protection.html#rds-pro-supported-db

## 追加された Finding タイプ

このセクションでは、データアクティビティ監視で新たに生成される Finding タイプを紹介します。

Finding タイプのドキュメントを見ると、「Feature: RDS DB Activity Monitoring」と記載された Finding が 7 種類追加されていました。

https://docs.aws.amazon.com/guardduty/latest/ug/findings-rds-protection.html

| Finding タイプ | 内容 | デフォルト重要度 |
| --- | --- | --- |
| `Exfiltration:RDS/AnomalousBehavior` | 異常な大量データの読み出し（`SELECT`） | Low / Medium / High |
| `Impact:RDS/AnomalousBehavior.Drop` | 異常な `DROP` の実行 | Medium / High |
| `Impact:RDS/AnomalousBehavior.Delete` | 異常な `DELETE` の実行 | Low / Medium / High |
| `Exfiltration:RDS/MaliciousIPCaller` | 既知の悪意のある IP からのデータ抽出クエリ | High |
| `Exfiltration:RDS/TorIPCaller` | Tor 出口ノードからのデータ抽出クエリ | High |
| `Impact:RDS/MaliciousIPCaller` | 既知の悪意のある IP からの破壊的なステートメント | High |
| `Impact:RDS/TorIPCaller` | Tor 出口ノードからの破壊的なステートメント | High |

これまでの RDS 保護の Finding は、`CredentialAccess` や `Discovery` といったログイン前後のタクティクスが中心でした。今回 `Exfiltration`（持ち出し）と `Impact`（破壊）が加わり、侵入後の被害そのものを捉えられるようになっています。

### AnomalousBehavior 系の重要度の決まり方

このセクションでは、機械学習ベースの Finding で重要度がどのように変わるかを整理します。

`AnomalousBehavior` 系の Finding は、操作元のネットワークや操作内容によって重要度が変わります。`Exfiltration:RDS/AnomalousBehavior` を例にすると以下の通りです。

| 重要度 | 条件 |
| --- | --- |
| Low | プライベートネットワークの IP アドレスから `SELECT` を実行 |
| Medium | パブリック IP アドレスから `SELECT` を実行 |
| High | 異常に大量の行を返す `SELECT` を実行し、かつ未知のパブリックネットワークからの操作、または高権限ロールや管理クライアントによる操作 |

`Impact:RDS/AnomalousBehavior.Delete` も同様の考え方です。`Impact:RDS/AnomalousBehavior.Drop` は異常な `DROP` で Medium、複数の `DROP` かつ未知のパブリックネットワーク、高権限ロールまたは管理クライアントからの操作で High となります。

### Finding に含まれるカウンター

このセクションでは、データアクティビティ系の Finding で確認できる情報を紹介します。

Finding の詳細には、異常と判断された操作に関する以下のカウンターが含まれます。

| カウンター | 内容 |
| --- | --- |
| `selectedRows` / `selectStatement` | `SELECT` で返された行数 / `SELECT` の実行回数 |
| `deletedRows` / `deleteStatement` | `DELETE` で削除された行数 / `DELETE` の実行回数 |
| `dropStatement` | `DROP` や `TRUNCATE` などの破壊的な操作の回数 |

https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings-summary.html#rds-pro-data-activity-anomaly

クエリ本文までは含まれないものの、「どのユーザーが」「どのくらいの行を」読み出したり削除したりしたのかが分かるため、初動の影響範囲の見積もりに役立ちそうです。

## 無料トライアルは個別に 30 日適用される

このセクションでは、データアクティビティ監視の無料トライアルの扱いを確認します。

コンソールでは、RDS Data Activity Monitoring の横に「無料トライアル: 30 日」と表示されていました。

ドキュメントにも、データアクティビティ監視の無料トライアルについて以下のように明記されています。ログインアクティビティ監視をすでに使っているアカウントでも、データアクティビティ監視を初めて有効化した場合は **別途 30 日間の無料トライアルが適用されます。**

> When you are already using RDS Protection for login activity in an AWS account and decide to enable RDS Protection for data activity for the first time, your account will get a 30-day free trial for RDS Protection for data activity.

実際に `get-remaining-free-trial-days` で確認してみると、RDS 保護自体（`RDS_LOGIN_EVENTS`）は無料期間が終了していますが、`RDS_DATA_RISK` は別枠で 30 日残っていることが分かります。

```bash
aws guardduty get-remaining-free-trial-days \
  --detector-id <detector-id> \
  --account-ids <account-id>
```

```json
{
    "Accounts": [
        {
            "AccountId": "<account-id>",
            "Features": [
                {
                    "Name": "RDS_LOGIN_EVENTS",
                    "FreeTrialDaysRemaining": 0
                },
                {
                    "Name": "RDS_DATA_RISK",
                    "FreeTrialDaysRemaining": 30
                }
            ]
        }
    ]
}
```

※ 出力は RDS 保護に関係する部分のみを抜粋しています。

すでに RDS 保護を長く使っているアカウントでも、追加費用なしで 30 日間試せます。PostgreSQL 系のデータベースを運用している場合は、まず有効化して無料期間中に料金の見積もりを確認するのがよさそうです。

:::message alert
無料トライアル終了後も自動で無効化されることはなく、そのまま課金が始まります。また、執筆時点では料金ページにデータアクティビティ監視の個別の料金は確認できませんでした。無料期間中に GuardDuty コンソールの「使用状況」などから RDS 保護全体の費用感を確認しておくことをおすすめします。
:::

https://aws.amazon.com/jp/guardduty/pricing/

## まとめ

今回は GuardDuty RDS 保護に追加された RDS Data Activity Monitoring について整理しました。

これまでの RDS 保護が検知できたのは不審なログインまででした。今回のアップデートで、ログイン後の大量読み出しや `DELETE`・`DROP` といったデータそのものへの被害につながる振る舞いも、`Exfiltration` / `Impact` の Finding として検知できるようになりました。正規の認証情報が漏えいして正常にログインされてしまったケースでも、その後の不審な操作を捉えられるのは大きな進化だと思います。

一方で、利用にあたっては以下の点に注意が必要です。

- 対応エンジンは Aurora PostgreSQL と RDS for PostgreSQL のみ
- ログインアクティビティ監視（RDS 保護）の有効化が前提
- 有効化直後は最大 2 週間の学習期間がある
- GuardDuty はログを提供しないため、Finding 発生後の調査にはデータベース側の監査ログを別途用意しておく必要がある

すでに RDS 保護を使っているアカウントでも、データアクティビティ監視には個別に 30 日間の無料トライアルが適用されます。Aurora PostgreSQL や RDS for PostgreSQL を利用している方は、まず有効化して検知内容と費用感を確かめてみてください！

この記事がどなたかの役に立つと嬉しいです。
