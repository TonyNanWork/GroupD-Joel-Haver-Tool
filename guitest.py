import sys, os, natsort, cv2, shutil

from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QListWidget,
                             QListWidgetItem, QSlider, QPushButton, QSizePolicy, QProgressBar, QMessageBox, QComboBox, 
                             QMenu, QAction, QToolButton)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, Qt, QSize, pyqtSignal, QThread
from scenechange import detectSceneChanges
from propagate import propagate, checkFolder,propagateScene
from faceLandmarkDetector import getBestFrame

from vid2img import vid2img
from img2vid import img2vid

class Worker(QThread):
    progress_callback = pyqtSignal(int)
    result_callback = pyqtSignal(object)

    def __init__(self, function, *args, callback=None, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.callback = callback  # Callback function for returning the result

    def run(self):
        try:
            # Call the function with provided arguments and keyword arguments
            result = self.function(*self.args, **self.kwargs, progress_callback=self.update_progress)
            if self.callback:  # Check if callback function is provided
                self.callback(result)  # Call the callback function with the result
            else:
                self.result_callback.emit(result)  # Emit the result if no callback function
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error occurred: {str(e)}")
            return

    def update_progress(self, progress):
        self.progress_callback.emit(progress)

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.frame_folder = "video_data"
        self.scene_files = [[]]
        self.scene_keyFrames = [[]]

        checkFolder("video_data")
        checkFolder("drawn")
        checkFolder("keyframes")
        checkFolder("output")

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

        self.controlsLayout = QHBoxLayout()

        # video folder        
        self.videoButton = QPushButton("Select Video File")
        self.videoButton.clicked.connect(self.selectVideo)
        self.controlsLayout.addWidget(self.videoButton)

        # Controls for play and stop
        self.playButton = QPushButton("Play")
        self.playButton.clicked.connect(self.playVideo)
        self.playButton.setEnabled(False)
        self.controlsLayout.addWidget(self.playButton)
        
        self.stopButton = QPushButton("Pause")
        self.stopButton.clicked.connect(self.stopVideo)
        self.stopButton.setEnabled(False)
        self.controlsLayout.addWidget(self.stopButton)

        # Timeline slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.valueChanged.connect(self.sliderChanged)
        self.slider.setEnabled(False)
        self.mainLayout.addWidget(self.slider)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.nextFrame)
        
        #  keyframe finder button
        self.keyframesButton = QPushButton("Find Keyframes")
        self.keyframesButton.clicked.connect(self.delete_keyframes)
        self.keyframesButton.clicked.connect(self.getKeyframes)
        self.keyframesButton.setEnabled(False)
        self.controlsLayout.addWidget(self.keyframesButton)
        
        # Propogate Button
        self.propagateButton = QPushButton("Propagate Drawn Frames")
        self.propagateButton.clicked.connect(self.startPropagation)
        self.propagateButton.setEnabled(False)
        self.controlsLayout.addWidget(self.propagateButton)
        
        self.outputButton = QPushButton("Convert Propagated Frames to Video")
        self.outputButton.hide()
        self.outputButton.clicked.connect(self.outputVideo)
        self.controlsLayout.addWidget(self.outputButton)
        
        # Add progress bar for frame propagation
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.hide()
        self.mainLayout.addWidget(self.progressBar) 
        
        self.mainLayout.addLayout(self.controlsLayout)
        self.setLayout(self.mainLayout)
        
        # self.frames_menu_button = QToolButton()
        # self.frames_menu_button.setText("Change Frame View")
        # self.frames_menu_button.setPopupMode(QToolButton.InstantPopup)
        # self.frames_menu = QMenu()
        
        # self.view_keyframes_button = QAction("Delete Keyframes", self)
        # self.view_keyframes_button.triggered.connect(self.delete_keyframes)
        # self.frames_menu.addAction(self.view_keyframes_button)
        
        # self.frames_menu_button.setMenu(self.frames_menu)
        # self.mainLayout.addWidget(self.frames_menu_button)
        
        self.option_menu_button = QToolButton()
        self.option_menu_button.setText("Extra Utilities")
        self.option_menu_button.setPopupMode(QToolButton.InstantPopup)
        self.option_menu = QMenu()
                
        self.select_drawn_folder = QAction("Select Drawn Frames Folder", self)
        self.select_drawn_folder.triggered.connect(self.selectDrawnFrame)
        self.option_menu.addAction(self.select_drawn_folder)
        
        self.delete_propagated_button = QAction("Delete Propagated Output Files", self)
        self.delete_propagated_button.triggered.connect(self.delete_output)
        self.option_menu.addAction(self.delete_propagated_button)
        
        self.delete_data_button = QAction("Delete Video Frame Files", self)
        self.delete_data_button.triggered.connect(self.delete_video)
        self.option_menu.addAction(self.delete_data_button)
        
        self.delete_keyframes_button = QAction("Delete Keyframes", self)
        self.delete_keyframes_button.triggered.connect(self.delete_keyframes)
        self.option_menu.addAction(self.delete_keyframes_button)
        
        self.option_menu_button.setMenu(self.option_menu)
        self.mainLayout.addWidget(self.option_menu_button)

    def delete_output(self):
        shutil.rmtree("output")
    def delete_video(self):
        shutil.rmtree("video_data")
    def delete_keyframes(self):
        shutil.rmtree("keyframes")

    def selectDrawnFrame(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder With Frames")
        if folder:
            self.drawn_folder = folder
            # Sort the files numerically - adds some extra wait time though
            self.drawn_frame_files = natsort.natsorted(
                [f for f in os.listdir(folder) if f.endswith('.png') or f.endswith('.jpg')]
            )

    def playVideo(self):
        self.playButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        if not self.isPlaying:
            self.timer.start(30)  # Adjust the frame rate as needed
            self.isPlaying = True

    def stopVideo(self):
        self.playButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.timer.stop()
        self.isPlaying = False

    def selectVideo(self):
        video_file, _ = QFileDialog.getOpenFileName(self, "Select Video File")
        if video_file:
            # Convert video file to frames
            vid2img(video_file)
            
            self.frame_folder = "video_data"
            # Sort the files numerically
            self.frame_files = natsort.natsorted(
                [f for f in os.listdir("video_data") if f.endswith('.png') or f.endswith('.jpg')]
            )
            
            self.current_frame = 0
            self.populateFrameList()
            self.slider.setMaximum(len(self.scene_files[self.current_scene]) - 1)
            self.showNextFrame()
            
            self.flipButtons(True)

    def getKeyframes(self):
        
        self.flipButtons(False)
        checkFolder("keyframes")
        
        self.scene_keyFrames[self.current_scene] = getBestFrame(self.frame_folder,self.scene_files[self.current_scene],30)
        self.keyframeList.clear()
        thumbnailSize = 150  # Desired thumbnail size

        # print(self.scene_keyFrames[self.current_scene])

        for file_path in self.scene_keyFrames[self.current_scene]:
            frame_path = os.path.join(self.frame_folder, file_path)
            
            shutil.copyfile(frame_path, "keyframes/"+ file_path)

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
        
        self.flipButtons(True)
        
    def startPropagation(self):
        self.progressBar.show()
        self.flipButtons(False)
        video = self.frame_folder
        
        drawn = "drawn"
        
        checkFolder("output")
        output = "output"
        
        self.propagationWorker = Worker(propagateScene, video, drawn, output,scene_files = self.scene_files[self.current_scene])
        
        self.propagationWorker.progress_callback.connect(self.updateProgress)
        self.propagationWorker.start()

        self.outputButton.show()
    
    def outputVideo(self):
        self.progressBar.show()
        self.flipButtons(False)
        
        self.outputWorker = Worker(img2vid, "output", "output.avi")
        self.outputWorker.progress_callback.connect(self.updateProgress)
        self.outputWorker.start()
    
    def updateProgress(self, value):
        self.progressBar.setValue(value)
        
        if value >= 100:
            QMessageBox.information(None, "Complete", "Processing complete!")
            #self.progressBar.hide()
            self.flipButtons(True)

    def populateFrameList(self):
        self.frameList.clear()

        changes = detectSceneChanges(self.frame_folder)
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

    def flipButtons(self, enabled):
        # Enable/Disable all buttons
        for button in self.findChildren(QPushButton):
            button.setEnabled(enabled)
        self.slider.setEnabled(enabled)
        self.option_menu_button.setEnabled(enabled)

    def createComboBox(self):
        comboBox = QComboBox()
        comboBox.addItem("Delete Propagated Frames")
        comboBox.addItem("Delete Video Frames ")
        comboBox.addItem("Change Drawn Frame Folder")
        comboBox.currentIndexChanged.connect(self.comboBoxChanged)
        return comboBox

def main():
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.resize(1600, 900)  # Adjust the initial size as needed
    player.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()