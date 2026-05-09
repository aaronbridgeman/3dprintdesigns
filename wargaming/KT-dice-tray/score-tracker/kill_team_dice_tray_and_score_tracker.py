import FreeCAD as App
import Part
import os

# Create a new document
doc = App.newDocument("KillTeamDiceTrayAndScoreTracker")

# --- Dimensions ---
wall        = 2.5     # Outer walls (optimal for 3D printing durability)
right_wall  = 2.5     # Right outer wall (consistent with left for structural integrity)
label_ledge = 9.0     # P1-side label area for crit/normal

# Die slot geometry
die_slot_w  = 16.0    # Each die slot width — fits 16mm dice
slot_div    = 1.0     # Thin raised divider between die slots
n_dice      = 4       # Dice per crits/normals tray

# Section Y-depths
slot_d      = 16.0    # Y-depth of each normals/crits tray (reduced by 1mm for tighter fit)
roll_cut_h  = 18.0    # Rolling arena cut depth (2mm shallower for easier pickup)
base_h      = 23.0    # Total tray height (3mm floor under rolling cut, optimized for material savings)

# Cut heights (Z, downward from top)
slot_cut_h  = 8.0     # Normals/crits die slots (2mm shallower for easier dice pickup)
score_cut_h = 8.0     # Score strip die slots (2mm shallower for easier dice pickup)

# Parametric label text (optional, printable geometry)
add_parametric_labels = True

# Text is built inside recessed label zones and raised back up for accent-color printing.
text_font_size = 5.0
text_raise_h = 0.5        # Raise text to flush with box top (= label_zone_extra_d, no outer recess)
text_padding_x = 0.8      # Keep text clear of zone side walls
text_padding_y = 0.8      # Keep text clear of zone top/bottom walls

# macOS default candidates; first existing path is used.
text_font_candidates = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]

# Accent zones for color filling (optional)
add_accent_zones    = True
outer_border_w      = 1.0    # Raised outer rim width (unused when outer_recess_d = 0)
outer_recess_d      = 0.0    # Outer border recess removed; interior flush with box top
label_zone_extra_d  = 0.5    # Recess in label zones for second accent color
score_label_clearance = 1.0  # Keep score-label recess 1mm clear of neighboring features on each side

# Exterior finishing
outer_corner_radius = 1.5    # Small fillet on outer vertical corners

# Additional material-saving features
add_material_savers = True

# 1) Bottom relief under the rolling arena (keeps a controlled skin thickness)
rolling_floor_relief_inset = 4.0
rolling_floor_relief_depth = 2.5

# 2) Thin the long outer side walls over the central span (leave corners thick)
long_edge_relief_depth = 0.5   # 2.5mm -> ~2.0mm where relief is applied
long_edge_relief_margin = 10.0 # Keep thicker wall near both ends for strength

# 4) Convert selected full-height dividers to partial-height dividers
add_partial_height_dividers = True
partial_divider_height = 11.0  # Remaining height for norm/crit row dividers above build plate
score_divider_height   = base_h * 0.5  # Half-height score-box inter-slot dividers

# --- Score strip (right side, aligned with outer dice rows) ---
# Single column, 12 stacked slots with reduced clearance:
# P1 side (top): CP | TEAM | CRIT | TAC | KILL | TP/INI P1
# P2 side (bot): TP/INI P2 | KILL | TAC | CRIT | TEAM | CP
n_score      = 12
score_slot_w = 14.0    # Reduced by 1mm per side in X for tighter score boxes
score_slot_d = 15.0    # Reduced by 1mm per side in Y for tighter score boxes
score_full_depth = True
score_buffer = 0.0     # No buffer: crits rows align directly with score rows
score_label_zone = 10.0 # Unified label area between dice and score tracker

# X layout: wall + ledge + dice + score_label_zone + score_slot + right_wall
dice_w       = n_dice * die_slot_w + (n_dice - 1) * slot_div   # 4*16 + 3*1 = 67mm
score_strip_x = wall + label_ledge + dice_w + score_label_zone   # x = 93mm
width        = score_strip_x + score_slot_w + right_wall
# score strip occupies x=score_strip_x..(score_strip_x + score_slot_w)

# Rolling area: from x=wall to just before the score label zone
roll_w = label_ledge + dice_w   # 12 + 67 = 79mm

# Score-tracker span drives overall tray depth.
score_span_d = n_score * score_slot_d + (n_score - 1) * slot_div
score_buffer = 0.0     # No buffer: crits rows align directly with score rows
total_depth = score_span_d + (2 * score_buffer) + (2 * wall)

# Rolling area depth is derived from the reduced overall depth.
roll_d = total_depth - (4 * slot_d + 6 * wall)
if roll_d <= 0:
    raise ValueError("Computed rolling-area depth is non-positive; adjust slot dimensions.")

# 1. Create the Main Body
base = Part.makeBox(width, total_depth, base_h)


def apply_outer_corner_rounding():
    global base
    if outer_corner_radius <= 0:
        return

    tol = 1e-6
    outer_vertical_edges = []

    for edge in base.Edges:
        v1 = edge.Vertexes[0].Point
        v2 = edge.Vertexes[1].Point

        # Vertical edge: same x/y, spans full body height in z.
        is_vertical = (abs(v1.x - v2.x) < tol) and (abs(v1.y - v2.y) < tol) and (abs(abs(v1.z - v2.z) - base_h) < tol)
        if not is_vertical:
            continue

        x_ok = (abs(v1.x - 0.0) < tol) or (abs(v1.x - width) < tol)
        y_ok = (abs(v1.y - 0.0) < tol) or (abs(v1.y - total_depth) < tol)
        if x_ok and y_ok:
            outer_vertical_edges.append(edge)

    if outer_vertical_edges:
        base = base.makeFillet(outer_corner_radius, outer_vertical_edges)

# --- Helper: cut a single rectangular box from the top ---
def _cut_box(x, y, z_from_top, bx, by, bz):
    global base
    cutout = Part.makeBox(bx, by, bz)
    cutout.translate(App.Vector(x, y, base_h - z_from_top + 0.01))
    base = base.cut(cutout)


def _top_recess(x, y, bx, by, depth):
    _cut_box(x, y, depth, bx, by, depth)


def _cut_box_from_bottom(x, y, bx, by, bz):
    global base
    cutout = Part.makeBox(bx, by, bz)
    cutout.translate(App.Vector(x, y, -0.01))
    base = base.cut(cutout)


def _resolve_font_path():
    for font_path in text_font_candidates:
        if os.path.exists(font_path):
            return font_path
    return None


def _make_shapestring_shape(text, size, rotation_deg, font_path):
    # Import Draft lazily so geometry still builds when text is disabled.
    import Draft

    ss = Draft.make_shapestring(String=text, FontFile=font_path, Size=size, Tracking=0.0)
    ss.Placement = App.Placement(
        App.Vector(0, 0, 0),
        App.Rotation(App.Vector(0, 0, 1), rotation_deg),
    )
    doc.recompute()

    shape = ss.Shape.copy()
    doc.removeObject(ss.Name)

    return shape


def _compute_uniform_text_size(label_specs, max_size, font_path):
    # label_specs entries: (text, zone_w, zone_h, rotation_deg)
    uniform_scale = 1.0

    for text, zone_w, zone_h, rotation_deg in label_specs:
        if zone_w <= 0 or zone_h <= 0:
            continue

        shape = _make_shapestring_shape(text, max_size, rotation_deg, font_path)
        bb = shape.BoundBox
        if bb.XLength <= 0 or bb.YLength <= 0:
            continue

        avail_w = max(zone_w - (2 * text_padding_x), 0.1)
        avail_h = max(zone_h - (2 * text_padding_y), 0.1)
        fit_scale = min(1.0, avail_w / bb.XLength, avail_h / bb.YLength)
        uniform_scale = min(uniform_scale, fit_scale)

    return max_size * uniform_scale


def _build_centered_text_solid(text, zone_x, zone_y, zone_w, zone_h, z, size, rotation_deg, raise_h, font_path):
    if zone_w <= 0 or zone_h <= 0:
        return None

    shape = _make_shapestring_shape(text, size, rotation_deg, font_path)
    bb = shape.BoundBox
    if bb.XLength <= 0 or bb.YLength <= 0:
        return None

    # Center the text shape inside the target zone.
    tx = zone_x + (zone_w - bb.XLength) / 2.0 - bb.XMin
    ty = zone_y + (zone_h - bb.YLength) / 2.0 - bb.YMin
    shape.translate(App.Vector(tx, ty, z))

    faces = list(shape.Faces)

    if not faces:
        return None

    solids = [face.extrude(App.Vector(0, 0, raise_h)) for face in faces]
    return Part.makeCompound(solids)


def apply_parametric_labels():
    global base

    if not add_parametric_labels:
        return

    font_path = _resolve_font_path()
    if not font_path:
        App.Console.PrintWarning("No valid font file found for parametric labels; skipping text geometry.\n")
        return

    # Row anchors (Y) reused for label placement.
    p1_crits_y = wall
    p1_normals_y = p1_crits_y + slot_d + wall
    roll_y = p1_normals_y + slot_d + wall
    p2_normals_y = roll_y + roll_d + wall
    p2_crits_y = p2_normals_y + slot_d + wall

    # Top level of the recessed label zones.
    label_zone_top_z = base_h - (outer_recess_d + label_zone_extra_d)

    # P1/P2 tray labels.
    p1_label_x = wall
    p2_label_x = wall + dice_w
    p1_specs = [
        ("CRIT", p1_label_x, p1_crits_y, -90.0),
        ("NORM", p1_label_x, p1_normals_y, -90.0),
    ]
    p2_specs = [
        ("NORM", p2_label_x, p2_normals_y, 90.0),
        ("CRIT", p2_label_x, p2_crits_y, 90.0),
    ]

    # Score-label text: one label per score box in the score-label zone.
    score_label_x = score_strip_x - score_label_zone
    score_label_recess_x = score_label_x + score_label_clearance
    score_label_recess_w = score_label_zone - (2 * score_label_clearance)
    if score_label_recess_w <= 0:
        return

    score_labels = [
        "CP", "TEAM", "CRIT", "TAC", "KILL", "TP/INI",
        "TP/INI", "KILL", "TAC", "CRIT", "TEAM", "CP",
    ]

    # Compute one shared text size that fits every label zone.
    uniform_label_specs = [
        ("CRIT", label_ledge, slot_d, -90.0),
        ("NORM", label_ledge, slot_d, -90.0),
        ("NORM", label_ledge, slot_d, 90.0),
        ("CRIT", label_ledge, slot_d, 90.0),
    ]
    for txt in score_labels[:min(n_score, len(score_labels))]:
        uniform_label_specs.append((txt, score_label_recess_w, score_slot_d, 90.0))

    uniform_text_size = _compute_uniform_text_size(uniform_label_specs, text_font_size, font_path)

    for text, zone_x, zone_y, rotation_deg in p1_specs + p2_specs:
        solid = _build_centered_text_solid(
            text=text,
            zone_x=zone_x,
            zone_y=zone_y,
            zone_w=label_ledge,
            zone_h=slot_d,
            z=label_zone_top_z,
            size=uniform_text_size,
            rotation_deg=rotation_deg,
            raise_h=text_raise_h,
            font_path=font_path,
        )
        if solid is not None:
            base = base.fuse(solid)

    score_label_z = label_zone_top_z
    y_pos = wall + score_buffer

    for i in range(min(n_score, len(score_labels))):
        text = score_labels[i]
        solid = _build_centered_text_solid(
            text=text,
            zone_x=score_label_recess_x,
            zone_y=y_pos,
            zone_w=score_label_recess_w,
            zone_h=score_slot_d,
            z=score_label_z,
            size=uniform_text_size,
            rotation_deg=90.0,
            raise_h=text_raise_h,
            font_path=font_path,
        )
        if solid is not None:
            base = base.fuse(solid)
        y_pos += score_slot_d + slot_div


def apply_accent_zones():
    if not add_accent_zones:
        return

    # 1) Outer accent border: recess the full interior from the top, leaving a 1mm raised perimeter.
    if outer_recess_d > 0:
        _top_recess(
            outer_border_w,
            outer_border_w,
            width - (2 * outer_border_w),
            total_depth - (2 * outer_border_w),
            outer_recess_d,
        )

    # Row anchors (Y) for label-zone accents.
    p1_crits_y = wall
    p1_normals_y = p1_crits_y + slot_d + wall
    roll_y = p1_normals_y + slot_d + wall
    p2_normals_y = roll_y + roll_d + wall
    p2_crits_y = p2_normals_y + slot_d + wall

    # 2) Score label accent zone with side clearances from dice and score boxes.
    score_label_x = score_strip_x - score_label_zone
    score_label_recess_x = score_label_x + score_label_clearance
    score_label_recess_w = score_label_zone - (2 * score_label_clearance)
    if score_label_recess_w > 0:
        _top_recess(
            score_label_recess_x,
            wall,
            score_label_recess_w,
            total_depth - (2 * wall),
            outer_recess_d + label_zone_extra_d,
        )

    # 3) P1 label zones (left side, both crit/normal rows).
    for y_pos in (p1_crits_y, p1_normals_y):
        _top_recess(
            wall,
            y_pos,
            label_ledge,
            slot_d,
            outer_recess_d + label_zone_extra_d,
        )

    # 4) P2 label zones (to the right of the P2 dice trays, connected to the tray edge).
    p2_dice_x = wall
    p2_label_x = p2_dice_x + dice_w
    for y_pos in (p2_normals_y, p2_crits_y):
        _top_recess(
            p2_label_x,
            y_pos,
            label_ledge,
            slot_d,
            outer_recess_d + label_zone_extra_d,
        )


def apply_material_savers():
    if not add_material_savers:
        return

    # Recompute row anchors for deterministic placement.
    p1_crits_y = wall
    p1_normals_y = p1_crits_y + slot_d + wall
    roll_y = p1_normals_y + slot_d + wall
    p2_normals_y = roll_y + roll_d + wall
    p2_crits_y = p2_normals_y + slot_d + wall

    # 1) Bottom relief pocket under the rolling arena floor.
    relief_w = max(roll_w - (2 * rolling_floor_relief_inset), 0.0)
    relief_d = max(roll_d - (2 * rolling_floor_relief_inset), 0.0)
    if relief_w > 0 and relief_d > 0 and rolling_floor_relief_depth > 0:
        _cut_box_from_bottom(
            wall + rolling_floor_relief_inset,
            roll_y + rolling_floor_relief_inset,
            relief_w,
            relief_d,
            rolling_floor_relief_depth,
        )

    # 2) Long-edge side wall thinning over the center span.
    relief_y = wall + long_edge_relief_margin
    relief_span = total_depth - (2 * wall) - (2 * long_edge_relief_margin)
    if long_edge_relief_depth > 0 and relief_span > 0:
        _cut_box(
            wall - long_edge_relief_depth,
            relief_y,
            base_h,
            long_edge_relief_depth,
            relief_span,
            base_h,
        )
        _cut_box(
            width - right_wall,
            relief_y,
            base_h,
            long_edge_relief_depth,
            relief_span,
            base_h,
        )

    # 4) Lower selected divider walls (between crit/norm rows) to partial height.
    if add_partial_height_dividers and partial_divider_height < base_h:
        top_cut = base_h - partial_divider_height
        divider_x = wall
        divider_w = label_ledge + dice_w
        for divider_y in (p1_crits_y + slot_d, p2_normals_y + slot_d):
            _cut_box(divider_x, divider_y, top_cut, divider_w, wall, top_cut)

    # Score strip inter-box dividers lowered to partial height.
    if add_partial_height_dividers and score_divider_height < base_h:
        score_top_cut = base_h - score_divider_height
        for i in range(n_score - 1):
            div_y = wall + score_slot_d + i * (score_slot_d + slot_div)
            _cut_box(score_strip_x, div_y, score_top_cut, score_slot_w, slot_div, score_top_cut)

# --- Normals/crits tray: single contiguous pocket (no internal dividers) ---
# P1 dice: label ledge on their left (x=4..23), dice from x=23
# P2 dice: label ledge on their left = our right (x=91..110-3=107 is right wall)
#          dice start from x=4, label on right side
def cut_dice_row(y_pos, x_start):
    _cut_box(x_start, y_pos, slot_cut_h, dice_w, slot_d, slot_cut_h)

# --- Rolling area: left portion of the central zone ---
def cut_rolling(y_pos):
    _cut_box(wall, y_pos, roll_cut_h, roll_w, roll_d, roll_cut_h)

# --- Score strip: single column of 11 slots on the right ---
# Symmetric layout (Y order, P1 end at top):
# CP, TEAM, CRIT, TAC, KILL, TP/INI, KILL, TAC, CRIT, TEAM, CP
def cut_score_strip_full_depth():
    # Keep score boxes aligned with outer rows and add end-wall buffer if configured.
    score_start_y = wall + score_buffer

    y = score_start_y
    for _ in range(n_score):
        _cut_box(score_strip_x, y, score_cut_h, score_slot_w, score_slot_d, score_cut_h)
        y += score_slot_d + slot_div

# 2. Apply all cuts (Y: P1 end -> P2 end)
p1_dice_x = wall + label_ledge   # x=23, ledge on P1's left
p2_dice_x = wall                 # x=4,  ledge on P2's right (our right)

apply_outer_corner_rounding()
apply_accent_zones()

current_y = wall

cut_dice_row(current_y, p1_dice_x)    # P1 CRITS
current_y += slot_d + wall

cut_dice_row(current_y, p1_dice_x)    # P1 NORMALS
current_y += slot_d + wall

roll_start_y = current_y
cut_rolling(current_y)                # Rolling area (left portion)
cut_score_strip_full_depth()          # Score strip runs full tray interior depth
current_y += roll_d + wall

cut_dice_row(current_y, p2_dice_x)    # P2 NORMALS
current_y += slot_d + wall

cut_dice_row(current_y, p2_dice_x)    # P2 CRITS

apply_parametric_labels()
apply_material_savers()

# 3. Add to document
part_obj = doc.addObject("Part::Feature", "KillTeamDiceTrayAndScoreTracker")
part_obj.Shape = base

doc.recompute()

Gui.SendMsgToActiveView("ViewFit")
