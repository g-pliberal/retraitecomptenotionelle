# Les salaires de 1930 à 1944 entrent au salaire annuel moyen

Le 22 novembre 2026, sur l'écart que la note du 20 novembre
(`2026-11-20-annees-des-assurances-sociales.md`) et celle du même jour sur le
salaire moyen d'avant juillet 1948 laissaient, et selon la règle du
propriétaire (« on corrige tout ce qui est faux »).

**L'écart.** Les années des assurances sociales comptaient à la durée du
régime général, pas à son salaire annuel moyen : leurs lignes allaient au
régime `assurances_sociales`, que `salaireDeReference` n'admettait pas. Une
pension liquidée avant 1960, dont les dix dernières années avant soixante ans
remontent avant 1945, se calculait sur les seules années d'après 1945.

**Lu.** La circulaire ministérielle n° 151 du 5 août 1946 (base de la Cnav,
CR_MIN_151_05081946), b), 1° : « il doit être procédé, pour la période du
1er juillet 1930 au 31 décembre 1944, à la revalorisation des salaires
correspondant aux cotisations versées [...]. Par mesure de simplification, les
cotisations seront directement revalorisées [...] 3 pour la période antérieure
au 31 décembre 1941 ; 2 pour les années 1942 et 1943 ; 1 pour l'année 1944 ».
L'arrêté du 14 mai 1946 n'est ni à l'index JORF de la DILA ni parmi les
fac-similés. La Cnav en publie la colonne, « Avant le 01/01/1949 », avec
toutes les suivantes, dans le tableau des cotisations d'avant 1947 de sa page
d'avant 2013 et de chaque édition du barème : 75,000 de 1930 à 1935 (25 fois
la cotisation, revalorisée par 3), 42,857 en 1936, 37,500 de 1937 à 1941,
25,000 en 1942 et 1943, 18,750 en 1944.

**Corrigé.** `scripts/fetch/cnav_revalorisation_cotisations.py` lit les
quatre-vingt-dix-huit colonnes, clées par date d'effet
(`legislation/revalorisation_cotisations_1930_1944.csv`), et corrige deux
coquilles de la page qu'il dit. Les coefficients de la circulaire sont dans
la version de la fiche `sam_annees_d_avant_1947`, que `FichesDatees` sert
désormais. `salaireDeReference` admet les lignes des régimes éteints que la
liquidation reprend (`regimesRepris`), et revalorise leur salaire par le
rapport de la colonne en vigueur à celle de 1946, multiplié par le
coefficient de la version (`coefficientDesAssurancesSociales`).

**Ce qui bouge.** Aucun des 935 témoins de simulation ; le coût des
avantages, de 0,1 milliard d'euros sur 213 (pages Coût et Avantages). Né en
1888, salarié au salaire moyen depuis 20 ans, parti à 62 ans au début de
1950 : les dix dernières années avant soixante ans, 1938 à 1947, comptent
désormais 1938 à 1944 ; salaire de référence de 366,49 € au lieu de
390,59 €, pension de 66,70 € au lieu de 71,09 € par an (28 %, 78/120), soit
6,2 % de moins. Né en 1890, parti à 65 ans en 1955 : 634,75 € au lieu de
637,12 €. Né en 1893, parti à 65 ans en 1958 : 832,14 € au lieu de 843,46 €.

**Les tests**, vus rouges : deux de `tests/test_salaire_annuel_moyen.py`,
posés à la main depuis la circulaire et les colonnes de la Cnav (une pension
de 1948, une de 1950), et leur portage dans `tests/js/moteur.test.js`.

**Relu sur Opus 5.5** (Fable 5.2 à sa limite jusqu'au 25 novembre), et repris :
la colonne d'avril 1958 (arrêté du 14 avril 1958) se perdait, la correction de
date du récupérateur des salaires la confondant avec celle de 1957 ; elle est
gardée, avec son test. Le même défaut, antérieur, ôte cette colonne à
`revalorisation_salaires_anciennes.csv` : les pensions d'avril 1958 à mars
1959 y lisent celle de 1957. Signalé, non touché.

**Reste.** L'arrêté du 14 mai 1946 au JO : il dira si 1936 et 1944 portent
bien les coefficients 3 et 1 de la circulaire (la fiche le déclare) ; 1945 et
1946, dont la caisse publie aussi des coefficients de cotisations, que le
modèle approche ; le salaire fictif des périodes assimilées d'avant août 1947.
