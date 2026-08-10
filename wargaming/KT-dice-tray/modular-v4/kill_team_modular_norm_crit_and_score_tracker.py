import FreeCAD as App
import Part

# Create document
doc = App.newDocument("KT_Modular_NormCrit_ScoreTracker_v4")

# --- Core dimensions ---
wall = 2.5
base_h = 12.0
module_width = 105.0

# Dice pocket sizes (+1mm from original)
norm_crit_die_d = 17.0
score_die_w = 17.0
score_die_d = 16.0
slot_div = 1.0

# Norm/Crit module (print twice)
label_ledge = 11.0
norm_crit_inner_w = module_width - (2 * wall) - label_ledge
norm_crit_d = 2 * wall + (2 * norm_crit_die_d) + slot_div
row_cut_h = 7.0

# Tracker module (compact Y)
# X columns (left to right): centered main score cluster (left score | center labels | right score)
center_strip_w = 18.0

main_cluster_w = (2 * score_die_w) + center_strip_w
main_cluster_x = (module_width - main_cluster_w) / 2.0
left_score_x = main_cluster_x
center_strip_x = left_score_x + score_die_w
right_score_x = center_strip_x + center_strip_w

if left_score_x < wall or (right_score_x + score_die_w + wall) > module_width:
    raise ValueError("Centered score cluster exceeds module width.")

# Y layout: 6 score rows (KILL, TAC, CRIT, CP, TEAM, INI/TP)
score_labels_top_to_bottom = ["KILL", "TAC", "CRIT", "CP", "TEAM", "INI/TP"]
score_row_count = len(score_labels_top_to_bottom)
score_d = (2 * wall) + (score_row_count * score_die_d) + ((score_row_count - 1) * slot_div)
score_cut_h = 7.0

# Side regions: P1/P2 labels + storage wells, aligned to score-row grid
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
label_cut_h = 0.5
storage_well_cut_h = 7.0

# Left side: P1 label aligned with KILL row, storage well aligned through INI/TP row.
p1_label_x = left_side_x0 + side_padding_x
p1_label_y = kill_y
p1_label_w = side_feature_w
p1_label_h = label_box_h

p1_storage_well_x = left_side_x0 + side_padding_x
p1_storage_well_y = p1_label_y + p1_label_h + side_gap_y
p1_storage_well_w = side_feature_w
p1_storage_well_h = score_field_y_top - p1_storage_well_y

# Right side: P2 label aligned with INI/TP row, storage well aligned through KILL row.
p2_label_x = right_side_x0 + side_padding_x
p2_label_y = ini_tp_y
p2_label_w = side_feature_w
p2_label_h = label_box_h

p2_storage_well_x = right_side_x0 + side_padding_x
p2_storage_well_y = kill_y
p2_storage_well_w = side_feature_w
p2_storage_well_h = p2_label_y - side_gap_y - p2_storage_well_y

# Connector geometry
n_tabs = 2
tab_w = 8.0
tab_h = 4.0
tab_depth = 4.0
connector_clearance = 0.25


def cut_from_top(solid, x, y, cut_h, bx, by, bz):
    cutter = Part.makeBox(bx, by, bz)
    cutter.translate(App.Vector(x, y, base_h - cut_h + 0.01))
    return solid.cut(cutter)


def add_tab(solid, x, y, z, bx, by, bz):
    tab = Part.makeBox(bx, by, bz)
    tab.translate(App.Vector(x, y, z))
    return solid.fuse(tab)


# --- Build Norm/Crit module ---
def build_norm_crit_module():
    piece = Part.makeBox(module_width, norm_crit_d, base_h)

    tray_x = wall + label_ledge
    tray_w = module_width - wall - tray_x

    # Two long open rectangular cuts
    row1_y = wall
    row2_y = wall + norm_crit_die_d + slot_div
    piece = cut_from_top(piece, tray_x, row1_y, row_cut_h, tray_w, norm_crit_die_d, row_cut_h)
    piece = cut_from_top(piece, tray_x, row2_y, row_cut_h, tray_w, norm_crit_die_d, row_cut_h)

    # Side label recesses for rotated NORM/CRIT text (added in slicer/paint)
    ledge_x = wall + 0.4
    ledge_w = max(label_ledge - 0.8, 0.1)
    piece = cut_from_top(piece, ledge_x, row1_y, 1.0, ledge_w, norm_crit_die_d, 1.0)
    piece = cut_from_top(piece, ledge_x, row2_y, 1.0, ledge_w, norm_crit_die_d, 1.0)

    # Female connector slots
    tab_y = wall + norm_crit_die_d - (tab_w / 2.0)
    for i in range(n_tabs):
        x_offset = (i + 1) * (module_width / (n_tabs + 1))
        piece = cut_from_top(
            piece,
            x_offset - tab_depth / 2,
            tab_y,
            tab_h + connector_clearance,
            tab_depth + connector_clearance,
            tab_w + connector_clearance,
            tab_h + connector_clearance,
        )

    return piece


# --- Build Score tracker ---
def build_score_tracker():
    piece = Part.makeBox(module_width, score_d, base_h)

    # Row anchors from top to bottom in Y
    row_y = [wall + i * (score_die_d + slot_div) for i in range(score_row_count)]

    # Left and right score boxes for each category row (including INI/TP as 6th row)
    for y in row_y:
        piece = cut_from_top(piece, left_score_x, y, score_cut_h, score_die_w, score_die_d, score_cut_h)
        piece = cut_from_top(piece, right_score_x, y, score_cut_h, score_die_w, score_die_d, score_cut_h)

    # Shallow center strip recess for rotated labels between paired boxes
    strip_y = wall
    strip_h = (score_row_count * score_die_d) + ((score_row_count - 1) * slot_div)
    piece = cut_from_top(piece, center_strip_x, strip_y, 0.8, center_strip_w, strip_h, 0.8)

    # Left side: P1 label area and storage well
    piece = cut_from_top(piece, p1_label_x, p1_label_y, label_cut_h, p1_label_w, p1_label_h, label_cut_h)
    piece = cut_from_top(piece, p1_storage_well_x, p1_storage_well_y, storage_well_cut_h, p1_storage_well_w, p1_storage_well_h, storage_well_cut_h)

    # Right side: P2 label area and storage well
    piece = cut_from_top(piece, p2_label_x, p2_label_y, label_cut_h, p2_label_w, p2_label_h, label_cut_h)
    piece = cut_from_top(piece, p2_storage_well_x, p2_storage_well_y, storage_well_cut_h, p2_storage_well_w, p2_storage_well_h, storage_well_cut_h)

    # Male tabs top and bottom for stack docking
    for i in range(n_tabs):
        x_offset = (i + 1) * (module_width / (n_tabs + 1))
        piece = add_tab(piece, x_offset - tab_depth / 2, -tab_depth + 0.01, base_h - tab_h, tab_depth, tab_w, tab_h)
        piece = add_tab(piece, x_offset - tab_depth / 2, score_d - 0.01, base_h - tab_h, tab_depth, tab_w, tab_h)

    return piece


norm_crit_piece = build_norm_crit_module()
score_piece = build_score_tracker()


# --- Place modules and assembled preview ---
norm1_obj = doc.addObject("Part::Feature", "NormCritModule_P1")
norm1_obj.Shape = norm_crit_piece

norm2_obj = doc.addObject("Part::Feature", "NormCritModule_P2")
norm2_obj.Shape = norm_crit_piece.copy()

score_obj = doc.addObject("Part::Feature", "ScoreTrackerModule")
score_obj.Shape = score_piece

# Assembled preview stack
norm1_preview = norm_crit_piece.copy()
score_preview = score_piece.copy()
score_preview.translate(App.Vector(0, norm_crit_d, 0))
norm2_preview = norm_crit_piece.copy()
norm2_preview.translate(App.Vector(0, norm_crit_d + score_d, 0))
assembled = norm1_preview.fuse(score_preview).fuse(norm2_preview)

asm_obj = doc.addObject("Part::Feature", "AssembledPreview")
asm_obj.Shape = assembled

# Move standalone modules for export convenience
norm2_obj.Placement = App.Placement(App.Vector(module_width + 20.0, 0, 0), App.Rotation())
score_obj.Placement = App.Placement(App.Vector(module_width + 20.0, norm_crit_d + 20.0, 0), App.Rotation())

# Console summary
App.Console.PrintMessage("Built modular v4: NormCritModule (print 2x), ScoreTrackerModule, AssembledPreview\n")
App.Console.PrintMessage(f"Module width: {module_width:.2f} mm\n")
App.Console.PrintMessage(f"Norm/Crit cuts: 2 x ({norm_crit_inner_w:.2f} x {norm_crit_die_d:.2f}) mm\n")
App.Console.PrintMessage("Norm/Crit labels: NORM top, CRIT bottom (90-degree on side ledge)\n")
App.Console.PrintMessage("Main score lanes + center labels are centered on X axis\n")
App.Console.PrintMessage("Center labels between score pairs: KILL, TAC, CRIT, CP, TEAM, INI/TP\n")
App.Console.PrintMessage(f"Tracker footprint: {module_width:.2f} x {score_d:.2f} mm\n")


doc.recompute()
Gui.SendMsgToActiveView("ViewFit")
