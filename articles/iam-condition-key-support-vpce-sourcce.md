---
title: "VPCエンドポイント系のポリシーの新しい条件キーによりVPCエンドポイントからの通信を制約しやすくなったので見てみた"
emoji: "🔑"
type: "tech"
topics: ["aws", "iam", "vpc"]
published: true
publication_name: cscloud_blog
published_at: 2025-08-30 07:00
---
こんにちは、CSC の平木です！

今回は、ポリシーを記述する際に使用するグローバル条件キーに新しく 3 つ

- `aws:VpceAccount`
- `aws:VpceOrgPaths`
- `aws:VpceOrgID`

が追加されたとのことでこれらを紹介します。

これらの新しい条件キーにより、VPC エンドポイントからのアクセス制御が、これまでよりもシンプルかつ大規模に管理可能となったのでそれぞれ見ていきます。

https://aws.amazon.com/about-aws/whats-new/2025/08/aws-iam-new-vpc-endpoint-condition-keys/

## 新しい条件キーで何ができるようになったか？

これまで VPC エンドポイント経由のアクセスを制御するには、個々の VPC エンドポイント ID を指定する必要がありました。
しかし、今回追加された新しい条件キーを使えば、VPC エンドポイントの「所有者」に基づいてアクセスを制限できるようになります。

それぞれの条件キーを見ていきましょう。

### aws:VpceAccount

このキーを使うと、特定の AWS アカウントが所有する VPC エンドポイントからのアクセスに制限をかけられます。
例えば、「この S3 バケットには、特定の開発アカウントの VPC エンドポイントからしかアクセスさせない」といった制御が可能で、VPC エンドポイント ID を 1 つ 1 つ指定する必要がなく、ポリシーのサイズも小さくでき、管理も楽になります。

#### サンプル

こちらの例は、特定のパートナーアカウントからの S3 読み取りアクセスを許可を与える場合のバケットポリシーです。

```json:バケットポリシー
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AccessToSpecificVpceAccountOnly",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::amzn-s3-demo-bucket1/*",
      "Condition": {
        "ForAnyValue:StringEquals": {
          "aws:VpceAccount": [
            "111122223333",
            "444455556666"
          ]
        }
      }
    }
  ]
}
```

![keisuke-poc2025-08-30-13-27-22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/f526c319-8af8-46a1-8bf2-ac8f2fb91c9d.png)

### aws:VpceOrgPaths

AWS Organizations を使っている場合、特定の組織単位（OU）パスに属する VPC エンドポイントからのアクセスに限定できます。
例えば、「本番環境の OU にある VPC エンドポイントからのみ、この S3 バケットにアクセスを許可する」といった、組織構造に基づいたきめ細かいアクセス制御が可能になります。

#### サンプル

こちらの例は、本番 OU 外またはテストサブ OU からの S3 書き込みアクセスを拒否する場合のバケットポリシーです。

```json:バケットポリシー
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccessFromSpecificOrgPaths",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::amzn-s3-demo-bucket1/*",
      "Condition": {
        "StringNotLike": {
          "aws:VpceOrgPaths": "o-xxxxxxxxxx/r-abcd/ou-prod-path/*"
        },
        "StringLike": {
          "aws:VpceOrgPaths": "o-xxxxxxxxxx/r-abcd/ou-prod-path/ou-test-sub-path/*"
        }
      }
    }
  ]
}
```

![keisuke-poc2025-08-30-13-53-10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/21d3864a-d562-4f74-b99a-fa5135165b26.png)

### aws:VpceOrgID

組織全体で一貫したセキュリティポリシーを適用したい場合に役立つのがこのキーです。
特定の AWS Organization に属する VPC エンドポイントからのアクセスのみを許可できます。
これにより、中央のセキュリティチームが組織全体のアクセス制御を強化し、意図しない外部からのアクセスを防ぐことができます。

#### サンプル

こちらの例は、組織の VPC エンドポイント外かつ特定のプロジェクトタグを持たないプリンシパルからの S3 アクセスを拒否する RCP です。

```json:RCP
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnforceNetworkPerimeterVpceOrgID",
      "Effect": "Deny",
      "Principal": "*",
      "Action": [
        "s3:*",
        "kms:*"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:PrincipalIsAWSService": "false",
          "aws:ViaAWSService": "false"
        },
        "StringNotEqualsIfExists": {
          "aws:VpceOrgID": "o-abcdef0123",
          "aws:PrincipalTag/network-perimeter-exception": "true"
        }
      }
    }
  ]
}
```

![keisuke-poc2025-08-30-14-22-22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/d472c4eb-92eb-456e-a3df-7c9eef54a85b.png)

## 新しい条件キーのメリット

以前は、VPC エンドポイント経由のアクセス制御は、`aws:SourceVpc`や`aws:SourceVpce`で個別の VPC ID や VPC エンドポイント ID をポリシーに列挙する必要がありました。
組織の拡大や VPC ・ VPC エンドポイントの増加に伴い、管理は煩雑化しました。これにより、設定ミスや設定もれも発生しやすくなります。

**以前のポリシー例（イメージ）**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-sensitive-bucket",
        "arn:aws:s3:::my-sensitive-bucket/*"
      ],
      "Condition": {
        "StringNotEquals": {
          "aws:SourceVpce": [
            "vpce-0123456789abcdef0",
            "vpce-fedcba9876543210f",
            "vpce-abcdef01234567890"
          ]
        }
      }
    }
  ]
}
```
↑こんな感じで、VPC エンドポイントが増えるたびにバケットポリシーを更新する必要がありました。

**新しい条件キーを使ったポリシー例（イメージ）**

新しい条件キーを使えば、こんなにシンプルになります。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-sensitive-bucket",
        "arn:aws:s3:::my-sensitive-bucket/*"
      ],
      "Condition": {
        "StringNotEquals": {
          "aws:VpceOrgID": "o-xxxxxxxxxx"
        }
      }
    }
  ]
}
```
↑組織 ID を指定するだけで、その組織内の VPC エンドポイントからのアクセスに限定できます。
ポリシーもスッキリし、管理も容易になります。

### 新しい条件キーのメリットまとめ

- スケーラビリティの向上：個々の VPC エンドポイント ID を列挙する必要がなくなり、大規模な環境でもポリシー管理が容易になります。
- 運用オーバーヘッドの削減：ポリシーの更新頻度が減り、管理者の負担が軽減されます。
- IAM ポリシーの簡素化：より読みやすく、理解しやすいポリシーを作成可能になります。
- ネットワーク境界制御の強化：組織や OU に基づいた、より堅牢なアクセス制御を実現します。

## 注意事項

これらの条件キーは現在時点（2025/08/30）、以下のサービスでサポートされています。

- AWS App Runner
- AWS Application Discovery Service
- AWS Cloud Map
- AWS CloudFormation
- AWS Compute Optimizer Console
- AWS DataSync
- AWS HealthImaging
- AWS HealthLake
- AWS HealthOmics
- AWS Identity and Access Management (except for the iam:PassRole action)
- AWS IoT FleetWise
- AWS IoT Wireless
- AWS Key Management Service
- AWS Lambda
- AWS Payment Cryptography
- AWS Private Certificate Authority
- AWS Recycle Bin
- AWS Storage Gateway
- AWS Systems Manager Incident Manager Contacts
- AWS Transfer Family
- Amazon Athena
- Amazon CloudWatch Application Insights
- Amazon Comprehend Medical
- Amazon Data Firehose
- Amazon Elastic Block Store
- Amazon EventBridge Scheduler
- Amazon Polly
- Amazon Rekognition
- Amazon Simple Storage Service
- Amazon Textract
- Amazon Transcribe
- Service Quotas

:::message alert
このキーをサポートされていないサービスで使用すると、意図しない認証が発生する可能性があります
:::

## 参考

https://aws.amazon.com/blogs/security/use-scalable-controls-to-help-prevent-access-from-unexpected-networks/

https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-network-properties

## おわりに

今回追加された`aws:VpceAccount`、`aws:VpceOrgPaths`、`aws:VpceOrgID`という新しい IAM 条件キーは、VPC エンドポイントを利用したアクセス制御を劇的に改善します。特に大規模な AWS 環境を運用している組織にとっては、セキュリティと運用の両面で大きなメリットをもたらします。

これらの新しい条件キーを活用することで、よりセキュアで管理しやすいポリシーを設計できます。

この記事がどなたかの役に立つと嬉しいです。

---

この記事は Qiita から移行しました。
