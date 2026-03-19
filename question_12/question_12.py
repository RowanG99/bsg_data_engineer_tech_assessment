import pandas as pd
import numpy as np
from IPython.display import display
from typing import List
import pycountry_convert as pc
import sqlite3
from datetime import datetime

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
#drop_years = list(range(1960, 2006))
#GDP = GDP.drop(columns=drop_years, errors="ignore")
country_names_renamed = {
    "Korea, Rep.":"South Korea",
    "Iran, Islamic Rep.":"Iran",
    "Hong Kong SAR, China":"Hong Kong",
}
GDP["Country Name"] = GDP["Country Name"].replace(country_names_renamed)

ScimEn = pd.read_excel("../journals.xls")

ScimEn_top_15 = ScimEn[ScimEn["Rank"] <= 15]
ScimEn.rename(columns={"Country": "Country Name"}, inplace=True)

ScimEn_energy_merge = pd.merge(ScimEn, energy, how="inner", on="Country Name")
ScimEn_energy_GDP_merge = pd.merge(ScimEn_energy_merge, GDP, how="inner", on="Country Name")

top15_by_renewable = ScimEn_energy_GDP_merge.nlargest(15, "% Renewable")
median_renewable = top15_by_renewable["% Renewable"].median()
ScimEn_energy_GDP_merge["% Renewable Above Top 15 Median"] = (
    ScimEn_energy_GDP_merge["% Renewable"] >= median_renewable
).astype(int)

ScimEn_energy_GDP_merge["RenewableBin"] = pd.cut(
    ScimEn_energy_GDP_merge["% Renewable"], bins=5
)

def alpha3_to_continent(alpha3_code):
    try:
        alpha2_code = pc.country_alpha3_to_country_alpha2(alpha3_code)
        continent_code = pc.country_alpha2_to_continent_code(alpha2_code)
        continent_map = {
            "AF": "Africa",
            "AS": "Asia",
            "EU": "Europe",
            "NA": "North America",
            "SA": "South America",
            "OC": "Oceania",
        }
        return continent_map[continent_code]
    except:
        return "Unknown"

ScimEn_energy_GDP_merge["Continent"] = ScimEn_energy_GDP_merge["Country Code"].apply(alpha3_to_continent)

ScimEn_energy_GDP_merge["RenewableBin"] = pd.cut(
    ScimEn_energy_GDP_merge["% Renewable"], bins=5
)

top15_by_renewable = ScimEn_energy_GDP_merge.nlargest(15, "% Renewable")

group_counts = top15_by_renewable.groupby(["Continent", "RenewableBin"]).size()
print(group_counts)

# ScimEn_energy_GDP_merge.to_excel("merged_with_top15%.xlsx", index=False)

conn = sqlite3.connect("assessment.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS top15_renewable (
    country_name TEXT PRIMARY KEY,
    continent TEXT,
    renewable_bin TEXT,
    percent_renewable REAL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
)
""")

for _, row in top15_by_renewable.iterrows():
    cursor.execute("""
        UPDATE top15_renewable
        SET continent=?, renewable_bin=?, percent_renewable=?, updated_at=?, deleted_at=NULL
        WHERE country_name=?
    """, (row["Continent"], str(row["RenewableBin"]), row["% Renewable"], datetime.now(), row["Country Name"]))

    if cursor.rowcount == 0:
        cursor.execute("""
            INSERT INTO top15_renewable (country_name, continent, renewable_bin, percent_renewable)
            VALUES (?, ?, ?, ?)
        """, (row["Country Name"], row["Continent"], str(row["RenewableBin"]), row["% Renewable"]))

active_countries = tuple(top15_by_renewable["Country Name"].tolist())
cursor.execute(f"""
    UPDATE top15_renewable
    SET deleted_at=?
    WHERE country_name NOT IN ({','.join(['?']*len(active_countries))})
      AND deleted_at IS NULL
""", (datetime.now(), *active_countries))


cursor.execute("""
    WITH ranked as (
     SELECT
       country_name,
       continent,
       percent_renewable,
       ROW_NUMBER() OVER (PARTITION BY continent ORDER BY percent_renewable DESC) as rn
        FROM top15_renewable
        WHERE deleted_at IS NULL
    )
     UPDATE top15_renewable
     SET deleted_at = CURRENT_TIMESTAMP
     WHERE country_name IN (
        SELECT country_name
        FROM ranked
        WHERE rn = 1
        )
     """)

cursor.execute("""
    CREATE VIEW v_top15_renewable_active AS
     SELECT 
        country_name,
        continent,
        renewable_bin,
        percent_renewable,
        inserted_at,
        updated_at
    FROM top15_renewable
    WHERE deleted_at IS NULL
     """)

cursor.execute("SELECT * FROM v_top15_renewable_active")

conn.commit()
conn.close()
