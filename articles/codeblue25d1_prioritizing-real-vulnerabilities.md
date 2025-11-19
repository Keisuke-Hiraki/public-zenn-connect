---
title: "[レポート] 本当の脆弱性に注目せよ ― セキュリティで本当に重要なものを優先する CODE BLUE 2025"
emoji: "🌐"
type: "idea"
topics: ["codeblue","security"]
published: true
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

今回は、日本発の世界トップクラスの専門家による最先端の技術研究が発表される国際的なサイバーセキュリティカンファレンス、CODE BLUE に参加してきたため参加レポートを執筆します。

https://codeblue.jp/

## 「“本当の”脆弱性に注目せよ ― セキュリティで本当に重要なものを優先する 」の概要

- Speakers: S2W INC. ヤン・ジョンヒョン氏
- Category: OpenTalks
- Location: Track 2(HALL A)

膨大な脆弱性の中から、実際にシステムや企業に影響を与える「本当の脆弱性」を見極めるための、S2W Threat Research & Intelligence Center（Talon）が開発した体系的な評価フレームワークを紹介します。
本講演では、社内プロジェクト「Vulnerability Structuring（脆弱性の構造化）」の開発プロセスと成果、およびこのフレームワークが実際のサービスに適用された事例を解説します。

https://codeblue.jp/program/time-table/day1-t2-opentalks-07/

## セッションレポート

本セッションは、適切な脆弱性の対応優先度の決定方法について TALON SCORE フレームワークと紐づけて解説する内容でした。

![](/images/codeblue25d1_prioritizing-real-vulnerabilities_2025-11-19-02-22-57.png)
*ヤン・ジョンヒョン氏の講演スライドより*

すべての脆弱性が同等ではない理由について、 2 つの例題から考えていきます。

まず 1 つ目の質問では、2 つの脆弱性のうちどちらが危険かについてです。

言うまでもなく、上の脆弱性のほうが下の脆弱性よりも CVSS ベーススコアが下側よりも高いため、上のほうが危険だと分かります。

![](/images/codeblue25d1_prioritizing-real-vulnerabilities_2025-11-19-09-37-17.png)
*ヤン・ジョンヒョン氏の講演スライドより*

続いて 2 つ目の質問では、どっちを優先的にパッチ適用すべきかという問いです。

多くの場合、 CVSS スコアの高い上が優先されるべきと考えがちです。  
しかし 登壇者の答えは下の CVE-2025-4123 が優先すべきと回答しました。

なぜ CVSS スコアが低い下の脆弱性が優先度が高いと考えられるかを紐解いていきます。

![](/images/codeblue25d1_prioritizing-real-vulnerabilities_2025-11-19-09-38-55.png)
*ヤン・ジョンヒョン氏の講演スライドより*

評価を行う上で、TALON スコアと呼ばれる実践型スコアリングシステムを活用して優先順位を決定しているとのことです。

TALON スコアでは、CVSS や EPSS などいくつかの要素の組み合わせにより優先順位の決定します。

![](/images/codeblue25d1_prioritizing-real-vulnerabilities_2025-11-19-09-43-03.png)
*ヤン・ジョンヒョン氏の講演スライドより*

先ほどの CVE を見てみると EPSS が高いことが分かります。

![](/images/codeblue25d1_prioritizing-real-vulnerabilities_2025-11-19-09-43-55.png)
*ヤン・ジョンヒョン氏の講演スライドより*

TALON では 5 つの要素を優先順位を決定するためのフレームワークとして採用しています。

- CVSS/Attack Vector
  - CVSS が高いほど危険性が増し、攻撃が容易となる
- 公開日
  - 古い脆弱性はパッチが公開されている可能性が高い
- PoC/Exploit
  - 脆弱性がどの程度研究されているかも重要な指標となる
- ITW
  - 実際の環境で悪用されているかどうか
- トレンド
  - どれだけ流行している脆弱性かどうか

スコアリングの方法としては以下の考え方になります。

- CVSS: スコアが高いほど、TALON スコアも高く加算
- Attack Vector: より遠隔であるほど、TALON スコアも高く加算
- PoC/Exploit ファイル: 公開状況に応じて TALON スコアを付与
- 情報源の信頼性: 信用のある機関や団体が公開しているものかどうかで TALON スコアを重み付けを行う
- ITW: 実際の環境で悪用された場合は、TALON スコアも高く加算

SNS や報道、ディープダークウェブで多く言及されるほど高くなるなど、単なる情報の羅列のみではなく、総合的な観点から算定することが重要とのことです。

ここからはケーススタディとして実例を紹介されました。

まず `Log4Shell` の例ですが、現在は公開から 4 年経過していることため、TSS（TALON スコア）は `3.48` と算出されたようです。

![](/images/codeblue25d1_prioritizing-real-vulnerabilities_2025-11-19-09-53-08.png)
*ヤン・ジョンヒョン氏の講演スライドより*

続いては `Citrix Bleeds` の例です。こちらは公開から約 2 年と直近のものであるため TSS も高く `3.91` と算出されています。

![](/images/codeblue25d1_prioritizing-real-vulnerabilities_2025-11-19-09-54-39.png)
*ヤン・ジョンヒョン氏の講演スライドより*

続いて `Chrome RCE` の例では、EPSS は低いものの TSS は高く算出されています。  
これは、 EPSS が低くても重大な脆弱性で早急に対応すべきという考えから、 TSS が高くなったとのことです。

![](/images/codeblue25d1_prioritizing-real-vulnerabilities_2025-11-19-09-55-39.png)
*ヤン・ジョンヒョン氏の講演スライドより*

最後にまとめとして、
全ての脆弱性に対応することは現実的ではないため、重点的に実施するために脆弱性を選定する必要がある、と話されていました。

![](/images/codeblue25d1_prioritizing-real-vulnerabilities_2025-11-19-10-03-58.png)
*ヤン・ジョンヒョン氏の講演スライドより*

## まとめ

こちらのセッションでは、
脆弱性を適切にトリアージしていくことの重要性
について詳しく知ることができました。

この記事がどなたかの役に立つと嬉しいです。