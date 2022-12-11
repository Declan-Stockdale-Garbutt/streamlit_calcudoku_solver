# streamlit_calcudoku_solver

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





