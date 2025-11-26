---
title: "新しく Organizations ポリシーに S3 ポリシーが爆誕しました！"
emoji: "🔍"
type: "tech"
topics: ["aws", "s3", "organizations", "security"]
published: true
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

皆さんは S3 のブロックパブリックアクセスの機能を活用して意図しない S3 公開を防げていますか？

通常、マルチアカウントにおいては SCP を活用し、 `PutPublicAccessBlock` や `PutBucketPublicAccessBlock` の API を Deny することで変更不可とさせていたかと思います。  
ただ、SCP を本格的に活用しようとするとクォータに引っかかったりそもそも自前でメンテナンスするのも手間がかかります。

そんな中ふとコンソールを見ると、S3 ポリシーという項目が増えていたのでご紹介します。

https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_s3.html

![](/images/organizations-policy-for-s3_2025-11-26-11-29-21.png)

## 3 行まとめ

- アカウントレベルの S3 ブロックパブリックアクセス設定の有効化無効化を強制化できるポリシー
- パブリックアクセスを制御する、`BlockPublicAcls`・`BlockPublicPolicy`・`IgnorePublicAcls`・`RestrictPublicBuckets`の 4 つ全てを有効にするか全てを無効にするかのいずれかを選択可能
- デタッチすると元の設定に戻る

## S3 ポリシーとは

S3 ポリシーは、AWS Organizations を使用して複数のメンバーアカウントにわたって S3 ブロックパブリックアクセスの設定を一元管理できる機能です。

S3 ポリシーを活用することで、今まで SCP で管理していたアクションを S3 ポリシーという形でマネージドに Organizations 全体で適用できます。

## S3 ポリシーの記法について

S3 ポリシーは GUI で指定もできますが JSON でも指定が可能です。

S3 ポリシーの大枠の構造としては以下のようになります。

```json
{
    "s3_attributes": {
        "public_access_block_configuration": {
            "@@assign": "all"
        }
    }
}
```

それぞれ上のレイヤーから見ていきます。

- s3_attributes
  - S3 ポリシーを扱う上でのドキュメントの最上位キーであり、S3 ポリシーのドキュメントだという宣言になります
- public_access_block_configuration
  - 組織全体で S3 のブロックパブリックアクセスを有効化する方法を定義します
- 継承演算子
  - 有効化または無効化を行うのか、子 OU に上書きを許可させるのかなどを指定できます
  - [継承演算子 - AWS Organizations](https://docs.aws.amazon.com/ja_jp/organizations/latest/userguide/policy-operators.html)
  - `@@assign` では、`all` または `none` のいずれかのみ選択できます
    - `all`: 組織レベルで 4 つの S3 ブロックパブリックアクセス設定をすべて有効にします
    - `none`: 組織レベルの制御を無効にし、個々のアカウントが独自のブロックパブリックアクセス設定を管理できるようにします

`all` で記載している 4 つの S3 ブロックパブリックアクセスの設定は以下 4 つを指します。

| 項目 | 内容 |
|---|---|
| BlockPublicAcls | 新しいパブリック ACL の付与をブロックします |
| BlockPublicPolicy | バケットまたはアクセスポイントポリシーを使用してパブリックアクセスを許可することをブロックします |
| IgnorePublicAcls | パブリックアクセスを許可する全ての ACL を無視します |
| RestrictPublicBuckets | パブリックアクセスを許可するポリシーを持つバケットまたはアクセスポイントのパブリックアクセスとクロスアカウントアクセスを無視します |

### 子 OU でポリシーの上書きを禁止にしたい場合

```json
{
    "s3_attributes": {
        "public_access_block_configuration": {
            "@@assign": "all",
            "@@operators_allowed_for_child_policies": ["@@none"]
        }
    }
}
```

## S3 ポリシーの有効化方法と使い方

S3 ポリシーの有効化とポリシー作成の手順について記載します。

まず Organizations からポリシーをナビゲーションペインで選択し、「S3 ポリシー」を押します。

![](/images/organizations-policy-for-s3_2025-11-26-11-55-02.png)

続いて、「S3 ポリシーを有効にする」を押します。

![](/images/organizations-policy-for-s3_2025-11-26-11-55-28.png)

「有効になりました」と表記されたら完了です。

![](/images/organizations-policy-for-s3_2025-11-26-11-56-03.png)

ポリシーを作成したい場合は、「ポリシーを作成」を押します。

上部では任意のポリシー名、説明、タグを指定します。

![](/images/organizations-policy-for-s3_2025-11-26-11-56-50.png)

GUI で設定したい場合はデフォルトのまま、「すべてのパブリックアクセスをブロック」にチェックを入れ、「ポリシーを作成」を押します。

![](/images/organizations-policy-for-s3_2025-11-26-12-00-43.png)

JSON エディタで設定したい場合は、JSON エディタのタブを押し、任意のポリシーを上書きし、「ポリシーを作成」を押します。

作成したポリシーはターゲットのタブから「アタッチ」を押し、任意の OU を選択するとアタッチできます。

![](/images/organizations-policy-for-s3_2025-11-26-12-02-09.png)

## まとめ

今回は S3 ポリシーについてご紹介しました。

re:Invent が近づくにつれ、Organizations ポリシーが一気に増え、今後の統制は Organizations ポリシーが主軸になっていくのかな？と思えてきました。

n 回目になりますが、IAM Access Analyzer にもこの機能の実装を…

この記事がどなたかの役に立つと嬉しいです。