import pandas as pd



countries = "https://minio.lab.sspcloud.fr/carcachoc/Countries_V202211.csv"
url = "https://minio.lab.sspcloud.fr/carcachoc/Gravity_V202211.csv"



cols_utiles = ["year", "iso3_o", "iso3_d", "distw_harmonic", "contig", "comlang_off", "gdp_ppp_pwt_o", "gdp_ppp_pwt_d","comrelig","comcol"]



comparaison = pd.read_csv(
    url, 
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
