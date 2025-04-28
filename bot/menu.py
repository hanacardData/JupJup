import pandas as pd

menu_df = pd.read_csv("data/menu.csv")


async def select_random_menu(target: str = "점심") -> dict[str, str]:
    if target not in menu_df.columns:
        target = "점심"
    return (
        menu_df.loc[menu_df[target] != ""]
        .groupby("구분", group_keys=False)
        .apply(lambda x: x.sample(1))
        .sample(3)
        .reset_index(drop=True)
        .to_dict(orient="records")
    )
