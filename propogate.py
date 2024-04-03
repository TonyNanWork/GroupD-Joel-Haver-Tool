import os, cv2, natsort
import numpy as np

# Compute optical flow using gradient constraint equation
# def compute_optical_flow(image1, image2):
#     gradient_x = cv2.Sobel(image1, cv2.CV_64F, 1, 0, ksize=5)
#     gradient_y = cv2.Sobel(image1, cv2.CV_64F, 0, 1, ksize=5)
    
    
#     temporal_gradient = image2 - image1

#     flow_x = -gradient_x * temporal_gradient
#     flow_y = -gradient_y * temporal_gradient
    
#     return flow_x, flow_y

def compute_optical_flow(im1, im2):
    #prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    #next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

    # Compute dense optical flow
    flow = cv2.calcOpticalFlowFarneback(im1, im2, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    return flow

# def compute_optical_flow(prev_frame, next_frame, window_size=2):
#     height, width = prev_frame.shape

#     # Compute derivatives of the first frame
#     Ix = np.gradient(prev_frame, axis=1)
#     Iy = np.gradient(prev_frame, axis=0)
#     It = next_frame - prev_frame

#     # Initialize flow vectors
#     flow = np.zeros((height, width, 2))

#     # Compute optical flow for each pixel
#     half_window = window_size // 2
#     # Compute optical flow for each pixel
#     for y in range(half_window, height - half_window):
#         for x in range(half_window, width - half_window):
#             # Ensure the window is within bounds
#             y_min = max(0, y - half_window)
#             y_max = min(height - 1, y + half_window)
#             x_min = max(0, x - half_window)
#             x_max = min(width - 1, x + half_window)

#             # Compute sum of products of derivatives in the window
#             Ix_window = Ix[y_min:y_max + 1, x_min:x_max + 1].flatten()
#             Iy_window = Iy[y_min:y_max + 1, x_min:x_max + 1].flatten()
#             It_window = It[y_min:y_max + 1, x_min:x_max + 1].flatten()

#             A = np.vstack((Ix_window, Iy_window)).T
#             b = -It_window[:, np.newaxis]

#             # Solve linear system
#             if np.linalg.matrix_rank(A) >= 2:
#                 flow[y, x] = np.linalg.lstsq(A, b, rcond=None)[0].reshape(2)

#     return flow

# warp drawn frame using flow
def warp_frame(flow, drawn_frame, interpolation=cv2.INTER_LINEAR):
    
    flow_x = flow[...,0]
    flow_y = flow[...,1]
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

def visualize_optical_flow(flow):
    # Split the flow into x and y components
    flow_x = flow[...,0]
    flow_y = flow[...,1]
    
    # Calculate magnitude and angle of flow vectors
    magnitude, angle = cv2.cartToPolar(flow_x, flow_y)
    
    # Normalize magnitude
    magnitude_normalized = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    
    # Convert angle to hue
    hue = angle * 180 / np.pi / 2
    saturation = np.ones_like(magnitude_normalized) * 255
    
    # Convert to HSV color space
    hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
    hsv[..., 0] = hue
    hsv[..., 1] = saturation
    hsv[..., 2] = magnitude_normalized.astype(np.uint8)
    
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
    for i in range(int(len(video_frames)/10)):
        video_frame = cv2.imread(os.path.join(video_frame_folder, video_frames[i]))
        next_video_frame = cv2.imread(os.path.join(video_frame_folder, video_frames[i+1]))

        # Find the closest drawn frame's index 
        closest_drawn = min(drawn_frames.keys(), key=lambda x: abs(x - i))
        # closest_drawn_frame = drawn_frames_mapping[clo]
        
        # Compute optical flow between consecutive video frames
        flow = compute_optical_flow(video_frame.mean(-1), next_video_frame.mean(-1))
        flow = compute_optical_flow(video_frame.mean(-1), drawn_frames[closest_drawn].mean(-1))
        
        flow_visualization = visualize_optical_flow(flow)
        flow_output_path = os.path.join("flow", f"flow_{os.path.splitext(video_frames[i])[0]}.png")
        cv2.imwrite(flow_output_path, flow_visualization)
        
        # Warp the frame
        warped = warp_frame(flow, drawn_frames[closest_drawn])

        # Save the frame
        output_frame = os.path.join(output_frame_folder, f'{os.path.splitext(video_frames[i])[0]}.jpg')
        cv2.imwrite(output_frame, warped)
        
        print(f"Done frame {i+1}")

        # flow_x, flow_y = compute_optical_flow(video_frame.mean(-1), drawn_frames[closest_drawn].mean(-1))

        # #flow_magnitude = np.sqrt(flow_x ** 2 + flow_y ** 2)
        # #print(f"Frame {i}: Optical flow magnitude = {np.mean(flow_magnitude)}")

        # flow_visualization = visualize_optical_flow(flow_x, flow_y)
        # flow_output_path = os.path.join("flow", f"flow_{os.path.splitext(video_frames[i])[0]}.png")
        # cv2.imwrite(flow_output_path, flow_visualization)

        # warped = warp_frame(flow_x, flow_y, drawn_frames[closest_drawn])

        # output_frame = os.path.join(output_frame_folder, f'{os.path.splitext(video_frames[i])[0]}.png')
        # cv2.imwrite(output_frame, warped)

video_folder = 'video_data'
drawn_folder = 'drawn'
output_folder = 'output'
flow_folder = 'flow'

check_folder(video_folder)
check_folder(drawn_folder)
check_folder(output_folder)
check_folder(flow_folder)

propagate(video_folder, drawn_folder, output_folder)