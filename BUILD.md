# Building and releasing

The Windows build must be done on Windows with Python 3.10+.

## Build

1. Close any running copy of the planner.
2. Run `build_exe.bat` in the repository folder. It creates a private `.venv`, installs PyInstaller and builds.
3. The finished program is the folder `dist\AION2CraftPlanner\`.
4. Test it: run `AION2CraftPlanner.exe`, click Fetch Prices, then **Exit app**.

## Release zip

1. Zip the **folder** `dist\AION2CraftPlanner` itself, so the zip contains `AION2CraftPlanner\AION2CraftPlanner.exe` and its support files.
2. Name it `AION2CraftPlanner-vX.Y.zip` (for example `AION2CraftPlanner-v10.0.zip`).
3. On GitHub: Releases -> Draft a new release -> choose a tag like `v10.0` -> attach the zip -> Publish.

Do not zip only the `.exe`, and do not commit `dist/`, `build/` or `.venv/` to the repository (the `.gitignore` already excludes them).
