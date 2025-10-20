---
title: "AWS の IdP 障害に備えて緊急時アクセス (Break-Glass Access) の手順を用意しよう"
emoji: "🚨"
type: "tech"
topics: ["aws", "iamidentitycenter", "organizations"]
published: true
published_at: 2025-10-21 07:00
---

こんにちは、CSC の平木です！

昨日（2025/10/20）16 時頃 (JST) 、us-east-1 の複数のサービスのエラー率が上昇する大規模障害が発生しました。

https://health.aws.amazon.com/health/status#multipleservices-us-east-1_1760948801

影響を受けたサービス一覧には AWS IAM Identity Center も含まれ、障害の対応に巻き込まれ AWS マネジメントコンソールにログインができなくなったご担当者様方には心中お察しいたします。

今回のような IdP の障害や IdP に対する侵害など、例外的な状況において緊急のアクセスをする手段を用いる必要があります。

今回は IAM Identity Center が障害を受けた場合を想定したケースをまとめてみます。

## IAM Identity Center はリージョナルサービス

AWS IAM Identity Center は、単一障害点を防ぐために Amazon S3 や Amazon EC2 などの高可用性で耐久性のある AWS サービスを使用しており高可用性を実現しています。

しかし、IAM Identity Center は、サービスを有効にしたリージョンからアクセスを行うため、有効にしたリージョンの API 操作に問題が発生してしまうと今回のようにログインできないケースが発生します。

https://docs.aws.amazon.com/singlesignon/latest/userguide/resiliency-regional-behavior.html

まれではありますが、決してないことではありません。

## Break-Glass Access (緊急時アクセス) とは？

Break-Glass Access とは、何か調べてみると以下のように説明されていました。

> ブレイクグラスアクセスとは、重大な緊急事態や例外的なケースで、アクセスが不十分なユーザーに通常のアクセス制御を回避するための昇格されたアクセス権が付与される場合に使用される手順を指します。その後、ユーザーは、通常の日常業務では実行しない緊急タスクを実行する目的で、通常はアクセスが許可されていないアカウントまたはターゲットに即座にアクセスできます。 (翻訳済み)  
> 引用： [What is Break-Glass Access? | SSH](https://www.ssh.com/academy/secrets-management/what-is-break-glass-access)

由来を調べてみると、火災報知機を引き出すためにガラスを割ることを指しているようです。

## Break-Glass Access を AWS でどうやって実装すべきか

実装方法については正直様々な方法が検討できるかと思います。

例えば
- ビジネスクリティカルなアカウント毎に緊急用の IAM ユーザーを作成しておく
- サードパーティ IdP を通常時は IAM Identity Center につなげ、緊急時には緊急用アカウントと直接接続し、スイッチロールする
- 緊急用アカウントに IAM ユーザーを作成しスイッチロールでワークロードアカウントに入る

などなど様々考えられると思います。

今回は、外部 IdP が使える場合とそうでない場合に分けてみていきます。

## 外部 IdP を使用する場合

### 事前に緊急アクセスアカウントを Organizations 内で発行する

最初のステップは Organizations 内に緊急アクセスアカウントを用意します。

![](/images/keisuke-poc2025-10-21-01-51-37.png)

平常時では緊急アクセスアカウントへのアクセスができることは望ましくないため、このアカウントへのアクセスには厳重に管理する必要があります。

例えば、コンソールログインがあった場合に発報する仕組みなどがあるとより気付けやすいかと思います。

### 緊急アクセス用リソースのプロビジョニング

追加する要素としては以下 3 点です。

- 3rd Party IdP に通常のワークロードで使用するグループとは別に緊急アクセス用のグループ（平常時はメンバーなし）を作成する
- 緊急アクセスアカウントと 3rd Party IdP とフェデレーションで接続する緊急オペレーションロールを作成する
- 緊急オペレーションからのアクセスを委任する緊急アクセスロールを各ワークロードアカウントに作成する

![](/images/keisuke-poc2025-10-21-02-12-59.png)

3rd Party IdP の緊急アクセスグループにメンバーを平常時に割り当てないことで平常時には誰も緊急アクセスアカウントにはログインできない状態を実現できます。

### 緊急時にメンバーの割り当て

緊急時に今までメンバーを割り当てていなかった緊急アクセスグループにメンバーを割り当てることで各ワークロードへ緊急用のロールを活用しアクセスします。

![](/images/keisuke-poc2025-10-21-02-22-51.png)

詳細は以下をご参照ください。

https://docs.aws.amazon.com/singlesignon/latest/userguide/emergency-access-implementation.html

## 外部 IdP を使用しない場合

### 事前に緊急アクセスアカウントを Organizations 内で発行する

最初のステップは外部 IdP の有無関係なく、Organizations 内に緊急アクセスアカウントを用意します。

![](/images/keisuke-poc2025-10-21-01-52-20.png)

外部 IdP ありの場合と同様で、このアカウントは厳重に管理する必要があります。

### 緊急アクセス用リソースのプロビジョニング

外部 IdP ではグループを設けましたが、IAM Identity Center を IdP とする場合はそれができないため、緊急アクセスアカウントにて IAM ユーザーを作成します。

![](/images/keisuke-poc2025-10-21-02-46-51.png)

1 人のみ作成してしまうと何かの設定ミスなどで利用できない場合にロックダウンしてしまうため、少なくとも 2 人のユーザーを確保することが推奨のようです。

各ユーザーから各ワークロードアカウントで作成した緊急アクセスロールへの委任を行うことで緊急アクセスの準備が整います。

https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/design-principles-for-your-multi-account-strategy.html#break-glass-access

### 緊急時に IAM ユーザーを活用

実際に緊急事態が発生した場合には、緊急オペレーションユーザーにてアクセスし各ワークロードへアクセスします。

緊急ユーザーは使いまわしせず、1 人に対してのみ緊急アクセスの権限を付与したり、個別の専用ユーザーを使用することで誰がどんな操作をしたのかを明確に記録できます。

ただし、管理が煩雑になるため可能な限り少ないユーザーを持つことが望ましいです。

![](/images/keisuke-poc2025-10-21-02-57-02.png)

## どんなロールを割り当てるべきか

各権限の割り当てについて、読み取り専用 (RO) とオペレーション (Ops) の 2 つの異なるロールから始めることを推奨されています。

そのためむやみに管理者権限を付与せず、緊急時に必要な権限のみ（例えばバックアップを取得する権限や EC2 の停止起動の権限など）与えることが望ましいです。

![](/images/keisuke-poc2025-10-21-02-33-14.png)
*AWS 公式ドキュメント How to design emergency role, account, and group mapping より*

https://docs.aws.amazon.com/singlesignon/latest/userguide/emergency-access-planning.html

https://docs.aws.amazon.com/singlesignon/latest/userguide/emergency-access-mapping-design.html

## Break-Glass Access の実装におけるポイント

緊急アクセスを実装するにあたって以下が重要なポイントになります。

- 関連リソースを削除させないようにする
  - 緊急アクセス用の IAM ロールや IAM ユーザーを削除されてしまうと経路がなくなってしまうため SCP などで適切に制限をかける必要があります
- 緊急アクセスユーザーの保護
  - 緊急アクセスできるユーザーは例外的な権限を持つことになるため、むやみにアクセスされないよう、ハードウェア MFA などの適用が推奨されています
- 緊急アクセスユーザーの利用に承認プロセスを挟む
  - 誰が何を目的として緊急アクセスするのかを管理者やチームメンバーが確実に判断できるようにすることで、誰が操作しているのかということが明確にできます
- 証跡をとるロジックを実装する
  - 緊急アクセスという例外的な状況ほど明確に証跡をとる必要があります。ログイン履歴や操作の API などを取得できるよう、 CloudTrail や EventBridge による通知などを実装しましょう

## 懸念事項

### IAM ユーザーは障害の影響を受けないの？

IAM ユーザーのコンソールログインに変えたところでグローバルサービスなのであれば、今回のような障害の影響を受けるのではないか？と思われるかと思います。

バージニア北部のエンドポイントからコンソールログインしてしまった場合は影響を受ける可能性がありますが、コンソールログインにおいてはリージョンサインインエンドポイントを使用してログインすることが可能であるため、ログインのフェーズにおいては回避が可能になります。

https://docs.aws.amazon.com/IAM/latest/UserGuide/disaster-recovery-resiliency.html

## 参考リンク

- [SEC03-BP03 Establish emergency access process - Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/sec_permissions_emergency_process.html)
- [How to plan your access model - AWS IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/emergency-access-planning.html)
- [SEC10-BP05 アクセスを事前プロビジョニングする - AWS Well-Architected フレームワーク](https://docs.aws.amazon.com/ja_jp/wellarchitected/latest/framework/sec_incident_response_pre_provision_access.html)
- [Design principles for your multi-account strategy - Organizing Your AWS Environment Using Multiple Accounts](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/design-principles-for-your-multi-account-strategy.html#break-glass-access)

## おわりに

Break-Glass Access の整備は、AWS 環境のセキュリティと可用性を確保するための重要な要素です。予期せぬ事態に備え、適切な設計と運用を行うことで、ビジネスへの影響を最小限に抑えることができますのでぜひ次の障害に備えて実装を検討してみていただければと思います。

この記事がどなたかの役に立つと嬉しいです。
