---
title: "Security Hub CSPMで検知した内容を、AI要約し、Jiraに起票し、Slack通知するワークフローをn8nで自動化してみた"
emoji: "🤖"
type: "tech"
topics: ["aws", "securityhub", "n8n"]
published: true
publication_name: cscloud_blog
published_at: 2025-09-11 07:00
---
こんにちは、CSC の平木です！

みなさんは普段、Security Hub のアラート管理はどのようにしていますか？

Security Hub の検知結果の一覧のみ活用したり、スプレッドシートを活用したり、Jira や Backlog などのプロジェクト管理ツールを使用して管理しているユーザーもいると思います。

今回は、AI エージェントとのコラボレーションで注目を浴びている n8n を活用し、
Security Hub のアラートの通知をトリガーとして、AI の要約から Jira への起票、Slack の通知の自動化を試してみました。

## 構成

今回は下記のような構成で作ってみました。

![keisuke-poc2025-09-10-22-37-50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/09706366-97e4-4551-ae4f-db812f21e50a.png)

1. EventBridge で Security Hub CSPM の中で Critical と High のイベントを検知します。
2. EventBridge で検知をしたら Lambda へイベントを渡し、n8n の webhook を呼び出します
3. Lambda からのイベントを受け取った n8n の webhook によりワークフローが起動します
4. まず検知したイベント JSON の内容を AI Agent のノードから Gemini を呼び出し、JSON の内容を要約します
5. （図中では省略）さらに要約した内容から具体的な対処法や懸念点などを整理する AI Agent ノードを呼び出します
6. それぞれ Gemini で整理した内容を Jira に起票します
7. Jira 起票後に Slack へ通知します

筆者は n8n のセルフホスト版で今回は検証しましたが、当然 SaaS 版でも実装可能です。

## 設定値

ここから具体的な中身を見ていきます。

一部手順などは割愛しますが参考となるブログを引用させていただきます。

### 必要なもの

- AWS 環境
- n8n 環境（SaaS 版、セルフホスト版は問いません）
- Jira アカウント API トークン
- Slack bot OAuth トークン

:::message alert
Slack との連携の際に n8n の HTTPS 化が必須のため、
n8n のセルフホスト版を利用する場合は証明書の設定などの事前準備が必要になりますのでお気を付けください。
:::

### EventBridge

EventBridge には下記イベントパターンを指定し、後続の Lambda をターゲットとして設定しています。

```json
{
  "source": ["aws.securityhub"],
  "detail-type": ["Security Hub Findings - Imported"],
  "detail": {
    "findings": {
      "Compliance": {
        "Status": ["FAILED"]
      },
      "RecordState": ["ACTIVE"],
      "Severity": {
        "Label": ["HIGH", "CRITICAL"]
      },
      "Workflow": {
        "Status": ["NEW"]
      }
    }
  }
}
```

### Lambda

Lambda は webhook URL 宛にイベントを POST リクエストするよう設定します。

Lambda の環境変数には、`N8N_WEBHOOK_URL`を設定し、
後続の n8n の webhook ノードに記載されている URL を値に設定してください。

:::details こちらをクリックして展開するとコードが見えます

```python
import json
import os
import urllib.request
import logging

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    EventBridge から受け取った Security Hub のイベントを n8n の Webhook に送信します。
    """
    # 環境変数から n8n の Webhook URL を取得
    # Lambda の環境変数に「N8N_WEBHOOK_URL」というキーで設定してください
    webhook_url = os.environ.get('N8N_WEBHOOK_URL')

    if not webhook_url:
        logger.error("環境変数 'N8N_WEBHOOK_URL' が設定されていません。")
        raise ValueError("n8n Webhook URL が設定されていません。")

    logger.info(f"受信したイベント: {json.dumps(event)}")

    # Security Hub の検知結果（イベントの'detail'部分）を取得
    # イベントに'detail'キーが存在しない場合は空の辞書を使用
    finding_detail = event.get('detail', {})
    
    # n8n に送信するデータ（ペイロード）を準備
    try:
        # 辞書を JSON 形式のバイト文字列に変換
        payload = json.dumps(finding_detail).encode('utf-8')
    except TypeError as e:
        logger.error(f"イベントデータの JSON シリアライズに失敗しました: {e}")
        raise

    # HTTP リクエストの作成
    headers = {
        'Content-Type': 'application/json'
    }
    req = urllib.request.Request(webhook_url, data=payload, headers=headers, method='POST')

    # n8n へリクエストを送信
    try:
        with urllib.request.urlopen(req) as response:
            logger.info(f"n8n への送信に成功しました。ステータスコード: {response.status}")
            response_body = response.read().decode('utf-8')
            logger.info(f"n8n からのレスポンス: {response_body}")

    except urllib.error.HTTPError as e:
        logger.error(f"n8n への送信中に HTTP エラーが発生しました。ステータスコード: {e.code}")
        logger.error(f"エラーレスポンス: {e.read().decode('utf-8')}")
        raise
    except urllib.error.URLError as e:
        logger.error(f"n8n への送信中に URL エラーが発生しました: {e.reason}")
        raise
        
    return {
        'statusCode': 200,
        'body': json.dumps('イベントを n8n に正常に転送しました。')
    }
```

:::

### n8n

続いて n8n のワークフローを作成していきます。

ワークフロー全体はこのように設定しています。

![keisuke-poc2025-09-10-23-00-48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/df65bde8-9771-4f10-af20-826f01a4309b.png)

#### webhook

まずは Lambda からのイベントの受け口かつワークフローのトリガーとなる webhook を設定します。

受け口になるため、HTTP メソッドには`POST`を指定します。

Production URL に記載の URL を、Lambda の環境変数へ設定してください。

![keisuke-poc2025-09-10-22-59-28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/196bfb1c-9a85-44f7-af43-38fe77141bd1.png)

#### 要約 AI Agent

検知内容を要約する AI ノードの設定をします。

Source for Prompt を`Define below`にすると Prompt を入力できるようになるため切り替え、Prompt には以下のように記載しました。

```
# Instructions 
You are an AWS security expert.
Please analyze the AWS Security Hub detection results (in JSON format) provided and summarize the main points in a concise 2~3 line sentence.
**IMPORTANT:** Your entire response MUST be in Japanese.

# Security Hub Detection Results 
\```json  <--適用時にはバックスラッシュを削除してください
{{ JSON.stringify($json.body.findings[0]) }} 
\``` <--適用時にはバックスラッシュを削除してください
```

下記は日本語訳版です。

```
# 指示
あなたは AWS セキュリティの専門家です。
提供された AWS Security Hub の検知結果（JSON 形式）を分析し、2~3 行の簡潔な文章で要点をまとめてください。
**重要:** 回答はすべて日本語でお願いします。

# Security Hub Detection Results
\``json
{{ JSON.stringify($json.body.findings[0]) }}. 
\```
```

Model は今回 Gemini を選択しましたが好みのモデルを選択してください。

![keisuke-poc2025-09-10-23-08-23.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/d3ae29e5-6f8e-4cdd-9b66-e4b50bcabf65.png)

#### 調査 AI Agent

続いて要約した内容から対処法や懸念点についてアドバイスする AI ノードを設定します。

基本は前述の AI ノードと同じです。

Prompt には以下を指定しました。

```
# Instructions 
You are an experienced cloud security consultant.
Based on the security detection summarized below, please propose risks and specific remedies.
Please describe your recommendations in polite language and avoid jargon so that even junior infrastructure staff can understand them.

# Security Detection Summary 
{{ JSON.stringify($json.output) }}

# Your task
1. **Risk Description:** Describe in one or two sentences the specific business risk (information leakage, service outage, unauthorized use, etc.) that could occur if this problem is left unaddressed.
2.**Specific steps to address the issue:**
    - Describe step-by-step, bulleted procedures to resolve this issue.
    - Please be specific, e.g., names of items to click on, etc., based on operations on the AWS Management Console. 
3. **Concerns:** 
If you have concerns about implementing specific improvement measures, please describe them. If there are no concerns, leave them out.
4.**Preventive measures:**
    - Please propose one or two permanent measures to prevent similar problems from occurring in the future.

---.
#### **Points of this prompt:**
**Persona Setup:** Specify the persona (role) of "experienced cloud security consultant" and ask for credibility and politeness.
**Designate target audience:** Control the quality of your output by adding "so that even young infrastructure professionals can understand it" to encourage plain language.
** **Decomposition of tasks:** Clearly separating the tasks into "risks," "procedures for dealing with them," and "measures to prevent recurrence" will help generate structured and comprehensive responses.
**Input data:** Using the summary `{{ JSON.stringify($json.output) }}` generated by the previous AI as input, the AI can start thinking with less noisy information and can expect highly accurate answers.
* **MUST** Only include content relevant to the given task, be sure to omit unnecessary comments, greetings, and sentences from the description, and reduce the amount of text as much as possible to make the text easy to read.
* **MUST** The initial greeting, e.g., "I am pleased to report ~" or "I propose ~" should always be deleted and the main topic should begin at the beginning.
* **IMPORTANT:** Your entire response MUST be in Japanese.
```

下記は日本語訳版です。

```
# 指示 
あなたは経験豊富なクラウドセキュリティコンサルタントです。
以下にまとめたセキュリティ検出結果に基づき、リスクと具体的な改善策を提案してください。
専門用語を避け、若手のインフラ担当者でも理解できるよう、丁寧な言葉で提言を記述してください。

# セキュリティ検出の概要 
{{ JSON.stringify($json.output) }}

# あなたのタスク
1. **リスクの説明:** この問題を放置した場合に発生する可能性のある具体的なビジネスリスク（情報漏えい、サービ ス停止、不正使用など）を 1～2 文で記述してください。
2.**問題に対処するための具体的な手順：***。
    - この問題を解決するための手順を段階的に箇条書きで記述してください。
    - AWS Management Console での操作に基づき、クリックする項目名など具体的に記述してください。3.
3. **懸念事項:** 
具体的な改善策の実施について懸念がある場合は、その内容を記載してください。懸念事項がない場合は、記入の必要はありません。
4.**予防策：***。
    - 今後同様の問題が発生しないよう、恒久的な対策を 1～2 つご提案ください。

---.
#### このプロンプトのポイント
**ペルソナ設定：** 「経験豊富なクラウドセキュリティコンサルタント」というペルソナ（役割）を指定し、信頼性と丁寧さを求める。
**ターゲット読者の指定： ** 「インフラに携わる若手でも理解できるように」を加えて、平易な表現を促すことで、アウトプットの質をコントロールする。
** タスクの分解：*** 「リスク」「対処手順」「再発防止策」に明確に分けることで、構造的かつ包括的な回答が生まれやすくなる。
**入力データ： **前の AI が生成したサマリー `{{ JSON.stringify($json.output) }}` を入力として使うことで、AI はノイズの少ない情報から思考を始めることができ、精度の高い回答が期待できる。
* **MUST** 与えられたタスクに関連する内容のみを記載し、説明文から不要なコメントや挨拶、文章は必ず省き、文章量をできるだけ減らして読みやすくする。
* 最初の挨拶、例えば「～をご報告いたします」「～を提案いたします」などは必ず削除し、本題は冒頭から始めること。
* 重要：** 回答はすべて日本語で行うこと。
```

![keisuke-poc2025-09-10-23-13-25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/2f674a5a-1d86-400d-a822-e460c31d506c.png)

#### Jira

続いては要約した内容を起票するために Jira のノードを追加します。

Credential to connect with でまずは認証を行います。

ここでは Jira の API トークンが必要になるので下記ブログを参考に取得してください。

https://takata.website/jira-api-token/

取得できたら Jira で使用しているメールアドレスと Jira のドメインと合わせて設定します。

![keisuke-poc2025-09-10-23-16-41.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/1b8f85da-9c0f-4f1d-a98f-a4688b0d7192.png)

認証が Success になったらその他の設定もしていきます。

| 設定項目 | 設定内容 | 例 |
| - | - | - |
| Resource | Issue |  |
| Operation | Create |  |
| Project | 起票するプロジェクト名を選択 |  |
| Issue Type | 起票するタイプ | タスク |
| Summary | 起票時のタイトル | 下記に記載します |
| Assignee | タスクにアサインする人 | 任意のメンバー |
| Description | 説明欄に記載する内容 | 下記に記載します |
| Priority | タスクの優先度 | 下記に記載します |

表中のものについて補足します。

Summary には以下とすると可変的に起票可能です。

```
[ {{ $('Webhook').item.json.body.findings[0].AwsAccountId }} ] {{ $('Webhook').item.json.body.findings[0].Title }} 検知通知
```

Description には下記を設定しました。

```
検知タイトル：  {{ $('Webhook').item.json.body.findings[0].Title }}
重要度： {{ $('Webhook').item.json.body.findings[0].Severity.Label }}
対象アカウント： {{ $('Webhook').item.json.body.findings[0].AwsAccountId }}
最終検知日時： {{ $('Webhook').item.json.body.findings[0].UpdatedAt }}

===要約===
{{ $('要約 AI Agent').item.json.output }}
==========

===詳細===
{{ $json.output }}
=========
```

Priority には以下のようにすると Critical の場合には Higher,High の場合には High,それ以下では Medium とできます。

```
{{ $('Webhook').item.json.body.findings[0].Severity.Label === "CRITICAL" ? "1" : ($('Webhook').item.json.body.findings[0].Severity.Label === "HIGH" ? "2" : "3") }}
```

![keisuke-poc2025-09-10-23-27-12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/fb29b504-c901-42e6-b80b-445b437a335a.png)

#### Slack

最後、Slack 通知の設定をします。

事前に Slack bot の設定などが必要なためアクセストークンの取得を以下ブログを参考に進めてください。

https://note.basicinc.jp/n/n41663113d997

認証が成功したら具体的な設定をします。

| 設定項目 | 設定内容 | 例 |
| - | - | - |
| Resource | Message |  |
| Operation | Send |  |
| Send Message To | Channel |  |
| Channel | 通知先の Slack チャネル |  |
| Message Type | Simple Text Message |  |
| Message Text | 通知内容 | 下記に記載します |

通知内容は以下のように設定しました。

```
:warning: Security Hub << *{{ $('Webhook').item.json.body.findings[0].Severity.Label }}* >>アラート :warning:

AWS アカウント ID： `{{ $('Webhook').item.json.body.findings[0].AwsAccountId }}` で
{{ $('Webhook').item.json.body.findings[0].Title }}
を検知しました。

Jira チケットを確認してください。
{{ $json.self }}
```

![keisuke-poc2025-09-10-23-32-08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/4a563eec-11db-454a-8956-2b27e8154a45.png)

こちらで完成です。

## やってみた

実際に稼働させてみました。

今回は任意のセキュリティグループを作成しインバウンドトラフィックにすべてのトラフィックを 0.0.0.0/0 で設定し、[[EC2.19] セキュリティグループは、リスクの高いポートへの無制限アクセスを許可してはいけません](https://docs.aws.amazon.com/ja_jp/securityhub/latest/userguide/ec2-controls.html#ec2-19) という Critical のアラートを発報させてみます。

リソース作成から数分後、ワークフローが開始し成功が確認できました。

![keisuke-poc2025-09-10-23-37-07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/4308e25a-d8a4-4e9a-bc5c-b1283fea2638.png)

まず Jira を確認すると以下のように起票されていました。

![keisuke-poc2025-09-10-23-38-48.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/d9b858d3-8bd1-48f4-99e0-f9dc7c2f513d.png)

:::details こちらをクリックして展開すると説明内容が見えます

```
検知タイトル：  EC2.19 Security groups should not allow unrestricted access to ports with high risk
重要度： CRITICAL
対象アカウント： 111122223333
最終検知日時： 2025-09-10T14:30:09.459Z

===要約===
AWS Security Hub の EC2.19 コントロールにより、EC2 セキュリティグループが高リスクポートへのインターネット（0.0.0.0/0）からの無制限なインバウンドアクセスを許可しており、クリティカルな問題として検出されました。
==========

===詳細===
リスクの説明
インターネットから誰でもアクセスできる状態になっているため、第三者による不正侵入や情報漏洩、サービス停止、さらにはシステムの悪用といった重大なセキュリティ事故につながる可能性があります。

課題を解決するための具体的な手順
この問題に対処するためには、以下の手順でセキュリティグループの設定を見直していただきます。

1.  *AWS マネジメントコンソールへのログイン:*
AWS マネジメントコンソールにログインします。
2.  *EC2 サービスへの移動:*
画面上部の検索バーで「EC2」と入力し、表示される「EC2」を選択します。
3.  *セキュリティグループの選択:*
左側のメニューから「ネットワークとセキュリティ」の下にある「セキュリティグループ」をクリックします。
4.  *問題のセキュリティグループの特定:*
問題が検出されたセキュリティグループを見つけて選択します。どのセキュリティグループが該当するかは、Security Hub の検出結果から確認できます。
5.  *インバウンドルールの確認:*
下部に表示されるタブの中から「インバウンドルール」を選択します。インターネット（`0.0.0.0/0`）からのアクセスを許可しているルール（特に「タイプ」が SSH、RDP、データベース関連など、一般的に高リスクとされるポート）を確認します。
6.  *インバウンドルールの編集:*
「インバウンドルールを編集」ボタンをクリックします。
7.  *ルールの変更または削除:*

  *アクセス元を限定する場合:* 問題のルールについて、「ソース」の項目を、例えば特定の IP アドレス（オフィスや VPN の IP アドレスなど）に限定します。複数の IP アドレスが必要な場合は、カンマ区切りで追加するか、適切な IP アドレス範囲（CIDR ブロック）を指定します。

  *アクセスが不要な場合:* もしそのポートへの外部からのアクセスが不要であれば、ルールの右端にある「削除」アイコン（X 印）をクリックしてルールを削除します。
8.  *変更の保存:*
    変更を適用するために「ルールを保存」ボタンをクリックします。

懸念事項
ルールを変更する前に、該当するポートがどのような目的でインターネットに公開されているか、また、そのポートへのアクセスを必要とするユーザーやシステムが他にないかを、関係者にご確認いただくことが非常に重要です。誤って必要なアクセスを遮断してしまうと、サービスが一時的に利用できなくなる可能性があります。

再発防止策
1.  *最小権限の原則の徹底:*
    新しいセキュリティグループを作成する際や、既存のセキュリティグループを変更する際には、必ず必要なポートとアクセス元（IP アドレス）のみを許可する「最小権限の原則」を徹底する運用ルールを設けること。また、定期的なセキュリティグループの棚卸しとレビューを行う仕組みを導入することも有効です。
2.  *管理用アクセスの制限:*
    SSH（ポート 22）や RDP（ポート 3389）のような管理用アクセスについては、直接インターネットに公開せず、踏み台サーバー（Bastion Host）や VPN 接続経由でのみアクセスを許可する設計を導入することを推奨します。これにより、攻撃にさらされる範囲を大幅に減らすことができます。
=========

```

:::

Slack を確認すると Jira のリンクとともに通知されていました。

![keisuke-poc2025-09-10-23-41-31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/045fcf2e-8cd5-4dba-bd0e-06ac5d21c5ae.png)

## さいごに

今回は、セキュリティアラートの分析からチケット起票、通知までの自動化を検証してみました。

セキュリティ運用は大変でありながら重要な業務でもあるので AI Agent を有効的に活用することで省力化し、より重要な業務に専念していくことが大事です。

今後も n8n と AI Agent をいろいろ触ってみたいと思います。

この記事がどなたかの役に立つと嬉しいです。

---

この記事は Qiita から移行しました。
