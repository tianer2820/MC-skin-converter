#!/usr/bin/env python3

import os
import sys
from PIL import Image, ImageDraw

class Skin:
    
    cropTable=[
        #rectangular regions of default skin
        {
            "head":(0,0,31,15),
            "body":(16,16,39,31),
            "right-arm":(40,16,55,31),
            "left-arm":(32,48,47,63),
            "right-leg":(0,16,15,31),
            "left-leg":(16,48,31,63)
        },
        #rectangular regions of overlay skin
        {
            "head":(32,0,63,15),
            "body":(16,32,39,47),
            "right-arm":(40,32,55,47),
            "left-arm":(48,48,63,63),
            "right-leg":(0,32,15,47),
            "left-leg":(0,48,15,63)
        }
    ]

    def __init__(self, image):
        self.skin = self.getCrops(image)

    """
    Split an image as different part of skin.
    """
    def getCrops(self, image):
        defaultSet={}
        for key in self.cropTable[0].keys():
            subImage = self.crop(image, cropTable[key])
            defaultSet.update( {key : subImage} )
        overlaySet={}
        for key in self.cropTable[1].keys():
            subImage = self.crop(image, cropTable2[key])
            overlaySet.update( {key : subImage} )
        skinSet={
            "default":defaultSet,
            "overlay":overlaySet
        }
        return skinSet
      
    """
    Checking all pixel are transparent in area.
    
    :param image: Pillow.Image
    :param box: tuple describe rectangular region.
    """
    def checkTransparentInArea(self, image, box):
        for x in range(box[0],box[2]):
            for y in range(box[1],box[3]):
                r,g,b,a = image.getpixel((x,y));
                if(a==0):
                    return True
        return False

    """
    Check isn't female skin?
    """
    def isFemale(self):
        rightArmImage = self.skin['default']['right-arm']
        #x0, y0, x1, y1
        areas=[
          (10,0,11,3),
          (14,4,15,5)
        ]
        for area in areas:
            if(checkTransparentInArea(rightArmImage, area)):
                return True
        return False

    def fixArm(self):
        rightArmImage = self.skin['default']['right-arm']
        imageDraw =  ImageDraw.Draw(rightArmImage)
        #fix yaw
        handImage = self.crop(rightArmImage, (7,0,9,3))
        #print(handImage.size)
        imageDraw.rectangle((7,0,9,3),(0,0,0,0))
        sideArmImage = self.crop(rightArmImage, (7,4,13,15))
        #print(sideArmImage.size)
        imageDraw.rectangle((7,4,13,15),(0,0,0,0))
        rightArmImage.paste(handImage,(8,0))
        rightArmImage.paste(sideArmImage,(9,4))
        rightArmImage.save('test0000111.png')

    def crop(self, image, box):
        return image.crop((box[0],box[1], box[2]+1, box[3]+1))

#rectangular regions of default skin
cropTable={
    "head":(0,0,31,15),
    "body":(16,16,39,31),
    "right-arm":(40,16,55,31),
    "left-arm":(32,48,47,63),
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

'''
@param Pillow.Image image
@param tuple box
'''
def checkTransparentInArea(image, box):
    for x in range(box[0],box[2]):
        for y in range(box[1],box[3]):
            r,g,b,a = image.getpixel((x,y));
            if(a==0):
                return True
    return False

def isFemale(rightArmImage):
    areas=[
      (10,0,11,3),#x0, y0, x1, y1
      (14,4,15,5)
    ]
    for area in areas:
        if(checkTransparentInArea(rightArmImage, area)):
            return True
    return False



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
    skin = Skin(image)
    skin.fixArm()
    '''
    skinSet = getCrops(image)
    if(isFemale(skinSet['default']['right-arm'])):
        print('is female!')
    else:
        print('is male!')
    '''
    #print(image.getpixel((0,8)))
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
