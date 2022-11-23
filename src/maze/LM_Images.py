# HERE IMAGES OF THE MAPS ARE GENERATED

### IMPORTS ###

from PIL import Image
import numpy as np


### FUNCTIONS ###

def create_image(view):
    
    # open tempate images
    im_player = Image.open('images/player.png')
    im_mummy = Image.open('images/mummy.png')
    im_floor = Image.open('images/floor.png')
    im_exit = Image.open('images/exit.png')  
    im_wall = Image.open('images/wall.png')
    
    imgs = []
    for row in range(view.shape[0]):
        for col in range(view.shape[1]):
            if view[row, col] == 'A':
                imgs.append(im_player)
            elif view[row, col] == '8':
                imgs.append(im_mummy)
            elif view[row, col] == 'E':
                imgs.append(im_exit)
            elif view[row, col] == 'X':
                imgs.append(im_wall)
            else:
                imgs.append(im_floor)
    
    rows, cols = view.shape
    
    
    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols*w, rows*h))
    grid_w, grid_h = grid.size
    
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i%cols*w, i//cols*h))

    return grid