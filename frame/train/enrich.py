import holidays
import pandas as pd


def add_holidays(
    df: pd.DataFrame, colname: str = "date", outname: str = "is_holiday"
) -> pd.DataFrame:
    ar_holidays = holidays.AR()
    df[outname] = df[colname].apply(ar_holidays.__contains__)
    return df
