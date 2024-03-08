import os, cv2, natsort

def compute_optical_flow(prev_frame, next_frame):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

    # Use the Lucas-Kanade method to compute optical flow
    flow = cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    return flow

def propagate(drawn_frame, video_frame, output_frame, flow):
        # Use the optical flow to propagate the drawn style to the original video frame
        warped_drawn_frame = cv2.remap(drawn_frame, flow, None, cv2.INTER_LINEAR)

        # Blend the warped drawn frame with the original video frame
        propagated_frame = cv2.addWeighted(video_frame, 0.5, warped_drawn_frame, 0.5, 0)

        # Save the propagated frame to the output folder
        cv2.imwrite(output_frame, propagated_frame)

# Specify the paths to the folders

if(not os.path.isdir('output')):
    os.mkdir("output")
    
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

for i in range(len(video_frames) - 1):
    video_frame = cv2.imread(os.path.join(video_frame_folder, video_frames[i]))
    next_video_frame = cv2.imread(os.path.join(video_frame_folder, video_frames[i+1]))
    output_frame = os.path.join(output_frame_folder, video_frames[i])

    # Compute optical flow between consecutive video frames
    flow = compute_optical_flow(video_frame, next_video_frame)

    # Iterate over drawn frames and propagate style to video frame
    for drawn_frame in drawn_frames:
        propagate(drawn_frame, video_frame, output_frame, flow)