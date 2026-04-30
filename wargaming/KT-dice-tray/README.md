# Kill Team Dice Tray and Score Tracker

This design now uses a single active folder.

## Active Working Folder

- `score-tracker/` is the only active working folder.
- `score-tracker/kill_team_dice_tray_and_score_tracker.py` is the current FreeCAD macro.
- `generate_diagrams.py` reads that macro and generates diagrams into `score-tracker/` by default:
   - `diagram_top_view.png`
   - `diagram_side_section.png`
   - `diagram_end_section.png`

## Versioning Convention (Git Tags)

Use Git tags to pin releases instead of creating new source folders.

### Suggested tag format

- `vMAJOR.MINOR.PATCH`
- Example: `v3.0.0`

### Typical release flow

1. Commit changes to the canonical files.
2. Create an annotated tag:

   `git tag -a v3.0.0 -m "Kill Team dice tray + score tracker v3.0.0"`

3. Push commit(s) and tag:

   `git push origin main --follow-tags`

### Working on next version

Edit files in `score-tracker/`, commit, and tag the new release (for example `v3.1.0`).
