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

The Tesseract directory must be added to the PATH 

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
(streamlit_calcudoku_solver)$ streamlit app.py

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

