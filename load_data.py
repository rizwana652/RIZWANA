# utils/load_data.py
import pandas as pd
from typing import Optional

def load_data(path: Optional[str] = "application_train.csv") -> pd.DataFrame:
    """
    Load and return the application_train CSV as a DataFrame.
    Provide full path if the CSV is not in the current working directory.
    """
    return pd.read_csv(path)
