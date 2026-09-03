---
title: "GuardDuty の Custom Detection Rules は「ルールを書く」のではなく「この環境では異常」を定義する機能だった件"
emoji: "🚨"
type: "tech"
topics: ["aws", "guardduty", "security"]
published: false
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

GuardDuty に Custom Detection Rules という機能が追加されました。

https://docs.aws.amazon.com/guardduty/latest/ug/custom-detection-rules.html

実際に有効化して動かした記録はスクラップに残しています。

https://zenn.dev/khirasan/scraps/ab23d84ba3d6e0

この機能がどのようなケースで活用余地がありそうかなどを考えてみました。

:::message
この記事の3行まとめ
- Custom Detection Rules は検知ロジックを自作する機能ではなく、AWS が保守するカタログから有効化するルールを選ぶ機能
- アカウント固有の「この操作が起きること自体が異常」という定義を GuardDuty に持ち込める
- カタログに一致するルールがあれば、発見的統制のために自作していた Config ルールの一部は置き換えられる（ただし既存の非準拠状態は検出できない）
:::

## GuardDuty の検知モデルに空いていた穴

これまでの GuardDuty の Finding は「どのアカウントで起きても疑わしい」振る舞いを検知するものでした。マイニングプールへの通信や既知の C2 ドメインへの DNS ルックアップなどは、環境を問わず黒に近いグレーです。

ただセキュリティチームの側には、「自分たちの環境ではこの操作は起きないはずだ」という肌感覚があります。

- AMI の共有が日常運用のアカウントもあるが、絶対に起きてはいけないアカウントもある
- MFA なしのサインインが常態化している環境もあれば、それ自体が異常な環境もある
- VPC Flow Logs の削除は、証跡を消す典型的な攻撃者の初動になり得る

この「操作の善悪が環境依存で決まる」領域は、GuardDuty が汎用的に判定できません。Custom Detection Rules は、その判定をユーザーに委ねる仕組みです。検知ロジックそのものは AWS が用意したまま、「自分のアカウントではこの振る舞いを異常として扱う」と決めるところだけがユーザーの仕事です。

ドキュメントも「有効にしたアカウントでは想定されていない、つまり疑わしい活動を検知する」と書いています。売りは異常の定義を持ち込めるところにあります。

## 検知ロジックの中身

各ルールは MITRE ATT&CK や AWS Threat Technique Catalog の語彙で、単一の脅威テクニックに対応づけられています。Threat Technique Catalog は AWS 環境で観測される脅威テクニックを ATT&CK にマッピングして公開しているもので、こちらから参照できます。

https://aws-samples.github.io/threat-technique-catalog-for-aws/

![](/images/Screenshot_2026-09-04_at_02-14-19.png)

この各ルールの検知ロジックはコンソールで確認できます。  
例えば `VPCFlowLogsDeleted` ルールを開くと、次の式が入っていました。

```
eventSource = 'ec2.amazonaws.com'
AND eventName = 'DeleteFlowLogs'
AND errorCode IS NULL
```

基本は、CloudTrail のイベントフィールドを評価する SQL ベースの条件式です。`errorCode IS NULL` が付いているのは、権限不足で失敗した `DeleteFlowLogs` を除くためでしょう。成功した削除だけを検知対象にしたいのかなと思います。

式がここまで読めると条件を足したくなりますが、ユーザーが変更できるのは有効化するかどうかとモードだけで、この式を編集する手段はなさそうです。

## Dry Run と Live の 2 モード

ルールをアカウントに適用する単位が Association です。Association はルールとアカウントを結びつけ、そのルールがどちらのモードで動くかを記録します。Association が無いルールは評価されません。

| モード | 挙動 | 失効 |
| --- | --- | --- |
| Live | ルールが一致すると Finding を生成する | 失効しない |
| Dry Run | 一致回数を CloudWatch メトリクスとして記録するだけで Finding は生成しない | 作成から 14 日で自動失効 |

Dry Run は本番投入前の試運転で使用するモードです。  
頻度の高いルールをいきなり Live にすると、Finding のノイズでトリアージ負荷が跳ね上がります。

まず Dry Run でメトリクスを見てから Live に倒す、という 2 段階の導入が前提の設計です。なおメトリクスが発行されるのはルールに一致したときだけなので、一度も一致しなければ何も出ません。

Association を作る操作自体は、コンソールで対象ルールを選んで `Actions` から `Enable (Dry Run)` / `Enable (Live)` を選ぶだけです。Dry Run と Live を実際に切り替えて Finding の出方が変わるところまでは、冒頭のスクラップに記録を残しています。

## どんなルールが用意されているのか

執筆時点（2026 年 9 月 3 日）で 33 種類のルールが登録されていました。`ListCustomDetectionRules` で取得したレスポンスの 1 件はこういう形です。

```json
{
  "RuleId": "admin-policy-attached-to-role",
  "Name": "AdminPolicyAttachedToRole",
  "Description": "Detects when admin policy is attached to an IAM role",
  "Severity": "HIGH",
  "DataSource": "CloudTrailManagementEvent",
  "Tactic": "Privilege Escalation",
  "Technique": "T1098.001 - Account Manipulation: Additional Cloud Credentials",
  "Service": "iam",
  "Language": "SQL",
  "Schema": "CloudTrail"
}
```

:::message alert
手元の aws-cli 2.36.35 では Custom Detection Rules 関連のサブコマンドがまだ存在せず、`Found invalid choice` で弾かれました。botocore を 1.43 系まで上げて boto3 から直接呼ぶと利用できたので、CLI で試す場合はバージョンを先に確認しておくのがおすすめです。
:::

ルールごとの脅威テクニックとの対応づけは、`Tactic` と `Technique` というフィールドで返ってきます。Technique に入るのは MITRE ATT&CK の ID で、33 件すべてに漏れなく付いていました。ユニークな Technique は 17 種類。カタログが ATT&CK のテクニック単位で設計されているのが、フィールドの粒度からそのまま読み取れます。

参照している ATT&CK も現行版でした。たとえば `VPCFlowLogsDeleted` の Tactic は `Defense Impairment`、Technique は `T1685.002 - Disable or Modify Tools: Disable or Modify Cloud Log`。ログ無効化のあたりは ATT&CK 側で ID と Tactic 名が改訂されているので、見覚えのある ID と違っていたら ATT&CK 本家を見に行くのが早いです。

https://attack.mitre.org/techniques/T1685/

33 件を Tactic で分類すると、こう散っています。

| Tactic | 件数 |
| --- | --- |
| Persistence | 9 |
| Privilege Escalation | 5 |
| Defense Impairment | 5 |
| Exfiltration | 4 |
| Impact | 3 |
| Credential Access | 2 |
| Initial Access | 2 |
| Execution | 1 |
| Lateral Movement | 1 |
| Resource Development | 1 |

Persistence と Privilege Escalation の 2 つで 14 件、全体の 4 割強を占めます。侵入の入口を捉えるより、入った後に足場を作る操作へ寄っている構成です。Severity は HIGH が 14、MEDIUM が 16、LOW が 3。対象サービスは IAM が 10 件で最多、次が EC2 の 7 件、RDS が 4 件でした。

:::details 33 ルールの全一覧（2026 年 9 月 3 日時点）
| ルール名 | Severity | Tactic | Technique | 検知内容 |
| --- | --- | --- | --- | --- |
| `AdminPolicyAttachedToRole` | HIGH | Privilege Escalation | T1098.001 - Account Manipulation: Additional Cloud Credentials | IAM ロールに管理者ポリシーがアタッチされた |
| `AdminPolicyAttachedToUser` | HIGH | Privilege Escalation | T1098.003 - Account Manipulation: Additional Cloud Roles | IAM ユーザーに管理者ポリシーがアタッチされた |
| `AMIExternalAccess` | HIGH | Exfiltration | T1537 - Transfer Data to Cloud Account | AMI が外部アカウントに共有された、または公開された |
| `BedrockServiceCredentialCreated` | MEDIUM | Privilege Escalation | T1098.001 - Account Manipulation: Additional Cloud Credentials | IAM のサービス固有の認証情報として Bedrock の API キーが生成された |
| `ConsoleLoginWithoutMFA` | MEDIUM | Initial Access | T1078.004 - Valid Accounts: Cloud Accounts | フェデレーション以外のユーザーが MFA なしでコンソールにサインインした |
| `DNSQueryLogsDeleted` | MEDIUM | Defense Impairment | T1685.002 - Disable or Modify Tools: Disable or Modify Cloud Log | Route 53 Resolver の DNS クエリログ設定が削除された |
| `EBSSnapshotExternalAccess` | HIGH | Exfiltration | T1537 - Transfer Data to Cloud Account | EBS スナップショットが外部アカウントに共有された、または公開された |
| `EC2InstanceSSHKeyPushed` | MEDIUM | Lateral Movement | T1021.004 - Remote Services: SSH | EC2 Instance Connect またはシリアルコンソール経由で SSH 公開鍵が送り込まれた |
| `EC2PasswordDataRetrieved` | MEDIUM | Credential Access | T1552 - Unsecured Credentials | EC2 の Windows 管理者パスワードデータが取得された |
| `EC2SecurityGroupPublicSSH` | MEDIUM | Persistence | T1133 - External Remote Services | セキュリティグループが SSH（22 番）を全 IP に開放した |
| `EC2TerminationProtectionEnabled` | LOW | Defense Impairment | T1685 - Disable or Modify Tools | EC2 の削除保護が有効化された |
| `EC2UserDataModified` | HIGH | Persistence | T1037 - Boot or Logon Initialization Scripts | EC2 のユーザーデータが変更された（再起動時のコマンド実行） |
| `IAMAccessKeyCreated` | LOW | Persistence | T1098.001 - Account Manipulation: Additional Cloud Credentials | IAM アクセスキーが作成された |
| `IAMRoleTrustPolicyModified` | MEDIUM | Persistence | T1098 - Account Manipulation | IAM ロールの信頼ポリシーが公開・クロスアカウント・自身宛てに緩められた |
| `IAMUserLoginProfileCreated` | HIGH | Persistence | T1098.001 - Account Manipulation: Additional Cloud Credentials | プログラム利用のみだった IAM ユーザーにログインプロファイルが作られた |
| `IAMUserLoginProfileUpdated` | MEDIUM | Persistence | T1098.001 - Account Manipulation: Additional Cloud Credentials | IAM ユーザーのログインプロファイルが更新された（パスワード変更） |
| `LambdaFunctionPublicAccess` | HIGH | Persistence | T1098 - Account Manipulation | リソースベースポリシーで Lambda 関数が誰からでも実行できる状態になった |
| `LambdaFunctionUrlPublicAccess` | HIGH | Persistence | T1556 - Modify Authentication Process | Lambda 関数 URL が公開アクセスで作成・更新された |
| `RDSIAMAuthDisabled` | MEDIUM | Defense Impairment | T1556 - Modify Authentication Process | RDS の IAM データベース認証が無効化された |
| `RDSMasterPasswordReset` | HIGH | Credential Access | T1556 - Modify Authentication Process | RDS のマスターパスワードがリセットされた |
| `RDSPubliclyAccessible` | HIGH | Initial Access | T1190 - Exploit Public-Facing Application | RDS が公開アクセス可能に変更された |
| `RDSSnapshotPubliclyShared` | HIGH | Exfiltration | T1537 - Transfer Data to Cloud Account | RDS のスナップショットが公開共有された |
| `RolesAnywhereTrustAnchorCreated` | MEDIUM | Persistence | T1098.001 - Account Manipulation: Additional Cloud Credentials | IAM Roles Anywhere のトラストアンカーが作成された |
| `S3BucketPolicyExternalAccess` | HIGH | Exfiltration | T1537 - Transfer Data to Cloud Account | S3 バケットポリシーが `*` または所有者以外のアカウントにアクセスを許可した |
| `S3CustomerProvidedKeysEnabled` | HIGH | Defense Impairment | T1685 - Disable or Modify Tools | S3 バケットで SSE-C が再度有効化された（ランサムウェアの準備） |
| `S3LifecycleRapidExpiration` | MEDIUM | Impact | T1485 - Data Destruction | S3 のライフサイクル設定が 1 日でオブジェクトを失効させる内容に変更された |
| `SageMakerLifecycleConfigModified` | MEDIUM | Execution | T1059 - Command and Scripting Interpreter | SageMaker ノートブックのライフサイクル設定が変更された |
| `SESAccountSendingEnabled` | LOW | Impact | T1496 - Resource Hijacking | SES のアカウント単位のメール送信が有効化された |
| `SESDomainIdentityVerified` | MEDIUM | Resource Development | T1586.002 - Compromise Accounts: Email Accounts | SES でドメイン ID が検証された（メール送信基盤の準備） |
| `SESFullAccessPolicyAttachedToRole` | MEDIUM | Privilege Escalation | T1098.001 - Account Manipulation: Additional Cloud Credentials | IAM ロールに SES のフルアクセスポリシーがアタッチされた |
| `SESFullAccessPolicyAttachedToUser` | MEDIUM | Privilege Escalation | T1098.001 - Account Manipulation: Additional Cloud Credentials | IAM ユーザーに SES のフルアクセスポリシーがアタッチされた |
| `SESProductionAccessEnabled` | MEDIUM | Impact | T1496 - Resource Hijacking | SES の本番アクセス（サンドボックス解除）が申請された |
| `VPCFlowLogsDeleted` | HIGH | Defense Impairment | T1685.002 - Disable or Modify Tools: Disable or Modify Cloud Log | VPC Flow Logs が削除された |
:::

ルールは AWS 側で継続的に追加・改善され、バージョン管理もされています。実際 `AdminPolicyAttachedToRole` は `CreatedAt` が 2026 年 6 月 29 日、`UpdatedAt` が 2026 年 9 月 1 日で、この記事を書いている 2 日前に更新が入っていました。最新の一覧は API を正とするのが安全です。

データソースは、現時点では CloudTrail の管理イベントのみ。ルールが一致すると、検知の最小単位として Signal が 1 件生成されます。同じ Tactic・Service・Technique を共有する Signal は 1 つの Finding に集約されます。Finding 名が `Tactic:Service/Technique` の形式なのは、この集約単位がそのまま名前に出ているからです。

## Config ルールとの棲み分け

「特定の操作が発生したら検知したい」という発見的統制は、これまで AWS Config か CloudTrail + EventBridge で組むのが定番でした。  
マネージドルールでカバーされない振る舞いは自作するしかありません。設定変更トリガー型のカスタムルールで Lambda に判定ロジックを書くか、CloudTrail をソースにした EventBridge ルールを組むかの二択です。

カタログにある `VPCFlowLogsDeleted` や `AdminPolicyAttachedToRole` は、まさにこれまで自作していた検知の類かなと思います。

判定ロジックを自前で保守する必要はなくなります。しかも検知結果は、重大度や MITRE ATT&CK のテクニックが付いた Finding として、既存の GuardDuty / Security Hub の通知経路にそのまま乗ってくれます。

ただし全面的な置き換えにはなりません。そもそも評価している対象が違います。

| 観点 | AWS Config ルール | Custom Detection Rules |
| --- | --- | --- |
| 評価対象 | リソースの現在の設定状態 | CloudTrail 管理イベント（発生した API コール） |
| 検出タイミング | 設定変更トリガー型または定期実行型 | 有効化後に条件に一致するイベントが発生した時のみ |
| 既存の非準拠状態 | 定期実行型なら検出できる（ドリフト検出） | 検出できない |
| ルールの網羅性 | マネージド＋カスタムで実質無制限 | AWS が保守するカタログの範囲内 |
| 出力 | コンプライアンス状態（準拠 / 非準拠） | Finding（重大度・アクター・MITRE ATT&CK のコンテキスト付き） |

運用でいちばん効いてくるのが「既存の非準拠状態を検出できない」ところかと思われます。

すでに公開されている S3 バケットや、すでにアタッチされている管理者ポリシーのような野良の設定ミスは、ルールを有効化しても検知されません。棚卸しには引き続き Config の定期実行型ルールや Security Hub CSPM が要ります。

棲み分けの線は「発生した操作を検知したいのか、現在の設定状態を監査したいのか」で引けます。タグ運用のようにカタログに無いチェックも、当然 Config の守備範囲のままです。

## マルチアカウントは委任管理者に集約されている

Organizations 環境で集中管理している場合は、メンバーアカウントにルールの管理権限がありません。有効化も無効化も、委任管理者アカウントからの操作になります。

委任管理者は Organization Configuration で、モードと対象アカウント（include / exclude リスト）を指定します。すると GuardDuty が、対象アカウントごとに Association を自動生成してくれます。include / exclude を両方省略した場合は、後から参加するアカウントも含めて組織全体が対象。

:::message alert
メンバーアカウント側から単体でルールを有効化・無効化・変更しようとすると `AccessDeniedException` が返ります。招待ベースで参加しているメンバーアカウントは、そもそもこの集中管理の対象外です。
:::

ハマりどころが 2 つあります。

1 つは、include / exclude を省略した「組織全体」の設定が、そのルールに対して排他的になる点です。同じルールに別モードの設定を追加しようとすると `ConflictException` が返ります。Live と Dry Run を共存させたい場合は、両方で対象アカウントを明示的な include リストとして指定する必要があります。

もう 1 つ、Organization Configuration を削除しても、そこから作られたメンバーアカウント側の Association は連動して削除されません。ルールはメンバー側で有効なまま残るので、完全に止めるならメンバーアカウント側も確認が必要です。

## まとめ

Custom Detection Rules で有効化できるのは、AWS が MITRE ATT&CK ベースで保守しているルールです。ユーザーが検知ロジックを書く余地はありません。

ただ、この機能が引き受けているのは、アカウントごとの正常と異常の線引きです。自分の環境で起きるはずのない操作があるなら、それを異常として宣言して、AWS が用意した検知ロジックに乗せて監視できます。Dry Run で影響を測ってから Live に倒す手順も、委任管理者への権限集約も、その線引きを組織として運用するための設計です。

まずは `ListCustomDetectionRules` でカタログを一覧して、発見的統制のために自作した Config ルールや EventBridge ルールと突き合わせてみてください。重複が見つかったら、Dry Run で 14 日間だけ並走させてメトリクスを比べる。それが一番安全な入口だと思います。

この記事がどなたかの役に立つと嬉しいです。
