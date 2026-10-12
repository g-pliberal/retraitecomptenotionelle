# Étape 6, la population : la persistance au voisinage du Smic certifiée

**Le 11 octobre 2026 : ce que deviennent, six ans durant, les salariés du
privé payés au voisinage du Smic en 2007 entre au dépôt, par sexe et par âge,
lu dans le document de travail de la DG Trésor qui l'a mesuré. Rester au Smic
six ans est rare, plus encore pour un homme : la persistance ne rendra pas
seule aux hommes de la population le minimum contributif qui leur manque.**

Demande du propriétaire : « vas-y, certifie la persistance au Smic », la
première pièce du bas de l'échelle que la seconde version de la population
laissait.

- *Où elle se trouve.* Trois études la mesurent, une quatrième s'en
  approche ; une seule la donne par sexe, année après année. Le Trésor-Éco n° 365 (juin 2025 ; Benyamina et
  Stutzmann) classe les trajectoires de 2013 à 2019 des salariés payés moins
  de 1,1 Smic, fonction publique comprise : un quart restent « durablement »
  au voisinage, et une femme y a 1,17 fois plus de chances qu'un homme,
  toutes choses égales par ailleurs, sans parts par sexe. Ananian et
  Calavrezo (Économie et Statistique n° 448-449, 2011) suivent les cohortes
  1995 à 2003 cinq ans : 6,5 % restent au voisinage toute la période, des
  femmes à 72 %, pour 60 % de la cohorte ; leur cohorte de 1995, suivie douze
  ans sexes réunis, en garde 6,7 % en 2007. Le dossier de l'Insee de 2024
  sur les bas revenus salariaux (Berger) suit le revenu de l'année, non le
  salaire horaire : des salariés à bas revenu en 2011 encore salariés du
  privé en 2019, 13 % l'ont été chaque année, sans répartition par sexe. Le
  document de travail de la DG Trésor n° 2018/3 (Bernard, Caurier, Ananian
  et Chamkhi, juin 2018) suit la cohorte de 2007 jusqu'en 2013, année par
  année : en tout, par âge (annexe 3, tableau A) et par sexe (tableau B).
  C'est lui que le dépôt certifie.
- *Le fichier.* `data/reference/macro/persistance_smic.csv`, 336 valeurs
  certifiées : pour la cohorte payée au voisinage en 2007 — de 80 % à 105 %
  du Smic horaire net, salariés du privé de 18 à 65 ans, panel DADS de
  l'Insee — et pour celle payée au-dessus, la part de chaque état chaque
  année de 2008 à 2013 : hors du champ, au voisinage, au-dessus, et
  au-dessus par tranche (1,05 à 1,1 Smic, 1,1 à 1,3, 1,3 à 1,6, plus de
  1,6). Le récupérateur (`scripts/fetch/dgtresor_trajectoires_smic.py`) lit
  les tableaux 7, A et B dans le PDF avec le lecteur du dépôt, recolle les
  nombres qu'il coupe (« 4 3,6 »), et n'écrit rien qu'ils ne tiennent leurs
  comptes : trois états qui font 100, quatre tranches qui font leur total,
  deux sexes qui, pondérés par leur part dans la cohorte (tableau 1 : 38,1 %
  d'hommes), redonnent l'ensemble à 0,22 point près ; intervertis, ils s'en
  écarteraient de 2,4 points. Les âges ne se contrôlent pas ainsi : pondérés par la composition
  du tableau 1, ils s'écartent de l'ensemble de 0,9 point, quand une cohorte
  plus jeune le redonnerait à 0,08 près ; ce tableau ne décrit pas
  exactement, par l'âge, la cohorte suivie. Niveau `certifiee` : les auteurs
  ont fait le calcul sur le panel. La licence du site ne permet pas de
  republier le document : il reste dans `data/brut/`, son empreinte vérifiée
  (`rediffusion: interdite` au manifeste). La vérification
  (`source_persistance_smic`), le manifeste (`dgtresor_trajectoires_smic`)
  et un fichier de tests (`tests/test_persistance_smic.py` : le lecteur sur
  des lignes rendues comme le PDF, le fichier certifié qui passe tous les
  contrôles, des sexes intervertis qui n'en passent pas) le portent ; le
  journal reçoit sa trace (146 séries, 72 580 valeurs), le parcours de
  présentation suit, et le fichier reste dans l'empreinte du modèle.
- *Ce qu'elle dit*, en pour cent de chaque cohorte de 2007, encore au
  voisinage du Smic chaque année, puis parmi ceux restés dans le champ en
  2013 :

  | | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | restés dans le champ, 2013 |
  |---|---|---|---|---|---|---|---|
  | ensemble | 38,4 | 24,3 | 17,8 | 17,8 | 15,8 | 11,1 | 18,8 |
  | hommes | 31,9 | 18,7 | 13,3 | 12,9 | 11,1 | 7,8 | 13,4 |
  | femmes | 42,7 | 28,1 | 20,9 | 21,0 | 19,0 | 13,3 | 22,4 |
  | 18-24 ans | 30,2 | 17,9 | 13,0 | 12,7 | 11,2 | 7,9 | 12,5 |
  | 25-34 ans | 34,0 | 21,0 | 15,0 | 14,8 | 13,1 | 9,5 | 15,6 |
  | 35-49 ans | 45,8 | 30,7 | 23,3 | 24,0 | 22,1 | 15,6 | 25,0 |
  | 50-65 ans | 46,4 | 29,1 | 20,9 | 19,6 | 15,9 | 10,4 | 27,5 |

  La plupart des sorties se font la première année, puis la pente
  s'adoucit. Ceux qui passent au-dessus y restent près : en 2013, 58 %
  d'entre eux sont sous 1,3 Smic (64 % des femmes, 50 % des hommes), 16 %
  au-delà de 1,6. Le champ perd 41 % de la cohorte en six ans, 62 % des
  50-65 ans, que la retraite emporte. Des salariés payés au-dessus en 2007,
  3,2 % sont au voisinage en 2008, 2,0 % en 2013.
- *Ce qu'elle laisse entrevoir*, ordre de grandeur et non mesure : les
  hommes au voisinage du Smic font 4 à 5 % des salariés hommes du privé
  chaque année de 2007 à 2013, les femmes 9 à 11 % des salariées (texte du
  document) ; six ans plus tard, 13 % de ces hommes restés dans le champ y
  sont encore. Moins d'un salarié homme sur cent est donc au Smic en 2007 et
  encore six ans plus tard, quand 12,2 % des hommes partis en 2023 ont le
  minimum contributif (EACR), et 5,2 % dans la seconde version de la
  population. L'écart des hommes tiendrait moins au Smic qu'à ce qui le
  borde : des carrières qui en sortent sans dépasser 1,3 Smic, et le volume
  de travail des années.
- *Ce qu'elle n'est pas.* Une carrière : six années d'une cohorte, celle
  d'une crise, et une sortie du champ qui ne dit pas si l'on revient. Un
  salaire de l'année : un salaire horaire, temps partiel compris. Ni la part
  des salariés au Smic : dans les DADS, sans l'assiette du Smic, le
  voisinage compte les primes, et ne touche que 6 à 7,5 % des salariés du
  privé selon les années, quand la revalorisation du 1er janvier 2016 en a
  concerné 10,5 % (Dares, Acemo). La part par sexe n'est que dans le texte
  du document, non certifiée.

**Ce qui reste** de l'étape : la mesure de la persistance dans la
population — une part des carrières de chaque sexe qui reste au voisinage
du Smic, et des carrières qui en sortent sans dépasser 1,3 Smic, tirées de
ces transitions, puis le minimum contributif contre l'EACR — ; le volume de
travail des carrières du bas, à chercher et certifier ; enfin, au
propriétaire, la bascule de la page.
