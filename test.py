#%%
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import sounddevice as sd
import numpy as np

app = pg.mkQApp("app")
win = pg.GraphicsLayoutWidget(show=True,title="win")
win.setWindowTitle("Real-time sound analysis")
p = win.addPlot(title='pen plot')
curve = p.plot(pen='c')

fs = 44100
chunk = 512
data = np.zeros(chunk)

def callback(indata, frames, time, status):
    global curve, data, app
    if status: print(status)
    data = indata[:,0]
    data = data/32768
    rms = np.sqrt(np.mean(data ** 2))
    print(f'{rms=}')
    curve.setData(data)
    pg.show()


with sd.InputStream(samplerate=fs, dtype='float32', blocksize=chunk, channels=1, callback=callback):
    sd.sleep(3*1000)

if __name__ == '__main__':
    pg.exec()
# %%
