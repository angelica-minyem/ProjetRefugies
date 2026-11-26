
# %%

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def charger_south_asia():
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

    #Problème:les données du CEPII (et donc la jointure) contiennent des doublons. Les copies comportent un grand nombre de 
    #données manquantes. Afin de nettoyer le base de données, création de la variable na_count, qui contient le nombre de 
    #données manquantes dans chaque ligne:

    south_asia["na_count"] = south_asia.isna().sum(axis=1)

    #L'original sera alors la ligne contenant le moins de données manquantes. Tri des lignes par les colonnes "year", "coo_iso",
    # "coa_iso", puis par na_count. La ligne la plus complète sera alors positionnée en premier, permettant d'identifier et de supprimer les doublons.

    south_asia = south_asia.sort_values(
        by=["year", "coo_iso", "coa_iso", "na_count"]
    )



    south_asia = south_asia.drop_duplicates(subset=["year", "coo_iso", "coa_iso"], keep='first')


    south_asia = south_asia.drop(columns="na_count")

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
    return south_asia

# Analyse du facteur lien colonial
# Calcul du nombre de pairs pays d'Asie du Sud/pays de destination des réfugiés concernés



def colonial_past():

    south_asia = charger_south_asia()

    colonial_past = south_asia[south_asia["col_dep_ever"] == True].drop(columns = "col_dep_ever")

    UK_average_share = colonial_past.groupby(["coo_name", "coa_name"])[
                            "destination_share"].mean().reset_index().rename(columns= 
                            {"destination_share": "mean_share_UK"})

    coo_names = colonial_past["coo_name"].unique()

    south_asia_others = south_asia[south_asia["coo_name"].isin(coo_names)]
    south_asia_others = south_asia_others[south_asia_others["coa_name"]!= "United Kingdom"
                                     ].drop(columns = "col_dep_ever")
                        
    others_average_share = south_asia_others.groupby("coo_name")[
                       "destination_share"].mean().reset_index().rename(columns= 
                       {"destination_share": "mean_share_others"})

    colonial_past_wide = colonial_past.pivot_table(
                        index=["coo_name", "coa_name"],
                        columns="year",
                        values="destination_share").reset_index()

    colonial_past_wide = colonial_past_wide.rename(columns={
                        2017: "destination_share_2017",
                        2018: "destination_share_2018",
                        2019: "destination_share_2019",
                        2020: "destination_share_2020"})

    colonial_past_wide = colonial_past_wide.merge(UK_average_share,
                        on=["coo_name", "coa_name"]).merge(others_average_share,
                        on="coo_name")

    colonial_past_wide["ratio"] = (colonial_past_wide["mean_share_UK"]/colonial_past_wide["mean_share_others"]).round(2)

    return colonial_past_wide


def charger_destination_shares(south_asia):
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
    return(south_asia)


    # Sélection des variables nécessaires à l'analyse de la répartition
    # des réfugiés entre les différents pays de destination.
    #destination_shares = south_asia[["year", "coo_name", "coa_name", "destination_share"]]

    # Conversion du dataframe obtenu en format parquet
    #destination_shares.to_parquet("destination_shares.parquet", index=False)

###############################
#Etude lien richesse immigration

def scatter_plot_pib_demandes_asile(south_asia):
    #On calcule pour chaque pays d'arrivée le nombre total de réfugiés en provenance de la région étudiée arrivant dans ce pays. 
    #On met cette information dans la table data accompagnée du PIB du pays d'arrivée, dans le but de faire un graphique reliant les deux. 
    data = south_asia.groupby(["coa_iso"]).agg(refugees_sum=pd.NamedAgg(column="refugees", aggfunc="sum"), gdp=pd.NamedAgg(column="gdpcap_d", aggfunc="max"))
    #On représente le nombre de réfugiés provenant de la région étudiée par rapport au PIB/hab de la destination.
    plt.figure(figsize=(10, 6))
    graph=plt.scatter(data["gdp"],data["refugees_sum"])
    plt.xlabel("PIB par habitant du pays destinataire (milliers de US$/hab)")
    plt.ylabel("Nombre de demandes d'asile provenant de la région Asie du sud")
    plt.title("Relation entre PIB et intensité des flux migratoires")
    plt.show()

def scatter_plot_ech_log(south_asia):
    #On calcule pour chaque pays le nombre total de réfugiés en provenance de la région étudiée arrivant dans ce pays. 
    #On met cette information dans la table data accompagnée du PIB du pays d'arrivée, dans le but de faire un graphique reliant les deux. 
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









#Cette fonction prend en argument un id de pays appartenant à la région étudiée et trace le nombre de réfugiés provenant de ce pays par rapport au PIB de la destination.
def analysis_by_country(south_asia,country):
    df_country = south_asia.loc[(south_asia["coo_iso"]==country)]
    data_country = df_country.groupby(["coa_iso"]).agg(refugees_sum=pd.NamedAgg(column="refugees", aggfunc="sum"), gdp=pd.NamedAgg(column="gdpcap_d", aggfunc="max"))
    plt.figure(figsize=(10, 6))
    graph=plt.scatter(data_country["gdp"],data_country["refugees_sum"])

    plt.xlabel("PIB/hab du pays destinataire")
    plt.ylabel("Nombre de demandes d'asile provenant du pays " + country)
    plt.title("Relation entre PIB et intensité des flux migratoires")
    plt.show()

###############################
#Etude frontière
#On calcule le pourcentage de demandes d'asiles réalisées dans un pays frontalier, par pays d'origine et par année
# frontiere_data = south_asia[["year", "coo_name", "coa_name", "destination_share","contig"]]
# frontiere_comm = frontiere_data.loc[frontiere_data["contig"]==True]
# frontiere_part = frontiere_comm.groupby(["year","coo_name"])["destination_share"].sum()
# #Graphique:
# import matplotlib.pyplot as plt

# plt.figure(figsize=(15, 6))

# frontiere_part.plot(kind="bar")

# plt.xlabel("Pays et année")
# plt.ylabel("Pourcentage de demandes d'asile réalisées dans un pays connexe")
# plt.title("Pourcentage de demandes d'asile réalisées dans un pays connexe par pays et année")

# plt.show()

###############################
#Etude langue
#On calcule le pourcentage de demandes d'asiles réalisées dans un pays partageant une langue officielle, par pays d'origine et par année
# frontiere_data = south_asia[["year", "coo_name", "coa_name", "destination_share","comlang_off"]]
# frontiere_comm = frontiere_data.loc[frontiere_data["comlang_off"]==True]
# frontiere_part = frontiere_comm.groupby(["year","coo_name"])["destination_share"].sum()
# #Graphique:
# import matplotlib.pyplot as plt

# plt.figure(figsize=(15, 6))

# frontiere_part.plot(kind="bar")

# plt.xlabel("Pays et année")
# plt.ylabel("Pourcentage de demandes d'asile réalisées dans un pays partageant une langue officielle")
# plt.title("Pourcentage de demandes d'asile réalisées dans un pays partageant une langue officielle par pays et année")

# plt.show()


###############################
#Etude distance
# %%

def analyse_distance(south_asia):


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

    # Lien pas assez visible, passage en log

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
# %%
