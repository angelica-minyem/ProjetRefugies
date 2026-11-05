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

# On retire alors les doublons incomplets.

south_asia = south_asia.drop_duplicates(subset=["year", "coo_iso", "coa_iso"], keep='first')

# On retire la colonne na_count, désormais inutile.

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

# Sélection des variables nécessaires à l'analyse de la répartition
# des réfugiés entre les différents pays de destination.
destination_shares = south_asia[["year", "coo_name", "coa_name", "destination_share"]]

# Conversion du dataframe obtenu en format parquet
destination_shares.to_parquet("destination_shares.parquet", index=False)

print(south_asia)

###############################
#Etude lien richesse immigration
#On calcule pour chaque pays le nombre total de réfugiés en provenance de la région étudiée arrivant dans ce pays. 
# On met cette information dans la table data accompagnée du PIB du pays d'arrivée, dans le but de faire un graphique reliant les deux. 
data = south_asia.groupby(["coa_iso"]).agg(refugees_sum=pd.NamedAgg(column="refugees", aggfunc="sum"), gdp=pd.NamedAgg(column="gdpcap_d", aggfunc="max"))
#On représente le nombre de réfugiés provenant de la région étudiée par rapport au PIB de la destination.
import matplotlib.pyplot as plt

# plt.figure(figsize=(10, 6))
# graph=plt.scatter(data["gdp"],data["refugees_sum"])
# plt.yscale('log')
# plt.xlabel("PIB du pays destinataire")
# plt.ylabel("Nombre de réfugiés provenant de la région Asie du sud")
# plt.title("Relation entre PIB et intensité des flux migratoires")
# plt.show()


#Cette fonction prend en argument un id de pays appartenant à la région étudiée et trace le nombre de réfugiés provenant de ce pays par rapport au PIB de la destination.
def analysis_by_country(country):
    df_country = south_asia.loc[(south_asia["coo_iso"]==country)]
    data_country = df_country.groupby(["coa_iso"]).agg(refugees_sum=pd.NamedAgg(column="refugees", aggfunc="sum"), gdp=pd.NamedAgg(column="gdpcap_d", aggfunc="max"))
    plt.figure(figsize=(10, 6))
    graph=plt.scatter(data_country["gdp"],data_country["refugees_sum"])
    plt.yscale('log')
    plt.xlabel("PIB du pays destinataire")
    plt.ylabel("Nombre de réfugiés provenant du pays" + country)
    plt.title("Relation entre PIB et intensité des flux migratoires")
    plt.show()


analysis_by_country("PAK")

###############################
# #CODE CARTE DANIEL
# import pandas as pd
# import geopandas as gpd
# import matplotlib.pyplot as plt
# import numpy as np
# from matplotlib.patches import FancyArrowPatch


# carte_url = "s3://dchitorog/Carte world/ne_110m_admin_0_countries.shp"

# #Chargement fond de carte mondial
# world = gpd.read_file(carte_url)
# world = world.to_crs(epsg=4326)
# world["iso_a3"] = world["ADM0_A3"].str.strip()

# # Calcul des centroïdes ( coordonnées latitude et longitude de chaque pays)
# centroids = world.geometry.centroid
# coords = pd.DataFrame({"iso" : world["iso_a3"], "lon" : centroids.x, "lat" : centroids.y})

# # On crée les flux
# flux_map = south_asia[(south_asia["year"] == 2017) & (south_asia["refugees"] > 0)].copy()
# # Pour bien visualiser, on décide un minimum de 500 réfugiés
# flux_map = flux_map[flux_map["refugees"] >= 500].copy()

# # Jointure pour récupérer les coordonnées du pays d'origine (départ)
# flux_map = flux_map.merge(coords.rename(columns={"iso": "coo_iso", "lon": "orig_lon", "lat": "orig_lat"}),
#     on="coo_iso",
#     how="inner")

# # Jointure pour récupérer les coordonnées du pays d'arrivée (destination)
# flux_map = flux_map.merge(coords.rename(columns={"iso": "coa_iso", "lon": "dest_lon", "lat": "dest_lat"}),
#     on="coa_iso",
#     how="inner")

# # Tracé cartographique
# fig, ax = plt.subplots(figsize=(18, 9))

# # Fond de carte mondial
# world.plot(ax=ax, color="#EAEAEA", edgecolor="#B5B5B5", linewidth=0.5)

# # Mise en évidence de l'Asie du Sud (zone de départ étudiée)
# south_asia_isos = flux_map["coo_iso"].unique()
# world[world["iso_a3"].isin(south_asia_isos)].plot(ax=ax, color="#FDE0DD", edgecolor="#FA9FB5", linewidth=0.8)

# # Tracé des flèches orientées
# for x, row in flux_map.iterrows() :
#     width = 1 + row["refugees"] * 10 ** (-5)  #( 1 correspondant à l'épaisseur minimale)
#     arrow = FancyArrowPatch(posA=(row["orig_lon"], row["orig_lat"]),posB=(row["dest_lon"], row["dest_lat"]),
#         connectionstyle="arc3,rad=0.25",arrowstyle="-|>",mutation_scale=10,color="#C51B8A",alpha=0.7,linewidth=width)
#     ax.add_patch(arrow)


# # Cadrage et titre
# ax.set_xlim(-180, 180)
# ax.set_ylim(-60, 85)
# ax.set_axis_off()
# ax.set_title("Principaux flux de réfugiés originaires d'Asie du Sud (2017)",fontsize=13,fontweight="bold",pad=15)

# plt.tight_layout()
# plt.show()

