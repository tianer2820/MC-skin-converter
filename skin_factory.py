import os
import sys
from PIL import Image, ImageDraw
from dataclasses import dataclass

@dataclass
class Area:
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0

    def get_position(self):
        return (self.x, self.y)

    def set_position(self, pos: tuple[int, int]):
        self.x = pos[0]
        self.y = pos[1]

    position = property(get_position, set_position)

    def get_size(self):
        return (self.w, self.h)
    
    def set_size(self, size: tuple[int, int]):
        self.w = size[0]
        self.h = size[1]
    
    size = property(get_size, set_size)

    @property
    def left(self):
        return self.x
    
    @property
    def right(self):
        return self.x + self.w

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.h



    def __getitem__(self, idx: int):
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        elif idx == 2:
            return self.w
        elif idx == 3:
            return self.h
        else:
            raise IndexError()
    
    def __len__(self):
        return 4


new_skin_elements = [
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
old_skin_elements = [
    "head",
    "body",
    "rightArm",
    "rightLeg",
    "head2"
]

skin_areas = {
    'head': Area(0, 0, 32, 16),
    'body': Area(16, 16, 24, 16),
    'rightArm': Area(40, 16, 16, 16),
    'leftArm': Area(32, 48, 16, 16),
    'rightLeg': Area(0, 16, 16, 16),
    'leftLeg': Area(16, 48, 16, 16),

    'head2': Area(32, 0, 32, 16),
    'body2': Area(16, 32, 24, 16),
    'rightArm2': Area(40, 32, 16, 16),
    'leftArm2': Area(48, 48, 16, 16),
    'rightLeg2': Area(0, 32, 16, 16),
    'leftLeg2': Area(0, 48, 16, 16),
}



def transparency_in_area(image: Image.Image, area: Area) -> bool:
    """
    return true if any pixel in that area is transparent
    """
    for dx in range(area.w):
        for dy in range(area.h):
            x = area.x + dx
            y = area.y + dy
            r, g, b, a = image.getpixel((x, y))
            if(a == 0):
                return True
    return False


def crop_img(image: Image.Image, area: Area):
    area = [
        area.left,
        area.top,
        area.right,
        area.bottom,
    ]
    return image.crop(area)


def move_area(img: Image.Image, area: Area, target):
    img_draw = ImageDraw.Draw(img)
    crop = crop_img(img, area)
    position1 = (area.left, area.top)
    position2 = (area.right-1, area.bottom-1)
    img_draw.rectangle(position1 + position2, (0, 0, 0, 0))  # clean
    img.paste(crop, target)


def mirror_area(img: Image.Image, area: Area):
    crop = crop_img(img, area)
    crop = crop.transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(crop, area.position)


def swap_area(img1: Image.Image, img2:Image.Image, area1: Area, area2: Area = None):
    if area2 is None:
        area2 = area1
    assert area1.size == area2.size
    crop1 = crop_img(img1, area1)
    crop2 = crop_img(img2, area2)
    img1.paste(crop2, area1.position)
    img2.paste(crop1, area2.position)





class SkinFactory:
    def __init__(self, img: Image.Image):
        img = img.convert('RGBA')
        self.skin_blocks = {}
        self.skin_blocks: dict[str, Image.Image]

        self._slice_skin(img)
        # check format
        if img.width == img.height:
            self.original_skin_format = 'new'
        else:
            self.original_skin_format = 'old'
        # check arm style
        if self.is_alex():
            self.original_arm_style = 'alex'
        else:
            self.original_arm_style = 'steve'

    def _slice_skin(self, img: Image.Image):
        """slice the skin img into different blocks"""
        # check skin format
        if img.width == img.height:
            old = False
            elements = new_skin_elements
        else:
            old = True
            elements = old_skin_elements

        for element in elements:
            sub_img = crop_img(img, skin_areas[element])
            self.skin_blocks[element] = sub_img
        
        if old:
            # manually copy arms and legs to both sides
            left_arm = self.skin_blocks['rightArm'].copy()
            self._mirror_arm(left_arm)
            self.skin_blocks['leftArm'] = left_arm

            left_leg = self.skin_blocks['rightLeg'].copy()
            self._mirror_leg(left_leg)
            self.skin_blocks['leftLEG'] = left_leg

            # manually create missing second layers
            for e in new_skin_elements:
                if e not in self.skin_blocks:
                    area = skin_areas[e]
                    empty_img = Image.new('RGBA', area.size, (0, 0, 0, 0))
                    self.skin_blocks[e] = empty_img


    def smart_convert(self,
            skin_format='keep', arm_style='keep',
            use_arm_from='right', use_leg_from='right',
            keep_second_layer=True) -> Image.Image:

        # check skin format
        if skin_format == 'keep':
            skin_format = self.original_skin_format

        if skin_format == 'new':
            if arm_style == 'keep' or arm_style == self.original_arm_style:
                return self.get_output_1_8()
            else:
                if arm_style == 'steve' and self.original_arm_style == 'alex':
                    self.to_steve_arms()
                elif arm_style == 'alex' and self.original_arm_style == 'steve':
                    self.to_alex_arms()
                return self.get_output_1_8()

        elif skin_format == 'old':
            if self.original_arm_style == 'alex':
                self.to_steve_arms()
            if keep_second_layer:
                self.merge_down_2nd_layer()
            return self.get_output_old()

        else:
            raise ValueError(f"Unknown skin format '{skin_format}'. Can be 'new', 'old', or 'keep'")

    def is_alex(self) -> bool:
        return self._is_alex_arm(self.skin_blocks['rightArm'])
    
    def _is_alex_arm(self, arm_block) -> bool:
        """check if skin is in the alex format (slim arms)"""
        areas = [
            Area(10, 0, 1, 4),
            Area(14, 4, 2, 12),
        ]
        for area in areas:
            if(transparency_in_area(arm_block, area)):
                return True
        return False


    def to_steve_arms(self):
        self._to_steve_arm(self.skin_blocks['rightArm'])
        self._to_steve_arm(self.skin_blocks['rightArm2'])
        self._to_steve_arm(self.skin_blocks['leftArm'])
        self._to_steve_arm(self.skin_blocks['leftArm2'])

    def to_alex_arms(self):
        self._to_alex_arm(self.skin_blocks['rightArm'])
        self._to_alex_arm(self.skin_blocks['rightArm2'])
        self._to_alex_arm(self.skin_blocks['leftArm'])
        self._to_alex_arm(self.skin_blocks['leftArm2'])


    def merge_down_2nd_layer(self):
        """Merge second layer into first layer.
        Useful when converting 1.8 skin to old format"""
        self.skin_blocks['body'].paste(self.skin_blocks['body2'], (0, 0), self.skin_blocks['body2'])
        self.skin_blocks['rightArm'].paste(self.skin_blocks['rightArm2'], (0, 0), self.skin_blocks['rightArm2'])
        self.skin_blocks['leftArm'].paste(self.skin_blocks['leftArm2'], (0, 0), self.skin_blocks['leftArm2'])
        self.skin_blocks['rightLeg'].paste(self.skin_blocks['rightLeg2'], (0, 0), self.skin_blocks['rightLeg2'])
        self.skin_blocks['leftLeg'].paste(self.skin_blocks['leftLeg2'], (0, 0), self.skin_blocks['leftLeg2'])

    def get_output_1_8(self) -> Image.Image:
        """Get the 1.8 skin format output image"""
        image = Image.new("RGBA", (64, 64))
        for element in new_skin_elements:
            subImage = self.skin_blocks[element]
            position = skin_areas[element].position
            image.paste(subImage, position)
        return image

    def get_output_old(self) -> Image.Image:
        """Get the 1.7- old skin format output image"""
        image = Image.new("RGBA", (64, 32))
        for element in old_skin_elements:
            subImage = self.skin_blocks[element]
            position = skin_areas[element].position
            image.paste(subImage, position)
        return image


    def _mirror_arm(self, arm_block: Image.Image, alex: bool = None):
        if alex is None:
            alex = self._is_alex_arm(arm_block)
        
        arm_elements_steve = {
            'top': Area(4, 0, 4, 4),
            'bottom': Area(8, 0, 4, 4),
            'front': Area(4, 4, 4, 12),
            'back': Area(12, 4, 4, 12),
            'right': Area(0, 4, 4, 12),
            'left': Area(8, 4, 4, 12),
        }
        arm_elements_alex = {
            'top': Area(4, 0, 3, 4),
            'bottom': Area(7, 0, 3, 4),
            'front': Area(4, 4, 3, 12),
            'back': Area(11, 4, 3, 12),
            'right': Area(0, 4, 4, 12),
            'left': Area(7, 4, 4, 12),
        }
        if alex:
            arm_elements = arm_elements_alex
        else:
            arm_elements = arm_elements_steve
        
        # mirror every area
        for element in arm_elements.keys():
            area = arm_elements[element]
            mirror_area(arm_block, area)
        # swap left and right area
        swap_area(arm_block, arm_block, arm_elements['left'], arm_elements['right'])

    def _mirror_leg(self, leg_block: Image.Image):
        self._mirror_arm(leg_block, alex=False)


    def swap_arms(self):
        alex = self.is_alex()
        self._mirror_arm(self.skin_blocks['rightArm'], alex)
        self._mirror_arm(self.skin_blocks['rightArm2'], alex)
        self._mirror_arm(self.skin_blocks['leftArm'], alex)
        self._mirror_arm(self.skin_blocks['leftArm2'], alex)

    def swap_legs(self):
        self._mirror_leg(self.skin_blocks['rightLeg'])
        self._mirror_leg(self.skin_blocks['rightLeg2'])
        self._mirror_leg(self.skin_blocks['leftLeg'])
        self._mirror_leg(self.skin_blocks['leftLeg2'])


    def _to_steve_arm(self, img_block: Image.Image):
        crop = crop_img(img_block, Area(6, 0, 9, 16))
        img_block.paste(crop, (7, 0))

        crop = crop_img(img_block, Area(14, 4, 2, 12))
        img_block.paste(crop, (15, 4))

        crop = crop_img(img_block, Area(10, 0, 2, 4))
        img_block.paste(crop, (11, 0))

    def _to_alex_arm(self, img_block: Image.Image):
        move_area(img_block, Area(11, 0, 2, 4), (10, 0))
        move_area(img_block, Area(15, 4, 2, 12), (14, 4))
        move_area(img_block, Area(7, 0, 9, 16), (6, 0))




