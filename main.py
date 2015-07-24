# -*- coding: utf-8 -*-
"""
@author: hazh

inpired by the code here http://stackoverflow.com/a/3244061/1795661

"""

import os
import sys
from PIL import Image, ImageDraw
import scipy
import scipy.misc
import scipy.cluster
import colorsys

NUM = 10
PATH = os.getcwd()

def router(mode):
    files = os.listdir(PATH)
    files.remove('main.py')                                         #Get list of images in current directory.
    for f in files:
        if mode == "0":                                             #Only run for new images.
            if (f[:3] != "hsv"):
                main(f)
        elif mode == "1":                                           #Run for all images in directory.
            main(f)        

def main(f):
    codebook, counts = get_colours(f)                               #Get main colours in image.
    f_path = os.path.join(PATH, f)                                  #Set the images path for later use.
    
    hsv = get_prominent_colour(codebook, counts)                    #Get the image's prominent colour.
    draw_colour_palette(codebook, counts)                           #Draw palette of colours.
    set_image_name(f_path, hsv)                                     #Rename the images by hue.
                
def get_colours(f):        
    im = Image.open(f)
    w, h = im.size
    wr, hr = int(w * 0.5), int(h * 0.5)
    im.resize((wr, hr))
    obs = scipy.misc.fromimage(im).astype(float)                    #Return a copy of a PIL image as a numpy array.
    shape = obs.shape                                               #Return first two dimensions of obs (array).
    try:                                           
        obs = obs.reshape(scipy.product(shape[:2]), shape[2])       #Turn obs into a 1 dimensional array.
        codebook, distortion = scipy.cluster.vq.kmeans(obs, NUM)
        code, distortion = scipy.cluster.vq.vq(obs, codebook)
        counts, bins = scipy.histogram(code, len(codebook))      
        return codebook, counts           
    except:
        print f + " IndexError - deleting..."
        os.remove(f)   
            
def get_prominent_colour(codebook, counts):
    index_max = scipy.argmax(counts)                                #Get index of highest count in counts.
    peak = codebook[index_max] / 255                                #Get the most prominent colour.
    hsv = colorsys.rgb_to_hsv(peak[0], peak[1], peak[2])            #Convert to hsv.
    return hsv
    
def set_image_name(f_path, hsv):
    name = "hsv"                                                    #Format image name.
    for x in hsv:
        name = name + "-" + str(x)
    name += ".png"
    name = os.path.join(PATH, name)
    os.rename(f_path, name)
    
def draw_colour_palette(codebook, counts):
    colours = []
    for code, count in zip(codebook, counts):
        rgb = (code[0], code[1], code[2])
        colour = (rgb, count)
        colours.append(colour)
    sorted_colours = sort_colours(colours)
    palette = Image.new("RGB", (500, 100))
    canvas = ImageDraw.Draw(palette)
    i = 0
    for c in sorted_colours:
        rgb = (int(c[0][0]), int(c[0][1]), int(c[0][2]))
        canvas.rectangle([(50*i,0),(50*(i+1),100)], fill = rgb)
        i +=1
    palette.show()

def sort_colours(colours):
    return sorted(colours, key=lambda tup: tup[1])       
        
if __name__ == "__main__":
    router(sys.argv[1])