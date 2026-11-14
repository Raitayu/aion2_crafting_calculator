# AION2 EU Craft Planner v10.0

A small local calculator for AION2 EU crafting costs. It models the Star / Dark / Ebony Dragon Lord evolution chains, the 25% combo chance, owned materials, Balaur buy-or-craft decisions, and market prices fetched from aion2.exchange for your EU server.

## Option A: Windows program (no Python needed)

1. Open the **Releases** page of this repository and download `AION2CraftPlanner-vX.Y.zip`.
2. Extract the whole zip, then run `AION2CraftPlanner.exe`.
3. Your browser opens the calculator at http://127.0.0.1:8765/. Use the **Exit app** button to stop it.

Windows SmartScreen may warn because the program is not code-signed. Only run builds you trust.

## Option B: Python (any OS)

Requires Python 3.10+. No extra packages.

- Windows: extract the repository, then double-click `Start Calculator.bat`.
- Mac/Linux: run `python3 local_planner.py`.

Do not open `calculator.html` directly: Fetch Prices needs the included local relay.

## Features

- Pick your EU server (46 supported); prices are cached per server.
- Owned materials: totals show Cash to spend and Full material value.
- Balaur buy-or-craft table with recommendation and optional threshold.
- Refresh status: success or failure, time, counts, newest price capture.
- Recipe editor: edit quantities, add stages or families, export/import recipes.

## Data and limitations

- Initial Quai prices are a Nov 13, 2026 snapshot; click Fetch Prices before relying on them.
- Expected-mode savings from owned items are estimates; use "No procs" for a safe budget.
- Dragon Lord intermediates are not bought automatically; Balaur is the only material sub-recipe.
- Prices, owned items and recipe edits are saved in your browser. Back up with Export prices / Export recipes.
- The local relay listens on 127.0.0.1 only and permits only the aion2.exchange items endpoint for EU servers.

## Building the Windows program

See [BUILD.md](BUILD.md).
