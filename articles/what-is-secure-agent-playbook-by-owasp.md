---
title: "OWASP Secure Agent Playbookのような体系的な思考ロジックでAIのコードのセキュリティレビューを品質向上させてみる"
emoji: "📋"
type: "tech"
topics: ["owasp", "security", "aiエージェント", "claudecode"]
published: false
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

AI エージェントを使ってコードのセキュリティレビューをしたことはありますか？  
AI に、「このコードのセキュリティをチェックして」と頼むと、それなりの結果は返ってきますが、その結果は本当に実際に効果があるものまたは今やるべきものでしょうか。

この記事では、素の AI に依頼した場合と OWASP が公開している **OWASP Secure Agent Playbook** を使った場合の違いを比較し、なぜセキュリティレビューには体系だったプレイブックが必要なのかを解説します。

:::message
**この記事の 3 行まとめ**

- AI に「セキュリティをレビューして」と素で頼んでも、重要な問題は検出できるが「リスクチェーン」や「意図された脆弱性と意図されていない問題の分離」のような専門家らしい視点は欠ける
- OWASP Secure Agent Playbook を使うと、OWASP 標準に基づいた体系的な手順でレビューが進み、監査可能なレポートが得られる
- Claude Code のプラグインとしてインストールするだけで使えるため、導入コストは低い
:::

## 素の AI に頼んだ場合の問題

まず、体系だったプレイブックを使わずに AI にセキュリティレビューを依頼した場合の結果を見てみましょう。対象として、OWASP が公式に提供している脆弱なサンプルアプリ WebGoat を使用しました。

https://github.com/WebGoat/WebGoat.git

:::message alert
WebGoat は教育目的で意図的に脆弱性を含んだアプリケーションです。実際のプロダクションコードではありません。
:::

「このコードのセキュリティ問題をレビューして」と AI に依頼したところ、以下のような結果が返ってきました。

:::details 素の AI によるレビュー結果（全文）

# WebGoat セキュリティコードレビュー結果

以下は、WebGoatプロジェクトのフレームワーク基盤コード（`container`、`server`、`webwolf` パッケージ）のセキュリティレビュー結果です。

レッスンコード（intentionally vulnerable）は除外し、本番環境で同様のパターンが使われた場合のリスクを評価しています。

---

## 総合評価

**Critical**

| 重要度      | 件数 |
| -------- | -: |
| Critical |  3 |
| High     |  7 |
| Medium   | 12 |
| Low      |  8 |

---

## Critical（即時対応必須）

### C-1. NoOpPasswordEncoder（平文パスワード保存）

* **場所:** `WebSecurityConfig.java`（WebGoat / WebWolf 両方）
* **問題:**
  `NoOpPasswordEncoder.getInstance()` を使用し、パスワードが平文で保存される。
* **影響:**
  DB漏洩時に全ユーザー認証情報が即座に悪用可能。
* **対策:**
  `BCryptPasswordEncoder`（コスト係数12以上）に移行する。

---

### C-2. CSRF保護の完全無効化

* **場所:** `WebSecurityConfig.java`（両方）

* **問題:**
  以下の設定により、CSRF保護が全面的に無効化されている。

  ```java
  .csrf(csrf -> csrf.disable())
  ```

* **影響:**
  攻撃者が被害者のセッションで任意操作可能。

* **対策:**
  CSRFレッスン用エンドポイントのみ例外とし、それ以外はCSRF保護を有効化する。

---

### C-3. Actuatorエンドポイントの認証なし公開

* **場所:** `WebSecurityConfig.java` + `application-webgoat.properties`
* **問題:**
  `/actuator/**` が `permitAll()` に設定されている。
  また、`env`、`configprops` が認証不要で公開されている。
* **影響:**
  DB接続文字列、シークレット、内部設定値が漏洩する。
* **対策:**
  `ADMIN` 権限を必須化し、公開エンドポイントを `health` のみに限定する。

---

## High（早期対応推奨）

| #   | 問題                  | 場所                               | 概要                                                                 |
| --- | ------------------- | -------------------------------- | ------------------------------------------------------------------ |
| H-1 | SQLインジェクション         | `UserService.java`               | OAuth2経由のユーザー名がバリデーション未適用のまま `CREATE SCHEMA` に連結される                |
| H-2 | セキュリティヘッダー全無効       | `WebSecurityConfig.java`         | `.headers(headers -> headers.disable())` により、XSS / クリックジャッキング防御が無効 |
| H-3 | パストラバーサル            | `FileServer.java`（WebWolf）       | `getOriginalFilename()` を未サニタイズでパスに使用                              |
| H-4 | 弱いパスワードポリシー         | `UserForm.java`                  | 最大10文字制限、複雑性要件なし                                                   |
| H-5 | 脆弱な依存関係             | `pom.xml`                        | `XStream 1.4.5`、`commons-collections 3.2.1`（RCEガジェット）              |
| H-6 | SSL無効 + ハードコードパスワード | `application-webgoat.properties` | `ssl.enabled=false`、パスワード `password` をソースに記載                       |
| H-7 | スタックトレース全公開         | `application-*.properties`       | `include-stacktrace=always` により、クラス名・バージョンが露出                      |

---

## Medium（計画的対応推奨）

主要な項目は以下のとおりです。

| ID   | 内容                                     |
| ---- | -------------------------------------- |
| M-1  | OAuth2ユーザー名バリデーション不足（H-1の攻撃チェーン）       |
| M-2  | WebWolf `GET /files/**` が認証不要          |
| M-3  | `POST /mail` が認証不要（スパムベクター）            |
| M-4  | メールコンテンツ未検証（Stored XSS）                |
| M-5  | ファイルアップロードのタイプ・サイズ制限なし                 |
| M-7  | セッション固定対策の明示設定なし                       |
| M-10 | Dockerの過剰な `--add-opens` フラグ（8モジュール開放） |

---

## 優先対応ロードマップ

### 即時（1〜2週間）

1. `BCryptPasswordEncoder` への移行
2. Actuator認証必須化 + 公開範囲縮小
3. OAuth2ユーザー名バリデーション追加（SQLi対策）
4. FileServerパストラバーサル修正
5. スタックトレース非公開化

（省略）

:::

重要度別に整理されており、主要な脆弱性を捉えている点は評価できますが、この結果には、いくつか気になる点があります。

- 複数の問題が組み合わさって成立する攻撃経路（リスクチェーン）が見えない
- 根拠となる標準の参照がない

これらは AI の能力の問題ではなく、何の手順に従うかがAIに対して指定されていないことが原因です。

## OWASP Secure Agent Playbook Project とは

https://github.com/OWASP/secure-agent-playbook

OWASP Secure Agent Playbook は、AI エージェントがセキュリティエンジニアリングタスクを実行するための、[OWASP](https://owasp.org/) が作成した構造化されたプレイブックです。

### 構成

プロジェクトは 3 層の構造になっています。

| 層 | 役割 |
|---|---|
| Agents | フォーカスされたシステムプロンプトを持つ自律型セキュリティスペシャリスト |
| Skills | `SKILL.md` 形式の自己完結したモジュール。Claude Code のプラグインとして配布 |
| Plays | 詳細なチェックリスト・判断基準・テンプレートを含む完全な参照手順書 |

呼び出し関係は `Agent → Skill（を呼び出す）→ Play（詳細手順）` となっています。

### 定義されている Agent

合計 6 体の Agent が定義されており、`security-team-lead` が司令塔として複数のスペシャリスト Agent を並列起動する構造になっています。

| Agent 名 | 役割 | 使用 Skill |
|---|---|---|
| `security-team-lead` | 司令塔。スペシャリストを並列起動し結果を統合する | `securability-engineering-review` |
| `code-security-reviewer` | コード脆弱性専門家 | `code-review-security`, `secrets-scan`, `web-security-review` |
| `dependency-auditor` | サプライチェーン・依存関係専門家 | `sca-audit` |
| `api-security-reviewer` | API セキュリティ専門家（REST/GraphQL/gRPC） | `api-security-review` |
| `mobile-security-reviewer` | モバイルセキュリティ専門家（Android/iOS） | `mobile-code-review` |
| `ai-security-assessor` | AI・エージェントセキュリティ専門家 | `agent-security-audit`, `mcp-server-review`, `llm-risk-assess`, `prompt-injection-test` |

`security-team-lead` の処理フローは以下の 3 フェーズで進みます。

1. **偵察フェーズ**: プロジェクトの構造・言語・フレームワークを把握し、どのスペシャリストを起動するか判断
2. **ディスパッチフェーズ**: 関連するスペシャリスト Agent を並列で起動
3. **統合フェーズ**: 全 Agent の結果を集約・重複排除してクロスドメインのリスク連鎖を特定し、SSEM スコア（0〜10）付きで最終レポートを出力


:::message
`security-team-lead` を使用するためには、Claude Codeのエージェントチームが有効化になっている必要があります。
[Claude Code セッションのチームを調整する - Claude Code Docs](https://code.claude.com/docs/ja/agent-teams#%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88%E3%83%81%E3%83%BC%E3%83%A0%E3%82%92%E6%9C%89%E5%8A%B9%E3%81%AB%E3%81%99%E3%82%8B)
:::

### 含まれているスキル

提供されているスキルは大きく 2 カテゴリに分かれます。

#### コード・インフラセキュリティ（11 スキル）

| スキル名 | 内容 |
|---|---|
| `code-review-security` | OWASP Top 10 + ASVS 準拠のセキュリティコードレビュー |
| `sca-audit` | 依存関係の CVE スキャン（到達可能性分析付き） |
| `secrets-scan` | ハードコードされた認証情報・API キーの検出 |
| `api-security-review` | OWASP API Top 10 (2023) 対応の API レビュー |
| `web-security-review` | OWASP Top 10 (2021) 対応の Web アプリレビュー |
| `mobile-code-review` | OWASP MASVS v2.1.0 準拠の Android/iOS レビュー |
| `iac-security-review` | Terraform/Kubernetes/CloudFormation の IaC セキュリティレビュー |
| `securability-engineering` | FIASSE v1.0.4 に基づくセキュアなコード生成 |
| `securability-engineering-review` | 0〜10 のスコアリング（SSEM）でコードのセキュリティ品質を評価 |
| `prd-securability-enhancement` | PRD・仕様書を ASVS カバレッジで強化（コード作成前に実施） |
| `security-guidance` | セキュリティに敏感なコードへの ASVS ガイダンス自動提示 |

#### AI・エージェントセキュリティ（6 スキル）

コードセキュリティに加え、AI エージェント特有のセキュリティリスクに対応したスキル群も提供されています。

| スキル名 | 内容 | 参照標準 |
|---|---|---|
| `agent-security-audit` | エージェントの権限・Injection 面・データ漏洩経路の監査 | OWASP LLM Top 10 |
| `llm-risk-assess` | LLM アプリを LLM Top 10 2025 で評価 | OWASP LLM Top 10 |
| `agentic-ai-risk-assess` | エージェント型 AI アプリを Top 10 Agentic 2026 で評価 | OWASP Agentic Top 10 |
| `mcp-server-review` | MCP サーバーのセキュリティレビュー | OWASP LLM Top 10 |
| `prompt-injection-test` | Arcanum PI Taxonomy に基づく Prompt Injection テスト | LLM01 |
| `multi-agentic-threat-model` | CSA MAESTRO の 7 層フレームワークによる脅威モデリング | CSA MAESTRO |

AI エージェントによるセキュリティレビューを AI エージェント自身に適用できる点も、このプロジェクトならではの特徴です。

### インストール方法

Claude Code に以下のコマンドでプラグインとしてインストールするだけで使えます。

```shell
# マーケットプレイスの追加
/plugin marketplace add OWASP/secure-agent-playbook
```

```shell
# スキルのインストール
/plugin install code-security-skills@agent-security-playbook
/plugin install ai-security-skills@agent-security-playbook
```

インストール後は、Claude Code の会話の中でスラッシュコマンドとして呼び出したり、コードをレビューするように指示したりすることでスキルが利用できるようになります。

## OWASP Secure Agent Playbook を使うと何が変わるか

続いて、同じ WebGoat に対して、OWASP Secure Agent Playbook の `/code-review-security` スキルを使ってレビューしてみました。

:::message
環境の関係上、プレイブックなしは Claude Code 以外の AI エージェントを使用しましたが、使用した LLM　のバージョンは比較用に揃えています。
:::

:::details OWASP Secure Agent Playbook によるレビュー結果（全文）

# OWASP WebGoat セキュリティアセスメントレポート

| 項目        | 内容                                                 |
| --------- | -------------------------------------------------- |
| 評価日       | 2026-06-07                                         |
| 対象        | WebGoat 2026.2-SNAPSHOT（Spring Boot 3.5 / Java 25） |
| 総合SSEMスコア | 4.3 / 10（Poor）                                     |

> **注意:** WebGoatは意図的に脆弱性を含む教育用アプリです。
> 本レポートでは「意図されていない問題」と「意図的設計だが実環境で過剰なリスクとなる問題」を分けて報告しています。

---

## 発見事項サマリー

| ID   | 重大度      | カテゴリ | タイトル                                     |
| ---- | -------- | ---- | ---------------------------------------- |
| F-01 | CRITICAL | 認証   | 平文パスワードストレージ（NoOpPasswordEncoder）        |
| F-02 | CRITICAL | 設定   | セキュリティヘッダー全無効化                           |
| F-03 | CRITICAL | 設定   | Actuatorエンドポイントが認証なしで公開                  |
| F-04 | HIGH     | 依存関係 | XStream 1.4.5（RCE多数のCVE）                 |
| F-05 | HIGH     | 依存関係 | jjwt 0.9.1（EOL・alg:none攻撃リスク）            |
| F-06 | HIGH     | 依存関係 | commons-collections 3.2.1（CVE-2015-6420） |
| F-07 | HIGH     | コード  | ユーザー名によるSQLスキーマ注入（UserService）           |
| F-08 | HIGH     | 設定   | スタックトレース全公開（include-stacktrace=always）   |
| F-09 | HIGH     | ファイル | ファイル名未検証によるパストラバーサル（FileServer）          |
| F-10 | MEDIUM   | 認証   | パスワード最大10文字の弱い制約                         |
| F-11 | MEDIUM   | 設定   | KeyStoreパスワードがデフォルトpassword              |
| F-12 | MEDIUM   | 設定   | SSLがデフォルト無効                              |
| F-13 | MEDIUM   | 認証   | JWTで全バリデーターをスキップ（setSkipAllValidators）   |

---

## 重要な発見事項（詳細）

### F-07: HIGH — スキーマ名SQL注入（意図されていない問題）

* **場所:** `UserService.java:53`

* **内容:**
  以下のように、ユーザー名をDDLに直接連結している。

  ```java
  "CREATE SCHEMA \"" + webGoatUser.getUsername() + "\" authorization dba"
  ```

  `UserForm.java` のバリデーションで大半はブロックされるが、OAuth登録パス経由でバイパスされる可能性がある。

* **修正:**
  UUID等の内部識別子でスキーマを作成し、ユーザー名とスキーマのマッピングテーブルを管理する。

---

### F-09: HIGH — パストラバーサル（意図されていない問題）

* **場所:** `FileServer.java:75`

* **内容:**
  以下のように、アップロードファイル名をそのままパス解決に使用している。

  ```java
  destinationDir.toPath().resolve(multipartFile.getOriginalFilename())
  ```

  `../` 等を含むファイル名により、任意ディレクトリへの書き込みが可能。
  また、`/fileupload/**` が認証なしで公開されている（`WebSecurityConfig.java:38`）。

* **修正:**
  以下のようにファイル名のみを取り出し、ディレクトリ境界チェックを追加する。

  ```java
  Paths.get(filename).getFileName().toString()
  ```

---

## リスクチェーン（高リスク）

### チェーンA

`commons-collections 3.2.1` + `InsecureDeserialization.java` により、認証済みユーザー全員がRCE可能。

```java
Runtime.getRuntime().exec()
```

### チェーンB

`NoOpPasswordEncoder` + `/actuator/env` 無認証公開により、DB接続情報取得後、全ユーザーの平文パスワード一覧を取得可能。

### チェーンC

`FileServer.java` のパストラバーサル + `/fileupload/**` 認証なし公開により、任意ファイル書き込みの可能性がある。

---

## 優先修正ロードマップ

| 優先度    | 対象                         | 対応内容                                        |
| ------ | -------------------------- | ------------------------------------------- |
| P1（即時） | F-07 `UserService.java:53` | OAuth登録パスのユーザー名サニタイズ追加                      |
| P1（即時） | F-09 `FileServer.java:75`  | `getFileName().toString()` でパス正規化           |
| P1（即時） | F-08 スタックトレース              | デフォルトを `never` に変更                          |
| P2（短期） | F-03 Actuator              | `permitAll()` から `/actuator/**` を除外         |
| P2（短期） | F-11 KeyStore              | `goatkeystore.pkcs12` を `.gitignore` に追加    |
| P3（中期） | F-04/F-06 依存関係             | XStream / commons-collections レッスンの追加認証でラップ |

---

## SSEMスコア内訳

| ピラー             |      スコア | 主な問題                                  |
| --------------- | -------: | ------------------------------------- |
| Maintainability | 5.5 / 10 | 静的可変フィールドによるテスト汚染                     |
| Trustworthiness | 3.0 / 10 | `NoOpPasswordEncoder`・全ヘッダー無効化・CSRF無効 |
| Reliability     | 4.3 / 10 | レート制限なし・タイムアウト未設定・パストラバーサル            |
| 総合              | 4.3 / 10 | 教育目的の意図的設計が主因だが、意図されていない問題も複数存在       |

:::

### 2 つのレポートの違い

| 観点 | プレイブックなし | プレイブックあり |
|---|---|---|
| 意図した脆弱性と意図しない問題の区別 | なし | あり（レポート冒頭で明示） |
| リスクチェーンの分析 | なし | あり（チェーン A〜C） |
| 定量的スコア | なし | SSEM スコア（0〜10）でピラー別に評価 |
| 参照標準の明示 | なし | OWASP Top 10・ASVS・CWE に紐づけ |
| 修正コードの提示 | 指針のみ | 具体的なコードスニペット付き |

プレイブックを使うと、AI モデルの能力ではなく**レビュー工程が構造化・標準化・監査可能な状態**になっていることがわかります。

### プレイブックはどのような思考ロジックで動いているか

なぜこれだけ差が出るのか、`code-review-security` プレイの内部構造を見て行きます。

https://github.com/OWASP/secure-agent-playbook/blob/main/plugins/code-security-skills/plays/code-review-security.md

このプレイは以下の 5 ステップで構成されています。

| ステップ | 内容 |
|---|---|
| Step 1: Scope & Context | レビュー対象の文脈を確定する |
| Step 2: Systematic Review by Vulnerability Class | 脆弱性クラスを影響度の高い順に審査する |
| Step 3: Framework-Specific Checks | 検出されたフレームワーク固有のチェックを追加する |
| Step 4: Diff-Specific Analysis | PR レビューの場合は差分に特化した分析を行う |
| Step 5: Produce Findings | ファインディングを規定フォーマットで記録する |

WebGoat への実際の適用を例に各ステップを見ていきます。

#### Step 1: まず「文脈」を確定させる

最初のステップでレビュー対象の文脈を 4 軸で確定させます。

- Language/Framework・言語/フレームワーク
  - どの脆弱性クラスが関連するかを決める
- Trust boundary・信頼の境界
  - サーバーサイド / クライアントサイド / ライブラリ / インフラコードの区別
- Data sensitivity:・データ機密性
  - PII・認証情報・金融データを扱うか
- Exposure・公開範囲
  - インターネット公開 / 社内のみ / ローカルのみ

WebGoat の場合は「Java / Spring Boot・サーバーサイド・ユーザー認証データ・インターネット公開想定」と確定してからレビューに入ります。

いきなりコードを読むように指示するのではなく、前提条件を明示的に確定させることが重要なんだなと感じます。

#### Step 2: 脆弱性クラスを影響度の高い順に審査する

次に、審査する順序が明示的に規定されています。

1. Injection・インジェクション攻撃（CWE-74、OWASP A03、OpenCRE 161-451）
2. Authentication & Session・認証とセッション  (CWE-287、OWASP A07、OpenCRE 633-428 )
3. Authorization・認証（CWE-862、OWASP A01、OpenCRE 724-770）
4. Cryptography・暗号化（CWE-327、OWASP A02、OpenCRE 278-646）
5. Data Exposure・データ漏洩（CWE-200、OWASP A01、OpenCRE 126-668）
6. Security Misconfiguration・セキュリティ設定の誤り（OWASP A05、OpenCRE 233-748）
7. Deserialization & Data Integrity・デシリアライゼーションとデータ整合性（CWE-502、OWASP A08、OpenCRE 854-643）

素の AI に「レビューして」と頼んだだけでは、この審査順序は存在しません。見つかった順・重大そうに見えた順でリストアップされます。

プレイブックを活用すると Injection を最初に審査するよう定められているため、今回だと `UserService.java:53` の SQL スキーマ注入が最優先で掘り下げられます。  
さらに各クラスの中に「SQL Injection の場合はクエリ内の文字列連結・パラメータ化の欠如・ORM の raw クエリを見る」のように具体的なチェック項目が列挙されており、見落としを構造的に防ぎます。

各チェック項目には OpenCRE のリンクが直接埋め込まれており（例: Injection には `[OpenCRE 161-451](https://www.opencre.org/cre/161-451)`）、ASVS・WSTG・NIST 800-53 への横断参照が自動解決されます。

**Step 3: フレームワーク固有のチェックを追加する**

Step 1 で確定した文脈をもとに、フレームワーク固有のリスクをさらに追加します。

WebGoat の場合では、 Spring を使っているため「SpEL インジェクション・Actuator の公開・マスアサインメント」という Spring 固有のチェックリストが自動的に追加されます。  
F-03（Actuator エンドポイントの認証なし公開）はこのステップで検出されます。素の AI はフレームワークの特性を文脈から推測しますが、チェック項目の列挙漏れが起きやすいです。

**Step 4: PR レビューの場合は差分に特化した分析をする**

今回はコードベース全体を対象にしているため Step 4 は適用外ですが、PR レビュー時はこのステップが機能します。

変更行とその周辺の未変更コードに既存の security control が維持されているかを確認し、新しいエンドポイントに既存の認証パターンと整合した認可が付与されているかを検証します。削除された validation や auth check も検出対象になります。

**Step 5: 攻撃シナリオを具体的に記録する**

各検出結果は、「ファイル:行番号・脆弱なコードスニペット・攻撃シナリオの具体的説明・修正済みコード・確信度（HIGH / MEDIUM / LOW）」の形式で記録するよう義務付けられています。  
F-07 に対しては攻撃シナリオとして「`UserForm.java` のバリデーションで大半はブロックされるが、OAuth 登録パス経由でバイパスされる可能性がある」と記述されます。

「どこから到達できるか」を明示することで、単なる脆弱性列挙を超えた記録になります。

### リスクチェーンは `security-team-lead` が担う

ここまでが `code-review-security` プレイ単体の役割です。

比較結果に出てきた「チェーン A〜C」は、`security-team-lead` エージェントが複数のスペシャリストの結果を統合する際に生成されます。  
`code-security-reviewer`（コードの問題）と `dependency-auditor`（依存関係の CVE）の結果が揃ってはじめて「F-06 の `commons-collections` と F-07 の SQL インジェクションを組み合わせると RCE になる」という連鎖が検出されます。一つのプレイではなく、エージェントのチームワークで成立している点が重要です。

これら一連のロジックは、熟練したセキュリティエンジニアが頭の中で自然にやっていることをプレイブックとして明文化したもので、AI が従う手順書として渡すことで、モデルの能力差によらず一定品質のレビューを再現できます。

## おまけ

今回検証してみて、ここに最新の脆弱性情報をコンテキストとして付与してあげるともっと効果が上がるのではないか？と思い、上位スキルとして以下を作成してみました。

:::details secure-agent-context-enricher スキル定義（全文）

---
name: secure-agent-context-enricher
description: Auxiliary vulnerability context provider for OWASP Secure Agent Playbook. Extracts CVE candidates from project dependencies, enriches them with CISA KEV, FIRST EPSS, NVD CVSS v4.0/v3.1, CVE Record/CNA, and CISA Vulnrichment, then passes the enriched context to OWASP Secure Agent Playbook as supporting material for security code review. OWASP Secure Agent Playbook remains the primary review engine and finding authority.
license: CC-BY-4.0
---

# secure-agent-context-enricher

Auxiliary vulnerability context provider for OWASP Secure Agent Playbook.
Phases 1 and 2 prepare CVE context. Phase 3 hands it to OWASP as the primary review engine.

## ABSOLUTE RULES (enforce before anything else)

**NEVER write any file to disk during this skill's execution.**
- All CVE enrichment data is held in the current session context only
- Exception: user explicitly says "ファイルに保存して", "save to file", or "--save"

## Role Boundary

```
OWASP Secure Agent Playbook
  = Main review engine              ← you defer to this
  = Scope decision owner            ← you do not override this
  = Security finding owner          ← you do not modify this
  = Code/API/Web/IaC/SCA/Agent/MCP review owner ← you do not duplicate this

secure-agent-context-enricher (YOU)
  = CVE candidate extractor
  = KEV/EPSS/CVSS/CVE Record/Vulnrichment fetcher
  = Context packager for OWASP agents
  = Post-review annotation helper (optional, user-initiated only)
```

## Execution Flow

### Phase 1 — Dependency Context Discovery

Scan the project for dependency files and lockfiles across all ecosystems:

| Ecosystem | Manifest | Lockfile (preferred) |
|-----------|----------|---------------------|
| Node.js | package.json | package-lock.json, yarn.lock, pnpm-lock.yaml |
| Python | requirements.txt, pyproject.toml | Pipfile.lock, poetry.lock |
| Java | pom.xml, build.gradle | gradle.lockfile |
| Go | go.mod | go.sum |
| Ruby | Gemfile | Gemfile.lock |
| Rust | Cargo.toml | Cargo.lock |
| .NET | *.csproj | packages.lock.json |
| PHP | composer.json | composer.lock |

Also scan for: Dockerfile, docker-compose.yml, SBOM files (*.cdx.json, *.spdx.json, sbom.json), existing scanner outputs (osv-scanner.json, trivy.json, grype.json, npm-audit.json, pip-audit.json).

Run available SCA scanners to extract CVE candidates (preference order):
1. `osv-scanner --lockfile=<path> --format=json`
2. `npm audit --json`
3. `pip-audit -r requirements.txt --format=json`
4. `trivy fs --format json --scanners vuln <path>`

If no scanner is available, record as `manual_context_needed` and continue.

### Phase 2 — Vulnerability Context Enrichment

For each CVE candidate, enrich in this exact order. On any API failure, record the error and continue — never halt for a single CVE.

**Step 1: CISA KEV**
- Download once per session: `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`
- Extract: `dateAdded`, `dueDate`, `knownRansomwareCampaignUse`, `requiredAction`

**Step 2: FIRST EPSS**
- Batch up to 100 CVEs: `https://api.first.org/data/v1/epss?cve=CVE-A,CVE-B,...`
- Response fields (both are required, must not be confused):
  - `epss` (0.0–1.0): probability of exploitation in the wild within the next 30 days
  - `percentile` (0.0–1.0): rank of this CVE relative to all scored CVEs (e.g. 0.9996 = top 0.04%)
- Always label each value with its field name when presenting — never say "EPSS score" for the percentile or vice versa

**Step 3: NVD CVSS**
- `https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={CVE_ID}`
- Use `NVD_API_KEY` header if env var is set (50 req/30s vs 5 req/30s without key)
- Priority: CVSS v4.0 first, then v3.1

**Step 4: CVE Record / CNA CVSS** (if NVD has no metrics)
- `https://cveawg.mitre.org/api/cve/{CVE_ID}`
- Extract CNA-provided CVSS from `containers.cna.metrics`

**Step 5: CISA Vulnrichment**
- `https://raw.githubusercontent.com/cisagov/vulnrichment/main/{YEAR}/{CVE_ID}.json`
- Extract SSVC decision values and ADP CVSS if available

**Primary CVSS priority:** NVD v4.0 > NVD v3.1 > CNA > CISA-ADP

### Phase 3 — Context Handoff to OWASP Secure Agent Playbook

Hold all enriched CVE data in the current session context (per-CVE: package info, KEV status, EPSS, primary CVSS, description, SSVC; summary: KEV-listed, high-EPSS ≥0.5, critical-CVSS ≥9.0, manual-review-needed).

Invoke OWASP Secure Agent Playbook's `security-team-lead` (or relevant agent) with the following prompt, embedding the in-session CVE context directly:

---

```
Use OWASP Secure Agent Playbook as the primary security review engine.

The vulnerability context below is auxiliary input from secure-agent-context-enricher.
Phases 1 and 2 (dependency discovery and CVE enrichment) were completed solely to prepare
this context — they do not constitute findings. All findings, scope decisions, and severity
assessments are yours to make.

Use this context to enhance your analysis in the following ways:

## 1. CVE Reachability Analysis
For each CVE in the context, verify:
- Is the affected package/version present in the runtime artifact (not just dev dependencies)?
- Is the vulnerable function or code path imported and actually called?
- Is the affected component reachable by untrusted input or network requests?
- Are authentication or privileges required before reaching the vulnerable path?

## 2. Attack Chain Investigation (Priority Focus)
Use the CVE context to investigate multi-step attack chains across components:
- Can a CVE in a dependency serve as an initial foothold that enables a higher-severity
  finding elsewhere (e.g., deserialization CVE → RCE, SSRF CVE → IMDS access)?
- Can multiple lower-severity CVEs be chained to achieve higher impact
  (e.g., info-disclosure CVE → authentication bypass → privilege escalation)?
- Do any KEV-listed or high-EPSS CVEs affect components at trust boundaries
  (API gateways, auth middleware, session handlers, file parsers, template engines)?
- Are there CVEs in components handling secrets, tokens, or credentials that could
  enable lateral movement or privilege escalation when combined with other findings?
- For Agent/MCP components: can a CVE in an HTTP client, parser, or sandbox library
  be chained with a prompt injection or tool misuse finding to exfiltrate data or
  execute unintended actions?

## 3. Cross-Domain Risk Amplification
Identify cases where a CVE amplifies the severity of a non-CVE finding:
- A code-level injection finding becomes critical if a CVE in the same request path
  provides an additional unauthenticated entry point
- An insecure configuration finding becomes exploitable if a CVE removes a defense
  that was implicitly relied upon
- An API authorization flaw becomes easier to exploit if a CVE reduces attacker effort

## 4. Interpretation Rules
Do NOT let KEV, EPSS, or CVSS scores override OWASP methodology. Treat them as:
- KEV: known exploitation confirmed in the wild — raises urgency for reachability verification
- EPSS `epss` field: probability of exploitation in the wild within 30 days — use to prioritize which CVEs to verify first
- EPSS `percentile` field: relative rank among all scored CVEs — indicates how this CVE compares to others, not an absolute probability
- CVSS: technical severity baseline — does not account for application-specific context

For code, API, Web, IaC, Secrets, Agent, and MCP findings without CVEs,
rely entirely on OWASP Secure Agent Playbook methodology and evidence-based analysis.

## Vulnerability Context
[in-session CVE enrichment data embedded here]
```

---

If OWASP agents are not directly callable, present the above prompt with the in-session context embedded for the user to copy into an OWASP session.

### Phase 4 — Optional Post-Review Annotation (user-initiated only)

Run ONLY when the user explicitly requests annotation of OWASP findings.

**Rules:**
- NEVER modify OWASP finding body, title, severity, confidence, CWE, or location
- NEVER annotate findings that have no `**CVE**:` field
- OWASP Secure Agent Playbook's `templates/finding.md` and `templates/report.md` formats are the output authority — do not invent a separate format
- Append KEV/EPSS/CVSS enrichment data to the existing `**CVE**:` line's finding block only, as supplemental lines after `**Confidence**:`

## Output

All output format follows OWASP Secure Agent Playbook's `templates/report.md` and `templates/finding.md` exactly. Do not invent a separate progress log or summary format.

The only status message allowed before handing off to OWASP:
```
[secure-agent-context-enricher] Phase 1: [M] CVEs found. Phase 2: [K] KEV / [J] high EPSS / [L] critical CVSS. Passing context to OWASP Secure Agent Playbook. (No files written.)
```

:::

### 追加されたロジック

AIにやりたいことを渡して生成してもらったので、内容を解説すると、ベースの OWASP Secure Agent Playbook に対して、このスキルは 4 つのフェーズを前段・後段に追加しています。

**Phase 1 — 依存関係スキャンで CVE 候補を抽出する**

`pom.xml` / `package-lock.json` / `go.sum` など全エコシステムの依存ファイルを読み込み、`osv-scanner` / `npm audit` / `trivy` を順番に試して CVE 候補を列挙します。ベースのプレイブックも依存関係の CVE スキャン（`sca-audit` スキル）を持っていますが、このフェーズはその結果を次の Phase 2 に渡すための準備として独立しています。

**Phase 2 — CVE を 5 つのソースで文脈付けする**

CVE 番号が手に入ったら、以下の順で情報を付加します。

| ソース | 付加する情報 | 意味 |
|---|---|---|
| CISA KEV | `dateAdded`・`knownRansomwareCampaignUse` | 実際に野外で悪用が確認された脆弱性かどうか |
| FIRST EPSS | スコア（0.0〜1.0）・パーセンタイル | 今後 30 日以内に悪用される確率の予測値 |
| NVD CVSS v4.0/v3.1 | 技術的な深刻度スコア | 技術的なベースライン（文脈を考慮しない） |
| CVE Record / CNA | NVD にメトリクスがない場合の代替 CVSS | — |
| CISA Vulnrichment | SSVC の決定値・ADP CVSS | 政府機関の優先度評価 |

ベースのプレイブックは CVE 番号と CVSS スコアは参照しますが、「その CVE が今現在実際に悪用されているか（KEV）」「悪用される確率（EPSS）」という**脅威インテリジェンス**は持っていないため追加情報として渡しています。

**Phase 3 — 文脈付きで OWASP に渡す**

Phase 2 で作った文脈を OWASP Secure Agent Playbook に渡す際、以下の 3 点の追加分析を指示します。

1. **CVE 到達可能性分析**: 脆弱なバージョンが存在するだけでなく、「そのコードパスが実際に呼ばれているか」「外部からの入力が到達できるか」を検証させる
2. **攻撃チェーン調査**: KEV 登録済み・高 EPSS の CVE がトラストバウンダリ（認証ミドルウェア・ファイルパーサー・テンプレートエンジン）に存在する場合、そこを起点にチェーンが成立しないかを優先的に調査させる
3. **クロスドメインリスク増幅**: コードレベルのインジェクション問題と同じリクエストパスに CVE が存在する場合、単体より深刻度が高まることを考慮させる

**Phase 4 — オプションの事後アノテーション**

ユーザーが明示的に要求した場合のみ、OWASP のレポートに KEV/EPSS/CVSS の情報を追記します。OWASP 側のファインディングの本文・重大度・CWE・場所は一切変更しないというルールが厳格に定められています。

このスキルは「OWASP Secure Agent Playbook のレビュー品質はそのままに、CVE の優先度判断に脅威インテリジェンスを加える」という役割分担になっています。

### 結果について

結果は以下のように返ってきました。

:::details 脅威インテリジェンス付きレビュー結果（全文）

# WebGoat セキュリティアセスメント — 完了レポート

`[secure-agent-context-enricher] Phase 1: 34 CVEs found. Phase 2: 1 KEV / 10 high EPSS / 2 critical CVSS. Passing context to OWASP Secure Agent Playbook. (No files written.)`

---

## 全体評価

**SSEM スコア: 3.2 / 10 — POOR**（意図的な脆弱アプリのため予測通り）

---

## 発見事項サマリー（33件）

### CRITICAL (5件)

| ID       | 題目                                                                         | CVE                                                 |
| -------- | ---------------------------------------------------------------------------- | --------------------------------------------------- |
| **F-01** | XStream 1.4.5 RCE デシリアライゼーション — **KEV 登録済み (EPSS 94%)**      | CVE-2021-39144                                      |
| **F-02** | commons-collections 3.2.1 ガジェットチェーン RCE                             | CVE-2015-6420 (CVSS 9.8), CVE-2015-7501 (CVSS 10.0) |
| **F-03** | `ObjectInputStream.readObject()` + `VulnerableTaskHolder` が OS コマンド実行 | —                                                   |
| **F-04** | JWT KID ヘッダー SQL インジェクション (`JWTHeaderKIDEndpoint`)               | —                                                   |
| **F-05** | `NoOpPasswordEncoder` — 平文パスワード保存                                   | —                                                   |

### HIGH (15件)

- **F-06**: XXE (`CommentsCache.parseXml`, `securityEnabled=false`)
- **F-07〜09**: XStream SSRF (CVE-2020-26258, EPSS 0.94) / パストラバーサル / 追加 RCE クラスタ
- **F-10**: Spring Actuator `/actuator/env` が認証ユーザー全員に公開 (**permitAll**)
- **F-11**: JWT JKU ヘッダー SSRF → AWS IMDS 到達可能
- **F-12〜14**: SQL インジェクション（複数エンドポイント）
- **F-15〜16**: パストラバーサル / Zip Slip
- **F-17**: IDOR（`IDOREditOtherProfile` に認可チェックなし）
- **F-18〜20**: CSRF グローバル無効化 / セキュリティヘッダー全無効 / スタックトレース全公開

---

## 重大なアタックチェーン

**Chain A — 認証済みユーザーによる RCE (CRITICAL)**
```
1. /registration (permitAll) でアカウント作成
2. POST /InsecureDeserialization/task に ysoserial CommonsCollections1 ペイロード送信
3. ObjectInputStream → InvokerTransformer ガジェットチェーン発火
4. Runtime.getRuntime().exec() → ホスト OS コマンド実行
```

**Chain B — JWT 偽造 → 権限昇格 (HIGH)**
```
1. KID SQL インジェクションで署名鍵を制御
2. admin=true の JWT を偽造
3. 管理者機能にアクセス
```

**Chain C — Actuator + WebWolf ファイル流出 (HIGH)**
```
1. GET /actuator/env (認証不要) → DB URL・OAuth シークレット漏洩
2. GET /WebWolf/files/{username}/ (認証不要) → アップロードファイル読取
```

**Chain D — XStream SSRF + AWS IMDS (HIGH, クラウド環境)**
```
1. CVE-2020-26258 XStream ペイロード
2. http://169.254.169.254/... へ HTTP GET
3. IAM 一時認証情報を取得 → AWS API への横移動
```

---

## 優先修正ロードマップ

### 即時対応 (CRITICAL)
1. XStream を 1.4.21+ にアップグレード（レッスン用は `VulnerableXStreamFactory` で分離）
2. commons-collections を 3.2.2+ にアップグレード
3. JEP 290 デシリアライゼーションフィルターを適用
4. `NoOpPasswordEncoder` → `BCryptPasswordEncoder` に変更
5. JWT KID の SQL をパラメータ化クエリに修正

### 短期対応 (HIGH, 1スプリント)
6. CSRF 保護を有効化（`csrf.disable()` を削除）
7. セキュリティヘッダーを有効化（`headers.disable()` を削除）
8. `server.error.include-stacktrace=never` に変更
9. `/actuator/**` を `WEBGOAT_ADMIN` ロール要求に制限
10. ファイルパスのカノニカル化（パストラバーサル対策）

---

**注意**: WebGoat は教育目的で意図的に脆弱に設計されているため、上記 CRITICAL 発見事項の多くはレッスンの一部です。本番環境に類似したシステムを構築する際は、これらのパターンを避けることが重要です！

:::

### 脅威インテリジェンスを加えるとレポートはどう変わるか

3 パターンの結果を並べると、追加のロジックが具体的に何を変えたかがわかります。

| 観点 | 素の AI | OWASP プレイブック | + 脅威インテリジェンス |
|---|---|---|---|
| 発見件数 | CRITICAL 3 / HIGH 7 / MEDIUM 12 | CRITICAL 3 / HIGH 6 / MEDIUM 4 | CRITICAL 5 / HIGH 15 |
| SSEM スコア | なし | 4.3 / 10 | 3.2 / 10 |
| CVE の優先度根拠 | なし | CVE 番号・CVSS スコア | KEV 登録・EPSS スコア付き |
| リスクチェーン数 | 0 | 3（チェーン A〜C） | 4（チェーン A〜D） |
| 最優先ファインディング | C-1 NoOpPasswordEncoder | F-01 NoOpPasswordEncoder | F-01 XStream RCE（KEV 登録・EPSS 0.94） |

注目すべき変化は 2 点です。

#### 最優先問題が変わった

素の AI もプレイブックも `NoOpPasswordEncoder`（平文パスワード保存）を Critical の筆頭に挙げていました。

しかし脅威インテリジェンスを加えると、XStream 1.4.5 の RCE（CVE-2021-39144）が筆頭になります。CISA KEV への登録と EPSS 94%という情報が加わることで、今すぐ実際に攻撃に使われる可能性が高いという軸で優先度が再評価されます。

#### チェーン D が新たに検出された

XStream の SSRF 脆弱性が AWS IMDSへの到達経路に繋がることが示されました。

これはコードの静的解析だけでは見えにくい問題で、「この CVE を持つコンポーネントがクラウド環境のトラストバウンダリにどう影響するか」という脅威インテリジェンス側の文脈があって初めて検出できます。

## まとめ

AI にセキュリティレビューを頼む場合、素のプロンプトで依頼するだけでは重要な問題を一通り列挙してくれる程度にとどまります。
プレイブックを使うと、意図された脆弱性と意図されていない問題の区別、複数問題が組み合わさるリスクチェーンの特定、OWASP 標準への紐づけ、定量的なスコアリングといった専門家らしい視点が加わります。

OWASP Secure Agent Playbook はその差分を埋めるための仕組みで、Claude Code のプラグインとして簡単に導入できます。コードのセキュリティレビューを AI に任せるなら、素で頼むのではなく体系だったプレイブックを使うことを強くお勧めします。
AI エージェントの活用が広がるにつれて、このようなプレイブックの重要性はますます高まっていくでしょう。

この記事がどなたかの役に立つと嬉しいです。
