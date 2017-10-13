import MyCamera as webcam
import cv2
import numpy as np
import py_graph_cpp

font = cv2.FONT_HERSHEY_SIMPLEX
fourcc = cv2.VideoWriter_fourcc(*'XVID')

# select the webcam the reader uses if the computer has multiple connected
capture = webcam.MyCamera(1, "output 1")

# initialize video recording
out = cv2.VideoWriter("output_video.avi", fourcc, 20.0, (640, 480))

while True:
    py_graph_cpp.resetGraph()

    # update frames
    capture.tick()
    frame1_copy = capture.getFrame("color").copy()
    img_grey = capture.getFrame("grey_blurred").copy()
    img_canny = capture.getFrame("canny").copy()

    # process canny image and find contours
    cv2.dilate(img_canny, np.ones((3, 3)), img_canny, iterations=2)
    cv2.erode(img_canny, np.ones((2, 2)), img_canny)
    _, contours, hierarchy = cv2.findContours(img_canny.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # skip iteration if no contours are found
    if len(contours) == 0:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # find the centers of all potential points in list of contours
    # assume largest contour is the paper
    centers = []
    biggest_contour_area = 0
    biggest_contour = contours[0]
    biggest_index = 0
    for i in range(len(contours)):
        contour = contours[i]
        bx, by, bw, bh = cv2.boundingRect(contour)
        contour_area = cv2.contourArea(contour)
        if 150000 > contour_area > biggest_contour_area:
            biggest_contour = contour
            biggest_contour_area = cv2.contourArea(contour)
            biggest = (bx, by, bw, bh)
            biggest_index = i
        centers.append((int((bx + bx + bw) / 2), int((by + by + bh) / 2)))

    # find and display corner points of paper
    epsilon = 0.1 * cv2.arcLength(biggest_contour, True)
    approx = cv2.approxPolyDP(biggest_contour, epsilon, True)
    cv2.drawContours(frame1_copy, approx, -1, (0, 255, 255), thickness=15)

    # display coordinates in the form (x,y)
    if len(approx) == 4:
        b1 = approx[0][0]
        b2 = approx[1][0]
        b3 = approx[2][0]
        b4 = approx[3][0]
        b1_str = "(" + str(b1[0]) + "," + str(b1[1]) + ")"
        b2_str = "(" + str(b2[0]) + "," + str(b2[1]) + ")"
        b3_str = "(" + str(b3[0]) + "," + str(b3[1]) + ")"
        b4_str = "(" + str(b4[0]) + "," + str(b4[1]) + ")"
        cv2.putText(frame1_copy, b1_str, (b1[0] - 5, b1[1] + 5),
                    font, .6, (0, 0, 255), 2)
        cv2.putText(frame1_copy, b2_str, (b2[0] - 5, b2[1] + 5),
                    font, .6, (0, 0, 255), 2)
        cv2.putText(frame1_copy, b3_str, (b3[0] - 5, b3[1] + 5),
                    font, .6, (0, 0, 255), 2)
        cv2.putText(frame1_copy, b3_str, (b4[0] - 5, b4[1] + 5),
                    font, .6, (0, 0, 255), 2)

    # iterate through all potential points and find which ones are within the paper contour
    graph_points = []
    vertex_id = 0
    for i in range(len(contours)):
        if len(approx) != 4:
            break
        x = int(centers[i][0])
        y = int(centers[i][1])
        in_square = cv2.pointPolygonTest(approx, (x, y), True)
        # draw vertex if it is inside the paper contour
        # add vertex to graph_point list for TSP calculation
        if in_square > 20 and 5 < cv2.contourArea(contours[i]) < 300:
            print("Vertex " + str(vertex_id) + str((x, y)) +
                  " distance from edge of paper: " + str(in_square))
            # cv2.putText(frame1_copy, str(vertex_id), (x + 5, y + 5), font, .6, (0, 0, 255), 2)
            graph_points.append((x, y))
            cv2.circle(frame1_copy, (x, y), 7, (0, 0, 255), -1)
            py_graph_cpp.addVertex(vertex_id, x, y)
            vertex_id += 1

    # skip TSP calculation if there are too many points in order to prevent lag
    if len(graph_points) > 1000:
        continue

    # compute the TSP and draw lines
    tsp_path = py_graph_cpp.VectorInt(py_graph_cpp.getTwoOptRoute())
    next_x = 0
    next_y = 0
    for i in range(len(tsp_path) - 1):
        current_id = tsp_path[i]
        next_id = tsp_path[i+1]
        current_x = graph_points[current_id][0]
        current_y = graph_points[current_id][1]
        next_x = graph_points[next_id][0]
        next_y = graph_points[next_id][1]
        cv2.line(frame1_copy,
                 (current_x, current_y),
                 (next_x, next_y),
                 (255, 0, 0), thickness=3)
    # draw line connecting the end back to the beginning
    if len(tsp_path) > 1:
        next_id = tsp_path[0]
        cv2.line(frame1_copy, (next_x, next_y),
                 (graph_points[next_id][0], graph_points[next_id][1]),
                 (255, 0, 0), thickness=3)

    # write and display frame
    out.write(frame1_copy)
    cv2.imshow("window", frame1_copy)
    cv2.imshow("canny", img_canny)

    # end program if q key is press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.imwrite("last_frame.jpeg", frame1_copy)
        break

# Release everything if job is finished
out.release()
cv2.destroyAllWindows()