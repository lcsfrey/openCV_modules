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
import cv2
import numpy as np
import time
import os
from datetime import datetime
from MyCamera import *
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


# Read in number to use for new file name
# Initialize recording
# returns a file writing object
def getRecordCount():
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

class MotionSensor(MyCamera):

    def __init__(self, camera_number, output_file):
        MyCamera.__init__(self, camera_number, output_file)
  
        self.text_display_offset = 15
        # Needed to initialize trackbars
        def nothing(x):
            x = x
            return x 

        cv2.createTrackbar('MIN_PIXELS', 'image', 1100, 5000, nothing)
        cv2.createTrackbar('MAX_PIXELS', 'image', 10000, 5000, nothing)

        # Global variables
        # define movement sensitivity
        self.MIN_PIXELS = 200
        self.MAX_PIXELS = 8000
        self.blob_area = 0

        # Saves movement to file if CAN_RECORD is True
        self.CAN_RECORD = False
        self.start_recording = False
        
        self.out_num = getRecordCount()
        #out_thresh = start_recording()

            # Initialize blob detector
            # returns a blob detector
        def detector():
            params = cv2.SimpleBlobDetector_Params()
            # Change thresholds
            params.minThreshold = self.threshMin
            params.maxThreshold = self.threshMax
            # Filter by Area.
            params.filterByArea = True
            params.minArea = self.minPixels

            detector = cv2.SimpleBlobDetector_create(params)
            return detector

        self.detector = detector()

    def getTotalChangeValue(self):
        return self.blob_area


    def find_movement(self):
        thresh_contours = self.getThresholdFrame().copy()
        _, cnts, hierarchy = cv2.findContours(thresh_contours, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        max_size_contour = None

        # determines the how much the next line of text is offset when
        # a line of text is printed
        offset = 20

        movement = self.getColorFrame()

        # for every contour
        for cnt in cnts:
            contour_area = cv2.contourArea(cnt)
            if self.MAX_PIXELS > contour_area > self.MIN_PIXELS:
                cv2.drawContours(movement, cnt, -1, (0, 0, 255), 3)
                

        num_non_zeros = cv2.countNonZero(self.getThresholdFrame())
        self.blob_area = num_non_zeros
        blob_size = "blob size = " + str(self.blob_area)
        self.display_text(movement, blob_size, (0, 0, 255))
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
        if self.CAN_RECORD is True:
            if self.MAX_PIXELS > num_non_zeros > self.MIN_PIXELS:
                self.frame_count = 0
                self.start_recording = True
                self.display_text(movement, "movement found!", (0, 255, 0))
            if self.start_recording is True and 15 >= self.frame_count > 0:
                # cv2.putText(movement, 'Size of blobs: ' + str(num_non_zeros), (5, 40), FONT, .75, (0, 255, 0), 2)
                str_date = str(datetime.now())
                print(str_date)
                color = (255, 255, 0)
                self.display_text(movement, str_date, color)
                self.out.write(movement)

                self.display_text(movement, 'Press R to stop', (150, 255, 50))
                # thresh_to_write = cv2.cvtColor(resized_threshold.copy(),  cv2.COLOR_GRAY2BGR)
                # out_thresh.write(resized_threshold)
            else:
                self.display_text(movement, 'Recording is on', (255, 255, 0))
                self.frame_count = 0
                self.start_recording = False
        else:
            if self.CAN_RECORD is False:
                self.display_text(movement, 'Recording is off', (150, 255, 50))
                self.display_text(movement, 'Press R to record', (150, 255, 50))

            self.start_recording = False
        
        return movement

        # get current positions of trackbars
    
    def process_trackbars(self):
        MyCamera.process_trackbars(self)
        self.MIN_PIXELS = cv2.getTrackbarPos('MIN_PIXELS', 'image')
        self.MAX_PIXELS = cv2.getTrackbarPos('MAX_PIXELS', 'image')

    def processKey(self, key):  
        MyCamera.processKey(self, key)
        if key == ord('r'):
            if self.CAN_RECORD is False:
                self.CAN_RECORD = True
                print("Recording turned on")
            else:
                self.CAN_RECORD = False
                print("Recording turned off")


def main():
    motion = MotionSensor(0, "output")
    key = ''
    while True:
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        else:
            motion.processKey(key)

        motion.tick()
        color_frame = motion.getColorFrame()
        threshold = motion.getThresholdFrame()
        movement = motion.find_movement()

        frame_names = ["color", "threshold", "movement"]
        frames = [color_frame, threshold, movement]
        showFrames(frame_names, frames)

if __name__ == "__main__":
    main()
