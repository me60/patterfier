import PIL

# Above line is redundant if we're importing specifically what we need with
# the below import statement
from PIL import Image, ImageDraw, ImageFont, ImageOps

image = Image.open('images/bwleaf.png')
image = image.convert('RGB')
target_image = Image.open('images/svettyeye.png')
target_image = target_image.convert('RGB')

seeds = []
neighbourhoods = []
black_space = []

# curious portion of code here
for i in range(image.size[0]):
    for j in range(image.size[1]):
        if image.getpixel((i,j)) == (0,0,0):
            black_pixel = i,j
            black_space.append(black_pixel)

neighbourhoods.append(black_space)

def seed_finder(pixel, direction, white_space):
    # max: interesting decision to check borders around a direction before it's
    # travelled to, you wouldn't need the line below the one below this one if
    # you did this when the direction is considered a current. This kind of
    # relativistic programming can be error prone
    directions = [(0,-1),(1,0),(0,1),(-1,0)]
    directions.remove(direction)
    for i in range(len(directions)):
        point = tuple_adder(directions[i], pixel)
        if point in white_space and point not in neighbourhoods and point not in seeds:
            seeds.append(point)

def tuple_adder(point_a,point_b):
    c = point_a[0]+point_b[0]
    d = point_a[1]+point_b[1]
    new_point = c,d
    return new_point

def white_finder():
    white_space = []
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if image.getpixel((i,j)) == (255,255,255):
                white_pixel = i,j
                white_space.append(white_pixel)
    return white_space
#function returns a list of every coordinate of every white pixel in the pattern image
# max: these comments usually go above the function they're about

def direction_finder(point):
    x,y = point
    surrounding_white = []
    a = x,y-1
    b = x+1,y
    c = x,y+1
    d = x-1,y
    if a in white_finder():
        surrounding_white.append((0,-1))
    if b in white_finder():
        surrounding_white.append((1,0))
    if c in white_finder():
        surrounding_white.append((0,1))
    if d in white_finder():
        surrounding_white.append((-1,0))

    if len(surrounding_white) == 0:
        return []

    else:
        return surrounding_white
#function takes a point and returns direction vector of first white pixel in clockwise order

def neighbourhood_finder(white_space):
    current_neighbourhood = []
    point = white_finder()[0]
    while (len(direction_finder(point)) > 0):
        direction_vector = direction_finder(point)[0]
        seed_finder(point, direction_vector, white_space)
        current_neighbourhood.append(point)
        image.putpixel(point, (0,0,0))
        white_space.remove(point)
        if point in seeds:
            seeds.remove(point)

        point = tuple_adder(point, direction_vector)

    image.putpixel(point,(0,0,0))
    white_space.remove(point)
    print('neighbourhood')
    image.show()
    if point in seeds:
        seeds.remove(point)

    current_neighbourhood.append(point)
    while len(seeds)>0:
        point = seeds[0]
        while len(direction_finder(point))>0:
            direction_vector = direction_finder(point)[0]
            seed_finder(point, direction_vector, white_space)
            current_neighbourhood.append(point)
            image.putpixel(point, (0,0,0))
            white_space.remove(point)
            if point in seeds:
                seeds.remove(point)

            point = tuple_adder(point, direction_vector)

        image.putpixel(point, (0,0,0))
        white_space.remove(point)

        if point in seeds:
            seeds.remove(point)

        current_neighbourhood.append(point)

    print('neighbourhood complete')
    seeds.clear()
    return current_neighbourhood

def patterfier(neighbourhoods, image):
    rs = []
    gs = []
    bs = []
    for i in range(len(neighbourhoods)):
        for j in range(len(neighbourhoods[i])):
            r,g,b = image.getpixel(neighbourhoods[i][j])
            rs.append(r)
            gs.append(g)
            bs.append(b)
        avg_r = int(sum(rs)/len(rs))
        avg_g = int(sum(gs)/len(gs))
        avg_b = int(sum(bs)/len(bs))
        for p in range(len(neighbourhoods[i])):
            image.putpixel(neighbourhoods[i][p], (avg_r, avg_g, avg_b))
        rs = []
        gs = []
        bs = []
        print('patterfied neighbourhood complete')
    image.show()

white_space = white_finder()

# keep loop conditional clauses in parentheses - less error prone
while (len(white_space) > 0):
    neighbourhoods.append(neighbourhood_finder(white_space))
image.show()
