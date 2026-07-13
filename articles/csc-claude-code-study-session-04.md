---
title: "[社内勉強会資料公開] Claude Code 入門 #4 — permissions・hooks・devcontainerで安全に使う"
emoji: "📖"
type: "tech"
topics: ["claudecode", "aiエージェント", "社内勉強会"]
published: false
published_at: 2026-08-04 09:30
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

CSC社内で開催している「CloudFastener の TAM(テクニカルアカウントマネージャー)向けに、Claude Codeを初歩から実践まで学ぶ勉強会」の第4回資料です。前回はCLAUDE.mdを使って、Claude Codeを自分の業務仕様にカスタマイズする方法を扱いました。

https://zenn.dev/cscloud_blog/articles/csc-claude-code-study-session-03

第4回は、Claude Codeを安全に運用するための「抑止・制限・隔離」という3段階の考え方を理解し、自分の環境にpermissions設定とhooksを一つずつ組み込むことがゴールです。セキュリティコンサルタントという職業柄、この回は特に丁寧に扱いたいテーマです。

:::message
**この記事の3行まとめ**

- Claude Codeを安全に使う考え方は「抑止(CLAUDE.md)・制限(permissions・hooks)・隔離(devcontainer)」の3段階で整理できる
- permissionsは読み取り系コマンドなど最小限の許可から始め、信頼が積み上がるにつれて範囲を広げていくのが基本
- 顧客データや出所不明なリポジトリを扱うときは、Devcontainerのような使い捨て環境で隔離するのが安全
:::

## 今日のゴール

Claude Codeを安全に運用するための「抑止・制限・隔離」という3段階の考え方を理解し、自分の環境にpermissions設定とhooksを一つずつ組み込む。

## 座学

### 「抑止・制限・隔離」という3つの安全対策

Claude Codeはファイルの読み書きやコマンド実行を自律的に行うため、何の対策もせずに使うと意図しない操作を実行してしまうリスクがあります。クラスメソッド社のDevelopersIOで公開されている社内勉強会資料(参考: https://dev.classmethod.jp/articles/claude-code-security-basics/ )では、安全に使うための考え方を次の3つの軸に整理しています。

1. **抑止**: そもそも危険な行動を取らせないよう、指示(CLAUDE.md)でルールを明示する
2. **制限**: 実行できる操作の範囲そのものを、設定(permissions・hooks)で技術的に絞り込む
3. **隔離**: 万が一想定外の操作が実行されても被害が及ばないよう、影響範囲を環境(sandbox・devcontainer)ごと分離する

CLAUDE.mdによる「抑止」は前回扱いました。今回は「制限」と「隔離」を中心に、セキュリティコンサルタントとして押さえておきたい設定を見ていきます。

### 制限その1: permissionsで実行できる操作を絞り込む

Claude Codeの挙動は `settings.json` というファイルで制御できます。この中の `permissions` 項目で、どのコマンドやファイル操作を「確認なしで実行してよいか(allow)」「実行させないか(deny)」を細かく指定できます(参考: https://code.claude.com/docs/en/permission-modes.md )。

例えば、次のような設定は「調査・確認のための読み取り系コマンドだけを許可し、それ以外(ファイルの書き込みや削除、外部への通信など)は都度確認を求める」という構成です。

```json
{
  "permissions": {
    "allow": [
      "Bash(ls *)",
      "Bash(find *)",
      "Bash(grep *)",
      "Bash(cat *)",
      "Bash(head *)",
      "Bash(tail *)",
      "Bash(wc *)",
      "Bash(pwd)",
      "Bash(env)"
    ],
    "deny": [
      "Bash(curl *)",
      "Read(./.env)"
    ]
  }
}
```

このように「読み取り・調査系のコマンドは自動実行してよいが、書き込みや外部通信を伴う操作は必ず人間が確認する」という運用は、実務で使う際の基本形としておすすめです。ポイントは、最初から幅広く許可するのではなく、最小限の範囲から始めて、Claude Codeの挙動に慣れて信頼が積み上がるにつれて少しずつ許可範囲を広げていくことです。

なお、`permissions` には個別コマンドの許可・拒否のほかに、`defaultMode` として動作モード全体を指定することもできます。

- `default`: 読み取り以外の操作はすべて確認を求める、最も保守的なモード
- `plan`: 変更を加える前に必ず計画を提示させるモード(前回紹介したPlan Mode)
- `acceptEdits`: ファイル編集や基本的なコマンドは自動承認するモード
- `bypassPermissions`: すべての操作を確認なしで実行するモード(隔離された使い捨て環境以外では推奨しません)

### 制限その2: hooksでライフサイクルイベントに処理を挟み込む

`hooks` は、Claude Codeのセッションの節目(セッション開始時、セッション終了時、ツール実行前など)に、任意のコマンドを自動的に実行させる仕組みです。「制限」だけでなく、記録の自動化にも活用できます。

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "path/to/save-session-notes.py"
          }
        ]
      }
    ]
  }
}
```

これは、セッションが終了するたびに、その日の作業内容を自動的に社内のナレッジベース(NotionやObsidianなど)へ記録するスクリプトを起動する設定の例です。こうしておくと、「今日Claude Codeと何をやり取りしたか」をわざわざ手動でメモしなくても、自然にチームの知識として蓄積されていきます。

このほか、`PreToolUse` フックを使えば、Claude Codeが特定のツールを実行する直前に、独自のチェックスクリプトを走らせて危険な操作をブロックする、といった高度な制限も可能です。

### 隔離: Dev Containerや使い捨て環境で試す

permissionsやhooksは「実行させない・記録する」という制限の仕組みですが、それでも「万が一」の可能性はゼロにはできません。そこで有効なのが、影響範囲そのものを隔離してしまう考え方です。

具体的には、Dev Container(VS CodeのDevcontainer機能やDockerコンテナ)のような使い捨て可能な環境の中でClaude Codeを動かし、ホストマシンの本体環境には一切触れさせない、という運用です。特に次のような場面では、隔離環境での実行を強く推奨します。

- 挙動のよくわからない外部のプラグインやMCPサーバーを試すとき
- 信頼できないリポジトリをcloneして中身を調査するとき
- `bypassPermissions` のような広い権限で一時的に作業したいとき

コンテナは使い終わったら破棄すればよいため、「試してみて何か変なことが起きても、被害はコンテナの中で完結する」という安心感を持って新しい機能を試すことができます。

### 制限と隔離の中間: 組み込みのsandboxモード

Devcontainerによる隔離は安心感が高い一方、Docker環境の準備や設定にひと手間かかります。もう少し手軽な選択肢として、Claude Codeには`/sandbox`という組み込み機能があります(参考: https://code.claude.com/docs/en/sandboxing.md )。これは、Bashコマンドの実行だけをOSレベルで隔離し、ファイルシステムやネットワークへのアクセスを制限する仕組みで、macOSは追加設定なしで、Linux/WSL2では`bubblewrap`の導入で利用できます(ネイティブWindowsは非対応)。

ただし、sandboxが隔離するのはBashコマンドの実行だけで、ファイル編集やMCPサーバーの動作までは隔離されません。「日常的な作業で確認の手間を減らしたい」場面ではsandboxモード、「出所不明なリポジトリやプラグインを全面的に隔離して試したい」場面ではDevcontainer、という使い分けを意識してください。

### 顧客データの取り扱いには特別な注意を

セキュリティコンサルタントの業務では、顧客の機密情報や診断対象システムの構成情報を扱う場面が多くあります。Claude Codeにこうした情報を読み込ませる際は、通常の業務データ以上に注意が必要です。

- 顧客との契約上、AIツールへのデータ入力が制限されていないかを事前に確認する
- 診断対象システムの認証情報やソースコードをそのままプロンプトに貼り付けない(必要な範囲だけを抜粋する)
- MCPサーバーなど外部連携機能を使う場合、送信先が信頼できるサービスかを確認する(この点は第8回のMCPの回で詳しく扱います)

「便利だから」という理由だけで顧客データを安易に投入せず、案件ごとの契約条件や社内ルールと照らし合わせる習慣をつけましょう。

### Claude Code自体のリスクも知っておく

Claude Code自体も一つのソフトウェアである以上、脆弱性が報告されることがあります。例えば、信頼できないリポジトリをcloneしてClaude Codeに読み込ませた際に、リポジトリ内に仕込まれた悪意のある指示(プロンプトインジェクション)が実行されてしまうリスクが指摘された事例があります(参考: https://prtimes.jp/main/html/rd/p/000000493.000021207.html 、 https://qiita.com/GeneLab_999/items/a02a5d32f472e3265397 )。

こうしたリスクへの備えとしても、「出所の分からないリポジトリやファイルを扱うときは隔離環境で」という原則が効いてきます。また、Claude Code自体も日々アップデートされているため、ネイティブインストーラの自動更新機能を有効にしておき、常に最新版を使うことも基本的な対策になります。

## ミニハンズオン

### 手順1: 自分のpermissions設定を確認する

まずは現在の設定を確認しましょう。プロジェクトディレクトリで次のコマンドを実行するか、Claude Codeのセッション内で `/permissions` と入力します。

**macOS / Linux / WSL(ターミナル)**
```bash
cat .claude/settings.json
```

**Windows(PowerShell)**
```powershell
Get-Content .claude\settings.json
```

まだ何も設定していない場合は、ファイルが存在しないか、`permissions` の項目が空のはずです。

### 手順2: 読み取り系コマンドだけを許可する設定を追加する

作業フォルダ(第1回で作成した `~/claude-work` など)に `.claude/settings.json` を作成し、座学で紹介した読み取り系コマンドのallowリストを書き込んでみましょう。慣れないうちは、Claude Code自身に「settings.jsonにpermissions設定を追加したい」と依頼して、対話形式で作ってもらうのもおすすめです。

```
.claude/settings.jsonに、ls・find・grep・catなどの読み取り系Bashコマンドだけを
自動承認するpermissions設定を追加してください。書き込み系の操作は含めないでください。
```

### 手順3: セッション終了時のhookを試す

簡単な例として、セッション終了時に「お疲れ様でした」と書かれたログファイルを作成するだけのシンプルなhookを設定してみます。

```
セッションが終了したときに、現在時刻を session-log.txt に追記する
SessionEndフックを設定してください。
```

実際にセッションを終了してみて、`session-log.txt` に記録が残っていることを確認しましょう。この仕組みを応用すれば、座学で紹介したような「作業内容の自動記録」に発展させることができます。

## まとめ+チーム資産化アクション(5分)

- 安全に使うための考え方は「抑止(CLAUDE.md)・制限(permissions・hooks)・隔離(devcontainer)」の3段階で整理できる
- permissionsは最小限の許可から始め、信頼が積み上がるにつれて範囲を広げていく
- 顧客データやリスクのある操作は、隔離された使い捨て環境で扱うことを徹底する

**チームへの持ち帰りアクション**: 今日作成したpermissions設定を、チームの標準テンプレートとして共有しましょう。案件ごとに異なる制約がある場合は、プロジェクトのCLAUDE.mdやsettings.jsonに明記し、チームメンバー全員が同じ安全基準で作業できるようにします。

## ベストプラクティスのひとこと

Claude Code公式のPermission Modesドキュメント(参考: https://code.claude.com/docs/en/permission-modes.md )では、`allow`/`deny`/`ask`によるルールベースの権限制御と、`default`から始まる段階的なモード設計が示されています。ここに通底しているのは「権限は最小の範囲から始めて、信頼が積み上がるにつれて徐々に広げる」という考え方です。いきなり `bypassPermissions` のような広い権限を与えるのではなく、まずは読み取り専用の範囲で挙動を観察し、問題がないと分かった操作から少しずつ自動承認の対象を広げていく、という段階的なアプローチを意識してください。

## おわりに

社内勉強会は今後も継続していく予定で、この形式で資料を公開していきます。次回はモデルの使い分けとeffort(推論の深さ)の調整方法を扱い、タスクの性質に応じて速度・思考力・コストのバランスを取る方法を紹介する予定です。今回扱ったpermissions設定は地味に見えますが、顧客の機密情報を扱うセキュリティコンサルタントにとっては最初に整えておくべき土台なので、ぜひ自分の環境にも組み込んでみてください。

この記事がどなたかの役に立つと嬉しいです。

## 参考リンク

- [Claude Code Permission Modes(公式)](https://code.claude.com/docs/en/permission-modes.md)
- [Claude Code ベストプラクティス(公式)](https://code.claude.com/docs/en/best-practices.md)
- [クラスメソッド DevelopersIO「Claude Codeを安全に使う」社内勉強会](https://dev.classmethod.jp/articles/claude-code-security-basics/)
- [Check Point ResearchによるClaude Code関連の脆弱性指摘](https://prtimes.jp/main/html/rd/p/000000493.000021207.html)
- [clone起点のリスクに関する解説記事(Qiita)](https://qiita.com/GeneLab_999/items/a02a5d32f472e3265397)
