"""네이버 증권 '가격 상위' 코스피 종목 200개를 수집해 kospi200.xlsx로 저장한다.

https://stock.naver.com/market/stock/kr/stocklist/priceTop 페이지는
Next.js 클라이언트 렌더링이라 HTML에 종목 데이터가 없다(BeautifulSoup으로 파싱할 표가 없음).
그래서 페이지가 내부적으로 호출하는 JSON API를 요청하고,
응답이 HTML 조각일 경우를 대비해 BeautifulSoup으로 텍스트를 정리한다.
"""
import sys

import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QMainWindow,
    QMessageBox, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Font

API_URL = "https://m.stock.naver.com/api/stocks/priceTop/KOSPI"
HEADERS = {"User-Agent": "Mozilla/5.0"}
PAGE_SIZE = 100
TARGET = 200

FIELDS = [
    ("itemCode", "종목코드"),
    ("stockName", "종목명"),
    ("closePrice", "현재가"),
    ("compareToPreviousClosePrice", "전일비"),
    ("fluctuationsRatio", "등락률(%)"),
    ("accumulatedTradingVolume", "거래량"),
    ("accumulatedTradingValueKrwHangeul", "거래대금"),
    ("marketValueHangeul", "시가총액"),
]


def clean(value):
    return BeautifulSoup(str(value), "html.parser").get_text(strip=True)


def fetch_page(page):
    res = requests.get(
        API_URL,
        params={"page": page, "pageSize": PAGE_SIZE},
        headers=HEADERS,
        timeout=10,
    )
    res.raise_for_status()
    return res.json()["stocks"]


def crawl(target=TARGET):
    rows = []
    page = 1
    while len(rows) < target:
        stocks = fetch_page(page)
        if not stocks:
            break
        for s in stocks:
            if s.get("stockEndType") != "stock":  # ETF/ETN 등 제외
                continue
            item = {label: clean(s.get(key, "")) for key, label in FIELDS}
            direction = s.get("compareToPreviousPrice", {}).get("name", "")
            if direction == "FALLING":
                item["전일비"] = "-" + item["전일비"]
                item["등락률(%)"] = "-" + item["등락률(%)"].lstrip("-")
            rows.append(item)
            if len(rows) == target:
                break
        page += 1
    return rows


def save_excel(rows, path="kospi200.xlsx"):
    labels = [label for _, label in FIELDS]
    wb = Workbook()
    ws = wb.active
    ws.title = "KOSPI200"
    ws.append(labels)
    for r in rows:
        ws.append([r[label] for label in labels])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for col in ws.columns:
        width = max(len(str(c.value or "")) for c in col)
        ws.column_dimensions[col[0].column_letter].width = width + 4
    ws.freeze_panes = "A2"
    wb.save(path)


STYLE = """
QMainWindow, QWidget#central { background: #f4f6fb; }
QLabel { color: #2d3748; font-size: 13px; }
QLabel#title { font-size: 22px; font-weight: bold; color: #1a365d; }
QLabel#subtitle { color: #718096; font-size: 12px; }
QSpinBox {
    background: white; border: 1px solid #cbd5e0; border-radius: 6px;
    padding: 5px 8px; min-width: 80px;
}
QSpinBox:focus { border: 1px solid #3182ce; }
QPushButton {
    background: #3182ce; color: white; border: none; border-radius: 6px;
    padding: 8px 18px; font-size: 13px; font-weight: bold;
}
QPushButton:hover { background: #2b6cb0; }
QPushButton:pressed { background: #2c5282; }
QPushButton:disabled { background: #cbd5e0; color: #f7fafc; }
QPushButton#save { background: #38a169; }
QPushButton#save:hover { background: #2f855a; }
QPushButton#save:disabled { background: #cbd5e0; }
QTableWidget {
    background: white; alternate-background-color: #edf2f7;
    border: 1px solid #e2e8f0; border-radius: 8px;
    gridline-color: transparent; selection-background-color: #bee3f8;
    selection-color: #1a365d; font-size: 13px;
}
QHeaderView::section {
    background: #2c5282; color: white; padding: 8px; border: none;
    font-weight: bold;
}
QStatusBar { background: #e2e8f0; color: #2d3748; }
QScrollBar:vertical { background: #f4f6fb; width: 10px; }
QScrollBar::handle:vertical { background: #a0aec0; border-radius: 5px; }
"""
UP_COLOR = QColor("#e53e3e")
DOWN_COLOR = QColor("#3182ce")


class CrawlThread(QThread):
    done = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, target):
        super().__init__()
        self.target = target

    def run(self):
        try:
            self.done.emit(crawl(self.target))
        except Exception as e:
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KOSPI 가격 상위 종목 크롤러")
        self.resize(900, 600)
        self.rows = []
        self.thread_ = None

        self.spin = QSpinBox()
        self.spin.setRange(1, 1000)
        self.spin.setValue(TARGET)
        self.btn_crawl = QPushButton("크롤링 시작")
        self.btn_save = QPushButton("엑셀 저장")
        self.btn_save.setObjectName("save")
        self.btn_save.setEnabled(False)
        for b in (self.btn_crawl, self.btn_save):
            b.setCursor(Qt.CursorShape.PointingHandCursor)

        title = QLabel("📈 KOSPI 가격 상위 종목")
        title.setObjectName("title")
        subtitle = QLabel("네이버 증권 데이터를 수집해 표로 보고 엑셀로 저장합니다")
        subtitle.setObjectName("subtitle")

        top = QHBoxLayout()
        top.addWidget(QLabel("종목 수:"))
        top.addWidget(self.spin)
        top.addWidget(self.btn_crawl)
        top.addWidget(self.btn_save)
        top.addStretch()

        self.table = QTableWidget(0, len(FIELDS))
        self.table.setHorizontalHeaderLabels([l for _, l in FIELDS])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        central = QWidget()
        central.setObjectName("central")
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 16, 20, 12)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(top)
        layout.addWidget(self.table)
        self.setCentralWidget(central)
        self.statusBar().showMessage("준비")

        self.btn_crawl.clicked.connect(self.start_crawl)
        self.btn_save.clicked.connect(self.save)

    def start_crawl(self):
        self.btn_crawl.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.statusBar().showMessage("크롤링 중...")
        self.thread_ = CrawlThread(self.spin.value())
        self.thread_.done.connect(self.on_done)
        self.thread_.failed.connect(self.on_failed)
        self.thread_.start()

    def on_done(self, rows):
        self.rows = rows
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j, (_, label) in enumerate(FIELDS):
                item = QTableWidgetItem(r[label])
                if j >= 2:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                if label in ("전일비", "등락률(%)"):
                    if r[label].startswith("-"):
                        item.setForeground(DOWN_COLOR)
                    elif r[label].strip("0.,") != "":
                        item.setForeground(UP_COLOR)
                self.table.setItem(i, j, item)
        self.btn_crawl.setEnabled(True)
        self.btn_save.setEnabled(bool(rows))
        self.statusBar().showMessage(f"총 {len(rows)}개 종목 수집 완료")

    def on_failed(self, msg):
        self.btn_crawl.setEnabled(True)
        self.statusBar().showMessage("실패")
        QMessageBox.critical(self, "오류", msg)

    def save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "엑셀 저장", "kospi200.xlsx", "Excel (*.xlsx)"
        )
        if not path:
            return
        try:
            save_excel(self.rows, path)
        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))
            return
        self.statusBar().showMessage(f"저장 완료: {path}")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Malgun Gothic", 10))
    app.setStyleSheet(STYLE)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
