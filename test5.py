import sys
import numpy as np
import sounddevice as sd
import pyqtgraph as pg
from PyQt6 import QtCore, QtWidgets
from time import perf_counter


# ガイドの呼・吸のRMS
notes = ["In", "Out"]
rms = [-30, -10]

# ガイドメロディーの音階と時間の対応表（適当に設定）
melody_notetime = [["In", 4],
          ["Out", 3],
          ["In", 3],
          ["Out", 4]]
melody = list()
times = list()
time = 0
for note,dulation in melody_notetime:
    melody.append(note)
    times.append(time)
    time += dulation
    melody.append(note)
    times.append(time)        

# ガイドメロディーの周波数と時間の配列に変換
melody_rms = np.array([rms[notes.index(note)] for note in melody])
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
graph.setLabel("left", "音圧レベル", "dB")
graph.setLabel("bottom", "時間", "s")
#graph.setXRange(0, 10) # x軸の範囲を0から10秒に設定
graph.setYRange(-40, 0) # y軸の範囲を0から1000kHzに設定
layout.addWidget(graph)

# ガイドメロディーのプロット
guide = graph.plot(melody_times, melody_rms, pen="g")

# 入力音声のプロット
mic = graph.plot(pen="c")

# 採点結果のラベル
score = QtWidgets.QLabel("採点結果：")
#score.setAlignment(QtCore.Qt.AlignCenter)
layout.addWidget(score)

t = 0
score_ = 0
rms0 = 1
# 音声解析と採点の関数
def analyze():
    global t, score_
    # 入力音声のデータを取得
    data = stream.read(stream.read_available)[0]
    if len(data) == 0:
        return # データがない場合は何もしない
    if t > melody_times[-1]:
        timer.stop()

    data = data.reshape(-1)
    #win = np.hamming(len(data)+1)[:len(data)]
    #data = data * win

    in_rms = np.sqrt(np.mean(data ** 2))
    in_rms = 20 * np.log10(in_rms/rms0) # RMS in [dB]

    # 入力音声のRMSと時間をプロットに追加
    input_rms = mic.yData
    input_times = mic.xData
    if input_times is None:
        input_rms = np.array([in_rms])
        input_times = np.array([t])
    else:
        if len(input_rms) > 2:
            input_rms[-1] = np.mean([input_rms[-2],in_rms]) 
        input_rms = np.append(input_rms, in_rms)
        input_times = np.append(input_times, t)

    # 古いデータを削除する
    #input_rms = input_rms[input_rms > t - 10]
    #input_times = input_times[input_times > t - 10]

    # 入力音声のプロットを更新
    mic.setData(input_times, input_rms)

    # ガイドメロディーの現在のRMSを求める
    guide_rms = np.interp(t, melody_times, melody_rms)

    # 入力音声とガイドメロディーの周波数の差を求める
    diff = np.abs(in_rms - guide_rms)

    # 差が10dB以内なら一致と判定し、採点結果を更新
    if diff < 20:
        score.setText(f"採点結果：{in_rms:.2f} dB,\t{guide_rms:.2f} dB,\t一致！,\t得点:{score_}")
    else:
        score.setText(f"採点結果：{in_rms:.2f} dB,\t{guide_rms:.2f} dB,\t不一致…,\t得点:{score_}")
    score_ += 4/(1+np.exp(diff))-1

    t += timer.interval()/1000

window.show()
name = input('名前を入力してください')
if name:
    # タイマーを作成し、音声解析と採点の関数を定期的に呼び出す
    timer = QtCore.QTimer()
    timer.timeout.connect(analyze)
    timer.start(100) # 1秒ごとに呼び出す

    # マイクからの入力ストリームを作成
    stream = sd.InputStream(samplerate=44100, channels=1)
    stream.start()

    # アプリケーションを実行
    #window.show()
    sys.exit(app.exec())
