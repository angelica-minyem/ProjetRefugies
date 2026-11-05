# %%
import plotly.express as px
import pandas as pd

overview = pd.read_csv("https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/overview.csv")

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
        "mean_destination_countries": "Mean number of destination countries",
        "refugees": "Total asylum seekers"
    }
)

fig.update_layout(
    title="Asylum seekers and destination diversity by region"
)

fig.show()
# %%
import pandas as pd
import matplotlib.pyplot as plt

destination_shares = pd.read_parquet(
    "https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/destination_shares.parquet")


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
            "Other",
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

    fig.suptitle(f"Top destinations of refugees from {country}")
    plt.tight_layout()
    plt.show()

# %%
