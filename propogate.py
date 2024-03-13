import os, cv2, natsort
import numpy as np

def compute_optical_flow(prev_frame, next_frame):
    # Compute dense optical flow
    return cv2.calcOpticalFlowFarneback(prev_frame, next_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)

# warp drawn frame using flow
def warp_frame(flow, drawn_frame, interpolation=cv2.INTER_LINEAR):
    h, w, _ = flow.shape
    remap_flow = flow.transpose(2, 0, 1)
    
    remap_xy = np.float32(np.mgrid[:h, :w][::-1])
    
    remap_x, remap_y = np.float32(remap_xy + remap_flow)
    return cv2.remap(drawn_frame, remap_x, remap_y, interpolation)

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

    # Find the closest drawn frame's index 
    closest_drawn = min(drawn_frames.keys(), key=lambda x: abs(x - i))
    
    # Compute optical flow between consecutive video frames
    flow = compute_optical_flow(video_frame.mean(-1), drawn_frames[closest_drawn].mean(-1))
    
    # Warp the frame
    warped = warp_frame(flow, drawn_frames[closest_drawn])
    
    # Save the frame
    output_frame = os.path.join(output_frame_folder, f"{os.path.splitext(video_frames[i])[0]}.jpg")
    cv2.imwrite(output_frame, warped)