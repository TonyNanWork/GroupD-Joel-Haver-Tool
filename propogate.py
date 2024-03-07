import optical_flow, os, cv2, natsort

def propagate(drawn_frame, video_frame, output_frame):
        # Compute optical flow between drawn frame and original video frame
        flow = optical_flow.compute_optical_flow(drawn_frame, video_frame)

        # Use the optical flow to propagate the drawn style to the original video frame
        # Example: Use the flow to warp the drawn frame onto the original video frame
        warped_drawn_frame = cv2.remap(drawn_frame, flow, None, cv2.INTER_LINEAR)

        # Save the propagated frame to the output folder
        cv2.imwrite(output_frame, warped_drawn_frame)

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