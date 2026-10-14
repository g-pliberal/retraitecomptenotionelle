# M@rel et Oscar, lus et classés ; la campagne 2025 de l'EACR, pas encore publiée

**Le 14 octobre 2026 : deux des pistes non vérifiées du registre sont
fermées, et la troisième chose qui restait attend la DREES.**

- *La demande.* Les pistes que la recherche du 1er octobre n'avait pas
  vérifiées, pour M@rel et Oscar : les trouver, les lire, les classer au
  registre (`data/reference/referents.yaml`). Puis confronter la campagne
  2025 de l'EACR comme les notes du 11 octobre l'ont fait de la campagne
  2024.
- *M@rel entre au registre (`marel`), pour son moteur.* Le registre écartait
  les simulateurs comme sources d'application ; le moteur de « Mon
  estimation retraite » y entre comme celui de la Cnav (`moteur_cnav`) :
  calculateur, non public, résultats publiés. Ce qu'on en lit :
  - le document n° 4 du COR (séance du 6 juillet 2016, `doc-3565`), écrit
    par l'Union Retraite, est la seule description publiée de ses
    projections. L'ancien M@rel se remplissait à la main et prenait les
    hypothèses du PLFSS sur quatre ans puis le scénario central du COR ; son
    successeur part d'un simulateur des seuls salariés d'un groupe
    Agirc-Arrco (lancé en mai 2016, base reconstituée et complémentaire
    réelle), lit la carrière des régimes et en prolonge la situation
    présente, le revenu croissant de 1,5 % par an (« comme l'inflation »),
    sans distinction de catégorie ;
  - le rapport d'activité 2023 de l'Union Retraite : 8 500 règles de calcul,
    quatre mises à jour en douze mois pour la réforme du 14 avril 2023 (en
    ligne le 12 juin, puis le 6 décembre), deux opérateurs de production,
    l'Agirc-Arrco et l'Assurance retraite, 25,8 millions de simulations en
    2023 ;
  - l'audition du directeur de l'Union Retraite au COR (28 janvier 2021) :
    3,3 millions de simulations en 2019, le « M@rel en 1 clic ».
  Rien ne se confronte : FranceConnect, la carrière réelle, ni règles ni
  sorties publiées. Ce qu'il fait mieux, plusieurs âges de départ côte à
  côte (« Ajouter un âge de départ »), est déjà au chantier 138.10, avec
  Oscar. Le registre compte désormais 70 modèles, 48 en France.
- *Oscar : rien depuis 2020.* Ni les documents du COR sur ses cas types (21
  avril 2022, n° 7 ; 25 mai 2023) ni l'annexe « pensions » au PLF 2025 ne le
  nomment. L'annexe nomme Pablo, la microsimulation du SRE, pour ses
  prévisions, le compte général de l'État et l'effet de la réforme de 2023
  (p. 40 et 197 du PDF) ; les cas types de fonctionnaires du COR
  s'établissent sur les comptes individuels de retraite du SRE (travaux de
  2013), sans outil nommé. Sa ligne le dit, relue le 14 octobre ; ses deux
  avantages (138.10, 138.14) restent.
- *La campagne 2025 de l'EACR n'est pas publiée.* Le jeu de la DREES
  (`donnes_eacr`) porte toujours la version du 26 mai 2026, que le dépôt
  lit déjà : `scripts/fetch/drees_eacr.py`, relancé, redonne les liquidants
  de 2023 à 17,9 % au minimum contributif (campagne 2024) et ceux de 2024 à
  17,4 % (`mico_estimation_drees`). La documentation de l'enquête (version
  du 18 mai 2026) en dit le calendrier : lancée en avril ou mai, réponses
  pour la fin septembre, puis contrôles ; la campagne 2025 a donc été
  collectée en 2026 et paraîtra au printemps 2027, si l'usage se tient.
  Rien n'a changé au dépôt.
- *Ce qui reste.* La campagne 2025, au printemps 2027 : relancer le
  récupérateur et `scripts/verifier_donnees.py`, puis
  `scripts/part_minimum_contributif.py`, et relire contre la grille élargie
  la ligne de 2024 qu'elle remplacera (+10,1 points contre l'estimation),
  ainsi que l'effet de la réforme de 2023 de 2023 à 2024. Les autres pistes
  non vérifiées du 1er octobre (Aphrodite et Osiris aujourd'hui, les
  sections libérales, l'IRCEC, la CAVIMAC, le Pension Adequacy Report, la
  Russie, la Mongolie, l'Azerbaïdjan, l'Égypte) ; les `referents` des
  fiches, à leur relecture.
