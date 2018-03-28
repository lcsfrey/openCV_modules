import cv2
import MyCamera
from motion_sensor import MotionSensor

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
    MyCamera.showFrames(frame_names, frames)