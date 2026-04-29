"""
Technical diagram generator for the Kill Team Dice Tray and Score Tracker.
Run this script to produce PNG diagrams for a given version folder.

Usage:
  python generate_diagrams.py [output_dir]

  output_dir  Path to the version folder where PNGs will be saved.
              Defaults to the directory of this script if omitted.

Outputs:
  - diagram_top_view.png    : Top-down plan view
  - diagram_side_section.png: Longitudinal cross-section (Y axis)
  - diagram_end_section.png : End cross-section (X axis)
"""

import sys
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

if len(sys.argv) > 1:
    OUT_DIR = os.path.abspath(sys.argv[1])
else:
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Base dimensions (fixed across all versions) ───────────────────────────────
width      = 110.0
wall       = 4.0
slot_d     = 18.0
roll_d     = 100.0
slot_cut_h = 10.0
roll_cut_h = 20.0
base_h     = 23.0

# ── Read optional overrides from the macro in the target folder ───────────────
label_ledge   = 0.0
score_label_zone = 0.0  # unified label area between dice and score tracker
score_label_ledge = 0.0  # (deprecated - kept for backwards compatibility)
score_d       = 0.0    # >0 → old v3-style score rows at each end
die_slot_w    = 16.0
slot_div      = 1.0
n_dice        = 5      # number of dice per crits/normals tray
n_score       = 0      # >0 → score strip on right side
right_wall    = 4.0
roll_d        = 100.0
score_slot_d  = 16.0   # Y-depth of each score slot
score_gap_w   = 1.0
score_full_depth = 0
score_buffer   = 0.0
outer_corner_radius = 0.0

macro_path = os.path.join(OUT_DIR, "deep_arena_dice_tray.py")
if os.path.exists(macro_path):
    with open(macro_path) as _f:
        for _line in _f:
            for _pat, _key in [
                (r"wall\s*=\s*([0-9.]+)",           "wall"),
                (r"base_h\s*=\s*([0-9.]+)",         "base_h"),
                (r"label_ledge\s*=\s*([0-9.]+)",   "label_ledge"),
                (r"score_label_zone\s*=\s*([0-9.]+)",   "score_label_zone"),
                (r"score_label_ledge\s*=\s*([0-9.]+)",   "score_label_ledge"),
                (r"slot_d\s*=\s*([0-9.]+)",        "slot_d"),
                (r"score_d\s*=\s*([0-9.]+)",       "score_d"),
                (r"die_slot_w\s*=\s*([0-9.]+)",    "die_slot_w"),
                (r"slot_div\s*=\s*([0-9.]+)",       "slot_div"),
                (r"n_dice\s*=\s*([0-9]+)",          "n_dice"),
                (r"n_score\s*=\s*([0-9]+)",         "n_score"),
                (r"right_wall\s*=\s*([0-9.]+)",     "right_wall"),
                (r"roll_d\s*=\s*([0-9.]+)",         "roll_d"),
                (r"score_slot_d\s*=\s*([0-9.]+)",   "score_slot_d"),
                (r"score_gap_w\s*=\s*([0-9.]+)",    "score_gap_w"),
                (r"score_full_depth\s*=\s*(True|False)", "score_full_depth"),
                (r"score_buffer\s*=\s*([0-9.]+)",   "score_buffer"),
                (r"outer_corner_radius\s*=\s*([0-9.]+)", "outer_corner_radius"),
            ]:
                _m = re.match(r"^\s*" + _pat, _line)
                if _m:
                    if _key == "score_full_depth":
                        globals()[_key] = 1 if _m.group(1) == "True" else 0
                    else:
                        globals()[_key] = float(_m.group(1))

n_dice  = int(n_dice)
n_score = int(n_score)
has_score_rows  = score_d > 0          # old v3: score rows at each end
has_score_strip = n_score > 0          # new v3 / v4: score strip on right side
score_full_depth = bool(score_full_depth)

# Recompute roll_d for score-strip versions (it's a derived expression in the macro)
if has_score_strip and (not score_full_depth) and score_slot_d > 0:
    roll_d = n_score * score_slot_d + max(0, n_score - 1) * slot_div

# ── Derived geometry ──────────────────────────────────────────────────────────
dice_w  = n_dice * die_slot_w + max(0, n_dice - 1) * slot_div
slot_w  = width - wall * 2 - label_ledge   # v1/v2 full-width slot
p1_x    = wall + label_ledge
p2_x    = wall

if has_score_rows:
    total_depth = (score_d * 2) + (slot_d * 4) + roll_d + (wall * 8)
    score_cut_w  = die_slot_w * 6 + slot_div * 5
elif has_score_strip and score_full_depth:
    # Score strip drives depth: 2*wall + score_span_d
    score_span_d = n_score * score_slot_d + max(0, n_score - 1) * slot_div
    total_depth = (2 * wall) + score_span_d
    score_cut_w  = 0.0
else:
    total_depth = (slot_d * 4) + roll_d + (wall * 6)
    score_cut_w  = 0.0

# Score strip geometry (single-column symmetric, new v3)
# score_label_zone is the space between rolling area and score boxes for labels
if has_score_strip:
    # Use score_label_zone if present, otherwise fall back to score_gap_w
    label_zone = score_label_zone if score_label_zone > 0 else score_gap_w
    score_strip_x = wall + label_ledge + dice_w + label_zone
    roll_w        = label_ledge + dice_w   # rolling area X-width
else:
    score_strip_x = 0.0
    roll_w        = width - wall * 2

if has_score_strip and score_full_depth:
    score_span_d = n_score * score_slot_d + max(0, n_score - 1) * slot_div
    score_start_y = wall + score_buffer
    score_span_d = 0.0

# ── Score category labels (P1 top → P2 bottom) ───────────────────────────────
# CP | TEAM | CRIT | TAC | KILL | TP/INI P1 | TP/INI P2 | KILL | TAC | CRIT | TEAM | CP
SCORE_LABELS_SYM = [
    "CP", "TEAM", "CRIT", "TAC", "KILL", "TP/INI P1",
    "TP/INI P2", "KILL", "TAC", "CRIT", "TEAM", "CP"
]
_sym_colors = [
    "#a5d6a7", "#81c784", "#66bb6a", "#4caf50", "#388e3c", "#ce93d8",
    "#e1bee7", "#e57373", "#ef9a9a", "#f48fb1", "#f8bbd0", "#fce4ec",
]

# ── Shared helper ─────────────────────────────────────────────────────────────
def dim_arrow(ax, x1, y1, x2, y2, text, fontsize=8):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="<->", color="dimgray", lw=1))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mx, my, text, ha="center", va="center", fontsize=fontsize,
            color="dimgray", bbox=dict(fc="white", ec="none", pad=1))

# ── Build cavity list (main section) ─────────────────────────────────────────
cavities = []
y = wall

if has_score_rows:
    cavities.append(dict(y=y, depth=score_d, cut_h=10.0, label="SCORE\n(P1)",
                         color="#e1bee7", x_start=wall, cut_w=score_cut_w, n_slots=6))
    y += score_d + wall

if has_score_strip:
    for lbl, color in [("CRITS\n(P1)", "#c8e6c9"), ("NORMALS\n(P1)", "#bbdefb")]:
        cavities.append(dict(y=y, depth=slot_d, cut_h=slot_cut_h, label=lbl,
                             color=color, x_start=p1_x, cut_w=dice_w, n_slots=1))
        y += slot_d + wall
else:
    for lbl, color in [("CRITS\n(P1)", "#c8e6c9"), ("NORMALS\n(P1)", "#bbdefb")]:
        cavities.append(dict(y=y, depth=slot_d, cut_h=slot_cut_h, label=lbl,
                             color=color, x_start=p1_x, cut_w=slot_w,
                             n_slots=5 if has_score_rows else 1))
        y += slot_d + wall

roll_start_y = y
cavities.append(dict(y=y, depth=roll_d, cut_h=roll_cut_h, label="ROLLING\nAREA",
                     color="#ffe0b2", x_start=wall, cut_w=roll_w, n_slots=1))
y += roll_d + wall

if has_score_strip:
    for lbl, color in [("NORMALS\n(P2)", "#bbdefb"), ("CRITS\n(P2)", "#c8e6c9")]:
        cavities.append(dict(y=y, depth=slot_d, cut_h=slot_cut_h, label=lbl,
                             color=color, x_start=p2_x, cut_w=dice_w, n_slots=1))
        y += slot_d + wall
else:
    for lbl, color in [("NORMALS\n(P2)", "#bbdefb"), ("CRITS\n(P2)", "#c8e6c9")]:
        cavities.append(dict(y=y, depth=slot_d, cut_h=slot_cut_h, label=lbl,
                             color=color, x_start=p2_x, cut_w=slot_w,
                             n_slots=5 if has_score_rows else 1))
        y += slot_d + wall

if has_score_rows:
    cavities.append(dict(y=y, depth=score_d, cut_h=10.0, label="SCORE\n(P2)",
                         color="#e1bee7", x_start=wall, cut_w=score_cut_w, n_slots=6))


def _draw_dividers(ax, c):
    if c["n_slots"] <= 1:
        return
    x = c["x_start"]
    for i in range(c["n_slots"] - 1):
        x += die_slot_w
        ax.plot([x + slot_div / 2, x + slot_div / 2],
                [c["y"], c["y"] + c["depth"]],
                color="#666", lw=0.8, zorder=3)
        x += slot_div


# ─────────────────────────────────────────────────────────────────────────────
# 1. TOP-DOWN PLAN VIEW
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 16))
ax.set_xlim(-10, width + 40)
ax.set_ylim(-12, total_depth + 22)
ax.set_aspect("equal")
ax.set_title("Kill Team Dice Tray and Score Tracker — Top View (Plan)", fontsize=13, fontweight="bold", pad=12)
ax.set_xlabel("Width  (mm)")
ax.set_ylabel("Depth  (mm)")
ax.tick_params(labelsize=8)

rounding = max(0.0, min(float(outer_corner_radius), width / 2.0, total_depth / 2.0))
if rounding > 0:
    body = mpatches.FancyBboxPatch(
        (0, 0), width, total_depth,
        boxstyle=f"round,pad=0,rounding_size={rounding}",
        linewidth=1.5, edgecolor="black", facecolor="#f5f5f5", zorder=1
    )
else:
    body = mpatches.Rectangle((0, 0), width, total_depth,
                              linewidth=1.5, edgecolor="black", facecolor="#f5f5f5", zorder=1)
ax.add_patch(body)

if rounding > 0:
    # Radius note so subtle fillets are still clear in the technical drawing.
    ax.annotate(
        f"R{rounding:.1f}",
        xy=(rounding, total_depth),
        xytext=(rounding + 10, total_depth - 12),
        fontsize=7,
        color="dimgray",
        bbox=dict(fc="white", ec="none", pad=1),
        arrowprops=dict(arrowstyle="->", color="dimgray", lw=1),
    )

for c in cavities:
    rect = mpatches.Rectangle((c["x_start"], c["y"]), c["cut_w"], c["depth"],
                               linewidth=1, edgecolor="#555", facecolor=c["color"], zorder=2)
    ax.add_patch(rect)
    cx = c["x_start"] + c["cut_w"] / 2
    cy = c["y"] + c["depth"] / 2
    ax.text(cx, cy, c["label"], ha="center", va="center",
            fontsize=8, fontweight="bold", color="#333")
    _draw_dividers(ax, c)

    if label_ledge > 0 and "ROLLING" not in c["label"] and "SCORE" not in c["label"]:
        is_p1 = "(P1)" in c["label"]
        ledge_x = wall if is_p1 else (c["x_start"] + c["cut_w"])
        ledge = mpatches.Rectangle((ledge_x, c["y"]), label_ledge, c["depth"],
                                    linewidth=0.8, edgecolor="#888", facecolor="#eeeeee",
                                    zorder=2, linestyle="--")
        ax.add_patch(ledge)
        lbl_txt = "CRITS" if "CRITS" in c["label"] else "NORMALS"
        ax.text(ledge_x + label_ledge / 2, cy, lbl_txt, ha="center", va="center",
                fontsize=6, color="#777", style="italic", rotation=90)

# ── Score strip: single symmetric column alongside rolling area ──────────────
if has_score_strip:
    sy = score_start_y if score_full_depth else roll_start_y
    labels = SCORE_LABELS_SYM[:n_score]
    for i, lbl in enumerate(labels):
        color = _sym_colors[i] if i < len(_sym_colors) else "#e0e0e0"
        slot_rect = mpatches.Rectangle((score_strip_x, sy), die_slot_w, score_slot_d,
                        linewidth=0.8, edgecolor="#555",
                        facecolor=color, zorder=3)
        ax.add_patch(slot_rect)
        ax.text(score_strip_x + die_slot_w / 2, sy + score_slot_d / 2,
            lbl, ha="center", va="center", fontsize=5.2,
            fontweight="bold", color="#222", rotation=90)
        sy += score_slot_d + slot_div

    # Score strip outline
    strip_h = score_span_d if score_full_depth else (n_score * score_slot_d + (n_score - 1) * slot_div)
    strip_outline = mpatches.Rectangle(
        (score_strip_x, score_start_y if score_full_depth else roll_start_y), die_slot_w, strip_h,
        linewidth=1.2, edgecolor="#444", facecolor="none", zorder=4)
    ax.add_patch(strip_outline)

    # P1/P2 end labels
    top_y = score_start_y if score_full_depth else roll_start_y
    ax.text(score_strip_x + die_slot_w / 2, top_y - 3, "P1 ▶",
            ha="center", va="bottom", fontsize=6, fontweight="bold", color="#388e3c")
    ax.text(score_strip_x + die_slot_w / 2, top_y + strip_h + 2, "◀ P2",
            ha="center", va="top", fontsize=6, fontweight="bold", color="#c62828")

    # Width annotation for score column
    dim_arrow(ax, score_strip_x, total_depth + 18,
              score_strip_x + die_slot_w, total_depth + 18,
              f"score\n{die_slot_w:.0f} mm", fontsize=7)

# Outer dimensions
dim_arrow(ax, 0, total_depth + 10 if not has_score_strip else total_depth + 26,
          width, total_depth + 10 if not has_score_strip else total_depth + 26,
          f"{width:.0f} mm")
dim_arrow(ax, width + 10, 0, width + 10, total_depth, f"{total_depth:.0f} mm")
for c in cavities:
    dim_arrow(ax, width + 22, c["y"], width + 22, c["y"] + c["depth"],
              f"{c['depth']:.0f}", fontsize=7)

ax.annotate("", xy=(wall, -8), xytext=(0, -8),
            arrowprops=dict(arrowstyle="<->", color="dimgray", lw=1))
ax.text(wall / 2, -10, f"wall\n{wall:.0f}", ha="center", va="top", fontsize=7, color="dimgray")

ax.grid(False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "diagram_top_view.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Saved diagram_top_view.png")


# ─────────────────────────────────────────────────────────────────────────────
# 2. LONGITUDINAL CROSS-SECTION
# ─────────────────────────────────────────────────────────────────────────────
fig_w = max(14, total_depth / 10)
fig, ax = plt.subplots(figsize=(fig_w, 6))
ax.set_xlim(-10, total_depth + 28)
ax.set_ylim(-5, base_h + 18)
ax.set_aspect("equal")
ax.set_title("Kill Team Dice Tray and Score Tracker — Longitudinal Cross-Section (Side View)",
             fontsize=13, fontweight="bold", pad=12)
ax.set_xlabel("Depth along tray  (mm)")
ax.set_ylabel("Height  (mm)")
ax.tick_params(labelsize=8)

body = mpatches.Rectangle((0, 0), total_depth, base_h,
                           linewidth=1.5, edgecolor="black", facecolor="#e8e8e8", zorder=1)
ax.add_patch(body)

for c in cavities:
    cut = mpatches.Rectangle((c["y"], base_h - c["cut_h"]), c["depth"], c["cut_h"],
                              linewidth=1, edgecolor="#555", facecolor=c["color"], zorder=2)
    ax.add_patch(cut)
    ax.text(c["y"] + c["depth"] / 2, base_h - c["cut_h"] / 2,
            c["label"].replace("\n", " "), ha="center", va="center",
            fontsize=7, fontweight="bold", color="#333")

# Show score strip in side section (10mm cut, same depth band as rolling area)
if has_score_strip:
    sy = score_start_y if score_full_depth else roll_start_y
    strip_cut_h = 10.0
    labels = SCORE_LABELS_SYM[:n_score]
    for i, lbl in enumerate(labels):
        color = _sym_colors[i] if i < len(_sym_colors) else "#e0e0e0"
        cut = mpatches.Rectangle((sy, base_h - strip_cut_h), score_slot_d, strip_cut_h,
                                  linewidth=0.8, edgecolor="#555",
                                  facecolor=color, zorder=3)
        ax.add_patch(cut)
        ax.text(sy + score_slot_d / 2, base_h - strip_cut_h / 2,
                lbl, ha="center", va="center", fontsize=5.5, color="#222")
        sy += score_slot_d + slot_div

dim_arrow(ax, total_depth + 10, 0, total_depth + 10, base_h, f"h={base_h:.0f} mm")

ra = next(c for c in cavities if "ROLLING" in c["label"])
floor = base_h - ra["cut_h"]
ax.annotate("", xy=(ra["y"] + ra["depth"] / 2, 0),
            xytext=(ra["y"] + ra["depth"] / 2, floor),
            arrowprops=dict(arrowstyle="<->", color="steelblue", lw=1.2))
ax.text(ra["y"] + ra["depth"] / 2 + 2, floor / 2, f"floor\n{floor:.0f} mm",
        ha="left", va="center", fontsize=7, color="steelblue")

ax.annotate("", xy=(ra["y"], base_h + 5), xytext=(ra["y"] + ra["depth"], base_h + 5),
            arrowprops=dict(arrowstyle="<->", color="dimgray", lw=1))
ax.text(ra["y"] + ra["depth"] / 2, base_h + 7,
        f"rolling {ra['depth']:.0f} mm", ha="center", va="bottom", fontsize=7, color="dimgray")

ax.grid(False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "diagram_side_section.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Saved diagram_side_section.png")


# ─────────────────────────────────────────────────────────────────────────────
# 3. END CROSS-SECTION
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 7))
ax.set_xlim(-12, width + 20)
ax.set_ylim(-5, base_h + 38)
ax.set_aspect("equal")
ax.set_title("Kill Team Dice Tray and Score Tracker — End Cross-Section", fontsize=11, fontweight="bold", pad=10)
ax.set_xlabel("Width  (mm)")
ax.set_ylabel("Height  (mm)")
ax.tick_params(labelsize=8)

body = mpatches.Rectangle((0, 0), width, base_h,
                           linewidth=1.5, edgecolor="black", facecolor="#e8e8e8", zorder=1)
ax.add_patch(body)

# Rolling area cut
roll_cut = mpatches.Rectangle(
    (wall, base_h - roll_cut_h), roll_w, roll_cut_h,
    linewidth=1, edgecolor="#555", facecolor="#ffe0b2",
    zorder=2, label=f"Rolling area ({roll_cut_h:.0f} mm deep, {roll_w:.0f} mm wide)")
ax.add_patch(roll_cut)

if has_score_strip:
    # Single score column
    score_col = mpatches.Rectangle(
        (score_strip_x, base_h - 10.0), die_slot_w, 10.0,
        linewidth=1, edgecolor="#555", facecolor="#ce93d8",
        zorder=3, label=f"Score strip ({die_slot_w:.0f} mm, 11 slots)")
    ax.add_patch(score_col)
    # Dimension: score column position
    dim_arrow(ax, score_strip_x, base_h + 24,
              score_strip_x + die_slot_w, base_h + 24,
              f"score\nx={score_strip_x:.0f}..{score_strip_x+die_slot_w:.0f}", fontsize=7)
    # Label ledge
    dim_arrow(ax, wall, base_h + 16, wall + label_ledge, base_h + 16,
              f"ledge {label_ledge:.0f} mm", fontsize=7)
    # Dice area width
    dim_arrow(ax, wall + label_ledge, base_h + 8,
              wall + label_ledge + dice_w, base_h + 8,
              f"dice {dice_w:.0f} mm", fontsize=7)
    # Label clearance gap
    dim_arrow(ax, wall + label_ledge + dice_w, base_h + 32,
              score_strip_x, base_h + 32,
              f"label gap {score_gap_w:.0f} mm", fontsize=7)
else:
    slot_cut = mpatches.Rectangle(
        (p1_x, base_h - slot_cut_h), slot_w, slot_cut_h,
        linewidth=1, edgecolor="#555", facecolor="#c8e6c9",
        zorder=4, label=f"Dice tray slot ({slot_w:.0f} mm wide)")
    ax.add_patch(slot_cut)
    if label_ledge > 0:
        ledge_patch = mpatches.Rectangle(
            (wall, base_h - slot_cut_h), label_ledge, slot_cut_h,
            linewidth=0.8, edgecolor="#888", facecolor="#eeeeee",
            zorder=5, linestyle="--", label=f"Label ledge ({label_ledge:.0f} mm)")
        ax.add_patch(ledge_patch)

# Standard dimension lines
dim_arrow(ax, 0, base_h + 8, width, base_h + 8, f"{width:.0f} mm")
dim_arrow(ax, wall, base_h + 16 if has_score_strip else base_h + 16,
          width - (right_wall if has_score_strip else wall),
          base_h + 16 if has_score_strip else base_h + 16,
          f"interior {width - wall - (right_wall if has_score_strip else wall):.0f} mm")
dim_arrow(ax, width + 8, 0, width + 8, base_h, f"{base_h:.0f} mm")
dim_arrow(ax, -10, base_h - roll_cut_h, -10, base_h, f"{roll_cut_h:.0f}", fontsize=7)

ax.legend(loc="lower right", fontsize=7, framealpha=0.8)
ax.grid(False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "diagram_end_section.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Saved diagram_end_section.png")

print("\nAll diagrams generated successfully.")
