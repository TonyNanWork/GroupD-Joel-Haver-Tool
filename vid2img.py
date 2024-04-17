import cv2, os, shutil
# vidcap = cv2.VideoCapture('video_src/8a.mp4')

# success, image = vidcap.read()

def vid2img(vid_src):
    vidcap = cv2.VideoCapture(vid_src)
    success, image = vidcap.read()
    
    if(not os.path.isdir('video_data')):
        os.mkdir("video_data")
    
    # simple file to images
    for vid_src in os.listdir("video_data"):
        file_path = os.path.join("video_data", vid_src)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    frame = 1
    while success:
        cv2.imwrite('video_data/%d.jpg' % frame, image)    
        success, image = vidcap.read()
        frame += 1