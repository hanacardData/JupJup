import os

SOURCES: list[str] = ["blog", "cafe"]
DATALAB_SOURCE: str = "datalab"
SAVE_PATH: str = "data"
DATA_PATH: str = os.path.join(SAVE_PATH, "data.csv")
TEST_CHANNEL_ID: str = "8895b3b4-1cff-cec7-b7bc-a6df449d3638"
SUBSCRIBE_CHANNEL_IDS: list[str] = [
    "bf209668-eca1-250c-88e6-bb224bf9071a",  # 데이터 사업부
    "51d15802-cfb6-2e1b-6eb2-c545d2331783",  # CRM 마케팅팀 송치성
    "6a7aa514-55a4-0afd-fd3e-4ed14ec6d81e",  # 트래블로그부 허준회
    "0a7211c1-ae81-e159-55de-7c6d84041508",  # 트래블로그부 허준회
    "749a747c-d3e2-8c28-fc0a-df870e4bfaf5",  # BIZ 운영팀 오지열
    "6a81b6d1-66e2-4da1-d1e0-ccae13d6e26a",  # 직원행복팀 하두선
    "ab53861e-8b62-b64a-7708-5755f1c57259",  # 대구센터 곽승열
    "b0adc6b3-e667-3b5c-9911-29266a39cd25",  # 업무지원부 허지숙
]
