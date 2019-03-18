from visual import *
# This routine watches scene.forward and changes the directions of
# the lights to stay fixed with respect to scene.forward.
# The effect is to let the user rotate the scene while keeping
# the lights fixed, as though one were rotating an object in the
# hand to examine it, with fixed lighting, rather than rotating
# the camera.

# To compare, comment out the while loop, in which case you'll see
# that when you rotate around to the back of the scene, it is dark.

# This requires Visual 5. A similar routine in Visual 3 would be
# somewhat more complicated because the lights were not objects
# and so could not be put in a frame. Instead, one would have to
# adjust the directions of the lights individually.

# Bruce Sherwood, May 2009
scene.material = materials.wood # default material for all objects
box(pos=(-2,0,0), color=color.red)
box(pos=(2,0,0), color=color.green, material=materials.marble)
cylinder(pos=(0,-0.5,0), radius=1, axis=(0,1,0), color=color.orange)
s = sphere(pos=(-2,0.8,0), radius=0.3, color=color.cyan,
           material=materials.emissive)
local_light(pos=s.pos, color=s.color)

lframe = frame()
for obj in scene.lights:
    if isinstance(obj, distant_light):
        obj.frame = lframe # put distant lights in a frame
old = vector(scene.forward) # keep a copy of the old forward
while 1:
    rate(50)
    if scene.forward != old:
        new = scene.forward
        axis = cross(old,new)
        angle = new.diff_angle(old)
        lframe.rotate(axis=axis, angle=angle)
        old = vector(new)
