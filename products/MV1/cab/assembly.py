"""MV1 cab

The cab's body, as it sits on the front drives' base links and the front
steering beam's posts: the front pivot's axis on x = 0, y = 0, the floor's
bottom on z = 0. MV1 places it over the front pivot.
"""
import cadquery as cq

body = load_part("body")

result = cq.Assembly(name="cab")
result.add(body.result, name="body", color=cq.Color(0.85, 0.75, 0.20))

regions = {}
