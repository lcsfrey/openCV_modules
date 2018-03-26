# /************************************************************************************
# **                                                                                 **
# **  MIT License                                                                    **
# **                                                                                 **
# **  Copyright (c) 2017 Lucas Frey                                                  **
# **                                                                                 **
# **  Permission is hereby granted, free of charge, to any person obtaining          **
# **  a copy of this software and associated documentation files (the "Software"),   **
# **  to deal in the Software without restriction, including without limitation      **
# **  the rights to use, copy, modify, merge, publish, distribute, sublicense,       **
# **  and/or sell copies of the Software, and to permit persons to whom the          **
# **  Software is furnished to do so, subject to the following conditions:           **
# **                                                                                 **
# **  The above copyright notice and this permission notice shall be included        **
# **  in all copies or substantial portions of the Software.                         **
# **                                                                                 **
# **  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS        **
# **  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    **
# **  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE    **
# **  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER         **
# **  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  **
# **  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  **
# **  SOFTWARE.                                                                      **
# **                                                                                 **
# ************************************************************************************/
 #############################
 #                           #
 #   Basic Security Camera   #
 #       By Lucas Frey       #
 #                           #
 #############################
import numpy as np
import cv2
import time
import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


from datetime import datetime

# Global variables
# index of the webcam that the app is using
WEBCAM_CHOICE = 0

# webcam resolution
webcam_resolution = (640, 480)

CAN_RECORD = False

# frame conversion properties
FONT = cv2.FONT_HERSHEY_SIMPLEX
CURRENT_FRAME_COUNT = 0
CANNY_MIN = 80
CANNY_MAX = 255
THRESH_MIN = 20

THRESH_MAX = 255
MIN_PIXELS = 1000
kernel7 = np.ones((5, 5), np.uint8)
kernel5 = np.ones((5, 5), np.uint8)
kernel3 = np.ones((3, 3), np.uint8)


# Read in number to use for new file name
# Initialize recording
# returns a file writing object
def start_recording():
    myfile = None
    filecount = -1
    countfile = os.path.join(THIS_FOLDER, 'output_count.txt')

    # Check if file exists and read in current  it if it does
    if os.path.exists(countfile):
        myfile = open(countfile, 'r+')
        filecount = myfile.read()
        int_filecount = int(filecount)
    else:
        myfile = open(countfile, 'w+')
    myfile.close()
    
    if int_filecount is -1:
        int_filecount = 0

    # define codec and filename
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    str_filecount = str(int_filecount)
    filename = 'movement_@_'
    mytime = time.strftime("  %d_%b_%Y_%x")
    filename = filename + mytime + '.avi'

    # increment avi filecount and store it back to output_count.txt
    out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
    int_filecount = int_filecount + 1
    myfile = open('output_count.txt', 'w')
    str_filecount = str(int_filecount)
    myfile.write(str_filecount)
    myfile.close()
    return out


# Initialize blob detector
# returns a blob detector
def detector():
    params = cv2.SimpleBlobDetector_Params()
    # Change thresholds
    params.minThreshold = 10
    params.maxThreshold = 255
    # Filter by Area.
    params.filterByArea = True
    params.minArea = 150

    detector = cv2.SimpleBlobDetector_create(params)
    return detector

# Needed for trackbar initialization
def nothing(x):
    x = x
    return x
# Create a black image, a window
img = np.zeros((300, 512, 3), np.uint8)
cv2.namedWindow('image')
# create trackbars for thresholds
cv2.createTrackbar('CANNY_MIN', 'image', 0, 255, nothing)
cv2.createTrackbar('CANNY_MAX', 'image', 0, 255, nothing)
cv2.createTrackbar('THRESH_MIN', 'image', 10, 255, nothing)
cv2.createTrackbar('THRESH_MAX', 'image', 255, 255, nothing)

cv2.createTrackbar('MIN_PIXELS', 'image', 500, 10000, nothing)

# update the trackbars
# (NOTE: currently unused. Program is currently reading trackbars from main)
def processes_trackbars(CANNY_MIN, CANNY_MAX, THRESH_MIN, THRESH_MAX, MIN_PIXELS):
    # get current positions of trackbars
    CANNY_MIN = cv2.getTrackbarPos('CANNY_MIN', 'image')
    CANNY_MAX = cv2.getTrackbarPos('CANNY_MAX', 'image')
    THRESH_MIN = cv2.getTrackbarPos('THRESH_MIN', 'image')
    THRESH_MAX = cv2.getTrackbarPos('THRESH_MAX', 'image')
    MIN_PIXELS = cv2.getTrackbarPos('MIN_PIXELS', 'image')

# initialize capture to default webcam
# initialize video writer
# initialize detector
# begin reading in frames
cap = cv2.VideoCapture(WEBCAM_CHOICE)
out = start_recording()
#out_thresh = start_recording()
detector = detector()

ret, frame1 = cap.read()
if ret is False:
    print("ERROR: couldn't read in frame1")
frame2 = frame1.copy()

# initialize resize data
# initialize older frame timeslots
r = 315.0 / frame1.shape[1]
dim = (315, int(frame1.shape[0] * r))
gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
difference = cv2.absdiff(gray1, gray2)
older_difference = difference.copy()
older_resized_threshold = difference.copy()
old_gray = gray2.copy()
older_gray = gray2.copy()

# Main while loop
while True:
    # Keyboard commands
    #   R = Allow/Disallow recording
    #   Q = Quit
    key = cv2.waitKey(1)
    if key == ord('r'):
        if CAN_RECORD is False:
            CAN_RECORD = True
        else:
            CAN_RECORD = False
    if key == ord('q'):
        break
    # Capture frame-by-frame, skipping loop if frame not read
    ret, frame2 = cap.read()
    if ret is False:
        continue
    frame1Copy = frame1.copy()
    frame2Copy = frame2.copy()

    # get current positions of trackbars
    CANNY_MIN = cv2.getTrackbarPos('CANNY_MIN', 'image')
    CANNY_MAX = cv2.getTrackbarPos('CANNY_MAX', 'image')
    THRESH_MIN = cv2.getTrackbarPos('THRESH_MIN', 'image')
    THRESH_MAX = cv2.getTrackbarPos('THRESH_MAX', 'image')
    MIN_PIXELS = cv2.getTrackbarPos('MIN_PIXELS', 'image')

    # Gray and blur images
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    cv2.blur(gray1, (3, 3), gray1)
    cv2.blur(gray2, (3, 3), gray2)

    # Difference and Threshold images
    # Combine with threshold older frames, erode image and dilate
    difference = cv2.absdiff(gray1, gray2)
    difference_copy = difference.copy()
    ret, resized_threshold = cv2.threshold(difference, THRESH_MIN, THRESH_MAX, cv2.THRESH_BINARY)
    resized_threshold_copy = resized_threshold.copy()
    cv2.bitwise_or(resized_threshold, older_resized_threshold.copy(), resized_threshold)
    cv2.erode(resized_threshold, kernel3, resized_threshold)
    #cv2.dilate(resized_threshold, kernel5, resized_threshold)

    cv2.imshow('threshold', resized_threshold)

    # Create canny image
    canny_gray_copy = gray2.copy()
    img_canny = cv2.Canny(canny_gray_copy, CANNY_MIN, CANNY_MAX)
    cv2.dilate(img_canny, kernel3,img_canny)

    # Find and draw contours around movement
    movement = frame2Copy.copy()
    thresh_contours = resized_threshold.copy()
    _, cnts, hierarchy = cv2.findContours(thresh_contours, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    max_size = 0
    max_size_contour = None
    
    # for every contour
    for cnt in cnts:
        contour_area = cv2.contourArea(cnt)
        if contour_area > max_size:
            x, y, w, h = cv2.boundingRect(cnt)
            # cv2.rectangle(movement, (x, y), (x + w, y + h), (0, 255, 0), 2)
            max_size_contour = cnt
            max_size = contour_area
        if contour_area > MIN_PIXELS:
            cv2.drawContours(movement, cnt, -1, (255, 0, 255), 2)
    # if recording has been enabled
    #   count the area of white pixels in the threshold
    #   if threshold image shows a large amount of white pixels(when there's movement on the screen),
    #       start recording
    #       print the amount of white pixels
    #       activate recording
    #   if we can record
    #       write frame to file
    # else
    #   prints that recording is turned off
    if CAN_RECORD is True:
        num_non_zeros = 0
        if start_recording is False or CURRENT_FRAME_COUNT % 16 is not 0:
            num_non_zeros = cv2.countNonZero(resized_threshold)
        if MIN_PIXELS+150 > num_non_zeros > MIN_PIXELS:
            CURRENT_FRAME_COUNT = 1
            start_recording = True
        if start_recording is True and 8 >= CURRENT_FRAME_COUNT > 0:
            CURRENT_FRAME_COUNT += 1
            # cv2.putText(movement, 'Size of blobs: ' + str(num_non_zeros), (5, 40), FONT, .75, (0, 255, 0), 2)
            str_date = str(datetime.now())
            cv2.putText(movement, str_date, (5, 20), FONT, .75, (0, 0, 255), 3)
            cv2.putText(movement, str_date, (5, 20), FONT, .75, (255, 0, 0), 1)
            out.write(movement)
            cv2.putText(movement, 'Press R to stop', (5, 40), FONT, .75, (150, 255, 50), 2)
            # thresh_to_write = cv2.cvtColor(resized_threshold.copy(),  cv2.COLOR_GRAY2BGR)
            # out_thresh.write(resized_threshold)
        else:
            cv2.putText(movement, 'Recording is on', (5, 20), FONT, .75, (150, 255, 50), 2)
            CURRENT_FRAME_COUNT = 0
            start_recording = False
    else:
        if CAN_RECORD is False:
            print("Recording turned off")
            cv2.putText(movement, 'Recording is off', (5, 20), FONT, .75, (0, 0, 255), 2)
            cv2.putText(movement, 'Press R to record', (5, 40), FONT, .75, (0, 0, 255), 2)

        CURRENT_FRAME_COUNT = 0
        start_recording = False

    cv2.putText(movement, 'Press Q to quit', (5, 60), FONT, .75, (0, 0, 255), 2)

    def showFrames(frame_names, frames):
            for i in range(len(frames)):
                cv2.imshow(frame_names[i], frames[i])

    frame_names = ["movement", "canny", "threshold"]
    frames = [movement, img_canny, resized_threshold]
    showFrames(frame_names, frames)

    # Push frames into older time slots
    frame1 = frame2Copy
    older_gray = old_gray
    old_gray = gray1
    gray1 = gray2
    older_difference = difference_copy
    older_resized_threshold = resized_threshold_copy

# Release everything if job is finished
out.release()
cap.release()
cv2.destroyAllWindows()
