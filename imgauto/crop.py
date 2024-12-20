import sys
import cv2
import numpy as np

from imgauto import cli, imgutil

VERSION = "1.0"
VERSION_DATE = "2021-11-28"


class ImgAutoCrop:
    """
    ImgAutoCrop()
    Crop an image removing rectangular black/white borders automagicly
    
    :image str: is a path string
    :target str: is a path string
    :tolerance int: is an int from 0 to 255
    :color int: is True/False depending if you want to cut the black or the white.
                to cut alpha channel, pass the string "alpha" to color
    :quality int: Quality on export (JPG, PNG compression...)

    USAGE:
    cropper = ImgAutoCrop("original.png", "cropped.png")
    cropper.run()

    ADVANCED:
    cropper = ImgAutoCrop("original.png", "cropped.png")
    if cropper.check():
        cropper.crop()
    """

    def __init__(self, original=None, target=None, tolerance=0, color=None, quality=None):
        self.path        = original
        self.target      = target
        self.tolerance   = tolerance
        self.cut_alpha   = (color == 'alpha')
        self.color       = color if not self.cut_alpha else 0
        self.quality     = quality
        self.crop_cords  = None
        self.image       = None
        self.imgarr      = None
        self.load()

    def run(self):
        """
        Do everything automaticly
        """
        if self.check():
            self.crop()

    def check(self):
        """
        Calculate colors and crop areas.
        Return False if can not crop, True if possible.
        """
        color = self.color
        if color is not None:
            if not self.check_color(self.imgarr, color):
                return False
        else:
            color = self.detect_color()
            if color is None:
                return False

        self.crop_cords = self.calc_crop(color)
        x0, y0, x1, y1 = self.crop_cords

        ox, oy = self.imgarr.shape
        if (x0 <= 0 and y0 <= 0 and x1 >= ox and y1 >= oy):
            # We havent changed the image size, so we are not going to crop it
            return False

        return True

    def crop(self):
        """
        Apply cropping (self.crop_cords) and save the result to self.target
        """
        if not self.crop_cords:
            if not self.check():
                raise ValueError("Can't crop the image")

        x0, y0, x1, y1 = self.crop_cords
        cropped = self.image[x0:x1, y0:y1]
        imgutil.save_image(cropped, self.target, quality=self.quality)

    def detect_color(self):
        """
        Detects if the image has white or black borders
        Returns 0 for black, 255 for white, None if can't detect
        """
        if self.check_color(self.imgarr, 0):
            return 0
        if self.check_color(self.imgarr, 255):
            return 255
        return None

    def check_color(self, arr, val):
        """Check for the corner value in arr"""
        return ((   arr[0][0] == val and arr[0][-1] == val)     # [| ] left
                or (arr[0][0] == val and arr[-1][0] == val)     # [‾‾] top
                or (arr[-1][0] == val and arr[-1][-1] == val)   # [__] bottom
                or (arr[0][-1] == val and arr[-1][-1] == val))  # [ |] right

    def load(self):
        """
        Loads self.image and self.imgarr
        """
        self.image  = cv2.imread(self.path, cv2.IMREAD_UNCHANGED)
        if self.cut_alpha:
            self.imgarr = self.load_alpha_channel(self.image)
        else:
            self.imgarr = np.array(cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY))

    def load_alpha_channel(self, image):
        """
        Returns the image array with 0 on the alpha pixels,
        1 for black and 255 for white.
        """
        # Validate if we actually have alpha channel
        if image.shape[2] < 4:
            raise ValueError("Image has no alpha channel")

        channels = cv2.split(image)
        alpha = channels[3]
        return alpha

    def calc_crop(self, color):
        """
        Returns (x0, y0, x1, y1) of crop area
        """
        tolerance = self.tolerance if not self.cut_alpha else 0
        imgarr    = self.imgarr

        # Mask of non-black pixels (assuming image has a single channel).
        mask = (imgarr < (255-tolerance)) if color > 127 else (imgarr > tolerance)

        # Coordinates of non-black pixels.
        coords = np.argwhere(mask)

        # Bounding box of non-black pixels.
        x0, y0 = coords.min(axis=0)
        x1, y1 = coords.max(axis=0) + 1   # slices are exclusive at the top

        return (x0, y0, x1, y1)

    def __str__(self):
        return f"ImageAutoCrop(cords={self.crop_cords}, target={self.path.rsplit('/', 1)[-1]})"

    def __repr__(self):
        return str(self)
