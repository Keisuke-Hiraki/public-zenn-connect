# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a [Zenn](https://zenn.dev/) content repository connected via Zenn CLI. Articles are written in Markdown and published to the `cscloud_blog` publication on Zenn.

The repository has the following structure:

```
articles/       # Zenn articles (Markdown)
books/          # Zenn books (currently unused)
images/         # Article screenshots and diagrams
presentations/  # Slidev presentation decks (not published to Zenn)
```

## Article Frontmatter

Every article in `articles/` must have this frontmatter:

```yaml
---
title: "記事タイトル"
emoji: "🔧"
type: "tech"        # "tech" or "idea"
topics: ["aws", "security"]  # up to 5 lowercase tags
published: false    # set to true when ready to publish
publication_name: cscloud_blog
---
```

- `published: false` = draft; `published: true` = live on Zenn
- New articles start as `published: false`
- Filename becomes the article slug (e.g., `articles/my-article.md` → `zenn.dev/cscloud_blog/articles/my-article`)
- Filenames starting with `!` (e.g., `!securityhub-all-summary.md`) are work-in-progress drafts

## Images

Images go in `images/` with the naming convention: `{article-slug}_{timestamp}.png`

Reference in articles as: `![](/images/filename.png)`

Screenshots taken directly from macOS (Cmd+Shift+4) may be named with the `SCR-YYYYMMDD-XXXX` pattern.

## Article Conventions (from existing articles)

- Written in **Japanese**
- Start with a brief self-introduction line referencing the author's role at CSC / CloudFastener
  - Example: `こんにちは、CSC の [CloudFastener](https://cloud-fastener.com/) というプロダクトで TAM のポジションで働いている平木です！`
- Use Zenn-specific Markdown extensions: `:::message` for info boxes, `:::message alert` for warnings
- Heading levels start at `##` (not `#`, since `#` is reserved for the title via frontmatter)
- URLs on their own line render as embed cards in Zenn (no need for `[text](url)` format)
- Main topics are AWS services and security
- Common topic tags: `aws`, `security`, `kms`, `iam`, `guardduty`, `inspector`, `organizations`, `securityhub`, `mcp`
- Emojis are allowed only in the frontmatter `emoji` field — do not use emojis in article body text or headings
- UI element names (button labels, tab names, menu items) should be wrapped in backticks or 鉤括弧「」

## Article Structure Best Practices

These patterns improve readability for long or comparison-focused articles:

- **N行まとめ**: Long articles benefit from a `:::message` "この記事のN行まとめ" block immediately after the intro paragraph, before the first `##` section
- **Comparison table up front**: Articles comparing old vs. new features should include a summary comparison table right after the まとめ block — not only at the end — so readers understand the key differences before reading the details
- **Section introductory sentences**: Each `###` section should begin with one sentence summarizing what the section covers, so readers can decide whether to read it in detail
- **Technical appendix placement**: Developer-specific sections (API schemas, event formats, etc.) should be placed after `## まとめ`, with a `:::message` note at the top indicating they are optional reading for non-technical readers
- **No duplicate content**: If a comparison table or summary is placed at the top, remove or replace any duplicate section at the end to avoid repetition

## Screenshots

- Place screenshots in `images/` following the naming convention: `{article-slug}_{timestamp}.png`
- Before publishing, blur or redact sensitive information visible in screenshots:
  - AWS Account IDs (12-digit numbers)
  - ARNs containing real resource identifiers
  - KMS key IDs, role names, Organization IDs, policy IDs
  - Any internal tool names or bookmarks not relevant to the article content
- Browser bookmarks/toolbar items unrelated to the article topic do not need to be hidden

## Presentations

The `presentations/` directory contains [Slidev](https://sli.dev/) slide decks. These are **not** published to Zenn.

- Each deck lives in its own subdirectory (e.g., `presentations/aws-marketplace-seminar/`)
- Each deck has `slides.md` (Slidev Markdown), `package.json`, and an `image/` directory

## Article Review

Use the `/blog-review` skill to review a draft article before publishing. The skill checks for:
- Technical accuracy
- Inflammatory or controversial content risk
- Typos and writing errors
- Secrets and sensitive information in both text and screenshots
