import cv2, os, natsort
# vidcap = cv2.VideoCapture('video_src/8a.mp4')

# success, image = vidcap.read()

def img2vid(image_folder, video_name, fps=30, codec='XVID', progress_callback=None):
    images = natsort.natsorted(
        [f for f in os.listdir(image_folder) if f.endswith('.png') or f.endswith('.jpg')]
    )

    if not images:
        print("No images found in the folder:", image_folder)
        return

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*codec)
    video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

        if progress_callback:
            progress_callback(int((images.index(image) + 1) * 100 / len(images)))

    cv2.destroyAllWindows()
    video.release()