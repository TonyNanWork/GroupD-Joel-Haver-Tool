import sys
import os
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QListWidget,
                             QListWidgetItem, QSlider, QPushButton, QSizePolicy)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt, QSize
from scenechange import detect_scene_changes_from_images
from propagate import propagate, check_folder
from faceLandmarkDetector import getBestMouth

import natsort

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.frame_folder = ""
        self.scene_files = [[]]
        self.scene_keyFrames = [[]]

        self.frame_files = []
        self.current_scene = 0
        self.current_frame = 0
        self.isPlaying = False

        self.initUI()
        #self.selectFolder()

    def initUI(self):
        self.mainLayout = QVBoxLayout()  # Main layout

        self.videoLayout = QHBoxLayout()
        # KeyFrame List 

        self.keyframeList = QListWidget()
        self.keyframeList.setViewMode(QListWidget.IconMode)
        self.keyframeList.currentRowChanged.connect(self.listKeyFrameChanged)
        self.keyframeList.setIconSize(QSize(200, 200))  # Ensure the icon size is set

        self.keyframeList.setFixedWidth(120)  # Set fixed width for the list
        self.videoLayout.addWidget(self.keyframeList)
        

        # Video display

        self.label = QLabel(self)
        self.videoLayout.addWidget(self.label)

        # Frame list
        self.frameList = QListWidget()
        self.frameList.setViewMode(QListWidget.IconMode)
        self.frameList.currentRowChanged.connect(self.listFrameChanged)
        self.frameList.setIconSize(QSize(200, 200))  # Ensure the icon size is set

        self.frameList.setFixedWidth(120)  # Set fixed width for the list
        self.videoLayout.addWidget(self.frameList)

        self.mainLayout.addLayout(self.videoLayout)

        # Filename label
        self.filenameLabel = QLabel("Filename will appear here")
        self.filenameLabel.setAlignment(Qt.AlignCenter)  # Center align the text
        self.mainLayout.addWidget(self.filenameLabel)

        # Controls for play and stop
        self.controlsLayout = QHBoxLayout()
        self.playButton = QPushButton("Play")
        self.playButton.clicked.connect(self.playVideo)
        self.stopButton = QPushButton("Stop")
        self.stopButton.clicked.connect(self.stopVideo)
        self.controlsLayout.addWidget(self.playButton)
        self.controlsLayout.addWidget(self.stopButton)
        self.mainLayout.addLayout(self.controlsLayout)

        # Timeline slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.valueChanged.connect(self.sliderChanged)
        self.mainLayout.addWidget(self.slider)

        self.setLayout(self.mainLayout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.nextFrame)
        
        # video folder button
        self.videoframeButton = QPushButton("Select Video Folder")
        self.videoframeButton.clicked.connect(self.selectFolder)
        self.controlsLayout.addWidget(self.videoframeButton)
        
        #  keyframe finder button
        self.keyframesButton = QPushButton("Find Keyframes")
        self.keyframesButton.clicked.connect(self.get_keyframes)
        self.controlsLayout.addWidget(self.keyframesButton)
        
        # Propogate Button
        self.propogateButton = QPushButton("Propogate")
        self.propogateButton.clicked.connect(self.flow_propogation)
        self.controlsLayout.addWidget(self.propogateButton)

    def playVideo(self):
        if not self.isPlaying:
            self.timer.start(30)  # Adjust the frame rate as needed
            self.isPlaying = True

    def stopVideo(self):
        self.timer.stop()
        self.isPlaying = False

    def selectFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder With Frames")
        if folder:
            self.frame_folder = folder
            # Sort the files numerically - adds some extra wait time though
            self.frame_files = natsort.natsorted(
                [f for f in os.listdir(folder) if f.endswith('.png') or f.endswith('.jpg')]
            )
            self.current_frame = 0
            self.populateFrameList()
            self.slider.setMaximum(len(self.scene_files[self.current_scene]) - 1)

            self.showNextFrame()

    def get_keyframes(self):
        self.scene_keyFrames[self.current_scene] = getBestMouth(self.frame_folder,self.scene_files[self.current_scene])

        self.keyframeList.clear()


        thumbnailSize = 150  # Desired thumbnail size

        for image in self.scene_keyFrames[self.current_scene]:
            frame_path = os.path.join(self.frame_folder, image)

            #frame_path = os.path.join(self.frame_folder, filename)
            pixmap = QPixmap(frame_path)

        # Scale the pixmap to the thumbnail size while maintaining aspect ratio
            scaledPixmap = pixmap.scaled(thumbnailSize, thumbnailSize, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Create an icon from the scaled pixmap
            icon = QIcon(scaledPixmap)

        # Create a list item and set its icon
            item = QListWidgetItem()
            item.setIcon(icon)

 
            item.setSizeHint(scaledPixmap.size())
            self.keyframeList.addItem(item)


            
            
            

    # Adjust the width of the QListWidget to accommodate the larger thumbnails
        self.frameList.setFixedWidth(thumbnailSize + 20)  # Adjust based on your UI needs
        print(self.scene_keyFrames[self.current_scene])
        

    def flow_propogation(self):
        if self.frame_folder:
            video = self.frame_folder  # Assuming the video data folder is the same as the frame folder
            drawn = "drawn"
            output = "output"
            propagate(video, drawn, output)
        else:
            print("Please select a folder containing video frames before performing optical flow.")
    

    def populateFrameList(self):
        self.frameList.clear()

        changes = detect_scene_changes_from_images(self.frame_folder)
        print(changes)
        changes.insert(0,self.frame_files[0])
        changes.append("placeholder")

        thumbnailSize = 150  # Desired thumbnail size

        scene_num = 0
        scenelist =[]

        for filename in self.frame_files:
            if filename == changes[scene_num]:
                frame_path = os.path.join(self.frame_folder, filename)
                pixmap = QPixmap(frame_path)

        # Scale the pixmap to the thumbnail size while maintaining aspect ratio
                scaledPixmap = pixmap.scaled(thumbnailSize, thumbnailSize, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Create an icon from the scaled pixmap
                icon = QIcon(scaledPixmap)

        # Create a list item and set its icon
                item = QListWidgetItem()
                item.setIcon(icon)

        # Optionally, set the text of the item here if desired, e.g., item.setText("Frame")
        
        # Set the size hint to ensure the list widget item is large enough to display the icon
                item.setSizeHint(scaledPixmap.size())

                self.frameList.addItem(item)

                scene_num = scene_num + 1
                self.scene_files.append([])
                self.scene_keyFrames.append([])

            self.scene_files[scene_num - 1].append(filename)
            
            

    # Adjust the width of the QListWidget to accommodate the larger thumbnails
        self.frameList.setFixedWidth(thumbnailSize + 20)  # Adjust based on your UI needs



    def showNextFrame(self):
        if self.frame_files and self.current_frame < len(self.scene_files[self.current_scene]):
            frame_path = os.path.join(self.frame_folder, self.scene_files[self.current_scene][self.current_frame])
            pixmap = QPixmap(frame_path)
            self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio))
            self.slider.setValue(self.current_frame)
            self.filenameLabel.setText(self.scene_files[self.current_scene][self.current_frame])

            if self.isPlaying:
                self.current_frame += 1
                if self.current_frame >= len(self.scene_files[self.current_scene]):
                    self.current_frame = 0  # Loop back to the first frame
                    self.stopVideo()  # Stop when reaching the last frame

    def nextFrame(self):
        self.showNextFrame()

    def sliderChanged(self, value):
        if 0 <= value < len(self.frame_files):
            self.current_frame = value
            self.showNextFrame()

    def listFrameChanged(self, currentRow):
        if 0 <= currentRow < len(self.frame_files):
            self.current_scene = currentRow
            self.current_frame = 0
            self.slider.setMaximum(len(self.scene_files[self.current_scene]) - 1)
            self.slider.setValue(0)
            self.showNextFrame()

    def listKeyFrameChanged(self, currentRow):
        index = self.scene_files[self.current_scene].index(self.scene_keyFrames[self.current_scene][currentRow])
        self.current_frame = index
        self.slider.setValue(index)
        self.showNextFrame()

def main():
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.resize(1600, 900)  # Adjust the initial size as needed
    player.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
