from PIL import Image, ImageDraw, ImageFont
import random
from django.conf import settings
import os


def draw_image(file_stream,key):
    size_x = 100
    size_y = 40

    im = Image.new("RGB", (size_x,size_y),(255,255,255))

    font = ImageFont.truetype(os.path.dirname(__file__)+"/courbd.ttf", 30)
    draw = ImageDraw.Draw(im)

    for x in range(1, random.randint(20,40) ):
        start_x = random.randint(1,size_x)
        start_y = random.randint(1,size_y)
        box_size = random.randint(1,20)

        color_r = random.randint(80,254)
        color_g = random.randint(80,254)
        color_b = random.randint(80,254)

        draw.rectangle( [start_x,start_y,start_x+box_size,start_y+box_size], fill=(color_r,color_g,color_b) )
                   
    start_x = 10
    for letter in key:
        font_size = font.getsize(letter)

        color_r = random.randint(50,70)
        color_g = random.randint(0,color_r)
        color_b = random.randint(0,color_g)

        pos_y = random.randint(2, size_y - font_size[1] )
        
        draw.text((start_x,pos_y), letter, font=font, fill=(color_r,color_g,color_b) )
        start_x += font_size[0] + 5


    for x in range(1, random.randint(5,10) ):
        start_x = random.randint(1,size_x)
        start_y = random.randint(1,size_y)
        box_size = random.randint(20,30)

        color_r = random.randint(200,254)
        color_g = random.randint(200,254)
        color_b = random.randint(200,254)
        
        draw.arc( [start_x,start_y,start_x+box_size,start_y+box_size], 0,360, (color_r,color_g,color_b) )
        
    del draw     

    im.save(file_stream,'PNG')

    return file_stream
    
    


