# Kill Team Dice Tray and Score Tracker

This design now uses a single source-of-truth file instead of versioned source folders.

## Canonical Source

- `kill_team_dice_tray_and_score_tracker.py` is the current FreeCAD macro.
- `generate_diagrams.py` reads that macro and generates:
  - `diagram_top_view.png`
  - `diagram_side_section.png`
  - `diagram_end_section.png`

## Versioning Convention (Git Tags)

Use Git tags to pin released versions instead of creating new `vX-*` source folders.

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

Edit the same canonical source file, commit, and tag the new release (for example `v3.1.0`).
