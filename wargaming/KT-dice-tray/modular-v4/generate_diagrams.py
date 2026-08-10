"""
Diagram generator for modular v4 concept.

Outputs in this folder:
- diagram_top_assembled.png
- diagram_top_norm_crit_module.png
- diagram_top_score_tracker_module.png
- diagram_bridge_key_accessory.png
- diagram_dimensions_summary.png
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Sync with macro values
wall = 2.5
module_width = 105.0
label_ledge = 11.0

norm_crit_die_d = 17.0
score_die_w = 17.0
score_die_d = 16.0
slot_div = 1.0

# Norm/Crit
norm_crit_inner_w = module_width - (2 * wall) - label_ledge
norm_crit_d = 2 * wall + (2 * norm_crit_die_d) + slot_div

# Tracker compact layout - centered main cluster with INI/TP as 6th pair row
center_strip_w = 18.0
main_cluster_w = (2 * score_die_w) + center_strip_w
main_cluster_x = (module_width - main_cluster_w) / 2.0
left_score_x = main_cluster_x
center_strip_x = left_score_x + score_die_w
right_score_x = center_strip_x + center_strip_w

score_labels_top_to_bottom = ["KILL", "TAC", "CRIT", "CP", "TEAM", "INI/TP"]
score_row_count = len(score_labels_top_to_bottom)
score_d = (2 * wall) + (score_row_count * score_die_d) + ((score_row_count - 1) * slot_div)

# Z-axis (height) dimensions
base_h = 12.0
cut_h = 7.0
remaining_base = base_h - cut_h

# Optional bridge-key geometry (for detachable module linking)
bridge_notch_len = 14.0
bridge_notch_half_w = 3.0
bridge_notch_cut_h = 2.2
bridge_key_clearance = 0.2

bridge_key_len = bridge_notch_len - bridge_key_clearance
bridge_key_w = (2.0 * bridge_notch_half_w) - bridge_key_clearance
bridge_key_bar_w = bridge_notch_half_w - (bridge_key_clearance / 2.0)
bridge_key_spine_w = 3.0
bridge_key_h = bridge_notch_cut_h - 0.15

# Side regions: ONE/TWO labels + storage wells, aligned to score-row grid
row_pitch = score_die_d + slot_div
kill_y = wall
ini_tp_y = wall + (score_row_count - 1) * row_pitch
score_field_y_top = score_d - wall

left_side_x0 = wall
left_side_x1 = left_score_x
right_side_x0 = right_score_x + score_die_w
right_side_x1 = module_width - wall

side_padding_x = 2.0
side_gap_y = slot_div
side_feature_w = (left_side_x1 - left_side_x0) - (2 * side_padding_x)
label_box_h = score_die_d
storage_well_cut_h = 7.0

# Left side: ONE label aligned with KILL row, storage well aligned through INI/TP row.
p1_label_x = left_side_x0 + side_padding_x
p1_label_y = kill_y
p1_label_w = side_feature_w
p1_label_h = label_box_h

p1_storage_well_x = left_side_x0 + side_padding_x
p1_storage_well_y = p1_label_y + p1_label_h + side_gap_y
p1_storage_well_w = side_feature_w
p1_storage_well_h = score_field_y_top - p1_storage_well_y

# Right side: TWO label aligned with INI/TP row, storage well aligned through KILL row.
p2_label_x = right_side_x0 + side_padding_x
p2_label_y = ini_tp_y
p2_label_w = side_feature_w
p2_label_h = label_box_h

p2_storage_well_x = right_side_x0 + side_padding_x
p2_storage_well_y = kill_y
p2_storage_well_w = side_feature_w
p2_storage_well_h = p2_label_y - side_gap_y - p2_storage_well_y

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


def draw_norm_crit(ax, x0=0.0, y0=0.0):
    ax.add_patch(mpatches.Rectangle((x0, y0), module_width, norm_crit_d, ec="black", fc="#f3f6fb", lw=1.5))

    # Side ledge and rotated row labels
    ax.add_patch(mpatches.Rectangle((x0 + wall, y0 + wall), label_ledge, norm_crit_d - 2 * wall, ec="#999", fc="#e8e8e8", lw=0.8))

    row1_y = y0 + wall
    row2_y = y0 + wall + norm_crit_die_d + slot_div
    ax.text(x0 + wall + label_ledge / 2, row1_y + norm_crit_die_d / 2, "NORM", ha="center", va="center", fontsize=10, weight="bold", rotation=90)
    ax.text(x0 + wall + label_ledge / 2, row2_y + norm_crit_die_d / 2, "CRIT", ha="center", va="center", fontsize=10, weight="bold", rotation=90)

    # Two long cuts
    tray_x = x0 + wall + label_ledge
    tray_w = module_width - wall - (wall + label_ledge)
    ax.add_patch(mpatches.Rectangle((tray_x, row1_y), tray_w, norm_crit_die_d, ec="#4d4d4d", fc="#cfe4ff", lw=1.2))
    ax.add_patch(mpatches.Rectangle((tray_x, row2_y), tray_w, norm_crit_die_d, ec="#4d4d4d", fc="#cfe4ff", lw=1.2))

    # Optional bridge-key edge notches (underside, shown dashed in top view)
    x_mid = x0 + module_width / 2.0
    y_mid = y0 + norm_crit_d / 2.0
    c = "#b06a2b"
    fc = "#fff4e8"
    ax.add_patch(mpatches.Rectangle((x_mid - bridge_notch_len / 2.0, y0), bridge_notch_len, bridge_notch_half_w, ec=c, fc=fc, lw=1.0, linestyle="--"))
    ax.add_patch(mpatches.Rectangle((x_mid - bridge_notch_len / 2.0, y0 + norm_crit_d - bridge_notch_half_w), bridge_notch_len, bridge_notch_half_w, ec=c, fc=fc, lw=1.0, linestyle="--"))
    ax.add_patch(mpatches.Rectangle((x0, y_mid - bridge_notch_len / 2.0), bridge_notch_half_w, bridge_notch_len, ec=c, fc=fc, lw=1.0, linestyle="--"))
    ax.add_patch(mpatches.Rectangle((x0 + module_width - bridge_notch_half_w, y_mid - bridge_notch_len / 2.0), bridge_notch_half_w, bridge_notch_len, ec=c, fc=fc, lw=1.0, linestyle="--"))


def draw_score(ax, x0=0.0, y0=0.0):
    ax.add_patch(mpatches.Rectangle((x0, y0), module_width, score_d, ec="black", fc="#fff8ef", lw=1.5))

    # Row anchors (top to bottom in view)
    row_y = [y0 + wall + i * (score_die_d + slot_div) for i in range(score_row_count)]

    # Paired score boxes + center rotated labels
    for i, label in enumerate(score_labels_top_to_bottom):
        y = row_y[i]
        ax.add_patch(mpatches.Rectangle((x0 + left_score_x, y), score_die_w, score_die_d, ec="#4d4d4d", fc="#ffd9c2", lw=1.0))
        ax.add_patch(mpatches.Rectangle((x0 + right_score_x, y), score_die_w, score_die_d, ec="#4d4d4d", fc="#ffe7d6", lw=1.0))
        ax.text(x0 + center_strip_x + center_strip_w / 2, y + score_die_d / 2, label, ha="center", va="center", fontsize=10, weight="bold", rotation=90)

    # Left side: ONE label area and storage well
    ax.add_patch(mpatches.Rectangle((x0 + p1_label_x, y0 + p1_label_y), p1_label_w, p1_label_h, ec="#999", fc="#f0f0f0", lw=0.8))
    ax.text(x0 + p1_label_x + p1_label_w / 2, y0 + p1_label_y + p1_label_h / 2, "ONE", ha="center", va="center", fontsize=14, weight="bold", rotation=90)
    ax.add_patch(mpatches.Rectangle((x0 + p1_storage_well_x, y0 + p1_storage_well_y), p1_storage_well_w, p1_storage_well_h, ec="#4d4d4d", fc="#e8f5e8", lw=1.0))

    # Right side: TWO label area and storage well
    ax.add_patch(mpatches.Rectangle((x0 + p2_label_x, y0 + p2_label_y), p2_label_w, p2_label_h, ec="#999", fc="#f0f0f0", lw=0.8))
    ax.text(x0 + p2_label_x + p2_label_w / 2, y0 + p2_label_y + p2_label_h / 2, "TWO", ha="center", va="center", fontsize=14, weight="bold", rotation=90)
    ax.add_patch(mpatches.Rectangle((x0 + p2_storage_well_x, y0 + p2_storage_well_y), p2_storage_well_w, p2_storage_well_h, ec="#4d4d4d", fc="#e8f5e8", lw=1.0))

    # Optional bridge-key edge notches (underside, shown dashed in top view)
    x_mid = x0 + module_width / 2.0
    y_mid = y0 + score_d / 2.0
    c = "#b06a2b"
    fc = "#fff4e8"
    ax.add_patch(mpatches.Rectangle((x_mid - bridge_notch_len / 2.0, y0), bridge_notch_len, bridge_notch_half_w, ec=c, fc=fc, lw=1.0, linestyle="--"))
    ax.add_patch(mpatches.Rectangle((x_mid - bridge_notch_len / 2.0, y0 + score_d - bridge_notch_half_w), bridge_notch_len, bridge_notch_half_w, ec=c, fc=fc, lw=1.0, linestyle="--"))
    ax.add_patch(mpatches.Rectangle((x0, y_mid - bridge_notch_len / 2.0), bridge_notch_half_w, bridge_notch_len, ec=c, fc=fc, lw=1.0, linestyle="--"))
    ax.add_patch(mpatches.Rectangle((x0 + module_width - bridge_notch_half_w, y_mid - bridge_notch_len / 2.0), bridge_notch_half_w, bridge_notch_len, ec=c, fc=fc, lw=1.0, linestyle="--"))


def plot_bridge_key_accessory():
    fig, ax = plt.subplots(figsize=(7.0, 4.2))

    # Top view key body (H-shape)
    x0, y0 = 8.0, 8.0
    ax.add_patch(mpatches.Rectangle((x0, y0), bridge_key_len, bridge_key_bar_w, ec="#222", fc="#f6c47a", lw=1.6))
    ax.add_patch(mpatches.Rectangle((x0, y0 + bridge_key_w - bridge_key_bar_w), bridge_key_len, bridge_key_bar_w, ec="#222", fc="#f6c47a", lw=1.6))
    ax.add_patch(mpatches.Rectangle((x0 + (bridge_key_len - bridge_key_spine_w) / 2.0, y0), bridge_key_spine_w, bridge_key_w, ec="#222", fc="#f1b965", lw=1.6))
    ax.text(x0 + bridge_key_len / 2.0, y0 + bridge_key_w / 2.0, "Bridge Key", ha="center", va="center", fontsize=10, weight="bold")

    # Show mating notch envelope for context
    env_x = x0 + bridge_key_len + 10.0
    env_y = y0
    ax.add_patch(mpatches.Rectangle((env_x, env_y), bridge_notch_len, 2 * bridge_notch_half_w, ec="#8a5a2b", fc="#fff0de", lw=1.0, linestyle="--"))
    ax.text(env_x + bridge_notch_len / 2.0, env_y + bridge_notch_half_w, "Mating\nnotch pair", ha="center", va="center", fontsize=8)

    # Dimension callouts
    ax.text(x0 + bridge_key_len / 2.0, y0 - 2.0, f"L = {bridge_key_len:.1f} mm", ha="center", va="top", fontsize=8)
    ax.text(x0 - 1.5, y0 + bridge_key_w / 2.0, f"W = {bridge_key_w:.1f} mm", ha="right", va="center", fontsize=8, rotation=90)
    ax.text(x0 + bridge_key_len / 2.0, y0 + bridge_key_w + 2.0, f"H = {bridge_key_h:.2f} mm", ha="center", va="bottom", fontsize=8)

    ax.set_title("Optional Accessory - H-Shaped Bridge Key (print 4-8x)")
    ax.set_aspect("equal")
    ax.set_xlim(0, env_x + bridge_notch_len + 8)
    ax.set_ylim(0, y0 + bridge_key_w + 10)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    save(fig, "diagram_bridge_key_accessory.png")


def plot_norm_crit():
    fig, ax = plt.subplots(figsize=(10, 3.8))
    draw_norm_crit(ax)
    ax.text(module_width / 2, -2.8, "Print this piece twice (one per player)", ha="center", fontsize=9, style="italic")
    ax.set_title("Modular v4 - Norm/Crit Module (2 Long Open Rows)")
    ax.set_aspect("equal")
    ax.set_xlim(-5, module_width + 10)
    ax.set_ylim(-4, norm_crit_d + 5)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    save(fig, "diagram_top_norm_crit_module.png")


def plot_score():
    fig, ax = plt.subplots(figsize=(10, 7.2))
    draw_score(ax)
    ax.set_title("Modular v4 - Score Tracker (Centered lanes + larger labels)")
    ax.set_aspect("equal")
    ax.set_xlim(-5, module_width + 10)
    ax.set_ylim(-5, score_d + 8)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    save(fig, "diagram_top_score_tracker_module.png")


def plot_assembled():
    fig, ax = plt.subplots(figsize=(10, 10))
    draw_norm_crit(ax, 0.0, 0.0)
    draw_score(ax, 0.0, norm_crit_d)
    draw_norm_crit(ax, 0.0, norm_crit_d + score_d)

    ax.set_title("Modular v4 - Assembled Vertical Stack")
    ax.set_aspect("equal")
    total_h = norm_crit_d + score_d + norm_crit_d
    ax.set_xlim(-5, module_width + 10)
    ax.set_ylim(-5, total_h + 10)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    save(fig, "diagram_top_assembled.png")


def plot_dimension_summary():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis("off")

    lines = [
        "Modular v4 Dimension Summary",
        "",
        "Layout: Norm/Crit P1 -> Score Tracker -> Norm/Crit P2",
        f"Module width: {module_width:.1f} mm",
        "",
        "Norm/Crit module (print 2x):",
        "  - Two long open cuts (no internal dividers)",
        f"  - Each cut: {norm_crit_inner_w:.1f} x {norm_crit_die_d:.1f} mm",
        "  - Side labels (90 deg): NORM top, CRIT bottom",
        "",
        "Score tracker (with ONE/TWO regions & token storage):",
        "  - Main score lanes + center label strip centered on X axis",
        "  - INI/TP is a 6th paired row (like TEAM, CP, etc.)",
        "  - Center labels between paired boxes (90 deg): KILL, TAC, CRIT, CP, TEAM, INI/TP",
        f"  - Side score box size: {score_die_w:.1f} x {score_die_d:.1f} mm",
        f"  - Tracker footprint: {module_width:.1f} x {score_d:.1f} mm",
        "  - Side regions (aligned to KILL and INI/TP rows):",
        f"    ONE (left): {p1_label_w:.0f}x{p1_label_h:.0f}mm label + storage well ({p1_storage_well_w:.0f}x{p1_storage_well_h:.0f}mm, {storage_well_cut_h:.0f}mm deep)",
        f"    TWO (right): {p2_label_w:.0f}x{p2_label_h:.0f}mm label + storage well ({p2_storage_well_w:.0f}x{p2_storage_well_h:.0f}mm, {storage_well_cut_h:.0f}mm deep)",
        "",
        "Optional bridge-key system:",
        f"  - Underside edge notch per side: {bridge_notch_len:.1f} x {bridge_notch_half_w:.1f} mm, {bridge_notch_cut_h:.1f} mm deep",
        f"  - H-key envelope: {bridge_key_len:.1f} x {bridge_key_w:.1f} x {bridge_key_h:.2f} mm (spine {bridge_key_spine_w:.1f} mm)",
        "  - Recommended quantity: 4-8 keys",
        "",
        f"Assembled stack height: {norm_crit_d + score_d + norm_crit_d:.1f} mm",
    ]

    ax.text(0.03, 0.97, "\n".join(lines), va="top", ha="left", fontsize=9, family="monospace")
    save(fig, "diagram_dimensions_summary.png")


def plot_side_profile():
    """Side view (Z-axis profile) showing module heights and cut depths."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Draw vertical stack (side view looking at Z-axis)
    x_offset = 5
    y_start = 0

    # Three modules stacked vertically
    modules = [
        ("Norm/Crit P1", norm_crit_d),
        ("Score Tracker", score_d),
        ("Norm/Crit P2", norm_crit_d),
    ]

    y_pos = y_start
    colors = ["#cfe4ff", "#ffd9c2", "#cfe4ff"]

    for i, (label, depth) in enumerate(modules):
        # Module outer body
        rect = mpatches.Rectangle((x_offset, y_pos), 20, base_h, ec="black", fc=colors[i], lw=2)
        ax.add_patch(rect)

        # Dice cut depth visualization
        cut_rect = mpatches.Rectangle(
            (x_offset + 1, y_pos + remaining_base),
            18,
            cut_h,
            ec="#ff6b6b",
            fc="#ffcccc",
            lw=1,
            linestyle="--"
        )
        ax.add_patch(cut_rect)

        # Edge notch zone marker (underside cut)
        notch_zone = mpatches.Rectangle((x_offset + 8, y_pos), 4, bridge_notch_cut_h, ec="#8a5a2b", fc="#fff0de", lw=1, linestyle="--")
        ax.add_patch(notch_zone)

        # Labels and dimensions
        ax.text(x_offset + 30, y_pos + base_h / 2, label, va="center", fontsize=10, weight="bold")
        ax.text(x_offset - 1, y_pos + base_h / 2, f"{base_h}mm", va="center", ha="right", fontsize=8)

        # Depth annotation
        ax.text(x_offset + 30, y_pos - 3, f"Depth: {depth:.0f} mm", va="top", fontsize=8, style="italic", color="#666")

        # Cut depth indicator
        ax.annotate(
            "",
            xy=(x_offset + 25, y_pos + remaining_base),
            xytext=(x_offset + 25, y_pos + base_h),
            arrowprops=dict(arrowstyle="<->", color="red", lw=1.5)
        )
        ax.text(x_offset + 27, y_pos + remaining_base + cut_h / 2, f"Cut\n{cut_h:.0f}mm", fontsize=7, color="red", weight="bold")

        y_pos += base_h + 3

    # Legend
    ax.text(x_offset, y_pos + 3, "Legend:", fontsize=9, weight="bold")
    ax.add_patch(mpatches.Rectangle((x_offset, y_pos + 5), 2, 2, ec="black", fc="#cfe4ff", lw=1))
    ax.text(x_offset + 4, y_pos + 6, "Solid base", fontsize=8, va="center")

    ax.add_patch(mpatches.Rectangle((x_offset, y_pos + 10), 2, 2, ec="#ff6b6b", fc="#ffcccc", lw=1, linestyle="--"))
    ax.text(x_offset + 4, y_pos + 11, f"Dice pocket ({cut_h:.0f}mm deep)", fontsize=8, va="center")

    ax.add_patch(mpatches.Rectangle((x_offset, y_pos + 15), 2, 2, ec="#8a5a2b", fc="#fff0de", lw=1, linestyle="--"))
    ax.text(x_offset + 4, y_pos + 16, f"Bridge-notch cut ({bridge_notch_cut_h:.1f}mm deep)", fontsize=8, va="center")

    ax.set_title("Side Profile - Z-Axis (Heights and Cut Depths)", fontsize=12, weight="bold")
    ax.set_aspect("equal")
    ax.set_xlim(0, 80)
    ax.set_ylim(-15, y_pos + 30)
    ax.set_xlabel("(arbitrary side view)")
    ax.set_ylabel("Z-Axis Height (mm)")
    ax.grid(True, alpha=0.2)
    save(fig, "diagram_side_profile_z_axis.png")


if __name__ == "__main__":
    plot_norm_crit()
    plot_score()
    plot_assembled()
    plot_bridge_key_accessory()
    plot_dimension_summary()
    plot_side_profile()
    print("Generated modular-v4 diagrams in:", OUT_DIR)
