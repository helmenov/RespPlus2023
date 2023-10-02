import sys
import numpy as np
import sounddevice as sd
import pyqtgraph as pg
from PyQt6 import QtCore, QtWidgets
from time import perf_counter

# マイクからの入力ストリームを作成
stream = sd.InputStream(samplerate=44100, channels=1)
stream.start()

# ガイドメロディーの音階と周波数の対応表
notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
freqs = [frq/2 for frq in freqs]

# ガイドメロディーの音階と時間の対応表（適当に設定）
melody = ["C4", "E4", "G4", "C5", "G4", "E4", "C4"]
times = [0, 1, 2, 3, 4, 5, 6]

# ガイドメロディーの周波数と時間の配列に変換
melody_freqs = np.array([freqs[notes.index(note)] for note in melody])
melody_times = np.array(times)

# アプリケーションの作成
app = QtWidgets.QApplication(sys.argv)

# ウィンドウの作成
window = QtWidgets.QWidget()
window.setWindowTitle("採点システム")
window.resize(800, 600)

# レイアウトの作成
layout = QtWidgets.QVBoxLayout()
window.setLayout(layout)

# グラフウィジェットの作成
graph = pg.PlotWidget()
graph.setLabel("left", "周波数", "Hz")
graph.setLabel("bottom", "時間", "s")
graph.setXRange(0, 10) # x軸の範囲を0から10秒に設定
graph.setYRange(0, 1000) # y軸の範囲を0から1000Hzに設定
layout.addWidget(graph)

# ガイドメロディーのプロット
guide = graph.plot(melody_times, melody_freqs, pen="g")

# 入力音声のプロット
input = graph.plot(pen="c")

# 採点結果のラベル
score = QtWidgets.QLabel("採点結果：")
#score.setAlignment(QtCore.Qt.AlignCenter)
layout.addWidget(score)

t = 0
# 音声解析と採点の関数
def analyze():
    global t
    # 入力音声のデータを取得
    data = stream.read(stream.read_available)[0]
    if len(data) == 0:
        return # データがない場合は何もしない
    if t > melody_times[-1]:
        timer.stop()

    data = data.reshape(-1)
    win = np.hamming(len(data)+1)[:len(data)]
    data = data * win

    # 現在の時間を取得
    #t = pg.ptime.time()

    # 高速フーリエ変換で周波数成分を求める
    freq = np.fft.rfft(data)[:int(len(data)//2)]
    freq = np.abs(freq) # 振幅スペクトルに変換

    # 周波数軸の値を求める
    f = np.fft.rfftfreq(len(data), d=1.0/44100)

    # 最大振幅の周波数を求める
    max_freq = f[np.argmax(freq)]
    print(max_freq)

    # 入力音声の周波数と時間をプロットに追加
    input_freqs = input.yData
    input_times = input.xData
    if input_times is None:
        input_freqs = np.array([max_freq])
        input_times = np.array([t])
    else:
        input_freqs = np.append(input_freqs, max_freq)
        input_times = np.append(input_times, t)

    # 古いデータを削除する
    input_freqs = input_freqs[input_times > t - 10]
    input_times = input_times[input_times > t - 10]

    # 入力音声のプロットを更新
    input.setData(input_times, input_freqs)

    # ガイドメロディーの現在の周波数を求める
    guide_freq = np.interp(t, melody_times, melody_freqs)

    # 入力音声とガイドメロディーの周波数の差を求める
    diff = np.abs(max_freq - guide_freq)

    # 差が50Hz以内なら一致と判定し、採点結果を更新
    if diff < 50:
        score.setText(f"採点結果：{max_freq:.2f}Hz, {guide_freq:.2f}Hz, 一致！")
    else:
        score.setText(f"採点結果：{max_freq:.2f}Hz, {guide_freq:.2f}Hz, 不一致…")

    t += timer.interval()/1000

# タイマーを作成し、音声解析と採点の関数を定期的に呼び出す
timer = QtCore.QTimer()
timer.timeout.connect(analyze)
timer.start(100) # 100ミリ秒ごとに呼び出す

# アプリケーションを実行
window.show()
sys.exit(app.exec())
