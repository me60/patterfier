import PIL
import os
import sys
from PIL import Image, ImageDraw

class Neighborhood:
    pixels = []
    def persist():
        # writes the pattern neighborhood list to memory
