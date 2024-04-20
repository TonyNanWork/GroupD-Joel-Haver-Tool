import cv2, os, shutil
# vidcap = cv2.VideoCapture('video_src/8a.mp4')

# success, image = vidcap.read()

def vid2img(vid_src, progress_callback = None):
    vidcap = cv2.VideoCapture(vid_src)
    success, image = vidcap.read()
    
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    processed_frames = 0
    
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
        frame_num = '%d' % frame
        #Output to test with ebsynth
        #frame_num = frame_num.zfill(4) 
        cv2.imwrite('video_data/'+ frame_num +'.jpg' , image)    
        success, image = vidcap.read()
        frame += 1
        
        if progress_callback:
            processed_frames += 1
            progress = int(processed_frames * 100 / total_frames)
            progress_callback(progress)