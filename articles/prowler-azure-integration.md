---
title: "Azure 環境を Prowler と連携してセキュリティアセスメントを実施してみた"
emoji: "✅"
type: "tech"
topics: ["azure", "prowler", "security"]
published: true
published_at: 2026-07-21 08:00
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

普段は AWS を扱うことが多いのですが、今回 Azure 環境をクラウドセキュリティ監査OSS「Prowler」でスキャンする機会がありましたので備忘録がてら投稿しました。

:::message
**この記事の3行まとめ**
- Azure 環境を Prowler でスキャンする場合には `--sp-env-auth` / `--az-cli-auth` / `--browser-auth` / `--managed-identity-auth` の4つの認証方式がある
- 「顧客にユーザーを払い出してもらう」運用では `--az-cli-auth` ＋ 管理グループ単位のロール付与が実務的な解
- 必要な権限は RBAC（`Reader` + カスタムロール `ProwlerRole`）と Microsoft Entra ID（Graph API 権限3つ）の2系統
:::

## Prowler とは

Prowler は AWS・Azure・Google Cloud・Kubernetes などマルチクラウドに対応したオープンソースのセキュリティ監査ツールです。CIS や NIST、ISO27001 といった各種コンプライアンスフレームワークに準拠したチェック項目を持ち、実行するだけで大量のセキュリティ設定ミスを検出できます。

SaaS 版の「Prowler Cloud」と OSS 版の「Prowler CLI」が存在しますが、今回は Prowler リポジトリをクローンして使う OSS 版（CLI）を利用しました。

https://github.com/prowler-cloud/prowler

## Azure 環境を Prowler でスキャンする場合の認証方式を選ぶ

Azure 環境を Prowler でスキャンする場合に対応する認証方式は次の4つで、いずれか1つを選択する形になります。

| フラグ | 認証方式 | 特徴 |
| --- | --- | --- |
| `--sp-env-auth` | Service Principal（サービスプリンシパル） | 公式推奨。Graph API のアプリ権限単位で必要な権限だけを厳密に絞り込める |
| `--az-cli-auth` | Azure CLI 認証 | `az login` 済みの資格情報をそのまま利用する。CLI 専用（Prowler Cloud では使用不可） |
| `--browser-auth` | ブラウザ対話ログイン | ブラウザでの対話ログインを行う。`--tenant-id` の指定が必須 |
| `--managed-identity-auth` | マネージド ID 認証 | Azure VM やコンテナなど、Azure リソース上で Prowler を実行する場合に使う |

Service Principal（サービスプリンシパル）は、人間ではなく Azure Portal に対して操作を行う「アプリケーション」自身に割り当てるアイデンティティです（いわゆる NHI = Non-Human Identity の一種）。公式ドキュメントでも Prowler Cloud で利用できるのはこの方式のみとされており、CLI でも推奨方式として案内されています。

なお `--managed-identity-auth` については、公式ドキュメントに次のような注意書きがあります。マネージド ID を Azure リソースに「有効化」しただけでは権限は一切付与されません。

:::message alert
マネージド ID を有効化しただけでは、そのリソースにスキャン権限が付与されるわけではありません。マネージド ID もサービスプリンシパルの一種であり、スキャン対象のサブスクリプションごとに `Reader` と `ProwlerRole` を明示的に割り当てる必要があります。
:::

## 必要な権限を整理する

Azure 環境を Prowler でスキャンする場合に必要とする権限は、公式ドキュメントによると、RBAC（Azure リソースへのアクセス）と Microsoft Entra ID（Graph API）の2系統に分かれます。

### RBAC（サブスクリプションスコープ）

サブスクリプションごとに次の2つのロールを割り当てる必要があります。

- **`Reader`**: Azure リソースへの読み取り専用アクセスを付与する組み込みロール
- **`ProwlerRole`**: `Reader` だけではカバーできない一部のチェック専用のカスタムロール

`ProwlerRole` はリポジトリの `permissions/prowler-azure-custom-role.json` で定義されており、含まれるアクションはこの2つだけです。

- `Microsoft.Web/sites/host/listkeys/action`: Function App のホストキー（アクセスキー）を取得する権限
- `Microsoft.Web/sites/config/list/Action`: Function App の設定情報を取得する権限

このロールが必要になるのは、次の4つのチェックに限られます。

- `app_function_access_keys_configured`
- `app_function_application_insights_enabled`
- `app_function_ftps_deployment_disabled`
- `app_function_latest_runtime_version`

:::message alert
`ProwlerRole` に含まれるアクションは「書き込み系」のアクションです。対象リソースに `ReadOnly` ロックが設定されていると、これらのチェックはエラーとなり findings が取得できません。
:::

### Microsoft Entra ID（Graph API）

Entra ID 関連のチェックを実行したい場合は、次の3つの Graph API アプリ権限が必要になります。公式ドキュメントには「実行に必須ではないが、機能を拡張する」権限と説明されています。

- `AuditLog.Read.All`: サインインログや操作ログなどの監査ログを読み取る権限
- `Directory.Read.All`: ユーザー・グループ・ディレクトリロールなどの Entra ID 情報を読み取る権限
- `Policy.Read.All`: 条件付きアクセスなどの各種ポリシー設定を読み取る権限

より制限的にしたい場合は `Directory.Read.All` の代わりに `Domain.Read.All` を使う選択肢もありますが、公式ドキュメントには「`DirectoryRoles` や `GetUsers` 系のチェックが動かなくなる」という副作用が明記されています。

なお、この Graph API 権限が必要になるのは `--sp-env-auth`（サービスプリンシパル）や `--managed-identity-auth`（マネージド ID）で認証する場合です。これらの方式では Azure Portal の通常のロール割り当て画面からは付与できず、Azure CLI で `appRoleAssignments` を直接操作する必要があります。

```bash
GRAPH_SP_ID=$(az ad sp list --display-name "Microsoft Graph" --query [0].id -o tsv)

az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/servicePrincipals/<principalId>/appRoleAssignments" \
  --headers "Content-Type=application/json" \
  --body "{\"principalId\": \"<principalId>\", \"resourceId\": \"$GRAPH_SP_ID\", \"appRoleId\": \"<App Role ID>\"}"
```

`<App Role ID>` には `Directory.Read.All`（`<directory-read-all-role-id>`）、`Policy.Read.All`（`<policy-read-all-role-id>`）、`AuditLog.Read.All`（`<auditlog-read-all-role-id>`）の3つをそれぞれ指定し、3回実行します。

今回の検証では `--az-cli-auth`（ユーザー認証）を選択したため、この Graph API 権限付与ではなく、後述する `Global Reader` ディレクトリロールの付与で代替しています。

## スコープ設計：個別サブスク vs 管理グループ

Prowler はデフォルトでは、実行したユーザーがアクセス可能な全サブスクリプションをスキャン対象にします。ただし実際にスキャンできるのは、あくまで**ロールが付与されているサブスクリプションだけ**です。

ここで検討が必要になるのが、ロールをどの単位で割り当てるかです。個別のサブスクリプションに割り当てる方法もありますが、対象サブスクリプションの数が増えるほど運用が煩雑になります。

そこで採用したのが、Azure の「管理グループ（Management Group）」への割り当てです。今回の検証環境では、テナントの最上位に位置する `Tenant Root Group` の配下に3つのサブスクリプションが存在する構成だったため、`Tenant Root Group` にロールを割り当てました。

公式ドキュメントにも、複数サブスクリプションを扱う場合の推奨事項として次のように明記されています。

> Role assignment should be done at the management group level instead of per subscription.
> （ロールの割り当ては、サブスクリプション単位ではなく管理グループレベルで行うべきです）

管理グループへの割り当てには、配下のサブスクリプションに自動的に権限が継承されるメリットがあります。将来サブスクリプションが追加されても、個別にロールを割り当てる必要がなく、自動的にスキャン対象へ組み込まれます。一方で、割り当てる範囲が意図せず広がりすぎるリスクもあるため、管理グループの階層構造は事前に把握しておく必要があります。

## 実際に権限を付与してみる

検証環境（テナント `<tenant-domain>`、Tenant Root Group 配下に3サブスクリプション）で、実際に権限を付与した手順です。

### Azure CLIのインストール

まずは、Azure CLI をインストールします。  
下記を参考に、環境に合わせてインストールしてください。

https://learn.microsoft.com/ja-jp/cli/azure/install-azure-cli?view=azure-cli-latest

### 専用ユーザーの作成

まず Entra ID に、スキャン専用のユーザーを作成します。

```bash
az ad user create --display-name "Prowler Scanner" \
  --user-principal-name "prowler-scanner@<tenant-domain>" \
  --password '<生成した強力な一時パスワード>' \
  --force-change-password-next-sign-in false
```

`--force-change-password-next-sign-in false` を指定して初回パスワード変更を無効化しておくと、非対話の CLI 運用がしやすくなります。ただし今回は最終的にブラウザでの対話ログインを選択したため、この設定は必須ではありませんでした。

### 管理グループへ Reader を割り当て

作成したユーザーに、管理グループ（Tenant Root Group）スコープで `Reader` ロールを割り当てます。

```bash
az role assignment create --role "Reader" \
  --assignee-object-id <principalId> --assignee-principal-type User \
  --scope /providers/Microsoft.Management/managementGroups/<mg-id>
```

### Entra 側に Global Reader を付与

Entra ID 側は、ディレクトリロールの `Global Reader` を Graph API 経由で付与しました。

```
POST https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments
{
  "principalId": "<principalId>",
  "roleDefinitionId": "<Global Reader のロール定義ID>",
  "directoryScopeId": "/"
}
```

## Prowler を実行する

権限付与が完了したら、専用ユーザーでログインしてスキャンを実行します。

```bash
az login   # 専用ユーザーでブラウザ対話ログイン
az account list
prowler azure --az-cli-auth #ターミナル上で出力結果を表示する場合
prowler azure --az-cli-auth -M csv json-ocsf html -o <output_dir> -F <filename> # 出力結果をファイルに保存する場合
```

### 検出結果サマリ

ターミナルで出力させると以下のように表示されました。

```bash
<user>@<host> prowler % prowler azure --az-cli-auth
                         _
 _ __  _ __ _____      _| | ___ _ __
| '_ \| '__/ _ \ \ /\ / / |/ _ \ '__|
| |_) | | | (_) \ V  V /| |  __/ |
| .__/|_|  \___/ \_/\_/ |_|\___|_| CLI - v5.35.0
|_|

Date: <scan-datetime>


│ You're getting a snapshot 📸. Prowler Cloud gives you the full picture:
│
│ ✓ Send your findings - directly from the Prowler CLI to Prowler Cloud.
│ ✓ Continuous Security Monitoring - custom scheduling and scan configuration with history, trends and alerts.
│ ✓ Triage - review findings, flag false positives and track accepted risk with your team.
│ ✓ Lighthouse AI + MCP - autonomous triage, custom dashboards, prioritization with prevention and remediation.
│ ✓ Alerts - get notified when anything you want is happening.
│ ✓ Live Compliance - dashboards for 50+ frameworks, always up to date.
│ ✓ Remediation - complete guided remediation including Autonomous remediation with Lighthouse AI.
│ ✓ Attack Path Visualization - see how attackers chain risks to reach your crown jewels.
│ ✓ Bulk Provisioning - add your entire AWS Organization in seconds.
│ ✓ Integrations - Anything with our MCP + Jira, Slack, AWS Security Hub, Amazon S3, SSO and RBAC.
│
│ Start free at 👉 cloud.prowler.com

-> Using the Azure credentials below:
  · Azure Tenant Domain: <tenant-domain> Azure Tenant ID: <tenant-id>
  · Azure Region: AzureCloud
  · Azure Subscriptions: ['<subscription-a-name>: <subscription-a-id>', '<subscription-b-name>: <subscription-b-id>', '<subscription-c-name>: <subscription-c-id>']
  · Azure Resource Groups: ALL
  · Azure Identity Type: User Azure Identity ID: prowler-scanner@<tenant-domain>

-> Using the following configuration:
  · Config File: <path-to-prowler>/config/config.yaml

Executing 188 checks, please wait...
-> Scan completed! |▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 188/188 [

Overview Results:
╭─────────────────────┬─────────────────────┬────────────────╮
│ 31.38% (203) Failed │ 68.62% (444) Passed │ 0.0% (0) Muted │
╰─────────────────────┴─────────────────────┴────────────────╯

Tenant Domain <tenant-domain> Scan Results (severity columns are for fails only):

Subscriptions scanned: <subscription-a-name> (<subscription-a-id>), <subscription-b-name> (<subscription-b-id>), <subscription-c-name> (<subscription-c-id>)
╭────────────┬─────────────┬───────────┬────────────┬────────┬──────────┬───────┬─────────╮
│ Provider   │ Service     │ Status    │   Critical │   High │   Medium │   Low │   Muted │
├────────────┼─────────────┼───────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ azure      │ appinsights │ FAIL (3)  │          0 │      0 │        0 │     3 │       0 │
├────────────┼─────────────┼───────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ azure      │ defender    │ FAIL (12) │          0 │     12 │        0 │     0 │       0 │
├────────────┼─────────────┼───────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ azure      │ entra       │ FAIL (11) │          0 │      5 │        5 │     1 │       0 │
├────────────┼─────────────┼───────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ azure      │ iam         │ FAIL (6)  │          0 │      3 │        3 │     0 │       0 │
├────────────┼─────────────┼───────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ azure      │ monitor     │ FAIL (36) │          0 │     11 │       25 │     0 │       0 │
├────────────┼─────────────┼───────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ azure      │ network     │ FAIL (36) │          0 │     24 │       12 │     0 │       0 │
├────────────┼─────────────┼───────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ azure      │ policy      │ PASS (3)  │          0 │      0 │        0 │     0 │       0 │
├────────────┼─────────────┼───────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ azure      │ sqlserver   │ FAIL (7)  │          1 │      1 │        5 │     0 │       0 │
├────────────┼─────────────┼───────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ azure      │ storage     │ FAIL (82) │          0 │     27 │       47 │     8 │       0 │
├────────────┼─────────────┼───────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ azure      │ vm          │ FAIL (10) │          0 │      4 │        6 │     0 │       0 │
╰────────────┴─────────────┴───────────┴────────────┴────────┴──────────┴───────┴─────────╯
* You only see here those services that contains resources.

Detailed results are in:
 - JSON-OCSF: <output_dir>/prowler-output-<tenant-domain>-<timestamp>.ocsf.json
 - CSV: <output_dir>/prowler-output-<tenant-domain>-<timestamp>.csv
 - HTML: <output_dir>/prowler-output-<tenant-domain>-<timestamp>.html

Compliance Status of C5_AZURE Framework:
╭──────────────────┬──────────────────┬────────────────╮
│ 27.1% (158) FAIL │ 72.9% (425) PASS │ 0.0% (0) MUTED │
╰──────────────────┴──────────────────┴────────────────╯

Compliance Status of CCC_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 28.77% (147) FAIL │ 71.23% (364) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of CIS_2.0_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 51.36% (132) FAIL │ 48.64% (125) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of CIS_2.1_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 52.57% (133) FAIL │ 47.43% (120) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of CIS_3.0_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 53.39% (134) FAIL │ 46.61% (117) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of CIS_4.0_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 29.03% (171) FAIL │ 70.97% (418) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of CIS_5.0_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 29.87% (178) FAIL │ 70.13% (418) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of CIS_6.0_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 28.08% (162) FAIL │ 71.92% (415) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of CIS_CONTROLS_8.1 Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 30.04% (170) FAIL │ 69.96% (396) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of CSA_CCM_4.0 Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 28.92% (179) FAIL │ 71.08% (440) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of DORA_2022_2554 Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 30.16% (187) FAIL │ 69.84% (433) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Estado de Cumplimiento de ENS_RD2022_AZURE:
╭────────────────────────┬─────────────────────┬────────────────╮
│ 51.87% (125) NO CUMPLE │ 48.13% (116) CUMPLE │ 0.0% (0) MUTED │
╰────────────────────────┴─────────────────────┴────────────────╯

Compliance Status of HIPAA_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 27.24% (152) FAIL │ 72.76% (406) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of ISO27001_2022_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 51.93% (121) FAIL │ 48.07% (112) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of MITRE_ATTACK_AZURE Framework:
╭──────────────────┬───────────────────┬────────────────╮
│ 46.92% (99) FAIL │ 53.08% (112) PASS │ 0.0% (0) MUTED │
╰──────────────────┴───────────────────┴────────────────╯

Compliance Status of NIS2_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 51.37% (131) FAIL │ 48.63% (124) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of PCI_4.0_AZURE Framework:
╭──────────────────┬──────────────────┬────────────────╮
│ 42.16% (43) FAIL │ 57.84% (59) PASS │ 0.0% (0) MUTED │
╰──────────────────┴──────────────────┴────────────────╯

Compliance Status of PROWLER_THREATSCORE_AZURE Framework:
╭───────────────────┬──────────────────┬────────────────╮
│ 62.28% (104) FAIL │ 37.72% (63) PASS │ 0.0% (0) MUTED │
╰───────────────────┴──────────────────┴────────────────╯

Compliance Status of RBI_CYBER_SECURITY_FRAMEWORK_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 23.71% (129) FAIL │ 76.29% (415) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of SECNUMCLOUD_3.2_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 25.89% (145) FAIL │ 74.11% (415) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Compliance Status of SOC2_AZURE Framework:
╭───────────────────┬───────────────────┬────────────────╮
│ 48.66% (109) FAIL │ 51.34% (115) PASS │ 0.0% (0) MUTED │
╰───────────────────┴───────────────────┴────────────────╯

Detailed compliance results are in <output_dir>/compliance/


│ You're getting a snapshot 📸. Prowler Cloud gives you the full picture:
│
│ ✓ Send your findings - directly from the Prowler CLI to Prowler Cloud.
│ ✓ Continuous Security Monitoring - custom scheduling and scan configuration with history, trends and alerts.
│ ✓ Triage - review findings, flag false positives and track accepted risk with your team.
│ ✓ Lighthouse AI + MCP - autonomous triage, custom dashboards, prioritization with prevention and remediation.
│ ✓ Alerts - get notified when anything you want is happening.
│ ✓ Live Compliance - dashboards for 50+ frameworks, always up to date.
│ ✓ Remediation - complete guided remediation including Autonomous remediation with Lighthouse AI.
│ ✓ Attack Path Visualization - see how attackers chain risks to reach your crown jewels.
│ ✓ Bulk Provisioning - add your entire AWS Organization in seconds.
│ ✓ Integrations - Anything with our MCP + Jira, Slack, AWS Security Hub, Amazon S3, SSO and RBAC.
│
│ Start free at 👉 cloud.prowler.com

<user>@<host> prowler %
```

### 具体的な検出内容

CS出力時のカラムの構造は以下です。

| # | カラム名 | 意味 |
| --- | --- | --- |
| 1 | `AUTH_METHOD` | スキャン実行に使った認証情報（例: `User: prowler-scanner@...`） |
| 2 | `TIMESTAMP` | この検出結果が生成された日時 |
| 3 | `ACCOUNT_UID` | 対象アカウントの一意ID（AzureならサブスクリプションID） |
| 4 | `ACCOUNT_NAME` | 対象アカウント名（サブスクリプション名） |
| 5 | `ACCOUNT_EMAIL` | アカウントに紐づくメールアドレス（AWSのアカウント登録メール等。Azureでは通常空） |
| 6 | `ACCOUNT_ORGANIZATION_UID` | 組織/テナントの一意ID |
| 7 | `ACCOUNT_ORGANIZATION_NAME` | 組織/テナント名 |
| 8 | `ACCOUNT_TAGS` | アカウントに付与されたタグ |
| 9 | `FINDING_UID` | この検出結果自体の一意ID（プロバイダ・チェックID・リソースIDから生成） |
| 10 | `PROVIDER` | クラウドプロバイダ名（`azure`, `aws`, `gcp` 等） |
| 11 | `CHECK_ID` | 実行されたチェックの識別子（例: `sqlserver_tde_encrypted_with_cmk`） |
| 12 | `CHECK_TITLE` | チェックの人が読める説明タイトル |
| 13 | `CHECK_TYPE` | チェックの分類種別（Prowler内部カテゴリ、空の場合あり） |
| 14 | `STATUS` | 判定結果：`FAIL`（不合格）/ `PASS`（合格） |
| 15 | `STATUS_EXTENDED` | 判定結果の詳細説明文（対象リソース名を含む具体的な理由） |
| 16 | `MUTED` | このfindingがミュート（無視）設定されているか（True/False） |
| 17 | `SERVICE_NAME` | 対象のクラウドサービス名（例: `sqlserver`, `storage`） |
| 18 | `SUBSERVICE_NAME` | サービスのサブカテゴリ（該当する場合） |
| 19 | `SEVERITY` | 重大度：`critical` / `high` / `medium` / `low` |
| 20 | `RESOURCE_TYPE` | 対象リソースの種別（例: `microsoft.sql/servers`） |
| 21 | `RESOURCE_UID` | 対象リソースの一意ID（Azure Resource ID等） |
| 22 | `RESOURCE_NAME` | 対象リソース名 |
| 23 | `RESOURCE_DETAILS` | リソースの追加詳細情報 |
| 24 | `RESOURCE_TAGS` | リソースに付与されたタグ |
| 25 | `PARTITION` | クラウドのパーティション（例: `AzureCloud`, `AzureUSGovernment`） |
| 26 | `REGION` | リソースが存在するリージョン |
| 27 | `DESCRIPTION` | チェック自体が何を確認しているかの説明 |
| 28 | `RISK` | このfindingがFAILである場合のセキュリティリスクの説明 |
| 29 | `RELATED_URL` | 関連する外部URL（参考リンク） |
| 30 | `REMEDIATION_RECOMMENDATION_TEXT` | 修復方法の推奨手順（テキスト） |
| 31 | `REMEDIATION_RECOMMENDATION_URL` | 修復ガイドへのリンク（Prowler Hub等） |
| 32 | `REMEDIATION_CODE_NATIVEIAC` | 修復用のネイティブIaCコード（Azureの場合Bicep） |
| 33 | `REMEDIATION_CODE_TERRAFORM` | 修復用のTerraformコード |
| 34 | `REMEDIATION_CODE_CLI` | 修復用のCLIコマンド（az CLI等） |
| 35 | `REMEDIATION_CODE_OTHER` | その他の修復手順（Azureポータル操作手順など） |
| 36 | `COMPLIANCE` | 対応するコンプライアンスフレームワークのマッピング（SOC2, ISO27001, NIS2, CIS, MITRE-ATTACK等をパイプ区切りで列記） |
| 37 | `CATEGORIES` | このfindingが属するカテゴリ（例: `encryption`） |
| 38 | `DEPENDS_ON` | このfindingが依存する他のfinding（関連性情報） |
| 39 | `RELATED_TO` | このfindingに関連する他のfinding |
| 40 | `NOTES` | 補足メモ・追加コンテキスト |
| 41 | `PROWLER_VERSION` | このスキャンを実行したProwlerのバージョン |
| 42 | `ADDITIONAL_URLS` | 参考になる追加の外部URL（複数） |
| 43 | `ACCOUNT_OU_UID` | 組織単位（OU）の一意ID（該当する場合） |
| 44 | `ACCOUNT_OU_NAME` | 組織単位（OU）の名前（該当する場合） |

## おわりに

いかがでしたでしょうか。今回は、Azure 環境を Prowler でスキャンする場合において実際に手を動かして検証しました。

この記事がどなたかの役に立つと嬉しいです。
