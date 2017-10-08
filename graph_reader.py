import MyCamera as webcam
import cv2
import numpy as np


def detector():
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 0
    params.maxThreshold = 256
    # Filter by Area.
    params.filterByArea = True
    params.minArea = 70
    params.maxArea = 1000
    # Filter by Circularity
    #params.filterByCircularity = True
    params.minCircularity = .8
    # Filter by Convexity
    #params.filterByConvexity = True
    params.minConvexity = 0.9
    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0
    # Filter by Color
    params.filterByColor = True
    params.blobColor = 255

    detector = cv2.SimpleBlobDetector_create(params)

    return detector


root = tk.Tk()

class Application(tk.Frame, threading.Thread):
    def __init__(self, master=None):
        super().__init__(master)

        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.show_threshold = tk.Button(self)
        self.show_threshold["text"] = "Threshold Image"
        self.show_threshold["command"] = self.say_hi
        self.show_threshold.pack(side="top")

        self.show_color = tk.Button(self)
        self.show_color["text"] = "Color Image"
        self.show_color["command"] = self.say_hi
        self.show_color.pack(side="top")

        self.show_canny = tk.Button(self)
        self.show_canny["text"] = "Canny Image"
        self.show_canny["command"] = self.say_hi
        self.show_canny.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.quit.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")


#app = Application(master=root)
# app.start()

capture = webcam.MyCamera(1, "output 1")
#bc = webcam.MyCamera(0, "output 0")
#ret = capture.__setattr__('CV_CAP_PROP_FRAME_WIDTH', 320)
#ret = capture.__setattr__('CV_CAP_PROP_FRAME_WIDTH', 280)
#ret = bc.__setattr__('CV_CAP_PROP_FRAME_WIDTH', 320)
#ret = bc.__setattr__('CV_CAP_PROP_FRAME_WIDTH', 280)

box_corners = np.array([(380, 50), (680, 50), (680, 400), (380, 400)])
#box = cv2.boundingRect(box_corners)

frame1_copy = capture.frame1
display_images = False
detector = detector()



while True:

    frame1_copy = t_frame1_copy.copy()
    grey_blurred = t_grey_blurred.copy()
    img_canny = t_img_canny.copy()
    gray_threshold = t_gray_threshold.copy()
    keypoints = detector.detect(gray_threshold)
    test_mask = np.ones(gray_threshold.shape, np.uint8)
    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    #im_with_keypoints = cv2.drawKeypoints(test_mask, keypoints, np.array([]), (255, 255, 255),
    #                                      cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.erode(img_canny, (3, 3), img_canny)
    cv2.dilate(img_canny, (5, 5), img_canny)



    _, contours, hierarchy = cv2.findContours(img_canny.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(len(contours))
    # Create a black image

    # Write some Text
    font = cv2.FONT_HERSHEY_SIMPLEX
    centers = np.zeros((len(contours),2))
    biggest = (0, 0, 0, 0)
    for i in range(len(contours)):
        cnt = contours[i]
        bx,by,bw,bh = cv2.boundingRect(cnt)

        if bh + bx > biggest[1] + biggest[3]:
            biggest = (bx, by, bw, bh)

        centers[i][0] = int((bx + bx + bw) / 2)
        centers[i][1] = int((by + by + bh) / 2)

    for i in range(len(contours)):
        output = str(i)
        x = int(centers[i][0])
        y = int(centers[i][1])
        bx = biggest[0]
        by = biggest[1]
        bw = biggest[2]
        bh = biggest[3]
        print(biggest)
        if x < bx or x > (bw + bx) or y < by or y >= (by + bh):
            continue
        if biggest != (bx , by, bw, bh):
            cv2.putText(frame1_copy, output, (x, y), font, .6, (0, 255, 00), 1)
            cv2.circle(frame1_copy, (x, y), 7, (0, 0, 255), -1)
        else:
            cv2.circle(frame1_copy, (x, y), 7, (0, 255, 0), -1)

    #cv2.floodFill(im_with_keypoints, None, (0,0), (255,255,255))
    #cv2.dilate(im_with_keypoints, (3,3), im_with_keypoints)
    #cv2.imshow("vertices", im_with_keypoints)


    #bc.tick()
    #wc_frame1 = bc.getFrame("color")
    #bc_frame1 = bc.getFrame("color")
   # bc_gray = bc.getFrame("grey_blurred")
    #bc_canny = bc.getFrame("canny")

    stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
    #cv2.resize(grey_blurred, (3, 3), grey_blurred, 320, 280)
    #cv2.resize(bc_gray, (3, 3), bc_gray, 320, 280)


    #cv2.imshow("bad camera color", bc_frame1)

    #cv2.imshow("web camera color", wc_frame1)


    imgInverted = capture.getFrame("inverted", img_canny.copy())
    imgThresh = capture.getFrame("threshold")
    #imgThreshInverted = capture.getFrame("inverted", imgThresh.copy())
    #cv2.erode(imgInverted, (9, 9), imgInverted)

    #cv2.rectangle(frame1_copy, (50, 50), (400, 300), (255, 255, 255), 3)
    #contours, heirarchy] = cv2.findContours(imgInverted.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    #cv2.drawContours(imgThresh, contours[0], -1, (255,255,255))

    cv2.imshow("window", frame1_copy)
    #cv2.imshow("inverted", imgInverted)
    #cv2.imshow("threshold", imgThresh)
    #cv2.imshow("canny", img_canny)



    cv2.imshow("threshold", gray_threshold)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.imwrite("img.jpeg", frame1_copy)
        break
    if cv2.waitKey(1) & 0xFF == ord('g'):
        display_images = True
    if cv2.waitKey(1) & 0xFF == ord('x'):
        cv2.destroyWindow("gray")
        cv2.destroyWindow("canny")
        display_images = False
        #plt.show()

    if display_images is True:
        cv2.imshow("gray", grey_blurred)
        cv2.imshow("canny", img_canny)

# Release everything if job is finished
out.release()
cv2.destroyAllWindows()
