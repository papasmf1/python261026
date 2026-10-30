"""컬리 상품 후기 300개 수집 -> pandas 감성 분석 -> matplotlib 막대 그래프"""
import time

import matplotlib.pyplot as plt
import pandas as pd
import requests

PRODUCT_NO = 5026468
MAX_REVIEWS = 300
API_URL = f"https://api.kurly.com/product-review/v4/contents-products/{PRODUCT_NO}/reviews"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.kurly.com/"}

POSITIVE_WORDS = ["맛있", "맛남", "최고", "만족", "좋아", "좋았", "좋네", "좋은", "추천", "재구매",
                  "부드럽", "연해", "깔끔", "신선", "푸짐", "든든", "훌륭", "굿", "맑", "깊"]
NEGATIVE_WORDS = ["별로", "실망", "아쉬", "짜", "싱거", "비싸", "질기", "냄새", "비린", "느끼",
                  "불만", "최악", "후회", "부족", "적어", "적네", "불편", "퍽퍽", "딱딱", "맛없"]


def fetch_reviews(limit=MAX_REVIEWS):
    rows, after = [], None
    while len(rows) < limit:
        params = {"sortType": "RECOMMEND"}
        if after:
            params["after"] = after
        res = requests.get(API_URL, headers=HEADERS, params=params, timeout=10)
        res.raise_for_status()
        data = res.json().get("data") or {}
        reviews = data.get("reviews") or []
        for r in reviews:
            rows.append({"no": r["no"], "date": r["registeredAt"], "contents": r["contents"]})
        after = (data.get("nextCursor") or {}).get("after")
        if not reviews or not after:
            break
        time.sleep(0.3)
    return pd.DataFrame(rows).drop_duplicates("no").head(limit).reset_index(drop=True)


def classify(text):
    pos = sum(w in text for w in POSITIVE_WORDS)
    neg = sum(w in text for w in NEGATIVE_WORDS)
    if pos > neg:
        return "긍정"
    if neg > pos:
        return "부정"
    return "중립"


def main():
    df = fetch_reviews()
    print(f"수집한 후기 수: {len(df)}")
    df.to_csv("kurly_reviews.csv", index=False, encoding="utf-8-sig")

    df["sentiment"] = df["contents"].apply(classify)
    counts = df["sentiment"].value_counts().reindex(["긍정", "부정", "중립"], fill_value=0)
    print(counts)

    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False
    ax = counts.plot(kind="bar", color=["#4CAF50", "#F44336", "#9E9E9E"], rot=0)
    for i, v in enumerate(counts):
        ax.text(i, v, str(v), ha="center", va="bottom")
    ax.set_title("컬리 [사미헌] 갈비탕 후기 감성 분석")
    ax.set_xlabel("의견")
    ax.set_ylabel("후기 수")
    plt.tight_layout()
    plt.savefig("kurly_sentiment.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
