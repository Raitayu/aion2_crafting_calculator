AION2 EU Craft Planner v9.3 - Complete Friends Bundle

REQUIREMENT: Python 3.10 or newer installed on each computer.
No third-party packages. Python itself is NOT bundled; this is not a standalone EXE.

WINDOWS
1. Extract the whole ZIP.
2. Double-click Start Calculator.bat.
3. Use the browser tab opened at http://127.0.0.1:8765/.
4. Keep the terminal window open. Ctrl+C stops the app.
5. Select your EU server and click Fetch Prices.
Do not open calculator.html directly: Fetch needs the included local relay.

MAC/LINUX: run python3 local_planner.py from the extracted folder.

EVERYTHING INCLUDED
calculator.html, local_planner.py, Windows launcher, README.
No formatting updater, server updater, prior HTML or separate proxy fix required.
46 EU servers: 23 Elyos and 23 Asmodian. Names/IDs from supplied API directory.
Quai default. Other server caches start empty, not with Quai prices.
Readable browser-local timestamps and listing counts built in.
19 item families, levels, start/target, combo scenarios and Total Cost rows.
Balaur Auto/Buy/Craft, expanded Essence/vendor costs, farming checkbox.
Paginated bulk refresh filters required items; per-server cache; JSON import/export.

UPGRADE
Close the previous launcher first (same port 8765).
Export prices as backup. v9 browser storage key aion9 is reused on the same localhost address/browser. Non-EU saved selection falls back to Quai; caches are not deleted.

DATA/LIMITATIONS
Initial Quai prices are the supplied Nov 13 snapshot, not live quotes. Refresh before relying on them.
Longsword/Dagger/Mace/Guard still use the unverified Greatsword quantity template.
No automatic buying of Dragon Lord intermediates; Balaur is the only material sub-recipe.
API summaries do not guarantee bulk availability. Craft interruptions excluded.
Server list is embedded, not automatically refreshed.
Live upstream connection was not testable in the build environment; paste/file imports are retained.
The relay binds only to 127.0.0.1 and permits only the fixed upstream items endpoint for EU IDs. No public proxy or disabled browser security.
