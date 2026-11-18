# Warehouse Event Board

A simple installable web app (PWA) for the Warehouse Food Hall KDS. It shows upcoming events that bring foot traffic downtown and gives a rough staffing note for each day.

## What's tracked
- Idaho Steelheads home games (Idaho Central Arena, next door)
- Boise State football, men's and women's basketball home games
- Concerts and shows at Idaho Central Arena
- Festivals and tournaments (Treefort, Big Sky Basketball Championships)
- Conventions at Boise Centre
- Warehouse and downtown events that aren't weekly (First Thursday)

Every event in `events.json` carries a `src` link to where its date came from.

## Using it
- Two views: **Next 2 weeks** and **Month**. Tap a day in Month view for details.
- Tap the colored chips to hide or show event types and impact levels. Choices are saved per device.
- The page refreshes its data every hour and redraws at midnight, so it can stay open on the KDS.
- Works offline with the last saved schedule.

## Updating events
Edit the lists in `tools/build_events.py`, run `python3 tools/build_events.py`, and commit `events.json`. Pushing to `main` redeploys automatically.

## Files
- `index.html` — the app
- `events.json` — event data (generated)
- `manifest.webmanifest`, `sw.js` — PWA install + offline support
- `tools/make_icons.py` — draws the app icons (run by the deploy workflow)
- `.github/workflows/pages.yml` — builds and deploys to GitHub Pages

## How it stays up to date (changed 2026-11-17)

The refresh now runs inside this repo. No Claude connector or scheduled task is involved.

- `.github/workflows/pages.yml` runs every morning (about 4-5 AM Boise time), on every push, and from the **Run workflow** button on the Actions tab.
- `tools/scrape.py` reads the sources a script can read: Idaho Central Arena, the Bronco football / men's / women's basketball schedules (home games only), the Boise Centre calendar, Treefort Music Hall, Knitting Factory, and the National Weather Service forecast. Results go to `data/auto.json`.
- `tools/build_events.py` holds the hand-checked rows (conventions from organizer pages, festivals, Warehouse one-offs), merges in `data/auto.json`, and writes `events.json`. `events.json` is built during the run and is no longer stored in the repo.
- If a site is down or changes its layout, that one source keeps its last good rows and the board says which source it couldn't reach. If the board itself goes 3+ days without a refresh, a banner appears on screen.
- A script can't read the Warehouse site, downtownboise.org listings, or convention organizer pages. Those rows are edited by hand in `tools/build_events.py` (see the `WATCH` list there), about once a month.
