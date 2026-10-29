"""김프가 홈페이지 표의 상위 20개 코인 정보를 CSV로 저장한다."""

import csv
import re
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://kimpga.com/"
TOP_N = 20
WAIT_SECONDS = 30
OUTPUT_PATH = Path(__file__).with_name("kimpga_top20.csv")
TABLE_SELECTOR = "table"
ROW_SELECTOR = "tbody tr"


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def crawl_top_coins() -> list[dict[str, str]]:
    driver = webdriver.Chrome()
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, WAIT_SECONDS)
        wait.until(
            lambda browser: len(
                browser.find_elements(
                    By.CSS_SELECTOR, f"{TABLE_SELECTOR} {ROW_SELECTOR}"
                )
            )
            >= TOP_N
        )

        table = driver.find_element(By.CSS_SELECTOR, TABLE_SELECTOR)
        headers = [
            normalize_text(header.text)
            for header in table.find_elements(By.CSS_SELECTOR, "thead th")
        ]
        if not headers:
            raise RuntimeError("코인 표의 열 이름을 찾지 못했습니다.")

        rows = table.find_elements(By.CSS_SELECTOR, ROW_SELECTOR)
        results: list[dict[str, str]] = []
        for rank, row in enumerate(rows[:TOP_N], start=1):
            values = [
                normalize_text(cell.text)
                for cell in row.find_elements(By.TAG_NAME, "td")
            ]
            if len(values) != len(headers):
                raise RuntimeError(
                    f"{rank}번째 행의 열 개수가 표 헤더와 일치하지 않습니다."
                )
            results.append({"순위": str(rank), **dict(zip(headers, values))})

        return results
    finally:
        driver.quit()


def save_to_csv(rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError("저장할 코인 데이터가 없습니다.")

    fieldnames = list(rows[0].keys())
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = crawl_top_coins()
    save_to_csv(rows)

    for row in rows:
        print(
            f"{row['순위']}. {row['이름']} | "
            f"현재가: {row['현재가']} | 김프: {row['김프']}"
        )
    print(f"\n총 {len(rows)}개 코인 저장 완료: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
