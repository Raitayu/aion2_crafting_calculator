# AION2 EU Craft Planner

A local calculator for AION 2 (EU servers). It plans crafting costs, compares craft-versus-buy decisions, works out soulbind reroll odds and costs, and can load your own character to suggest which soulbind line to reroll next. Prices come from aion2.exchange and character data from the official AION 2 site, both through a small relay that runs on your own computer.

## Install

### Option A: Windows program (no Python needed)

1. Open the **Releases** page of this repository and download the newest `AION2CraftPlanner-X.Y.zip`.
2. Extract the whole zip, then run `AION2CraftPlanner.exe`.
3. Your browser opens the calculator at http://127.0.0.1:8765/. Use the **Exit app** button to stop it.

Windows SmartScreen may warn because the program is not code-signed. Only run builds you trust.

### Option B: Python (any OS)

Requires Python 3.10+. No extra packages.

- Windows: extract the repository, then double-click `Start Calculator.bat`.
- Mac/Linux: run `python3 local_planner.py`.

Do not open `calculator.html` directly. Fetching prices and characters needs the included local relay.

## Tabs and features

### Crafting Prices

- Pick your EU server (46 supported). Prices are cached separately for each server.
- Models the Star, Dark and Ebony Dragon Lord evolution chains, including the 25% combo chance.
- Fetch Prices refreshes the selected chain or all supported chains, and shows the result, time, counts and newest price capture.
- Owned materials reduce the totals, which show Cash to spend and Full material value.
- Balaur buy-or-craft table with a recommendation.
- Shopping list for what you still need to buy.
- Recipe editor: edit quantities, add stages or families, and export or import recipes.
- "No procs" mode gives a safe budget; the expected mode estimates savings from owned items.

### Splendent Prices

Craft versus buy comparison for Artisan's Splendent items.

### Material Prices and Owned Materials

Edit material prices by hand or from fetched data, and record what you already own. Export prices to back them up.

### Cooking

Shows whether crafting food to sell is worth it, using vendor ingredient costs in Kina.

### Soulbind Odds and Soulbind Pools

- Pools lists which stats each equipment slot can roll, with their odds, for each class.
- The reroll calculator compares your next roll, simulates a realistic number of rerolls, and shows the best case by number of lines.
- Set a fodder price in the Reroll cost box to see expected kina costs.

### Character

Look up an EU character by name and server to see their equipment and soulbind lines. The tab also holds the damage model, reroll advice and line editor below.

## Damage model and reroll advice

The model ranks soulbind rerolls by modeled damage. It is a comparison tool, not an exact damage predictor.

- It follows a community damage formula for PvE bosses and ignores Boss Defense, Power Shard and Attack Bonus. Every value is editable. The fields start with sample values, so replace them with your own stats.
- Critical hit chance is capped at 50%. Boss Critical Hit Resist defaults to an estimated 1,200 for Ludra on Global, so adjust it if your game shows a different chance. Crit stats are worth little when you are below it.
- Combat Speed counts as extra hits per second, scaled by a "counts for" percentage (100% means all your damage speeds up).
- Skills (Gladiator for now): Overhead Slam, Rending Blow and Ruinous Blow use per-level damage data. Enter each skill's total level and its share of your damage.
- Passives (Gladiator): Identify Weakness, Attack Preparation, Impact Hit, Experienced Counterstrike and Murderous Burst convert each rank into the stats it gives. Buff uptimes are editable.
- Every line is compared at its maximum roll, both your current lines and the possible rerolls, so a line is always compared with another maximum roll.
- Reroll ranking simulates your next rerolls (10 by default), including the fact that a removed stat returns to the pool. Ties go to the line with the lowest pool chance.
- Skill lines sitting exactly on a Specialty level (8, 12, 16 or 20) are never suggested for rerolling, and Move Speed on earrings and boots is never suggested either. Set "Protect Specialty levels and kept lines" to 0 to allow both.
- Specialty options are not valued by the model, and other classes' skills count as 0 until their data is added.

To add a class, add lines to `DMG_SKILL_LIST` (skills) or `DMG_PASSIVES` (passives) in `calculator.html`. To keep another line on a slot, add it to `DMG_KEEP`.

### Set my current lines

The official site can lag behind the game by minutes or more, so a line you just rolled may not show up yet. Under the reroll table, each equipped slot has an editor: pick the stat you rolled and the advice updates at once. A stat the item already has cannot be picked, because a reroll can never land on it. Edits are remembered in your browser per character and item, and they clear on their own when the loaded data shows the same lines. After gaining or losing a skill line, also update that skill's level under Skills.

## Updates

The page checks the newest GitHub release and shows a banner when a newer version exists.

## Privacy and limits

- The relay listens on 127.0.0.1 only and accepts only requests from the calculator page.
- It contacts only aion2.exchange (prices) and the official AION 2 character pages, for EU servers only.
- Character requests are spaced out and cached for 10 minutes. Nothing is sent anywhere else.
- Prices, owned items, recipe edits, model settings and line edits are saved in your browser. Use Export prices and Export recipes to keep backups.
- Initial Quai prices are an old snapshot. Click Fetch Prices before relying on them.
- Dragon Lord intermediates are not bought automatically. Balaur is the only material sub-recipe.

## Releases and building

Publishing a GitHub release builds the Windows zip automatically (`.github/workflows/release.yml`) and attaches `AION2CraftPlanner-<tag>.zip`. See [BUILD.md](BUILD.md) for building by hand.
