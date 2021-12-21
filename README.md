# Extraction of information and drawings 
Splitting data and drawings from an engineering drawing <br />
Able to extract data such as drawing number, date, title, and etc. <br />
Storing extracted data in a Microsoft Excel spreadsheet file <br />
Crop drawings from engineering drawing

## Installation
1. Download or clone this repository

## Download tesseract 
2. You need to have Tesseract OCR installed on your computer. <br />
Download tesseract from https://github.com/UB-Mannheim/tesseract/wiki

## Add tesseract.exe path to your script
3. Find the absolute path for tesseract.exe after installation
```
tess.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
```

## Environment Setup
4. Select python.exe in the Scripts/environment file as the interpreter path to activate the environment if it is not activated yet

## Run the python file
5. Change into the AI_assignment2 directory
```
cd AI_assignment2
```
6.  Run the python script
