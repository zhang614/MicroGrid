from visual import *
from solarTracking import *
from PIL import Image
import os
import math

#make solar panel texture
image = Image.open('panel.jpg')
im = image.resize((1024,1024), Image.ANTIALIAS)
(width, height) = im.size
print width
print height
solarTexture = materials.texture(data=im, mapping="sign", interpolate=False)
#materials.saveTGA("solarPanel",im)
#solarTexture = materials.texture(data=materials.loadTGA("flower128"), mapping="rectangular")

print solarTexture

#setup the 3D scene
scene = display(title='Two support tracker',
     x=0, y=0, width=600, height=600,
     background=(0.6,0.6,0.6), autoscale = False)
scene.range = 150
#solar panel (3) is 9'9" wide by 6'5" high
#works out the needed height of the pole so that panel does
#not touch the ground when facing dawn on winter solstic (the worst case)
ewDim = 117 #9*12+9
nsDim = 77 #6*12+5
panelHeight = 3

#post
postLength = 6*12
postWidth = 4
#SUN
sunD = 1000
distant_light(direction=(0,sunD, sunD*cos(winterE)), color=color.white)
#SUN Assamuth angles to design tilt angles
winterMaxAltitude = math.radians(maxElevation(winterSolstice)) #relative to the verticle
winterMaxTilt = pi/2 - winterMaxAltitude - math.radians(10) #don't go all the way down for winter
summerMaxAltitude = math.radians(maxElevation(summerSolstice)) #relative to the verticle
summerMaxTilt = pi/2-summerMaxAltitude
print "winter Tilt= "+ str(math.degrees(winterMaxTilt))
print "summer Tilt= " + str(math.degrees(summerMaxTilt))
#sweepMax = summerMaxTilt+winterMaxTilt
#rotate
#(1,0,0) Change x for tilt angle (pitch) #winter to summer
#0,1,0) change y for yaw (not done with panels)
#(0,0,1) change in roll (follow the sun)

#Orientation
#X +right -left
#Y +up  -down
#Z +in  -out


#Panel Assemble
panelA = frame()
#panel
panel = box(frame=panelA, pos=(0,2+panelHeight/2,0), length=panelHeight, height=ewDim, width=nsDim,
            material = solarTexture, axis=(0,1,0)) #gray(0.5)) #flat
centerRod = cylinder(frame=panelA, pos=(0,0,-1*nsDim/2), axis=(0,0,nsDim),radius=2, materials = materials.chrome)
crossRod = cylinder(frame=panelA, pos=(-1*ewDim/2,0,0), axis=(ewDim,0,0),radius=1, materials = materials.chrome)

#tilt rotation
panelCenter = panelA.frame_to_world((0,0,0)) #center for panel in frame
panelSouth = panelA.frame_to_world((0,0,nsDim/2)) #south end of panel in frame + is south

#Ground
groundLength = 30
ground = frame()
post = box(frame=ground, pos=panelCenter+(0,-1*postLength/2,0), length=postLength, height=postWidth, width=postWidth,axis=(0,-1*postLength,0),materials = materials.chrome)
floor = box(frame=ground, pos=panelCenter+(0,-1*postLength,0), length=2, height=200, width=200,axis=(0,-1*postLength,0),materials = materials.chrome, opacity=0.3)
southText = text(frame=ground, pos=panelCenter+(0, -1*postLength, nsDim/2), text="South", color=color.red,
           depth=0.1, height=7, align="center")

tiltSteps = 4
tiltRange = summerMaxTilt-winterMaxTilt #summer to winter range
tiltIncrement = tiltRange/tiltSteps

def displayMonth(month):
    return text(frame=ground, pos=panelCenter+(ewDim*.4, -1*postLength, nsDim/2), text="month="+str(month % 12), color=color.black,
               depth=0.1, height=7, align="center")

def tiltThePanel(years=1, stepsPerSolstice=6, origin=panelCenter, trackAtStops=True):
    #moves through years, assumes neutral start (flat), returns in the same position
    #stepsPerSolstice could be 0 (just winter to summer, then summer to winter)
    #if trackAtStops, then do one day track (east to west at each stop)
    tiltIncrement = (winterMaxTilt - summerMaxTilt)/(1+stepsPerSolstice) #how much to move from summer to/from winter
    panelA.rotate(angle=summerMaxTilt, axis=(1,0,0), origin=panelCenter)     #starts at summer
    tiltAngle = summerMaxTilt
    month = 6
    newMonth = text(text="")
    for i in range(0, years):
        for direction in [+1,-1]:
            #scene.waitfor('click keydown')
            # move from summer to winter, winter to summer
            for tilt in range(0, 1+stepsPerSolstice):
                rate(1)
                newMonth.visible = False
                newMonth = displayMonth(month)
                if trackAtStops:
                    tiltVector = (0,-1*sin(tiltAngle),cos(tiltAngle))
                    trackTheSun(tiltVector)#print "tilt angle "+str(math.degrees(pi/2-tiltAngle))
                panelA.rotate(angle=direction*tiltIncrement, axis=(1,0,0), origin=panelCenter) #(1,0,0) Change x for tilt angle
                tiltAngle = tiltAngle + direction*tiltIncrement
                month = month+1
                #scene.waitfor('click keydown')
                
##tiltIncrement = (winterMaxTilt - summerMaxTilt)/10
##panelA.rotate(angle=summerMaxTilt, axis=(1,0,0), origin=panelSouth) #originally neutral
##tiltAngle = summerMaxTilt
##tiltVector = (0,-1*sin(tiltAngle),cos(tiltAngle))
##for tiltIndex in range(0,10):
##    trackTheSun(tiltVector)
##    panelA.rotate(angle=tiltIncrement, axis=(1,0,0), origin=panelSouth) #(1,0,0) Change x for tilt angle
##    tiltAngle = tiltAngle + tiltIncrement
##    scene.waitfor('click keydown')
##    tiltVector = (0,-1*sin(tiltAngle),cos(tiltAngle))
                    
def trackTheSun(alongVector, steps=100, trackRange=pi*0.6, origin=panelCenter):
    # track the sun, assumes neutral start (noon), returns in same position
    angleIncrement = trackRange/steps
    panelA.rotate(angle=-1*trackRange/2, axis=alongVector, origin=origin) #start in the morning
    scene.waitfor('click keydown')
    for track in range(0, steps):
        rate(20)
        panelA.rotate(angle=angleIncrement, axis=alongVector, origin=origin)
    #scene.waitfor('click keydown')
    panelA.rotate(angle=-1*trackRange/2, axis=alongVector, origin=origin) #set to neutral
    #scene.waitfor('click keydown')

#print "angle Increment= "+ str(math.degrees(tiltIncrement)

    

##RUN THE SCRIPT
    
#makeSolarPanels()
tiltThePanel(stepsPerSolstice=5)



##from visual import *
##import Image # Must install PIL
##name = "flower"
##width = 128 # must be power of 2
##height = 128 # must be power of 2
image = Image.open('panel.jpg')
#print(im.size) # optionally, see size of image
# Optional cropping:
im = image.crop((4,4,68,68)) # (0,0) is upper left
im.show()
##im = im.resize((width,height), Image.ANTIALIAS)
solarTexture = materials.texture(data=im, mapping="sign")
materials.saveTGA("solarPanel",im)
data = materials.loadTGA("solarPanel")
solarTexture = materials.texture(data=data)
##
##At a later time you can say data = materials.loadTGA(name) to retrieve the image data from the targa file.
##As a convenience, a texture can also be created directly from the PIL image data, like this:

#IMAGE CODE
def makeSolarPanels():
    """Merge two images into one, displayed side by side
    :param file1: path to first image file
    :param file2: path to second image file
    :return: the merged Image object
    """
    image = Image.open('panel.jpg')
    (width, height) = image.size
    result_width = 3*width
    result_height = height

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image, box=(0, 0))
    result.paste(im=image, box=(width, 0))
    result.paste(im=image, box=(2*width,0))
    result.save("solarPanel.jpg")
    (w,h)=result.size
    print w
    print h




