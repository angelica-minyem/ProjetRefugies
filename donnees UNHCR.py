import requests
import pandas as pd

# Récupération des régions UNHCR
URL = "https://api.unhcr.org/population/v1/regions"
params = {"limit": 3000, "page": 1}

req = requests.get(URL, params = params)
regions_brut= req.json()

regions = pd.DataFrame([{"id": region["id"], "name": region["name"]}
                        for region in regions_brut["items"]])

regions = regions.sort_values(axis = 0, by = "id").reset_index(drop = True)


# Récupération des informations de chaque pays :
# identifiants, codes, noms (FR/ENG) et régions (FR/ENG)
URL2 = "https://api.unhcr.org/population/v1/countries"
params2= {"limit": 300, "page": 1}

req2 = requests.get(URL2, params = params2)
pays_brut = req2.json()

countries = pd.DataFrame([{"id": country["id"], 
                        "iso": country["iso"],
                        "name": country["name"],
                        "region": country["region"]} 
                        for country in pays_brut["items"]])


# Récupération du nombre de réfugiés présents en fin d'année
# coo = country of origin ; coa = country of asylum
# coo_all=True et coa_all=True permettent de récupérer toutes les paires origine-destination
URL3 = "https://api.unhcr.org/population/v1/population"

params3 = {"limit": 300, "page": 1, 
            "yearFrom": 2017, "yearTo": 2020,
            "coo_all": True, "coa_all": True}

refugees_raw = []
max_pages = requests.get(URL3, params=params3).json()["maxPages"]

for page in range(1, max_pages + 1):
    params3["page"] = page
    data = requests.get(URL3, params=params3).json()
    refugees_raw.extend(data["items"])

selected_var = ["year", "coo_iso", "coo_name", "coa_iso", "coa_name", "refugees", "asylum_seekers"]
refugees = pd.DataFrame(refugees_raw)[selected_var]

# Conversion en numérique pour permettre les opérations statistiques

refugees["refugees"] = pd.to_numeric(refugees["refugees"])
refugees["asylum_seekers"] = pd.to_numeric(refugees["asylum_seekers"])

# Ajout de la région du pays d'origine

mixed_df = refugees.merge(countries[["iso", "region"]],
                        left_on="coo_iso", right_on="iso", how="left")

print(mixed_df.head(3))


# Région d'origine totalisant le plus de demandeurs d'asile
print(
    mixed_df.groupby("region")["asylum_seekers"].sum().idxmax()
)
