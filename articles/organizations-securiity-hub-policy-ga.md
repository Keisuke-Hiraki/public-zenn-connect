---
title: "Organizations に新しいポリシー「Security Hub ポリシー」が追加されていたので試してみる"
emoji: "🛡️"
type: "tech"
topics: ["aws", "organizations", "securityhub"]
published: true
publication_name: cscloud_blog
published_at: 2025-07-03 07:00
---
こんにちは、CSC の平木です！

みなさん、Organizations のポリシーは活用してますか？

今回、Organizations に新しいポリシー「Security Hub ポリシー」が追加されていたので、何ができるのか検証し解説します。

## 3 行まとめ

- Security Hub CSPM ではなく Security Hub を中央集権管理するもの
- 「リージョンを指定/すべてのリージョン」において「すべてのアカウント/対象の OU 配下のアカウント」の Security Hub を一括で有効化・無効化できる
- 中央設定とは別物なので注意

## Security Hub ポリシーとは

AWS Organizations と連携し、組織全体の Security Hub の設定を一元的に管理・強制できる仕組みです。
管理アカウントまたは委任管理者がポリシーを定義し、組織や OU（組織単位）に適用することで、全アカウントに一貫したセキュリティ基準を自動的に適用できます。

https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_security_hub.html

:::message alert
注意事項
AWS Security Hub の有効化または無効化を強制させる作用が働くのであって、
Security Hub CSPM には適用されないのでご注意ください。
:::

## 主な特徴・メリット

- 組織全体・複数リージョンで Security Hub を一元管理
- 新規アカウント追加時も自動でポリシー適用される
- OU ごとに柔軟な設定が可能
- メンバーアカウントによる設定変更を防止
- 親ポリシー・子ポリシーの継承で細やかな制御

## 中央設定との違い

AWS Security Hub CSPM という呼称になる前は、
中央設定により、Organizations 配下の AWS アカウントをまとめて中央集権的に管理できました。

Security Hub が Security Hub と Security Hub CSPM に分離したことにより、
Security Hub CSPM は中央設定で管理し、Security Hub は Security Hub ポリシーにより管理する形となります。

詳しいことはまた次の記事で触れていきたいと思います。

## ポリシーの動作・継承

- ポリシーはルート OU や 各 OU にアタッチし、下位アカウントに継承されます。
- 複数のポリシーが適用される場合、下位（アカウントに近い）ポリシーが優先されます。
- `ALL_SUPPORTED`を指定すると、今後追加されるリージョンも自動的にカバーします。
- 有効化・無効化の両方に同じリージョンが指定された場合は「無効化」が優先されます。（IAM ポリシーと同じですね）

## ポリシーの構造

下記は構造の例です。

```json
{
   "securityhub":{
      "enable_in_regions":{
         "@@append  | @@assign | @@remove":[
            "<リージョン名> | ALL_SUPPORTED"
         ]
      },
      "disable_in_regions":{
         "@@append  | @@assign | @@remove":[
            "<リージョン名> | ALL_SUPPORTED"
         ]
      }
   }
}
```

- **securityhub**
    - ポリシー設定のトップレベルコンテナ（決まり文句的なやつ）
- **enable_in_regions**
    - Security Hub を有効化するリージョンのリスト
    - 空の記載でも可
- **disable_in_regions**
    - Security Hub を無効化するリージョンのリスト
    - 空の記載でも可
- **継承演算子（`@@assign`, `@@append`, `@@remove`）**
    - `@@assign`: 親ポリシーの値を上書き
    - `@@append`: 親ポリシーの値に追加
    - `@@remove`: 親ポリシーの値から指定したリージョンを削除

## やってみた

Organizations 内のポリシータブをクリックすると、`Security Hub ポリシー`が追加されていることがわかります。

まずはここをクリックします。

![securityhubpolicy_2025-07-03-18-04-08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/301431fe-2f10-4f02-853b-e9b30ffee197.png)

「Security Hub ポリシーを有効にする」を押すと機能を有効化できます。

![securityhubpolicy_2025-07-03-18-06-46.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/45454d5a-aea7-4a7a-917b-9704de13b6ea.png)

有効化できたらまずサンプルで一個ポリシーを作成していきます。

![securityhubpolicy_2025-07-03-18-07-55.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/b146cda2-4da1-4a11-821c-111d5723b702.png)

サンプルとして以下のようにポリシーを作成してみました。

```json
{
  "securityhub": {
    "enable_in_regions": {
      "@@append": [
        "ap-northeast-3"
      ]
    },
    "disable_in_regions": {
      "@@append": [
        "ap-northeast-1"
      ]
    }
  }
}
```

違いがわかりやすいよう大阪リージョンの設定を有効化し、東京リージョンを無効にしてみます。

![securityhubpolicy_2025-07-03-18-11-24.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/53d86bbb-1c54-4e03-9241-0c18cc434d5c.png)

ポリシーを作成したら OU またはアカウントに割り当てを行う必要があるため、ターゲットから「アタッチ」を押します。

![securityhubpolicy_2025-07-03-18-12-00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/053ec494-c91d-4f6d-ba18-f78a75caaeb5.png)

続いて対象の OU またはアカウントにチェックを入れ、「ポリシーのアタッチ」を選択します。

![securityhubpolicy_2025-07-03-18-14-01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/d81fef09-14b2-4890-aa30-85a3345480d9.png)

これで割り当ては完了です。

実際に対象のアカウント内で見てみると、有効化または無効化を確認でき、それぞれ無効化・有効化してみたら権限エラーが出ていることも確認できました。

![securityhubpolicy_2025-07-03-18-18-12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/92c44cca-1936-4025-8211-3cc66671bdd8.png)

![securityhubpolicy_2025-07-03-18-18-57.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/c3ea381e-55ec-413a-af37-40094f12f31c.png)

![securityhubpolicy_2025-07-03-18-19-42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/cb3e5d49-549c-45c6-93ac-6e953c294ca1.png)

![securityhubpolicy_2025-07-03-18-20-27.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/3feb2bf3-fb05-41e9-b210-d570708c2bae.png)

## おまけ

ポリシーをデタッチした場合、
既存の設定は残るため切り戻したい場合は手動で対応が必要です。

## 参考リンク

- [Security Hub policies - AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_security_hub.html)

## まとめ

今回は、Organizations で新しくできたポリシー「Security Hub ポリシー」について解説しました。

Security Hub が分裂したことにより、今後 Orgaznitions における Security Hub の集約管理も少し変わってきそうです。

ぜひこの機能を活用しガバナンスを強化いただければと思います。

この記事がどなたかの役に立つとうれしいです。

---

この記事は Qiita から移行しました。
