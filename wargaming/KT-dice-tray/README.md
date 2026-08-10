# Kill Team Dice Tray and Score Tracker

This design now uses a single active folder.

## Active Working Folder

- `score-tracker/` is the only active working folder.
- `score-tracker/kill_team_dice_tray_and_score_tracker.py` is the current FreeCAD macro.
- `generate_diagrams.py` reads that macro and generates diagrams into `score-tracker/` by default:
   - `diagram_top_view.png`
   - `diagram_side_section.png`
   - `diagram_end_section.png`

## Design Variants

### `score-tracker/` (v3/v4 Classic)

Monolithic tray with integrated dice pockets, rolling arena, and side-mounted score tracker.

### `modular-v4/` (Modular Alternative)

A new experimental variant featuring:
- **Two independent modules**: Norm/Crit tray + Standalone score tracker
- **Optional bridge-key linking**: Underside edge notches + detachable H-shaped bridge key
- **No rolling arena**: Full-width norm/crit rows maximize dice space
- **Enlarged die pockets**: All slots increased by +1.0 mm for better fit
- **Clear ONE/TWO orientation**: Score tracker has mirrored side-label layout
- **Programmatic engraved labels**: Center and side labels are generated in the FreeCAD macro
- **Standalone usable**: Each module printable and functional on its own
- **Retained assembled width**: 105 mm (same as classic version)

See `modular-v4/README.md` for details on building, assembly, and customization.

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
