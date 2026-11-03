# Étape 2 : les chiffres de 2024 du panorama de la DREES

**Reprise, au 3 novembre 2026.** L'étape est faite, sauf la fiche 5, qui
attend le propriétaire : porter à `pensions_brutes_nettes.csv` ses montants
de 2023 et 2024 (feuille « F05_Tableau 1 compl_bis »), qui déplacent le taux
effectif de la page Coût (action 138, étape 3) ; sur son accord, une source
d'appoint dans `verifier_donnees.py`, comme `source_age_conjoncturel_panorama`.
Les fiches 5, 8 et 15 laissent des confrontations à l'étape 4, close sans
elles, parce qu'elles n'étaient pas encore à confronter quand elle a commencé ;
le reste va aux étapes 5 et 6, fiche par fiche
(`data/reference/drees_panorama_2026.yaml`).

**Le 3 novembre 2026, ce qui est fait.** Tout est tenu par
`tests/test_drees_panorama_2024.py`, les valeurs attendues lues dans le PDF,
à la page citée, ou dans le classeur de la fiche, à la feuille citée.

1. *Les totaux recoupés au dépôt.* Les retraités de droit direct de 2004 à
   2024 (fiche 1, tableau 1), la ligne « Tous régimes » du cadrage de
   l'EACR, année par année, 17 298 000 fin 2024 ; leurs femmes, leurs hommes
   et leur pension hors majoration, 1 647 euros, la table C ; sept régimes du
   tableau 2, leur caisse du cadrage. Les 858 000 liquidants de 2024 (fiche
   2), le champ `nl_ddir` de la table C, et ceux de quatre caisses, la table
   B. L'âge des nouveaux retraités de 2024 (fiche 16, graphique 3), la table
   B au dixième près. Leur décote et leur surcote (fiche 17), la table H, sauf
   la surcote des civils de l'État, 37,6 % au panorama, 38,9 % au cube du SRE
   que la table H reprend : écart déclaré, tenu par le test. La part des
   nouveaux retraités portés au minimum (fiche 8, graphique 1), celle de
   `minimum_contributif_liquidants.csv` de 2020 à 2024 ; de 2012 à 2019, le
   panorama la dit de 0,2 à 1,1 point plus haute, à éclaircir à l'étape 4.
   Les 426,7 milliards du risque vieillesse-survie de 2024 (fiche 10,
   encadré 1), `depenses_retraite.csv`. Les 842 300 pensionnés d'invalidité
   de 2022 (fiche 25, graphique 1), la somme des caisses de la table I du
   témoin de 2022. La pension moyenne de 2008 à 2022 de
   `pensions_brutes_nettes.csv`, que le classeur de la fiche 5 redonne à
   l'euro près, sur son champ (France et étranger), quand le tableau 1
   imprimé ne compte que les résidents en France.
2. *Ce que le dépôt n'avait pas.* `scripts/fetch/drees_panorama_classeurs.py`
   lit dans l'archive, chaque classeur vérifié à son empreinte, les fiches
   15, 22 et 25, par leurs libellés, et dépose ce qu'il lit dans
   `data/brut/drees_panorama_2026.json` ; `verifier_donnees.py` le certifie.
   L'âge conjoncturel de 2023 et 2024, 62,95 ans fin 2024, « 62 ans et 11
   mois », va à `age_conjoncturel_depart.csv` en source d'appoint du jeu du
   portail, qui s'arrête à 2022 : le panorama ne prend le relais qu'après la
   dernière année du portail, parce qu'il révise de quelques centièmes des
   années anciennes. Le cumul emploi-retraite de 2014 à 2024 (au niveau
   `haute`, l'enquête Emploi étant un sondage) et la retraite progressive par
   régime vont à `cumul_emploi_retraite.csv`, neuf ; les pensions
   d'invalidité de 2015 à 2024, puis, fin 2024, par régime, leurs têtes, leur
   âge, leurs nouveaux, leur pension et leur dépense, à
   `pensions_invalidite.csv`, neuf. La mesure de l'âge de départ de la grille
   (`test_age_conjoncturel.py`) tient avec ses deux années de plus.
3. *Les trois citations anciennes.* `scripts/part_minimum_contributif.py`
   cite l'édition 2018 (fiche 9, EIR 2012) pour les artisans et les
   commerçants du RSI : l'édition 2026 ne la remplace pas, l'EIR 2020 rangeant
   la SSI au régime général ; son graphique 1 donne la part du RSI portée au
   minimum jusqu'en 2012, 39,3 % des artisans et 47,1 % des commerçants en
   2011, ce qui corrobore les 40 et 47 % que le script tient du RSI pour
   cette année-là. `docs/risque_de_defaut.md` cite la fiche 18 de 2025 (le
   Baromètre de 2024) : c'est un récit, qui ne se récrit pas ; la fiche 19 de
   2026 (Baromètre de 2025) dit 55 % des non-retraités qui attendent un
   niveau de vie moins bon que l'ensemble de la population (38 % « plutôt »,
   17 % « bien »), contre 54 %, et un âge idéal de 61 ans et 11 mois. La page
   des cas types cite le taux de remplacement de l'édition 2025, 74,8 %
   contre 73,8 % : la fiche 6 de 2026 (graphique 4, au classeur) donne, pour
   la génération 1953, 77,1 % dans le privé, 68,9 % dans le public, 75,4 %
   tous secteurs, médianes nettes des salariés à carrière complète ; à une
   session du site.

**Ce que l'étape n'a pas fait, et pourquoi.** Les 4,4 millions de
bénéficiaires d'une réversion (fiche 3) ne se recoupent pas : le dépôt n'en
garde que la masse, et le panorama ne donne pas leur montant. Les 395,3
milliards de pensions de retraite (fiche 10) sont une part du poste E11-2
dont le dépôt n'a pas les sous-postes, et leur répartition par régime groupe
les caisses autrement que `depenses_retraite_regimes.csv`. Le profil des
cumulants (fiche 23), les nouveaux allocataires du minimum vieillesse et
leurs dépenses (fiche 27), et les séries que le suivi destine aux référents
vont à l'étape 6, avec les classeurs.

**Pour les autres files.** File J : les confrontations des fiches 5 (par
régime, tableaux 2 et 4), 8 (la génération 1953 au minimum) et 15 (graphiques
2, 5 à 7), que l'étape 4 n'a pas vues. File I : `part_minimum_contributif.py` peut citer
le graphique 1 de la fiche 8 à côté du RSI de 2011. File C :
`scripts/age_conjoncturel.py` dit encore la série « 2004 à 2022 ». File du
site : la citation de 2025 de la page des cas types. Le propriétaire : la
fiche 5. Deux tests de `test_donnees.py` sur l'inventaire des régimes
échouaient avant l'étape, sans elle ; GitHub refait ce fichier.
