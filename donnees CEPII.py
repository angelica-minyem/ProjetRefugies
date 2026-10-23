import pandas as pd



countries = "https://minio.lab.sspcloud.fr/carcachoc/Countries_V202211.csv"
url = "https://minio.lab.sspcloud.fr/carcachoc/Gravity_V202211.csv"



cols_utiles = ["year", "iso3_o", "iso3_d", "distw_harmonic", "contig", "comlang_off", "gdp_ppp_pwt_o", "gdp_ppp_pwt_d","comrelig","comcol"]



cepii_df = pd.read_csv(
    url, 
    usecols=cols_utiles,
    low_memory=False
)



cepii_df = cepii_df[cepii_df["year"] == 2017]
cepii_df=cepii_df[cepii_df["iso3_o"]!=cepii_df["iso3_d"]]

cepii_df['contig'] = cepii_df['contig'].replace(0, False)
cepii_df['comlang_off'] = cepii_df['comlang_off'].replace(0, False)
cepii_df['comcol'] = cepii_df['comcol'].replace(0, False)
cepii_df['contig'] = cepii_df['contig'].replace(1, True)
cepii_df['comlang_off'] = cepii_df['comlang_off'].replace(1, True)
cepii_df['comcol'] = cepii_df['comcol'].replace(1, True)
print(cepii_df)
