from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog
from videoThread import VideoThread


class VideoCaptureDialog(QDialog):
    def __init__(self):
        super(VideoCaptureDialog, self).__init__()
        self.setStyleSheet("background:#A5E6D7; color: black;font-weight: bold; font-size: 10pt")

        self.Window = uic.loadUi('ui/videoCaptureDialog.ui', self)
        self.setWindowTitle('Video yakala')

        self.setFixedSize(self.size())

        self.videoThread = VideoThread()
        self.videoThread.changePixmap.connect(self.setImage)
        self.videoThread.setTerminationEnabled(True)

        self.Window.checkBoxEmotion.setVisible(True)
        self.Window.checkBoxAngry.setVisible(False)
        self.Window.checkBoxDisgust.setVisible(False)
        self.Window.checkBoxScared.setVisible(False)
        self.Window.checkBoxHappy.setVisible(False)
        self.Window.checkBoxSad.setVisible(False)
        self.Window.checkBoxSurprised.setVisible(False)
        self.Window.checkBoxNeutral.setVisible(False)
        self.Window.pushButtonStart.setVisible(True)

        self.checkBoxEmotion.stateChanged.connect(self.onEmotionChanged)

    def closeEvent(self, event):
        if self.VideoThread.isRunning():
            self.VideoThread.quit()


    @pyqtSlot()
    def onEmotionChanged(self):
        if self.Window.checkBoxEmotion.isChecked():
            self.Window.checkBoxAngry.setVisible(True)
            self.Window.checkBoxDisgust.setVisible(True)
            self.Window.checkBoxScared.setVisible(True)
            self.Window.checkBoxHappy.setVisible(True)
            self.Window.checkBoxSad.setVisible(True)
            self.Window.checkBoxSurprised.setVisible(True)
            self.Window.checkBoxNeutral.setVisible(True)
        else:
            self.Window.checkBoxAngry.setVisible(False)
            self.Window.checkBoxDisgust.setVisible(False)
            self.Window.checkBoxScared.setVisible(False)
            self.Window.checkBoxHappy.setVisible(False)
            self.Window.checkBoxSad.setVisible(False)
            self.Window.checkBoxSurprised.setVisible(False)
            self.Window.checkBoxNeutral.setVisible(False)

    @pyqtSlot()
    def on_pushButtonStart_clicked(self):
        self.Window.labelVideoFrame.setText('Başlatılıyor, lütfen bekleyin...')



        option_emotions = []
        if self.Window.checkBoxEmotion.isChecked():
            if self.Window.checkBoxAngry.isChecked():
                option_emotions.append(0)
            if self.Window.checkBoxDisgust.isChecked():
                option_emotions.append(1)
            if self.Window.checkBoxScared.isChecked():
                option_emotions.append(2)
            if self.Window.checkBoxHappy.isChecked():
                option_emotions.append(3)
            if self.Window.checkBoxSad.isChecked():
                option_emotions.append(4)
            if self.Window.checkBoxSurprised.isChecked():
                option_emotions.append(5)
            if self.Window.checkBoxNeutral.isChecked():
                option_emotions.append(6)

        self.videoThread.options = {
            'emotions': option_emotions,
        }

        self.videoThread.start()

    @pyqtSlot()
    def on_pushButtonClose_clicked(self):
        self.close()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.Window.labelVideoFrame.setPixmap(QPixmap.fromImage(image))
