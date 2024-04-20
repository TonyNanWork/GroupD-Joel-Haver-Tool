import cv2
import os
import natsort
# import time

# Converts images in folder to video
def img2vid(image_folder, video_name, fps=30, progress_callback = None):
    
    #start = time.time()
    images = natsort.natsorted(
       [f for f in os.listdir(image_folder) if f.endswith('.png') or f.endswith('.jpg')]
    )
    #images.sort(key=lambda x: int(x.split('.')[0]))
    
    # print(len(images))
    print(images)
    processed_frames = 0
    
    if not images:
        print("No images found in the folder: ", image_folder)
        return
    
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, fps, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))
            
        if progress_callback:
                processed_frames += 1
                progress = int(processed_frames * 100 / len(images))
                progress_callback(progress)

    cv2.destroyAllWindows()
    video.release()
    #end = time.time()
    #print(end-start)

# folder_path = "output"
# output_video_name = "output.avi"
# images_to_video(folder_path, output_video_name)
