# Kill Team Modular Norm/Crit Tray + Standalone Score Tracker (v4)

This variant implements a modular redesign with two independent pieces:

- **Norm/Crit module** (no rolling arena)
- **Standalone score tracker**
- **Optional bridge key accessory** (small detachable link)

The pieces can be used independently, and optionally bridged together using printed keys when you want a fixed arrangement.

## What Changed

1. New folder for this version: `modular-v4/`.
2. Removed the central rolling arena concept from this design variant.
3. Added universal underside edge notch features so any two touching modules can be linked with optional bridge keys.
4. Retained assembled overall width at **105 mm** (same as active score-tracker macro baseline).
5. Score tracker is a standalone unit with clear ONE and TWO orientation.
6. Labels are generated directly in the macro (engraved text), so slicer-side text setup is no longer required.
7. All die pocket dimensions were increased by **+1.0 mm**.

## Files

- `kill_team_modular_norm_crit_and_score_tracker.py` FreeCAD macro for both modules and an assembled preview.
- `generate_diagrams.py` Generates concept diagrams and section-style visuals.

## Build (FreeCAD)

1. Open FreeCAD.
2. Run `kill_team_modular_norm_crit_and_score_tracker.py`.
3. Export desired bodies:
   - `NormCritModule`
   - `ScoreTrackerModule`
   - `BridgeKeyAccessory` (print 4-8x)
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
- `diagram_bridge_key_accessory.png`
- `diagram_dimensions_summary.png`
- `diagram_side_profile_z_axis.png`

## Notes

- Bridge keys use a small built-in clearance (`bridge_key_clearance`) for PLA/PETG test prints.
- Bridge key geometry is H-shaped so each side seats into a module notch, with a center spine connecting across the seam.
- If bridge keys are too tight/loose, tweak `bridge_key_clearance` in the macro.
