---
title: "AWS Security Agentを組織で活用していく上での考慮点を考えてみた"
emoji: "🔐"
type: "tech"
topics: ["aws", "securityagent"]
published: true
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

2026年3月、AWS Security Agent がGAリリースされました。設計レビュー・コードレビュー・ペネトレーションテストをAIエージェントが一気通貫で担うというかなり先進的なサービスです。

https://aws.amazon.com/jp/about-aws/whats-new/2026/03/aws-security-agent-ondemand-penetration/

本ブログでは、まず OWASP Juice Shop を ECS Fargate に構築してペネトレーションテストを実際に実行した「やってみた」感想と、組織でこのサービスを本格活用していくうえで現時点で見えている考慮点・注意点を整理します。

## まずはやってみた

### 構成概要

意図的に脆弱性を含む学習用アプリ [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/) を ECS Fargate でホストし、ALB 経由で公開した構成でテストしてみました。

- **VPC**: パブリック/プライベートサブネット構成
- **ALB**: インターネット向け、IP制限あり
- **ECS Fargate**: Juice Shop コンテナをプライベートサブネットで稼働
- **NAT Gateway**: コンテナのアウトバウンド通信用

:::message
ペネトレーションテストは本番環境には実施しないでください。本ブログでも検証専用の非本番環境を使用しています。
:::

今回使用した CloudFormation テンプレートはこちらです。参考にしてください。

:::details juice-shop-cfn.yaml（全文）

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: OWASP Juice Shop on ECS Fargate

Parameters:
    AllowedIP:
        Type: String

Resources:
    # VPC
    VPC:
        Type: AWS::EC2::VPC
        Properties:
            CidrBlock: 10.0.0.0/16
            EnableDnsSupport: true
            EnableDnsHostnames: true
            Tags:
                - Key: Name
                  Value: juice-shop-vpc

    InternetGateway:
        Type: AWS::EC2::InternetGateway

    IGWAttachment:
        Type: AWS::EC2::VPCGatewayAttachment
        Properties:
            VpcId: !Ref VPC
            InternetGatewayId: !Ref InternetGateway

    # Public Subnets
    PublicSubnet1:
        Type: AWS::EC2::Subnet
        Properties:
            VpcId: !Ref VPC
            CidrBlock: 10.0.1.0/24
            AvailabilityZone: !Select [0, !GetAZs ""]
            MapPublicIpOnLaunch: true
            Tags:
                - Key: Name
                  Value: juice-shop-public-1

    PublicSubnet2:
        Type: AWS::EC2::Subnet
        Properties:
            VpcId: !Ref VPC
            CidrBlock: 10.0.2.0/24
            AvailabilityZone: !Select [1, !GetAZs ""]
            MapPublicIpOnLaunch: true
            Tags:
                - Key: Name
                  Value: juice-shop-public-2

    PublicRouteTable:
        Type: AWS::EC2::RouteTable
        Properties:
            VpcId: !Ref VPC

    PublicRoute:
        Type: AWS::EC2::Route
        DependsOn: IGWAttachment
        Properties:
            RouteTableId: !Ref PublicRouteTable
            DestinationCidrBlock: 0.0.0.0/0
            GatewayId: !Ref InternetGateway

    PublicSubnet1RTA:
        Type: AWS::EC2::SubnetRouteTableAssociation
        Properties:
            SubnetId: !Ref PublicSubnet1
            RouteTableId: !Ref PublicRouteTable

    PublicSubnet2RTA:
        Type: AWS::EC2::SubnetRouteTableAssociation
        Properties:
            SubnetId: !Ref PublicSubnet2
            RouteTableId: !Ref PublicRouteTable

    # NAT Gateway
    NatEIP:
        Type: AWS::EC2::EIP
        Properties:
            Domain: vpc

    NatGateway:
        Type: AWS::EC2::NatGateway
        Properties:
            AllocationId: !GetAtt NatEIP.AllocationId
            SubnetId: !Ref PublicSubnet1

    # Private Subnets
    PrivateSubnet1:
        Type: AWS::EC2::Subnet
        Properties:
            VpcId: !Ref VPC
            CidrBlock: 10.0.10.0/24
            AvailabilityZone: !Select [0, !GetAZs ""]
            Tags:
                - Key: Name
                  Value: juice-shop-private-1

    PrivateSubnet2:
        Type: AWS::EC2::Subnet
        Properties:
            VpcId: !Ref VPC
            CidrBlock: 10.0.11.0/24
            AvailabilityZone: !Select [1, !GetAZs ""]
            Tags:
                - Key: Name
                  Value: juice-shop-private-2

    PrivateRouteTable:
        Type: AWS::EC2::RouteTable
        Properties:
            VpcId: !Ref VPC

    PrivateRoute:
        Type: AWS::EC2::Route
        Properties:
            RouteTableId: !Ref PrivateRouteTable
            DestinationCidrBlock: 0.0.0.0/0
            NatGatewayId: !Ref NatGateway

    PrivateSubnet1RTA:
        Type: AWS::EC2::SubnetRouteTableAssociation
        Properties:
            SubnetId: !Ref PrivateSubnet1
            RouteTableId: !Ref PrivateRouteTable

    PrivateSubnet2RTA:
        Type: AWS::EC2::SubnetRouteTableAssociation
        Properties:
            SubnetId: !Ref PrivateSubnet2
            RouteTableId: !Ref PrivateRouteTable

    # Security Groups
    ALBSecurityGroup:
        Type: AWS::EC2::SecurityGroup
        Properties:
            GroupDescription: ALB SG - restricted to allowed IP
            VpcId: !Ref VPC
            SecurityGroupIngress:
                - IpProtocol: tcp
                  FromPort: 80
                  ToPort: 80
                  CidrIp: !Ref AllowedIP

    ECSSecurityGroup:
        Type: AWS::EC2::SecurityGroup
        Properties:
            GroupDescription: ECS SG - allow from ALB only
            VpcId: !Ref VPC
            SecurityGroupIngress:
                - IpProtocol: tcp
                  FromPort: 3000
                  ToPort: 3000
                  SourceSecurityGroupId: !Ref ALBSecurityGroup

    # ALB
    ALB:
        Type: AWS::ElasticLoadBalancingV2::LoadBalancer
        Properties:
            Name: juice-shop-alb
            Scheme: internet-facing
            Subnets:
                - !Ref PublicSubnet1
                - !Ref PublicSubnet2
            SecurityGroups:
                - !Ref ALBSecurityGroup

    TargetGroup:
        Type: AWS::ElasticLoadBalancingV2::TargetGroup
        Properties:
            Name: juice-shop-tg
            Port: 3000
            Protocol: HTTP
            VpcId: !Ref VPC
            TargetType: ip
            HealthCheckPath: /
            HealthCheckIntervalSeconds: 30
            HealthyThresholdCount: 2
            UnhealthyThresholdCount: 3

    Listener:
        Type: AWS::ElasticLoadBalancingV2::Listener
        Properties:
            LoadBalancerArn: !Ref ALB
            Port: 80
            Protocol: HTTP
            DefaultActions:
                - Type: forward
                  TargetGroupArn: !Ref TargetGroup

    # ECS
    ECSCluster:
        Type: AWS::ECS::Cluster
        Properties:
            ClusterName: juice-shop-cluster

    TaskExecutionRole:
        Type: AWS::IAM::Role
        Properties:
            AssumeRolePolicyDocument:
                Version: "2012-10-17"
                Statement:
                    - Effect: Allow
                      Principal:
                          Service: ecs-tasks.amazonaws.com
                      Action: sts:AssumeRole
            ManagedPolicyArns:
                - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

    LogGroup:
        Type: AWS::Logs::LogGroup
        Properties:
            LogGroupName: /ecs/juice-shop
            RetentionInDays: 7

    TaskDefinition:
        Type: AWS::ECS::TaskDefinition
        Properties:
            Family: juice-shop
            Cpu: "512"
            Memory: "1024"
            NetworkMode: awsvpc
            RequiresCompatibilities:
                - FARGATE
            ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
            ContainerDefinitions:
                - Name: juice-shop
                  Image: bkimminich/juice-shop:latest
                  PortMappings:
                      - ContainerPort: 3000
                  LogConfiguration:
                      LogDriver: awslogs
                      Options:
                          awslogs-group: !Ref LogGroup
                          awslogs-region: !Ref AWS::Region
                          awslogs-stream-prefix: ecs

    ECSService:
        Type: AWS::ECS::Service
        DependsOn: Listener
        Properties:
            Cluster: !Ref ECSCluster
            ServiceName: juice-shop-service
            TaskDefinition: !Ref TaskDefinition
            DesiredCount: 1
            LaunchType: FARGATE
            NetworkConfiguration:
                AwsvpcConfiguration:
                    Subnets:
                        - !Ref PrivateSubnet1
                        - !Ref PrivateSubnet2
                    SecurityGroups:
                        - !Ref ECSSecurityGroup
                    AssignPublicIp: DISABLED
            LoadBalancers:
                - ContainerName: juice-shop
                  ContainerPort: 3000
                  TargetGroupArn: !Ref TargetGroup

Outputs:
    JuiceShopURL:
        Description: Juice Shop URL
        Value: !Sub http://${ALB.DNSName}
```

:::

セットアップからペネトレーションテスト実行までの手順は以下のスクラップで簡易的に記載しているので参考にしてみてください。

https://zenn.dev/khirasan/scraps/3c77af32cc5f7a

セットアップで特に詰まったポイントとして、**Security AgentのVPC/サブネット設定**があります。最初パブリックサブネットの指定で失敗し、設定を見直してようやくテストできました。

### テスト結果

![](/images/security-agent-ga-organization_2026-04-02_04h49_08.png)

今回の実行結果のサマリーです。

| 項目 | 値 |
|------|-----|
| 総実行時間 | 3時間37分32秒 |
| 推定コスト | 約 $181（$50/タスク時間） |
| 無料トライアル | 新規顧客は最大200時間・2ヶ月間無料 |

Juice Shop は意図的に多数の脆弱性を仕込んだアプリです。実際に検出された脆弱性の種類や重大度のスクリーンショットは上記の通りです。

:::message
所見の説明は現時点では英語のみです。日本語への対応を期待したいところです。
:::

## 組織で活用していくうえでの考慮点

GAされた AWS Security Agent を組織のセキュリティ基盤として活用していくにあたり、**権限設計・データ管理・運用ルール・コスト制御**の観点で整理しました。

### データ処理地域とコンプライアンス

- **モデルトレーニングへのデータ利用**：なし。顧客データは AWS の学習に使用されない
- **サードパーティへのデータ共有**：なし
- **保管時暗号化**：テスト結果・所見・ログはすべて AWS KMS で暗号化
- **クロスリージョン推論（Cross-Region Inference）**：自動的に有効になっており、無効化不可

#### 日本のリージョン利用時の処理基盤は？

公式ドキュメントによれば、 **日本国内で発生した推論要求は、日本国内で処理されます。** と明記されています。
https://docs.aws.amazon.com/securityagent/latest/userguide/security-best-practices.html#_cross_region_inference

したがって、「国内処理」要件がある顧客も適合できます。

:::message alert
SCP や IAM ポリシーでクロスリージョンアクセスを過度に制限していると、推論処理やサービス全体の動作に支障が出る可能性があります。Security Agent を導入する前に、関連リージョンへのアクセスが通っているかを確認してください。
:::

### ID・アクセス管理の設計

セットアップ時に選ぶアクセス方式は後から変更できない点に注意が必要です。

エージェントスペースのセットアップ時に「IAM Identity Center（SSO）」か「IAM 専用アクセス」かを選択しますが、**後から変更するにはエージェントスペースを削除して再作成する必要があります**。
組織全体への展開前に、どちらの方式で統一するかを先に決めてください。

また、IAM Identity Centerを選択する場合はリージョンに注意する必要があります。

アプリケーション、エージェントスペース、IAM Identity Centerの組織インスタンスが全て東京リージョンなど同一である場合は問題ありませんが、いずれかが異なるリージョンの場合は変わってきます。

- まず、アプリケーションはIAM Identity Centerを有効にするリージョンと同じリージョンである必要があります。
- また、IAM Identity Centerはエージェントスペースを有効にするリージョンと同じリージョンである必要があります。

例えば、アプリケーションは東京リージョンだが、IAM Identity Centerの組織インスタンスがバージニア北部の場合だとどこでエージェントスペースを作るべきか分かりませんね。

そこで登場するのがIAM Identity Centerのアカウントインスタンスです。

図のように新規でアカウントインスタンスを作成することで利用可能です。

![](/images/security-agent-ga-organization_security_agent_iic.drawio.png)

IAM Identity Centerの組織インスタンスとアカウントインスタンスの違いは以下のブログに詳しく書かれていましたのでご参照ください。

https://blog.serverworks.co.jp/difference-of-sso-instance-type-between-organization-and-account

### エージェントスペースの設計

AWS は「**1アプリケーション = 1 Agent Space**」を推奨しています。エージェントスペースはアプリごとの独立した隔離空間で、以下を個別に管理します。

- 接続された GitHub リポジトリ
- 設計レビューの履歴
- ペネトレーションテストの設定・境界・結果
- セキュリティ所見

- 共有ドメイン配下に複数サービスがぶら下がる場合は、ドメイン単位・パス単位・環境単位のどれでエージェントスペースを切るかを事前に統一する
- 1アカウント/リージョンあたり最大100個のエージェントスペースを作成可能（調整可能）

### ペネトレーションテストの安全な実施

**非本番環境での実施**が大前提となります。

AWSも非本番環境での実施を強く推奨しています。本番と同等の構成を持つ独立したステージング環境を用意したうえで実施してください。

#### スコープ設計の徹底

テスト対象 URL（Target Domain）の所有確認だけでなく、**Out-of-scope URL の丁寧な定義**が重要です。以下のような副作用のある機能は必ず除外してください。

- データの削除・更新を行うエンドポイント
- 外部通知（メール送信・Webhook）を発火する機能
- 課金・決済処理
- CDN キャッシュをパージするような操作

#### Accessible URLs の設計

認証連携先や必要最小限の依存先のみを登録します。登録した URL には認証情報やテストデータが送信される前提で評価してください。

#### AI の非決定性を前提に設計する

Security Agent の実行挙動は確率的であり、実行ごとに結果が異なる可能性があります。

- 初回は**短いスコープ・監視付き**で実施する
- 重要なリリース前に複数回実施して所見の安定性を確認する
- AI が生成した所見は必ず人が検証してから修正着手する

### 認証情報・秘密情報の取り扱い

ペネトレーションテスト時に認証が必要な場合、対象アプリへのアクセス認証情報を渡す必要があります。

- **専用・最小権限・短命**のテスト用資格情報を用意する（本番の人間用アカウントを流用しない）
- 可能であれば Lambda 経由の動的払い出しを使い、静的シークレットを避ける
- CloudWatch Logs にどの粒度の情報が記録されるかを確認し、**ログ保持期間・閲覧権限・エクスポート制御・監査ルール**を事前に設定する

### GitHub 連携と自動修正 PR の運用ルール

#### 対応する GitHub の種類

| 種類 | 対応状況 | 備考 |
|------|---------|------|
| GitHub.com | 対応 | 全リージョン |
| GitHub Enterprise Cloud | 対応 | 現時点では `us-east-1` のみ（東京リージョン未対応） ※1|
| GitHub Enterprise Server | 未対応 | — |

※1 https://aws.amazon.com/about-aws/whats-new/2026/01/aws-security-agent-ghe-support/

:::message alert
**1 GitHub 組織 = 1 AWS アカウント**という制約があります。GitHub App は GitHub 組織ごとに 1 回しかインストールできないため、同一 GitHub 組織を複数の AWS アカウントで共有することができません。マルチアカウント構成では、どのアカウントで GitHub 連携を管理するかを先に決めてください。
:::

**自動修正 PR の運用ルール**

自動コード修復（Automated Remediation）機能は、現時点では **`us-east-1` のみ対応**です。東京リージョン（`ap-northeast-1`）では未対応なので注意が必要です。

この機能が利用できるリージョンで運用する場合も、**自動マージは禁止**とし、以下のプロセスを必ず通すルールを組織として定めてください。

1. 人によるコードレビュー
2. CI での自動テスト
3. セキュリティ確認

また、コードレビューコメントの重大度閾値・通知先・例外承認フローを決めてから開発現場に展開しましょう。

### ネットワーク・マルチアカウント構成

#### プライベートアプリのテスト

インターネット非公開のアプリを診断する場合は、VPC 接続・サブネット・NAT Gateway・セキュリティグループの設計を事前に固めてください。今回の Juice Shop の検証でもネットワーク設定の詰まりが発生しました。

#### AWS Organizations 配下での推奨パターン

複数のアカウントにまたがるアプリのペネトレーションテストには、**共有 VPC（AWS RAM）を活用した中央集権方式**が使えます。

```
Organizations
├── 中央セキュリティアカウント（Agent Space を管理）
│   └── RAM で VPC を受け取ってペンテストを実行
└── 各アプリアカウント
    └── RAM で VPC を中央アカウントへ共有
```

- 同一 Organizations 内のアカウント間で AWS RAM を使って VPC リソースを中央アカウントへ共有
- 中央アカウントで Agent Space を作成し、そこからペネトレーションテストを実行

### コスト管理

| 機能 | 料金 |
|------|------|
| 設計レビュー | 無料（月200回まで） |
| コードレビュー | 無料（月1,000回まで） |
| ペネトレーションテスト | **$50/タスク時間（秒単位課金）** |

参考として、今回の Juice Shop テストでは 3時間37分のテストで約 **$181** かかりました。（厳密には無料期間のため発生していません。）
AWS 公式の目安では、標準的なアプリで24時間程度（約$1,200）になるケースもあります。

組織での一括利用を検討する場合、**予約制・優先順位制御**を設けてから段階展開するのが費用を抑えるうえで有効です。

## 参考

- [AWS Security Blog: AWS Security Agent on-demand penetration testing now generally available](https://aws.amazon.com/blogs/security/aws-security-agent-on-demand-penetration-testing-now-generally-available/)
- [AWS Security Agent User Guide: Security best practices](https://docs.aws.amazon.com/securityagent/latest/userguide/security-best-practices.html)
- [AWS Security Agent User Guide: Set up AWS Security Agent](https://docs.aws.amazon.com/securityagent/latest/userguide/setup-security-agent.html)
- [AWS Security Agent User Guide: Enable penetration test](https://docs.aws.amazon.com/securityagent/latest/userguide/enable-penetration-test.html)
- [AWS Security Agent User Guide: Service Quotas](https://docs.aws.amazon.com/securityagent/latest/userguide/quotas.html)
- [AWS Security Agent Pricing](https://aws.amazon.com/security-agent/pricing/)

## おわりに

Security Agent は有望なサービスですが、全社横展開を即決するより、**まず限定PoC** で各観点を検証するのが妥当です。
