---
title: "KMSが最終使用状況を追跡できるようになったので新しいKMS条件キーを使って使用中のKMSキーを削除から保護してみる"
emoji: "🔑"
type: "tech"
topics: ["aws", "kms"]
published: false
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

2026年4月、AWS KMS に**KMSキーの最終使用状況を追跡できる新機能**が追加されました。
あわせて、新しい KMS 条件キー `kms:TrailingDaysWithoutKeyUsage` を使うことで、**直近使用されたKMSキーを誤削除から守るポリシー**が設定できるようになりました。

https://aws.amazon.com/jp/about-aws/whats-new/2026/04/aws-kms-tracks-last-usage-kms-keys/

本記事では、このアップデートの概要と、新規で追加された KMS 条件キーとSCPを活用した保護の仕組みを実際に検証した内容をご紹介します。

## アップデートの概要

これまでKMSキーの使用状況を確認するにはCloudTrailログを手動で分析する必要がありましたが、今回のアップデートにより以下の情報がコンソールやAPIから直接確認できるようになりました。

| 情報 | 内容 |
|---|---|
| 最終使用日時 | 最後に暗号化操作が実行されたタイムスタンプ |
| 操作タイプ | `Encrypt`、`GenerateDataKey` などの操作種別 |
| CloudTrail イベントID | 対応するCloudTrailイベントの識別子 |

:::message
追跡対象となる操作は `Decrypt`、`Encrypt`、`GenerateDataKey`、`Sign`、`Verify` などの**暗号化操作**のみです。キーポリシーの変更など非暗号化操作は追跡されません。
具体的な対象操作の一覧はこちらをご覧ください。
https://docs.aws.amazon.com/kms/latest/developerguide/monitoring-keys-determining-usage.html#examine-last-usage:~:text=Tracked%20cryptographic%20operations
:::

## コンソールで最終使用状況を確認する

KMSコンソールのキー詳細ページから、最終使用状況が一目で確認できます。

![](/images/SCR-20260511-iskb.png)
*KMSキー詳細ページ - 最終暗号化操作の情報（操作タイプ・タイムスタンプ・CloudTrail EventIDが表示される）*

![](/images/SCR-20260511-iujl.png)
*一度も使用されていないキーでは最終使用情報が空欄になる*

AWS CLI から `GetKeyLastUsage` APIで同様の情報を取得することもできます。

```bash
aws kms get-key-last-usage --key-id "1234abcd-12ab-34cd-56ef-1234567890ab"
```

使用履歴があるキーのレスポンス例：

```json
{
    "KeyCreationDate": 1773253425.56,
    "KeyId": "1234abcd-12ab-34cd-56ef-1234567890ab",
    "TrackingStartDate": 1773253425.56,
    "KeyLastUsage": {
        "Timestamp": 1773253497.0,
        "Operation": "Encrypt",
        "KmsRequestId": "040cce3e-9ef3-4651-b8cf-e47c9bafdc9b",
        "CloudTrailEventId": "2cfd5892-ea8c-4342-ad49-4b9594b06a8b"
    }
}
```

一度も使用されていないキーでは `KeyLastUsage` フィールドが空のオブジェクト `{}` になります。

:::message alert
`TrackingStartDate`（追跡開始日）より前に作成されたキーは、それ以前の使用履歴が記録されていません。`KeyLastUsage` が空であっても、追跡開始前に使用されていた可能性があります。確実に使用状況を把握するには、CloudTrailの過去ログも合わせて確認することを推奨します。

なお、今回のアップデート（2026年4月）以前に作成されたKMSキーは、コンソール上で `TrackingStartDate` が一律 **2026年4月23日** として表示されるようです。この日付より前の使用履歴はトラッキングの対象外となるため、古くから存在するキーについては特に CloudTrail ログでの補完確認を推奨します。
:::

## kms:TrailingDaysWithoutKeyUsage 条件キーとは

`kms:TrailingDaysWithoutKeyUsage` は、**KMSキーが最後に暗号化操作を実行してから経過した日数**を表す条件キーです。

https://docs.aws.amazon.com/kms/latest/developerguide/conditions-kms.html#conditions-kms-trailing-days-without-key-usage

### 値の計算ロジック

| 状況 | 計算式 |
|---|---|
| 追跡開始後に使用されたキー | `現在日付 - 最終使用日` |
| 追跡開始後に作成され、未使用のキー | `現在日付 - キー作成日` |
| 追跡開始前に作成され、追跡開始後も未使用 | `現在日付 - TrackingStartDate` |

:::message
値は常に**切り捨て**られます（例：29.9日 → 29として評価）。
:::

### 使用できる操作

この条件キーは以下の操作に対してのみ使用できます。

- `kms:ScheduleKeyDeletion`
- `kms:DisableKey`

## SCP の設定

### ポリシーの考え方

今回構成するSCPは「**X日以内に使用されたKMSキーの削除・無効化を組織全体で拒否する**」というものです。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ProtectActivelyUsedKMSKeys",
      "Effect": "Deny",
      "Action": [
        "kms:ScheduleKeyDeletion",
        "kms:DisableKey"
      ],
      "Resource": "*",
      "Condition": {
        "NumericLessThanEquals": {
          "kms:TrailingDaysWithoutKeyUsage": "30"
        }
      }
    }
  ]
}
```

`kms:TrailingDaysWithoutKeyUsage` が `30` 以下（= 過去30日以内に使用されたキー）の場合に `ScheduleKeyDeletion` と `DisableKey` を拒否するポリシーです。

:::message alert
SCPの `Deny` は最優先です。`AdministratorAccess` 権限を持つユーザーであっても、このSCPが適用されているOU配下のアカウントでは削除・無効化操作がブロックされます。
:::

## やってみた

4つのKMSキーを用意し、SCPによる保護の動作を確認します。

### 検証環境

| 項目 | 詳細 |
|---|---|
| SCPの条件 | `NumericLessThanEquals: 2`（2日以内に使用されたキーを拒否） |
| キー1 | 追跡開始日（2026/4/23）から一度も使用したことのないKMSキー |
| キー2 | 検証直前にEncrypt操作を実行したKMSキー |
| キー3 | 検証4日前にDecrypt操作を実行したKMSキー |
| キー4 | 検証直前に作成し一度も使用したことのないKMSキー |

### 検証1：一度も使用されていないキーへの無効化の試行

キー1は追跡開始日（2026年4月23日）以来一度も使用されていません。

ドキュメントの計算ロジックによると、「追跡開始前に作成され、追跡開始後も未使用」のキーは `現在日付 - TrackingStartDate` で計算されます。

```
現在日付（2026/5/11）- TrackingStartDate（2026/4/23）= 18日
```

SCPの条件 `NumericLessThanEquals: 2` に対して **18 > 2** のため、Denyにマッチせず**無効化が許可**されます。

![](/images/SCR-20260511-izoh.png)
*キー1 - SCPによるブロックなしで無効化が成功*

### 検証2：直近使用されたキーへの無効化の試行

キー2は検証直前にEncrypt操作を実行したキーです。  
`kms:TrailingDaysWithoutKeyUsage = 0`（今日使用）となり、SCPの条件 `NumericLessThanEquals: 2` にマッチするため**Denyが適用**されます。

```
DisableKey リクエストが失敗しました
AccessDeniedException - User: arn:aws:sts::XXXXXXXXXXXX:assumed-role/rolename is not authorized to perform: kms:DisableKey on resource: arn:aws:kms:ap-northeast-1:XXXXXXXXXXXX:key/key-id with an explicit deny in a service control policy: arn:aws:organizations::YYYYYYYYYYYY:policy/o-aaabbbccc/service_control_policy/p-0xn1knc2
```

![](/images/SCR-20260511-jama.png)
*キー2 - SCPによる拒否エラー（直近使用されたキーが確実に保護される）*

### 検証3：数日前に使用されたキーへの削除試行

キー3は4日前にDecrypt操作を実行したキーです。`kms:TrailingDaysWithoutKeyUsage = 4`。SCPの条件 `NumericLessThanEquals: 2` に対して **4 > 2** のため、Denyにマッチせず**無効化が許可**されます。

![](/images/SCR-20260511-jcfd.png)
*キー3 - SCPによるブロックなしで無効化が成功*

### 検証4：直前に作成した未使用キーへの無効化の試行

キー4は検証直前に作成したばかりで、一度も暗号化操作を行っていないキーです。

ドキュメントの計算ロジックによると、「追跡開始後に作成され、未使用のキー」は `現在日付 - キー作成日` で計算されます。今日作成したキーは経過日数が `0` となります。

キー1（追跡開始前から存在する未使用キー）とは異なり、`TrackingStartDate` ではなく**キー作成日が起点**になる点がポイントです。

SCPの条件 `NumericLessThanEquals: 2` に対して **0 ≤ 2** のため、Denyにマッチし**無効化が拒否**されます。

```
DisableKey リクエストが失敗しました
AccessDeniedException - User: arn:aws:sts::XXXXXXXXXXXX:assumed-role/rolename is not authorized to perform: kms:DisableKey on resource: arn:aws:kms:ap-northeast-1:XXXXXXXXXXXX:key/key-id with an explicit deny in a service control policy: arn:aws:organizations::YYYYYYYYYYYY:policy/o-aaabbbccc/service_control_policy/p-0xn1knc2
```

![](/images/SCR-20260511-jhfw.png)
*キー4 - 作成直後の未使用キーもSCPによりブロック*

### 検証結果まとめ

| キー | 最終使用 | TrailingDaysWithoutKeyUsage | SCPの動作 |
|---|---|---|---|
| キー1（追跡前作成・未使用） | なし（TrackingStartDateから18日経過） | 18 | ✅ 無効可能 |
| キー2（直近使用） | 今日 Encrypt | 0 | ❌ 無効拒否 |
| キー3（4日前使用） | 4日前 Decrypt | 4 | ✅ 無効可能 |
| キー4（追跡後作成・未使用） | なし（作成0日目） | 0 | ❌ 無効拒否 |

**直近2日以内に使用されたキー2と、作成直後の未使用キー4がSCPによって保護**されることを確認できました。

注目すべきはキー1とキー4の違いです。どちらも「未使用」ですが、`TrailingDaysWithoutKeyUsage` の計算起点が異なります。キー1はアップデート前から存在するため `TrackingStartDate`（2026年4月23日）が起点となり18日が経過しているのに対し、キー4は今日作成のため起点がキー作成日となり経過日数は0日です。この違いにより、保護の有無が分かれる結果となりました。

## 運用上の注意点

### 作成直後の不要なキーも削除できなくなる

`kms:TrailingDaysWithoutKeyUsage` は未使用キーでも作成日からの経過日数で評価されます。  
テスト目的で作成したキーをすぐ削除したい場合でも、設定した日数以内はSCPによりブロックされます。  
テスト・開発用OUにはSCPを適用しない、または除外条件を設けることを検討してください。

### 閾値の選定について

サービスによってはKMSの暗号化操作を頻繁に呼び出さないケースがあります。  
たとえば、Amazon EBSはボリュームがEC2インスタンスにアタッチされるタイミングでのみ `Decrypt` を呼び出します。  
本番環境への適用前に、組織のワークロード特性に合わせた閾値を検討することを推奨します。

## まとめ

2026年4月のアップデートにより、KMSキーの最終使用状況がコンソールやAPIから簡単に確認できるようになりました。これだけでも未使用キーの特定やクリーンアップの判断が格段に楽になります。

さらに `kms:TrailingDaysWithoutKeyUsage` 条件キーをSCPと組み合わせることで、**使用中のKMSキーを組織全体で誤削除から守るガードレール**を設定できます。

KMSキーが削除されると、そのキーで暗号化されたデータは**永続的に復元不可能**になります。今回紹介したSCPは、そのような取り返しのつかない事故を防ぐための有効な一手です。ぜひ組織のセキュリティポリシーに組み込むことを検討してみてください。

この記事がどなたかの役に立つと嬉しいです。
