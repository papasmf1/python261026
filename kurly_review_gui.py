"""PyQt6 GUI: 왼쪽 후기 리스트 / 오른쪽 감성 분석 막대 차트"""
import sys

import matplotlib
matplotlib.use("QtAgg")
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QListWidget,
                             QListWidgetItem, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)

from kurly_review_analysis import classify, fetch_reviews

COLORS = {"긍정": "#4CAF50", "부정": "#F44336", "중립": "#9E9E9E"}


class CrawlThread(QThread):
    done = pyqtSignal(pd.DataFrame)
    failed = pyqtSignal(str)

    def run(self):
        try:
            df = fetch_reviews()
            df["sentiment"] = df["contents"].apply(classify)
            self.done.emit(df)
        except Exception as e:
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("컬리 후기 감성 분석")
        self.resize(1200, 650)
        self.thread_ = None

        self.status = QLabel("'후기 수집' 버튼을 눌러주세요.")
        self.button = QPushButton("후기 수집 (300개)")
        self.button.clicked.connect(self.start)
        self.list = QListWidget()
        self.list.setWordWrap(True)
        self.fig = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.fig)

        left = QVBoxLayout()
        left.addWidget(QLabel("후기 목록"))
        left.addWidget(self.list)
        right = QVBoxLayout()
        right.addWidget(QLabel("감성 분석 차트"))
        right.addWidget(self.canvas)
        body = QHBoxLayout()
        body.addLayout(left, 1)
        body.addLayout(right, 1)

        root = QVBoxLayout()
        top = QHBoxLayout()
        top.addWidget(self.button)
        top.addWidget(self.status, 1)
        root.addLayout(top)
        root.addLayout(body)
        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

    def start(self):
        self.button.setEnabled(False)
        self.status.setText("수집 중... 잠시만 기다려주세요.")
        self.thread_ = CrawlThread()
        self.thread_.done.connect(self.show_result)
        self.thread_.failed.connect(self.show_error)
        self.thread_.start()

    def show_error(self, msg):
        self.status.setText(f"오류: {msg}")
        self.button.setEnabled(True)

    def show_result(self, df):
        self.list.clear()
        for _, r in df.iterrows():
            text = r["contents"].replace("\n", " ")
            item = QListWidgetItem(f"[{r['sentiment']}] {text[:150]}")
            item.setForeground(QColor(COLORS[r["sentiment"]]))
            item.setToolTip(r["contents"])
            self.list.addItem(item)

        counts = df["sentiment"].value_counts().reindex(["긍정", "부정", "중립"], fill_value=0)
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.bar(counts.index, counts.values, color=[COLORS[k] for k in counts.index])
        for i, v in enumerate(counts.values):
            ax.text(i, v, str(v), ha="center", va="bottom")
        ax.set_title("후기 감성 분석")
        ax.set_ylabel("후기 수")
        self.fig.tight_layout()
        self.canvas.draw()

        self.status.setText(f"후기 {len(df)}개 수집 완료")
        self.button.setEnabled(True)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
