import cv2, os
import numpy as np

def compute_optical_flow(prev_frame, next_frame):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

    # Use the Lucas-Kanade method to compute optical flow
    flow = cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    return flow

def compute_optical_flow_frames(folder_path):
    frames = os.listdir(folder_path)
    frames.sort()  # Make sure frames are sorted in the correct order

    for i in range(len(frames) - 1):
        prev_frame = cv2.imread(os.path.join(folder_path, frames[i]))
        next_frame = cv2.imread(os.path.join(folder_path, frames[i + 1]))

        flow = compute_optical_flow(prev_frame, next_frame)

        # Use 'flow' to propagate the animation to the next frame
        # implement logic for drawing on the next frame based on the optical flow

        # Use the flow to warp the next frame
        # warped_next_frame = cv2.remap(next_frame, flow, None, cv2.INTER_LINEAR)

        # Save the modified frame to a new folder or process it further
        # cv2.imwrite(os.path.join(output_folder, frames[i + 1]), warped_next_frame)
