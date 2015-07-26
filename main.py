# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 21:39:53 2015

@author: Haz
"""
import sys
import os
from PIL import Image, ImageDraw
import scipy
import scipy.misc
import scipy.cluster
from colormath.color_objects import LabColor, sRGBColor, HSVColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import subprocess

NUM = 10

# get_prominent_colour_index() calls get_prominent_colour_index()
# set_image_name() calls get_image_src_input()

def router(mode):
    file_dir = os.path.join(os.getcwd(), "img")
    files = os.listdir(file_dir)
    if mode == "0":
        update(file_dir, files)
    elif mode == "1":
        override(file_dir, files)
    new_files = os.listdir(file_dir)
    draw_overview(new_files)

def update(file_dir, files):
    for f in files:
        if f[:3] != "hsv":
            main(file_dir, f)
    
def override(file_dir, files):
    for f in files:
        main(file_dir, f)
        
def main(file_dir, f):
    file_path = os.path.join(file_dir, f)
    image = get_image(file_path)
    image = resize_image(image)
    image = get_image_as_array(image)
    codebook, counts = get_codebook_and_counts(image) # code == colour
    colours_hist = get_colours_hist(codebook, counts)
    colours_hist_sorted = sort_hist(colours_hist)
    lab_colours_sorted = get_lab_colours(colours_hist_sorted)
    index = get_prominent_colour_index(lab_colours_sorted)
    colour = get_prominent_colour(colours_hist_sorted, index)
    draw_colour_palette(colours_hist_sorted, index)
    name = set_image_name(file_dir, file_path, colour) 

def get_image(file_path):
    image = Image.open(file_path)
    return image

def resize_image(image):
    width, height = image.size
    new_image = image.resize((int(width*0.5), int(height*0.5)))
    return new_image

def get_image_as_array(image):
    return scipy.misc.fromimage(image).astype(float)

def get_codebook_and_counts(image):                        
    shape = image.shape                                                                                                    
    image = image.reshape(scipy.product(shape[:2]), shape[2])                       
    codebook, distortion = scipy.cluster.vq.kmeans(image, NUM)
    code, distortion = scipy.cluster.vq.vq(image, codebook)
    counts, bins = scipy.histogram(code, len(codebook))      
    return codebook, counts  

def get_colours_hist(codebook, counts):
    colours_hist = []
    for code, count in zip(codebook, counts):
        rgb = tuple(x/255 for x in code)
        colour = (rgb, count)
        colours_hist.append(colour)
    return colours_hist

def sort_hist(hist):
    return sorted(hist, key=lambda tup: tup[1])

def get_lab_colours(hist): 
    lab_colours = []
    for c in hist:
        rgb = sRGBColor(c[0][0], c[0][1], c[0][2])
        lab_colours.append(convert_color(rgb, LabColor))
    return lab_colours 

def get_prominent_colour_index(lab_colours):
    wrgb = sRGBColor(1,1,1)
    w = convert_color(wrgb, LabColor) 
    i, j = 1, 2
    tol = 100
    while tol > 20 and i < 8:
        white_check = compare_colours([w, lab_colours[-i]], 1, 2)
        if white_check > 5:       
            tol = compare_colours(lab_colours, i, j)
        i += 1
        j += 1
    return i

def compare_colours(lab_colours, i, j):                                         
    return delta_e_cie2000(lab_colours[-i], lab_colours[-j])

def get_prominent_colour(hist, i):
    rgb = tuple(x for x in hist[-i][0])                               
    hsv = convert_color(sRGBColor(*rgb), HSVColor, through_rgb_type=sRGBColor)
    return hsv
    
def draw_colour_palette(hist, m):
    palette = Image.new("RGB", (500, 200))
    canvas = ImageDraw.Draw(palette)
    i = 0
    for c in hist:
        rgb = sRGBColor(c[0][0], c[0][1], c[0][2])
        rgb_int_tuple = tuple(int(x*255) for x in rgb.get_value_tuple())
        canvas.rectangle([(50*i,0),(50*(i+1),100)], fill = rgb_int_tuple)
        i +=1
    pc = hist[NUM - m][0]
    canvas.rectangle([(0,100),(500,200)], fill = tuple(int(x*255) for x in pc))
    palette.show()
    
def set_image_name(file_dir, old_path, colour):
    name = "hsv"                                                                
    for x in colour.get_value_tuple():
        name = name + "-" + str(x)
    #src = get_image_src_input(old_path)
    #name += "-----" + src
    name += ".png"
    name = os.path.join(file_dir, name)
    os.rename(old_path, name)
    
def get_image_src_input(path):
    image = Image.open(path)
    image.show()
    src = raw_input("img src: ")
    del image
    return src

def draw_overview(files):
    overview = Image.new("RGB", (len(files)*10, 100))
    canvas = ImageDraw.Draw(overview)
    colours = []
    for f in files:
        f = f[4:-4]
        hsv = tuple(float(x) for x in f.split("-"))
        colours.append(hsv)
    sorted_colours = sorted(colours, key=lambda tup: tup[0])
    i = 0
    for colour in sorted_colours:
        rgb = convert_color(HSVColor(*colour), sRGBColor, through_rgb_type=sRGBColor)
        canvas.rectangle([(i*10,0),((i+1)*10,100)], fill = tuple(int(x*255) for x in rgb.get_value_tuple())) 
        i += 1
    overview.show()

if __name__ == "__main__":
    router(sys.argv[1])