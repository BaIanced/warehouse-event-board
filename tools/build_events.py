#!/usr/bin/env python3
"""Builds events.json for the Warehouse staffing tracker.
Every row traces to a source URL. Times are local Boise time (MT).
Run: python3 tools/build_events.py  (writes ../events.json)
"""
import json, os, datetime as dt

SRC = {
    "steel_home": "https://echl.s3.us-east-2.amazonaws.com/production/idh/uploads/files/2026-27%20Schedules/2026-27%20Idaho%20Steelheads%20Home%20Schedule.pdf",
    "ica": "https://idahocentralarena.com/events/",
    "fb": "https://broncosports.com/news/2026/5/27/football-boise-state-pac-12-announce-2026-conference-tv-selections-and-kickoff-times",
    "mbb": "https://broncosports.com/sports/mens-basketball/schedule",
    "wbb": "https://broncosports.com/sports/womens-basketball/schedule",
    "treefort": "https://treefortmusicfest.com/treefort-music-fest-2027-the-countdown-begins/",
    "bigsky": "https://www.idahonews.com/news/local/big-sky-basketball-tournaments-to-stay-in-boise-through-2031",
    "firstthu": "https://www.downtownboise.org/events/first-thursday",
    "rcon": "https://lidarnews.com/event/r-con-boise-2026/",
    "artsnw": "https://artsnw.org/conference_overview",
    "isba": "https://www.idsba.org/convention/",
    "fot": "https://www.saintalphonsus.org/foundation/events/festival-of-trees/admission-and-attractions",
    "warehouse": "https://www.warehouseboise.com/",   # Warehouse one-offs (also /entertainment, FB/IG)
    "taste": "https://downtownboise.org/events/taste",
    "mining": "https://www.sharedaudiences.com/events/idaho-mining-conference-2026",
    "market": "https://www.idahonews.com/news/idaho-photo-galleries/capital-city-public-market-opens-2026-season",
    "treelight": "https://downtownboise.org/events/downtown-holiday-tree-lighting",
    "shopsmall": "https://downtownboise.org/events/our-downtown-events/shop-small",
    "potatobowl": "https://www.famousidahopotatobowl.com/",
    "bsucal": "https://www.boisestate.edu/registrar/boise-state-academic-calendars/2026-2027-academic-calendar-at-a-glance/",
}

# HOW THIS FILE FITS TOGETHER (since 2026-11-16)
#   tools/scrape.py  reads the sites a script can read (arena, Bronco schedules, Boise Centre,
#                    two nearby clubs, weather) every morning in GitHub Actions -> data/auto.json
#   this file        holds the HAND-CHECKED rows below (conventions found on organizer pages,
#                    festivals, Warehouse one-offs), merges in data/auto.json, and writes events.json
# Hand-checked rows win on wording; the scraped rows fill in times, doors, and anything new.
#
# Sources a script can't read - re-check these by hand about once a month. Only add an event once
# a page shows a confirmed date. Never guess a date.
#   OWNER SAYS the Downtown Holiday Tree Lighting is HUGE -> keep it at impact "max" each year.
#   Not confirmed as of 2026-11-16: Idaho Potato Drop (New Year's Eve) - idahopotatodrop.com showed no date.
WATCH = [
    "https://www.warehouseboise.com/  (+ /entertainment, FB/IG) - Warehouse one-offs",
    "https://downtownboise.org/events/events-calendar - DBA calendar",
    "https://downtownboise.org/events/downtown-holiday-tree-lighting",
    "https://downtownboise.org/events/shop-small",
    "https://www.visitboise.com/events/ - Visit Boise calendar (use month filter)",
    "https://boisedev.com , https://www.idahopress.com/boiseweekly - local news",
    "Organizer pages + web search for Boise Centre conventions",
    "Employee tips (e.g. Facebook groups): confirm on an official page before adding",
    "https://idahopotatodrop.com/ - New Year's Eve at the Capitol; add once this year's page is up",
    "https://egyptiantheatre.net/events/ , https://www.morrisoncenter.com/events - theatre shows",
    "Summer: Alive After Five (Grove Plaza), Boise Pride, Art in the Park, Twilight Criterium, Boise Farmers Market",
    "Idaho Legislature session dates (Capitol is downtown): https://legislature.idaho.gov/",
]

ICA = "Idaho Central Arena (next door)"
EMA = "ExtraMile Arena (campus)"
ALB = "Albertsons Stadium (campus)"

events = []
def add(cat, title, start, time=None, end=None, venue="", impact="med", src="", note=""):
    events.append({k: v for k, v in dict(
        cat=cat, title=title, start=start, end=end or start, time=time,
        venue=venue, impact=impact, src=SRC[src], note=note or None).items() if v is not None})

# --- Steelheads hockey (home only) ---
add("hockey", "Steelheads vs Tahoe (preseason)", "2026-10-11", "4:10 PM", venue=ICA, impact="high", src="ica")
steel = [
 ("2026-10-23","Allen Americans"),("2026-10-24","Allen Americans"),
 ("2026-11-04","Rapid City Rush"),("2026-11-06","Rapid City Rush"),("2026-11-07","Rapid City Rush"),
 ("2026-11-18","Maine Mariners"),("2026-11-20","Maine Mariners"),("2026-11-21","Maine Mariners"),
 ("2026-12-02","Rapid City Rush"),("2026-12-04","Rapid City Rush"),("2026-12-05","Rapid City Rush"),
 ("2026-12-09","Tulsa Oilers"),("2026-12-11","Tulsa Oilers"),("2026-12-12","Tulsa Oilers"),
 ("2026-12-30","New Mexico Goatheads"),("2027-01-01","New Mexico Goatheads"),("2027-01-02","New Mexico Goatheads"),
 ("2027-01-20","Wichita Thunder"),("2027-01-22","Wichita Thunder"),("2027-01-23","Wichita Thunder"),
 ("2027-02-03","New Mexico Goatheads"),("2027-02-05","New Mexico Goatheads"),("2027-02-06","New Mexico Goatheads"),
 ("2027-02-26","Allen Americans"),("2027-02-27","Allen Americans"),
 ("2027-03-12","Tulsa Oilers"),("2027-03-13","Tulsa Oilers"),
 ("2027-03-17","Tahoe Knight Monsters"),("2027-03-19","Tahoe Knight Monsters"),("2027-03-20","Tahoe Knight Monsters"),
 ("2027-03-31","Kalamazoo Wings"),("2027-04-02","Kalamazoo Wings"),("2027-04-03","Kalamazoo Wings"),
 ("2027-04-07","Kansas City Mavericks"),("2027-04-09","Kansas City Mavericks"),("2027-04-10","Kansas City Mavericks"),
]
for d, opp in steel:
    add("hockey", f"Steelheads vs {opp}", d, "7:10 PM", venue=ICA, impact="high", src="steel_home")
add("hockey", "ECHL All-Star Classic", "2027-01-26", "TBD", end="2027-01-27", venue=ICA, impact="high",
    src="steel_home", note="League all-star event hosted in Boise; times TBD")

# --- Boise State football (home only, remaining) ---
for d, opp, t in [("2026-10-31","Texas State","8:00 PM"),("2026-11-14","Oregon State","4:00 PM"),
                  ("2026-11-21","San Diego State","7:30 PM")]:
    add("football", f"Broncos football vs {opp}", d, t, venue=ALB, impact="high", src="fb")
add("football", "Famous Idaho Potato Bowl", "2026-12-21", "12:30 PM", venue=ALB, impact="med", src="potatobowl",
    note="College bowl game (teams announced in early December). Monday lunchtime kickoff")

# --- Boise State men's basketball (home only) ---
add("mbb", "Broncos men's hoops vs Idaho (exhibition)", "2026-10-10", "5:00 PM", venue=ICA, impact="high", src="mbb")
add("mbb", "Broncos men's hoops vs Washington (exhibition)", "2026-10-17", "7:00 PM", venue=ICA, impact="high", src="mbb")
add("mbb", "Broncos men's hoops vs Bismarck State (exhibition)", "2026-10-29", "TBA", venue=EMA, impact="low", src="mbb")
for d, opp in [("2026-11-04","West Coast Baptist"),("2026-11-08","Butler"),("2026-11-11","Oakland"),
               ("2026-11-20","Sam Houston"),("2026-11-24","Idaho State"),("2026-12-12","Texas A&M-Corpus Christi"),
               ("2026-12-16","Utah Valley"),("2026-12-29","Lamar"),("2027-01-09","Oregon State"),
               ("2027-01-13","Washington State"),("2027-01-23","San Diego State"),("2027-01-27","Utah State"),
               ("2027-02-10","Gonzaga"),("2027-02-13","Fresno State"),("2027-02-20","Texas State"),
               ("2027-03-03","Colorado State")]:
    add("mbb", f"Broncos men's hoops vs {opp}", d, "TBA", venue=EMA, impact="low", src="mbb")

# --- Boise State women's basketball (home only) ---
for d, opp, t in [("2026-11-02","Bushnell","11:00 AM"),("2026-11-06","Portland State","6:30 PM"),
                  ("2026-11-10","CSUN","6:30 PM"),("2026-11-13","Utah","6:30 PM"),("2026-11-15","Utah Tech","1:00 PM"),
                  ("2026-11-22","UC Davis","2:00 PM"),("2026-12-11","Sacramento State","6:30 PM"),
                  ("2026-12-13","Santa Clara","2:00 PM"),("2026-12-20","UC Riverside","2:00 PM"),
                  ("2026-12-22","Saint Mary's","2:00 PM"),("2026-12-31","South Dakota","2:00 PM"),
                  ("2027-01-14","Washington State","TBA"),("2027-01-16","Gonzaga","TBA"),
                  ("2027-01-24","Colorado State","TBA"),("2027-02-06","Texas State","TBA"),
                  ("2027-02-11","Utah State","TBA"),("2027-02-14","San Diego State","TBA"),
                  ("2027-02-24","Oregon State","TBA"),("2027-03-06","Fresno State","TBA")]:
    add("wbb", f"Broncos women's hoops vs {opp}", d, t, venue=EMA, impact="low", src="wbb")

# --- Concerts & shows ---
add("music", "Dwight Yoakam (concert)", "2026-11-12", "8:00 PM", venue=ICA, impact="high", src="ica",
    note="Doors 6:30 PM")

# --- Festivals & tournaments ---
add("festival", "Treefort Music Fest", "2027-03-31", "All day", end="2027-04-04", venue="Downtown Boise",
    impact="max", src="treefort", note="5-day downtown festival; overlaps Steelheads Mar 31, Apr 2, Apr 3")
add("festival", "Big Sky Basketball Championships", "2027-03-05", "All day", end="2027-03-10", venue=ICA,
    impact="max", src="bigsky", note="Men's + women's tournament; visiting fan groups often meet at the Warehouse")

# --- Conventions (Boise Centre, across the street) ---
# Boise Centre's own calendar is empty right now, so these come from organizer pages.
add("convention", "R-CON Boise (conference)", "2026-10-12", "All day", end="2026-10-15",
    venue="Boise Centre (across the street)", impact="med", src="rcon")
add("convention", "Arts Northwest conference", "2026-10-19", "All day", end="2026-10-22",
    venue="Boise Centre + Egyptian Theatre", impact="med", src="artsnw")
add("convention", "Idaho Mining Conference", "2026-10-26", "All day", end="2026-10-27",
    venue="Boise Centre (across the street)", impact="med", src="mining",
    note="Dates match the Warehouse newsletter (9/28); listing site is not the organizer")
add("convention", "Idaho School Boards Association convention", "2026-11-04", "All day", end="2026-11-06",
    venue="Boise Centre (across the street)", impact="med", src="isba")
add("convention", "Saint Alphonsus Festival of Trees", "2026-11-24", "5:00 PM", end="2026-11-30",
    venue="Boise Centre (across the street)", impact="med", src="fot",
    note="Gala Tue 11/24; public hours Wed 10-8, Thu (Thanksgiving) 2-6, Fri 10-9, Sat 10-8, Sun 10-5; fashion show Mon 11/30")

# --- Warehouse & downtown (non-weekly) ---
for d in ["2026-11-05","2026-12-03","2027-01-07","2027-02-04","2027-03-04","2027-04-01"]:
    acts = {"2026-11-05": "Spencer Batt", "2026-12-03": "Jake Ransom",   # from warehouseboise.com/entertainment
            "2027-01-07": "Natalie Soma", "2027-02-04": "Jessa Larson"}
    add("downtown", "First Thursday (downtown + Warehouse live music)", d, "5:00 PM",
        venue="Downtown Boise / Warehouse", impact="med", src="firstthu",
        note=f"Warehouse live music 5-8 PM: {acts[d]}" if d in acts else "")

add("festival", "Downtown Holiday Tree Lighting", "2026-11-27", "5:00 PM", venue="Grove Plaza (outside the door)",
    impact="max", src="treelight",
    note="5-6 PM on the Grove; also opens the Holidays on the Grove vendor sheds. Owner: this one is huge")
add("downtown", "Small Business Saturday (downtown shops)", "2026-11-28", "All day", venue="Downtown Boise",
    impact="med", src="shopsmall", note="Downtown-wide shopping promo; day after the tree lighting")

# Warehouse Food Hall one-offs (warehouseboise.com; check every week)
WH = "Warehouse Food Hall (here)"
add("downtown", "Halloween Hangout at the Warehouse", "2026-10-19", "5:30 PM", venue=WH, impact="med",
    src="warehouse", note="5:30-8:30 PM; DJ, kids' activities, costume contest. Free, family-friendly")
for d, t, nt in [("2026-10-17","5:00 PM","5-8 PM"),("2026-11-21","4:00 PM","4-7 PM"),("2026-12-05","4:00 PM","4-7 PM")]:
    add("downtown", "SCION THE BAND live at the Warehouse", d, t, venue=WH, impact="low", src="warehouse",
        note=f"Live jazz/blues/funk, {nt}")
add("downtown", "Taste of Downtown Boise", "2026-10-16", "All day", end="2026-10-25",
    venue="Downtown Boise (Warehouse vendors participating)", impact="med", src="taste",
    note="10-day dining promo; Loading Dock, Brotherly Love, Totally Smashed, CAMP specials $14 or less")

# --- Weekly regulars (hidden by default on the board) ---
d = dt.date(2026, 10, 10)
while d <= dt.date(2026, 12, 19):          # 2026 season ends Dec 19
    add("weekly", "Capital City Public Market", d.isoformat(), "9:30 AM",
        venue="Grove Plaza / 8th St (outside the door)", impact="med", src="market",
        note="Saturday market, 9:30 AM – 1:30 PM")
    d += dt.timedelta(days=7)

# --- Merge in the rows scraped by tools/scrape.py (data/auto.json) ---
import re, difflib
try:
    from zoneinfo import ZoneInfo
    NOW = dt.datetime.now(ZoneInfo("America/Boise"))          # the Action runs in UTC
except Exception:
    NOW = dt.datetime.now()
TODAY = NOW.date()
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
try:
    with open(os.path.join(ROOT, "data", "auto.json")) as f:
        auto = json.load(f)
except (OSError, ValueError):
    auto = {"sources": {}, "events": {}}
    print("NOTE: data/auto.json missing - building from the hand-checked rows only")
try:
    with open(os.path.join(ROOT, "data", "weather.json")) as f:
        auto["weather"] = json.load(f)
except (OSError, ValueError):
    auto["weather"] = []

def _norm(t):
    t = t.lower()
    t = re.sub(r"\(.*?\)", " ", t)                      # drop parentheticals
    t = re.sub(r"\b(the|at|vs|annual|2026|2027|live|conference|convention|saint alphonsus)\b", " ", t)
    return re.sub(r"[^a-z0-9]+", " ", t).strip()
def _dup(a, b):
    if a["start"] > b["end"] or b["start"] > a["end"]:
        return False
    x, y = _norm(a["title"]), _norm(b["title"])
    if not x or not y:
        return False
    return x in y or y in x or difflib.SequenceMatcher(None, x, y).ratio() >= 0.8

GAMES = ("hockey", "football", "mbb", "wbb")           # one game per team per day -> match on the date
SRC_OF = {"hockey": "ica", "football": "fb", "mbb": "mbb", "wbb": "wbb"}
def _twin(e, pool):
    if e["cat"] in GAMES:
        return next((k for k in pool if k["cat"] == e["cat"] and k["start"] == e["start"]), None)
    return next((k for k in pool if _dup(k, e)), None)

added = changed = 0
for key, rows in (auto.get("events") or {}).items():
    for a in rows:
        twin = _twin(a, [k for k in events if not k.get("auto")])   # only match hand-checked rows
        if twin is None:
            events.append(dict(a, auto=key)); added += 1
            continue
        twin["seen"] = True                              # the official page still lists it
        if a.get("time") not in (None, "TBA", "TBD", "All day") and twin.get("time") != a["time"]:
            print(f"TIME  {twin['title']} {twin['start']}: {twin.get('time')} -> {a['time']}")
            twin["time"] = a["time"]; changed += 1
        if a.get("doors"):
            twin["doors"] = a["doors"]
        if a["cat"] in GAMES and a["venue"] != twin["venue"]:
            twin["venue"], twin["impact"] = a["venue"], a["impact"]
print(f"auto rows: {added} added, {changed} times updated")

# A hand-entered game that the official schedule no longer shows on that date was probably moved or
# cancelled. Don't delete it (the scraper could be wrong) - flag it so the board says "verify".
for e in events:
    k = SRC_OF.get(e["cat"])
    if (k and not e.get("auto") and not e.get("seen") and e["start"] >= TODAY.isoformat()
            and e["title"].startswith(("Broncos", "Steelheads vs"))
            and (auto.get("sources") or {}).get(k, {}).get("ok")):
        e["check"] = True
        print(f"CHECK {e['title']} {e['start']} is not on the official schedule page any more")
    e.pop("seen", None)

# --- De-duplicate the hand-checked rows against each other ---
kept = []
for e in events:
    twin = None if e.get("auto") else next((k for k in kept if not k.get("auto") and _dup(k, e)), None)
    if twin:
        print(f"DUPLICATE dropped: {e['title']} ({e['start']}) ~ {twin['title']}")
    else:
        kept.append(e)
events[:] = kept


# --- Staffing guidance from the Oct 2025-Oct 2026 Square sales report (see event-staffing-report) ---
# Headcount = people on the clock at the dinner/rush peak. Lunch stays at 2 for nearly every event type.
# Types without a measurable lift get the normal-day number so nobody over-schedules.
# Returns (text for the card, lunch headcount, dinner headcount). None = no number for that part.
def _normal(d):
    wd = d.weekday()                                   # Mon=0 ... Sun=6
    return 4 if wd == 4 else 3 if wd == 5 else 2
def staff_for(e, d=None):
    d = d or dt.date.fromisoformat(e["start"]); cat = e["cat"]; t = e["title"]; ven = e["venue"]
    wd = d.weekday(); wkend = wd in (4, 5)
    if cat == "hockey" and e.get("time") == "7:10 PM":
        n = 5 if wkend else 3
        return f"Staff {n} on the clock 5:00-7:30 PM (lunch 2)", 2, n
    if cat == "festival" and t.startswith("Big Sky"):
        return "Staff 4 at dinner (5 on Saturday); lunch 2-3 - lunch is busy too", 3, 5 if wd == 5 else 4
    if cat == "festival" and t.startswith("Treefort"):
        return "Staff 3 at dinner, lunch 2 (provisional - little history)", 2, 3
    if cat == "football" and t.startswith("Broncos football"):
        return "Staff 6 at dinner (peaks ~6 PM and ~8 PM), lunch 3 (provisional - little history)", 3, 6
    if cat == "music":
        return "Staff 3-4 in the 90 min before the show (only 1 show of history)", 2, 4
    if cat == "mbb" and ("Idaho Central" in ven or "next door" in ven):
        return "Staff 4 in the 90 min before tip-off (only 1 game of history)", 2, 4
    if cat == "downtown" and t.startswith("First Thursday"):
        return "Staff 3 at dinner (lift is small; judgment call)", 2, 3
    if cat in ("convention", "mbb", "wbb", "weekly"):
        return f"Normal staffing for the day (lunch 2, dinner {_normal(d)}) - no measurable lift", None, None
    return None, None, None
for e in events:
    st = staff_for(e)[0]
    if st: e["staff"] = st

# sanity: every date parses, end >= start
for e in events:
    s = dt.date.fromisoformat(e["start"]); en = dt.date.fromisoformat(e["end"])
    assert en >= s, e
events.sort(key=lambda e: (e["start"], e.get("time") or ""))

# --- Day-by-day plan: one lunch number and one dinner number per day -------------------------
# Takes the HIGHEST number any event that day calls for (never adds them together - there is no
# sales history for two big events on one night, so the board flags those as "stacked" instead).
BIG = ("high", "max")
plan = {}
day = TODAY - dt.timedelta(days=1)
while day <= TODAY + dt.timedelta(days=180):
    di = day.isoformat()
    todays = [e for e in events if e["start"] <= di <= e["end"] and e["cat"] != "shows"]
    lunch, dinner, why = 2, _normal(day), None
    for e in todays:
        _, l, n = staff_for(e, day)
        if l and l > lunch: lunch = l
        if n and n > dinner: dinner, why = n, e["title"]
    big = [e["title"] for e in todays if e["impact"] in BIG]
    nohist = [e["title"] for e in todays if e["impact"] in BIG and staff_for(e, day)[2] is None]
    if todays:
        p = {"lunch": lunch, "dinner": dinner, "base": _normal(day)}
        if why: p["why"] = why
        if len(big) >= 2: p["stack"] = len(big)
        if nohist: p["nohist"] = nohist
        plan[di] = p
    day += dt.timedelta(days=1)

# --- Calendar context: things that shift normal traffic but aren't events ----------------------
def nth(year, month, weekday, n):                      # n-th weekday of a month (n=-1 -> last)
    if n > 0:
        d = dt.date(year, month, 1)
        d += dt.timedelta(days=(weekday - d.weekday()) % 7 + 7 * (n - 1))
    else:
        d = dt.date(year + (month == 12), month % 12 + 1, 1) - dt.timedelta(days=1)
        d -= dt.timedelta(days=(d.weekday() - weekday) % 7)
    return d
context = []
def ctx(label, start, end=None, kind="info"):
    s = start.isoformat() if isinstance(start, dt.date) else start
    en = (end.isoformat() if isinstance(end, dt.date) else end) or s
    context.append({"start": s, "end": en, "label": label, "kind": kind})
OFF = "government offices and banks closed"
for y in (TODAY.year, TODAY.year + 1):
    tg = nth(y, 11, 3, 4)
    ctx(f"New Year's Day - {OFF}", dt.date(y, 1, 1), kind="holiday")
    ctx(f"MLK / Idaho Human Rights Day - {OFF}", nth(y, 1, 0, 3), kind="holiday")
    ctx(f"Presidents' Day - {OFF}", nth(y, 2, 0, 3), kind="holiday")
    ctx(f"Memorial Day - {OFF}", nth(y, 5, 0, -1), kind="holiday")
    ctx(f"Juneteenth - {OFF}", dt.date(y, 6, 19), kind="holiday")
    ctx(f"Independence Day - {OFF}", dt.date(y, 7, 4), kind="holiday")
    ctx(f"Labor Day - {OFF}", nth(y, 9, 0, 1), kind="holiday")
    ctx(f"Columbus / Indigenous Peoples' Day - {OFF}", nth(y, 10, 0, 2), kind="holiday")
    ctx(f"Veterans Day - {OFF}", dt.date(y, 11, 11), kind="holiday")
    ctx("Thanksgiving Day", tg, kind="holiday")
    ctx("Black Friday", tg + dt.timedelta(days=1), kind="holiday")
    ctx("Christmas Eve", dt.date(y, 12, 24), kind="holiday")
    ctx(f"Christmas Day - {OFF}", dt.date(y, 12, 25), kind="holiday")
    ctx("New Year's Eve", dt.date(y, 12, 31), kind="holiday")
# Boise State academic calendar (SRC["bsucal"]) - re-enter each summer when the new calendar posts
ctx("Boise State on Thanksgiving break (no classes)", "2026-11-23", "2026-11-29", kind="school")
ctx("Boise State finals week", "2026-12-14", "2026-12-18", kind="school")
ctx("Boise State commencement", "2026-12-19", kind="school")
ctx("Boise State between semesters (classes resume Jan 11)", "2026-12-20", "2027-01-10", kind="school")
ctx("Boise State spring break (no classes)", "2027-03-15", "2027-03-19", kind="school")
ctx("Boise State finals week", "2027-05-03", "2027-05-07", kind="school")
ctx("Boise State commencement", "2027-05-07", "2027-05-08", kind="school")
context = [c for c in context if c["end"] >= (TODAY - dt.timedelta(days=31)).isoformat()]
context.sort(key=lambda c: c["start"])

for e in events:
    e.pop("seen", None)

out = {
    "updated": TODAY.isoformat(),
    "built": NOW.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if NOW.tzinfo else NOW.isoformat(),
    "sources": [dict(key=k, **{f: v.get(f) for f in ("label", "ok", "last_ok", "url")})
                for k, v in (auto.get("sources") or {}).items()],
    "weather": auto.get("weather") or [],
    "context": context,
    "context_src": SRC["bsucal"],
    "plan": plan,
    "categories": {
        "hockey":   {"label": "Hockey",            "color": "#4FA3FF"},
        "football": {"label": "Football",          "color": "#FF7A1A"},
        "mbb":      {"label": "Men's Hoops",       "color": "#FFB547"},
        "wbb":      {"label": "Women's Hoops",     "color": "#F2D16B"},
        "music":    {"label": "Arena Shows",       "color": "#C77DFF"},
        "festival": {"label": "Festivals & Tourneys","color": "#FF5C8A"},
        "convention":{"label": "Boise Centre",     "color": "#3DDC97"},
        "downtown": {"label": "Warehouse & Downtown","color": "#7FD1C7"},
        "weekly":   {"label": "Weekly regulars",   "color": "#A3A9B3", "defaultOff": True},
        "shows":    {"label": "Nearby club shows", "color": "#8E9BFF", "defaultOff": True},
    },
    "events": events,
}
path = os.path.join(ROOT, "events.json")
with open(path, "w") as f:
    json.dump(out, f, indent=1)
print(f"wrote {len(events)} events -> {os.path.normpath(path)}")
bad = [s["label"] for s in out["sources"] if not s["ok"]]
if bad:
    print("SOURCES FAILED THIS RUN: " + ", ".join(bad))
