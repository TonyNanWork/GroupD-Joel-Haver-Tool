import cv2
import os

def images_to_video(image_folder, video_name, fps=30):
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images.sort(key=lambda x: int(x.split('.')[0]))  # Sort images numerically
    if not images:
        print("No images found in the folder: ", image_folder)
        return
    
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, fps, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()


if __name__ == "__main__":
    folder_path = "output"
    output_video_name = "output.avi"
    images_to_video(folder_path, output_video_name)
