#!/usr/bin/env python3
"""Update a scheme's interest rate everywhere it appears on its calculator page.

Small-savings rates (PPF, SSY) are notified quarterly. Each rate is written into
roughly 17 places per page - body copy, hero pill, meta description, og/twitter
tags, the JSON-LD WebApplication description, the FAQ answer inside the schema
string, the visible FAQ, the input default and the JS constant. Updating those by
hand is how schema ends up contradicting body copy.

    python3 scripts/set_rates.py --show              # current rates
    python3 scripts/set_rates.py --ppf 7.0 --ssy 8.0 # apply
    python3 scripts/set_rates.py --ppf 7.0 --dry-run

Cross-page mentions are handled too: ssy-calculator.html compares itself with
PPF's rate, so changing --ppf also corrects that sentence.
"""
import re, sys, os, argparse
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# scheme -> (page it owns, every page that states the rate)
SCHEMES = {
    "ppf": {"page": "ppf.html", "also": ["ssy-calculator.html", "epf-calculators.html"], "label": "PPF"},
    "ssy": {"page": "ssy-calculator.html", "also": [], "label": "SSY"},
    # EPFO declares annually, not with the quarterly small-savings cycle,
    # but it has the same scattered-literal problem.
    "epf": {"page": "epf-calculators.html", "also": [], "label": "EPF"},
}


def current(scheme):
    """Read the rate from the page's own input default - the single source of truth."""
    path = os.path.join(ROOT, SCHEMES[scheme]["page"])
    s = open(path, encoding="utf-8").read()
    ids = {"ppf": "interestRate", "ssy": "ssyRate", "epf": "epfRate"}
    m = re.search(r'id="%s"[^>]*value="([\d.]+)"' % ids[scheme], s)
    if not m:
        m = re.search(r'value="([\d.]+)"[^>]*id="%s"' % ids[scheme], s)
    return m.group(1) if m else None


def bump(text, old, new):
    """Replace the rate only where it stands alone as a number."""
    rx = re.compile(r"(?<![\d.])" + re.escape(old) + r"(?![\d.])")
    return rx.subn(new, text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ppf")
    ap.add_argument("--ssy")
    ap.add_argument("--epf")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verified", default=date.today().strftime("%-d %B %Y"),
                    help='date for the "rate verified" line (default: today)')
    a = ap.parse_args()

    if a.show or not (a.ppf or a.ssy or a.epf):
        for k in SCHEMES:
            print(f"  {SCHEMES[k]['label']:4s} {current(k)}%")
        return 0

    total = 0
    for scheme in ("ppf", "ssy", "epf"):
        new = getattr(a, scheme)
        if not new:
            continue
        old = current(scheme)
        if old is None:
            print(f"could not read the current {scheme} rate", file=sys.stderr)
            return 2
        if old == new:
            print(f"{SCHEMES[scheme]['label']}: already {new}%")
            continue
        for page in [SCHEMES[scheme]["page"]] + SCHEMES[scheme]["also"]:
            path = os.path.join(ROOT, page)
            s = open(path, encoding="utf-8").read()
            out, n = bump(s, old, new)
            # refresh the verified-as-of line on the scheme's own page
            if page == SCHEMES[scheme]["page"]:
                out = re.sub(r"(rate verified [\d.]+% p\.a\. as of )[^<]*?(\.</strong>)",
                             lambda m: m.group(1) + a.verified + m.group(2), out)
            if n and not a.dry_run:
                open(path, "w", encoding="utf-8").write(out)
            if n:
                print(f"  {SCHEMES[scheme]['label']}: {old}% -> {new}%  ({n} places in {page})")
                total += n
    if a.dry_run:
        print(f"\ndry run - {total} replacements not written")
    elif total:
        print(f"\n{total} replacements written. Re-run --show to confirm.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
