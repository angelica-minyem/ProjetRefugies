# %%

import pandas as pd
import plotly.express as px

from analyse_preliminaire import create_overview, create_overview_south_asia

unhcr_url = "https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/unhcr_df.parquet"
unhcr_df = pd.read_parquet(unhcr_url)

# %%

# Affichage du scatter plot à partir du tableau "overview"
# construit dans analyse_preliminaire.
# Le graphique compare les régions d'origine selon le volume total
# de demandes d'asile et le nombre moyen de pays de destination.

overview = create_overview(unhcr_df)

fig = px.scatter(
    overview,
    x="mean_destination_countries",
    y="refugees",
    hover_name="region_origin",
    hover_data={
        "mean_destination_countries": ":.1f",
        "refugees": ":,"
    },
    labels={
        "mean_destination_countries": "Nombre moyen de pays de destination",
        "refugees": "Nombre total de demandes d'asile"
    }
)

fig.update_layout(
    title="Demandes d'asile et diversité des destinations par région d'origine"
)

fig.show()

# %%

# Affichage du scatter plot à partir du tableau "overview_south_asia"
# construit dans analyse_preliminaire.
# Le graphique compare les pays d'Asie du Sud selon le volume total
# de demandes d'asile et le nombre moyen de pays de destination.

overview_south_asia = create_overview_south_asia(unhcr_df)

fig = px.scatter(
    overview_south_asia,
    x="mean_destination_countries",
    y="refugees",
    hover_name="coo_name",
    hover_data={
        "mean_destination_countries": ":.1f",
        "refugees": ":,"
    },
    labels={
        "mean_destination_countries": "Nombre moyen de pays de destination",
        "refugees": "Nombre total de demandes d'asile"
    }
)

fig.update_layout(
    title="Demandes d'asile et diversité des destinations par pays d'origine en Asie du Sud"
)

fig.show()

# %%

import matplotlib.pyplot as plt

destination_shares = pd.read_parquet(
    "https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/destination_shares.parquet"
)

# Affichage, pour un pays d'origine donné, des cinq principales
# destinations et de la part restante pour chaque année entre 2017 et 2020.

def plot_destinations(country):

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    years = [2017, 2018, 2019, 2020]

    for year, ax in zip(years, axes.flatten()):

        destination_top5 = destination_shares[
            (destination_shares["year"] == year) &
            (destination_shares["coo_name"] == country)
        ].sort_values(
            by="destination_share",
            ascending=False,
            ignore_index=True
        ).head(5)

        other_share = 1 - destination_top5["destination_share"].sum()

        destination_top5.loc[len(destination_top5)] = [
            year,
            country,
            "Autres",
            other_share
        ]

        destination_top5.plot.pie(
            y="destination_share",
            labels=destination_top5["coa_name"],
            autopct="%1.1f%%",
            ax=ax,
            legend=False
        )

        ax.set_title(str(year))
        ax.set_ylabel("")

    fig.suptitle(f"Principales destinations des demandeurs d'asile originaires de {country}")
    plt.tight_layout()
    plt.show()

countries = overview_south_asia["coo_name"].unique()
for country in countries :
    plot_destinations(country)
# %%