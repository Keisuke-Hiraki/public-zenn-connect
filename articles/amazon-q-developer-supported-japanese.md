---
title: "Amazon Q Developer が日本語に対応したので Security Hub CSPM で検知した内容の是正方法を相談してみた"
emoji: "🤖"
type: "tech"
topics: ["aws", "amazonqdeveloper", "securityhub"]
published: true
publication_name: cscloud_blog
published_at: 2025-08-02 07:00
---
こんにちは、CSC の平木です！

みなさんは Amazon Q Developer を使用していますか？

今までは英語でしか対話できなかったためなかなか実用では使いづらいと思っていた方もいるかと思います（コンソール搭載チャット以外は日本語でも反応はあったという噂）が、アップデートで晴れて日本語を含む多くの言語をサポートしました。

https://aws.amazon.com/jp/about-aws/whats-new/2025/07/q-developer-multi-language-support/

今回は Security Hub CSPM を活用し、検知内容を Amazon Q Developer（以下、Q Developer）に問い合わせ対象のリソースの検索と是正方法を相談してみようと思います。

:::message alert
Q Developer の使用には AWS 管理ポリシーの`AmazonQDeveloperAccess`またはその権限を含んでいるユーザーを使用する必要があります
:::

## やってみた

今回はたまたま自分の環境で `[S3.8] S3 汎用バケットはパブリックアクセスをブロックする必要があります` が検知していたので、これが失敗している原因となる S3 バケットと対処法を聞いてみます。

https://docs.aws.amazon.com/ja_jp/securityhub/latest/userguide/s3-controls.html#s3-8

まずは以下で問い合わせました。

```
[S3.8]S3 general purpose buckets should block public access が Security Hub CSPM で検知しているので、これの原因となる S3 バケットを教えてください
```

実際聞いてみたところ、まずはシステムプロンプトとして定義されているのか①言語の指定とセキュリティ関連んの問い合わせだというフラグ付けが行われ、②実際に Q Developer 側での調査が開始しました。

![keisuke-poc2025-08-02-18-03-14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/6956913e-75e7-43cc-8e1f-919d37675921.png)


そのあと実際に下記のように回答されました。

```
Security Hub CSPM で検知されている [S3.8] の原因となる S3 バケットを特定しました。

原因となる S3 バケット:

    <対象の S3 バケット名>

このバケットは、すべてのパブリックアクセスブロック設定が無効になっています：

    BlockPublicAcls: false
    IgnorePublicAcls: false
    BlockPublicPolicy: false
    RestrictPublicBuckets: false

解決方法: Security Hub finding [S3.8] を解決するには、<対象の S3 バケット名>
バケットのすべてのパブリックアクセスブロック設定を有効にする必要があります。これは S3 コンソールまたは AWS CLI/API を使用して実行できます。

なお、アカウント内の他のすべての S3 バケットは、推奨されるセキュアな設定（4 つの設定すべてが true
）で適切に構成されています。

この分析は AWS アカウントのすべてのリージョンで実行されているため、S3 バケットのパブリックアクセス設定の完全な状況を提供しています。
```

バケット名のため伏せていますが実際一致する S3 バケット名と聞いてない解決法まで教えてくれました。

![keisuke-poc2025-08-02-18-08-03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/cda8f97b-09dd-4a08-9965-a2dc2f405946.png)

念のため対象の S3 バケットを確認したところパブリックアクセスがオフになっていました。

![keisuke-poc2025-08-02-18-10-37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/205c5fdd-6e60-4314-9e71-f4fe1f05b0b2.png)

では続いて対処法をコンソールでの操作方法と AWS CLI での方法の 2 通り細かく聞いてみます。

```
検知したコントロールを是正するためにコンソールでの操作方法と AWS CLI での方法の 2 通りで詳細を教えてください
```

問い合わせると以下のように回答がありました。

```
S3.8 コントロールを是正するための詳細な操作方法を、AWS マネジメントコンソールと AWS CLI の両方でご説明します。
AWS マネジメントコンソールでの操作方法

1. S3 コンソールにアクセス

    AWS マネジメントコンソールにサインインし、S3 コンソール（https://s3.console.aws.amazon.com/s3/）を開きます。

2. 対象のバケットを選択

    バケットのリストから「<対象の S3 バケット名>」バケットを見つけ、クリックします。

3. アクセス許可の編集

    「アクセス許可」タブを選択します。
    「パブリックアクセスのブロック（バケット設定）」セクションまでスクロールし、「編集」ボタンをクリックします。

4. パブリックアクセスをブロック

    「すべてのパブリックアクセスをブロック」チェックボックスを選択します。
    「変更の保存」ボタンをクリックします。
    確認ダイアログが表示されたら、「confirm」と入力し、「確認」ボタンをクリックします。

AWS CLI での操作方法

1. AWS CLI の設定確認

    AWS CLI がインストールされ、適切に設定されていることを確認します。

2. パブリックアクセスブロック設定の適用

    以下のコマンドを実行して、バケットのパブリックアクセスをブロックします：

aws s3api put-public-access-block --bucket <対象の S3 バケット名> --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

3. 設定の確認

    以下のコマンドを実行して、設定が正しく適用されたことを確認します：

aws s3api get-public-access-block --bucket <対象の S3 バケット名>

出力で全ての設定が true
になっていることを確認します。
重要な注意点

    これらの手順を完了することで、S3.8 コントロールの是正が行われ、指定された S3 バケットのパブリックアクセスがブロックされます。
    この設定により、バケットとその中のオブジェクトへの意図しないパブリックアクセスを防ぐことができます。
    セキュリティのベストプラクティスとして、必要な場合を除き、S3 バケットへのパブリックアクセスは常にブロックすることをお勧めします。
    これらの変更を本番環境に適用する前に、テスト環境で影響を確認することも重要です。
```

![keisuke-poc2025-08-02-18-15-29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/a44d7443-9a42-4e51-b9a7-14617bac1d75.png)

コンソールでの操作方法において日本語での表記と合致した手順を出力してくれたのがかなりクオリティ高く最高だなと感じました。

## 余談

チャットタイトルを日本語にできるかチャレンジしたところ、ここは英数字と記号のみのようでした

![keisuke-poc2025-08-02-18-18-03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/a756dfcf-deed-4f6f-9039-45669bd5de78.png)

## おわりに

今回は Q Developer が日本語対応したので日本語でやり取りをしてみました。

もうトラブルシューティングこれでいいんじゃね？と思うほどのユーザー体験でかなり満足できました。

今後使い続け有用な使い方を見つけたら発信してみようと思います。

この記事がどなたかの役に立つと嬉しいです。

---

この記事は Qiita から移行しました。
