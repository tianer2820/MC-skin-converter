#!/usr/bin/env python3

import os
import sys
from PIL import Image

#rectangular regions of default skin
cropTable={
    "head":(0,0,31,15),
    "body":(16,16,39,31),
    "right-arm":(40,16,55,31),
    "left-arm":(32,48,46,63),
    "right-leg":(0,16,15,31),
    "left-leg":(16,48,31,63)
}

#rectangular regions of overlay skin
cropTable2={
    "head":(32,0,63,15),
    "body":(16,32,39,47),
    "right-arm":(40,32,55,47),
    "left-arm":(47,48,63,63),
    "right-leg":(0,32,15,47),
    "left-leg":(0,48,15,63)
}

def getCrops(image):
    defaultSet={}
    for key in cropTable.keys():
        subImage = image.crop(cropTable[key])
        defaultSet.update( {key : subImage} )
    overlaySet={}
    for key in cropTable2.keys():
        subImage = image.crop(cropTable2[key])
        overlaySet.update( {key : subImage} )
    skinSet={
        "default":defaultSet,
        "overlay":overlaySet
    }
    return skinSet

def testSplit(filePath, image):
    for key in cropTable.keys():
        subImage = image.crop(cropTable[key])
        subImage.save(filePath + "." +key +".png")

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
    print(image.getpixel((0,8)))
    #testSplit(filePath,image)
    
    
    
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
