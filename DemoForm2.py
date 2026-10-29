# DemoForm2.py 
# DemoForm2.ui(화면단) + DemoForm2.py(로직단)
import sys 
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic
#웹크롤링을 위한 선언
from bs4 import BeautifulSoup
#웹서버에 요청
import urllib.request 
#정규표현식
import re

#화면을 로딩(파일명 변경)
form_class = uic.loadUiType("DemoForm2.ui")[0]

#폼클래스 정의(상속받는 부모 클래스를 QMainWindow로 변경)
class DemoForm(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label.setText("PyQt6 사용하기")
    #슬롯메서드 추가
    def firstClick(self):
        f = open("clien.txt", "wt", encoding="utf-8")
        hdr = {'User-Agent': 'Mozilla/5.0'}
        for i in range(0,10):
            url = "https://www.clien.net/service/board/sold?&od=T31&category=0&po=" + str(i)
            print(url)    
            #요청객체 생성
            req = urllib.request.Request(url, headers=hdr)
            page = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(page, 'html.parser')
            #매물 정보 추출 
            items = soup.find_all('span', attrs={'data-role': 'list-title-text'})
            for item in items:
                title = item.text.strip() 
                #화면에 있는 입력 문자열
                search = self.lineEdit.text()
                if re.search(search, title):
                    print(title)
                    f.write(title + "\n")
        #파일 닫기
        f.close()
        self.label.setText("클리앙 중고 장터 크롤링완료")
    def secondClick(self):
        self.label.setText("두 번째 버튼 클릭!!")
    def thirdClick(self):
        self.label.setText("세 번째 버튼 클릭했음")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = DemoForm()
    demo.show()
    app.exec()