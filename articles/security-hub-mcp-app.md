---
title: "Security Hub MCP App × Claude Desktop の機能が追加されたので使い所を考えてみた"
emoji: "🔍"
type: "tech"
topics: ["aws", "securityhub", "mcp", "claude", "security"]
published: true
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

皆さんは Security Hub の Finding、severity の高い順に対応していますか？

2026 年 7 月 27 日に「AWS Security Hub MCP App」が Preview として公開されました。

https://aws.amazon.com/jp/about-aws/whats-new/2026/07/aws-security-hub-mcp-app/

MCP サーバーが 1 つ増えたという話ではなく、セキュリティ運用の中でこれがどこに効くのかを知りたかったので、実在するマルチアカウント組織に対して提供されている 8 つのツールを一通り叩いてみました。

この記事では、実測した結果をもとに「どんな活用イメージがあるのか」「実務で何が変わるのか」を整理します。  
機能の一覧紹介ではなく、Preview を触った一次検証レポートとしてお伝えできればと思います。

なお、インストールや設定といったセットアップ手順そのものは、別の Scrap に検証記録としてまとめていますのでご興味ありましたら見てみてください。

https://zenn.dev/khirasan/scraps/d8a6beffdf3f2c

:::message
**この記事の 6 行まとめ**
- Security Hub MCP App はローカルで動作する read-only な MCP サーバーで、追加費用はかからない（現時点では Claude Desktop 専用）
- Security Hub v2 が既に相関させたデータへの到達コストをほぼゼロ
- 効果があるのは「深く 1 件を調べる」用途で、全件棚卸しや月次レポートの自動生成には向かない
- Exposure Finding の severity は「対応の優先度」ではなく「構成上のリスクの型」であり、`resource_detail` と突き合わせて初めて対応順序が決まる
- Azure の Finding は一覧・相関・攻撃経路までは追えるが、`network_path` は仕様上 AWS 前提でマルチクラウド対応が非対称
- 現時点は「AI に判断を任せる」段階ではなく「AI に材料を集めさせて人間が判断する」段階
:::

## Security Hub MCP App とは

前提として 4 点だけ押さえておけば十分です。

- **実体はローカル MCP サーバー**です。手元のマシン上で動作し、既存の AWS credential chain を使って Security Hub API を直接叩きます。サーバー自体は認証情報を保持しません
- **現時点では Claude Desktop 専用**です。デスクトップ拡張機能という形で提供されているため、Claude Code からは利用できません
- **提供される 8 つのツールはすべて read-only** です。環境に変更を加えることはできません
- 1 回のツールコールが**二重の出力**を返します。エージェントが推論に使うテキスト要約と、同じ会話内にレンダリングされる対話型ビジュアライゼーションの 2 つです

Security Hub が有効なすべての AWS 商用リージョンで利用可能で、追加費用はかかりません。

https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-v2-mcp-app.html

![](/images/Screenshot_2026-07-28_at_13-40-14.png)
*Claude Desktop の「ディレクトリ」から見た Security Hub MCP App*

:::message alert
セットアップ手順そのものは前述の Scrap にまとめていますが、組織で使う場合の注意点を 2 つだけ補足しておきます。

- Claude の Team / Enterprise プランでは、この手のデスクトップ拡張機能は管理者によるアローリスト登録を経ないとインストールできないため、事前に申請フローを踏んでおく必要があります
- 公開直後のバンドルには不具合がありました。AWS サポートに改善案を連携したところ修正版の 0.2.1 で解消され、今回の検証時点では `manifest.json` を見ると 0.3.2 まで進んでいたので、Preview を触る場合はまずバンドルを最新にしておくのが安全です
:::

## この機能で何が嬉しいのか
 
実際に試して感じた活用イメージは以下の 6 つです。  
それぞれ本記事の中で、実際のレスポンスと併せて掘っていきます。

| 活用イメージ | 実務で何が変わるか |
|---|---|
| エスカレーションの一次解析 | CRITICAL 1 件の相関シグナル 9 件・攻撃経路・修復手順を数分で構造化できる |
| 顧客向け提案・報告資料の下書き | 攻撃経路を日本語のリスクストーリーに変換できる |
| CVE トリアージの根拠づけ | 「今すぐ対応でなくてよい理由」をスコアの実測値で説明できる |
| 重大度の妥当性検証 | MEDIUM の EC2 が実は停止中の開発機だと切り分けられる |
| 新人向けのトリアージ教材 | 「severity で終わらせず実体まで下りる」思考の流れを会話ログとして残せる |
| マルチクラウド横断の確認 | AWS と Azure の Exposure が同じ一覧に並び、相関・攻撃経路まで同じ深さで追える（ネットワーク経路の可視化のみ AWS 前提） |

Security Hub v2 の Exposure Finding は、脆弱性・設定不備・到達可能性・権限影響を**すでに相関させた状態**で持っています。  
MCP App は、**その相関済みデータへの到達コストをほぼゼロにしたこと**だと考えています。

従来は Security Hub・IAM・EC2・Inspector・RDS と 5 画面を横断して、人間が突き合わせていた判断です。  
それが 1 〜 2 ターンの会話で済むようになります。

相関そのものを作っているのは Security Hub 側であって AI ではありません。  
AI がやっているのは取得・要約・文脈付けです。「AI が攻撃経路を見つけてくれる」という理解で導入すると、期待値がズレてしまいます。

## 活用イメージ①: エスカレーションの一次解析と報告資料の下書き

1 つ目の活用イメージは、アラートが上がってきたときの一次解析です。

CRITICAL 1 件を例に、`top_exposures` → `finding_detail` → `attack_path` → `recommendation` の流れを追ってみました。

`top_exposures` で最上位に出ていたのは、  
`Potential Unauthorized Access: IAM user has unrotated access keys, has weak password policies, and has MFA disabled with high-impact effective permissions`   
というタイトルの CRITICAL Finding です。  
対象は `AWS::IAM::User` で、traitCounts は `Impact: 1` / `Misconfiguration: 8` となっていました。

### 「原因」と「背景」が分けて返ってくる

`finding_detail` ツールを 1 回叩くと、以下がまとめて返ってきました。

- ヘッダ情報（title / severity / accountId / findingTypes / createdTime など）
- `findingTypes`: `Exposure/Potential Privilege Escalation/Valid Cloud Credentials`
- OCSF の `impact: High` / `likelihood: High`（severity とは別軸で持っている点がポイントです）
- 相関シグナル 9 件
- `resource_relationship`（ノード 9・エッジ 8 のグラフ構造）
- `remediation.kb_article_list`（trait 別の公式ドキュメントリンク）

![](/images/Screenshot_2026-08-20_at_01-29-27.png)
*finding_detail で得られる詳細ビュー*

説明資料を作る立場から見て一番効いたのは、相関シグナルの trait が 2 種類に分かれていることでした。

```json
[
  {
    "title": "MFA should be enabled for all IAM users that have a console password",
    "type": "Finding",
    "traits": [
      {
        "category": "Misconfiguration",
        "name": "The IAM user does not have MFA enabled",
        "type": "Contributing Trait"
      }
    ]
  },
  {
    "title": "AWS::IAM::Group TestUserGroup01",
    "type": "ResourceConfiguration",
    "traits": [
      {
        "category": "Misconfiguration",
        "name": "The IAM user has an administrative access policy",
        "type": "Contextual Trait"
      }
    ]
  }
]
```

`Contributing Trait` はこの Exposure を成立させている要因で、MFA 無効・パスワードポリシー脆弱・アクセスキー未ローテーションなどが該当します。  
一方の `Contextual Trait` は文脈情報で、AdministratorAccess ポリシーの付与や未使用クレデンシャルなどが入ります。

顧客への報告資料は、たいてい「何が原因でこうなったのか」と「周辺状況として何があるのか」を書き分ける必要があります。  
この区別が API レスポンスの時点で付いているので、そのまま資料の構成に流せます。

地味なところですが、実務で一番効いた部分でした。

### 攻撃経路は「なぜ危険か」まで含めて取りに行く必要がある

`attack_path` を叩くと、以下のような経路がグラフとして返ってきます。

![](/images/Screenshot_2026-08-20_at_01-30-18.png)
*attack_path で得られたグラフ構造*

```
IAM User (TestUser01)
  ├─ Is in Account ──────────→ Account 111122223333
  ├─ Is attached to Group ───→ IAM Group (TestUserGroup01)
  │                              └─ Is attached to Policy → AdministratorAccess
  └─ Has access to ──────────→ RDS DBClusterSnapshot × 5
```

ノードには `kind`（`identity` / `data`）が付くため、ID が権限を経てデータに到達している構図はひと目で分かります。

ただし、ここに落とし穴がありました。  
返ってきたエッジを見ると、ラベルは `Has access to` だけで、severity も全部 `info` になっています。

```json
{
  "edges": [
    { "from": "Node0", "to": "Node1", "label": "Is in Account",          "severity": "info" },
    { "from": "Node0", "to": "Node2", "label": "Is attached to Group",   "severity": "info" },
    { "from": "Node2", "to": "Node3", "label": "Is attached to Policy",  "severity": "info" },
    { "from": "Node0", "to": "Node4", "label": "Has access to",          "severity": "info" },
    { "from": "Node0", "to": "Node5", "label": "Has access to",          "severity": "info" }
  ]
}
```

これだけでは「アクセスできる」という事実しか分からず、**なぜ危険なのかが説明できません。**  
エッジに severity の強調もないため、危険な経路が視覚的に浮き上がってこないという課題もありそうです。

ところが、同じ Finding の `finding_detail` の `raw` 側を読むと、まったく同じエッジに `privilege_attack_info_list` が入っていました。

```json
{
  "uid": "edge_Node0_Node4",
  "name": "AWS::IAM::User->AWS::RDS::DBClusterSnapshot",
  "relation": "Has access to",
  "labels": ["capability_advancing_1"],
  "source": "Node0",
  "target": "Node4",
  "privilege_attack_info_list": [
    {
      "attack": {
        "tactic": { "name": "Exfiltration", "uid": "TA0010" },
        "technique": { "name": "Data Transfer to Cloud Account", "uid": "T1537" }
      },
      "privilege_info_list": [
        { "name": "rds:CopyDBClusterSnapshot" },
        { "name": "rds:RestoreDBClusterFromSnapshot" },
        { "name": "rds:RestoreDBInstanceFromDBSnapshot" }
      ]
    }
  ]
}
```

MITRE ATT&CK の `TA0010 Exfiltration` / `T1537 Data Transfer to Cloud Account`（攻撃手法の分類体系における「データ持ち出し」の戦術・技術）と、`rds:CopyDBClusterSnapshot` などの具体的な権限名は、**raw の中にしか存在しません。**

権限の終着点も `resource_relationship` のノード側に明示されています。

```json
{ "name": "Node3", "type": "AWS::IAM::Policy", "uid": "arn:aws:iam::aws:policy/AdministratorAccess" }
```

つまり、報告資料の下書きに使うのであれば `attack_path` 単体では足りず、`finding_detail` の raw と併用する必要があるということになります。  
これが今回の検証で得た一番の実務ノウハウでした。

両方を揃えると、日本語のリスクストーリーまで一気に書けます。  

```
MFA 無効・パスワードポリシー脆弱・アクセスキー未ローテーションという要因が重なっている。この IAM ユーザーは AdministratorAccess を持つため、侵害された場合は RDS スナップショットを別アカウントにコピー・復元してデータを持ち出せる（T1537）
```

といった具合です。

「AdministratorAccess が付いているので危険です」で終わる報告と、経路と手法まで書いた報告では、説明力がまったく違ってきます。

締めに `recommendation` を叩くと、UI ではなくテキスト（Markdown）が返ってきました。

```json
{
  "desc": "To remediate this finding, see the documentation. We recommend that you remediate traits in the order listed below.",
  "markdown": "[User MFA Disabled](...)\n\n[Weak Password Policies](...)\n\n[Unrotated Access Keys](...)\n\n[Has Capability Advancing Path](...)",
  "source": "live"
}
```

**修復推奨順にリンクが並ぶ**ので、対応手順の下書きとしてそのまま使えます。

ここまでで、従来はコンソールを Security Hub → IAM → RDS と行き来していた作業が数分に収まりました。

## 活用イメージ②: 重大度を疑う - MEDIUM の EC2 は本当に MEDIUM なのか

2 つ目は、今回一番ピンときた活用イメージです。  
Finding の severity を鵜呑みにせず、**妥当性そのものを検証する**という使い方です。

`top_exposures` に `Potential Resource Hijacking: EC2 instance has software vulnerabilities with high-impact effective permissions` という MEDIUM の Finding が出ていました。  
これを `correlated_finding_detail` → `finding_overview` → `resource_detail` の順に掘っていきます。

### CVE 一覧は取れるが、そこに優先順位はない

まず、親 Finding の `traits` にある `Vulnerability` を指定して `correlated_finding_detail` を実行すると、traitCounts どおり 10 件の CVE が返ってきました。  
以下は、そのうち先頭 3 件の抜粋です。

```json
{
  "traitName": "Vulnerability",
  "findings": [
    { "id": "007ad0cb...", "title": "CVE-2026-43043 - kernel, kernel-libbpf and 1 more", "severity": "", "status": "" },
    { "id": "03c4a2c5...", "title": "CVE-2026-42010 - gnutls",                          "severity": "", "status": "" },
    { "id": "050f5b1a...", "title": "CVE-2026-22796 - openssl, openssl-fips-provider-latest and 1 more", "severity": "", "status": "" }
  ]
}
```

見てのとおり `severity` と `status` が空文字で返ります。  
**この一覧だけでは優先順位がつけられません。** 次の `finding_overview` に進むための入口として使うツール、という位置づけになりそうです。

### CVE トリアージの根拠づけが 1 〜 2 ターンで組み立てられる

`correlated_finding_detail` で得た CVE の ID を `finding_overview` に渡すと、OCSF（セキュリティイベントの標準スキーマ）準拠の詳細情報が返ってきます。  
`CVE-2026-42010`（gnutls）の実測値がこちらです。

| 項目 | 値 |
|---|---|
| EPSS | 0.0105（約 1%） |
| CVSS (Amazon Linux) | 7.1 HIGH - `AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N` |
| CVSS (MITRE) | 7.1 HIGH |
| CVSS (NVD) | 9.8 CRITICAL - `PR:N/C:H/I:H/A:H`（Amazon Linux との差分のみ抜粋） |
| `is_exploit_available` | false |
| `is_fix_available` | true |
| `fix_coverage` | Complete |
| `fixed_in_version` | `0:3.8.3-8.amzn2023.0.3` |
| パッケージ | gnutls 3.8.3-8.amzn2023.0.1 (rpm) |
| 検出元 | Inspector（`productv2/aws/inspector`） |

:::details 実際のレスポンス（vulnerabilities[0] から抜粋）

```json
{
  "cve": {
    "uid": "CVE-2026-42010",
    "epss": { "score": "0.0105" },
    "cvss": [
      {
        "vendor_name": "Amazon Linux",
        "base_score": 7.1,
        "severity": "HIGH",
        "vector_string": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N"
      },
      {
        "vendor_name": "MITRE",
        "base_score": 7.1,
        "severity": "HIGH",
        "vector_string": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N"
      },
      {
        "vendor_name": "NVD",
        "base_score": 9.8,
        "severity": "CRITICAL",
        "vector_string": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "adjusted_score": 7.1,
        "adjusted_vector_string": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N"
      }
    ]
  },
  "is_exploit_available": false,
  "is_fix_available": true,
  "fix_coverage": "Complete",
  "affected_packages": [
    {
      "name": "gnutls",
      "version": "3.8.3",
      "release": "8.amzn2023.0.1",
      "fixed_in_version": "0:3.8.3-8.amzn2023.0.3",
      "package_manager": "OS",
      "architecture": "X86_64"
    }
  ]
}
```

:::

注目していただきたいのは、同一の CVE で **NVD が 9.8 CRITICAL、Amazon Linux が 7.1 HIGH** と評価が分かれている点です。  
NVD は `PR:N`（権限不要）、ディストリ側は `PR:L`（低権限が必要）と前提が違うためです。

さらに NVD のエントリ自体に `adjusted_score: 7.1` という調整値が入っており、Security Hub 側でディストリの実態に合わせた値も保持していることが分かります。

そして EPSS（30 日以内に実際に悪用される確率の推定値）は 0.0105、つまり約 1% です。  
`is_exploit_available` は false、`is_fix_available` は true で `fixed_in_version` まで明記されています。

これが揃うと、トリアージの説明が 1 〜 2 ターンで組み立てられます。  
「NVD のスコアだけ見れば 9.8 ですが、EPSS は約 1%、Exploit も未確認、修正済みパッケージは提供されているので、次回のパッチ適用サイクルで対応します」といった説明です。

従来この材料集めは、NVD・ディストリのアドバイザリ・EPSS を個別に見に行く作業でした。  
顧客への説明品質が明確に上がるポイントだと感じています。

### そして、実体を見に行くと話が変わる

最後に、対象の EC2 インスタンスに対して `resource_detail` を実行しました。  
AWS Config の configuration item 相当が丸ごと返ってきます。

```json
{
  "resourceType": "AWS::EC2::Instance",
  "resourceGuid": "i-xxxxxxxx",
  "category": "Compute",
  "config": {
    "configuration": {
      "instanceType": "t3.small",
      "state": { "code": "80", "name": "stopped" },
      "stateTransitionReason": "User initiated (2026-08-18 11:00:20 GMT)",
      "publicIpAddress": null,
      "publicDnsName": "",
      "privateIpAddress": "10.0.0.61",
      "metadataOptions": {
        "httpTokens": "required",
        "httpEndpoint": "enabled",
        "instanceMetadataTags": "disabled"
      },
      "monitoring": { "state": "disabled" },
      "platformDetails": "Linux/UNIX",
      "iamInstanceProfile": { "arn": "arn:aws:iam::111122223333:instance-profile/dev-EC2InstanceProfile" }
    }
  },
  "tags": [
    { "key": "Name",      "value": "dev-work-01" },
    { "key": "AutoStop",  "value": "true" },
    { "key": "aws:cloudformation:stack-name", "value": "dev-work-01-EC2-xxxxxxxx" }
  ]
}
```

見るべきは 4 点です。

- `state: stopped` - **停止中**
- `publicIpAddress: null` - **パブリック IP なし**
- `metadataOptions.httpTokens: "required"` - **IMDSv2 強制済み**
- タグの `AutoStop: true` - 自動停止対象、つまり常時稼働を前提としていない

CloudFormation スタック管理下で、Name タグからも開発用途だと分かります。

Exposure Finding は「脆弱性あり × 高権限」という条件で MEDIUM を付けていますが、実体は**停止中でパブリック IP もなく、IMDSv2 も強制済みの開発用インスタンス**でした。

**ここが本記事で一番お伝えしたいことです。**  
Exposure Finding の severity は、稼働状態・到達可能性・IMDSv2 の有無を割り引いていません。  
つまり severity は「対応の優先度」ではなく「構成上のリスクの型」を表しており、`resource_detail` と突き合わせて初めて対応順序が決まるということになります。
 
従来はコンソールを Security Hub → EC2 → Inspector と行き来して突き合わせていた判断が、**1 つの会話の中で 2 ターンで完了しました。**

この「severity で終わらせず実体まで下りる」という思考の流れが会話ログとしてそのまま残るので、新人セキュリティ運用担当者のトリアージ教材としても使えるはずです。

## 活用イメージ③: マルチクラウドを同じインターフェースで追う

3 つ目は、AWS 以外のクラウドも同じ場所で確認できるという点です。

`top_exposures` は 1 ページ 5 件固定・severity 降順で返るのですが、member / Audit / ai の 3 アカウントが横断して自然に混ざって返ってきます。  
それだけでなく、**Azure リソースも同じ一覧に並びます。**

これは最近 Security Hub が Azure との統合に対応したためで、コネクタを作成しておけば Azure の Exposure も同じインターフェースで扱えるようになります。

https://zenn.dev/cscloud_blog/articles/aws-azure-config-integration

![](/images/Screenshot_2026-08-20_at_01-32-04.png)
*top_exposures が返す対話型の一覧ビュー*

```json
{
  "title": "Potential Initial Access: Potentially internet reachable Azure virtual machine has an open network security group",
  "severity": "LOW",
  "primaryResourceType": "microsoft.compute/virtualmachines",
  "cloudProvider": "Azure",
  "resourceOwnerId": "<azure-subscription-id>",
  "resourceRegion": "eastus",
  "accountId": "444455556666",
  "accountName": "Audit",
  "traits": ["Reachability", "Assumability", "Misconfiguration"],
  "traitCounts": { "Reachability": 2, "Assumability": 1, "Misconfiguration": 2 }
}
```

`cloudProvider: "Azure"`、`primaryResourceType: microsoft.compute/virtualmachines` となっており、Azure Subscription をアカウント単位として扱っているようです。  
Security Hub v2 のマルチクラウド取り込みが、MCP 経由でもそのまま見えるということになります。

リージョンについても横断が効いていました。  
当環境では ap-northeast-1（東京）だけでなく **ap-northeast-3（大阪）の Finding も混在**して返ってきており、リージョンを指定し直す必要はありませんでした。

「AWS は Security Hub、Azure は Defender for Cloud」と画面を分けて確認していた運用に対して、少なくとも一次確認は同じインターフェースに寄せられます。

上記の Azure VM の Finding は `Reachability` trait を 2 件持っていて、`top_exposures` の一覧にも出るし `finding_detail` でも `attack_path` でも問題なく扱えました。  

ただし、ネットワーク到達経路を展開する `network_path` だけはおそらく現在時点では対象外でした。  
マルチクラウドの統合は **「一覧・相関・攻撃経路までは同じインターフェースで追えるが、ネットワーク経路の可視化はまだ AWS 前提」** という状態だと理解しておくのが正確そうです。調べた記録は後述の折りたたみにまとめています。

## 向く用途と向かない用途

ここまでメリット中心に書いてきましたが、向かない用途をはっきりさせておかないと導入判断を誤ってしまいます。

| 向く | 向かない |
|---|---|
| エスカレーション時の一次解析 | 全件棚卸し・資産インベントリ |
| 単一 finding の深掘り | 月次定期レポートの自動生成 |
| 重大度の妥当性検証 | 修復の自動実行（read-only なので原理的に不可） |
| 顧客説明資料の下書き | SLA 管理・チケット連携 |

`top_exposures` は 1 ページ 5 件固定で、`nextToken` による opaque なページングで辿っていく形になっています。  
当環境では 6 ページ目で `nextToken` が消えて枯渇し、この組織の Exposure Finding は**全 28 件**だと分かりました。

つまり 28 件程度の規模であれば 6 コールで全件見きれます。  
ただし顧客環境のように数百件あるケースを考えると、5 件ずつのページングで全件を舐めるのは現実的ではありません。

実測したページの中身を見ても、1 ページ目に CRITICAL 1 件と MEDIUM 4 件、2 〜 3 ページ目は LOW 中心で、下位ページは同種の指摘（DynamoDB の削除保護無効など）で埋まっていきました。

深刻度の裾野が長く、**「上位 N 件を素早く見る」設計**であることがはっきり分かります。

また `correlated_finding_detail` にはページングパラメータが見当たりませんでした。  
当環境では traitCounts が 10・返却も 10 件だったため確認できませんでしたが、実運用の EC2 が数百件の CVE を抱えている場合に全件見られるのかは、この検証では確認できていません。

MSSP の月次レポート業務にそのまま置き換わるものではなく、**「深く 1 件」の道具**だと理解しています。

### ツールのまとめ

| ツール | 概要 | 実測での挙動 |
|---|---|---|
| `top_exposures` | 重大度降順で Exposure Finding を一覧 | 動いた。ただし 1 ページ 5 件固定なので、件数が多い環境の全件棚卸しには向かない |
| `finding_detail` | 1 件の Finding を深掘り | 動いた。相関シグナル・resource_relationship・修復リンクまで 1 コールで取得できる |
| `attack_path` | 攻撃経路のグラフを取得 | 制約あり。整形後のレスポンスから ATT&CK 情報と権限名が欠落する |
| `network_path` | ネットワーク到達経路を取得 | 当環境では展開できず。Azure の Finding は仕様上対象外で、AWS 側は該当 Finding がなく未検証 |
| `correlated_finding_detail` | 特定 trait に紐づく相関 Finding を列挙 | 制約あり。`severity` / `status` が空文字、ページングパラメータもない |
| `finding_overview` | CVE 等の詳細情報を取得 | 動いた。ベンダー別 CVSS・EPSS・修正版情報まで一括で取得でき、情報密度が最も高い |
| `resource_detail` | リソースの Config 相当を取得 | 動いた。severity の妥当性を検証する決め手になる |
| `recommendation` | 修復推奨を trait 別に取得 | 動いた。UI ではなくテキストを返す。修復推奨順に並ぶ |

なお表の中で `network_path` だけ「展開できず」となっているのが気になったので、バンドルの `index.js` まで読んで理由を確認しました。  
結論としては不具合ではなく、**`network_path` が収集対象とするノードの型が Azure の Finding には無かった**というだけの話でした。本題からは逸れるので、調べた記録は折りたたんでおきます。

:::details network_path が展開されなかった理由（バンドルを読んで調べた記録）
公式ドキュメントには Internet Gateway → NACL → Security Group → ENI → Instance という順序付きホップの図が掲載されています。  
これを当環境で再現しようとしたのですが、3 段階の試行を経ても再現できませんでした。

1 つ目、CRITICAL の IAM 系 Finding に対して実行すると `nodes: []`, `edges: []`, `source: "fallback"`, `notFound: true` が返りました。  
IAM ユーザーにネットワーク経路はないので、これは仕様通りだと考えられます。

2 つ目、`Reachability` trait を 2 件持つ Azure VM の Finding に対して実行しても、同じく `notFound: true` でした。`availablePathIds` も返ってきません。

```json
{
  "view": "network-path",
  "findingId": "arn:aws:securityhub:ap-northeast-1:444455556666:exposure:b8c8c029...",
  "nodes": [],
  "edges": [],
  "source": "fallback",
  "notFound": true
}
```

3 つ目、`finding_detail` の raw から `type: "InternetReachability"` ノードの `uid` を手で拾って `pathId` として渡したところ `source: "live"` で解決しました。  
ただし返ってきたのはノード 1 個（Public IP Address）、エッジ 0 本でした。

```json
{
  "view": "network-path",
  "pathTitle": "203.0.113.154:22 is reachable from the internet (vm-dev-01-ip)",
  "nodes": [
    {
      "sublabel": "eastus · Public IP Address",
      "resourceType": "microsoft.network/publicipaddresses",
      "severity": "MEDIUM"
    }
  ],
  "edges": [],
  "source": "live"
}
```

一方、同じ Finding の raw 側の `resource_relationship` には経路データが存在していました。

```
PublicInternet → InternetReachability → publicipaddresses
  → networkinterfaces → virtualnetworks/subnets → virtualmachines → disks
```

データはあるのに、`network_path` ビューが展開しきれていないという状態です。

そこでバンドルの `index.js` を読んでみると、`getNetworkPath()` は内部で `collapsedNetworkPathUids()` を呼んでおり、そこでは以下のように **`type` が `CollapsedNetworkPath` のノードだけを収集**していました。

```js
if (n3.type === COLLAPSED_NETWORK_PATH_TYPE && n3.uid) uids.push(n3.uid);
```

一方、今回の Azure VM の Finding が持っていたのは `InternetReachability` 型のノードでした。  
型が一致しないため収集対象から外れ、結果として `availablePathIds` が空になり `notFound: true` が返る、という流れです。

**つまり実装を読む限り、これは不具合ではありません。** データ側の条件が成立していなかった、というのが正確な理解になります。

`pathId` を手で渡したときにノード 1 個で止まったことにも説明が付きました。  
このケースではフォールバックの `stepsToFinding()` が使われるのですが、これは `networkReachabilityDetails.networkPath.steps` という **AWS 固有の構造**を読みに行きます。Azure の Finding にはこの構造がないため、ホップの展開が発火しません。

さらにバンドル内にはモックデータも含まれており、期待されている経路の形が明示されていました。

```
PublicInternet → CollapsedNetworkPath → NetworkAcl → SecurityGroup → NetworkInterface
```

公式ドキュメントの図と一致する形です。  
`CollapsedNetworkPath` 型のノードを持つ AWS 側の Reachability Finding があれば動く見込みですが、**当環境の AWS 側には `Reachability` trait を持つ Finding が 1 件もなかった**ため、そこは検証できていません。

`Reachability` trait を持っていたのは前述の Azure VM 2 件のみで、AWS 側は 0 件でした。  
したがって「AWS でも動かない」と一般化はできず、あくまで未検証という扱いになります。
:::

### 観測した粗さの一覧

実際に試して確認した Preview としての粗さを整理しておきます。

1. `network_path` の対応がクラウド間で非対称。Azure の Finding は一覧・`finding_detail`・`attack_path` には出てくるが、`network_path` の展開対象外
2. `correlated_finding_detail` の `severity` / `status` が空
3. `attack_path` の整形出力から MITRE ATT&CK と権限情報が欠落する（raw には存在する）
4. `attack_path` のエッジ severity が全て `info` で危険経路が強調されない
5. `correlated_finding_detail` にページングがない

1 つ目はバグではなく設計上の非対称性ですが、マルチクラウドで使う側からすると期待値のズレとして現れます。  
残りについても「使えない」というレベルではなく、raw を併読すれば回避できるものです。ただし、そのぶん人間側が構造を理解している必要がありそうです。

## まとめ

今回は、AWS Security Hub MCP App を実際に叩いてみた結果と、その活用イメージについて考えてみました。

8 つのツールを一通り触った結論としては、これは「AI に判断させる」ものではなく、**「AI に材料を集めさせて、人間が判断する」**ための道具だと整理できました。

一番のメリットは、Security Hub v2 が既に持っている相関済みデータへの到達コストがほぼゼロになることです。  
エスカレーションの一次解析、CVE トリアージの根拠づけ、severity の妥当性検証といった「深く 1 件を調べる」場面で、説明品質が明確に上がると感じています。  
逆に、全件棚卸しや月次レポートの自動生成といった網羅性が要る業務には、現時点では向かないという印象です。

そして個人的に一番の収穫は、MEDIUM だった EC2 が停止中の開発機だと分かったことでした。  
severity を「優先度」として読んでいると判断を誤ってしまいます。実体まで下りる癖をつけるうえでも、この道具はかなり効きそうです。

マルチクラウドで使う方向けに 1 つだけ添えておくと、Azure の Finding も一覧・相関・攻撃経路までは同じインターフェースで追える一方、ネットワーク経路の展開は仕様上 AWS 前提でした。今後のアップデートで対応が広がると嬉しいなと思っています。

最後に改めて 1 点だけ補足しておくと、現時点で使えるのは Claude Desktop からのみで、Claude Code やその他 AI エージェントからは利用できません。  
前述のコンテキストコストを考えると、必要な項目だけを抽出して扱える形で使えると嬉しいところなので、そのあたりも含めて今後の動きを追っていきたいと思います。

この記事がどなたかの役に立つと嬉しいです。
