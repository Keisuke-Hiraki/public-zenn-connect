---
title: "Security Hubの新規コントロールのSSM.7による、SSMドキュメントのブロックパブリック共有を一括で全リージョン適用してみた"
emoji: "🔒"
type: "tech"
topics: ["aws", "securityhub", "ssm", "cloudformation"]
published: true
publication_name: cscloud_blog
published_at: 2025-07-18 07:00
---
:::message alert
**追記（2026年10月21日）**: その後 CloudFormation に `AWS::SSM::ServiceSetting` リソースタイプが追加され、東京リージョンでも利用できるようになりました。
CloudFormation StackSets を使って Organizations 配下の全アカウント・全リージョンへ一括適用する方法を後半の「追記: CloudFormation StackSetsで全アカウント・全リージョンに適用する」に追加しています。
:::

こんにちは、CSCの平木です！

Security Hubを運用している界隈では少しざわつきましたが、
先日、Security Hubの新規コントロールにSSM.7が追加されました。

https://blog.denet.co.jp/security-hub-ssm7/?doing_wp_cron=1752822300.2307579517364501953125

こちらはCriticalで検知されるため、
一括で適用できるコマンドを調べてみました。

## 早速コマンド

下記コマンドをCloudShellなど任意のシェル環境から実行いただければ全リージョンで一括で適用できます。

```
for region in $(aws ec2 describe-regions --query "Regions[].RegionName" --output text)
do
  if aws ssm update-service-setting \
    --setting-id /ssm/documents/console/public-sharing-permission \
    --setting-value Disable \
    --region ${region} 2>/dev/null; then
    echo "✅ 処理完了: ${region}"
  else
    echo "⚠️ スキップ: ${region}"
  fi
done
```

## 追記: CloudFormation StackSetsで全アカウント・全リージョンに適用する

このセクションでは、複数アカウントをまとめて対処したい場合に向けて、CloudFormation StackSets で Organizations 配下の全メンバーアカウント・全リージョンへ一括適用する方法を紹介します。

### AWS::SSM::ServiceSetting が利用可能に

`AWS::SSM::ServiceSetting` は SSM のサービス設定を CloudFormation で管理できるリソースタイプで、これを使うとSSM.7の設定もテンプレート化できます。

下記の記事執筆時点では東京リージョンで未提供だったため、カスタムリソースでの回避策が紹介されていました。

https://dev.classmethod.jp/articles/ssm7-block-public-sharing-cfn-stacksets/

2026年10月時点で確認したところ、東京リージョンを含むデフォルトで有効なすべてのリージョンで `AWS::SSM::ServiceSetting` が提供されていました（東京リージョンは2026年8月27日に追加）。
そのため、現在はカスタムリソースを使わずにシンプルなテンプレートで実現できます。

### テンプレート

適用するテンプレートは下記のとおりです。`ssm7-block-public-sharing.yaml` などの名前で保存してください。

```yaml:ssm7-block-public-sharing.yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: Block public sharing of SSM documents (Security Hub CSPM SSM.7)
Resources:
  SsmDocumentPublicSharingSetting:
    Type: AWS::SSM::ServiceSetting
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain
    Properties:
      SettingId: /ssm/documents/console/public-sharing-permission
      SettingValue: Disable
```

:::message alert
**`DeletionPolicy: Retain` は必ず付けてください。**
`AWS::SSM::ServiceSetting` は削除時に `ssm:ResetServiceSetting` を実行する仕様です。この設定のデフォルト値は `Enable`（パブリック共有を許可）なので、Retain を付けずにスタックを削除すると、パブリック共有が許可された状態に戻ってしまいます。
StackSets の場合、アカウントが対象 OU から外れたときやスタックインスタンスを削除したときにもスタックが削除されるため注意が必要です。
:::

### 注意点

StackSets での運用にあたり、事前に押さえておきたい注意点は下記のとおりです。

- **管理アカウント自身には適用されない**
  サービスマネージド型の StackSets は、Organizations 管理アカウントにはデプロイされません。管理アカウントは前半のコマンドで個別に設定してください。
- **メンバーアカウントで無効なリージョンは失敗する**
  メンバーアカウント側でオプトインリージョンが無効な場合や、SCP でリージョンを制限している場合、そのリージョンのスタックインスタンスは失敗します。デプロイ時は「障害耐性」の値を大きめに設定しておくと、一部が失敗してもデプロイ全体が止まらずに進みます。
- **既に手動で設定済みのアカウントにも適用できる**
  前半のコマンドなどで既に `Disable` にしているアカウントでも、同じ値で上書きされるだけなので問題ありません。

## おわりに

今回はSSM.7に対処するための全リージョンにおける一括設定を調べてみました。

手動の設定方法はこちらが参考になります。

https://dev.classmethod.jp/articles/securityhub-fsbp-remediation-ssm-7/

~~CloudFormationでの設定方法は見当たらなかったのでSatckSetsを活用したマルチアカウントでの設定は執筆時点では難しそうかと思いました。（もしあったらすみません）~~
**追記（2026年10月）**: 現在は `AWS::SSM::ServiceSetting` を使ってStackSetsでマルチアカウントに一括適用できるようになりました。
Terraformでは[aws_ssm_service_setting](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_service_setting)のリソースタイプがあるのでTerraform管理しているユーザーはこちらで実行してみるとよいです。

この記事がどなたかの役に立つと嬉しいです。

---

この記事は Qiita から移行しました。
