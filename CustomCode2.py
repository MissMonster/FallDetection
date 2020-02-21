import cv2
import numpy as np
import time

MODE = "COCO"

if MODE is "COCO":
    protoFile = "models/pose/coco/pose_deploy_linevec.prototxt"
    weightsFile = "models/pose/coco/pose_iter_440000.caffemodel"
    nPoints = 18
    POSE_PAIRS = [ [1,0],[1,2],[1,5],[2,3],[3,4],[5,6],[6,7],[1,8],[8,9],[9,10],[1,11],[11,12],[12,13],[0,14],[0,15],[14,16],[15,17]]

elif MODE is "MPI" :
    protoFile = "models/pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt"
    weightsFile = "models/pose/mpi/pose_iter_160000.caffemodel"
    nPoints = 15
    POSE_PAIRS = [[0,1], [1,2], [2,3], [3,4], [1,5], [5,6], [6,7], [1,14], [14,8], [8,9], [9,10], [14,11], [11,12], [12,13] ]


inWidth = 368
inHeight = 368
#threshold 0, so it doesn't append 'None'
threshold = 0.05


input_source = "models/sample_video1.mp4"
cap = cv2.VideoCapture(input_source)
hasFrame, frame = cap.read()

vid_writer = cv2.VideoWriter('models/output1.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 20, (frame.shape[1],frame.shape[0]))

net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

def DrawPoints(count = 0):
    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                              (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inpBlob)
    output = net.forward()

    H = output.shape[2]
    W = output.shape[3]
    # Empty list to store the detected keypoints
    points = []

    #for i in range(nPoints):
        # confidence map of corresponding body's part.
    probMap = output[0, 0, :, :]

        # Find global maxima of the probMap.
    minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
        
        # Scale the point to fit on the original image
    x = (frameWidth * point[0]) / W
    y = (frameHeight * point[1]) / H

    if prob > threshold : 
        #cv2.circle(frameCopy, (int(x), int(y)), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
        #cv2.putText(frameCopy, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, lineType=cv2.LINE_AA)

        # Add the point to the list if the probability is greater than the threshold
        points.append((int(x), int(y)))
    else :
        points.append(None)

    print(points)

    #if points.append(None) -> TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'
    if None not in points:
        headHeight = np.array(points[0][1])
    #draws circle and shows y value
        cv2.circle(frame, points[0],8 , (0,255,0), thickness=-1, lineType = cv2.FILLED)
        cv2.putText(frame, "{}".format(int(y)), points[0], cv2.FONT_HERSHEY_COMPLEX, .8, (255, 50, 0), 2, lineType=cv2.LINE_AA)
        #get int value for y
        return int(headHeight)
    else:
        return headHeight_prev

    # Draw Skeleton
"""    for pair in POSE_PAIRS:
        partA = pair[0]
        partB = pair[1]

        if points[partA] and points[partB]:
            cv2.line(frame, points[partA], points[partB], (0, 255, 255), 3, lineType=cv2.LINE_AA)
            cv2.circle(frame, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.circle(frame, points[partB], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
"""
def DetectFall(time_prev, headHeight, headHeight_prev, t):
    #point y at curr frame - point y at previous
    delta_distance = headHeight - headHeight_prev
    #time for 1 frame to be processed
    delta_time = time.time() - t
    time_prev = t
    print(delta_time)

    #needs change of algorithm
    if delta_distance/delta_time > 0.1 and time_prev > 0:
        return True
    else:
        return False

count = 0
time_prev = 0
headHeight = 0

while cv2.waitKey(1) < 0:
    t = time.time()
    hasFrame, frame = cap.read()
    frameCopy = np.copy(frame)
    if not hasFrame:
        cv2.waitKey()
        cv2.destroyAllWindows()
        break

    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]

    headHeight_prev = headHeight
    headHeight = DrawPoints()
    #error check
    print(headHeight, headHeight_prev)

    if DetectFall(time_prev, headHeight, headHeight_prev, t):
        count += 1
    
    #in case of faulty detections
    if count > 5:
        cv2.putText(frame, "Fall Detected", (50,50), 
                    cv2.FONT_HERSHEY_COMPLEX, .8, (0,0,255), 2, lineType=cv2.LINE_AA)

    #cv2.putText(frame, "time taken = {:.2f} sec".format(time.time() - t), (50, 50), cv2.FONT_HERSHEY_COMPLEX, .8, (255, 50, 0), 2, lineType=cv2.LINE_AA)
    # cv2.putText(frame, "OpenPose using OpenCV", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 50, 0), 2, lineType=cv2.LINE_AA)
    # cv2.imshow('Output-Keypoints', frameCopy)
    cv2.imshow('Output-Skeleton', frame)

    vid_writer.write(frame)

vid_writer.release()    