import requests
import pandas as pd

# Récupération des régions UNHCR
URL = "https://api.unhcr.org/population/v1/regions"
params = {"limit": 3000, "page": 1}

req = requests.get(URL, params = params)
regions_brut= req.json()

regions = pd.DataFrame([{"id": region["id"], "name": region["name"], "name_fr": region["name_fr"]}
                        for region in regions_brut["items"]])

regions = regions.sort_values(axis = 0, by = "id").reset_index(drop = True)


# Récupération des informations de chaque pays :
# identifiants, codes, noms (FR/ENG) et régions (FR/ENG)
URL2 = "https://api.unhcr.org/population/v1/countries"
params2= {"limit": 300, "page": 1}

req2 = requests.get(URL2, params = params2)
pays_brut = req2.json()

countries = pd.DataFrame([{"id": country["id"], "code": country["code"], "iso": country["iso"],
                        "name": country["name"], "nameFr": country["nameFr"], 
                        "region": country["region"], "regionFr": country["regionFr"]} 
                        for country in pays_brut["items"] ])


# Récupération du nombre de réfugiés présents en fin d'année
# coo = country of origin ; coa = country of asylum
# coo_all=True et coa_all=True permettent de récupérer toutes les paires origine-destination
URL3 = "https://api.unhcr.org/population/v1/population"
params3= {"limit": 300, "page": 1, "yearFrom": 2020, "yearTo": 2020, 
            "coo_all" : True, "coa_all" : True }

req3 = requests.get(URL3, params= params3)
refugies_brut = req3.json()

refugies = pd.DataFrame([{"year": entree["year"], 
                        "coo_id": entree["coo_id"], "coo_name" : entree["coo_name"], "coo": entree["coo"], "coo_iso": entree["coo_iso"],
                        "coa_id": entree["coa_id"], "coa_name" : entree["coa_name"], "coa": entree["coa"], "coa_iso": entree["coa_iso"],
                        "nb_refugies": entree["refugees"],
                        "demandeurs_asiles": entree["asylum_seekers"]} for entree in refugies_brut["items"] 
                        ])

# Conversion en numérique pour permettre les opérations statistiques
refugies["nb_refugies"] = pd.to_numeric(refugies["nb_refugies"])
