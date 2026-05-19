"""Parametric configuration for Kill Team aura aids.

This file is pure Python so both the FreeCAD macro and the diagram generator
can read the same values.
"""

from dataclasses import dataclass
from typing import Optional

# Printer build plate (Bambu Lab P2S)
BUILD_PLATE_X_MM = 256.0
BUILD_PLATE_Y_MM = 256.0
BUILD_PLATE_MARGIN_MM = 4.0

# Output modes
GENERATE_PRINT_LAYOUT = True
GENERATE_ASSEMBLY_PREVIEW = False
ASSEMBLY_PREVIEW_OFFSET_X_MM = -420.0
ASSEMBLY_PREVIEW_SPACING_Y_MM = 80.0
PRINT_LAYOUT_AID_GAP_Y_MM = 24.0

# Unit conversion
MM_PER_INCH = 25.4


@dataclass(frozen=True)
class HandleSpec:
    style: str = "low_profile_knob"
    hub_radius_mm: float = 9.0
    hub_thickness_mm: float = 3.2
    knob_radius_mm: float = 7.0
    knob_height_mm: float = 11.0
    loop_inner_radius_mm: float = 6.0
    loop_thickness_mm: float = 3.0
    loop_height_mm: float = 14.0
    tbar_length_mm: float = 18.0
    tbar_thickness_mm: float = 4.0
    tbar_post_radius_mm: float = 3.0
    tbar_post_height_mm: float = 11.0


@dataclass(frozen=True)
class ConnectorSpec:
    assembly_style: str = "press_fit_tabs"
    tab_width_mm: float = 5.6
    tab_length_mm: float = 4.2
    tab_clearance_mm: float = 0.25
    fit_preset: str = "medium"


@dataclass(frozen=True)
class AuraAidSpec:
    name: str
    short_label: str
    base_diameter_mm: float
    aura_range_in: float
    ring_thickness_mm: float = 2.4
    center_clearance_radial_mm: float = 1.0
    spoke_width_mm: float = 5.0
    center_spoke_count: int = 6
    ring_window_count: int = 36
    ring_window_ratio: float = 0.62
    ring_rail_mm: float = 1.2
    outer_rail_mm: Optional[float] = None
    force_split_segments: Optional[int] = None


HANDLE_STYLE = "low_profile_knob"

HANDLE_PRESETS = {
    "low_profile_knob": HandleSpec(
        style="low_profile_knob",
        hub_radius_mm=9.0,
        hub_thickness_mm=3.2,
        knob_radius_mm=7.0,
        knob_height_mm=11.0,
    ),
    "loop_handle": HandleSpec(
        style="loop_handle",
        hub_radius_mm=9.0,
        hub_thickness_mm=3.2,
        knob_radius_mm=6.0,
        knob_height_mm=8.0,
        loop_inner_radius_mm=6.5,
        loop_thickness_mm=3.0,
        loop_height_mm=15.0,
    ),
    "t_bar": HandleSpec(
        style="t_bar",
        hub_radius_mm=9.0,
        hub_thickness_mm=3.2,
        knob_radius_mm=6.0,
        knob_height_mm=8.0,
        tbar_length_mm=18.0,
        tbar_thickness_mm=4.0,
        tbar_post_radius_mm=3.0,
        tbar_post_height_mm=11.0,
    ),
}

HANDLE = HANDLE_PRESETS[HANDLE_STYLE]

CONNECTOR_TOLERANCE_PRESETS = {
    "tight": 0.18,
    "medium": 0.25,
    "loose": 0.33,
}

CONNECTOR_FIT_PRESET = "medium"

CONNECTOR = ConnectorSpec(
    assembly_style="press_fit_tabs",
    tab_width_mm=5.6,
    tab_length_mm=4.2,
    tab_clearance_mm=CONNECTOR_TOLERANCE_PRESETS[CONNECTOR_FIT_PRESET],
    fit_preset=CONNECTOR_FIT_PRESET,
)

ENABLE_PART_LABELS = False
PART_LABEL_TEXT_SIZE_MM = 3.2
PART_LABEL_RAISE_MM = 0.5
PART_LABEL_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]

# Requested Sanctifiers aids.
AURA_AIDS: list[AuraAidSpec] = [
    AuraAidSpec(
        name="sanctifiers_aura_6in_32mm_base",
        short_label="S6-32",
        base_diameter_mm=32.0,
        aura_range_in=6.0,
        spoke_width_mm=4.0,
        center_spoke_count=8,
        ring_window_count=48,
        ring_window_ratio=0.72,
        outer_rail_mm=1.6,
        force_split_segments=4,
    ),
    AuraAidSpec(
        name="sanctifiers_aura_3in_25mm_base",
        short_label="S3-25",
        base_diameter_mm=25.0,
        aura_range_in=3.0,
        spoke_width_mm=4.0,
        center_spoke_count=6,
        ring_window_count=30,
        ring_window_ratio=0.70,
        force_split_segments=None,
    ),
]
