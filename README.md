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
