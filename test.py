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
    skin = Skin(image)
    #skin.fixArms()
    #skin.getOutput().save("output." + filePath )
    #skin.getDegradedOutput().save("output2." + filePath)
    #skin.mergeDown()
    #skin.getDegradedOutput().save("output3." + filePath)
    skin.useLeftArm()
    #skin.getOutput().save("output." + filePath )
    skin.getDegradedOutput().save("output2." + filePath)

    
    
    
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
