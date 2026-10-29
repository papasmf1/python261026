import sys
from BikeManager import BikeManager
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QAbstractItemView, QHeaderView,
)

STYLE = """
QWidget {
    background-color: #1e1e2f;
    color: #f0f0f5;
    font-family: 'Malgun Gothic', 'Segoe UI';
    font-size: 14px;
}
QLabel#title {
    font-size: 26px;
    font-weight: bold;
    color: #ffffff;
    padding: 12px;
    border-radius: 12px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ff512f, stop:1 #dd2476);
}
QLabel { background: transparent; font-weight: bold; color: #ffb86c; }
QLineEdit {
    background-color: #2b2b45;
    border: 2px solid #44446a;
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: #dd2476;
}
QLineEdit:focus { border: 2px solid #ff79c6; }
QLineEdit:read-only { background-color: #25253b; color: #888aa8; }
QPushButton {
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 10px;
    padding: 9px 16px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #667eea, stop:1 #764ba2);
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #8fa2ff, stop:1 #9b6bd1);
}
QPushButton:pressed { background: #4b3a8a; padding-top: 11px; }
QPushButton#add { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #11998e, stop:1 #38ef7d); }
QPushButton#edit { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f7971e, stop:1 #ffd200); color: #222; }
QPushButton#delete { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #cb2d3e, stop:1 #ef473a); }
QPushButton#search { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2193b0, stop:1 #6dd5ed); }
QPushButton#add:hover, QPushButton#edit:hover,
QPushButton#delete:hover, QPushButton#search:hover { border: 2px solid white; }
QTableWidget {
    background-color: #25253b;
    alternate-background-color: #2d2d4a;
    border: 2px solid #44446a;
    border-radius: 10px;
    gridline-color: #3a3a5c;
    selection-background-color: #dd2476;
    selection-color: white;
}
QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
    color: white;
    font-weight: bold;
    padding: 8px;
    border: none;
}
QScrollBar:vertical { background: #25253b; width: 12px; border-radius: 6px; }
QScrollBar::handle:vertical { background: #667eea; border-radius: 6px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""

BUTTON_NAMES = {"입력": "add", "수정": "edit", "삭제": "delete", "검색": "search"}


class BikeProductApp(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = BikeManager()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("자전거용품 관리")
        self.resize(640, 560)
        self.setStyleSheet(STYLE)

        title = QLabel("🚴 자전거용품 관리")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.id_edit = QLineEdit()
        self.id_edit.setReadOnly(True)
        self.id_edit.setPlaceholderText("자동 생성")
        self.name_edit = QLineEdit()
        self.price_edit = QLineEdit()

        form = QGridLayout()
        form.addWidget(QLabel("ID"), 0, 0)
        form.addWidget(self.id_edit, 0, 1)
        form.addWidget(QLabel("이름"), 1, 0)
        form.addWidget(self.name_edit, 1, 1)
        form.addWidget(QLabel("가격"), 2, 0)
        form.addWidget(self.price_edit, 2, 1)

        buttons = QHBoxLayout()
        for text, slot in (("입력", self.add_item), ("수정", self.update_item),
                           ("삭제", self.delete_item), ("검색", self.search_item),
                           ("전체보기", self.load_data)):
            btn = QPushButton(text)
            btn.setObjectName(BUTTON_NAMES.get(text, ""))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(slot)
            buttons.addWidget(btn)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "이름", "가격"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellClicked.connect(self.on_row_selected)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self.table)

    def read_inputs(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "오류", "이름을 입력하세요.")
            return None
        try:
            price = int(self.price_edit.text().strip())
        except ValueError:
            QMessageBox.warning(self, "오류", "가격은 정수로 입력하세요.")
            return None
        return name, price

    def clear_inputs(self):
        self.id_edit.clear()
        self.name_edit.clear()
        self.price_edit.clear()

    def fill_table(self, rows):
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(value)))

    def load_data(self):
        self.fill_table(self.manager.get_all())

    def on_row_selected(self, row, _col):
        self.id_edit.setText(self.table.item(row, 0).text())
        self.name_edit.setText(self.table.item(row, 1).text())
        self.price_edit.setText(self.table.item(row, 2).text())

    def add_item(self):
        data = self.read_inputs()
        if data is None:
            return
        self.manager.add(*data)
        self.clear_inputs()
        self.load_data()

    def update_item(self):
        if not self.id_edit.text():
            QMessageBox.warning(self, "오류", "수정할 행을 선택하세요.")
            return
        data = self.read_inputs()
        if data is None:
            return
        self.manager.update(int(self.id_edit.text()), *data)
        self.clear_inputs()
        self.load_data()

    def delete_item(self):
        if not self.id_edit.text():
            QMessageBox.warning(self, "오류", "삭제할 행을 선택하세요.")
            return
        if QMessageBox.question(self, "확인", "삭제하시겠습니까?") != QMessageBox.StandardButton.Yes:
            return
        self.manager.delete(int(self.id_edit.text()))
        self.clear_inputs()
        self.load_data()

    def search_item(self):
        keyword = self.name_edit.text().strip()
        self.fill_table(self.manager.search(keyword))

    def closeEvent(self, event):
        self.manager.close()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BikeProductApp()
    win.show()
    sys.exit(app.exec())
