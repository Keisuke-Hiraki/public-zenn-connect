---
title: "新しく登場した AWS MCP Server と IAM Policy Autopilot を使用して高速で AWS リソースの構築とそれに必要な IAM ポリシーの分析をしてみた"
emoji: "🔍"
type: "tech"
topics: ["aws", "mcp", "iam"]
published: true
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

本日のアップデートにて、AWS MCP Server と IAM Policy Autopilot というものが発表されました。

この 2 種類のアップデートの登場により、AI を用いて思い描いた AWS 環境の構築がスピーディーかつハイクオリティにできるようになったのかなと感じたため執筆しました。
この 2 種類のアップデートと実際にやってみた内容をご紹介します。

## AWS MCP Server とは

AWS の MCP サーバー自体は今までいくつもありました。

今回の違いとして AWS 公式のフルマネージドなリモート MCP サーバーとして登場したという点です。

AWS Knowledge MCP と AWS API MCP を統合した 1 つの MCP として構成されているため、
今までこの 2 種類を使っていた方はもうこちらへ切り替えたほうが良さそうです。

https://docs.aws.amazon.com/aws-mcp/latest/userguide/what-is-mcp-server.html

### AWS MCP Server の利用方法

今回は、Kiro CLI の利用を想定して記載します。  
各 MCP クライアントで大きな違いはありませんが、公式ドキュメントをご参照ください。

まず既存で以下 2 種類を使用していた方は `mcp.json` などからそのエントリを削除しましょう。

- aws-api-mcp-server
- aws-knowledge-mcp-server

次に、代わりに以下を `mcp.json`に挿入します。

```json
{
  "mcpServers": {
    "aws-mcp": {
      "command": "uvx",
      "timeout": 100000,
      "transport": "stdio",
      "args": [
        "mcp-proxy-for-aws@latest",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--metadata", "AWS_REGION=ap-northeast-1"
      ]
    }
  }
}
```

` "--metadata", "AWS_REGION=ap-northeast-1"` はリージョンの指定でありオプションのため削っても別のリージョンを指定しても問題ないです。
デフォルトでは、 `us-east-1` になります。

## IAM Policy Autopilot とは

アプリケーションを EC2 や Lambda などへデプロイし、IAM ポリシーを適用する際に、権限が微妙に足りずエラーがたびたび発生してもどかしい思いをしたことはありませんか？

そんな悩みを高速で解決できるのがこの IAM Policy Autopilot で、  
アプリケーションのコードなどから必要な権限を分析し、適用すべき IAM ポリシーを提案してくれます。

リリース日の現時点（2025/12/01）では以下の言語で作成されたコードに対応しています。

- Python
- Go
- Typescript

IAM Policy Autopilot は、現在 MCP と CLI ツールの 2 種類で使用できるようになっているため、
今回は、先ほどの AWS MCP Server との掛け合わせで使用してみたいと思います。

https://aws.amazon.com/jp/blogs/aws/simplify-iam-policy-creation-with-iam-policy-autopilot-a-new-open-source-mcp-server-for-builders/

https://github.com/awslabs/iam-policy-autopilot

### IAM Policy Autopilot (MCP 版) の利用方法

今回は、Kiro CLI の利用を想定して記載します。  
各 MCP クライアントであまり大して変わらないですが、公式ドキュメントをご参照ください。

IAM Policy Autopilot を使用するには、以下のコマンドを実行します。

```bash:uv/uvx を使用する場合
kiro-cli mcp add \
  --name iam-policy-autopilot \
  --command "uvx" \
  --args "iam-policy-autopilot","mcp-server"
```

または

```bash:pip を使用する場合
kiro-cli mcp add \
  --name iam-policy-autopilot \
  --command "iam-policy-autopilot" \
  --args "mcp-server"
```

## やってみた

では、実際に AWS MCP Server と IAM Policy Autopilot を使用してみます。

今回は、既存の `keisuke-poc-vpc` というリソースを調査させ、EC2 と SNS トピックを作成する CloudFormation テンプレートを生成してもらいました。  
また、S3 のファイルの中身を処理し SNS で通知する Lambda の Python コードから必要な IAM ポリシーを提案してもらう部分をやってみました。

![](/images/aws-mcp-server-iam-policy-autopilot_2025-12-01-20-42-36.png)

今回は、Kiro CLI を使用し 2 つの MCP を事前に設定しておいたので以下のような画面でスタートします。  
`/mcp` から 2 つの MCP が設定されていることが分かります。

![](/images/aws-mcp-server-iam-policy-autopilot_2025-12-01-20-43-28.png)

:::message
事前に AWS の認証情報の設定は必要なので、`aws configure`または`aws configure sso`や環境変数などで認証情報をセットしておいてください。
:::

準備は整っているので早速以下のように指示してみます。

```
これからあなたには既存の VPC 環境に EC2 とメール通知を行う Amazon SNS を作成する CloudFormation テンプレートを生成し、AWS 環境に作成いただきます。\
AWS の MCP を利用し、既存の VPC から keisuke-poc という名前を含むものを調査し、その VPC を使用するようにしてください。\
EC2 は Amazon Linux 2023 を利用してください。\
EC2 から Amazon SNS 経由で通知と SNS のサブスクリプションを変更できる権限を IAM Policy Autopilot で作成してください。
```

するとまず、構築に必要な VPC を検索され、

![](/images/aws-mcp-server-iam-policy-autopilot_2025-12-01-20-47-51.png)

想定されるアプリケーションのコードから、IAM Policy Autopilot を使用して IAM ポリシーを分析してくれています。

![](/images/aws-mcp-server-iam-policy-autopilot_2025-12-01-20-49-28.png)

結果、以下のような CloudFormation テンプレートを生成し、AWS にもデプロイしてくれました。

```yml
AWSTemplateFormatVersion: '2010-09-09'
Description: EC2 instance with SNS notification capabilities

Parameters:
  VpcId:
    Type: String
    Default: vpc-0f993a9524be81212
  SubnetId:
    Type: String
    Default: subnet-043c03fd92df643ba
  EmailAddress:
    Type: String
    Description: Email address for SNS notifications

Resources:
  SNSTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: ec2-notification-topic
      Subscription:
        - Endpoint: !Ref EmailAddress
          Protocol: email

  EC2SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for EC2 instance
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0

  EC2InstanceRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: SNSAccessPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - kms:Decrypt
                  - kms:GenerateDataKey
                Resource: !Sub 'arn:aws:kms:${AWS::Region}:${AWS::AccountId}:key/*'
                Condition:
                  StringEquals:
                    kms:ViaService: !Sub 'sns.${AWS::Region}.amazonaws.com'
              - Effect: Allow
                Action:
                  - sns:Publish
                  - sns:Subscribe
                Resource: !Sub 'arn:aws:sns:${AWS::Region}:${AWS::AccountId}:*'
              - Effect: Allow
                Action: iam:PassRole
                Resource: '*'
                Condition:
                  StringEquals:
                    iam:PassedToService: sns.amazonaws.com
              - Effect: Allow
                Action: sns:Unsubscribe
                Resource: '*'

  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref EC2InstanceRole

  EC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-03852a41f1e05c8e4
      InstanceType: t3.micro
      IamInstanceProfile: !Ref EC2InstanceProfile
      SecurityGroupIds:
        - !Ref EC2SecurityGroup
      SubnetId: !Ref SubnetId
      Tags:
        - Key: Name
          Value: ec2-sns-instance

Outputs:
  InstanceId:
    Description: EC2 Instance ID
    Value: !Ref EC2Instance
  SNSTopicArn:
    Description: SNS Topic ARN
    Value: !Ref SNSTopic
```

::: details やり取りの全文を見たい場合はこちらを展開

```
> これからあなたには既存の VPC 環境に EC2 とメール通知を行う Amazon SNS を作成する CloudFormation テンプレートを生成し、AWS 環境に作成いただきます。\
AWS の MCP を利用し、既存の VPC から keisuke-poc という名前を含むものを調査し、その VPC を使用するようにしてください。\
EC2 は Amazon Linux 2023 を利用してください。\
EC2 から Amazon SNS 経由で通知と SNS のサブスクリプションを変更できる権限を IAM Policy Autopilot で作成してください。

> 既存の VPC 環境を調査して、EC2 と SNS を含む CloudFormation テンプレートを作成します。まず、keisuke-poc という名前を含む VPC を探します。
Running tool aws___call_aws with the param (from mcp server: aws-mcp)
 ⋮  {
 ⋮    "cli_command": "aws ec2 describe-vpcs --filters Name=tag:Name,Values=*keisuke-poc*"
 ⋮  }

Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:

> y

 - Completed in 11.625s

Running tool aws___call_aws with the param (from mcp server: aws-mcp)
 ⋮  {
 ⋮    "cli_command": "aws ec2 describe-vpcs"
 ⋮  }

Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:

> t

 - Completed in 5.511s

> keisuke-poc-vpc を見つけました（VPC ID: vpc-0123456789abcdef0）。次に、この VPC のサブネットを確認します。
Running tool aws___call_aws with the param (from mcp server: aws-mcp)
 ⋮  {
 ⋮    "cli_command": "aws ec2 describe-subnets --filters Name=vpc-id,Values=vpc-0123456789abcdef0"
 ⋮  }
 - Completed in 5.319s

> 次に、Amazon Linux 2023 の最新 AMI ID を取得します。
Running tool aws___call_aws with the param (from mcp server: aws-mcp)
 ⋮  {
 ⋮    "cli_command": "aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text"
 ⋮  }
 - Completed in 6.112s

> 現在のリージョンとアカウント ID を確認します。
Running tool aws___call_aws with the param (from mcp server: aws-mcp)
 ⋮  {
 ⋮    "cli_command": "aws sts get-caller-identity"
 ⋮  }
 - Completed in 6.53s

> それでは、EC2 から SNS を操作するためのサンプルコードを作成し、IAM Policy Autopilot でポリシーを生成します。
I'll create the following file: /home/user/work/ec2_sns_sample.py (using tool: write)
Purpose: EC2 から SNS を操作するサンプルコード

+     1: import boto3
+     2:
+     3: sns = boto3.client('sns')
+     4:
+     5: # SNS トピックへの通知
+     6: sns.publish(
+     7:     TopicArn='arn:aws:sns:ap-northeast-1:123456789012:example-topic',
+     8:     Message='Test message'
+     9: )
+    10:
+    11: # SNS サブスクリプションの変更
+    12: sns.subscribe(
+    13:     TopicArn='arn:aws:sns:ap-northeast-1:123456789012:example-topic',
+    14:     Protocol='email',
+    15:     Endpoint='example@example.com'
+    16: )
+    17:
+    18: sns.unsubscribe(
+    19:     SubscriptionArn='arn:aws:sns:ap-northeast-1:123456789012:example-topic:subscription-id'
+    20: )


Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:

> t

Creating: /home/user/work/ec2_sns_sample.py
 - Completed in 0.3s

Running tool generate_application_policies with the param (from mcp server: iam-policy-autopilot)
 ⋮  {
 ⋮    "SourceFiles": [
 ⋮      "/home/user/work/ec2_sns_sample.py"
 ⋮    ],
 ⋮    "Region": "ap-northeast-1",
 ⋮    "Account": "123456789012",
 ⋮    "ServiceHints": [
 ⋮      "sns"
 ⋮    ]
 ⋮  }

Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:

> t

 - Completed in 1.330s

> IAM Policy Autopilot でポリシーが生成されました。このポリシーを確認してください：

json
{
  "Id": "IamPolicyAutopilot",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": [
        "arn:aws:kms:ap-northeast-1:123456789012:key/*"
      ],
      "Condition": {
        "StringEquals": {
          "kms:ViaService": [
            "sns.ap-northeast-1.amazonaws.com"
          ]
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish",
        "sns:Subscribe"
      ],
      "Resource": [
        "arn:aws:sns:ap-northeast-1:123456789012:*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:PassRole"
      ],
      "Resource": [
        "*"
      ],
      "Condition": {
        "StringEquals": {
          "iam:PassedToService": [
            "sns.amazonaws.com"
          ]
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Unsubscribe"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}


このポリシーで問題なければ、CloudFormation テンプレートを作成します。よろしいですか？
 ▸ Credits: 0.57 • Time: 1m 53s

> 作成してください

> CloudFormation テンプレートを作成します。
I'll create the following file: /home/user/work/ec2-sns-stack.yaml (using tool: write)
Purpose: EC2 と SNS の CloudFormation テンプレート作成

+     1: AWSTemplateFormatVersion: '2010-09-09'
+     2: Description: EC2 instance with SNS notification capabilities
+     3:
+     4: Parameters:
+     5:   VpcId:
+     6:     Type: String
+     7:     Default: vpc-0123456789abcdef0
+     8:   SubnetId:
+     9:     Type: String
+    10:     Default: subnet-0123456789abcdef0
+    11:   EmailAddress:
+    12:     Type: String
+    13:     Description: Email address for SNS notifications
+    14:
+    15: Resources:
+    16:   SNSTopic:
+    17:     Type: AWS::SNS::Topic
+    18:     Properties:
+    19:       TopicName: ec2-notification-topic
+    20:       Subscription:
+    21:         - Endpoint: !Ref EmailAddress
+    22:           Protocol: email
+    23:
+    24:   EC2SecurityGroup:
+    25:     Type: AWS::EC2::SecurityGroup
+    26:     Properties:
+    27:       GroupDescription: Security group for EC2 instance
+    28:       VpcId: !Ref VpcId
+    29:       SecurityGroupIngress:
+    30:         - IpProtocol: tcp
+    31:           FromPort: 22
+    32:           ToPort: 22
+    33:           CidrIp: 0.0.0.0/0
+    34:
+    35:   EC2InstanceRole:
+    36:     Type: AWS::IAM::Role
+    37:     Properties:
+    38:       AssumeRolePolicyDocument:
+    39:         Version: '2012-10-17'
+    40:         Statement:
+    41:           - Effect: Allow
+    42:             Principal:
+    43:               Service: ec2.amazonaws.com
+    44:             Action: sts:AssumeRole
+    45:       Policies:
+    46:         - PolicyName: SNSAccessPolicy
+    47:           PolicyDocument:
+    48:             Version: '2012-10-17'
+    49:             Statement:
+    50:               - Effect: Allow
+    51:                 Action:
+    52:                   - kms:Decrypt
+    53:                   - kms:GenerateDataKey
+    54:                 Resource: !Sub 'arn:aws:kms:${AWS::Region}:${AWS::AccountId}:key/*'
+    55:                 Condition:
+    56:                   StringEquals:
+    57:                     kms:ViaService: !Sub 'sns.${AWS::Region}.amazonaws.com'
+    58:               - Effect: Allow
+    59:                 Action:
+    60:                   - sns:Publish
+    61:                   - sns:Subscribe
+    62:                 Resource: !Sub 'arn:aws:sns:${AWS::Region}:${AWS::AccountId}:*'
+    63:               - Effect: Allow
+    64:                 Action: iam:PassRole
+    65:                 Resource: '*'
+    66:                 Condition:
+    67:                   StringEquals:
+    68:                     iam:PassedToService: sns.amazonaws.com
+    69:               - Effect: Allow
+    70:                 Action: sns:Unsubscribe
+    71:                 Resource: '*'
+    72:
+    73:   EC2InstanceProfile:
+    74:     Type: AWS::IAM::InstanceProfile
+    75:     Properties:
+    76:       Roles:
+    77:         - !Ref EC2InstanceRole
+    78:
+    79:   EC2Instance:
+    80:     Type: AWS::EC2::Instance
+    81:     Properties:
+    82:       ImageId: ami-0123456789abcdef0
+    83:       InstanceType: t3.micro
+    84:       IamInstanceProfile: !Ref EC2InstanceProfile
+  85:       SecurityGroupIds:
+    86:         - !Ref EC2SecurityGroup
+    87:       SubnetId: !Ref SubnetId
+    88:       Tags:
+    89:         - Key: Name
+    90:           Value: ec2-sns-instance
+    91:
+    92: Outputs:
+    93:   InstanceId:
+    94:     Description: EC2 Instance ID
+    95:     Value: !Ref EC2Instance
+    96:   SNSTopicArn:
+    97:     Description: SNS Topic ARN
+    98:     Value: !Ref SNSTopic

Creating: /home/user/work/ec2-sns-stack.yaml
 - Completed in 0.0s

> CloudFormation テンプレートを作成しました。次にスタックをデプロイします。メール通知用のメールアドレスを教えてください。
 ▸ Credits: 0.22 • Time: 14s

> user@example.com を使用してください、

> CloudFormation スタックをデプロイします。
Running tool aws___call_aws with the param (from mcp server: aws-mcp)
 ⋮  {
 ⋮    "cli_command": "aws cloudformation create-stack --stack-name ec2-sns-stack --template-body file:///home/user/work/ec2-sns-stack.yaml --parameters ParameterKey=EmailAddress,ParameterValue=user@example.com --capabilities CAPABILITY_IAM"
 ⋮  }
 - Completed in 5.891s

I will run the following command: aws cloudformation create-stack --stack-name ec2-sns-stack --template-body file:///home/user/work/ec2-sns-stack.yaml --parameters ParameterKey=EmailAddress,ParameterValue=user@example.com --capabilities CAPABILITY_IAM --region ap-northeast-1 (using tool: shell)
Purpose: CloudFormation スタックのデプロイ


Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:

> y

{
    "StackId": "arn:aws:cloudformation:ap-northeast-1:123456789012:stack/ec2-sns-stack/12345678-1234-1234-1234-1234567890ab"
}
 - Completed in 1.221s

> スタックの作成が開始されました。ステータスを確認します。
I will run the following command: aws cloudformation describe-stacks --stack-name ec2-sns-stack --region ap-northeast-1 --query 'Stacks[0].StackStatus' --output text (using tool: shell)
Purpose: スタック作成状況の確認


Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:

> y

CREATE_IN_PROGRESS
 - Completed in 0.912s

I will run the following command: aws cloudformation wait stack-create-complete --stack-name ec2-sns-stack --region ap-northeast-1 && echo "Stack creation completed successfully" (using tool: shell)
Purpose: スタック作成完了まで待機


Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:

> y

Stack creation completed successfully
 - Completed in 0.702s

I will run the following command: aws cloudformation describe-stacks --stack-name ec2-sns-stack --region ap-northeast-1 --query 'Stacks[0].Outputs' --output table (using tool: shell)
Purpose: スタックの出力情報を取得


Allow this action? Use 't' to trust (always allow) this tool for the session. [y/n/t]:

> y

------------------------------------------------------------------------------------------------------  
|                                           DescribeStacks                                           |  
+-----------------+--------------+-------------------------------------------------------------------+  
|   Description   |  OutputKey   |                            OutputValue                            |  
+-----------------+--------------+-------------------------------------------------------------------+  
|  EC2 Instance ID|  InstanceId  |  i-0123456789abcdef0                                              |  
|  SNS Topic ARN  |  SNSTopicArn |  arn:aws:sns:ap-northeast-1:123456789012:ec2-notification-topic   |  
+-----------------+--------------+-------------------------------------------------------------------+  
 - Completed in 0.615s

> CloudFormation スタックのデプロイが完了しました！

作成されたリソース：
- **EC2 インスタンス**: i-0123456789abcdef0 (Amazon Linux 2023)
- **SNS トピック**: arn:aws:sns:ap-northeast-1:123456789012:ec2-notification-topic
- **VPC**: vpc-0123456789abcdef0 (keisuke-poc-vpc)
- **サブネット**: subnet-0123456789abcdef0 (public subnet)

EC2 インスタンスには、IAM Policy Autopilot で生成したポリシーが適用されており、以下の操作が可能です：
- SNS トピックへのメッセージ送信 (sns:Publish)
- SNS サブスクリプションの作成 (sns:Subscribe)
- SNS サブスクリプションの削除 (sns:Unsubscribe)
- KMS 暗号化された SNS トピックへのアクセス

user@example.com 宛に SNS サブスクリプション確認メールが送信されているので、確認してサブスクリプションを承認してください。
 ▸ Credits: 0.41 • Time: 4m 14s
```

:::

続いて Lambda のコードから必要な IAM ポリシーも分析してみてもらいました。

Lambda のサンプルコードが以下です。

```python
import boto3
import csv
from io import StringIO

s3 = boto3.client('s3')
sns = boto3.client('sns')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    response = s3.get_object(Bucket=bucket, Key=key)
    csv_content = response['Body'].read().decode('utf-8')
    
    reader = csv.DictReader(StringIO(csv_content))
    total_cost = sum(float(row['cost']) for row in reader)
    
    message = f"File: s3://{bucket}/{key}\nTotal Cost: {total_cost}"
    
    sns.publish(
        TopicArn='arn:aws:sns:ap-northeast-1:012345678912:ec2-notification-topic',
        Subject='S3 CSV Cost Summary',
        Message=message
    )
    
    return {'statusCode': 200, 'body': f'Total cost: {total_cost}'}
```

パッと見、S3 や SNS の権限が必要そうだなとは思いますが、実際はなんの API が必要かなど調べるのも面倒かと思います。

そのため Kiro にて以下のように問い合わせると

```
lambda_function.py の中身を参照し、IAM Policy Autopilot を使用して必要な IAM ポリシーを分析してください
```

以下のような IAM ポリシーが必要だと提案してくれました。

```json
{
  "Id": "IamPolicyAutopilot",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt"
      ],
      "Resource": [
        "arn:aws:kms:ap-northeast-1:012345678912:key/*"
      ],
      "Condition": {
        "StringEquals": {
          "kms:ViaService": [
            "s3.ap-northeast-1.amazonaws.com"
          ]
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectLegalHold",
        "s3:GetObjectRetention",
        "s3:GetObjectTagging",
        "s3:GetObjectVersion"
      ],
      "Resource": [
        "arn:aws:s3:::*/*",
        "arn:aws:s3:ap-northeast-1:012345678912:accesspoint/*/object/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3-object-lambda:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::*/*",
        "arn:aws:s3:ap-northeast-1:012345678912:accesspoint/*/object/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": [
        "arn:aws:kms:ap-northeast-1:012345678912:key/*"
      ],
      "Condition": {
        "StringEquals": {
          "kms:ViaService": [
            "sns.ap-northeast-1.amazonaws.com"
          ]
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": [
        "arn:aws:sns:ap-northeast-1:012345678912:*"
      ]
    }
  ]
}
```

若干 KMS や S3 Object Lambda に関する権限など、今回は不要と思われるものが含まれていますが、
必要な権限については充足していそうです。

このように、IAM Policy Autopilot を使用することで、アプリケーションコードから必要な IAM ポリシーを簡単に分析・生成できることが分かりました。

## まとめ

今回は、新しく登場した AWS MCP Server と IAM Policy Autopilot について見ていきました。

IAM Policy Autopilot に関しては CLI ツールもあるため、
例えば CI/CD パイプラインに IAM Access Analyzer のカスタムポリシーチェックと IAM Policy Autopilot を組み合わせることで、アプリケーションに必要なポリシーのチェックの過不足を自動で検証し、最小権限の原則の適用の自動化のクオリティが向上するのではないでしょうか。

この記事がどなたかの役に立つと嬉しいです。