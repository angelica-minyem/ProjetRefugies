import pandas as pd

# Chargement des données UNHCR nettoyées depuis le stockage Onyxia
unhcr_df = pd.read_parquet("https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/unhcr_df.parquet")

# -------------------------------------------------------------------
# Diagnostic macro des déplacements selon la région d'origine
#
# Objectif :
# comparer les régions d'origine selon deux dimensions :
#   1. le nombre total de demandeurs d'asile ;
#   2. le nombre moyen de pays de destination par pays d'origine et par année.
#
# Ce diagnostic permet d'identifier une région combinant un volume
# important de demandeurs d'asile et une diversité élevée de destinations.
# -------------------------------------------------------------------

# On conserve uniquement les couples origine-destination pour lesquels
# au moins un demandeur d'asile est recensé.

unhcr_df = unhcr_df[unhcr_df["asylum_seekers"] > 0]

# Nombre total de demandeurs d'asile par région d'origine,
# classé par ordre décroissant.

overview1 = (unhcr_df.groupby("region_origin")["asylum_seekers"]
            .sum().reset_index().sort_values(axis=0, by="asylum_seekers", ascending=False))

# Nombre de pays de destination distincts pour chaque pays d'origine
# et chaque année.

overview0 = (unhcr_df.groupby(["coo_name", "year", "region_origin"])["coa_name"].nunique()
            .reset_index().rename(columns={"coa_name": "destination_countries"}))

# Nombre moyen de pays de destination par région d'origine.
# La moyenne est calculée sur les couples pays d'origine-année.
overview2 = (overview0.groupby(["region_origin"])["destination_countries"]
            .mean()
            .reset_index()
            .rename(columns={"destination_countries": "mean_destination_countries"}))

# Regroupement des deux indicateurs dans un même tableau.
overview = overview1.merge(overview2, 
            on="region_origin", 
            how="left")

overview.to_csv("overview.csv", index=False)