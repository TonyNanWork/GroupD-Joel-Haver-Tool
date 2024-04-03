import os, cv2, natsort
import numpy as np

# Compute dense optical flow
def compute_optical_flow(prev_frame, next_frame):
    return cv2.calcOpticalFlowFarneback(prev_frame, next_frame, None, pyr_scale = 0.5, levels = 3, winsize = 15, iterations = 5, poly_n = 5, poly_sigma = 1.2, flags = 0)

# warp drawn frame using flow
def warp_frame(flow, drawn_frame, interpolation=cv2.INTER_LINEAR):
    h, w, _ = flow.shape
    remap_flow = flow.transpose(2, 0, 1)
    remap_xy = np.float32(np.mgrid[:h, :w][::-1])
    
    remap_x, remap_y = np.float32(remap_xy + remap_flow)
    return cv2.remap(drawn_frame, remap_x, remap_y, interpolation)

def visualize_optical_flow(flow):
    hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
    hsv[..., 1] = 255

    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])

    hsv[..., 0] = ang * 180 / np.pi / 2
    hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)

    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def check_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        
def get_video_frames(folder):
    return natsort.natsorted(f for f in os.listdir(folder) if f.endswith('.png') or f.endswith('jpg'))
    
def get_drawn_frames(folder):
    drawn_frames = {}
    for drawn_frame_name in os.listdir(folder):
        drawn_frame_path = os.path.join(folder, drawn_frame_name)
        drawn_frame_index = int(drawn_frame_name.split('.')[0])
        drawn_frame = cv2.imread(drawn_frame_path)
        drawn_frames[drawn_frame_index] = drawn_frame
    return drawn_frames

def propagate(video_frame_folder, drawn_frame_folder, output_frame_folder):
    
    video_frames = get_video_frames(video_frame_folder)
    #print(video_frames)
    drawn_frames = get_drawn_frames(drawn_frame_folder)

    # drawn_frames_mapping = {i: cv2.imread(os.path.join(drawn_frame_folder, frame)) for i, frame in enumerate(drawn_frames)}
    
    # Iterate over each video frame and propagate the drawn style
    for i in range(int(len(video_frames)/10)):
        video_frame = cv2.imread(os.path.join(video_frame_folder, video_frames[i]))
        next_video_frame = cv2.imread(os.path.join(video_frame_folder, video_frames[i+1]))

        # Find the closest drawn frame's index 
        closest_drawn = min(drawn_frames.keys(), key=lambda x: abs(x - i))
        #closest_drawn_frame = drawn_frames_mapping[clo]
        
        # Compute optical flow between consecutive video frames
        #flow = compute_optical_flow(video_frame.mean(-1), next_video_frame.mean(-1))
        flow = compute_optical_flow(video_frame.mean(-1), drawn_frames[closest_drawn].mean(-1))
        
        flow_visualization = visualize_optical_flow(flow)
        flow_output_path = os.path.join("flow", f"flow_{os.path.splitext(video_frames[i])[0]}.png")
        cv2.imwrite(flow_output_path, flow_visualization)
        
        # Warp the frame
        warped = warp_frame(flow, drawn_frames[closest_drawn])
        
        # Save the frame
        output_frame = os.path.join(output_frame_folder, f'{os.path.splitext(video_frames[i])[0]}.jpg')
        cv2.imwrite(output_frame, warped)

video_folder = 'video_data'
drawn_folder = 'drawn'
output_folder = 'output'
flow_folder = 'flow'

check_folder(video_folder)
check_folder(drawn_folder)
check_folder(output_folder)
check_folder(flow_folder)

propagate(video_folder, drawn_folder, output_folder)