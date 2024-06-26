import cv2
import numpy as np
import os
import natsort

def detectSceneChanges(frames_dir, threshold=60):
    frame_files = None
    if (type(frames_dir) == str):
    # List all frame images in the directory sorted by name
        frame_files = natsort.natsorted([f for f in os.listdir(frames_dir) if f.endswith('.png') or f.endswith('.jpg')])
    else:
        frame_files = frames_dir
    #print(frame_files)
    if len(frame_files) == 0:
        print("No image frames found in the directory")
        return []

    # Read the first frame and initialize variables
    prev_frame = cv2.imread(os.path.join(frames_dir, frame_files[0]))
   
    prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_frame_gray = cv2.resize(prev_frame_gray,(0, 0),fx=0.5, fy=0.5)
    prev_frame_gray = cv2.GaussianBlur(prev_frame_gray, (21, 21), 0)

    scene_changes = []

    for idx, frame_file in enumerate(frame_files[1:], start=1):  # Start from the second image
        frame = cv2.imread(os.path.join(frames_dir, frame_file))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray,(0, 0),fx=0.5, fy=0.5)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Calculate the absolute difference between current frame and previous frame
        frame_delta = cv2.absdiff(prev_frame_gray, gray)
        thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)[1]

        # Find the percentage of changed pixels
        change_percent = np.sum(thresh) / thresh.size
        
        if change_percent > threshold:
            #print(f"Scene change detected at image: {frame_file}")
            scene_changes.append(frame_file)

        # Update previous frame
        prev_frame_gray = gray.copy()

    return scene_changes

if __name__ == "__main__":

    frames_dir = 'video_data1'
    scene_changes = detectSceneChanges(frames_dir)
    print("Scene changes at images:", scene_changes)
