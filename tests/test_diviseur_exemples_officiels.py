"""Le diviseur éprouvé sur les exemples officiels de six comptes étrangers.

Action 138, étape 11 (registre, chantier 138.11). Chaque pays publie, avec ses
diviseurs, la table de mortalité qui les fait : on la lit à sa source, on la
donne au diviseur du dépôt (``diviseur_de_courbe``, et son jumeau
``diviseurDeCourbe``), et l'on confronte le résultat au chiffre publié. Un
écart se comprend avant de se corriger ; ici, il n'en reste aucun qui ne
s'explique.

* **Finlande** (mémo de l'ETK du 26 octobre 2023, ``eak2024.pdf``, annexe 1,
  lu le 14 octobre 2026) : EAL2009 = 16,778288 et EAL2024 = 17,718722, au taux
  de 2 %, de 62 à 100 ans. La formule de l'ETK est celle du dépôt : survie
  moyenne de l'année, actualisée en son milieu. Exact au millionième.
* **Pologne** (communiqué du président du GUS du 25 mars 2026, sa table en
  mois ; table D, « Tablica trwania życia dla obu płci łącznie w 2025 r. »,
  publiée le 27 juillet 2026, lus le 14 octobre 2026) : 222,7 mois à 65 ans.
  Sans actualisation, le diviseur du dépôt est l'espérance de vie du GUS, à
  l'intervalle ouvert de 100 ans près, que la table close par ``T100/l100``.
  Le communiqué arrondit l'espérance au centième d'année AVANT de la
  multiplier par douze : sans cet arrondi, 222,76 mois donneraient 222,8.
  Ses trente et un âges ronds, de 60 à 90 ans, se refont tous au dixième de
  mois, sauf 64 ans, où l'arrondi tombe sur le fil : les colonnes en entiers
  de la table D y donnent 19,30515 ans, l'espérance refaite de ses quotients
  19,30485 ; 231,7 mois au communiqué, 231,6 au dépôt.
* **Suède** (PFS 2026:2, décidée le 2 septembre 2026, génération 1960 ; SCB,
  ``LivslangdFemarigA``, « totalt », risques de 2020-2024, lus le 14 octobre
  2026) : 19,13 à 62 ans, 17,34 à 65 ans. Le diviseur suédois est la valeur de
  douze mensualités versées d'avance (SFB 62:36), la survie linéaire dans
  l'année, au taux de 1,6 % ; celui du dépôt, une rente continue. Il est donc
  plus court d'un vingt-quatrième d'année, à 0,1 % près : 17,298 contre 17,34.
  La formule suédoise, écrite ici, refait la grille au centième de 62 à 103
  ans ; au-delà, elle lit la mortalité d'après 110 ans, que SCB ne publie pas,
  et la PFS borne le diviseur à 1,00.
* **Italie** (Nota tecnica du décret du 20 novembre 2024, tableaux A et C.2,
  lue le 14 octobre 2026) : le diviseur à 65 ans, 19,049, est la moyenne des
  deux sexes de deux termes, la pension directe, 17,590, et la réversion,
  1,460. Le second, la réversion tarifée dans le diviseur, est un choix du
  programme que le propriétaire tranche (registre, ``a_trancher``) : seul le
  premier s'éprouve ici. L'Italie le compte en annuité annuelle d'avance au
  taux de 1,5 %, moins ``k = 0,4615`` pour treize mensualités d'avance ; la
  rente continue du dépôt vaut l'annuité moins un demi : elle est plus courte
  de 0,5 − 0,4615 = 0,0385 an, à 0,004 près. La formule italienne, écrite ici,
  refait les deux sexes et leur moyenne au millième, de 57 à 71 ans (six
  dix-millièmes au plus, les quotients étant publiés à sept décimales).
* **Lettonie** (VSAA, table G du 1er janvier 2026 ; CSB, tables IRP030 et
  IRP020 de 2024, lues le 14 octobre 2026) : 17,76 à 65 ans. La table G
  recopie l'espérance de vie du moment, deux sexes, de 2024 (IRP030), et non
  une espérance de génération ; sans actualisation, le diviseur du dépôt la
  refait au centième aux âges ronds sur la table abrégée (IRP020), la
  mortalité constante entre deux âges publiés, l'intervalle ouvert de 90 ans
  clos par la table G elle-même (4,05). Entre eux, la table G
  interpole l'espérance en ligne droite. La table abrégée ne dit pas la
  mortalité d'entre deux âges ronds : le dépôt ne s'y éprouve pas, et
  l'écart que la convexité de l'espérance donne à G, un peu trop long, est
  au registre.
* **Norvège** (NAV, ``Delingstall.xlsx``, publié le 26 juin 2026 ; forskrift
  2009-12-22-1810, vedlegg, formules 1 à 4 ; SSB, table 07902, « Begge
  kjønn », lus le 14 octobre 2026) : la grille entière de la génération 1965,
  20,41 à 62 ans, mois par mois jusqu'à 75 ans. La formule (4), écrite ici,
  la refait au centième, chacun de ses 157 nombres. Elle diffère de celle du
  dépôt de deux façons : l'escompte de 0,9925 par année entière, et non au
  milieu de l'année, soit 0,9925^½ exactement ; le gain d'héritage, la survie
  à l'âge de départ rapportée à la survie moyenne de 27 à 66 ans (0,964 à 62
  ans), choix du programme que le registre garde ``a_trancher``.

Ce que ces écarts disent au dépôt : le terme des versements. La pension
française se paie par mois à terme échu (R. 355-2 du code de la sécurité
sociale) ; le diviseur exact serait l'annuité moins 13/24 d'année, et non la
rente continue. Le registre le garde ``a_trancher`` : le README définit le
diviseur comme l'espérance de vie restante, que le dépôt calcule exactement.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from retraite_notionnelle.moteur.conversion import diviseur_de_courbe

RACINE = Path(__file__).resolve().parents[1]


def _lire(texte: str) -> list[float]:
    return [float(x) for x in texte.split()]


# ---------------------------------------------------------------------------
# Les tables, lues à leur source
# ---------------------------------------------------------------------------

#: SCB, risques de décès en pour mille, deux sexes, 2020-2024, de 62 à 110 ans.
SUEDE_RISQUES_2020_2024 = _lire("""
    5.59 6.38 7.19 7.90 8.82 9.80 10.76 12.06 13.10 14.62 16.20 17.96 20.03
    22.29 24.63 27.97 31.67 35.45 39.56 45.16 51.27 58.49 66.68 75.89 84.83
    97.93 112.09 126.15 143.52 161.60 179.67 202.32 222.65 240.67 263.58
    287.99 313.89 341.24 370.01 400.13 431.52 464.08 497.68 532.18 567.40
    603.14 639.14 675.13 710.80
""")

#: ETK, mémo eak2024.pdf, annexe 1 : risques en pour mille de 62 à 100 ans,
#: q100 = 1 000, pour 2009 (mortalité 2003-2007) et 2024 (2018-2022).
FINLANDE_RISQUES_2003_2007 = _lire("""
    9.59 10.29 11.05 12.31 13.02 13.69 15.26 16.54 18.40 20.32 21.98 25.28
    26.72 30.65 33.10 38.32 43.19 47.67 53.66 60.03 66.50 76.00 83.82 94.07
    106.44 117.49 130.85 149.96 162.49 188.32 202.56 225.06 238.53 257.39
    283.97 309.15 332.80 349.08 1000.00
""")

FINLANDE_RISQUES_2018_2022 = _lire("""
    7.62 7.95 9.25 9.95 10.76 11.36 13.09 13.90 15.30 16.54 18.51 20.20
    22.37 24.63 27.23 29.49 33.20 37.00 42.65 47.92 55.66 60.86 68.82 79.23
    89.89 102.84 113.40 127.12 146.89 167.55 186.73 206.36 229.71 251.56
    281.64 302.21 335.08 332.56 1000.00
""")

#: Nota tecnica, tableau A : probabilités de mort de 2023, de 57 à 119 ans.
ITALIE_HOMMES_2023 = _lire("""
    0.0047679 0.0051418 0.0055808 0.0061001 0.0067188 0.0074133 0.0082921
    0.0091737 0.0101843 0.0112657 0.0123808 0.0135255 0.0149923 0.0168331
    0.0188242 0.0210861 0.0229580 0.0255079 0.0271700 0.0298034 0.0334159
    0.0380877 0.0427315 0.0500621 0.0561440 0.0627106 0.0699165 0.0765799
    0.0860164 0.0981704 0.1128744 0.1278743 0.1452182 0.1650864 0.1861044
    0.2057569 0.2290189 0.2499055 0.2693988 0.2976836 0.3216615 0.3453783
    0.3696101 0.3998852 0.4357998 0.4696011 0.5039111 0.5384345 0.5728597
    0.6068779 0.6401860 0.6725058 0.7035823 0.7331983 0.7611755 0.7873800
    0.8117172 0.8341352 0.8546181 0.8731848 0.8898802 0.9047735 0.9179502
""")

ITALIE_FEMMES_2023 = _lire("""
    0.0026936 0.0028841 0.0032159 0.0035542 0.0038934 0.0043023 0.0046764
    0.0050852 0.0056979 0.0063450 0.0069262 0.0075227 0.0082550 0.0091926
    0.0103040 0.0117036 0.0131335 0.0147842 0.0165309 0.0188035 0.0213463
    0.0244716 0.0275714 0.0322113 0.0367799 0.0421512 0.0477931 0.0535917
    0.0618865 0.0724171 0.0842423 0.0976538 0.1124177 0.1298549 0.1466190
    0.1643034 0.1844927 0.2057978 0.2307524 0.2559014 0.2774486 0.2987334
    0.3235643 0.3545996 0.3943162 0.4263282 0.4590162 0.4921130 0.5253374
    0.5584056 0.5910349 0.6229601 0.6539399 0.6837584 0.7122365 0.7392341
    0.7646464 0.7884067 0.8104837 0.8308774 0.8496115 0.8667368 0.8823163
""")

#: GUS, table D de 2025, deux sexes : q_x de 60 à 99 ans ; à 100 ans,
#: l100 = 1 802 et T100 = 4 300, l'intervalle ouvert.
POLOGNE_2025 = _lire("""
    0.00923 0.01014 0.01114 0.01231 0.01355 0.01486 0.01624 0.01764 0.01907
    0.02058 0.02218 0.02393 0.02586 0.02799 0.03036 0.03304 0.03598 0.03929
    0.04301 0.04722 0.05206 0.05757 0.06386 0.0712 0.07955 0.08896 0.0993
    0.11068 0.12259 0.13529 0.14856 0.16265 0.17732 0.19296 0.2093 0.22628
    0.24373 0.2616 0.27994 0.29801
""")

POLOGNE_ESPERANCE_A_100 = 4300 / 1802

#: PFS 2026:2, § 1, génération 1960, de 62 à 103 ans.
PFS_2026_2 = dict(zip(range(62, 104), _lire("""
    19.13 18.53 17.93 17.34 16.75 16.15 15.56 14.96 14.37 13.78 13.19 12.61
    12.02 11.45 10.87 10.30 9.75 9.20 8.66 8.13 7.62 7.12 6.64 6.18 5.74 5.31
    4.92 4.55 4.20 3.88 3.59 3.32 3.08 2.86 2.65 2.45 2.26 2.09 1.93 1.79 1.65
    1.53
""")))

#: Nota tecnica, tableau C.2 : le terme de la pension directe (« dante
#: causa »), hommes, femmes, total, de 57 à 71 ans.
ITALIE_C2_DIRECTE = {57: (21.266, 23.534, 22.400), 58: (20.678, 22.942, 21.810),
                     59: (20.086, 22.344, 21.215), 60: (19.490, 21.743, 20.616),
                     61: (18.892, 21.137, 20.015), 62: (18.294, 20.528, 19.411),
                     63: (17.695, 19.916, 18.805), 64: (17.098, 19.299, 18.198),
                     65: (16.502, 18.677, 17.590), 66: (15.908, 18.055, 16.981),
                     67: (15.316, 17.431, 16.374), 68: (14.726, 16.804, 15.765),
                     69: (14.136, 16.173, 15.155), 70: (13.550, 15.540, 14.545),
                     71: (12.971, 14.906, 13.939)}
ITALIE_K = 0.4615

#: Le communiqué du GUS, en mois, aux âges ronds de 60 à 90 ans (la colonne
#: des mois révolus « 0 », relue en entier le 18 octobre 2026, action 89).
GUS_2026 = dict(zip(range(60, 91), _lire("""
    268.9 259.4 250.0 240.7 231.7 222.7 214.1 205.4 197.0 188.8 180.6 172.6
    164.6 156.8 149.2 141.7 134.3 127.1 120.0 113.2 106.4 100.0 93.7 87.7
    82.0 76.6 71.5 66.7 62.3 58.1 54.2
""")))

#: Table D de 2025, à 64 ans, ses colonnes en entiers : l64 = 86 256 et T64 =
#: 1 665 185. Leur rapport, 19,30515 ans, passe le seuil de 19,305 où
#: l'espérance refaite des quotients publiés, 19,30485, reste en deçà : 231,7
#: mois au communiqué, 231,6 au dépôt. Un arrondi sur le fil, non une règle.
GUS_ARRONDI_SUR_LE_FIL = 64
POLOGNE_L64, POLOGNE_T64 = 86_256, 1_665_185

#: CSB, table IRP020 de 2024, deux sexes : survivants à 40, 45, …, 90 ans,
#: sur 100 000 naissances (la table abrégée ne publie que ces âges).
LETTONIE_SURVIVANTS_2024 = dict(zip(range(40, 95, 5), _lire("""
    96931 95286 93022 89781 85247 79590 71910 62017 50060 35151 19366
""")))

#: VSAA, « G no 2026. gada 1. janvāra », de 40 à 90 ans : la table IRP030 de
#: 2024 du CSB, recopiée.
LETTONIE_G_2026 = dict(zip(range(40, 91), _lire("""
    37.87 37.00 36.12 35.24 34.36 33.48 32.64 31.79 30.94 30.09 29.24 28.43
    27.63 26.82 26.01 25.20 24.45 23.69 22.93 22.17 21.41 20.68 19.95 19.22
    18.49 17.76 17.09 16.41 15.74 15.07 14.39 13.78 13.16 12.54 11.92 11.30
    10.73 10.15 9.58 9.00 8.42 7.94 7.45 6.97 6.48 6.00 5.61 5.22 4.83 4.44
    4.05
""")))

#: SSB, table 07902, « Begge kjønn », quotients de décès en pour mille ; de
#: 27 à 59 ans, les deux années où la génération 1965 a cet âge, x et x + 1
#: (formule 1a) : à 27 ans, 1992 et 1993, …, à 59 ans, 2024 et 2025.
NORVEGE_1965_AVANT_60 = _lire("""
    0.816 0.571 0.547 0.773 0.884 0.568 0.647 0.668 0.689 0.594 0.659
    0.693 0.934 0.72 0.887 0.832 1.16 0.974 1.115 0.801 1.171 0.984 0.909
    0.954 1.211 1.038 1.338 0.935 1.047 0.986 1.084 1.035 1.488 1.446
    1.227 1.315 1.306 1.544 1.649 1.688 1.741 1.602 1.821 1.763 2.014
    1.927 1.945 1.942 2.073 2.205 2.16 2.044 2.459 2.144 2.812 2.518 2.762
    2.979 3.065 2.831 3.692 3.289 3.554 3.666 4.081 3.986
""")

#: Même table, de 60 à 106 ans, les dix années 2016 à 2025 (formule 1b) ;
#: SSB clôt sa table à 106 ans par un quotient de 1 000 ‰.
NORVEGE_2016_2025 = {
    2016: _lire("""
        5.428 6.242 6.424 7.106 7.803 9.012 9.871 10.733 11.646 13.847
        13.564 15.745 17.187 18.983 21.341 22.807 25.729 29.522 33.704
        37.848 41.572 47.895 55.124 63.518 68.998 76.888 92.256
        103.601 116.937 126.744 143.686 162.585 182.516 208.354
        220.325 246.788 282.559 286.014 313.328 345.39 352.197 393.469
        463.768 441.119 409.905 396.945 1000
    """),
    2017: _lire("""
        5.099 5.316 5.833 7.102 7.214 8.213 9.739 10.512 11.55 12.82
        13.64 15.216 17.422 19.569 20.592 23.715 24.647 29.04 34.406
        36.717 43.296 49.972 52.34 58.016 70.698 78.264 91.855 101.788
        111.308 133.708 149.397 162.442 183.244 197.537 225.354
        262.671 272.354 284.816 303.136 325.56 348.84 406.725 325.12
        343.229 385.393 404.598 1000
    """),
    2018: _lire("""
        4.954 5.501 6.067 6.53 7.808 7.8 9.011 10.011 11.126 12.664
        13.609 14.952 17.43 17.217 19.604 24.109 24.345 28.61 34.2
        38.365 40.493 47.426 52.771 63.003 69.308 72.211 87.089 99.909
        113.82 133.515 144.83 158.953 184.241 189.165 224.318 256.812
        265.926 287.246 316.59 341.352 372.793 343.38 435.282 400.554
        471.809 428.791 1000
    """),
    2019: _lire("""
        4.429 5.545 6.363 7.279 6.901 8.528 8.503 9.433 9.46 12.33
        12.808 15.335 16.626 19.172 20.006 24.054 24.684 28.769 29.923
        36.579 38.917 45.568 50.149 62.227 68.763 74.578 84.197 97.961
        114.178 118.071 141.604 163.364 177.57 194.977 213.39 232.757
        265.044 306.011 302.488 322.707 389.038 370.896 366.797
        293.778 443.325 421.53 1000
    """),
    2020: _lire("""
        4.745 4.768 5.707 6.489 6.622 7.383 8.897 9.959 10.358 11.474
        12.77 14.522 16.358 18.207 20.442 22.016 23.651 27.273 30.835
        33.893 40.837 42.252 51.857 57.549 67.101 77.218 79.175 93.348
        108.576 128.116 139.366 151.606 175.049 193.602 217.244
        233.833 255.681 296.508 308.996 327.849 376.308 334.25 362.872
        387.494 365.994 351.071 1000
    """),
    2021: _lire("""
        4.174 4.783 5.354 6.884 7.345 8.262 8.842 9.274 9.562 11.335
        12.773 14.932 16.297 18.243 19.841 22.995 24.246 28.988 31.335
        35.783 36.219 45.939 51.744 58.247 67.637 72.857 88.623
        101.061 112.998 127.104 139.634 151.017 184.976 194.186
        216.729 235.58 259.56 287.862 307.228 358.301 379.669 379.68
        380.37 455.476 380.37 351.071 1000
    """),
    2022: _lire("""
        4.525 5.502 5.719 6.532 7.134 7.905 9.517 9.871 10.209 12.811
        12.761 15.209 17.328 18.666 21.271 24.926 27.026 30.844 33.225
        36.422 40.365 46.205 52.563 63.322 70.715 80.073 91.162
        102.051 122.192 137.837 153.311 168.6 196.981 213.149 244.968
        265.333 299.033 313.852 342.985 342.265 397.469 409.788
        454.162 474.017 438.276 499.291 1000
    """),
    2023: _lire("""
        4.346 4.865 5.492 6.21 6.731 7.968 8.448 9.946 10.217 11.662
        12.176 14.466 15.386 18.136 20.24 22.244 25.232 27.628 32.114
        35.833 38.215 46.712 50.025 56.899 67.104 73.836 86.576 96.424
        109.994 126.731 141.139 157.837 183.432 206.972 220.45 244.444
        284.257 293.192 298.802 330.081 374.503 436.309 405.129
        432.327 414.074 304.856 1000
    """),
    2024: _lire("""
        4.579 5.331 4.952 5.555 6.794 7.62 8.661 9.828 10.195 12.076
        13.054 14.654 15.469 16.472 19.987 22.43 25.382 27.049 31.633
        35.151 40.127 44.195 51.537 53.823 63.854 75.669 85.9 93.638
        109.757 120.927 139.813 158.802 178.325 200.71 227.716 236.217
        269.245 301.905 309.326 342.327 338.36 405.857 423.829 410.395
        398.958 404.935 1000
    """),
    2025: _lire("""
        4.815 4.761 5.32 6.576 6.196 7.212 8.351 9.275 9.749 11.754
        11.978 14.282 16.201 17.663 20.204 22.593 23.502 27.231 31.427
        37.71 39.501 47.027 52.703 60.923 63.442 74.818 84.626 97.92
        108.241 125.171 142.731 166.43 175.182 191.403 232.345 250.634
        283.903 307.014 304.856 331.719 349.922 391.765 437.858
        435.282 338.862 459.567 1000
    """),
}

#: NAV, Delingstall.xlsx, feuille « Delingstall », publiée le 26 juin 2026 :
#: la génération 1965, de 62 ans et 0 mois à 75 ans et 0 mois, mois par mois.
NAV_1965 = _lire("""
    20.41 20.34 20.27 20.21 20.14 20.07 20.00 19.93 19.87 19.80 19.73
    19.66 19.59 19.53 19.46 19.39 19.32 19.26 19.19 19.12 19.05 18.98
    18.92 18.85 18.78 18.71 18.64 18.58 18.51 18.44 18.37 18.31 18.24
    18.17 18.10 18.03 17.97 17.90 17.83 17.76 17.70 17.63 17.56 17.49
    17.42 17.36 17.29 17.22 17.15 17.09 17.02 16.95 16.88 16.82 16.75
    16.68 16.61 16.55 16.48 16.41 16.34 16.28 16.21 16.14 16.07 16.01
    15.94 15.87 15.80 15.74 15.67 15.60 15.53 15.47 15.40 15.33 15.27
    15.20 15.13 15.06 15.00 14.93 14.86 14.80 14.73 14.66 14.60 14.53
    14.46 14.40 14.33 14.26 14.20 14.13 14.06 14.00 13.93 13.86 13.80
    13.73 13.66 13.60 13.53 13.47 13.40 13.33 13.27 13.20 13.13 13.07
    13.00 12.94 12.87 12.81 12.74 12.67 12.61 12.54 12.48 12.41 12.35
    12.28 12.22 12.15 12.09 12.02 11.96 11.89 11.83 11.76 11.70 11.63
    11.57 11.50 11.44 11.37 11.31 11.24 11.18 11.12 11.05 10.99 10.92
    10.86 10.79 10.73 10.67 10.60 10.54 10.48 10.41 10.35 10.29 10.22
    10.16 10.10 10.03
""")


def _courbe(risques: list[float], premier_age: int, age: int, echelle: float = 1.0) -> list[float]:
    """Les survies depuis ``age``, ``l_(x+1) = l_x (1 − q_x)``, jusqu'au bout de
    la table."""
    courbe = [1.0]
    for q in risques[age - premier_age:]:
        courbe.append(courbe[-1] * (1.0 - q / echelle))
    return courbe


def _finlande(risques: list[float]) -> list[float]:
    return _courbe(risques, 62, 62, 1000.0)


def _suede(age: int) -> list[float]:
    return _courbe(SUEDE_RISQUES_2020_2024, 62, age, 1000.0)


def _italie(risques: list[float], age: int) -> list[float]:
    return _courbe(risques, 57, age)


def _pologne(age: int) -> list[float]:
    return _courbe(POLOGNE_2025, 60, age)


def _survivant_letton(age: int) -> float:
    """Le survivant de la table abrégée à un âge quelconque de 40 à 90 ans :
    la force de mortalité constante entre deux âges publiés."""
    if age >= 90:
        return LETTONIE_SURVIVANTS_2024[90]
    debut = age - (age - 40) % 5
    l0, l5 = LETTONIE_SURVIVANTS_2024[debut], LETTONIE_SURVIVANTS_2024[debut + 5]
    return l0 * (l5 / l0) ** ((age - debut) / 5)


def _lettonie(age: int) -> list[float]:
    """La survie depuis ``age``, d'année en année jusqu'à 90 ans."""
    return [_survivant_letton(x) / _survivant_letton(age) for x in range(age, 91)]


def _esperance_lettone(diviseur: float, courbe: list[float]) -> float:
    """Le diviseur, clos à 90 ans par l'intervalle ouvert, que la table G
    elle-même donne (4,05)."""
    return diviseur + courbe[-1] * LETTONIE_G_2026[90]


def _quotient_norvegien(age: int) -> float:
    """Forskrift 2009-12-22-1810, vedlegg, formules (1a) et (1b), pour la
    génération 1965 : la moyenne des deux années de l'âge jusqu'à 59 ans, des
    dix années 2016 à 2025 ensuite ; 1 où SSB ne publie rien."""
    if age <= 59:
        i = 2 * (age - 27)
        return (NORVEGE_1965_AVANT_60[i] + NORVEGE_1965_AVANT_60[i + 1]) / 2000
    if age > 106:
        return 1.0
    return sum(annee[age - 60] for annee in NORVEGE_2016_2025.values()) / 10000


def _survie_norvegienne() -> dict[int, float]:
    """Formule (2) : la survie de la génération 1965 depuis 27 ans."""
    survie = {27: 1.0}
    for age in range(28, 108):
        survie[age] = survie[age - 1] * (1.0 - _quotient_norvegien(age - 1))
    return survie


def _norvege(age: int) -> list[float]:
    survie = _survie_norvegienne()
    return [survie[x] / survie[age] for x in range(age, 108)]


#: Le taux qu'implique le facteur de 0,9925 par an de la formule (4).
NORVEGE_TAUX = 1 / 0.9925 - 1


def _cas() -> dict[str, tuple[list[float], float]]:
    """Chaque courbe et son taux, sous un nom, pour les deux moteurs."""
    cas = {"fi_2009": (_finlande(FINLANDE_RISQUES_2003_2007), 0.02),
           "fi_2024": (_finlande(FINLANDE_RISQUES_2018_2022), 0.02)}
    cas.update({f"se_{age}": (_suede(age), 0.016) for age in PFS_2026_2})
    for age in ITALIE_C2_DIRECTE:
        cas[f"it_h_{age}"] = (_italie(ITALIE_HOMMES_2023, age), 0.015)
        cas[f"it_f_{age}"] = (_italie(ITALIE_FEMMES_2023, age), 0.015)
    cas.update({f"pl_{age}": (_pologne(age), 0.0) for age in GUS_2026})
    cas.update({f"lv_{age}": (_lettonie(age), 0.0) for age in range(40, 90, 5)})
    cas.update({f"no_{age}": (_norvege(age), NORVEGE_TAUX) for age in range(62, 76)})
    return cas


def _python() -> dict[str, float]:
    return {nom: diviseur_de_courbe(courbe, taux) for nom, (courbe, taux) in _cas().items()}


@pytest.fixture(scope="module")
def deux_moteurs() -> dict[str, dict[str, float]]:
    """Le diviseur de chaque cas, par le Python et par le portage."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    entree = json.dumps({nom: [courbe, taux] for nom, (courbe, taux) in _cas().items()})
    script = ('import { diviseurDeCourbe } from "./moteur/js/conversion.js";'
              f"const cas = {entree};"
              "const sortie = {};"
              "for (const [nom, [courbe, taux]] of Object.entries(cas))"
              " sortie[nom] = diviseurDeCourbe(courbe, taux);"
              "console.log(JSON.stringify(sortie));")
    sortie = subprocess.run(["node", "--input-type=module", "-e", script], cwd=RACINE,
                            capture_output=True, text=True, encoding="utf-8", check=True)
    return {"python": _python(), "javascript": json.loads(sortie.stdout)}


def test_les_deux_moteurs_rendent_le_meme_diviseur(deux_moteurs):
    python, javascript = deux_moteurs["python"], deux_moteurs["javascript"]
    assert python.keys() == javascript.keys()
    for nom, valeur in python.items():
        assert javascript[nom] == pytest.approx(valeur, rel=1e-13), nom


# ---------------------------------------------------------------------------
# Finlande : la formule même du dépôt
# ---------------------------------------------------------------------------

def test_la_finlande_au_millionieme(deux_moteurs):
    """EAL2009 et EAL2024, au millionième, et le coefficient qui s'en tire."""
    for moteur in deux_moteurs.values():
        assert round(moteur["fi_2009"], 6) == 16.778288
        assert round(moteur["fi_2024"], 6) == 17.718722
        assert round(round(moteur["fi_2009"], 6) / round(moteur["fi_2024"], 6), 5) == 0.94692


# ---------------------------------------------------------------------------
# Pologne : l'espérance de vie, arrondie au centième d'année
# ---------------------------------------------------------------------------

def _mois_gus(diviseur: float, courbe: list[float]) -> float:
    """Le diviseur, clos par l'intervalle ouvert de 100 ans, en mois, comme le
    communiqué l'écrit : l'espérance arrondie au centième d'année, puis par
    douze, au dixième."""
    esperance = diviseur + courbe[-1] * POLOGNE_ESPERANCE_A_100
    return round(round(esperance, 2) * 12, 1)


def test_la_pologne_au_dixieme_de_mois(deux_moteurs):
    for moteur in deux_moteurs.values():
        for age, publie in GUS_2026.items():
            if age != GUS_ARRONDI_SUR_LE_FIL:
                assert _mois_gus(moteur[f"pl_{age}"], _pologne(age)) == publie, age
    # L'arrondi au centième d'année fait le dixième de mois : sans lui, 222,8.
    brut = deux_moteurs["python"]["pl_65"] + _pologne(65)[-1] * POLOGNE_ESPERANCE_A_100
    assert round(brut * 12, 1) == 222.8


def test_a_64_ans_l_arrondi_du_gus_tombe_sur_le_fil(deux_moteurs):
    """Les entiers de la table D passent 19,305 ans, l'espérance refaite de
    ses quotients non : le communiqué écrit 231,7 mois, le dépôt 231,6."""
    age = GUS_ARRONDI_SUR_LE_FIL
    gus = POLOGNE_T64 / POLOGNE_L64
    assert round(gus, 2) == 19.31 and round(round(gus, 2) * 12, 1) == GUS_2026[age]
    for moteur in deux_moteurs.values():
        refaite = moteur[f"pl_{age}"] + _pologne(age)[-1] * POLOGNE_ESPERANCE_A_100
        assert 19.3048 < refaite < 19.305 < gus < 19.3052
        assert _mois_gus(moteur[f"pl_{age}"], _pologne(age)) == 231.6


# ---------------------------------------------------------------------------
# Suède : douze mensualités d'avance
# ---------------------------------------------------------------------------

def _delningstal(courbe: list[float], taux: float = 0.016) -> float:
    """SFB 62:36, rapport orange, annexe A.8 : douze mensualités versées
    d'avance, la survie linéaire dans l'année."""
    total = 0.0
    for annee in range(len(courbe) - 1):
        for mois in range(12):
            survie = courbe[annee] + (courbe[annee + 1] - courbe[annee]) * mois / 12
            total += survie * (1.0 + taux) ** -(annee + mois / 12) / 12
    return total


def test_la_suede_au_centieme_par_sa_convention():
    for age, publie in PFS_2026_2.items():
        assert round(_delningstal(_suede(age)), 2) == publie, age


def test_le_diviseur_du_depot_est_plus_court_d_un_vingt_quatrieme_d_annee(deux_moteurs):
    """Rente continue contre mensualités d'avance : 1/24 d'année, que
    l'actualisation écorne d'un millième au plus."""
    for moteur in deux_moteurs.values():
        assert round(moteur["se_65"], 2) == 17.30
        for age, publie in PFS_2026_2.items():
            ecart = _delningstal(_suede(age)) - moteur[f"se_{age}"]
            assert ecart == pytest.approx(1 / 24, abs=0.002), age
            assert publie - moteur[f"se_{age}"] == pytest.approx(1 / 24, abs=0.007), age


# ---------------------------------------------------------------------------
# Italie : l'annuité d'avance moins k, le terme de la pension directe
# ---------------------------------------------------------------------------

def _annuite_italienne(courbe: list[float], taux: float = 0.015) -> float:
    """Nota tecnica, allegato tecnico : la somme des survies actualisées, de
    t = 0 à w − x, moins k."""
    return sum(survie * (1.0 + taux) ** -t for t, survie in enumerate(courbe)) - ITALIE_K


def test_l_italie_au_millieme_par_sa_convention():
    for age, (hommes, femmes, total) in ITALIE_C2_DIRECTE.items():
        h = _annuite_italienne(_italie(ITALIE_HOMMES_2023, age))
        f = _annuite_italienne(_italie(ITALIE_FEMMES_2023, age))
        # Les quotients publiés à sept décimales laissent un demi-millième.
        assert h == pytest.approx(hommes, abs=0.0006), age
        assert f == pytest.approx(femmes, abs=0.0006), age
        assert (h + f) / 2 == pytest.approx(total, abs=0.0006), age


def test_le_diviseur_du_depot_rend_la_pension_directe_moins_0_0385(deux_moteurs):
    """La rente continue vaut l'annuité d'avance moins un demi, à l'ordre près
    de l'actualisation ; l'Italie retire 0,4615."""
    for moteur in deux_moteurs.values():
        for age, (hommes, femmes, total) in ITALIE_C2_DIRECTE.items():
            depot = (moteur[f"it_h_{age}"] + moteur[f"it_f_{age}"]) / 2
            assert total - depot == pytest.approx(0.5 - ITALIE_K, abs=0.004), age
        assert round((moteur["it_h_65"] + moteur["it_f_65"]) / 2, 3) == 17.548


# ---------------------------------------------------------------------------
# Lettonie : l'espérance de vie du moment, interpolée entre les âges ronds
# ---------------------------------------------------------------------------

def test_la_lettonie_au_centieme_aux_ages_ronds(deux_moteurs):
    """Sans actualisation, le diviseur du dépôt est l'espérance de vie du CSB,
    sur la table abrégée de 2024, la mortalité constante entre deux âges
    publiés : au centième, de 40 à 85 ans, les survivants étant publiés à
    l'unité."""
    for moteur in deux_moteurs.values():
        for age in range(40, 90, 5):
            esperance = _esperance_lettone(moteur[f"lv_{age}"], _lettonie(age))
            assert esperance == pytest.approx(LETTONIE_G_2026[age], abs=0.01), age


def test_la_lettonie_interpole_entre_les_ages_ronds():
    """Entre deux âges ronds, la table G interpole l'espérance en ligne
    droite ; elle est publiée au centième, d'où le centième d'écart.
    L'espérance étant convexe en l'âge, la ligne droite l'allonge un peu."""
    for age, publie in LETTONIE_G_2026.items():
        debut = age - (age - 40) % 5
        if debut == age:
            continue
        pente = (LETTONIE_G_2026[debut + 5] - LETTONIE_G_2026[debut]) / 5
        assert publie == pytest.approx(LETTONIE_G_2026[debut] + pente * (age - debut), abs=0.01), age


# ---------------------------------------------------------------------------
# Norvège : la grille publiée de NAV, le gain d'héritage et l'escompte entier
# ---------------------------------------------------------------------------

def _gain_d_heritage(age: int) -> float:
    """La survie à l'âge de départ rapportée à la survie moyenne de 27 à 66
    ans."""
    survie = _survie_norvegienne()
    return survie[age] / (sum(survie[i] for i in range(27, 67)) / 40)


def _delingstall(age: int) -> float:
    """Formule (4) : le gain d'héritage, fois la survie moyenne de chaque
    année, escomptée de 0,9925 par année entière."""
    courbe = _norvege(age)
    return _gain_d_heritage(age) * sum(0.9925 ** t * (courbe[t] + courbe[t + 1]) / 2
                                       for t in range(len(courbe) - 1))


def test_la_norvege_au_centieme_par_sa_convention():
    """Les 157 diviseurs de la génération 1965, de 62 ans à 75 ans, mois par
    mois : chaque âge entier par la formule (4), chaque mois en ligne droite
    entre deux âges entiers. Tous au centième."""
    grille = iter(NAV_1965)
    for age in range(62, 76):
        for mois in range(12 if age < 75 else 1):
            debut = _delingstall(age)
            fin = _delingstall(age + 1) if mois else debut
            assert round(debut + (fin - debut) * mois / 12, 2) == next(grille), (age, mois)
    assert next(grille, None) is None


def test_le_diviseur_du_depot_rend_le_delingstall_sans_heritage(deux_moteurs):
    """Le dépôt escompte au milieu de l'année, NAV en son début : à taux égal,
    le facteur 0,9925^½ les sépare, exactement. Le gain d'héritage (0,964 à 62
    ans, 0,827 à 75 ans) est le reste ; il est au registre, ``a_trancher``."""
    for moteur in deux_moteurs.values():
        for age in range(62, 76):
            depot = moteur[f"no_{age}"] / 0.9925 ** 0.5
            assert depot * _gain_d_heritage(age) == pytest.approx(_delingstall(age), rel=1e-12), age
        assert round(moteur["no_62"], 2) == 21.09
        assert round(_gain_d_heritage(62), 3) == 0.964
