import sys
import numpy as np
import sounddevice as sd
import pyqtgraph as pg
from PyQt6 import QtCore, QtWidgets

# マイク入力の設定
fs = 44100 # サンプリングレート
duration = 10 # 録音時間（秒）
channels = 1 # チャンネル数

# マイク入力のストリームを作成
stream = sd.InputStream(samplerate=fs, channels=channels)
stream.start() # ストリームを開始

# PyQt5のアプリケーションを作成
app = QtWidgets.QApplication(sys.argv)

# ウィンドウを作成
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('マイク入力音声の解析')
win.resize(800, 600)
win.show()

# プロット領域を作成
plot1 = win.addPlot(title='波形', row=0, col=0)
plot2 = win.addPlot(title='スペクトル', row=1, col=0)

# プロット領域にカーブを追加
curve1 = plot1.plot(pen='y')
curve2 = plot2.plot(pen='c')

# x軸のラベルを設定
plot1.setLabel('bottom', '時間', 's')
plot2.setLabel('bottom', '周波数', 'Hz')

# y軸の範囲を設定
#plot1.setYRange(-1, 1)
plot2.setXRange(20, 4000)
plot2.setYRange(0,10)

# FFTのパラメータ
nfft = 1024 # FFTのサンプル数
window = np.hanning(nfft) # 窓関数（ハニング窓）
overlap = nfft // 2 # オーバーラップのサンプル数

# バッファの初期化
buffer = np.zeros(nfft)
sig = np.zeros(nfft)

# グローバル変数
t = 0 # 経過時間

# タイマーイベント発生時に実行する関数
def update():
    global buffer, t, sig
    # マイク入力のデータを読み込む
    data, overflowed = stream.read(nfft - overlap)
    data = data.reshape(-1) # 1次元配列に変換
    # バッファにデータを追加
    buffer[:-overlap] = buffer[overlap:]
    buffer[-overlap:] = data
    if t == 0:
        sig = data
    else:
        sig = np.r_[sig,data]
    # 窓関数をかける
    windowed = buffer * window
    # FFTを計算
    spectrum = np.fft.rfft(windowed)
    # 振幅スペクトルを計算
    amplitude = np.abs(spectrum)
    # 対数スペクトルを計算
    log_spectrum = 20 * np.log10(amplitude + 1e-12)
    # 経過時間を更新
    t += (nfft - overlap) / fs
    # x軸のデータを生成
    x1 = np.linspace(t, t+ nfft/fs, nfft)
    x11 = np.arange(0, t, 1/fs) # 波形のx軸
    x2 = np.linspace(0, fs / 2, nfft // 2 + 1) # スペクトルのx軸
    # カーブのデータを設定
    #curve1.setData(x=x1, y=buffer)
    curve1.setData(x=x11, y=sig) # 波形のカーブ
    curve2.setData(x=x2, y=log_spectrum) # スペクトルのカーブ

# タイマーを作成
timer = QtCore.QTimer()
timer.timeout.connect(update) # タイマーイベント発生時に実行する関数
timer.start(10) # タイマーを開始（10ミリ秒ごとにイベント発生）

# アプリケーションを実行
sys.exit(app.exec())
