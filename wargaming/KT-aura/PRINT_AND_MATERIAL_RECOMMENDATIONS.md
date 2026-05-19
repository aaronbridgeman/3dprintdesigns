# KT Aura Aids: Print + Material Recommendations

This guide targets Bambu Lab P2S printing for:
- segmented 6in aura around 32mm base
- single-piece 3in aura around 25mm base

## Recommended print settings

## 1) General profile

- Nozzle: 0.4mm
- Layer height: 0.20mm (good default)
- First layer height: 0.22mm
- Line width: 0.42mm
- Material: PLA or PETG
- Cooling: standard (high fan for PLA, moderate for PETG)

## 2) Perimeters and top/bottom

- Wall loops/perimeters: 3
- Top layers: 4
- Bottom layers: 4
- Infill: 12% gyroid (mainly for hub/handle volume)

Why: most strength is from perimeters on these thin geometry parts.

## 3) Speed (safe-fit first)

- Outer wall speed: 40 mm/s
- Inner wall speed: 60 mm/s
- Infill speed: 80 mm/s
- First layer speed: 20 mm/s

Why: cleaner tab/slot dimensions and less post-fit tuning.

## 4) Supports

- Ring/spoke segments: supports OFF
- Hub with handle:
  - low-profile knob: supports OFF
  - loop handle: supports ON, build plate only
  - t-bar: supports ON, build plate only

## 5) Orientation

- Segments: flat on bed, spokes upward from bed plane (as generated)
- Hub: flat on bed
- Keep labels up-facing where possible for readability

## 6) Dimensional accuracy for press-fit joints

Start at medium preset (`CONNECTOR_FIT_PRESET = "medium"`).

If tabs are too tight:
- move to `loose`, or
- add XY compensation of -0.02mm to -0.05mm on male features (slicer-dependent)

If tabs are too loose:
- move to `tight`, or
- reduce negative XY compensation

## 7) Material-specific quick notes

PLA:
- best dimensional accuracy
- easiest press-fit dialing

PETG:
- tougher and less brittle
- often needs slightly looser fit (recommend `loose` preset first)

## Practical defaults for your two current aids

## 6in / 32mm segmented aura

- Keep segmentation automatic (already plate-safe)
- Use 0.20mm layers
- Perimeters: 3
- Infill: 12%
- Fit preset: `medium` for PLA, `loose` for PETG

## 3in / 25mm single-piece aura

- Same profile as above
- Consider 0.16mm layers if you want cleaner small text labels

## Material reduction while retaining utility

Yes. You already have the right architecture (open windows + spokes + segmentation). The biggest safe savings are from geometry tuning in config.

## A) Increase openness of ring windows (high impact)

In each `AuraAidSpec`:
- increase `ring_window_ratio` from 0.62 to 0.70-0.78
- increase `ring_window_count` moderately (for smoother look while keeping rails)

Effect:
- less ring material
- better visibility
- slightly lower torsional stiffness (usually acceptable for tabletop aid)

Safe start:
- 6in aid: `ring_window_ratio = 0.72`
- 3in aid: `ring_window_ratio = 0.70`

## B) Reduce ring thickness slightly (medium impact)

- reduce `ring_thickness_mm` from 2.4 to 2.0 (or 1.8 for PLA if careful)

Effect:
- significant mass reduction
- lower bending stiffness

Safe start:
- 2.0mm for both aids

## C) Reduce spoke width/count conservatively (medium impact)

- `spoke_width_mm`: reduce from 5.0 to 4.0
- `center_spoke_count`: keep current values unless you see excess stiffness

Effect:
- lower mass near center
- maintain ring stability if rails are kept healthy

Safe start:
- 6in aid: keep 8 spokes, set width to 4.0mm
- 3in aid: keep 6 spokes, set width to 4.0mm

## D) Keep rail thickness above a minimum (critical for utility)

- do not reduce `ring_rail_mm` below 1.0 with 0.4 nozzle
- recommended range: 1.1-1.4mm

Effect:
- protects ring continuity and accidental flex damage

## E) Handle mass reduction (optional)

If handle feels overbuilt:
- low-profile knob:
  - reduce `knob_height_mm` from 11.0 to 8.5-9.5
  - reduce `knob_radius_mm` from 7.0 to 6.0-6.5

Effect:
- noticeable material/time reduction
- still usable grip for hovering over models

## Suggested lightweight preset to try first

Apply these in `aura_config.py`:

- `ring_thickness_mm = 2.0`
- `spoke_width_mm = 4.0`
- 6in aid:
  - `ring_window_ratio = 0.72`
  - `ring_window_count = 48` (unchanged)
- 3in aid:
  - `ring_window_ratio = 0.70`
  - `ring_window_count = 30` (unchanged)
- Keep `ring_rail_mm = 1.2`

This usually cuts material while keeping practical rigidity.

## Validation loop after changes

1. Run diagrams:
   - `python generate_diagrams.py`
2. Build single macro:
   - `python build_single_macro.py`
3. Print one segment + hub test first (for the 6in aid)
4. If fit is tight/loose, switch connector preset before full print

## If utility starts to drop

Symptoms:
- ring feels floppy
- tabs crack during assembly
- hub wobbles under handle force

Rollback order:
1. increase `ring_thickness_mm`
2. decrease `ring_window_ratio`
3. increase `spoke_width_mm`
4. move connector fit back toward `medium`
