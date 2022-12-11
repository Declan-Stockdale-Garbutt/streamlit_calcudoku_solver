import csp
import re
import sys
import cv2
import os
import time
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
import calcudoku_solver as calcudoku
import image_preprocessing as img_proc

widthImg = 600
heightImg = 600


class KenKen():

    def __init__(self, size, lines):

        self.variables = list()
        self.neighbors = dict()
        self.blockVar = list()
        self.blockOp = list()
        self.blockValue = list()
        self.blockVariables = list()


        """Create variables list"""
        for i in range(size):
            for j in range(size):
                self.variables.append('K' + str(i) + str(j))

        """Create domains dictionary"""
        dictDomainsValues = list(range(1, size+1))
        self.domains = dict((v, dictDomainsValues) for v in self.variables)

        """Create neighbors dictionary"""
        for v in self.variables:
            dictNeighborValue = []
            coordinateX = int(list(v)[1])
            coordinateY = int(list(v)[2])

            for i in range(size):
                if i != coordinateY:
                    string = 'K' + str(coordinateX) + str(i)
                    dictNeighborValue.append(string)
                if i != coordinateX:
                    string = 'K' + str(i) + str(coordinateY)
                    dictNeighborValue.append(string)

            self.neighbors[v] = dictNeighborValue


        """Create constraint data lists"""
        for l in lines:
            #st.write(l)
            var, op, val = l.split()
            #st.write('var',var,'op',op,'val',val)
            self.blockVar.append(re.findall('\d+', var))
            self.blockOp.append(op)
            self.blockValue.append(int(val))


        for i in range(len(self.blockVar)):
            blockList = []
            for j in range(0, len(self.blockVar[i]), 2):
                string = 'K' + str(self.blockVar[i][j]) + str(self.blockVar[i][j+1])
                blockList.append(string)

            self.blockVariables.append(blockList)


    def kenken_constraint(self, A, a, B, b):
        #print('ken_ken_constraints function')
        #print(self.neighbors)
        if B in self.neighbors[A] and a == b:
            return False

        for n in self.neighbors[A]:
            if n in game_kenken.infer_assignment() and game_kenken.infer_assignment()[n] == a:
                return False

        for n in self.neighbors[B]:
            if n in game_kenken.infer_assignment() and game_kenken.infer_assignment()[n] == b:
                return False

        blockA = blockB = 0

        for i in range(len(self.blockVariables)):
            if A in self.blockVariables[i]:
                blockA = i
            if B in self.blockVariables[i]:
                blockB = i

        if blockA == blockB:
            blockNum = blockA
            if self.blockOp[blockNum] == "''":
                if A != B:
                    return False
                elif a != b:
                    return False
                elif a != self.blockValue[blockNum]:
                    return False

                return True

            elif self.blockOp[blockNum] == 'add':
                sum = assigned = 0

                for v in self.blockVariables[blockNum]:
                    if v == A:
                        sum += a
                        assigned += 1
                    elif v == B:
                        sum += b
                        assigned += 1
                    elif v in game_kenken.infer_assignment():
                        sum += game_kenken.infer_assignment()[v]
                        assigned += 1

                if sum == self.blockValue[blockNum] and assigned == len(self.blockVariables[blockNum]):
                    return True
                elif sum < self.blockValue[blockNum] and assigned < len(self.blockVariables[blockNum]):
                    return True
                else:
                    return False

            elif self.blockOp[blockNum] == 'mult':
                sum = 1
                assigned = 0

                for v in self.blockVariables[blockNum]:
                    if v == A:
                        sum *= a
                        assigned += 1
                    elif v == B:
                        sum *= b
                        assigned += 1
                    elif v in game_kenken.infer_assignment():
                        sum *= game_kenken.infer_assignment()[v]
                        assigned += 1

                if sum == self.blockValue[blockNum] and assigned == len(self.blockVariables[blockNum]):
                    return True
                elif sum <= self.blockValue[blockNum] and assigned < len(self.blockVariables[blockNum]):
                    return True
                else:
                    return False

            elif self.blockOp[blockNum] == 'div':
                return max(a, b) / min(a, b) == self.blockValue[blockNum]

            elif self.blockOp[blockNum] == 'sub':
                return max(a, b) - min(a, b) == self.blockValue[blockNum]

        else:
            constraintA = self.kenken_constraint_op(A, a, blockA)
            constraintB = self.kenken_constraint_op(B, b, blockB)

            return constraintA and constraintB


    def kenken_constraint_op(self, var, val, blockNum):
        #print('kenken_constraints op function')
        if self.blockOp[blockNum] == "''":
            return val == self.blockValue[blockNum]

        elif self.blockOp[blockNum] == 'add':
            sum2 = 0
            assigned2 = 0

            for v in self.blockVariables[blockNum]:
                if v == var:
                    sum2 += val
                    assigned2 += 1
                elif v in game_kenken.infer_assignment():
                    sum2 += game_kenken.infer_assignment()[v]
                    assigned2 += 1

            if sum2 == self.blockValue[blockNum] and assigned2 == len(self.blockVariables[blockNum]):
                return True
            elif sum2 < self.blockValue[blockNum] and assigned2 < len(self.blockVariables[blockNum]):
                return True
            else:
                return False

        elif self.blockOp[blockNum] == 'mult':
            sum2 = 1
            assigned2 = 0

            for v in self.blockVariables[blockNum]:
                if v == var:
                    sum2 *= val
                    assigned2 += 1
                elif v in game_kenken.infer_assignment():
                    sum2 *= game_kenken.infer_assignment()[v]
                    assigned2 += 1

            if sum2 == self.blockValue[blockNum] and assigned2 == len(self.blockVariables[blockNum]):
                return True
            elif sum2 <= self.blockValue[blockNum] and assigned2 < len(self.blockVariables[blockNum]):
                return True
            else:
                return False

        elif self.blockOp[blockNum] == 'div':
            for v in self.blockVariables[blockNum]:
                if v != var:
                    constraintVar2 = v

            if constraintVar2 in game_kenken.infer_assignment():
                constraintVal2 = game_kenken.infer_assignment()[constraintVar2]
                return max(constraintVal2, val) / min(constraintVal2, val) == self.blockValue[blockNum]
            else:
                for d in game_kenken.choices(constraintVar2):
                    if max(d, val) / min(d, val) == self.blockValue[blockNum]:
                        return True

                return False

        elif self.blockOp[blockNum] == 'sub':
            for v in self.blockVariables[blockNum]:
                if v != var:
                    constraintVar2 = v

            if constraintVar2 in game_kenken.infer_assignment():
                constraintVal2 = game_kenken.infer_assignment()[constraintVar2]
                return max(constraintVal2, val) - min(constraintVal2, val) == self.blockValue[blockNum]
            else:
                for d in game_kenken.choices(constraintVar2):
                    if max(d, val) - min(d, val) == self.blockValue[blockNum]:
                        return True

                return False


    def show_solved(self, dic, size, cell_length,linked_cells,num_of_cells,list_cell_box_pixels,workingImg,show):
        solved_puzzle = np.empty((size,size),int)

        for i in range(size):
            try:
                for j in range(size):

                        string = 'K' + str(j) + str(i)
                        string_2 = (str(dic[string]) + " ")
                        solved_puzzle[i,j] = string_2

            except:
                st.write('Error occured. There is likely as issue with OCR, Please disregard output and try another puzzle')
                # show images of tesseract images and output possibly allowing for correction
                #calcudoku.ocr_linked_cells(cell_size,list_connected_cells,number_of_cells,list_cell_top_right_pix,imgWarped,show=True)
                break
            print()
        return solved_puzzle
        #st.write(solved_puzzle)




if __name__ == '__main__':

    # set up containers for streamlit
    header = st.container()

    image_selection = st.container()
    folder_selection = st.container()
    image_display = st.container()
    image_processing = st.container()
    save_container = st.container()

    # Set up navigation sidebar for streamlit
    add_selectbox = st.sidebar.radio(
        "Navigation menu ",
        ("Calcudoku solver", "Requirements","How it works", "More detail on training tesseract model","Future work","About")
        )

    if add_selectbox == 'Calcudoku solver':

        # Page title container
        with header:
            st.title('Calcudoku/KenKen solver application')
            st.subheader(' This app developed by Declan Stockdale-Garbutt ')

        #select image
        with image_selection:
            st.write("")
            st.write("Please upload an image or drag and drop one from the example puzzle folder here https://github.com/Declan-Stockdale/streamlit_calcudoku_solver/tree/master/Example_boards (open selected file and drag and drop)")

            if "image_upload_file_name_a" not in st.session_state:
                st.session_state.image_upload_file_name_a = 'placeholder'

            image_upload = st.file_uploader("",type=['jpg','jpeg','png'])

        # Diplay image and see if rotation is necessary
        with image_display:

            if image_upload is not None:

                # Block to check if filename is the same
                # if it is everyting is kept
                # if it changes all session states are reset

                # init new file
                if "image_upload_file_name_b" not in st.session_state:
                    st.session_state.image_upload_file_name_b = image_upload.name
                else:
                    st.session_state.image_upload_file_name_b = image_upload.name

                # check file is same or different
                if st.session_state.image_upload_file_name_b == st.session_state.image_upload_file_name_a:
                    pass
                else: # reset everything
                    st.session_state.image_upload_file_name_a = image_upload.name
                    st.session_state.state_is_solved = False
                    st.session_state.solved_puzzle = False
                    st.session_state.time_to_solve = False
                    st.session_state.colour = False

                st.session_state.image_upload_file_name = image_upload.name

                # Options to rotate image
                st.subheader('Displaying chosen image')
                image = Image.open(image_upload)

                rotate_radio = st.radio('Optional - rotate image',
                                        ('None - Default',
                                        'Clockwise',
                                        'Anticlockwise',
                                        'Flip 180'))

                if rotate_radio == 'Clockwise':
                    img = image.rotate(270,expand=1)

                if rotate_radio == 'Anticlockwise':
                    img = image.rotate(90,expand=1)

                if rotate_radio == 'Flip 180':
                    img = image.rotate(180)

                if rotate_radio == 'None - Default':
                    img = image

                img = np.array(img)
                st.image(img, caption="Uploaded image", width=600, use_column_width=False)

                imgThresh = img_proc.preProcessing(img)
                biggest = img_proc.getContours(imgThresh)


                if biggest.size == 0:
                    st.write('Unable to detect grid, please try another image')

                else:
                    st.write("")
                    st.subheader('Displaying captured playing area from selected image')
                    imgWarped = img_proc.getWarp(img,biggest,widthImg,heightImg)
                    # go back
                    grid_img = Image.fromarray(imgWarped)

                    st.image(imgWarped, caption="Grid", use_column_width=False)

                    with image_processing:
                        st.subheader('Solving puzzle')

                        # get image in useable format
                        imgThresh2 = img_proc.preProcessing(imgWarped)

                        # get cell length
                        cell_length = calcudoku.find_cell_length_pixels(imgThresh2)

                        # get number of cells
                        number_of_cells = calcudoku.get_number_of_cells(imgThresh2,cell_length)

                        # get cell size
                        cell_size = calcudoku.size_of_cell(imgThresh2,number_of_cells)

                        # get both lists needed for ocr detection later on
                        list_cell_top_right_pix,list_cell_centre_pix = calcudoku.find_cell_box_coords(cell_size, number_of_cells)

                        # Get vertically and horizontally connected cells
                        vert_connected_cells = calcudoku.find_vertically_connected_cells(imgThresh2,number_of_cells,cell_size)
                        hor_connected_cells = calcudoku.find_horizontally_connected_cells(imgThresh2,number_of_cells,cell_size)

                        # Graph theory to mach shared cells and turn into list
                        all_connected_cells = calcudoku.find_all_connected_cells(vert_connected_cells,hor_connected_cells)
                        list_connected_cells = calcudoku.dict_to_list(all_connected_cells)

                        # flat list of all connected cells - used later to fnd unconnected cells
                        flat_list_connected_cells = calcudoku.get_all_linked_cells(list_connected_cells)

                        # get coords of given box in playing grid
                        known_cell_coords = calcudoku.get_known_boxes_cell_coords(list_cell_top_right_pix,flat_list_connected_cells)

                        # OCR on math operators and given box
                        ocr_linked = calcudoku.ocr_linked_cells(cell_size,list_connected_cells,number_of_cells,list_cell_top_right_pix,imgWarped)# dirname
                        ocr_given = calcudoku.ocr_given_cells(known_cell_coords,cell_size,list_connected_cells,number_of_cells,list_cell_top_right_pix,imgWarped)#dirname

                        # combine output from OCR into parsable format for solver
                        combined_ocr_results = calcudoku.combine_ocr_linked_and_given(ocr_linked,ocr_given)

                        # solver from https://github.com/chanioxaris/kenken-solver
                        try:
                            kenken = KenKen(number_of_cells, combined_ocr_results)
                            game_kenken = csp.CSP(kenken.variables, kenken.domains, kenken.neighbors, kenken.kenken_constraint)

                            # start time for solving process
                            if "state_is_solved" not in st.session_state:
                                st.session_state.state_is_solved = False

                            ## Start time
                            start = time.time()

                            # spinner to show that its working
                            while st.session_state.state_is_solved == False:
                                with st.spinner(text="In progress... This can take a few minutes"):

                                    # solve puzzle
                                    solved = kenken.show_solved(csp.backtracking_search(game_kenken, inference=csp.mac), number_of_cells,cell_size,list_connected_cells,number_of_cells,list_cell_top_right_pix,imgWarped,show=False)

                                    # set value to true to break loop
                                    st.session_state.state_is_solved = True

                                    # Block remember solved puzzle output when changing colour
                                    if 'solved_puzzle' not in st.session_state:
                                        st.session_state.solved_puzzle = False

                                    # keep output of saved puzzle instead of resolving
                                    st.session_state.solved_puzzle = solved

                                    # Block to keep time of completion steady when colour changes
                                    end = time.time()
                                    if "time_to_solve" not in st.session_state:
                                        st.session_state.time_to_solve = False

                                    st.session_state.time_to_solve = end-start


                            # Display how long it took
                            st.write("Time taken to solve puzzle:", round(st.session_state.time_to_solve,2), "seconds")

                            # process output from numpy to coordinates to print to
                            to_print = calcudoku.preprocess_for_printing(number_of_cells,list_cell_centre_pix,flat_list_connected_cells,st.session_state.solved_puzzle)

                            with save_container:

                                # Display image and allow for colour change without resolving puzzle
                                if st.session_state.state_is_solved:

                                    #S Select colour
                                    colour = st.selectbox("Colour of output",
                                        ('Red','Green', 'Yellow', 'Blue', 'Purple','Sky Blue','Dark Purple','Black'))

                                    # if selection is true will be by defualt as its intially set to first option
                                    if colour:
                                        # display image using stored solved puzzle
                                        solved_image_picture = img_proc.write_solved_puzzle(to_print,imgWarped,number_of_cells,colour)
                                        st.image(solved_image_picture)

                        except ValueError:
                            st.write('Error in optical character recognition, please try another puzzle')



    if add_selectbox == 'Requirements':
        st.header("Requirements")
        st.subheader('Tesseract for Optical Character Recognition (OCR)')
        st.write('For calcudoku solver to work properly, a version of Tesseract must be available. This heroku app includes a tesseract build.')
        st.write('If necessary, Tesseract can be downloaded from the link below')
        st.write('https://tesseract-ocr.github.io/tessdoc/Downloads.html')

        st.subheader("Custom trained models")
        st.write('In addition two custom trained tesseract language models will need to be added into the tesseract/tessdata folder. Both will be available in the github repo here https://github.com/Declan-Stockdale/calcudoku_tesseract_buildpack')
        st.write('The first model is known as math_cells for recognising numbers and math operators in math cells')
        st.write('The second model known as given_cells is used to recognise the number in solid cells')

        st.write('While both do similar things, the different fonts and the requirement for perfect character recognition required two seperate models.The process beind training the models can be found under the "How it works" option.')

    if add_selectbox == "How it works":
        st.header("How it works")
        st.write("This application was built using python")

        st.subheader("Upload an image")
        st.write("Firstly an image of a kenken/calcudoku puzzle is uploaded")
        st.write("Puzzles can be screenshots from either the website https://api.razzlepuzzles.com/calcudoku or the app available on bothe the Apple store and the Google play store")
        st.write("The image is then kept in the local machines ram as a bytes type object")

        st.subheader("Opencv2 Computer vision")
        st.write("The python computer vision library Opencv2 is used to process and detect various features within the uploaded image. For opencv2 to function correctly, the image as a bytes type object must be converted to a numpy array for proper opencv2 functionality.")

        st.subheader("Finding the playing grid")
        st.write("The image is converted into a back and white image for easier processing")
        st.write("Various other preprocessing steps such as blurring, canning, dialiation and eroding occur to remove noise for easier grid detection")
        st.write("The next step is find the coordinates of the largest area enclosed within white lines. Assuming there is minimal noise, this should be the playing grid")

        st.write("The coordinates are given as top left, bottom left, bottom right, top right")
        st.write("These are rearranged to be top left, top right, bottom left, bottom right")
        st.write("The grid is then rotated and scaled to make it a square which is then displayed for the user to see.")

        st.subheader("Finding number of cells")
        st.write("The number of cells is found firstly by rastering vertically and recording the distance between white pixels. The same is done with a horizontal raster")
        st.write("Small values are removed (encountered noise, a math operator or a given cell)")
        st.write("The minimum value of the remaining values is recorded as the cell length in pixels, other values should be multiple of this value e.g. two cells, three cells ")
        st.write("It's performed horizontally and vertcally incase there is a weird grid e.g. all cells are horizontally connected which wouldn't find the cell lengh on a horizontal raster")
        st.write("The number of cells is found by dividing the shape of the size of the square grid from the previous section by the cell length rounded to the nearest integer")

        st.subheader("Finding connected cells")
        st.write(" A raster process similar to the one used to find cell pixel size is implemented")
        st.write(" From the previous step we know the cell size and shape and can determine the coordinates of each box within the calcudoku grid.")
        st.write(" We will iterate over the pixels which constiture the borders of boxes to determine if they are connected.")
        st.write(" If no border is encountered (e.g. no white pixels) along the entire search length, then the boxes must be connected as there is no border between them.")
        st.write(" Instead of starting at the top of the cell, to save some computation, we'll start at the 3/4 distance and search until we hit the first 1/4 of the next box")
        st.write(" By doing this we are only searching half the box distance and should avoid hitting math operators which occur in the top left of boxes.")
        st.write("This process is first performed vertically then horizontally")

        st.write("Graph networking is implemented to find boxes such as L shaped or squares where there's a box connected vertically and horizontally")
        st.write(" The returned result is a list of connected boxes where each box coordinates is returned as a tuple")
        st.write("All the math operators are in te top left most square of all connected boxes so sorting the returned list by these allows us to get cells containing math operators")
        st.write("In addition we can find all the cells containing given values by finding all cells not in the connected cell list")

        st.subheader('Optical Character Recognition (OCR) using Tesseract')
        st.write("Two custom models were trained following the instructions in this article https://towardsdatascience.com/simple-ocr-with-tesseract-a4341e4564b6")
        st.write("The first model math_cells is used to detect math operators, while the second given_cells is used to predict gven numbers in cells")

        st.write('There is minor tweaking on the predicions for the math_cells with multiple math operators occuring in some predicitons such as 7+x where we only want 7+ etc')
        st.write("The final output from both OCR results is a list of the connected boxes operator number (e.g. [(0,0),(0,1)] add 7)")
        st.write("This output is then put through the kenken solver adapted from code from this repository https://github.com/chanioxaris/kenken-solver")

        st.write('The output is an array of the results')
        st.write('To write the output onto the image we have do do a bit more work')

        st.subheader('Writing output to image')
        st.write('The output from the kenken solver is an array and the list of centre pixel coordinates is a flat list')
        st.write('By matching the index of the array as a number we can grab the centre pixel values of the box where we want to write that prediction to')
        st.write('Once we have a list of middle cell coordinates and the prediction we can write it onto the original grid image')
        st.write('A few modificaitons must be made first, largely as opencv2 writes the text starting with the bottom left where the coordinates are specified. The coordinates we have are for the centre of the box and will need to be modified.')
        st.write('The centre coordinate need to adjusted by the size of the height and width of the written text to diplay nicely')
        st.write('As each box can contain only one number and they are quite similar in size, we can modify all the coordinates by the same value.')

    if add_selectbox == 'More detail on training tesseract model':
        st.header("More detail on training tesseract model")
        st.write("This section goes into the detail regarding training the two custom tesseract models")
        st.write("Following on from the instruction provided in this article https://towardsdatascience.com/simple-ocr-with-tesseract-a4341e4564b6 ")
        st.write(" I along with other commenters on the article struggled with various steps to build the relevant files. I tried various versions of tesseract and found that only version 5.0.0.20190623 worked whereas 4 other installations failed at various steps.")

        st.subheader("Why was training necessary?")
        st.write("The reason further training was required was becuase tesseract with its base 'eng' model wasn't accurate enough to detect either the numbers or the math operators.")
        st.write("I don't think it has the capacity to detect the divide ÷ symbol which made passing the relevant arguments to the main solver impossible")

        st.write('To find out exactly how accurate the native tesseract "eng" model is, I wrote a script in jupyter notebook to compare the prediction to the labelled data')
        st.write('The inital accuracy was around 50 - 60% using the 3342 labelled data points but with experimenting to try and remove cell borders, additional cropping improved the performance up to ~ 70%')
        st.write('This was clearly not good enough and a custom model needed to be implemented')


        st.subheader("Generating the data")
        st.write('The first step was to generate some training data. This was performed by taking hundreds of screenshots of calcudoku games mostly 9x9 as to generate the most number of math operators within the shortest period of time.')
        st.write('The screen shots were parsed through the main calcudoku program up until the point where OCR occurs')
        st.write('At this point the images were saved to a seperate training folder with each file being named number_ witht he first 1_, the second 2_ and so on. There were about 7000 images generated')
        st.write('I manually labelled 3342 images with their corresponding math operators, so the file name was number_mathoperator. If the math operator of the first image was 280+, it would be named 1_280+. This was time consuming and errors were made.')


        st.subheader('Labelling process')
        st.write('Over 250 labelled math operator images using JTess box editor to properly identify and relabel images.')
        st.write('The most common misses from the "eng" model were that the numbers were poorly captured and if they were, they were mistaken as letters or the crop size was far too large including signifacant black space to eith side of the intended number. The multiplication sign was commonly mistaken for addition sign and the divide sign was never captured.')
        st.write('Through tedious relabelling of the numerous incorrectly labelled images, a model could be built following the tutorial')
        st.write("This custom model was named math_cells")

        st.subheader("Math_cell model vs native Tesseract performance")
        st.write('Running the same jupyter notebook but now with the new model called "math_cells", the accuracy of tesseract improved enormously up to 98%. It was still giving errors such as 72x was shown as x72x along with multiple math symbols being detected')
        st.write("I included the filename of wrongly predicted images to make sure I had labelled them correctly and this was the main source of error at this stage with 30 incorrecly labelled images needing to be relabelled.")
        st.write("I wrote some additional line of code to detect common errors in the tesseract predicitons which led to a final accuracy of 99.71% over 3342 images.")

        st.subheader("Given_cells vs native Tesseract performance")
        st.write('A very similar process was performed on boxes containing given values or what I occassionally refer to as solid cells.')
        st.write("The labelling process was less tedious as I created new folders labelled 1 through 9 and cut all the 1s into the 1 folder etc")
        st.write("I then appended the folder name to the end of the file. After implementing the new model called 'given_cells' and tweaking the cropping, the performance rose to 100% over 1320 images")

    if add_selectbox == "Future work":
        st.header("Future work")
        st.write('Goal 1.')
        st.write('Aim to get real time OCR working. This will be problematic due to difficulty processing incoming image and having the required resolution to detect the math operators with larger sized boards')

        st.write('Goal 2.')
        st.write("Occassionaly an error with the OCR occurs making the puzzle impossible to solve. I would like to display all the tesseract images along with the prediciton and allow for manual corrections. This would also rely on streamlit session state which is not working at this point")

    if add_selectbox == "About":
        st.header("About")

        st.write("My name is Declan Stockdale-Garbutt and l'm undertaking a Masters in Data Science in Australia")
        st.write("This project was undertaken as a hobby and to develop various programming skills and gain experience deploying apps.")
