# Étape 2, huitième et dernière famille : les périodes assimilées, confrontées à OpenFisca

**Le 16 octobre 2026, la demande.** La onzième de onze sessions parallèles,
le propriétaire absent : « action 153, la dernière famille de l'étape 2 : les
périodes assimilées, confrontées à OpenFisca comme les sept familles
d'avant. » Aucun fichier des pages ni de la saisie n'est touché, aucun
déplacé ; la liste des textes n'est pas inscrite, le modèle n'est pas touché.

**Ce qui a été lu.** OpenFisca-France-Pension 0.1.3, installé à part (avec un
`setuptools` d'avant 70) : `TypesStatutDuCotisant`, les durées annuelles du
régime général — `_annuelle`, `_periode_assimilee_annuelle`,
`_cotisee_annuelle` —, `_surcote_trimestres` et `_pension_minimale`. Au
dépôt, `droit/compter.py` (les périodes assimilées de l'action 130, sixième
domaine), les quatre fiches de ces périodes et `surcote_regime_general`.
Dans l'index LEGI, récupéré pour l'occasion : D. 351-1-4. Le journal de
veille a son entrée (`2026-10-16-action-153-periodes-assimilees.yaml`).

**La convention de traduction**, écrite en tête de
`scripts/fetch/openfisca_periodes_assimilees.py` et portée par le témoin
(`tests/temoins/openfisca_periodes_assimilees.json`). OpenFisca ne compte pas
les trimestres d'une période assimilée : il reçoit, année par année et par
catégorie, ceux qu'elle valide, et les mène à la pension. Le dépôt compte donc
les trimestres des périodes déclarées dans la chronologie ; le témoin les
écrit en clair, et OpenFisca les reçoit — les stages de formation à sa
catégorie « chômage, pré-retraite, reconversion et formation », les sportifs
et le complément de l'apprentissage aux « autres périodes assimilées ». Des
non-cadres nés un 1er janvier, au seul régime général, liquidant au
1er janvier de 2016 à 2021 : les stages ne valident que depuis 2015, sa table
de revalorisation s'arrête à 2023. Les stages d'insertion et le congé
supplémentaire de naissance, qui ne valident qu'après septembre 2023 et
juillet 2026, restent hors de sa portée.

**Ce qui est fait.** Onze profils, des générations 1951 à 1958 : quinze mois
de stage sans salaire, des jours de stage déclarés, des stages qui complètent
un salaire de deux ou trois trimestres, une année de 900 € et son jumeau sans
salaire, un sportif inscrit de 2012 à 2015, un apprenti de 2014 à 2016, un an
de stage après l'âge légal et son jumeau qui travaille, deux petits salaires
au minimum contributif, dont un sous les 120 trimestres cotisés.
`tests/test_oracle_periodes_assimilees.py`, au niveau des contrôles : neuf
tests, la convention d'abord — le dépôt compte encore, de chaque période, les
trimestres que le témoin porte —, et le jumeau JavaScript sur les onze
pensions. Le manifeste a sa ligne (`openfisca_periodes_assimilees_oracle`) ;
le registre un écart, et son point 153.2, désormais `repris` ; les fiches
`stages_formation_professionnelle`, `sportifs_haut_niveau`, `apprentissage`
et `surcote_regime_general` leur bloc `referents` ; les limites un
paragraphe.

**Ce que la confrontation a trouvé.** Rien chez nous. Les trimestres
assimilés s'ajoutent à ceux du salaire, quatre par année au plus, et comptent
à la décote et à la proratisation ; ils n'entrent ni à la durée cotisée, ni à
la surcote, ni à la majoration du minimum contributif ni à son seuil de
120 trimestres cotisés ; une année dont le salaire n'achète pas un trimestre
reste hors du salaire annuel moyen, qu'un stage la complète ou non. Tout
concorde, le minimum contributif au centime. Un écart chez OpenFisca, hors de
la famille mais trouvé par elle :

| profil | le dépôt | OpenFisca | ce qui tranche |
|---|---|---|---|
| né le 1er janvier 1955, carrière complète, parti en 2020 | onze trimestres de surcote, dont trois en 2017 | huit : rien en 2017 | D. 351-1-4 : « le nombre de trimestres civils entiers suivant celui au cours duquel cet âge a été atteint » |

Sa formule ne fait courir la surcote d'une année que si le trimestre qui suit
l'âge légal commence au plus tard le 1er janvier : tout assuré qui atteint
l'âge légal hors du dernier trimestre perd la surcote de cette année-là. Les
deux jumeaux du salaire annuel moyen, partis le jour de leurs soixante-trois
ans, retrouvent la décote au jour anniversaire, déjà au registre. L'oracle a
donc trouvé vingt-sept erreurs chez OpenFisca, une à cette famille, et quatre
chez nous.

**Ce qui reste douteux.** Rien de neuf : la règle qui compte les trimestres
d'une période — cinquante jours de stage, quatre-vingt-dix d'inscription, la
durée du contrat —, qu'OpenFisca n'a pas, ne se confronte qu'aux exemples
officiels de l'action 130 (`tests/test_periodes_assimilees_exemples_officiels.py`).

**Ce qui devrait s'écrire dans les pages**, que cette session ne touche pas :
rien n'y devient faux.

**Ce qui reste.** L'étape 2 est finie, et avec elle ce que l'action avait à
faire. Restent au propriétaire le signalement à OpenFisca, de vingt-sept
erreurs, et la borne du 2 août 1951 (KALI) ; l'action se clôt quand il les
aura tranchés.
