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

def getBestFrame(folder_path, frame_list, threshold = 25, top_n=10, frame_diff_threshold=50):
    returnlist = []
    scene_frames = []
    largest_features_list = []
    used_frames = set()
    last_selected_frame = None

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
                eye_size = getEyeSize(landmarks) 
                eye_mouth = mouth_size + eye_size
                
                largest_features_list.append((eye_mouth, filename))
                scene_frames.append(filename)


            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            gray = cv2.resize(gray,(0, 0),fx=0.5, fy=0.5)

            if previous_frame is not None:
                #print(filename)
                frame_delta = cv2.absdiff(previous_frame, gray)
                thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)[1]
            
                # Find the percentage of changed pixels
                change_percent = np.sum(thresh) / thresh.size
                
                if change_percent > threshold:
                    print("change found")
                    #print(f"Scene change detected at image: {frame_file}")
                    largest_features_list.sort(reverse=True)
                    for i in range(top_n):
                        if largest_features_list[i][1] not in used_frames:
                            if last_selected_frame is None or abs(frame_list.index(largest_features_list[i][1]) - frame_list.index(last_selected_frame)) >= frame_diff_threshold:
                                returnlist.append(largest_features_list[i][1])
                                used_frames.add(largest_features_list[i][1])
                                last_selected_frame = largest_features_list[i][1]
                                break
                    largest_features_list = []
                    scene_frames = []
                    

            previous_frame = gray.copy()
    
    largest_features_list.sort(reverse=True)
    for i in range(top_n):
        if largest_features_list[i][1] not in used_frames:
            if last_selected_frame is None or abs(frame_list.index(largest_features_list[i][1]) - frame_list.index(last_selected_frame)) >= frame_diff_threshold:
                returnlist.append(largest_features_list[i][1])
                used_frames.add(largest_features_list[i][1])

    
    print(returnlist)
    
    return returnlist