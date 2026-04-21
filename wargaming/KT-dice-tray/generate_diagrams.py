"""
Technical diagram generator for the Deep Arena Dice Tray.
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
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import os

import re

if len(sys.argv) > 1:
    OUT_DIR = os.path.abspath(sys.argv[1])
else:
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Tray dimensions (must match deep_arena_dice_tray.py) ──────────────────────
width      = 110.0
slot_d     = 18.0
roll_d     = 100.0
wall       = 4.0
slot_cut_h = 10.0
roll_cut_h = 20.0
base_h     = 25.0
total_depth = (slot_d * 4) + roll_d + (wall * 6)   # 196 mm

# ── Read optional label_ledge from the macro in the target folder ─────────────
label_ledge = 0.0
macro_path = os.path.join(OUT_DIR, "deep_arena_dice_tray.py")
if os.path.exists(macro_path):
    with open(macro_path) as _f:
        for _line in _f:
            _m = re.match(r"^\s*label_ledge\s*=\s*([0-9.]+)", _line)
            if _m:
                label_ledge = float(_m.group(1))
                break

# Derived slot geometry
slot_w = width - wall * 2 - label_ledge   # cut width for P1/P2 slots
p1_x   = wall + label_ledge               # P1 slot starts after ledge (LHS)
p2_x   = wall                             # P2 slot starts at inner wall (RHS ledge)

# ── Cavity layout along Y ─────────────────────────────────────────────────────
# Each cavity: y, depth, cut_h, label, color, x_start, cut_w
cavities = []
y = wall
for label, depth, cut_h, color, x_start, cw in [
    ("CRITS\n(P1)",   slot_d, slot_cut_h, "#c8e6c9", p1_x, slot_w),
    ("NORMALS\n(P1)", slot_d, slot_cut_h, "#bbdefb", p1_x, slot_w),
    ("ROLLING\nAREA", roll_d, roll_cut_h, "#ffe0b2", wall, width - wall * 2),
    ("NORMALS\n(P2)", slot_d, slot_cut_h, "#bbdefb", p2_x, slot_w),
    ("CRITS\n(P2)",   slot_d, slot_cut_h, "#c8e6c9", p2_x, slot_w),
]:
    cavities.append(dict(y=y, depth=depth, cut_h=cut_h, label=label,
                         color=color, x_start=x_start, cut_w=cw))
    y += depth + wall


# ─────────────────────────────────────────────────────────────────────────────
# 1. TOP-DOWN PLAN VIEW
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 14))
ax.set_xlim(-10, width + 30)
ax.set_ylim(-10, total_depth + 20)
ax.set_aspect("equal")
ax.set_title("Deep Arena Dice Tray — Top View (Plan)", fontsize=13, fontweight="bold", pad=12)
ax.set_xlabel("Width  (mm)")
ax.set_ylabel("Depth  (mm)")
ax.tick_params(labelsize=8)

# Outer body
body = mpatches.Rectangle((0, 0), width, total_depth,
                           linewidth=1.5, edgecolor="black",
                           facecolor="#f5f5f5", zorder=1)
ax.add_patch(body)

# Cavities + optional label ledges
for c in cavities:
    rect = mpatches.Rectangle(
        (c["x_start"], c["y"]),
        c["cut_w"],
        c["depth"],
        linewidth=1, edgecolor="#555",
        facecolor=c["color"], zorder=2
    )
    ax.add_patch(rect)
    cx = c["x_start"] + c["cut_w"] / 2
    cy = c["y"] + c["depth"] / 2
    ax.text(cx, cy, c["label"], ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#333")

    # Draw label ledge strip if present (not rolling area)
    if label_ledge > 0 and "ROLLING" not in c["label"]:
        is_p1 = "(P1)" in c["label"]
        ledge_x = wall if is_p1 else (c["x_start"] + c["cut_w"])
        ledge = mpatches.Rectangle(
            (ledge_x, c["y"]), label_ledge, c["depth"],
            linewidth=0.8, edgecolor="#888",
            facecolor="#eeeeee", zorder=2, linestyle="--"
        )
        ax.add_patch(ledge)
        ledge_label = "CRITS" if "CRITS" in c["label"] else "NORMALS"
        ax.text(ledge_x + label_ledge / 2, cy, ledge_label,
                ha="center", va="center", fontsize=6.5,
                color="#777", style="italic", rotation=90)

# Dimension arrows: width
def dim_arrow(ax, x1, y1, x2, y2, text, offset=(0, 0), fontsize=8):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="<->", color="dimgray", lw=1))
    mx, my = (x1 + x2) / 2 + offset[0], (y1 + y2) / 2 + offset[1]
    ax.text(mx, my, text, ha="center", va="center",
            fontsize=fontsize, color="dimgray",
            bbox=dict(fc="white", ec="none", pad=1))

dim_arrow(ax, 0, total_depth + 8, width, total_depth + 8,
          f"{width:.0f} mm", fontsize=8)
dim_arrow(ax, width + 8, 0, width + 8, total_depth,
          f"{total_depth:.0f} mm", fontsize=8)

# Individual cavity depth labels on the right
for c in cavities:
    dim_arrow(ax, width + 16, c["y"], width + 16, c["y"] + c["depth"],
              f"{c['depth']:.0f}", fontsize=7)

# Wall thickness callout
ax.annotate("", xy=(wall, -6), xytext=(0, -6),
            arrowprops=dict(arrowstyle="<->", color="dimgray", lw=1))
ax.text(wall / 2, -8.5, f"wall\n{wall:.0f} mm",
        ha="center", va="top", fontsize=7, color="dimgray")

ax.grid(False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "diagram_top_view.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Saved diagram_top_view.png")


# ─────────────────────────────────────────────────────────────────────────────
# 2. LONGITUDINAL CROSS-SECTION (cut along Y, looking in from the side)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
ax.set_xlim(-10, total_depth + 25)
ax.set_ylim(-5, base_h + 15)
ax.set_aspect("equal")
ax.set_title("Deep Arena Dice Tray — Longitudinal Cross-Section (Side View)", fontsize=13, fontweight="bold", pad=12)
ax.set_xlabel("Depth along tray  (mm)")
ax.set_ylabel("Height  (mm)")
ax.tick_params(labelsize=8)

# Solid body profile
body = mpatches.Rectangle((0, 0), total_depth, base_h,
                           linewidth=1.5, edgecolor="black",
                           facecolor="#e8e8e8", zorder=1)
ax.add_patch(body)

# Cut cavities (shown as removals from the top)
for c in cavities:
    cut = mpatches.Rectangle(
        (c["y"], base_h - c["cut_h"]),
        c["depth"],
        c["cut_h"],
        linewidth=1, edgecolor="#555",
        facecolor=c["color"], zorder=2
    )
    ax.add_patch(cut)
    ax.text(c["y"] + c["depth"] / 2, base_h - c["cut_h"] / 2,
            c["label"].replace("\n", " "),
            ha="center", va="center", fontsize=7.5, fontweight="bold", color="#333")

# Height dimension arrows on the right
dim_arrow(ax, total_depth + 8, 0, total_depth + 8, base_h,
          f"Total h\n{base_h:.0f} mm", fontsize=8)

# Floor thickness callout for rolling area
ra = next(c for c in cavities if "ROLLING" in c["label"])
floor = base_h - ra["cut_h"]
ax.annotate("", xy=(ra["y"] + ra["depth"] / 2, 0),
            xytext=(ra["y"] + ra["depth"] / 2, floor),
            arrowprops=dict(arrowstyle="<->", color="steelblue", lw=1.2))
ax.text(ra["y"] + ra["depth"] / 2 + 2, floor / 2,
        f"floor\n{floor:.0f} mm",
        ha="left", va="center", fontsize=7, color="steelblue")

# Depth label for rolling cut
ax.annotate("", xy=(ra["y"], base_h + 5), xytext=(ra["y"] + ra["depth"], base_h + 5),
            arrowprops=dict(arrowstyle="<->", color="dimgray", lw=1))
ax.text(ra["y"] + ra["depth"] / 2, base_h + 7,
        f"{ra['depth']:.0f} mm", ha="center", va="bottom", fontsize=7, color="dimgray")

ax.grid(False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "diagram_side_section.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Saved diagram_side_section.png")


# ─────────────────────────────────────────────────────────────────────────────
# 3. END CROSS-SECTION (cut along X, looking from the end)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 6))
ax.set_xlim(-12, width + 20)
ax.set_ylim(-5, base_h + 28)
ax.set_aspect("equal")
ax.set_title("Deep Arena Dice Tray — End Cross-Section\n(Slot trench | solid centre walls shown)", fontsize=11, fontweight="bold", pad=10)
ax.set_xlabel("Width  (mm)")
ax.set_ylabel("Height  (mm)")
ax.tick_params(labelsize=8)

# Outer body
body = mpatches.Rectangle((0, 0), width, base_h,
                           linewidth=1.5, edgecolor="black",
                           facecolor="#e8e8e8", zorder=1)
ax.add_patch(body)

# Show the two cavity profiles: a slot trench (with ledge) and the deep rolling area
# Slot shown as P1 view (ledge on left)
slot_cut = mpatches.Rectangle(
    (p1_x, base_h - slot_cut_h), slot_w, slot_cut_h,
    linewidth=1, edgecolor="#555", facecolor="#c8e6c9",
    zorder=4, label=f"Slot trench ({slot_cut_h:.0f} mm deep, {slot_w:.0f} mm wide)"
)
roll_cut = mpatches.Rectangle(
    (wall, base_h - roll_cut_h), width - wall * 2, roll_cut_h,
    linewidth=1, edgecolor="#555", facecolor="#ffe0b2",
    zorder=2, label=f"Rolling area ({roll_cut_h:.0f} mm deep)"
)
ax.add_patch(slot_cut)
ax.add_patch(roll_cut)

# Draw the ledge strip on LHS (P1 view) if present
if label_ledge > 0:
    ledge_patch = mpatches.Rectangle(
        (wall, base_h - slot_cut_h), label_ledge, slot_cut_h,
        linewidth=0.8, edgecolor="#888", facecolor="#eeeeee",
        zorder=4, linestyle="--", label=f"Label ledge ({label_ledge:.0f} mm)"
    )
    ax.add_patch(ledge_patch)
    dim_arrow(ax, wall, base_h + 14, wall + label_ledge, base_h + 14,
              f"ledge\n{label_ledge:.0f} mm", fontsize=7)

# Dimension: width
dim_arrow(ax, 0, base_h + 8, width, base_h + 8, f"{width:.0f} mm", fontsize=8)
# Interior width
dim_arrow(ax, wall, base_h + 21, width - wall, base_h + 21,
          f"interior {width - wall*2:.0f} mm", fontsize=8)
# Slot cut width
if label_ledge > 0:
    dim_arrow(ax, p1_x, base_h + 8, p1_x + slot_w, base_h + 8,
              f"slot {slot_w:.0f} mm", fontsize=7)
# Wall thickness
dim_arrow(ax, 0, -3, wall, -3, f"wall\n{wall:.0f}", fontsize=7)
# Total height
dim_arrow(ax, width + 8, 0, width + 8, base_h, f"{base_h:.0f} mm", fontsize=8)
# Slot cut depth
dim_arrow(ax, -10, base_h - slot_cut_h, -10, base_h,
          f"{slot_cut_h:.0f}", fontsize=7)
# Rolling cut depth
dim_arrow(ax, -3, base_h - roll_cut_h, -3, base_h,
          f"{roll_cut_h:.0f}", fontsize=7)

ax.legend(loc="lower right", fontsize=7.5, framealpha=0.8)
ax.grid(False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "diagram_end_section.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Saved diagram_end_section.png")

print("\nAll diagrams generated successfully.")
