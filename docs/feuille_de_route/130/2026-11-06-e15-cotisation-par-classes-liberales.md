# Les écarts de R-E15 repris, et `cotisation_par_classes_liberales` lue au droit (E15)

File E, E15, le 6 novembre 2026 (action 130, vague 11, sur Opus), après E14 (5202765) et
sa relecture R-E15 (f9f425e). Index de la DILA récupérés ce jour : JORF à jour du
3 novembre 2026, LEGI du 2 novembre ; recherches en SQL sur toute la table `doc`, au
titre puis au texte, sans borne de réponses. Aucun taux, aucune valeur servie ne change ;
aucune erreur n'est corrigée.

## 1. Les écarts de R-E15 (`surcote_par_age_seul`, version `avant_2007`)

**(a) Les arrêtés de la CAVEC d'avant 2008.** Relus au JORF, de 1948 au 1er mars 2008
(titres « expert » et « compta », « commissaires aux comptes », puis les arrêtés de
statuts dont le texte nomme les experts-comptables). Les six de R-E15, depuis 1979, sont
bien ceux qui touchent le complémentaire, chacun relu : 17 juin 1980
(JORFTEXT000000680010, « ART. 52,55,57,58 ET 61 AU REGIME D'ASSURANCE VIEILLESSE
COMPLEMENTAIRE », « CES ARRETES SERONT PUBLIES AU BULLETIN OFFICIEL DU MINISTERE DE LA
SANTE ET DE LA SECURITE SOCIALE ») ; 22 août 1986 (JORFTEXT000000862986, « (ART. 47 ET 55
ANNEXE 2) ») ; 9 mars 1987 (JORFTEXT000000321565, « 4EME PARTIE,TITRES XVI (ART. 52) ET
XVII (ART. 57 ET 58) ») ; 23 juillet 1992 (JORFTEXT000000724876) ; 13 mai 1994
(JORFTEXT000000731984, titre seul) ; 27 février 2003 (JORFARTI000001710064, « (art. 58) »,
« publié intégralement au Bulletin officiel n° 2003-14 »). Une précision sur R-E15, qui
disait celui de 1992 « titre et mention seuls » : sa mention nomme les articles, « (art. 49
et 50) ». Avant 1979, l'index en porte dix autres, de 1961 à 1977, par leur seul titre
(8 novembre 1961, art. 57 ; 7 novembre 1962 ; 3 février 1964, art. 44 à 47, 49, 56, 57 à
59 et 61 ; 22 juin 1964, art. 62 ; 21 avril 1966, art. 61 et la suppression de l'art. 58 ;
12 décembre 1967 ; 23 décembre 1970, art. 60 ; 26 février 1974 ; 10 juin 1976 ; 25 mars
1977, JORFTEXT000000312784) ; aucun du 28 février 2003 au 21 février 2008. La fiche les
nomme (les six, et les dix en un mot), et renvoie ceux de 1986 à 1994 au fac-similé ou au
Bulletin officiel.

**(b) « un article 3.14 qui existait donc ».** Récrit à ce que disent les indices :
l'arrêté du 22 février 2008 approuve les articles « 3.1, 3.3, 3.4, […] 3.20 », sans 3.2
(JORFARTI000018197775, relu), et dit « L'article 3.14 est ainsi rédigé »
(JORFARTI000018197778, relu) : une numérotation en 3.x déjà en place, semble-t-il ; mais
l'arrêté de 2003 nomme encore l'« art. 58 », et le texte qui a introduit la numérotation,
avec ce que disait son article 3.14, n'est pas identifié. Le point non tranché de E14 n'en
change pas. La même tournure, à la CPRN (« « rédige » l'article 16 de ses statuts, qui
existait donc », version de 2014), n'est pas de l'écart de R-E15, qui l'a relue conforme :
elle reste.

**(c) Les statuts de la CAVP d'avant 2009.** Relu : l'arrêté du 11 mai 2009, article 2
(JORFARTI000020694602) : « Les arrêtés du 29 décembre 1948 portant approbation des statuts
de la section professionnelle des pharmaciens et du 1er juin 1950 portant approbation des
statuts de la section professionnelle des pharmaciens relatifs au régime complémentaire
d'assurance vieillesse sont abrogés. » La note de E14 est un récit : ils sont nommés ici et
dans le bloc « Reprise », avec ceux de la CAVEC et de la Cipav, au Bulletin officiel.

## 2. `cotisation_par_classes_liberales`, lue au droit

**Les rédactions lues.** L'article 2 de chaque décret, dans LEGI, toutes ses versions :
CARPV, décret n° 50-1318, onze (1950, 1954, 1967, 1982, 1993, 1997, 2012, 2015, 2022, 2025,
juillet 2026) ; CAVEC, décret n° 53-506, six (1980, 1987, 2008, 2012, 2025, juillet 2026),
la rédaction de 1953 n'étant qu'au fac-similé (lue le 27 septembre 2026, non relue) ;
Cipav, décret n° 79-262, six (1979, 1985, 30 décembre 2012, 2013, 2023, juillet 2026). Les
statuts au JORF, avec l'article qui les date ou, à défaut, leur publication : CAVEC, 22
février 2008 (publié le 1er mars, en vigueur le 2), 9 février 2012 (le 24 février), 27 mars
2012 (le 15 avril), 20 août 2018 (le 5 septembre) ; CARPV, 16 avril 2014 (le 18 mai),
2 novembre 2015 (le 2 décembre), 18 octobre 2021 (« entrent en vigueur le 1er janvier
2022 ») ; Cipav, 18 décembre 2015 (« entre en vigueur le 1er janvier 2016 »), 16 mars 2021
(le 31 mars). Les montants annuels restent ceux que `classes_cotisation_epoques.yaml` lit,
décret par décret (action 131) ; relus ici, la section de la Cipav aux décrets de 1998 et de
2010 (« Classe 1 : 3 406 F », sans taux d'appel) et la classe A de la CAVEC en 2025
(décret n° 2025-1076, article 12 : « cotisation forfaitaire de la classe A : 782 euros »).

**Les versions.** Quinze, sur `revenu.annee`, l'exercice, coupé au 1er janvier : neuf
`supposee` jusqu'en 2015, tant que les statuts de la Cipav (d'avant 2016), de la CAVEC
(d'avant 2008) ou de la CARPV (d'avant 2014) ne sont qu'au Bulletin officiel, puis six
`lue`. Les trente et une rédactions de `textes_a_rattacher` y sont toutes citées ; la liste
est ôtée. L'exemple `cipav_cotisations_2022` passe à la version de 2022.

**Le modèle sert-il chaque règle ?** Oui, à ce que les textes lus écrivent, régime par
régime et date par date (`classes_cotisation_epoques.yaml`, blocs `epoques` et `regles`,
confrontés à chaque rédaction) : les classes et leurs points ou multiples, les classes 5, 7
et 10 de la Cipav en 1980, 1981 et 1982, le revenu de l'avant-dernière année (CARPV de 1998
à 2021, CAVEC de 2008 à 2018), de l'année précédente (CAVEC depuis 2019, CARPV depuis 2022,
Cipav de 2016 à 2020), de l'année même (Cipav depuis 2021), la classe de début (A deux ans à
la CAVEC de 2012 à 2018, un an depuis ; B deux ans à la CARPV de 2014 à 2021, un an depuis ;
A deux ans à la Cipav de 2016 à 2020). Hors de là, des approximations, déclarées une à une :
la CARPV d'avant 1998 et la CAVEC d'avant 1980 (des barèmes sans égard au revenu, servis par
une grille de revenu ramenée), la valeur de l'acte vétérinaire et les bornes (conventions
déjà déclarées), les exercices sans décret lu, l'année de revenu avant les statuts lus, les
statuts en vigueur en cours d'année, les options (classe supérieure, classes réduites de la
CARPV, classe III de la CAVEC, appel réduit de la Cipav, cotisations facultatives), les
statuts que le simulateur ne pose pas (expert-comptable salarié inscrit à l'ordre,
vétérinaire des 11°, 12° et 23° de L. 311-3), et le prorata au mois de la CARPV, qui
proratise au trimestre.

**Un point non tranché neuf : le cumul à la CAVEC.** Décret n° 53-506, article 2, depuis le
1er janvier 2013 (LEGIARTI000026885098, et ses deux rédactions suivantes) : « En cas de
cumul de l'activité libérale et salariée, les cotisations afférentes au présent régime sont
appelées dans les conditions prévues à l'alinéa précédent, sans pouvoir être inférieures à
la cotisation en classe C. » Le modèle range le cumulant sur son seul revenu libéral (aucun
code ne connaît ce minimum). Lecture A : le décret vaut pour tout salariat, et le modèle sert
trop peu. Lecture B : l'« activité … salariée » est celle de l'expert-comptable salarié de
l'alinéa suivant, et les statuts de 2018 (JORFARTI000037363871, partie 2, article 3, 5 : « En
cas de cumul d'un revenu d'activité TNS et d'un revenu d'activité salariée, la cotisation
afférente au régime de retraite complémentaire est appelée dans les conditions prévues au 1
du présent article. « L'affilié a la possibilité d'opter pour la classe C ») n'en font
qu'une option, que le modèle ne sert jamais. Les deux tiennent : le décret prime, mais la
caisse applique ses statuts, et le texte ne dit pas quel salariat.

Cas posé, moteur Python (`Simulateur.carriere_parcours`, réglages par défaut), un script
hors du dépôt : née en mars 1960, salariée du privé non cadre depuis 22 ans (niveau de
salaire 1), expert-comptable en cumul de 55 ans à la liquidation à 65 ans (niveau 0,1). Le modèle range chaque année en classe A : pour 2024, le revenu libéral de 2023,
5 353,54 €, est sous la borne de 16 190 € ; cotisation de 760 € (la grille de 2024 du
modèle : 760 € la classe A, 4 496,67 € la classe C). Pension de la CAVEC servie : 621,59 €
par an (« cotisations revalorisées 7,462 € × rendement 8.33% »).
- Lecture A, l'année 2024 seule : classe C, 284 points au lieu de 48 ;
  284 × 760 / 48 = 215 840 / 48 = 4 496,6667 € ; 4 496,6667 − 760 = 3 736,6667 € de
  cotisation ; × 0,0833 = 311,2643, soit **311,26 €** de pension annuelle, avant la
  revalorisation de 2024 à la liquidation.
- Lecture A, toute la carrière, si le minimum vaut aussi les deux années de classe A
  d'office des statuts de 2012 (toutes les années du cas sont en classe A, et la pension
  est linéaire en la cotisation, la grille étant en points) : 621,5875 × 284 / 48 =
  621,5875 × 5,9167 = 3 677,7258 € ; 3 677,7258 − 621,5875 = 3 056,1383, soit
  **3 056,14 €** par an servis en moins.
- Lecture B : **0 €**.

Déclaré à la fiche (approximation de `classes_de_2013` à `reglements_de_2026`, et
`sources.a_relire`), non corrigé : au propriétaire.

**Ce que E9 rapportait à la fiche** (ligne 184 de sa note). La classe B d'office de la
CARPV et la classe A de la CAVEC la première année : lues (statuts de 2014 et de 2021,
décret depuis le 1er juillet 2026 ; statuts de 2012 et de 2018, décret depuis le 1er
juillet 2026), servies. La classe 3 d'office de la CAVP pendant deux ans (décret n° 49-580,
article 2, rédaction du décret n° 2026-418, article 4, JORFARTI000054153444, relu) : la CAVP
n'est pas un régime de la fiche ; `decret_2026_418_liberaux` la porte, le modèle servant à
toutes les classes la même fraction en répartition. La classe des notaires, sur la moyenne
de leurs produits de N − 4 à N − 2, son coût selon la classe, l'âge et la date de serment
(décret n° 49-578, article 2-3, rédaction du décret n° 2026-418, article 2,
JORFARTI000054153399, relu ; l'annexe 1) : la section B de la CPRN, que le modèle ne calcule
pas (`cprn_complementaire.yaml`, `manque`) ; aucune fiche de règle ne la porte. Ni l'une ni
l'autre n'est ajoutée à la fiche.

**`LUES_AU_DROIT`.** La fiche y entre : `tests/test_carte.py`, vu rouge à son entrée
(`domaine`, `lit`, `ecrit`, `dates_qui_decident`, `versions`, `approximations` manquants),
vert ensuite, sans rien forcer.

## Tests

`tests/test_sections_liberales.py`, `tests/test_carte.py`, `tests/test_textes.py`,
`tests/test_regle_de_chacun.py`, `tests/test_versions.py`, `tests/test_carte_du_depot.py`,
`tests/test_fiche_des_liberaux.py`, `tests/test_contrats.py` : 158 verts ;
`tests/test_oracle.py`, `tests/test_sources_a_explorer.py`, `tests/test_simulateurs.py` :
303 verts. `python -m pytest -m rapide` : 4 589 verts, 9 sautés ; sous
`PRESOMPTIONS_DECALEES=1` : 4 384 verts, 214 sautés. Le paquet refait
(`construire_donnees.py`) ne change pas : il ne lit pas les fiches.

## Pour la suite

Au propriétaire : le point non tranché du cumul à la CAVEC, avec les erreurs déjà déclarées.
Au fac-similé ou au seul Bulletin officiel : les statuts de la CAVEC d'avant 2008, de la
Cipav d'avant 2016 (et ses arrêtés de 1979 à 2006), de la CAVP d'avant 2009 (arrêtés du
29 décembre 1948 et du 1er juin 1950), de la CPRN de 2004 ; les décrets annuels de 1979 à
1983 et de 1989 ; la valeur de l'acte vétérinaire de 1950 à 2015.
