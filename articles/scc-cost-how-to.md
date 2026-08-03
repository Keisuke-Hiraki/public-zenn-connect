---
title: "Security Command Center Premium のコストを1つずつ確認しながら計算する"
emoji: "🧮"
type: "idea"
topics: ["googlecloud", "security", "scc", "cost"]
published: true
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

みなさんは、 Security Command Center（以下 SCC）を使用して Google Cloud のセキュリティ管理を行っていますか？

Google Cloud の SCC は、有効化するティアや課金方式によって費用の考え方が大きく変わります。特に Premium ティアの従量課金（Pay-as-you-go）は「保護対象リソースの使用量に応じた課金」という仕組みのため、事前に見積もりを立てにくいと感じている方も多いのではないでしょうか。

今回は、SCC のティアと課金方式の考え方を1つずつ確認しながら、最終的に自分の環境で従量課金の月額コストの目安を計算できるところまでをまとめます。

:::message
この記事の3行まとめ
- SCC で料金が発生するのは Premium と Enterprise の2ティアで、Premium のみ「従量課金」と「定額サブスクリプション」の両方から選べる（Enterprise は定額サブスクリプションのみ）
- Premium の従量課金は「保護対象リソースの使用量（vCPU 時間相当など）× 単価」で決まり、組織レベルとプロジェクトレベルで単価が異なる
- サービスごとの記入テンプレに使用量を埋めて計算式に当てはめれば、従量課金の月額コストの目安を自分で計算できる
:::

:::message alert
本記事に記載する単価・計算例は執筆時点（2026年8月）の公式情報に基づいていますが、Google Cloud の料金は変更される可能性があります。正式な見積もりの際は必ず最新の公式情報を確認してください。

https://cloud.google.com/security-command-center/pricing?hl=ja
:::

## SCC のサービスティアと課金方式を整理する

SCC には3つのサービスティアがあり、まずどのティアで料金が発生するのか、また各ティアでどの課金方式を選べるのかを把握しておく必要があります。

https://docs.cloud.google.com/security-command-center/docs/service-tiers?hl=ja

| ティア | 概要 | 課金方式 | 有効化の単位 |
| --- | --- | --- | --- |
| Standard | Google Cloud のみを対象とした基本的なセキュリティポスチャー管理 | 無料 | プロジェクトまたは組織 |
| Premium | Standard の全機能に加えて、セキュリティポスチャー管理・攻撃パス分析・脅威検出・コンプライアンスを提供 | 定額サブスクリプション（組織レベルのみ）／従量課金（Pay-as-you-go） | プロジェクトまたは組織 |
| Enterprise | Google Cloud・AWS・Azure をカバーするマルチクラウド CNAPP | 定額サブスクリプションのみ | 組織のみ |

料金が発生するのは Premium と Enterprise の2ティアで、Standard は無料です。このうち Enterprise は定額サブスクリプションのみで、従量課金の選択肢はありません。従量課金が選べるのは Premium だけであり、以降は Premium の従量課金にフォーカスして解説します。

なお、SCC の料金は他の Google Cloud サービスの料金とは別に発生します。また、この従量課金・定額サブスクリプションのいずれを選んでも、Web Security Scanner によるスキャン対象リソースの追加コストなど、SCC 自体の料金には現れない間接的なコストが発生する場合があります。この点は記事後半の「間接的に発生するコスト」で解説します。

### 定額サブスクリプションの考え方

本記事のメインは従量課金の計算方法ですが、Premium・Enterprise の定額サブスクリプションがどのような考え方で価格が決まるかも押さえておきます。

定額サブスクリプションは、超過課金や後日の追加請求が発生しない、予測しやすい価格を提供するプランです。Google Cloud 側の料金は、Google Cloud Marketplace の購入や Premium Support などのプロフェッショナルサービスを除いた、Google Cloud サービスへの支出予測額に基づいて決まります。

- 年間の Google Cloud 総支出（またはその支出コミットメント）が1,500万米ドルを超える場合は、営業担当または Google Cloud パートナーへの問い合わせが必要
- 1,500万米ドル以下の場合、年間の Google Cloud コンポーネントの費用は次のいずれかで計算される
  - 支出コミットメントがない場合：現在の支出水準に基づく年間予測支出額の5％（1年契約で購入）
  - 支出コミットメントがある場合：年間コミットメント額と、成長率を加味した年間予測支出額のうち大きい方の5％
- 年間の最低サブスクリプション費用は15,000米ドル

Enterprise の定額サブスクリプションは、この Google Cloud コンポーネントに加えて、AWS・Azure などの他クラウド環境を監視する分のコンポーネントが別途加算される2階建ての料金体系です。他クラウド分は、監視対象アセット数が Google Cloud 環境に対してどの程度の規模かによって、Google Cloud コンポーネント費用の0％〜（規模に応じて）100％超の追加費用が発生します。

具体的な契約条件（最低契約期間や更新条件など）や他クラウド分の詳細な料率は公式ページで確認してください。

https://cloud.google.com/security-command-center/pricing?hl=ja

## Premium 従量課金の考え方

Premium ティアの従量課金の考え方を理解するために、まず基本となる計算ロジックを確認します。

Premium の従量課金は、サービスごとに定められた課金単位（vCPU 時間、操作回数、処理データ量など）の使用量に、単価を掛けて算出します。多くのサービスは vCPU 時間ベースの単価ですが、Cloud Storage のように操作回数ベース、BigQuery オンデマンドのように処理データ量ベースのサービスもあります。

もう1つ重要なのが、単価は SCC Premium を有効化した単位によって異なる、という点です。

- **組織レベル**で SCC Premium を有効化した場合の単価
- **プロジェクトレベル**で SCC Premium を有効化した場合の単価

同じ使用量でも、組織レベルで有効化した方が単価は低くなります。したがって、複数プロジェクトを組織単位でまとめて保護する場合と、プロジェクト単位で個別に有効化する場合とでは、同じ構成でも月額コストが変わってきます。

なお GKE を Standard モードで実行している場合、ワーカーノードの使用量は Compute Engine の項目に含めて計算します。GKE 関連で個別の単価が設定されているのは Autopilot モードのみです。

この「使用量 × 単価（組織／プロジェクトで異なる）」という考え方を、以降のサービスごとの計算式に当てはめていきます。

## 記入テンプレート

実際に計算する前に、まず自分の環境の使用量を記入するテンプレートを用意しました。このテンプレートに使用量を埋めたうえで、後述する計算式に当てはめると月額コストの目安が算出できます。

:::message
マシンタイプから vCPU 数への換算や、GKE Autopilot の使用量（vCPU 時間）の集計は、見積もりを行う側で実施する前提です。
:::

| サービス | 記入項目 |
| --- | --- |
| Compute Engine（GKE Standard のノードを含む） | マシンタイプ ［　　　　　　　　　］ × ［　　］台（複数行可） |
| GKE Autopilot | 対象期間の合計使用 vCPU 時間 ［　　　　］vCPU時間 |
| Cloud SQL | マシン構成 ［　　　　　　　　　］ × ［　　］インスタンス／可用性 ［ゾーン／高可用性］／リードレプリカ数 ［　　］台 |
| App Engine Standard | インスタンスクラス ［F1／F2／F4／F4_1G など］／最小インスタンス数 ［　　］台 |
| App Engine Flexible | サービス名 ［　　　　　　　　　］／CPU 設定 ［　　］／最小インスタンス数 ［　　］台 |
| Cloud Storage | バケット数 ［　　］個 |
| Artifact Analysis／Artifact Registry | スキャン対象イメージ数 ［　　］個 |
| BigQuery オンデマンド | BigQuery を使用するプロジェクト数 ［　　］個 |
| BigQuery Editions | 予約スロット数 ［　　］スロット |
| Cloud Run | Cloud Run サービス数 ［　　］個 |
| AlloyDB | プライマリのマシンタイプ ［　　　　　　　　　］ × ［　　］台／リードプールのマシンタイプ ［　　　　　　　　　］ × ［　　］台 |
| Model Armor | （固定の暫定前提で計算） |

```
| サービス | 記入項目 |
| --- | --- |
| Compute Engine（GKE Standard のノードを含む） | マシンタイプ ［　　　　　　　　　］ × ［　　］台（複数行可） |
| GKE Autopilot | 対象期間の合計使用 vCPU 時間 ［　　　　］vCPU時間 |
| Cloud SQL | マシン構成 ［　　　　　　　　　］ × ［　　］インスタンス／可用性 ［ゾーン／高可用性］／リードレプリカ数 ［　　］台 |
| App Engine Standard | インスタンスクラス ［F1／F2／F4／F4_1G など］／最小インスタンス数 ［　　］台 |
| App Engine Flexible | サービス名 ［　　　　　　　　　］／CPU 設定 ［　　］／最小インスタンス数 ［　　］台 |
| Cloud Storage | バケット数 ［　　］個 |
| Artifact Analysis／Artifact Registry | スキャン対象イメージ数 ［　　］個 |
| BigQuery オンデマンド | BigQuery を使用するプロジェクト数 ［　　］個 |
| BigQuery Editions | 予約スロット数 ［　　］スロット |
| Cloud Run | Cloud Run サービス数 ［　　］個 |
| AlloyDB | プライマリのマシンタイプ ［　　　　　　　　　］ × ［　　］台／リードプールのマシンタイプ ［　　　　　　　　　］ × ［　　］台 |
| Model Armor | （固定の暫定前提で計算） |
```

記入し終えたら、次のセクションでサービスごとに計算式を確認していきます。

:::message
テンプレートの各項目は、Google Cloud CLI（`gcloud` / `bq`）のコマンドで確認できるものが多くあります。各サービスの節に確認用コマンドの例を掲載していますが、CLI のオプションはバージョンによって変わることがあるため、実行前に `gcloud <サブコマンド> --help` で最新のオプションを確認してください。
:::

## サービスごとの計算式

ここからはサービスごとに、テンプレートに記入した使用量をどのように計算式に当てはめるかを確認します。単価はいずれも米ドルです。

### Compute Engine（GKE Standard のノードを含む）

Compute Engine は、マシンタイプごとの月額換算額に台数を掛けて計算します。GKE を Standard モードで実行している場合、そのワーカーノードもこの Compute Engine の使用量に含めて計算します。同一環境に複数のマシンタイプが混在する場合は、マシンタイプごとに計算して合算します。

マシンタイプ別の台数は、以下のコマンドで確認できます。720時間稼働している前提で計算するため、`status=RUNNING` で稼働中のインスタンスのみに絞り込みます。

```bash
gcloud compute instances list --filter="status=RUNNING" --format="value(machineType.basename())" | sort | uniq -c
```

GKE Standard のノードプールを個別に確認したい場合は以下のコマンドを使いますが、`initialNodeCount` はノードプール作成時点の初期ノード数であり、オートスケーリングや手動でのリサイズ後の現在のノード数とは異なる場合があります。GKE のノードは Compute Engine の一種として作成されるため、実際の現在のノード数を確認する場合は GKE が自動付与するラベルで Compute Engine 側を絞り込む方法が確実です。

```bash
gcloud compute instances list --filter="status=RUNNING AND labels.goog-k8s-cluster-name=CLUSTER_NAME AND labels.goog-k8s-cluster-location=LOCATION" --format="value(machineType.basename())" | sort | uniq -c
```

:::message
上記でクラスタ別に集計した台数を、最初の `gcloud compute instances list` の結果に別途加算すると二重計上になります。あくまで「全体の台数のうち、どれが GKE のものか」を確認する目的で使ってください。
:::

計算式：
- 組織レベル ＝ 各マシンタイプの月額換算額 × 台数の合計
- プロジェクトレベル ＝ 各マシンタイプの月額換算額 × 台数の合計

計算例（e2-standard-4 × 3台、vCPU数4として計算）：
- 組織レベル ＝ 4 × 3台 × 720時間 × 0.0057米ドル ＝ 49.248米ドル／月
- プロジェクトレベル ＝ 4 × 3台 × 720時間 × 0.0071米ドル ＝ 61.344米ドル／月

:::message alert
GKE Standard のノードを Compute Engine の台数として計算したうえで、GKE Autopilot の計算にも同じリソースを含めてしまうと二重計上になります。Standard モードのクラスタと Autopilot モードのクラスタは、それぞれ別のクラスタとして扱ってください。
:::

### GKE Autopilot

GKE Autopilot は Standard モードとは異なる単価が設定されており、クラスタ数ではなく実際に使用した vCPU 時間の合計に応じて課金されます。クラスタ数から一定の前提で概算することはできないため、対象期間中に使用した vCPU 時間の合計を確認する必要があります。

Autopilot クラスタの一覧自体は以下のコマンドで確認できますが、実際の使用 vCPU 時間は Cloud Monitoring のメトリクスや Cloud Billing のレポートから確認してください。

```bash
gcloud container clusters list --filter="autopilot.enabled=true" --format="value(name)"
```

計算式：
- 組織レベル ＝ 使用 vCPU 時間の合計 ÷ 1,000 × 0.0057米ドル
- プロジェクトレベル ＝ 使用 vCPU 時間の合計 ÷ 1,000 × 0.0071米ドル

計算例（使用 vCPU 時間の合計が5,000時間の場合）：
- 組織レベル ＝ 5,000 ÷ 1,000 × 0.0057米ドル ＝ 0.0285米ドル／月
- プロジェクトレベル ＝ 5,000 ÷ 1,000 × 0.0071米ドル ＝ 0.0355米ドル／月

### Cloud SQL

Cloud SQL は、通常インスタンス数にリードレプリカ数と高可用性構成時のスタンバイ数を加えた「構成台数」に、マシン構成別の月額換算額を掛けて計算します。

インスタンスのマシン構成・可用性タイプ・インスタンス種別は、以下のコマンドで確認できます。

```bash
gcloud sql instances list --format="table(name,settings.tier,settings.availabilityType,instanceType)"
```

計算式：
- 構成台数 ＝ 通常インスタンス数 ＋ リードレプリカ数 ＋ 高可用性構成の場合のスタンバイ数
- 組織レベル ＝ マシン構成別月額換算額 × 構成台数
- プロジェクトレベル ＝ マシン構成別月額換算額 × 構成台数

:::message
高可用性構成は、プライマリとスタンバイの2台分として概算します。
:::

### App Engine Standard

App Engine Standard は、最小インスタンス数に単価を掛けて計算します。インスタンスクラスによる単価差は本記事では簡略化しています。

対象バージョンのインスタンスクラスと最小インスタンス数は、以下のコマンドで確認できます。

```bash
gcloud app versions describe VERSION_ID --service=SERVICE_ID --format="table(instanceClass,automaticScaling.minTotalInstances)"
```

計算式：
- 組織レベル ＝ 最小インスタンス数 × 720時間 × 0.001425米ドル ＝ 最小インスタンス数 × 1.026米ドル
- プロジェクトレベル ＝ 最小インスタンス数 × 720時間 × 0.001781米ドル ＝ 最小インスタンス数 × 1.28232米ドル

### App Engine Flexible

App Engine Flexible は、CPU 設定と最小インスタンス数を組み合わせて計算します。

対象バージョンの CPU 設定と最小インスタンス数は、以下のコマンドで確認できます。

```bash
gcloud app versions describe VERSION_ID --service=SERVICE_ID --format="table(resources.cpu,automaticScaling.minTotalInstances)"
```

計算式：
- 組織レベル ＝ CPU 設定 × 最小インスタンス数 × 720時間 × 0.0057米ドル
- プロジェクトレベル ＝ CPU 設定 × 最小インスタンス数 × 720時間 × 0.0071米ドル

### Cloud Storage

Cloud Storage はバケット数ベースで計算します。1バケットあたり Class A 操作 100,000回／月、Class B 操作 1,000,000回／月という暫定前提を置いています。

プロジェクト内のバケット数は、以下のコマンドで確認できます。

```bash
gcloud storage buckets list --format="value(name)" | wc -l
```

計算式：
- 組織レベル ＝ バケット数 × 100,000回 ÷ 1,000 × 0.0016米ドル ＋ バケット数 × 1,000,000回 ÷ 1,000 × 0.00016米ドル ＝ バケット数 × 0.32米ドル
- プロジェクトレベル ＝ バケット数 × 100,000回 ÷ 1,000 × 0.002米ドル ＋ バケット数 × 1,000,000回 ÷ 1,000 × 0.0002米ドル ＝ バケット数 × 0.40米ドル

### Artifact Analysis／Artifact Registry

スキャン対象イメージ数ベースで計算します。1イメージあたり月4回スキャンされるという暫定前提です。組織レベルとプロジェクトレベルで単価差はありません。

:::message
Artifact Analysis によるスキャンは、Artifact Registry や GKE 自体の利用料を増加させません。この単価は SCC Premium 自体の従量課金分です。
:::

指定リポジトリ内のイメージ数は、以下のコマンドで確認できます（リポジトリが複数ある場合はリポジトリごとに実行します）。

```bash
gcloud artifacts docker images list LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY --format="value(package)" | wc -l
```

計算式：
- 組織レベル・プロジェクトレベル共通 ＝ イメージ数 × 4回 × 0.20米ドル ＝ イメージ数 × 0.80米ドル

### BigQuery オンデマンド

BigQuery を使用するプロジェクト数ベースで計算します。1プロジェクトあたり月10TiBを処理するという暫定前提です。

組織内で BigQuery のデータセットを持つプロジェクト数は、Cloud Asset Inventory を使って以下のコマンドで確認できます（`project` は `projects/{PROJECT_NUMBER}` 形式で返るため、重複排除の単位としてそのまま利用できます）。

```bash
gcloud asset search-all-resources --scope=organizations/ORG_ID --asset-types=bigquery.googleapis.com/Dataset --format="value(project)" | sort -u | wc -l
```

:::message alert
このコマンドで分かるのは「BigQuery のデータセットを保有しているプロジェクト数」であり、概算のための代理指標です。実際にクエリを実行して処理データ量が発生したプロジェクト数や、他プロジェクトのデータセットに対してクエリを実行しているプロジェクトは、この方法では把握できません。より正確な月間処理量を確認したい場合は、`INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION` ビューで `project_id` と `total_bytes_billed` を集計する方法もあります（組織レベルの `roles/bigquery.resourceViewer` 権限が必要です）。
:::

計算式：
- 組織レベル ＝ プロジェクト数 × 10TiB × 0.80米ドル ＝ プロジェクト数 × 8.00米ドル
- プロジェクトレベル ＝ プロジェクト数 × 10TiB × 1.00米ドル ＝ プロジェクト数 × 10.00米ドル

### BigQuery Editions

予約スロット数ベースで計算します。

:::message
公式の計算例では1か月の平均稼働時間として730時間（365日÷12か月×24時間）が使われていますが、本記事では他サービスとの計算のシンプルさを優先し、720時間（24時間×30日）を暫定的な前提として使用しています。より厳密に計算したい場合は730時間で計算してください。
:::

予約（Reservation）のスロット数は、Cloud SDK に含まれる `bq` コマンドで確認できます。

```bash
bq ls --reservation --project_id=PROJECT_ID --location=LOCATION
```

計算式（720時間で計算する場合）：
- 組織レベル ＝ スロット数 × 720時間 × 0.004384米ドル ＝ スロット数 × 3.15648米ドル
- プロジェクトレベル ＝ スロット数 × 720時間 × 0.00548米ドル ＝ スロット数 × 3.9456米ドル

### Cloud Run

Cloud Run サービス数ベースで計算します。1サービスあたり 1 vCPU、1インスタンス相当が720時間稼働するという暫定前提です。

プロジェクト内の Cloud Run サービス数は、以下のコマンドで確認できます。`--region` を指定しなければ既定でプロジェクト内の全リージョンが対象になりますが、`run/region` プロパティを設定している環境やリージョン別エンドポイントを有効にしている環境では挙動が変わることがあるため、実行結果のリージョン列で意図した範囲になっているか確認してください。

```bash
gcloud run services list --format="value(metadata.name)" | wc -l
```

:::message
サービス数はスケール・トゥ・ゼロや複数インスタンスへのスケールアウトを反映しません。「1サービスあたり 1 vCPU、1インスタンス相当が720時間稼働する」という前提はあくまで暫定的な目安である点に注意してください。
:::

計算式：
- 組織レベル ＝ サービス数 × 1 × 720時間 × 0.0057米ドル ＝ サービス数 × 4.104米ドル
- プロジェクトレベル ＝ サービス数 × 1 × 720時間 × 0.0071米ドル ＝ サービス数 × 5.112米ドル

### AlloyDB

プライマリとリードプールのマシンタイプ別インスタンス数を合計して計算します。

クラスタ内のインスタンス種別・マシン構成は、以下のコマンドで確認できます。

```bash
gcloud alloydb instances list --cluster=CLUSTER_ID --region=REGION --format="table(name,instanceType,machineConfig.cpuCount,readPoolConfig.nodeCount)"
```

:::message alert
リードプール（`READ_POOL`）は1つのインスタンスリソースの中に複数ノードを持てるため、単純にインスタンス数を数えるだけでは台数を過少に見積もってしまう可能性があります。`PRIMARY` と `SECONDARY`（高可用性構成のスタンバイ）はインスタンス数として1台ずつ数え、`READ_POOL` は `readPoolConfig.nodeCount` の値をノード数として掛け合わせてください。
:::

計算式：
- 構成台数 ＝ プライマリ・セカンダリのインスタンス数 ＋ リードプールの `readPoolConfig.nodeCount` の合計
- 組織レベル ＝ 各マシンタイプの月額換算額 × 構成台数
- プロジェクトレベル ＝ 各マシンタイプの月額換算額 × 構成台数

### Model Armor

Model Armor は SCC Premium・Enterprise に含まれており、単体購入することもできます。従量課金は月間の利用トークン数に応じて発生しますが、無料で使える範囲（無料枠）はプランによって異なります。

- Enterprise または Premium のサブスクリプション：月間30億トークンまで無料
- Premium の従量課金（組織レベル・プロジェクトレベルいずれも）：月間200万トークンまで無料
- Model Armor を単体で利用する場合：月間200万トークンまで無料

無料枠を超えた分は、いずれのプランでも100万トークンあたり0.10米ドルです。本記事は Premium の従量課金を前提にしているため、月間200万トークンの無料枠で計算します。ここでは月間10,000,000トークンを使用するという暫定前提を置いて計算します。

:::message
Model Armor のトークン使用量はリソースの一覧取得ではなく利用量メトリクスにあたるため、他のサービスのような単純な CLI の一覧コマンドはありません。実際の使用量を確認する場合は Cloud Monitoring や請求データのエクスポートを利用してください。
:::

計算式（従量課金・月間10,000,000トークン使用の場合）：
- 組織レベル・プロジェクトレベル共通 ＝ （10,000,000 － 2,000,000）÷ 1,000,000 × 0.10米ドル ＝ 0.80米ドル

## 間接的に発生するコスト

SCC 自体の料金とは別に、ティアや課金方式に関わらず発生しうる間接的なコストもあります。見積もりの際にはこれらも念頭に置いておくと安心です。

- **追加のスキャナーの利用料**：Sensitive Data Protection やサードパーティ製スキャナーなど、SCC にデータを追加する有料スキャナーを使う場合、それぞれの提供元の利用料が別途発生します
- **脆弱性スキャン対象リソースの増加コスト**：Web Security Scanner のような組み込みの脆弱性スキャナーは、スキャン対象となる App Engine・Compute Engine・GKE のリソース使用量やネットワーク送信（egress）トラフィックを増加させることがあります。ただし Artifact Analysis による Artifact Registry・GKE のスキャンは、これらのリソースコストを増加させません
- **ログの取り込み・保存コスト**：SCC の検出結果などのログデータの取り込みや保存には、別途 Cloud Logging の料金が発生します
- **他クラウドのデータ取り込み・保存コスト**：Enterprise ティアでマルチクラウド対応を利用する場合、他クラウドからのデータ取り込みや保存に伴うコストが発生することがあります

これらの間接的なコストは、請求上 SCC やその関連サービスのものとして明示されないため、見落としやすい点として注意が必要です。

## 合計を計算する

各サービスの月額概算額を計算できたら、それらを単純に足し合わせるだけで SCC Premium 従量課金の月額概算が求められます。

SCC Premium 従量課金 月額概算 ＝ Compute Engine概算額（GKE Standard含む） ＋ GKE Autopilot概算額 ＋ Cloud SQL概算額 ＋ App Engine概算額 ＋ Cloud Storage概算額 ＋ Artifact Registry概算額 ＋ BigQuery概算額 ＋ Cloud Run概算額 ＋ AlloyDB概算額 ＋ Model Armor概算額

実際にテンプレートへ数値を入れて計算してみます。

前提として、以下のような構成を想定します。

- Compute Engine：e2-standard-4（vCPU4） × 3台
- GKE Autopilot：対象期間の使用 vCPU 時間の合計が5,000時間
- Cloud Storage：5バケット
- Artifact Registry：10イメージ
- BigQuery オンデマンド：3プロジェクト
- Cloud Run：4サービス
- Model Armor：暫定前提どおり（月間10,000,000トークン使用）

| サービス | 組織レベル | プロジェクトレベル |
| --- | --- | --- |
| Compute Engine | 49.2480米ドル | 61.3440米ドル |
| GKE Autopilot | 0.0285米ドル | 0.0355米ドル |
| Cloud Storage | 1.6000米ドル | 2.0000米ドル |
| Artifact Registry | 8.0000米ドル | 8.0000米ドル |
| BigQuery オンデマンド | 24.0000米ドル | 30.0000米ドル |
| Cloud Run | 16.4160米ドル | 20.4480米ドル |
| Model Armor | 0.8000米ドル | 0.8000米ドル |
| **合計** | **約100.09米ドル／月** | **約122.63米ドル／月** |

同じ構成でも、組織レベルで有効化した方がプロジェクトレベルより月額で約22米ドル安くなることが分かります。GKE Autopilot は使用 vCPU 時間ベースであるため、Compute Engine のような台数ベースのサービスと比べて金額のスケール感が大きく異なる点にも注意してください。

## まとめ

SCC のコストを考える際は、まず料金が発生するのは Premium と Enterprise であり、そのうち従量課金を選べるのは Premium だけである、という点を押さえたうえで、「使用量 × 単価」という基本の計算ロジックに立ち返るのが分かりやすいと思います。

記入テンプレートに自分の環境の使用量を埋め、サービスごとの計算式に当てはめて合算すれば、正式な見積もりの前段として従量課金の月額コストの目安を自分で掴むことができます。コストの予測しやすさを重視する場合は、この従量課金の目安と合わせて、定額サブスクリプションの見積もりも営業担当に確認するとよいでしょう。

繰り返しになりますが、単価や課金対象サービスは変更される可能性があるため、実際の契約や見積もりの際は必ず最新の公式情報を確認するか、Google Cloud の担当窓口に確認するようにしてください。

この記事がどなたかの役に立つと嬉しいです。
