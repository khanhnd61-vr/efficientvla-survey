#!/usr/bin/env python3
"""Build index.html for the Efficient VLA Atlas.

Reads ../awesome-efficient-vla/README.md (survey taxonomy, 211 papers) and
extras.json (papers added by hand), writes papers.json and index.html.
Run:  python3 build.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
README = HERE.parent / "awesome-efficient-vla" / "README.md"
TEMPLATE = HERE / "index.template.html"
EXTRAS = HERE / "extras.json"
ANALYSIS = HERE / "analysis.json"
OUT_JSON = HERE / "papers.json"
OUT_HTML = HERE / "index.html"

AREA_RE = re.compile(r"^## (\d)\. (.+?)\s*$")
CAT_RE = re.compile(r"^### (\d\.\d) (.+?)\s*$")
ENTRY_RE = re.compile(
    r"^- \[\*\*(?P<title>.+?)\*\*\]\((?P<url>[^)]+)\)\s*·\s*`(?P<date>\d{4}-\d{2})`\s*·\s*(?P<rest>.*)$"
)
SUB_RE = re.compile(r"<sub>(.*?)</sub>\s*$")
LINK_RE = re.compile(r"\[(Code|Project)\]\(([^)]+)\)")
VENUE_RE = re.compile(r"Venue:\s*([^·<]+)")
SEC_RE = re.compile(r"Sec\.\s*([\d.; ]+)")


def clean(s: str) -> str:
    s = s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return re.sub(r"\s+", " ", s).strip()


def parse_readme(path: Path):
    areas, cats, papers = {}, {}, []
    area_id = cat_id = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = AREA_RE.match(line)
        if m:
            area_id = m.group(1)
            areas[area_id] = clean(m.group(2))
            continue
        m = CAT_RE.match(line)
        if m:
            cat_id = m.group(1)
            cats[cat_id] = {"id": cat_id, "name": clean(m.group(2)), "area": cat_id[0]}
            continue
        m = ENTRY_RE.match(line)
        if not m or cat_id is None:
            continue
        rest = m.group("rest")
        sub = SUB_RE.search(rest)
        blurb = SUB_RE.sub("", rest).strip()
        code = project = venue = None
        secondary = []
        if sub:
            s = sub.group(1)
            for kind, url in LINK_RE.findall(s):
                if kind == "Code":
                    code = url
                else:
                    project = url
            v = VENUE_RE.search(s)
            if v:
                venue = clean(v.group(1))
            sec = SEC_RE.search(s)
            if sec:
                secondary = [x.strip() for x in sec.group(1).split(";") if x.strip()]
        papers.append(
            {
                "title": clean(m.group("title")),
                "url": m.group("url").strip(),
                "date": m.group("date"),
                "blurb": clean(blurb),
                "code": code,
                "project": project,
                "venue": venue,
                "category": cat_id,
                "secondary": secondary,
                "source": "survey",
            }
        )
    return areas, cats, papers


def main():
    areas, cats, papers = parse_readme(README)
    survey_count = len(papers)

    extras = json.loads(EXTRAS.read_text(encoding="utf-8"))
    for a in extras.get("areas", []):
        areas.setdefault(a["id"], a["name"])
    for c in extras.get("categories", []):
        cats.setdefault(c["id"], {"id": c["id"], "name": c["name"], "area": c["id"][0]})
    for p in extras.get("papers", []):
        p.setdefault("code", None)
        p.setdefault("project", None)
        p.setdefault("venue", None)
        p.setdefault("secondary", [])
        p.setdefault("note", None)
        p["source"] = "added"
        if p["category"] not in cats:
            sys.exit(f"extras.json: unknown category {p['category']} for {p['title']}")
        papers.append(p)

    papers.sort(key=lambda p: (p["date"], p["title"]), reverse=True)

    # Analysis: problem / gaps / direction per area and category; key papers resolved by title fragment.
    analysis = json.loads(ANALYSIS.read_text(encoding="utf-8"))
    for cid, a in analysis["categories"].items():
        if cid not in cats:
            sys.exit(f"analysis.json: unknown category {cid}")
        keys = []
        for frag in a.pop("key", []):
            hits = [i for i, p in enumerate(papers) if frag.lower() in p["title"].lower()]
            if not hits:
                print(f"warning: analysis.json key '{frag}' matched no paper", file=sys.stderr)
                continue
            keys.append(hits[0])
        a["key"] = keys
        cats[cid]["analysis"] = a
    area_analysis = analysis["areas"]
    for aid in area_analysis:
        if aid not in areas:
            sys.exit(f"analysis.json: unknown area {aid}")
    data = {
        "areas": [{"id": k, "name": v, "analysis": area_analysis.get(k)} for k, v in sorted(areas.items())],
        "categories": sorted(cats.values(), key=lambda c: c["id"]),
        "papers": papers,
        "counts": {"survey": survey_count, "added": len(papers) - survey_count},
    }
    OUT_JSON.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

    tpl = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = tpl.replace("/*__DATA__*/", payload)
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"{survey_count} survey papers + {data['counts']['added']} added "
          f"across {len(cats)} categories -> {OUT_HTML.name}, {OUT_JSON.name}")


if __name__ == "__main__":
    main()
