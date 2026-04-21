import FreeCAD as App
import Part

# Create a new document
doc = App.newDocument("DeepArenaDiceTray")

# --- Dimensions ---
width = 110.0      # Fixed width
slot_d = 18.0      # Trench depth for 16mm dice
roll_d = 100.0     # Expanded central rolling area depth
wall = 4.0         # Wall/Divider thickness

# Depth of the floor cuts
slot_cut_h = 10.0  # Trench floor depth
roll_cut_h = 20.0  # Deep arena floor depth
base_h = 25.0      # Total tray height (leaves 5mm floor under the 20mm cut)

# Total Depth Calculation:
# 4 trenches (18*4) + 1 rolling (100) + 6 walls (4*6) = 72 + 100 + 24 = 196mm
total_depth = (slot_d * 4) + roll_d + (wall * 6)

# 1. Create the Main Body
base = Part.makeBox(width, total_depth, base_h)

# Helper function to create and cut a trench/area
def cut_cavity(y_pos, d_depth, d_height):
    global base
    cutout = Part.makeBox(width - (wall * 2), d_depth, d_height)
    # Positions the cut at the top of the block
    cutout.translate(App.Vector(wall, y_pos, base_h - d_height + 0.01))
    base = base.cut(cutout)

# 2. Apply the Cuts (Stacked from Player 1 to Player 2)
current_y = wall

# Player 1 Side
cut_cavity(current_y, slot_d, slot_cut_h)      # CRITS (P1)
current_y += slot_d + wall
cut_cavity(current_y, slot_d, slot_cut_h)      # NORMALS (P1)
current_y += slot_d + wall

# Central Deep Arena
cut_cavity(current_y, roll_d, roll_cut_h)      # ROLLING AREA (20mm Deep)
current_y += roll_d + wall

# Player 2 Side
cut_cavity(current_y, slot_d, slot_cut_h)      # NORMALS (P2)
current_y += slot_d + wall
cut_cavity(current_y, slot_d, slot_cut_h)      # CRITS (P2)

# Add to document
part_obj = doc.addObject("Part::Feature", "DeepArenaTray")
part_obj.Shape = base

doc.recompute()
Gui.SendMsgToActiveView("ViewFit")
