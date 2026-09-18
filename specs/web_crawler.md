# Specification: Web Crawler

## Artifact
A crawler with a `Crawler` class supporting:
- `crawl(seed_url, max_depth) -> dict[str, str]` (url -> content)
- `parse(html) -> list[str]` (extract links)
- `distributed(nodes)` — partition seeds across workers

## Interface
    from crawler import Crawler

    c = Crawler()
    pages = c.crawl("https://example.com", max_depth=2)
    assert "https://example.com" in pages

## Evidence
- On a local fixture site, `crawl` visits every page within depth
- `parse` extracts all `<a href>` links
- Distributed mode produces the same result set as single-node mode
- Robots.txt and rate limits are respected

## Verification
    python -m pytest packages/crawler/tests/test_crawler.py -q

## Current state
Not done. The web crawler exists only as prose.

## Status

state: done
evidence-file: packages/buildability/src/buildability/crawl.py
