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

from datetime import datetime
import cv2
from MyCamera import MyCamera, showFrames

# Read in number to use for new file name
# Initialize recording
# returns a file writing object
def getRecordCount():
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    countfile = os.path.join(THIS_FOLDER, 'output_count.txt')

    # Check if file exists and read in current  it if it does
    if os.path.exists(countfile):
        myfile = open(countfile, 'r+')
        filecount = myfile.read()
        int_filecount = int(filecount)
    else:
        int_filecount = 0
    myfile.close()

    # define codec and filename
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    filename = 'movement_%d_@_' % (int_filecount)
    mytime = time.strftime("%d_%b_%Y_%x")
    filename = filename + mytime + '.avi'

    # increment avi filecount and store it back to output_count.txt
    out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
    with open(countfile, 'w') as myfile:
        myfile.write(str(int_filecount + 1))
    return out

class MotionSensor(MyCamera):

    def __init__(self, camera_number):
        MyCamera.__init__(self, camera_number, display_trackbars=True)
        # define movement_frame sensitivity
        self.min_pixels = 2000
        self.max_pixels = 20000
        self.blob_area = 0
        self.text_display_offset = 15
        # Saves movement_frame to file if can_record is True
        self.can_record = False
        self.start_recording = False

        # get current positions of trackbars
        def nothing(x):
            x = x
            return x

        cv2.createTrackbar('min_pixels', self.trackbar_window_name, self.min_pixels, 5000, nothing)
        cv2.createTrackbar('max_pixels', self.trackbar_window_name, self.max_pixels, 30000, nothing)

    def getDifferenceValue(self):
        return self.blob_area

    def movementFound(self):
        if self.max_pixels > self.blob_area > self.min_pixels:
            return True

    def findMovementFrame(self):
        """ Returns image with movement_frame in frame outlined """

        movement_frame = self.getColorFrame()
        threshold_frame = self.getThresholdFrame(dilation_iterations=3)
        _, cnts, hierarchy = cv2.findContours(threshold_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        num_non_zeros = cv2.countNonZero(threshold_frame)
        self.blob_area = num_non_zeros
        blob_size = "blob size = " + str(self.blob_area)

        str_date = str(datetime.now())
        self.display_text(movement_frame, str_date, (255, 255, 0))
        self.display_text(movement_frame, blob_size, (0, 0, 255))
    
        if self.can_record is True:
            self.display_text(movement_frame, 'Recording is on', (255, 255, 0))
            self.display_text(movement_frame, 'Press R to stop', (150, 255, 50))
        else:
            self.display_text(movement_frame, 'Recording is off', (150, 255, 50))
            self.display_text(movement_frame, 'Press R to record', (150, 255, 50))

        if self.max_pixels > num_non_zeros > self.min_pixels:
            self.start_recording = True
            self.display_text(movement_frame, "movement_frame found!", (0, 255, 0))

        # for every contour
        for cnt in cnts:
            contour_area = cv2.contourArea(cnt)
            if self.movementFound():
                cv2.drawContours(movement_frame, cnt, -1, (0, 0, 255), 3)

        return movement_frame


    # get current positions of trackbars
    def process_trackbars(self):
        MyCamera.process_trackbars(self)
        self.min_pixels = cv2.getTrackbarPos('min_pixels', self.trackbar_window_name)
        self.max_pixels = cv2.getTrackbarPos('max_pixels', self.trackbar_window_name)


    def processKey(self, key):
        if key == ord('r'):
            if self.can_record is False:
                self.can_record = True
                print("Recording turned on")
            else:
                self.can_record = False
                print("Recording turned off")


def main():
    motion = MotionSensor(0)
    key = ''
    while True:
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        else:
            motion.processKey(key)

        motion.tick()
        color_frame = motion.getColorFrame()
        threshold_frame = motion.getThresholdFrame(dilation_iterations=3)
        movement_frame = motion.findMovementFrame()

        frame_names = ["threshold_frame", "movement_frame"]
        frames = [threshold_frame, movement_frame]
        showFrames(frame_names, frames)

if __name__ == "__main__":
    main()
