import sys
import serial
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLineEdit, QTextEdit, QLabel)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSlot, QObject, QThread, pyqtSignal
import matplotlib.pyplot as plt

class runThread (QObject):

    end = pyqtSignal ()
    start = pyqtSignal()
    plot = pyqtSignal()
    displayText = pyqtSignal (str)
    global fig, ax, xs, ys
    xs = []
    ys = []

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.runner = True  # provide a bool run condition for the class


    def work (self):
        count = 0
        self.runner = True
        if ser.is_open is not True:  # Check the serial port again whether it is open or not.
            ser.open()
        while(self.runner):
            signal = ser.readline().decode('utf-8')
            signal2 =  signal.replace('\r\n', '')
            self.displayText.emit(signal)
            count = count + 1
            if ((signal2.find('B')== -1) and (signal2.find('\n')== -1) and (signal2.find('C')== -1) and (len(signal2) > 0 ) and (len(signal2) < 5 )  ) :
                signal3 = int(signal2)
                ys.append(signal3)
                xs.append(count)
            if (signal2.find('B') != -1) :
                self.runner = False


    def stop (self):
        self.plot.emit()
        self.end.emit()
        ser.close()


class SerialUI(QMainWindow):

    global ser
    global bpm
    global samplingrate
    global serialcmd
    ser = serial.Serial()
    global flag
    flag = True
    wrong = 0
    stopper = pyqtSignal()
    starter = pyqtSignal()

    def __init__(self):
        super(SerialUI,self).__init__()
        self.InitUI()

    def InitUI(self):
        # QMainWindow settings
        self.setWindowTitle('Heart Monitor')
        self.setStyleSheet("background-color: beige")
        self.setGeometry(10, 10, 1100, 750)
        self.move(500, 300)

        # Create push button
        self.b1 = QPushButton('Start', self)
        self.b1.move(350, 650)
        self.b1.setStyleSheet("background-color: white")
        self.b1.clicked.connect(self.start_call)


        self.b2 = QPushButton('BPM', self)
        self.b2.move(500, 650)
        self.b2.setStyleSheet("background-color: white")
        self.b2.clicked.connect(self.get_bpm)

        self.b3 = QPushButton('Plot', self)
        self.b3.move(650, 650)
        self.b3.setStyleSheet("background-color: white")

        self.lb5 = QLabel(self)
        self.lb5.resize(100, 50)
        self.lb5.move(10, 50)
        self.lb5.setText("COMPORT:")

        # Create textbox
        self.tb1 = QLineEdit(self)  # COMPORT
        self.tb1.resize(150,70)
        self.tb1.setStyleSheet("background-color: white")
        self.tb1.move(100,50)

        self.lb6 = QLabel(self)
        self.lb6.resize(100, 50)
        self.lb6.move(260, 50)
        self.lb6.setText("BAUDRATE:")

        self.tb2 = QLineEdit(self)  # BAUDRATE
        self.tb2.resize(150, 70)
        self.tb2.setStyleSheet("background-color: white")
        self.tb2.move(360, 50)

        self.lb7 = QLabel(self)
        self.lb7.resize(130, 50)
        self.lb7.move(520, 50)
        self.lb7.setText("SAMPLINGRATE:")

        # Create textbox
        self.tb4 = QLineEdit(self)  # Sampling Rate
        self.tb4.resize(150, 70)
        self.tb4.setStyleSheet("background-color: white")
        self.tb4.move(650, 50)

        self.lb8 = QLabel(self)
        self.lb8.resize(130, 50)
        self.lb8.move(810, 50)
        self.lb8.setText("SAMPLINGTIME:")

        # Create textbox
        self.tb5 = QLineEdit(self)  # Time
        self.tb5.resize(150, 70)
        self.tb5.setStyleSheet("background-color: white")
        self.tb5.move(940, 50)

        # Create label
        self.lb1 = QLabel(self)
        self.lb1.setFont(QFont('SansSerif', 15))
        self.lb1.setStyleSheet("color: black")
        self.lb1.resize(200,50)
        self.lb1.move(300,160)
        self.lb1.setText("Terminal:")

        self.tb3 = QTextEdit(self)
        self.tb3.setFont(QFont('SansSerif', 15))
        self.tb3.setStyleSheet("color: black")
        self.tb3.setStyleSheet("background-color: white")
        self.tb3.resize(500, 400)
        self.tb3.move(300, 230)


        self.thread = QThread()
        self.worker = runThread ()
        self.stopper.connect(self.worker.stop)
        self.worker.plot.connect(self.plot)
        self.worker.moveToThread(self.thread)
        #self.worker.end.connect(self.thread.quit)
        #self.worker.end.connect(self.worker.deleteLater)
        #self.worker.end.connect(self.thread.deleteLater)
        self.worker.displayText.connect(self.display)
        self.thread.started.connect(self.worker.work)
        #self.thread.finished.connect(self.worker.stop)
        self.b3.clicked.connect(self.stop_call)
        self.starter.connect (self.worker.start)
        self.show()

    def stop_call(self):
        self.stopper.emit()


    def get_bpm(self):
        self.tb3.append("BPM: " +self.bpm)

    def display(self,heart):
        if (heart != "") :
            if heart[0] != "B":
                self.tb3.append(heart)
            else:
                self.bpm= heart[5:-2]

    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(xs, ys)
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.30)
        plt.title('Heart Beat')
        plt.ylabel('ECG Output')
        plt.ylabel('Count')
        plt.show()





    @pyqtSlot()
    def start_call(self):
        xs.clear()
        ys.clear()
        # # Serial settings
        ser.close()
        try :
            self.thread.terminate()
        except :
            ser.close()
        try:
            ser.port = self.tb1.text()
            ser.baudrate = self.tb2.text()

            if ser.is_open is not True:  # Check the serial port again whether it is open or not.
                ser.open()

            try:
                serialcmd = self.tb5.text()
                userInput = int(serialcmd)
                for x in range(len(serialcmd)):
                    ser.write(serialcmd[x].encode())
                ser.write("\r".encode())

                self.samplingrate = self.tb4.text()
                serialcmd = self.samplingrate
                userInput = int(serialcmd)
                for x in range(len(serialcmd)):
                    ser.write(serialcmd[x].encode())
                ser.write("\r".encode())
                self.thread.setTerminationEnabled(True)
                self.thread.start()
            except ValueError:
                self.tb3.append("Invalid Sampling Rate")
        except :
            self.tb3.append("Invalid Serial Port")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SerialUI()
    sys.exit(app.exec_())