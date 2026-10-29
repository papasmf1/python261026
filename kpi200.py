"""네이버 증권 '가격 상위' 코스피 종목 200개를 수집해 kospi200.xlsx로 저장한다.

https://stock.naver.com/market/stock/kr/stocklist/priceTop 페이지는
Next.js 클라이언트 렌더링이라 HTML에 종목 데이터가 없다(BeautifulSoup으로 파싱할 표가 없음).
그래서 페이지가 내부적으로 호출하는 JSON API를 요청하고,
응답이 HTML 조각일 경우를 대비해 BeautifulSoup으로 텍스트를 정리한다.
"""
import requests
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


def main():
    rows = crawl()
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
    wb.save("kospi200.xlsx")

    for i, r in enumerate(rows, 1):
        print(i, r["종목코드"], r["종목명"], r["현재가"], r["등락률(%)"])
    print(f"총 {len(rows)}개 종목 -> kospi200.xlsx")


if __name__ == "__main__":
    main()
