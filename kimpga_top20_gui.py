"""김프가 상위 20개 코인을 QTableWidget에 표시하는 PyQt6 GUI."""

import sys

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from kimpga_top20 import OUTPUT_PATH, crawl_top_coins, save_to_csv


class CrawlWorker(QThread):
    finished_ok = pyqtSignal(list)
    failed = pyqtSignal(str)

    def run(self) -> None:
        try:
            self.finished_ok.emit(crawl_top_coins())
        except Exception as exc:  # 크롤링 오류를 UI에 전달
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("김프가 상위 20개 코인")
        self.resize(900, 650)
        self.rows: list[dict[str, str]] = []
        self.worker: CrawlWorker | None = None

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setAlternatingRowColors(True)

        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.clicked.connect(self.start_crawl)
        self.save_button = QPushButton("CSV 저장")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_csv)
        self.status = QLabel("준비됨")

        buttons = QHBoxLayout()
        buttons.addWidget(self.refresh_button)
        buttons.addWidget(self.save_button)
        buttons.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(buttons)
        layout.addWidget(self.table)
        layout.addWidget(self.status)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.start_crawl()

    def start_crawl(self) -> None:
        self.refresh_button.setEnabled(False)
        self.status.setText("데이터를 가져오는 중...")
        self.worker = CrawlWorker()
        self.worker.finished_ok.connect(self.show_rows)
        self.worker.failed.connect(self.show_error)
        self.worker.start()

    def show_rows(self, rows: list[dict[str, str]]) -> None:
        self.rows = rows
        headers = list(rows[0].keys())
        self.table.clear()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, header in enumerate(headers):
                self.table.setItem(r, c, QTableWidgetItem(row[header]))
        self.table.resizeColumnsToContents()
        self.status.setText(f"총 {len(rows)}개 코인 표시 완료")
        self.refresh_button.setEnabled(True)
        self.save_button.setEnabled(True)

    def show_error(self, message: str) -> None:
        self.status.setText(f"오류: {message}")
        self.refresh_button.setEnabled(True)

    def save_csv(self) -> None:
        save_to_csv(self.rows)
        self.status.setText(f"저장 완료: {OUTPUT_PATH}")


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
