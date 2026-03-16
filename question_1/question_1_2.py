import pandas as pd
import numpy as np
from IPython.display import display

GDP = pd.read_excel(
    "../world_bank.xls",
    skiprows=4
)

country_names_renamed = {
    "Korea, Rep.":"South Korea",
    "Iran, Islamic Rep.":"Iran",
    "Hong Kong SAR, China":"Hong Kong",
}

GDP["Country Name"] = GDP["Country Name"].replace(country_names_renamed)

display(GDP.head())
GDP.to_excel("cleaned_world_bank.xlsx", index=False)

