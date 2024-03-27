import os, cv2, natsort
import numpy as np

# Compute optical flow using gradient constraint equation
def compute_optical_flow(image1, image2):
    gradient_x = cv2.Sobel(image1, cv2.CV_64F, 1, 0, ksize=5)
    gradient_y = cv2.Sobel(image1, cv2.CV_64F, 0, 1, ksize=5)
    
    temporal_gradient = image2 - image1

    flow_x = -gradient_x * temporal_gradient
    flow_y = -gradient_y * temporal_gradient
    
    return flow_x, flow_y

# warp drawn frame using flow
def warp_frame(flow_x, flow_y, drawn_frame, interpolation=cv2.INTER_LINEAR):
    h, w = flow_x.shape[:2]
    
    # Generate grid coordinates
    grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
    
    # Compute destination coordinates by adding flow vectors
    map_x = grid_x + 4 * flow_x
    map_y = grid_y + 4 * flow_y
    
    # Ensure destination coordinates are within image bounds
    map_x = np.clip(map_x, 0, w - 1)
    map_y = np.clip(map_y, 0, h - 1)
    
    # Convert coordinates to float32
    map_x = map_x.astype(np.float32)
    map_y = map_y.astype(np.float32)
    
    return cv2.remap(drawn_frame, map_x, map_y, interpolation)

def visualize_optical_flow(flow_x, flow_y):
    # Calculate magnitude and angle of flow vectors
    magnitude, angle = cv2.cartToPolar(flow_x, flow_y)
    
    # Normalize magnitude
    magnitude_normalized = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    
    hue = angle * 180 / np.pi / 2
    saturation = np.ones_like(magnitude_normalized) * 255
    
    # Convert to HSV color space
    hsv = np.zeros((flow_x.shape[0], flow_x.shape[1], 3), dtype=np.uint8)
    hsv[..., 0] = hue
    hsv[..., 1] = saturation
    #hsv[..., 2] = magnitude_normalized.astype(np.uint8)
    hsv[..., 2] = magnitude.astype(np.uint8)
    
    # Convert HSV to BGR for visualization
    flow_visualization = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return flow_visualization

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
    for i in range(len(video_frames) - 1):
        video_frame = cv2.imread(os.path.join(video_frame_folder, video_frames[i]))
        next_video_frame = cv2.imread(os.path.join(video_frame_folder, video_frames[i+1]))

        # Find the closest drawn frame's index 
        closest_drawn = min(drawn_frames.keys(), key=lambda x: abs(x - i))
        #closest_drawn_frame = drawn_frames_mapping[clo]
        
        # Compute optical flow between consecutive video frames
        #flow = compute_optical_flow(video_frame.mean(-1), next_video_frame.mean(-1))
        # flow = compute_optical_flow(video_frame.mean(-1), drawn_frames[closest_drawn].mean(-1))
        
        # flow_visualization = visualize_optical_flow(flow)
        # flow_output_path = os.path.join("flow", f"flow_{os.path.splitext(video_frames[i])[0]}.png")
        # cv2.imwrite(flow_output_path, flow_visualization)
        
        # # Warp the frame
        # warped = warp_frame(flow, drawn_frames[closest_drawn])

        # # Save the frame
        # output_frame = os.path.join(output_frame_folder, f'{os.path.splitext(video_frames[i])[0]}.png')
        # cv2.imwrite(output_frame, warped)
                # Compute optical flow between consecutive video frames using the provided function
        flow_x, flow_y = compute_optical_flow(video_frame.mean(-1), drawn_frames[closest_drawn].mean(-1))

        #flow_magnitude = np.sqrt(flow_x ** 2 + flow_y ** 2)
        #print(f"Frame {i}: Optical flow magnitude = {np.mean(flow_magnitude)}")

        flow_visualization = visualize_optical_flow(flow_x, flow_y)
        flow_output_path = os.path.join("flow", f"flow_{os.path.splitext(video_frames[i])[0]}.png")
        cv2.imwrite(flow_output_path, flow_visualization)

        warped = warp_frame(flow_x, flow_y, drawn_frames[closest_drawn])

        output_frame = os.path.join(output_frame_folder, f'{os.path.splitext(video_frames[i])[0]}.png')
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