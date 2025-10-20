---
title: "AWSのIdP障害に備えて緊急時アクセス(Break glass access)手順を用意しよう"
emoji: "🚨"
type: "tech"
topics: ["aws", "iam", "security", "organizations"]
published: true
---

# AWSのIdP障害に備えて緊急時アクセス(Break glass access)手順を用意しよう

こんにちは、CSCの平木です！

AWSへのアクセスに外部IdP（Identity Provider）を利用している組織は多いと思います。しかし、IdPに障害が発生した場合、AWS環境へのアクセスができなくなる可能性があります。このような緊急時に備えて、Break glass access（緊急時アクセス）手順を準備しておくことが重要です。

参考リンク: [AWS IAM Identity Center - Break glass access](https://docs.aws.amazon.com/singlesignon/latest/userguide/emergency-access.html)

## Break glass accessとは

Break glass accessは、通常のアクセス手段が利用できない緊急時に、システムへアクセスするための代替手段です。「ガラスを割って」という名前の通り、緊急時のみ使用する特別なアクセス方法を指します。

| 項目 | 通常のアクセス | Break glass access |
|------|--------|--------|
| 認証方法 | 外部IdP（SAML/OIDC） | IAMユーザー |
| 使用頻度 | 日常的 | 緊急時のみ |
| 管理方法 | IdP側で管理 | AWS IAM で管理 |
| MFA | IdP側で設定 | IAM側で設定 |
| アクセス権限 | 役割に応じて細分化 | 管理者権限 |

特徴的な点としては、

* IdP障害時の最終手段として機能する
* 厳格な管理とモニタリングが必要
* 定期的なテストと更新が推奨される

が挙げられるかなと思います。

## Break glass accessの準備手順

### 1. 専用IAMユーザーの作成

IdP障害時にアクセスできる専用のIAMユーザーを作成します。

```bash
# AWS CLIでIAMユーザーを作成
aws iam create-user --user-name break-glass-admin
```

![IAMユーザー作成画面](画像URL)

ポイント：
- ユーザー名は用途が明確にわかるものにする
- 複数のユーザーを作成して冗長化することも検討
- Organizations環境では管理アカウントに作成

### 2. 強力なパスワードとMFAの設定

```bash
# パスワードポリシーの確認
aws iam get-account-password-policy

# MFAデバイスの有効化（マネジメントコンソールで実施）
```

ポイント：
- パスワードは複数の管理者で分割管理
- MFAは物理トークンまたは複数のバーチャルMFAを準備
- 認証情報は金庫など物理的に安全な場所に保管

### 3. 適切な権限の付与

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

AdministratorAccessポリシーをアタッチするか、カスタムポリシーで必要最小限の権限を設定します。

```bash
# AdministratorAccessポリシーをアタッチ
aws iam attach-user-policy \
  --user-name break-glass-admin \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

### 4. アクセスキーの管理

コンソールアクセスだけでなく、CLI/APIアクセスも必要な場合：

```bash
# アクセスキーの作成
aws iam create-access-key --user-name break-glass-admin
```

作成したアクセスキーは暗号化して安全に保管します。

## モニタリングとアラート設定

Break glass accessの使用を検知するため、CloudTrailとCloudWatch Alarmsを設定します。

### CloudTrail イベントの監視

```yaml
# CloudWatch Logs フィルターパターン例
{ ($.userIdentity.type = "IAMUser") && ($.userIdentity.userName = "break-glass-admin") }
```

### SNS通知の設定

```bash
# SNSトピックの作成
aws sns create-topic --name break-glass-access-alert

# CloudWatch Alarmの設定
aws cloudwatch put-metric-alarm \
  --alarm-name BreakGlassAccessAlert \
  --alarm-description "Break glass IAM user accessed" \
  --metric-name BreakGlassLogin \
  --namespace Custom/Security \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

## メリットと留意点

### メリット

* **IdP障害時の確実なアクセス手段** - 外部依存を排除した独立したアクセス経路
* **ビジネス継続性の向上** - 緊急時でもAWS環境の管理・復旧が可能
* **コンプライアンス要件への対応** - 多くのセキュリティフレームワークで推奨される対策

### 留意点

* **定期的なテストが必須**
  + 最低でも四半期に1回は実際にログインしてアクセス可能か確認
  + MFAデバイスの動作確認
  + 認証情報の保管場所と取り出し手順の確認
* **厳格なアクセス管理**
  + 使用時は必ず複数人で立ち会う
  + 使用後は詳細なレポートを作成
  + CloudTrailログを保存して監査証跡を残す
* **認証情報のローテーション**
  + パスワードは定期的に変更（推奨：年1回以上）
  + アクセスキーを使用している場合は90日ごとにローテーション
  + ローテーション時は必ず複数人で実施
* **組織全体での手順の共有**
  + Break glass accessの存在と使用手順を文書化
  + 関係者全員が手順を理解していることを確認
  + 緊急連絡先リストとともに管理

## おわりに

IdP障害は予期せず発生する可能性があり、その際にAWS環境へアクセスできないことは重大なビジネスリスクとなります。Break glass accessを適切に準備・管理することで、緊急時でも確実にシステムを運用できる体制を構築できます。

ただし、Break glass accessは強力な権限を持つため、その管理には細心の注意が必要です。定期的なテスト、厳格なモニタリング、そして組織全体でのガバナンス体制の整備を忘れずに実施しましょう。

この記事がどなたかの役に立つと嬉しいです。
