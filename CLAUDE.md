# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a [Zenn](https://zenn.dev/) content repository connected via Zenn CLI. Articles are written in Markdown and published to the `cscloud_blog` publication on Zenn.

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

## Images

Images go in `images/` with the naming convention: `{article-slug}_{timestamp}.png`

Reference in articles as: `![](/images/filename.png)`

## Article Conventions (from existing articles)

- Written in **Japanese**
- Start with a brief self-introduction line referencing the author's role at CSC / CloudFastener
- Use Zenn-specific Markdown extensions: `:::message` for info boxes, `:::message alert` for warnings
- Heading levels start at `##` (not `#`, since `#` is reserved for the title via frontmatter)
- URLs on their own line render as embed cards in Zenn (no need for `[text](url)` format)
- Main topics are AWS services and security
