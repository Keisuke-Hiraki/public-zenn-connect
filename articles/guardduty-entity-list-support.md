---
title: "Amazon GuardDutyでドメインも脅威リストや信頼リストに入れられるEntity listが追加されていたので試してみる"
emoji: "🕵️"
type: "tech"
topics: ["aws", "guardduty"]
published: true
publication_name: cscloud_blog
published_at: 2025-08-19 07:00
---
こんにちは、CSC の平木です！

みなさん、GuardDuty を使用してセキュリティ対策していますか？

GuardDuty では検知がノイズになるのを防ぐためや確実に検知させるために
もとより信頼できる IP リスト（Trusted IP list）と脅威リスト（Threat IP list）があります。

今日 GuardDuty を覗いていたところ Entity lists - 新規と書いてある場所が追加されており、
どうやらまだドキュメントにも追加されていないようなのでどんなものなのか調べてみました。

:::message
（8/18 追記）
確認したところドキュメントも更新されていました
[Customizing threat detection with entity lists and IP address lists - Amazon GuardDuty](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_upload-lists.html)
:::

しかも、文中には Entity lists **(recommended)** となっています。

![gd_entity_list_2025-08-15-21-26-34.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/81a1d0cc-aada-48ba-9b3b-a04beded8653.png)

## Entity list とは

まずコンソール上の説明欄を見てみます。

> GuardDuty supports both entity lists and IP lists. Entity lists (recommended) can include both IP addresses and domains. GuardDuty will generate findings for entries provided in threat lists and exclude findings generated from trusted lists.

> GuardDuty は、エンティティ リストと IP リストの両方をサポートしています。エンティティ リスト (推奨) には、IP アドレスとドメインの両方を含めることができます。GuardDuty は、脅威リストで提供されたエントリの調査結果を生成し、信頼済みリス トから生成された調査結果は除外します。（Deepl 翻訳）

コンソールの説明を読む限りどうやら今まで IP リストでは当然 IP のみしか指定できなかったのに対して、エンティティリストでは IP とドメインを含めることができるようです。

しかも（推奨）と書いているので今後はおそらくこっちを使ってね、という形になるのかなと推測できます。

## Entity list で扱えるリスト形式

IP リストではいくつかテキスト形式に箇条書きで記載するだけでなく、
Open Threat Exchange (OTX)TM CSV 形式や AlienVaultTM Reputation Feed 形式などいくつかのリスト形式をサポートしていました。

Entity list で扱えるリスト形式がサポートしているリスト形式は本日時点ではドキュメントへの記載はありませんでしたが、コンソールを見ると IP リストと同じ形式をサポートしているようです。

![gd_entity_list_2025-08-15-21-37-39.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/f11cf98c-2726-46eb-a53f-6d422941f005.png)

各リスト形式についてはこちらのページで確認できます。

https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_upload-lists.html

## やってみた

記載方法もなんとなく分かったところで実際にドメインを信頼リストに入れて動作確認をしてみます。

まずはアラートを鳴らしてみます。

今回は下記ブログを参照させていただき、
`CryptoCurrency:EC2/BitcoinTool.B!DNS` を検出させるためのドメインを呼び出してみます。

https://dev.classmethod.jp/articles/guardduty-suppression-rule-request-domain-suffix/

対象ドメインへのdigコマンド実行後、しばらくすると検知が確認できました。

![gd_entity_list_2025-08-15-22-14-36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/29d1e99a-ffae-4590-be4b-2046778c3752.png)

![gd_entity_list_2025-08-15-22-16-15.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/e22b37c0-ad62-41d1-95c4-339ff5c77880.png)

![gd_entity_list_2025-08-15-22-17-01.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/7a30c948-9f00-41e7-a0f8-e5e4f5854864.png)

では続いて
- ①`pool.minergate.com`
- ②`②xmr.pool.minergate.com`
- ③`pool.supportxmr.com`

の中で③を記載したテキストファイルを S3 バケットに配置し、検証してみます。

まずは S3 バケットにドメインを記載したテキストファイルをアップロードします。

![gd_entity_list_2025-08-15-21-50-43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/598192c2-59f1-49e6-9738-4e9162c6b9c7.png)

続いて「設定 > リスト」から Entity lists のタブであることを確認し、「Add a trusted entity list」を押します

![gd_entity_list_2025-08-15-21-58-26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/7963093d-80e1-4843-9286-6d6b59590d48.png)

続いて、リスト名・リストを配置したオブジェクト URL ・形式を選択または入力し、
同意しますにチェックを入れ、「リストの追加」を押します。

![gd_entity_list_2025-08-15-21-55-47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/f02a2840-ebec-4f4c-a472-03bb245a9c4f.png)

設定できたらアクティブ化するためにアクションから「有効化」を押してアクティブになれば完了です。

![gd_entity_list_2025-08-15-21-59-36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/d536d817-5176-41ff-9f51-1741b18ca41e.png)

早速全てのドメインへ dig コマンドをたたいてみました。

![gd_entity_list_2025-08-15-23-30-50.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/f89dfb79-059b-48ba-9843-0c85a762ad93.png)

![gd_entity_list_2025-08-15-23-31-30.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/76236592-c2d3-43fd-92e9-6984e09a01ea.png)

![gd_entity_list_2025-08-15-23-32-10.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/0436eead-b629-4c33-9578-b575be392126.png)

1 個余分なものが検知していますが、信頼リストに入れた`③pool.supportxmr.com`は検知していないことが分かりました。

## 登録できるリストの数

こちらは IP リスト同様、
信頼されたエンティティリストの数は 1 個、
脅威のエンティティリストは 6 個
が上限のようです。

![gd_entity_list_2025-08-15-23-36-40.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/cc3ad637-0047-42b2-b069-2f7ce139174a.png)

## リストを更新したい場合

こちらも IP リスト同様、編集ボタンを押し、リストの更新を押すと最新の S3 オブジェクトを参照してくれます。

![gd_entity_list_2025-08-15-22-21-16.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/65fb9b2d-618f-4618-9065-069ce955c9cf.png)

![gd_entity_list_2025-08-15-22-21-49.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/886a6334-0b06-4818-bf76-c4af189e6eb5.png)

## おわりに

今回はふと追加されていたエンティティリストを見ていきました。

今までは抑制ルールを作成すれば自動アーカイブされていきましたが、
エンティティリストを活用することでより GuardDuty を効果的に使えるかと思われます。

この記事がどなたかの役に立つと嬉しいです。

---

この記事は Qiita から移行しました。
