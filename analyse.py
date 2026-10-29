import pandas as pd

# Chargement des bases UNHCR et CEPII nettoyées depuis le stockage Onyxia
cepii_url = "https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/cepii_df.parquet"
unhcr_url = "https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/unhcr_df.parquet"

df_unhcr = pd.read_parquet(unhcr_url)
df_cepii = pd.read_parquet(cepii_url)

# Restriction de l'analyse aux demandeurs d'asile originaires d'Asie du Sud,
# région retenue à l'issue du diagnostic macro préliminaire.
df_unhcr = df_unhcr[df_unhcr["region_origin"] == "Southern Asia"].drop(
                    columns = "region_origin")

# Jointure des données UNHCR et CEPII à partir de l'année,
# du pays d'origine et du pays de destination.

south_asia = pd.merge(df_unhcr, df_cepii,
            left_on=["year", "coo_iso", "coa_iso"],
            right_on=["year", "iso3_o", "iso3_d"],
            how="inner").drop(columns=["iso3_o", "iso3_d"])

# Vérification du nombre d'observations avant et après la jointure : pb la jointure rajoute des lignes :(

print(df_unhcr.shape)
print(south_asia.shape)


# -------------------------------------------------------------------

# Nombre total de réfugiés par pays d'origine et par année,
# toutes destinations confondues.
refugees_by_origin = south_asia.groupby(["year", "coo_name"])["refugees"].sum().reset_index().rename(
                                            columns={"refugees": "total_refugees_origin"})


# Ajout du nombre total de réfugiés correspondant à chaque pays d'origine
# et chaque année dans la base principale.
south_asia = south_asia.merge(refugees_by_origin, on=["year", "coo_name"])

# Calcul de la part des réfugiés présente dans chaque pays de destination.
south_asia["destination_share"] = south_asia["refugees"]/south_asia["total_refugees_origin"]

# Suppression de la variable intermédiaire devenue inutile.
south_asia = south_asia.drop(columns="total_refugees_origin")

# Sélection des variables nécessaires à l'analyse de la répartition
# des réfugiés entre les différents pays de destination.
refugee_destination_shares = south_asia[["year", "coo_name", "coa_name", "destination_share"]]
