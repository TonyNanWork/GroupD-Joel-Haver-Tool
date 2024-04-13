import cv2
import dlib
import numpy as np
import os


# Paths and initialization
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')  # Ensure the model file is in the correct location



def get_mouth_size(landmarks):
    mouth_width = landmarks[54][0] - landmarks[48][0]
    mouth_height = landmarks[57][1] - landmarks[51][1]
    return mouth_width * mouth_height

def getBestMouth(folder_path,frame_list):

    returnlist = []

    largest_mouth_size = 0
    image_with_largest_mouth = None

    # Process each image in the folder
    for filename in frame_list:
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            image = cv2.imread(image_path)
            if image is None:
                continue
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)
            
            for face in faces:
                landmarks = predictor(gray, face)
                landmarks = [(p.x, p.y) for p in landmarks.parts()]
                
                mouth_size = get_mouth_size(landmarks) 
                if mouth_size > largest_mouth_size:
                    largest_mouth_size = mouth_size
                    image_with_largest_mouth = filename
    returnlist.append(image_with_largest_mouth)
    return returnlist

