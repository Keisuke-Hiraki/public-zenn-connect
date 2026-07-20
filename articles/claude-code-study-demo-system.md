---
title: "Cognitoでユーザーを作るだけでブラウザからClaude Codeを触れる勉強会用サンドボックスを作った話"
emoji: "🖥️"
type: "tech"
topics: ["claudecode", "ecs", "cognito", "bedrock"]
published: true
published_at: 2026-07-21 08:00
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

Claude Code の社内勉強会をやるにあたって、「参加者に Claude Code を触ってもらいたいが、人によってはすぐに Anthropic のモデルにアクセスするための環境を用意できる人とできない人がいる」という課題がありました。

そこで、Cognito でユーザーを1人作成するだけで、ブラウザからそのままターミナル操作で Claude Code を使える使い捨てのサンドボックス環境を作り、GitHub で公開しました。

https://github.com/Keisuke-Hiraki/claude-playground-poc

この記事では、なぜこれを作ったのか、内部でどういうロジックが動いているのか、そして構築する中でハマったポイントを整理します。

:::message
この記事の5行まとめ
- 参加者ごとに使い捨てのコンテナを動的に立ち上げ、ブラウザ経由でその中の Claude Code にターミナルアクセスさせる仕組み
- 認証は Cognito + ALB の `authenticate-cognito` に任せ、ゲートウェイは ALB が発行する署名済み JWT を検証するだけ
- 参加者の実効権限は ECS タスクロールの IAM ポリシーそのものであり、Bedrock の3モデルへの `InvokeModel` のみに絞っている
- モデルは Amazon Bedrock 経由のみに固定し、利用時間帯・セッション時間に上限を設けて自動停止させる
- ローカル確認用の Docker Compose 構成と、AWS 本番相当の Terraform 構成を1つの `gateway/server.js` で両立させている
:::

## なぜ作ったのか

Claude Code の勉強会でハンズオンをやろうとすると、大抵は「各自の PC に Claude Code をインストールしてもらい、API キーか Bedrock のクレデンシャルを配る」という準備が発生します。事前にサブスクリプション契約が必要になる場合もあります。これは環境差異によるトラブルが起きやすく、クレデンシャル配布も管理コストが高いです。

一方で、Claude Code は元々ターミナル上で動く CLI なので、「ブラウザで開けるターミナル」を用意してそこに Claude Code を起動しておけば、参加者は URL を開くだけで済みます。

要件を整理すると次のようになります。

- 参加者は Cognito Hosted UI でユーザーを作成する（あるいは許可されたメールドメインで自己登録する）だけで使える
- 各参加者は他の参加者から隔離された、自分専用のコンテナを持つ
- 利用できる Claude モデルは Bedrock 経由の指定モデルのみに強制する
- 利用時間帯とセッション時間に上限を設け、勉強会が終わったらリソースが自動的に片付く

## 全体アーキテクチャ

構成は大きく3つのパーツからなります。

- **gateway**: ユーザーごとのコンテナへの WebSocket プロキシを行う Node.js サーバー（ECS Fargate 常駐サービス）
- **per-user container**: Claude Code + [ttyd](https://github.com/tsl0922/ttyd)（ブラウザ向け PTY サーバー）を同梱したコンテナ。gateway が参加者のログインを検知したタイミングで動的に `RunTask` する
- **Cognito + ALB**: ログイン認証を担当。ALB の `authenticate-cognito` リスナーアクションが Cognito Hosted UI へのリダイレクトとログイン後のセッションCookie発行を行う

参加者から見た流れはこうです。

1. ALB の URL にアクセス
2. 未ログインなら Cognito Hosted UI にリダイレクトされ、ログイン（またはメールドメイン制限付きの自己登録）
3. ログイン後、ALB が署名済みの ID 情報を `x-amzn-oidc-data` ヘッダーに載せてリクエストを gateway に転送
4. gateway がそのユーザー専用の Fargate タスクをまだ持っていなければ `ecs:RunTask` で起動し、起動完了を待ってから WebSocket をプロキシ
5. ブラウザに ttyd の画面が表示され、`bash` にログインした状態になる。そこから `claude` を起動すれば Claude Code が使える

![](/images/ChatGPT_Image_20260720_23_42_41.png)

## 認証のロジック: ALBの署名済みJWTを検証する

ここが設計上一番気を使った部分です。ALB の `authenticate-cognito` アクションは、認証済みリクエストに次の3つのヘッダーを付与します。

- `x-amzn-oidc-accesstoken`
- `x-amzn-oidc-identity`（平文のユーザー識別子）
- `x-amzn-oidc-data`（ES256 で署名された JWT）

AWS のドキュメントには、`x-amzn-oidc-identity` を単体で信頼してはならず、`x-amzn-oidc-data` を ALB 自身の公開鍵で検証すべきという要件があります。これを怠ると、ALB の手前に到達できる経路さえあれば `x-amzn-oidc-identity` ヘッダーを偽装してなりすましできてしまうからです。

`gateway/server.js` の `verifyOidcJwt` はこの検証を行っています。

```js
async function verifyOidcJwt(token) {
  const [headerB64, payloadB64, sigB64] = token.split('.');
  const header = JSON.parse(base64UrlDecode(headerB64).toString('utf8'));
  const payload = JSON.parse(base64UrlDecode(payloadB64).toString('utf8'));

  if (header.alg !== 'ES256') throw new Error(`unexpected alg: ${header.alg}`);
  if (payload.exp && Date.now() / 1000 > payload.exp) throw new Error('token expired');

  const pem = await fetchAlbPublicKeyPem(header.kid);
  const publicKey = crypto.createPublicKey(pem);
  const verified = crypto.verify(
    'sha256',
    Buffer.from(`${headerB64}.${payloadB64}`),
    { key: publicKey, dsaEncoding: 'ieee-p1363' },
    base64UrlDecode(sigB64),
  );
  if (!verified) throw new Error('signature verification failed');
  return payload;
}
```

ALB の公開鍵は `kid`（鍵ローテーション用の識別子）ごとに `https://public-keys.auth.elb.<region>.amazonaws.com/<kid>` から取得でき、取得結果は `kid` 単位でメモリキャッシュしています。検証を通過した JWT の `sub`（Cognito のユーザー識別子）と `email` を、以降のセッション管理のキーとして使います。

この「ALB認証＋WebSocketプロキシ」の組み合わせは、AWSの公式ドキュメントに明文化された動作保証があるわけではありませんが、実際にCognitoログイン→ALB署名検証→動的タスク起動→WebSocketプロキシまで一連の動作を確認済みです。

## セッション管理のロジック: 動的なタスク起動と自動停止

参加者ごとのコンテナは常時起動させず、初回アクセス時に `RunTask` で起動します。`gateway/server.js` の `sessions` という `Map`（`sub` → セッション状態）でこれを管理しています。

```js
async function getOrCreateSession(sub, email) {
  const existing = sessions.get(sub);
  if (existing) {
    if (existing.launchPromise) await existing.launchPromise;
    return sessions.get(sub);
  }

  if (!isWithinLaunchWindow(Date.now())) {
    const err = new Error(`access is only available ...`);
    err.statusCode = 403;
    throw err;
  }

  const session = { status: 'launching', launchPromise: null };
  sessions.set(sub, session);
  session.launchPromise = launchSession(sub, email)
    .catch((err) => { sessions.delete(sub); throw err; })
    .finally(() => { const s = sessions.get(sub); if (s) s.launchPromise = null; });
  await session.launchPromise;
  return sessions.get(sub);
}
```

ポイントは次の通りです。

- 同一ユーザーからの同時多重リクエストに対して、起動処理を1回だけ実行するよう `launchPromise` で直列化している
- 利用可能時間帯（JST基準）の外からのアクセスは、タスクを起動せずに 403 を返す
- タスク起動後は `DescribeTasks` をポーリングしてタスクが `RUNNING` になるまで待ち、ENI からプライベートIPを解決してからプロキシ先として登録する
- 起動中は3秒ごとに自動リロードする簡易な待機ページを返す
- セッションには「利用可能時間帯の終了時刻」と「セッション開始からの上限（`SESSION_MAX_MINUTES`）」のどちらか早い方を期限として設定し、`setTimeout` で `ecs:StopTask` を呼んで自動停止する
- コンテナ側でも `entrypoint.sh` が `timeout ${SESSION_MAX_MINUTES}m ttyd ...` の形で ttyd プロセス自体を包んでおり、gateway とは独立してコンテナ自身が時間経過で終了する二重の保険をかけている

時間帯・セッション時間の管理状態（`sessions` の `Map`）は gateway プロセス内のメモリ上にあるため、gateway自体を再起動すると全参加者のセッション管理状態が失われます。ただし、起動済みの参加者コンテナ自体は上記の `timeout` によって時間経過で自律的に終了するため、gatewayの再起動がセッションの自動停止そのものを無効化するわけではありません。勉強会1回分の使い捨て運用としては割り切っていますが、恒久的な運用に転用する場合はこの管理状態の揮発性を認識しておく必要があります。

## セキュリティ設計: 参加者の実効権限はIAMタスクロールそのもの

このシステムでは、参加者にコンテナ内のシェルをそのまま渡します。つまり、**ECSタスクロール（`terraform/iam.tf` の `user_task`）に付与した権限が、そのまま参加者の実効権限になります**。この設計における最重要のセキュリティ境界です。

```hcl
data "aws_iam_policy_document" "bedrock_invoke_approved_models" {
  statement {
    sid    = "InvokeApprovedModelsOnly"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]
    resources = concat(
      [for id in local.approved_model_ids : "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:inference-profile/${var.bedrock_model_prefix}.anthropic.${id}"],
      [for id in local.approved_model_ids : "arn:aws:bedrock:*::foundation-model/anthropic.${id}"],
    )
  }
}
```

コンテナの `settings.json`（`ANTHROPIC_MODEL` 等の環境変数）でも利用モデルをこの3モデルに絞っていますが、これはあくまで「デフォルトの挙動」を明示しているだけで、実際の強制力を持つのは IAM ポリシー側です。参加者がコンテナ内で環境変数を書き換えても、IAMポリシーが許可していないモデルへの `InvokeModel` はAWS側で拒否されます。3モデルの内訳は Opus 4.6（`claude-opus-4-6-v1`）・Sonnet 5（`claude-sonnet-5`、デフォルト）・Haiku 4.5（`claude-haiku-4-5-20251001-v1:0`、小型・高速用モデルとしても使用）で、inference profile のプレフィックスは既定で `global` にしています（データレジデンシー上の理由があれば `jp` などのリージョンスコープなプレフィックスに変更できます）。

ネットワーク境界も同様の考え方で設計しています。

- 参加者コンテナはパブリックIPを持たず、プライベートサブネットに配置
- 参加者コンテナへの `ttyd`（7681番ポート）への通信は gateway のセキュリティグループからのみ許可
- gateway への通信も ALB のセキュリティグループからのみ許可
- ECR（`ecr.api`/`ecr.dkr`）/CloudWatch Logs/Bedrock（`bedrock-runtime`）/STS へのアクセスは NAT Gateway 経由ではなく VPC インターフェースエンドポイント経由に絞り、S3 も Gateway 型エンドポイント経由にすることで、NAT Gatewayが落ちても最低限の機能が維持できるようにしている

さらに、コンテナ内には `docker/init-firewall.sh` という egress 制限スクリプトも用意していますが、これはデフォルトで無効（`ENABLE_FIREWALL=false`）にしています。理由は、このスクリプトがドメイン名前解決を起動時に1回だけ行ってIPアドレスをiptables/ipsetに登録する方式のため、DNSトンネリングによる回避余地があるという既知の制約（[claude-code#36907](https://github.com/anthropics/claude-code/issues/36907), [#35197](https://github.com/anthropics/claude-code/issues/35197)）があるためです。あくまでセキュリティグループ・NAT境界の上に載せる多層防御としての位置付けであり、これ単体を信頼した設計にはしていません。

## ハマったポイント

### Bedrock利用時でも`api.anthropic.com`へのアクセスが発生する

`CLAUDE_CODE_USE_BEDROCK=1` を設定していても、Claude Code は自動更新チェックやテレメトリなど一部の補助的な通信で `api.anthropic.com` 等の Anthropic 側エンドポイントにアクセスを試みることがあります。これに気づかずVPCエンドポイントのみで完結する構成を最初に考えていましたが、これらの通信がタイムアウトするまでCLIがBedrockへのリクエストに進めない、という挙動に遭遇しました。

対策として、プライベートサブネットにNAT Gatewayを設置して一般的なインターネットegressを確保し、加えて `DISABLE_AUTOUPDATER=1` / `DISABLE_TELEMETRY=1` / `DISABLE_ERROR_REPORTING=1` を設定してこの通信自体を減らしています（完全にゼロにはなりません）。

### Bedrockモデルの利用にはMarketplaceの利用規約同意が別途必要

BedrockでAnthropicモデルを使うには、IAM権限とは別にAWS Marketplaceの利用規約に一度同意する必要があります。これを忘れると、Claude Codeの初回リクエストが

```
API Error: 403 Model access is denied due to IAM user or service role is not
authorized to perform the required AWS Marketplace actions ...
```

というエラーになるのですが、これがすぐに表面化せず、CLI側がしばらくリトライしてから403が出るという分かりにくい挙動になります。デプロイ時点ではエラーにならないため見落としやすく、`scripts/accept_bedrock_agreements.sh` で account/region ごとに一度実行する運用にしています。`variables.tf` の `bedrock_model_ids`（`opus`/`sonnet`/`haiku` の3項目を持つ固定構造）でモデルIDを変更した場合も、このスクリプトの再実行が必要です。スクリプト側のモデルID一覧は `variables.tf` から自動で読み込まれるわけではなくハードコードしているため、変更時は両方を手動で同期する必要があります。

### ALB認証とWebSocketの組み合わせ

ALBの `authenticate-cognito` はHTTPリクエストのCookie検証を前提とした機能で、WebSocketのUpgradeリクエストに対してもこれが正しく機能するかどうかは、AWSの公式ドキュメントに明記された保証がありません。実際に Cognito ログイン → ALB署名検証 → 動的タスク起動 → WebSocketプロキシの一連の流れを動作確認していますが、ドキュメント化されていない挙動に依存している以上、将来的にAWS側の仕様変更で影響を受ける可能性はゼロではないという点は認識しておく必要があります。

## ローカル確認用構成とAWS本番相当構成を1つのコードで両立させる

このリポジトリのもう1つの特徴は、`gateway/server.js` という1ファイルの中で「ローカル(Docker Compose)モード」と「AWS(Terraform)モード」の両方を実装している点です。`ECS_CLUSTER` 環境変数の有無で分岐します。

```js
const ECS_CLUSTER = process.env.ECS_CLUSTER || null;
const DYNAMIC_MODE = Boolean(ECS_CLUSTER);
```

- **ローカルモード**（`DYNAMIC_MODE = false`）: Cognito・ALBなしで、`gateway/users.json` の静的マップに従って `/login?user=alice` のようなクエリでユーザーを切り替える。認証は一切行わない、あくまでルーティングとコンテナビルドの動作確認用
- **AWSモード**（`DYNAMIC_MODE = true`）: 前述のALB署名検証と動的タスク起動が有効になる

CI/CDやテストコードは用意していないため、変更を加えるたびにこの2モードを手動で確認する運用にしています。両モードを1ファイルに共存させているのは、ルーティングロジックの本体（プロキシ処理）を分岐させず、認証・タスク起動部分だけを条件分岐に閉じ込めるためです。

## まとめ

Cognitoでユーザーを1人作るだけでブラウザからClaude Codeのターミナルに触れる、勉強会向けの使い捨てサンドボックス環境を作りました。  
設計の要点は、ALBに認証を任せつつゲートウェイ側でJWTを再検証すること、参加者の実効権限をECSタスクロールのIAMポリシーだけに閉じ込めること、利用時間帯とセッション時間を制限して確実にリソースが片付くようにすることです。

Bedrock利用時でも一般的なインターネットegressが必要になる点やMarketplace同意の分かりにくいエラーなど、実際に動かしてみて初めて分かる制約もいくつかありました。同様の勉強会・ハンズオン環境を検討している方の参考になれば幸いです。

この記事がどなたかの役に立つと嬉しいです。
