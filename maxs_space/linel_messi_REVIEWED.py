# !! I'll mark any comments I've written with !!
# !! I hope I don't come across as too much of a fanny with the instruction-like
# syntax in my comments - with small suggestions it's easier just to point them
# out

import PIL
from random import randrange
from PIL import Image, ImageDraw, ImageFont

image = Image.open('images/bird.jpg')

# !! With a program like this, it's entirely possible that you will revisit
# specific functionality a few months down the line. Names like width and height
# might seem lengthy, but save time in the long run. Also, single character
# variable names are typically used locally (within functions), to refer to
# loop parameters (like 'x' and 'y') and generic counters (usually referenced
# with 'c') - I had a global single-named character in patterfier that was
# causing an extremely irritating bug within a function - speaking from very
# recent experience here.
a, b = image.size

lino = Image.new(mode="RGB", size=(a, b), color = (256, 256, 256))

# !! This function is a little large - much of this functionality can be
# separated out. This helps a ton with future debugging if you're revisiting
# functionality.
def line_drawer_vertical():

    # !! When going with amount variables, I use something like 'noof_', but
    # this has little bearing. However, we might want to separate out input
    # validation into a different function and pass the sanitised values into
    # this function as a parameter.
    how_many_tones = int(input('how many tones?: ' ))

    # !! 'list' is redundant.
    list_avg_tones = []
    list_tile_coords = []

    # !! good use of naming here.
    tile_width = 112
    tile_height = 112

    # !! You'll need to define these globally (outside of the scope of any
    # function) if you choose to decompose further.
    rgb_image = image.convert('RGB')
    pixels = rgb_image.load()
    draw_image = ImageDraw.Draw(lino)

    # !! Off the top of my head there are some image file types where retrieving
    # the dimensions is a non-constant operation - it's safer to get these
    # values once at the beginning (more efficient).
    width, height = image.size
    int(width)
    int(height)

    # !! Keep whitespace formatting consistent (spaces between '=' - it doesn't
    # matter what formats you use, it does matter that you use the same format
    # everywhere - you might want to look into a linter? (I don't use one but
    # they're good if you don't want to worry about pretty code as you're
    # writing it)).
    rs=[]
    gs=[]
    bs=[]

    total_cells = int(int(width/tile_width)*int(height/tile_height))

    last_x = 0
    last_y = 0

    for i in range(0, total_cells):

        for y in range(last_y,(last_y +tile_height)):

            for x in range(last_x, (last_x+tile_width)):

                r,g,b = rgb_image.getpixel((x, y))

                rs.append(r)
                gs.append(g)
                bs.append(b)

                # !! Use (parentheses) as much as possible with any kind of
                # compound conditional (if statement that includes one or more
                # separated 'and' or 'or' delimited clauses) - this will
                # improve readability and make the fine grained logic less
                # error prone
                if x == width-1 and y == ((last_y+tile_height)-1):

                    avg_r = int(sum(rs)/len(rs))
                    avg_gr = int(sum(gs)/len(gs))
                    avg_b = int(sum(bs)/len(bs))

                    # !! Good use of (parentheses) but I'd include a bit more
                    # spacing if I wasn't intimately familiar with what this
                    # does
                    average_tone = int(((avg_r)+(avg_gr)+(avg_b))/3)

                    coords = [last_x, last_y, x, y]

                    list_tile_coords.append(coords)

                    last_x = 0

                    last_y = last_y + tile_height

                    rs = []
                    gs = []
                    bs = []

                    list_avg_tones.append(average_tone)

                if x == ((last_x+tile_width)-1) and y == ((last_y+tile_height)-1):

                    avg_r = int(sum(rs)/len(rs))
                    avg_gr = int(sum(gs)/len(gs))
                    avg_b = int(sum(bs)/len(bs))

                    average_tone = int(((avg_r)+(avg_gr)+(avg_b))/3)

                    coords = [last_x, last_y, x, y]

                    list_tile_coords.append(coords)

                    last_x = last_x + tile_width

                    # !! I believe these can be put beneath the conditionals to
                    # get rid of some lines
                    rs = []
                    gs = []
                    bs = []

                    list_avg_tones.append(average_tone)

    max_tone = max(list_avg_tones)

    # !! This codeblock appears to be the beef of this algorithm - without
    # comments it's very difficult to understand what's going on here. I can
    # see how it translates to an output visually - it's very impressive what
    # you've done, but this algorithm needs refinement if you're going to
    # keep working with it.
    # ~
    # Good use of j and k as loop parameter names - these are used discipline-
    # wide.
    for j in range(total_cells):
        list = []

        # !! Why index from 1?
        for i in range(1, how_many_tones+1):
            y = (max_tone/how_many_tones)*i
            list.append(y)

        # !! I have no fucking clue what's going on here (not being mean-
        # spirited).
        # ~
        # Inline lambdas, Laurie? What is this? Stanford? The problem I find
        # with lambdas is that they almost always need accompanying comments -
        # only in some cases are they easier to read - they do tend to be more
        # succinct and less error prone on average, so congrats for branching
        # out - a lot of people avoid them but they're smart.
        index = list[min(range(len(list)), key = lambda i: abs(list[i]-list_avg_tones[j]))]

        # !! The +1,-1 'flip-flop' logic is great for getting something to work,
        # but horrible to look at later on for figuring out what something does.
        # With indices arithmetic you need to make sure each line is on the
        # same page as the last line - a bit difficult to appreciate this
        # concept in writing. Since your knowledge of the process executed in
        # this codeblock is far more intimate than mine, I'm sure it won't be
        # tricky to simplify this a little
        tone = list.index(index)+1
        a,b,c,d = list_tile_coords[j]
        for k in range(1, how_many_tones-tone+1):
            wedges = how_many_tones - tone+1
            x_coords = a+((c-a)/wedges)*k
            draw_image.line([x_coords, b, x_coords, d], fill = 0, width = 1)

    lino.show()
    return lino

def line_drawer_horizontal(vertical_image):
    how_many_tones = int(input('how many tones?: ' ))

    list_avg_tones = []
    list_tile_coords = []

    # !! A separate function should be used to handle tile size and hard coded
    # config so you don't have to jump around the program to change things
    # when you load in a new image. Eventually, the program should be able to
    # deduce hard coded constants for each image without having to change
    # anything - but this is a later optimisation for user experience more than
    # anything else.
    tile_width = 112
    tile_height = 112

    rgb_image = image.convert('RGB')

    pixels = rgb_image.load()

    draw_image = ImageDraw.Draw(vertical_image)

    width, height = image.size
    int(width)
    int(height)

    rs=[]
    gs=[]
    bs=[]

    total_cells = int(int(width/tile_width)*int(height/tile_height))

    last_x = 0
    last_y = 0

    for i in range(0, total_cells):

        for y in range(last_y,(last_y +tile_height)):

            for x in range(last_x, (last_x+tile_width)):

                r,g,b = rgb_image.getpixel((x, y))

                rs.append(r)
                gs.append(g)
                bs.append(b)

                if x == width-1 and y == ((last_y+tile_height)-1):

                    avg_r = int(sum(rs)/len(rs))
                    avg_gr = int(sum(gs)/len(gs))
                    avg_b = int(sum(bs)/len(bs))

                    average_tone = int(((avg_r)+(avg_gr)+(avg_b))/3)

                    coords = [last_x, last_y, x, y]

                    list_tile_coords.append(coords)

                    last_x = 0

                    last_y = last_y + tile_height

                    rs = []
                    gs = []
                    bs = []

                    list_avg_tones.append(average_tone)

                if x == ((last_x+tile_width)-1) and y == ((last_y+tile_height)-1):

                    avg_r = int(sum(rs)/len(rs))
                    avg_gr = int(sum(gs)/len(gs))
                    avg_b = int(sum(bs)/len(bs))

                    average_tone = int(((avg_r)+(avg_gr)+(avg_b))/3)

                    coords = [last_x, last_y, x, y]

                    list_tile_coords.append(coords)

                    last_x = last_x + tile_width

                    rs = []
                    gs = []
                    bs = []

                    list_avg_tones.append(average_tone)

    max_tone = max(list_avg_tones)

    # !! This codeblock can be decomposed into its own function but I'm sure
    # you know that.
    for j in range(total_cells):
        list = []
        for i in range(1, how_many_tones+1):
            y = (max_tone/how_many_tones)*i
            list.append(y)
        index = list[min(range(len(list)), key = lambda i: abs(list[i]-list_avg_tones[j]))]
        tone = list.index(index)+1
        a,b,c,d = list_tile_coords[j]
        for k in range(1, how_many_tones-tone+1):
            wedges = how_many_tones - tone+1
            y_coords = b+((d-b)/wedges)*k
            draw_image.line([a, y_coords, c, y_coords], fill = 0, width = 1)

    vertical_image.show()

line_drawer_horizontal(line_drawer_vertical())

# !! Overall, the functionality you've added is brilliant initiative - I'm
# excited to see how this could be used for patterfier. Only some comments on
# general readability - the comments on your algorithm design could do with an
# in-person consultation as I could find myself sitting here writing an essay
# on how it's to be done, and I don't want to do that (saves you and me both
# of having to write *and* read that).

# For coding in general, I'd focus on some basic commenting and readability,
# function decomposition (I get that this is proof of concept, but I felt it was
# worth commenting on), and instance-derived config values that are currently
# implemented as hard-coded values (I also think you know this, also thought it
# might be of use commenting on).
