import pandas as pd

# Chargement des données UNHCR nettoyées depuis le stockage Onyxia
unhcr_df = pd.read_parquet(
    "https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/unhcr_df.parquet"
)

# Calculs de statistiques descriptives globales

n_applications = unhcr_df["refugees"].sum()
nunique_coo = unhcr_df["coo_name"].nunique()
nunique_coa = unhcr_df["coa_name"].nunique()
nunique_region = unhcr_df["region_origin"].nunique()


print("Statistiques descriptives globales")
print("Nombre total de nouvelles demandes d'asile :", n_applications)
print("Nombre de pays d'origine distincts :", nunique_coo)
print("Nombre de pays de destination distincts :", nunique_coa)
print("Nombre de régions d'origine :", nunique_region)


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


overview = create_overview(unhcr_df)

# Calcul de la part des nouvelles demandes d'asile provenant
# d'Asie du Sud dans l'ensemble des demandes observées.
south_asia_share = (overview[overview["region_origin"] == "Southern Asia"]["refugees"].iloc[0] 
                    / n_applications)*100

print("Part de demandeurs d'asile venant d'Asie du Sud :",
      round(south_asia_share, 2), "%")


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


overview_southasia = create_overview_south_asia(unhcr_df)

# Calcul de la part des nouvelles demandes d'asile provenant
# d'Afghanistan parmi l'ensemble des demandes originaires d'Asie du Sud.
afghanistan_share = (overview_southasia[overview_southasia["coo_name"] == "Afghanistan"]["refugees"].iloc[0]/
                    (overview_southasia["refugees"].sum()))*100

print("Part des demandeurs d'asile sud-asiatiques originaires d'Afghanistan :",
      round(afghanistan_share, 2), "%")


# Conservation des pays d'Asie du Sud hors Afghanistan afin de comparer
# la diversité de leurs destinations à celle de l'Afghanistan.
overview_southasia_without_afghanistan = overview_southasia[
                                        overview_southasia["coo_name"] != "Afghanistan"
                                        ]

# Calcul de la médiane du nombre moyen de destinations
# pour les pays d'Asie du Sud hors Afghanistan.
median_destinations = (overview_southasia_without_afghanistan[
                        "mean_destination_countries"
                        ].median())

print(
    "Médiane du nombre moyen de destinations des demandeurs d'asile sud-asiatiques hors Afghanistan :",
    median_destinations)


# Calcul du nombre moyen de destinations pour l'Afghanistan
# afin de le comparer à la médiane des autres pays de la région.
afghanistan_destinations = (overview_southasia[
                            overview_southasia["coo_name"] == "Afghanistan"
                            ]["mean_destination_countries"].iloc[0])

print(
    "Nombre moyen de destinations pour l'Afghanistan :",
    afghanistan_destinations)