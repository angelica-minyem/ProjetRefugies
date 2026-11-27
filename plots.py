import pandas as pd
import plotly.express as px
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch
from sklearn.linear_model import LinearRegression
from analyse_preliminaire import create_overview, create_overview_south_asia


def world_scatter_plot():
    """
    Affichage du scatter plot à partir du tableau "overview" 
    construit dans analyse preliminaire
    Le graphique compare les régions du monde selon le volume total
    de demandes d'asile et le nombre moyen de pays de destination

    """

    unhcr_url = "https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/unhcr_df.parquet"
    unhcr_df = pd.read_parquet(unhcr_url)
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

def south_asia_scatter_plot():
    """
    Affichage du scatter plot à partir du tableau "overview_south_asia" 
    construit dans analyse preliminaire
    Le graphique compare les pays d'Asie du Sud selon le volume total
    de demandes d'asile et le nombre moyen de pays de destination

    """ 

    unhcr_url = "https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/unhcr_df.parquet"
    unhcr_df = pd.read_parquet(unhcr_url)
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


def plot_destinations(country):

    """
    Affichage, pour un pays d'origine donné, des cinq principales
    destinations et de la part restante pour chaque année entre 2017 et 2020.
    """
    destination_shares = pd.read_parquet("https://minio.lab.sspcloud.fr/angelik/ProjetRefugies/destination_shares.parquet")
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


def affichage_country(overview_south_asia) :
    countries = overview_south_asia["coo_name"].unique()
    for country in countries :
        plot_destinations(country)


def plot_carte_flux(south_asia,carte_url="https://minio.lab.sspcloud.fr/dchitorog/Carte%20world/ne_110m_admin_0_countries.shp",seuil=5000,):
    """
    Affiche la carte mondiale des principaux flux cumulés (2017-2020)
    de demandeurs d'asile originaires d'Asie du Sud.
    """
    #Chargement fond de carte mondial
    world = gpd.read_file(carte_url)
    world = world.to_crs(epsg=4326)
    world["iso_a3"] = world["ADM0_A3"].str.strip()

    # Calcul des centroïdes ( coordonnées latitude et longitude de chaque pays)
    centroids = world.geometry.centroid
    coords = pd.DataFrame({"iso" : world["iso_a3"], "lon" : centroids.x, "lat" : centroids.y})

    # On regroupe les flux sur les 4 années pour chaque pays
    flux_map = south_asia.groupby(["coo_iso", "coo_name", "coa_iso", "coa_name"], as_index=False)["refugees"].sum()
    # On crée les flux, Pour bien visualiser, on décide un minimum de 5000 réfugiés
    flux_map = flux_map[flux_map["refugees"] >= seuil].sort_values(by="refugees", ascending=False).copy()

    # Jointure pour récupérer les coordonnées du pays d'origine (départ)
    flux_map = flux_map.merge(coords.rename(columns={"iso": "coo_iso", "lon": "orig_lon", "lat": "orig_lat"}),
        on="coo_iso",
        how="inner")

    # Jointure pour récupérer les coordonnées du pays d'arrivée (destination)
    flux_map = flux_map.merge(coords.rename(columns={"iso": "coa_iso", "lon": "dest_lon", "lat": "dest_lat"}),
        on="coa_iso",
        how="inner")

    # Palette de couleurs par pays d'origine
    origins = sorted(flux_map["coo_name"].unique())
    palette = plt.cm.tab10(np.linspace(0, 1, len(origins)))
    color_dict = {orig: palette[i] for i, orig in enumerate(origins)}

    # Tracé cartographique
    fig, ax = plt.subplots(figsize=(18, 9))

    # Fond de carte mondial
    world.plot(ax=ax, color="#EAEAEA", edgecolor="#B5B5B5", linewidth=0.5)

    # Mise en évidence de l'Asie du Sud (zone de départ étudiée)
    south_asia_isos = flux_map["coo_iso"].unique()
    world[world["iso_a3"].isin(south_asia_isos)].plot(ax=ax, color="#FDE0DD", edgecolor="#FA9FB5", linewidth=0.8)

    # Tracé des flèches orientées
    for x, row in flux_map.iterrows() :
        width = 0.5 + row["refugees"] *2*10 ** (-5)  #( 1 correspondant à l'épaisseur minimale, le facteur 2*10**(-5) pour un meilleur visuel)
        c = color_dict[row["coo_name"]]
        arrow = FancyArrowPatch(posA=(row["orig_lon"], row["orig_lat"]),posB=(row["dest_lon"], row["dest_lat"]),
            connectionstyle="arc3,rad=0.25",arrowstyle="-|>",mutation_scale=10,color=c,alpha=0.7,linewidth=width)
        ax.add_patch(arrow)

    # Légende pays d'origine
    legend_origins = [Line2D([0], [0], color=color_dict[orig], lw=2.5, marker=">", markersize=6, label=orig)for orig in origins]
    leg_origins = ax.legend(handles=legend_origins,title="Pays d'origine",loc="lower left",frameon=True,facecolor="white",
        framealpha=0.9,edgecolor="#CCCCCC",fontsize=9,title_fontsize=10)
    ax.add_artist(leg_origins)

    # Légende 2 : Échelle des volumes
    paliers = [5000, 50000, 200000]
    paliers = [p for p in paliers if p <= flux_map["refugees"].max() * 1.2]

    legend_scale = [Line2D([0], [0], color="#555555", lw= 0.5 + val * 2 * 10 ** (-5), label=f"{val:,.0f} réfugiés".replace(",", " "))for val in paliers]
    ax.legend(handles=legend_scale,title="Volume du flux",loc="lower right",frameon=True,facecolor="white",
        framealpha=0.9,edgecolor="#CCCCCC",fontsize=9,title_fontsize=10)

    # Cadrage et titre
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_axis_off()
    ax.set_title("Principaux flux de réfugiés originaires d'Asie du Sud (2017-2020)",fontsize=13,fontweight="bold",pad=15)

    plt.tight_layout()
    plt.show()


def plot_regression_distance_simple(south_asia):
    """
    Estime et trace la régression linéaire simple de destination_share
    en fonction de la distance harmonique pondérée (distw_harmonic).
    """
    # Préparation des données valides et tri par distance croissante
    dist_df = south_asia[(south_asia["refugees"] > 0) & (south_asia["distw_harmonic"].notna())].copy()
    dist_df = dist_df.sort_values(by="distw_harmonic")

    # Régression linéaire simple du choix de la destination selon la distance
    x = dist_df[["distw_harmonic"]]
    y = dist_df["destination_share"]

    reg_simple = LinearRegression()
    reg_simple.fit(x, y)

    print("Modèle simple - Constante :", reg_simple.intercept_)
    print("Modèle simple - Pente :", reg_simple.coef_[0])
    print("Modèle simple - R² :", reg_simple.score(x, y))

    # Graphique : nuage de point et droite de régression

    plt.figure(figsize=(10, 6))
    plt.scatter(dist_df["distw_harmonic"], y, alpha=0.5, label="Observations")
    plt.plot(dist_df["distw_harmonic"], reg_simple.predict(x), color="red", linewidth=2, label="Régression linéaire")
    plt.xlabel("Distance pondérée entre pays (en km)")
    plt.ylabel("Part des demandes d'asile choisissant la destination")
    plt.title("Régression linéaire simple : choix de destination selon la distance")
    plt.legend()
    plt.show()



def plot_regression_distance_log(south_asia):
    """
    Estime et trace la régression log-log de ln(destination_share)
    en fonction de ln(distw_harmonic).
    """
    dist_df = south_asia[(south_asia["refugees"] > 0) & (south_asia["distw_harmonic"].notna())].copy()
    dist_df = dist_df.sort_values(by="distw_harmonic")

    # Transformation logarithmique des deux variables
    dist_df["log_dist"] = np.log(dist_df["distw_harmonic"])
    dist_df["log_share"] = np.log(dist_df["destination_share"])

    # Régression linéaire modèle log-log
    x_log = dist_df[["log_dist"]]
    y_log = dist_df["log_share"]

    reg_log = LinearRegression()
    reg_log.fit(x_log, y_log)

    print("Modèle log-log - Constante :", reg_log.intercept_)
    print("Modèle log-log - Pente (élasticité) :", reg_log.coef_[0])
    print("Modèle log-log - R² :", reg_log.score(x_log, y_log))

    # Graphique : nuage de point et droite de régression log-log

    plt.figure(figsize=(10, 6))
    plt.scatter(dist_df["log_dist"], y_log, alpha=0.5, label="Observations (log)")
    plt.plot(dist_df["log_dist"], reg_log.predict(x_log), color="red", linewidth=2, label="Régression log-log")
    plt.xlabel("Logarithme de la distance : ln(distw_harmonic)")
    plt.ylabel("Logarithme de la part de destination : ln(destination_share)")
    plt.title("Modèle log-log : choix de destination selon la distance")
    plt.legend()
    plt.show()


###############################
#Etude lien richesse immigration

def scatter_plot_pib_demandes_asile(south_asia):
    ###Cette fonction prend en argument le database south_asia et trace le nombre de demandeurs d'asile arrivant dans un pays en fonction de son PIB/hab ###

    #On calcule pour chaque pays d'arrivée le nombre total de demandeurs d'asile en provenance de la région étudiée arrivant dans ce pays. 
    #On met cette information dans la table data accompagnée du PIB du pays d'arrivée, dans le but de faire un graphique reliant les deux. 
    data = south_asia.groupby(["coa_iso"]).agg(refugees_sum=pd.NamedAgg(column="refugees", aggfunc="sum"), gdp=pd.NamedAgg(column="gdpcap_d", aggfunc="max"))
    #On représente le nombre de demandeurs d'asile provenant de la région étudiée par rapport au PIB/hab de la destination.
    plt.figure(figsize=(10, 6))
    graph=plt.scatter(data["gdp"],data["refugees_sum"])
    plt.xlabel("PIB par habitant du pays destinataire (milliers de US$/hab)")
    plt.ylabel("Nombre de demandes d'asile provenant de la région Asie du sud")
    plt.title("Relation entre PIB et intensité des flux migratoires")
    plt.show()


def scatter_plot_ech_log(south_asia):
    ### Cette fonction prend en argument le database south_asia et trace le nombre de demandeurs d'asile arrivant dans un pays en fonction de son PIB/hab, avec une échelle logarithmique. ###

    #On calcule pour chaque pays le nombre total de réfugiés en provenance de la région étudiée arrivant dans ce pays. 
    #On met cette information dans la table data accompagnée du PIB du pays d'arrivée.
    data = south_asia.groupby(["coa_iso"]).agg(refugees_sum=pd.NamedAgg(column="refugees", aggfunc="sum"), gdp=pd.NamedAgg(column="gdpcap_d", aggfunc="max"))
    #On représente le nombre de réfugiés provenant de la région étudiée par rapport au PIB/hab de la destination.
    plt.figure(figsize=(10, 6))
    graph=plt.scatter(data["gdp"],data["refugees_sum"])
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("PIB par habitant du pays destinataire (milliers de US$/hab)")
    plt.ylabel("Nombre de demandes d'asile provenant de la région Asie du sud")
    plt.title("Relation entre PIB et intensité des flux migratoires")
    plt.show()



def reg_lin_log_log(south_asia):
    ### Cette fonction prend en argument le database south_asia et réalise la régression linéaire log-log du nombre de demandeurs d'asile arrivant dans un pays en fonction de son PIB/hab ###

    #On calcule pour chaque pays le nombre total de réfugiés en provenance de la région étudiée arrivant dans ce pays. 
    #On met cette information dans la table data accompagnée du PIB du pays d'arrivée, dans le but de faire un graphique reliant les deux. 
    data = south_asia.groupby(["coa_iso"]).agg(refugees_sum=pd.NamedAgg(column="refugees", aggfunc="sum"), gdp=pd.NamedAgg(column="gdpcap_d", aggfunc="max"))
    # Régression linéaire log-log du nombre de demandes d'asile en provenance de l'asie du sud est en fonction du PIB/hab de la destination.
    x = np.log(data[["gdp"]]).fillna(0)
    y = np.log(data[["refugees_sum"]]).fillna(0)

    reg_log = LinearRegression()
    reg_log.fit(x, y)

    print("Modèle log-log - Constante :", reg_log.intercept_)
    print("Modèle log - Pente :", reg_log.coef_[0])
    print("Modèle log - R² :", reg_log.score(x, y))

    # Graphique : nuage de point et droite de régression

    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, alpha=0.5, label="Observations")
    plt.plot(x, reg_log.predict(x), color="red", linewidth=2, label="Régression linéaire")
    plt.xlabel("PIB par habitant du pays destinataire (milliers de US$/hab)")
    plt.ylabel("Nombre de demandes d'asile provenant de la région Asie du sud")
    plt.title("Régression linéaire log-log :nombre de demandes d'asile en provenance de l'asie du sud est en fonction du PIB/hab de la destination.")
    plt.legend()
    plt.show()









def analysis_by_country(south_asia,country):
    ### Cette fonction prend en argument un id de pays appartenant à la région étudiée et trace le nombre de réfugiés provenant de ce pays par rapport au PIB de la destination. ###

    df_country = south_asia.loc[(south_asia["coo_iso"]==country)]
    data_country = df_country.groupby(["coa_iso"]).agg(refugees_sum=pd.NamedAgg(column="refugees", aggfunc="sum"), gdp=pd.NamedAgg(column="gdpcap_d", aggfunc="max"))
    plt.figure(figsize=(10, 6))
    graph=plt.scatter(data_country["gdp"],data_country["refugees_sum"])

    plt.xlabel("PIB/hab du pays destinataire")
    plt.ylabel("Nombre de demandes d'asile provenant du pays " + country)
    plt.title("Relation entre PIB et intensité des flux migratoires")
    plt.show()
