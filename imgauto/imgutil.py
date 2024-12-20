import cv2
from imgauto import config

def save_image(img, target, quality=None):
    """
    Save an OpenCV (cv2) image array to a file
    It automaticly detects the format from target extension
    """
    if target.lower().endswith('png'):
        cv2.imwrite(target, img,
                    [cv2.IMWRITE_PNG_COMPRESSION, quality or config.PNG_COMPRESSION])
    elif target.lower().endswith('jpg') or target.lower().endswith('jpeg'):
        cv2.imwrite(target, img,
                    [cv2.IMWRITE_JPEG_QUALITY, quality or config.JPG_QUALITY])
    elif target.lower().endswith('webp'):
        cv2.imwrite(target, img,
                    [cv2.IMWRITE_WEBP_QUALITY, quality or config.JPG_QUALITY])
    elif target.lower().endswith('tiff'):
        cv2.imwrite(target, img)
    else:
        raise ValueError(f"Can't detect image type on {target}")
