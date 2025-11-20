---
title: "[レポート] ギャップに要注意：Windows イベントログの見落としを検出する（そして修正する!） CODE BLUE 2025"
emoji: "🌐"
type: "idea"
topics: ["codeblue","security"]
published: true
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

今回は、日本発の世界トップクラスの専門家による最先端の技術研究が発表される国際的なサイバーセキュリティカンファレンス、CODE BLUE に参加してきたため参加レポートを執筆します。

https://codeblue.jp/

## 「ギャップに要注意：Windows イベントログの見落としを検出する（そして修正する!） 」の概要

- Speakers: 株式会社 NTT データグループ 高橋 福助氏 / 大和セキュリティ 田中ザック氏
- Category: Bluebox
- Location: Track 3(Room 3)

Windows イベントログは DFIR において重要ですが、デフォルト設定ではログサイズの制限や不十分なポリシーにより、脅威検出の死角が生じることがあります。
本セッションでは、Windows イベントログの監査設定を評価・改善するための 2 つのオープンソースツール「WELA」と「EventLog-Baseline-Guide」を紹介します。
これらのツールを活用することで、ログの可視性ギャップを解消し、データに基づいた効果的な DFIR 体制の強化に貢献します。

https://codeblue.jp/program/time-table/day2-t3-02/

## セッションレポート

本セッションでは、

- なかなか使いこなせるまでが難しい Windows イベントログの基本
- デジタル・フォレンジックとインシデント対応（DFIR）の時によく使うイベントログ
- デフォルト設定の課題
- 手動では大変なログ設定を楽にするツールの解説

について話されています。

まず、Windows イベントログ解析の特徴ですが、

- どの Windows 端末にも入っていてフォレンジック調査の基本の一部となる
- 事前に適切な設定することで EDR と同等の証拠が残せる
- ただしかなり癖が強く最初は分かりづらい
- インシデント対応として扱えるようにするために、準備段階で迅速に解析できるようなトレーニングへ時間を割く必要がある

などが挙げられるとのことです。

この図は、Windows DFIR の Artifact の MindMap ですが、
赤い枠で囲われている部分が Windows のイベントログのアーティファクトが調査に大きく寄与する部分です。

そんな設定を最大限に生かすためにどのように設定改善できるかを説明していただいています。

![](/images/codeblue25d2_windows_eventlog_2025-11-19-23-41-22.png)
*高橋氏の講演スライドより*

まずはイベントログの基礎知識です。

Windows XP/2003 では、`.evt`拡張子のイベントログのタイプが使用され、  
パフォーマンス悪く、ログ転送ができないため設定自体を無効にされることが多かったようです。
Windows Vista 以降では、`.evtx`拡張子になり、現在見るような形式になりました。

EVTX は、マイクロソフトの独自バイナリフォーマットの XML ファイルになり、テキストエディタで cat や remove のような形式では参照できないが、イベントビューアーなどの専用のツールで解析は可能です。

イベントログの構造のパターンは 2 種類あります。

```xml-doc:パターン 1
<Event>
  <System>
    <EventData>
```

```xml-doc:パターン 2
<Event>
  <System>
    <UserData>
```

System 配下は固定で共通のデータが入るが、 \<EventData\> または \<UserData\> の中身はイベントによって構造が変わってきます。

下記はイベントの見本でイベントビューアーで見たものです。

![](/images/codeblue25d2_windows_eventlog_2025-11-19-23-59-31.png)
*高橋氏の講演スライドより*

![](/images/codeblue25d2_windows_eventlog_2025-11-19-23-59-42.png)
*高橋氏の講演スライドより*

キーバリューペアでフィールド名も変わってくる、基本は人が読めない 16 進数や%%2313 コードが使用されているとのことです。

<System>フィールドの各フィールド名一覧です。

DFIR の観点では以下のフィールドに着目すべきとのことです。

- Provider Name
- EventID
- TimeCreated

全てのログで共通で重要になるフィールドとのことです。

![](/images/codeblue25d2_windows_eventlog_2025-11-20-00-01-05.png)
*高橋氏の講演スライドより*

ログレベルも出ますが、運用観点で利用が主であり、DFIR ではあまり利用されません。

![](/images/codeblue25d2_windows_eventlog_2025-11-20-00-03-44.png)
*高橋氏の講演スライドより*

<EventData>と<UserData>のフィールドはイベントごとに大きく異なり、規則性もあまりないため、数百種類の様々なフィールドを見分けられるように慣れる必要があります。

続いてはビューアーの説明に入り、
まずビルドインのイベントログビューアーは Event View と呼ばれています。
これは簡単な確認はできるが、DFIR には向いていないものだと言います。ただし急ぎの場合は利用するケースもあるようです。

下記のように GUI でログの設定が可能です。

![](/images/codeblue25d2_windows_eventlog_2025-11-20-00-08-56.png)
*高橋氏の講演スライドより*

多くあるイベントログの中で良く使用される主なイベントログは以下です。

- Application
- Security
- Setup
- System
- Forwarded Events

主なログ以外にもアプリケーションとサービスログがあり、
普段記録されないが重要なエビデンスがログとして出力されることもあるようです。

続いてメインのアジェンダでもある「イベントログのデフォルト設定の課題」について考えます。

デフォルトの監査設定で調査にあたる企業も少なくないが、DFIR 用ではデフォルト設定では不十分であり、調査に利用したいログの 7~9 割が記録されていないようです。  
デフォルトのログサイズは 20MB 程度なので、重要なログはすぐに上書きされ証拠がなくなってしまい数 10 時間程度でなくなってしまうのが課題として挙げられます。  
プロセス実行に関するログが残らないのでフォレンジック調査がとても困難になります。

ここで、Sigma ルールというものを知る必要があるため解説します。

ログデータに対してシグネチャを定義して攻撃を検知するための業界標準フォーマットの形式で無償で利用可能で Sigma を活用することで様々な SIEM に保管および利用が可能です。

https://github.com/SigmaHQ/sigma

![](/images/codeblue25d2_windows_eventlog_2025-11-20-00-26-10.png)
*高橋氏の講演スライドより*

DFIR に必要なログを考えたときに、
デフォルトだと Sigma 検知ルールに対応しているイベントの 1 割程度しかカバーできません。  
全てのイベントログの設定を有効にすると 75%程度カバー可能となります。  
Sysmon を使うことでさらにカバー範囲を広げることができます。

![](/images/codeblue25d2_windows_eventlog_2025-11-20-00-31-40.png)
*高橋氏の講演スライドより*

Sigma 検知ルールにおいてデフォルト設定だとほとんどの項目においてログが不足している状態になります。

![](/images/codeblue25d2_windows_eventlog_2025-11-20-00-50-44.png)
*高橋氏の講演スライドより*

ちなみに、講演当日のニュースで Sysmon が Windows ネイティブ機能で標準実装されたため運用オーバーヘッドが低減しました。

https://techcommunity.microsoft.com/blog/windows-itpro-blog/native-sysmon-functionality-coming-to-windows/4468112

デフォルトログ設定の問題の例として以下のイベントが取れないことも挙げられます。

- イベント ID： `4625`
  - アカウントがログオンに失敗したイベント
- イベント ID： `4776`
  - NTLM 認証失敗ログ（パスワード推測/スプレー攻撃等が検知不可）
- イベント ID： `4688`
  - プロセス作成ログ

このような設定は、
1 台のサーバであれば、ローカルグループポリシー、auditpol、wevtutil、reg コマンド
複数台のサーバであれば、グループポリシー、InTune
などで確認可能です。

下記はコマンドの例です。

![](/images/codeblue25d2_windows_eventlog_2025-11-20-01-04-44.png)
*高橋氏の講演スライドより*

ログをチェックしていても記録されなかったりチェックしていなくても記録されたりもあるため、  
GPO を設定後に適切な形でログ出力されるかは確認する必要があります。

![](/images/codeblue25d2_windows_eventlog_2025-11-20-01-06-12.png)
*高橋氏の講演スライドより*

Windows イベントログ設定ガイドとして以下 3 つが挙げられます。

- Windwos
  - [システム監査ポリシーの推奨事項 | Microsoft Learn](https://learn.microsoft.com/ja-jp/windows-server/identity/ad-ds/plan/security-best-practices/audit-policy-recommendations?tabs=winclient)
- Australian Cyber Security Centre (ACSC)
  - [Windows event logging and forwarding](https://www.cyber.gov.au/business-government/detecting-responding-to-threats/event-logging/windows-event-logging-and-forwarding)
  -  ログ保管期間に関する記述もある
- 大和セキュリティ - DFIR と脅威ハンティングのための Windows イベントログ設定ガイド
  - [Yamato Security's Windows Event Log Configuration Guide For DFIR And Threat Hunting](https://github.com/Yamato-Security/EnableWindowsLogSettings)
  - ログの推奨サイズに関する記述もある

様々な推奨設定があるが、たくさんあるイベントログの推奨設定を全て覚えるのは難しいし大変なため、
楽ができるツールを紹介していただいています。

1 つ目は、`WELA`(Windows Event Log Auditor) というツールがあります。

https://github.com/Yamato-Security/WELA

MITRE ATT&CK の可視化も可能です。

![](/images/codeblue25d2_windows_eventlog_2025-11-20-01-48-05.png)
*高橋氏の講演スライドより*

`EventLog-Baseline-Guide` というツールも紹介されます。

https://github.com/Yamato-Security/EventLog-Baseline-Guide

おまけで Hayabusa というログメトリクスに関するログの保持期間をウォッチできるツールをご紹介いただきました。

最後のまとめとなりますが、  
イベントログデフォルト設定には課題がありログサイズや監査設定には不十分です。  
ガイドはありますが 1 つ 1 つは大変なため、ツールを活用し簡単に実装していくことが重要です。

## まとめ

こちらのセッションでは、
Windows の最適なイベントログの設定方法を理解する方法
について詳しく知ることができました。

この記事がどなたかの役に立つと嬉しいです。