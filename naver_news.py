import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

SEARCH_URL = "https://search.naver.com/search.naver"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
    )
}
MAX_ARTICLES = 5

NEWS_CONTAINER_SELECTOR = ".fds-news-item-list-desk"
ARTICLE_LINK_SELECTOR = 'a[href*="n.news.naver.com/mnews/article/"]'
TITLE_SELECTOR = ".sds-comps-text-type-headline1"
SUMMARY_SELECTOR = ".sds-comps-text-type-body1"
BODY_SELECTORS = ("#dic_area", "#newsct_article", "#articleBodyContents")
OUTPUT_PATH = Path(__file__).with_name("naver_result.xlsx")


def fetch_soup(
    url: str, params: dict[str, str] | None = None
) -> BeautifulSoup:
    response = requests.get(
        url, params=params, headers=HEADERS, timeout=15
    )
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_text(element: Tag | None, separator: str = " ") -> str:
    if element is None:
        return ""
    return element.get_text(separator, strip=True)


def get_news_items(soup: BeautifulSoup) -> list[tuple[str, str, str]]:
    news_container = soup.select_one(NEWS_CONTAINER_SELECTOR)
    if news_container is None:
        return []

    items: list[tuple[str, str, str]] = []
    seen_urls: set[str] = set()

    for link in news_container.select(ARTICLE_LINK_SELECTOR):
        url = link.get("href")
        if not isinstance(url, str) or url in seen_urls:
            continue

        title = ""
        summary = ""
        parent = link.parent
        while isinstance(parent, Tag) and parent is not news_container:
            title_element = parent.select_one(TITLE_SELECTOR)
            summary_element = parent.select_one(SUMMARY_SELECTOR)
            if title_element is not None and summary_element is not None:
                title = get_text(title_element)
                summary = get_text(summary_element)
                break
            parent = parent.parent

        items.append((url, title, summary))
        seen_urls.add(url)
        if len(items) >= MAX_ARTICLES:
            break

    return items


def get_article_body(soup: BeautifulSoup) -> str:
    for selector in BODY_SELECTORS:
        element = soup.select_one(selector)
        if element is not None:
            for unwanted in element.select("script, style, .reporter_info, .byline"):
                unwanted.decompose()
            return get_text(element, separator="\n")
    return ""


def save_to_excel(
    rows: list[tuple[int, str, str, str, str]], path: Path
) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "네이버 뉴스"
    worksheet.append(["번호", "제목", "요약", "기사 URL", "본문"])

    for row in rows:
        worksheet.append(row)

    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions
    for column, width in {"A": 8, "B": 45, "C": 60, "D": 65, "E": 100}.items():
        worksheet.column_dimensions[column].width = width
    for row in worksheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    workbook.save(path)


def main() -> None:
    search_soup = fetch_soup(
        SEARCH_URL,
        params={
            "where": "nexearch",
            "sm": "top_hty",
            "fbm": "0",
            "ie": "utf8",
            "query": "반도체",
        },
    )
    news_items = get_news_items(search_soup)

    if not news_items:
        print("네이버 뉴스 결과를 찾지 못했습니다.")
        return

    results: list[tuple[int, str, str, str, str]] = []
    for index, (url, search_title, summary) in enumerate(news_items, start=1):
        article_soup = fetch_soup(url)

        title = get_text(
            article_soup.select_one(
                "h2#title_area, h2.media_end_head_headline"
            )
        )
        if not title:
            title_tag = article_soup.select_one('meta[property="og:title"]')
            if title_tag is not None:
                title = str(title_tag.get("content", "")).strip()
        if not title:
            title = search_title or "제목을 찾지 못했습니다."

        body = get_article_body(article_soup)

        results.append((index, title, summary, url, body))
        print(f"\n[{index}] {title}")
        print(url)
        if summary:
            print(f"검색 결과 요약: {summary}")
        print(body or "본문을 찾지 못했습니다.")
        time.sleep(1)

    save_to_excel(results, OUTPUT_PATH)
    print(f"\n엑셀 파일 저장 완료: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
