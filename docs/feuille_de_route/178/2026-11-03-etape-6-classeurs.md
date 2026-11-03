# Étape 6 : les séries des classeurs du panorama de la DREES, à leur place

**Le 3 novembre 2026, ce qui est fait.** Les huit fiches que le suivi
renvoyait à l'étape 6 (01, 03, 16, 17, 22, 23, 25, 27) ont leurs séries dans
`data/reference/macro/`, lues dans leurs classeurs par
`scripts/fetch/drees_panorama_classeurs.py`, chaque classeur vérifié à son
empreinte, et certifiées par `scripts/verifier_donnees.py`. Au suivi, chacune
est `au_depot`, à l'étape 7, ce qui reste nommé pour la clôture. Tout est
tenu par `tests/test_drees_panorama_series.py` : les lecteurs, sur des
feuilles réduites telles que le classeur les écrit ; les fichiers, aux
valeurs que le PDF imprime, à la page citée, ou que le classeur porte ; et,
quand `data/brut/` a l'archive, quatre recoupements à la source.

1. *Au fichier que le dépôt tenait.* `cumul_emploi_retraite.csv` reçoit la
   retraite progressive du régime général depuis 1989 (fiche 22, graphique
   1, le recueil de la Cnav), en appoint du tableau 2, dont elle redonne les
   trois années ; `haute`, une transcription.
2. *Sept fichiers neufs.* `pensions_invalidite_age.csv` (fiche 25,
   graphique 2 et son complément : par âge et par sexe, de 2014 à 2024) ;
   `minimum_vieillesse_regimes.csv` (fiche 27, tableau 1 : par régime de
   versement et par territoire, l'ASI comprise) et
   `minimum_vieillesse_effectifs.csv` (graphique 1 : depuis 1960) ;
   `cumul_emploi_retraite_profil.csv` (fiche 23 : l'âge de 2014 à 2024, la
   catégorie et le temps de travail, `haute` comme l'enquête Emploi ; le
   cumul dans un même régime ; la génération 1950) ;
   `rapport_emploi_retraites.csv` (fiche 1, graphique 1, dont les retraités
   sont, année par année, ceux du cadrage de l'EACR) ;
   `retraites_generations.csv` (la polypension de la fiche 1, l'âge de
   liquidation de la fiche 16, le taux de liquidation, la décote et la
   surcote de la fiche 17, par génération) ; `reversion_beneficiaires.csv`
   (fiche 3, graphiques 2 et 4).
3. *Aux référents.* Le registre `referents.yaml` décrit des modèles, sans
   séries chiffrées ; ce que le suivi y envoyait — les séries de l'EIR et
   d'Ancetre que le modèle peut affronter — est dans les trois derniers
   fichiers, où une confrontation les lira. La part des polypensionnés des
   générations 1954 à 1957, qu'Ancetre estime, y est `haute`.
4. *Ce que les classeurs disent de travers*, déclaré dans les en-têtes. Le
   graphique 2 de la fiche 25 dit « en milliers » des personnes. La fiche 23
   dit 21,4 % de la génération 1950 en cumul avant 67 ans dans son chapeau,
   22,7 % dans son texte et son tableau 5, que le fichier suit ; son texte
   cite l'EIR de 2020 et l'EIC de 2021, ses tableaux l'inverse ; son
   tableau 3 écrit « 80 % » et « 50 % » en nombres. Aux graphiques 4 et 5 de
   la fiche 17, de 1939 à 1945, chaque génération impaire vaut la moyenne
   de ses voisines. Le graphique 5 de la fiche 16 arrondit la génération
   1953 autrement que le tableau 1 (37 % à 61 ans, contre 38 %) : le tableau
   la donne seul. Le titre du graphique 1 de la fiche 17 finit sur l'année
   de l'échantillon, 2020 : la génération se lit après « née en ».
5. *Le lecteur.* Une année d'en-tête se lit avec un renvoi collé
   (« 20141 »), un libellé numérique comme le classeur l'écrit (« 0.8 »),
   et l'apostrophe courbe vaut la droite. Un fichier brut lu avant qu'une
   série n'y entre la dit absente, non fausse.

**Ce qui reste**, pour la clôture (étape 7), fiche par fiche au suivi : les
feuilles que le suivi ne destinait à rien — les flux et les pyramides des
fiches 1 et 3, la carte et le tableau 3 de la fiche 1, les compléments des
fiches 3, 16, 17 et 23, la génération 1957 de la fiche 17 —, et deux choses
que seul le PDF chiffre : les départs après 67 ans (fiche 16, encadré 2), les
70 660 nouveaux allocataires du minimum vieillesse et ses dépenses (fiche 27,
le jeu `drees_minimum_vieillesse` du vivier).

**Pour les autres files.** File J : les confrontations que ces séries
permettent — la polypension de la grille, qui n'a aucun polyaffilié, sa
réversion, ses âges et ses taux de liquidation par génération — ne sont pas
faites ici. Le bloc « Reprise » de l'action 178 compte encore l'étape 6 parmi
celles à commencer : à récrire par la session qui le tient. L'entrée `ancetre`
du registre des référents pourrait citer le jeu des classeurs à son champ
`manifeste`. Aucune question au propriétaire.
