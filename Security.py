import numpy as np
import cv2
import random
import time
import warnings

can_record = False
recording_already_started = False
font = cv2.FONT_HERSHEY_SIMPLEX

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


def write_frame(frame):
    if can_record is True:
        out.write(frame)

def detector():
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 10
    params.maxThreshold = 255
    # Filter by Area.
    params.filterByArea = True
    params.minArea = 150
    #params.maxArea = 3000

    detector = cv2.SimpleBlobDetector_create(params)

    return detector

def nothing(x):
    x = x
    return x

# Create a black image, a window
img = np.zeros((300,512,3), np.uint8)
cv2.namedWindow('image')
# create trackbars for color change
cv2.createTrackbar('cannyMin', 'image', 0, 255, nothing)
cv2.createTrackbar('cannyMax', 'image', 0, 255, nothing)
cv2.createTrackbar('threshMin', 'image', 10, 255, nothing)
cv2.createTrackbar('threshMax', 'image', 255, 255, nothing)
cv2.createTrackbar('minPixels', 'image', 1000, 3000, nothing)

cap = cv2.VideoCapture(1)
out = start_recording()
detector = detector()


ret, frame1 = cap.read()
if ret is True:
    imgContours1 = frame1.shape

ret, frame2 = cap.read()
if ret is True:
    imgContours2 = frame2.shape
ret, frame2 = cap.read()
ret, frame2 = cap.read()
kernel7 = np.ones((5, 5), np.uint8)
kernel5 = np.ones((5, 5), np.uint8)
kernel3 = np.ones((3, 3), np.uint8)

r = 315.0 / frame1.shape[1]
dim = (315, int(frame1.shape[0] * r))
gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
difference = cv2.absdiff(gray1, gray2)

old_gray = gray2.copy()
older_gray = gray2.copy()
old_imgContours = frame1.copy()
older_imgContours = frame1.copy()
oldest_imgContours = frame1.copy()
count_frames = 0
cannyMin = 80
cannyMax = 255
threshMin = 170
threshMax = 255
minPixels = 1000

while True:
    # Capture frame-by-frame
    ret, frame2 = cap.read()
    if ret is False:
        continue
    frame1Copy = frame1
    frame2Copy = frame2

    # get current positions of four trackbars
    cannyMin = cv2.getTrackbarPos('cannyMin','image')
    cannyMax = cv2.getTrackbarPos('cannyMax','image')
    threshMin = cv2.getTrackbarPos('threshMin','image')
    threshMax = cv2.getTrackbarPos('threshMax','image')
    minPixels = cv2.getTrackbarPos('minPixels', 'image')

    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    cv2.blur(gray1, (3, 3), gray1)
    cv2.blur(gray2, (3, 3), gray2)

    difference = cv2.absdiff(gray1, gray2)
    older_difference = cv2.absdiff(older_gray, old_gray)
    ret, resized_threshold = cv2.threshold(difference, threshMin, threshMax, cv2.THRESH_BINARY)
    ret, older_resized_threshold = cv2.threshold(older_difference, threshMin, threshMax, cv2.THRESH_BINARY)
    cv2.bitwise_or(resized_threshold, older_resized_threshold, resized_threshold)

    cv2.erode(resized_threshold, kernel3, resized_threshold)
    cv2.dilate(resized_threshold, kernel5, resized_threshold)
    cv2.imshow('threshold', resized_threshold)


    canny_gray_copy = gray2.copy()
    imgCanny = cv2.Canny(canny_gray_copy, cannyMin, 255)
    cv2.dilate(imgCanny, kernel3,imgCanny)

    thresh_contours = resized_threshold.copy()
    tempthresh = resized_threshold
    _, cnts, hierarchy = cv2.findContours(thresh_contours.copy(), cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    imgContours1 = frame2Copy.copy()
    for cnt in cnts:
        if cv2.contourArea(cnt) > 300:
            cv2.drawContours(gray2, cnts, -1, (0,0,255), 3)
        if cv2.contourArea(cnt) > 150 and cv2.contourArea(cnt) <= 300:
            cv2.drawContours(gray2, cnts, -1, (0, 255, 0), 3)

    #cv2.imshow("Contours", imgContours1)

    keypoints = detector.detect(resized_threshold.copy())
    im_with_keypoints = cv2.drawKeypoints(frame2Copy.copy(), keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imshow("Keypoints", im_with_keypoints)

    num_non_zeros = cv2.countNonZero(resized_threshold)
    if num_non_zeros > minPixels and can_record is True:
        start_recording = True
        count_frames = 0
        print("Number of ones: " + str(num_non_zeros))


    if start_recording is True and count_frames < 30:
        movement = gray2.copy()
        count_frames += 1
        cv2.putText(movement, 'Hello World!', (10, 500), font, 1, (255, 255, 255), 2)
        cv2.imshow('movement', movement)
        print("Recording turned on")
        if recording_already_started is False:

            recording_already_started = True
        else:
            out.write(movement)

    else:
        if can_record is not True:
            print("Recording turned off")
        if recording_already_started is True:

            recording_already_started = False
        count_frames = 0
        cv2.destroyWindow('movement')
        start_recording = False

    #cv2.imshow('canny', imgCanny)
    cv2.imshow('canny', gray2)
    frame1 = frame2Copy.copy()
    older_gray = old_gray.copy()
    old_gray = gray1.copy()
    gray1 = gray2.copy()

    key = cv2.waitKey(1)
    if key == ord('r'):
        if can_record is False:
            can_record = True

        else:
            can_record = False

    if key == ord('q'):
        break
    if key == ord('h'):
        plt.show()

# Release everything if job is finished
out.release()
cap.release()
cv2.destroyAllWindows()