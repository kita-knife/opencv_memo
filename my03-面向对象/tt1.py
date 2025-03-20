'''
Here is my attempt. It's in C++, but can be easily ported to python since most are OpenCV functions.

A brief outline of the method, comments in the code should help, too.

- Load the image
- Convert to grayscale
- Binaryze the image (threshold)
- Thinning, to have thin contours and help findContours
- Get contours
- For each contour, get convex hull (to handle open contours), and classify according to circularity. Handle each shape differently.
    Circle : find the minimum encolsing circle, or the best fitting ellipse
    Recrangle : find the boundinx box, or the minimum oriented bounding box.
    Triangle : search for the intersection of the minimum enclosing circle with the original shape, as they would intersect in the three vertices of the triangle.
'''

import cv2
import imutils
from imutils import contours
import numpy as np

img = cv2.imread('children-draw.png')
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img = cv2.threshold(img, 10, 255, cv2.THRESH_BINARY_INV)[1]

refCnts = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
# print(refCnts)
refCnts = imutils.grab_contours(refCnts)
refCnts = imutils.contours.sort_contours(refCnts, method="left-to-right")[0]

# cv2.imshow('ref', img)
# cv2.waitKey(0)

print(refCnts)