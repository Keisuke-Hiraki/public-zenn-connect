---
title: "Security Hub CSPM に金融業界向けのセキュリティ基準「CRI Profile v2.2」が追加されました"
emoji: "🏦"
type: "tech"
topics: ["aws", "securityhub", "security"]
published: true
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

皆さんは Security Hub CSPM のセキュリティ基準を何種類有効化していますか？

AWS 基礎セキュリティのベストプラクティス（FSBP）や CIS AWS Foundations Benchmark を有効化している方は多いと思いますが、2026 年 10 月 14 日に Security Hub CSPM へ新しいセキュリティ基準 **CRI Profile v2.2** が追加されました。

https://docs.aws.amazon.com/securityhub/latest/userguide/doc-history.html

そもそも CRI Profile とは何なのか、Security Hub CSPM でどのコントロールが対象になるのかを整理してみました。

:::message
この記事の 3 行まとめ

- CRI Profile は、金融機関の業界団体 Cyber Risk Institute（CRI）が作成した、金融業界向けのサイバーリスク管理フレームワークで、v2.2 は NIST CSF 2.0 に準拠しています
- Security Hub CSPM の CRI Profile v2.2 標準には **404 個** のコントロールが含まれ、そのうち 88 個は FSBP には含まれないコントロールです
- 対象は自動チェックできる要件だけなので、PCI DSS 標準と同じく、すべてのチェックに合格しても CRI Profile への準拠が証明されるわけではありません
:::

## CRI Profile とは

Security Hub CSPM の話に入る前に、CRI Profile そのものが何なのかを整理します。

### Cyber Risk Institute（CRI）が作った金融業界向けフレームワーク

CRI Profile は、金融機関や業界団体で構成される非営利の連合体 **Cyber Risk Institute（CRI）** が開発したサイバーセキュリティフレームワークです。

https://cyberriskinstitute.org/cri-profile-overview/

金融機関は、各国・各地域の金融規制当局からさまざまなサイバーセキュリティ要件を求められます。
規制ごとに個別に自己評価をしていると、似たような内容を何度も評価・報告することになり、大きな負担になります。

CRI Profile はこうした規制当局の要求事項や業界標準を共通の要件セットにまとめたもので、**一度の評価で複数の規制に対する報告に活用できる** ことを目的としています。

### CRI Profile v2.2 の特徴

CRI の公式サイトに記載されている v2.2 の主な特徴をまとめます。

| 項目 | 内容 |
| --- | --- |
| ベース | NIST サイバーセキュリティフレームワーク（CSF）2.0 |
| 要件の数 | 318 個のコントロール目標（「診断ステートメント」と呼ばれる） |
| マッピング | NIST SP 800-53 Rev.5、DORA（EU デジタル・オペレーショナル・レジリエンス法）、MITRE ATT&CK など約 40 の規制・業界標準 |
| 評価方法 | 最初に 9 つの質問に答えて組織の影響度（Impact Tier）を決め、Tier に応じて回答すべき診断ステートメントを絞り込む |

NIST CSF 2.0 がベースになっているため、要件は CSF の 6 つの機能（GV: 統治、ID: 識別、PR: 防御、DE: 検知、RS: 対応、RC: 復旧）に沿って整理されています。
診断ステートメントの ID も `PR.AA-02.01` のように、CSF のカテゴリ（この例では PR.AA: アイデンティティ管理、認証、アクセス制御）に枝番を付けた形式になっています。

CRI の公式サイトによると、広く使われている他の評価手法と比べて、影響度の高い組織（Tier 1）でも評価の質問数を 36%、影響度の低い組織（Tier 4）では 58% 削減できるとされています。

:::message
日本の金融機関では FISC 安全対策基準や金融庁の「金融分野におけるサイバーセキュリティに関するガイドライン」が主に参照されますが、CRI Profile は米国を中心にグローバルで利用されています。海外拠点を持つ金融機関や、海外の金融機関と取引がある事業者にとっては、Security Hub CSPM 上で CRI Profile のコントロール観点を確認できるのは便利だと思います。
:::

## Security Hub CSPM の CRI Profile v2.2 標準

このセクションでは、Security Hub CSPM に追加された CRI Profile v2.2 標準の位置づけと注意点を紹介します。

https://docs.aws.amazon.com/securityhub/latest/userguide/standards-reference-cri-profile.html

### 自動チェックできる要件のみが対象

このセクションでは、この標準でカバーされる範囲を確認します。

ドキュメントでは、カバー範囲について以下のように説明されています。

> AWS Security Hub CSPM provides security controls that support a subset of CRI Profile v2.2 requirements. (中略) Note that the controls don't support CRI Profile v2.2 requirements that require manual checks.

つまり、Security Hub CSPM がチェックするのは CRI Profile の要件のうち **AWS リソースの設定から自動で判定できるもの** だけで、手動での確認が必要な要件は対象外です。

あわせて、標準を有効化してチェックに合格しても、それだけで CRI Profile v2.2 への準拠を確立・証明するものではない、とも明記されています。

> Enabling this standard, and passing the checks for its controls, doesn't by itself establish or certify compliance with CRI Profile v2.2.

:::message alert
「Security Hub CSPM の CRI Profile 標準のスコアが 100% だから CRI Profile に準拠している」とは言えない点に注意してください。PCI DSS 標準と同じく、公式な監査に加えて、ガバナンス（GV）や対応手順といった組織・運用面の要件は別途評価が必要です。
:::

### findings には CRI Profile の診断ステートメント ID が入っていた

実際に有効化した環境で生成された findings の中身を確認します。

検証環境で CRI Profile v2.2 標準を有効化し、生成された findings を見てみると、`Compliance.RelatedRequirements` に CRI Profile の診断ステートメント ID が入っていました。いくつか抜粋すると以下のとおりです。

| コントロール ID | 関連する CRI Profile の診断ステートメント |
| --- | --- |
| Account.2 | ID.AM-08.02 |
| CloudTrail.3 | DE.AE-02.01, DE.AE-03.01, DE.AE-03.02, PR.PS-01.01, PR.PS-04.02, PR.PS-04.03, RS.AN-07.01 |
| CloudWatch.16 | ID.AM-08.03, ID.AM-08.05, PR.PS-04.01, PR.PS-04.03 |
| DynamoDB.4 | PR.DS-11.01 |
| IAM.19 | PR.AA-02.01, PR.AA-03.01, PR.AA-05.02 |
| S3.14 | PR.AA-05.01, PR.DS-01.01, PR.IR-03.01, PR.PS-01.03 |

findings の JSON では以下のように `CRI Profile v2.2/` というプレフィックス付きで格納されています。

```json
"Compliance": {
    "Status": "FAILED",
    "RelatedRequirements": [
        "CRI Profile v2.2/PR.AA-02.01",
        "CRI Profile v2.2/PR.AA-03.01",
        "CRI Profile v2.2/PR.AA-05.02"
    ],
    "SecurityControlId": "IAM.19",
    "AssociatedStandards": [
        {
            "StandardsId": "standards/cri-profile/v/2.2.0"
        }
    ]
}
```

CloudTrail.3 のように 1 つのコントロールが 7 つの診断ステートメントに紐づいているものもありました。監査対応で「この診断ステートメントに関係する AWS 側の設定はどうなっているか」を聞かれたときは、`RelatedRequirements` で findings を絞り込むと当たりをつけやすそうです。

## 対象のコントロール

続いて、CRI Profile v2.2 標準に含まれるコントロールの傾向と一覧を紹介します。

### 重要度とサービスの内訳

`list-security-control-definitions` で確認したところ、CRI Profile v2.2 標準には 404 個のコントロールが含まれていました。

| 重要度 | コントロール数 |
| --- | --- |
| 重大（CRITICAL） | 29 |
| 高（HIGH） | 64 |
| 中（MEDIUM） | 231 |
| 低（LOW） | 80 |
| 合計 | 404 |

対象サービスは 69 種類で、コントロール数の多いサービスは以下のとおりです。

| サービス | コントロール数 |
| --- | --- |
| Amazon EC2 | 36 |
| Amazon RDS | 35 |
| IAM | 24 |
| Amazon S3 | 20 |
| Elastic Load Balancing | 18 |
| Amazon CloudWatch | 17 |
| Amazon CloudFront | 12 |
| Amazon Redshift | 11 |
| AWS WAF | 10 |
| Amazon OpenSearch Service | 10 |
| Amazon GuardDuty | 10 |
| Amazon ECS | 10 |

### FSBP との比較

このセクションでは、多くの環境で有効化されている FSBP と比べて、CRI Profile v2.2 標準のコントロールがどう違うのかを整理します。

| 項目 | コントロール数 |
| --- | --- |
| CRI Profile v2.2 と FSBP の両方に含まれる | 316 |
| CRI Profile v2.2 のみに含まれる | 88 |
| FSBP の総コントロール数（参考） | 371 |

CRI Profile v2.2 のみに含まれる 88 個のコントロールを眺めてみると、まず目につくのは CIS AWS Foundations Benchmark でおなじみの監視・IAM 系のコントロールです。

- CloudWatch.1 〜 14: root ユーザーの利用、不正な API 呼び出し、IAM ポリシー変更などを検知するメトリクスフィルターとアラーム
- IAM.9 〜 IAM.19、IAM.22、IAM.26 〜 IAM.28: パスワードポリシーの文字種や長さ、MFA、未使用の認証情報や期限切れ証明書の削除、IAM Access Analyzer の有効化

残りは、データの保護や復元性に関するものが中心でした。

- S3.7、S3.14、S3.15、S3.20、S3.22、S3.23 など: クロスリージョンレプリケーション、バージョニング、Object Lock、MFA 削除、オブジェクトレベルのログ
- DynamoDB.4、EC2.28、RDS.26 など: AWS Backup のバックアッププランへの登録
- MQ.5、MQ.6、Neptune.9、NetworkFirewall.1、Redshift.16 など: マルチ AZ 構成

このほか、Amplify.2 や EC2.174 といったリソースのタグ付け（資産管理の観点と思われます）、Account.2（AWS Organizations への所属）、KMS.4（KMS キーのローテーション）、ELB.16（ALB への WAF の関連付け）なども含まれています。

ざっくり言うと、**FSBP に CIS AWS Foundations Benchmark の監視・IAM 系コントロールと、バックアップやマルチ AZ といった復元性のコントロールを足したような構成** です。DORA のようなオペレーショナル・レジリエンスの規制にマッピングしているフレームワークなので、復元性のコントロールが多いのは納得感があります。

### コントロール一覧

CRI Profile v2.2 標準に含まれる 404 個のコントロールの一覧です。数が多いためアコーディオンに格納しています。
「FSBP にも含まれる」列が `-` のものが、CRI Profile v2.2 標準のみに含まれるコントロールです。

:::details コントロール一覧（404 個）
| コントロール ID | タイトル | 重要度 | FSBP にも含まれる |
| --- | --- | --- | --- |
| [Account.1](https://docs.aws.amazon.com/securityhub/latest/userguide/account-controls.html#account-1) | Security contact information should be provided for an AWS account. | 中 | ○ |
| [Account.2](https://docs.aws.amazon.com/securityhub/latest/userguide/account-controls.html#account-2) | AWS account should be part of an AWS Organizations organization | 高 | - |
| [ACM.1](https://docs.aws.amazon.com/securityhub/latest/userguide/acm-controls.html#acm-1) | Imported and ACM-issued certificates should be renewed after a specified time period | 中 | ○ |
| [ACM.2](https://docs.aws.amazon.com/securityhub/latest/userguide/acm-controls.html#acm-2) | RSA certificates managed by ACM should use a key length of at least 2,048 bits | 高 | ○ |
| [Amplify.2](https://docs.aws.amazon.com/securityhub/latest/userguide/amplify-controls.html#amplify-2) | Amplify branches should be tagged | 低 | - |
| [APIGateway.1](https://docs.aws.amazon.com/securityhub/latest/userguide/apigateway-controls.html#apigateway-1) | API Gateway REST and WebSocket API execution logging should be enabled | 中 | ○ |
| [APIGateway.2](https://docs.aws.amazon.com/securityhub/latest/userguide/apigateway-controls.html#apigateway-2) | API Gateway REST API stages should be configured to use SSL certificates for backend authentication | 中 | ○ |
| [APIGateway.3](https://docs.aws.amazon.com/securityhub/latest/userguide/apigateway-controls.html#apigateway-3) | API Gateway REST API stages should have AWS X-Ray tracing enabled | 低 | ○ |
| [APIGateway.4](https://docs.aws.amazon.com/securityhub/latest/userguide/apigateway-controls.html#apigateway-4) | API Gateway should be associated with a WAF Web ACL | 中 | ○ |
| [APIGateway.5](https://docs.aws.amazon.com/securityhub/latest/userguide/apigateway-controls.html#apigateway-5) | API Gateway REST API cache data should be encrypted at rest | 中 | ○ |
| [APIGateway.8](https://docs.aws.amazon.com/securityhub/latest/userguide/apigateway-controls.html#apigateway-8) | API Gateway routes should specify an authorization type | 中 | ○ |
| [APIGateway.9](https://docs.aws.amazon.com/securityhub/latest/userguide/apigateway-controls.html#apigateway-9) | Access logging should be configured for API Gateway V2 Stages | 中 | ○ |
| [AppFlow.1](https://docs.aws.amazon.com/securityhub/latest/userguide/appflow-controls.html#appflow-1) | Amazon AppFlow flows should be tagged | 低 | - |
| [AppRunner.1](https://docs.aws.amazon.com/securityhub/latest/userguide/apprunner-controls.html#apprunner-1) | App Runner services should be tagged | 低 | - |
| [AppSync.2](https://docs.aws.amazon.com/securityhub/latest/userguide/appsync-controls.html#appsync-2) | AWS AppSync should have field-level logging enabled | 中 | ○ |
| [AppSync.5](https://docs.aws.amazon.com/securityhub/latest/userguide/appsync-controls.html#appsync-5) | AWS AppSync GraphQL APIs should not be authenticated with API keys | 高 | ○ |
| [Athena.4](https://docs.aws.amazon.com/securityhub/latest/userguide/athena-controls.html#athena-4) | Athena workgroups should have logging enabled | 中 | ○ |
| [AutoScaling.1](https://docs.aws.amazon.com/securityhub/latest/userguide/autoscaling-controls.html#autoscaling-1) | Auto scaling groups associated with a load balancer should use ELB health checks | 低 | ○ |
| [AutoScaling.2](https://docs.aws.amazon.com/securityhub/latest/userguide/autoscaling-controls.html#autoscaling-2) | Amazon EC2 Auto Scaling group should cover multiple Availability Zones | 中 | ○ |
| [AutoScaling.3](https://docs.aws.amazon.com/securityhub/latest/userguide/autoscaling-controls.html#autoscaling-3) | Auto Scaling group launch configurations should configure EC2 instances to require Instance Metadata Service Version 2 (IMDSv2) | 高 | ○ |
| [Autoscaling.5](https://docs.aws.amazon.com/securityhub/latest/userguide/autoscaling-controls.html#autoscaling-5) | Amazon EC2 instances launched using Auto Scaling group launch configurations should not have Public IP addresses | 高 | ○ |
| [AutoScaling.6](https://docs.aws.amazon.com/securityhub/latest/userguide/autoscaling-controls.html#autoscaling-6) | Auto Scaling groups should use multiple instance types in multiple Availability Zones | 中 | ○ |
| [AutoScaling.9](https://docs.aws.amazon.com/securityhub/latest/userguide/autoscaling-controls.html#autoscaling-9) | EC2 Auto Scaling groups should use EC2 launch templates | 中 | ○ |
| [Backup.1](https://docs.aws.amazon.com/securityhub/latest/userguide/backup-controls.html#backup-1) | AWS Backup recovery points should be encrypted at rest | 中 | ○ |
| [Batch.2](https://docs.aws.amazon.com/securityhub/latest/userguide/batch-controls.html#batch-2) | Batch scheduling policies should be tagged | 低 | - |
| [Batch.4](https://docs.aws.amazon.com/securityhub/latest/userguide/batch-controls.html#batch-4) | Compute resources properties in managed Batch compute environments should be tagged | 低 | - |
| [CloudFront.1](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-1) | CloudFront distributions should have a default root object configured | 高 | ○ |
| [CloudFront.3](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-3) | CloudFront distributions should require encryption in transit | 中 | ○ |
| [CloudFront.4](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-4) | CloudFront distributions should have origin failover configured | 低 | ○ |
| [CloudFront.5](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-5) | CloudFront distributions should have logging enabled | 中 | ○ |
| [CloudFront.6](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-6) | CloudFront distributions should have WAF enabled | 中 | ○ |
| [CloudFront.7](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-7) | CloudFront distributions should use custom SSL/TLS certificates | 低 | ○ |
| [CloudFront.8](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-8) | CloudFront distributions should use SNI to serve HTTPS requests | 低 | ○ |
| [CloudFront.9](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-9) | CloudFront distributions should encrypt traffic to custom origins | 中 | ○ |
| [CloudFront.10](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-10) | CloudFront distributions should not use deprecated SSL protocols between edge locations and custom origins | 中 | ○ |
| [CloudFront.12](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-12) | CloudFront distributions should not point to non-existent S3 origins | 高 | ○ |
| [CloudFront.13](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-13) | CloudFront distributions should use origin access control | 中 | ○ |
| [CloudFront.15](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudfront-controls.html#cloudfront-15) | CloudFront distributions should use the recommended TLS security policy | 中 | ○ |
| [CloudTrail.1](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudtrail-controls.html#cloudtrail-1) | CloudTrail should be enabled and configured with at least one multi-Region trail that includes read and write management events | 高 | ○ |
| [CloudTrail.2](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudtrail-controls.html#cloudtrail-2) | CloudTrail should have encryption at-rest enabled | 中 | ○ |
| [CloudTrail.3](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudtrail-controls.html#cloudtrail-3) | At least one CloudTrail trail should be enabled | 高 | - |
| [CloudTrail.4](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudtrail-controls.html#cloudtrail-4) | CloudTrail log file validation should be enabled | 低 | ○ |
| [CloudTrail.5](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudtrail-controls.html#cloudtrail-5) | CloudTrail trails should be integrated with Amazon CloudWatch Logs | 中 | ○ |
| [CloudTrail.6](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudtrail-controls.html#cloudtrail-6) | Ensure the S3 bucket used to store CloudTrail logs is not publicly accessible | 重大 | - |
| [CloudTrail.7](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudtrail-controls.html#cloudtrail-7) | Ensure S3 bucket access logging is enabled on the CloudTrail S3 bucket | 低 | - |
| [CloudWatch.1](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-1) | A log metric filter and alarm should exist for usage of the "root" user | 低 | - |
| [CloudWatch.2](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-2) | Ensure a log metric filter and alarm exist for unauthorized API calls | 低 | - |
| [CloudWatch.3](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-3) | Ensure a log metric filter and alarm exist for Management Console sign-in without MFA | 低 | - |
| [CloudWatch.4](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-4) | Ensure a log metric filter and alarm exist for IAM policy changes | 低 | - |
| [CloudWatch.5](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-5) | Ensure a log metric filter and alarm exist for CloudTrail configuration changes | 低 | - |
| [CloudWatch.6](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-6) | Ensure a log metric filter and alarm exist for AWS Management Console authentication failures | 低 | - |
| [CloudWatch.7](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-7) | Ensure a log metric filter and alarm exist for disabling or scheduled deletion of customer created CMKs | 低 | - |
| [CloudWatch.8](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-8) | Ensure a log metric filter and alarm exist for S3 bucket policy changes | 低 | - |
| [CloudWatch.9](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-9) | Ensure a log metric filter and alarm exist for AWS Config configuration changes | 低 | - |
| [CloudWatch.10](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-10) | Ensure a log metric filter and alarm exist for security group changes | 低 | - |
| [CloudWatch.11](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-11) | Ensure a log metric filter and alarm exist for changes to Network Access Control Lists (NACL) | 低 | - |
| [CloudWatch.12](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-12) | Ensure a log metric filter and alarm exist for changes to network gateways | 低 | - |
| [CloudWatch.13](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-13) | Ensure a log metric filter and alarm exist for route table changes | 低 | - |
| [CloudWatch.14](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-14) | Ensure a log metric filter and alarm exist for VPC changes | 低 | - |
| [CloudWatch.15](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-15) | CloudWatch alarms should have specified actions configured | 高 | - |
| [CloudWatch.16](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-16) | CloudWatch log groups should be retained for a specified time period | 中 | - |
| [CloudWatch.17](https://docs.aws.amazon.com/securityhub/latest/userguide/cloudwatch-controls.html#cloudwatch-17) | CloudWatch alarm actions should be enabled | 高 | - |
| [CodeBuild.1](https://docs.aws.amazon.com/securityhub/latest/userguide/codebuild-controls.html#codebuild-1) | CodeBuild Bitbucket source repository URLs should not contain sensitive credentials | 重大 | ○ |
| [CodeBuild.2](https://docs.aws.amazon.com/securityhub/latest/userguide/codebuild-controls.html#codebuild-2) | CodeBuild project environment variables should not contain clear text credentials | 重大 | ○ |
| [CodeBuild.3](https://docs.aws.amazon.com/securityhub/latest/userguide/codebuild-controls.html#codebuild-3) | CodeBuild S3 logs should be encrypted | 低 | ○ |
| [CodeBuild.4](https://docs.aws.amazon.com/securityhub/latest/userguide/codebuild-controls.html#codebuild-4) | CodeBuild project environments should have a logging configuration | 中 | ○ |
| [CodeBuild.7](https://docs.aws.amazon.com/securityhub/latest/userguide/codebuild-controls.html#codebuild-7) | CodeBuild report group exports should be encrypted at rest | 中 | ○ |
| [CodeGuruProfiler.1](https://docs.aws.amazon.com/securityhub/latest/userguide/codeguruprofiler-controls.html#codeguruprofiler-1) | CodeGuru Profiler profiling groups should be tagged | 低 | - |
| [CodeGuruReviewer.1](https://docs.aws.amazon.com/securityhub/latest/userguide/codegurureviewer-controls.html#codegurureviewer-1) | CodeGuru Reviewer repository associations should be tagged | 低 | - |
| [Cognito.2](https://docs.aws.amazon.com/securityhub/latest/userguide/cognito-controls.html#cognito-2) | Cognito identity pools should not allow unauthenticated identities | 中 | ○ |
| [Cognito.3](https://docs.aws.amazon.com/securityhub/latest/userguide/cognito-controls.html#cognito-3) | Password policies for Cognito user pools should have strong configurations | 中 | ○ |
| [Config.1](https://docs.aws.amazon.com/securityhub/latest/userguide/config-controls.html#config-1) | AWS Config should be enabled and use the service-linked role for resource recording | 重大 | ○ |
| [Connect.2](https://docs.aws.amazon.com/securityhub/latest/userguide/connect-controls.html#connect-2) | Amazon Connect instances should have CloudWatch logging enabled | 中 | ○ |
| [DataFirehose.1](https://docs.aws.amazon.com/securityhub/latest/userguide/datafirehose-controls.html#datafirehose-1) | Firehose delivery streams should be encrypted at rest | 中 | ○ |
| [DataSync.1](https://docs.aws.amazon.com/securityhub/latest/userguide/datasync-controls.html#datasync-1) | DataSync tasks should have logging enabled | 中 | ○ |
| [DataSync.2](https://docs.aws.amazon.com/securityhub/latest/userguide/datasync-controls.html#datasync-2) | DataSync tasks should be tagged | 低 | - |
| [DMS.1](https://docs.aws.amazon.com/securityhub/latest/userguide/dms-controls.html#dms-1) | Database Migration Service replication instances should not be public | 重大 | ○ |
| [DMS.6](https://docs.aws.amazon.com/securityhub/latest/userguide/dms-controls.html#dms-6) | DMS replication instances should have automatic minor version upgrade enabled | 中 | ○ |
| [DMS.7](https://docs.aws.amazon.com/securityhub/latest/userguide/dms-controls.html#dms-7) | DMS replication tasks for the target database should have logging enabled | 中 | ○ |
| [DMS.8](https://docs.aws.amazon.com/securityhub/latest/userguide/dms-controls.html#dms-8) | DMS replication tasks for the source database should have logging enabled | 中 | ○ |
| [DMS.9](https://docs.aws.amazon.com/securityhub/latest/userguide/dms-controls.html#dms-9) | DMS endpoints should use SSL | 中 | ○ |
| [DMS.10](https://docs.aws.amazon.com/securityhub/latest/userguide/dms-controls.html#dms-10) | DMS endpoints for Neptune databases should have IAM authorization enabled | 中 | ○ |
| [DMS.11](https://docs.aws.amazon.com/securityhub/latest/userguide/dms-controls.html#dms-11) | DMS endpoints for MongoDB should have an authentication mechanism enabled | 中 | ○ |
| [DMS.12](https://docs.aws.amazon.com/securityhub/latest/userguide/dms-controls.html#dms-12) | DMS endpoints for Redis OSS should have TLS enabled | 中 | ○ |
| [DocumentDB.1](https://docs.aws.amazon.com/securityhub/latest/userguide/documentdb-controls.html#documentdb-1) | Amazon DocumentDB clusters should be encrypted at rest | 中 | ○ |
| [DocumentDB.2](https://docs.aws.amazon.com/securityhub/latest/userguide/documentdb-controls.html#documentdb-2) | Amazon DocumentDB clusters should have an adequate backup retention period | 中 | ○ |
| [DocumentDB.3](https://docs.aws.amazon.com/securityhub/latest/userguide/documentdb-controls.html#documentdb-3) | Amazon DocumentDB manual cluster snapshots should not be public | 重大 | ○ |
| [DocumentDB.4](https://docs.aws.amazon.com/securityhub/latest/userguide/documentdb-controls.html#documentdb-4) | Amazon DocumentDB clusters should publish audit logs to CloudWatch Logs | 中 | ○ |
| [DocumentDB.5](https://docs.aws.amazon.com/securityhub/latest/userguide/documentdb-controls.html#documentdb-5) | Amazon DocumentDB clusters should have deletion protection enabled | 中 | ○ |
| [DocumentDB.6](https://docs.aws.amazon.com/securityhub/latest/userguide/documentdb-controls.html#documentdb-6) | Amazon DocumentDB clusters should be encrypted in transit | 中 | ○ |
| [DynamoDB.1](https://docs.aws.amazon.com/securityhub/latest/userguide/dynamodb-controls.html#dynamodb-1) | DynamoDB tables should automatically scale capacity with demand | 中 | ○ |
| [DynamoDB.2](https://docs.aws.amazon.com/securityhub/latest/userguide/dynamodb-controls.html#dynamodb-2) | DynamoDB tables should have point-in-time recovery enabled | 中 | ○ |
| [DynamoDB.3](https://docs.aws.amazon.com/securityhub/latest/userguide/dynamodb-controls.html#dynamodb-3) | DynamoDB Accelerator (DAX) clusters should be encrypted at rest | 中 | ○ |
| [DynamoDB.4](https://docs.aws.amazon.com/securityhub/latest/userguide/dynamodb-controls.html#dynamodb-4) | DynamoDB tables should be present in a backup plan | 中 | - |
| [DynamoDB.6](https://docs.aws.amazon.com/securityhub/latest/userguide/dynamodb-controls.html#dynamodb-6) | DynamoDB tables should have deletion protection enabled | 中 | ○ |
| [DynamoDB.7](https://docs.aws.amazon.com/securityhub/latest/userguide/dynamodb-controls.html#dynamodb-7) | DynamoDB Accelerator clusters should be encrypted in transit | 中 | ○ |
| [EC2.1](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-1) | EBS snapshots should not be configured to be publicly restorable | 重大 | ○ |
| [EC2.2](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-2) | VPC default security groups should not allow inbound or outbound traffic | 高 | ○ |
| [EC2.3](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-3) | Attached EBS volumes should be encrypted at-rest | 中 | ○ |
| [EC2.4](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-4) | Stopped EC2 instances should be removed after a specified time period | 中 | ○ |
| [EC2.6](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-6) | VPC flow logging should be enabled in all VPCs | 中 | ○ |
| [EC2.7](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-7) | EBS default encryption should be enabled | 中 | ○ |
| [EC2.8](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-8) | EC2 instances should use Instance Metadata Service Version 2 (IMDSv2) | 高 | ○ |
| [EC2.9](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-9) | EC2 instances should not have a public IPv4 address | 高 | ○ |
| [EC2.10](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-10) | Amazon EC2 should be configured to use VPC endpoints that are created for the Amazon EC2 service | 中 | ○ |
| [EC2.12](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-12) | Unused EC2 EIPs should be removed | 低 | - |
| [EC2.13](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-13) | Security groups should not allow ingress from 0.0.0.0/0 or ::/0 to port 22 | 高 | - |
| [EC2.14](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-14) | Security groups should not allow ingress from 0.0.0.0/0 or ::/0 to port 3389 | 高 | - |
| [EC2.15](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-15) | EC2 subnets should not automatically assign public IP addresses | 中 | ○ |
| [EC2.16](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-16) | Unused Network Access Control Lists should be removed | 低 | ○ |
| [EC2.17](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-17) | EC2 instances should not use multiple ENIs | 低 | ○ |
| [EC2.18](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-18) | Security groups should only allow unrestricted incoming traffic for authorized ports | 高 | ○ |
| [EC2.19](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-19) | Security groups should not allow unrestricted access to ports with high risk | 重大 | ○ |
| [EC2.20](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-20) | Both VPN tunnels for an AWS Site-to-Site VPN connection should be up | 中 | ○ |
| [EC2.21](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-21) | Network ACLs should not allow ingress from 0.0.0.0/0 to port 22 or port 3389 | 中 | ○ |
| [EC2.22](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-22) | Unused EC2 security groups should be removed | 中 | - |
| [EC2.23](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-23) | EC2 Transit Gateways should not automatically accept VPC attachment requests | 高 | ○ |
| [EC2.24](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-24) | EC2 paravirtual instance types should not be used | 中 | ○ |
| [EC2.25](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-25) | EC2 launch templates should not assign public IPs to network interfaces | 高 | ○ |
| [EC2.28](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-28) | EBS volumes should be in a backup plan | 低 | - |
| [EC2.51](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-51) | EC2 Client VPN endpoints should have client connection logging enabled | 低 | ○ |
| [EC2.53](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-53) | EC2 security groups should not allow ingress from 0.0.0.0/0 to remote server administration ports | 高 | - |
| [EC2.54](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-54) | EC2 security groups should not allow ingress from ::/0 to remote server administration ports | 高 | - |
| [EC2.170](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-170) | EC2 launch templates should use Instance Metadata Service Version 2 (IMDSv2) | 低 | ○ |
| [EC2.171](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-171) | EC2 VPN connections should have logging enabled | 中 | ○ |
| [EC2.173](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-173) | EC2 Spot Fleet requests with launch parameters should enable encryption for attached EBS volumes | 中 | ○ |
| [EC2.174](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-174) | EC2 DHCP option sets should be tagged | 低 | - |
| [EC2.176](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-176) | EC2 prefix lists should be tagged | 低 | - |
| [EC2.177](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-177) | EC2 traffic mirror sessions should be tagged | 低 | - |
| [EC2.178](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-178) | EC2 traffic mirror filters should be tagged | 低 | - |
| [EC2.180](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-180) | EC2 network interfaces should have source/destination checking enabled | 中 | ○ |
| [EC2.181](https://docs.aws.amazon.com/securityhub/latest/userguide/ec2-controls.html#ec2-181) | EC2 launch templates should enable encryption for attached EBS volumes | 中 | ○ |
| [ECR.1](https://docs.aws.amazon.com/securityhub/latest/userguide/ecr-controls.html#ecr-1) | ECR private repositories should have image scanning configured | 高 | ○ |
| [ECR.2](https://docs.aws.amazon.com/securityhub/latest/userguide/ecr-controls.html#ecr-2) | ECR private repositories should have tag immutability configured | 中 | ○ |
| [ECR.3](https://docs.aws.amazon.com/securityhub/latest/userguide/ecr-controls.html#ecr-3) | ECR repositories should have at least one lifecycle policy configured | 中 | ○ |
| [ECS.2](https://docs.aws.amazon.com/securityhub/latest/userguide/ecs-controls.html#ecs-2) | ECS services should not have public IP addresses assigned to them automatically | 高 | ○ |
| [ECS.3](https://docs.aws.amazon.com/securityhub/latest/userguide/ecs-controls.html#ecs-3) | ECS task definitions should not share the host's process namespace | 高 | ○ |
| [ECS.4](https://docs.aws.amazon.com/securityhub/latest/userguide/ecs-controls.html#ecs-4) | ECS containers should run as non-privileged | 高 | ○ |
| [ECS.5](https://docs.aws.amazon.com/securityhub/latest/userguide/ecs-controls.html#ecs-5) | ECS task definitions should configure containers to be limited to read-only access to root filesystems | 高 | ○ |
| [ECS.8](https://docs.aws.amazon.com/securityhub/latest/userguide/ecs-controls.html#ecs-8) | Secrets should not be passed as container environment variables | 高 | ○ |
| [ECS.9](https://docs.aws.amazon.com/securityhub/latest/userguide/ecs-controls.html#ecs-9) | ECS task definitions should have a logging configuration | 高 | ○ |
| [ECS.10](https://docs.aws.amazon.com/securityhub/latest/userguide/ecs-controls.html#ecs-10) | ECS Fargate services should run on the latest Fargate platform version | 中 | ○ |
| [ECS.12](https://docs.aws.amazon.com/securityhub/latest/userguide/ecs-controls.html#ecs-12) | ECS clusters should use Container Insights | 中 | ○ |
| [ECS.16](https://docs.aws.amazon.com/securityhub/latest/userguide/ecs-controls.html#ecs-16) | ECS task sets should not automatically assign public IP addresses | 高 | ○ |
| [ECS.17](https://docs.aws.amazon.com/securityhub/latest/userguide/ecs-controls.html#ecs-17) | ECS task definitions should not use host network mode | 中 | - |
| [EFS.1](https://docs.aws.amazon.com/securityhub/latest/userguide/efs-controls.html#efs-1) | Elastic File System should be configured to encrypt file data at-rest using AWS KMS | 中 | ○ |
| [EFS.2](https://docs.aws.amazon.com/securityhub/latest/userguide/efs-controls.html#efs-2) | Amazon EFS volumes should be in backup plans | 中 | ○ |
| [EFS.3](https://docs.aws.amazon.com/securityhub/latest/userguide/efs-controls.html#efs-3) | EFS access points should enforce a root directory | 中 | ○ |
| [EFS.4](https://docs.aws.amazon.com/securityhub/latest/userguide/efs-controls.html#efs-4) | EFS access points should enforce a user identity | 中 | ○ |
| [EFS.6](https://docs.aws.amazon.com/securityhub/latest/userguide/efs-controls.html#efs-6) | EFS mount targets should not be associated with subnets that assign public IP addresses on launch | 中 | - |
| [EFS.7](https://docs.aws.amazon.com/securityhub/latest/userguide/efs-controls.html#efs-7) | EFS file systems should have automatic backups enabled | 中 | ○ |
| [EFS.8](https://docs.aws.amazon.com/securityhub/latest/userguide/efs-controls.html#efs-8) | EFS file systems should be encrypted at rest | 中 | ○ |
| [EKS.1](https://docs.aws.amazon.com/securityhub/latest/userguide/eks-controls.html#eks-1) | EKS cluster endpoints should not be publicly accessible | 高 | ○ |
| [EKS.2](https://docs.aws.amazon.com/securityhub/latest/userguide/eks-controls.html#eks-2) | EKS clusters should run on a supported Kubernetes version | 高 | ○ |
| [EKS.8](https://docs.aws.amazon.com/securityhub/latest/userguide/eks-controls.html#eks-8) | EKS clusters should have audit logging enabled | 中 | ○ |
| [ElastiCache.1](https://docs.aws.amazon.com/securityhub/latest/userguide/elasticache-controls.html#elasticache-1) | ElastiCache (Redis OSS) clusters should have automatic backups enabled | 高 | ○ |
| [ElastiCache.2](https://docs.aws.amazon.com/securityhub/latest/userguide/elasticache-controls.html#elasticache-2) | ElastiCache clusters should have automatic minor version upgrades enabled | 高 | ○ |
| [ElastiCache.3](https://docs.aws.amazon.com/securityhub/latest/userguide/elasticache-controls.html#elasticache-3) | ElastiCache replication groups should have automatic failover enabled | 中 | ○ |
| [ElastiCache.4](https://docs.aws.amazon.com/securityhub/latest/userguide/elasticache-controls.html#elasticache-4) | ElastiCache replication groups should be encrypted at rest | 中 | ○ |
| [ElastiCache.5](https://docs.aws.amazon.com/securityhub/latest/userguide/elasticache-controls.html#elasticache-5) | ElastiCache replication groups should be encrypted in transit | 中 | ○ |
| [ElastiCache.6](https://docs.aws.amazon.com/securityhub/latest/userguide/elasticache-controls.html#elasticache-6) | ElastiCache (Redis OSS) replication groups of earlier versions should have Redis OSS AUTH enabled | 中 | ○ |
| [ElastiCache.7](https://docs.aws.amazon.com/securityhub/latest/userguide/elasticache-controls.html#elasticache-7) | ElastiCache clusters should not use the default subnet group | 高 | ○ |
| [ElasticBeanstalk.1](https://docs.aws.amazon.com/securityhub/latest/userguide/elasticbeanstalk-controls.html#elasticbeanstalk-1) | Elastic Beanstalk environments should have enhanced health reporting enabled | 低 | ○ |
| [ElasticBeanstalk.2](https://docs.aws.amazon.com/securityhub/latest/userguide/elasticbeanstalk-controls.html#elasticbeanstalk-2) | Elastic Beanstalk managed platform updates should be enabled | 高 | ○ |
| [ElasticBeanstalk.3](https://docs.aws.amazon.com/securityhub/latest/userguide/elasticbeanstalk-controls.html#elasticbeanstalk-3) | Elastic Beanstalk should stream logs to CloudWatch | 高 | ○ |
| [ELB.1](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-1) | Application Load Balancer should be configured to redirect all HTTP requests to HTTPS | 中 | ○ |
| [ELB.2](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-2) | Classic Load Balancers with SSL/HTTPS listeners should use a certificate provided by AWS Certificate Manager | 中 | ○ |
| [ELB.3](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-3) | Classic Load Balancer listeners should be configured with HTTPS or TLS termination | 中 | ○ |
| [ELB.4](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-4) | Application load balancer should be configured to drop invalid http headers | 中 | ○ |
| [ELB.5](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-5) | Application and Classic Load Balancers logging should be enabled | 中 | ○ |
| [ELB.6](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-6) | Application, Gateway, and Network Load Balancers should have deletion protection enabled | 中 | ○ |
| [ELB.7](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-7) | Classic Load Balancers should have connection draining enabled | 低 | ○ |
| [ELB.8](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-8) | Classic Load Balancers with SSL listeners should use a predefined security policy that has strong configuration | 中 | ○ |
| [ELB.9](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-9) | Classic Load Balancers should have cross-zone load balancing enabled | 中 | ○ |
| [ELB.10](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-10) | Classic Load Balancer should span multiple Availability Zones | 中 | ○ |
| [ELB.12](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-12) | Application Load Balancer should be configured with defensive or strictest desync mitigation mode | 中 | ○ |
| [ELB.13](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-13) | Application, Network and Gateway Load Balancers should span multiple Availability Zones | 中 | ○ |
| [ELB.14](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-14) | Classic Load Balancer should be configured with defensive or strictest desync mitigation mode | 中 | ○ |
| [ELB.16](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-16) | Application Load Balancers should be associated with an AWS WAF web ACL | 中 | - |
| [ELB.17](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-17) | Application and Network Load Balancers with listeners should use recommended security policies | 中 | ○ |
| [ELB.18](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-18) | Application and Network Load Balancer listeners should use secure protocols to encrypt data in transit | 中 | ○ |
| [ELB.21](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-21) | Application and Network Load Balancer target groups should use encrypted health check protocols | 中 | ○ |
| [ELB.22](https://docs.aws.amazon.com/securityhub/latest/userguide/elb-controls.html#elb-22) | ELB target groups should use encrypted transport protocols | 中 | ○ |
| [EMR.1](https://docs.aws.amazon.com/securityhub/latest/userguide/emr-controls.html#emr-1) | Amazon EMR cluster primary nodes should not have public IP addresses | 高 | ○ |
| [EMR.2](https://docs.aws.amazon.com/securityhub/latest/userguide/emr-controls.html#emr-2) | Amazon EMR block public access setting should be enabled | 重大 | ○ |
| [EMR.3](https://docs.aws.amazon.com/securityhub/latest/userguide/emr-controls.html#emr-3) | Amazon EMR security configurations should have encryption at rest enabled | 中 | ○ |
| [EMR.4](https://docs.aws.amazon.com/securityhub/latest/userguide/emr-controls.html#emr-4) | Amazon EMR security configurations should have encryption in transit enabled | 中 | ○ |
| [ES.1](https://docs.aws.amazon.com/securityhub/latest/userguide/es-controls.html#es-1) | Elasticsearch domains should have encryption at-rest enabled | 中 | ○ |
| [ES.2](https://docs.aws.amazon.com/securityhub/latest/userguide/es-controls.html#es-2) | Elasticsearch domains should not be publicly accessible | 重大 | ○ |
| [ES.3](https://docs.aws.amazon.com/securityhub/latest/userguide/es-controls.html#es-3) | Elasticsearch domains should encrypt data sent between nodes | 中 | ○ |
| [ES.4](https://docs.aws.amazon.com/securityhub/latest/userguide/es-controls.html#es-4) | Elasticsearch domain error logging to CloudWatch Logs should be enabled | 中 | ○ |
| [ES.5](https://docs.aws.amazon.com/securityhub/latest/userguide/es-controls.html#es-5) | Elasticsearch domains should have audit logging enabled | 中 | ○ |
| [ES.6](https://docs.aws.amazon.com/securityhub/latest/userguide/es-controls.html#es-6) | Elasticsearch domains should have at least three data nodes | 中 | ○ |
| [ES.7](https://docs.aws.amazon.com/securityhub/latest/userguide/es-controls.html#es-7) | Elasticsearch domains should be configured with at least three dedicated master nodes | 中 | ○ |
| [ES.8](https://docs.aws.amazon.com/securityhub/latest/userguide/es-controls.html#es-8) | Connections to Elasticsearch domains should be encrypted using the latest TLS security policy | 中 | ○ |
| [EventBridge.3](https://docs.aws.amazon.com/securityhub/latest/userguide/eventbridge-controls.html#eventbridge-3) | EventBridge custom event buses should have a resource-based policy attached | 低 | ○ |
| [EventBridge.4](https://docs.aws.amazon.com/securityhub/latest/userguide/eventbridge-controls.html#eventbridge-4) | EventBridge global endpoints should have event replication enabled | 中 | - |
| [FSx.1](https://docs.aws.amazon.com/securityhub/latest/userguide/fsx-controls.html#fsx-1) | FSx for OpenZFS file systems should be configured to copy tags to backups and volumes | 低 | ○ |
| [FSx.2](https://docs.aws.amazon.com/securityhub/latest/userguide/fsx-controls.html#fsx-2) | FSx for Lustre file systems should be configured to copy tags to backups | 低 | ○ |
| [FSx.3](https://docs.aws.amazon.com/securityhub/latest/userguide/fsx-controls.html#fsx-3) | FSx for OpenZFS file systems should be configured for Multi-AZ deployment | 中 | ○ |
| [FSx.5](https://docs.aws.amazon.com/securityhub/latest/userguide/fsx-controls.html#fsx-5) | FSx for Windows File Server file systems should be configured for Multi-AZ deployment | 中 | ○ |
| [Glue.3](https://docs.aws.amazon.com/securityhub/latest/userguide/glue-controls.html#glue-3) | AWS Glue machine learning transforms should be encrypted at rest | 中 | ○ |
| [Glue.4](https://docs.aws.amazon.com/securityhub/latest/userguide/glue-controls.html#glue-4) | AWS Glue Spark jobs should run on supported versions of AWS Glue | 中 | ○ |
| [GuardDuty.1](https://docs.aws.amazon.com/securityhub/latest/userguide/guardduty-controls.html#guardduty-1) | GuardDuty should be enabled | 高 | ○ |
| [GuardDuty.5](https://docs.aws.amazon.com/securityhub/latest/userguide/guardduty-controls.html#guardduty-5) | GuardDuty EKS Audit Log Monitoring should be enabled | 高 | ○ |
| [GuardDuty.6](https://docs.aws.amazon.com/securityhub/latest/userguide/guardduty-controls.html#guardduty-6) | GuardDuty Lambda Protection should be enabled | 高 | ○ |
| [GuardDuty.7](https://docs.aws.amazon.com/securityhub/latest/userguide/guardduty-controls.html#guardduty-7) | GuardDuty EKS Runtime Monitoring should be enabled | 高 | ○ |
| [GuardDuty.8](https://docs.aws.amazon.com/securityhub/latest/userguide/guardduty-controls.html#guardduty-8) | GuardDuty Malware Protection for EC2 should be enabled | 高 | ○ |
| [GuardDuty.9](https://docs.aws.amazon.com/securityhub/latest/userguide/guardduty-controls.html#guardduty-9) | GuardDuty RDS Protection should be enabled | 高 | ○ |
| [GuardDuty.10](https://docs.aws.amazon.com/securityhub/latest/userguide/guardduty-controls.html#guardduty-10) | GuardDuty S3 Protection should be enabled | 高 | ○ |
| [GuardDuty.11](https://docs.aws.amazon.com/securityhub/latest/userguide/guardduty-controls.html#guardduty-11) | GuardDuty Runtime Monitoring should be enabled | 高 | ○ |
| [GuardDuty.12](https://docs.aws.amazon.com/securityhub/latest/userguide/guardduty-controls.html#guardduty-12) | GuardDuty ECS Runtime Monitoring should be enabled | 中 | ○ |
| [GuardDuty.13](https://docs.aws.amazon.com/securityhub/latest/userguide/guardduty-controls.html#guardduty-13) | GuardDuty EC2 Runtime Monitoring should be enabled | 中 | ○ |
| [IAM.1](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-1) | IAM policies should not allow full "*" administrative privileges | 高 | ○ |
| [IAM.2](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-2) | IAM users should not have IAM policies attached | 低 | ○ |
| [IAM.3](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-3) | IAM users' access keys should be rotated every 90 days or less | 中 | ○ |
| [IAM.4](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-4) | IAM root user access key should not exist | 重大 | ○ |
| [IAM.5](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-5) | MFA should be enabled for all IAM users that have a console password | 中 | ○ |
| [IAM.6](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-6) | Hardware MFA should be enabled for the root user | 重大 | ○ |
| [IAM.7](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-7) | Password policies for IAM users should have strong configurations | 中 | ○ |
| [IAM.8](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-8) | Unused IAM user credentials should be removed | 中 | ○ |
| [IAM.9](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-9) | MFA should be enabled for the root user | 重大 | - |
| [IAM.10](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-10) | Password policies for IAM users should have strong configurations | 中 | - |
| [IAM.11](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-11) | Ensure IAM password policy requires at least one uppercase letter | 中 | - |
| [IAM.12](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-12) | Ensure IAM password policy requires at least one lowercase letter | 中 | - |
| [IAM.13](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-13) | Ensure IAM password policy requires at least one symbol | 中 | - |
| [IAM.14](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-14) | Ensure IAM password policy requires at least one number | 中 | - |
| [IAM.15](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-15) | Ensure IAM password policy requires minimum password length of 14 or greater | 中 | - |
| [IAM.16](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-16) | Ensure IAM password policy prevents password reuse | 低 | - |
| [IAM.17](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-17) | Ensure IAM password policy expires passwords within 90 days or less | 低 | - |
| [IAM.18](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-18) | Ensure a support role has been created to manage incidents with AWS Support | 低 | - |
| [IAM.19](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-19) | MFA should be enabled for all IAM users | 中 | - |
| [IAM.21](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-21) | IAM customer managed policies that you create should not allow wildcard actions for services | 低 | ○ |
| [IAM.22](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-22) | IAM user credentials unused for 45 days should be removed | 中 | - |
| [IAM.26](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-26) | Expired SSL/TLS certificates managed in IAM should be removed | 中 | - |
| [IAM.27](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-27) | IAM identities should not have the AWSCloudShellFullAccess policy attached | 中 | - |
| [IAM.28](https://docs.aws.amazon.com/securityhub/latest/userguide/iam-controls.html#iam-28) | IAM Access Analyzer external access analyzer should be enabled | 高 | - |
| [Inspector.1](https://docs.aws.amazon.com/securityhub/latest/userguide/inspector-controls.html#inspector-1) | Amazon Inspector EC2 scanning should be enabled | 高 | ○ |
| [Inspector.2](https://docs.aws.amazon.com/securityhub/latest/userguide/inspector-controls.html#inspector-2) | Amazon Inspector ECR scanning should be enabled | 高 | ○ |
| [Inspector.3](https://docs.aws.amazon.com/securityhub/latest/userguide/inspector-controls.html#inspector-3) | Amazon Inspector Lambda code scanning should be enabled | 高 | ○ |
| [Inspector.4](https://docs.aws.amazon.com/securityhub/latest/userguide/inspector-controls.html#inspector-4) | Amazon Inspector Lambda standard scanning should be enabled | 高 | ○ |
| [IoTTwinMaker.2](https://docs.aws.amazon.com/securityhub/latest/userguide/iottwinmaker-controls.html#iottwinmaker-2) | AWS IoT TwinMaker workspaces should be tagged | 低 | - |
| [IVS.1](https://docs.aws.amazon.com/securityhub/latest/userguide/ivs-controls.html#ivs-1) | IVS playback key pairs should be tagged | 低 | - |
| [IVS.2](https://docs.aws.amazon.com/securityhub/latest/userguide/ivs-controls.html#ivs-2) | IVS recording configurations should be tagged | 低 | - |
| [Keyspaces.1](https://docs.aws.amazon.com/securityhub/latest/userguide/keyspaces-controls.html#keyspaces-1) | Amazon Keyspaces keyspaces should be tagged | 低 | - |
| [Kinesis.1](https://docs.aws.amazon.com/securityhub/latest/userguide/kinesis-controls.html#kinesis-1) | Kinesis streams should be encrypted at rest | 中 | ○ |
| [KMS.1](https://docs.aws.amazon.com/securityhub/latest/userguide/kms-controls.html#kms-1) | IAM customer managed policies should not allow decryption actions on all KMS keys | 中 | ○ |
| [KMS.2](https://docs.aws.amazon.com/securityhub/latest/userguide/kms-controls.html#kms-2) | IAM principals should not have IAM inline policies that allow decryption actions on all KMS keys | 中 | ○ |
| [KMS.3](https://docs.aws.amazon.com/securityhub/latest/userguide/kms-controls.html#kms-3) | AWS KMS keys should not be deleted unintentionally | 重大 | ○ |
| [KMS.4](https://docs.aws.amazon.com/securityhub/latest/userguide/kms-controls.html#kms-4) | AWS KMS key rotation should be enabled | 中 | - |
| [KMS.5](https://docs.aws.amazon.com/securityhub/latest/userguide/kms-controls.html#kms-5) | KMS keys should not be publicly accessible | 重大 | ○ |
| [Lambda.1](https://docs.aws.amazon.com/securityhub/latest/userguide/lambda-controls.html#lambda-1) | Lambda function policies should prohibit public access | 重大 | ○ |
| [Lambda.2](https://docs.aws.amazon.com/securityhub/latest/userguide/lambda-controls.html#lambda-2) | Lambda functions should use supported runtimes | 中 | ○ |
| [Lambda.3](https://docs.aws.amazon.com/securityhub/latest/userguide/lambda-controls.html#lambda-3) | Lambda functions should be in a VPC | 低 | - |
| [Lambda.5](https://docs.aws.amazon.com/securityhub/latest/userguide/lambda-controls.html#lambda-5) | VPC Lambda functions should operate in multiple Availability Zones | 中 | ○ |
| [Lambda.7](https://docs.aws.amazon.com/securityhub/latest/userguide/lambda-controls.html#lambda-7) | Lambda functions should have AWS X-Ray active tracing enabled | 低 | - |
| [Macie.1](https://docs.aws.amazon.com/securityhub/latest/userguide/macie-controls.html#macie-1) | Macie should be enabled | 中 | ○ |
| [Macie.2](https://docs.aws.amazon.com/securityhub/latest/userguide/macie-controls.html#macie-2) | Macie automated sensitive data discovery should be enabled | 高 | ○ |
| [MQ.2](https://docs.aws.amazon.com/securityhub/latest/userguide/mq-controls.html#mq-2) | ActiveMQ brokers should stream audit logs to CloudWatch | 中 | ○ |
| [MQ.5](https://docs.aws.amazon.com/securityhub/latest/userguide/mq-controls.html#mq-5) | ActiveMQ brokers should use active/standby deployment mode | 低 | - |
| [MQ.6](https://docs.aws.amazon.com/securityhub/latest/userguide/mq-controls.html#mq-6) | RabbitMQ brokers should use cluster deployment mode | 低 | - |
| [MSK.1](https://docs.aws.amazon.com/securityhub/latest/userguide/msk-controls.html#msk-1) | MSK clusters should be encrypted in transit among broker nodes | 中 | ○ |
| [MSK.2](https://docs.aws.amazon.com/securityhub/latest/userguide/msk-controls.html#msk-2) | MSK clusters should have enhanced monitoring configured | 低 | - |
| [MSK.3](https://docs.aws.amazon.com/securityhub/latest/userguide/msk-controls.html#msk-3) | MSK Connect connectors should be encrypted in transit | 中 | ○ |
| [MSK.4](https://docs.aws.amazon.com/securityhub/latest/userguide/msk-controls.html#msk-4) | Amazon MSK clusters should have public access disabled | 重大 | ○ |
| [MSK.5](https://docs.aws.amazon.com/securityhub/latest/userguide/msk-controls.html#msk-5) | MSK connectors should have logging enabled | 中 | ○ |
| [MSK.6](https://docs.aws.amazon.com/securityhub/latest/userguide/msk-controls.html#msk-6) | MSK clusters should disable unauthenticated access | 中 | ○ |
| [Neptune.1](https://docs.aws.amazon.com/securityhub/latest/userguide/neptune-controls.html#neptune-1) | Neptune DB clusters should be encrypted at rest | 中 | ○ |
| [Neptune.2](https://docs.aws.amazon.com/securityhub/latest/userguide/neptune-controls.html#neptune-2) | Neptune DB clusters should publish audit logs to CloudWatch Logs | 中 | ○ |
| [Neptune.3](https://docs.aws.amazon.com/securityhub/latest/userguide/neptune-controls.html#neptune-3) | Neptune DB cluster snapshots should not be public | 重大 | ○ |
| [Neptune.4](https://docs.aws.amazon.com/securityhub/latest/userguide/neptune-controls.html#neptune-4) | Neptune DB clusters should have deletion protection enabled | 低 | ○ |
| [Neptune.5](https://docs.aws.amazon.com/securityhub/latest/userguide/neptune-controls.html#neptune-5) | Neptune DB clusters should have automated backups enabled | 中 | ○ |
| [Neptune.6](https://docs.aws.amazon.com/securityhub/latest/userguide/neptune-controls.html#neptune-6) | Neptune DB cluster snapshots should be encrypted at rest | 中 | ○ |
| [Neptune.7](https://docs.aws.amazon.com/securityhub/latest/userguide/neptune-controls.html#neptune-7) | Neptune DB clusters should have IAM database authentication enabled | 中 | ○ |
| [Neptune.8](https://docs.aws.amazon.com/securityhub/latest/userguide/neptune-controls.html#neptune-8) | Neptune DB clusters should be configured to copy tags to snapshots | 低 | ○ |
| [Neptune.9](https://docs.aws.amazon.com/securityhub/latest/userguide/neptune-controls.html#neptune-9) | Neptune DB clusters should be deployed across multiple Availability Zones | 中 | - |
| [NetworkFirewall.1](https://docs.aws.amazon.com/securityhub/latest/userguide/networkfirewall-controls.html#networkfirewall-1) | Network Firewall firewalls should be deployed across multiple Availability Zones | 中 | - |
| [NetworkFirewall.2](https://docs.aws.amazon.com/securityhub/latest/userguide/networkfirewall-controls.html#networkfirewall-2) | Network Firewall logging should be enabled | 中 | ○ |
| [NetworkFirewall.3](https://docs.aws.amazon.com/securityhub/latest/userguide/networkfirewall-controls.html#networkfirewall-3) | Network Firewall policies should have at least one rule group associated | 中 | ○ |
| [NetworkFirewall.4](https://docs.aws.amazon.com/securityhub/latest/userguide/networkfirewall-controls.html#networkfirewall-4) | The default stateless action for Network Firewall policies should be drop or forward for full packets | 中 | ○ |
| [NetworkFirewall.5](https://docs.aws.amazon.com/securityhub/latest/userguide/networkfirewall-controls.html#networkfirewall-5) | The default stateless action for Network Firewall policies should be drop or forward for fragmented packets | 中 | ○ |
| [NetworkFirewall.6](https://docs.aws.amazon.com/securityhub/latest/userguide/networkfirewall-controls.html#networkfirewall-6) | Stateless network firewall rule group should not be empty | 中 | ○ |
| [NetworkFirewall.9](https://docs.aws.amazon.com/securityhub/latest/userguide/networkfirewall-controls.html#networkfirewall-9) | Network Firewall firewalls should have deletion protection enabled | 中 | ○ |
| [NetworkFirewall.10](https://docs.aws.amazon.com/securityhub/latest/userguide/networkfirewall-controls.html#networkfirewall-10) | Network Firewall firewalls should have subnet change protection enabled | 中 | ○ |
| [Opensearch.1](https://docs.aws.amazon.com/securityhub/latest/userguide/opensearch-controls.html#opensearch-1) | OpenSearch domains should have encryption at rest enabled | 中 | ○ |
| [Opensearch.2](https://docs.aws.amazon.com/securityhub/latest/userguide/opensearch-controls.html#opensearch-2) | OpenSearch domains should not be publicly accessible | 重大 | ○ |
| [Opensearch.3](https://docs.aws.amazon.com/securityhub/latest/userguide/opensearch-controls.html#opensearch-3) | OpenSearch domains should encrypt data sent between nodes | 中 | ○ |
| [Opensearch.4](https://docs.aws.amazon.com/securityhub/latest/userguide/opensearch-controls.html#opensearch-4) | OpenSearch domain error logging to CloudWatch Logs should be enabled | 中 | ○ |
| [Opensearch.5](https://docs.aws.amazon.com/securityhub/latest/userguide/opensearch-controls.html#opensearch-5) | OpenSearch domains should have audit logging enabled | 中 | ○ |
| [Opensearch.6](https://docs.aws.amazon.com/securityhub/latest/userguide/opensearch-controls.html#opensearch-6) | OpenSearch domains should have at least three data nodes | 中 | ○ |
| [Opensearch.7](https://docs.aws.amazon.com/securityhub/latest/userguide/opensearch-controls.html#opensearch-7) | OpenSearch domains should have fine-grained access control enabled | 高 | ○ |
| [Opensearch.8](https://docs.aws.amazon.com/securityhub/latest/userguide/opensearch-controls.html#opensearch-8) | Connections to OpenSearch domains should be encrypted using the latest TLS security policy | 中 | ○ |
| [Opensearch.10](https://docs.aws.amazon.com/securityhub/latest/userguide/opensearch-controls.html#opensearch-10) | OpenSearch domains should have the latest software update installed | 中 | ○ |
| [Opensearch.11](https://docs.aws.amazon.com/securityhub/latest/userguide/opensearch-controls.html#opensearch-11) | OpenSearch domains should have at least three dedicated primary nodes | 低 | - |
| [PCA.1](https://docs.aws.amazon.com/securityhub/latest/userguide/pca-controls.html#pca-1) | AWS Private CA root certificate authority should be disabled | 低 | ○ |
| [RDS.1](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-1) | RDS snapshot should be private | 重大 | ○ |
| [RDS.2](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-2) | RDS DB Instances should prohibit public access, as determined by the PubliclyAccessible configuration | 重大 | ○ |
| [RDS.3](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-3) | RDS DB instances should have encryption at-rest enabled | 中 | ○ |
| [RDS.4](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-4) | RDS cluster snapshots and database snapshots should be encrypted at rest | 中 | ○ |
| [RDS.5](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-5) | RDS DB instances should be configured with multiple Availability Zones | 中 | ○ |
| [RDS.6](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-6) | Enhanced monitoring should be configured for RDS DB instances | 低 | ○ |
| [RDS.7](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-7) | RDS clusters should have deletion protection enabled | 中 | ○ |
| [RDS.8](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-8) | RDS DB instances should have deletion protection enabled | 低 | ○ |
| [RDS.9](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-9) | RDS DB instances should publish logs to CloudWatch Logs | 中 | ○ |
| [RDS.10](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-10) | IAM authentication should be configured for RDS instances | 中 | ○ |
| [RDS.11](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-11) | RDS instances should have automatic backups enabled | 中 | ○ |
| [RDS.12](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-12) | IAM authentication should be configured for RDS clusters | 中 | ○ |
| [RDS.13](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-13) | RDS automatic minor version upgrades should be enabled | 高 | ○ |
| [RDS.14](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-14) | Amazon Aurora clusters should have backtracking enabled | 中 | ○ |
| [RDS.15](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-15) | RDS DB clusters should be configured for multiple Availability Zones | 中 | ○ |
| [RDS.16](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-16) | Aurora DB clusters should be configured to copy tags to DB snapshots | 低 | ○ |
| [RDS.17](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-17) | RDS DB instances should be configured to copy tags to snapshots | 低 | ○ |
| [RDS.19](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-19) | Existing RDS event notification subscriptions should be configured for critical cluster events | 低 | ○ |
| [RDS.20](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-20) | Existing RDS event notification subscriptions should be configured for critical database instance events | 低 | ○ |
| [RDS.21](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-21) | An RDS event notifications subscription should be configured for critical database parameter group events | 低 | ○ |
| [RDS.22](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-22) | An RDS event notifications subscription should be configured for critical database security group events | 低 | ○ |
| [RDS.23](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-23) | RDS instances should not use a database engine default port | 低 | ○ |
| [RDS.24](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-24) | RDS Database Clusters should use a custom administrator username | 中 | ○ |
| [RDS.25](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-25) | RDS database instances should use a custom administrator username | 中 | ○ |
| [RDS.26](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-26) | RDS DB instances should be protected by a backup plan | 中 | - |
| [RDS.27](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-27) | RDS DB clusters should be encrypted at rest | 中 | ○ |
| [RDS.34](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-34) | Aurora MySQL DB clusters should publish audit logs to CloudWatch Logs | 中 | ○ |
| [RDS.35](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-35) | RDS DB clusters should have automatic minor version upgrade enabled | 中 | ○ |
| [RDS.36](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-36) | RDS for PostgreSQL DB instances should publish logs to CloudWatch Logs | 中 | ○ |
| [RDS.37](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-37) | Aurora PostgreSQL DB clusters should publish logs to CloudWatch Logs | 中 | ○ |
| [RDS.38](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-38) | RDS for PostgreSQL DB instances should be encrypted in transit | 中 | ○ |
| [RDS.39](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-39) | RDS for MySQL DB instances should be encrypted in transit | 中 | ○ |
| [RDS.41](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-41) | RDS for SQL Server DB instances should be encrypted in transit | 中 | ○ |
| [RDS.44](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-44) | RDS for MariaDB DB instances should be encrypted in transit | 中 | ○ |
| [RDS.45](https://docs.aws.amazon.com/securityhub/latest/userguide/rds-controls.html#rds-45) | Aurora MySQL DB clusters should have audit logging enabled | 中 | ○ |
| [Redshift.1](https://docs.aws.amazon.com/securityhub/latest/userguide/redshift-controls.html#redshift-1) | Amazon Redshift clusters should prohibit public access | 重大 | ○ |
| [Redshift.2](https://docs.aws.amazon.com/securityhub/latest/userguide/redshift-controls.html#redshift-2) | Connections to Amazon Redshift clusters should be encrypted in transit | 中 | ○ |
| [Redshift.3](https://docs.aws.amazon.com/securityhub/latest/userguide/redshift-controls.html#redshift-3) | Amazon Redshift clusters should have automatic snapshots enabled | 中 | ○ |
| [Redshift.4](https://docs.aws.amazon.com/securityhub/latest/userguide/redshift-controls.html#redshift-4) | Amazon Redshift clusters should have audit logging enabled | 中 | ○ |
| [Redshift.6](https://docs.aws.amazon.com/securityhub/latest/userguide/redshift-controls.html#redshift-6) | Amazon Redshift should have automatic upgrades to major versions enabled | 中 | ○ |
| [Redshift.7](https://docs.aws.amazon.com/securityhub/latest/userguide/redshift-controls.html#redshift-7) | Redshift clusters should use enhanced VPC routing | 中 | ○ |
| [Redshift.8](https://docs.aws.amazon.com/securityhub/latest/userguide/redshift-controls.html#redshift-8) | Amazon Redshift clusters should not use the default Admin username | 中 | ○ |
| [Redshift.10](https://docs.aws.amazon.com/securityhub/latest/userguide/redshift-controls.html#redshift-10) | Redshift clusters should be encrypted at rest | 中 | ○ |
| [Redshift.15](https://docs.aws.amazon.com/securityhub/latest/userguide/redshift-controls.html#redshift-15) | Redshift security groups should allow ingress on the cluster port only from restricted origins | 高 | ○ |
| [Redshift.16](https://docs.aws.amazon.com/securityhub/latest/userguide/redshift-controls.html#redshift-16) | Redshift cluster subnet groups should have subnets from multiple Availability Zones | 中 | - |
| [Redshift.18](https://docs.aws.amazon.com/securityhub/latest/userguide/redshift-controls.html#redshift-18) | Redshift clusters should have Multi-AZ deployments enabled | 中 | ○ |
| [RedshiftServerless.1](https://docs.aws.amazon.com/securityhub/latest/userguide/redshiftserverless-controls.html#redshiftserverless-1) | Amazon Redshift Serverless workgroups should use enhanced VPC routing | 高 | ○ |
| [RedshiftServerless.2](https://docs.aws.amazon.com/securityhub/latest/userguide/redshiftserverless-controls.html#redshiftserverless-2) | Connections to Redshift Serverless workgroups should be required to use SSL | 中 | ○ |
| [RedshiftServerless.3](https://docs.aws.amazon.com/securityhub/latest/userguide/redshiftserverless-controls.html#redshiftserverless-3) | Redshift Serverless workgroups should prohibit public access | 高 | ○ |
| [RedshiftServerless.6](https://docs.aws.amazon.com/securityhub/latest/userguide/redshiftserverless-controls.html#redshiftserverless-6) | Redshift Serverless namespaces should export logs to CloudWatch Logs | 中 | ○ |
| [Route53.2](https://docs.aws.amazon.com/securityhub/latest/userguide/route53-controls.html#route53-2) | Route 53 public hosted zones should log DNS queries | 中 | ○ |
| [S3.1](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-1) | S3 general purpose buckets should have block public access settings enabled | 中 | ○ |
| [S3.2](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-2) | S3 general purpose buckets should block public read access | 重大 | ○ |
| [S3.3](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-3) | S3 general purpose buckets should block public write access | 重大 | ○ |
| [S3.5](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-5) | S3 general purpose buckets should require requests to use TLS | 中 | ○ |
| [S3.6](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-6) | S3 general purpose bucket policies should restrict access to other AWS accounts | 高 | ○ |
| [S3.7](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-7) | S3 general purpose buckets should use cross-Region replication | 低 | - |
| [S3.8](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-8) | S3 general purpose buckets should block public access | 高 | ○ |
| [S3.9](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-9) | S3 general purpose buckets should have server access logging enabled | 中 | ○ |
| [S3.10](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-10) | S3 general purpose buckets with versioning enabled should have Lifecycle configurations | 中 | - |
| [S3.11](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-11) | S3 general purpose buckets should have event notifications enabled | 中 | - |
| [S3.12](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-12) | ACLs should not be used to manage user access to S3 general purpose buckets | 中 | ○ |
| [S3.13](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-13) | S3 general purpose buckets should have Lifecycle configurations | 低 | ○ |
| [S3.14](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-14) | S3 general purpose buckets should have versioning enabled | 低 | - |
| [S3.15](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-15) | S3 general purpose buckets should have Object Lock enabled | 中 | - |
| [S3.17](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-17) | S3 general purpose buckets should be encrypted at rest with AWS KMS keys | 中 | - |
| [S3.19](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-19) | S3 access points should have block public access settings enabled | 重大 | ○ |
| [S3.20](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-20) | S3 general purpose buckets should have MFA delete enabled | 低 | - |
| [S3.22](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-22) | S3 general purpose buckets should log object-level write events | 中 | - |
| [S3.23](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-23) | S3 general purpose buckets should log object-level read events | 中 | - |
| [S3.24](https://docs.aws.amazon.com/securityhub/latest/userguide/s3-controls.html#s3-24) | S3 Multi-Region Access Points should have block public access settings enabled | 高 | ○ |
| [SageMaker.1](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-1) | Amazon SageMaker notebook instances should not have direct internet access | 高 | ○ |
| [SageMaker.2](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-2) | SageMaker notebook instances should be launched in a custom VPC | 高 | ○ |
| [SageMaker.3](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-3) | Users should not have root access to SageMaker notebook instances | 高 | ○ |
| [SageMaker.4](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-4) | SageMaker endpoint production variants should have an initial instance count greater than 1 | 中 | ○ |
| [SageMaker.5](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-5) | SageMaker models should have network isolation enabled | 中 | ○ |
| [SageMaker.8](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-8) | SageMaker notebook instances should run on supported platforms | 中 | ○ |
| [SecretsManager.1](https://docs.aws.amazon.com/securityhub/latest/userguide/secretsmanager-controls.html#secretsmanager-1) | Secrets Manager secrets should have automatic rotation enabled | 中 | ○ |
| [SecretsManager.2](https://docs.aws.amazon.com/securityhub/latest/userguide/secretsmanager-controls.html#secretsmanager-2) | Secrets Manager secrets configured with automatic rotation should rotate successfully | 中 | ○ |
| [SecretsManager.3](https://docs.aws.amazon.com/securityhub/latest/userguide/secretsmanager-controls.html#secretsmanager-3) | Remove unused Secrets Manager secrets | 中 | ○ |
| [SecretsManager.4](https://docs.aws.amazon.com/securityhub/latest/userguide/secretsmanager-controls.html#secretsmanager-4) | Secrets Manager secrets should be rotated within a specified number of days | 中 | ○ |
| [ServiceCatalog.1](https://docs.aws.amazon.com/securityhub/latest/userguide/servicecatalog-controls.html#servicecatalog-1) | Service Catalog portfolios should be shared within an AWS organization only | 中 | ○ |
| [SNS.1](https://docs.aws.amazon.com/securityhub/latest/userguide/sns-controls.html#sns-1) | SNS topics should be encrypted at-rest using AWS KMS | 中 | - |
| [SNS.4](https://docs.aws.amazon.com/securityhub/latest/userguide/sns-controls.html#sns-4) | SNS topic access policies should not allow public access | 重大 | ○ |
| [SQS.1](https://docs.aws.amazon.com/securityhub/latest/userguide/sqs-controls.html#sqs-1) | Amazon SQS queues should be encrypted at rest | 中 | ○ |
| [SQS.3](https://docs.aws.amazon.com/securityhub/latest/userguide/sqs-controls.html#sqs-3) | SQS queue access policies should not allow public access | 重大 | ○ |
| [SSM.1](https://docs.aws.amazon.com/securityhub/latest/userguide/ssm-controls.html#ssm-1) | EC2 instances should be managed by AWS Systems Manager | 中 | ○ |
| [SSM.2](https://docs.aws.amazon.com/securityhub/latest/userguide/ssm-controls.html#ssm-2) | EC2 instances managed by Systems Manager should have a patch compliance status of COMPLIANT after a patch installation | 高 | ○ |
| [SSM.3](https://docs.aws.amazon.com/securityhub/latest/userguide/ssm-controls.html#ssm-3) | EC2 instances managed by Systems Manager should have an association compliance status of COMPLIANT | 低 | ○ |
| [SSM.4](https://docs.aws.amazon.com/securityhub/latest/userguide/ssm-controls.html#ssm-4) | SSM documents should not be public | 重大 | ○ |
| [SSM.6](https://docs.aws.amazon.com/securityhub/latest/userguide/ssm-controls.html#ssm-6) | SSM Automation should have CloudWatch logging enabled | 中 | ○ |
| [SSM.7](https://docs.aws.amazon.com/securityhub/latest/userguide/ssm-controls.html#ssm-7) | SSM documents should have the block public sharing setting enabled | 重大 | ○ |
| [StepFunctions.1](https://docs.aws.amazon.com/securityhub/latest/userguide/stepfunctions-controls.html#stepfunctions-1) | Step Functions state machines should have logging turned on | 中 | ○ |
| [Transfer.2](https://docs.aws.amazon.com/securityhub/latest/userguide/transfer-controls.html#transfer-2) | Transfer Family servers should not use FTP protocol for endpoint connection | 中 | ○ |
| [Transfer.3](https://docs.aws.amazon.com/securityhub/latest/userguide/transfer-controls.html#transfer-3) | Transfer Family connectors should have logging enabled | 中 | ○ |
| [Transfer.4](https://docs.aws.amazon.com/securityhub/latest/userguide/transfer-controls.html#transfer-4) | Transfer Family agreements should be tagged | 低 | - |
| [Transfer.6](https://docs.aws.amazon.com/securityhub/latest/userguide/transfer-controls.html#transfer-6) | Transfer Family connectors should be tagged | 低 | - |
| [WAF.1](https://docs.aws.amazon.com/securityhub/latest/userguide/waf-controls.html#waf-1) | AWS WAF Classic Global Web ACL logging should be enabled | 中 | ○ |
| [WAF.2](https://docs.aws.amazon.com/securityhub/latest/userguide/waf-controls.html#waf-2) | AWS WAF Classic Regional rules should have at least one condition | 中 | ○ |
| [WAF.3](https://docs.aws.amazon.com/securityhub/latest/userguide/waf-controls.html#waf-3) | AWS WAF Classic Regional rule groups should have at least one rule | 中 | ○ |
| [WAF.4](https://docs.aws.amazon.com/securityhub/latest/userguide/waf-controls.html#waf-4) | AWS WAF Classic Regional web ACLs should have at least one rule or rule group | 中 | ○ |
| [WAF.6](https://docs.aws.amazon.com/securityhub/latest/userguide/waf-controls.html#waf-6) | AWS WAF Classic global rules should have at least one condition | 中 | ○ |
| [WAF.7](https://docs.aws.amazon.com/securityhub/latest/userguide/waf-controls.html#waf-7) | AWS WAF Classic global rule groups should have at least one rule | 中 | ○ |
| [WAF.8](https://docs.aws.amazon.com/securityhub/latest/userguide/waf-controls.html#waf-8) | AWS WAF Classic global web ACLs should have at least one rule or rule group | 中 | ○ |
| [WAF.10](https://docs.aws.amazon.com/securityhub/latest/userguide/waf-controls.html#waf-10) | AWS WAF web ACLs should have at least one rule or rule group | 中 | ○ |
| [WAF.11](https://docs.aws.amazon.com/securityhub/latest/userguide/waf-controls.html#waf-11) | AWS WAF web ACL logging should be enabled | 低 | - |
| [WAF.12](https://docs.aws.amazon.com/securityhub/latest/userguide/waf-controls.html#waf-12) | AWS WAF rules should have CloudWatch metrics enabled | 中 | ○ |
| [WorkSpaces.1](https://docs.aws.amazon.com/securityhub/latest/userguide/workspaces-controls.html#workspaces-1) | WorkSpaces user volumes should be encrypted at rest | 中 | ○ |
| [WorkSpaces.2](https://docs.aws.amazon.com/securityhub/latest/userguide/workspaces-controls.html#workspaces-2) | WorkSpaces root volumes should be encrypted at rest | 中 | ○ |
:::

## 有効化手順

このセクションでは、Security Hub CSPM のコンソールから CRI Profile v2.2 標準を有効化する手順を紹介します。

1. Security Hub CSPM コンソールの左メニューから `セキュリティ基準` を開きます

![](/images/Screenshot_2026-10-15_at_10-04-34.png)

2. 一覧から `CRI Profile v2.2.0` を探し、`標準を有効化` をクリックします

![](/images/Screenshot_2026-10-15_at_10-04-57.png)

3. 確認ダイアログが表示されるので、`有効化` をクリックします

![](/images/Screenshot_2026-10-15_at_10-05-32.png)

4. 有効化後、しばらくするとコントロールのチェックが開始され、セキュリティスコアが表示されます

AWS CLI で有効化する場合は、以下のコマンドを実行します。

```bash
aws securityhub batch-enable-standards \
  --standards-subscription-requests '[{"StandardsArn":"arn:aws:securityhub:ap-northeast-1::standards/cri-profile/v/2.2.0"}]' \
  --region ap-northeast-1
```

:::message
Security Hub CSPM の中央設定（Central configuration）を利用している場合は、委任管理者アカウントの設定ポリシーで CRI Profile v2.2 標準を有効化することで、組織内のアカウント・リージョンに一括で適用できます。
:::

## まとめ

今回は、Security Hub CSPM に追加された CRI Profile v2.2 標準について整理しました。

CRI Profile v2.2 標準の 404 個のコントロールのうち、316 個は FSBP と共通です。FSBP だけを有効化している環境であれば、新たに評価対象になるのは CloudWatch アラームや IAM のパスワードポリシー、バックアップ・マルチ AZ などを中心とした 88 個になります。findings には CRI Profile の診断ステートメント ID も入るので、CRI Profile をベースに自己評価をしている金融機関にとっては、AWS 側の設定状況を確認する材料として使いやすいと思います。

ただし、Security Hub CSPM がチェックするのは自動で判定できる一部の要件だけです。CRI Profile への準拠を目指す場合は、組織・運用面の評価と組み合わせて使うことになります。

金融機関や、金融機関向けにサービスを提供している方は、まず 1 つのアカウントで有効化して、FSBP との差分の 88 個がどのくらい FAILED になるかを見てみるところから始めるのがよさそうです。

この記事がどなたかの役に立つと嬉しいです。
