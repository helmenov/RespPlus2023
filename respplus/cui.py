import sounddevice as sd
import numpy as np

DURATION = 10 # record in [s]

def callback(indata, frames:int, time, status):
    """print RMS

    Args:
        indata (_type_): _description_
        frames (int): _description_
        time (_type_): _description_
        status (_type_): _description_
    """
    RMS = np.sqrt(np.mean(indata ** 2))
    print(f'{RMS=}')

def main():
    # 収音
    with sd.InputStream(
        channels = 1,
        dtype = 'float32',
        callback = callback
    ):
        sd.sleep(int(DURATION * 1000))

    # 

if __name__ == '__main__':
    main()
