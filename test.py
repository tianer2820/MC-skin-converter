#!/usr/bin/env python3
import os
import sys
from Skin import Skin
from PIL import Image

def processSkin(filePath):
    try :
        image = Image.open(filePath)
    except IOError :
        failure += 1
        
    width, height = image.size
    #print(width);
    if(width!=64 or height!=64):
        print("file size wrong, skip: "+filePath);
        return
    skin1 = Skin(image)
    skin1.useLeftArm()
    skin1.getOutput().save(filePath + "use-left-arm.png")
    skin2 = Skin(image)
    skin2.useLeftLeg()
    skin2.getOutput().save(filePath + "use-left-leg.png")
    #skin.fixArms()
    #skin.getOutput().save("output." + filePath )
    #skin.getDegradedOutput().save("output2." + filePath)
    #skin.mergeDown()
    #skin.getDegradedOutput().save("output3." + filePath)
    #skin.useLeftLeg()
    #skin.getOutput().save("output." + filePath )
    #skin.getDegradedOutput().save("output2." + filePath)

    
    
    
try :
    arg = sys.argv[1]
except IndexError :
    print("Usage: format17.py <file|dir>")
    sys.exit(1)


skins = [arg]
path = ""

if os.path.isdir(arg) :
    path = arg
    skins = os.listdir(arg)

for sfile in skins :
    processSkin(os.path.join(path, sfile))
