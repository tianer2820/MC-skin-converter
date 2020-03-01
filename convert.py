#!/usr/bin/env python3
import os
import sys
from argparse import ArgumentParser
from Skin import Skin
from PIL import Image

def checkFile(filePath):
    try :
        image = Image.open(filePath)
    except IOError as e:
        print(e.errno)
        print(e)
        return False
        
    width, height = image.size
    if(width!=64 or height!=64):
        print("Size or file are wrong, skip: " + filePath);
        return False
    return True

"""
:param filePath: string
:param arguments: objects 
"""
def processSkin(filePath, arguments):
    image = Image.open(filePath)

    skin = Skin(image)

    if(arguments.unslim is None):
        if(skin.isFemale):
            skin.fixArms()
    elif(arguments.unslim==1):
        skin.fixArms()

    if(arguments.merge):
        skin.mergeDown()

    if(arguments.part=='arm'):
        skin.useLeftArm()
    elif(arguments.part=='leg'):
        skin.useLeftLeg()
    elif(arguments.part=='both'):
        skin.useLeftArm()
        skin.useLeftLeg()

    if(arguments.keep):
        skin.getOutput().save(filePath)
    else:
        skin.getDegradedOutput().save(filePath)

    
parser = ArgumentParser(prog='Minecraft Skin Converter')

parser.add_argument("source", type=str,
                    help='The skin file or folder which contain skins, you wnat to converted.')
                    
parser.add_argument('-f','--force-unslim', dest='unslim', choices=[0, 1], type=int,
                    help='Forcing process to fix slimmer arms or not. If set to "0", it willn\'t auto detect.')

parser.add_argument('-l','--use-left', dest='part', choices=['arm', 'leg', 'both'], 
                    help='Using lef arm, leg or both to degraded skin.')
                    
parser.add_argument('-k','--keep', dest='keep', default=0, choices=[0, 1], type=int,
                    help='Keeping overlay. (Return 64*64 file.)')
                    
parser.add_argument('-m','--merge-down', dest='merge', default=1, choices=[0, 1], type=int,
                    help='Merge overlay down.')

arguments = parser.parse_args()

skins = [arguments.source]
path = ""

if os.path.isdir(arguments.source) :
    path = arguments.source
    skins = os.listdir(arguments.source)

for sfile in skins :
    filePath = os.path.join(path, sfile)
    if(not checkFile(filePath)):
        continue
    processSkin(filePath, arguments)
