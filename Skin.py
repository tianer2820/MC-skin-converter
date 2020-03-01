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
    degradedElements =[
        "head",
        "body",
        "rightArm",
        "rightLeg",
        "head2"
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
    Merge overlay down.
    """
    def mergeDown(self):
        self.body.paste(self.body2, (0,0), self.body2)
        self.rightArm.paste(self.rightArm2, (0,0), self.rightArm2)
        self.leftArm.paste(self.leftArm2, (0,0), self.leftArm2)
        self.rightLeg.paste(self.rightLeg2, (0,0), self.rightLeg2)
        self.leftLeg.paste(self.leftLeg2, (0,0), self.leftLeg2)

    """
    Check isn't female skin?
    
    :return: boolean
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
    Get entire image
    
    :return: Pillow.Image
    """
    def getOutput(self):
        image = Image.new("RGBA", (64, 64))
        for element in SkinMeta.elements:
            subImage = getattr(self, element)
            position = getattr(SkinMeta, element).position
            image.paste(subImage, position)
        return image

    """
    Get degraded image, which is v1.7(64*32).
    
    :return: Pillow.Image
    """
    def getDegradedOutput(self):
        image = Image.new("RGBA", (64, 32))
        for element in SkinMeta.degradedElements:
            subImage = getattr(self, element)
            position = getattr(SkinMeta, element).position
            image.paste(subImage, position)
        return image
        
    def fixArms(self):
        self.fixRightArm()
        self.fixLeftArm()

    def useLeftArm(self):
        missions ={
          'top': [(4,0), (4,4)],  #position, size
          'bottom': [(8,0), (4,4)],
          'front':[(4,4), (4,12)], 
          'back': [(12,4), (4,12)],
          'right':[(0,4), (4,12)], 
          'left': [(8,4), (4,12)]
        }

        for mission in missions.values():
            self.copyReserveAndPaste(self.leftArm, self.rightArm, mission[0], mission[1])
            
        self.copyPasteSwitch(self.rightArm, [(0,4), (8,4)], (4,12))

    def useLeftLeg(self):
        missions ={
          'top': [(4,0), (4,4)],  #position, size
          'bottom': [(8,0), (4,4)],
          'right':[(0,4), (4,12)], 
          'front':[(4,4), (4,12)], 
          'left': [(8,4), (4,12)],
          'back': [(12,4), (4,12)]
        }
        for mission in missions.values():
            self.copyReserveAndPaste(self.leftLeg, self.rightLeg, mission[0], mission[1])

    """
    ========Private stuff========
    """

    """
    
    """
    def copyReserveAndPaste(self, sourceImage, targetImage, position, size):
        image = self.cropImage(sourceImage, position, size).transpose(Image.FLIP_LEFT_RIGHT)
        targetImage.paste(image, position)
   
    def copyPaste(self, sourceImage, targetImage, position, size):
        image = self.cropImage(sourceImage, position, size)
        targetImage.paste(image, position)
        
    def copyPasteSwitch(self, image, positions, size):
        image1 = self.cropImage(image, positions[0], size)
        image2 = self.cropImage(image, positions[1], size)
        image.paste(image2, positions[0])
        image.paste(image1, positions[1])


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
        
    """
    The female skin has lost 1 pixel of arm,
    and older skin do not support it.
    """
    def fixLeftArm(self):
        leftArmImage = self.leftArm
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

    """
    Cut image down and move it to another position
    
    :param image: Pillow.Image
    :param position: tuple which has two element.
    :param size: tuple which has two element.
    :param target: tuple which has two element.
    """
    def cutAndMoveImage(self, image, position, size, target):
        imageDraw = ImageDraw.Draw(image)
        cropImage = self.cropImage(image, position, size)
        position2 = (position[0]+size[0]-1,position[1]+size[1]-1)
        imageDraw.rectangle(position + position2,(0,0,0,0)) #clean
        image.paste(cropImage, target)
        
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
