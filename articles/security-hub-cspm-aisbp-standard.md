---
title: "Security Hub CSPM に新しいセキュリティ標準の「AI Security Best Practices v1.0.0」が登場"
emoji: "🔒"
type: "tech"
topics: ["aws", "security", "securityhub", "bedrock", "sagemaker"]
published: true
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

AI ワークロードを AWS 上で構築するとき、各サービスのセキュリティ設定を網羅的に確認するのは意外と手間がかかります。  
SageMaker ノートブックのインターネットアクセス設定、Bedrock データソースへのカスタマー管理 KMS キーの適用、Bedrock AgentCore ゲートウェイの認証設定といった項目を、個別にドキュメントを調べながら確認する必要がありました。

2026年7月1日、Security Hub CSPM にこうした確認を自動化する新スタンダード「AI Security Best Practices v1.0.0」が追加されました。  
Amazon Bedrock・Bedrock AgentCore・Amazon SageMaker を対象にした 31 個のコントロールで、AI ワークロードのセキュリティベストプラクティスへの準拠状況を継続的に評価します。

https://aws.amazon.com/about-aws/whats-new/2026/06/aws-security-hub-cspm-ai-security/

:::message
**この記事の5行まとめ**

- Security Hub CSPM に「AI Security Best Practices v1.0.0」スタンダードが2026年6月30日に追加された
- Amazon Bedrock (1)、Bedrock AgentCore (7)、Amazon SageMaker (23) を対象とした 31 個のコントロールで構成される
- HIGH が 9 コントロール、MEDIUM が 22 コントロールで、ネットワーク分離・暗号化・アクセス制御・監査ログを幅広くカバー
- デフォルトでは無効のため、Security Hub コンソールまたは CLI から手動で有効化する必要がある
- Bedrock AgentCore 向けの 7 コントロールはすべて新規で、AI エージェント特有のリスク（ゲートウェイ認証・コードインタープリタのネットワーク制御・ブラウザセッション録画など）に対応している
:::

![](/images/Screenshot_2026-07-01_at_00-51-16.png)

![](/images/Screenshot_2026-07-01_at_00-53-31.png)

## AI Security Best Practices v1.0.0 とは

Security Hub CSPM のスタンダードは、特定のセキュリティフレームワークや AWS のベストプラクティスへの準拠状況を継続的に評価するコントロール集です。  

既存の AWS Foundational Security Best Practices (FSBP) が AWS サービス全般を幅広く対象にしているのに対し、今回追加された AI Security Best Practices は AI ワークロードに特化した内容になっています。

スタンダードは AWS セキュリティエキスパートが設計したもので、「ネットワーク分離」「保存時の暗号化」「転送時の暗号化」「アクセス制御」「可用性」「監査ログ」「プラットフォーム管理」といったセキュリティドメインを横断してカバーします。

スタンダードの ARN は以下の形式です（`{region}` は利用するリージョンのコードに置換）。

```
arn:aws:securityhub:{region}::standards/ai-security-best-practices/v/1.0.0
```

https://docs.aws.amazon.com/securityhub/latest/userguide/standards-ai-security.html

**デフォルトでは無効**のため、使用するには明示的に有効化する必要があります。対象サービスのコントロール数は下表のとおりです。

| サービス | コントロール数 |
|---|---|
| Amazon Bedrock | 1 |
| Amazon Bedrock AgentCore | 7 |
| Amazon SageMaker | 23 |
| 合計 | **31** |

## コントロール一覧

執筆時点でのコントロール一覧を重要度別にまとめます。  
HIGH が 9 コントロール、MEDIUM が 22 コントロールです。

### HIGH

| コントロールID | 内容 | サービス |
|---|---|---|
| [BedrockAgentCore.1](https://docs.aws.amazon.com/securityhub/latest/userguide/bedrockagentcore-controls.html#bedrockagentcore-1) | ランタイムを VPC ネットワークモードで構成すること | Bedrock AgentCore |
| [BedrockAgentCore.2](https://docs.aws.amazon.com/securityhub/latest/userguide/bedrockagentcore-controls.html#bedrockagentcore-2) | ゲートウェイのインバウンドリクエストに認証を必須にすること | Bedrock AgentCore |
| [BedrockAgentCore.5](https://docs.aws.amazon.com/securityhub/latest/userguide/bedrockagentcore-controls.html#bedrockagentcore-5) | カスタムブラウザにパブリックネットワークモードを使用しないこと | Bedrock AgentCore |
| [BedrockAgentCore.7](https://docs.aws.amazon.com/securityhub/latest/userguide/bedrockagentcore-controls.html#bedrockagentcore-7) | カスタムコードインタープリタにプライベートネットワーク構成を使用すること | Bedrock AgentCore |
| [SageMaker.1](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-1) | ノートブックインスタンスのダイレクトインターネットアクセスを無効にすること | SageMaker |
| [SageMaker.2](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-2) | ノートブックインスタンスをカスタム VPC 内で起動すること | SageMaker |
| [SageMaker.3](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-3) | ノートブックインスタンスへのルートアクセスを許可しないこと | SageMaker |
| [SageMaker.20](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-20) | モデル説明可能性ジョブ定義でネットワーク分離を有効にすること | SageMaker |
| [SageMaker.25](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-25) | モデル品質ジョブ定義でネットワーク分離を有効にすること | SageMaker |

### MEDIUM

| コントロールID | 内容 | サービス |
|---|---|---|
| [Bedrock.1](https://docs.aws.amazon.com/securityhub/latest/userguide/bedrock-controls.html#bedrock-1) | データソースをカスタマー管理 KMS キーで暗号化すること | Bedrock |
| [BedrockAgentCore.3](https://docs.aws.amazon.com/securityhub/latest/userguide/bedrockagentcore-controls.html#bedrockagentcore-3) | AgentCore Memory をカスタマー管理 KMS キーで暗号化すること | Bedrock AgentCore |
| [BedrockAgentCore.4](https://docs.aws.amazon.com/securityhub/latest/userguide/bedrockagentcore-controls.html#bedrockagentcore-4) | AgentCore ゲートウェイをカスタマー管理 KMS キーで暗号化すること | Bedrock AgentCore |
| [BedrockAgentCore.6](https://docs.aws.amazon.com/securityhub/latest/userguide/bedrockagentcore-controls.html#bedrockagentcore-6) | カスタムブラウザのセッション録画を有効にし S3 保存先を設定すること | Bedrock AgentCore |
| [SageMaker.4](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-4) | エンドポイントの本番バリアントの初期インスタンス数を 2 以上にすること | SageMaker |
| [SageMaker.5](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-5) | モデルでネットワーク分離を有効にすること | SageMaker |
| [SageMaker.8](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-8) | ノートブックインスタンスをサポート済みプラットフォームで実行すること | SageMaker |
| [SageMaker.9](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-9) | データ品質ジョブ定義でコンテナ間トラフィック暗号化を有効にすること | SageMaker |
| [SageMaker.10](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-10) | モデル説明可能性ジョブ定義でコンテナ間トラフィック暗号化を有効にすること | SageMaker |
| [SageMaker.11](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-11) | データ品質ジョブ定義でネットワーク分離を有効にすること | SageMaker |
| [SageMaker.12](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-12) | モデルバイアスジョブ定義でネットワーク分離を有効にすること | SageMaker |
| [SageMaker.13](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-13) | モデル品質ジョブ定義でコンテナ間トラフィック暗号化を有効にすること | SageMaker |
| [SageMaker.14](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-14) | モニタリングスケジュールでネットワーク分離を有効にすること | SageMaker |
| [SageMaker.15](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-15) | モデルバイアスジョブ定義でコンテナ間トラフィック暗号化を有効にすること | SageMaker |
| [SageMaker.16](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-16) | モデルのプライマリコンテナに VPC 内のプライベートレジストリを使用すること | SageMaker |
| [SageMaker.17](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-17) | フィーチャーグループのオフラインストアを KMS キーで暗号化すること | SageMaker |
| [SageMaker.18](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-18) | フィーチャーグループの標準ストレージを使うオンラインストアを KMS キーで暗号化すること | SageMaker |
| [SageMaker.19](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-19) | マルチコンテナ推論パイプラインに VPC 内のプライベートレジストリを使用すること | SageMaker |
| [SageMaker.21](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-21) | ノートブックインスタンスをカスタマー管理 KMS キーで暗号化すること | SageMaker |
| [SageMaker.22](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-22) | モニタリングスケジュールでコンテナ間トラフィック暗号化を有効にすること | SageMaker |
| [SageMaker.23](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-23) | 推論実験のインスタンスストレージボリュームをカスタマー管理 KMS キーで暗号化すること | SageMaker |
| [SageMaker.24](https://docs.aws.amazon.com/securityhub/latest/userguide/sagemaker-controls.html#sagemaker-24) | 推論実験のデータストレージをカスタマー管理 KMS キーで暗号化すること | SageMaker |

## セキュリティドメイン別の解説

31 個のコントロールを機能別に分類すると、どのような考え方で設計されているかが見えてきます。

### ネットワーク保護：AIリソースをインターネットから切り離す

HIGH 重要度のコントロールの大半がネットワーク保護に分類されています。  

Bedrock AgentCore については、ランタイム・カスタムブラウザ・カスタムコードインタープリタのいずれも「PUBLIC モードを使用しない」または「VPC モードを使用する」ことが求められます。

SageMaker ノートブックについては、FSBP にも SageMaker.1（ダイレクトインターネットアクセスの無効化）と SageMaker.2（カスタム VPC 内での起動）が含まれていますが、今回の AI Security Best Practices にも同じコントロールが採用されました。

BedrockAgentCore.7 では、カスタムコードインタープリタのネットワークモードとして `PUBLIC` だけでなく `SANDBOX` も不合格対象になっています。コードを実行する環境では、サンドボックスであっても VPC による制御が求められるという厳しい基準です。

### 暗号化：保存時と転送時の両面をカバー

暗号化に関するコントロールは「保存時（8個）」と「転送時（5個）」の 2 軸で構成されています。

保存時の暗号化コントロールはカスタマー管理 KMS キー（CMK）の使用を要求するものがほとんどで、AWS マネージドキーによるデフォルト暗号化では不合格となります。  

Bedrock AgentCore の Memory（BedrockAgentCore.3）と Gateway（BedrockAgentCore.4）が個別のコントロールで管理されている点は、AI エージェントが会話履歴やコンテキストといった機密性の高いデータを保持することを意識した設計です。

転送時の暗号化コントロール（SageMaker.9・10・13・15・22）はいずれも SageMaker のジョブ定義を対象にしており、複数コンテナを使う分散処理においてコンテナ間のトラフィックを暗号化するかどうかを確認します。

### アクセス制御：認証と権限の最小化

BedrockAgentCore.2 は「ゲートウェイのインバウンドリクエストに認証を設定すること」を求めています。  
認証が設定されていなければ、ネットワークアクセスさえあれば誰でも AI エージェントを呼び出せることになります。AI エージェントが外部から呼び出される構成において特に重要なコントロールです。

SageMaker.3 は「ノートブックインスタンスへのルートアクセスを許可しないこと」です。ルートアクセスが有効だと、ユーザーがシステムパッケージの変更やログの削除を行える可能性があり、最小権限の原則に反します。

SageMaker.16・19 は「コンテナイメージを VPC 内のプライベートレジストリから取得すること」を求めます。Docker Hub などのパブリックレジストリからのイメージ取得は、外部への依存が生まれ供給網攻撃（サプライチェーン攻撃）のリスクにつながるため、内部で管理するレジストリからの取得が推奨されます。

### 監査ログ：AI エージェントの操作を記録に残す

BedrockAgentCore.6 は「カスタムブラウザのセッション録画を有効にし、S3 の保存先を設定すること」を求めます。  
AI エージェントが自律的にブラウザを操作する場合、後から「どのページに何をしたか」を追跡できる手段が必要です。S3 への録画は、インシデント発生時の調査やコンプライアンス対応において根拠資料として機能します。

### 可用性・プラットフォーム管理

SageMaker.4 は「エンドポイントの本番バリアントの初期インスタンス数を 2 以上にすること」で、単一インスタンス構成による可用性リスクへの対応を求めます。  
AI 推論エンドポイントはリアルタイムのトラフィックを受けることが多く、冗長構成はサービス継続性の観点から欠かせません。

SageMaker.8 は「ノートブックインスタンスをサポート済みプラットフォームで実行すること」で、サポートが切れた古いランタイム上で動作するノートブックインスタンスに対して警告します。

## まとめ

AI Security Best Practices v1.0.0 は、Amazon Bedrock・Bedrock AgentCore・SageMaker を使う環境でのセキュリティ設定を継続的に可視化するための新スタンダードです。

特に Bedrock AgentCore 向けの 7 コントロールはすべて新規で、「ゲートウェイに認証を設定する」「コードインタープリタにパブリックモードを使わない」「ブラウザセッションを録画して S3 に保存する」といった、AI エージェント特有のリスクに対応した内容になっています。SageMaker の 23 コントロールは FSBP と重複するものも含まれていますが、「AI ワークロードとして SageMaker を使う場合に何を確認すべきか」を一つのスタンダードで把握できる点が便利です。

AI ワークロードを利用している環境でまずスタンダードを有効化し、現在の設定との差分を確認してみてください。
