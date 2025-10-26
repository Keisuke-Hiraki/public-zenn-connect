---
title: "Google Cloud 初心者が Prowler と連携してセキュリティアセスメントを実施してみた"
emoji: "✅"
type: "tech"
topics: ["googlecloud", "prowler", "#zennfes2025infra"]
published: true
published_at: 2025-10-23 07:00
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastner](https://cloud-fastener.com/) というプロダクトで TAM をやっています平木です！

普段は AWS のクラウドセキュリティを取り扱うことが多いですが、
今回 Google Cloud 環境のセキュリティアセスメントを Prowler を活用して実施する機会があったため、備忘録も兼ねて執筆したいと思います。

またせっかくなので Google Cloud の各用語の解説なども挟みながら記載してみたいと思います。

https://github.com/prowler-cloud/prowler/

## Prowler とは

Prowler はクラウド環境におけるコンプライアンス状況を監視・チェックし、セキュリティのベストプラクティスのリコメンデーションを受け取れるセキュリティツールです。

SaaS 版と OSS 版の 2 種類あり、今回の記事では OSS 版のケースで執筆したいと思います。

CIS や NIST などのような業界のセキュリティフレームワークを活用し、マルチクラウドに対応しているためコンプライアンス状況のチェックの標準化が可能です。

https://github.com/prowler-cloud/prowler

## 早速やってみる

今回はローカル環境で Prowler を実行し、今回は組織とプロジェクトに対してそれぞれ実行してみたいと思います。

Google Cloud における組織とプロジェクトは、
Google Cloud のテナント構成はツリー状で考えた時のルートにあたる一番上に存在するリソースを`組織`、
具体的なリソースが所属する基本的な単位を`プロジェクト`と呼びます。

プロジェクトを束ねる`フォルダー`も存在しますが、Prowler ではフォルダーの概念が登場することはなさそう（あったらすみません）なので大丈夫です。

### 必要な作業をまとめる

作業の全体像としては以下です。

- 必要なパッケージをそろえる
- サービスアカウントを任意のプロジェクトに作成する
- 権限の設定を行う
- gcloud cli のセットアップを行う
- Prowler を実行

です。それでは細かく見ていきます。

### 必要なパッケージをそろえる

今回の作業環境は以下です。

- Windows コマンドプロンプト
- Python 3.11 (最新バージョンの安定板を利用すれば基本的には問題ないと思います)
- Prowler CLI
- gcloud CLI

Prowler CLI のインストール方法は様々ですが、今回は pip でインストールしました。

```bash
pip install prowler
```

https://docs.prowler.com/getting-started/installation/prowler-cli

Google Cloud のコマンドラインツールの gcloud CLI を Windows 環境にインストールする方法は以下のブログが大変分かりやすいです。

https://blog.g-gen.co.jp/entry/how-to-install-gcloud-to-windows

インストールができたら `gcloud init` で初期化が必要ですが、ここで指定する Project ID は一旦はどこでも大丈夫です。

https://cloud.google.com/sdk/docs/initializing?hl=ja

### サービスアカウントを任意のプロジェクトに作成する

続いてサービスアカウントというものを作っていきます。

Google Cloud では人間が扱うユーザーの ID とアプリケーションなどの Non-Human Identity（NHI:非人間）が扱うサービスアカウントがあります。

こちらのブログが大変分かりやすいです。

https://dev.classmethod.jp/articles/google-cloud-service-account/

今回はこのサービスアカウントの権限借用という一時的にユーザーがサービスアカウントになりすます仕組みを活用します。

なりすますことでアクセスキーを払い出すことなくユーザーを使用できるためセキュリティ上好ましいです。

今回はサービスアカウントになりすました上で Prowler を動かしてみます。

https://docs.cloud.google.com/iam/docs/service-account-impersonation?hl=ja

ではサービスアカウントを作っていきたいと思います。

まず、サービスアカウントを作成したいプロジェクトへ遷移します。
今回は SammplePJ というプロジェクトを用意しました。

![](/images/keisuke-poc2025-10-23-01-05-42.png)

検索メニューで IAM と打ち、IAM へ移動します。候補にサービスアカウントがあればそちらへ既に飛んで大丈夫です。

![](/images/keisuke-poc2025-10-23-01-07-35.png)

IAM > サービスアカウントを選択します。

![](/images/keisuke-poc2025-10-23-01-09-26.png)

「サービスアカウントを作成」を押します。

![](/images/keisuke-poc2025-10-23-01-10-26.png)

任意のサービスアカウント名（今回は`prowler-auditor`）を入力し、権限は触らずに「完了」を押します。

これでサービスアカウントの作成は完了です。

![](/images/keisuke-poc2025-10-23-01-33-04.png)

サービスアカウントのアドレスは後で使用するので控えておいてください。

### 権限の設定を行う

続いて権限周りの設定を行います。

権限は 2 種類設定します。

- サービスアカウントにアクセス権を持つプリンシパルの設定
- サービスアカウントへの権限の追加
  - 単一プロジェクトのみ使用したい場合は、特定のプロジェクトにて実施
  - 組織全体で使用したい場合は、組織ノードにて実施

#### サービスアカウントにアクセス権を持つプリンシパルの設定

サービスアカウントに対してどんなプリンシパルがどんな権限でアクセスできるかの権限の設定をします。

サービスアカウント作成完了するとリストに増えているため、メール列の先ほど作成した分をクリックします。

![](/images/keisuke-poc2025-10-23-01-38-36.png)

「アクセス権を持つプリンシパル」タブを押します。

![](/images/keisuke-poc2025-10-23-01-40-16.png)

「アクセスを許可」を押します。

![](/images/keisuke-poc2025-10-23-01-41-38.png)

新しいプリンシパルに Google Cloud で使用する自身のプリンシパルを入力します。

ロールを割り当てるでは以下 2 種類を指定します。

- `サービスアカウントユーザー`
- `サービスアカウント トークン作成者`

これによって指定したプリンシパルはサービスアカウントになりすます権限が付与されます。

最後「保存」を押し、完了です。

![](/images/keisuke-poc2025-10-23-01-43-26.png)

#### サービスアカウントへの権限の追加

サービスアカウントに何の権限が必要かを定義します。

単一プロジェクトにてセキュリティアセスメントするようであれば、必要なプロジェクトノードへスイッチしてください。
複数プロジェクトまたは組織全体でアセスメントするようであれば、組織ノードへスイッチしてください。

「アクセスを許可」を押します。

![](/images/keisuke-poc2025-10-23-01-48-49.png)

新しいプリンシパルに、サービスアカウントのアドレスを入力します。

ロールを割り当てるに以下を割り当てます。

- `参照者`
- `セキュリティ監査担当者`
- `フォルダ閲覧者`
- `クラウドアセット閲覧者`
- `組織ポリシー閲覧者`

最後「保存」を押します。

![](/images/keisuke-poc2025-10-23-02-11-00.png)

### gcloud cli のセットアップを行う

準備が完了したのでここからコマンドラインの作業に移ります。

まだ gcloud CLI の認証が完了していない場合は以下を実行します。

```bash
gcloud auth application-default login
```

認証が出来たら、サービスアカウントへのなりすまし設定をします。

```bash
gcloud config set auth/impersonate_service_account <サービスアカウントのアドレス>
# (例) gcloud config set auth/impersonate_service_account prowler-auditor@XXX.iam.gserviceaccount.com
```

`Updated property [auth/impersonate_service_account].`と出力されれば OK です。

現在どのアカウントの設定になっているか気になる場合は以下コマンドで見れます。

```bash
gcloud config list
```

すると以下のように返ってきます。

```
[accessibility]
screen_reader = False
[auth]
impersonate_service_account = prowler-auditor@XXX.iam.gserviceaccount.com
[core]
account = sample@example.com
disable_usage_reporting = True
project = samplepj-XXXXXX

Your active configuration is: [default]
```

これでセットアップ完了です。

### Prowler を実行

ここで Prowler を実行します。

3 パターンあります。

```bash
# 単一プロジェクトのみの場合
prowler gcp --project-id <プロジェクト ID>

# 複数プロジェクトの場合
prowler gcp --project-ids <プロジェクト A ID> <プロジェクト B ID> <プロジェクト C ID>...

# 組織全体の場合
prowler gcp --organization-id <組織 ID>
```

各 ID はこちらで確認できます。

![](/images/keisuke-poc2025-10-23-02-27-40.png)

上手く実行開始されると以下のようになります。

![](/images/keisuke-poc2025-10-23-02-37-40.png)

出力全文もこのような形です。

```bash
C:\Users\USER_NAME>prowler gcp --project-id samplepj-XXXXXX
                         _
 _ __  _ __ _____      _| | ___ _ __
| '_ \| '__/ _ \ \ /\ / / |/ _ \ '__|
| |_) | | | (_) \ V  V /| |  __/ |
| .__/|_|  \___/ \_/\_/ |_|\___|_|v5.12.3
|_| the handy multi-cloud security tool

Date: 2025-10-23 02:36:22

-> Using the GCP credentials below:
  · GCP Account: default
  · GCP Project IDs: samplepj-XXXXXX
  · Profile: default

-> Using the following configuration:
  · Config File: C:\Users\USER_NAME\AppData\Local\Programs\Python\Python311\Lib\site-packages\prowler\config/config.yaml

Executing 79 checks, please wait...
-> Scan completed! |▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 79/79 [100%] in 31.3s

Overview Results:
╭────────────────────┬─────────────────┬────────────────╮
│ 100.0% (12) Failed │ 0.0% (0) Passed │ 0.0% (0) Muted │
╰────────────────────┴─────────────────┴────────────────╯

Project ID/s samplepj-XXXXXX Scan Results (severity columns are for fails only):
╭────────────┬───────────┬──────────┬────────────┬────────┬──────────┬───────┬─────────╮
│ Provider   │ Service   │ Status   │   Critical │   High │   Medium │   Low │   Muted │
├────────────┼───────────┼──────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ gcp        │ artifacts │ FAIL (1) │          0 │      0 │        1 │     0 │       0 │
├────────────┼───────────┼──────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ gcp        │ gcr       │ FAIL (1) │          0 │      0 │        1 │     0 │       0 │
├────────────┼───────────┼──────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ gcp        │ iam       │ FAIL (1) │          0 │      1 │        0 │     0 │       0 │
├────────────┼───────────┼──────────┼────────────┼────────┼──────────┼───────┼─────────┤
│ gcp        │ logging   │ FAIL (9) │          0 │      0 │        9 │     0 │       0 │
╰────────────┴───────────┴──────────┴────────────┴────────┴──────────┴───────┴─────────╯
* You only see here those services that contains resources.

Detailed results are in:
 - JSON-OCSF: C:\Users\USER_NAME/output/prowler-output-default-20251023023622.ocsf.json
 - CSV: C:\Users\USER_NAME/output/prowler-output-default-20251023023622.csv
 - HTML: C:\Users\USER_NAME/output/prowler-output-default-20251023023622.html

Compliance Status of CIS_2.0_GCP Framework:
╭──────────────────┬───────────────┬────────────────╮
│ 100.0% (10) FAIL │ 0.0% (0) PASS │ 0.0% (0) MUTED │
╰──────────────────┴───────────────┴────────────────╯

Compliance Status of CIS_3.0_GCP Framework:
╭─────────────────┬───────────────┬────────────────╮
│ 100.0% (9) FAIL │ 0.0% (0) PASS │ 0.0% (0) MUTED │
╰─────────────────┴───────────────┴────────────────╯

Compliance Status of CIS_4.0_GCP Framework:
╭─────────────────┬───────────────┬────────────────╮
│ 100.0% (9) FAIL │ 0.0% (0) PASS │ 0.0% (0) MUTED │
╰─────────────────┴───────────────┴────────────────╯

Estado de Cumplimiento de ENS_RD2022_GCP:
╭───────────────────────┬─────────────────┬────────────────╮
│ 100.0% (11) NO CUMPLE │ 0.0% (0) CUMPLE │ 0.0% (0) MUTED │
╰───────────────────────┴─────────────────┴────────────────╯

Compliance Status of ISO27001_2022_GCP Framework:
╭──────────────────┬───────────────┬────────────────╮
│ 100.0% (10) FAIL │ 0.0% (0) PASS │ 0.0% (0) MUTED │
╰──────────────────┴───────────────┴────────────────╯

Compliance Status of MITRE_ATTACK_GCP Framework:
╭──────────────────┬───────────────┬────────────────╮
│ 100.0% (11) FAIL │ 0.0% (0) PASS │ 0.0% (0) MUTED │
╰──────────────────┴───────────────┴────────────────╯

Compliance Status of NIS2_GCP Framework:
╭──────────────────┬───────────────┬────────────────╮
│ 100.0% (12) FAIL │ 0.0% (0) PASS │ 0.0% (0) MUTED │
╰──────────────────┴───────────────┴────────────────╯

Compliance Status of PCI_4.0_GCP Framework:
╭──────────────────┬───────────────┬────────────────╮
│ 100.0% (10) FAIL │ 0.0% (0) PASS │ 0.0% (0) MUTED │
╰──────────────────┴───────────────┴────────────────╯

Compliance Status of PROWLER_THREATSCORE_GCP Framework:
╭─────────────────┬───────────────┬────────────────╮
│ 100.0% (9) FAIL │ 0.0% (0) PASS │ 0.0% (0) MUTED │
╰─────────────────┴───────────────┴────────────────╯

Compliance Status of SOC2_GCP Framework:
╭──────────────────┬───────────────┬────────────────╮
│ 100.0% (12) FAIL │ 0.0% (0) PASS │ 0.0% (0) MUTED │
╰──────────────────┴───────────────┴────────────────╯

Detailed compliance results are in C:\Users\USER_NAME/output/compliance/


C:\Users\USER_NAME>
```

#### CSV カラムの解説

成果物として出力された CSV ファイルを見るとこのようなカラム構成でした。

| カラム名 | 説明 |
|---------|------|
| **AUTH_METHOD** | 認証方法（例：Principal: default） |
| **TIMESTAMP** | チェック実行日時 |
| **ACCOUNT_UID** | GCP プロジェクト ID |
| **ACCOUNT_NAME** | GCP プロジェクト名 |
| **ACCOUNT_EMAIL** | アカウントのメールアドレス |
| **ACCOUNT_ORGANIZATION_UID** | 組織 ID |
| **ACCOUNT_ORGANIZATION_NAME** | 組織名 |
| **ACCOUNT_TAGS** | アカウントに付与されたタグ |
| **FINDING_UID** | 検出結果の一意識別子 |
| **PROVIDER** | クラウドプロバイダー（gcp） |
| **CHECK_ID** | チェック項目の ID |
| **CHECK_TITLE** | チェック項目のタイトル |
| **CHECK_TYPE** | チェックタイプ（Security、Configuration など） |
| **STATUS** | チェック結果（PASS / FAIL） |
| **STATUS_EXTENDED** | チェック結果の詳細説明 |
| **MUTED** | ミュート設定の有無（True / False） |
| **SERVICE_NAME** | 対象の GCP サービス名 |
| **SUBSERVICE_NAME** | 対象のサブサービス名 |
| **SEVERITY** | 深刻度（critical / high / medium / low） |
| **RESOURCE_TYPE** | リソースタイプ（Service、Network など） |
| **RESOURCE_UID** | リソースの一意識別子 |
| **RESOURCE_NAME** | リソース名 |
| **RESOURCE_DETAILS** | リソースの詳細情報 |
| **RESOURCE_TAGS** | リソースに付与されたタグ |
| **PARTITION** | パーティション情報 |
| **REGION** | リージョン（global など） |
| **DESCRIPTION** | チェック項目の説明 |
| **RISK** | リスクの詳細説明 |
| **RELATED_URL** | 関連ドキュメントの URL |
| **REMEDIATION_RECOMMENDATION_TEXT** | 修正方法の推奨テキスト |
| **REMEDIATION_RECOMMENDATION_URL** | 修正方法の参考 URL |
| **REMEDIATION_CODE_NATIVEIAC** | ネイティブ IaC での修正コード |
| **REMEDIATION_CODE_TERRAFORM** | Terraform での修正コード |
| **REMEDIATION_CODE_CLI** | CLI での修正コマンド |
| **REMEDIATION_CODE_OTHER** | その他の修正方法 |
| **COMPLIANCE** | 準拠しているコンプライアンスフレームワーク（CIS、PCI-DSS など） |
| **CATEGORIES** | カテゴリ分類 |
| **DEPENDS_ON** | 依存関係 |
| **RELATED_TO** | 関連項目 |
| **NOTES** | 備考・注釈 |
| **PROWLER_VERSION** | Prowler のバージョン |


## おわりに

いかがでしたでしょうか。今回はGoogle Cloudの勉強もしつつでしたが、概念はやはりAWSと変わらないものなのかなと思いました。

これからもマルチクラウドを想定した提案などしていけるといいですね！

この記事がどなたかの役に立つと嬉しいです。
