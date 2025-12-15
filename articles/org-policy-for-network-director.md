---
title: "新しく 13 番目の Organizations ポリシーになるネットワークセキュリティディレクターポリシーが追加されました！"
emoji: "🔍"
type: "tech"
topics: ["aws", "networksecuritydirector", "organizations", "security"]
published: true
published_at: 2025-12-16 07:00
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

皆さんは AWS Shield Network Security Director をご存じですか？

AWS Shield Network Security Director は、今年の 2025/06/17 の re:Inforce で公開された現在パブリックプレビュー中の AWS Shield の機能です。  
主にアカウント全体におけるコンピューティング、ネットワーク、ネットワークセキュリティリソースの設定値を AWS ベストプラクティスと脅威インテリジェンスに照らして分析・評価する機能となります。

詳細は下記をご参照ください。

https://www.wafcharm.com/jp/blog/new-aws-feature-network-security-director-preview-announced/

今回 Organizations ポリシーとして AWS Shield Network Security Director の有効化を一元管理可能なネットワークセキュリティディレクターポリシーが登場していたのでご紹介します。

https://docs.aws.amazon.com/ja_jp/waf/latest/developerguide/nsd-what-it-is.html

![](/images/org-policy-for-network-director_2025-12-15-23-19-44.png)

:::message
2025/12/16 現時点では、Organizations からの作成は、
「The provided policy document does not meet the requirements of the specified policy type.」
のようなエラーが表示され、正常に完了できませんでした。
リリース直後で不安定なのか不明ですが、Organizations のコンソール画面から適用できた場合には追記します。
:::

## 3 行まとめ

- AWS Shield Network Security Director の設定を組織全体または OU、アカウント単位でリージョン別に有効化・無効化を一元管理が可能
- 記法はほとんど Security Hub ポリシーと同じ
- 現時点ではパブリックプレビュー中のサービスを扱っているため変更がかかる可能性はあります

## ネットワークセキュリティディレクターポリシーとは

ネットワークセキュリティディレクターポリシーは、AWS Organizations を使用して複数のメンバーアカウントにわたって AWS Shield Network Security Director の有効化の有無を一元管理できる機能です。

AWS Shield Network Security Director を活用することで、管理アカウントから Organizations 全体において設定漏れなく適用できます。

## ネットワークセキュリティディレクターポリシーの記法について

ネットワークセキュリティディレクターポリシーの大枠の構造としては以下のようになります。

```json
{
    "network_security_director": {
        "enablement": {
            "network_security_scan": {
                "enable_in_regions": {
                    "@@append  | @@assign | @@remove": [
                        "<有効化したいリージョン>" | "ALL_SUPPORTED" | "<空欄も可>"
                        ]
                },
                "disable_in_regions": {
                    "@@append  | @@assign | @@remove": [
                        "<無効化したいリージョン>" | "<空欄も可>"
                        ]
                    }
                }
            }
        }
    }
}
```

それぞれ上のレイヤーから見ていきます。

- network_security_director
  - ネットワークセキュリティディレクターポリシーを扱う上でのドキュメントの最上位キーであり、これがネットワークセキュリティディレクターポリシーのドキュメントであることを宣言します
- enablement
  - 組織全体で AWS Shield Network Security Director を有効化する方法を定義し、スキャン構成が含まれます。
- network_security_scan
  - ネットワーク セキュリティスキャンの強制構成を定義します。
- enable_in_regions or disable_in_regions
  - 有効または無効にするリージョンをリスト形式で表記できます
- 継承演算子
  - 指定したリージョンについて追加を行うのか削除を行うのか、子 OU に上書きを許可させるのかなどを指定できます
  - [継承演算子 - AWS Organizations](https://docs.aws.amazon.com/ja_jp/organizations/latest/userguide/policy-operators.html)

### Organizations 全体で Network Security Director の有効化を強制したい場合

Organizations 全体で全てのリージョンで Network Security Director を有効化を強制したい場合は以下のようなポリシーを作成し、root OU に割り当てます。

無効化するリージョンがない場合でも項目としては用意しておく必要があります。

また継承演算子の `@@operators_allowed_for_child_policies` を活用することで、子 OU での上書きを許可したり禁止したりでき、値が `none` の場合は上書きを禁止にできます。

```json
{
    "network_security_director": {
        "enablement": {
            "network_security_scan": {
                "enable_in_regions": {
                    "@@assign": ["ALL_SUPPORTED"],
                    "@@operators_allowed_for_child_policies": ["@@none"]
                },
                "disable_in_regions": {
                    "@@assign": [],
                    "@@operators_allowed_for_child_policies": ["@@none"]
                    }
                }
            }
        }
    }
}
```

### Organizations 全体で東京リージョンと大阪リージョンでのみ Network Security Director を有効化したい場合

東京リージョンと大阪リージョンで Network Security Director を有効化したいといった場合には、
以下のようなポリシーを root OU に割り当てることで全てのアカウントで有効化されます。

```json
{
    "network_security_director": {
        "enablement": {
            "network_security_scan": {
                "enable_in_regions": {
                    "@@assign": ["ap-northeast-1","ap-northeast-3"]
                },
                "disable_in_regions": {
                    "@@assign": []
                    }
                }
            }
        }
    }
}
```

## ネットワークセキュリティディレクターポリシーの有効化方法と使い方

ネットワークセキュリティディレクターポリシーの有効化とポリシー作成の手順について記載します。

### 管理アカウントでのサービス有効化

まずネットワークセキュリティディレクターポリシーを使用するには管理アカウントでサービスのセットアップが必要です。

Organizations 管理アカウントにログインし、AWS Shield から Network Security Director の「Get Started」に移動します。

![](/images/org-policy-for-network-director_2025-12-15-23-38-37.png)

遷移するとこの画面に移動し、いくつか設定項目が表示されます。

![](/images/org-policy-for-network-director_2025-12-15-23-39-36.png)

「Set a delegated administrator」は委任管理アカウントの指定のため、Recommended の選択肢のアカウントまたは明示的に任意のアカウントを指定してください。

「Updates to delegated administrator policy」は委任管理者がサービス管理できるように委任ポリシーを更新するかどうかの選択肢であり、特に指定がなければ「Update the policy for me」を選択してください。

ポリシーの更新を承認するチェックボックスにチェックを入れ、「Complete get started」を押してください。

![](/images/org-policy-for-network-director_2025-12-15-23-40-20.png)

### ポリシーの有効化（失敗例）

**成功した手順を知りたい方はこちらのセクションは飛ばしてください。**

まず Organizations からポリシーをナビゲーションペインで選択し、「ネットワークセキュリティディレクターポリシー」を押します。

![](/images/org-policy-for-network-director_2025-12-15-23-34-59.png)

続いて、「ネットワークセキュリティディレクターポリシーを有効化」を押します。

![](/images/org-policy-for-network-director_2025-12-15-23-35-40.png)

「有効になりました」と表記されたら完了です。

ポリシーを作成したい場合は、「ポリシーを作成」を押します。

![](/images/org-policy-for-network-director_2025-12-15-23-46-54.png)

上部では任意のポリシー名、説明、タグを指定します。

![](/images/org-policy-for-network-director_2025-12-15-23-47-36.png)

下部で任意のポリシードキュメントを反映させ、「ポリシーを作成」を押したら完了です。

![](/images/org-policy-for-network-director_2025-12-15-23-48-36.png)

と思いきや、`The provided policy document does not meet the requirements of the specified policy type.`というエラーが出てしまい先に進めませんでした。

![](/images/org-policy-for-network-director_2025-12-16-00-10-51.png)

現時点では上記の手順でポリシーを有効化できなかったため、AWS CLI からも試してみましたが同様に正常に完了しませんでした。

これがサービス仕様なのか現在リリース直後で不安定なのか不明ですが、
何か正常に動作させる方法がないかと探していたところ、Network Security Director の委任管理アカウントを操作していないことに気付いたので、触ってみたところ成功したため、その手順を次に解説します。

### ポリシーの作成（成功例）

Network Security Director の委任管理アカウントへ切り替え、Network Security Director の画面に遷移し、「Enable」を押します。

![](/images/org-policy-for-network-director_2025-12-16-00-15-27.png)

まずポリシー名や Description の入力を問われるため、任意の値を指定します。

![](/images/org-policy-for-network-director_2025-12-16-00-16-16.png)

続いて、2 種類の設定項目があります。

1 つ目が適用するアカウントの範囲です。  
こちらでは組織全体の「All organizational units and accounts」または任意の OU またはアカウントを指定できる「Target specific organizational units and accounts」のいずれかの選択を求められるため、適切な方を選択します。

2 つ目は有効化または無効化するリージョンです。  
有効化するリージョンは必ず指定が必要です。

最後「Enable network security director」を押せば作成完了です。

![](/images/org-policy-for-network-director_2025-12-16-00-21-33.png)

作成が完了するとポリシー一覧が確認できます。

![](/images/org-policy-for-network-director_2025-12-16-00-23-12.png)

### ポリシーの確認と有効化の確認

Network Security Director で作成したポリシーは Organizations ポリシーの画面でも確認できます。

どうやらポリシータイプ、ネットワークセキュリティディレクターポリシー (カスタマーマネージド) として管理されているようです。
ただこのポリシーをいじると同様のエラーが出るため、基本的には Network Security Director のコンソールで作成・変更が必要なようです。

![](/images/org-policy-for-network-director_2025-12-16-00-26-03.png)

![](/images/org-policy-for-network-director_2025-12-16-00-33-44.png)

どのアカウントがどのリージョンで有効化されているかは、Network Security Director の Dashboard の Accounts という項目で確認できます。

リージョンを切り替えることで確認したいことを変更できます。

![](/images/org-policy-for-network-director_2025-12-16-00-31-06.png)

![](/images/org-policy-for-network-director_2025-12-16-00-31-43.png)

## まとめ

今回は ネットワークセキュリティディレクターポリシーについてご紹介しました。

ネットワークセキュリティディレクターポリシーを活用することでより柔軟かつ確実に Network Security Director を組織全体で有効化でき、組織のネットワークセキュリティに関する分析評価を実施できます。

一部公式ドキュメント通りに行かない部分もありましたが、今後の改善で修正されるのか、あるいはこれが意図した動作なのかについては、変更があり次第、この記事で更新します。

そして 1 万回目になりますが IAM Access Analyzer にもこの機能の実装を…

この記事がどなたかの役に立つと嬉しいです。