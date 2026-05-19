# Kill Team Aura Aids (Sanctifiers)

Parametric 3D-print aids for visualizing aura coverage in Kill Team.

The aura is now an open lattice (not a solid ring):
- Inner and outer circular rails keep shape strength.
- Repeating windows keep plenty of visibility through the aid.
- Radial spokes connect ring to the center handle hub.

This folder contains:
- `aura_config.py`: all editable parameters.
- `sanctifiers_aura_aids.py`: FreeCAD macro that builds printable parts.
- `generate_diagrams.py`: technical step diagrams for review before FreeCAD import.
- `build_single_macro.py`: bundles source into one import-ready macro file.
- `build_all.py`: runs diagrams + single-file macro build in one command.
- `PRINT_AND_MATERIAL_RECOMMENDATIONS.md`: recommended Bambu print settings and lightweight tuning guidance.

## Current presets

- `sanctifiers_aura_6in_32mm_base`
- `sanctifiers_aura_3in_25mm_base`

## Build-plate handling

The script uses a Bambu Lab P2S build plate (`256x256mm`) and automatically splits oversized aids into multiple printable segments.

- Small aid that fits: generated as a single piece.
- Oversized aid: generated as radial segments plus a center hub with a low-profile knob.

Default oversized assembly style is press-fit tabs/slots.

## Added options

- Embossed part labels on every printable piece (for example `S6-32-P1`, `S6-32-H`).
- Handle presets:
	- `low_profile_knob`
	- `loop_handle`
	- `t_bar`
- Connector fit presets:
	- `tight`
	- `medium`
	- `loose`

## Generate diagrams

Run from this folder:

```bash
python generate_diagrams.py
```

Outputs one diagram image per preset, with 4 steps:
1. Aura geometry
2. Plate-fit and segmentation decision
3. Top-view printable piece layout
4. Side profile (ring, hub, knob)

Diagrams also show:
- Open-window ring pattern.
- Active handle preset.
- Active connector fit preset.
- Whether part labels are enabled.

## Build in FreeCAD

1. Open FreeCAD.
2. Run macro: `sanctifiers_aura_aids.py`.
3. The macro creates one document named `KillTeamAuraAids` with all printable parts laid out for export.
4. Export each part object as STL/3MF.

By default, the macro now creates two object sets:
- Assembly preview objects (`*_preview_*`): arranged as an assembled circle for visual checking.
- Print layout objects (`*_part_*`): arranged for export/printing.

You can control this in `aura_config.py`:
- `GENERATE_ASSEMBLY_PREVIEW`
- `GENERATE_PRINT_LAYOUT`
- `ASSEMBLY_PREVIEW_OFFSET_X_MM`
- `ASSEMBLY_PREVIEW_SPACING_Y_MM`
- `PRINT_LAYOUT_AID_GAP_Y_MM` (vertical spacing between different aid sets in print layout)

## Build single-file macro (easy import)

If you want one self-contained macro file for FreeCAD import:

```bash
python build_single_macro.py
```

This generates:
- `sanctifiers_aura_aids_macro.py`

You can import/run that one file directly in FreeCAD.

## One-command build (diagrams + macro)

To regenerate diagrams and the single-file macro together:

```bash
python build_all.py
```

This runs, in order:
1. `generate_diagrams.py`
2. `build_single_macro.py`

## Editing for future combinations

Add or edit entries in `AURA_AIDS` inside `aura_config.py`:

- `short_label`: short code used for embossed part IDs.
- `base_diameter_mm`: model base diameter.
- `aura_range_in`: aura distance in inches.
- `ring_thickness_mm`: ring body thickness.
- `center_clearance_radial_mm`: radial clearance around base.
- `spoke_width_mm`: spoke width between ring and center.
- `center_spoke_count`: number of radial spokes.
- `ring_window_count`: number of ring windows.
- `ring_window_ratio`: per-window angular fraction inside each bucket.
- `ring_rail_mm`: preserved inner/outer rail thickness.
- `force_split_segments`: set an integer to override auto segmentation.

Global settings are also in `aura_config.py`:
- Build plate dimensions and margin.
- Handle presets and selected style.
- Connector dimensions and selected fit preset.
- Part label settings and font candidates.

## Notes

- Default handle remains low-profile knob unless changed in config.
- The center clearance default is 1.0mm radial.
- FreeCAD-specific imports (`FreeCAD`, `Part`) are expected to resolve only in FreeCAD runtime.
