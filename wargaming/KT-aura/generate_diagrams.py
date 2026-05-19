"""Generate technical diagrams for Kill Team aura aids.

Usage:
  python generate_diagrams.py [output_dir]

Outputs one 4-step diagram per aura aid configuration.
"""

import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from aura_config import (  # noqa: E402
    AURA_AIDS,
    BUILD_PLATE_MARGIN_MM,
    BUILD_PLATE_X_MM,
    BUILD_PLATE_Y_MM,
    CONNECTOR,
    ENABLE_PART_LABELS,
    HANDLE,
    HANDLE_STYLE,
    MM_PER_INCH,
)


def _aura_mm(aura_in):
    return aura_in * MM_PER_INCH


def _outer_r(spec):
    return (spec.base_diameter_mm / 2.0) + _aura_mm(spec.aura_range_in)


def _inner_r(spec):
    return (spec.base_diameter_mm / 2.0) + spec.center_clearance_radial_mm


def _chord_length(radius, segment_count):
    return 2.0 * radius * math.sin(math.pi / segment_count)


def _segment_count_for_plate(outer_radius):
    max_span = min(BUILD_PLATE_X_MM, BUILD_PLATE_Y_MM) - (2.0 * BUILD_PLATE_MARGIN_MM)
    if (2.0 * outer_radius) <= max_span:
        return 1

    for n in range(2, 25):
        if _chord_length(outer_radius, n) <= max_span:
            return n
    raise ValueError("Could not find segment count <= 24")


def _safe_name(name):
    return "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in name)


def _draw_open_ring_windows(ax, cx, cy, inner_r, outer_r, window_count, window_ratio, rail_mm, color="white"):
    window_inner = inner_r + rail_mm
    window_outer = outer_r - rail_mm
    if window_count <= 0 or window_ratio <= 0 or window_outer <= window_inner:
        return

    bucket = 360.0 / window_count
    window_angle = bucket * min(max(window_ratio, 0.0), 0.95)
    for i in range(window_count):
        mid = i * bucket
        theta1 = mid - (window_angle / 2.0)
        theta2 = mid + (window_angle / 2.0)
        ax.add_patch(
            mpatches.Wedge(
                (cx, cy),
                window_outer,
                theta1,
                theta2,
                width=(window_outer - window_inner),
                facecolor=color,
                edgecolor=color,
                linewidth=0.0,
                zorder=3,
            )
        )


def _draw_step_1(ax, spec, inner_r, outer_r):
    ax.set_title("Step 1: Aura Geometry", fontsize=10, fontweight="bold")

    outer = mpatches.Circle((0, 0), outer_r, fill=False, linewidth=2.0, edgecolor="#1b5e20")
    ring_fill = mpatches.Wedge((0, 0), outer_r, 0, 360, width=(outer_r - inner_r), facecolor="#dcedc8", edgecolor="none", zorder=1)
    base = mpatches.Circle((0, 0), spec.base_diameter_mm / 2.0, fill=False, linewidth=1.5, edgecolor="#0d47a1")
    center_clear = mpatches.Circle((0, 0), inner_r, fill=False, linewidth=1.0, edgecolor="#6d4c41", linestyle="--")

    ax.add_patch(ring_fill)
    _draw_open_ring_windows(
        ax,
        0,
        0,
        inner_r,
        outer_r,
        spec.ring_window_count,
        spec.ring_window_ratio,
        spec.ring_rail_mm,
    )
    ax.add_patch(outer)
    ax.add_patch(base)
    ax.add_patch(center_clear)

    ax.annotate(
        f"Aura range = {spec.aura_range_in:.1f} in ({_aura_mm(spec.aura_range_in):.1f} mm)",
        xy=(outer_r, 0),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=8,
        color="#1b5e20",
    )
    ax.annotate(
        f"Base = {spec.base_diameter_mm:.1f} mm",
        xy=(spec.base_diameter_mm / 2.0, 0),
        xytext=(10, -18),
        textcoords="offset points",
        fontsize=8,
        color="#0d47a1",
    )
    ax.annotate(
        f"Open ring: {spec.ring_window_count} windows, rail {spec.ring_rail_mm:.1f} mm",
        xy=(0, -outer_r),
        xytext=(10, -10),
        textcoords="offset points",
        fontsize=8,
        color="#33691e",
    )

    lim = outer_r + 20
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.grid(False)
    ax.set_xlabel("mm")
    ax.set_ylabel("mm")


def _draw_step_2(ax, outer_r, segment_count):
    ax.set_title("Step 2: Plate Fit / Segmentation", fontsize=10, fontweight="bold")

    max_span = min(BUILD_PLATE_X_MM, BUILD_PLATE_Y_MM) - (2.0 * BUILD_PLATE_MARGIN_MM)
    full_d = 2.0 * outer_r
    chord = _chord_length(outer_r, segment_count)

    rows = [
        f"Build plate: {BUILD_PLATE_X_MM:.0f} x {BUILD_PLATE_Y_MM:.0f} mm",
        f"Usable span: {max_span:.1f} mm (margin {BUILD_PLATE_MARGIN_MM:.1f} mm per side)",
        f"Full outer diameter: {full_d:.1f} mm",
        f"Selected segments: {segment_count}",
        f"Segment chord: {chord:.1f} mm",
        f"Assembly: {CONNECTOR.assembly_style}",
        f"Fit preset: {CONNECTOR.fit_preset}",
        f"Handle preset: {HANDLE_STYLE}",
        f"Part labels: {'on' if ENABLE_PART_LABELS else 'off'}",
    ]

    box = mpatches.FancyBboxPatch(
        (0.05, 0.15),
        0.9,
        0.72,
        boxstyle="round,pad=0.02",
        transform=ax.transAxes,
        linewidth=1.2,
        edgecolor="#555",
        facecolor="#f7f7f7",
    )
    ax.add_patch(box)

    y = 0.86
    for row in rows:
        ax.text(0.09, y, row, transform=ax.transAxes, fontsize=8.3, va="top")
        y -= 0.085

    status = "Single piece fits" if segment_count == 1 else "Split required for print"
    color = "#2e7d32" if segment_count == 1 else "#c62828"
    ax.text(0.09, 0.08, status, transform=ax.transAxes, fontsize=9.5, fontweight="bold", color=color)

    ax.set_axis_off()


def _draw_step_3(ax, spec, inner_r, outer_r, segment_count):
    ax.set_title("Step 3: Top View Build Pieces", fontsize=10, fontweight="bold")

    plate = mpatches.Rectangle((0, 0), BUILD_PLATE_X_MM, BUILD_PLATE_Y_MM, fill=False, linewidth=1.6, edgecolor="#333")
    ax.add_patch(plate)

    if segment_count == 1:
        cx = BUILD_PLATE_X_MM / 2.0
        cy = BUILD_PLATE_Y_MM / 2.0
        scale = (BUILD_PLATE_X_MM - 2 * BUILD_PLATE_MARGIN_MM) / (2.0 * outer_r)
        draw_outer_r = outer_r * scale
        draw_inner_r = inner_r * scale

        ax.add_patch(mpatches.Wedge((cx, cy), draw_outer_r, 0, 360, width=(draw_outer_r - draw_inner_r), facecolor="#dcedc8", edgecolor="#1b5e20", linewidth=1.2))
        _draw_open_ring_windows(
            ax,
            cx,
            cy,
            draw_inner_r,
            draw_outer_r,
            spec.ring_window_count,
            spec.ring_window_ratio,
            spec.ring_rail_mm * scale,
            color="white",
        )

        spoke_count = max(3, spec.center_spoke_count)
        for i in range(spoke_count):
            ang = math.radians(i * (360.0 / spoke_count))
            x0 = cx + HANDLE.hub_radius_mm * scale * math.cos(ang)
            y0 = cy + HANDLE.hub_radius_mm * scale * math.sin(ang)
            x1 = cx + draw_inner_r * math.cos(ang)
            y1 = cy + draw_inner_r * math.sin(ang)
            ax.plot([x0, x1], [y0, y1], color="#0d47a1", linewidth=1.0)

        ax.text(cx, cy, f"{spec.short_label}\nP1", ha="center", va="center", fontsize=8)
    else:
        seg_angle = 360.0 / segment_count
        cx = BUILD_PLATE_X_MM / 2.0
        cy = BUILD_PLATE_Y_MM / 2.0
        scale = 0.72 * (BUILD_PLATE_X_MM / (2.0 * outer_r))

        for i in range(segment_count):
            theta1 = i * seg_angle
            theta2 = (i + 1) * seg_angle
            wedge = mpatches.Wedge(
                (cx, cy),
                outer_r * scale,
                theta1,
                theta2,
                width=(outer_r - inner_r) * scale,
                fill=False,
                linewidth=1.1,
                edgecolor="#1b5e20",
            )
            ax.add_patch(wedge)

            mid = math.radians((theta1 + theta2) / 2.0)
            x0 = cx + HANDLE.hub_radius_mm * scale * math.cos(mid)
            y0 = cy + HANDLE.hub_radius_mm * scale * math.sin(mid)
            x1 = cx + inner_r * scale * math.cos(mid)
            y1 = cy + inner_r * scale * math.sin(mid)
            ax.plot([x0, x1], [y0, y1], color="#0d47a1", linewidth=1.0)

        ax.add_patch(mpatches.Circle((cx, cy), HANDLE.hub_radius_mm * scale, fill=False, linewidth=1.1, edgecolor="#6d4c41"))
        ax.text(cx, cy, f"{spec.short_label}-H\n+{segment_count} tabs", ha="center", va="center", fontsize=7.2)

    ax.text(6, BUILD_PLATE_Y_MM + 4, f"{spec.name}", fontsize=8.5, va="bottom")
    ax.set_xlim(-5, BUILD_PLATE_X_MM + 5)
    ax.set_ylim(-5, BUILD_PLATE_Y_MM + 15)
    ax.set_aspect("equal")
    ax.grid(False)
    ax.set_xlabel("plate X (mm)")
    ax.set_ylabel("plate Y (mm)")


def _draw_step_4(ax, spec):
    ax.set_title("Step 4: Side Profile", fontsize=10, fontweight="bold")

    ring_t = spec.ring_thickness_mm
    hub_t = HANDLE.hub_thickness_mm
    knob_h = HANDLE.knob_height_mm

    ax.add_patch(mpatches.Rectangle((0, 0), 44, ring_t, linewidth=1.2, edgecolor="#1b5e20", facecolor="#e8f5e9"))
    ax.add_patch(mpatches.Rectangle((16, 0), 12, hub_t, linewidth=1.2, edgecolor="#6d4c41", facecolor="#efebe9"))

    if HANDLE.style == "loop_handle":
        ax.add_patch(mpatches.Rectangle((19, hub_t + 1.0), 6, 10, linewidth=1.2, edgecolor="#6d4c41", facecolor="#d7ccc8"))
        ax.text(31, hub_t + 8.0, "loop", fontsize=8)
    elif HANDLE.style == "t_bar":
        ax.add_patch(mpatches.Rectangle((21, hub_t), 2, 11, linewidth=1.2, edgecolor="#6d4c41", facecolor="#d7ccc8"))
        ax.add_patch(mpatches.Rectangle((16, hub_t + 11), 12, 3, linewidth=1.2, edgecolor="#6d4c41", facecolor="#bcaaa4"))
        ax.text(31, hub_t + 12.5, "t-bar", fontsize=8)
    else:
        ax.add_patch(
            mpatches.Rectangle(
                (19, hub_t),
                6,
                knob_h,
                linewidth=1.2,
                edgecolor="#6d4c41",
                facecolor="#d7ccc8",
            )
        )
        ax.text(31, hub_t + 8.0, "knob", fontsize=8)

    ax.annotate("ring", xy=(43, ring_t), xytext=(48, ring_t + 1.2), fontsize=8)
    ax.annotate(f"{ring_t:.1f} mm", xy=(22, ring_t / 2.0), xytext=(2, 3.8), fontsize=8)
    ax.annotate(f"hub {hub_t:.1f} mm", xy=(28, hub_t), xytext=(30, hub_t + 2.0), fontsize=8)
    ax.annotate(f"handle style: {HANDLE.style}", xy=(25, hub_t + knob_h), xytext=(31, hub_t + knob_h + 1.5), fontsize=8)

    ax.set_xlim(-2, 62)
    ax.set_ylim(-1, hub_t + knob_h + 5)
    ax.grid(False)
    ax.set_xlabel("profile width (mm)")
    ax.set_ylabel("height (mm)")


def generate_one(spec, out_dir):
    inner_r = _inner_r(spec)
    outer_r = _outer_r(spec)
    segment_count = spec.force_split_segments or _segment_count_for_plate(outer_r)

    fig, axs = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle(
        f"Kill Team Aura Aid: {spec.name}\n"
        f"Base {spec.base_diameter_mm:.1f}mm, Aura {spec.aura_range_in:.1f}in, "
        f"Outer Diameter {2 * outer_r:.1f}mm",
        fontsize=12,
        fontweight="bold",
    )

    _draw_step_1(axs[0, 0], spec, inner_r, outer_r)
    _draw_step_2(axs[0, 1], outer_r, segment_count)
    _draw_step_3(axs[1, 0], spec, inner_r, outer_r, segment_count)
    _draw_step_4(axs[1, 1], spec)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    output_name = f"diagram_steps_{_safe_name(spec.name)}.png"
    output_path = os.path.join(out_dir, output_name)
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {output_path}")


def main():
    if len(sys.argv) > 1:
        out_dir = os.path.abspath(sys.argv[1])
    else:
        out_dir = SCRIPT_DIR

    os.makedirs(out_dir, exist_ok=True)

    for spec in AURA_AIDS:
        generate_one(spec, out_dir)

    print("All aura diagrams generated successfully.")


if __name__ == "__main__":
    main()
