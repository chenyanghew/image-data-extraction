import numpy as np
import cv2
from matplotlib import pyplot as pt
import openpyxl
import pytesseract as tess
from pytesseract import Output

tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# change this one only
img = cv2.imread('images/04.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 0, 1, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
drawing = gray.copy()
gray_ori = gray.copy()
edges = cv2.Canny(gray, 0, 1)
[nrow, ncol] = edges.shape
full_size = nrow * ncol

# remove the extra padding outside the border
contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
for i in range(0, 1):
    peri = cv2.arcLength(contours[i], True)
    approx = cv2.approxPolyDP(contours[i], 0.01 * peri, True)
    x,y,w,h = cv2.boundingRect(approx)
    area = cv2.contourArea(approx)
    if area > (0.5 * full_size):
        gray = gray[y:y+h, x:x+w]
        [nrow, ncol] = gray.shape
    else:
        i = -1
        peri = cv2.arcLength(contours[i], True)
        approx = cv2.approxPolyDP(contours[i], 0.001 * peri, True)
        x,y,w,h = cv2.boundingRect(approx)
        area = cv2.contourArea(approx)
        gray = gray[y:y+h, x:x+w]
        [nrow, ncol] = gray.shape

# original copy of binary image without outside padding for later use
gray_ori = gray.copy()
gray_ori2 = gray.copy()

# creating a mask and changing all the region that we want to 1
[nrow, ncol] = gray.shape
img_area = nrow * ncol
mask = np.zeros((nrow,ncol), dtype=np.uint8)
for c in contours:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.01 * peri, True)
    x,y,w,h = cv2.boundingRect(approx)
    area = cv2.contourArea(approx)
    if area < (1/2)*img_area and len(approx) == 4:
        mask[y:y+h, x:x+w] = 1

# extracting the region that we want using the mask we created
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25,25))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
contours2,hierarchy2 = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for c in contours2:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.01 * peri, True)
    x,y,w,h = cv2.boundingRect(approx)
    area = cv2.contourArea(approx)
    if area > (1/9)*img_area :
        ROI = gray_ori[y:y+h, x:x+w]
        ROI[ROI >= 1] = 255    

try:
    cv2.imwrite('roi.png',ROI)
    ROI3 = ROI
except: 
    ROI = drawing           
    ROI2 = ROI                  # if no ROI found is invalid, we will use the backup image
    cv2.imwrite('roi.png',ROI)
        
# removing the region from the original image
drawing = cv2.add(gray_ori, mask)   
drawing[drawing >= 1] = 255  
drawing_backup = drawing

# crop the drawings from original image(without title block region)
contours_final, hierarchy_final = cv2.findContours(drawing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
largest = 0
for i in range(0, len(contours_final)):
    peri = cv2.arcLength(contours_final[i], True)
    approx = cv2.approxPolyDP(contours_final[i], 0.01 * peri, True)
    x,y,w,h = cv2.boundingRect(approx)
    area = cv2.contourArea(approx)
    if area != img_area:
        if area > largest:
            largest = area
            drawing = gray_ori[y:y+h, x:x+w]
            drawing[drawing >= 1] = 255    
            cv2.imwrite('drawing.png', drawing)
            [drawing_nrow, drawing_ncol] = drawing.shape
            # check drawing size, because it might select the entire image
            if drawing_nrow*drawing_ncol >= ncol*nrow*0.8:
                drawing = drawing_backup
                [nrow6, ncol6] = drawing.shape
                nrow7 = nrow6 - 200
                ncol7 = ncol6 - 200
                drawing[0:200, :] = 255
                drawing[:, 0:200] = 255
                drawing[nrow7:nrow6, :] = 255
                drawing[:, ncol7:ncol6] = 255
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (500,500))
                kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (20,20))
                drawing = cv2.morphologyEx(drawing, cv2.MORPH_OPEN, kernel, iterations=1)
                drawing = cv2.dilate(drawing, kernel2)
                drawing = cv2.morphologyEx(drawing, cv2.MORPH_OPEN, kernel, iterations=1)
                drawing = cv2.dilate(drawing, kernel2)
                drawing = cv2.bitwise_not(drawing)
                drawing[drawing >= 1] = 1
                contours, hierarchy = cv2.findContours(drawing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                largest2 = 0
                for i in range(0, len(contours)):
                    peri = cv2.arcLength(contours[i], True)
                    approx = cv2.approxPolyDP(contours[i], 0.01 * peri, True)
                    x,y,w,h = cv2.boundingRect(approx)
                    area = cv2.contourArea(approx)
                    if area > largest2:
                        lagest = area
                        drawing = gray_ori2[y:y+h, x:x+w]
                        drawing[drawing >= 1] = 255    
                        cv2.imwrite('drawing.png', drawing)

# using the roi that we obtained 
img = cv2.imread("roi.png", 1)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# append information into an array
contours, hierarchy = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=lambda contour: cv2.boundingRect(contour)[0] + cv2.boundingRect(contour)[1] * gray.shape[1])
data = []
scattered_data = []
[nrow, ncol] = gray.shape
img_size = nrow * ncol
for i in range(1, len(contours)):
    # check whether the drawing number is seperated by small boxes
    if i + 1 < len(contours):
        area = cv2.contourArea(contours[i])
        area2 = cv2.contourArea(contours[i+1])
        if area2 < 1/100 * img_size and area2 > 500:
            peri = cv2.arcLength(contours[i], True)
            approx = cv2.approxPolyDP(contours[i], 0.05 * peri, True)
            x,y,w,h = cv2.boundingRect(approx)
            approx2 = cv2.approxPolyDP(contours[i+1], 0.05 * peri, True)
            x2,y2,w2,h2 = cv2.boundingRect(approx2)
            ROI = gray[y:y+h+h2, x:x+w]
            text = tess.image_to_string(ROI)
            extra = "!@#$%^&*()_+-={}|[]\;',/<>?`~" 
            for char in extra:                  # remove any weird symbol
                text = text.replace(char, "")
            text = " ".join(text.split())       # remove any spaces
            if ":" in text:
                text2 = text.split(":")
                text2[0] += ":"
                scattered_data.append(text2)
    peri = cv2.arcLength(contours[i], True)
    approx = cv2.approxPolyDP(contours[i], 0.05 * peri, True)
    x,y,w,h = cv2.boundingRect(approx)
    ROI = gray[y:y+h, x:x+w]
    text = tess.image_to_string(ROI)
    text = " ".join(text.split())
    if "[" in text:
        text = text.replace("[", "|")
    if "]" in text:
        text = text.replace("]", "|")
    if ":" in text:
        text = text.split(":")
        text[0] += ":"
        data.append(text)

# replace current information with a more reliable one
for d in range(len(scattered_data)):
    a = scattered_data[d][0]
    for d2 in range(len(data)):
        if data[d2][0] == a and scattered_data[d][1] != '':
            data[d2][1] = scattered_data[d][1]
   
# if there is less than lets say 8 data; that means the roi that is extracted is probably just one part of it
if len(data) < 8:
    contours, hierarchy = cv2.findContours(gray_ori, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda contour: cv2.boundingRect(contour)[0] + cv2.boundingRect(contour)[1] * gray.shape[1])
    data = []
    scattered_data = []
    [nrow, ncol] = gray_ori.shape
    img_size = nrow * ncol
    for i in range(1, len(contours)):
        if i + 1 < len(contours):
            area = cv2.contourArea(contours[i])
            area2 = cv2.contourArea(contours[i+1])
            if area2 < 1/100 * img_size and area2 > 500:
                peri = cv2.arcLength(contours[i], True)
                approx = cv2.approxPolyDP(contours[i], 0.05 * peri, True)
                x,y,w,h = cv2.boundingRect(approx)
                approx2 = cv2.approxPolyDP(contours[i+1], 0.05 * peri, True)
                x2,y2,w2,h2 = cv2.boundingRect(approx2)
                ROI = gray_ori[y:y+h+h2, x:x+w]
                text = tess.image_to_string(ROI)
                extra = "!@#$%^&*()_+-={}|[]\;',/<>?`~" 
                for char in extra:                  # remove any weird symbol
                    text = text.replace(char, "")
                text = " ".join(text.split())       # remove any spaces
                if ":" in text:
                    text2 = text.split(":")
                    text2[0] += ":"
                    scattered_data.append(text2)
        peri = cv2.arcLength(contours[i], True)
        approx = cv2.approxPolyDP(contours[i], 0.05 * peri, True)
        x,y,w,h = cv2.boundingRect(approx)
        ROI = gray_ori[y:y+h, x:x+w]
        text = tess.image_to_string(ROI)
        text = " ".join(text.split())
        if "[" in text:
            text = text.replace("[", "|")
        if "]" in text:
            text = text.replace("]", "|")
        if ":" in text:
            text = text.split(":")
            text[0] += ":"
            if len(text) == 2:
                data.append(text)
                
# if we cant extract information from the ROI
extra_step = False
if len(data) == 0:
    try:
        gray_ori = ROI2
    except:
        gray_ori = ROI3
    contours, hierarchy = cv2.findContours(gray_ori, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda contour: cv2.boundingRect(contour)[0] + cv2.boundingRect(contour)[1] * gray.shape[1])
    data = []
    scattered_data = []
    for i in range(1, len(contours)):
        peri = cv2.arcLength(contours[i], True)
        approx = cv2.approxPolyDP(contours[i], 0.05 * peri, True)
        x,y,w,h = cv2.boundingRect(approx)
        area = cv2.contourArea(contours[i])
        if area > 5000:
            ROI = gray_ori[y:y+h, x:x+w]
            text = tess.image_to_string(ROI)
            text = " ".join(text.split())
            if "=" in text:
                text = text.replace("=", "-")
            if "[" in text:
                text = text.replace("[", "|")
            if "]" in text:
                text = text.replace("]", "|")
            if ":" in text:
                text = text.split(":")
                text[0] += ":"
                if len(text) == 2:
                    data.append(text)
    extra_step = True

# to remove any duplicates
if extra_step == True:
   data_set = set(map(tuple,data))
   new_data = map(list,data_set)
        
# lastly, insert all data into an excel file    
book = openpyxl.Workbook()
if extra_step == False:
    for info in data:
        sheet = book.active
        sheet.append(info)
        book.save("Information.xlsx")
if extra_step == True:
    for info in new_data:
        sheet = book.active
        sheet.append(info)
        book.save("Information.xlsx")


