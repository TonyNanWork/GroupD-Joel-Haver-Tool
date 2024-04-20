import cv2
import dlib
import numpy as np
import os


# Paths and initialization
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')  # Ensure the model file is in the correct location

def getMouthSize(landmarks):
    mouth_width = landmarks[54][0] - landmarks[48][0]
    mouth_height = landmarks[57][1] - landmarks[51][1]
    return mouth_width * mouth_height

def getEyeSize(landmarks):
    leftEyeWidth = landmarks[44][0] - landmarks[47][0]
    leftEyeHeight = landmarks[45][1] - landmarks[48][1]

    rightEyeWidth = landmarks[38][0] - landmarks[41][0]
    rightEyeHeight  = landmarks[39][1] - landmarks[42][1]
    return leftEyeWidth * leftEyeHeight + rightEyeWidth * rightEyeHeight

def getBestFrame(folder_path,frame_list, threshold = 25):
    returnlist = []

    largest_features = 0
    best_image = None
    
    count = 0
    # Process each image in the folder
    previous_frame = None
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
                
                mouth_size = getMouthSize(landmarks) 
                eye_size = getMouthSize(landmarks) 
                eye_mouth = mouth_size + eye_size
                if mouth_size > largest_features:
                    largest_features = eye_mouth
                    best_image = filename


            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            gray = cv2.resize(gray,(0, 0),fx=0.5, fy=0.5)

            if count > 0:
                print(filename)
                frame_delta = cv2.absdiff(previous_frame, gray)
                thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)[1]
            
                # Find the percentage of changed pixels
                change_percent = np.sum(thresh) / thresh.size
                
                if change_percent > threshold:
                    print("change found")
                    #print(f"Scene change detected at image: {frame_file}")
                    returnlist.append(best_image)
                    largest_features = 0
                    best_image = filename
    

            previous_frame = gray.copy()
            count = count + 1
    returnlist.append(best_image)
    return returnlist

