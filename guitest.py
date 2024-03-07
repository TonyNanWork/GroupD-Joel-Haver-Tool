import sys
import os
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QListWidget,
                             QListWidgetItem, QSlider, QPushButton, QSizePolicy)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt, QSize

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.frame_folder = ""
        self.frame_files = []
        self.current_frame = 0
        self.isPlaying = False

        self.initUI()
        self.selectFolder()

    def initUI(self):
        self.mainLayout = QVBoxLayout()  # Main layout

        # Video display
        self.videoLayout = QHBoxLayout()
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

    def playVideo(self):
        if not self.isPlaying:
            self.timer.start(100)  # Adjust the frame rate as needed
            self.isPlaying = True

    def stopVideo(self):
        self.timer.stop()
        self.isPlaying = False

    def selectFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder With Frames")
        if folder:
            self.frame_folder = folder
            self.frame_files = sorted([f for f in os.listdir(folder) if f.endswith('.png')])
            self.current_frame = 0
            self.slider.setMaximum(len(self.frame_files) - 1)
            self.populateFrameList()
            self.showNextFrame()


    def populateFrameList(self):
        self.frameList.clear()
        thumbnailSize = 150  # Desired thumbnail size

        for filename in self.frame_files:
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

    # Adjust the width of the QListWidget to accommodate the larger thumbnails
        self.frameList.setFixedWidth(thumbnailSize + 20)  # Adjust based on your UI needs



    def showNextFrame(self):
        if self.frame_files and self.current_frame < len(self.frame_files):
            frame_path = os.path.join(self.frame_folder, self.frame_files[self.current_frame])
            pixmap = QPixmap(frame_path)
            self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio))
            self.slider.setValue(self.current_frame)
            self.filenameLabel.setText(self.frame_files[self.current_frame])

            if self.isPlaying:
                self.current_frame += 1
                if self.current_frame >= len(self.frame_files):
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
            self.current_frame = currentRow
            self.showNextFrame()

def main():
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.resize(1000, 800)  # Adjust the initial size as needed
    player.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
