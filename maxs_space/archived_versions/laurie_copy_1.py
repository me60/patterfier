import PIL

from PIL import Image, ImageDraw

image = Image.open('images/500.jpg')
rgb_image = image.convert('RGB')
draw_image = ImageDraw.Draw(rgb_image)

width,height = image.size

tile_width = 25
tile_height = 25

current_tile = []
rs=[]
gs=[]
bs=[]

total_cells = int(int(width/tile_width) * int(height/tile_height))

last_x = 0
last_y = 0
list = []

for i in range(0, total_cells):
    for y in range(last_y,(last_y+tile_height)):
        for x in range(last_x,(last_x+tile_width)):

            r,g,b = rgb_image.getpixel((x,y))

            list.append(r)
            list.append(g)
            list.append(b)

            ag = int((0.299*r) + (0.587*g) + (0.114*b))

            current_tile.append(ag)

            rs.append(r)
            gs.append(g)
            bs.append(b)


            if x == width-1 and y == ((last_y+tile_height)-1):

                #calculates average rgb values for a whole tile
                avg_r = int(sum(rs)/len(rs))
                avg_gr = int(sum(gs)/len(gs))
                avg_b = int(sum(bs)/len(bs))

                avg_gray = sum(current_tile)/len(current_tile)

                avg_g_scale = int((avg_gray/255)*10)

                avg_g_scale = avg_g_scale*25

                draw_image.rectangle([last_x, last_y, x, y], fill = ((avg_r),(avg_gr), (avg_b)))

                last_x = 0
                last_y = last_y + tile_height

                current_tile = []
                rs = []
                gs = []
                bs = []


            if x == ((last_x+tile_width)-1) and y == ((last_y+tile_height)-1):

                avg_r = int(sum(rs)/len(rs))
                avg_gr = int(sum(gs)/len(gs))
                avg_b = int(sum(bs)/len(bs))

                avg_gray = sum(current_tile)/len(current_tile)

                avg_g_scale = int((avg_gray/255)*10)

                avg_g_scale = avg_g_scale*25


                draw_image.rectangle([last_x, last_y, x, y], fill = ((avg_r),(avg_gr), (avg_b)))
                last_x = last_x + tile_width

                current_tile = []
                rs = []
                gs = []
                bs = []

rgb_image.show()
