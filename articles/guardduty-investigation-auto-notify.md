---
title: "GuardDuty Investigation の分析完了を Lambda Durable Functions を活用して自動通知してみた"
emoji: "🔬"
type: "tech"
topics: ["aws", "guardduty", "security", "lambda"]
published: false
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

本日 GuardDuty に **Investigation (Preview)** という機能が追加されました。  
Finding や AWS アカウントの脅威ポスチャを AI が自動分析してくれる機能で、有効化してざっと試してみた内容をスクラップにまとめています。

https://zenn.dev/khirasan/scraps/3fba320e241a9f

機能概要自体はすでにクラスメソッドさんにてわかりやすくまとめてくださっている方がいます。

https://dev.classmethod.jp/articles/guardduty-investigation-preview-trial/

今回は「Finding が発生したら自動で Investigation を開始して、結果が出たら Slack に通知する」仕組みを実際に作ってみた内容を書いていきます。

:::message
この記事のポイント

- GuardDuty Investigation は非同期 API のため、完了を待つ仕組みが必要
- EventBridge → Lambda Durable Functions の構成で、単一関数に Finding 検知〜AI 分析〜Slack 通知までをまとめて実装できる
- Lambda Durable Functions の `context.wait()` を使うと、ポーリング待機中はコンピューティングリソースを消費しない
:::

## 作るもの

GuardDuty が Finding を検知したタイミングで Investigation を自動起動し、分析が完了したら Slack に通知するフローです。

Investigation の API は非同期で処理が走り、数分〜十数分後に完了します。通常の Lambda でポーリングループを書くと最大 15 分のタイムアウト制限が問題になりますが、今回は **Lambda Durable Functions** を使うことでこの問題をシンプルに解決します。

## Lambda Durable Functions とは

Lambda Durable Functions は 2025 年に追加された Lambda のネイティブ機能で、長時間実行されるマルチステップのワークフローを Lambda 単体で構築できます。

通常の Lambda では途中で状態を保持できませんが、Durable Functions はチェックポイント＆リプレイの仕組みにより、関数が再起動されても前回の続きから処理を再開します。`context.wait()` でサスペンドしている間はコンピューティングリソースが消費されないため、数時間・数日にわたる待機も追加コストなく実現できます。

Step Functions との比較で言うと、Step Functions はステートマシン定義（ASL）を別途書く必要があるのに対して、Durable Functions は通常の Python コードでワークフローを表現できます。GuardDuty Investigation のような「単一サービスの API を叩いて待つだけ」のシンプルなポーリングには Durable Functions のほうが向いています。

## アーキテクチャ

![](/images/ChatGPT_Image_2026年6月23日 20_52_15.png)

Step Functions のステートマシン定義は不要で、単一の Lambda 関数にすべてのロジックが収まります。

## 実装

### EventBridge ルール

Critical（Severity ≥ 9）の Finding のみに絞ってトリガーします。プレビュー中は 1 アカウントあたり 1 日 10 件・合計 100 件の制限があるため、最も緊急度の高い Critical に限定するのが無難です。

```json
{
  "source": ["aws.guardduty"],
  "detail-type": ["GuardDuty Finding"],
  "detail": {
    "severity": [{
      "numeric": [">=", 9]
    }]
  }
}
```

CLI で作成する場合は次のとおりです。ターゲットには後述のバージョン付き ARN を指定します。

```bash
# ルールを作成
aws events put-rule \
  --name guardduty-investigation-trigger \
  --event-pattern '{"source":["aws.guardduty"],"detail-type":["GuardDuty Finding"],"detail":{"severity":[{"numeric":[">=",9]}]}}' \
  --state ENABLED \
  --region ap-northeast-1

# Lambda を EventBridge のターゲットに追加（バージョン付き ARN を使う）
aws events put-targets \
  --rule guardduty-investigation-trigger \
  --targets 'Id=guardduty-investigation-notifier,Arn=arn:aws:lambda:ap-northeast-1:<ACCOUNT_ID>:function:guardduty-investigation-notifier:1' \
  --region ap-northeast-1

# Lambda 側にも EventBridge からの invoke 許可を付与
aws lambda add-permission \
  --function-name guardduty-investigation-notifier:1 \
  --statement-id allow-eventbridge \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:ap-northeast-1:<ACCOUNT_ID>:rule/guardduty-investigation-trigger \
  --region ap-northeast-1
```

### Lambda Durable Function

`@durable_execution` デコレータをハンドラに付けることで Durable Functions が有効になります。各処理ステップは `@durable_step` デコレータを付けた関数として定義し、`context.step()` で呼び出します。

ソースコードは GitHub に置いています。

https://github.com/Keisuke-Hiraki/public-zenn-connect/blob/main/codes/guardduty-investigation/lambda_function.py

主要な処理の流れを抜粋して説明します。

**Investigation の開始**

`TriggerPrompt` にアカウント ID を渡すことで、アカウント全体の脅威ポスチャを分析対象にします。AWS コンソールから手動実行したときと同じプロンプト形式に、トリガーした Finding タイプを補足情報として添えています。

```python
@durable_step
def start_investigation(step_context, account_id, finding_type):
    resp = guardduty.create_investigation(
        DetectorId=DETECTOR_ID,
        TriggerPrompt=f"Analyze organization account with account id: {account_id}. Triggered by finding type: {finding_type}.",
    )
    return resp['InvestigationId']
```

`TriggerPrompt` の書き方によって Investigation の分析スコープが変わります。今回はアカウントスコープで実施しましたが、Finding を直接指定したり、Organizations 全体を対象にすることも可能です。

| スコープ | TriggerPrompt の例 |
| --- | --- |
| アカウント（今回） | `Analyze organization account with account id: {account_id}.` |
| Finding 指定 | `Analyze finding with id: {finding_id} in account {account_id}.` |
| Organizations 全体 | `Analyze AWS organization with management account id: {management_account_id}.` |

Finding 指定は特定の検知に絞った詳細分析に向いており、Organizations 全体はより広い視点での脅威ポスチャ把握に有効です。ただし、スコープが広いほど分析に時間がかかる傾向があります。

**ポーリングループ**

`context.wait()` でサスペンドし、1 分ごとにステータスを確認します。COMPLETED または FAILED になるまでループします。

```python
@durable_execution
def lambda_handler(event, context: DurableContext):
    detail = event['detail']
    investigation_id = context.step(start_investigation(detail['accountId'], detail['type']))

    while True:
        context.wait(Duration.from_minutes(1))
        result = context.step(get_investigation_status(investigation_id))
        if result['status'] in ('COMPLETED', 'FAILED'):
            break

    context.step(send_slack_notification(result, detail['type'], detail['accountId'], detail['id']))
```

**日本語化と URL 無効化**

Investigation のレスポンス（リスク評価・概要・推奨事項）はすべて英語で返ってくるため、Amazon Translate で日本語に変換します。また、通知テキスト内のドメインや URL は `defang_urls()` で無効化します。

```python
def defang_urls(text):
    import re
    text = re.sub(r'https?://', lambda m: m.group().replace('http', 'hxxp'), text)
    text = re.sub(r'(?<=[a-zA-Z0-9])\.((?:[a-zA-Z0-9-]+\.)*[a-zA-Z]{2,})', lambda m: '[.]' + m.group(1), text)
    return text

def translate_to_ja(text):
    if not text:
        return text
    resp = translate.translate_text(Text=text, SourceLanguageCode='en', TargetLanguageCode='ja')
    return defang_urls(resp['TranslatedText'])
```

**推奨事項の取得**

`GetInvestigation` のレスポンスに含まれる `Summary` JSON の中に `recommendations` フィールドがあり、IMMEDIATE / SHORT_TERM の優先度付きで推奨対応が取得できます。これも翻訳して通知に含めます。

```python
summary = json.loads(inv.get('Summary', '{}'))
recommendations = summary.get('recommendations', {}).get('items', [])
```

ポイントをいくつか補足します。

**`context.wait()` の間はコストゼロ**

`context.wait(Duration.from_minutes(1))` でサスペンドしている 1 分間は Lambda のコンピューティングリソースが消費されません。実際の動作確認では Investigation の完了まで約 5 分かかり 4 回のポーリング待機がありましたが、その間の Lambda 課金はゼロです。

**チェックポイントにより途中から再開できる**

`context.step()` で包んだ処理はチェックポイントが記録されます。`start_investigation` が完了した後に何らかの理由で関数が再起動されても、CreateInvestigation を再度呼び出すことなく続きから再開します。

:::message alert
プレビュー期間中は Finding analysis の対象が Extended Threat Detection（XTD）の全 Finding と一部プランの Finding に限られます。対象外の Finding を指定した場合は `FAILED` になる可能性があります。
:::

### 必要な IAM 権限

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "guardduty:CreateInvestigation",
        "guardduty:GetInvestigation"
      ],
      "Resource": "arn:aws:guardduty:<REGION>:<ACCOUNT_ID>:detector/<DETECTOR_ID>/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:CheckpointDurableExecution",
        "lambda:GetDurableExecutionState"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "translate:TranslateText",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:<REGION>:<ACCOUNT_ID>:secret:guardduty-slack-webhook*"
    }
  ]
}
```

GuardDuty の `Resource` は `detector/<DETECTOR_ID>/*` とワイルドカードを付けることで、detector 配下の investigation リソースまでカバーします。`detector/<DETECTOR_ID>` のみにすると `CreateInvestigation` の呼び出し時に AccessDenied になるので注意が必要です。実際に構築してみてハマったポイントでした。

`lambda:CheckpointDurableExecution` と `lambda:GetDurableExecutionState` は Durable Functions のチェックポイント操作に必要な権限です。コンソールから「Enable durable execution」を有効にして関数を作成すると、実行ロールにこれらが自動で付与されます。

CLI でロールとポリシーを作成する場合は次のとおりです。

```bash
# 信頼ポリシーのファイルを作成
cat > /tmp/trust-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name guardduty-investigation-notifier-role \
  --assume-role-policy-document file:///tmp/trust-policy.json

aws iam put-role-policy \
  --role-name guardduty-investigation-notifier-role \
  --policy-name guardduty-investigation-notifier-policy \
  --policy-document file:///tmp/policy.json
```

### Secrets Manager への Slack Webhook URL の登録

Slack の Incoming Webhook URL を Secrets Manager に格納します。Lambda の環境変数に直接 URL を持たせないことで、ローテーションや権限管理がしやすくなります。

まず Slack の管理画面から Incoming Webhook の URL を取得し、以下のコマンドで登録します。

```bash
aws secretsmanager create-secret \
  --name guardduty-slack-webhook \
  --secret-string '{"webhook_url": "https://hooks.slack.com/services/<WORKSPACE_ID>/<APP_ID>/<TOKEN>"}' \
  --region ap-northeast-1
```

Lambda 側では環境変数 `SLACK_SECRET_NAME` にシークレット名（`guardduty-slack-webhook`）を渡し、実行時に `GetSecretValue` で取得します。シークレット名を変える場合は Lambda の環境変数も合わせて変更してください。

### Lambda 関数のデプロイ

Lambda Durable Functions を使う場合、コンソールの関数作成画面で「Enable durable execution」を有効にして作成するか、CLI では `--durable-config` オプションが必要です。

```bash
# SDK を含めてパッケージを作成
pip install aws_durable_execution_sdk_python -t /tmp/package
cp lambda_function.py /tmp/package/
cd /tmp/package && zip -r ../guardduty-investigation.zip .

# 関数を作成（Durable 設定付き）
aws lambda create-function \
  --function-name guardduty-investigation-notifier \
  --runtime python3.12 \
  --role arn:aws:iam::<ACCOUNT_ID>:role/guardduty-investigation-notifier-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb:///tmp/guardduty-investigation.zip \
  --environment "Variables={DETECTOR_ID=<DETECTOR_ID>,SLACK_SECRET_NAME=guardduty-slack-webhook}" \
  --timeout 30 \
  --durable-config '{"RetentionPeriodInDays": 7, "ExecutionTimeout": 3600}' \
  --region ap-northeast-1

# バージョンを発行して EventBridge のターゲットにはバージョン付き ARN を指定する
aws lambda publish-version \
  --function-name guardduty-investigation-notifier \
  --region ap-northeast-1
```

`--durable-config` の `ExecutionTimeout` が必須で、省略すると `InvalidParameterValueException` になります。また、Durable Functions は **バージョン固定した ARN を使った呼び出しが必要** です。`$LATEST` を使うとチェックポイントリプレイ時にコードの不整合が起きる可能性があるため、デプロイ後に必ずバージョンを発行し、EventBridge のターゲットにはバージョン付き ARN を指定してください。

## EventBridge で完了を検知できれば Durable Functions は不要になる

今回 Durable Functions でポーリングしている理由は、**GuardDuty Investigation の完了を EventBridge で検知できないから**です。

GuardDuty が EventBridge に送るイベントは現時点では `GuardDuty Finding`（Finding の生成・更新）のみで、Investigation の `COMPLETED` / `FAILED` に相当するイベントタイプは存在しません。

もし将来的に Investigation 完了イベントが追加されれば、以下のようにシンプルな構成に変えられます。

```
Finding 生成
  → Lambda① で CreateInvestigation して終了（数秒で完了）
  → EventBridge "GuardDuty Investigation Completed" を受け取る（将来対応時）
  → Lambda② で GetInvestigation → Slack 通知（数秒で完了）
```

この構成であれば Durable Functions は不要で、Lambda 2 本と EventBridge ルール 2 本だけで済みます。

## 動作確認

有効化の手順や Finding を発生させた様子はスクラップを参照してください。

https://zenn.dev/khirasan/scraps/3fba320e241a9f

### テスト Finding の生成

GuardDuty の検証用 EC2 インスタンスに Systems Manager Session Manager 経由でアクセスし、C&C サーバーとして登録されているドメインへ `dig` コマンドを実行することで `Backdoor:EC2/C&CActivity.B!DNS` の Finding を発生させました。

```bash
aws ssm send-command \
  --instance-ids <INSTANCE_ID> \
  --document-name AWS-RunShellScript \
  --parameters 'commands=["dig guarddutyc2activityb.com"]' \
  --region ap-northeast-1
```

Finding が生成された後、EventBridge の配信は `FindingPublishingFrequency: FIFTEEN_MINUTES` の設定に依存します。同じ Finding タイプの 2 回目以降の発生は最大 15 分の集約ウィンドウで届くため、初回のトリガー確認には少し待つか、新規 Finding タイプを発生させるのが確実です。

### 実行確認

非同期 invoke で動作を確認できます。Durable Function は同期 invoke だと `ExecutionTimeout` が 15 分を超える場合にエラーになるため、`--invocation-type Event` が必要です。

```bash
aws lambda invoke \
  --function-name guardduty-investigation-notifier:1 \
  --invocation-type Event \
  --payload '{"detail":{"id":"<FINDING_ID>","accountId":"<ACCOUNT_ID>","type":"Backdoor:EC2/C&CActivity.B!DNS","severity":9.0}}' \
  --cli-binary-format raw-in-base64-out \
  output.json
```

実行が開始されると `DurableExecutionArn` が返ってきます。

```json
{
    "StatusCode": 202,
    "DurableExecutionArn": "arn:aws:lambda:ap-northeast-1:<ACCOUNT_ID>:function:guardduty-investigation-notifier:1/durable-execution/..."
}
```

実行状況は `list-durable-executions-by-function` で確認できます。

```bash
aws lambda list-durable-executions-by-function \
  --function-name guardduty-investigation-notifier \
  --region ap-northeast-1
```

```json
{
    "DurableExecutions": [
        {
            "DurableExecutionName": "<EXECUTION_ID>",
            "Status": "SUCCEEDED",
            "StartTimestamp": "2026-06-23T19:50:03.054000+09:00",
            "EndTimestamp": "2026-06-23T19:55:23.193000+09:00"
        }
    ]
}
```

### 実行ログの流れ

CloudWatch Logs でステップごとの処理を追えます。実際に動かしたときのログがこちらです。

```
19:50:16 [INFO] start_investigation    Investigation started: d2cf7a0d-...
19:51:17 [INFO] get_investigation_status  Investigation status: RUNNING
19:52:17 [INFO] get_investigation_status  Investigation status: RUNNING
19:53:18 [INFO] get_investigation_status  Investigation status: RUNNING
19:54:18 [INFO] get_investigation_status  Investigation status: RUNNING
19:55:19 [INFO] get_investigation_status  Investigation status: COMPLETED
19:55:23 [INFO] send_slack_notification   Slack notification sent
```

`19:50:16` に CreateInvestigation を呼び出し、1 分ごとに `context.wait()` でサスペンド → `GetInvestigation` を繰り返して、`19:55:19`（約 5 分後）に COMPLETED を確認。その後 Amazon Translate で日本語化・URL 無効化を行い、`19:55:23` に Slack 通知が完了しました。COMPLETED 検知から Slack 送信まで約 3.7 秒は Translate API の呼び出し時間です。

`context.wait()` でサスペンド中はコンピューティングリソースが消費されないため、4 回のポーリング待機（合計約 4 分）は実質コストゼロです。

### 実際の Slack 通知内容

実際に届いた通知の内容は以下のとおりです。Amazon Translate による日本語訳と URL 無効化が適用されています。

:::details 通知内容を展開する

**Finding Type**: Backdoor:EC2/C&CActivity.B!DNS / **Account**: `<ACCOUNT_ID>` / **RiskLevel**: Critical / **Confidence**: High

**リスク評価**

> 単一の EC2 インスタンス (`<INSTANCE_ID>`) は、2 つのクリティカルアタックシーケンスの相関関係、C&C DNS、クリプトマイニング、DGA アクティビティを含む 9/12 の調査結果の中心となっています。これらはすべて異常で、事前のベースラインのない一日のバーストに集中しており、活発な侵害が行われています。

**概要**

> アカウント `<ACCOUNT_ID>` は AWS アカウント `<MANAGEMENT_ACCOUNT_ID>` によって管理されている GuardDuty メンバーアカウントで、アクティブなディテクター (`<DETECTOR_ID>`) を備えています。この調査は `Backdoor:EC2/C&CActivity.B!DNS` 検出がきっかけでした — DNS ベースの検出により、EC2 インスタンスがコマンドアンドコントロールインフラストラクチャと一致するドメイン（具体的には「guarddutyc2activityb[.]com」）を解決していることがわかります。2026-05-27 から 2026-06-23 までの合計 12 件の調査結果の中で、アカウントではほぼ完全に単一のホスト（EC2 インスタンス `<INSTANCE_ID>`）に集中した、狭く重大度の高い EC2 脅威アクティビティの急増が見られました（12 件のうち 9 件、75%）。重大度プロファイルは圧倒的に脅威アクターの行動階層で、9 件は High（8.0）、2 件は Critical（9.0）で、Low は 1 件のみです。60 日間の分析期間では、観測された 6 種類の検出タイプはすべて異常と分類され、ベースラインノイズが繰り返し発生することはありません。時系列パターンは目を見張るものがあります: 2026-05-27 に 1 件の調査結果が更新された後、27 日間の沈黙、そして 2026-06-22/23 に 11 件の更新が集中しました。C&C DNS、クリプトマイニング（`CryptoCurrency:EC2/BitcoinTool.B`）、DGA スタイルの DNS（`Trojan:EC2/DGADomainRequest.B`）、および 2 つのクリティカル `AttackSequence:EC2/CompromisedInstanceGroup` の相関結果がすべて同じホストで同日に発生しており、アクティブな単一ホストの EC2 侵害と一致しています。基本的な検出テレメトリ（CloudTrail、VPC フローログ、DNS ログ、EBS マルウェア対策）が完全に有効になっており、DNS ベースの信号に信頼性が与えられています。ただし、Runtime Monitoring は無効になっており、オンホストテレメトリがないためバックドアプロセス、その親、または実行パスを確認するためのプロセスの実行・ネットワークの起源・ファイルアクティビティの可視化ができません。そのため調査はネットワークとコントロールプレーンに限定されます。2026-06-22/23 のバーストでアーカイブされていない 3 件の調査結果が、アクティブなプライオリティキューとして残っています。いずれの調査結果も異常で重大度が高いため、抑制ルールは不要です。

**主な観察内容**

> - EC2 インスタンス `<INSTANCE_ID>` は、クリティカル `AttackSequence:EC2/CompromisedInstanceGroup` の相関結果を含む 12 件のうち 9 件（75%）の焦点となっています。
> - 6 つの検出タイプはすべて 60 日以内に異常値（ベースラインタイプがゼロ）に分類されており、繰り返し発生する検出ノイズではありません。
> - この時系列パターンは 27 日間の沈黙の後、2026-06-22/23 に 1 日で 11 件の更新情報が急増したことを示しています。これは新たに検出された活発な侵害が相関関係のある調査結果に急速に充実したものと一致しています。
> - 2 つのクリティカル（9.0）`AttackSequence:EC2/CompromisedInstanceGroup` の調査結果から、C&C DNS・クリプトマイニング・DGA シグナルが統一された侵害シナリオに関連付けられました。
> - トリガーとなる `Backdoor:EC2/C&CActivity.B!DNS` は有効な DNS ログによってサポートされるため、根拠のある検出シグナルとなっています。

**推奨事項**

> - [緊急] クリティカルな AttackSequence の相関関係に関する詳細な調査を開始する
> - [緊急] クリプトマイニングツールの検出（BitcoinTool.B）に関する詳細な調査を開始する
> - [緊急] DGA の DNS アクティビティ（Trojan DGADomainRequest.B）に関する詳細な調査を開始する
> - [短期] Runtime Monitoring を有効にして EC2 インスタンスのホストレベルの可視性を実現
> - [短期] S3 バケットと IAM アクセスキーを対象とする S3 Protection を有効にする

:::

Investigation のレスポンスはリスク評価・概要・観察内容・推奨事項まで英語で返ってきますが、Amazon Translate を通すことで日本語チームがそのまま読める形で届きます。推奨事項には優先度（緊急 / 短期）が付いているので、対応の順序付けにもそのまま活用できそうです。

## まとめ

今回は新しく登場した GuardDuty Investigation の自動通知を実装してみました。

Investigation 機能自体はまだプレビューで対応している Finding の種類も限られていますが、GA に向けて対応範囲が広がっていくと思うので、今のうちに通知基盤を作っておくと後々スムーズに移行できそうです。

また DevOps Agent を使うことで、GuardDuty の Finding の原因について調査することも可能ですが、今回触った GuardDuty Investigation との違いは別の機会に見ていこうと思います。

https://zenn.dev/cscloud_blog/articles/devops-agent-guardduty-integration

この記事がどなたかの役に立つと嬉しいです。
