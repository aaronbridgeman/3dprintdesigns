import FreeCAD as App
import Part
import os

try:
    import Draft
except Exception:
    Draft = None

try:
    import FreeCADGui as Gui
except Exception:
    Gui = None

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

# Y layout: 6 score rows (KILL, TAC, CRIT, CP, TEAM, TP/INI)
score_labels_top_to_bottom = ["KILL", "TAC", "CRIT", "CP", "TEAM", "TP/INI"]
score_row_count = len(score_labels_top_to_bottom)
score_d = (2 * wall) + (score_row_count * score_die_d) + ((score_row_count - 1) * slot_div)
score_cut_h = 7.0

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

# Programmatic text embossing. Every label rises to base_h + text_relief_h.
norm_text_size = 3.4
crit_text_size = 3.4
score_center_text_size = 3.5
side_label_text_size = 4.5
text_relief_h = 0.6

FONT_CANDIDATES = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/Arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]

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


def find_font_file():
    for candidate in FONT_CANDIDATES:
        if os.path.isfile(candidate):
            return candidate
    return None


font_file = find_font_file()
if Draft is None:
    raise RuntimeError("Draft module is required for programmatic labels but could not be imported.")
if font_file is None:
    raise RuntimeError("No usable TTF font found for programmatic labels.")


def cut_from_top(solid, x, y, cut_h, bx, by, bz):
    cutter = Part.makeBox(bx, by, bz)
    cutter.translate(App.Vector(x, y, base_h - cut_h + 0.01))
    return solid.cut(cutter)


def emboss_text_centered(solid, text, center_x, center_y, size, height, rotation_deg=0.0):
    text_obj = Draft.makeShapeString(String=text, FontFile=font_file, Size=size, Tracking=0.0)
    doc.recompute()
    text_shape = text_obj.Shape.copy()
    doc.removeObject(text_obj.Name)

    if text_shape.isNull():
        raise RuntimeError(f"Failed to generate text shape for '{text}'.")

    # Apply rotation first at origin
    if abs(rotation_deg) > 0.001:
        text_shape.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 0, 1), rotation_deg))
    
    # Normalize to positive XY after rotation
    bb_pre = text_shape.BoundBox
    text_shape.translate(App.Vector(-bb_pre.XMin, -bb_pre.YMin, 0))

    # Center on the common module top surface.
    bb = text_shape.BoundBox
    place_x = center_x - (bb.XLength / 2.0)
    place_y = center_y - (bb.YLength / 2.0)
    text_shape.translate(App.Vector(place_x, place_y, base_h))

    # Extrude upward so every label shares the same final top height.
    text_solid = text_shape.extrude(App.Vector(0, 0, height))
    return solid.fuse(text_solid)


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

    # Raised NORM/CRIT labels centered between outer edge (X=0) and tray cutout start.
    ledge_center_x = tray_x / 2.0
    piece = emboss_text_centered(
        piece,
        "NORM",
        ledge_center_x,
        row1_y + (norm_crit_die_d / 2.0),
        norm_text_size,
        text_relief_h,
        90.0,
    )
    piece = emboss_text_centered(
        piece,
        "CRIT",
        ledge_center_x,
        row2_y + (norm_crit_die_d / 2.0),
        crit_text_size,
        text_relief_h,
        90.0,
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

    # Raised center labels between paired score boxes.
    for i, label in enumerate(score_labels_top_to_bottom):
        y = row_y[i]
        piece = emboss_text_centered(
            piece,
            label,
            center_strip_x + (center_strip_w / 2.0),
            y + (score_die_d / 2.0),
            score_center_text_size,
            text_relief_h,
            90.0,
        )

    # Left side: raised ONE label and storage well.
    piece = cut_from_top(piece, p1_storage_well_x, p1_storage_well_y, storage_well_cut_h, p1_storage_well_w, p1_storage_well_h, storage_well_cut_h)

    # Right side: raised TWO label and storage well.
    piece = cut_from_top(piece, p2_storage_well_x, p2_storage_well_y, storage_well_cut_h, p2_storage_well_w, p2_storage_well_h, storage_well_cut_h)

    # Raised side labels: ONE/TWO.
    piece = emboss_text_centered(
        piece,
        "ONE",
        p1_label_x + (p1_label_w / 2.0),
        p1_label_y + (p1_label_h / 2.0),
        side_label_text_size,
        text_relief_h,
        90.0,
    )
    piece = emboss_text_centered(
        piece,
        "TWO",
        p2_label_x + (p2_label_w / 2.0),
        p2_label_y + (p2_label_h / 2.0),
        side_label_text_size,
        text_relief_h,
        90.0,
    )

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
App.Console.PrintMessage(f"All labels are embossed to {base_h + text_relief_h:.2f} mm total height\n")
App.Console.PrintMessage("Main score lanes + raised center labels are centered on X axis\n")
App.Console.PrintMessage("Raised center labels between score pairs: KILL, TAC, CRIT, CP, TEAM, TP/INI\n")
App.Console.PrintMessage("Raised side labels: ONE (left), TWO (right)\n")
App.Console.PrintMessage(f"Tracker footprint: {module_width:.2f} x {score_d:.2f} mm\n")


doc.recompute()
if Gui is not None:
    try:
        if hasattr(Gui, "SendMsgToActiveView"):
            Gui.SendMsgToActiveView("ViewFit")
        elif hasattr(Gui, "activeDocument") and Gui.activeDocument() is not None:
            active_view = Gui.activeDocument().activeView()
            if active_view is not None and hasattr(active_view, "fitAll"):
                active_view.fitAll()
    except Exception:
        # Non-GUI or limited GUI contexts can skip view fitting safely.
        pass
