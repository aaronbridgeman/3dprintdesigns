# Kill Team Modular Norm/Crit Tray + Standalone Score Tracker (v4)

This variant implements a modular redesign with two independent pieces:

- **Norm/Crit module** (no rolling arena)
- **Standalone score tracker**

The pieces can be used independently or docked together using a press-fit seam.

## What Changed

1. New folder for this version: `modular-v4/`.
2. Removed the central rolling arena concept from this design variant.
3. Added modular join features so parts fit together neatly and can be separated.
4. Retained assembled overall width at **105 mm** (same as active score-tracker macro baseline).
5. Score tracker is a standalone unit with clear P1 and P2 orientation.
6. All die pocket dimensions were increased by **+1.0 mm**.

## Files

- `kill_team_modular_norm_crit_and_score_tracker.py` FreeCAD macro for both modules and an assembled preview.
- `generate_diagrams.py` Generates concept diagrams and section-style visuals.

## Build (FreeCAD)

1. Open FreeCAD.
2. Run `kill_team_modular_norm_crit_and_score_tracker.py`.
3. Export desired bodies:
   - `NormCritModule`
   - `ScoreTrackerModule`
   - Optional `AssembledPreview`

## Diagram Generation

From this folder:

```powershell
python generate_diagrams.py
```

Outputs:

- `diagram_top_assembled.png`
- `diagram_top_norm_crit_module.png`
- `diagram_top_score_tracker_module.png`
- `diagram_dimensions_summary.png`

## Notes

- Join fit uses a medium default clearance suitable for PLA/PETG test prints.
- If the seam is too tight/loose on your printer, tweak `connector_clearance` in the macro.
