# Building and releasing

The Windows program is built automatically by GitHub Actions whenever you publish a release. You only need to build by hand for local testing.

## Publish a release (automatic build)

1. Update the files you changed, usually `calculator.html` and sometimes `local_planner.py`, and commit them to `main`. Keep the file name `calculator.html` exactly, because the build copies it into the program.
2. Set the version inside `calculator.html` (the `APP_VERSION` value, shown in the page header and title). It must match the release tag, so version `13.3` is released with the tag `13.3`.
3. On GitHub, go to Releases and choose Draft a new release.
4. In "Choose a tag", type the new version (for example `13.3`), choose "Create new tag on publish", and set the target to `main`.
5. Add a title and notes, then publish.
6. Open the Actions tab and watch the "Build Windows release" run. It takes about five minutes.
7. When it finishes, `AION2CraftPlanner-<tag>.zip` is attached to the release automatically. Do not upload a zip yourself.
8. Download the zip, extract the whole folder, run `AION2CraftPlanner.exe`, click Fetch Prices, look up a character, then click **Exit app**.

The page compares its own version with the newest release tag and shows an update banner when the release is newer. Use a tag with the same number as `APP_VERSION`, with or without a leading `v`.

Pushing commits alone does not build anything. Only publishing a release, or running the workflow by hand, does.

## What the workflow does

The workflow is `.github/workflows/release.yml`. It runs on Windows with Python 3.12, installs PyInstaller, builds the `--onedir` program with `calculator.html` bundled in, zips the `AION2CraftPlanner` folder, saves the zip as a workflow artifact, and attaches it to the release.

You can also start it from the Actions tab with "Run workflow". That run builds a zip named `AION2CraftPlanner-test.zip` as an artifact only, and does not touch any release.

If a build fails, open the failed run in the Actions tab to read the error. After you fix the cause, publish the release again: delete the release and its tag, then recreate it.

## Build by hand (optional)

This needs Windows and Python 3.10 or newer.

1. Close any running copy of the planner.
2. Run `build_exe.bat` in the repository folder. It creates a private `.venv`, installs PyInstaller and builds.
3. The finished program is the folder `dist\AION2CraftPlanner\`.
4. Test it: run `AION2CraftPlanner.exe`, click Fetch Prices, then **Exit app**.

Do not commit `dist/`, `build/` or `.venv/` to the repository. The `.gitignore` already excludes them.

## Run without building

For quick tests, run `python local_planner.py` (or double-click `Start Calculator.bat` on Windows) in the repository folder. Do not open `calculator.html` directly, because fetching prices and characters needs the local relay.
