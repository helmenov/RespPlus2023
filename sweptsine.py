from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

app = pg.mkQApp("App")
win = pg.GraphicsLayoutWidget(show=True, title="basic")
win.resize(500,500)
win.setWindowTitle('pyqtgraph example: 1D-Plot')
pg.setConfigOptions(antialias=True)

p = win.addPlot(title='real-time line plot')
curve = p.plot(pen='c')

fps = 60
n_samples = 500
fo = 1
data = np.zeros(n_samples)

iter = 0
def update():
    global curve, data, iter, fps, fo, n_samples

    fo = 0.1 + iter / n_samples
    t = (1.0 / fps) * iter
    idx = iter % n_samples
    data[idx] = np.sin(2.0 * np.pi * fo * t)
    pos = idx + 1 if idx < n_samples else 0
    curve.setData(np.r_[data[pos:n_samples], data[0:pos]])
    iter += 1

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(int(1/fps * 1000))

if __name__ == '__main__':
    pg.exec()
