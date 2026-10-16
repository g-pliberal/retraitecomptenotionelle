# Étape 2, cinquième famille : les minima, confrontés à OpenFisca

**Le 16 octobre 2026, la demande.** La septième de treize sessions
parallèles, le propriétaire absent : « action 153, étape 2, famille suivante.
Les minima — le minimum garanti de la CNRACL, nul chez OpenFisca, et ce qu'il
calcule des autres —, confrontés à OpenFisca dans un script et un test
frères. » Aucun fichier des pages ni de la saisie n'est touché, aucun déplacé ;
la liste des textes n'est pas inscrite, seul le cliquet des rédactions sans
statut s'abaisse d'une unité (`perimetre.yaml`), la fiche du minimum garanti
citant une rédaction de plus.

**Ce qui a été lu.** OpenFisca-France-Pension 0.1.3, installé à part (avec un
`setuptools` d'avant 70) : `fonction_publique_minimum_garanti`,
`cnracl_minimum_garanti`, `regime_general_cnav_pension_minimale` et
`_pension_brute`, les paramètres `minimum_garanti/`, identiques à ceux du
dépôt (`minimum_garanti.csv`). Dans les index JORF et LEGI : la loi
n° 2010-1330, articles 45 et 53 ; le décret n° 2010-1744, article 3 ; le
décret n° 2003-1306, article 22 ; D. 351-2-1. Le journal de veille a son
entrée (`2026-10-16-action-153-minima.yaml`).

**La convention de traduction**, écrite en tête de
`scripts/fetch/openfisca_minima.py` et portée par le témoin
(`tests/temoins/openfisca_minima.json`) :

- *Les fonctionnaires* : la carrière des familles d'avant, sédentaire, sans
  enfant, au traitement bas pour que le minimum joue.
- *Les salariés* : celle de `openfisca_regime_general.py`, non-cadres à
  salaire constant, entrés tard, partis à l'âge du taux plein.
- *Ce qui se compare* : le minimum garanti rapporté à sa référence — le dépôt
  la gèle en 2004 et la revalorise comme les pensions, OpenFisca la prend au
  point d'indice de l'année, un écart déjà tranché (`tests/test_oracle.py`) ;
  le minimum contributif au centime.

**Ce qui est fait.** Seize profils : quatre fonctionnaires de l'État sur le
barème (vingt, dix-huit, quarante ans ; treize ans sous le d), leurs trois
jumeaux de la CNRACL, l'ancien droit sous quinze ans, la minoration
transitoire, un départ décoté sans minimum ; cinq salariés au minimum
contributif, de 2009 à 2014, et un ajourné. `tests/test_oracle_minima.py`, au
niveau des contrôles : neuf tests, la convention d'abord, et le jumeau
JavaScript sur les seize. Le manifeste a sa ligne (`openfisca_minima_oracle`) ;
le registre quatre écarts, le point 153.2 et le bilan repris ; les fiches
`minimum_garanti` et `minimum_contributif` leur bloc `referents`, la première
sa lecture du jour ; les limites un paragraphe.

**Ce que la confrontation a trouvé.** Rien chez nous. Le barème de L. 17 —
ses marches datées, la référence entière à quarante ans, le d sous quinze ans
depuis 2011 —, la condition de taux plein depuis 2011 et le minimum
contributif, base et majoration, concordent. Quatre écarts chez OpenFisca :

| profil | le dépôt | OpenFisca | ce qui tranche |
|---|---|---|---|
| les trois profils de la CNRACL | le minimum de leur jumeau de l'État | zéro : les services de l'État, écrits en dur | décret n° 2003-1306, article 22 ; loi n° 2010-1330, article 45, VII |
| État, né en 1950, treize ans, parti en 2013 | le c : 57,5 % × 52/60 de la référence | le d : 52/162 | loi n° 2010-1330, article 45, V : L. 17 « dans [sa] rédaction antérieure » |
| État, né en 1951, sept trimestres de décote, parti à 61 ans en 2012 | le minimum, l'âge d'annulation minoré de neuf trimestres | aucun minimum | loi n° 2010-1330, article 45, IV ; décret n° 2010-1744, article 3 |
| salarié né en 1951, 124 trimestres, parti à 66 ans en 2017 | le minimum sur 137 trimestres corrigés, la majoration sur 124 cotisés | 124/163 du minimum majoré | circulaire Cnav n° 8/89, point 3 |

L'oracle a donc trouvé vingt-deux erreurs chez OpenFisca, quatre à cette
famille, et trois chez nous.

**Ce qui reste douteux.** La durée corrigée du minimum contributif tient à la
circulaire de 1989, que la fiche `majoration_duree_apres_65_ans` cite ;
D. 351-2-1 parle de « trimestres d'assurance effectivement accomplis ». Aucune
circulaire postérieure lue ne la reprend ni ne la dément : à confirmer par une
circulaire récente de la Cnav avant de signaler l'écart.

**Ce qui devrait s'écrire dans les pages**, que cette session ne touche pas :
rien n'y devient faux.

**Ce qui reste.** L'étape 2 continue, une famille par session : les points
enfants et la minoration de l'Arrco, les périodes assimilées, le salaire annuel
moyen sur des salaires qui varient. Le propriétaire tranche le signalement à
OpenFisca, de vingt-deux erreurs désormais.
