import FreeCAD as App
import Part

# Create a new document
doc = App.newDocument("DeepArenaDiceTray")

# --- Dimensions ---
width = 110.0      # Fixed width
slot_d = 18.0      # Trench depth for 16mm dice
roll_d = 100.0     # Expanded central rolling area depth
wall = 4.0         # Wall/Divider thickness

# Label ledge: flat top-surface strip left for engraved/written labels
label_ledge = 20.0  # Width of the label strip per player side

# Depth of the floor cuts
slot_cut_h = 10.0  # Trench floor depth
roll_cut_h = 20.0  # Deep arena floor depth
base_h = 25.0      # Total tray height (leaves 5mm floor under the 20mm cut)

# Total Depth Calculation:
# 4 trenches (18*4) + 1 rolling (100) + 6 walls (4*6) = 72 + 100 + 24 = 196mm
total_depth = (slot_d * 4) + roll_d + (wall * 6)

# 1. Create the Main Body
base = Part.makeBox(width, total_depth, base_h)

# Helper function to create and cut a cavity.
# x_start: X position of the cut (from left)
# cut_w:   Width of the cut along X
def cut_cavity(y_pos, d_depth, d_height, x_start=wall, cut_w=None):
    global base
    if cut_w is None:
        cut_w = width - (wall * 2)
    cutout = Part.makeBox(cut_w, d_depth, d_height)
    # Positions the cut at the top of the block
    cutout.translate(App.Vector(x_start, y_pos, base_h - d_height + 0.01))
    base = base.cut(cutout)

# Derived slot widths:
#   P1 slots: label ledge on the LEFT  (player's left as they face the tray)
#   P2 slots: label ledge on the RIGHT (player's left as they face from the other end)
slot_w   = width - (wall * 2) - label_ledge   # 110 - 8 - 20 = 82 mm
p1_x     = wall + label_ledge                 # cut starts after the ledge (left side)
p2_x     = wall                               # cut starts at the inner wall (right side)

# 2. Apply the Cuts (Stacked from Player 1 to Player 2)
current_y = wall

# Player 1 Side — label ledge on LHS (their left)
cut_cavity(current_y, slot_d, slot_cut_h, x_start=p1_x, cut_w=slot_w)   # CRITS (P1)
current_y += slot_d + wall
cut_cavity(current_y, slot_d, slot_cut_h, x_start=p1_x, cut_w=slot_w)   # NORMALS (P1)
current_y += slot_d + wall

# Central Deep Arena — full interior width, no ledge
cut_cavity(current_y, roll_d, roll_cut_h)      # ROLLING AREA (20mm Deep)
current_y += roll_d + wall

# Player 2 Side — label ledge on RHS (their left when viewed from P2 end)
cut_cavity(current_y, slot_d, slot_cut_h, x_start=p2_x, cut_w=slot_w)   # NORMALS (P2)
current_y += slot_d + wall
cut_cavity(current_y, slot_d, slot_cut_h, x_start=p2_x, cut_w=slot_w)   # CRITS (P2)

# Add to document
part_obj = doc.addObject("Part::Feature", "DeepArenaTray")
part_obj.Shape = base

doc.recompute()
Gui.SendMsgToActiveView("ViewFit")
