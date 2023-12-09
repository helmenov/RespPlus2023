import sys
import numpy as np
import sounddevice as sd
import pyqtgraph as pg
from PyQt6 import QtCore, QtWidgets
from time import perf_counter
import pandas as pd

df = pd.read_csv('pattern.csv')
melody_noteperiod = df.values.tolist()
# ガイドメロディーの音階と時間の対応表（適当に設定）
#melody_noteperiod = [["In", 4],
#          ["Out", 3],
#          ["In", 3],
#          ["Out", 4]]
t = 0
q = 0
maxq = 50
guide_n = list()
guide_q = list()
guide_t = list()
for note,period in melody_noteperiod:
    mperiod = 1000*period
    if note == "In":
        dq = maxq/mperiod
    elif note == "Out":
        dq = -maxq/mperiod
    elif note == "Stay":
        dq = 0
    for _ in range(mperiod):
        guide_n.append(note)
        guide_q.append(q)
        guide_t.append(t)
        q += dq
        t += 1/1000
guide_n.append(note)
guide_q.append(q)
guide_t.append(t)
guide_q = np.array(guide_q)
guide_t = np.array(guide_t)

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
graph.setLabel("left", "呼吸パターン", "")
graph.setLabel("bottom", "時間", "s")
graph.showGrid(x=True,y=False,alpha=0.5)
#graph.setXRange(0, 10) # x軸の範囲を0から10秒に設定
#graph.setYRange(-40, 0) # y軸の範囲を0から1000kHzに設定
layout.addWidget(graph)

# ガイドメロディーのプロット
guide = graph.plot(guide_t, guide_q, pen="g")

# 入力音声のプロット
mic = graph.plot(pen="c")

# 採点結果のラベル
score = QtWidgets.QLabel("採点結果：")
#score.setAlignment(QtCore.Qt.AlignCenter)
layout.addWidget(score)

t = 0
score_ = 0
in_crms = 0
silence = 0
rest_crms = None
weight = 0
# 音声解析と採点の関数
def analyze():
    global t, score_, in_crms, silence, rest_crms, weight
    # 入力音声のデータを取得
    data = stream.read(stream.read_available)[0]
    if len(data) == 0:
        return # データがない場合は何もしない

    data = data.reshape(-1)
    if t == 0:
        silence = np.sqrt(np.mean(data ** 2))
        in_rms = 0
    else:
        in_rms = np.max([0, np.sqrt(np.mean(data ** 2)) - silence])

    if t > guide_t[-1]:
        timer.stop()
        return

    if guide_q[int(np.round(t*1000))] < (1e-3):
        score_ += int(weight*100*np.exp(-in_crms))
        score.setText(f'採点結果: {score_}点')
        in_crms = 0
    if guide_q[int(np.round(t*1000))] > maxq - (1e-3):
        weight = in_crms

    if guide_n[int(np.round(t*1000))] == "In":
        in_crms += 10*in_rms
    elif guide_n[int(np.round(t*1000))] == "Out":
        in_crms -= in_rms
    elif guide_n[int(np.round(t*1000))] == "Stay":
        pass

    # 入力音声のRMSと時間をプロットに追加
    input_crms = mic.yData
    input_times = mic.xData
    if input_times is None:
        input_crms = np.array([in_crms])
        input_times = np.array([t])
    else:
        if len(input_crms) > 2:
            input_crms[-1] = np.mean([input_crms[-2],in_crms])
        input_crms = np.append(input_crms, in_crms)
        input_times = np.append(input_times, t)

    # 古いデータを削除する
    #input_rms = input_rms[input_rms > t - 10]
    #input_times = input_times[input_times > t - 10]

    # 入力音声のプロットを更新
    mic.setData(input_times, input_crms)



    t += timer.interval()/1000


print(sd.query_devices())
dev_i = int(input(">"))
dev_o = int(input("<"))
sd.default.device = [dev_i, dev_o]
# マイクからの入力ストリームを作成
stream = sd.InputStream(samplerate=44100, channels=1)

name = input('名前を入力してください')
if name:
    window.show()
    # タイマーを作成し、音声解析と採点の関数を定期的に呼び出す
    timer = QtCore.QTimer()
    timer.timeout.connect(analyze)
    timer.start(10) # 10msごとに呼び出す

    stream.start()

    # アプリケーションを実行
    #window.show()
    sys.exit(app.exec())
