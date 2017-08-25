import cv2
import numpy as np
import time


# Needed to initialize trackbars
def nothing(x):
    x = x
    return x


# Webcam object used to interact with frames
class MyCamera:

    # Initializes camera and Mats
    def __init__(self, camera_number, output_file):
        self.outfilename = output_file
        self.cap = cv2.VideoCapture(camera_number)
        ret, self.frame1 = self.cap.read()
        ret, self.frame2 = self.cap.read()
        ret, self.frame3 = self.cap.read()
        ret, self.frame4 = self.cap.read()
        self.frame_count = 0
        self.grey = self.frame1.copy()
        self.cannyMin = 100
        self.cannyMax = 128
        self.threshMin = 127
        self.threshMax = 255
        self.minPixels = 1000

        # Create a black image, a window
        # img = np.zeros((300, 512, 3), np.uint8)
        cv2.namedWindow('image')
        # create trackbars for thresholds
        cv2.createTrackbar('cannyMin', 'image', self.cannyMin, 255, nothing)
        cv2.createTrackbar('cannyMax', 'image', self.cannyMax, 255, nothing)
        cv2.createTrackbar('threshMin', 'image', self.threshMin, 255, nothing)
        cv2.createTrackbar('threshMax', 'image', self.threshMax, 255, nothing)
        cv2.createTrackbar('minPixels', 'image', 1000, 5000, nothing)

    # Process frame and output the result
    # input:  string indicating what image to get
    #         image to invert if choice is "inverted"
    #
    # output: outputs Mat of your choice
    def getFrame(self, choice, image=None, min_thresh=30, max_thresh=255):
        if choice is "color":
            value = self.frame1
            return value
        if choice is "grey_blurred":
            self.grey = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2GRAY)
            grey_blurred = cv2.blur(self.grey, (3,3))
            return grey_blurred
        if choice is "canny":
            canny = cv2.Canny(self.grey.copy(), self.cannyMin, self.cannyMax)
            canny = cv2.dilate(canny, (3, 3))
            return canny
        if choice is "inverted":
            cv2.bitwise_not(image, image)
            return image
        if choice is "threshold":
            t_gray1 = cv2.cvtColor(self.frame1.copy(), cv2.COLOR_BGR2GRAY)
            t_gray2 = cv2.cvtColor(self.frame2.copy(), cv2.COLOR_BGR2GRAY)
            difference = cv2.absdiff(t_gray1, t_gray2)
            ret, threshold = cv2.threshold(difference, self.threshMin, self.threshMax, cv2.THRESH_BINARY)
            threshold = cv2.dilate(threshold, (3, 3))
            return threshold
        if choice is "gray_threshold":
            t_gray2 = cv2.cvtColor(self.frame2.copy(), cv2.COLOR_BGR2GRAY)
            #difference = cv2.absdiff(t_gray1, t_gray2)
            ret, threshold = cv2.threshold(t_gray2, self.threshMin, self.threshMax, cv2.THRESH_BINARY)
            cv2.bitwise_not(threshold, threshold)
            return threshold

    # get current positions of trackbars
    def process_trackbars(self):
        self.cannyMin = cv2.getTrackbarPos('cannyMin', 'image')
        self.cannyMax = cv2.getTrackbarPos('cannyMax', 'image')
        self.threshMin = cv2.getTrackbarPos('threshMin', 'image')
        self.threshMax = cv2.getTrackbarPos('threshMax', 'image')

    # update frames
    def tick(self):
        self.frame4 = self.frame3
        self.frame3 = self.frame2
        self.frame2 = self.frame1
        ret, self.frame1 = self.cap.read()
        self.frame_count += 1
        self.process_trackbars()


class MyVideoWriter:
    def __init__(self, camera_number, output_file):
        self.out = None
        self.can_record = False

    def camera_intialize(self):
        if self.can_record is True:
            self.out = start_recording()

    # Read in number to use for new file name
    # Initialize recording
    # returns a file writing object
    def start_recording(self):
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







