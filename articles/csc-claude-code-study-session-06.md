---
title: "[社内勉強会資料公開] Claude Code 入門 #6 — Agent Skillsで業務をテンプレ化する"
emoji: "📖"
type: "tech"
topics: ["claudecode", "aiエージェント", "社内勉強会"]
published: false
published_at: 2026-08-18 09:30
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

CSC社内で開催している「CloudFastener の TAM(テクニカルアカウントマネージャー)向けに、Claude Codeを初歩から実践まで学ぶ勉強会」の第6回資料です。前回はモデルとeffortの使い分けを扱い、タスクの性質に応じて思考力と速度・コストのバランスを調整する方法を学びました。

https://zenn.dev/cscloud_blog/articles/csc-claude-code-study-session-05

第6回は、Agent Skills(エージェントスキル)の仕組みを理解し、自分の定型業務を1つスキル化してみることがゴールです。

:::message
**この記事の3行まとめ**

- Agent Skillsは、特定の作業をするときだけClaude Codeに読み込ませる手順書であり、CLAUDE.mdとは「常に読み込むか、必要なときだけ読み込むか」で役割が分かれる
- descriptionの書き方がスキルの自動発動を左右するため、ユーザーが自然に使いそうな言い回しを複数含めておくとよい
- SKILL.mdは手書きにこだわらず、公式の`skill-creator`を使うと発動条件の作り込みまで対話的に進められる
:::

## 今日のゴール

Agent Skills(エージェントスキル)の仕組みを理解し、自分の定型業務を1つスキル化してみる。

## 座学

### Agent Skillsとは何か

前回までの回で、CLAUDE.mdという「Claude Codeに毎回読み込ませる基本ルール」を扱いました。しかし、業務のすべてのルールをCLAUDE.mdに詰め込むと、ファイルが肥大化し、かえってClaude Codeが本当に重要な指示を読み落としやすくなってしまいます。

そこで登場するのが「Agent Skills(エージェントスキル)」です。Skillは、特定の作業をするときだけClaude Codeに読み込ませる手順書のようなもので、`.claude/skills/<skill-name>/SKILL.md` というファイルに定義します。ユーザーが `/skill-name` と入力して手動で呼び出すこともできますし、SKILL.mdに書かれた説明文(description)をもとに、Claude Codeが「今の会話にはこのスキルが必要そうだ」と自動的に判断して発動させることもできます。

### Progressive Disclosure(段階的開示)という設計思想

CLAUDE.mdとSkillsの最大の違いは、「いつ読み込まれるか」です。

- **CLAUDE.md**: セッションが始まるたびに、常に読み込まれる
- **Skills**: そのスキルが必要になった場面でだけ読み込まれる

この仕組みを「Progressive Disclosure(段階的開示)」と呼びます。Claude Codeは最初、各スキルの`name`と`description`(概要)だけを把握しており、実際に本文(具体的な手順)を読み込むのは、そのスキルが必要だと判断した瞬間だけです。これにより、使っていないスキルがどれだけ増えても、普段の会話のコンテキスト(文脈情報の容量)を圧迫しません。

たとえるなら、CLAUDE.mdは「デスクに常に置いてある業務マニュアルの表紙」、Skillsは「棚にしまってあり、必要なときだけ取り出す作業手順書の束」というイメージです。

なお、Agent Skillsはもともと Anthropic が開発した仕組みですが、現在はオープンな標準規格として公開されており、Claude Code以外の複数のAIエージェントツールでも採用が広がっています(参考: https://agentskills.io/home )。特定のツールに縛られない汎用スキルとして育てていける、という点も覚えておくとよいでしょう。

### SKILL.mdの基本構造

SKILL.mdは、ファイルの先頭に「YAML frontmatter」と呼ばれるメタ情報のブロックを置き、その下に実際の指示文を書くという構造になっています。

```markdown
---
name: summarize-changes
description: 未コミットの変更内容を要約し、リスクをフラグ立てするスキル
---

## 現在の変更内容

!`git diff HEAD`

## 指示

上記の変更内容を2〜3個のポイントでまとめ、以下のリスク
(エラーハンドリング不足、ハードコードされた値、テスト未更新)
があれば指摘してください。
```

主なfrontmatterのフィールドは以下のとおりです。

| フィールド | 役割 |
|---|---|
| `name` | スキルの名前(`/name`で呼び出せる) |
| `description` | どんな場面で使うスキルかの説明。Claude Codeが自動発動を判断する際の手がかりになる |
| `allowed-tools` | このスキル実行中に、確認なしで使ってよいツールを制限する |

特に`description`は、単なる説明文ではなく「発動条件そのもの」だと捉えるとよいでしょう。ユーザーが自然に使いそうな言い回しを複数含めておくと、Claude Codeが的確なタイミングでスキルを呼び出してくれるようになります。

SKILL.md本体のボリュームには目安があり、Agent Skillsの仕様では500行・5,000トークン程度に収めることが推奨されています(参考: https://agentskills.io/skill-creation/best-practices )。それ以上の詳細な手順や参照資料は、`references/`フォルダに分けて「〇〇のときはこのファイルを読む」と指示しておくことで、必要なときだけ追加で読み込ませることができます。これもProgressive Disclosureの考え方の延長です。

また、実務で使い込んでいくと、「このシステムのユーザーIDはAPIでは`uid`という名前になっている」といった、Claude Codeが自力では気づけない環境固有の落とし穴に出会うことがあります。こうした情報は「Gotchas(落とし穴)」という見出しでSKILL.mdにまとめておくと、同じ間違いを繰り返させずに済みます。

### 実例: 実務で使っているスキルの紹介

筆者が実際に業務で使っているスキルをいくつか紹介します。いずれも「よく発生するのに、毎回一から指示するのが面倒な作業」をスキル化したものです。

- **WAFログ分析スキル(waf-query / waf-analyze)**: AWS WAFのログをAmazon Athena(ログをSQLで検索できるサービス)でクエリし、多段階で分析してリスクを評価し、追加・変更すべきWAFルールを提案します。「WAFログを分析して」「攻撃されているか確認して」といった自然な日本語の一言で自動的に発動するよう、descriptionに想定される言い回しを複数書き込んであります。
- **ナレッジ検索スキル(obsidian-search)**: 過去のセッションで得た知見をまとめたノートから、必要な情報を検索するスキルです。「以前どう対応したか思い出せない」という場面で活躍します。
- **設定監査スキル(claude-code-config-check)**: プロジェクトのClaude Code設定(CLAUDE.mdやsettings.jsonなど)を、Anthropic公式のベストプラクティスに照らしてチェックするスキルです。「設定が正しいか確認して」といった依頼で自動的に発動します。

これらに共通するのは、「診断業務や運用業務のなかで繰り返し行っている手順」を切り出している点です。TAMの業務にも、同じように繰り返し発生する定型作業が必ずあるはずです。

### CLAUDE.mdとSkillsの使い分け

| | CLAUDE.md | Skills |
|---|---|---|
| 読み込まれるタイミング | 毎回(セッション開始時) | 必要なときだけ |
| 向いている内容 | プロジェクト共通の基本ルール、コーディング規約 | 特定の作業手順、頻度は低いが複雑な処理 |
| ボリュームの目安 | 200行以下を推奨 | 個々のスキルは目的を絞って簡潔に |

迷ったときの目安は、「そのルールは会話のたびに必要か、それとも特定の作業のときだけ必要か」です。前者はCLAUDE.md、後者はSkillsに書くと役割がすっきり分かれます。

### SKILL.mdは手書きせず、`skill-creator`に作ってもらう

ここまでSKILL.mdの構造を説明してきましたが、実際にスキルを作るときは、frontmatterやdescriptionの書き方を一から自分で考える必要はありません。Anthropicは、スキル作成そのものを支援する`skill-creator`というSkillを`anthropics/skills`リポジトリで公式に配布しています(参考: https://github.com/anthropics/skills )。

`skill-creator`は、作りたいスキルの目的をヒアリングしながらSKILL.mdのひな形を生成し、テストケースの作成・実行や、descriptionが意図通りに発動するかの検証まで対話的に進めてくれます。プラグインの仕組み(次回詳しく扱います)を使って導入し、`/skill-creator` と呼び出すか「新しいスキルを作りたい」と話しかければ自動的に発動します。今日のハンズオンも、このskill-creatorを使って進めていきます。

## ミニハンズオン

自分の定型業務を1つ、簡単なスキルにしてみましょう。ここでは例として「議事録をアクションアイテムに整形するスキル」を作ります。

### 手順1: skill-creatorを導入する

作業フォルダ(`~/claude-work`)で、次のコマンドを実行します。

```
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
```

### 手順2: skill-creatorに作りたいスキルを伝える

```
新しいスキルを作りたいです。会議の議事録テキストを読み取り、
担当者・期限・タスク内容の3項目を表形式で抽出するスキルにしてください。
「議事録からアクションアイテムを抽出して」「タスクを整理して」といった
依頼で自動的に発動するようにしたいです。
```

skill-creatorが目的や発動条件をヒアリングしながら、`.claude/skills/`配下にSKILL.mdを作成してくれます。手書きでは迷いがちなdescriptionの言い回しも、対話の中で一緒に詰めていけます。

### 手順3: 動作確認する

手元にある実際の議事録を1件用意するか、なければ「適当な会議の議事録メモを1つ作って」とClaude Codeに頼んでサンプルを作ってもらい、次のように依頼してみます。

```
このメモのアクションアイテムを整理して。
```

descriptionが適切であれば、Claude Codeが自動的に先ほど作ったスキルを見つけ出し、発動します。うまく発動しない場合は、直接スキル名で呼び出して確認したうえで、skill-creatorに「descriptionをもっと発動しやすい言い回しに直して」と頼み、調整してもらいましょう。

### 手順4: 実際の業務に近づける

診断報告書のひな形生成や、顧客からの問い合わせメールのカテゴリ分類など、自分の業務に近い形にカスタマイズしてみましょう。最初から完璧を目指す必要はありません。次回以降、使いながら少しずつ育てていくものだと考えてください。

## まとめ+チーム資産化アクション(5分)

- Skillsは「特定の作業のときだけ読み込まれる手順書」であり、CLAUDE.mdと役割を分担することでコンテキストを圧迫せずに済む
- descriptionの書き方が、スキルが的確に発動するかどうかを左右する
- SKILL.mdは手書きにこだわらず、公式の`skill-creator`を使うと発動条件の作り込みまで対話的に進められる
- 繰り返し行っている業務ほど、スキル化の効果が大きい

**チームへの持ち帰りアクション**: 今日作ったスキルを、実際の業務で1週間使ってみてください。うまくいかなかった点は、次回の勉強会までにskill-creatorを使って再調整し、チームの共有フォルダ(`.claude/skills/`)に置いてメンバー間で使い回せるようにしましょう。

## ベストプラクティスのひとこと

カンリー社内勉強会資料(Zenn)では、「フィードバックの資産化」という考え方が紹介されています。これは、Claude Codeとのやり取りで得た気づきを、次のような段階を踏んで組織の資産に変えていくというモデルです。

1. **その場で修正する**: 会話の中でその都度指摘し、その回だけ直す
2. **ルール化する**: 繰り返し指摘するようなら、CLAUDE.mdにルールとして書き込む
3. **スキル化する**: さらに複雑な手順として繰り返し使うなら、今日学んだSkillsとして切り出す
4. **自動化する**: 完全に定型化できたら、hooksやMCPと組み合わせて自動実行する

今日作ったスキルは、まさにこの「3. スキル化する」の段階にあたります。自分の中で「これは毎回同じ手順だな」と感じた作業があれば、CLAUDE.mdに書き足す前に、まずSkills化を検討してみるとよいでしょう。あわせて、Agent Skillsのオープン仕様を整備しているagentskills.ioのベストプラクティスガイド(参考: https://agentskills.io/skill-creation/best-practices )が強調する「エージェントが既に知っていることは書かず、知らないことだけを書く」という原則も意識してください。

## おわりに

社内勉強会は今後も継続していく予定で、この形式で資料を公開していきます。次回はプラグインとマーケットプレイスを使って、今日学んだSkillsを含む複数の機能をまとめて拡張する方法を扱う予定です。定型業務のスキル化は地味に見えて積み重なると大きな効果を生む部分なので、ぜひ自分の業務で試してみてください。

この記事がどなたかの役に立つと嬉しいです。

## 参考リンク

- [Claude Code Skills(公式)](https://code.claude.com/docs/en/skills.md)
- [Claude Code ベストプラクティス(公式)](https://code.claude.com/docs/en/best-practices.md)
- [Agent Skills 公式仕様サイト](https://agentskills.io/home)
- [Agent Skills スキル作成のベストプラクティス](https://agentskills.io/skill-creation/best-practices)
- [anthropics/skills(skill-creatorを含む公式サンプル集、GitHub)](https://github.com/anthropics/skills)
- [クラスメソッド DevelopersIO「Claude Code Skills(Agent Skills)入門」社内勉強会](https://dev.classmethod.jp/en/articles/claude-code-skills-for-cloud-bu-consulting-members/)
- [カンリー社内Claude Code勉強会資料(Zenn)](https://zenn.dev/canly/articles/cc0891517e45cc)
