# Efficient VLA Atlas

A static GitHub Pages site that taxonomizes efficient vision-language-action research:
the 211 papers from [Awesome-Efficient-VLA](https://github.com/guanweifan/awesome-efficient-vla)
(13 survey categories) plus benchmark, robustness, delay-aware and compact-policy papers
added after the survey's August 2026 cutoff, with reading notes on what is settled and what is open.

## Files

- `build.py` parses `../awesome-efficient-vla/README.md` and `extras.json`, then writes `papers.json` and `index.html`.
- `index.template.html` is the page; `build.py` inlines the data so the page works offline and on GitHub Pages.
- The taxonomy map in the page is an inline SVG drawn by the page script from the same data: five columns follow the VLA pipeline (design, train, run, ship, measure), circle area tracks each category's primary-paper count, and links come from the survey's secondary section tags. Clicking a circle filters the paper list.
- `extras.json` holds hand-added papers and the extra area 7 (Evaluation and Robustness).
- `analysis.json` holds, for every area and category, the problem it addresses, the open gaps, and one proposed research direction (bit, flip, first experiments, claim, cost in GPU-days, fit, risk) plus key-paper title fragments that `build.py` resolves against the paper list. The page renders it as the "Analysis" section: area tabs, a direction board with type filters and sorting, expandable category cards, and a per-browser shortlist that can be copied as Markdown. The Analysis section; deep link to a card with `#gap-5.1` or `#gap-A5`.

## Update

```bash
cd awesome-efficient-vla && git pull && cd ..
python3 site/build.py
```

## Publish to GitHub Pages

The site is deployed from the `main` branch root of
[khanhnd61-vr/efficientvla-survey](https://github.com/khanhnd61-vr/efficientvla-survey)
and served at <https://khanhnd61-vr.github.io/efficientvla-survey/>
(also <https://havi.fit/efficientvla-survey/> through the account's custom domain).
After rebuilding, commit `index.html` and `papers.json` together with the source files and push:

```bash
python3 build.py
git add -A && git commit -m "Update atlas" && git push
```

GitHub Pages rebuilds within about a minute.
