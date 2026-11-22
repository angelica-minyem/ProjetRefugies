
# %%

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
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
# "coa_iso", puis par na_count. La ligne la plus complète sera alors positionnée en premier, permettant d'identifier et de supprimer les doublons.

south_asia = south_asia.sort_values(
    by=["year", "coo_iso", "coa_iso", "na_count"]
)



south_asia = south_asia.drop_duplicates(subset=["year", "coo_iso", "coa_iso"], keep='first')


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
destination_shares = south_asia[["year", "coo_name", "coa_name", "destination_share"]]

# Conversion du dataframe obtenu en format parquet
destination_shares.to_parquet("destination_shares.parquet", index=False)

###############################
#Etude lien richesse immigration
#On calcule pour chaque pays le nombre total de réfugiés en provenance de la région étudiée arrivant dans ce pays. 
# On met cette information dans la table data accompagnée du PIB du pays d'arrivée, dans le but de faire un graphique reliant les deux. 
data = south_asia.groupby(["coa_iso"]).agg(refugees_sum=pd.NamedAgg(column="refugees", aggfunc="sum"), gdp=pd.NamedAgg(column="gdpcap_d", aggfunc="max"))



# Régression linéaire log-log du nombre de demanges d'asile en provenance de l'asie du sud est en fonction du PIB/hab de la destination.
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
plt.xlabel("PIB par habitant du pays destinataire")
plt.ylabel("Nombre de demandes d'asile provenant de la région Asie du sud")
plt.title("Régression linéaire log-log :nombre de demandes d'asile en provenance de l'asie du sud est en fonction du PIB/hab de la destination.")
plt.legend()
plt.show()





#On représente le nombre de réfugiés provenant de la région étudiée par rapport au PIB/hab de la destination, accompagnés de la droite de regression.

plt.figure(figsize=(10, 6))
graph=plt.scatter(data["gdp"],data["refugees_sum"])

plt.xlabel("PIB par habitant du pays destinataire")
plt.ylabel("Nombre de demandes d'asile provenant de la région Asie du sud")
plt.title("Relation entre PIB et intensité des flux migratoires")
plt.show()


#Cette fonction prend en argument un id de pays appartenant à la région étudiée et trace le nombre de réfugiés provenant de ce pays par rapport au PIB de la destination.
def analysis_by_country(country):
    df_country = south_asia.loc[(south_asia["coo_iso"]==country)]
    data_country = df_country.groupby(["coa_iso"]).agg(refugees_sum=pd.NamedAgg(column="refugees", aggfunc="sum"), gdp=pd.NamedAgg(column="gdpcap_d", aggfunc="max"))
    plt.figure(figsize=(10, 6))
    graph=plt.scatter(data_country["gdp"],data_country["refugees_sum"])
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("PIB/hab du pays destinataire")
    plt.ylabel("Nombre de demandes d'asile provenant du pays " + country)
    plt.title("Relation entre PIB et intensité des flux migratoires")
    plt.show()
analysis_by_country("IND")

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
frontiere_data = south_asia[["year", "coo_name", "coa_name", "destination_share","comlang_off"]]
frontiere_comm = frontiere_data.loc[frontiere_data["comlang_off"]==True]
frontiere_part = frontiere_comm.groupby(["year","coo_name"])["destination_share"].sum()
#Graphique:
import matplotlib.pyplot as plt

plt.figure(figsize=(15, 6))

frontiere_part.plot(kind="bar")

plt.xlabel("Pays et année")
plt.ylabel("Pourcentage de demandes d'asile réalisées dans un pays partageant une langue officielle")
plt.title("Pourcentage de demandes d'asile réalisées dans un pays partageant une langue officielle par pays et année")

plt.show()
# %%
###############################
# #CODE CARTE DANIEL
import geopandas as gpd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch

carte_url = "s3://dchitorog/Carte world/ne_110m_admin_0_countries.shp"

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
flux_map = flux_map[flux_map["refugees"] >= 5000].sort_values(by="refugees", ascending=False).copy()

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

# %%

###############################
#Etude distance
# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

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
