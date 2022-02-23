'''
Calcudoku
'''
import cv2
import os
import numpy as np
import pandas as pd
import networkx as nx
import sys
import streamlit as st
import math

#tesseract OCR import and filepath
import pytesseract

#pytesseract.pytesseract.tesseract_cmd =r'C:/Program Files/Tesseract-OCR/tesseract'



def find_cell_length_pixels(image):
    '''
    This function is used to find the size of the calcudoku puzzle
    - Uses the black and white image of the playing grid
    - It firstly starts at the top of the grid and moves down unitl the bottom of the grid
    - If at any point it encounters a solid line (white pixel) it records the distance between its last white pixel and appends to a list
    - Once at the bottom it then moves along and does the same
    - The same process is done left to right as well
    - Once all distances have been appended and filtered out for encountering possible noise the minimum of the list is taken
    - This should be the size of the smallest box

    - The idea is that the line passes through a unconnected cell rather than multiple connected cells before encountering a border
    '''

    guess = 0 # set to zero as its the origin point
    list_size = [] # list to append to

    for pix in range(0,image.shape[0]-1): # loop vertically
        pixel_colour = image[image.shape[0]-5,pix] # get fixel colour
        if pixel_colour == 255: #  if pixel colour is white - encountered grid line
            list_size.append(int(pix-guess)) # get distance between start and when it encountered a grid line
            guess = pix # change guess to where border was last encountered

    guess = 0 # set to zero as its the origin point
    for pix in range(0,image.shape[0]-1):
        pixel_colour = image[pix,image.shape[0]-10] # loop horizontally
        if pixel_colour == 255: #if pixel colour is white - encountered grid line
            list_size.append(int(pix-guess)) # get distance between start and when it encountered a grid line
            guess = pix # change guess to where border was last encountered

    list_size[:] = [x for x in list_size if x > 15] # remove small values, encountered given number, math operator or noise

    cell_length = min(list_size)    # find minimum remaining value
    return cell_length


def get_number_of_cells(blackAndWhiteImage,cell_length):
    '''
    Size of image divided by cell size = number of cells in calcudoku grid
    '''
    num_of_cells = int(math.floor(blackAndWhiteImage.shape[0]/cell_length))
    return  num_of_cells

def size_of_cell(image,num_of_cells):
    '''
    Get size of cell as float value
    '''
    cell_sizes = image.shape[0]/num_of_cells
    return cell_sizes

def find_cell_box_coords(cell_sizes,num_of_cells):
    '''
    Get top left coordinate of each cell - used later for cropping
    Get centre coordinate of each cell - used later for text writing

    - start point is half the cell width, found by dividing the cell width by 2
    - create empty list for top left coordinates and centre coordinates

    - Loop over number of cells in grid vertically and horizonally appending relevant coordinates
    '''

    start_point = int(round(cell_sizes/2,0)) # half box size
    list_cell_box_pixels = [] # top left pixels
    list_of_centre_pix = [] # centre pixles

    for x_coor in range(0,num_of_cells): # loop horizontally over number of cells
        x_coordinate = start_point+int(round(x_coor*cell_sizes,0)) # set left for that row
        for y_coor in range(0,num_of_cells): # loop vertically over number of cells
            y_coordinate = start_point+int(round(y_coor*cell_sizes,0)) # set top value for that row
            list_cell_box_pixels.append([(x_coor,y_coor),(x_coordinate-start_point,y_coordinate-start_point)]) # append  cell coorindates and pixel coordinates of top left
            list_of_centre_pix.append([x_coordinate,y_coordinate]) # append cell coordinates and pixel coordinates of centres

    return list_cell_box_pixels, list_of_centre_pix

def find_vertically_connected_cells(imgThresh2,num_of_cells,cell_sizes):
    '''
    Want to find all verticall connected cell in thresholded image (only solid lines remain, no connected cells grids are visible)
    - Start at 3/4 down in cell
    - find all pixel values along another quarter cell length down
     - if any of them are white, the cells are not connected as its encountered a solid grid , move to next veritcal cell and try again
     - if it gets to end of pixels to check and no cells found, cells are connected
     - append connected cells to list
    '''
    cell_middle = int(round(cell_sizes/2,0)) # start in middle of cell
    quarter_cell = int(round(cell_middle/2,0)) # get quarter cell length

    vertically_connected_cells = [] # empty list

    for x_coor in range(0,num_of_cells): # go through cels holding columns constand and chekcing rows
        x_coordinate = cell_middle+int(round(x_coor*cell_sizes,0)) # get middle of cell x coordinate
        for y_coor in range(0,num_of_cells): # go through cells in columns
            #y_coordinate = cell_middle+int(round(y_coor*cell_sizes,0)) # get middle of cell y coordinate

            if y_coor == num_of_cells-1: # make sure it doesn't go beyond range of cell size
                pass
            else:

                for pixels in range(1,cell_middle+1): # only want to check along possible line of border

                    pixel_colour = imgThresh2[int(y_coor*cell_sizes+cell_middle+quarter_cell+pixels),x_coordinate] # -> this is where the modification has to be   check pixel value 0 = black, 255 -= white

                    if pixel_colour == 255:# encountered white line - grid line
                        break # cells not connected move onto next one
                    else: # no border encountered -> cells are connected
                        if pixels == cell_middle: # has gone through entire line without encountering a cell border
                            vertically_connected_cells.append([tuple((int(x_coor),int(y_coor))),tuple((int(x_coor),int(y_coor+1)))])# append cells

    return vertically_connected_cells


def find_horizontally_connected_cells(imgThresh2,num_of_cells,cell_sizes):

    cell_middle = int(round(cell_sizes/2,0))
    quarter_cell = int(round(cell_middle/2,0))

    horizontally_connected_cells = [] # empty list

    for y_coor in range(0,num_of_cells):# go through cells holding rows constand and chekcing columns
        y_coordinate = cell_middle+int(round(y_coor*cell_sizes,0)) # get middle of cell x coordinate
        for x_coor in range(0,num_of_cells): # go through cells in row
            x_coordinate = cell_middle+int(round(x_coor*cell_sizes,0))
            if x_coor == int(num_of_cells-1): # make sure it stays in bounds no need to check if right most cell is connected
                pass
            else:
                for pixels in range(1,cell_middle+1):  # holding x coor while going hrough vert line#
                    pixel_colour = imgThresh2[y_coordinate,int(x_coor*cell_sizes+cell_middle+quarter_cell+pixels)]#check from last quarter of cell to 1/4 of next cel

                    if pixel_colour == 255: # was 255 white-> has encountered a line, cells arent connected
                        break
                    else: # no border encountered -> cells are connected
                        if pixels == cell_middle: # has gone through entire line without encoutnering a cell border
                            horizontally_connected_cells.append([tuple((int(x_coor),int(y_coor))),tuple((int(x_coor+1),int(y_coor)))]) #a append cell and next cell

    return horizontally_connected_cells

def find_all_connected_cells(vertically_connected_cells,horizontally_connected_cells):
    '''
    Uses graph theory to combine cell which are both in vertical and horizontal list e.g. a L shape where the bottom left is connected vertiall and horizontally
    -
    '''
    # vertically linked
    V=nx.Graph()
    V.add_edges_from(vertically_connected_cells)
    vertical_list = list(nx.connected_components(V))
    # horizontally linked
    H=nx.Graph()
    H.add_edges_from(horizontally_connected_cells)
    horizontal_list=list(nx.connected_components(H))

    combined_connected_list = vertical_list+horizontal_list # add lists together
    return combined_connected_list

def dict_to_list(combined_connected_list):
    '''
    converts the dict of combined cells into a list
    '''
    linked_cells = []

    while len(combined_connected_list)>0:
        first, *rest = combined_connected_list
        first = set(first)

        lf = -1
        while len(first)>lf:
            lf = len(first)

            rest2 = []
            for r in rest:
                if len(first.intersection(set(r)))>0:
                    first |= set(r)
                else:
                    rest2.append(r)
            rest = rest2

        first = sorted(first, key=lambda element: (element[1], element[0])) # sort vertically then horizontally, the first will have a math operator
        linked_cells.append((list(first)))
        combined_connected_list = rest

    return linked_cells

#OCR
def ocr_linked_cells(cell_length,linked_cells,num_of_cells,list_cell_box_pixels,workingImg,show=False):
    '''
    Perform ocr using custom trained model math_cells on math operators 720x etc

    '''
    ocr_linked_cells = []

    h=int(round(cell_length,0))
    w=int(round(cell_length,0))

    # sometimes OCr gives double math operators want to remove them
    double_math = ['--','-+','-x','-÷',
             '+-','++','+x','+÷',
             'x-','x+','xx','x÷',
             '÷-','÷+','÷x','÷÷',]

    for i in range(0,len(linked_cells)): # iterate over all linked cells contianing math operators
        for j in range(0,len(list_cell_box_pixels)):# go through all cells with additional box coordinates
            if linked_cells[i][0] == list_cell_box_pixels[j][0]: # if thre is a match

                x = list_cell_box_pixels[j][1][0]+3 # get box pixel coordinate, add 3 to remove possible grid inclusion
                y = list_cell_box_pixels[j][1][1]+3 # get box pixel coordinate , add 3 to remove possible grid inclusion

                crop = workingImg[y:y+h, x:x+w] # crop image to cell of math operator

                cropped_resize = cv2.resize(crop,(600,600)) # resize to 600,600
                cropped_resize_crop = cropped_resize[20:200,20:500]# was 30: # OCR orks better when there is less stuff on left an top of image

                cropped_gray =cv2.cvtColor(cropped_resize_crop, cv2.COLOR_BGR2GRAY) # convert to black and white
                thresh = cv2.threshold(cropped_gray,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] # perform thresh holding

                #st.image(crop, caption = 'crop')
                #st.image(cropped_resize, caption = 'cropped_resize')
                #st.image(cropped_resize_crop, caption = 'cropped_resize_crop')
                #st.image(cropped_gray, caption = 'cropped_gray')
                #st.image(thresh, caption = 'thresh'+str(list_cell_box_pixels[j][0])+str(list_cell_box_pixels[j][1]))

                text = pytesseract.image_to_string(thresh,lang = 'math_cells', config = '--psm 6 --oem 3') # OCR

                # Fixing wrong predictions > above 99% accuracy
                text=text.replace(" ","")
                text=text.replace("\n\x0c","")
                text=text.replace("-22x","72x")

                if text[0] == '-':
                    text = text[1:]

                if text[0] == 'x':
                    text = text[1:]

                # large values must be multiplcation
                try:
                    if int(text) > 9999 and 'x' not in str(text):
                        print('huh?')
                        text = text[:-1]
                        text = text+'x'
                except:
                    pass
                # check double math  occurances,
                if any(substring in text for substring in double_math):
                    mult_len = text.find('x')

                    # if not in will be set to 0 and wont work set to high number instead
                    if mult_len < 0:
                        mult_len = 100

                    add_len = text.find('+')
                    if add_len < 0:
                        add_len = 100

                    sub_len = text.find('-')
                    if sub_len < 0:
                        sub_len = 100

                    div_len = text.find('÷')
                    if div_len < 0:
                        div_len = 100

                    end_text = min(mult_len,add_len,sub_len,div_len)
                    text = text[:end_text+1]

                # change text from symbol to english
                if '+' in text:
                    text = text.replace('+',"")
                    text = text.strip()
                    text = "add "+text

                if '-' in text:
                    text = text.replace('-',"")
                    text = text.strip()
                    text = "sub "+text

                if 'x' in text:
                    text = text.replace('x',"")
                    text = text.strip()
                    text = "mult "+text

                if '÷' in text:
                    text = text.replace('÷',"")
                    text = text.strip()
                    text = "div "+text
                # [(cell 1), (cell 2)] add 7 etc
                ocr_linked_cells.append(str(linked_cells[i]).replace(" ","")+" "+text)

                if show ==True:
                    st.image(thresh,caption = str(text))

    return ocr_linked_cells


def get_all_linked_cells(linked_cells):
    '''
    flatten list of all cells e.g. [(x1,y1)], [(x2,y2)] -> [(x1,y1), (x2,y2)]
    '''
    flattened_list_linked_cells = [item for sublist in linked_cells for item in sublist]
    return flattened_list_linked_cells


def get_known_boxes_cell_coords(list_cell_box_pixels,all_connected_cells):#linked_cells
    '''
    Get coordinates of cells with known values aka given values
    '''
    known_cell_coords = []

    for i in range(0,len(list_cell_box_pixels)): #go through list of all box coordinates
        if list_cell_box_pixels[i][0] not in all_connected_cells: # if box coordinate not in list of linked cells  must be isoalted and given
            known_cell_coords.append(list_cell_box_pixels[i][0]) # append

    return known_cell_coords

def ocr_given_cells(known_cell_coords,cell_length,linked_cells,num_of_cells,list_cell_box_pixels,workingImg):
    '''
    Perform OCR on known cells using given_cell model in tesseract

    '''
    ocr_given_cells = []

    h=int(round(cell_length,0))
    w=int(round(cell_length,0))

    for i in range(0,len(known_cell_coords)):

        x = known_cell_coords[i][0]*w
        y = known_cell_coords[i][1]*h

        # find solid number box
        number_box = workingImg[y:y+h, x:x+w] # get coordinate
        cropped_resize = cv2.resize(number_box,(600,600)) # resize to 600,600

        cropped_gray =cv2.cvtColor(cropped_resize, cv2.COLOR_BGR2GRAY) # turn to black and white
        thresh = cv2.threshold(cropped_gray,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] # thresholding

        thresh = thresh[180:500,150:500] # crop again improves tesseract performance # was 150

        text = pytesseract.image_to_string(thresh,lang = 'given_cells', config = '-c tessedit_char_whitelist=0123456789 --psm 10 --oem 3')
        text = text.strip("\n\x0c")
        text = text.replace(" ","")

        # solver function needs an operator here so I chose add
        text = 'add '+text
        cell_coords = tuple(known_cell_coords[i])
        ocr_given_cells.append(str(cell_coords).replace(" ","")+" "+text)

    return ocr_given_cells

def combine_ocr_linked_and_given(ocr_linked_cells,ocr_given_cells):
    '''
    Combines both ocr lists
    '''
    combined_list = ocr_linked_cells+ocr_given_cells

    return combined_list

#@st.experimental_memo
def preprocess_for_printing(size, list_cell_centre_pix,connected_cells,solved_puzzle):
    '''
    Takes solved puzzle which is a numpy array (solved_puzzle)
    Takes connected cell, don't need to print known cells (connected_cells)
    list_cell_centre_pix is a flat array
    '''
    coordinate_for_solve_numbers = []

    for num in range(0,len(connected_cells)):
        x = connected_cells[num][0]
        y = connected_cells[num][1]

        centre_pix = list_cell_centre_pix[x*size+y] # find index of connected_cells and find in list_cell_centre_pix

        solved_value = solved_puzzle[y,x] # Get number to print

        coordinate_for_solve_numbers.append((centre_pix,solved_value)) # (coordinates to print), number to print

    return coordinate_for_solve_numbers
