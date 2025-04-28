import pandas as pd

menu_df = pd.read_csv("data/menu.csv")


async def select_random_menu(target: str = "점심") -> dict[str, str]:
    if target not in menu_df.columns:
        target = "점심"
    selected_data = (
        menu_df.loc[~menu_df[target].isna()]
        .groupby("구분")
        .apply(lambda x: x.sample(1))
        .sample(3)
        .reset_index(drop=True)[["구분", "위치", "전화번호", "상호", "메뉴", "가격대"]]
        .to_dict(orient="records")
    )

    result: str = "식당정보를 줍줍했어요!:\n"
    for idx, item in enumerate(selected_data, start=1):
        result += f"{idx}. ###{item.pop('상호')}###\n"
        for key, value in item.items():
            if pd.isna(value):
                continue
            result += f"   - **{key}**: {value}\n"
        result += "\n"
    return result
