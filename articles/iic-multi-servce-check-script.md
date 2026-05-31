---
title: "IAM Identity Center の一時的な認証情報を使って複数のセキュリティサービス有効化状況を確認するスクリプトを作ってみた"
emoji: "🔍"
type: "tech"
topics: ["aws", "iamidentitycenter", "securityhub", "guardduty"]
published: true
publication_name: cscloud_blog
published_at: 2025-07-14 07:00
---
こんにちは、CSC の平木です！

複数の AWS アカウントを管理している環境では、セキュリティサービスの設定状況を一括で確認したいことがありますよね。
今回は、**IAM Identity Center**の一時的な認証情報を使用して、複数の AWS アカウントにスイッチロールし、**AWS Security Hub**、**AWS GuardDuty**、**IAM Access Analyzer** の有効化状況をチェックするスクリプトを作成してみました。

## 背景

- とある制約からスイッチロール元では CloudShell が使用できない
- Organizations 外の AWS アカウントのセキュリティサービスの有効化状況をスイッチロール経由で確認したい

上記のため、今回は、IAM Identity Centerの一時的な認証情報から各 AWS アカウントへスイッチロールしチェックしてみました。

![aws_iic_switch.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/456c64aa-bd2d-4fdd-8d92-7ead3501710f.png)

## やってみた

### 前提条件

#### 必要な設定
- IAM Identity Center のプロファイル設定済み
- 各対象アカウントでのスイッチロール権限
- Security Hub の読み取り権限

#### 必要なツール
- AWS CLI（v2 推奨）
- jq（JSON パーサー）
- bash（スクリプト実行環境）

### スクリプトの構成

#### ファイル構成

コードは下記 GitHub リポジトリにも配置済みです。

https://github.com/Keisuke-Hiraki/aws-security-audit-checker-scripts

```
aws-security-audit-checker-scripts/
├── check_security_hub_status.sh  # Security Hub チェックスクリプト
├── check_guardduty_status.sh     # GuardDuty チェックスクリプト
├── check_analyzer_status.sh      # Access Analyzer チェックスクリプト
├── accounts.list                 # チェック対象アカウント一覧
└── regions.list                  # チェック対象リージョン一覧
```

#### アカウントリスト

```text:accounts.list
123456789012
234567890123
345678901234
456789012345
```

#### リージョンリスト

```text:regions.list
us-east-1
us-east-2
us-west-1
us-west-2
ap-south-1
ap-northeast-1
ap-northeast-2
ap-northeast-3
ap-southeast-1
ap-southeast-2
ca-central-1
eu-central-1
eu-west-1
eu-west-2
eu-west-3
eu-north-1
sa-east-1
```

:::message alert
注意事項
ファイルの改行コードは必ず **LF**（Unix 形式）にしてください。
Windows 環境で作成する場合、改行コードが **CRLF** になってしまうと、スクリプトが正常に動作しない可能性があります。
:::

### Security Hub チェックスクリプト

```bash:check_security_hub_status.sh
#!/bin/bash

# --- 設定項目 ---
PROFILE_NAME="your-profile-name"
ASSUME_ROLE_NAME="YourAssumeRoleName"
ACCOUNT_FILE="./accounts.list"
REGION_FILE="./regions.list"

# 設定ファイルの存在チェック
if [[ ! -f "$ACCOUNT_FILE" ]]; then
    echo "エラー: アカウントリストファイル '$ACCOUNT_FILE' が見つかりません。" >&2
    exit 1
fi
if [[ ! -f "$REGION_FILE" ]]; then
    echo "エラー: リージョンリストファイル '$REGION_FILE' が見つかりません。" >&2
    exit 1
fi

# ファイルからアカウント ID とリージョンを配列に読み込む
mapfile -t TARGET_ACCOUNTS < "$ACCOUNT_FILE"
mapfile -t REGIONS < "$REGION_FILE"

# SSO ログインセッションを開始/更新
echo "IAM Identity Center のログインセッションを更新します..." >&2
aws sso login --profile ${PROFILE_NAME} >&2

# CSV ヘッダーを出力
echo "AccountId,Region,SecurityHubStatus"

# 各アカウントに対してループ処理
for ACCOUNT_ID in "${TARGET_ACCOUNTS[@]}"; do
  # 空行はスキップ
  [[ -z "$ACCOUNT_ID" ]] && continue

  echo "--- Checking Account: ${ACCOUNT_ID} ---" >&2
  ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ASSUME_ROLE_NAME}"

  # IAM Identity Center のプロファイルを使って AssumeRole を実行
  TEMP_CREDS=$(aws sts assume-role \
    --role-arn ${ROLE_ARN} \
    --role-session-name "SecurityHubCheck-$(date +%s)" \
    --profile ${PROFILE_NAME} \
    --output json)

  # assume-role に失敗した場合はスキップ
  if [ $? -ne 0 ]; then
    echo "${ACCOUNT_ID},ALL,FailedToAssumeRole"
    continue
  fi

  # 一時的な認証情報を環境変数にエクスポート
  export AWS_ACCESS_KEY_ID=$(echo $TEMP_CREDS | jq -r .Credentials.AccessKeyId)
  export AWS_SECRET_ACCESS_KEY=$(echo $TEMP_CREDS | jq -r .Credentials.SecretAccessKey)
  export AWS_SESSION_TOKEN=$(echo $TEMP_CREDS | jq -r .Credentials.SessionToken)

  # 各リージョンに対してループ処理
  for REGION in "${REGIONS[@]}"; do
    # 空行はスキップ
    [[ -z "$REGION" ]] && continue

    # Security Hub のステータスを確認
    if aws securityhub describe-hub --region ${REGION} > /dev/null 2>&1; then
      STATUS="ENABLED"
    else
      STATUS="DISABLED_OR_NOT_AVAILABLE"
    fi
    echo "${ACCOUNT_ID},${REGION},${STATUS}"
  done

  # 環境変数をクリア
  unset AWS_ACCESS_KEY_ID
  unset AWS_SECRET_ACCESS_KEY
  unset AWS_SESSION_TOKEN
done

echo "--- All checks completed. ---" >&2
```

### GuardDuty チェックスクリプト

```bash:check_guardduty_status.sh
#!/bin/bash

# --- 設定項目 ---
PROFILE_NAME="your-profile-name"
ASSUME_ROLE_NAME="YourAssumeRoleName"
ACCOUNT_FILE="./accounts.list"
REGION_FILE="./regions.list"

# --- スクリプト本体 ---
if [[ ! -f "$ACCOUNT_FILE" ]]; then
    echo "エラー: アカウントリストファイル '$ACCOUNT_FILE' が見つかりません。" >&2
    exit 1
fi
if [[ ! -f "$REGION_FILE" ]]; then
    echo "エラー: リージョンリストファイル '$REGION_FILE' が見つかりません。" >&2
    exit 1
fi

mapfile -t TARGET_ACCOUNTS < "$ACCOUNT_FILE"
mapfile -t REGIONS < "$REGION_FILE"

echo "IAM Identity Center のログインセッションを更新します..." >&2
aws sso login --profile ${PROFILE_NAME} >&2

echo "AccountId,Region,GuardDutyStatus"

for ACCOUNT_ID in "${TARGET_ACCOUNTS[@]}"; do
  [[ -z "$ACCOUNT_ID" ]] && continue
  echo "--- Checking GuardDuty on Account: ${ACCOUNT_ID} ---" >&2
  ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ASSUME_ROLE_NAME}"

  TEMP_CREDS=$(aws sts assume-role --role-arn ${ROLE_ARN} --role-session-name "GuardDutyCheck" --profile ${PROFILE_NAME} --output json)
  if [ $? -ne 0 ]; then
    echo "${ACCOUNT_ID},ALL,FailedToAssumeRole"
    continue
  fi

  export AWS_ACCESS_KEY_ID=$(echo $TEMP_CREDS | jq -r .Credentials.AccessKeyId)
  export AWS_SECRET_ACCESS_KEY=$(echo $TEMP_CREDS | jq -r .Credentials.SecretAccessKey)
  export AWS_SESSION_TOKEN=$(echo $TEMP_CREDS | jq -r .Credentials.SessionToken)

  for REGION in "${REGIONS[@]}"; do
    [[ -z "$REGION" ]] && continue
    
    # list-detectors で DetectorId のリストを取得し、その数が 0 より大きいか確認
    if aws guardduty list-detectors --region ${REGION} --output json | jq -e '.DetectorIds | length > 0' > /dev/null 2>&1; then
      STATUS="ENABLED"
    else
      STATUS="DISABLED"
    fi
    echo "${ACCOUNT_ID},${REGION},${STATUS}"
  done

  unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
done

echo "--- GuardDuty checks completed. ---" >&2
```

### IAM Access Analyzer チェックスクリプト

```bash:check_analyzer_status.sh
#!/bin/bash

# --- 設定項目 ---
PROFILE_NAME="your-profile-name"
ASSUME_ROLE_NAME="YourAssumeRoleName"
ACCOUNT_FILE="./accounts.list"
REGION_FILE="./regions.list"

# --- スクリプト本体 ---
if [[ ! -f "$ACCOUNT_FILE" ]]; then
    echo "エラー: アカウントリストファイル '$ACCOUNT_FILE' が見つかりません。" >&2
    exit 1
fi
if [[ ! -f "$REGION_FILE" ]]; then
    echo "エラー: リージョンリストファイル '$REGION_FILE' が見つかりません。" >&2
    exit 1
fi

mapfile -t TARGET_ACCOUNTS < "$ACCOUNT_FILE"
mapfile -t REGIONS < "$REGION_FILE"

echo "IAM Identity Center のログインセッションを更新します..." >&2
aws sso login --profile ${PROFILE_NAME} >&2

echo "AccountId,Region,AccessAnalyzerStatus"

for ACCOUNT_ID in "${TARGET_ACCOUNTS[@]}"; do
  [[ -z "$ACCOUNT_ID" ]] && continue
  echo "--- Checking IAM Access Analyzer on Account: ${ACCOUNT_ID} ---" >&2
  ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ASSUME_ROLE_NAME}"

  TEMP_CREDS=$(aws sts assume-role --role-arn ${ROLE_ARN} --role-session-name "AnalyzerCheck" --profile ${PROFILE_NAME} --output json)
  if [ $? -ne 0 ]; then
    echo "${ACCOUNT_ID},ALL,FailedToAssumeRole"
    continue
  fi

  export AWS_ACCESS_KEY_ID=$(echo $TEMP_CREDS | jq -r .Credentials.AccessKeyId)
  export AWS_SECRET_ACCESS_KEY=$(echo $TEMP_CREDS | jq -r .Credentials.SecretAccessKey)
  export AWS_SESSION_TOKEN=$(echo $TEMP_CREDS | jq -r .Credentials.SessionToken)

  for REGION in "${REGIONS[@]}"; do
    [[ -z "$REGION" ]] && continue

    # list-analyzers で ACCOUNT タイプのアナライザーリストを取得し、その数が 0 より大きいか確認
    if aws accessanalyzer list-analyzers --type ACCOUNT --region ${REGION} --output json | jq -e '.analyzers | length > 0' > /dev/null 2>&1; then
      STATUS="ENABLED"
    else
      STATUS="DISABLED"
    fi
    echo "${ACCOUNT_ID},${REGION},${STATUS}"
  done

  unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
done

echo "--- IAM Access Analyzer checks completed. ---" >&2
```

### 共通変数の設定

各スクリプトでは以下の共通変数を使用しています。実行前に環境に合わせて変更してください：

```bash
# --- 設定項目 ---
PROFILE_NAME="your-profile-name"            # IAM Identity Center のプロファイル名
ASSUME_ROLE_NAME="YourAssumeRoleName"       # 各アカウントのスイッチロール名（共通のスイッチロール名を使用することを前提）
ACCOUNT_FILE="./accounts.list"              # チェック対象アカウント一覧ファイル
REGION_FILE="./regions.list"                # チェック対象リージョン一覧ファイル
```

#### 変数の説明
- **PROFILE_NAME**: `aws configure sso` で設定したプロファイル名
- **ASSUME_ROLE_NAME**: 各アカウントに作成されたスイッチロール用の IAM ロール名
- **ACCOUNT_FILE**: チェック対象の AWS アカウント ID を記載したファイルパス
- **REGION_FILE**: チェック対象のリージョンを記載したファイルパス

### 実行方法

#### 1. IAM Identity Center の設定

まず、IAM Identity Center のプロファイルを設定する必要があります：

```bash
# IAM Identity Center プロファイルの設定
aws configure sso

# 以下の情報を入力します：
 SSO session name (Recommended): my-sso
 SSO start URL [None]: https://your-domain.awsapps.com/start
 SSO region [None]: ap-northeast-1
 SSO registration scopes [sso:account:access]: [Enter]
 
# 次に、使用するアカウントとロールを選択：
# There are X AWS accounts available to you.
# Using the account ID 123456789012
# The only role available to you is: PowerUserAccess
# Using the role name "PowerUserAccess"
 CLI default client Region [None]: [Enter]
 CLI default output format [None]: [Enter]
 CLI profile name [PowerUserAccess-123456789012]: your-profile-name

# 設定確認
aws configure list-profiles

# プロファイルでのログインテスト
aws sso login --profile your-profile-name
```

#### 必要な設定項目
- **SSO start URL**: IAM Identity Center のアクセスポータル URL
- **SSO region**: IAM Identity Center が有効化されているリージョン
- **プロファイル名**: スクリプト内の `PROFILE_NAME` と一致させる（例：`your-profile-name`）

#### 2. スクリプトの準備
```bash
# 実行権限を付与
chmod +x check_security_hub_status.sh check_guardduty_status.sh check_analyzer_status.sh

# 設定ファイルの編集（必要に応じて）
vi accounts.list  # チェック対象アカウントを記載
vi regions.list   # チェック対象リージョンを記載

# 各スクリプトの変数の編集（必要に応じて）
vi check_security_hub_status.sh
vi check_guardduty_status.sh
vi check_analyzer_status.sh
```

#### 3. スクリプトの実行
```bash
# Security Hub の状況確認
./check_security_hub_status.sh > security_hub_status.csv

# GuardDuty の状況確認
./check_guardduty_status.sh > guardduty_status.csv

# IAM Access Analyzer の状況確認
./check_analyzer_status.sh > analyzer_status.csv
```

### 出力例

各スクリプトを実行すると、以下のような CSV 形式で結果が出力されます：

#### Security Hub の出力例
```csv
AccountId,Region,SecurityHubStatus
123456789012,us-east-1,ENABLED
123456789012,us-east-2,DISABLED_OR_NOT_AVAILABLE
123456789012,ap-northeast-1,ENABLED
123456789012,ap-northeast-2,ENABLED
```

#### GuardDuty の出力例
```csv
AccountId,Region,GuardDutyStatus
123456789012,us-east-1,ENABLED
123456789012,us-east-2,ENABLED
123456789012,ap-northeast-1,ENABLED
123456789012,ap-northeast-2,DISABLED
```

#### IAM Access Analyzer の出力例
```csv
AccountId,Region,AccessAnalyzerStatus
123456789012,us-east-1,ENABLED
123456789012,us-east-2,DISABLED
123456789012,ap-northeast-1,ENABLED
123456789012,ap-northeast-2,DISABLED
```

#### 出力結果の見方
- **AccountId**: チェック対象の AWS アカウント ID
- **Region**: チェック対象のリージョン
- **各サービスの Status**: 各セキュリティサービスの状態
  - `ENABLED`: サービスが有効化されている
  - `DISABLED` / `DISABLED_OR_NOT_AVAILABLE`: サービスが無効またはサポートされていない
  - `FailedToAssumeRole`: スイッチロールに失敗（権限不足など）

## 制約事項

### IAM Identity Center の制約
- **セッション有効期限**: IAM Identity Center のセッションには有効期限があるため、長時間の実行時は再認証が必要
- **プロファイル設定**: 事前に `aws configure sso` でプロファイルの設定が必要

### スイッチロール の制約
- **ロール権限**: 各アカウントに適切なスイッチロール用のロールが作成されている必要がある
- **信頼関係**: IAM Identity Center のアカウントからのスイッチロールが許可されている必要がある

## おわりに

今回は、IAM Identity Center を使用して複数 AWS アカウントの Security Hub 有効化状況をチェックするスクリプトを作成しました。

複数アカウント環境でのセキュリティサービスのチェックにぜひご活用ください。

この記事がどなたかの役に立つと嬉しいです。

---

この記事は Qiita から移行しました。
