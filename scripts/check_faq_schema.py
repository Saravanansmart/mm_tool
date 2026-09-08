#!/usr/bin/env python3
"""Regression check: every page's FAQPage schema must exactly match its
visible <details>/<summary> FAQ accordion, and JSON-LD must parse.

This exact bug (schema silently drifting from visible content) was found
and fixed site-wide once already — see PR #29. Run this before every
deploy, or on a schedule, so it can't happen again unnoticed.

Usage: python3 scripts/check_faq_schema.py
Exit code 0 = clean, 1 = problems found (also printed to stdout).
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def body_faqs(page_html):
    qs = re.findall(r"<summary>(.*?)</summary>", page_html, re.S)
    return {html.unescape(re.sub(r"<[^>]+>", "", q)).strip() for q in qs}


def schema_faqs(page_html):
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page_html, re.S):
        data = json.loads(m)  # let this raise — invalid JSON-LD is itself a failure
        if data.get("@type") == "FAQPage":
            return {q["name"] for q in data["mainEntity"]}
    return None


def main():
    problems = []
    pages = sorted(glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(os.path.join(ROOT, "blog", "*.html")))

    for path in pages:
        rel = os.path.relpath(path, ROOT)
        src = open(path, encoding="utf-8").read()
        if "noindex" in src:
            continue

        try:
            schema = schema_faqs(src)
        except json.JSONDecodeError as e:
            problems.append(f"{rel}: invalid JSON-LD ({e})")
            continue

        body = body_faqs(src)
        if not body and schema is None:
            continue  # page legitimately has no FAQ section (e.g. index pages)
        if body and schema is None:
            problems.append(f"{rel}: has {len(body)} visible FAQ(s) but no FAQPage schema")
            continue
        if schema is not None and not body:
            problems.append(f"{rel}: has FAQPage schema ({len(schema)} entries) but no visible FAQ accordion")
            continue
        if body != schema:
            only_body = body - schema
            only_schema = schema - body
            detail = []
            if only_body:
                detail.append(f"visible-only: {sorted(only_body)}")
            if only_schema:
                detail.append(f"schema-only: {sorted(only_schema)}")
            problems.append(f"{rel}: FAQ schema does not match visible content — {'; '.join(detail)}")

    if problems:
        print(f"FAQ schema/content check: {len(problems)} problem(s) found\n")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"FAQ schema/content check: clean across {len(pages)} pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
