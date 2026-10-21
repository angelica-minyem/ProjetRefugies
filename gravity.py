import pandas as pd



countries = "https://minio.lab.sspcloud.fr/carcachoc/Countries_V202211.csv"
url = "https://minio.lab.sspcloud.fr/carcachoc/Gravity_V202211.csv"



cols_utiles = ["year", "iso3_o", "iso3_d", "distw_harmonic", "contig", "comlang_off", "gdp_ppp_pwt_o", "gdp_ppp_pwt_d","comrelig","comcol"]



comparaison = pd.read_csv(
    url, 
    usecols=cols_utiles,
    low_memory=False
)



comparaison = comparaison[comparaison["year"] == 2017]
comparaison=comparaison[comparaison["iso3_o"]!=comparaison["iso3_d"]]

comparaison['contig'] = comparaison['contig'].replace(0, False)
comparaison['comlang_off'] = comparaison['comlang_off'].replace(0, False)
comparaison['comcol'] = comparaison['comcol'].replace(0, False)
comparaison['contig'] = comparaison['contig'].replace(1, True)
comparaison['comlang_off'] = comparaison['comlang_off'].replace(1, True)
comparaison['comcol'] = comparaison['comcol'].replace(1, True)
print(comparaison)
