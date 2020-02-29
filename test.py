#!/usr/bin/env python3

import os
import sys
from PIL import Image, ImageDraw

class Area:
    def __init__(self,box):
        self.position = (box[0], box[1])
        self.size = (box[2], box[3])
        self.area = box

class SkinMeta:
    elements =[
        "head",
        "body",
        "rightArm",
        "leftArm",
        "rightLeg",
        "leftLeg",
        "head2",
        "body2",
        "rightArm2",
        "leftArm2",
        "rightLeg2",
        "leftLeg2"
    ]
    
    head = Area((0,0,32,16))
    body = Area((16,16,24,16))
    rightArm = Area((40,16,16,16))
    leftArm = Area((32,48,16,16))
    rightLeg = Area((0,16,16,16))
    leftLeg = Area((16,48,16,16))
    
    head2 = Area((32,0,32,16))
    body2 = Area((16,32,24,16))
    rightArm2 = Area((40,32,16,16))
    leftArm2 = Area((48,48,16,16))
    rightLeg2 = Area((0,32,16,16))
    leftLeg2 = Area((0,48,16,16))

class Skin:
    def __init__(self, image):
        self.loadSkin(image)

    """
    Split an image as different part of skin.
    :param image: Pillow.Image
    """
    def loadSkin(self, image):
        for element in SkinMeta.elements:
            position = getattr(SkinMeta, element).position
            size = getattr(SkinMeta, element).size
            subImage = self.cropImage(image, position, size)
            setattr(self, element, subImage)
            #test
            #subImage.save("HHHHH." +element +".png")
            
    """
    Crop image by location and size.
    
    :param image: Pillow.Image
    :param location: tuple which has two element.
    :param size: tuple which has two element.
    """
    def cropImage(self, image, location, size):
        area = [
            location[0],
            location[1],
            location[0]+size[0],
            location[1]+size[1],
        ]
        return image.crop(area)
        
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
        rightArmImage = self.rightArm
        #x0, y0, x1, y1
        areas=[
          (10,0,11,3),
          (14,4,15,5)
        ]
        for area in areas:
            if(checkTransparentInArea(rightArmImage, area)):
                return True
        return False

    """
    The female skin has lost 1 pixel of arm,
    and older skin do not support it.
    """
    def fixRightArm(self):
        rightArmImage = self.rightArm
        imageDraw =  ImageDraw.Draw(rightArmImage)
        #fix yaw
        handImage = self.cropImage(rightArmImage, (7,0),(3,4))
        sideArmImage = self.cropImage(rightArmImage, (7,4),(7,12))
        imageDraw.rectangle((7,0,15,15),(0,0,0,0))#clean right side
        rightArmImage.paste(handImage,(8,0))
        rightArmImage.paste(sideArmImage,(9,4))
        #fill blank
        missions = [
            [(6,0),(1,16),(7,0)],#position, size, target position
            [(10,0),(1,4),(11,0)],
            [(9,4),(1,12),(8,4)]
        ]
        for mission in missions:
            fill = self.cropImage(rightArmImage, mission[0],mission[1])
            rightArmImage.paste(fill,mission[2])

        #rightArmImage.save('test0000111.png')
        
    """
    The female skin has lost 1 pixel of arm,
    and older skin do not support it.
    """
    def fixLeftArm(self):
        leftArmImage = self.leftArm
        #imageDraw =  ImageDraw.Draw(rightArmImage)
        #move hand
        self.cutAndMoveImage(leftArmImage, (7,0), (3,4), (9,0))
        #move side arm1
        self.cutAndMoveImage(leftArmImage, (7,4), (7,12), (8,4))
        #move shoulder and side arm
        self.cutAndMoveImage(leftArmImage, (4,0), (3,16), (5,0))
        
        #fill blank
        missions = [
            [(5,0),(1,16),(4,0)],#position, size, target position
            [(9,0),(1,4),(8,0)],
            [(14,4),(1,12),(15,4)]
        ]
        for mission in missions:
            fill = self.cropImage(leftArmImage, mission[0], mission[1])
            leftArmImage.paste(fill,mission[2])

        leftArmImage.save('test0000111.png')
        

    def cutAndMoveImage(self, image, position, size, target):
        imageDraw = ImageDraw.Draw(image)
        cropImage = self.cropImage(image, position, size)
        position2 = (position[0]+size[0]-1,position[1]+size[1]-1)
        imageDraw.rectangle(position + position2,(0,0,0,0)) #clean
        image.paste(cropImage, target)
        

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
    skin.fixLeftArm()
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
