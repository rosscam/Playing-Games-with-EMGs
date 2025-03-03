import numpy as np
import pyusbdux as dux
import scipy.signal as signal
import time
from playwright.sync_api import sync_playwright
import sys
import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow

class IIRfilter:
    #a0 is always 1 so no need to pass it into the class
    def __init__(self, _b0, _b1, _b2, _a1, _a2):
        self.b0 = _b0
        self.b1 = _b1
        self.b2 = _b2
        self.a1 = _a1
        self.a2 = _a2
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0

    def filter(self, input):
        out = self.b0 * input + self.b1 * self.x1 + self.b2 * self.x2 - self.a1 * self.y1 - self.a2 * self.y2
        self.x2 = self.x1
        self.y2 = self.y1
        self.x1 = input
        self.y1 = out
        return out


def character_control(input):
    global jump
    if input > 0.2:
        jump = True

class DataCallback(dux.Callback):
    def __init__(self):
        super().__init__()
        self.previous = time.perf_counter() 
        self.counter = 0
        self.total = 0
    
    def sample_rate(self):
        current_time = time.perf_counter()
        elapsed_time = current_time - self.previous
        self.previous = current_time 
        self.total += elapsed_time
        
        self.counter += 1
        if self.counter == fs:
            avg_sample_time = self.total / fs
            sample_rate = 1 / avg_sample_time
            print(sample_rate)
            self.counter = 0
            self.total = 0

    def hasSample(self, s):
        global raw_signal, filtered
        raw_signal = s[0]
        filtered = filter0.filter(raw_signal)
        filtered = filter1.filter(filtered)
        filtered = filter2.filter(filtered)
        character_control(np.abs(filtered))
        self.sample_rate()
        
class RealTimePlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EMG Trace")
        self.graphWidget = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.graphWidget)

        self.rawPlot = self.graphWidget.addPlot(row=0, col=0, title="Raw Signal")
        self.rawCurve = self.rawPlot.plot(pen='r', name="Raw Signal")

        self.filteredPlot = self.graphWidget.addPlot(row=1, col=0, title="Filtered Signal")
        self.filteredCurve = self.filteredPlot.plot(pen='b', name="Filtered Signal")

        self.raw_data = []
        self.filtered_data = []
        self.time = []
        self.start_time = time.time()

        # Timer for updating the plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(40)

    def update_plot(self):
        global raw_signal, filtered
        current_time = time.time() - self.start_time

        self.time.append(current_time)
        self.raw_data.append(raw_signal)
        self.filtered_data.append(filtered)

        if len(self.raw_data) > 500:
            self.raw_data = self.raw_data[-500:]
            self.filtered_data = self.filtered_data[-500:]
            self.time = self.time[-500:]

        self.rawCurve.setData(self.time, self.raw_data)
        self.filteredCurve.setData(self.time, self.filtered_data)

if __name__ == "__main__":
    # Initialize the Playwright browser
    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://poki.com/en/g/jetpack-joyride?campaign=14345574698&adgroup=126929114300&extensionid=&targetid=dsa-645606693027&location=9046941&matchtype=&network=g&device=c&devicemodel=&creative=604135176409&keyword=&placement=&target=&gad_source=1&gclid=CjwKCAiAmMC6BhA6EiwAdN5iLdG0RTb7bGqWjCRhJwyf_aBNo46xA7htzaj-JkLkaMfW4WriBnOhRBoCFTEQAvD_BwE") 


    fs = 250
    f1 = 45
    f2 = 55
    sosnp = signal.butter(2, [f1/fs*2, f2/fs*2], 'stop', output='sos')

    f3 = 20
    soshp = signal.butter(2, f3/fs*2, 'high', output='sos')

    sos = np.vstack([soshp, sosnp])

    filter0 = IIRfilter(sos[0][0], sos[0][1], sos[0][2], sos[0][4], sos[0][5])
    filter1 = IIRfilter(sos[1][0], sos[1][1], sos[1][2], sos[1][4], sos[1][5])
    filter2 = IIRfilter(sos[2][0], sos[2][1], sos[2][2], sos[2][4], sos[2][5])

    cb = DataCallback()
    dux.open()
    dux.start(cb, 1, fs)

    jump = False
    raw_signal = 0 
    filtered = 0 

    app = QApplication(sys.argv)
    main_window = RealTimePlot()

    def browser_control():
        global jump
        if jump:
            page.keyboard.down('Space')
        else:
            page.keyboard.up('Space')
        jump = False


    control_timer = QTimer()
    control_timer.timeout.connect(browser_control)
    control_timer.start(40) 

    main_window.show()
    sys.exit(app.exec_())

    dux.stop()
