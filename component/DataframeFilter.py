# Filtering out rows that don't match the condition
import pandas as pd

def dataframe_processing(csv_file, column_name, condition):
    df = pd.read_csv(csv_file, header = 0)
    filtered_df = df[df[column_name].apply(condition)]
    return filtered_df
