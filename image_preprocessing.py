'''
image preprocessing
'''
import cv2
import os
import numpy as np
import pandas as pd
import networkx as nx
import streamlit as st
import math

widthImg = 600
heightImg = 600

def preProcessing(img):
    '''
    Takes input image and perforns various processing using opencv2
    - Convert image to black and white
    - Blue the image
    - Perform canny
    - image dialation and erosion to remove noise
    '''

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5,5),1)
    imgCanny = cv2.Canny(imgBlur,50,50)
    kernel = np.ones((3,3))
    imgDialation = cv2.dilate(imgCanny, kernel, iterations = 2)
    imgThresh = cv2.erode(imgDialation, kernel, iterations = 1)

    return imgThresh

def getContours(img):
    '''
    Find largest area - hopefully will be playing area of calcudoku puzzle
    - iterate through various areas enclosed within lines
    - If current area is larger than previous, then set maxArea to that value
    - Largest should be playing area
    - Coordinates of largest area returned: top left, bottom left, bottom right, top right
    '''
    biggest = np.array([])
    maxArea = 0
    contours, heirachy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 15000: # mightneed to adjust
            #cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 3)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02*peri, True)
            if area > maxArea and len(approx) == 4:
                biggest = approx
                maxArea = area

    # Get image conours of board
    #img_1 = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
    #img_1=cv2.drawContours(img_1, biggest, -1, (255, 0, 0), 20)
    #st.image(img_1)

    return biggest

def reorder(myPoints):
    '''
    Reorders points from getContours
    - from: top left, bottom left, bottom right, top right
    - to: top left, top right, bottom left, bottom right
    '''
    myPoints = myPoints.reshape((4,2))
    myPointsNew = np.zeros((4, 1, 2), np.int32)
    add = myPoints.sum(1)

    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] = myPoints[np.argmax(add)]

    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] =  myPoints[np.argmin(diff)]
    myPointsNew[2] =  myPoints[np.argmax(diff)]

    return myPointsNew

def getWarp(img,biggest,widthImg,heightImg):
    '''
    Warp the image of the deteced playing grid
    - known points are got from biggest function and reordered
    - ideal points are set as points_2
    - cv2 getPerspectiveTransform is used to rotate and scale the image
    '''
    biggest = reorder(biggest)
    points_1 = np.float32(biggest)
    points_2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
    matrix = cv2.getPerspectiveTransform(points_1,points_2)
    imgOutput = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
    return imgOutput

def black_and_white(imgWarped):
    '''
    Perform preprocessing on playing grid
    - Thresholding now is set to 128 to remove the seperator etween connected cells
    - necessary for finding connected cells
    '''
    grayImage = cv2.cvtColor(imgWarped, cv2.COLOR_BGR2GRAY)
    (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, 128, 255, cv2.THRESH_BINARY) # was thresh,blackAndWhite...
    return blackAndWhiteImage

#@st.experimental_memo
def write_solved_puzzle(list_of_centres_and_values,filepath,number_of_cells,colour):
    '''
    Writes the solved puzzle values to onto the warped playing grid image
    - iterates over list of centres of boxes for unknown values (opposed to given values from calcudoku)
    - Text is written using the lower left value, at the moment we only have centre pixel values
    - They will need to be decreased by the text height and width to make sure the text is displayed optimally
    - The ratios to offset were found by trial and error
    '''
    image = cv2.imread(filepath)

    fontscale = round(1.5 *9/number_of_cells,1)
    thickness = math.floor(fontscale)

    for pix in range(0,len(list_of_centres_and_values)):

        x_centre = list_of_centres_and_values[pix][0][0] # get x centre pixel value
        x_centre_offset = x_centre-math.floor(fontscale*11) # offset by some value

        y_centre = list_of_centres_and_values[pix][0][1] # get y centre pixel value
        y_centre_offset = y_centre+math.floor(fontscale*15) # offset by some value

        # get colours
        if colour == 'Green':
            colour_values = (0, 255, 0)
        elif colour == 'Red':
            colour_values = (255,0,0)
        elif colour == 'Yellow':
            colour_values = (255,215,0)
        elif colour == 'Blue':
            colour_values = (0,255,255)
        elif colour == 'Sky Blue':
            colour_values = (0,191,255)
        elif colour == 'Dark Purple':
            colour_values = (139,0,139)
        elif colour == 'Purple':
            colour_values = (1186,85,211)
        elif colour == 'Black':
            colour_values = (0,0,0)

        # write to image
        image = cv2.putText(image,str(list_of_centres_and_values[pix][1]),(x_centre_offset,y_centre_offset),cv2.FONT_HERSHEY_SIMPLEX, fontscale, colour_values, thickness, cv2.LINE_AA)
    return image
