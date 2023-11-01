import cv2
import numpy as np
import pytesseract

# Load the image
img = cv2.imread('car.jpg')

# Convert the image to gray scale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Use Sobel operator to detect the edges
sobel = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=3)

# Use threshold to get binary image
ret, threshold = cv2.threshold(sobel, 0, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)

# Use morphological operation to remove noise
element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 9))
element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (24, 6))
dilation = cv2.dilate(threshold, element2, iterations=1)
erosion = cv2.erode(dilation, element1, iterations=1)
dilation2 = cv2.dilate(erosion, element2, iterations=3)

# Find all the contours in the image
contours, hierarchy = cv2.findContours(dilation2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# For each contour, find the bounding rectangle and draw it
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    # Make sure the contour area is big enough
    if cv2.contourArea(cnt) > 2000:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        roi = gray[y:y+h, x:x+w]
        # Use Tesseract to do OCR on the cropped image
        text = pytesseract.image_to_string(roi)
        print("Detected license plate Number is:", text)

# Display the image
cv2.imshow('image', img)
cv2.waitKey(0)
