#!/usr/bin/env python3
import os
import sys
import json
from glob import iglob
from itertools import takewhile
from pathlib import Path
from subprocess import Popen, PIPE
from typing import List, Union

from PyQt5.QtCore import QDir, Qt, QUrl, QTime, QFile
from PyQt5.QtGui import QIcon
import PyQt5.QtGui
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSlider,
    QStyle,
    QVBoxLayout,
    QMessageBox,
    QDialog, QTextEdit, QLineEdit,
    QGroupBox, QSpacerItem
)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction
from fire import Fire
from loguru import logger
from printPosition.printPosition import printPosition as printp

#vfpath = None # video file path
#config = {'vdirpath': QDir.homePath()}
config = {'vdirpath': QDir.homePath()+'/0Downloads/JD', 'vfpath': '/home/alex/0Downloads/JD/Contra Force Construct 2 Fun Game 4 players ai - 1 Stage + Boss (720p_30fps_H264-192kbit_AAC).mp4', 'svfpath': '/home/alex/0Downloads/JD/0Contra Force', 'rewind_step': '500'}

class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        self.ss = 0

        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle(f"qtrimvid")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        """
        groupBox = QGroupBox()
        layout = QVBoxLayout()
        groupBox.setLayout(layout)


        self.trimFromInputR = QLineEdit("")

        label = QLabel('3213')
        layout.addWidget(label)
        verticalSpacer = QSpacerItem(10, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addItem(verticalSpacer)

        layout.addWidget(self.trimFromInputR)
        """

        self.positionLabel = QLabel("")
        self.durationLabel = QLabel("")
        rewindStepl = QLabel('Rewind step in ms:')
        self.rewindStepInput = QLineEdit(config['rewind_step']) #QTextEdit
        self.rewindStepInput.setFixedWidth(110)


        self.strimFromInputH = QLineEdit("")
        self.strimFromInputM = QLineEdit("")
        self.strimFromInputS = QLineEdit("")
        #self.strimFromInputS.textChanged.connect(self.mediaChangePosition)
        #self.strimFromInputS.textEdited.connect(self.mediaChangePosition)
        self.strimFromInputM.returnPressed.connect(lambda:self.mediaChangePosition('m'))
        self.strimFromInputS.returnPressed.connect(lambda:self.mediaChangePosition('s'))

        self.strimFromInputMS = QLineEdit("")

        self.etrimInputH = QLineEdit("")
        self.etrimInputM = QLineEdit("")
        self.etrimInputS = QLineEdit("")
        self.etrimInputMS = QLineEdit("")
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Create new action
        openAction = QAction(QIcon("open.png"), "&Open", self)
        openAction.setShortcut("Ctrl+O")
        openAction.setStatusTip("Open video")
        #print(QDir.homePath())
        #print(path)
        #print(config['vdirpath'])#        print(Path(config['vdirpath']))
        #exit(0)
        #openAction.triggered.connect(lambda fileNames=QDir.homePath()+'/0Downloads': self.openFile())
        self.config = config
        #printp(config['vdirpath'])
        #exit(0)
        #openAction.triggered.connect(lambda : self.openFile(self, config['vdirpath']))
        openAction.triggered.connect(self.openFile)

        self.trimFromButton = QPushButton()
        self.trimFromButton.setEnabled(False)
        self.trimFromButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.trimFromButton.setText("Trim from here")
        self.trimFromButton.clicked.connect(self.trimFrom)

        trimFromAction = QAction(QIcon("start.png"), "&Trim from here", self)
        trimFromAction.setShortcut("Ctrl+s")
        trimFromAction.setStatusTip("Trim from here")
        trimFromAction.triggered.connect(self.trimFrom)

        self.trimToButton = QPushButton()
        self.trimToButton.setEnabled(False)
        self.trimToButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.trimToButton.setText("Trim to here")
        self.trimToButton.clicked.connect(self.trimTo)

        trimToAction = QAction(QIcon("end.png"), "&Trim to here", self)
        trimToAction.setShortcut("Ctrl+e")
        trimToAction.setStatusTip("Trim to here")
        trimToAction.triggered.connect(self.trimTo)

        # Create exit action
        exitAction = QAction(QIcon("exit.png"), "&Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit application")
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        actionsMenu = menuBar.addMenu("&Trims")
        # fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
        actionsMenu.addAction(trimFromAction)
        actionsMenu.addAction(trimToAction)

        # Create toolbar for quick actions
        self.openFileButton = QPushButton()
        self.openFileButton.setIcon(self.style().standardIcon(QStyle.SP_FileDialogStart))
        self.openFileButton.clicked.connect(lambda:self.openFile(config['vdirpath'], False))
        self.openLastFileButton = QPushButton()
        self.openLastFileButton.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        self.openLastFileButton.clicked.connect(lambda:self.openFile(None, config['vfpath']))

        fileToolBar = self.addToolBar("File")
        #fileToolBar.addWidget(self.fontSizeSpinBox)
        fileToolBar.addWidget(self.openFileButton)
        fileToolBar.addWidget(self.openLastFileButton)
        fileToolBar.addWidget(rewindStepl)
        fileToolBar.addWidget(self.rewindStepInput)

        #rverticalSpacer = QSpacerItem(False, -15, QSizePolicy.Minimum, QSizePolicy.Minimum)
        #fileToolBar.addWidget(rverticalSpacer)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionLabel)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addWidget(self.durationLabel)
        #controlLayout.addWidget(self.trimFromInputH)

        #controlLayout.addWidget(verticalSpacer)

        #controlLayout.addWidget(groupBox)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        verticalSpacer = QSpacerItem(False, -15, QSizePolicy.Minimum, QSizePolicy.Minimum)

        layout.addItem(verticalSpacer)

        controlLayout2 = QHBoxLayout()
        controlLayout2.setContentsMargins(0, 0, 0, 0)

        controlLayout2.addWidget(self.trimFromButton)

        controlLayout2.addWidget(self.strimFromInputH)
        controlLayout2.addWidget(QLabel(":"))
        controlLayout2.addWidget(self.strimFromInputM)
        controlLayout2.addWidget(QLabel(":"))
        controlLayout2.addWidget(self.strimFromInputS)
        controlLayout2.addWidget(QLabel(":"))
        controlLayout2.addWidget(self.strimFromInputMS)

        controlLayout2.addWidget(self.etrimInputH)
        controlLayout2.addWidget(QLabel(":"))
        controlLayout2.addWidget(self.etrimInputM)
        controlLayout2.addWidget(QLabel(":"))
        controlLayout2.addWidget(self.etrimInputS)
        controlLayout2.addWidget(QLabel(":"))
        controlLayout2.addWidget(self.etrimInputMS)

        controlLayout2.addWidget(self.trimToButton)

        layout.addLayout(controlLayout2)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self, fileNames: Union[List[Path], Path]): # dirPath,
        #printp(self.config['vdirpath']) exit(0) print(dirPath) print(fileNames)
        if not fileNames:
            fileNames, _ = QFileDialog.getOpenFileNames(
                self, "Open File", self.config['vdirpath'] #dirPath#QDir.homePath()
            )

        printp(fileNames) #return

        if fileNames:
            if not isinstance(fileNames, list):
                fileNames = [fileNames]
            self.mediaPlayer.stop()
            self.playlist = QMediaPlaylist()
            for fileName in fileNames:
                self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
                config['vfpath'] = fileName
                fn = os.path.basename(fileName)

            self.playlist.setCurrentIndex(0)
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
            self.mediaPlayer.setPlaylist(self.playlist)
            self.playButton.setEnabled(True)
            self.trimToButton.setEnabled(True)
            self.trimFromButton.setEnabled(True)
            #self.setWindowTitle(f" qtrimvid - {self.mediaPlayer.currentMedia().canonicalUrl().toString()}")
            self.setWindowTitle(f" qtrimvid: - {fn}")
            #self.play()

    def exitCall(self):
        sys.exit(app.exec_())

    def trim(self, vfpath, ss=0, t=None):
        #print(path)
        printp(ss)
        printp(t)
        if vfpath == None:
            return
        printp(ss)
        printp(t)
        printp(vfpath) # tmp_path = f"{vfpath}.tmp{os.path.splitext(vfpath)[1]}"

        fn_setted = False
        count = 0
        while fn_setted != True:
            if count == 0:
                tmp_path = f"{os.path.splitext(config['vfpath'])[0]}_trimmed{os.path.splitext(config['vfpath'])[1]}"
            else:
                tmp_path = f"{os.path.splitext(config['vfpath'])[0]}_trimmed_{count}{os.path.splitext(config['vfpath'])[1]}"
            count += 1
            if not os.path.isfile(tmp_path):
                fn_setted = True
        printp(tmp_path)

        # p = wProcess()
        par = [
            "ffmpeg", "-y", "-i", vfpath,# "-ss", str(ss),
            *(["-ss", str(ss)] if ss != 0 else []),
            *(["-t", str(t)] if t is not None else []),
            "-vcodec", "copy", "-acodec", "copy",
            tmp_path,
        ]
        printp(par)
        self.mediaPlayer.pause()
        #return exit(0)
        p = Popen(par, stderr=PIPE, stdout=PIPE)


        '''if p.wait() == 0:
            logger.info(p.stdout.read().decode())
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.config['vdirpath']) #QDir.homePath() , initialFilter='*.mp4'
            if fileName:
                os.rename(tmp_path, fileName)
                self.openFile(fileName)
        else:
            err_text = p.stderr.read().decode()
            logger.error(err_text)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText(err_text)
            msg.setWindowTitle("Error")
            msg.exec_()
            os.unlink(tmp_path)'''

    def trimFrom(self):
        position = self.mediaPlayer.position()
        printp(position)
        h = str(int((position / 3600000) % 24))
        self.strimFromInputH.setText(h)
        m = str(int((position / 60000) % 60))
        self.strimFromInputM.setText(m)

        s = int((position / 1000) % 60)
        printp(s)
        self.ss = s
        self.strimFromInputS.setText(str(s))
        ms = str(position/1000)
        ms = ms.split('.')[1].lstrip('0')
        self.strimFromInputMS.setText(ms)
        #print(str(ms-int(ms))[1:])
       # print(self.strimFromInputH.setText)
        return
        p = int(self.mediaPlayer.position() / 1000)
        self.trim(
            self.mediaPlayer.currentMedia()
            .canonicalUrl()
            .toString()
            .replace("file://", ""),
            ss=p,
        )

    def trimTo(self):
        #print(self.ss) #return
        position = self.mediaPlayer.position() #position = int(self.mediaPlayer.position() / 1000)
        printp(position)
        h = str(int((position / 3600000) % 24))
        self.etrimInputH.setText(h)
        m = str(int((position / 60000) % 60))
        self.etrimInputM.setText(m)

        s = int((position / 1000) % 60)
        printp(s)
        self.etrimInputS.setText(str(s))
        ms = str(position/1000)
        ms = ms.split('.')[1].lstrip('0')
        self.etrimInputMS.setText(ms)

        self.trim(
            self.mediaPlayer.currentMedia()
            .canonicalUrl()
            .toString()
            .replace("file://", ""),
            ss=self.ss,
            t=s-self.ss,
        )

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def mediaChangePosition(self, input):
        print(input)
        print(input)
        return
        self.positionSlider.setValue(position)
        self.positionLabel.setText(
            QTime(
                int((position / 3600000)) % 24,
                int((position / 60000)) % 60,
                int((position / 1000)) % 60,
            ).toString()
        )

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        self.positionLabel.setText(
            QTime(
                int((position / 3600000)) % 24,
                int((position / 60000)) % 60,
                int((position / 1000)) % 60,
            ).toString()
        )


    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        self.durationLabel.setText(f"{duration/1000}")
        self.durationLabel.setText(
            QTime(
                int((duration / 3600000)) % 24,
                int((duration / 60000)) % 60,
                int((duration / 1000)) % 60,
            ).toString()
        )

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.trimToButton.setEnabled(False)
        self.trimFromButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.inp = QLineEdit()
        self.label = QLabel()
        self.inp.textChanged.connect(self.onTextChanged)

        layout.addWidget(self.inp)
        layout.addWidget(self.label)
        self.show()
    def onTextChanged(self, text):
        if text:
            l = list(filter(os.path.isfile, iglob(os.path.expanduser(text))))
            self.label.setText('\n'.join(l[:20]) + f'{len(l)} total' if len(l)>=20 else '')




app = QApplication(sys.argv)


def main(*path: List[Path]):
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    if path:
        player.openFile(path)
    sys.exit(app.exec_())


if __name__ == "__main__":
    Fire(main)
