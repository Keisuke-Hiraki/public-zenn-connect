---
title: "DevOps Agentに『脆弱性のあるパッケージを直して』と頼んだら、SSM Run Commandでアップグレードしてくれた話"
emoji: "📦"
type: "tech"
topics: ["aws", "devopsagent", "ssm", "security", "guardduty"]
published: true
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

これまで 2 回、AWS DevOps Agent と GuardDuty を連携させた検証記事を書いてきました。

https://zenn.dev/cscloud_blog/articles/devops-agent-guardduty-integration  
https://zenn.dev/cscloud_blog/articles/devops-agent-guardduty-directed-actions

前回の記事では、エージェントアクション（Directed Actions）によってセキュリティグループの書き換えやスナップショット作成といった「封じ込め」まで DevOps Agent に代行させられることを確認しました。

検証したのは EC2 / ネットワーク系の操作が中心だったので、今回は運用でもよくある「OS パッケージの脆弱性をアップグレードする」というシナリオを試してみました。

結論を先に言うと、**本当にアップグレードしてくれました**。  
チャットで「このパッケージ、脆弱性のある古いバージョンのままだから直して」と頼んで承認するだけで、実際に CVE のあるパッケージが最新版に上がるところまで、思っていたよりすんなり動きました。

## この記事の4行まとめ

:::message

- `ssm:SendCommand`（SSM Run Command）は DevOps Agent の Directed Actions のサポート対象アクションに含まれており、チャットで依頼して承認するだけで、実在する CVE を持つパッケージのアップグレードを実行できた
- 対象インスタンス 1 台・特定の Run Command ドキュメントだけに絞った最小権限の Elevated Role でも問題なく機能する
- 実行後は CloudTrail に承認したオペレーターの識別情報付きで記録され、誰が何を承認して何が実行されたかを追跡できる
- GuardDuty の自律調査（DNS 系の検知）からはパッケージ脆弱性への言及は出てこないが、これは検知の性質上当然で、チャットで直接依頼すれば問題なく実行できる

:::

## 検証したいこと

前回までの検証で、DevOps Agent のエージェントアクションが `ec2:ModifyInstanceAttribute` や `ec2:CreateSnapshot` といった EC2 / ネットワーク系の操作を代行できることは確認済みでした。今回はこれをもう一段踏み込んで、次を確認します。

- `ssm:SendCommand` は Directed Actions のサポート対象アクションに含まれているか
- 含まれているなら、実際にインスタンス内の脆弱性のあるパッケージを最新版にアップグレードできるか

「サポート対象アクションかどうか」は、前回記事で説明した通りコンソールの `View Supported Actions` 一覧でしか確認できず、公式ドキュメントにも一覧の記載はありません。今回も実際にチャットで依頼して挙動を見る、という力技での検証です。

## やってみた

前回記事の検証環境（VPC・EC2・Elevated Role・permissions boundary）は検証後にすべて削除していたため、今回は最小構成で作り直しました。

```
VPC（パブリックサブネット、IGW あり）
└── EC2 (t3.micro / AL2023 / SSM 管理、Project タグ付き・使い捨て)

DevOps Agent Agent Space
└── aws association（monitor account、Elevated Role を新規登録）
```

前回はプライベートサブネット＋ NAT ＋ SSM VPC エンドポイントという構成でしたが、今回は検証を素早く回したかったので、パブリックサブネットに SSM 管理対象の EC2 を 1 台立てるだけの簡易構成にしています。

### Elevated Role は最小権限で作成

前回記事では管理ポリシー `AIDevOpsAgentActionsPolicy`（ほぼ全アクション許可）＋ ABAC な permissions boundary という構成でしたが、今回は検証したい操作が `ssm:SendCommand` 1 つだけだったので、最初からカスタマー管理ポリシーで対象インスタンスと Run Command ドキュメントに絞った権限だけを付与しました。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowRunCommandOnTestInstanceOnly",
      "Effect": "Allow",
      "Action": "ssm:SendCommand",
      "Resource": [
        "arn:aws:ec2:ap-northeast-1:<account-id>:instance/i-0EXAMPLE00000000",
        "arn:aws:ssm:ap-northeast-1::document/AWS-RunShellScript",
        "arn:aws:ssm:ap-northeast-1::document/AWS-RunPatchBaseline"
      ]
    },
    {
      "Sid": "AllowCommandStatusRead",
      "Effect": "Allow",
      "Action": [
        "ssm:GetCommandInvocation",
        "ssm:ListCommandInvocations",
        "ssm:ListCommands",
        "ssm:DescribeInstanceInformation",
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

「封じ込めアクションを広く試したい」場合は前回のような ABAC が向いていますが、「特定の 1 アクションが使えるかを検証したい」だけなら、最初からリソースを絞ったカスタマーポリシーの方がシンプルで安全だと思います。Elevated Role の信頼ポリシーは前回と同じ（`aidevops.amazonaws.com` に `sts:AssumeRole` / `sts:SetSourceIdentity` / `sts:TagSession` を許可）です。

### あえて脆弱性のあるバージョンに落とした

素の Amazon Linux 2023 の最新 AMI はパッケージも最新なので、そのままだと「アップグレードする対象」がありません。そこで検証用に `expat`（XML パーサライブラリ）を意図的に古いバージョンへダウングレードしました。

```shell
$ rpm -q expat
expat-2.8.3-1.amzn2023.0.1.x86_64

$ dnf downgrade -y expat-2.5.0-1.amzn2023.0.4
（略）
Downgraded:
  expat-2.5.0-1.amzn2023.0.4.x86_64
```

`expat` の 2.5.0 系には CVE-2023-52425（CVSS 7.5、High）などの既知の脆弱性があります。緊急対応が必要な Critical ではないものの、実運用でも「そういえばまだ上げてなかった」となりがちな、非クリティカルな脆弱性の典型例として選びました。依存関係の都合で `python3` / `python3-libs` も一緒に古いバージョンへ引き戻されましたが、動作自体に問題はありませんでした。

## チャットで頼んだら、本当に直してくれた

コンソールのチャットで、対象インスタンスの脆弱性を具体的に伝えて依頼してみます。

```
インスタンス i-0EXAMPLE00000000 で expat パッケージが脆弱性のある古いバージョン
(expat-2.5.0-1.amzn2023.0.4、CVE-2023-52425 など)のままになっています。
SSM Run Command (AWS-RunShellScript) を使って `dnf upgrade -y expat python3 python3-libs`
を実行し、最新バージョンにアップグレードしてください。
```

![](/images/Screenshot_2026-09-17_at_15-00-54.png)

すると承認パネルがきちんと表示されました。ツール `use_aws`、オペレーション `ssm:send_command`、対象パラメータ（`InstanceIds` / `DocumentName` / `Parameters`）に加えて、リスク評価・ブラストラディウス・ロールバック手順まで前回記事で見たのと同じ形式で提示されます。ここで初めて「あ、本当にこの CVE を認識した上で、具体的な実行計画まで組み立ててるんだ」というのが実感できて、地味に感動しました。

承認すると、数秒で実行が完了しました。実行前後のパッケージバージョンを比較すると、実際にアップグレードされていることが確認できます。

| パッケージ | 実行前 | 実行後 |
| --- | --- | --- |
| expat | 2.5.0-1.amzn2023.0.4 | 2.8.3-1.amzn2023.0.1 |
| python3 | 3.9.16-1.amzn2023.0.9 | 3.9.25-1.amzn2023.0.9 |
| python3-libs | 3.9.16-1.amzn2023.0.9 | 3.9.25-1.amzn2023.0.9 |

![](/images/Screenshot_2026-09-16_at_00-20-08.png)

CloudTrail にも `ssm:SendCommand` の実行が記録され、`sourceIdentity` は前回記事と同じ `op.<operator>.apr.<approvalId>` の形式で、承認したオペレーターの識別情報が付与されていました。

```
sourceIdentity: op.AROAXXXXXXXXXXXXXXXXX-<name>@<masked>.apr.01a0XXXX-XXXX
```

実行主体が人間の手作業から DevOps Agent に置き換わっただけで、承認という最後の踏み込みは変わらず人間側に残っていますが、実際に手を動かす部分（対象を特定し、正しいコマンドを組み立て、実行し、結果を確認する）を丸ごと任せられるのは、思っていたより実用性が高いと感じました。

最小権限の Elevated Role（対象インスタンス 1 台・ドキュメント 2 種類のみ許可）でも、承認フローや実行結果に特に問題は見られませんでした。検証用の広い権限を用意しなくても、「このインスタンスのこの操作だけ」という粒度でスコープを絞って安全に試せる、というのも実務的には嬉しいポイントです。

## まとめ

- `ssm:SendCommand` は DevOps Agent の Directed Actions のサポート対象アクションに含まれていて、チャットで依頼 → 承認パネルで確認 → 承認、という流れで実際に CVE のあるパッケージをアップグレードできた
- 対象インスタンス・ドキュメントを絞った最小権限の Elevated Role でも問題なく機能する。「特定の 1 アクションだけ試したい」ケースでは、前回記事の ABAC boundary よりシンプルな選択肢になる
- 実行結果は CloudTrail に承認者の識別情報付きで記録されるため、「誰が何を承認して、何が実行されたか」を後から追跡できる
- GuardDuty の DNS 系検知からの自律調査では、OS パッケージの脆弱性対応という提案は出てこない。これは検知の性質上想定通りで、パッケージ対応はチャットで直接依頼するのが現実的な使い方

セキュリティグループの変更やスナップショット作成に続いて、SSM Run Command 経由の運用作業まで「チャットで頼んで承認するだけ」で完結する範囲に入ってきました。深夜に叩き起こされたオペレーターが、コンソールを開いてコマンドを打つ代わりに、チャットで一言頼んで承認ボタンを押すだけで済む場面が着実に増えていきそうです。

攻撃の予兆から悪用されるリスクを未然に防ぐアクションのハードルがここまで減るのはかなり嬉しいと思います。

この記事がどなたかの役に立つと嬉しいです。
