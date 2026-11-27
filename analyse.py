
# %%

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def charger_south_asia():
    ### Cette fonction crée le dataframe south_asia à partir de df_unhcr et df_cepii. Renvoie south_asia. ###

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

    # Nombre total de demandeurs d'asile par pays d'origine et par année,
    # toutes destinations confondues.
    refugees_by_origin = south_asia.groupby(["year", "coo_name"])["refugees"].sum().reset_index().rename(
                                                columns={"refugees": "total_refugees_origin"})


    # Ajout du nombre total de demandeurs d'asile correspondant à chaque pays d'origine
    # et chaque année dans la base principale.
    south_asia = south_asia.merge(refugees_by_origin, on=["year", "coo_name"])

    # Calcul de la part des demandeurs d'asile présente dans chaque pays de destination.
    south_asia["destination_share"] = south_asia["refugees"]/south_asia["total_refugees_origin"]

    # Suppression de la variable intermédiaire devenue inutile.
    south_asia = south_asia.drop(columns="total_refugees_origin")
    return south_asia



def colonial_past():

    # Analyse du facteur lien colonial
    # Calcul du nombre de pairs pays d'Asie du Sud/pays de destination des demandeurs d'asile concernés   

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
    ### Ajoute la colonne "destination share" au dataframe south_asia, correspondant à la part des demandeurs d'asile présente dans chaque pays de destination. Prend en argument le dataframe south_asia et renvoie le dataframe south_asia modifié.

    # Calcul du nombre total de demandeurs d'asile par pays d'origine et par année,
    # toutes destinations confondues.
    refugees_by_origin = south_asia.groupby(["year", "coo_name"])["refugees"].sum().reset_index().rename(
                                                columns={"refugees": "total_refugees_origin"})


    # Ajout du nombre total de demandeurs d'asile correspondant à chaque pays d'origine
    # et chaque année dans la base principale.
    south_asia = south_asia.merge(refugees_by_origin, on=["year", "coo_name"])

    # Calcul de la part des demandeurs d'asile présente dans chaque pays de destination.
    south_asia["destination_share"] = south_asia["refugees"]/south_asia["total_refugees_origin"]

    # Suppression de la variable intermédiaire devenue inutile.
    south_asia = south_asia.drop(columns="total_refugees_origin")
    return(south_asia)


    # Sélection des variables nécessaires à l'analyse de la répartition
    # des réfugiés entre les différents pays de destination.
    #destination_shares = south_asia[["year", "coo_name", "coa_name", "destination_share"]]

    # Conversion du dataframe obtenu en format parquet
    #destination_shares.to_parquet("destination_shares.parquet", index=False)


