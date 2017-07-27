#############################
#                           #
#   Basic Security Camera   #
#       By Lucas Frey       #
#                           #
#############################
import numpy as np
import cv2
import time

# Global variables
can_record = False
recording_already_started = False
font = cv2.FONT_HERSHEY_SIMPLEX
webcam_resolution = 640 * 480
count_frames = 0
num_non_zeros = 0;
cannyMin = 80
cannyMax = 255
threshMin = 170
threshMax = 255
minPixels = 1000
kernel7 = np.ones((5, 5), np.uint8)
kernel5 = np.ones((5, 5), np.uint8)
kernel3 = np.ones((3, 3), np.uint8)


# Read in number to use for new file name
# Initialize recording
# returns a file writing object
def start_recording():
    myfile = open('output_count.txt', 'r+')
    filecount = -1
    filecount = myfile.read()
    myfile.close()
    int_filecount = int(filecount)
    if int_filecount is -1:
        int_filecount = 0
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    str_filecount = str(int_filecount)
    filename = 'movement_#' + str_filecount
    mytime = time.strftime("  %d_%m_%Y")
    filename = filename + mytime + '.avi'
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
cv2.createTrackbar('cannyMin', 'image', 0, 255, nothing)
cv2.createTrackbar('cannyMax', 'image', 0, 255, nothing)
cv2.createTrackbar('threshMin', 'image', 10, 255, nothing)
cv2.createTrackbar('threshMax', 'image', 255, 255, nothing)
cv2.createTrackbar('minPixels', 'image', 1000, 5000, nothing)

# update the trackbars
# (NOTE: currently unused. Program is currently reading trackbars from main)
def processes_trackbars(cannyMin, cannyMax, threshMin, threshMax, minPixels):
    # get current positions of trackbars
    cannyMin = cv2.getTrackbarPos('cannyMin','image')
    cannyMax = cv2.getTrackbarPos('cannyMax','image')
    threshMin = cv2.getTrackbarPos('threshMin','image')
    threshMax = cv2.getTrackbarPos('threshMax','image')
    minPixels = cv2.getTrackbarPos('minPixels', 'image')

# initialize capture to default webcam
# initialize video writer
# initialize detector
# begin reading in frames
cap = cv2.VideoCapture(0)
out = start_recording()
detector = detector()
ret, frame1 = cap.read()
while ret is False:
    ret, frame1 = cap.read()
ret, frame2 = cap.read()
while ret is False:
    ret, frame2 = cap.read()

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
    # Capture frame-by-frame, skipping loop if frame not read
    # Make copies of original frames
    ret, frame2 = cap.read()
    if ret is False:
        continue
    frame1Copy = frame1.copy()
    frame2Copy = frame2.copy()

    # get current positions of trackbars
    cannyMin = cv2.getTrackbarPos('cannyMin','image')
    cannyMax = cv2.getTrackbarPos('cannyMax','image')
    threshMin = cv2.getTrackbarPos('threshMin','image')
    threshMax = cv2.getTrackbarPos('threshMax','image')
    minPixels = cv2.getTrackbarPos('minPixels', 'image')

    # Gray and blur images
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    cv2.blur(gray1, (3, 3), gray1)
    cv2.blur(gray2, (3, 3), gray2)

    # Difference and Threshold images
    # Combine with threshold older frames, erode image and dilate
    difference = cv2.absdiff(gray1, gray2)
    difference_copy = difference.copy()
    ret, resized_threshold = cv2.threshold(difference, threshMin, threshMax, cv2.THRESH_BINARY)
    resized_threshold_copy = resized_threshold.copy()
    cv2.bitwise_or(resized_threshold, older_resized_threshold.copy(), resized_threshold)
    cv2.erode(resized_threshold, kernel3, resized_threshold)
    cv2.dilate(resized_threshold, kernel5, resized_threshold)
    cv2.imshow('threshold', resized_threshold)

    # Create canny image
    canny_gray_copy = gray2.copy()
    imgCanny = cv2.Canny(canny_gray_copy, cannyMin, cannyMax)
    cv2.dilate(imgCanny, kernel3,imgCanny)

    movement = frame2Copy.copy()
    # Find and draw contours around movement
    thresh_contours = resized_threshold.copy()
    _, cnts, hierarchy = cv2.findContours(thresh_contours, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    max_size = 0;
    max_size_contour = None;
    for cnt in cnts:
        contour_area = cv2.contourArea(cnt)
        if contour_area > max_size:
            max_size_contour = cnt
            max_size = contour_area
        if contour_area > 4000:
            cv2.drawContours(movement, cnt, -1, (0, 0, 255), 3)
        if contour_area > 200 and contour_area <= 600:
            cv2.drawContours(movement   , cnts, -1, (255, 255, 255), 2)

    x, y, w, h = cv2.boundingRect(max_size_contour)
    cv2.rectangle(movement, (x, y), (x + w, y + h), (0, 255, 0), 2)
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
    if can_record is True:
        if start_recording is False or count_frames % 16 is not 0:
            num_non_zeros = cv2.countNonZero(resized_threshold)
        if num_non_zeros > minPixels and num_non_zeros < 100000:
            count_frames = 1
            start_recording = True
        if start_recording is True and count_frames <= 32:
            count_frames += 1
            cv2.putText(movement, 'Movement Found!', (5, 25), font, 1, (0, 255, 0), 2)
            cv2.putText(movement, 'Size of blobs: ' + str(num_non_zeros), (5, 55), font, 1, (0, 255, 0), 2)
            cv2.putText(movement, 'Press R to stop', (5, 85), font, 1, (150, 255, 50), 2)
            out.write(movement)
        else:
            cv2.putText(movement, 'Recording is on', (5, 25), font, 1, (150, 255, 50), 2)
            cv2.putText(movement, 'Press R to stop', (5, 55), font, 1, (150, 255, 50), 2)
            count_frames = 0
    else:
        if can_record is not True:
            print("Recording turned off")
            cv2.putText(movement, 'Recording is off', (5, 25), font, 1, (0, 0, 255), 2)
            cv2.putText(movement, 'Press R to record', (5, 50), font, 1, (0, 0, 255), 2)
        count_frames = 0
        start_recording = False

    # Show frames
    cv2.imshow("movement", movement)
    # cv2.imshow('gray', gray2)
    # cv2.imshow('canny', imgCanny)
    cv2.imshow('threshold', resized_threshold)

    #Push frames into older timeslots
    frame1 = frame2Copy.copy()
    older_gray = old_gray.copy()
    old_gray = gray1.copy()
    gray1 = gray2.copy()
    older_difference = difference_copy.copy()
    older_resized_threshold = resized_threshold_copy.copy()

    # Keyboard commands
    #   R = Allow/Disallow recording
    #   Q = Quit
    key = cv2.waitKey(1)
    if key == ord('r'):
        if can_record is False:
            can_record = True
        else:
            can_record = False
    if key == ord('q'):
        break

# Release everything if job is finished
out.release()
cap.release()
cv2.destroyAllWindows()