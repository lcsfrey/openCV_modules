import cv2
import numpy as np
import time

def showFrames(frame_names, frames):
    for i in range(len(frames)):
        cv2.imshow(frame_names[i], frames[i])

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
        
        # Needed to initialize trackbars
        def nothing(x):
            x = x
            return x 

        # create trackbars for thresholds
        cv2.createTrackbar('cannyMin', 'image', self.cannyMin, 255, nothing)
        cv2.createTrackbar('cannyMax', 'image', self.cannyMax, 255, nothing)
        cv2.createTrackbar('threshMin', 'image', self.threshMin, 255, nothing)
        cv2.createTrackbar('threshMax', 'image', self.threshMax, 255, nothing)
        cv2.createTrackbar('MIN_PIXELS', 'image', 1000, 5000, nothing)
        cv2.createTrackbar('MAX_PIXELS', 'image', 1000, 5000, nothing)

    # Process frame and output the result
    # input:  string indicating what image to get
    #         image to invert if choice is "inverted"
    #
    # output: outputs Mat of your choice
    def getColorFrame(self):
        return self.frame1.copy()
    
    def getGreyFrame(self, image=None, min_thresh=30, max_thresh=255):
        grey_blurred = None
        if image is None:
            self.grey = cv2.cvtColor(self.frame1.copy(), cv2.COLOR_BGR2GRAY)
            grey_blurred = cv2.blur(self.grey, (3,3))
        else:
            grey_blurred = cv2.blur(image.copy(), (3,3))
        return grey_blurred

    def getCannyFrame(self, image=None, dilation_kernel=(3,3), dilation_iterations=1, 
                    canny_min=None, canny_max = None):
        canny = cv2.Canny(self.grey.copy(), self.cannyMin, self.cannyMax)
        for i in range (dilation_iterations):
            canny = cv2.dilate(canny, dilation_kernel)
        return canny

    def getThresholdFrame(self, image_1=None, image_2=None, min_thresh=None, max_thresh=None):
        t_gray1 = cv2.cvtColor(self.frame1.copy(), cv2.COLOR_BGR2GRAY)
        t_gray2 = cv2.cvtColor(self.frame2.copy(), cv2.COLOR_BGR2GRAY)
        difference = cv2.absdiff(t_gray1, t_gray2)
        ret, threshold = cv2.threshold(difference, self.threshMin, self.threshMax, cv2.THRESH_BINARY)
        threshold = cv2.dilate(threshold, (3, 3))
        return threshold

    def getGreyThresholdFrame(self, image=None, min_thresh=None, max_thresh=None):
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
        self.MIN_PIXELS = cv2.getTrackbarPos('MIN_PIXELS', 'image')
        self.MAX_PIXELS = cv2.getTrackbarPos('MAX_PIXELS', 'image')

    # update frames
    def tick(self):
        self.frame4 = self.frame3
        self.frame3 = self.frame2
        self.frame2 = self.frame1
        ret, self.frame1 = self.cap.read()
        self.frame_count += 1
        self.process_trackbars()

    def processKey(self, key):
        if key == ord('q'):
            return 'q'


class MyVideoWriter:
    def __init__(self, camera_number, output_file):
        self.out = None
        self.can_record = False
        

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

    def camera_intialize(self):
        if self.can_record is True:
            self.out = MyVideoWriter.start_recording()
