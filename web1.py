# web1.py 
from bs4 import BeautifulSoup

#파일을 로딩(mode를 read text, "wt"-> write text)
page = open("chap09_test.html", "rt", encoding="utf-8").read()
#검색이 용이한 객체 
soup = BeautifulSoup(page, "html.parser")
#전체 보기 
#print(soup.prettify())
#<p>몽땅 검색해 
#print(soup.find_all("p"))
#<a>몽땅 검색해
#print(soup.find_all("a"))
#첫번째<p>만 검색
#print(soup.find("p"))
#조건검색:<p class="outer-text">
#print(soup.find_all("p", class_="outer-text"))
#attrs속성 사용
#print(soup.find_all("p", attrs={"class": "outer-text"}))
#id속성검색 
#print(soup.find_all("p", id="first"))
#태그 내부에 문자열 검색 
for tag in soup.find_all("p"):
    title = tag.text.strip()
    title = title.replace("\n", "")
    print(title)

print("---문자열 처리 메서드---")
data = "<<<   spam ham egg  >>>"
result = data.strip("<> ")
print(data)
print(result)

result = result.replace("spam", "스팸")
print(result)

#리스트로 변환
lst = result.split()
print(lst)

#리스트를 문자열로 변환
result2 = ":)".join(lst)
print(result2)

#정규표현식
import re

result = re.search("[0-9]*th", "35th")
print(result)
print(result.group())

result = re.search("\d{4}", "올해는 2026년입니다.")
print(result)
print(result.group())

result = re.search("apple", "this is apple")
print(result)
print(result.group())

