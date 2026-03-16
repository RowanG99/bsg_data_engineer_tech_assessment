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

def gdp_change_for_6th_country(GDP: pd.DataFrame) -> tuple:
    year_cols = list(range(1960, 2016))
    cols_to_use = ["Country Name"] + year_cols
    GDP_years = GDP[cols_to_use].copy()
    GDP_years["avg_gdp"] = GDP_years[year_cols].mean(axis=1)
    sorted_gdp = GDP_years.sort_values("avg_gdp", ascending=False)
    sixth_country = sorted_gdp.iloc[5]
    country_name = sixth_country["Country Name"]
    gdp_change = sixth_country[2015] - sixth_country[2006]
    percentage_change = (gdp_change / sixth_country[2006]) * 100

    print(f"6th largest average GDP country: {country_name}")
    print(f"GDP in 2006: {sixth_country[2006]}")
    print(f"GDP in 2015: {sixth_country[2015]}")
    print(f"Absolute change (2006–2015): {gdp_change}")
    print(f"Percentage change (2006–2015): {percentage_change:.2f}%")

    return country_name, gdp_change, percentage_change

res = gdp_change_for_6th_country(GDP=GDP)
