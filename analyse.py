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

#Problème:les données du CEPII (et donc la jointure) contiennent des doublons. Les copies comportent un grand nombre de 
#données manquantes. Afin de nettoyer le base de données, création de la variable na_count, qui contient le nombre de 
#données manquantes dans chaque ligne:

south_asia["na_count"] = south_asia.isna().sum(axis=1)

#L'original sera alors la ligne contenant le moins de données manquantes. Tri des lignes par les colonnes "year", "coo_iso",
# "coa_iso", puis par na_count. La ligne la plus complète sera alors positionnée en premier.

south_asia = south_asia.sort_values(
    by=["year", "coo_iso", "coa_iso", "na_count"]
)

#On retire alors les doublons incomplets.

south_asia = south_asia.drop_duplicates(subset=["year", "coo_iso", "coa_iso"], keep='first')

#On retire la colonne na_count, désormais inutile.

south_asia = south_asia.drop(columns="na_count")

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
