import pandas as pd
import numpy as np
from IPython.display import display
from typing import List


energy = pd.read_excel(
    "../energy_indicators.xls",
    skiprows=17,
    skipfooter=38,
    usecols="C:F"
)

energy.columns = ["Country", "Energy Supply", "Energy Supply per Capita", "% Renewable"]
energy.rename(columns={"Country": "Country Name"}, inplace=True)
energy.replace("...", np.nan, inplace=True)
energy["Energy Supply per Capita"] = energy["Energy Supply per Capita"].fillna(np.nan)
energy["Energy Supply"] = energy["Energy Supply"].fillna(np.nan)
energy["Energy Supply"] *= 1000000
energy["% Renewable"] = energy["% Renewable"].round(2)
country_names_renamed = {
    "Republic of Korea":"South Korea",
    "United States of America":"United States",
    "United Kingdom of Great Britain and Northern Ireland":"United Kingdom",
    "China, Hong Kong Special Administrative Region":"Hong Kong",
}
energy["Country Name"] = energy["Country Name"].str.replace(r"\d+", "", regex=True)
energy["Country Name"] = energy["Country Name"].str.replace(r"\(.*\)", "", regex=True).str.strip()
energy["Country Name"] = energy["Country Name"].replace(country_names_renamed)

GDP = pd.read_excel(
    "../world_bank.xls",
    skiprows=4
)
drop_years = list(range(1960, 2006))
GDP = GDP.drop(columns=drop_years, errors="ignore")
country_names_renamed = {
    "Korea, Rep.":"South Korea",
    "Iran, Islamic Rep.":"Iran",
    "Hong Kong SAR, China":"Hong Kong",
}
GDP["Country Name"] = GDP["Country Name"].replace(country_names_renamed)

ScimEn = pd.read_excel("../journals.xls")

#ScimEn = ScimEn[ScimEn["Rank"] <= 15]
ScimEn.rename(columns={"Country": "Country Name"}, inplace=True)

ScimEn_energy_merge = pd.merge(ScimEn, energy, how="inner", on="Country Name")
ScimEn_energy_GDP_merge = pd.merge(ScimEn_energy_merge, GDP, how="inner", on="Country Name")

energy_countries = set(energy["Country Name"])
gdp_countries = set(GDP["Country Name"])
scimen_countries = set(ScimEn["Country Name"])
union_countries = energy_countries | gdp_countries | scimen_countries
intersection_count = ScimEn_energy_GDP_merge["Country Name"].nunique()
rows_lost = len(union_countries) - intersection_count
print("Rows lost due to merge:", rows_lost)

def calc_lost_rows_all(energy: pd.DataFrame, GDP: pd.DataFrame, ScimEn: pd.DataFrame) -> int:
    merged_all = pd.merge(pd.merge(ScimEn, energy, how="inner", on="Country Name"),
                          GDP, how="inner", on="Country Name")   
    energy_countries = set(energy["Country Name"])
    gdp_countries = set(GDP["Country Name"])
    scimen_countries = set(ScimEn["Country Name"])
    union_countries = energy_countries | gdp_countries | scimen_countries
    intersection_count = merged_all["Country Name"].nunique()
    rows_lost = len(union_countries) - intersection_count
    
    return rows_lost

lost_data = calc_lost_rows_all(energy=energy, GDP=GDP, ScimEn=ScimEn)
print(lost_data)

