"""MV1 bed

The rear bed: its tray on four legs, in the MV1's x and y, the legs'
feet on z = 0 (MV1 places it on the base plate's top).
"""
import cadquery as cq

tray = load_part("tray")
leg = load_part("leg")

result = cq.Assembly(name="bed")
for i, (x, y) in enumerate(tray.leg_spots, 1):
    result.add(leg.result, name=f"leg_{i}", color=cq.Color(0.30, 0.30, 0.30),
               loc=cq.Location(cq.Vector(x, y, 0)))
result.add(tray.result, name="tray", color=cq.Color(0.55, 0.30, 0.15),
           loc=cq.Location(cq.Vector(0, 0, leg.height)))

regions = {}
