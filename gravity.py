import os
import pandas as pd
import requests
import zipfile

url = "https://minio.lab.sspcloud.fr"

zip_path = "Gravity_csv_V202211.zip"

extract_dir = "data/gravity"



if not os.path.exists(zip_path):

    print("Téléchargement en cours...")

    response = requests.get(url, stream=True)

    with open(zip_path, "wb") as f:

        for chunk in response.iter_content(chunk_size=8192):

            f.write(chunk)

    print("Téléchargement terminé.")



# Extraction

if not os.path.exists(extract_dir):

    print("Extraction...")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:

        zip_ref.extractall(extract_dir)

    print("Fichiers extraits dans :", extract_dir)




cols_utiles = ["year", "iso3_o", "iso3_d", "distw_harmonic", "contig", "comlang_off", "gdp_ppp_pwt_o", "gdp_ppp_pwt_d","comrelig","comcol"]



df = pd.read_csv(
    "data/gravity/Gravity_V202211.csv", 
    usecols=cols_utiles,
    low_memory=False
)



df = df[df["year"] == 2017]
df=df[df["iso3_o"]!=df["iso3_d"]]

df['contig'] = df['contig'].replace(0, False)
df['comlang_off'] = df['comlang_off'].replace(0, False)
df['comcol'] = df['comcol'].replace(0, False)
df['contig'] = df['contig'].replace(1, True)
df['comlang_off'] = df['comlang_off'].replace(1, True)
df['comcol'] = df['comcol'].replace(1, True)
print(df)
