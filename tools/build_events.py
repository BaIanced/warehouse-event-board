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
    "market": "https://www.idahonews.com/news/idaho-photo-galleries/capital-city-public-market-opens-2026-season",
}

# Extra sources to re-check every week (not tied to a row yet). Only add an event once
# one of these shows a confirmed 2026-27 date. Known gaps as of 2026-10-16:
#   Holiday Tree Lighting + Small Business Saturday 2026 dates not posted yet (2025 pages only).
#   OWNER SAYS Downtown Holiday Tree Lighting (Grove Plaza, 2025 was Fri Nov 28 5-6 PM) IS HUGE:
#   add as cat "festival", impact "max" the moment a 2026 date is confirmed. Never guess the date.
WATCH = [
    "https://www.warehouseboise.com/  (+ /entertainment, FB/IG) - Warehouse one-offs",
    "https://downtownboise.org/events/events-calendar - DBA calendar",
    "https://downtownboise.org/events/downtown-holiday-tree-lighting",
    "https://downtownboise.org/events/shop-small",
    "https://www.visitboise.com/events/ - Visit Boise calendar (use month filter)",
    "https://boisedev.com , https://www.idahopress.com/boiseweekly - local news",
    "Organizer pages + web search for Boise Centre conventions",
    "Employee tips (e.g. Facebook groups): confirm on an official page before adding",
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
    add("mbb", f"Broncos men's hoops vs {opp}", d, "TBA", venue=EMA, impact="med", src="mbb")

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
add("convention", "Idaho School Boards Association convention", "2026-11-04", "All day", end="2026-11-06",
    venue="Boise Centre (across the street)", impact="med", src="isba")
add("convention", "Saint Alphonsus Festival of Trees", "2026-11-24", "5:00 PM", end="2026-11-29",
    venue="Boise Centre (across the street)", impact="med", src="fot",
    note="Gala Tue 11/24; public hours Wed 10-8, Thu (Thanksgiving) 2-6, Fri 10-9, Sat 10-8, Sun 10-5; fashion show Mon 11/30")

# --- Warehouse & downtown (non-weekly) ---
for d in ["2026-11-05","2026-12-03","2027-01-07","2027-02-04","2027-03-04","2027-04-01"]:
    acts = {"2026-11-05": "Spencer Batt", "2026-12-03": "Jake Ransom"}   # from warehouseboise.com
    add("downtown", "First Thursday (downtown + Warehouse live music)", d, "5:00 PM",
        venue="Downtown Boise / Warehouse", impact="med", src="firstthu",
        note=f"Warehouse live music 5-8 PM: {acts[d]}" if d in acts else "")

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

# --- De-duplicate: same day-range overlap + similar title (or one title inside the other) ---
import re, difflib
def _norm(t):
    t = t.lower()
    t = re.sub(r"\(.*?\)", " ", t)                      # drop parentheticals
    t = re.sub(r"\b(the|at|vs|annual|2026|2027|live|conference|convention)\b", " ", t)
    return re.sub(r"[^a-z0-9]+", " ", t).strip()
def _dup(a, b):
    if a["start"] > b["end"] or b["start"] > a["end"]:
        return False
    x, y = _norm(a["title"]), _norm(b["title"])
    if not x or not y:
        return False
    return x in y or y in x or difflib.SequenceMatcher(None, x, y).ratio() >= 0.8
kept = []
for e in events:
    twin = next((k for k in kept if _dup(k, e)), None)
    if twin:
        print(f"DUPLICATE dropped: {e['title']} ({e['start']}) ~ {twin['title']}")
    else:
        kept.append(e)
events[:] = kept

# sanity: every date parses, end >= start
for e in events:
    s = dt.date.fromisoformat(e["start"]); en = dt.date.fromisoformat(e["end"])
    assert en >= s, e
events.sort(key=lambda e: (e["start"], e.get("time") or ""))

out = {
    "updated": dt.date.today().isoformat(),
    "categories": {
        "hockey":   {"label": "Hockey",            "color": "#4FA3FF"},
        "football": {"label": "Bronco Football",   "color": "#FF7A1A"},
        "mbb":      {"label": "Men's Hoops",       "color": "#FFB547"},
        "wbb":      {"label": "Women's Hoops",     "color": "#F2D16B"},
        "music":    {"label": "Concerts & Shows",  "color": "#C77DFF"},
        "festival": {"label": "Festivals & Tourneys","color": "#FF5C8A"},
        "convention":{"label": "Conventions",      "color": "#3DDC97"},
        "downtown": {"label": "Warehouse & Downtown","color": "#7FD1C7"},
        "weekly":   {"label": "Weekly regulars",   "color": "#A3A9B3", "defaultOff": True},
    },
    "events": events,
}
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "events.json")
with open(path, "w") as f:
    json.dump(out, f, indent=1)
print(f"wrote {len(events)} events -> {os.path.normpath(path)}")
