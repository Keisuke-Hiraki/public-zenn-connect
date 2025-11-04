---
title: "Windows サーバで Trojan:EC2/DGADomainRequest.B を検知したら誤検知の疑いありだったため整理してみた"
emoji: "🪟"
type: "tech"
topics: ["aws", "windows", "guardduty"]
published: true
published_at: 2025-11-04 07:00
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

先日、Windows サーバにおいて Amazon GuardDuty で検知した [Trojan:EC2/DGADomainRequest.B](https://docs.aws.amazon.com/ja_jp/guardduty/latest/ug/guardduty_finding-types-ec2.html#trojan-ec2-dgadomainrequestb) を調査するという機会がありました。

すると、とある事象の組み合わせによって誤検知と疑われたため、今回はその詳細について見ていきます。

## 早速結論

先に知りたいという方に結論だけ箇条書きで記載します。
詳細を知りたい方は続きを読んでください。

- EC2Launch v2 の DNS サフィックスの継承の設定と、 Windows クライアントから DNS リクエストがランダムに送信される挙動が組み合わさることで DGA のドメインと似たリクエストが発生することがある
- 以下を実施することで誤検知が解消される可能性がある
  - EC2Launch v2 バージョンが `2.0.1643` 未満の場合は最新バージョンに引き上げる
  - EC2Launch v2 の 以下のいずれかの対応をする
    - レジストリ `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\Tcpip\Parameters\UseDomainNameDevolution` の値を `0` に設定（**要 OS 再起動**）
    - レジストリ `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\Dnscache\Parameters\DomainNameDevolutionLevel` の値を `1` に設定（**要サービス再起動**）
- 対処するのは、クライアント側の Windows インスタンスで実施
- ログ上で UDP 53 以外の記録であったり、名前解決に成功している場合はマルウェアを疑う必要がある

## 背景

まず今回の環境の構成についてです。

EC2 でホスティングされた Active Directory のドメインコントローラーの配下にいくつかの Windows サーバを管理しています。

今回はそのドメイン名を、 `example.co.jp` としておきます。

対象のアカウント全体で GuardDuty を有効化しており、EC2 マルウェアプロテクションも有効化していました。

![](/images/windows-dga-active-directory_2025-11-03-23-17-15.png)

## 事象

GuardDuty の運用する中である日、GuardDuty から Severity が High のものを検知したので確認すると今回のきっかけとなる `Trojan:EC2/DGADomainRequest.B` でした。

![](/images/windows-dga-active-directory_2025-11-03-23-17-26.png)
*画像はイメージです*

::: details JSON での結果を見たい人はこちらを展開して確認してください

ASFF のサンプルは以下です。

```json:ASFF
{
  "Action": {
    "ActionType": "DNS_REQUEST",
    "DnsRequestAction": {
      "Domain": "dglvrrerxokcxc.co.jp",
      "Protocol": "UDP",
      "Blocked": false
    }
  },
  "AwsAccountId": "123456789012",
  "AwsAccountName": "security-sample-account",
  "CompanyName": "Amazon",
  "CreatedAt": "2025-10-01T10:00:00.000Z",
  "Description": "The EC2 instance i-1234567890abcdef0 is querying algorithmically generated domains. Such domains are commonly used by malware and could be an indication of a compromised EC2 instance.",
  "FindingProviderFields": {
    "Types": [
      "TTPs/Command and Control/Trojan:EC2-DGADomainRequest.B"
    ],
    "Severity": {
      "Normalized": 60,
      "Label": "HIGH",
      "Product": 8
    }
  },
  "FirstObservedAt": "2025-10-01T09:30:00.000Z",
  "GeneratorId": "arn:aws:guardduty:ap-northeast-1:123456789012:detector/sampledetectorid1234567890",
  "Id": "arn:aws:guardduty:ap-northeast-1:123456789012:detector/sampledetectorid1234567890/finding/samplefindingid1234567890",
  "LastObservedAt": "2025-10-01T10:00:00.000Z",
  "ProcessedAt": "2025-10-01T10:05:00.000Z",
  "ProductArn": "arn:aws:securityhub:ap-northeast-1::product/aws/guardduty",
  "ProductFields": {
    "aws/guardduty/service/action/dnsRequestAction/blocked": "false",
    "aws/guardduty/service/archived": "false",
    "aws/guardduty/service/additionalInfo/value": "",
    "aws/guardduty/service/action/dnsRequestAction/domainWithSuffix": "dglvrrerxokcxc.co.jp",
    "aws/guardduty/service/resourceRole": "TARGET",
    "aws/guardduty/service/featureName": "DnsQueryLogs",
    "aws/guardduty/service/action/dnsRequestAction/vpcOwnerAccountId": "123456789012",
    "aws/guardduty/service/count": "5",
    "aws/guardduty/service/action/dnsRequestAction/domain": "dglvrrerxokcxc.co.jp",
    "aws/guardduty/service/additionalInfo/type": "default",
    "aws/guardduty/service/serviceName": "guardduty",
    "aws/guardduty/service/action/dnsRequestAction/protocol": "UDP",
    "aws/guardduty/service/detectorId": "sampledetectorid1234567890",
    "aws/guardduty/service/eventFirstSeen": "2025-10-01T09:30:00.000Z",
    "aws/guardduty/service/eventLastSeen": "2025-10-01T10:00:00.000Z",
    "aws/guardduty/service/action/actionType": "DNS_REQUEST",
    "aws/securityhub/FindingId": "arn:aws:securityhub:ap-northeast-1::product/aws/guardduty/arn:aws:guardduty:ap-northeast-1:123456789012:detector/sampledetectorid1234567890/finding/samplefindingid1234567890",
    "aws/securityhub/ProductName": "GuardDuty",
    "aws/securityhub/CompanyName": "Amazon"
  },
  "ProductName": "GuardDuty",
  "RecordState": "ACTIVE",
  "Region": "ap-northeast-1",
  "Resources": [
    {
      "Details": {
        "AwsEc2Instance": {
          "Type": "t3.medium",
          "VpcId": "vpc-0samplevpc123456789",
          "IpV4Addresses": [
            "172.31.20.100"
          ],
          "SubnetId": "subnet-0samplesubnet12345",
          "LaunchedAt": "2024-05-01T00:00:00.000Z",
          "IamInstanceProfileArn": "arn:aws:iam::123456789012:instance-profile/SampleInstanceProfileRole"
        }
      },
      "Id": "arn:aws:ec2:ap-northeast-1:123456789012:instance/i-1234567890abcdef0",
      "Partition": "aws",
      "Region": "ap-northeast-1",
      "Tags": {
        "Environment": "dev",
        "Name": "sample-ec2-instance"
      },
      "Type": "AwsEc2Instance"
    }
  ],
  "Sample": true,
  "SchemaVersion": "2018-10-08",
  "Severity": {
    "Label": "HIGH",
    "Normalized": 60,
    "Product": 8
  },
  "SourceUrl": "https://ap-northeast-1.console.aws.amazon.com/guardduty/home?region=ap-northeast-1#/findings?macros=current&fId=samplefindingid1234567890",
  "Title": "The EC2 instance i-1234567890abcdef0 queried a DGA domain name.",
  "Types": [
    "TTPs/Command and Control/Trojan:EC2-DGADomainRequest.B"
  ],
  "UpdatedAt": "2025-10-01T10:05:30.000Z",
  "Workflow": {
    "Status": "NEW"
  },
  "WorkflowState": "NEW"
}
```

OCSF のサンプルは以下です。

```json:OCSF
{
  "metadata": {
    "log_version": "2018-10-08",
    "product": {
      "feature": {
        "uid": "arn:aws:guardduty:ap-northeast-1:123456789012:detector/sampledetectorid1234567890",
        "name": "DnsQueryLogs"
      },
      "uid": "arn:aws:securityhub:ap-northeast-1::product/aws/guardduty",
      "name": "GuardDuty",
      "vendor_name": "Amazon",
      "version": null
    },
    "processed_time_dt": "2025-10-01T10:05:00.000000",
    "profiles": [
      "cloud",
      "datetime",
      "linux"
    ],
    "version": "1.1.0",
    "extensions": [
      {
        "name": "linux",
        "uid": "1",
        "version": "1.1.0"
      }
    ]
  },
  "time": 1762040730000,
  "time_dt": "2025-10-01T10:05:30.000000+00:00",
  "confidence_score": null,
  "message": null,
  "cloud": {
    "account": {
      "uid": "123456789012"
    },
    "region": "ap-northeast-1",
    "provider": "AWS"
  },
  "resource": null,
  "finding_info": {
    "created_time_dt": "2025-10-01T10:00:00.000000+00:00",
    "uid": "arn:aws:guardduty:ap-northeast-1:123456789012:detector/sampledetectorid1234567890/finding/samplefindingid1234567890",
    "desc": "The EC2 instance i-1234567890abcdef0 is querying algorithmically generated domains. Such domains are commonly used by malware and could be an indication of a compromised EC2 instance.",
    "title": "The EC2 instance i-1234567890abcdef0 queried a DGA domain name.",
    "modified_time_dt": "2025-10-01T10:05:30.000000+00:00",
    "first_seen_time_dt": "2025-10-01T09:30:00+00:00",
    "last_seen_time_dt": "2025-10-01T10:00:00+00:00",
    "related_events": null,
    "types": [
      "TTPs/Command and Control/Trojan:EC2-DGADomainRequest.B"
    ],
    "src_url": "https://ap-northeast-1.console.aws.amazon.com/guardduty/home?region=ap-northeast-1#/findings?macros=current&fId=samplefindingid1234567890"
  },
  "remediation": null,
  "compliance": null,
  "vulnerabilities": null,
  "resources": [
    {
      "type": "AwsEc2Instance",
      "uid": "arn:aws:ec2:ap-northeast-1:123456789012:instance/i-1234567890abcdef0",
      "cloud_partition": "aws",
      "region": "ap-northeast-1",
      "labels": [
        "Environment=dev",
        "Name=sample-ec2-instance"
      ],
      "data": {
        "AwsEc2Instance": {
          "Type": "t3.medium",
          "VpcId": "vpc-0samplevpc123456789",
          "IpV4Addresses": [
            "172.31.20.100"
          ],
          "SubnetId": "subnet-0samplesubnet12345",
          "LaunchedAt": "2024-05-01T00:00:00.000Z",
          "IamInstanceProfileArn": "arn:aws:iam::123456789012:instance-profile/SampleInstanceProfileRole"
        }
      },
      "criticality": null,
      "owner": null
    }
  ],
  "evidences": [
    {
      "data": {},
      "actor": null,
      "process": null,
      "api": null,
      "src_endpoint": null,
      "connection_info": {
        "protocol_name": "UDP",
        "direction_id": 2,
        "direction": "Outbound"
      },
      "dst_endpoint": null,
      "query": {
        "hostname": "dglvrrerxokcxc.co.jp"
      }
    }
  ],
  "class_name": "Detection Finding",
  "class_uid": 2004,
  "category_name": "Findings",
  "category_uid": 2,
  "severity_id": 4,
  "severity": "High",
  "activity_name": "Update",
  "activity_id": 2,
  "type_uid": 200402,
  "type_name": "Detection Finding: Update",
  "status": "New",
  "unmapped": {
    "ProductFields.aws/guardduty/service/action/dnsRequestAction/blocked": "false",
    "ProductFields.aws/guardduty/service/additionalInfo/type": "default",
    "Severity.Normalized": "60",
    "ProductFields.aws/securityhub/ProductName": "GuardDuty",
    "ProductFields.aws/guardduty/service/action/dnsRequestAction/domain": "dglvrrerxokcxc.co.jp",
    "ProductFields.aws/guardduty/service/serviceName": "guardduty",
    "Action.DnsRequestAction.Protocol": "UDP",
    "ProductFields.aws/guardduty/service/action/dnsRequestAction/vpcOwnerAccountId": "123456789012",
    "Action.ActionType": "DNS_REQUEST",
    "ProductFields.aws/guardduty/service/detectorId": "sampledetectorid1234567890",
    "ProductFields.aws/guardduty/service/eventFirstSeen": "2025-10-01T09:30:00.000Z",
    "Action.DnsRequestAction.Blocked": "false",
    "ProductFields.aws/guardduty/service/resourceRole": "TARGET",
    "FindingProviderFields.Severity.Product": "8",
    "FindingProviderFields.Types[]": "TTPs/Command and Control/Trojan:EC2-DGADomainRequest.B",
    "Sample": "true",
    "ProductFields.aws/guardduty/service/eventLastSeen": "2025-10-01T10:00:00.000Z",
    "RecordState": "ACTIVE",
    "ProductFields.aws/guardduty/service/archived": "false",
    "ProductFields.aws/guardduty/service/action/actionType": "DNS_REQUEST",
    "Severity.Product": "8",
    "FindingProviderFields.Severity.Normalized": "60",
    "WorkflowState": "NEW",
    "ProductFields.aws/guardduty/service/count": "5",
    "ProductFields.aws/securityhub/CompanyName": "Amazon",
    "AwsAccountName": "security-sample-account",
    "FindingProviderFields.Severity.Label": "HIGH",
    "ProductFields.aws/securityhub/FindingId": "arn:aws:securityhub:ap-northeast-1::product/aws/guardduty/arn:aws:guardduty:ap-northeast-1:123456789012:detector/sampledetectorid1234567890/finding/samplefindingid1234567890",
    "Action.DnsRequestAction.Domain": "dglvrrerxokcxc.co.jp"
  },
  "accountid": "123456789012",
  "region": "ap-northeast-1",
  "asl_version": null,
  "observables": [
    {
      "name": "resources[].uid",
      "value": "arn:aws:ec2:ap-northeast-1:123456789012:instance/i-1234567890abcdef0",
      "type": "Resource UID",
      "type_id": 10
    },
    {
      "name": "evidences[].query.hostname",
      "value": "dglvrrerxokcxc.co.jp",
      "type": "Hostname",
      "type_id": 1
    }
  ],
  "eventday": "20251001",
  "@timestamp": "2025-10-01T10:07:00.000000Z"
}
```

:::

この検知内容を見ると、EC2 インスタンス `i-1234567890abcdef0` が `dglvrrerxokcxc.co.jp` というドメイン名をクエリした結果、`Trojan:EC2/DGADomainRequest.B` が検知していることがわかります。

### Trojan:EC2/DGADomainRequest.B とは

今回登場した Trojan:EC2/DGADomainRequest.B とはどんな検知なのかを調べました。

公式ドキュメントには以下のように記載があります。

> この検出結果は、 AWS 環境のリスト化した EC2 インスタンスがドメイン生成アルゴリズム (DGA) のドメインをクエリしようとしていることを知らせるものです。EC2 インスタンスは侵害されている可能性があります。  
DGA は、大量のドメイン名を定期的に生成してコマンドアンドコントロール (C&C) サーバーとのランデブーポイントとするために使用されます。C&C サーバーは、ボットネットのメンバーにコマンドを発行するコンピュータであり、一般的なタイプのマルウェアに感染して制御されたインターネットのコネクテッドデバイスのコレクションです。ランデブーポイントの候補数が多いと、感染されたコンピュータは毎日これらのドメイン名の一部にアクセスしてアップデートやコマンドを受け取ろうとするため、ボットネットを効果的にシャットダウンすることが困難となります。  
参考： [GuardDuty EC2 の検出結果タイプ - Amazon GuardDuty](https://docs.aws.amazon.com/ja_jp/guardduty/latest/ug/guardduty_finding-types-ec2.html#trojan-ec2-dgadomainrequestb)

### ドメイン生成アルゴリズム（DGA）とは

ドメイン生成アルゴリズム（DGA: Domain Generation Algorithm）とは、マルウェアが C&C サーバー（C2 サーバー）と通信するために使用するドメイン名を動的に生成する技術です。

1 日に数千数万といった「ランダム文字列+TLD」のような存在しないドメインを生成しその中に C2 サーバーと通信できる存在するドメインを紛れ込ませることで、セキュリティシステムによる検知を回避しやすくします。

![](/images/windows-dga-active-directory_2025-11-03-23-25-43.png)
*引用： [ドメイン生成アルゴリズムとは| Akamai](https://www.akamai.com/ja/glossary/what-are-dgas)*

DGA は、マルウェアが感染したデバイスから C&C サーバーへの接続を確立するために使用されるため対処が必要となります。

## 調査

今回調査観点ポイントとして、以下 3 つのログを取得し調査しました。

- Windows イベントログ
- VPC フローログ
- DNS デバッグログ

### Windows イベントログ

Windows イベントログでは、Windows システム内で起こったイベントを記録しておいてくれる場所です。

検知時間帯において新規プロセスが動いていた場合はそのアプリケーションが疑わしいと思われるため調査します。

結論、今回有効化前に別の原因だと判明したため確認しませんでしたが、
もし再発した場合にはこちらのブログに追記しようと思います。

具体的にはイベント ID 4688 を確認することで特定可能です。

https://learn.microsoft.com/ja-jp/windows-server/identity/ad-ds/manage/component-updates/command-line-process-auditing

### VPC フローログ

VPC フローログでは、VPC 内のネットワークトラフィックをキャプチャしログとして保存できます。

今回、検知時間帯において Windows クライアントから 53 番ポートでのトラフィックを検知していることが確認できました。

この内容から、ドメインコントローラーだけでなくクライアント側の Windows サーバーも疑いの対象を広げました。

### DNS デバッグログ

DNS デバッグログでは、Windows の DNS クライアントが行った DNS クエリの詳細なログを取得できます。

https://learn.microsoft.com/ja-jp/previous-versions/windows/it-pro/windows-server-2003/cc759581(v=ws.10)?redirectedfrom=MSDN

今回 DNS デバッグログを確認していると以下のようなログの形式が確認できました。

```shell
2025/10/01 9:30:50 0D28 PACKET  00000292D65BCC80 UDP Rcv 10.143.100.80   3aee   Q [0001   D   NOERROR] A      (15)dglvrrerxokcxc(7)example(2)co(2)jp(0)
2025/10/01 9:30:50 0D28 PACKET  00000292D56DCD10 UDP Snd 10.143.0.2      5810   Q [0001   D   NOERROR] A      (15)dglvrrerxokcxc(7)example(2)co(2)jp(0)
2025/10/01 9:30:50 0D28 PACKET  00000292D5A0AD90 UDP Rcv 10.143.0.2      5810 R Q [8381   DR NXDOMAIN] A      (15)dglvrrerxokcxc(7)example(2)co(2)jp(0)
2025/10/01 9:30:50 0D28 PACKET  00000292D65BCC80 UDP Snd 10.143.100.80   3aee R Q [8381   DR NXDOMAIN] A      (15)dglvrrerxokcxc(7)example(2)co(2)jp(0)
2025/10/01 9:30:50 0D28 PACKET  00000292D6CCB920 UDP Rcv 10.143.100.80   cae2   Q [0001   D   NOERROR] A      (15)dglvrrerxokcxc(2)co(2)jp(0)
2025/10/01 9:30:50 0D28 PACKET  00000292D65BCC80 UDP Snd 10.143.0.2      7bf9   Q [0001   D   NOERROR] A      (15)dglvrrerxokcxc(2)co(2)jp(0)
2025/10/01 9:30:50 0D28 PACKET  00000292D76FD570 UDP Rcv 10.143.0.2      7bf9 R Q [8381   DR NXDOMAIN] A      (15)dglvrrerxokcxc(2)co(2)jp(0)
2025/10/01 9:30:50 0D28 PACKET  00000292D6CCB920 UDP Snd 10.143.100.80   cae2 R Q [8381   DR NXDOMAIN] A      (15)dglvrrerxokcxc(2)co(2)jp(0)
```

DNS デバッグログの読み方は以下ブログが大変参考になります。

https://qiita.com/urushibata/items/8728708e7737371e6ba1

このログを見ると、 `dglvrrerxokcxc.co.jp` というドメイン名のクエリと `dglvrrerxokcxc.example.co.jp` ドメインのクエリがあることが分かり、`example.co.jp`のサフィックスとして`co.jp`が付与されている？ように見えました。

## 要因

上記から誤検知を疑い調査を深め、AWS サポートも頼りながら進めていくと以下 2 点が結論として浮上しました。

### Windows 起動エージェント の DNS サフィックスの継承

1 つ目の要因について見ていきます。

EC2 における Windows AMI にはデフォルトで EC2 インスタンスのスタートアップ時にタスクを実行する Windows 起動エージェントと呼ばれるものがあります。  
この Windows 起動エージェントを使用すると Windows インスタンスがドメインの名前解決に使用する DNS サフィックスのリストを設定できます。

画面ではこんな感じに見えるようです。

![](/images/windows-dga-active-directory_2025-11-04-00-07-55.png)
*引用： https://docs.aws.amazon.com/ja_jp/AWSEC2/latest/UserGuide/ec2launch-v2-settings.html*

この Windows 起動エージェントの DNS サフィックスについて重要なポイントとして「ドメイン名の継承」というものを知っておく必要がありました。

#### ドメイン名の継承とは

公式ドキュメントには以下のように記載があります。

> ドメイン名の継承は Active Directory の動作であり、子ドメインのコンピュータが、完全修飾ドメイン名を使用せずに親ドメインのリソースにアクセスすることを可能にします。デフォルトでは、ドメイン名の継承は、ドメイン名の進行でノードが残り 2 つになるまで続きます。  
参考： [EC2 Windows 起動エージェントの DNS サフィックスを設定する - Amazon Elastic Compute Cloud](https://docs.aws.amazon.com/ja_jp/AWSEC2/latest/UserGuide/launch-agents-set-dns.html)

例えば今回のような`example.co.jp`の場合は`example.co.jp`と`co.jp`がデフォルトで継承されるとのことでした。  
要するに、`test.example.co.jp`へのリクエストが失敗した場合、`test.co.jp`という形でリクエストされます。

今回、DNS デバッグログで 2 種類見えたのはこれが要因のようでした。

### Windows DNS クライアントによるランダムな DNS リクエスト

2 つ目の要因について見ていきます。

Windows ではコンピュータが起動したときやネットワークプロパティが変更された場合に、ランダムな DNS リクエストを実行することがあるようです。

サーバやネットワークの検出などのために使用されるとのことで、今回の肝である DGA っぽいランダム性はここから出るものだと疑われます。

https://learn.microsoft.com/ja-jp/troubleshoot/windows-client/networking/dns-requests-random-network-properties-change

実際に当該時間帯に疑われるクライアントサーバにて停止起動が発生するタイミングがありました。

### ここまで整理

以上の 2 点から誤検知と疑われました。

整理すると以下のような感じです。

![](/images/windows-dga-active-directory_2025-11-04-00-41-07.png)

## 対処

ここから実際にどう対処するか記載します。

今回肝となる Windows サーバによるランダムな DNS リクエストについては止められないため、`co.jp`が継承されないようにドメインの継承の設定を見直します。

2020 年 6 月以降に作成された Windows サーバでは EC2Launch v2 というエージェントがインストールされているため、EC2Launch v2 を前提に記載します。

必要な作業は状況によって違います。

- EC2Launch v2 バージョンが `2.0.1643` 未満の場合は、最新バージョンに引き上げる（**要 OS 再起動**）
- EC2Launch v2 の 以下のいずれかの対応をする
  - 継承の動作を無効化させる
  - 継承のレベルを変更する

### EC2Launch v2 のバージョンアップ

ドメインの継承レベルの変更ができるようになったのは、EC2Launch v2 のバージョンが`2.0.1643`からのため、それより古いバージョンを利用している場合は最新のバージョンに更新する必要があります。

現在のバージョンを確認するには PowerShell で以下のコマンドを実行することで確認できます。

```powershell
& "C:\Program Files\Amazon\EC2Launch\EC2Launch.exe" version
```

インストール方法やバージョンをコントロールパネルで確認する方法などは以下ドキュメントから確認できます。

https://docs.aws.amazon.com/ja_jp/AWSEC2/latest/UserGuide/ec2launch-v2-install.html

### ドメインの継承の変更

続いてドメインの継承に関する設定を変更します。

変更する方法としては 2 通りあり、そもそもの継承の動作を無効化させるものと継承のレベルを変更するものです。

#### 継承の動作を無効化させる

継承の動作を無効化させたい場合は、レジストリを以下のように変更します。
- Key:`HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\Tcpip\Parameters\UseDomainNameDevolution`
- Value: `1`→`0` 

継承の動作を無効化することで、子ドメインの Windows サーバは明示的に指定した完全修飾ドメイン名を使用したクエリを実行することとなります。

このレジストリキーを変更した場合は、反映に OS の再起動が必要になりますので、ご注意ください。

#### 継承のレベルを変更する

継承のレベルを変更したい場合は、レジストリを以下のように変更します。
- Key: `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services\Dnscache\Parameters\DomainNameDevolutionLevel`
- Value: `2`→`指定したいレベルの数`

例えば今回のような`example.co.jp`のみ使用させたい場合は、`1`を指定します。

継承レベルを `1` に設定することで、子ドメインの Windows サーバは親ドメインのルートドメイン名のみを継承するようになります。

このレジストリキーの変更の反映にはサービスの再起動が必要になります。

PowerShell 上で以下のコマンドを実行することでサービス再起動が可能です。

```powershell
Restart-Service dnscache
```
https://learn.microsoft.com/en-us/answers/questions/2245481/2-dns-servers

ドメインの継承については以下を参照ください。

https://docs.aws.amazon.com/ja_jp/AWSEC2/latest/UserGuide/launch-agents-set-dns.html

## 参考

- [EC2 Windows 起動エージェントの DNS サフィックスを設定する - Amazon Elastic Compute Cloud](https://docs.aws.amazon.com/ja_jp/AWSEC2/latest/UserGuide/launch-agents-set-dns.html)
- [DNS 要求は、起動後またはネットワーク プロパティの変更後にランダムに表示される - Windows Client | Microsoft Learn](https://learn.microsoft.com/ja-jp/troubleshoot/windows-client/networking/dns-requests-random-network-properties-change)
- [EC2Launch v2 のバージョン履歴 - Amazon Elastic Compute Cloud](https://docs.aws.amazon.com/ja_jp/AWSEC2/latest/UserGuide/ec2launchv2-versions.html)
- [EC2Launch v2 の最新バージョンのインストール - Amazon Elastic Compute Cloud](https://docs.aws.amazon.com/ja_jp/AWSEC2/latest/UserGuide/ec2launch-v2-install.html)
- [GuardDuty EC2 の検出結果タイプ - Amazon GuardDuty](https://docs.aws.amazon.com/ja_jp/guardduty/latest/ug/guardduty_finding-types-ec2.html#trojan-ec2-dgadomainrequestb)

## おわりに

以上、Windows サーバで Trojan:EC2/DGADomainRequest.B を検知したら誤検知の疑いありだったため整理してみた、でした。

今回は、ポート UDP　53 かつ DNS デバッグログの Rev が NXDOMAIN であったため誤検知を疑うことができましたがこれが別のプロトコルだったり、名前解決が成功していた場合にはマルウェアの疑いが高まりますのでご注意ください。

この記事がどなたかの役に立つと嬉しいです。