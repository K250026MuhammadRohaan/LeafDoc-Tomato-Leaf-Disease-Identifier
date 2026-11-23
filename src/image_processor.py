# ======================================================================
# image_processor.py
# LeafDoc - loads a leaf photo, prepares it and measures its colours.
# ======================================================================

import os
import numpy as np
from PIL import Image                      # Pillow: opens image files
from matplotlib.colors import rgb_to_hsv   # converts RGB colours to HSV

from exceptions import InvalidImageError

# Names of the 6 numbers (features) we measure from every leaf.
# The order here is the order used everywhere else in the project.
FEATURE_NAMES = [
    "brown_pct",         # % of leaf pixels that look brown
    "yellow_pct",        # % of leaf pixels that look yellow
    "green_pct",         # % of leaf pixels that look green
    "mean_hue",          # average hue (colour type)
    "mean_saturation",   # average saturation (how strong the colour is)
    "mean_brightness",   # average brightness (value)
]


class ImageProcessor:
    """Loads a photo, prepares it, and turns it into colour features."""

    def __init__(self, image_size=(128, 128)):
        # Private attribute (starts with _): the size every photo is resized to
        self._image_size = image_size

    # ------------------------------------------------------------------
    def load_image(self, path):
        """Open the file and return it as a 3D NumPy array (height, width, 3).

        Raises InvalidImageError if the file is missing, not an image or broken.
        """
        # 1) Does the file exist?
        if not os.path.isfile(path):
            raise InvalidImageError("File not found: " + str(path))

        # 2) Does it have an image extension?
        if not path.lower().endswith((".jpg", ".jpeg", ".png")):
            raise InvalidImageError("Not a .jpg/.png image file: " + str(path))

        # 3) Can Pillow really open it? (a renamed text file will fail here)
        try:
            with Image.open(path) as img:
                img.verify()                       # checks the file is not damaged
            with Image.open(path) as img:          # verify() closes the file, so reopen
                rgb_image = img.convert("RGB")     # make sure we have 3 colour channels
                return np.array(rgb_image)         # picture -> NumPy array
        except (OSError, SyntaxError, ValueError) as error:
            raise InvalidImageError("Damaged or invalid image: " + str(path)) from error

    # ------------------------------------------------------------------
    def preprocess(self, image):
        """Resize -> scale to 0-1 -> change colours from RGB to HSV."""
        # Resize to the size we chose (128 x 128)
        small = Image.fromarray(image).resize(self._image_size)
        # Pixel values are 0-255; dividing by 255 scales them to 0-1 (normalise)
        scaled = np.array(small) / 255.0
        # RGB -> HSV. Result is still shape (128, 128, 3) with values 0-1
        hsv_image = rgb_to_hsv(scaled)
        return hsv_image

    # ------------------------------------------------------------------
    def extract_features(self, hsv_image):
        """Measure the leaf colours. Returns a dict {feature name: number}.

        Everything is done with boolean masks (True/False arrays).
        """
        # Slice the 3 channels (channel slicing)
        hue = hsv_image[:, :, 0]
        saturation = hsv_image[:, :, 1]
        brightness = hsv_image[:, :, 2]

        # Mask of "leaf pixels": we ignore very pale/grey (background) and very dark pixels
        leaf_mask = (saturation > 0.15) & (brightness > 0.15)
        leaf_count = leaf_mask.sum()   # how many True values (leaf pixels)

        if leaf_count == 0:
            raise InvalidImageError("No leaf colours found in this image.")

        # Colour masks (hue is between 0 and 1 in HSV):
        #   brown  = orange-ish hue and not too bright
        #   yellow = yellow hue
        #   green  = green hue
        brown_mask = leaf_mask & (hue >= 0.02) & (hue < 0.11) & (brightness < 0.75)
        yellow_mask = leaf_mask & (hue >= 0.11) & (hue < 0.19)
        green_mask = leaf_mask & (hue >= 0.19) & (hue < 0.45)

        features = {
            # percentage = number of True pixels / leaf pixels * 100
            "brown_pct": 100.0 * brown_mask.sum() / leaf_count,
            "yellow_pct": 100.0 * yellow_mask.sum() / leaf_count,
            "green_pct": 100.0 * green_mask.sum() / leaf_count,
            # average colour values, only over the leaf pixels
            "mean_hue": float(hue[leaf_mask].mean()),
            "mean_saturation": float(saturation[leaf_mask].mean()),
            "mean_brightness": float(brightness[leaf_mask].mean()),
        }
        return features

    # ------------------------------------------------------------------
    def get_features(self, path):
        """Calls all necessary functions on path, with one function call."""
        image = self.load_image(path)
        hsv_image = self.preprocess(image)
        return self.extract_features(hsv_image)
