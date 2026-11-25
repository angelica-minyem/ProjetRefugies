import pandas as pd

# Chargement des données UNHCR nettoyées depuis le stockage Onyxia
unhcr_df = pd.read_parquet("https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/unhcr_df.parquet")

def create_overview(unhcr_df):
    """
    Construit un tableau récapitulatif des nouvelles demandes d'asile
    à l'échelle des régions d'origine.

    Pour chaque région d'origine, le tableau contient :
    - le nombre total de nouvelles demandes d'asile entre 2017 et 2020 ;
    - le nombre moyen de pays de destination.

    Le nombre moyen de destinations est calculé à partir des couples
    pays d'origine-année.
    """

    # Conservation uniquement des observations avec au moins
    # une nouvelle demande d'asile.
    unhcr_df = unhcr_df[unhcr_df["refugees"] > 0]

    # Nombre total de nouvelles demandes d'asile par région d'origine.
    overview1 = (unhcr_df.groupby("region_origin")["refugees"]
                .sum()
                .reset_index()
                .sort_values(by="refugees", ascending=False))

    # Nombre de pays de destination distincts pour chaque pays d'origine
    # et chaque année.
    overview0 = (unhcr_df.groupby(
                ["coo_name", "year", "region_origin"])["coa_name"]
                .nunique()
                .reset_index()
                .rename(columns={"coa_name": "destination_countries"}))

    # Nombre moyen de pays de destination par région d'origine.
    overview2 = (overview0.groupby("region_origin")["destination_countries"]
                .mean()
                .reset_index()
                .rename(columns={"destination_countries": "mean_destination_countries"}))

    # Regroupement des deux indicateurs.
    overview = overview1.merge(
                overview2,
                on="region_origin",
                how="left")

    return overview



def create_overview_south_asia(unhcr_df):
    """
    Construit un tableau récapitulatif des nouvelles demandes d'asile
    pour les pays d'origine appartenant à Southern Asia
    (région d'analyse choisie pour cette étude).

    Pour chaque pays d'origine, le tableau contient :
    - le nombre total de nouvelles demandes d'asile entre 2017 et 2020 ;
    - le nombre moyen de pays de destination sur cette période.
    """

    # Conservation uniquement des observations avec au moins
    # une nouvelle demande d'asile.
    unhcr_df = unhcr_df[unhcr_df["refugees"] > 0]

    # Conservation des pays d'origine appartenant à Southern Asia.
    south_asia = unhcr_df[unhcr_df["region_origin"] == "Southern Asia"]

    # Nombre total de nouvelles demandes d'asile par pays d'origine.
    overview1 = (south_asia.groupby("coo_name")["refugees"]
                .sum()
                .reset_index()
                .sort_values(by="refugees", ascending=False))

    # Nombre de pays de destination distincts pour chaque pays d'origine
    # et chaque année.
    overview0 = (south_asia.groupby(["coo_name", "year"])["coa_name"]
                .nunique()
                .reset_index()
                .rename(columns={"coa_name": "destination_countries"}))

    # Nombre moyen de pays de destination pour chaque pays d'origine.
    overview2 = (overview0.groupby("coo_name")["destination_countries"]
                .mean()
                .reset_index()
                .rename(columns={"destination_countries": "mean_destination_countries"}))

    # Regroupement des deux indicateurs.
    overview = overview1.merge(
                overview2,
                on="coo_name",
                how="left")

    return overview