import pandas as pd

# Chargement des bases UNHCR et CEPII nettoyées depuis le stockage Onyxia
cepii_url = "https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/cepii_df.parquet"
unhcr_url = "https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/unhcr_df.parquet"

df_unhcr = pd.read_parquet(unhcr_url)
df_cepii = pd.read_parquet(cepii_url)

# Restriction de l'analyse aux demandeurs d'asile originaires d'Asie du Sud,
# région retenue à l'issue du diagnostic macro préliminaire.
df_unhcr = df_unhcr[df_unhcr["region_origin"] == "Southern Asia"]

# Jointure des données UNHCR et CEPII à partir de l'année,
# du pays d'origine et du pays de destination.
# Une jointure interne est utilisée afin de ne conserver que les couples
# origine-destination présents dans les deux bases.
df_jointure = pd.merge(df_unhcr, df_cepii,
            left_on=["year", "coo_iso", "coa_iso"],
            right_on=["year", "iso3_o", "iso3_d"],
            how="inner").drop(columns=["iso3_o", "iso3_d"])

# Vérification du nombre d'observations avant et après la jointure : pb la jointure rajoute des lignes :(

print(df_unhcr.shape)
print(df_jointure.shape)

