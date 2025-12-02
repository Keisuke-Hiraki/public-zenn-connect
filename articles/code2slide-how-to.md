---
title: "Claude Code にソースコードを読ませ、Nano Banana Pro でスライドの画像を生成する効果的なプロンプトを考えてみる"
emoji: "📄"
type: "tech"
topics: ["画像生成", "gemini", "chatgpt", "claudecode", "nanobanana"]
published: true
---

こんにちは、CSC の平木です！

普段、業務の中でスライド作成を行うことが多いためスライド作成の効率を上げられる方法を探しているのですが、以前 X を眺めていたところ、このようなポストを拝見しました。

https://x.com/nukonuko/status/1995063528013861050?s=20

これを見かけ、ぜひ ~~パク~~ 参考にしてみたいと思い、  
どのようなプロンプトにすればソースコードのみで一貫性のあるスライド資料を生成できるかを今回考えてみました。

今回は、ポストでも言及されていた、Claude Code にソースコードのプロジェクト全体を読み込ませ、Nano Banana Pro に渡すプロンプトを生成し、最終的にスライド資料全体を Nano Banana Pro のみで作っていきたいと思います。

検証として弊社が OSS として公開している Kong Gateway の更なるセキュリティ向上のため API Security 機能を Gateway に追加するための Kong プラグイン、[sasanka](https://github.com/cybersecuritycloud/sasanka/blob/master/README.ja.md) のコードを活用してみました。

https://github.com/cybersecuritycloud/sasanka

## Nano Banana Pro のプロンプトの最適化

まず Gemini 3 Pro Image (通称 Nano Banana Pro) にどういった点を気を付けるとより効果的に理想の画像を生成してくれるのかについて調べてみました。

こちらは既に回答があり、以下の Google の公式ブログで解説されています。

https://blog.google/products/gemini/prompting-tips-nano-banana-pro/

どんな要素をプロンプトに含むと良いかについては冒頭で言及されており、以下 6 つが挙げられています。

- 主題： どんな画像なのかの鮮明で具体的なオブジェクトの情報
- 構図： どのようなフレーミングなのかの指示
- アクション： その画像の中でどんな動きが起きているかの情報
- 場所： どのようなシーンなのかの物理・心情における背景
- スタイル： どのような美的感覚のビジュアルかの情報
- 編集手段： 既存の画像を修正したい場合は修正したいものの具体的な変更内容

![](/images/code2slide-how-to_2025-12-02-11-00-27.png)

ではこれをスライド生成に置き換えて考えてみると以下のようになるのではないかと考えました。

- 主題： スライドにどんな情報を割り当てたいかの明確な情報
- 構図： 文章と図や表との配置
- アクション： スライドをどんなストーリーにするかの情報
- 場所： どのようなペルソナに向けたスライドなのかの情報
- スタイル： スライドの配色やフォントやサイズ
- 編集手段： 既存のスライドを修正したい場合は修正したいものの具体的な変更内容

![](/images/code2slide-how-to_2025-12-02-11-00-57.png)

## やってみた

この考えをもとに Gemini (Gemini 3 Pro) と ChatGPT (GPT5.1) を活用しプロンプトを 2 パターン生成してみました。

![](/images/code2slide-how-to_2025-12-02-09-58-08.png)

また README から簡単に推測できてしまうことを避けるため、今回は意図的に README などのドキュメントの類はソースコードのフォルダからは削除してみました。

そのため純粋にソースコードのみからスライドを生成してもらいます。

### Claude Code に渡すプロンプト

Gemini と ChatGPT には基本的には以下のプロンプトを与えました。
ただしヒアリング内容によって変わった部分があるため両者のプロンプトの方針が少しずれている面もあります。

```
生成 AI にアプリケーションのソースコードを参照させ、画像生成 AI でそのソースコードに関するスライド資料を生成してもらうためのプロンプトを生成してください。
必要に応じてヒアリングもしてください。
```

得られた気付きとして、両者とも構造化されたアウトプットを生成するように指示している点が挙げられます。

やはり AI が読み取る以上、AI が理解しやすい方式で指示するほうが効率が良いのかなと思います。

#### Gemini

まずは Gemini が提案するプロンプトは以下でした。

```mk

---
# 役割
あなたは、ソースコードの内容を深く理解し、それをビジネスや技術チームに説明するための「説得力のあるスライド資料」を作成する熟練のドキュメンテーションエンジニアです。
画像生成 AI「Nano Banana Pro」に対し、**図解だけでなく、詳細な日本語の説明文を含んだスライド**を出力させるための高度なプロンプトを作成してください。

# 入力情報
1. **ターゲット**: [エンジニア、プロジェクトマネージャー]
   ※技術詳細を知りたいが、ビジネス価値も理解したい層。
2. **デザイン**: [外資系コンサル風、信頼感、プロフェッショナル]
   - 白背景に濃紺の文字、読みやすいサンセリフ体。
3. **ソースコード**:
{{ここにソースコードのフォルダパスを貼り付け}}

# 依頼内容
ソースコードを解析し、プロジェクトの全容が誰にでも伝わる**計 8〜10 枚のプレゼンテーション資料**の構成を考え、各スライドの「Nano Banana Pro 用プロンプト（英語）」を作成してください。
**「画像だけの雰囲気資料」ではなく、スライド内に意味のある日本語の文章（タイトル、箇条書き、説明文）が含まれるように指示してください。**

## スライド構成案（ストーリーライン）
以下の流れで構成してください。
1. **表紙**: アプリ名とサブタイトル。
2. **背景/課題**: なぜこのコードが必要なのか（現状の課題）。
3. **ソリューション概要**: アプリが何をするものか（解決策）。
4. **主要機能一覧**: 機能の箇条書き。
5. **アーキテクチャ図**: システム構成と技術スタック。
6. **詳細ロジック (1)**: コアとなるアルゴリズムや処理フローの図解と説明。
7. **詳細ロジック (2)**: データの流れや DB 構造の図解と説明。
8. **ユースケース**: ユーザーがどう使うかのフロー。
9. **今後の展望**: 拡張性や将来のロードマップ。
10. **まとめ**: プロジェクトの価値の再提示。

# プロンプト作成ルール（Nano Banana Pro 最適化：テキスト重視版）
Nano Banana Pro に対して、レイアウトと日本語テキストの内容を厳密に指示するため、以下のフォーマットを使用してください。

**プロンプト構造:**
`[Layout Strategy], [Visual Content], [Japanese Text Content], [Style & Design], [High Quality Tags]`

**記述のポイント（ここが重要です）:**
1.  **Layout Strategy (レイアウト)**:
    - 画像と文字が重ならないよう、領域を分ける指示を入れる。
    - 例: "Split screen layout, visual diagram on the left, text description on the right", "Two-column slide layout".
2.  **Japanese Text Content (テキスト内容)**:
    - スライドに記載すべき具体的な日本語を指示する。
    - **Title**: スライドのヘッダー。
    - **Bullet points**: コードから抽出した重要なポイント（3 行程度）。
    - 記述例: `Text details: Title "システム構成図", Bullet points "・ React によるフロントエンド\n ・ Go 言語のバックエンド API\n ・ AWS 上のマイクロサービス"`.
3.  **Visual Content (図解)**:
    - テキストの内容を補完する図（フローチャート、アイコン、UI モックアップ）。

# 出力フォーマット
---
## Slide [番号]: [日本語スライドタイトル]
- **スライドの狙い**: [このスライドで何を伝えるか]
- **Nano Banana Pro 用プロンプト**: [ここに英語プロンプトを記述] --ar 16:9
---
```

#### ChatGPT

続いて ChatGPT が提案するプロンプトは以下でした。

```mk

---

あなたは **企業向け技術資料の専門スライドデザイナー兼ソフトウェアアーキテクト** です。
これから渡すアプリケーションのソースコード（またはリポジトリ構成）を解析し、
**Nano Banana Pro で “スライド画像＋スライド内テキスト内容” を日本語で生成するためのプロンプトセット** を作成してください。

---

## ■ 厳守すべき制約（最優先ルール）

* **ソースコードやリポジトリ構成から読み取れない内容は、一切推測・創作しないこと。**
* 想像・類推・一般論による補完であっても、ソースコードから明確に根拠が取れない情報は
  **スライド内容に含めないこと。**
* 必要な情報がソースコードから読み取れない場合、その情報に対応するスライドは
  **生成しない** か、**JSON 上で「情報不足のためこのスライドは生成しない」と明示** してください。
* 「改善点」「ロードマップ」なども、**実装やコメントから明確に読み取れない限り生成しない** こと。
  （一般論で埋めない）

---

## ■ 解析タスク

渡されたソースコードから、**コードから客観的に読み取れる範囲のみ** を使って、以下を整理してください：

1. システム概要（目的・ユースケース）
2. 技術スタック
3. アーキテクチャ構成
4. 主要ユースケース／機能
5. 処理フロー
6. データモデル
7. セキュリティ・例外処理
8. 今後の改善点（※コード・コメント等から客観的に読み取れる場合に限る）

※ 各項目について、**コードから根拠が取れない場合は「情報不足」扱いとし、その項目を前提とするスライドは生成しないか、スキップしたことを JSON 上で明記してください。**

---

## ■ スライド構成（10 枚以上を上限とするガイドライン）

以下はあくまで「候補構成」です。
**ソースコードから十分な情報が読み取れるスライドのみ生成してください。**
情報不足の場合、そのスライドはスキップしてください。

1. タイトルスライド
2. システム概要
3. 特徴・ユースケース
4. 全体アーキテクチャ
5. コンポーネント構成
6. 処理フロー
7. データモデル
8. 代表機能
9. 非機能要件
10. 改善点・ロードマップ

※ 11 枚目以降の追加スライドも、**ソースコードから根拠がある場合のみ** 生成してください。
※ 結果としてスライド枚数が 10 枚未満になっても構いません。**正確性を優先** してください。

---

## ■ 各スライドで生成すべき内容

### ① スライド本文テキスト（日本語）

* 説明文
* 箇条書き
* 図表の説明文
* ペルソナに応じたトーン調整（デフォルト：エンジニア向け）

※ 各文・各箇条書きは、対応する内容がソースコードから実際に確認できる場合にのみ記述してください。

---

### ② Nano Banana Pro 用「画像生成プロンプト（日本語＋英語）」

スライド画像内の文字は **すべて日本語で生成させる** ように、明確に指示してください。

#### ● スライドの見た目

* 16:9 横長スライド
* 白背景 + ブルーアクセント
* カッチリした企業向けデザイン
* フラットアイコン・ボックス構成

#### ● 画像内テキスト（必ず日本語）

Nano Banana Pro が誤解しないよう、
**「画像内テキストはすべて日本語で描画すること」** を明記し、
スライドに描画するテキストを行単位で指定してください。

例：

画像内テキストはすべて日本語で描画すること。

タイトル（日本語）:
「システム全体アーキテクチャ」

本文箇条書き（日本語）:
- Web フロントから API へのデータフロー
- 認証サービスとの連携
- DB アクセス概要

補足説明（日本語）:
「このスライドはアーキテクチャの全体像を示します」

上記の各テキスト内容も、ソースコードから読み取れる事実に基づくものだけを記述してください。

#### ● 図表構成

* ボックス図
* アーキテクチャ図
* フローチャート
* ER 図（抽象化）
* UI イメージ（必要に応じて）

※ ソースコードの生文字列（コード・シークレット等）は絶対に描画しない
※ 会社名・サービス名は指定された場合のみ使用し、指定がなければ抽象名（「本システム」など）を使用

---

## ■ 出力形式

以下の JSON 形式で出力してください。
**実際に生成するスライドのみ `slides` に含め、情報不足でスキップしたスライドは含めないか、別途コメントとして明示してください。**

{
  "slides": [
    {
      "id": 1,
      "title": "スライドタイトル",
      "text_content_ja": "このスライドの本文テキスト（段落＋箇条書き）。すべてソースコードから読み取れる事実に基づくこと。",
      "image_prompt_ja": "Nano Banana Pro に渡すスライド画像生成指示。画像内テキストを必ず日本語で描画するよう明示し、内容はソースコードから読み取れる事実のみに基づいて詳細に記述する。",
      "image_prompt_en": "Same as image_prompt_ja translated into English, explicitly instructing that all in-image text must be in Japanese and all content must be strictly based on facts observable in the source code, with no speculative or invented information."
    }
    // Slide 2 以降も同様。情報不足で生成しないスライドはここに含めない。
  ],
  "notes": "もし想定されるスライド構成のうち、情報不足のため生成しなかったものがあれば、そのスライド名と『ソースコードから十分な情報が得られないため生成しなかった』旨をここに列挙する。"
}

---

## ■ 入力欄

以下に解析対象のソースコードまたはリポジトリ構成を貼り付けてください：

{{ソースコードのフォルダパスを貼る}}

---

## ■ 特殊ルール（再掲）

* **ソースコードから読み取れない不正確な情報は、一切生成しないこと。**
* 情報が足りない箇所について、推測や一般論で補わないこと。
* 情報不足のスライドは無理に作らず、「生成しない」か「スキップした」旨を JSON 上で明示すること。
* 画像内テキストはすべて日本語で描画するよう、毎スライドの `image_prompt_ja` / `image_prompt_en` に明記すること。

---

```

### Nano Banana Pro に渡すプロンプト

ソースコードと与えたプロンプトをもとに Claude Code が出力した中間プロンプトも掲載しておきます。

こちらは実際に使う際には、ソースコードによって異なるためあまり参考にしなくても良さそうです。

画像生成を促しやすいように冒頭に「指示に従いそれぞれの画像を生成してください。」だけ追加しています。

#### Gemini のプロンプトをもとに生成されたプロンプト

```mk
指示に従いそれぞれの画像を生成してください。

---
  Slide 1: 表紙

  - スライドの狙い: プロジェクト名と概要を印象的に提示し、聴衆の関心を引く
  - Nano Banana Pro 用プロンプト:

  Professional business presentation title slide, modern minimalist design, white background with dark     
  navy accents. Text details: Main title "Sasanka (サザンカ)", Subtitle "Kong API Gateway
  セキュリティプラグイン統合ソリューション", Version "v2.0.0", elegant sans-serif typography, clean        
  corporate aesthetic, subtle gradient effect on title, professional consulting firm style, ultra high     
  quality, 8k resolution --ar 16:9

  ---
  Slide 2: 背景と課題

  - スライドの狙い: API セキュリティの現状課題を明確化し、ソリューションの必要性を訴求
  - Nano Banana Pro 用プロンプト:
  Split screen professional slide layout, white background. Left side: warning icons and security
  threat symbols (shield with crack, malware icon, injection attack symbol) in red and orange gradient.    
   Right side: Japanese text content. Text details: Title "解決すべきセキュリティ課題", Bullet points      
  "・ SQL インジェクション、XSS 等の脆弱性攻撃の増加\n ・ CORS 設定ミスによるデータ漏洩リスク\n ・不正なパラメ    
  ータやヘッダーによる攻撃\n ・リアルタイム検知と防御の必要性\n ・ API Gateway 層での包括的な防御が不可欠",    
   dark navy text, clean sans-serif font, professional consulting presentation style, high quality --ar    
   16:9

  ---
  Slide 3: ソリューション概要

  - スライドの狙い: Sasanka が提供する価値とアプローチを簡潔に伝える
  - Nano Banana Pro 用プロンプト:
  Two-column professional slide, white background. Left side: shield icon with checkmarks, security        
  layers illustration in blue and green gradient. Right side: Japanese text description. Text details:     
  Title "Sasanka - 統合セキュリティソリューション", Subtitle "Kong API Gateway 向け包括的防御システム",     
  Description "Kong
  API ゲートウェイのプラグインアーキテクチャを活用し、13 種類の専門プラグインで多層防御を実現。リクエスト    
  /レスポンスの各フェーズで脅威を検知・ブロックし、API エコシステム全体を保護します。", bullet point        
  "・ Lua 言語による高速処理\n ・拡張可能なプラグイン設計\n ・リアルタイム検知とブロック", dark navy text,     
  professional style, high detail --ar 16:9

  ---
  Slide 4: 主要機能一覧

  - スライドの狙い: 13 個のプラグイン機能を整理して提示し、包括性を訴求
  - Nano Banana Pro 用プロンプト:
  Professional feature list slide, white background, grid layout with icons. Text details: Title
  "13 の専門プラグインによる多層防御", Four categories with icons: Category 1 "攻撃検知・防御"
  "・ libinjection - SQLi/XSS 検知\n ・ pm - パターンマッチング\n ・ magika - ファイル検証", Category 2
  "アクセス制御" "・ allowkey - パラメータホワイトリスト\n ・ strictparameter - 厳格な型検証\n ・ ua-filter     
  - User-Agent 制御", Category 3 "プロトコル制御" "・ CORS - クロスオリジン制御\n ・ safehost -
  ホスト検証\n ・ saferedirect - リダイレクト保護\n ・ clickjacking - UI 攻撃防御", Category 4 "監視・運用"     
  "・ telemetry - メトリクス収集\n ・ std-logger - ログ出力\n ・ detecthandling - 検知処理\n ・ core -
  プラグイン基盤", clean icons in blue gradient, dark navy text, consulting style, high quality --ar       
  16:9

  ---
  Slide 5: アーキテクチャ図

  - スライドの狙い: システム構成と技術スタックを視覚的に説明
  - Nano Banana Pro 用プロンプト:
  Technical architecture diagram slide, white background. Visual: layered architecture diagram showing     
  Kong Gateway at center, with plugin layers around it. Text details: Title "システムアーキテクチャ",      
  Architecture layers from top to bottom: "クライアント層" → "Kong API Gateway" → "Sasanka プラグイン層     
  (ssk-core 基盤)" → "アップストリームサービス", Side annotation "技術スタック:\n ・言語:
  Lua\n ・プラットフォーム: Kong Gateway\n ・バージョン: 2.0.0\n ・プラグイン数: 13\n ・処理フェーズ:
  access/header_filter/body_filter/log", Flow arrows in blue, component boxes in light blue and white,     
  dark navy text, professional technical diagram style, high detail --ar 16:9

  ---
  Slide 6: 詳細ロジック (1) - コアフレームワーク

  - スライドの狙い: ssk-core の拡張可能な設計とプラグイン実行フローを解説
  - Nano Banana Pro 用プロンプト:
  Split technical slide, white background. Left side: flowchart showing plugin lifecycle (init_worker →    
   access → header_filter → body_filter → log phase). Right side: Japanese explanation. Text details:      
  Title "コアフレームワーク (ssk-core)", Subtitle "拡張可能なプラグイン実行基盤", Description text         
  "各プラグインは core モジュールを継承し、ハンドラー関数を登録。Kong のリクエスト処理フローの各フェーズで    
  順次実行され、検知時は即座にブロック可能。", Key features "・ OOP 風の継承メカニズム 
  (extend)\n ・ハンドラー登録システム\n ・グローバル/ローカル実行モード\n ・パフォーマンス最適化機能",        
  Code snippet example in small font "function _M:add_handler(cat, h, ...)", flowchart in blue 
  gradient, dark navy text, technical presentation style, high quality --ar 16:9

  ---
  Slide 7: 詳細ロジック (2) - 検知エンジン

  - スライドの狙い: libinjection を例に、脅威検知のメカニズムを説明
  - Nano Banana Pro 用プロンプト:
  Two-column technical slide, white background. Left side: data flow diagram showing request → decode →    
   libinjection check → fingerprint → block/allow decision. Right side: detailed explanation. Text
  details: Title "脅威検知エンジンの仕組み", Example "libinjection プラグイン", Process steps "1.
  リクエストパラメータの抽出\n2. URL/Base64 等のデコード処理\n3. libinjection.sqli() / .xss()
  による解析\n4. 検知時はフィンガープリント記録\n5. エラーコード返却とブロック実行", Detection codes       
  "・ 1301: SQL Injection 検知\n ・ 1302: XSS Attack 検知", Code example "local d, fingerprint =
  libinjection.sqli(subj)\nif d then return detect_code end", diagram arrows in red and blue, dark navy    
   text, security-focused design, professional style, high detail --ar 16:9

  ---
  Slide 8: ユースケース

  - スライドの狙い: 実際の利用シーンをフロー図で示し、導入イメージを具体化
  - Nano Banana Pro 用プロンプト:
  User flow diagram slide, white background. Visual: numbered workflow from 1 to 5 with icons. Text        
  details: Title "典型的なユースケース", Subtitle "E コマースサイトの決済 API 保護", Flow steps with
  icons: "1. クライアントから決済リクエスト受信" → "2. allowkey: 許可パラメータのみ通過" → "3.
  libinjection: SQLi/XSS 検査" → "4. strictparameter: 型・形式検証" → "5. telemetry:
  メトリクス記録しつつ転送", Side note
  "検知時の動作:\n ・即座にエラーレスポンス返却\n ・詳細ログを std-logger で出力\n ・ detecthandling
  で後続処理制御\n ・アップストリームへは到達させない", workflow arrows in green and blue gradient,
  icons in modern flat style, dark navy text, consulting presentation aesthetic, high quality --ar 16:9    

  ---
  Slide 9: 今後の展望

  - スライドの狙い: 拡張性と将来のロードマップを示し、継続的な価値を訴求
  - Nano Banana Pro 用プロンプト:
  Roadmap and future vision slide, white background. Visual: upward trending arrow with milestone
  markers. Text details: Title "拡張性と今後の展望", Current status "v2.0.0 -
  13 プラグインによる包括防御を実現", Future roadmap "短期 (Q1-Q2):\n ・ AI/ML
  による異常検知プラグイン\n ・ Rate limiting 統合\n ・ GraphQL 対応強化", Mid-term "中期 (Q3-Q4):\n ・ Zero     
  Trust Architecture 対応\n ・ Kubernetes native 統合\n ・マルチクラウド対応", Long-term
  "長期:\n ・自動脅威インテリジェンス連携\n ・プラグインマーケットプレイス\n ・ SaaS 版提供", Extension note    
   "プラグインアーキテクチャ:\n 新たなセキュリティ要件にも\n プラグイン追加で柔軟に対応可能", timeline       
  visualization in blue gradient, milestone icons, dark navy text, strategic presentation style, high      
  detail --ar 16:9

  ---
  Slide 10: まとめ

  - スライドの狙い: プロジェクトの価値を再提示し、行動喚起で締めくくる
  - Nano Banana Pro 用プロンプト:
  Professional closing slide, white background with subtle gradient. Visual: centered shield icon with     
  checkmark, surrounded by key benefit badges. Text details: Title "Sasanka がもたらす価値", Three key     
  benefits in boxes: Box 1 "包括的な防御" "13 種類のプラグインで\nAPI 層の多層防御を実現", Box 2
  "高いパフォーマンス" "Lua 実装による低レイテンシ\n リアルタイム検知・ブロック", Box 3 "拡張性と柔軟性"     
  "プラグイン追加で\n 新たな脅威にも対応可能", Bottom section "導入メリット:\n ・開発生産性の向上 -
  セキュリティコードの分離\n ・運用コスト削減 - 統合管理による効率化\n ・コンプライアンス対応 -
  監査証跡の自動記録", Call to action "GitHub: github.com/your-repo/sasanka", benefit boxes in light       
  blue, shield icon in blue gradient, dark navy text, professional consulting summary style, high
  quality --ar 16:9

  ---
```

#### ChatGPT のプロンプトをもとに生成されたプロンプト

```json
指示に従いそれぞれの画像を生成してください。

 {
    "slides": [
      {
        "id": 1,
        "title": "Sasanka - Kong API ゲートウェイセキュリティプラグイン集",
        "text_content_ja": "Sasanka（SSK）は、CyberSecurityCloud 社が開発した Kong API
  Gateway 用のセキュリティプラグイン集です。\n\n 基本情報：\n- バージョン: 2.0.0\n- 実装言語: Lua\n-
  ライセンス: Apache 2.0\n- パッケージ形式: LuaRocks\n\n 本システムは、API Gateway 層でのセキュリティ対策    
  を包括的に提供し、SQL インジェクション、XSS、CORS、クリックジャッキングなど多様な脅威に対応します。",     
        "image_prompt_ja":
  "画像内テキストはすべて日本語で描画すること。\n\n16:9 横長の企業向けプレゼンテーションスライド。白背景    
  にブルーアクセント。フラットデザイン。\n\n タイトル（画面上部、大きく）:\n「Sasanka」\n「Kong
  API ゲートウェイセキュリティプラグイン集」\n\n サブタイトル（中央上部）:\n「バージョン
  2.0.0」\n\n 主要情報（中央、3 列のボックス）:\n 左ボックス:\n「実装言語」\n「Lua」\n\n 中央ボックス:\n「     
  開発元」\n「CyberSecurityCloud」\n\n 右ボックス:\n「ライセンス」\n「Apache
  2.0」\n\n 下部（箇条書き）:\n「✓ Kong API Gateway 用プラグイン」\n「✓ 包括的なセキュリティ対策」\n「✓      
  LuaRocks パッケージ形式」\n\n ロゴやアイコンは抽象的なセキュリティシールドのイメージを使用。",
        "image_prompt_en": "All in-image text MUST be in Japanese.\n\n16:9 landscape corporate
  presentation slide. White background with blue accents. Flat design.\n\nTitle (top,
  large):\n「Sasanka」\n「Kong API ゲートウェイセキュリティプラグイン集」\n\nSubtitle
  (center-top):\n「バージョン 2.0.0」\n\nMain information (center, 3 column boxes):\nLeft
  box:\n「実装言語」\n「Lua」\n\nCenter box:\n「開発元」\n「CyberSecurityCloud」\n\nRight
  box:\n「ライセンス」\n「Apache 2.0」\n\nBottom (bullet points):\n「✓ Kong API
  Gateway 用プラグイン」\n「✓ 包括的なセキュリティ対策」\n「✓ LuaRocks パッケージ形式」\n\nUse abstract      
  security shield imagery for logo/icons. All content strictly based on source code analysis."
      },
      {
        "id": 2,
        "title": "システム概要",
        "text_content_ja": "Sasanka は、Kong API
  Gateway のプラグインシステムを活用したセキュリティソリューションです。\n\n システムの目的：\n-
  API 層での包括的なセキュリティ対策\n- 入力検証とインジェクション攻撃の防御\n-
  セキュリティヘッダの適切な設定\n- リアルタイムな脅威検知とハンドリング\n\n アーキテクチャの特徴：\n-      
  共通コア（ssk-core）による統一的な実装基盤\n- プラグイン単位での機能分離\n- Kong
  API ゲートウェイのライフサイクルフェーズに対応\n- 柔軟な設定とカスタマイズ\n\nLua で実装され、Kong API     
  Gateway のネイティブなプラグイン機構として動作します。",
        "image_prompt_ja": "画像内テキストはすべて日本語で描画すること。\n\n16:9 横長の企業向けプレゼン     
  テーションスライド。白背景にブルーアクセント。\n\n タイトル（上部）:\n「システム概要」\n\n 中央（2 列構     
  成）:\n 左列「システムの目的」ボックス:\n「• API 層でのセキュリティ対策」\n「•
  入力検証とインジェクション防御」\n「• セキュリティヘッダ設定」\n「•
  リアルタイム脅威検知」\n\n 右列「アーキテクチャ特徴」ボックス:\n「• 共通コア（ssk-core）基盤」\n「•       
  プラグイン単位の機能分離」\n「• Kong ライフサイクル対応」\n「•
  柔軟な設定・カスタマイズ」\n\n 下部（強調ボックス）:\n「Lua 実装 × Kong API
  Gateway ネイティブプラグイン」\n\n シンプルなアイコンとボックス構成で見やすく。",
        "image_prompt_en": "All in-image text MUST be in Japanese.\n\n16:9 landscape corporate
  presentation slide. White background with blue accents.\n\nTitle (top):\n「システム概要」\n\nCenter      
  (2 columns):\nLeft column「システムの目的」box:\n「• API 層でのセキュリティ対策」\n「•
  入力検証とインジェクション防御」\n「• セキュリティヘッダ設定」\n「• リアルタイム脅威検知」\n\nRight      
  column「アーキテクチャ特徴」box:\n「• 共通コア（ssk-core）基盤」\n「• プラグイン単位の機能分離」\n「•    
   Kong ライフサイクル対応」\n「• 柔軟な設定・カスタマイズ」\n\nBottom (emphasis box):\n「Lua 実装 × Kong    
   API Gateway ネイティブプラグイン」\n\nSimple icons and box composition for clarity. All content
  strictly based on source code."
      },
      {
        "id": 3,
        "title": "全体アーキテクチャ",
        "text_content_ja": "Sasanka は、Kong API Gateway のプラグインアーキテクチャに組み込まれ、リクエス    
  ト・レスポンスの各フェーズで動作します。\n\n コンポーネント構成：\n1. ssk-core（共通基盤）\n   -
  core.lua: プラグインベースクラス\n   - request.lua: リクエスト処理\n   - response.lua:
  レスポンス処理\n   - params.lua: パラメータ処理\n   - decoder.lua: デコード処理\n   -
  lib/matcher.lua: パターンマッチング\n   - lib/utils.lua: ユーティリティ関数\n\n2.
  各セキュリティプラグイン\n   - handler.lua: プラグイン処理ロジック\n   - schema.lua:
  設定スキーマ定義\n   - daos.lua: データアクセスオブジェクト\n\n プラグインは共通コアを継承し、統一的な    
  インターフェースで実装されています。",
        "image_prompt_ja": "画像内テキストはすべて日本語で描画すること。\n\n16:9 横長の企業向けプレゼン     
  テーションスライド。白背景にブルーアクセント。アーキテクチャ図。\n\n タイトル（上部）:\n「全体アーキテ    
  クチャ」\n\n 中央（階層構造図）:\n 最上部層:\n「Kong API Gateway」（大きなボックス）\n\n 中間層（Kong の     
  内部）:\n「SSK 共通基盤（ssk-core）」ボックス\n 内部テキスト:\n「core / request / response」\n「params     
  / decoder / matcher」\n\n 下層（プラグイン群、6 個の小ボックスを横並び）:\n「ua-filter」「libinjection     
  」「cors」\n「strictparameter」「pm」「他 7 個」\n\n 各プラグインボックス内:\n「handler.lua」\n「schema.    
  lua」\n\n 矢印で継承関係を表現（下層プラグイン →
  中間層コア）\n\n 右下に補足:\n「統一的なインターフェース」",
        "image_prompt_en": "All in-image text MUST be in Japanese.\n\n16:9 landscape corporate
  presentation slide. White background with blue accents. Architecture diagram.\n\nTitle
  (top):\n「全体アーキテクチャ」\n\nCenter (layered structure diagram):\nTop layer:\n「Kong API
  Gateway」(large box)\n\nMiddle layer (inside Kong):\n「SSK 共通基盤（ssk-core）」box\nInternal
  text:\n「core / request / response」\n「params / decoder / matcher」\n\nBottom layer (plugin cluster,    
   6 small boxes
  horizontally):\n「ua-filter」「libinjection」「cors」\n「strictparameter」「pm」「他 7 個」\n\nInside      
  each plugin box:\n「handler.lua」\n「schema.lua」\n\nArrows showing inheritance (bottom plugins →        
  middle core)\n\nBottom-right note:\n「統一的なインターフェース」\n\nAll content strictly based on        
  source code architecture."
      },
      {
        "id": 4,
        "title": "セキュリティプラグイン一覧",
        "text_content_ja": "Sasanka には 13 個のセキュリティプラグインが含まれています。各プラグインは独立    
  して有効化でき、組み合わせて使用できます。\n\n 入力検証系：\n- ssk-strictparameter:
  パラメータの型・範囲・必須チェック\n- ssk-allowkey: 許可されたキーのみ受け付け\n- ssk-pm:
  カスタムパターンマッチング\n\n インジェクション対策：\n- ssk-libinjection:
  SQL インジェクション・ XSS 検知\n\nCORS ・ヘッダ制御：\n- ssk-cors: CORS ポリシー設定と検証\n-
  ssk-clickjacking: X-Frame-Options ヘッダ設定\n\n ホスト・リダイレクト検証：\n- ssk-safehost:
  Host ヘッダ検証\n- ssk-saferedirect: 安全なリダイレクト検証\n\n フィルタリング：\n- ssk-ua-filter:
  User-Agent フィルタリング\n- ssk-magika: ファイルタイプ検証\n\n 運用支援：\n- ssk-telemetry:
  パフォーマンステレメトリ収集\n- ssk-detecthandling: 検知時のカスタムレスポンス\n- ssk-std-logger:        
  標準ロガー",
        "image_prompt_ja": "画像内テキストはすべて日本語で描画すること。\n\n16:9 横長の企業向けプレゼン     
  テーションスライド。白背景にブルーアクセント。\n\n タイトル（上部）:\n「セキュリティプラグイン一覧（13    
  個）」\n\n 中央（4 列のカテゴリボックス）:\n\n 左列「入力検証」:\n「strictparameter」\n「allowkey」\n「p    
  m」\n\n 中左列「インジェクション対策」:\n「libinjection」\n\n 中右列「CORS ・ヘッダ」:\n「cors」\n「clic    
  kjacking」\n\n「ホスト・リダイレクト」:\n「safehost」\n「saferedirect」\n\n 右列「フィルタリング」:\n     
  「ua-filter」\n「magika」\n\n「運用支援」:\n「telemetry」\n「detecthandling」\n「std-logger」\n\n 下部    
  （強調テキスト）:\n「各プラグイン独立動作 | 柔軟な組み合わせ可能」",
        "image_prompt_en": "All in-image text MUST be in Japanese.\n\n16:9 landscape corporate
  presentation slide. White background with blue accents.\n\nTitle
  (top):\n「セキュリティプラグイン一覧（13 個）」\n\nCenter (4 category columns with boxes):\n\nLeft        
  column「入力検証」:\n「strictparameter」\n「allowkey」\n「pm」\n\nCenter-left
  column「インジェクション対策」:\n「libinjection」\n\nCenter-right column「CORS ・ヘッダ」:\n「cors」\n    
  「clickjacking」\n\n「ホスト・リダイレクト」:\n「safehost」\n「saferedirect」\n\nRight
  column「フィルタリング」:\n「ua-filter」\n「magika」\n\n「運用支援」:\n「telemetry」\n「detecthandlin    
  g」\n「std-logger」\n\nBottom (emphasis text):\n「各プラグイン独立動作 |
  柔軟な組み合わせ可能」\n\nAll content strictly from source code plugin list."
      },
      {
        "id": 5,
        "title": "処理フロー（Kong ライフサイクル）",
        "text_content_ja": "Sasanka プラグインは、Kong API
  Gateway のリクエスト処理ライフサイクルの各フェーズで動作します。\n\n プラグインフェーズ：\n\n1.
  init_worker\n   - ワーカープロセス起動時に 1 回のみ実行\n   - グローバル初期化処理\n\n2. access\n   -      
  クライアントからのリクエスト受信後、アップストリームへ転送前\n   -
  入力検証、パラメータチェック、パターンマッチング実行\n   - 検知時はここでブロック可能\n\n3.
  header_filter\n   - アップストリームからレスポンスヘッダ受信時\n   -
  レスポンスヘッダの追加・変更\n\n4. body_filter\n   - アップストリームからレスポンスボディ受信時\n   -    
   レスポンスボディの検証・変更\n\n5. log\n   - トランザクション終了時\n   -
  ログ出力、テレメトリデータ送信\n\ncore.lua の preprocess() 関数が各フェーズで共通の前処理を行い、各プラ     
  グインのハンドラ関数を呼び出します。",
        "image_prompt_ja": "画像内テキストはすべて日本語で描画すること。\n\n16:9 横長の企業向けプレゼン     
  テーションスライド。白背景にブルーアクセント。フローチャート。\n\n タイトル（上部）:\n「処理フロー（Ko    
  ng ライフサイクル）」\n\n 中央（縦方向のフローチャート、5 ステップ）:\n\n ステップ 1 ボックス:\n「1.
  init_worker」\n「ワーカー起動時・初期化」\n\n↓ 矢印\n\n ステップ 2 ボックス（強調・青背景）:\n「2.
  access」\n「入力検証・パターンマッチ」\n「★検知時ブロック可能」\n\n↓
  矢印「アップストリームへ」\n\n ステップ 3 ボックス:\n「3. header_filter」\n「レスポンスヘッダ処理」\n\n↓    
   矢印\n\n ステップ 4 ボックス:\n「4. body_filter」\n「レスポンスボディ処理」\n\n↓
  矢印\n\n ステップ 5 ボックス:\n「5. log」\n「ログ・テレメトリ送信」\n\n 右側に補足:\n「core.lua
  preprocess()」\n「共通前処理実行」",
        "image_prompt_en": "All in-image text MUST be in Japanese.\n\n16:9 landscape corporate
  presentation slide. White background with blue accents. Flowchart.\n\nTitle
  (top):\n「処理フロー（Kong ライフサイクル）」\n\nCenter (vertical flowchart, 5 steps):\n\nStep 1
  box:\n「1. init_worker」\n「ワーカー起動時・初期化」\n\n↓ arrow\n\nStep 2 box (emphasized, blue
  background):\n「2. access」\n「入力検証・パターンマッチ」\n「★検知時ブロック可能」\n\n↓
  arrow「アップストリームへ」\n\nStep 3 box:\n「3. header_filter」\n「レスポンスヘッダ処理」\n\n↓
  arrow\n\nStep 4 box:\n「4. body_filter」\n「レスポンスボディ処理」\n\n↓ arrow\n\nStep 5 box:\n「5.       
  log」\n「ログ・テレメトリ送信」\n\nRight side note:\n「core.lua
  preprocess()」\n「共通前処理実行」\n\nAll content from Kong phase implementation in source code."        
      },
      {
        "id": 6,
        "title": "入力検証機能",
        "text_content_ja":
  "Sasanka は、リクエストの各パラメータに対して包括的な検証を実行します。\n\n 検証対象パラメータ：\n-        
  param_req_path: URL パス\n- param_req_query: クエリパラメータ\n- param_req_header: HTTP ヘッダ\n-
  param_req_body: リクエストボディ\n- param_req_cookie: Cookie\n- param_res_header: レスポンスヘッダ\n-    
   param_res_body: レスポンスボディ\n\nssk-strictparameter による厳格な検証：\n- type:
  データ型チェック（boolean, int, number, uuid, date, date-time, regex）\n- required:
  必須パラメータチェック\n- min/max: 値の範囲チェック（数値・文字列長）\n- pattern:
  正規表現パターンマッチング\n\nssk-allowkey によるホワイトリスト制御：\n-
  事前定義されたキーのみ受け付け\n- 予期しないパラメータを検知・ブロック\n\ndecoder.lua により、URL エン     
  コード等のデコード処理を行った上で検証を実行します。",
        "image_prompt_ja": "画像内テキストはすべて日本語で描画すること。\n\n16:9 横長の企業向けプレゼン     
  テーションスライド。白背景にブルーアクセント。\n\n タイトル（上部）:\n「入力検証機能」\n\n 左側（検証対    
  象リスト）:\n「検証対象パラメータ」\n「• URL パス」\n「• クエリパラメータ」\n「• HTTP ヘッダ」\n「•        
  リクエストボディ」\n「• Cookie」\n「•
  レスポンスヘッダ・ボディ」\n\n 右上（strictparameter ボックス）:\n「strictparameter 厳格な検証」\n「✓      
  type: データ型チェック」\n「  (boolean/int/number/uuid/date...)」\n「✓ required: 必須チェック」\n「✓     
  min/max: 範囲チェック」\n「✓ pattern: 正規表現」\n\n 右下（allowkey ボックス）:\n「allowkey
  ホワイトリスト制御」\n「✓ 許可キーのみ受付」\n「✓
  予期しないパラメータ検知」\n\n 下部（補足）:\n「decoder.lua: デコード後検証実行」",
        "image_prompt_en": "All in-image text MUST be in Japanese.\n\n16:9 landscape corporate
  presentation slide. White background with blue accents.\n\nTitle (top):\n「入力検証機能」\n\nLeft        
  side (validation targets list):\n「検証対象パラメータ」\n「• URL パス」\n「• クエリパラメータ」\n「•      
  HTTP ヘッダ」\n「• リクエストボディ」\n「• Cookie」\n「• レスポンスヘッダ・ボディ」\n\nRight top
  (strictparameter box):\n「strictparameter 厳格な検証」\n「✓ type: データ型チェック」\n「
  (boolean/int/number/uuid/date...)」\n「✓ required: 必須チェック」\n「✓ min/max: 範囲チェック」\n「✓      
  pattern: 正規表現」\n\nRight bottom (allowkey box):\n「allowkey ホワイトリスト制御」\n「✓
  許可キーのみ受付」\n「✓ 予期しないパラメータ検知」\n\nBottom (note):\n「decoder.lua:
  デコード後検証実行」\n\nAll features from strictparameter and allowkey handler code."
      },
      {
        "id": 7,
        "title": "インジェクション対策",
        "text_content_ja": "ssk-libinjection プラグインは、libinjection ライブラリを使用して SQL インジェク    
  ションと XSS 攻撃を検知します。\n\n 検知機能：\n- SQL インジェクション検知（libinjection.sqli）\n  -
  検知コード: 1301\n  - fingerprint（攻撃パターン）を詳細情報として記録\n\n-
  XSS（クロスサイトスクリプティング）検知（libinjection.xss）\n  - 検知コード: 1302\n  -
  fingerprint（攻撃パターン）を詳細情報として記録\n\n 検証対象：\n- req_path: URL パス全体\n- req_query:     
  クエリパラメータ全体\n- req_body: リクエストボディ全体\n-
  個別パラメータ（key 指定時）\n\n 検証方式：\n- デコード後の値に対して検証実行\n- 検知時は詳細情報（key,    
   value, decoded, fingerprint）を記録\n- タグによるカスタム分類が可能\n\nlibinjection ライブラリがロー     
  ドできない場合はエラーログを出力し、検証をスキップします。",
        "image_prompt_ja": "画像内テキストはすべて日本語で描画すること。\n\n16:9 横長の企業向けプレゼン     
  テーションスライド。白背景にブルーアクセント。\n\n タイトル（上部）:\n「インジェクション対策（libinjec    
  tion）」\n\n 中央上部（2 列ボックス）:\n 左ボックス「SQL インジェクション検知」:\n「検知コード:
  1301」\n「libinjection.sqli」\n「fingerprint 記録」\n\n 右ボックス「XSS 検知」:\n「検知コード:
  1302」\n「libinjection.xss」\n「fingerprint 記録」\n\n 中央下部（検証対象ボックス）:\n「検証対象」\n「•    
   URL パス全体（req_path）」\n「• クエリパラメータ全体（req_query）」\n「•
  リクエストボディ全体（req_body）」\n「•
  個別パラメータ（key 指定時）」\n\n 下部（処理フロー、横並び 3 ボックス）:\n「デコード処理」→「libinjectio    
  n 検証」→「検知詳細記録」\n\n 右下補足:\n「タグによるカスタム分類可能」",
        "image_prompt_en": "All in-image text MUST be in Japanese.\n\n16:9 landscape corporate
  presentation slide. White background with blue accents.\n\nTitle
  (top):\n「インジェクション対策（libinjection）」\n\nCenter-top (2 column boxes):\nLeft
  box「SQL インジェクション検知」:\n「検知コード:
  1301」\n「libinjection.sqli」\n「fingerprint 記録」\n\nRight box「XSS 検知」:\n「検知コード:
  1302」\n「libinjection.xss」\n「fingerprint 記録」\n\nCenter-bottom (validation targets
  box):\n「検証対象」\n「• URL パス全体（req_path）」\n「• クエリパラメータ全体（req_query）」\n「•
  リクエストボディ全体（req_body）」\n「• 個別パラメータ（key 指定時）」\n\nBottom (processing flow, 3      
  horizontal boxes):\n「デコード処理」→「libinjection 検証」→「検知詳細記録」\n\nBottom-right
  note:\n「タグによるカスタム分類可能」\n\nAll features from libinjection handler implementation."
      },
      {
        "id": 8,
        "title": "CORS ・セキュリティヘッダ制御",
        "text_content_ja": "ssk-cors と ssk-clickjacking プラグインにより、CORS ポリシーとセキュリティヘッ     
  ダを制御します。\n\nssk-cors 機能：\n\n 検証機能（block 有効時）：\n- Origin 検証（検知コード: 401）\n  -    
   allow_origins に含まれない Origin をブロック\n- Method 検証（検知コード: 402）\n  -
  allow_methods に含まれない HTTP メソッドをブロック\n- Header 検証（検知コード: 403）\n  - allow_headers に    
  含まれないヘッダをブロック\n\n レスポンスヘッダ設定（modify_response_header 有効時）：\n-
  Access-Control-Allow-Origin\n- Access-Control-Allow-Methods\n- Access-Control-Allow-Headers\n-
  Access-Control-Expose-Headers\n- Access-Control-Max-Age\n-
  Access-Control-Allow-Credentials\n\nssk-clickjacking 機能：\n- X-Frame-Options ヘッダの設定\n- クリック    
  ジャッキング攻撃対策\n\n 両プラグインとも header_filter フェーズでレスポンスヘッダを設定します。",
        "image_prompt_ja": "画像内テキストはすべて日本語で描画すること。\n\n16:9 横長の企業向けプレゼン     
  テーションスライド。白背景にブルーアクセント。\n\n タイトル（上部）:\n「CORS ・セキュリティヘッダ制御」    
  \n\n 左側（CORS ボックス）:\n「ssk-cors」\n\n「検証機能（block 時）」\n「✓ Origin 検証（401）」\n「✓
  Method 検証（402）」\n「✓ Header 検証（403）」\n\n「レスポンスヘッダ設定」\n「•
  Access-Control-Allow-Origin」\n「• Access-Control-Allow-Methods」\n「•
  Access-Control-Allow-Headers」\n「• Access-Control-Expose-Headers」\n「•
  Access-Control-Max-Age」\n「• Access-Control-Allow-Credentials」\n\n 右側（クリックジャッキングボック     
  ス）:\n「ssk-clickjacking」\n\n「X-Frame-Options 設定」\n「クリックジャッキング対策」\n\n 下部（補足）:    
  \n「header_filter フェーズで動作」",
        "image_prompt_en": "All in-image text MUST be in Japanese.\n\n16:9 landscape corporate
  presentation slide. White background with blue accents.\n\nTitle
  (top):\n「CORS ・セキュリティヘッダ制御」\n\nLeft side (CORS
  box):\n「ssk-cors」\n\n「検証機能（block 時）」\n「✓ Origin 検証（401）」\n「✓ Method 検証（402）」\n「✓    
   Header 検証（403）」\n\n「レスポンスヘッダ設定」\n「• Access-Control-Allow-Origin」\n「•
  Access-Control-Allow-Methods」\n「• Access-Control-Allow-Headers」\n「•
  Access-Control-Expose-Headers」\n「• Access-Control-Max-Age」\n「•
  Access-Control-Allow-Credentials」\n\nRight side (clickjacking
  box):\n「ssk-clickjacking」\n\n「X-Frame-Options 設定」\n「クリックジャッキング対策」\n\nBottom
  (note):\n「header_filter フェーズで動作」\n\nAll features from cors and clickjacking handler code."       
      },
      {
        "id": 9,
        "title": "検知・ハンドリング機構",
        "text_content_ja": "Sasanka は、統一的な検知データ構造とカスタマイズ可能なハンドリング機構を提供    
  します。\n\n 検知データ構造：\n```\n{\n  detect_code: 検知コード（整数）,\n  tags: タグ配列,\n
  details: {\n    key: パラメータキー,\n    value: 検知された値,\n    その他検知内容に応じた詳細情報\n     
   }\n}\n```\n\n 検知コード体系：\n- 200 台: パターンマッチ（ssk-pm）\n- 300 台:
  ホスト検証（ssk-safehost）\n- 400 台: CORS 検証（ssk-cors）\n- 700 台:
  User-Agent 検証（ssk-ua-filter）\n- 1300 台: libinjection（SQL/XSS）\n- 1500 台:
  リダイレクト検証（ssk-saferedirect）\n- 1800 台: 厳格なパラメータ検証（ssk-strictparameter）\n-
  2500 台: 許可キー検証（ssk-allowkey）\n\nssk-detecthandling 機能：\n- タグベースのフィルタ設定\n-
  カスタムステータスコード\n- カスタムレスポンスヘッダ\n- カスタムレスポンスボディ\n-
  遅延設定（delay）\n\ncommon.lua の on_detect() 関数が検知時のハンドリングを統括します。",
        "image_prompt_ja": "画像内テキストはすべて日本語で描画すること。\n\n16:9 横長の企業向けプレゼン     
  テーションスライド。白背景にブルーアクセント。\n\n タイトル（上部）:\n「検知・ハンドリング機構」\n\n 左    
  上（検知データ構造ボックス）:\n「検知データ構造」\n「• detect_code: 検知コード」\n「• tags:
  タグ配列」\n「• details: 詳細情報」\n「  - key, value,
  その他」\n\n 右上（検知コード体系ボックス）:\n「検知コード体系」\n「200:
  パターンマッチ（pm）」\n「300: ホスト検証（safehost）」\n「400: CORS（cors）」\n「700:
  User-Agent（ua-filter）」\n「1300: インジェクション（libinjection）」\n「1500:
  リダイレクト（saferedirect）」\n「1800: 厳格検証（strictparameter）」\n「2500:
  許可キー（allowkey）」\n\n 下部（detecthandling ボックス）:\n「ssk-detecthandling
  カスタムハンドリング」\n「✓ タグベースフィルタ」\n「✓ カスタムステータスコード」\n「✓
  カスタムヘッダ・ボディ」\n「✓ 遅延設定」\n\n 最下部:\n「common.lua on_detect() で統括」",
        "image_prompt_en": "All in-image text MUST be in Japanese.\n\n16:9 landscape corporate
  presentation slide. White background with blue accents.\n\nTitle
  (top):\n「検知・ハンドリング機構」\n\nTop-left (detection data structure
  box):\n「検知データ構造」\n「• detect_code: 検知コード」\n「• tags: タグ配列」\n「• details:
  詳細情報」\n「  - key, value, その他」\n\nTop-right (detection code system
  box):\n「検知コード体系」\n「200: パターンマッチ（pm）」\n「300: ホスト検証（safehost）」\n「400:        
  CORS（cors）」\n「700: User-Agent（ua-filter）」\n「1300: インジェクション（libinjection）」\n「1500:    
   リダイレクト（saferedirect）」\n「1800: 厳格検証（strictparameter）」\n「2500:
  許可キー（allowkey）」\n\nBottom (detecthandling box):\n「ssk-detecthandling
  カスタムハンドリング」\n「✓ タグベースフィルタ」\n「✓ カスタムステータスコード」\n「✓
  カスタムヘッダ・ボディ」\n「✓ 遅延設定」\n\nBottom:\n「common.lua on_detect() で統括」\n\nAll from        
  detection code constants and detecthandling handler."
      },
      {
        "id": 10,
        "title": "インストール・デプロイ",
        "text_content_ja":
  "Sasanka プラグインは、LuaRocks を使用してインストールします。\n\n インストール方法：\n\n1.
  libinjection ライブラリのインストール：\n   - install_libinjection.sh の実行\n   -
  ssk-libinjection プラグインの依存ライブラリ\n\n2. 全プラグインの一括インストール：\n   -
  install_all.sh の実行\n   - rocks ディレクトリ内の全.rock ファイルをインストール\n   -
  各プラグインは「sudo luarocks install」で個別インストール\n\n3. クイックスタート：\n   -
  quickstart.sh の実行\n   - tools/quickstart.py による自動セットアップ\n\n パッケージ形式：\n-
  LuaRocks 形式（.rockspec, .rock）\n- specs ディレクトリ: rockspec 定義ファイル\n- rocks ディレクトリ:        
  ビルド済みパッケージ\n\n バージョン管理：\n- VERSION ファイルに全体バージョン（2.0.0）を記録\n-
  各プラグインは個別にバージョン管理（例:
  ssk-ua-filter-2.0.0-1）\n\nKong 設定への組み込み後、各プラグインを有効化して使用します。",
        "image_prompt_ja": "画像内テキストはすべて日本語で描画すること。\n\n16:9 横長の企業向けプレゼン     
  テーションスライド。白背景にブルーアクセント。\n\n タイトル（上部）:\n「インストール・デプロイ」\n\n 中    
  央（3 ステップの縦フロー）:\n ステップ 1 ボックス:\n「1.
  libinjection インストール」\n「install_libinjection.sh」\n\n↓\n\n ステップ 2 ボックス:\n「2.
  全プラグイン一括インストール」\n「install_all.sh」\n「sudo luarocks
  install」\n\n↓\n\n ステップ 3 ボックス:\n「3. クイックスタート」\n「quickstart.sh」\n「tools/quickstart.    
  py」\n\n 右側（パッケージ形式ボックス）:\n「パッケージ形式」\n「• LuaRocks 形式」\n「•
  .rockspec 定義ファイル」\n「•
  .rock ビルド済みパッケージ」\n\n 下部（バージョン管理ボックス）:\n「バージョン管理」\n「全体:
  VERSION（2.0.0）」\n「個別: 各プラグイン独立管理」\n\n 最下部:\n「Kong 設定 → プラグイン有効化」",
        "image_prompt_en": "All in-image text MUST be in Japanese.\n\n16:9 landscape corporate
  presentation slide. White background with blue accents.\n\nTitle
  (top):\n「インストール・デプロイ」\n\nCenter (3-step vertical flow):\nStep 1 box:\n「1.
  libinjection インストール」\n「install_libinjection.sh」\n\n↓\n\nStep 2 box:\n「2.
  全プラグイン一括インストール」\n「install_all.sh」\n「sudo luarocks install」\n\n↓\n\nStep 3
  box:\n「3. クイックスタート」\n「quickstart.sh」\n「tools/quickstart.py」\n\nRight side (package
  format box):\n「パッケージ形式」\n「• LuaRocks 形式」\n「• .rockspec 定義ファイル」\n「•
  .rock ビルド済みパッケージ」\n\nBottom (version management box):\n「バージョン管理」\n「全体:
  VERSION（2.0.0）」\n「個別: 各プラグイン独立管理」\n\nBottom:\n「Kong 設定 → プラグイン有効化」\n\nAll    
   from install scripts and package structure in source."
      }
    ],
    "notes": "上記 10 枚のスライドは、すべて Sasanka プロジェクトのソースコードから直接読み取れる情報のみに    
  基づいて作成しました。以下の情報は、ソースコードから十分な根拠が得られなかったため、スライドには含め     
  ていません：\n\n- ユースケースや導入事例（コード内に記載なし）\n-
  性能指標やベンチマーク結果（テレメトリ収集機能はあるが、具体的な数値データなし）\n-
  他の WAF 製品との比較（コード内に記載なし）\n- 今後のロードマップや改善計画（コード内に記載なし）\n-       
  実際の攻撃パターンや検知事例（コード内に記載なし）\n\n すべてのスライド内容は、handler.lua、schema.lua    
  、core.lua、rockspec ファイル等のソースコードから客観的に確認できる事実のみで構成されています。"
  }
```

### 出来上がったスライド

#### Gemini のプロンプトをもとに生成されたスライド

@[speakerdeck](6cae7029515b42f19580cc3b532b3aca)

#### ChatGPT のプロンプトをもとに生成されたスライド

@[speakerdeck](01e714fcad7d4a38ab622b39278fc73a)

## 出力してみて分かった点

- スライド生成をさせる技術としては完璧に近い
- 完璧に近いからこそスライド構成のイメージやストーリーを明確にイメージし、生成 AI に指示する必要がある（今回は Claude Code）
- 生成 AI が読むからこそ JSON のような構造化データで指示をすることで AI にも理解しやすいように意図を人間から AI に伝えられる
- いきなり 100%のスライドは出力されないので、都度細かい指示を出すことで求める 100%の成果物が作れます

## おわりに

今回は、Nano Banana Pro にスライド資料を生成してもらうにあたってどんなプロンプトを与えるべきかを考えてみました。

ストーリー的には Gemini のほうが相手に伝えるということを明確に意図していたのかストーリーとして理解しやすかったですが、ヒアリングしていない項目だったため「今後の展望」などソースコードには記載されていない想像によるスライドが混入してしまいました。

ペルソナの指定が今回は両者ともにエンジニア向けだったためその観点から言うと本来は ChatGPT のプロンプトのほうが正確なのかなとも感じましたが、README をスライド化した感覚のためどの機能のどういう特徴があるかという部分にもう少し言及してくれると良かったのかなと感じました。

この記事がどなたかの役に立つと嬉しいです。