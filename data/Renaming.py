# Renaming the RUN name in plot_data_05.csv
import pandas as pd

naming = pd.read_csv("naming.csv",
                    index_col=["NAME_IN_MODEL"])

df = pd.read_csv("plot_data_05.csv")

# Create a dictionary from the naming DataFrame
naming_dict = naming["NAME"].to_dict()

# Map the values in the DataFrame using the naming dictionary
df["RUN"] = df["RUN"].map(naming_dict)

df.to_csv('plot_data_05.csv')

print (df)