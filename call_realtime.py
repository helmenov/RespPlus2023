#%%
import sounddevice as sd
import numpy as np
from matplotlib import pyplot as plt

#%% 収音しながら，関数呼び出し
def callback_input(indata, frames, time, status):
    print(f'RMS = {RMS(indata)}')

def RMS(indata):
    return np.sqrt(np.mean(indata ** 2))

DURATION = 10
with sd.InputStream(channels = 1, dtype = 'float32', callback = callback_input):
    sd.sleep(DURATION * 1000) # スリープというより，この時間内にcallbackが働く

#%% 再生しながら，関数呼び出し
# いまいちよくわからない
def callback_output(outdata, frames, time, status):
    print(f'{outdata.shape=},{frames=}')

DURATION = 10
with sd.OutputStream(channels=2,dtype='float32',callback=callback_output):
    sd.sleep(DURATION * 1000)

# %%
def callback_io(indata, outdata, frames, time, status):
    outdata = indata[::-1]

DURATION = 10
with sd.Stream(channels=1, dtype='float32',callback=callback_io):
    sd.sleep(int(DURATION * 1000))

# %%
