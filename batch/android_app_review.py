from datetime import datetime, timedelta

from google_play_scraper import Sort, reviews

hanamoney_id = "kr.co.hanamembers.hmscustomer"
hanacard_id = "com.hanaskcard.paycla"
langs = ["ko", "en"]


def get_app_reviews() -> tuple[set[str], set[str]]:
    hanamoney_results = []
    hanapay_results = []

    for lang in langs:
        _hanamoney_results, _ = reviews(
            hanamoney_id,
            lang=lang,
            country="kr",
            sort=Sort.NEWEST,
            count=10,
        )
        _hanapay_results, _ = reviews(
            hanacard_id,
            lang=lang,
            country="kr",
            sort=Sort.NEWEST,
            count=10,
        )
        hanamoney_results.extend(_hanamoney_results)
        hanapay_results.extend(_hanapay_results)

    hanamoney_results = set(
        [
            r["content"]
            for r in hanamoney_results
            if r["at"] >= datetime.now() - timedelta(days=1)
        ]
    )
    hanapay_results = set(
        [
            r["content"]
            for r in hanapay_results
            if r["at"] >= datetime.now() - timedelta(days=1)
        ]
    )
    return hanamoney_results, hanapay_results
