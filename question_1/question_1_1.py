import pandas as pd
import numpy as np
from IPython.display import display

energy = pd.read_excel(
    "../energy_indicators.xls",
    skiprows=17,
    skipfooter=38,
    usecols="C:F"
)


# Some extra cleaning ;)
energy.columns = ["Country", "Energy Supply", "Energy Supply per Capita", "% Renewable"]
energy.replace("...", np.nan, inplace=True)
energy["Energy Supply per Capita"].fillna(np.nan, inplace=True)
energy["Energy Supply"].fillna(np.nan, inplace=True)
energy["Energy Supply"] *= 1000000
energy["% Renewable"] = energy["% Renewable"].round(2)

country_names_renamed = {
    "Republic of Korea":"South Korea",
    "United States of America":"United States",
    "United Kingdom of Great Britain and Northern Ireland":"United Kingdom",
    "China, Hong Kong Special Administrative Region":"Hong Kong",
}

energy["Country"] = energy["Country"].str.replace(r"\d+", "", regex=True)
energy["Country"] = energy["Country"].str.replace(r"\(.*\)", "", regex=True).str.strip()
energy["Country"] = energy["Country"].replace(country_names_renamed)

display(energy.head())
energy.to_excel("cleaned_energy.xlsx", index=False)
