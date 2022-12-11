# streamlit calcudoku solver

This program was built to solve calcudoku puzzles from the calcudoku app on the Google play store.
Calcudoku puzzles are identical to KenKen puzzles

## How it works
This program utilizes Streamlit to find solutions to uploaded calcudoku puzzles
All image processing is performed using OpenCV. 
The text extraction iis performed using a trained Tesseract model.
The puzzle solving is performed using code from https://github.com/chanioxaris/kenken-solver.


## App deployment

### Heroku
This app has been deployed on Heroku https://calcudokusolver.herokuapp.com/ Heroku has undergone updates since deployment and app may no longer be functional


### Run Locally
This is alot more involved and may involve modifying the code to include paths to relevant files

The Tesseract directory must be added to the PATH. Links to download here https://github.com/tesseract-ocr/tessdoc/blob/main/Installation.md

In calcucdoku_solver.py lines 235, 354 should point to tessdata folder e.g. --tessdata-dir "tessdata directory" --psm 6 --oem 3 

 Mine looks like this --tessdata-dir "C:/Program Files/Tesseract-OCR/tessdata" --psm 6 --oem 3
 
The tessdata folder whoul also have the math_cells and given_cells traineddata files. If not, copy them into the folder.
 
 
```bash
# Create virtual environment click y to install additional downloads if required
$ conda create -n streamlit_calcudoku_solver python=3.8

# Activate the virtual environment:
$ conda activate streamlit_calcudoku_solver

# clone directory into virtual environment
(streamlit_calcudoku_solver)$ git clone https://github.com/Declan-Stockdale/streamlit_calcudoku_solver.git

# move into virtual environment directory
$ cd streamlit_calcudoku_solver

# install required python packages
(streamlit_calcudoku_solver)$ pip install -r requirements.txt

# Run the app
(streamlit_calcudoku_solver)$ streamlit run app.py

# To deactivate (when you're done):
(streamlit_calcudoku_solver)$ conda deactivate
```

To access the app later without re-installing it

```bash
# Activate the environment
$conda activate streamlit_calcudoku_solver

# navigate inside the directory
(streamlit_calcudoku_solver)$cd streamlit_calcudoku_solver

# run app
(streamlit_calcudoku_solver)$stremlit run app.py

# To deactivate (when you're done):
(streamlit_calcudoku_solver)$ conda deactivate
```

## Functionality

### Main page
#### Uploading a fil
Must uplaod a relevant file here. Examples are available in the link to the github page.

![image](https://user-images.githubusercontent.com/53500810/206888390-b7610bd1-5712-44ce-9ddd-77024d5aa2d6.png)

Here is a suitable 8x8 board taken from a screenshot of the calcudoku app on the Google play store

![image](https://user-images.githubusercontent.com/53500810/206888437-7ffa0541-37f3-4c9e-a0c7-50ce9ee56de2.png)

#### Displaying the puzzle
Once a suitable file is uploaded, tha pop will show the captured image along with the playing area

![image](https://user-images.githubusercontent.com/53500810/206888491-efd034b8-c784-4c54-bb7c-2c52c37ebada.png)


![image](https://user-images.githubusercontent.com/53500810/206888507-4e355bf9-07e3-451d-b1ff-b5a6e5e5f6e0.png)

#### Solving the puzzle
A spinning image may appear while the puzzle is completed. When it has finished, it will be displayed along with time to complete. The larger the puzzle, the longer the time to solve.

![image](https://user-images.githubusercontent.com/53500810/206888559-eb9356f3-ddf6-4dc3-8cbf-0f10b4840bb1.png)


There is also the option to change the colour to one of nuerous options

![image](https://user-images.githubusercontent.com/53500810/206888577-ad9a853f-09f0-4f51-b797-c8891f186456.png)


![image](https://user-images.githubusercontent.com/53500810/206888583-7016a40c-7d46-4cec-8681-345c6e299b1c.png)

## How it works

The python computer vision library Opencv2 is used to process and detect various features within the uploaded image. For opencv2 to function correctly, the image as a bytes type object must be converted to a numpy array for proper opencv2 functionality.

The image is converted into a back and white image for easier processing

![grayscale of input](https://user-images.githubusercontent.com/53500810/206888769-71bb4081-f260-4c97-a95f-a9f321d7138e.jpeg)


Various other preprocessing steps such as blurring, canning, dialiation and eroding occur to remove noise for easier grid detection

![Blur of input](https://user-images.githubusercontent.com/53500810/206888729-91e3c26a-b3d6-4d17-bb3d-4d9fd04be5c5.jpeg)
![Canny of input](https://user-images.githubusercontent.com/53500810/206888749-7371d06a-22d3-4137-a97e-c004ac72887e.jpeg)
![Dialiation of inpu](https://user-images.githubusercontent.com/53500810/206888751-58fd66df-e0f9-4d68-9b08-c471b26aa1f4.jpeg)
![Erosion of input](https://user-images.githubusercontent.com/53500810/206888784-f534bd39-a38d-4527-984b-d51cf90dd1b9.jpeg)


The next step is find the coordinates of the largest area enclosed within white lines. Assuming there is minimal noise, this should be the playing grid

The coordinates are given as top left, bottom left, bottom right, top right
![Unordered contour coordinates](https://user-images.githubusercontent.com/53500810/206888781-f4e96f27-8663-4de8-9708-655e33f07cae.JPG)


These are rearranged to be top left, top right, bottom left, bottom right
![Uploading Ordered contour coordinates.JPG…]()

The grid is then rotated and scaled to make it a square which is then displayed for the user to see.
![Black and white grid](https://user-images.githubusercontent.com/53500810/206888796-89e92914-b924-446b-ac93-a9c42f11fb5d.jpg)

#### Finding number of cells
The number of cells is found firstly by rastering vertically and recording the distance between white pixels. The same is done with a horizontal raster

Small values are removed (encountered noise, a math operator or a given cell)

The minimum value of the remaining values is recorded as the cell length in pixels, other values should be multiple of this value e.g. two cells, three cells

It's performed horizontally and vertcally incase there is a weird grid e.g. all cells are horizontally connected which wouldn't find the cell lengh on a horizontal raster

The number of cells is found by dividing the shape of the size of the square grid from the previous section by the cell length rounded to the nearest integer

### Finding connected cells
A raster process similar to the one used to find cell pixel size is implemented

From the previous step we know the cell size and shape and can determine the coordinates of each box within the calcudoku grid.

We will iterate over the pixels which constiture the borders of boxes to determine if they are connected.

If no border is encountered (e.g. no white pixels) along the entire search length, then the boxes must be connected as there is no border between them.

Instead of starting at the top of the cell, to save some computation, we'll start at the 3/4 distance and search until we hit the first 1/4 of the next box

By doing this we are only searching half the box distance and should avoid hitting math operators which occur in the top left of boxes.

This process is first performed vertically then horizontally

Graph networking is implemented to find boxes such as L shaped or squares where there's a box connected vertically and horizontally

The returned result is a list of connected boxes where each box coordinates is returned as a tuple

All the math operators are in te top left most square of all connected boxes so sorting the returned list by these allows us to get cells containing math operators

In addition we can find all the cells containing given values by finding all cells not in the connected cell list

#### Optical Character Recognition (OCR) using Tesseract
Two custom models were trained following the instructions in this article https://towardsdatascience.com/simple-ocr-with-tesseract-a4341e4564b6

The first model math_cells is used to detect math operators, while the second given_cells is used to predict gven numbers in cells

There is minor tweaking on the predicions for the math_cells with multiple math operators occuring in some predicitons such as 7+x where we only want 7+ etc

The final output from both OCR results is a list of the connected boxes operator number (e.g. [(0,0),(0,1)] add 7)

This output is then put through the kenken solver adapted from code from this repository https://github.com/chanioxaris/kenken-solver

The output is an array of the results

To write the output onto the image we have do do a bit more work

### Writing output to image
The output from the kenken solver is an array and the list of centre pixel coordinates is a flat list

By matching the index of the array as a number we can grab the centre pixel values of the box where we want to write that prediction to

Once we have a list of middle cell coordinates and the prediction we can write it onto the original grid image

A few modificaitons must be made first, largely as opencv2 writes the text starting with the bottom left where the coordinates are specified. The coordinates we have are for the centre of the box and will need to be modified.

The centre coordinate need to adjusted by the size of the height and width of the written text to diplay nicely

As each box can contain only one number and they are quite similar in size, we can modify all the coordinates by the same value.


## Training Optical Character Recognition
This section goes into the detail regarding training the two custom tesseract models

Following on from the instruction provided in this article https://towardsdatascience.com/simple-ocr-with-tesseract-a4341e4564b6

I along with other commenters on the article struggled with various steps to build the relevant files. I tried various versions of tesseract and found that only version 5.0.0.20190623 worked whereas 4 other installations failed at various steps.

### Why was training necessary?
The reason further training was required was becuase tesseract with its base 'eng' model wasn't accurate enough to detect either the numbers or the math operators.

I don't think it has the capacity to detect the divide ÷ symbol which made passing the relevant arguments to the main solver impossible

To find out exactly how accurate the native tesseract "eng" model is, I wrote a script in jupyter notebook to compare the prediction to the labelled data

The inital accuracy was around 50 - 60% using the 3342 labelled data points but with experimenting to try and remove cell borders, additional cropping improved the performance up to ~ 70%

This was clearly not good enough and a custom model needed to be implemented

### Generating the data
The first step was to generate some training data. This was performed by taking hundreds of screenshots of calcudoku games mostly 9x9 as to generate the most number of math operators within the shortest period of time.

The screen shots were parsed through the main calcudoku program up until the point where OCR occurs

At this point the images were saved to a seperate training folder with each file being named number_ witht he first 1_, the second 2_ and so on. There were about 7000 images generated

I manually labelled 3342 images with their corresponding math operators, so the file name was number_mathoperator. If the math operator of the first image was 280+, it would be named 1_280+. This was time consuming and errors were made.

### Labelling process
Over 250 labelled math operator images using JTess box editor to properly identify and relabel images.

![math_jtess_box_editor](https://user-images.githubusercontent.com/53500810/206888954-bf4e5119-a637-4ce6-b6ed-d9db3026abbd.JPG)

The most common misses from the "eng" model were that the numbers were poorly captured and if they were, they were mistaken as letters or the crop size was far too large including signifacant black space to eith side of the intended number. The multiplication sign was commonly mistaken for addition sign and the divide sign was never captured.

Through tedious relabelling of the numerous incorrectly labelled images, a model could be built following the tutorial

This custom model was named math_cells


### Math_cell model vs native Tesseract performance
Running the same jupyter notebook but now with the new model called "math_cells", the accuracy of tesseract improved enormously up to 98%. It was still giving errors such as 72x was shown as x72x along with multiple math symbols being detected

I included the filename of wrongly predicted images to make sure I had labelled them correctly and this was the main source of error at this stage with 30 incorrecly labelled images needing to be relabelled.

I wrote some additional line of code to detect common errors in the tesseract predicitons which led to a final accuracy of 99.71% over 3342 images.

### Given_cells vs native Tesseract performance
A very similar process was performed on boxes containing given values or what I occassionally refer to as solid cells.

![solid_jtess_box_edior](https://user-images.githubusercontent.com/53500810/206888960-2b52f781-5654-4fb2-a0dd-9ab4e10aa531.JPG)

The labelling process was less tedious as I created new folders labelled 1 through 9 and cut all the 1s into the 1 folder etc

I then appended the folder name to the end of the file. After implementing the new model called 'given_cells' and tweaking the cropping, the performance rose to 100% over 1320 images



