from datetime import datetime, timedelta

from google_play_scraper import Sort, reviews

hanamoney_id = "kr.co.hanamembers.hmscustomer"
hanacard_id = "com.hanaskcard.paycla"
langs = ["ko", "en"]


def get_app_reviews() -> tuple[list[str], list[str]]:
    hanamoney_results = []
    hanapay_results = []

    for lang in langs:
        _hanamoney_results, _ = reviews(
            hanamoney_id,
            lang=lang,
            country="kr",
            sort=Sort.NEWEST,
            count=20,
        )
        _hanapay_results, _ = reviews(
            hanacard_id,
            lang=lang,
            country="kr",
            sort=Sort.NEWEST,
            count=20,
        )
        hanamoney_results.extend(_hanamoney_results)
        hanapay_results.extend(_hanapay_results)

    hanamoney_results = set(
        [
            r["content"]
            for r in hanamoney_results
            if r["at"] >= datetime.now() - timedelta(days=3) and len(r["content"]) > 10
        ]
    )
    hanapay_results = set(
        [
            r["content"]
            for r in hanapay_results
            if r["at"] >= datetime.now() - timedelta(days=3) and len(r["content"]) > 10
        ]
    )
    return list(hanamoney_results), list(hanapay_results)


if __name__ == "__main__":
    hanamoney_reviews, hanapay_reviews = get_app_reviews()

    if hanamoney_reviews:
        print("하나머니 최신 앱 리뷰입니다:")
        for review in hanamoney_reviews:
            print(review)

    if hanapay_reviews:
        print("하나페이 최신 앱 리뷰입니다:")
        for review in hanapay_reviews:
            print(review)
