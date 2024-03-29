#!/usr/bin/env python3

"""
Objects Detection with yolo on webcam
"""





# Detecting Objects on Image with OpenCV deep learning library


# Reading RGB image

# Loading Yolo v3 Network

##Inferencing the image

# Getting Bounding Boxes

# NMR -Non Max suppression

# Drawing Bounding Boxes with Labels


# Importing needed libraries
import numpy as np
import cv2
import time

import sys

import pyzed.sl as sl

import math

"""
Start of:
Reading stream video from camera
"""

# Defining 'VideoCapture' object
# and reading stream video from camera
#camera = cv2.VideoCapture(0)



# Create a Camera object
zed = sl.Camera()

# Create a InitParameters object and set configuration parameters
init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD1080 # Use HD720 opr HD1200 video mode, depending on camera type.

init_params.camera_fps = 30  # Set fps at 30
zed.set_camera_settings(sl.VIDEO_SETTINGS.BRIGHTNESS, 7 )


# Open the camera
err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
    print("Camera Open : "+repr(err)+". Exit program.")
    exit()
runtime = sl.RuntimeParameters()
image_size = zed.get_camera_information().camera_configuration.resolution
image_size.width = image_size.width /2
image_size.height = image_size.height /2
image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
depth_image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
point_cloud = sl.Mat()
#camera = image_zed.get_data()
runtime_parameters = sl.RuntimeParameters()

print(type(image_zed.get_data()))


camera = image_zed






# camera = cv2.VideoCapture('Carla_RGB_SEMANTIC.mp4')


# Preparing variables for spatial dimensions of the frames
h, w = None, None

# Loading COCO class labels from file
# Opening file
# Pay attention! If you're using Windows, yours path might looks like:
# r'yolo-coco-data\coco.names'
# or:
# 'yolo-coco-data\\coco.names'
with open('detector/obj.names') as f:
    # Getting labels reading every line
    # and putting them into the list
    labels = [line.strip() for line in f]

# loading config file and weights
network = cv2.dnn.readNetFromDarknet('detector/yolov4-tiny-custom.cfg',
                                     'detector/yolov4-tiny-custom_last.weights')

# Getting list with names of all layers from YOLO v3 network
layers_names_all = network.getLayerNames()

# Getting only output layers' names that we need from YOLO v3 algorithm
# with function that returns indexes of layers with unconnected outputs
layers_names_output = [layers_names_all[i - 1] for i in network.getUnconnectedOutLayers()]

# Setting minimum probability to eliminate weak predictions
probability_minimum = 0.5

# Setting threshold for filtering weak bounding boxes
# with non-maximum suppression
threshold = 0.3

# Generating colours for representing every detected object
# with function randint(low, high=None, size=None, dtype='l')
colours = np.random.randint(0, 255, size=(len(labels), 3), dtype='uint8')
# milimetre cinsinden değerleri girelim.


focalLength = 200
tabela_uzunlugu = 500
bilinen_uzaklik = 784


# def lidarCallback(x):
#     print("lidar",x.lidar)


# rospy.Subscriber("/lidar", Lidar, lidarCallback)


def focal_lenght_calculator(bilinen_uzaklik, box_height, tabela_uzunlugu):
    global focalLength
    focalLength = (bilinen_uzaklik * box_height) / tabela_uzunlugu


def distance_to_camera(tabela_uzunlugu, focalLength, pixel_uzunlugu):
    return (tabela_uzunlugu * focalLength) / pixel_uzunlugu


# Defining loop for catching frames
while True:
    # Capturing frame-by-frame from camera           
    #  
    #_, frame = camera.read()
    if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image_zed, sl.VIEW.LEFT)

        zed.retrieve_measure(depth_image_zed, sl.MEASURE.DEPTH)

        zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)

    err = zed.grab(runtime)
    if err == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
        zed.retrieve_image(depth_image_zed, sl.VIEW.DEPTH, sl.MEM.CPU, image_size)
        zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA, sl.MEM.CPU, image_size)

        image_ocv = image_zed.get_data()
        depth_image_ocv = depth_image_zed.get_data()
        frame = image_ocv[:, :, :-1]

        ##################################
        # Getting spatial dimensions of the frame
        # we do it only once from the very beginning
        # all other frames have the same dimension
        if w is None or h is None:
            # Slicing from tuple only first two elements
            h, w = frame.shape[:2]

        # Getting blob from current frame
        # The 'cv2.dnn.blobFromImage' function returns 4-dimensional blob from current
        # frame after mean subtraction, normalizing, and RB channels swapping
        # Resulted shape has number of frames, number of channels, width and height
        # E.G.:
        # blob = cv2.dnn.blobFromImage(image, scalefactor=1.0, size, mean, swapRB=True)
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                                     swapRB=True, crop=False)

        # Implementing forward pass with our blob and only through output layers
        # Calculating at the same time, needed time for forward pass
        network.setInput(blob)  # setting blob as input to the network
        start = time.time()
        output_from_network = network.forward(layers_names_output)
        end = time.time()

        # Showing spent time for single current frame
        # print('Current frame took {:.5f} seconds'.format(end - start))

        # Preparing lists for detected bounding boxes,
        # obtained confidences and class's number
        bounding_boxes = []
        confidences = []
        class_numbers = []

        # Going through all output layers after feed forward pass
        for result in output_from_network:
            # Going through all detections from current output layer
            for detected_objects in result:
                # Getting 80 classes' probabilities for current detected object
                scores = detected_objects[5:]
                # Getting index of the class with the maximum value of probability
                class_current = np.argmax(scores)
                # Getting value of probability for defined class
                confidence_current = scores[class_current]

                # # Check point
                # # Every 'detected_objects' numpy array has first 4 numbers with
                # # bounding box coordinates and rest 80 with probabilities
                # # for every class
                # print(detected_objects.shape)  # (85,)

                # Eliminating weak predictions with minimum probability
                if confidence_current > probability_minimum:
                    # Scaling bounding box coordinates to the initial frame size
                    # YOLO data format keeps coordinates for center of bounding box
                    # and its current width and height
                    # That is why we can just multiply them elementwise
                    # to the width and height
                    # of the original frame and in this way get coordinates for center
                    # of bounding box, its width and height for original frame
                    box_current = detected_objects[0:4] * np.array([w, h, w, h])

                    # Now, from YOLO data format, we can get top left corner coordinates
                    # that are x_min and y_min
                    x_center, y_center, box_width, box_height = box_current
                    x_min = int(x_center - (box_width / 2))
                    y_min = int(y_center - (box_height / 2))

                    # Adding results into prepared lists
                    bounding_boxes.append([x_min, y_min,
                                           int(box_width), int(box_height)])
                    confidences.append(float(confidence_current))
                    class_numbers.append(class_current)

        # Implementing non-maximum suppression of given bounding boxes
        # With this technique we exclude some of bounding boxes if their
        # corresponding confidences are low or there is another
        # bounding box for this region with higher confidence

        # It is needed to make sure that data type of the boxes is 'int'
        # and data type of the confidences is 'float'
        # https://github.com/opencv/opencv/issues/12789
        results = cv2.dnn.NMSBoxes(bounding_boxes, confidences,
                                   probability_minimum, threshold)

        # Checking if there is at least one detected object
        # after non-maximum suppression
        if len(results) > 0:
            # Going through indexes of results
            for i in results.flatten():
                # Getting current bounding box coordinates,
                # its width and height
                x_min, y_min = bounding_boxes[i][0], bounding_boxes[i][1]
                box_width, box_height = bounding_boxes[i][2], bounding_boxes[i][3]

                # Preparing colour for current bounding box
                # and converting from numpy array to list
                colour_box_current = colours[class_numbers[i]].tolist()

                # # # Check point
                # print(type(colour_box_current))  # <class 'list'>
                # print(colour_box_current)  # [172 , 10, 127]

                # Drawing bounding box on the original current frame
                frame_mat = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #print(x_center)
                err, point_cloud_value = point_cloud.get_value(x_center, y_center)
                if math.isfinite(point_cloud_value[2]):
                    distance = math.sqrt(point_cloud_value[0] * point_cloud_value[0] +
                                         point_cloud_value[1] * point_cloud_value[1] +
                                         point_cloud_value[2] * point_cloud_value[2])
                    print(f"Distance to Camera at ({x_center},{y_center}): {distance}")
                else:
                    print(f"The distance cannot be computed at ({x_center},{y_center})")

                cv2.rectangle(frame_mat, (x_min, y_min),
                              (x_min + box_width, y_min + box_height),
                              colour_box_current, 2)

                # Preparing text with label and confidence for current bounding box
                text_box_current = '{}: {:.4f}'.format(labels[int(class_numbers[i])],
                                                       confidences[i])

                # Putting text with label and confidence on the original image
                cv2.putText(frame_mat, text_box_current, (x_min, y_min - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour_box_current, 2)

                if focalLength == 0:
                    focal_lenght_calculator(bilinen_uzaklik, box_height, tabela_uzunlugu)

                j = distance_to_camera(tabela_uzunlugu, focalLength, box_height)
                k = int(j / 10)

                # b = str(class_numbers[0]) +','+str(x_min)+','+str(y_min)+','+str(box_width)+','+str(box_height)+','+str(k)
                b = str(class_numbers[0]) + ',' + str(k)

                print(labels[int(class_numbers[i])],confidences[i])

                ###Deneme

                # '1'+','
                # c = '2'+','+str(class_numbers[0]) +','+str(x_min)+','+str(y_min)+','+str(box_width)+','+str(box_height)

                # c.data = c
        # Showing results obtained from camera in Real Time11,274,200,67,67,772.2985074626865

        # Showing current frame with detected objects
        # Giving name to the window with current frame
        # And specifying that window is resizable
        #cv2.namedWindow('YOLO v3 Real Time Detections', cv2.WINDOW_NORMAL)
        # Pay attention! 'cv2.imshow' takes images in BGR format

        cv2.imshow('YOLO v3 Real Time Detections', frame)
        # Breaking the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Releasing camera

    # Destroying all opened OpenCV windows

