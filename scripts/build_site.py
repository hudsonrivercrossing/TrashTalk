#!/usr/bin/env python3
"""Build the static Trash Talk homepage and HTML pages from publish-longform Markdown."""

from __future__ import annotations

import html
import re
import shutil
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISH_ROOT = ROOT / "transcripts" / "assemblyai"
SITE_ROOT = ROOT / "site"
LOGO_SOURCE = ROOT / "assets" / "branding" / "trash-talk-icon.svg"
LOGO_OUTPUT = SITE_ROOT / "assets" / "branding" / "trash-talk-icon.svg"
CSS_PATH = "assets/site.css"


def inline_markdown(value: str) -> str:
    escaped = html.escape(value, quote=False)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*(.+?)\*", r"<em>\1</em>", escaped)
    return escaped


def slug_for(path: Path) -> str:
    match = re.search(r"(20\d{2})(\d{2})(\d{2}).*?part\s*(\d+)", path.stem, re.I)
    if match:
        year, month, day, part = match.groups()
        return f"{year}-{month}-{day}-part-{int(part)}"
    slug = re.sub(r"[^\w\-]+", "-", path.stem.lower(), flags=re.UNICODE).strip("-")
    return slug or "conversation"


def article_date(path: Path) -> tuple[str, str]:
    match = re.search(r"(20\d{2})(\d{2})(\d{2})", path.stem)
    if not match:
        return "对谈", ""
    year, month, day = match.groups()
    try:
        parsed = date(int(year), int(month), int(day))
    except ValueError:
        return "对谈", ""
    return parsed.strftime("%Y.%m.%d"), parsed.isoformat()


def parse_markdown(path: Path) -> tuple[str, str, list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    title = next((line[2:].strip() for line in lines if line.startswith("# ")), path.stem)
    deck = ""
    body_start = 0
    for index, line in enumerate(lines):
        if line.startswith("# "):
            body_start = index + 1
            break
    body_lines = lines[body_start:]
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    if body_lines and body_lines[0].startswith("*") and body_lines[0].endswith("*"):
        deck = body_lines.pop(0).strip().strip("*").strip()

    paragraphs: list[str] = []
    current: list[str] = []
    for line in body_lines:
        if line.strip() == "---":
            continue
        if not line.strip():
            if current:
                paragraphs.append(" ".join(part.strip() for part in current))
                current = []
            continue
        current.append(line.strip())
    if current:
        paragraphs.append(" ".join(part.strip() for part in current))
    return title, deck, paragraphs


def render_turns(paragraphs: list[str]) -> str:
    turns: list[dict[str, object]] = []
    label_pattern = re.compile(r"^\*\*([AB])：\*\*\s*(.*)$", re.S)
    for paragraph in paragraphs:
        match = label_pattern.match(paragraph)
        if match:
            turns.append({"speaker": match.group(1), "paragraphs": [match.group(2)]})
        elif turns:
            turns[-1]["paragraphs"].append(paragraph)  # type: ignore[union-attr]
        else:
            turns.append({"speaker": "", "paragraphs": [paragraph]})

    output: list[str] = []
    for turn in turns:
        speaker = str(turn["speaker"])
        paragraphs_in_turn = turn["paragraphs"]
        speaker_class = f" speaker-{speaker.lower()}" if speaker else ""
        label = (
            f'<span class="speaker-label" aria-label="Speaker {speaker}">{speaker}</span>'
            if speaker
            else ""
        )
        body = "\n".join(
            f"<p>{inline_markdown(str(paragraph))}</p>" for paragraph in paragraphs_in_turn
        )
        output.append(
            f'<section class="turn{speaker_class}" data-speaker="{speaker}">'
            f"{label}<div class=\"turn-copy\">{body}</div></section>"
        )
    return "\n".join(output)


def document_head(title: str, description: str, base_path: str) -> str:
    safe_title = html.escape(title)
    safe_description = html.escape(description, quote=True)
    css_href = f"{base_path}{CSS_PATH}"
    favicon_href = f"{base_path}assets/branding/trash-talk-icon.svg"
    return f'''<!doctype html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f5f1e7">
  <meta name="description" content="{safe_description}">
  <title>{safe_title} · 乱丢垃圾 / Trash Talk</title>
  <link rel="icon" href="{favicon_href}" type="image/svg+xml">
  <link rel="stylesheet" href="{css_href}">
</head>'''


def render_article(path: Path, article_number: int) -> tuple[str, dict[str, str]]:
    title, deck, paragraphs = parse_markdown(path)
    slug = slug_for(path)
    date_label, iso_date = article_date(path)
    href = f"articles/{slug}.html"
    description = deck or title
    turns = render_turns(paragraphs)
    header = document_head(title, description, "../")
    page = f'''{header}
<body class="article-page">
  <a class="skip-link" href="#main">跳到正文</a>
  <main id="main" class="article-shell">
    <header class="article-intro">
      <p class="eyebrow"><time datetime="{iso_date}">{date_label}</time></p>
      <h1>{html.escape(title)}</h1>
      <p class="article-deck">{html.escape(deck)}</p>
      <div class="article-meta"><span>两个人的对谈</span><span class="meta-dot" aria-hidden="true"></span><span>按原对话顺序整理</span></div>
    </header>
    <div class="article-rule" aria-hidden="true"><span>{article_number:02d}</span><i></i><span>—</span></div>
    <article class="dialogue" aria-label="对谈正文">
      {turns}
    </article>
    <nav class="article-end" aria-label="文章导航">
      <a href="../index.html#archive"><span aria-hidden="true">←</span> 回到全部对谈</a>
      <a href="#main">回到顶部 <span aria-hidden="true">↑</span></a>
    </nav>
  </main>
  <footer class="site-footer article-footer"><span>乱丢垃圾 · TRASH TALK</span><span>把话说开，也把话留下。</span></footer>
</body>
</html>
'''
    return page, {
        "title": title,
        "deck": deck,
        "slug": slug,
        "href": href,
        "date": date_label,
        "iso_date": iso_date,
    }


def render_home(articles: list[dict[str, str]]) -> str:
    if articles:
        items = []
        for number, article in enumerate(articles, start=1):
            items.append(
                f'''<a class="archive-item" href="{html.escape(article['href'], quote=True)}">
  <span class="archive-number">{number:02d}</span>
  <span class="archive-copy"><span class="archive-meta">{html.escape(article['date'])} <i>·</i> 对谈</span>
    <span class="archive-title">{html.escape(article['title'])}</span>
    <span class="archive-deck">{html.escape(article['deck'])}</span></span>
  <span class="archive-arrow" aria-hidden="true">↗</span>
</a>'''
            )
        archive = "\n".join(items)
    else:
        archive = '<p class="empty-note">新的对谈正在路上。</p>'
    page = f'''{document_head("首页", "两个人，聊一个话题；不赶着下结论。", "")}
<body class="home-page">
  <a class="skip-link" href="#archive">跳到文章列表</a>
  <main id="main">
    <section class="hero" aria-labelledby="hero-title">
      <figure class="hero-mark">
        <img src="assets/branding/trash-talk-icon.svg" width="350" height="350" alt="乱丢垃圾 Trash Talk 黄色方形标志，黑色中文字与飞起的纸团">
      </figure>
      <div class="hero-copy">
        <p class="eyebrow">乱丢垃圾 · TRASH TALK</p>
        <h1 id="hero-title" class="visually-hidden">乱丢垃圾 · Trash Talk</h1>
        <p class="hero-deck">脑子里攒了些东西，<br>先一股脑倒出来。</p>
        <p class="hero-note">两个人，聊一个话题；不赶着下结论。闲聊，聊什么、聊成什么样，边聊边说。</p>
        <a class="read-link" href="#archive">往下读 <span aria-hidden="true">↓</span></a>
      </div>
    </section>
    <section id="archive" class="archive" aria-label="对谈列表">
      <p class="archive-count archive-summary">{len(articles):02d} <span>篇长谈</span></p>
      <div class="archive-list">{archive}</div>
    </section>
  </main>
  <footer class="site-footer home-footer"><span>乱丢垃圾 · TRASH TALK</span><span>把话说开，也把话留下。</span></footer>
</body>
</html>
'''
    return page


def main() -> None:
    sources = sorted(PUBLISH_ROOT.glob("*/*.publish-longform.md"))
    SITE_ROOT.mkdir(parents=True, exist_ok=True)
    article_dir = SITE_ROOT / "articles"
    article_dir.mkdir(parents=True, exist_ok=True)
    for old_page in article_dir.glob("*.html"):
        old_page.unlink()

    articles: list[dict[str, str]] = []
    for number, source in enumerate(sources, start=1):
        rendered, metadata = render_article(source, number)
        (article_dir / f"{metadata['slug']}.html").write_text(rendered, encoding="utf-8")
        articles.append(metadata)

    (SITE_ROOT / "index.html").write_text(render_home(articles), encoding="utf-8")
    LOGO_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LOGO_SOURCE, LOGO_OUTPUT)
    print(f"Built homepage and {len(articles)} article page(s) in {SITE_ROOT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
