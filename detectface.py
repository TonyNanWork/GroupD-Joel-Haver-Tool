import cv2
import dlib
import numpy as np
import os


def process_frame(image_path):
    # import required libraries

    # read input image
    img = cv2.imread(image_path)

    # convert to grayscale of each frames
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # read the haarcascade to detect the faces in an image
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # read the haarcascade to detect the eyes in an image
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye_tree_eyeglasses.xml')

    # detects faces in the input image
    faces = face_cascade.detectMultiScale(gray, 1.5, 9)
    print('Number of detected faces:', len(faces))
    roi_gray = None
    roi_color = None
    # loop over the detected faces
    for (x,y,w,h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
    
    # detects eyes of within the detected face area (roi)
    eyes = eye_cascade.detectMultiScale(roi_gray)
    print(eyes)
    
    # draw a rectangle around eyes
    for (ex,ey,ew,eh) in eyes:
        cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,255),2)

    # display the image with detected eyes
    cv2.imshow('Eyes Detection',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
        




# Process all PNG frames in a directory
frames_directory = 'video_data'
for frame in os.listdir(frames_directory):
    if frame.endswith('.jpg') or frame.endswith('.png'):
        process_frame(os.path.join(frames_directory, frame))

cv2.destroyAllWindows()