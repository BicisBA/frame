import holidays
import pandas as pd


def add_holidays(
    df: pd.DataFrame, colname: str = "ts", outname: str = "is_holiday"
) -> pd.DataFrame:
    ar_holidays = holidays.AR()
    df[outname] = df[colname].dt.date.apply(ar_holidays.__contains__)
    return df
