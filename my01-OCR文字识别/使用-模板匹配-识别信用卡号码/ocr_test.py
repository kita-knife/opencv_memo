# import the necessary packages
from imutils import contours
import pytesseract
import numpy as np
import argparse
import imutils
import cv2

args = {'image':'card1.png',
        'reference':'reference.png'
        }

# define a dictionary that maps the first digit of a credit card
# number to the credit card type
FIRST_NUMBER = {
	"3": "American Express",
	"4": "Visa",
	"5": "MasterCard",
	"6": "Discover Card"
}

# load the reference OCR-A image from disk, convert it to grayscale,
# and threshold it, such that the digits appear as *white* on a
# *black* background
# and invert it, such that the digits appear as *white* on a *black*
ref = cv2.imread(args["reference"])
ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
ref = cv2.threshold(ref, 10, 255, cv2.THRESH_BINARY_INV)[1]
ref = cv2.resize(ref, (540, 82))

# cv2.imshow('ref', ref)
# cv2.waitKey(0)
# assert None
##Now let’s locate contours on our OCR-A font image:

# find contours in the OCR-A image (i.e,. the outlines of the digits)
# sort them from left to right, and initialize a dictionary to map
# digit name to the ROI
refCnts = cv2.findContours(ref.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
# print(refCnts)
refCnts = imutils.grab_contours(refCnts)
refCnts = contours.sort_contours(refCnts, method="left-to-right")[0]
# cv2.drawContours(ref, refCnts, -1, (0,0,255), 3)
# cv2.imshow('ref', ref)
# cv2.waitKey(0)
# print(refCnts[0].size)
digits = {}

# loop over the OCR-A reference contours
row,col=ref.shape
# print(col,row)
per = col//10
for i in range(10):
	# compute the bounding box for the digit, extract it, and resize
	# it to a fixed size
	roi = ref[:, i*per:per*(i+1)]
	roi = cv2.resize(roi, (57, 88))
	# img2 = cv2.rectangle(ref, (i*per,0), ((i+1)*per,row), (0,0,255),2)
	# cv2.imshow('image', ref)
	# cv2.waitKey(0)

	# update the digits dictionary, mapping the digit name to the ROI
	digits[i] = roi
# for loc in digits:
#     x, y, w, h = loc
#     img2 = cv2.rectangle(ref, (x,y), (x+w,y+h), 255,2)
# cv2.imshow('image', img2)
# cv2.waitKey(0)


# print(len(digits.items()))

# assert None
# initialize a rectangular (wider than it is tall) and square
# structuring kernel
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

# load the input image, resize it, and convert it to grayscale
image = cv2.imread(args["image"])
image = imutils.resize(image, width=300)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# cv2.imshow('gray', gray)
# cv2.waitKey(0)

# apply a tophat (whitehat) morphological operator to find light
# regions against a dark background (i.e., the credit card numbers)
tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, rectKernel)

# cv2.imshow('tophat', tophat)
# cv2.waitKey(0)

# compute the Scharr gradient of the tophat image, then scale
# the rest back into the range [0, 255]
gradX = cv2.Sobel(tophat, ddepth=cv2.CV_32F, dx=1, dy=0,
	ksize=-1)
gradX = np.absolute(gradX)
(minVal, maxVal) = (np.min(gradX), np.max(gradX))
gradX = (255 * ((gradX - minVal) / (maxVal - minVal)))
gradX = gradX.astype("uint8")

# cv2.imshow('gradX', gradX)
# cv2.waitKey(0)

# apply a closing operation using the rectangular kernel to help
# cloes gaps in between credit card number digits, then apply
# Otsu's thresholding method to binarize the image
gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
thresh = cv2.threshold(gradX, 0, 255,
	cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# apply a second closing operation to the binary image, again
# to help close gaps between credit card number regions
thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)

# cv2.imshow('thresh', thresh)
# cv2.waitKey(0)

# find contours in the thresholded image, then initialize the
# list of digit locations
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
locs = []
locs1 = []
# print(cnts[0])

# assert None
# loop over the contours
for (i, c) in enumerate(cnts):
	# compute the bounding box of the contour, then use the
	# bounding box coordinates to derive the aspect ratio
	(x, y, w, h) = cv2.boundingRect(c)
	locs1.append((x, y, w, h))
	# locs.append((x, y, w, h))
	# print(x,y,x,h)
	ar = w / float(h)

	# since credit cards used a fixed size fonts with 4 groups
	# of 4 digits, we can prune potential contours based on the
	# aspect ratio
	if ar > 2.5 and ar < 4.0:
		# contours can further be pruned on minimum/maximum width
		# and height
		if (w > 40 and w < 55) and (h > 10 and h < 20):
			# append the bounding box region of the digits group
			# to our locations list
			locs.append((x, y, w, h))

# for loc in locs1:
#     x, y, w, h = loc
#     img2 = cv2.rectangle(gradX, (x,y), (x+w,y+h), 255,2)
# cv2.imshow('image', img2)
# cv2.waitKey(0)
# assert None

# sort the digit locations from left-to-right, then initialize the
# list of classified digits
locs = sorted(locs, key=lambda x:x[0])
output = []

# loop over the 4 groupings of 4 digits
for (i, (gX, gY, gW, gH)) in enumerate(locs):
	# initialize the list of group digits
	groupOutput = []

	# extract the group ROI of 4 digits from the grayscale image,
	# then apply thresholding to segment the digits from the
	# background of the credit card
	group = gray[gY - 5:gY + gH + 5, gX - 5:gX + gW + 5]
	group = cv2.threshold(group, 0, 255,
		cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	# cv2.imshow('image', group)
	# cv2.waitKey(0)

	# detect the contours of each individual digit in the group,
	# then sort the digit contours from left to right
	digitCnts = cv2.findContours(group.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	digitCnts = imutils.grab_contours(digitCnts)
	digitCnts = contours.sort_contours(digitCnts,
		method="left-to-right")[0]
	# print(len(digitCnts))
    # loop over the digit contours
	for c in digitCnts:
		# compute the bounding box of the individual digit, extract
		# the digit, and resize it to have the same fixed size as
		# the reference OCR-A images
		
		(x, y, w, h) = cv2.boundingRect(c)
		roi = group[y:y + h, x:x + w]
		roi = cv2.copyMakeBorder(roi,3,3,3,3,cv2.BORDER_CONSTANT,value=[0,0,0])
		roi = cv2.resize(roi, (57, 88))
		kernel = np.ones((5,5),np.uint8)
		roi = cv2.erode(255-roi,kernel,iterations = 1)
		roi = cv2.GaussianBlur(roi, (5, 5), 0)
		# cv2.imshow('Gaussian Blurred Image', roi)
		# cv2.waitKey(0)

		# initialize a list of template matching scores	
		scores = []
		# loop over the reference digit name and digit ROI
	
		for (digit, digitROI) in digits.items():
			# apply correlation-based template matching, take the
			# score, and update the scores list
			result = cv2.matchTemplate(roi, digitROI,
				cv2.TM_CCOEFF)
			# cv2.imshow("roi", roi)
			# cv2.waitKey(0)
			# cv2.imshow("digitROI", digitROI)
			# cv2.waitKey(0)
			(_, score, _, _) = cv2.minMaxLoc(result)
			# print("score is:",score)
			# print(score)
			scores.append(score)
		# print(scores)
		# the classification for the digit ROI will be the reference
		# digit name with the *largest* template matching score
		groupOutput.append(str(np.argmax(scores)))
		
        # draw the digit classifications around the group
	cv2.rectangle(image, (gX - 5, gY - 5),
		(gX + gW + 5, gY + gH + 5), (0, 0, 255), 2)
	cv2.putText(image, "".join(groupOutput), (gX, gY - 15),
		cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)

	# update the output digits list
	output.extend(groupOutput)

# print(output)
# display the output credit card information to the screen
print("Credit Card Type: {}".format(FIRST_NUMBER[output[0]]))

print("Credit Card #: {}".format("".join(output)))
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
