import os, cv2, natsort
import numpy as np

def compute_optical_flow(prev_frame, next_frame):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

    # Compute optical flow
    flow = cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    return flow

def propagate(drawn_frame, flow):
    # Convert drawn frame to grayscale
    # drawn_gray = cv2.cvtColor(drawn_frame, cv2.COLOR_BGR2GRAY)

    # Remap the drawn frame using the optical flow
    warped_drawn_frame = cv2.remap(drawn_frame, flow[..., 0], flow[..., 1], cv2.INTER_LINEAR)

    return warped_drawn_frame


# Specify the paths to the folders
drawn_frame_folder = "drawn"
video_frame_folder = "video_data"
output_frame_folder = "output"

# Load all drawn frames
drawn_frames = {}
for drawn_frame_name in os.listdir(drawn_frame_folder):
    drawn_frame_path = os.path.join(drawn_frame_folder, drawn_frame_name)
    drawn_frame_index = int(drawn_frame_name.split('.')[0])
    drawn_frame = cv2.imread(drawn_frame_path)
    drawn_frames[drawn_frame_index] = drawn_frame

# Sort and load video frames
video_frames = natsort.natsorted(
    [f for f in os.listdir(video_frame_folder) if f.endswith('.png') or f.endswith('.jpg')]
)

# Iterate over each video frame and propagate the drawn style
for i in range(len(video_frames) - 1):
    video_frame = cv2.imread(os.path.join(video_frame_folder, video_frames[i]))
    next_video_frame = cv2.imread(os.path.join(video_frame_folder, video_frames[i+1]))

    # Compute optical flow between consecutive video frames
    flow = compute_optical_flow(video_frame, next_video_frame)

    # Find the closest drawn frame index
    closest_drawn_frame_index = min(drawn_frames.keys(), key=lambda x: abs(x - i))

    # Propagate the drawn style using the optical flow
    propagated_frame = propagate(drawn_frames[closest_drawn_frame_index], flow)

    # Save the propagated frame with a unique filename
    output_frame = os.path.join(output_frame_folder, f"{os.path.splitext(video_frames[i])[0]}.jpg")
    cv2.imwrite(output_frame, propagated_frame)