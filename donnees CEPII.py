import pandas as pd

# Chargement des données CEPII Gravity depuis le stockage Onyxia
url = "https://minio.lab.sspcloud.fr/carcachoc/Gravity_V202211.csv"

# Sélection des variables utiles à l'analyse :
# year : année de l'observation
# iso3_o / iso3_d : codes ISO3 des pays d'origine et de destination
# distw_harmonic : distance harmonique pondérée entre les deux pays
# contig : indique si les deux pays partagent une frontière
# comlang_off : indique si les deux pays partagent une langue officielle ou principale
# gdpcap_ppp_o / gdpcap_ppp_d : PIB par habitant en PPA des pays d'origine et de destination
# comrelig : indice de proximité religieuse entre les deux pays
# col_dep_ever : indique l'existence passée d'une relation coloniale entre les deux pays
use_cols = ["year", "iso3_o", "iso3_d", "distw_harmonic", 
                "contig", "comlang_off", "gdpcap_ppp_o", 
                "gdpcap_ppp_d", "comrelig", "col_dep_ever"]


# Lecture uniquement des colonnes utiles et renommage des variables de PIB par habitant
cepii_df = pd.read_csv(
    url, 
    usecols=use_cols,
    low_memory=False
).rename(columns = {"gdpcap_ppp_o": "gdpcap_o", 
                    "gdpcap_ppp_d": "gdpcap_d"})


# Conservation des années communes avec les données UNHCR
cepii_df = cepii_df[cepii_df["year"].between(2017, 2020)]

# Suppression des couples pour lesquels le pays d'origine et le pays de destination sont identiques
cepii_df = cepii_df[cepii_df["iso3_o"] != cepii_df["iso3_d"]]

# Conversion de l'année en entier afin d'assurer la compatibilité avec la clé de jointure UNHCR
cepii_df["year"] = cepii_df["year"].astype(int)

# Conversion des variables indicatrices 0/1 en booléens
cepii_df['contig'] = cepii_df['contig'].replace(0, False)
cepii_df['comlang_off'] = cepii_df['comlang_off'].replace(0, False)
cepii_df['col_dep_ever'] = cepii_df['col_dep_ever'].replace(0, False)

cepii_df['contig'] = cepii_df['contig'].replace(1, True)
cepii_df['comlang_off'] = cepii_df['comlang_off'].replace(1, True)
cepii_df['col_dep_ever'] = cepii_df['col_dep_ever'].replace(1, True)

# Conversion du dataframe en fichier parquet

cepii_df.to_parquet("cepii_df.parquet", index=False)