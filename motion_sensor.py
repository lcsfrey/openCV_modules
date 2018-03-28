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
from MyCamera import MyCamera
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
        # Global variables

        # define movement sensitivity
        self.MIN_PIXELS = 2500
        self.MAX_PIXELS = 8000

        # frame conversion properties
        self.FONT = cv2.FONT_HERSHEY_SIMPLEX

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
        return 0


    def find_movement(self):
        thresh_contours = self.getThresholdFrame().copy()
        _, cnts, hierarchy = cv2.findContours(thresh_contours, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        max_size = 0
        max_size_contour = None
        movement = self.getColorFrame()

        # for every contour
        for cnt in cnts:
            contour_area = cv2.contourArea(cnt)
            if contour_area > max_size:
                x, y, w, h = cv2.boundingRect(cnt)
                # cv2.rectangle(movement, (x, y), (x + w, y + h), (0, 255, 0), 2)
                max_size_contour = cnt
                max_size = contour_area
            if contour_area > self.MIN_PIXELS:
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
        if self.CAN_RECORD is True:
            num_non_zeros = 0
            if self.start_recording is False or self.frame_count % 16 is not 0:
                num_non_zeros = cv2.countNonZero(self.getGreyThresholdFrame())
            if self.MAX_PIXELS > num_non_zeros > self.MIN_PIXELS:
                self.frame_count = 1
                self.start_recording = True
            if self.start_recording is True and 8 >= self.frame_count > 0:
                self.frame_count += 1
                # cv2.putText(movement, 'Size of blobs: ' + str(num_non_zeros), (5, 40), FONT, .75, (0, 255, 0), 2)
                str_date = str(datetime.now())
                cv2.putText(movement, str_date, (5, 20), self.FONT, .75, (0, 0, 255), 3)
                cv2.putText(movement, str_date, (5, 20), self.FONT, .75, (255, 0, 0), 1)
                self.out.write(movement)
                cv2.putText(movement, 'Press R to stop', (5, 40), self.FONT, .75, (150, 255, 50), 2)
                # thresh_to_write = cv2.cvtColor(resized_threshold.copy(),  cv2.COLOR_GRAY2BGR)
                # out_thresh.write(resized_threshold)
            else:
                cv2.putText(movement, 'Recording is on', (5, 20), self.FONT, .75, (150, 255, 50), 2)
                self.frame_count = 0
                self.start_recording = False
        else:
            if self.CAN_RECORD is False:
                print("Recording turned off")
                cv2.putText(movement, 'Recording is off', (5, 20), self.FONT, .75, (0, 0, 255), 2)
                cv2.putText(movement, 'Press R to record', (5, 40), self.FONT, .75, (0, 0, 255), 2)

            self.frame_count = 0
            self.start_recording = False
        
        return movement

    def processKey(self, key):  
        MyCamera.processKey(self, key)
        if key == ord('r'):
            if self.CAN_RECORD is False:
                self.CAN_RECORD = True
            else:
                self.CAN_RECORD = False


#frame_names = ["movement", "canny", "threshold"]
#frames = [movement, img_canny, resized_threshold]
#showFrames(frame_names, frames)