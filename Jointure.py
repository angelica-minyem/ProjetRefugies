import pandas as pd

comparaison_url = "https://minio.lab.sspcloud.fr/dchitorog/cepii_clean.parquet"
mixed_url = "https://minio.lab.sspcloud.fr/dchitorog/unhcr_clean.parquet"

df_unhcr = pd.read_parquet(mixed_url)
df_cepii = pd.read_parquet(comparaison_url)

df_unhcr["year"] = df_unhcr["year"].astype(int)
df_cepii["year"] = df_cepii["year"].astype(int)

df_jointure = pd.merge(df_unhcr,df_cepii,
    left_on=["year", "coo_iso", "coa_iso"],
    right_on=["year", "iso3_o", "iso3_d"],
    how="inner",
)

print(df_jointure)