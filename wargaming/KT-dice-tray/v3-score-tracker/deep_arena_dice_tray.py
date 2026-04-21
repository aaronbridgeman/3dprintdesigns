import FreeCAD as App
import Part

# Create a new document
doc = App.newDocument("DeepArenaDiceTray_v3")

# --- Dimensions ---
width       = 110.0   # Fixed width (X axis)
wall        = 4.0     # Left outer wall
right_wall  = 3.0     # Right outer wall (thinner to fit score strip)
label_ledge = 15.0    # P1-side ledge; reduced to preserve 110mm overall width

# Die slot geometry
die_slot_w  = 16.0    # Each die slot width — fits 16mm dice
slot_div    = 1.0     # Thin raised divider between die slots
n_dice      = 4       # Dice per crits/normals tray

# Section Y-depths
slot_d      = 17.0    # Y-depth of each normals/crits tray (16mm dice + 0.5mm clearance each side)
roll_cut_h  = 20.0    # Deep rolling arena cut depth
base_h      = 25.0    # Total tray height (5mm floor under rolling cut)

# Cut heights (Z, downward from top)
slot_cut_h  = 10.0    # Normals/crits die slots
score_cut_h = 10.0    # Score strip die slots

# --- Score strip (right side, aligned with outer dice rows) ---
# Single column, 12 stacked 17mm slots (16mm dice + 0.5mm clearance each side):
# P1 side (top): CP | TEAM | CRIT | TAC | KILL | TP/INI P1
# P2 side (bot): TP/INI P2 | KILL | TAC | CRIT | TEAM | CP
n_score      = 12
score_slot_d = 17.0    # 16mm dice + 0.5mm clearance each side (matches slot_d)
score_full_depth = True
score_buffer = 0.0     # No buffer: crits rows align directly with score rows

# X layout: wall(4) + ledge(15) + dice(67) + label-gap(5) + score(16) + r_wall(3) = 110
dice_w       = n_dice * die_slot_w + (n_dice - 1) * slot_div   # 4*16 + 3*1 = 67mm
score_gap_w  = 5.0   # Clearance between dice area and score strip for labels
score_strip_x = wall + label_ledge + dice_w + score_gap_w        # x = 91mm
# score strip occupies x=91..107, right wall x=107..110

# Rolling area: from x=wall to just before the label clearance gap
roll_w = label_ledge + dice_w   # 15 + 67 = 82mm (x=4..86)

# Score-tracker span drives overall tray depth.
# 12*17 + 11*1 = 215mm score span; + 2*4mm walls = 223mm total.
score_span_d = n_score * score_slot_d + (n_score - 1) * slot_div
score_buffer = 0.0     # No buffer: crits rows align directly with score rows
total_depth = score_span_d + (2 * score_buffer) + (2 * wall)

# Rolling area depth is reduced to fit the new overall depth:
# total_depth = 4*slot_d + roll_d + 6*wall  => roll_d = 223 - 68 - 24 = 131mm
roll_d = 131.0

# 1. Create the Main Body
base = Part.makeBox(width, total_depth, base_h)

# --- Helper: cut a single rectangular box from the top ---
def _cut_box(x, y, z_from_top, bx, by, bz):
    global base
    cutout = Part.makeBox(bx, by, bz)
    cutout.translate(App.Vector(x, y, base_h - z_from_top + 0.01))
    base = base.cut(cutout)

# --- Normals/crits tray: n_dice individual slots with dividers ---
# P1 dice: label ledge on their left (x=4..23), dice from x=23
# P2 dice: label ledge on their left = our right (x=91..110-3=107 is right wall)
#          dice start from x=4, label on right side
def cut_dice_row(y_pos, x_start):
    x = x_start
    for _ in range(n_dice):
        _cut_box(x, y_pos, slot_cut_h, die_slot_w, slot_d, slot_cut_h)
        x += die_slot_w + slot_div

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
Gui.SendMsgToActiveView("ViewFit")
