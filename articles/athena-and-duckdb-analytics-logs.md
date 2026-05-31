---
title: "S3内のログに対してAthenaまたはDuckDBを活用してクエリするだけの最小権限は何か調べてみた"
emoji: "🦆"
type: "tech"
topics: ["aws", "athena", "duckdb", "s3"]
published: true
publication_name: cscloud_blog
published_at: 2025-07-24 07:00
---
こんにちは、CSCの平木です！

皆さんはS3に保管されたログのクエリをしていますか？

AWS S3に保存されたログを分析する際に、

- クエリだけしたいなら必要最低限の権限は何か
- 事前にどんな準備をしていれば上記の権限だけ与えれば済むか

を調査する機会があったため本記事では、AthenaとDuckDBそれぞれのケースで、
最小権限と事前に何をしておくと良いのかの手順を整理します。

## 前提条件

クエリを実行したい人は、もともと[SecurityAudit](https://docs.aws.amazon.com/ja_jp/aws-managed-policy/latest/reference/SecurityAudit.html)のAWS管理ポリシーが付与されているものとします。

## Athenaを利用する場合

### 事前に準備が必要なこと

例えば担当者などが管理者などへクエリする環境がほしいと言われた場合に実施するものと仮定します。

- Athena ワークグループの作成
  - ワークグループは既にチームや部署で作られているものがあれば新規で作成する必要はあまりないです
- Athena データベースの作成
  - ワークグループ同様必要に応じて作成してください
- Athena テーブルの作成
- Lake Formationでクエリしたいユーザーまたはロールに対して権限追加
- クエリを実行したいユーザーまたはロールに必要な権限の追加（Athena/Glue/S3）

### （依頼を受けた人が行う）手順

#### Athena ワークグループの作成

ワークグループを作成することでリソースの分離やワークグループ内でのクエリのデータ量の上限などを設けられるため作成しておくと良いです。
デフォルトで存在する Primary を使用しても問題ないです。

![2025-07-17-21-03-36.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/0e89ddf1-090e-48f9-88a8-137d4050e938.png)

:::message alert
Athenaを設定する（クエリを実行する）リージョンは、クエリを行いたいS3バケットと同じでなくても使用することはできますが、意図しない費用増加に繋がります。
意図してクロスリージョンで利用する場合には問題ないですが、別段クロスリージョンでなくても良い場合は同じリージョンで実行すると良さそうです。
参考例： [Athena のリージョンを間違えて17万円を無駄にしてしまった話 #S3 - Qiita](https://qiita.com/gorooe/items/6010f309f6321ac3f5bf)
:::

ナビゲーションペインからワークグループを選択します。

![025-07-17-21-08-42.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/6e002ec1-1b09-4c44-99b6-fa9b9b476a68.png)

「ワークグループの作成」を押します。

![2025-07-17-21-09-16.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/cc4ba83a-6b3e-4f3d-8e7f-7f3d2d75d005.png)


任意のワークグループ名を入力し、エンジンタイプを要件に応じて設定します。
今回は`Athena SQL`にしました。

![2025-07-17-21-10-09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/6f056d08-3253-4999-b4e4-aee96d2004a3.png)

続いて認証は環境に応じたほうを選択すべきですが、
今回は`IAM`を選択します。

クエリ結果の設定については、
S3バケットにクエリ結果を保管したい場合は`カスタムマネージド`を選択すべきですが、
別段クエリのみだけできれば問題なければ`Athenaマネージド`がおすすめです。（個別のS3バケットが不要かつ追加料金がないため）

詳しくはこちらのブログが分かりやすいです。

https://dev.classmethod.jp/articles/update-amazon-athena-aws-managed-storage-query-results/

![2025-07-17-21-10-21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/33aac2b9-2f7c-44dc-a16d-552599bb77c8.png)

必要に応じてオプションの設定をして「ワークグループを作成」を押せばワークグループの作成は完了です。

スクショ内ではクエリのデータ量の上限を設定しています。

![2025-07-17-21-22-08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/5f37bbf1-6fca-4280-87f9-9292065ef2cc.png)

#### Athena データベースの作成

エディタで以下SQLを実行します。

```SQL
CREATE DATABASE <データベース名>;
```

![2025-07-17-21-24-02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/72c40493-1008-4b49-bfe2-c16030f41e7a.png)

#### テーブルの作成

同様にテーブル作成用のSQLをエディタで実行します。

以下はCloudTrailの例です。

```sql
CREATE EXTERNAL TABLE cloudtrail_logs_partition_projection (
    eventVersion STRING,
    userIdentity STRUCT<
        type: STRING,
        principalId: STRING,
        arn: STRING,
        accountId: STRING,
        invokedBy: STRING,
        accessKeyId: STRING,
        userName: STRING,
        sessionContext: STRUCT<
            attributes: STRUCT<
                mfaAuthenticated: STRING,
                creationDate: STRING>,
            sessionIssuer: STRUCT<
                type: STRING,
                principalId: STRING,
                arn: STRING,
                accountId: STRING,
                userName: STRING>>>,
    eventTime STRING,
    eventSource STRING,
    eventName STRING,
    awsRegion STRING,
    sourceIpAddress STRING,
    userAgent STRING,
    errorCode STRING,
    errorMessage STRING,
    requestParameters STRING,
    responseElements STRING,
    additionalEventData STRING,
    requestId STRING,
    eventId STRING,
    resources ARRAY<STRUCT<
        arn: STRING,
        accountId: STRING,
        type: STRING>>,
    eventType STRING,
    apiVersion STRING,
    readOnly STRING,
    recipientAccountId STRING,
    serviceEventDetails STRING,
    sharedEventID STRING,
    vpcEndpointId STRING
)
COMMENT 'CloudTrail table for ${BucketName} bucket'
PARTITIONED BY (region string, date string)
ROW FORMAT SERDE 'com.amazon.emr.hive.serde.CloudTrailSerde'
STORED AS INPUTFORMAT 'com.amazon.emr.cloudtrail.CloudTrailInputFormat'
OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 's3://[バケット名]/AWSLogs/[アカウントID]/CloudTrail/'
TBLPROPERTIES (
    'projection.enabled' = 'true',
    'projection.date.type' = 'date',
    'projection.date.range' = 'NOW-1YEARS,NOW',
    'projection.date.format' = 'yyyy/MM/dd',
    'projection.date.interval' = '1',
    'projection.date.interval.unit' = 'DAYS',
    'projection.region.type' = 'enum',
    'projection.region.values'='us-east-1,us-east-2,us-west-1,us-west-2,ap-south-1,ap-northeast-1,ap-northeast-2,ap-northeast-3,ap-southeast-1,ap-southeast-2,ca-central-1,eu-central-1,eu-west-1,eu-west-2,eu-west-3,eu-north-1,sa-east-1',
    'storage.location.template' = 's3://[バケット名]/AWSLogs/[アカウントID]/CloudTrail/${region}/${date}',
    'classification'='cloudtrail',
    'compressionType'='gzip',
    'typeOfData'='file',
    'classification'='cloudtrail'
);
```

#### Lake Formation権限の追加

Lake Formationと調べて、CatalogからDefaultのアカウントIDを選択します。

![2025-07-17-23-39-44.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/f8fbdd8f-f2e5-45f9-9ee3-6b0e02640686.png)

Permissionタブから「Grants」を押します。

![2025-07-17-23-42-43.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/eae8522b-5804-4faa-b766-bb845d6d8d3c.png)

Principal typeを`Principal`を選択し、
Principalsで`IAM users and roles`を選択した上で許可を与えたいユーザーまたはロールを指定します。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/28e6140d-e7e1-4b12-824e-5df1dd76a5d5.png)

LF-Tags or catalog resourcesでは、`Name Data Catalog resources`を選択し、
CatalogではDefaultとなっているアカウントIDを、
Databasesでは先ほど作成したデータベース名を、
Tablesでは先ほど作成したテーブル名を指定します。

![2025-07-17-23-45-18.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/cc35c4a2-bef3-4738-a068-0c8b18198be0.png)

Table permissionsでは`Select`と`Describe`にチェックを入れ、
「Grants」を押すと完了です。

![2025-07-17-23-47-47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1046178/b95658c8-9533-4b33-b5e3-e453a3736899.png)

#### 権限の追加

クエリを実行したいユーザーまたはロールに以下の権限を追加してください。

<アカウントID>、<ワークグループ名>、<バケット名>は対応するものを置換してください。

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AthenaConsoleListAccess",
            "Effect": "Allow",
            "Action": [
                "athena:ListDataCatalogs",
                "athena:ListEngineVersions",
                "athena:ListWorkGroups"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AthenaQueryExecutionAccess",
            "Effect": "Allow",
            "Action": [
                "athena:BatchGetQueryExecution",
                "athena:GetQueryExecution",
                "athena:GetQueryResults",
                "athena:GetQueryRuntimeStatistics",
                "athena:StartQueryExecution"
            ],
            "Resource": "arn:aws:athena:*:<アカウントID>:workgroup/<ワークグループ名>"
        },
        {
            "Sid": "GlueReadOnlyAccess",
            "Effect": "Allow",
            "Action": [
                "glue:BatchGetPartition",
                "glue:GetDatabase",
                "glue:GetDatabases",
                "glue:GetPartition",
                "glue:GetPartitions",
                "glue:GetTable",
                "glue:GetTables"
            ],
            "Resource": [
                "arn:aws:glue:*:<アカウントID>:catalog",
                "arn:aws:glue:*:<アカウントID>:database/*",
                "arn:aws:glue:*:<アカウントID>:table/*/*"
            ]
        },
        {
            "Sid": "LakeFormationAccess",
            "Effect": "Allow",
            "Action": [
                "lakeformation:GetDataAccess"
            ],
            "Resource": "*"
        }
    ]
}
```

### （依頼した人が行う）手順

#### サンプルクエリ

事前準備してもらったら動作するか確認

```SQL
SELECT * FROM cloudtrail_logs_partition_projection WHERE region = 'ap-northeast-1' AND date = '2025/07/01' LIMIT 10;
```

## 2. DuckDB（CloudShell）を利用する場合

### 事前に準備が必要なこと

- クエリを実行したいユーザーまたはロールに必要な権限の追加（CloudShell/S3）

### （依頼を受けた人が行う）手順

#### 権限の追加

クエリをしたいユーザーまたはロールに以下の権限を追加で付与します。

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudShellFullAccess",
            "Effect": "Allow",
            "Action": [
                "cloudshell:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DenyCloudShellFileUploadDownload",
            "Effect": "Deny",
            "Action": [
                "cloudshell:GetFileDownloadUrls",
                "cloudshell:GetFileUploadUrls"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowS3ListBucket",
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::<バケット名>"
        },
        {
            "Sid": "AllowS3GetObject",
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::<バケット名>/*"
        }
    ]
}
```

### （依頼した人が行う）手順

#### 1. CloudShellでDuckDB CLIをインストール

```shell
curl -LO https://github.com/duckdb/duckdb/releases/download/v1.3.2/duckdb_cli-linux-amd64.zip
unzip duckdb_cli-linux-amd64.zip
rm duckdb_cli-linux-amd64.zip
```

#### 2. DuckDBを起動

```shell
./duckdb cloudtrail-analysis

D INSTALL httpfs;
D LOAD httpfs;
D CREATE SECRET (
      TYPE S3,
      PROVIDER CREDENTIAL_CHAIN
  );
```

#### 3. テーブル作成

CloudTrailの例です。

日付などは実際使用するものに読み替えてください。

```sql
CREATE TABLE ct_detailed AS
WITH raw_events AS (
    SELECT 
        unnest(Records) AS Event
    FROM 
        read_json(
            's3://(バケット名)/(CloudTrailまでのパス)/CloudTrail/ap-northeast-1/2025/07/01/*.json.gz',
            maximum_depth=2
        )
)
SELECT
    json_extract_string(Event, '$.eventVersion') AS eventVersion,
    json_extract_string(Event, '$.eventTime') AS eventTime,
    json_extract_string(Event, '$.eventSource') AS eventSource,
    json_extract_string(Event, '$.eventName') AS eventName,
    json_extract_string(Event, '$.awsRegion') AS awsRegion,
    json_extract_string(Event, '$.sourceIPAddress') AS sourceIPAddress,
    json_extract_string(Event, '$.userAgent') AS userAgent,
    json_extract_string(Event, '$.userIdentity.type') AS userType,
    json_extract_string(Event, '$.userIdentity.principalId') AS principalId,
    json_extract_string(Event, '$.userIdentity.arn') AS userArn,
    json_extract_string(Event, '$.userIdentity.accountId') AS accountId,
    json_extract_string(Event, '$.userIdentity.accessKeyId') AS accessKeyId,
    json_extract_string(Event, '$.userIdentity.userName') AS userName,
    json_extract_string(Event, '$.userIdentity.sessionContext.attributes.creationDate') AS sessionCreationDate,
    json_extract_string(Event, '$.userIdentity.sessionContext.attributes.mfaAuthenticated') AS mfaAuthenticated,
    json_extract_string(Event, '$.requestID') AS requestID,
    json_extract_string(Event, '$.eventID') AS eventID,
    json_extract_string(Event, '$.readOnly') AS readOnly,
    json_extract_string(Event, '$.eventType') AS eventType,
    json_extract_string(Event, '$.managementEvent') AS managementEvent,
    json_extract_string(Event, '$.recipientAccountId') AS recipientAccountId,
    json_extract_string(Event, '$.eventCategory') AS eventCategory
FROM 
    raw_events;
```

以上で準備は完了です。

## 参考

- [Amazon Athenaだけを使える権限でAWSマネジメントコンソールを使う方法 - サーバーワークスエンジニアブログ](https://blog.serverworks.co.jp/2024/06/17/171404)
- [CloudTrailのクエリをDuckDBに置き換えてクラウド破産と無縁な分析基盤を作る #AWS - Qiita](https://qiita.com/watany/items/a2d4f767674b969c5e89)

## まとめ

今回は、AthenaとDuckDBを使用する場合の最小権限と手順を整理してみました。

当然ではありますが、管理者の立場である事前準備を行う人はさらに権限が必要な点にはご注意ください。
ここから別であれやりたいこれやりたいといった要望もあると思いますので、
ぜひカスタムしていただければと思います。

この記事がどなたかの役に立つとうれしいです。

---

この記事は Qiita から移行しました。
