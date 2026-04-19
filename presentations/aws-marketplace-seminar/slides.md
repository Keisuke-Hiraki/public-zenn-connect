---
theme: default
colorSchema: dark
title: マルウェア感染を実際に目撃して見たリアルについて
info: |
  平木佳介 (@k_hirasan)
  株式会社サイバーセキュリティクラウド
  CloudSec JP #005
transition: slide-left
mdc: true
fonts:
  sans: 'Noto Sans JP'
  mono: 'JetBrains Mono'
  weights: '400,600,700'
layout: cover
background: '#0d1117'
---

<div style="position:absolute;top:24px;right:32px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#f97316;letter-spacing:0.1em;opacity:0.9;">
  ⚠ INCIDENT REPORT
</div>

<div style="margin-top:24px;">
  <h1 style="font-size:2.2rem;line-height:1.35;font-weight:700;color:#f0f6fc;margin:0 0 16px;">
    マルウェア感染を実際に目撃して<br>見たリアルについて
  </h1>
  <p style="font-size:1.1rem;color:#8b949e;margin:0 0 32px;">
    ——検証前に整えるべきセキュリティ体制
  </p>
</div>

<hr style="border:none;border-top:1px solid #21262d;margin-bottom:28px;" />

<div style="display:flex;justify-content:space-between;align-items:flex-end;">
  <div>
    <p style="font-size:1.05rem;font-weight:700;color:#f0f6fc;margin:0;">平木佳介</p>
    <p style="font-size:0.82rem;color:#8b949e;margin:4px 0 2px;">株式会社サイバーセキュリティクラウド</p>
    <p style="font-size:0.82rem;color:#f97316;font-family:'JetBrains Mono',monospace;margin:0;">@k_hirasan</p>
  </div>
  <div style="text-align:right;font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#484f58;line-height:1.8;">
    CloudSec JP #005
  </div>
</div>

<!--
今日は自分が実際に踏んだセキュリティインシデントの話をさせてください。
-->

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:24px;">自己紹介</h1>

<div style="display:grid;grid-template-columns:200px 1fr;gap:24px;align-items:start;">
  <div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:20px;text-align:center;">
    <img src="./image/sns_logo.jpg" style="width:100px;height:100px;border-radius:50%;object-fit:cover;border:2px solid #f97316;margin-bottom:10px;display:block;margin-left:auto;margin-right:auto;" />
    <p style="font-size:1.05rem;font-weight:700;color:#f0f6fc;margin:0 0 6px;">平木 佳介</p>
    <p style="font-size:0.75rem;color:#f97316;font-family:'JetBrains Mono',monospace;margin:0;">@k_hirasan</p>
  </div>
  <div style="display:flex;flex-direction:column;gap:14px;">
    <div>
      <p style="font-size:0.65rem;color:#f97316;font-weight:700;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 4px;">COMPANY</p>
      <p style="font-size:0.95rem;color:#f0f6fc;margin:0;">株式会社サイバーセキュリティクラウド</p>
    </div>
    <div>
      <p style="font-size:0.65rem;color:#f97316;font-weight:700;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 4px;">ROLE</p>
      <p style="font-size:0.95rem;color:#f0f6fc;margin:0;">TAM（テクニカルアカウントマネージャー）</p>
      <p style="font-size:0.82rem;color:#8b949e;margin:2px 0 0;">プロダクト: CloudFastener</p>
    </div>
    <div>
      <p style="font-size:0.65rem;color:#f97316;font-weight:700;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 4px;">DOMAIN</p>
      <p style="font-size:0.9rem;color:#e6edf3;margin:0;">AWS / Azure / Google Cloud セキュリティ</p>
    </div>
    <div style="background:#161b22;border-left:3px solid #f97316;padding:10px 14px;border-radius:0 4px 4px 0;">
      <p style="font-size:0.88rem;color:#f0f6fc;margin:0;">今日は <span style="color:#f97316;font-weight:700;">自分が遭遇したインシデント</span> の話をします 🙃</p>
    </div>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:24px;">本日のアジェンダ</h1>

<div style="display:flex;flex-direction:column;gap:10px;margin-top:8px;">
  <div style="display:flex;align-items:center;gap:16px;background:#161b22;border-radius:6px;padding:14px 18px;">
    <span style="font-family:'JetBrains Mono',monospace;color:#f97316;font-size:1.1rem;font-weight:700;min-width:28px;">01</span>
    <span style="color:#f0f6fc;font-size:0.95rem;">インシデントの概要——何が起きたのか</span>
    <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#484f58;">〜4min</span>
  </div>
  <div style="display:flex;align-items:center;gap:16px;background:#161b22;border-radius:6px;padding:14px 18px;">
    <span style="font-family:'JetBrains Mono',monospace;color:#f97316;font-size:1.1rem;font-weight:700;min-width:28px;">02</span>
    <span style="color:#f0f6fc;font-size:0.95rem;">「Marketplace = 安全」という思い込み</span>
    <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#484f58;">〜4min</span>
  </div>
  <div style="display:flex;align-items:center;gap:16px;background:#161b22;border-radius:6px;padding:14px 18px;">
    <span style="font-family:'JetBrains Mono',monospace;color:#f97316;font-size:1.1rem;font-weight:700;min-width:28px;">03</span>
    <span style="color:#f0f6fc;font-size:0.95rem;">調査で判明した侵害の実態</span>
    <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#484f58;">〜5min</span>
  </div>
  <div style="display:flex;align-items:center;gap:16px;background:#161b22;border-radius:6px;padding:14px 18px;">
    <span style="font-family:'JetBrains Mono',monospace;color:#f97316;font-size:1.1rem;font-weight:700;min-width:28px;">04</span>
    <span style="color:#f0f6fc;font-size:0.95rem;">なぜ7日間気付けなかったのか</span>
    <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#484f58;">〜3min</span>
  </div>
  <div style="display:flex;align-items:center;gap:16px;background:#161b22;border:1px solid #f97316;border-radius:6px;padding:14px 18px;">
    <span style="font-family:'JetBrains Mono',monospace;color:#f97316;font-size:1.1rem;font-weight:700;min-width:28px;">05</span>
    <span style="color:#f97316;font-size:0.95rem;font-weight:600;">検証前に整えるべきセキュリティ体制</span>
    <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#f97316;">〜5min</span>
  </div>
</div>

---
layout: section
background: '#0d1117'
---

<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center;height:100%;">
  <div>
    <p style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#f97316;letter-spacing:0.12em;margin-bottom:12px;">CHAPTER 01</p>
    <h1 style="color:#f0f6fc;font-size:2.4rem;font-weight:700;line-height:1.3;">インシデントの概要</h1>
  </div>
  <div style="display:flex;flex-direction:column;gap:14px;opacity:0.55;">
    <div style="display:flex;align-items:center;gap:12px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#8b949e;white-space:nowrap;">侵害期間</span>
      <span style="font-family:'JetBrains Mono',monospace;font-size:2.8rem;font-weight:700;color:#ef4444;line-height:1;">7<span style="font-size:1.2rem;">日間</span></span>
    </div>
    <div style="display:flex;align-items:center;gap:12px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#8b949e;white-space:nowrap;">ポートスキャン</span>
      <span style="font-family:'JetBrains Mono',monospace;font-size:2.8rem;font-weight:700;color:#ef4444;line-height:1;">2,360<span style="font-size:1.2rem;">回</span></span>
    </div>
    <div style="display:flex;align-items:center;gap:12px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#8b949e;white-space:nowrap;">GuardDuty</span>
      <span style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:#ef4444;line-height:1;">19件 / ALL CRITICAL</span>
    </div>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:16px;">今回の構成と背景</h1>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
  <div>
    <p style="font-size:0.65rem;color:#f97316;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 8px;">WHAT WE DID</p>
    <div style="display:flex;flex-direction:column;gap:8px;">
      <div style="background:#161b22;border-left:3px solid #f97316;padding:11px 14px;border-radius:0 4px 4px 0;">
        <p style="font-size:0.88rem;color:#f0f6fc;margin:0;line-height:1.6;">
          生成 AI アプリ構築プラットフォーム <strong style="color:#f97316;">Dify</strong> を<br>
          AWS Marketplace から EC2 へデプロイ
        </p>
      </div>
      <div style="background:#161b22;border-left:3px solid #8b949e;padding:11px 14px;border-radius:0 4px 4px 0;">
        <p style="font-size:0.88rem;color:#f0f6fc;margin:0;line-height:1.6;">
          ALB で SSL 終端を設定し<br>HTTPS でアクセスできるよう構成
        </p>
      </div>
      <div style="background:#161b22;border-left:3px solid #eab308;padding:11px 14px;border-radius:0 4px 4px 0;">
        <p style="font-size:0.82rem;color:#eab308;margin:0;line-height:1.6;">
          目的はあくまで <strong>「検証」</strong><br>
          <span style="color:#8b949e;font-size:0.78rem;">"すぐ消すし、どうせ大丈夫だろう"</span>
        </p>
      </div>
    </div>
  </div>
  <div>
    <p style="font-size:0.65rem;color:#f97316;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 8px;">ENVIRONMENT</p>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;padding:14px 16px;">
      <table style="width:100%;border-collapse:collapse;font-size:0.82rem;">
        <tbody>
          <tr>
            <td style="padding:5px 0;border-bottom:1px solid #21262d;color:#8b949e;white-space:nowrap;">AMI</td>
            <td style="padding:5px 0 5px 12px;border-bottom:1px solid #21262d;color:#ef4444;font-family:'JetBrains Mono',monospace;font-size:0.78rem;">Dify Premium v1.4.2</td>
          </tr>
          <tr>
            <td style="padding:5px 0;border-bottom:1px solid #21262d;color:#8b949e;">インスタンス</td>
            <td style="padding:5px 0 5px 12px;border-bottom:1px solid #21262d;color:#e6edf3;font-family:'JetBrains Mono',monospace;font-size:0.78rem;">c5.2xlarge (8 vCPU)</td>
          </tr>
          <tr>
            <td style="padding:5px 0;border-bottom:1px solid #21262d;color:#8b949e;">ネットワーク</td>
            <td style="padding:5px 0 5px 12px;border-bottom:1px solid #21262d;color:#e6edf3;font-size:0.8rem;">プライベートサブネット + NAT GW</td>
          </tr>
          <tr>
            <td style="padding:5px 0;color:#8b949e;">リージョン</td>
            <td style="padding:5px 0 5px 12px;color:#e6edf3;font-size:0.8rem;">ap-northeast-1（東京）</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.25);border-radius:6px;padding:10px 14px;margin-top:10px;font-size:0.82rem;color:#e6edf3;line-height:1.6;">
      構成が完了した時点では<br>
      <span style="color:#f97316;font-weight:700;">すべてが順調に見えました</span>
    </div>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:16px;">ある日の深夜</h1>

<div style="display:grid;grid-template-columns:1.6fr 1fr;gap:20px;align-items:start;">
  <div>
    <div style="background:#161b22;border-left:3px solid #f97316;padding:12px 16px;border-radius:0 4px 4px 0;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#e6edf3;line-height:1.7;margin-bottom:14px;">
      <span style="color:#f97316;">FROM:</span> trustandsafety@support.aws.com<br>
      <span style="color:#f97316;">DATE:</span> 深夜 22:24 JST<br>
      <hr style="border-color:#30363d;margin:8px 0;" />
      We've received a report(s) that your AWS resource(s)<br>
      has been implicated in <span style="color:#ef4444;font-weight:700;">Port Scanning</span>.
    </div>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;padding:13px 15px;">
      <p style="font-size:0.82rem;color:#8b949e;margin:0 0 7px;">このメールをきっかけに調査を開始</p>
      <p style="font-size:0.9rem;color:#f0f6fc;margin:0;line-height:1.6;">
        AWS Marketplace 経由でデプロイした EC2 が<br>
        <span style="color:#ef4444;font-weight:700;">完全に侵害されていた</span>ことが判明<br>
        <span style="font-size:0.78rem;color:#8b949e;">約7日間にわたって悪用されていた</span>
      </p>
    </div>
  </div>
  <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;padding:16px;">
    <p style="font-size:0.65rem;color:#f97316;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 14px;">DAMAGE SUMMARY</p>
    <div style="display:flex;flex-direction:column;gap:12px;">
      <div>
        <p style="font-size:0.68rem;color:#8b949e;margin:0 0 1px;">侵害期間</p>
        <p style="font-family:'JetBrains Mono',monospace;color:#ef4444;font-size:1.5rem;font-weight:700;margin:0;line-height:1;">約 7日間</p>
      </div>
      <div>
        <p style="font-size:0.68rem;color:#8b949e;margin:0 0 1px;">ポートスキャン</p>
        <p style="font-family:'JetBrains Mono',monospace;color:#ef4444;font-size:1.5rem;font-weight:700;margin:0;line-height:1;">2,360回</p>
      </div>
      <div>
        <p style="font-size:0.68rem;color:#8b949e;margin:0 0 1px;">GuardDuty 検知</p>
        <p style="font-family:'JetBrains Mono',monospace;color:#ef4444;font-size:1.2rem;font-weight:700;margin:0;line-height:1;">19件 / All Critical</p>
      </div>
    </div>
  </div>
</div>

<!--
深夜に届いた1通のメール。AWS の Trust & Safety チームから。自分のインスタンスがポートスキャン攻撃の踏み台になっているという内容。
-->

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:16px;">インシデントのタイムライン</h1>
<div style="position:relative;padding-left:24px;">
  <div style="position:absolute;left:10px;top:0;bottom:0;width:2px;background:#21262d;"></div>
  <div style="display:flex;flex-direction:column;gap:0;">
    <div style="display:flex;gap:16px;align-items:flex-start;padding-bottom:16px;">
      <div style="position:relative;z-index:1;"><div style="width:14px;height:14px;border-radius:50%;background:#22c55e;border:2px solid #0d1117;margin-left:-19px;margin-top:4px;"></div></div>
      <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;padding:10px 14px;flex:1;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;"><span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#22c55e;">1日目 02:04</span><span style="font-size:0.78rem;color:#f0f6fc;">EC2 インスタンス起動</span></div>
        <p style="font-size:0.72rem;color:#8b949e;margin:0;">Dify Premium v1.4.2 デプロイ完了 / ALB + HTTPS 構成</p>
      </div>
    </div>
    <div style="display:flex;gap:16px;align-items:flex-start;padding-bottom:16px;">
      <div style="position:relative;z-index:1;"><div style="width:14px;height:14px;border-radius:50%;background:#eab308;border:2px solid #0d1117;margin-left:-19px;margin-top:4px;"></div></div>
      <div style="background:#161b22;border:1px solid #eab308;border-radius:6px;padding:10px 14px;flex:1;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;"><span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#eab308;">1日目〜2日目</span><span style="font-size:0.78rem;color:#f0f6fc;">初期侵入（推定）→ マルウェア展開</span></div>
        <p style="font-size:0.72rem;color:#8b949e;margin:0;">CVE-2025-55182 を悪用した RCE / CPU: 7-17%（マルウェア展開中）</p>
      </div>
    </div>
    <div style="display:flex;gap:16px;align-items:flex-start;padding-bottom:16px;">
      <div style="position:relative;z-index:1;"><div style="width:14px;height:14px;border-radius:50%;background:#f97316;border:2px solid #0d1117;margin-left:-19px;margin-top:4px;"></div></div>
      <div style="background:#161b22;border:1px solid #f97316;border-radius:6px;padding:10px 14px;flex:1;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;"><span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#f97316;">2日目 06:13</span><span style="font-size:0.78rem;color:#f97316;font-weight:600;">GuardDuty が検知開始</span><span style="background:rgba(239,68,68,0.15);color:#ef4444;font-size:0.65rem;padding:1px 7px;border-radius:3px;border:1px solid rgba(239,68,68,0.4);">19件 / All Critical</span></div>
        <p style="font-size:0.72rem;color:#8b949e;margin:0;">通知設定なし → 誰も気づかない</p>
      </div>
    </div>
    <div style="display:flex;gap:16px;align-items:flex-start;padding-bottom:16px;">
      <div style="position:relative;z-index:1;"><div style="width:14px;height:14px;border-radius:50%;background:#ef4444;border:2px solid #0d1117;margin-left:-19px;margin-top:4px;"></div></div>
      <div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.4);border-radius:6px;padding:10px 14px;flex:1;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;"><span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#ef4444;">4日目〜9日目</span><span style="font-size:0.78rem;color:#ef4444;font-weight:600;">暗号通貨マイニング全開 + ポートスキャン攻撃継続</span></div>
        <p style="font-size:0.72rem;color:#8b949e;margin:0;">CPU 87-94% 継続 / ネットワーク 100GB/日流出 / 2,360回の攻撃</p>
      </div>
    </div>
    <div style="display:flex;gap:16px;align-items:flex-start;">
      <div style="position:relative;z-index:1;"><div style="width:14px;height:14px;border-radius:50%;background:#22c55e;border:2px solid #0d1117;margin-left:-19px;margin-top:4px;"></div></div>
      <div style="background:#161b22;border:1px solid #22c55e;border-radius:6px;padding:10px 14px;flex:1;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;"><span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#22c55e;">9日目 22:24</span><span style="font-size:0.78rem;color:#22c55e;font-weight:600;">AWS Abuse Report で初めて気づく</span></div>
        <p style="font-size:0.72rem;color:#8b949e;margin:0;">調査開始 → 10日目 00:30 インスタンス終了</p>
      </div>
    </div>
  </div>
</div>

---
layout: section
background: '#0d1117'
---

<div style="display:grid;grid-template-columns:1.1fr 1fr;gap:32px;align-items:center;height:100%;">
  <div>
    <p style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#f97316;letter-spacing:0.12em;margin-bottom:12px;">CHAPTER 02</p>
    <h1 style="color:#f0f6fc;font-size:2rem;font-weight:700;line-height:1.3;">「Marketplace = 安全」<br>という思い込み</h1>
  </div>
  <div style="opacity:0.55;display:flex;flex-direction:column;gap:10px;">
    <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:6px;padding:14px 18px;">
      <p style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#ef4444;letter-spacing:0.12em;margin:0 0 6px;">CVE-2025-55182</p>
      <p style="font-family:'JetBrains Mono',monospace;font-size:3rem;font-weight:700;color:#ef4444;margin:0;line-height:1;">10.0<span style="font-size:1rem;color:#8b949e;margin-left:6px;">/ 10.0</span></p>
      <p style="font-size:0.75rem;color:#8b949e;margin:4px 0 0;">CVSS スコア / 認証不要 RCE</p>
    </div>
    <p style="font-size:0.75rem;color:#8b949e;font-family:'JetBrains Mono',monospace;margin:0;">Dify リリースより 6ヶ月後も脆弱なまま掲載継続</p>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:16px;">思い込みと現実のギャップ</h1>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:16px;">
  <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;padding:14px 16px;">
    <p style="font-size:0.65rem;color:#8b949e;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 8px;">ASSUMPTION（思い込み）</p>
    <p style="font-size:0.9rem;color:#f0f6fc;margin:0;line-height:1.7;">
      "AWS Marketplace に掲載されているなら<br>
      ある程度セキュリティが<br>担保されているはずだ"
    </p>
  </div>
  <div style="background:#161b22;border:1px solid #ef4444;border-radius:6px;padding:14px 16px;">
    <p style="font-size:0.65rem;color:#ef4444;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 8px;">REALITY（現実）</p>
    <p style="font-size:0.9rem;color:#f0f6fc;margin:0;line-height:1.7;">
      Marketplace は <span style="color:#ef4444;font-weight:700;">流通の場</span>にすぎない<br>
      バージョン管理・脆弱性対応は<br>
      <span style="color:#ef4444;font-weight:700;">ベンダー次第、利用者の責任</span>
    </p>
  </div>
</div>

<table style="width:100%;border-collapse:collapse;font-size:0.83rem;">
  <thead>
    <tr>
      <th style="background:#161b22;color:#f97316;padding:7px 14px;text-align:left;font-weight:600;border-bottom:1px solid #30363d;">項目</th>
      <th style="background:#161b22;color:#f97316;padding:7px 14px;text-align:left;font-weight:600;border-bottom:1px solid #30363d;">詳細</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:6px 14px;border-bottom:1px solid #21262d;color:#8b949e;">使用バージョン</td>
      <td style="padding:6px 14px;border-bottom:1px solid #21262d;color:#f0f6fc;font-family:'JetBrains Mono',monospace;">Dify Premium 1.4.2（2025年6月リリース）</td>
    </tr>
    <tr>
      <td style="padding:6px 14px;border-bottom:1px solid #21262d;color:#8b949e;">内包脆弱性</td>
      <td style="padding:6px 14px;border-bottom:1px solid #21262d;color:#f0f6fc;">
        <span style="font-family:'JetBrains Mono',monospace;color:#ef4444;">CVE-2025-55182</span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;background:rgba(239,68,68,0.12);color:#ef4444;padding:1px 7px;border-radius:3px;border:1px solid rgba(239,68,68,0.4);margin-left:8px;">CVSS 10.0</span>
        <span style="color:#8b949e;margin-left:8px;">(React2Shell)</span>
      </td>
    </tr>
    <tr>
      <td style="padding:6px 14px;color:#8b949e;">CVE 公開日</td>
      <td style="padding:6px 14px;color:#f0f6fc;">
        2025年12月
        <span style="color:#ef4444;font-weight:700;margin-left:8px;">← Dify リリースより 6ヶ月後も脆弱なまま掲載継続</span>
      </td>
    </tr>
  </tbody>
</table>

<div style="margin-top:12px;background:rgba(249,115,22,0.06);border:1px solid rgba(249,115,22,0.3);border-radius:6px;padding:9px 14px;font-size:0.82rem;color:#f0f6fc;line-height:1.6;">
  「掲載されているから安全」ではなく、<span style="color:#f97316;font-weight:700;">バージョンの鮮度とベンダーの脆弱性対応速度を自分で確認する</span>ことが不可欠
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:14px;">CVE-2025-55182 — React2Shell</h1>

<div style="display:grid;grid-template-columns:1fr 1.2fr;gap:16px;align-items:start;">
  <div>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;padding:14px;margin-bottom:12px;">
      <table style="width:100%;border-collapse:collapse;font-size:0.8rem;">
        <tbody>
          <tr>
            <td style="color:#8b949e;padding:4px 8px;white-space:nowrap;">脆弱性タイプ</td>
            <td style="color:#ef4444;font-weight:700;padding:4px 8px;">RCE（リモートコード実行）</td>
          </tr>
          <tr>
            <td style="color:#8b949e;padding:4px 8px;">CVSS スコア</td>
            <td style="font-family:'JetBrains Mono',monospace;color:#ef4444;font-weight:700;font-size:1.15rem;padding:4px 8px;">10.0 / 10.0</td>
          </tr>
          <tr>
            <td style="color:#8b949e;padding:4px 8px;">認証要否</td>
            <td style="color:#ef4444;font-weight:700;padding:4px 8px;">不要（認証なしで RCE）</td>
          </tr>
          <tr>
            <td style="color:#8b949e;padding:4px 8px;white-space:nowrap;">影響コンポーネント</td>
            <td style="font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#e6edf3;padding:4px 8px;">React Server Components</td>
          </tr>
          <tr>
            <td style="color:#8b949e;padding:4px 8px;">影響バージョン</td>
            <td style="font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#e6edf3;padding:4px 8px;">React 19.0.0 / Next.js 15.2.3</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.25);border-radius:6px;padding:11px 14px;font-size:0.82rem;color:#e6edf3;line-height:1.65;">
      CVE 公開（2025/12）時点でインターネット上に<br>
      <span style="color:#ef4444;font-weight:700;">脆弱な Dify インスタンスが多数稼働</span><br>
      攻撃者はすでに PoC を持っていた
    </div>
  </div>
  <div>
    <p style="font-size:0.65rem;color:#f97316;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 8px;">ESTIMATED ATTACK FLOW</p>
    <div style="background:#161b22;border-left:3px solid #f97316;padding:12px 16px;border-radius:0 4px 4px 0;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#e6edf3;line-height:1.9;">
      攻撃者<br>
      <span style="color:#484f58;">  ↓  CVE-2025-55182 exploit</span><br>
      ALB → EC2 <span style="color:#ef4444;">[RCE成功]</span><br>
      <span style="color:#484f58;">  ↓  Phase 1: 初期侵入</span><br>
      XMRig マイナーダウンロード<br>
      ポートスキャンツール設置<br>
      Backdoor (Mythic C2) 設置<br>
      <span style="color:#484f58;">  ↓  Phase 2: マルウェア展開（2日間）</span><br>
      C&amp;C サーバーと接続・命令受信<br>
      <span style="color:#484f58;">  ↓  Phase 3: 悪意ある活動（約4.5日間）</span><br>
      <span style="color:#ef4444;">マイニング + ポートスキャン 2,360回</span>
    </div>
    <div style="margin-top:10px;background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.3);border-radius:6px;padding:9px 14px;font-size:0.8rem;color:#e6edf3;display:flex;align-items:center;gap:12px;">
      <span style="color:#22c55e;font-weight:700;font-family:'JetBrains Mono',monospace;white-space:nowrap;">✅ 現在は修正済み</span>
      <span>Dify Premium は現在 <strong style="color:#22c55e;">v1.13.2</strong> — CVE-2025-55182 は是正済み</span>
    </div>
  </div>
</div>

---
layout: section
background: '#0d1117'
---

<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center;height:100%;">
  <div>
    <p style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#f97316;letter-spacing:0.12em;margin-bottom:12px;">CHAPTER 03</p>
    <h1 style="color:#f0f6fc;font-size:2.4rem;font-weight:700;line-height:1.3;">調査で判明した<br>侵害の実態</h1>
  </div>
  <div style="opacity:0.55;display:flex;flex-direction:column;gap:10px;">
    <div style="background:#161b22;border-left:3px solid #ef4444;padding:10px 14px;border-radius:0 4px 4px 0;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#8b949e;">
      XMRig マイニング（Monero）<span style="color:#ef4444;margin-left:8px;">CPU 87-94%</span>
    </div>
    <div style="background:#161b22;border-left:3px solid #ef4444;padding:10px 14px;border-radius:0 4px 4px 0;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#8b949e;">
      Backdoor:EC2/C&amp;CActivity.B<span style="color:#ef4444;margin-left:8px;">Mythic C2</span>
    </div>
    <div style="background:#161b22;border-left:3px solid #ef4444;padding:10px 14px;border-radius:0 4px 4px 0;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#8b949e;">
      Network OUT<span style="color:#ef4444;margin-left:8px;">100 GB / 日</span>
    </div>
    <p style="font-size:0.7rem;color:#8b949e;font-family:'JetBrains Mono',monospace;margin:4px 0 0;">GuardDuty 検知 19件 — All Critical</p>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:14px;">GuardDuty は全部見ていた</h1>

<div style="display:grid;grid-template-columns:1.4fr 1fr;gap:18px;align-items:start;">
  <div>
    <p style="font-size:0.82rem;color:#8b949e;margin:0 0 10px;">
      侵害から約24時間後（2日目 06:13）から継続的に検知。
      全 <span style="color:#ef4444;font-weight:700;">19件がすべて Critical レベル</span>。
    </p>
    <table style="width:100%;border-collapse:collapse;font-size:0.78rem;">
      <thead>
        <tr>
          <th style="background:#161b22;color:#f97316;padding:6px 10px;text-align:left;font-weight:600;border-bottom:1px solid #30363d;">検知タイプ</th>
          <th style="background:#161b22;color:#f97316;padding:6px 10px;text-align:left;font-weight:600;border-bottom:1px solid #30363d;">内容</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#e6edf3;">Impact:EC2/PortSweep</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#ef4444;font-weight:600;">2,360回 のポートスキャン</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#e6edf3;">CryptoCurrency:EC2/BitcoinTool.B</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#e6edf3;">XMRig マイニング（Monero）</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#e6edf3;">CryptoCurrency:Runtime/BitcoinTool.B</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#e6edf3;">コンテナ内でのマイニング検知</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#e6edf3;">UnauthorizedAccess:EC2/TorRelay</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#e6edf3;">Tor リレーノードとの通信</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#e6edf3;">UnauthorizedAccess:EC2/TorClient</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#e6edf3;">Tor エントリーノードとの通信</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#e6edf3;">Backdoor:EC2/C&amp;CActivity.B</td>
          <td style="padding:5px 10px;color:#ef4444;font-weight:600;">Mythic C2 サーバー通信</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;padding:16px;text-align:center;">
      <p style="font-size:0.65rem;color:#8b949e;font-family:'JetBrains Mono',monospace;margin:0 0 4px;">FIRST DETECTION</p>
      <p style="font-family:'JetBrains Mono',monospace;color:#f97316;font-size:1.2rem;font-weight:700;margin:0 0 2px;">2日目 06:13</p>
      <p style="font-size:0.72rem;color:#8b949e;margin:0 0 16px;">侵害から約24時間後</p>
      <hr style="border:none;border-top:1px solid #21262d;margin-bottom:14px;" />
      <p style="font-size:0.65rem;color:#8b949e;font-family:'JetBrains Mono',monospace;margin:0 0 4px;">NOTIFIED VIA</p>
      <p style="font-family:'JetBrains Mono',monospace;color:#ef4444;font-size:1.2rem;font-weight:700;margin:0 0 2px;">9日目 22:24</p>
      <p style="font-size:0.72rem;color:#8b949e;margin:0 0 16px;">AWS Abuse Report で初めて気づく</p>
      <hr style="border:none;border-top:1px solid #21262d;margin-bottom:14px;" />
      <p style="font-size:0.72rem;color:#ef4444;font-weight:700;margin:0;">
        検知 → 気づくまで<br>
        <span style="font-family:'JetBrains Mono',monospace;font-size:2rem;line-height:1.2;">7日間</span>
      </p>
    </div>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:20px;">被害者でありながら、加害者になるという現実</h1>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;">
  <div>
    <p style="font-size:0.82rem;color:#8b949e;margin:0 0 12px;line-height:1.7;">
      GuardDuty が検知した <span style="font-family:'JetBrains Mono',monospace;color:#ef4444;">Impact:EC2/PortSweep</span> の2,360件はすべて、
      侵害された EC2 から<strong style="color:#f0f6fc;">第三者の組織に向けて実行された攻撃</strong>です。
    </p>
    <div style="display:flex;flex-direction:column;gap:10px;">
      <div style="background:#161b22;border-left:3px solid #ef4444;padding:11px 14px;border-radius:0 4px 4px 0;font-size:0.82rem;color:#e6edf3;line-height:1.6;">
        <strong style="color:#ef4444;">攻撃を受けた組織</strong>からすると、<br>
        攻撃元はこの AWS アカウント
      </div>
      <div style="background:#161b22;border-left:3px solid #f97316;padding:11px 14px;border-radius:0 4px 4px 0;font-size:0.82rem;color:#e6edf3;line-height:1.6;">
        <strong style="color:#f97316;">Abuse Report が届いたのは</strong>、<br>
        その被害者が AWS に通報したから
      </div>
      <div style="background:#161b22;border-left:3px solid #22c55e;padding:11px 14px;border-radius:0 4px 4px 0;font-size:0.82rem;color:#e6edf3;line-height:1.6;">
        <strong style="color:#22c55e;">インシデントに気づいたきっかけ</strong>は<br>
        他者を攻撃していたから届いた通報
      </div>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:12px;">
    <div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.3);border-radius:6px;padding:16px;text-align:center;">
      <p style="font-size:0.65rem;color:#ef4444;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 10px;">WHAT ACTUALLY HAPPENED</p>
      <p style="font-family:'JetBrains Mono',monospace;color:#ef4444;font-size:2rem;font-weight:700;margin:0 0 4px;line-height:1;">2,360回</p>
      <p style="font-size:0.75rem;color:#8b949e;margin:0 0 12px;">他の組織への攻撃（7日間）</p>
      <hr style="border:none;border-top:1px solid #21262d;margin-bottom:12px;" />
      <p style="font-size:0.82rem;color:#f0f6fc;margin:0;line-height:1.6;">
        「自分が損するだけ」は<br>
        <strong style="color:#ef4444;">根本的に誤った考え方</strong>
      </p>
    </div>
    <div style="background:rgba(249,115,22,0.07);border:1px solid rgba(249,115,22,0.3);border-radius:6px;padding:13px 14px;font-size:0.82rem;color:#f0f6fc;line-height:1.7;">
      セキュリティ対策は自分を守るためだけでなく<br>
      <span style="color:#f97316;font-weight:700;">他者への攻撃加担を防ぐ責任</span>でもある
    </div>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:14px;">CPU とネットワークが語る侵害の進行</h1>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
  <div>
    <p style="font-size:0.65rem;color:#f97316;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 7px;">CPU UTILIZATION — c5.2xlarge (8 vCPU)</p>
    <table style="width:100%;border-collapse:collapse;font-size:0.8rem;">
      <thead>
        <tr>
          <th style="background:#161b22;color:#f97316;padding:6px 10px;text-align:left;border-bottom:1px solid #30363d;">期間</th>
          <th style="background:#161b22;color:#f97316;padding:6px 10px;text-align:left;border-bottom:1px solid #30363d;">CPU</th>
          <th style="background:#161b22;color:#f97316;padding:6px 10px;text-align:left;border-bottom:1px solid #30363d;">状態</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#8b949e;">1日目 〜 2日目</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;color:#22c55e;">1-7%</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#22c55e;font-size:0.78rem;">正常</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#8b949e;">2日目 〜 4日目</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;color:#eab308;">7-17%</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#eab308;font-size:0.78rem;">マルウェア展開中</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#8b949e;">4日目 08:00〜</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;color:#f97316;">43-84%</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#f97316;font-size:0.78rem;">マイニング開始</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;color:#f0f6fc;font-weight:600;">4日目 14:00〜</td>
          <td style="padding:5px 10px;font-family:'JetBrains Mono',monospace;color:#ef4444;font-weight:700;">87-94%</td>
          <td style="padding:5px 10px;color:#ef4444;font-size:0.78rem;font-weight:700;">🔴 全開 (4.5日継続)</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div>
    <p style="font-size:0.65rem;color:#f97316;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 7px;">NETWORK OUT</p>
    <table style="width:100%;border-collapse:collapse;font-size:0.8rem;margin-bottom:12px;">
      <thead>
        <tr>
          <th style="background:#161b22;color:#f97316;padding:6px 10px;text-align:left;border-bottom:1px solid #30363d;">期間</th>
          <th style="background:#161b22;color:#f97316;padding:6px 10px;text-align:left;border-bottom:1px solid #30363d;">送信量/時</th>
          <th style="background:#161b22;color:#f97316;padding:6px 10px;text-align:left;border-bottom:1px solid #30363d;">送信量/日</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#8b949e;">2日目 〜 3日目</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;color:#e6edf3;">1.5 GB</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;color:#e6edf3;">36 GB</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;color:#f0f6fc;font-weight:600;">4日目 〜 9日目</td>
          <td style="padding:5px 10px;font-family:'JetBrains Mono',monospace;color:#ef4444;font-weight:700;">4.2 GB</td>
          <td style="padding:5px 10px;font-family:'JetBrains Mono',monospace;color:#ef4444;font-weight:700;">100 GB</td>
        </tr>
      </tbody>
    </table>
    <div style="background:rgba(234,179,8,0.08);border:1px solid rgba(234,179,8,0.3);border-radius:6px;padding:10px 14px;font-size:0.82rem;color:#eab308;line-height:1.65;">
      💡 <strong>CPU 80%超が30分継続</strong> でアラートがあれば<br>
      <span style="color:#f0f6fc;">4日目 14:00 に異常を検知できた</span><br>
      <span style="font-size:0.75rem;color:#8b949e;">→ 被害期間を7日から約3日に短縮できた</span>
    </div>
  </div>
</div>

<div style="margin-top:16px;">
  <p style="font-size:0.65rem;color:#f97316;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 8px;">CPU UTILIZATION — VISUAL</p>
  <div style="display:flex;flex-direction:column;gap:6px;">
    <div style="display:flex;align-items:center;gap:10px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#8b949e;white-space:nowrap;width:110px;">1〜2日目</span>
      <div style="flex:1;background:#21262d;border-radius:3px;height:14px;overflow:hidden;">
        <div style="width:7%;height:100%;background:#22c55e;border-radius:3px;"></div>
      </div>
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#22c55e;width:60px;">1–7%</span>
      <span style="font-size:0.7rem;color:#22c55e;">正常</span>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#8b949e;white-space:nowrap;width:110px;">2〜4日目</span>
      <div style="flex:1;background:#21262d;border-radius:3px;height:14px;overflow:hidden;">
        <div style="width:17%;height:100%;background:#eab308;border-radius:3px;"></div>
      </div>
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#eab308;width:60px;">7–17%</span>
      <span style="font-size:0.7rem;color:#eab308;">マルウェア展開</span>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#8b949e;white-space:nowrap;width:110px;">4日目 08:00〜</span>
      <div style="flex:1;background:#21262d;border-radius:3px;height:14px;overflow:hidden;">
        <div style="width:84%;height:100%;background:#f97316;border-radius:3px;"></div>
      </div>
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#f97316;width:60px;">43–84%</span>
      <span style="font-size:0.7rem;color:#f97316;">マイニング開始</span>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#f0f6fc;white-space:nowrap;font-weight:700;width:110px;">4日目 14:00〜</span>
      <div style="flex:1;background:#21262d;border-radius:3px;height:14px;overflow:hidden;">
        <div style="width:94%;height:100%;background:#ef4444;border-radius:3px;"></div>
      </div>
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#ef4444;font-weight:700;width:60px;">87–94%</span>
      <span style="font-size:0.7rem;color:#ef4444;font-weight:700;">全開 4.5日継続</span>
    </div>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:14px;">ネットワーク構成と「幸運な事実」</h1>

<div style="display:grid;grid-template-columns:1.5fr 1fr;gap:18px;align-items:start;">
  <div>
    <p style="font-size:0.65rem;color:#f97316;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 7px;">NETWORK ARCHITECTURE</p>
    <div style="background:#161b22;border-left:3px solid #f97316;padding:13px 16px;border-radius:0 4px 4px 0;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#e6edf3;line-height:1.9;">
      Internet<br>
      <span style="color:#484f58;">  │ HTTPS</span><br>
      <span style="color:#484f58;">  ↓</span><br>
      ALB <span style="color:#8b949e;">(パブリックサブネット)</span><br>
      <span style="color:#484f58;">  │ HTTP</span><br>
      <span style="color:#484f58;">  ↓</span><br>
      <span style="color:#ef4444;">EC2 [Dify / 侵害済み]</span> <span style="color:#8b949e;">(プライベート)</span><br>
      <span style="color:#ef4444;">  │ Port Scan 2,360回</span><br>
      <span style="color:#484f58;">  ↓</span><br>
      NAT Gateway <span style="color:#eab308;">(踏み台として悪用)</span><br>
      <span style="color:#ef4444;">  │ 外部に向けて攻撃</span><br>
      <span style="color:#484f58;">  ↓</span><br>
      外部ホスト（攻撃対象）<br>
      <br>
      <span style="color:#ef4444;">攻撃者 ←→ NAT Gateway ←→ EC2</span><br>
      <span style="color:#484f58;">      （C&amp;C通信 / Tor経由）</span>
    </div>
  </div>
  <div>
    <div style="background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.3);border-radius:6px;padding:14px;margin-bottom:12px;">
      <p style="font-size:0.65rem;color:#22c55e;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 8px;">✅ LUCKY FACT</p>
      <p style="font-size:0.88rem;color:#f0f6fc;margin:0 0 8px;line-height:1.6;">
        EC2 に <strong>IAM インスタンスプロファイルが未設定</strong>だった
      </p>
      <p style="font-size:0.78rem;color:#8b949e;margin:0;line-height:1.5;">
        もし <code>AdministratorAccess</code> が付与されていたら...<br>
        • 高額な EC2 インスタンスの大量起動<br>
        • S3 バケットからの機密データ窃取<br>
        • IAM 権限の昇格・横展開<br>
        • Bedrock 経由の LLM 不正呼び出し
      </p>
    </div>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;padding:11px 14px;font-size:0.8rem;line-height:1.6;margin-bottom:10px;">
      <span style="color:#8b949e;">CloudTrail 確認 →</span><br>
      <span style="color:#22c55e;font-weight:600;">特権昇格 API コールは一切なし</span><br>
      <span style="color:#f0f6fc;">被害は EC2 内に完全に封じ込め</span>
    </div>
    <p style="font-size:0.72rem;color:#8b949e;margin:0;line-height:1.5;">
      ※ プライベートサブネット配置のため直接アクセス不可だったが、NAT Gateway 経由で外部との通信が可能だったため攻撃の踏み台として悪用された
    </p>
  </div>
</div>

---
layout: section
background: '#0d1117'
---

<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center;height:100%;">
  <div>
    <p style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#f97316;letter-spacing:0.12em;margin-bottom:12px;">CHAPTER 04</p>
    <h1 style="color:#f0f6fc;font-size:2.4rem;font-weight:700;line-height:1.3;">なぜ7日間<br>気付けなかったのか</h1>
  </div>
  <div style="opacity:0.55;display:flex;flex-direction:column;gap:12px;">
    <div style="display:flex;align-items:baseline;gap:10px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#8b949e;white-space:nowrap;">失敗 01</span>
      <span style="font-size:0.82rem;color:#ef4444;">GuardDuty 通知未設定</span>
    </div>
    <div style="display:flex;align-items:baseline;gap:10px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#8b949e;white-space:nowrap;">失敗 02</span>
      <span style="font-size:0.82rem;color:#ef4444;">CloudWatch アラーム未設定</span>
    </div>
    <div style="display:flex;align-items:baseline;gap:10px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#8b949e;white-space:nowrap;">失敗 03</span>
      <span style="font-size:0.82rem;color:#ef4444;">「検証環境だから」という油断</span>
    </div>
    <div style="margin-top:4px;border-top:1px solid #21262d;padding-top:12px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#8b949e;">検知から通知まで</span>
      <span style="font-family:'JetBrains Mono',monospace;font-size:2.2rem;font-weight:700;color:#ef4444;margin-left:10px;line-height:1;">7<span style="font-size:1rem;">日間</span></span>
    </div>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:18px;">3つの検知失敗</h1>

<div style="display:flex;flex-direction:column;gap:12px;">
  <div style="display:grid;grid-template-columns:44px 1fr;gap:14px;align-items:start;background:#161b22;border-radius:6px;padding:14px 16px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:1.8rem;color:#ef4444;font-weight:700;line-height:1;padding-top:2px;">01</span>
    <div>
      <p style="font-size:0.95rem;font-weight:700;color:#f0f6fc;margin:0 0 5px;">GuardDuty の通知設定が未実施</p>
      <p style="font-size:0.82rem;color:#8b949e;margin:0;line-height:1.55;">
        SNS / EventBridge によるアラートを設定していなかった。19件の Critical 検知がコンソールに溜まったまま、誰も見ていなかった。
        <span style="color:#ef4444;font-weight:600;">「有効化した」≠「通知設定した」</span>
      </p>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:44px 1fr;gap:14px;align-items:start;background:#161b22;border-radius:6px;padding:14px 16px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:1.8rem;color:#ef4444;font-weight:700;line-height:1;padding-top:2px;">02</span>
    <div>
      <p style="font-size:0.95rem;font-weight:700;color:#f0f6fc;margin:0 0 5px;">CloudWatch アラームの未設定</p>
      <p style="font-size:0.82rem;color:#8b949e;margin:0;line-height:1.55;">
        CPU 90% 台が4.5日継続、ネットワーク送信100GB/日が5日続いても、誰にも通知が飛ばなかった。異常なメトリクスはコンソールに記録されていたが見ていなかった。
      </p>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:44px 1fr;gap:14px;align-items:start;background:#161b22;border-radius:6px;padding:14px 16px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:1.8rem;color:#ef4444;font-weight:700;line-height:1;padding-top:2px;">03</span>
    <div>
      <p style="font-size:0.95rem;font-weight:700;color:#f0f6fc;margin:0 0 5px;">「検証環境だから」という油断</p>
      <p style="font-size:0.82rem;color:#8b949e;margin:0;line-height:1.55;">
        "細かい監視設定は後でいい"——この判断が7日間という検知遅延の直接の原因。攻撃者にとって検証環境か本番環境かは関係ない。踏み台として使えれば十分。
      </p>
    </div>
  </div>
</div>

<div style="margin-top:14px;background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.3);border-radius:6px;padding:10px 16px;font-size:0.85rem;color:#f0f6fc;line-height:1.7;">
  気づかなかった7日間、EC2 は <span style="color:#ef4444;font-weight:700;">第三者の組織に2,360回の攻撃を行い続けていた</span>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:14px;">実際のインシデント対応と反省</h1>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
  <div>
    <p style="font-size:0.65rem;color:#22c55e;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 7px;">WHAT WE DID ✅</p>
    <table style="width:100%;border-collapse:collapse;font-size:0.8rem;">
      <thead>
        <tr>
          <th style="background:#161b22;color:#f97316;padding:5px 10px;text-align:left;border-bottom:1px solid #30363d;">#</th>
          <th style="background:#161b22;color:#f97316;padding:5px 10px;text-align:left;border-bottom:1px solid #30363d;">対応内容</th>
          <th style="background:#161b22;color:#f97316;padding:5px 10px;text-align:left;border-bottom:1px solid #30363d;">時刻</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;color:#22c55e;">1</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#e6edf3;">GuardDuty 検知内容確認</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#8b949e;">9日目 22:30</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;color:#22c55e;">2</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#e6edf3;">影響範囲特定（CloudTrail）</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#8b949e;">9日目 22:45</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;font-family:'JetBrains Mono',monospace;color:#22c55e;">3</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#e6edf3;">IAM 権限悪用の有無確認</td>
          <td style="padding:5px 10px;border-bottom:1px solid #21262d;color:#8b949e;">9日目 23:15</td>
        </tr>
        <tr>
          <td style="padding:5px 10px;font-family:'JetBrains Mono',monospace;color:#22c55e;">4</td>
          <td style="padding:5px 10px;color:#e6edf3;">EC2 インスタンス終了</td>
          <td style="padding:5px 10px;color:#8b949e;">10日目 00:30</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div>
    <p style="font-size:0.65rem;color:#ef4444;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 7px;">WHAT WE MISSED ❌（フォレンジック証拠保全）</p>
    <div style="display:flex;flex-direction:column;gap:8px;">
      <div style="background:#161b22;border-left:3px solid #ef4444;padding:9px 12px;border-radius:0 4px 4px 0;font-size:0.82rem;">
        <p style="color:#f0f6fc;margin:0 0 2px;">封じ込め（SG で通信遮断）が先</p>
        <p style="color:#8b949e;font-size:0.75rem;margin:0;">→ 安全にインターネットから切り離してから調査</p>
      </div>
      <div style="background:#161b22;border-left:3px solid #ef4444;padding:9px 12px;border-radius:0 4px 4px 0;font-size:0.82rem;">
        <p style="color:#f0f6fc;margin:0 0 2px;">EBS スナップショット未取得</p>
        <p style="color:#8b949e;font-size:0.75rem;margin:0;">→ マルウェア詳細分析ができなかった</p>
      </div>
      <div style="background:#161b22;border-left:3px solid #ef4444;padding:9px 12px;border-radius:0 4px 4px 0;font-size:0.82rem;">
        <p style="color:#f0f6fc;margin:0 0 2px;">メモリダンプ未取得</p>
        <p style="color:#8b949e;font-size:0.75rem;margin:0;">→ 実行中プロセスの解析不可</p>
      </div>
      <div style="background:#161b22;border-left:3px solid #ef4444;padding:9px 12px;border-radius:0 4px 4px 0;font-size:0.82rem;">
        <p style="color:#f0f6fc;margin:0 0 2px;">VPC Flow Logs 詳細未分析</p>
        <p style="color:#8b949e;font-size:0.75rem;margin:0;">→ 全通信先の特定ができなかった</p>
      </div>
    </div>
    <div style="background:rgba(234,179,8,0.08);border:1px solid rgba(234,179,8,0.3);border-radius:6px;padding:10px 12px;margin-top:9px;font-size:0.8rem;color:#eab308;line-height:1.6;">
      ⚠ <strong>インスタンス終了は最後の手段</strong><br>
      <span style="color:#f0f6fc;">先に封じ込め・証拠保全 → その後に終了</span>
    </div>
  </div>
</div>

---
layout: section
background: '#0d1117'
---

<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center;height:100%;">
  <div>
    <p style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#f97316;letter-spacing:0.12em;margin-bottom:12px;">CHAPTER 05</p>
    <h1 style="color:#f0f6fc;font-size:2.4rem;font-weight:700;line-height:1.3;">検証前に整えるべき<br>セキュリティ体制</h1>
  </div>
  <div style="opacity:0.55;display:flex;flex-direction:column;gap:12px;">
    <div style="display:flex;align-items:center;gap:14px;background:#161b22;border-radius:6px;padding:12px 16px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:#f97316;min-width:28px;">①</span>
      <span style="font-size:0.82rem;color:#e6edf3;">AMI バージョン・CVE 確認</span>
    </div>
    <div style="display:flex;align-items:center;gap:14px;background:#161b22;border-radius:6px;padding:12px 16px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:#f97316;min-width:28px;">②</span>
      <span style="font-size:0.82rem;color:#e6edf3;">GuardDuty 通知設定</span>
    </div>
    <div style="display:flex;align-items:center;gap:14px;background:#161b22;border-radius:6px;padding:12px 16px;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:#f97316;min-width:28px;">③</span>
      <span style="font-size:0.82rem;color:#e6edf3;">IAM 最小権限（NHI）</span>
    </div>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:10px;">最低限の 3つの対策</h1>

<p style="font-size:0.82rem;color:#8b949e;margin:0 0 14px;line-height:1.6;">
  「本番環境だけの話」ではありません——開発・検証環境でも侵害されれば他者への攻撃の踏み台になります。
</p>

<div style="display:flex;flex-direction:column;gap:11px;">
  <div style="display:grid;grid-template-columns:44px 1fr;gap:14px;align-items:start;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:14px 16px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:1.8rem;color:#f97316;font-weight:700;line-height:1;padding-top:2px;">①</span>
    <div>
      <p style="font-size:0.95rem;font-weight:700;color:#f97316;margin:0 0 5px;">Marketplace AMI のバージョン・脆弱性確認</p>
      <p style="font-size:0.82rem;color:#8b949e;margin:0;line-height:1.55;">
        デプロイ前に最新バージョンか確認し、内包ソフトウェアの CVE をベンダーの GitHub・セキュリティアドバイザリで調べる。脆弱なバージョンが侵害の入口になれば他者への攻撃の踏み台になる。
      </p>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:44px 1fr;gap:14px;align-items:start;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:14px 16px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:1.8rem;color:#f97316;font-weight:700;line-height:1;padding-top:2px;">②</span>
    <div>
      <p style="font-size:0.95rem;font-weight:700;color:#f97316;margin:0 0 5px;">GuardDuty の通知設定（有効化だけでは不十分）</p>
      <p style="font-size:0.82rem;color:#8b949e;margin:0;line-height:1.55;">
        EventBridge → SNS → Email/Slack で Critical 検知を即座に通知。<span style="color:#f0f6fc;">有効化のみ ≒ 有効化していないのと同じ。</span>これだけで7日間 → 数時間に短縮できた。
      </p>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:44px 1fr;gap:14px;align-items:start;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:14px 16px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:1.8rem;color:#f97316;font-weight:700;line-height:1;padding-top:2px;">③</span>
    <div>
      <p style="font-size:0.95rem;font-weight:700;color:#f97316;margin:0 0 5px;">コンピューティングサービスへの IAM 権限を最小権限に</p>
      <p style="font-size:0.82rem;color:#8b949e;margin:0;line-height:1.55;">
        特に Non-Human Identity（NHI）の権限は十分注意。今回はインスタンスプロファイル未設定が唯一の功績。<span style="color:#f0f6fc;">必要最小限の権限のみを付与する。</span>
      </p>
    </div>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:14px;">対策① バージョン・脆弱性確認の手順</h1>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start;">
  <div>
    <p style="font-size:0.65rem;color:#f97316;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 8px;">BEFORE DEPLOY CHECKLIST</p>
    <div style="display:flex;flex-direction:column;gap:8px;">
      <div style="background:#161b22;border-left:3px solid #f97316;padding:10px 14px;border-radius:0 4px 4px 0;font-size:0.82rem;">
        <p style="color:#f97316;font-weight:700;margin:0 0 3px;">1. Marketplace の AMI バージョン確認</p>
        <p style="color:#8b949e;margin:0;line-height:1.5;">製品ページのバージョン履歴で最新版かチェック</p>
      </div>
      <div style="background:#161b22;border-left:3px solid #f97316;padding:10px 14px;border-radius:0 4px 4px 0;font-size:0.82rem;">
        <p style="color:#f97316;font-weight:700;margin:0 0 3px;">2. ベンダーの GitHub / Security Advisory 確認</p>
        <p style="color:#8b949e;margin:0;line-height:1.5;">CVE が公開されていないか、パッチは当たっているか</p>
      </div>
      <div style="background:#161b22;border-left:3px solid #f97316;padding:10px 14px;border-radius:0 4px 4px 0;font-size:0.82rem;">
        <p style="color:#f97316;font-weight:700;margin:0 0 3px;">3. 内包コンポーネントの CVE 確認</p>
        <p style="color:#8b949e;margin:0;line-height:1.5;">今回: Dify 1.4.2 → React 19.0.0 → CVE-2025-55182</p>
      </div>
    </div>
  </div>
  <div>
    <p style="font-size:0.65rem;color:#ef4444;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 8px;">TODAY'S INCIDENT IN TIMELINE</p>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;padding:14px;font-size:0.8rem;line-height:1.8;">
      <div style="display:flex;gap:10px;align-items:center;margin-bottom:8px;">
        <span style="font-family:'JetBrains Mono',monospace;color:#8b949e;white-space:nowrap;">2025/06</span>
        <span style="color:#e6edf3;">Dify 1.4.2 リリース</span>
      </div>
      <div style="display:flex;gap:10px;align-items:center;margin-bottom:8px;">
        <span style="font-family:'JetBrains Mono',monospace;color:#ef4444;white-space:nowrap;">2025/12</span>
        <span style="color:#ef4444;font-weight:600;">CVE-2025-55182 公開</span>
      </div>
      <div style="display:flex;gap:10px;align-items:center;margin-bottom:8px;opacity:0.6;">
        <span style="font-family:'JetBrains Mono',monospace;color:#8b949e;white-space:nowrap;">　 〜</span>
        <span style="color:#8b949e;">脆弱なバージョンが Marketplace に掲載継続</span>
      </div>
      <div style="display:flex;gap:10px;align-items:center;margin-bottom:8px;">
        <span style="font-family:'JetBrains Mono',monospace;color:#ef4444;white-space:nowrap;">2026/02</span>
        <span style="color:#ef4444;font-weight:600;">インシデント発生</span>
      </div>
      <div style="display:flex;gap:10px;align-items:center;">
        <span style="font-family:'JetBrains Mono',monospace;color:#22c55e;white-space:nowrap;">2026/04</span>
        <span style="color:#22c55e;">v1.13.2 に更新・CVE 是正済み</span>
      </div>
    </div>
    <div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.25);border-radius:6px;padding:9px 14px;margin-top:10px;font-size:0.8rem;color:#e6edf3;line-height:1.5;">
      CVE 公開から約 <strong style="color:#ef4444;">2ヶ月後</strong> に被害発生<br>
      その間、Marketplace には脆弱版が掲載され続けていた
    </div>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:14px;">対策② GuardDuty — 通知を即時に受け取る</h1>

<div style="display:grid;grid-template-columns:1.2fr 1fr;gap:18px;align-items:start;">
  <div>
    <p style="font-size:0.65rem;color:#f97316;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 7px;">EVENTBRIDGE RULE — EVENT PATTERN</p>
    <div style="background:#161b22;border-left:3px solid #f97316;padding:12px 16px;border-radius:0 4px 4px 0;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#e6edf3;line-height:1.8;">
      {<br>
      &nbsp;&nbsp;<span style="color:#22c55e;">"source"</span>: [<span style="color:#f97316;">"aws.guardduty"</span>],<br>
      &nbsp;&nbsp;<span style="color:#22c55e;">"detail-type"</span>: [<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#f97316;">"GuardDuty Finding"</span><br>
      &nbsp;&nbsp;],<br>
      &nbsp;&nbsp;<span style="color:#22c55e;">"detail"</span>: {<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#22c55e;">"severity"</span>: [{<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#22c55e;">"numeric"</span>: [<span style="color:#f97316;">"&gt;=", 7</span>]<br>
      &nbsp;&nbsp;&nbsp;&nbsp;}]<br>
      &nbsp;&nbsp;}<br>
      }
    </div>
  </div>
  <div>
    <p style="font-size:0.65rem;color:#f97316;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 7px;">NOTIFICATION FLOW</p>
    <div style="background:#161b22;border-left:3px solid #22c55e;padding:12px 16px;border-radius:0 4px 4px 0;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#e6edf3;line-height:1.9;margin-bottom:14px;">
      GuardDuty Finding<br>
      <span style="color:#484f58;">  ↓</span><br>
      EventBridge Rule<br>
      <span style="color:#484f58;">  (severity &gt;= 7.0)</span><br>
      <span style="color:#484f58;">  ↓</span><br>
      SNS Topic<br>
      <span style="color:#484f58;">  ↓</span><br>
      <span style="color:#22c55e;">Email / Slack 即時通知 ✅</span>
    </div>
    <div style="background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.3);border-radius:6px;padding:10px 14px;font-size:0.82rem;color:#22c55e;line-height:1.6;">
      これだけで<br>
      <span style="color:#f0f6fc;font-weight:700;">7日間 → 数時間</span> に短縮できた
    </div>
    <div style="margin-top:10px;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:9px 12px;">
      <p style="font-size:0.6rem;color:#8b949e;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 6px;">BEFORE / AFTER</p>
      <div style="display:flex;flex-direction:column;gap:5px;font-size:0.75rem;">
        <div style="display:flex;align-items:center;gap:6px;">
          <span style="color:#ef4444;font-family:'JetBrains Mono',monospace;font-size:0.65rem;white-space:nowrap;min-width:44px;">BEFORE</span>
          <span style="color:#8b949e;font-size:0.72rem;">通知設定なし → 7日後に Abuse Report</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;padding:0 4px;">
          <div style="flex:1;height:2px;background:#ef4444;border-radius:1px;"></div>
          <span style="color:#ef4444;font-size:0.65rem;white-space:nowrap;">7日間</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;margin-top:2px;">
          <span style="color:#22c55e;font-family:'JetBrains Mono',monospace;font-size:0.65rem;white-space:nowrap;min-width:44px;">AFTER</span>
          <span style="color:#8b949e;font-size:0.72rem;">EventBridge → SNS → Email/Slack</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;padding:0 4px;">
          <div style="flex:1;height:2px;background:#22c55e;border-radius:1px;"></div>
          <span style="color:#22c55e;font-size:0.65rem;font-weight:700;white-space:nowrap;">数時間</span>
        </div>
      </div>
    </div>
  </div>
</div>

---
background: '#0d1117'
---

<h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:14px;">対策③ IAM 最小権限——NHI の権限管理</h1>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
  <div>
    <p style="font-size:0.65rem;color:#ef4444;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 8px;">もし AdministratorAccess が付与されていたら</p>
    <div style="display:flex;flex-direction:column;gap:8px;">
      <div style="background:rgba(239,68,68,0.07);border-left:3px solid #ef4444;padding:10px 14px;border-radius:0 4px 4px 0;font-size:0.82rem;">
        <p style="color:#ef4444;font-weight:700;margin:0 0 2px;">💸 高額な EC2 インスタンスの大量起動</p>
        <p style="color:#8b949e;margin:0;font-size:0.75rem;">攻撃者がコンピューティングリソースを不正利用</p>
      </div>
      <div style="background:rgba(239,68,68,0.07);border-left:3px solid #ef4444;padding:10px 14px;border-radius:0 4px 4px 0;font-size:0.82rem;">
        <p style="color:#ef4444;font-weight:700;margin:0 0 2px;">🔓 S3 バケットからの機密データ窃取</p>
        <p style="color:#8b949e;margin:0;font-size:0.75rem;">顧客データ・認証情報・ソースコードの流出</p>
      </div>
      <div style="background:rgba(239,68,68,0.07);border-left:3px solid #ef4444;padding:10px 14px;border-radius:0 4px 4px 0;font-size:0.82rem;">
        <p style="color:#ef4444;font-weight:700;margin:0 0 2px;">🤖 Bedrock 経由の LLM 不正呼び出し</p>
        <p style="color:#8b949e;margin:0;font-size:0.75rem;">莫大な推論コストの発生</p>
      </div>
      <div style="background:rgba(239,68,68,0.07);border-left:3px solid #ef4444;padding:10px 14px;border-radius:0 4px 4px 0;font-size:0.82rem;">
        <p style="color:#ef4444;font-weight:700;margin:0 0 2px;">↗ IAM 権限の昇格・横展開</p>
        <p style="color:#8b949e;margin:0;font-size:0.75rem;">他のリソースへの侵害拡大</p>
      </div>
    </div>
  </div>
  <div>
    <p style="font-size:0.65rem;color:#22c55e;font-family:'JetBrains Mono',monospace;letter-spacing:0.1em;margin:0 0 8px;">BEST PRACTICE</p>
    <div style="background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.3);border-radius:6px;padding:14px;margin-bottom:12px;">
      <p style="font-size:0.88rem;color:#f0f6fc;margin:0 0 10px;font-weight:600;">最小権限の原則</p>
      <div style="display:flex;flex-direction:column;gap:7px;font-size:0.82rem;">
        <div style="color:#e6edf3;">✅ 必要な操作のみを許可する権限設計</div>
        <div style="color:#e6edf3;">✅ インスタンスプロファイルは必要な場合のみ付与</div>
        <div style="color:#e6edf3;">✅ ワイルドカード（<code style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;">*</code>）アクションを避ける</div>
        <div style="color:#e6edf3;">✅ リソース指定を具体的に絞り込む</div>
      </div>
    </div>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:6px;padding:12px 14px;font-size:0.82rem;line-height:1.6;">
      <p style="color:#f97316;font-weight:700;margin:0 0 5px;">特に Non-Human Identity（NHI）に注意</p>
      <p style="color:#8b949e;margin:0;line-height:1.5;">
        EC2・Lambda・ECS タスクなど人が直接操作しない ID への権限は見落としがち——今回の教訓
      </p>
    </div>
  </div>
</div>

---
layout: center
background: '#0d1117'
---

<div style="max-width:820px;margin:0 auto;">
  <h1 style="color:#f0f6fc;font-size:1.8rem;margin-bottom:18px;text-align:left;">まとめ</h1>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:11px;margin-bottom:18px;">
    <div style="background:#161b22;border-left:4px solid #ef4444;border-radius:0 6px 6px 0;padding:13px 15px;">
      <p style="font-size:0.65rem;font-family:'JetBrains Mono',monospace;color:#ef4444;letter-spacing:0.1em;margin:0 0 6px;">RISK</p>
      <p style="font-size:0.85rem;color:#f0f6fc;margin:0;line-height:1.6;">Marketplace でも CVSS 10.0 の脆弱性を含む AMI が提供され続ける——<strong>バージョン確認は自分の責任</strong></p>
    </div>
    <div style="background:#161b22;border-left:4px solid #ef4444;border-radius:0 6px 6px 0;padding:13px 15px;">
      <p style="font-size:0.65rem;font-family:'JetBrains Mono',monospace;color:#ef4444;letter-spacing:0.1em;margin:0 0 6px;">TRAP</p>
      <p style="font-size:0.85rem;color:#f0f6fc;margin:0;line-height:1.6;">GuardDuty の通知設定なし = 有効化していないのと同じ——<strong>検証環境も例外ではない</strong></p>
    </div>
    <div style="background:#161b22;border-left:4px solid #22c55e;border-radius:0 6px 6px 0;padding:13px 15px;">
      <p style="font-size:0.65rem;font-family:'JetBrains Mono',monospace;color:#22c55e;letter-spacing:0.1em;margin:0 0 6px;">MINIMUM</p>
      <p style="font-size:0.85rem;color:#f0f6fc;margin:0;line-height:1.6;">IAM 最小権限の原則は必須——<strong>今回はこれだけが救いだった</strong></p>
    </div>
    <div style="background:#161b22;border-left:4px solid #ef4444;border-radius:0 6px 6px 0;padding:13px 15px;">
      <p style="font-size:0.65rem;font-family:'JetBrains Mono',monospace;color:#ef4444;letter-spacing:0.1em;margin:0 0 6px;">IMPACT</p>
      <p style="font-size:0.85rem;color:#f0f6fc;margin:0;line-height:1.6;">侵害された EC2 は7日間で2,360回の攻撃を他の組織に実行——<strong style="color:#ef4444;">被害者が加害者になった</strong></p>
    </div>
  </div>

  <div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.3);border-radius:6px;padding:13px 18px;font-size:0.9rem;color:#f0f6fc;line-height:1.7;margin-bottom:14px;text-align:left;">
    自分のリソースが侵害されても、<strong style="color:#ef4444;">「検証環境だし自分が損するだけ」ではない</strong><br>
    侵害されたインスタンスは攻撃者の武器になり、<strong>その矛先は何の関係もない第三者に向かう</strong>
  </div>

  <div style="background:rgba(249,115,22,0.07);border:1px solid rgba(249,115,22,0.3);border-radius:6px;padding:13px 18px;font-size:0.88rem;color:#f0f6fc;line-height:1.7;margin-bottom:16px;text-align:left;">
    <span style="color:#f97316;font-weight:700;">Marketplace 製品であっても、検証環境であっても、セキュリティの基盤は最初から整える</span><br>
    <span style="font-size:0.8rem;color:#8b949e;display:block;margin-top:6px;">セキュリティ対策は「自分を守る」だけが目的ではない——<span style="color:#f97316;font-weight:600;">他者への攻撃加担を防ぐ責任</span>でもある</span>
  </div>

  <div style="text-align:right;font-size:0.78rem;">
    <span style="font-family:'JetBrains Mono',monospace;color:#f97316;margin-left:12px;">@k_hirasan</span>
  </div>
</div>

---
layout: center
background: '#0d1117'
---

<div style="text-align:center;">
  <h1 style="color:#f0f6fc;font-size:2.8rem;font-weight:700;margin-bottom:0;">ご清聴ありがとうございました！</h1>
</div>
