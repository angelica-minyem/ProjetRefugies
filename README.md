# Projet Python pour la Data Science

_Auteurs : Angélica MINYEM MI NGUI, Alexandre BÉGUEC, Daniel CHITOROG (2026)._

## Sujet : Déterminants du choix du pays de destination des demandeurs d'asile d'Asie du Sud (2017–2020)

Les déplacements forcés de populations constituent un enjeu géopolitique et humanitaire majeur. Parmi les grandes régions émettrices mondiales, l'Asie du Sud occupe une place singulière entre 2017 et 2020 : marquée par des crises prolongées, elle combine un volume élevé de nouvelles demandes d'asile et une forte diversité de pays de destination à l'échelle mondiale. La période **2017–2020** permet d'observer les déterminants structurels de ces flux avant les ruptures liées à la crise sanitaire puis aux bouleversements géopolitiques de 2021.

**Problématique** : Quels sont les facteurs géographiques, économiques et culturels qui déterminent le choix du pays de destination des demandeurs d'asile originaires d'Asie du Sud ?

Dans cette étude, nous mesurons les flux migratoires à partir des **nouvelles demandes d'asile** enregistrées annuellement par l'UNHCR (`PT == "ASY"`), et l'attractivité relative de chaque pays d'accueil par la **part des demandes d'asile** qui s'y dirige (`destination_share`).

## Données

Nous croisons deux sources de données publiques :
- **Pays et régions d'origine (UNHCR)** : récupération automatisée des noms de pays, codes ISO alpha-3 et régions du monde via l'API publique de l'UNHCR ('https://api.unhcr.org/population/v1/countries').
- **Variables bilatérales géographiques, économiques et culturelles (CEPII Gravity, 2017–2020)** : extraction des variables de distance harmonique pondérée (`distw_harmonic`), PIB par habitant en PPA (`gdpcap_d`, `gdpcap_o`), frontière commune (`contig`), langue officielle commune (`comlang_off`), proximité religieuse (`comrelig`) et passé colonial (`col_dep_ever`).
- **Fond de carte mondial (Natural Earth)** : fichier vectoriel (`ne_110m_admin_0_countries.shp`) pour la cartographie des flux.

Le nettoyage comprend l'harmonisation des types, la suppression des doublons CEPII après jointure (sélection de l'observation la plus complète via `na_count`) et le calcul de la variable `destination_share`.

## Démarche et analyses

Le rapport suit une progression en trois étapes :
1. **Diagnostic macroscopique** : comparaison des régions du monde selon le volume de demandes d'asile et la diversité des destinations (graphiques Plotly), justifiant le choix de l'Asie du Sud.
2. **Exploration et cartographie de l'Asie du Sud** : carte mondiale des principaux flux cumulés (2017–2020, seuil $\ge 5\,000$ demandes) avec GeoPandas, profil des 9 pays de la région et répartition annuelle du top 5 des destinations.
3. **Analyse des déterminants** :
   - **Distance géographique (`distw_harmonic`)** : régression linéaire simple puis modèle log-log (`scikit-learn`), mise en perspective du faible $R^2$ avec la littérature (spécificité 'ASY' vs réfugiés de masse).
   - **Richesse du pays d'accueil (`gdpcap_d`)** : nuages de points et régression log-log.
   - **Facteurs culturels et frontaliers** : part des demandes dirigées vers un pays partageant une langue officielle (`comlang_off`), une frontière (`contig`) ou des liens historiques/religieux (`col_dep_ever`, `comrelig`).

## Structure du dépôt

- `main.ipynb` : notebook principal contenant l'ensemble de l'analyse, des visualisations et des interprétations.
- `donnees_UNHCR.py` : collecte des données UNHCR (API pays/régions + fichier Excel des demandes d'asile), nettoyage et export en `unhcr_df.parquet`.
- `donnees_CEPII.py` : extraction des variables bilatérales de la base *CEPII Gravity* (2017–2020), nettoyage et export en `cepii_df.parquet`.
- `analyse_preliminaire.py` : construction des tableaux macroscopiques par région et par pays d'Asie du Sud.
- `analyse.py` : jointure des bases (`south_asia`), calcul de `destination_share` et analyses économiques/historiques (PIB par habitant, lien colonial).
- `plots.py` : fonctions de visualisation (nuages de points Plotly, camemberts de destinations, carte des flux GeoPandas, régressions sur la distance).
- `requirements.txt` : liste des dépendances Python nécessaires à la reproduction du projet.

## Reproduction du projet

1. Cloner le dépôt :
   ```bash
   git clone [https://github.com/angelica-minyem/ProjetRefugies.git](https://github.com/angelica-minyem/ProjetRefugies.git)
   cd ProjetRefugies
   ```
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Ouvrir `main.ipynb` et exécuter toutes les cellules (*Restart & Run All*). Les données pré-nettoyées (`unhcr_df.parquet`, `cepii_df.parquet`, `destination_shares.parquet`) ainsi que le fond de carte sont chargés automatiquement depuis le stockage public SSP Cloud.
