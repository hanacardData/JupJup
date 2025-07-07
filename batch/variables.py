import os

SOURCES: list[str] = ["blog", "cafe"]
DATALAB_SOURCE: str = "datalab"
SAVE_PATH: str = "data"
EXTRACTED_DATA_COUNT: int = 100
DATA_PATH: str = os.path.join(SAVE_PATH, "data.csv")
TRAVELLOG_DATA_PATH: str = os.path.join(SAVE_PATH, "travellog_data.csv")
COMPARE_TRAVEL_DATA_PATH: str = os.path.join(SAVE_PATH, "compare_travel_data.csv")
TEST_CHANNEL_ID: str = "8895b3b4-1cff-cec7-b7bc-a6df449d3638"

# 트래블로그UX부 우수현
TRAVELLOG_CHANNEL_ID: str = "59fc2740-d582-8072-4c63-add08f331dda"

# 트래블로그 비교 채널
COMPARE_TRAVEL_CHANNEL_ID: str = "5d12d31b-baa8-b92f-ad6b-1e0ef2642e5d"

SUBSCRIBE_CHANNEL_IDS: list[str] = [
    "bf209668-eca1-250c-88e6-bb224bf9071a",  # 데이터 사업부
    "51d15802-cfb6-2e1b-6eb2-c545d2331783",  # CRM 마케팅팀 송치성
    "6a7aa514-55a4-0afd-fd3e-4ed14ec6d81e",  # 트래블로그부 허준회
    "0a7211c1-ae81-e159-55de-7c6d84041508",  # 트래블로그부 허준회
    "749a747c-d3e2-8c28-fc0a-df870e4bfaf5",  # BIZ 운영팀 오지열
    "6a81b6d1-66e2-4da1-d1e0-ccae13d6e26a",  # 직원행복팀 하두선
    "ab53861e-8b62-b64a-7708-5755f1c57259",  # 대구센터 곽승열
    "b0adc6b3-e667-3b5c-9911-29266a39cd25",  # 업무지원부 허지숙
    "0ad1869f-18d0-ccca-418e-c2dbfcfb3d92",  # 디지털본부 박상준
    "1d344ebb-a0b5-c044-5454-51f390bad4e9",  # 손님케어센터 서정은
    "26a62def-63c3-7023-e08e-10610bc97e96",  # 감사부 이정욱
    "8e1d14fb-535d-174e-35f6-3a5b7cdd7bfe",  # 발급팀 조복엽
    "599dab73-3c5a-91ef-3925-2187d8ba3e87",  # 하나페이사업부 서지은
    "115639965",  # 감사부 이명주
    "8c81a639-960d-4e0e-2626-5773f3dd3486",  # 손님관리부 백호선
]
