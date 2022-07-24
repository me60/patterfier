# import, import as, from import
import PIL
import os
import sys
import imageio
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from random import randrange
from scipy import ndimage
from math import pow
from math import sqrt
from input_validation import validate

# GOAL: This program will accept images in the images directory underneath the
# working directory. It accepts two command line arguments, the first being a
# path to the image that is used as the pattern overlay, with the second being
# the image that the overlay will be applied to.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The program will first manipulate the overlay image such that suitably energy
# dense regions of the image are coloured in an averaged grayscale palette. We
# reduce the energy-applied regions to grayscale values between 1 and 10,
# intensifying the grayscale quality of the pixels with values >= 5 such that
# they are the same extent of black, with those coming in at a value < 5 simply
# being removed.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Once the pattern overlay has had the energy algorithm applied to it in the way
# we just laid out, we determine the "neighborhoods" of the energy-normalised
# pattern overlay image. These are the contiguous regions between energy-marked
# borders that will be used for the "cut and colour" procedure used on the
# second argument-supplied image. We will first attempt to use a span fill
# method of "[flood filling](https://en.wikipedia.org/wiki/Flood_fill)"
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Overlays will be located in the overlays folder and will be named as so:
# <name>_<repeat_no>_<width>_<height>(_processed)
# Where:
#   - <name> : is just a name that is appropriate for what the overlay is
#   - <repeat_no> : is an autonumber for the # of repetitions of the <name>
#     that exist in the overlays directory
#   - <width>,<height> : image dimensions
#   - (_processed) : if the image has been fed through the energy normalisation
#   - process and can be immediately used for the purposes of cut and colour
#     (further optimisations can be made in the persisted state of the already
#     processed image - for instance, seamless boundaries between neighborhoods
#     will be calculated in the same way for each time a new image is used
#     against an already "processed" overlay)

# USAGE:
# $ python patterfier_v1.py <pattern_overlay_path> <image_path>

# CONSTRAINTS:
# - Pattern overlays must be of the exact same dimensions as the image
# - Patterns need not contain closing shapes as the edges of images are
#   definite in shape closing

# geo4 and phrog3 are the SAME DIMENSIONS! USE A NOISE THRESHOLD OF 300 TO WORK

overlay_img = Image.open('overlays/geo17_2.png')
# !!! USE rgb_img FOR VIEWING AND SAVING IMAGES !!!
rgb_img = overlay_img.convert('RGB')
# !!! USE drw_img FOR IMAGE DRAW LIBRARY CALLS !!!
drw_img = ImageDraw.Draw(rgb_img)
# !!! USE pixels TO RECOLOUR SINGLE PIXELS !!!
pixels = rgb_img.load()
WIDTH, HEIGHT = rgb_img.size

# jfifs and jpgs work
target_img = Image.open('images/science2.png')
target_rgb_img = target_img.convert('RGB')
target_drw_img = ImageDraw.Draw(target_rgb_img)
pixels_2 = target_rgb_img.load()
WIDTH_2, HEIGHT_2 = target_rgb_img.size

c1 = 0
c2 = 0
c3 = 0

VIEW_AS_GIF = False

#if (WIDTH != WIDTH_2 or HEIGHT != HEIGHT_2):
    #print("Ensure the overlay and target image possess the same dimensions")
    #exit()

# Opens the default image viewer of machine OS to show the manipulated overlay
# image
def show_overlay_img():
    rgb_img.show()

# Does the above for the final image, i.e. overlay applied to image,
# neighborhood average tones are captured and those areas are filled with their
# average tone
def show_final_image():
    target_rgb_img.show()

# A pretty sorry excuse of avoiding exception handling...
def foo():
    return

# Removes an element if it exists without throwing an error
def rmv(value, list):
    try:
        list.remove(value)
        return list
    except ValueError:
        foo()
    return list

# Detects which (if any) elements of the convolution kernel will be out of
# bounds and returns a list of strings that will contain the codes of the
# elements that are in bounds (for a given pixel at dimensions x and y)
def derive_kernel(x, y):
    ret = ['TL','TM','TR','ML','MR','BL','BM','BR']
    if (x-1 < 0):
        ret = rmv('TL', ret)
        ret = rmv('ML', ret)
        ret = rmv('BL', ret)
    if (x+1 == WIDTH):
        ret = rmv('TR', ret)
        ret = rmv('MR', ret)
        ret = rmv('BR', ret)
    if (y-1 < 0):
        ret = rmv('TL', ret)
        ret = rmv('TM', ret)
        ret = rmv('TR', ret)
    if (y+1 == HEIGHT):
        ret = rmv('BL', ret)
        ret = rmv('BM', ret)
        ret = rmv('BR', ret)
    return ret

# Returns the single grayscale colour for a pixel from the image - dimensions
# supplied simply as x and y
def grayscale(x, y):
    # RGB from the image
    r,g,b = rgb_img.getpixel((x,y))
    # calculate its weighted grayscale value (formula online)
    return int((0.299*r) + (0.587*g) + (0.114*b))

# Bases are the standard sobel convolution kernel
KERNEL_X_BASE = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
KERNEL_Y_BASE = [1, 2, 1, 0, 0, 0, -1, -2, -1]

# Between 1 and 1000, this value influences the relationship between noise
# sensitivity and accentuated edge sharpness. This value would normally be
# dictated by an AI or noise cancellation algorithm, but we'll let the user
# choose its value for now
NOISE_THRESHOLD = 260

# Codes
# TL ~ x-1,y-1 : TM ~ x,y-1 : TR ~ x+1,y-1
# ML ~ x-1,y : MM ~ x,y : MR ~ x+1,y
# BL ~ x-1,y+1 : BM ~ x,y+1 : BR ~ x+1,y+1
# Base Kernel Indexes
# +-------+
# | 0 1 2 |
# | 3 4 5 |
# | 6 7 8 |
# +-------+

#   Sobel Refine
#   ^^^^^^^^^^^^
#   Dictate the appropriate noise - sharpness ratio and colour the edges black
def sobel_refine(accumulators):
    for x in range(0,WIDTH):
        for y in range(0,HEIGHT):
            # mill-entise the accumulators for fine colloquial refinement
            accumulators[y][x] = ((accumulators[y][x] / 255) * 100)
            if accumulators[y][x] >= NOISE_THRESHOLD:
                # white
                pixels[x,y] = (255,255,255)
                #pixels[x,y] = (0,0,0)
            else:
                # black
                if VIEW_AS_GIF == True:
                    persistMidEnergy()
                pixels[x,y] = (0,0,0)
                #pixels[x,y] = (255,255,255)
    print(" >> Applied Sobel Refinement and Enhancement << ")
    #show_overlay_img()
    span_fill_capture()

#   Sobel Cut
#   ^^^^^^^^^
#   Apply sobel edge detection, colouring energy areas in black, everything
#   else in white
def sobel_cut():
    # These are our accumulators for both directions of the sobel filter
    # application
    kernel_x_sq = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]
    kernel_y_sq = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]

    # This will be calculated at the end of each iteration where each element is
    # the square root of its equivalent kernel_x_sq kernel_y_sq
    kernel_both_sqrt = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]

    for x in range(0, WIDTH):
        for y in range(0, HEIGHT):
            base_grayscale = grayscale(x, y)

            if VIEW_AS_GIF == True:
                persistEnergy()

            # 2d array convention to be followed in this loop !! thing[y][x] !!

            # Depending on the boundaries present with the current kernel, only
            #z   apply the calculation to affected pixels
            bounded_dims = derive_kernel(x, y)
            kernel_x_sq[y][x] += pow((KERNEL_X_BASE[4] * base_grayscale), 2)
            kernel_y_sq[y][x] += pow((KERNEL_Y_BASE[4] * base_grayscale), 2)

            print('sobel_cut -> ', x,' + ', y)

            # Switch statement for matched boundary cases
            for i in bounded_dims:
                if i == 'TL':
                    kernel_x_sq[y-1][x-1] += pow((KERNEL_X_BASE[0] * base_grayscale), 2)
                    kernel_y_sq[y-1][x-1] += pow((KERNEL_Y_BASE[0] * base_grayscale), 2)
                if i == 'TM':
                    kernel_x_sq[y-1][x] += pow((KERNEL_X_BASE[1] * base_grayscale), 2)
                    kernel_y_sq[y-1][x] += pow((KERNEL_Y_BASE[1] * base_grayscale), 2)
                if i == 'TR':
                    kernel_x_sq[y-1][x+1] += pow((KERNEL_X_BASE[2] * base_grayscale), 2)
                    kernel_y_sq[y-1][x+1] += pow((KERNEL_Y_BASE[2] * base_grayscale), 2)
                if i == 'ML':
                    kernel_x_sq[y][x-1] += pow((KERNEL_X_BASE[3] * base_grayscale), 2)
                    kernel_y_sq[y][x-1] += pow((KERNEL_Y_BASE[3] * base_grayscale), 2)
                if i == 'MR':
                    kernel_x_sq[y][x+1] += pow((KERNEL_X_BASE[5] * base_grayscale), 2)
                    kernel_y_sq[y][x+1] += pow((KERNEL_Y_BASE[5] * base_grayscale), 2)
                if i == 'BL':
                    kernel_x_sq[y+1][x-1] += pow((KERNEL_X_BASE[6] * base_grayscale), 2)
                    kernel_y_sq[y+1][x-1] += pow((KERNEL_Y_BASE[6] * base_grayscale), 2)
                if i == 'BM':
                    kernel_x_sq[y+1][x] += pow((KERNEL_X_BASE[7] * base_grayscale), 2)
                    kernel_y_sq[y+1][x] += pow((KERNEL_Y_BASE[7] * base_grayscale), 2)
                if i == 'BR':
                    kernel_x_sq[y+1][x+1] += pow((KERNEL_X_BASE[8] * base_grayscale), 2)
                    kernel_y_sq[y+1][x+1] += pow((KERNEL_Y_BASE[8] * base_grayscale), 2)

                # Calculate the relevant Sobel energy in-place
                kernel_both_sqrt[y][x] = sqrt(kernel_x_sq[y][x] + kernel_y_sq[y][x])

    print(" >> Applied Sobel Filter in its Raw Form << ")
    # Allow the user to see the refinement level by changing constants
    sobel_refine(kernel_both_sqrt)

#   Sobel Direction Projection
#   ^^^^^^^^^^^^
#   Scan neighbourhood borders with a discovery kernel, travelling in accordance
#   with Sobel directionality - repeat for each neighborhood border. When a gap
#   is noticed, project a phantom kernel in the last calculated Sobel direction
#   of the border until another edge is discovered, draw a single pixel to
#   bridge the borders
def sobel_project():
    return

#   Seam Thinning
#   ^^^^^^^^^^^^^
#   use x algorithm to thin each seam to 1 pixel
def thin_seams():
    return

# 1 = black/out-of-bounds, 2 = unexplored (white), 3 = seed (already considered
# for future recurse) for a specific x,y coordinate
def get_border_code(x, y, seeds):
    if (x,y) in seeds:
        return (x,y,3)

    # If it's out of bounds, it's a 1
    if ((x < 0) or (y < 0) or (x > (WIDTH-1)) or (y > (HEIGHT-1))):
        return (x,y,1)

    r,g,b = rgb_img.getpixel((x,y))

    # Black and very dark grey pixels detected as 1s
    if ((r == 0 and g == 0 and b == 0) or (r == 255 and g == 0 and b == 0)):
        return (x,y,1)

    # At this stage, it must be a 2 (white pixel)
    if (r == 255 and g == 255 and b == 255):
        return (x,y,2)

neighborhoods = []
global m

#   Span Fill Capture
#   ^^^^^^^^^^^^^^^^^
#   Use span filling with neighbourhood objects that have a pixel list
#   attribute that should be filled with the pixel coordinates. Extend each span
#   in the direction of each border by half the border width.
def span_fill_capture():

    # Find a white pixel
    m = 0
    for x in range(WIDTH):
        for y in range(HEIGHT):
            r,g,b = rgb_img.getpixel((x,y))

            # If we encounter a white pixel, start capturing
            if (r == 255 and g == 255 and b == 255):

                if VIEW_AS_GIF == True:
                    persistFillCapture()

                # Where we start - this is a dynamic tuple that could take
                # coordinates from a seed later on, to start with, this will
                # always be the upper-then-leftmost white pixel in a given
                # neighborhood
                direction = (x,y)

                # The pixel coordinates of each pixel in the neighborhood - this
                # gets added to the neighborhoods list when the last pixel in
                # the neighborhood is discovered
                neighborhood = []

                # This is the first pixel in the neighborhood - get its
                # colour and put it into the current neighborhood's list
                neighborhood.append(direction)

                # As we go through each neighborhood, if there are multiple
                # pixels around the current that are white, we explore the first
                # and store the unexplored in this array. Should we run into an
                # area of the neighborhood near completely encased in black, we
                # can traverse to a seed in the array to continue capturing
                seeds = []

                # This is the loop that captures a neighborhood
                while (True):

                    if VIEW_AS_GIF == True:
                        persistFillCapture()

                    #print(len(neighborhoods))

                    # Get the current direction's pixel - for any new
                    # neighborhood, this will be x and y from white-searching
                    current_x,current_y = direction
                    neighborhood.append(direction)

                    r,g,b = rgb_img.getpixel(direction)
                    #print(">>> neighborhood: ", m, " --- ", direction, " colour: ", r,g,b)

                    # Colour the current pixel black on the overlay so it is not
                    # accidentally found when searching for the next
                    # neighborhood
                    pixels[current_x,current_y] = (255,0,0)

                    # This is filled with area around the pixel in order:
                    # 0 : Directly Above
                    # 1 : Directly Below
                    # 2 : Left
                    # 3 : Right
                    current_borders = []
                    current_borders.append(get_border_code(current_x,current_y-1,seeds))
                    current_borders.append(get_border_code(current_x,current_y+1,seeds))
                    current_borders.append(get_border_code(current_x-1,current_y,seeds))
                    current_borders.append(get_border_code(current_x+1,current_y,seeds))

                    # We need these booleans for some conditions later
                    two_found = False
                    three_found = False

                    # The coordinates of the next pixel...
                    direction = ()

                    # ...we also need a generic counter
                    c = 0

                    # ...and an escape boolean
                    exit = False

                    # Get what's around the current pixel to:
                    # a) choose a white pixel as a new direction to travel to if
                    #    one exists
                    # b) generate a new seed if there is one so that we may
                    #    travel to it if we run into a wall later on
                    # c) choose a seed encountered around the pixel to travel to
                    #    if there is one
                    for i in current_borders:
                        around_x,around_y,code = i
                        c = c + 1
                        #print(around_x,around_y,code)

                        if (code == 3):
                            three_found = True

                        # This is when a white pixel has already been found
                        # around the current, so the new white pixel is turned
                        # into a seed for the future
                        if ((code == 2) and (two_found == True)):
                            seeds.append((around_x,around_y))

                        if (code == 2 and (two_found == False) and (exit == False)):
                            direction = (around_x,around_y)
                            two_found = True
                            exit = True

                    # Direction will be chosen at this point if exit is true -
                    # locate next pixel
                    if (exit == True):
                        continue

                    # If there are no white pixels around and there are no
                    # coordinates left as seeds, we can say with 100% assurance
                    # that the current neighborhood is filled - search for next
                    # by adding the current neighborhood to the neighborhoods,
                    # setting x and y to 0, and breaking
                    if ((two_found == False) and (len(seeds) == 0)):
                        m = m + 1
                        neighborhoods.append(neighborhood)
                        # Search for the next white pixel by zeroing x and y for
                        # next iteration of white-searching (inefficient - we
                        # can wall/sobel project to find adjacent neighborhoods)
                        x = 0
                        y = 0
                        break

                    # If there are no white pixels around but there are still
                    # seeds, make the direction the first seed encountered
                    if ((two_found == False) and (len(seeds) != 0)):
                        direction = seeds.pop(0)

    print(">>> Finished Capturing Neighborhoods <<<")
    # This point will naturally be reached when there are no white pixels left
    span_fill_colour()

#   Span Fill Persist
#   ^^^^^^^^^^^^^^^^^
# - This is done for all detected neighborhoods, once done, the pixel values
#   are written to a file such that they can be used again for the same pattern
#   but a different image
def span_fill_persist():
    return

#   Span Fill Colour
#   ^^^^^^^^^^^^^^^^
# - The neighborhood objects, loaded into memory, are iterated over. Pixel
#   colours are captured, averaged, and recoloured with their average
def span_fill_colour():

    print("here?")

    # This can be made more efficient by storing target colours and averaging as
    # we go along when capturing

    avg_rs = []
    avg_gs = []
    avg_bs = []

    for n in neighborhoods:
        rs = []
        gs = []
        bs = []
        noof_pixels = len(n)
        c = 0
        for pixel in n:
            x,y = pixel
            r,g,b = target_rgb_img.getpixel((x,y))
            rs.append(r)
            gs.append(g)
            bs.append(b)
            if (c == (noof_pixels-1)):
                # calculates average red green and blue values for an entire
                # neighborhood tile
                avgr = int(sum(rs) / len(rs))
                avggr = int(sum(gs) / len(gs))
                avgb = int(sum(bs) / len(bs))
                color = (avgr,avggr,avgb)
                avg_rs.append(avgr)
                avg_gs.append(avggr)
                avg_bs.append(avgb)
                for target_pixel in n:
                    x_t,y_t = target_pixel
                    pixels_2[x_t,y_t] = color
            c = c + 1

    print(">>> Finished Colouring Neighborhoods <<<")

    black = (0,0,0)

    o_avg_r = int(sum(avg_rs) / len(avg_rs))
    o_avg_g = int(sum(avg_gs) / len(avg_gs))
    o_avg_b = int(sum(avg_bs) / len(avg_bs))

    for x in range(WIDTH):
        for y in range(HEIGHT):
            r,g,b = rgb_img.getpixel((x,y))
            #print(r,g,b)
            if (r == 0 and g == 0 and b == 0):
                pixels_2[x,y] = (o_avg_r,o_avg_g,o_avg_b)
                #pixels_2[x,y] = (255,255,255)

    print(">>> Finished Colouring Trim <<<")
    show_final_image()
    persist()

#   Processing Energy Persist
#   ^^^^^^^^^^^^^^^^^^^^^^^^^
# - The last image is viewed and saved (neighborhoods filled bit by bit)
def persistMidEnergy():
    global c1
    c1 += 1
    rgb_img.save('images/last_animation/1' + str(c1) + '.jpg')

#   Energy Persist
#   ^^^^^^^^^^^^^
# - The last image is viewed and saved (neighborhoods filled bit by bit)
def persistEnergy():
    global c2
    c2 += 1
    rgb_img.save('images/last_animation/2' + str(c2) + '.jpg')

#   Neighborhood Fill Persist
#   ^^^^^^^^^^^^^^^^^^^^^^^^^
# - The last image is viewed and saved (neighborhoods filled bit by bit)
def persistFillCapture():
    global c3
    c3 += 1
    target_rgb_img.save('images/last_animation/3' + str(c3) + '.jpg')
    aa

#   Image Persist
#   ^^^^^^^^^^^^^
# - The last image is viewed and saved (neighborhoods filled bit by bit)
def persistFinal():
    target_rgb_img.save('images/last_processed.jpg')

# If gif is toggled, images of the process are captured and saved to a separated
# directory. This function iterates over these images to produce a gif
def viewAsGif():
    if VIEW_AS_GIF == False:
        return
    images = []
    for filename in filenames:
        images.append(imageio.imread(('/images/' + filename)))
    imageio.mimsave('last_done.gif', images)

# Call Order
# ----------
sobel_cut()
viewAsGif()

# Graveyard
# ~
# for y in range(0, HEIGHT):
#     print(y)
#     neighborhood = {}
#     for x in range(0, WIDTH):
#         coord_here_joined_existing_neighborhood = False
#         r,g,b = rgb_img.getpixel((x,y))
#         neighborhood = {}
#         if (r == 255 and g == 255 and b == 255):
#             #print(x,y)
#             for n in neighborhoods:
#                 if ((((y-1) > -1) and ((x,y-1) in n)) or (((x-1) > -1) and ((x-1,y) in n))):
#                     # This should be a new entry in an already existing
#                     # neighborhood
#                     n[x,y] = True
#                     coord_here_joined_existing_neighborhood = True
#                     break
#             if (coord_here_joined_existing_neighborhood == False):
#                 neighborhood[x,y] = True
#                 neighborhoods.append(neighborhood)
# ~
# if ((three_found == True) and (two_found == True) and (c == 3) and (exit == False)):
#     for j in current_borders:
#         seed_x,seed_y,code = j
#         if (code == 3):
#             direction = seeds[seeds.index((seed_x,seed_y))]
#             seeds.remove((seed_x,seed_y))
#             exit = True
