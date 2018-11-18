from .helpers import *
from .report_functions import *


def print_df(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)
