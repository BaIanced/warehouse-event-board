#!/usr/bin/env python3
"""Pulls the sources a script can read and writes data/auto.json.

Runs inside the GitHub Actions workflow (no Claude, no connector, standard library only).
Each source is independent: if one site is down or changes its layout, that source keeps
its last good rows from data/auto.json and is reported as failed - the rest still update.

Run: python3 tools/scrape.py            (live fetch)
     python3 tools/scrape.py --dir DIR  (parse saved pages in DIR - used for testing)
"""
import datetime as dt, html, json, os, re, sys, time, urllib.request

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
AUTO = os.path.join(ROOT, "data", "auto.json")
WEATHER = os.path.join(ROOT, "data", "weather.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
try:
    from zoneinfo import ZoneInfo
    TODAY = dt.datetime.now(ZoneInfo("America/Boise")).date()   # the Action runs in UTC
except Exception:
    TODAY = dt.date.today()

ICA = "Idaho Central Arena (next door)"
EMA = "ExtraMile Arena (campus)"
ALB = "Albertsons Stadium (campus)"
MON = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

SOURCES = {   # key: (label shown on the board, url, saved-page name for --dir)
    "ica":      ("Idaho Central Arena",      "https://idahocentralarena.com/events/", "ica.html"),
    "fb":       ("Bronco football",          "https://broncosports.com/sports/football/schedule", "fb.html"),
    "mbb":      ("Bronco men's basketball",  "https://broncosports.com/sports/mens-basketball/schedule", "mbb.html"),
    "wbb":      ("Bronco women's basketball","https://broncosports.com/sports/womens-basketball/schedule", "wbb.html"),
    "boisecentre": ("Boise Centre",          "https://www.boisecentre.com/attend/events/", "bc.html"),
    "tmh":      ("Treefort Music Hall",      "https://treefortmusichall.com/shows/", "tmh.html"),
    "knit":     ("Knitting Factory",         "https://bo.knittingfactory.com/", "kf.html"),
    "weather":  ("Weather forecast",         "https://api.weather.gov/gridpoints/BOI/133,86/forecast", "fc.json"),
}
# Fewer rows than this means the page layout probably changed -> treat as a failure, keep old rows.
MIN_ROWS = {"ica": 1, "fb": 0, "mbb": 0, "wbb": 0, "boisecentre": 0, "tmh": 1, "knit": 1, "weather": 5}


def fetch(url, saved=None, tries=3):
    if saved:
        with open(saved, encoding="utf-8", errors="replace") as f:
            return f.read()
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:                     # retry, then give up on this source only
            err = e
            time.sleep(4 * (i + 1))
    raise RuntimeError(f"{type(err).__name__}: {err}")


def text(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>|<[^>]+>", " ", s, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def clock(raw):
    """'7:10pm' / '7 PM' / '5PM' / '12:30 p.m.' -> '7:10 PM'. Returns None if it isn't a time."""
    m = re.search(r"(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\.?", raw or "", re.I)
    if not m or not 1 <= int(m.group(1)) <= 12:
        return None
    return f"{int(m.group(1))}:{m.group(2) or '00'} {m.group(3).upper()}M"


def long_date(raw):
    """'November 18, 2026' -> date."""
    m = re.search(r"([A-Za-z]{3})[a-z]*\.? (\d{1,2}), (\d{4})", raw or "")
    if not m or m.group(1).lower() not in MON:
        return None
    return dt.date(int(m.group(3)), MON[m.group(1).lower()], int(m.group(2)))


def near_year(month, day):
    """Sites that print 'Nov 20' with no year: pick the occurrence closest to today, looking ahead."""
    for y in (TODAY.year, TODAY.year + 1):
        try:
            d = dt.date(y, month, day)
        except ValueError:
            continue
        if d >= TODAY - dt.timedelta(days=45):
            return d
    return None


def row(cat, title, start, time_=None, end=None, venue="", impact="med", src="", note=None, doors=None):
    r = dict(cat=cat, title=title, start=start.isoformat(), end=(end or start).isoformat(),
             time=time_ or "TBA", venue=venue, impact=impact, src=src)
    if note:
        r["note"] = note
    if doors:
        r["doors"] = doors
    return r


# ---------------------------------------------------------------- Idaho Central Arena
def src_ica(page, url):
    out, seen = [], set()
    for it in re.split(r'(?=<div data-elementor-type="loop-item")', page)[1:]:
        h = re.search(r"<h4[^>]*>(.*?)</h4>", it, re.S)
        info = [text(x) for x in re.findall(r"elementor-post-info__item[^>]*>(.*?)</span>", it, re.S)]
        d = next((long_date(x) for x in info if long_date(x)), None)
        if not h or not d:
            continue
        title = text(h.group(1))
        link = re.search(r'href="(https://idahocentralarena\.com/events/[^"]+)"', it)
        doors = next((clock(x) for x in info if x.lower().startswith("doors")), None)
        start = next((clock(x) for x in info if x.lower().startswith("start")), None)
        if (title, d) in seen:                     # the page prints the list twice (desktop + mobile)
            continue
        seen.add((title, d))
        if "steelheads-hockey" in it[:1200] or title.lower().startswith("idaho steelheads"):
            cat, title = "hockey", re.sub(r"^Idaho Steelheads vs\.?", "Steelheads vs", title)
        else:
            cat = "music"
        out.append(row(cat, title, d, start, venue=ICA, impact="high",
                       src=link.group(1) if link else url, doors=doors))
    return out


# ---------------------------------------------------------------- Boise State (broncosports.com)
def nuxt(page):
    """The schedule pages embed their data as a flat JSON array where values point at other slots."""
    m = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', page, re.S)
    if not m:
        raise ValueError("schedule data block not found")
    return json.loads(m.group(1))


def bronco(page, url, cat):
    arr = nuxt(page)

    def val(i, depth=0):                           # resolve one slot (shallow - enough for a game row)
        v = arr[i] if isinstance(i, int) and 0 <= i < len(arr) else None
        if isinstance(v, dict) and depth < 2:
            return {k: val(x, depth + 1) for k, x in v.items()}
        return v
    label = {"football": "Broncos football", "mbb": "Broncos men's hoops", "wbb": "Broncos women's hoops"}[cat]
    out, seen = [], set()
    for v in arr:
        if not (isinstance(v, dict) and {"date", "opponent", "location", "at_vs"} <= set(v)):
            continue
        g = val(arr.index(v))
        date_s, loc = g.get("date"), g.get("location") or ""
        if not isinstance(date_s, str) or not re.match(r"\d{4}-\d{2}-\d{2}", date_s):
            continue
        if "boise" not in str(loc).lower():        # HOME / in-town games only
            continue
        d = dt.date.fromisoformat(date_s[:10])
        opp = (g.get("opponent") or {}).get("title") if isinstance(g.get("opponent"), dict) else None
        fac = (g.get("facility") or {}).get("title") if isinstance(g.get("facility"), dict) else ""
        if not opp or (d, opp) in seen:
            continue
        seen.add((d, opp))
        blob = f"{fac} {loc}".lower()
        if "idaho central" in blob:
            venue = ICA
        elif cat == "football":
            venue = ALB
        else:
            venue = EMA
        impact = "high" if cat == "football" or venue == ICA else "low"
        tm = None if g.get("tbd") is True else clock(str(g.get("time") or ""))
        exh = " (exhibition)" if "exhibition" in opp.lower() else ""
        opp = re.sub(r"\s*\(exhibition\)", "", opp, flags=re.I)
        out.append(row(cat, f"{label} vs {opp}{exh}", d, tm, venue=venue, impact=impact, src=url))
    return out


# ---------------------------------------------------------------- Boise Centre
def src_boisecentre(page, url):
    out = []
    for card in re.findall(r'<article class="event-card([^"]*)">(.*?)</article>', page, re.S):
        kind, body = card[0].strip(), card[1]
        h = re.search(r"<h3[^>]*>(.*?)</h3>", body, re.S)
        days = re.findall(r'class="month">\s*([A-Za-z]{3})[a-z]*\s*</span>\s*<span class="day">\s*(\d{1,2})', body)
        if not h or not days or days[0][0].lower() not in MON:
            continue
        start = near_year(MON[days[0][0].lower()], int(days[0][1]))
        if not start:
            continue
        end = start
        if len(days) > 1 and days[-1][0].lower() in MON:
            m2, d2 = MON[days[-1][0].lower()], int(days[-1][1])
            end = dt.date(start.year + (1 if m2 < start.month else 0), m2, d2)
        link = re.search(r'class="button" href="([^"]+)"', body)
        catline = re.search(r"Category:\s*([^<]+)", body)
        note = f"Boise Centre lists this as: {text(catline.group(1))}" if catline else None
        out.append(row("convention", text(h.group(1)), start, "All day", end=end,
                       venue="Boise Centre (across the street)", impact="med",
                       src=link.group(1) if link else url, note=note))
    return out


# ---------------------------------------------------------------- Nearby club shows (hidden by default)
def src_tmh(page, url):
    out = []
    for blk in page.split("mh-show-wrapper")[1:]:
        d = re.search(r"id='dat'>(\d{1,2})/(\d{1,2})/(\d{4})<", blk)
        name = re.search(r"class='mh-h1'>(.*?)</div>", blk, re.S)
        if not d or not name:
            continue
        doors = re.search(r"id='doo'>([^<]*)<", blk)
        link = re.search(r"data-link='([^']+)'", blk)
        cats = re.search(r"categories:\s*([^<]*)<", blk)
        room = text(cats.group(1)) if cats else "Treefort Music Hall"
        if "treefort music hall" not in room.lower():   # the same feed lists other venues; keep the hall only
            continue
        t = clock(doors.group(1)) if doors else None
        out.append(row("shows", text(name.group(1)), dt.date(int(d.group(3)), int(d.group(1)), int(d.group(2))),
                       t, venue="Treefort Music Hall (722 W Broad St)", impact="low",
                       src="https://treefortmusichall.com" + link.group(1) if link else url,
                       note="Time shown is doors" if t else None))
    return out


def src_knit(page, url):
    out = []
    for blk in page.split('class="tw-section"')[1:]:
        name = re.search(r'class="tw-name[^"]*"[^>]*>(.*?)</div>', blk, re.S)
        dm = re.search(r'class="tw-event-date[^"]*"[^>]*>\s*([A-Za-z]{3})[a-z]*\.? (\d{1,2})', blk)
        if not name or not dm or dm.group(1).lower() not in MON:
            continue
        d = near_year(MON[dm.group(1).lower()], int(dm.group(2)))
        if not d:
            continue
        tm = re.search(r"Show:\s*([0-9: ]+[ap]\.?m\.?)", text(blk), re.I)
        link = re.search(r'href="(https://bo\.knittingfactory\.com/tm-event/[^"]+)"', blk)
        out.append(row("shows", text(name.group(1)), d, clock(tm.group(1)) if tm else None,
                       venue="Knitting Factory (416 S 9th St)", impact="low",
                       src=link.group(1) if link else url))
    return out


# ---------------------------------------------------------------- Weather (National Weather Service)
def src_weather(page, url):
    days = {}
    for p in json.loads(page)["properties"]["periods"]:
        d = days.setdefault(p["startTime"][:10], {"date": p["startTime"][:10]})
        pop = (p.get("probabilityOfPrecipitation") or {}).get("value") or 0
        d["pop"] = max(d.get("pop", 0), pop)
        if p.get("isDaytime"):
            d["hi"], d["text"] = p["temperature"], p["shortForecast"]
        else:
            d["lo"] = p["temperature"]
            d.setdefault("text", p["shortForecast"])
    return [days[k] for k in sorted(days)]


PARSERS = {
    "ica": src_ica, "boisecentre": src_boisecentre, "tmh": src_tmh, "knit": src_knit, "weather": src_weather,
    "fb": lambda p, u: bronco(p, u, "football"),
    "mbb": lambda p, u: bronco(p, u, "mbb"),
    "wbb": lambda p, u: bronco(p, u, "wbb"),
}


def main():
    saved_dir = sys.argv[sys.argv.index("--dir") + 1] if "--dir" in sys.argv else None
    try:
        with open(AUTO) as f:
            prev = json.load(f)
    except (OSError, ValueError):
        prev = {}
    out = {"checked": TODAY.isoformat(), "sources": {}, "events": {}, "weather": []}
    failed = []
    for key, (label, url, fname) in SOURCES.items():
        old = (prev.get("sources") or {}).get(key, {})
        st = {"label": label, "url": url, "ok": True, "last_ok": TODAY.isoformat()}
        try:
            rows = PARSERS[key](fetch(url, os.path.join(saved_dir, fname) if saved_dir else None), url)
            if len(rows) < MIN_ROWS[key]:
                raise ValueError(f"only {len(rows)} rows parsed - page layout may have changed")
            if key != "weather":                    # drop anything already over
                rows = [r for r in rows if r["end"] >= TODAY.isoformat()]
                rows.sort(key=lambda r: (r["start"], r["title"]))
        except Exception as e:
            st.update(ok=False, last_ok=old.get("last_ok"), error=str(e)[:200])
            rows = [] if key == "weather" else (prev.get("events") or {}).get(key, [])
            failed.append(key)
        st["count"] = len(rows)
        out["sources"][key] = st
        if key == "weather":
            out["weather"] = rows
        else:
            out["events"][key] = rows
        print(f"{'ok  ' if st['ok'] else 'FAIL'} {key:12} {len(rows):3} rows" + (f"  <- {st.get('error')}" if not st["ok"] else ""))
    os.makedirs(os.path.dirname(AUTO), exist_ok=True)
    # Weather changes every day, so it lives in its own file that is never committed.
    with open(WEATHER, "w") as f:
        json.dump(out.pop("weather"), f, indent=1)
    # data/auto.json IS committed (it is the "last good copy" each source falls back to). To keep the
    # history readable it is only rewritten when something real changed, plus every Monday - the
    # Monday commit also keeps GitHub from switching off the schedule (it does that after 60 quiet days).
    ok_map = lambda d: {k: v.get("ok") for k, v in (d.get("sources") or {}).items()}
    same = prev.get("events") == out["events"] and ok_map(prev) == ok_map(out)
    if same and TODAY.weekday() != 0:
        print("no event changes - data/auto.json left as is")
    else:
        with open(AUTO, "w") as f:
            json.dump(out, f, indent=1)
        print(f"wrote {os.path.relpath(AUTO, ROOT)}")
    print(f"failed sources: {', '.join(failed) or 'none'}")
    # Exit code 2 = a source has been failing for more than 3 days -> the workflow marks the run failed
    # (after it has already published the site) so GitHub flags it.
    old = [k for k in failed if not out["sources"][k].get("last_ok")
           or (TODAY - dt.date.fromisoformat(out["sources"][k]["last_ok"])).days > 3]
    if old and "--strict" in sys.argv:
        print("STILL FAILING after 3+ days: " + ", ".join(old))
        sys.exit(2)


if __name__ == "__main__":
    main()
