---
title: "GuardDuty のカスタム検知ルールが Runtime Monitoring に対応したので実際に検知させてみた"
emoji: "🐧"
type: "tech"
topics: ["aws", "guardduty", "security"]
published: false
publication_name: cscloud_blog
---

こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！

先日、GuardDuty の Custom Detection Rules（カスタム検知ルール）について記事を書きました。

https://zenn.dev/cscloud_blog/articles/guardduty-custom-detection-rules-use-case

この時点では CloudTrail の管理イベント、つまり AWS API の操作だけが検知対象でした。今回のアップデートで Runtime Monitoring のルールが追加され、OS 内の操作も検知できるようになっています。たとえば、ユーザーを root グループに追加する `usermod` や、`dnscat` のような DNS トンネリングツールの実行です。

実際に EC2 上でコマンドを実行して、検知されるところまで確認してみました。

:::message
この記事の3行まとめ
- Custom Detection Rules に、Linux の OS 内の操作を検知するルールが 55 件追加された（全体で 88 件）
- 対象は EC2・EKS・ECS Fargate で、Runtime Monitoring の有効化が前提
- プロセス名で判定するルールもあり、バイナリ名を変えるだけで回避できるものもある
:::

## 何ができるようになったのか

追加された 55 件のルールでどのような操作を検知できるかを整理します。

GuardDuty 標準の Runtime Monitoring の検知は、マイニングや既知の悪性ドメインへの通信のように「どの環境でも怪しい」振る舞いを検知するものでした。今回追加されたルールは、`useradd` や `crontab` の編集のように、環境によっては普通に行われる操作が対象です。

ルールを個別に有効化できるので、「自分たちのサーバーではこの操作は起きないはず」というものだけを選んで監視できます。前回記事の「この環境では異常」を定義するという考え方が、OS の中にまで広がったイメージです。

コンソールの Custom Detection Rules の画面で保護プランを Runtime Monitoring に絞り込むと、追加された 55 件のルールが表示されます。

![](/images/Screenshot_2026-10-16_at_15-41-04.png)

55 件を検知内容でざっくり分けると、次のようになります。

| カテゴリ | 検知できる操作の例 |
| --- | --- |
| ユーザー・権限の操作 | `useradd` でのユーザー作成、`usermod` での root グループへの追加、sudoers の変更、setuid ビットの付与 |
| 永続化（居座り）の仕込み | cron や systemd サービスの作成、`authorized_keys` への鍵の追加、`.bashrc` の変更、PAM 設定の変更 |
| 防御の無効化・痕跡の削除 | auditd やファイアウォールの停止、セキュリティ系サービスの kill、ログファイルの削除 |
| ツールの持ち込み・実行 | `curl` / `wget` でのスクリプトのダウンロード、`/tmp` のファイルへの実行権限の付与、`python -c` でのシェル起動 |
| 情報収集 | `find` でのクレデンシャルや SSH 鍵の探索、`/etc/shadow` の読み取り、`tcpdump` などのパケットキャプチャ |
| 外部への送信・通信 | DNS トンネリングツールの実行、`rclone` でのクラウドストレージへのコピー、cloudflared や tor の使用 |
| コンテナ | コンテナ内での対話シェルの起動、`nsenter` でのコンテナエスケープ |

重大度は 55 件中 47 件が MEDIUM です。HIGH は root グループへのユーザー追加や DNS トンネリングツールの実行、コンテナエスケープなど 6 件でした。

:::details 追加された 55 ルールの一覧（2026 年 10 月 16 日時点）
| ルール名 | 重大度 | 検知内容 |
| --- | --- | --- |
| `AddSetUIDCapability` | HIGH | `setcap` で `cap_setuid` などの危険なケーパビリティをバイナリに付与した |
| `AuditDisabled` | MEDIUM | `systemctl` や `auditctl` などで auditd を停止・無効化した |
| `AuditdKeylogger` | MEDIUM | `auditctl` で全コマンドの実行を記録するルールを追加した（コマンド履歴の窃取） |
| `Base64EncodeDecode` | MEDIUM | base64 / base32 / xxd / uudecode でエンコード・デコードした |
| `BpftoolProgramLoaded` | MEDIUM | `bpftool` で eBPF プログラムをカーネルにロードした |
| `ChmodInTmpDirectory` | MEDIUM | `/tmp` や `/var/tmp` のファイルに実行権限を付けた |
| `CurlWgetExfiltrateData` | MEDIUM | `curl` / `wget` のアップロードオプションでファイルを外部に送信した |
| `CurlWgetScriptDownload` | MEDIUM | `curl` / `wget` でスクリプトやバイナリをダウンロードした（パイプでシェルに渡すパターンを含む） |
| `DataEncryptionUsingCommandLineUtilities` | MEDIUM | `openssl` / `gpg` / `7z` / `zip` などでデータを暗号化した |
| `DataSplittingForExfiltration` | MEDIUM | `split` でファイルを分割した |
| `DebugfsRawDiskAccess` | MEDIUM | `debugfs` を `/dev/sda1` などのブロックデバイスに対して実行した |
| `DnsTunnelingToolExecuted` | HIGH | iodine / dnscat / dns2tcp / dnsteal などの DNS トンネリングツールを実行した |
| `DumpProcessMemoryFromProc` | HIGH | `/proc/<pid>/mem` などからプロセスのメモリを読み取った |
| `FindCommandReconCloudCredentials` | MEDIUM | `find` で AWS / Azure / GCP などのクレデンシャルファイルを探した |
| `FindCommandReconKeyMaterial` | MEDIUM | `find` で SSH 鍵や GPG キーリング、PEM ファイルを探した |
| `FindCommandReconSetuidSetgidFiles` | MEDIUM | `find` で setuid / setgid ビットの付いたファイルを探した |
| `FirewallConfigModified` | MEDIUM | ファイアウォールの設定ファイルを書き換え・削除した |
| `FirewallDisablement` | MEDIUM | iptables / ufw / firewalld などを無効化・フラッシュした |
| `InlinePythonExecution` | MEDIUM | `python -c` で pty / os.system / subprocess を使うコードを実行した |
| `InteractiveLocalAccountCreation` | MEDIUM | `useradd` でローカルユーザーを作成した |
| `InteractiveShellInsideAContainer` | MEDIUM | `docker exec` や `kubectl exec` などでコンテナ内に対話シェルを起動した |
| `KernelHardeningDisabled` | MEDIUM | `sysctl` で ASLR などのカーネル保護を緩めた |
| `KillCommandUsage` | MEDIUM | `killall` / `pkill` でセキュリティ・監査・ログ系のプロセスを停止した |
| `LDPreloadFunctionHijack` | MEDIUM | `/etc/ld.so.preload` を書き換え・削除した |
| `LogManipulation` | MEDIUM | システムログファイルを切り詰め・上書き・削除した |
| `NetworkSnifferToolExecuted` | MEDIUM | tcpdump / tshark / ngrep / nmap を実行した |
| `NewUserAddedToRootGroup` | HIGH | `usermod` / `gpasswd` でユーザーを root グループに追加した |
| `NobodyUserManipulation` | HIGH | `usermod` で nobody ユーザーにログインシェルやホームディレクトリを設定した |
| `NsenterContainerEscape` | HIGH | `nsenter` でホストの名前空間に入った（コンテナエスケープ） |
| `PAMConfigModification` | MEDIUM | `/etc/pam.d/` 配下の PAM 設定を変更した |
| `PasswordModification` | MEDIUM | `/etc/passwd` を書き換えようとした |
| `PasswordShadowFileDiscovery` | MEDIUM | `/etc/shadow` や `/etc/passwd` を読み取った |
| `PromiscuousModeEnabled` | MEDIUM | `ip link` / `ifconfig` で NIC をプロミスキャスモードにした |
| `RawSocketCreated` | MEDIUM | パケットキャプチャに使われる raw ソケットを作成した |
| `RemoteFileCopy` | MEDIUM | `scp` / `rsync` / `sftp` でリモートとファイルを転送した |
| `S3DataExfiltrationWithRclone` | MEDIUM | `rclone` でクラウドストレージにデータをコピー・同期した |
| `SSHAuthorizedKeysModification` | MEDIUM | `authorized_keys` を書き換えようとした |
| `SSHWithHostKeyCheckingDisabled` | MEDIUM | `StrictHostKeyChecking=no` で localhost に SSH 接続した |
| `ScheduledJobManipulation` | MEDIUM | cron や at のジョブファイルを作成・変更した |
| `ServiceStoppedOrDisabled` | MEDIUM | `systemctl` でセキュリティ・ログ・監視系のサービスを停止・無効化した |
| `SetUidFlagSet` | MEDIUM | `chmod` でファイルに setuid ビットを付けた |
| `ShellFromUtilities` | MEDIUM | awk / busybox / emacs / cpan などからシェルを起動した |
| `ShellRCFileManipulated` | MEDIUM | `.bashrc` や `.profile` などのシェル設定ファイルを変更した |
| `SqliteDatabaseDump` | LOW | `sqlite3` でデータベースの中身を書き出した |
| `SshFromPublicIPAddress` | MEDIUM | パブリック IP からの SSH ログインが成功した |
| `SudoPrivilegeEnumeration` | MEDIUM | `sudo -l` で sudo 権限を列挙した |
| `SudoerFileLinked` | MEDIUM | `/etc/sudoers` へのリンクを作成した |
| `SudoerFileManipulation` | MEDIUM | `/etc/sudoers` や `/etc/sudoers.d/` 配下を変更した |
| `SudoerFileRead` | MEDIUM | `/etc/sudoers` や `/etc/sudoers.d/` 配下を読み取った |
| `SudoerFileRenamed` | MEDIUM | ファイルを `/etc/sudoers` や `/etc/sudoers.d/` にリネーム・移動した |
| `SuspiciousExecutionPath` | MEDIUM | `/dev/shm` などの不審なパスからプロセスを実行した |
| `SuspiciousProtocolTunneling` | MEDIUM | SSH ポートフォワードや cloudflared / devtunnel / tor を使用した |
| `SystemdServiceManipulation` | MEDIUM | systemd のユニットファイルや init スクリプトを作成・変更・削除した |
| `SystemdTransientServiceCreated` | MEDIUM | `systemd-run` で一時的なサービスやタイマーを作成した |
| `VirtualizationDetection` | LOW | 仮想マシン上で動いているかを判定するコマンドを実行した |
:::

## 実際に検知させてみた

このセクションでは、EC2 上でコマンドを実行して、実際に Finding が出るかを確認した結果をまとめます。

東京リージョンに Amazon Linux 2023 の EC2 を 1 台用意し、Runtime Monitoring のエージェントを自動インストールで入れました。そのうえで次の 3 つのルールを Live で有効化しています。

- `NewUserAddedToRootGroup`（root グループへのユーザー追加）
- `DnsTunnelingToolExecuted`（DNS トンネリングツールの実行）
- `InteractiveLocalAccountCreation`（ローカルユーザーの作成）

有効化したルールは、一覧の「Live organization configuration」欄が「Partial (1 account included)」になります。検証アカウントだけを対象に有効化しているため、Partial と表示されています。

![](/images/Screenshot_2026-10-16_at_15-45-47.png)

![](/images/Screenshot_2026-10-16_at_15-45-59.png)

エージェントが入ると、Runtime Monitoring のカバレッジ画面で EC2 が「正常（Healthy）」と表示されます。

![](/images/Screenshot_2026-10-16_at_15-52-24.png)

実行したコマンドは次のとおりです。

```bash
useradd gdtestuser
usermod -aG root gdtestuser

# dnscat 本体は使わず、sleep を dnscat という名前でコピーして実行
cp /usr/bin/sleep /tmp/dnscat && /tmp/dnscat 2
```

`dnscat` は本物のツールを入れていません。このルールはプロセス名で判定しているので、無害な `sleep` を `dnscat` という名前で実行するだけで検知の条件を満たします。

### 結果

コマンドを実行してから約 2 分半で、3 種類の Finding が生成されました。

![](/images/Screenshot_2026-10-16_at_16-16-43.png)

画面に 5 件並んでいるのは、追加で `gpasswd -a gdtestuser root` と `usermod -g 0 gdtestuser` も試したためです。同じルールでも、コマンドの書き方が違うと別の Finding になりました。

| ルール | 実行したコマンド | 重大度 |
| --- | --- | --- |
| `NewUserAddedToRootGroup` | `usermod -aG root gdtestuser` | HIGH |
| `DnsTunnelingToolExecuted` | `/tmp/dnscat 2` | HIGH |
| `InteractiveLocalAccountCreation` | `useradd gdtestuser` | MEDIUM |

Finding には、どのプロセスから実行されたかという親子関係も記録されていました。今回は SSM Run Command から実行したので、SSM エージェントからシェルを経由して `usermod` が起動された流れが見えます。正規の運用作業なのか、不審な SSH セッションからの操作なのかを切り分けるときの手がかりになります。

なお、実行したコマンドラインはそのまま残らず、ユーザー名などがマスクされた形で記録されていました。たとえば `usermod -aG root gdtestuser` は `usermod -G root <user>`、追加で試した `usermod -g 0 gdtestuser` は `usermod -g 0 <user>` と記録されています。

![](/images/Screenshot_2026-10-16_at_16-17-48.png)

### 名前を変えると検知されない

試しに、同じ `sleep` を `dnsc4t` という名前でコピーして実行してみました。こちらは Finding が生成されませんでした。

このルールはプロセス名が `dnscat` や `iodine` などと一致するかで判定しているので、名前を変えれば検知されません。バイナリ名を変える程度の工夫をする攻撃者には効かないということです。不用意にツールを持ち込んだケースや、許可していないツールが使われたケースを拾う仕掛け、と捉えるのがよさそうです。

一方で、`authorized_keys` や `/etc/ld.so.preload` の変更を検知するルールは、ファイルを書き込みで開く操作自体を見ています。使うコマンドには左右されにくいタイプです。ルールによって回避のしやすさが違う点は押さえておきたいところです。

## どのルールから有効化するか

このセクションでは、55 件のルールをどこから有効化するかの考え方を整理します。

Runtime のルールは、ワークロードの使われ方によってノイズの量が大きく変わります。起きたらすぐ調査すべきものと、普段の運用でも起きるものに分けて考えるのがおすすめです。

### Live で有効化しやすいルール

起きたら即調査、と判断しやすいのは次のようなルールです。

- root グループへのユーザー追加、コンテナエスケープなど重大度 HIGH のルール
- DNS トンネリングツールや `rclone` など、サーバー上で正規に使うことがほぼ無いツールの実行
- PAM 設定や sudoers、`/etc/ld.so.preload` など、普段の運用で触らないファイルの変更

コンテナやイミュータブルなインフラで運用していて、稼働中のサーバーに人が入らない前提なら、ユーザーの作成や `authorized_keys` の変更も Live にしやすいはずです。デプロイ後に OS 内でユーザーや鍵が増えること自体が異常になります。

### Dry Run から始めたいルール

普段の運用やアプリケーションでも起きる操作は、まず Dry Run で頻度を測った方が安全です。

- base64 でのエンコード・デコード、`scp` / `rsync` でのファイル転送、`curl` / `wget` でのスクリプトのダウンロード
- `sudo -l` での権限確認、`tcpdump` でのパケットキャプチャ
- コンテナ内での対話シェルの起動（`kubectl exec` で調査する運用がある場合）
- cron や systemd サービスの変更（構成管理ツールやパッケージ更新で発生する場合）

base64 や scp は、アプリケーションの起動スクリプトやバックアップ処理で使われていてもおかしくありません。いきなり Live にすると、Finding がノイズで埋まる可能性があります。

## まとめ

Custom Detection Rules が Runtime Monitoring に対応しました。「この環境では異常」と宣言できる範囲が、AWS API の操作から OS 内の操作にまで広がっています。

実際に試したところ、root グループへのユーザー追加や DNS トンネリングツールの実行は、数分で Finding になりました。どのプロセスから実行されたかも分かるので、運用作業なのか不審な操作なのかも判断しやすくなっています。

一方で、プロセス名だけで判定するルールは、バイナリ名を変えると回避できます。前回記事と同じく、Dry Run で頻度を測ってから Live に切り替える手順を踏むのが安全です。

まずは Runtime Monitoring が有効になっている環境で、重大度 HIGH のルールと、正規に使うことがほぼ無いツールの検知ルールから試してみてください。

この記事がどなたかの役に立つと嬉しいです。
