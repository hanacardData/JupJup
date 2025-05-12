import os

SOURCES: list[str] = ["blog", "cafe"]
DATALAB_SOURCE: str = "datalab"
SAVE_PATH: str = "data"
DATA_PATH: str = os.path.join(SAVE_PATH, "data.csv")
TEST_CHANNEL_ID: str = "8895b3b4-1cff-cec7-b7bc-a6df449d3638"
SUBSCRIBE_CHANNEL_IDS: list[str] = [
    "bf209668-eca1-250c-88e6-bb224bf9071a",  # 데이터 사업부
    "bb16f67c-327d-68e3-2e03-4215e67f8eb2",  # 물결님 동기
]
