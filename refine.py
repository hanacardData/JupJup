import pandas as pd


def refine_data(data: pd.DataFrame) -> pd.DataFrame:
    return data.loc[data["is_posted"] == 0]  # FIXME: 물결님 헤엎-!
