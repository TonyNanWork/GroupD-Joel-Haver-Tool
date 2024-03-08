import os, cv2, natsort

def compute_optical_flow(prev_frame, next_frame):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

    # Use the Lucas-Kanade method to compute optical flow
    flow = cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    return flow

def propagate(drawn_frame, video_frame, output_frame):
        # Compute optical flow between drawn frame and original video frame
        flow = compute_optical_flow(drawn_frame, video_frame)

        # Use the optical flow to propagate the drawn style to the original video frame
        h, w = drawn_frame.shape[:2]
        flow_map = -flow * 2  # Scale the flow map to match pixel coordinates
        remapped_frame = cv2.remap(drawn_frame, flow_map, None, cv2.INTER_LINEAR)
        #warped_drawn_frame = cv2.remap(drawn_frame, flow, None, cv2.INTER_LINEAR)

        # Save the propagated frame to the output folder
        cv2.imwrite(output_frame, remapped_frame)

# Specify the paths to the folders
drawn_frame_folder = "drawn"
video_frame_folder = "video_data"
output_frame_folder = "output"

# Load all drawn frames
drawn_frames = []
for drawn_frame_name in os.listdir(drawn_frame_folder):
    drawn_frame_path = os.path.join(drawn_frame_folder, drawn_frame_name)
    drawn_frame = cv2.imread(drawn_frame_path)
    drawn_frames.append(drawn_frame)


# Iterate over each video frame and propagate the drawn style from each drawn frame
video_frames = natsort.natsorted(
    [f for f in os.listdir(video_frame_folder) if f.endswith('.png') or f.endswith('.jpg')]
)

for frame_name in video_frames:
    video_frame = cv2.imread(os.path.join(video_frame_folder, frame_name))
    output_frame = os.path.join(output_frame_folder, frame_name)

    # Propagate the drawn style from each drawn frame to the video frame
    for drawn_frame in drawn_frames:
        propagate(drawn_frame, video_frame, output_frame)