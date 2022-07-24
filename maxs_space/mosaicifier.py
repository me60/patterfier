import PIL
from PIL import Image, ImageDraw
import sys
import random

# GOAL: This program accepts images in the images directory beneath the working
# directory. It will print the width and height divisors of the image before
# using hard-coded values to "mosaic"-ify the image. There are 2 colour palettes
# available to apply to the mosaic tiles, average grayscale and average colour.
# These can be toggled simply by changing the code in the loops

# USAGE: This program accepts no command line arguments
# $ python mosaicifier

print(sys.argv[1:])

# TODO >
# - Inputs
#   - filename
#   - colour_palette
#   - mosaic_tile_size
# - Function Decomposition
# - Prime Dimension Handling

image = Image.open('images/bird.jpg')

# debug colours
neon_g = (0,255,0)
neon_b = (0,0,255)
neon_p = (254,1,154)

# a source version of the image where each pixel's colour is represented in rgb
# the image has to be converted to a drawing type image to draw in rectangular
# "tiles" that we re-colour on the fly
rgb_image = image.convert('RGB')
drw_img = ImageDraw.Draw(rgb_image)

# we'll need the dimensions later for iteration through pixels
width, height = rgb_image.size

widths = []
heights = []
print("width divisors:")
for i in range(2,width):
    if width % i == 0:
        widths.append(i)
        print(i)
print("height divisors:")
for i in range(2,height):
    if height % i == 0:
        heights.append(i)
        print(i)
if len(heights) == 0 or len(widths) == 0:
    print("prime dimension, tiling impossible")
    exit()

# this is changed to be the first element of comparisons as soon as it's set
lowest = 3000
tile_width = 0
tile_height = 0

# gets the closest square tiles available
# if there are multiple square tile sizes available, picks the smallest
for i in range(0,len(widths)):
    for j in range(0,len(heights)):
        current = abs(widths[i] - heights[j])
        if i == 0 and j == 0:
            lowest = current
            tile_width = widths[i]
            tile_height = heights[j]
        elif current < lowest:
            lowest = current
            tile_width = widths[i]
            tile_height = heights[j]

# tile dimension choosing not available yet, can change manually here though!
tile_width = 9
tile_height = 10

print("lowest pixel difference:",lowest,"width:",tile_width,"height:",tile_height)

total_tiles = int(int(width / tile_width) * int(height / tile_height))
print(total_tiles)

last_y = 0
last_x = 0
current_tile = []
rs = []
gs = []
bs = []

# returns (a,b,c)
def find_addends(red,green,blue):
    x = int((red + green + blue) / 3)
    vals = []
    limit = x * 3
    for i in range(0,3):
        r = random.randint(0, limit)
        limit = limit - r
        vals.append(r)
    return (vals[0],vals[1],vals[2])

# for each tile...
for i in range(0,total_tiles):
    # vertically iterate through the tile first...
    for y in range(last_y,(last_y+tile_height)):
        # ...then iterate through each row at that height...
        for x in range(last_x,(last_x+tile_width)):

            # get the rgb of each individual pixel
            r,g,b = rgb_image.getpixel((x,y))
            # calculate its weighted grayscale value (formula online)
            ag = int((0.299*r) + (0.587*g) + (0.114*b))
            # add it to the current tile's grayscale values
            current_tile.append(ag)
            # keep a hold of raw rgb values if average colour palette is to be
            # used
            rs.append(r)
            gs.append(g)
            bs.append(b)

            # if we're at the edge of the image then move down and back to the
            # left hand side of the image
            if x == width-1 and y == ((last_y+tile_height)-1):

                # should be a function!

                # calculates average red green and blue values for an entire
                # mosaic tile
                avgr = int(sum(rs) / len(rs))
                avggr = int(sum(gs) / len(gs))
                avgb = int(sum(bs) / len(bs))

                # current_tile stores average grayscale values for each pixel
                # within a tile

                # calculates average grayscale value for an entire mosaic tile
                avgg = sum(current_tile) / len(current_tile)
                # grayscale value between 1 and 10 (integer cast round)
                avg_grayscale_colour = int((avgg / 255) * 10)
                # amplify grayscale by 25 so it's easier to see

                avg_grayscale_colour = avg_grayscale_colour * 15

                a,b,c = find_addends(avgr,avggr,avgb)

                drw_img.rectangle([last_x,last_y,x,y], fill=((a),(b),(c)))
                str_col = str(avg_grayscale_colour)
                #drw_img.text((last_x, last_y), str_col)

                last_x = 0
                last_y = last_y + tile_height

                # should be a function!
                current_tile = []
                rs = []
                gs = []
                bs = []


            # if we've reached the bottom right of a tile, colour the tile and
            # move to the next one
            elif x == ((last_x+tile_width)-1) and y == ((last_y+tile_height)-1):

                # should be a function!
                avgr = int(sum(rs) / len(rs))
                avggr = int(sum(gs) / len(gs))
                avgb = int(sum(bs) / len(bs))
                avgg = sum(current_tile) / len(current_tile)
                avg_grayscale_colour = int((avgg / 255) * 10)
                avg_grayscale_colour = avg_grayscale_colour * 15
                a,b,c = find_addends(avgr,avggr,avgb)
                drw_img.rectangle([last_x,last_y,x,y], fill=((a),(b),(c)))
                str_col = str(avg_grayscale_colour)
                #drw_img.text((last_x, last_y), str_col)

                # should be a function!
                current_tile = []
                rs = []
                gs = []
                bs = []

                last_x = last_x + tile_width

rgb_image.save('images/last_processed.jpg')
rgb_image.show()
