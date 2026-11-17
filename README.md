# Smartsheet to HubSpot

A picture dictionary for staff moving from the two Smartsheet logs (Patient Intake (MAIN) and NM Patient Log) to HubSpot.
Live at https://gmyoung.github.io/smartsheet-to-hubspot/

- The page looks like the old sheet. Click the column you used to fill; the bar at the bottom says what it was and has the button **Walk me through it in HubSpot**.
- The walkthrough starts on the ICT Patients list, goes into the patient, to the right tab and to the field, one step at a time, with the place circled on a screenshot.

Every patient, phone number and address here is made up; the screenshots are from the test sandbox.

## Keeping it current

This site is kept current with HubSpot: every change staff can see (a field, card, tab, button, step or name) is carried into the staff handbook and into this site in the same piece of work (HubSpot project, decision D225).

What to change, by what changed in HubSpot:

| What changed | Change here |
|---|---|
| How a thing is done, or its name | The text: `GROUPS` in `scripts/smartsheet_dictionary.py` of the HubSpot project (columns: Smartsheet column, sheet letters, what it was, where it is now, how it is done now) |
| A field moved on its card, or a card looks different | Retake that card's screenshot (table below), then fix the circles in `TARGETS` in `build.py` |
| A tab was renamed or moved, or a form opens from another button | `TAB_STEP`, `TAB_OF` and `BEFORE` in `build.py`, with a new screenshot if the tab row or menu looks different |
| A new field that takes over an old column | A row in `GROUPS`, a circle in `TARGETS` |
| The Smartsheet side (a column, the fake rows) | `sheets.json` |

Then:

1. After a text change, run `python -I scripts/smartsheet_dictionary.py` in the HubSpot project first (it rewrites the text table there and stops if a column of either sheet is missing or used twice). Then here `python -I build.py`: it reads `GROUPS` from `E:\CodeX\hubspot-ict-cm\scripts\smartsheet_dictionary.py`, writes `data.js`, and stops if a circle names a dictionary row or a screenshot that does not exist.
2. Look at the changed column in a browser. Serve the folder (`python -I -m http.server 8765 --bind 127.0.0.1`) and open `http://127.0.0.1:8765/#hph/J` (sheet / column letter); a file opened straight from disk does not load in the test browser.
3. Commit and push; GitHub Pages publishes `main` in about a minute.

### Screenshots

All are 1568 x 726, taken in the sandbox (portal 52133122) on the demo patient Brenda Castellanos, a made-up person (the first fake row of the Humboldt Park sheet). Circles are `[x, y, width, height]` in pixels of the screenshot. Never use a screenshot from production or of a real patient.

| File in `img/` | Shows | Retake when this changes (HubSpot project) |
|---|---|---|
| `new-patient` | New ICT Patient page | `coverage-card/src/app/pages/Home.tsx` |
| `patients-list` | ICT Patients list | the list's columns or the left menu |
| `overview-1`, `overview-3` | Patient page: the left card, the tab row, Overview tab | `OverviewCard.tsx`, the left sidebar, the tab row |
| `tabs-more`, `activities-menu` | The More tabs menu, the Add activities menu | the tab row, HubSpot's own menus |
| `demographics-1`, `-2`, `-3` | Patient Demographics tab | `DemographicsCard.tsx`, `dob.tsx`, `address.tsx` |
| `ed-visit`, `ed-notes` | Hospital EMR tab: ED Visit, ED Visit Notes | `EdVisitCard.tsx`, `CaseNotesCard.tsx` |
| `tracker-1`, `-2`, `-3` | Hospital EMR tab: Hospital EMR Tracker | `HospitalTrackerCard.tsx` |
| `log-call` | Log a Call | HubSpot's call form, the call outcomes |
| `insurance-top`, `-form`, `-policy`, `-verify`, `-notpl` | Insurance and Verification tab | `CoverageCard.tsx` |
| `attorney-top`, `-form`, `-verify` | Patient Attorney tab | `AttorneyCard.tsx` |

Not on the site yet: the Lien and Collection tab and the Care Coordination record (no screenshots), so columns that live there have text only.

## Files

- `index.html`: the page (the sheet, the bottom bar, the walkthrough). No build step, no libraries.
- `build.py`: writes `data.js` from `sheets.json` (the fake rows) and the dictionary text of the HubSpot project.
- `sheets.json`, `img/`, `data.js` (generated; committed so GitHub Pages can serve it).
