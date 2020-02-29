#!/usr/bin/python 

import os
import sys
from PIL import Image

cropTable={
    "head":(0,0,31,15),
    "body":(16,16,39,31),
    "right-arm":(40,16,55,31),
    "left-arm":(32,48,46,63),
    "right-leg":(0,16,15,31),
    "left-leg":(16,48,31,63)
}
cropTable2={
    "head":(32,0,63,15),
    "body":(16,32,39,47),
    "right-arm":(40,32,55,47),
    "left-arm":(47,48,63,63),
    "right-leg":(0,32,15,47),
    "left-leg":(0,48,15,63)
}

def testSplit(filePath, image):
    for key in cropTable1.keys():
        subImage = image.crop(cropTable1[key])
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
    testSplit(filePath,image)
    
    
    
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
