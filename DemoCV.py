import base64
import mimetypes
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

load_dotenv()

MODEL = "gpt-4o-mini"
PROMPT = "이 사진의 내용을 자세히 분석해서 한국어로 설명해 주세요."


class AnalyzeThread(QThread):
    finished_ok = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError(".env에 OPENAI_API_KEY가 없습니다.")
            mime = mimetypes.guess_type(self.path)[0] or "image/jpeg"
            with open(self.path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime};base64,{b64}"},
                            },
                        ],
                    }
                ],
            )
            self.finished_ok.emit(resp.choices[0].message.content or "")
        except Exception as e:
            self.failed.emit(str(e))


class Form(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("사진 분석기 (OpenAI Vision)")
        self.resize(700, 700)
        self.image_path = None
        self.worker = None

        self.imageLabel = QLabel("사진을 업로드하세요")
        self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imageLabel.setMinimumHeight(350)
        self.imageLabel.setStyleSheet("border: 1px dashed gray;")

        self.uploadBtn = QPushButton("사진 업로드")
        self.uploadBtn.clicked.connect(self.upload_image)
        self.analyzeBtn = QPushButton("분석하기")
        self.analyzeBtn.setEnabled(False)
        self.analyzeBtn.clicked.connect(self.analyze_image)

        self.resultText = QTextEdit()
        self.resultText.setReadOnly(True)
        self.resultText.setPlaceholderText("분석 결과가 여기에 표시됩니다.")

        layout = QVBoxLayout()
        layout.addWidget(self.imageLabel)
        layout.addWidget(self.uploadBtn)
        layout.addWidget(self.analyzeBtn)
        layout.addWidget(self.resultText)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "사진 선택", "", "Images (*.png *.jpg *.jpeg *.gif *.webp *.bmp)"
        )
        if not path:
            return
        self.image_path = path
        pix = QPixmap(path)
        self.imageLabel.setPixmap(
            pix.scaled(
                600,
                350,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.analyzeBtn.setEnabled(True)
        self.resultText.clear()

    def analyze_image(self):
        if not self.image_path:
            return
        self.analyzeBtn.setEnabled(False)
        self.uploadBtn.setEnabled(False)
        self.resultText.setPlainText("분석 중...")
        self.worker = AnalyzeThread(self.image_path)
        self.worker.finished_ok.connect(self.on_result)
        self.worker.failed.connect(self.on_error)
        self.worker.start()

    def on_result(self, text):
        self.resultText.setPlainText(text)
        self.analyzeBtn.setEnabled(True)
        self.uploadBtn.setEnabled(True)

    def on_error(self, msg):
        self.resultText.clear()
        QMessageBox.critical(self, "오류", msg)
        self.analyzeBtn.setEnabled(True)
        self.uploadBtn.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Form()
    win.show()
    sys.exit(app.exec())
