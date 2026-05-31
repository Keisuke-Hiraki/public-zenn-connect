---
title: "Security Hubの新規コントロールのSSM.7による、SSMドキュメントのブロックパブリック共有を一括で全リージョン適用してみた"
emoji: "🔒"
type: "tech"
topics: ["aws", "securityhub", "ssm"]
published: true
publication_name: cscloud_blog
published_at: 2025-07-18 07:00
---
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

## おわりに

今回はSSM.7に対処するための全リージョンにおける一括設定を調べてみました。

手動の設定方法はこちらが参考になります。

https://dev.classmethod.jp/articles/securityhub-fsbp-remediation-ssm-7/

CloudFormationでの設定方法は見当たらなかったのでSatckSetsを活用したマルチアカウントでの設定は執筆時点では難しそうかと思いました。（もしあったらすみません）
Terraformでは[aws_ssm_service_setting](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_service_setting)のリソースタイプがあるのでTerraform管理しているユーザーはこちらで実行してみるとよいです。

この記事がどなたかの役に立つと嬉しいです。

---

この記事は Qiita から移行しました。
