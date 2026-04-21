import FreeCAD as App
import Part

# Create a new document
doc = App.newDocument("DeepArenaDiceTray_v3")

# --- Dimensions ---
width       = 110.0   # Fixed width (X axis)
wall        = 2.5     # Outer walls (optimal for 3D printing durability)
right_wall  = 2.5     # Right outer wall (consistent with left for structural integrity)
label_ledge = 12.0    # P1-side label area for crit/normal (12mm zone)

# Die slot geometry
die_slot_w  = 16.0    # Each die slot width — fits 16mm dice
slot_div    = 1.0     # Thin raised divider between die slots
n_dice      = 4       # Dice per crits/normals tray

# Section Y-depths
slot_d      = 17.0    # Y-depth of each normals/crits tray (16mm dice + 0.5mm clearance each side)
roll_cut_h  = 20.0    # Deep rolling arena cut depth
base_h      = 23.0    # Total tray height (3mm floor under rolling cut, optimized for material savings)

# Cut heights (Z, downward from top)
slot_cut_h  = 10.0    # Normals/crits die slots
score_cut_h = 10.0    # Score strip die slots

# Text labeling (optional)
add_text    = False   # Set to True to add engraved reference text (recommended: manual labeling instead)

# Accent zones for color filling (optional)
add_accent_zones    = True
outer_border_w      = 1.0    # Raised outer rim width
outer_recess_d      = 1.0    # Recess depth inside outer rim
label_zone_extra_d  = 0.5    # Extra recess in label zones so they can be a second accent color
score_label_clearance = 1.0  # Keep score-label recess 1mm clear of neighboring features on each side

# Exterior finishing
outer_corner_radius = 1.5    # Small fillet on outer vertical corners

# --- Score strip (right side, aligned with outer dice rows) ---
# Single column, 12 stacked 17mm slots (16mm dice + 0.5mm clearance each side):
# P1 side (top): CP | TEAM | CRIT | TAC | KILL | TP/INI P1
# P2 side (bot): TP/INI P2 | KILL | TAC | CRIT | TEAM | CP
n_score      = 12
score_slot_d = 17.0    # 16mm dice + 0.5mm clearance each side (matches slot_d)
score_full_depth = True
score_buffer = 0.0     # No buffer: crits rows align directly with score rows
score_label_zone = 10.0 # Unified label area between dice and score tracker

# X layout: wall(2.5) + ledge(12) + dice(67) + score_label_zone(10) + score(16) + r_wall(2.5) = 110
dice_w       = n_dice * die_slot_w + (n_dice - 1) * slot_div   # 4*16 + 3*1 = 67mm
score_strip_x = wall + label_ledge + dice_w + score_label_zone   # x = 93mm
# score strip occupies x=93..109, right wall x=109..110

# Rolling area: from x=wall to just before the score label zone
roll_w = label_ledge + dice_w   # 12 + 67 = 79mm

# Score-tracker span drives overall tray depth.
# 12*17 + 11*1 = 215mm score span; + 2*2.5mm walls = 220mm total.
score_span_d = n_score * score_slot_d + (n_score - 1) * slot_div
score_buffer = 0.0     # No buffer: crits rows align directly with score rows
total_depth = score_span_d + (2 * score_buffer) + (2 * wall)

# Rolling area depth is optimized for the new overall depth:
# total_depth = 4*slot_d + roll_d + 6*wall  => roll_d = 220 - 68 - 15 = 137mm
roll_d = 137.0

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


def apply_accent_zones():
    if not add_accent_zones:
        return

    # 1) Outer accent border: recess the full interior from the top, leaving a 1mm raised perimeter.
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
    # Keep each score box at 16mm and add buffer space from each end wall.
    score_start_y = wall + score_buffer

    y = score_start_y
    for _ in range(n_score):
        _cut_box(score_strip_x, y, score_cut_h, die_slot_w, score_slot_d, score_cut_h)
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

# 3. Add to document
part_obj = doc.addObject("Part::Feature", "DeepArenaTray_v3")
part_obj.Shape = base

doc.recompute()

# --- Optional: Add reference text labels (visual only, not engraved) ---
if add_text:
    from Draft import make_text
    import Draft
    
    # P1 label on left side (in label ledge area)
    text_p1 = make_text("P1", placement=App.Placement(App.Vector(6, 10, base_h), App.Rotation()))
    text_p1.FontSize = 3.0
    doc.addObject(text_p1)
    
    # P2 label on left side (in bottom label ledge)
    text_p2 = make_text("P2", placement=App.Placement(App.Vector(6, 207, base_h), App.Rotation()))
    text_p2.FontSize = 3.0
    doc.addObject(text_p2)
    
    # Score strip label on right side
    text_score = make_text("SCORE", placement=App.Placement(App.Vector(95, 8, base_h), App.Rotation()))
    text_score.FontSize = 2.5
    doc.addObject(text_score)

Gui.SendMsgToActiveView("ViewFit")
