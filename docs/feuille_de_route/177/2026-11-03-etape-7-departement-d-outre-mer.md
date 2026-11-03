# Étape 7 : le département d'outre-mer dans la saisie

**Le 3 novembre 2026, ce qui est fait.** Le site sert les règles qui lisent le
département d'outre-mer : le seuil du trimestre des années travaillées
outre-mer jusqu'en 1995 (R. 753-21, R. 351-9 ; action 138, étape 6) et
l'exonération de l'artisan et du commerçant des DOM sous 390 € (L. 756-3,
D. 756-7 ; étape 4). Quatre commits, chacun son test vu rouge d'abord
(`tests/test_saisie_de_l_outre_mer.py`, vingt cas).

1. *La forme du champ.* « Années outre-mer » (`outre_mer`,
   « 1975:1994:reunion »), par années entières comme les dispenses de
   l'assiette minimale, et non un menu sur chaque période : il sert d'un seul
   mécanisme le relevé, dont le format « année:régime:revenu » ne dit pas le
   lieu, et les métiers ; il tient à l'année comme les règles, R. 351-9
   comptant au seuil du département l'année travaillée outre-mer « au cours de
   tout ou partie » d'elle, l'exonération se jugeant sur le revenu de l'année ;
   replié dans les options, à côté de la Lodeom, il ne coûte rien au formulaire
   vierge, déjà à son budget de 191 mots. Les codes sont ceux du modèle
   (`DEPARTEMENTS_D_OUTRE_MER`) ; Mayotte se refuse, qui se dit par le statut
   de la période.
2. *La saisie* (`saisie.js`, `cdaeb42`). `outreMerAnalyse` lit et refuse comme
   les dispenses — une ligne mal formée, une année hors de toute carrière, une
   plage à l'envers, deux départements la même année —, plus un département
   inconnu et Mayotte ; `verifier` le prononce, l'adresse le garde. Chaque
   ligne d'emploi du relevé prend le département de son année, une année
   d'interruption aucun.
3. *Le contexte* (`contexte.js`). Les années qui prolongent le relevé jusqu'au
   départ prennent celui de leur année, et la métropole celles que le champ ne
   nomme pas, comme une dispense, quand `prolongerReleve` poursuivrait celui de
   la dernière ligne ; le contrôle du relevé (action 138, étape 10) lit son
   seuil au département de la ligne : 1982 à La Réunion contre 422,01 €, et non
   553,39 €. Le parcours reçoit les années.
4. *La chronologie, dans les deux moteurs* (`9079673`). `duParcours` et son
   jumeau `du_parcours` coupent chaque métier, principal ou ajouté, au
   1er janvier où le département change, et chaque morceau porte `outre_mer` ;
   `Carriere.depuisParcours` et `depuis_parcours` le transmettent. Le jumeau
   Python rend les mêmes faits que le portage, la dispense mêlée aux coupures.
5. *Le formulaire* (`pages.js`, `fe2dafb`, `541eca4`). Le champ et sa bulle :
   chaque département sous son code, ce que ses années changent, le montant de
   l'exonération lu au paquet (`exoneration_independants_outre_mer`), l'année
   d'arrivée et celle de départ à nommer, même entamées.
6. *Les témoins* (`construire_temoins.py`). `outre_mer_reunion_au_plancher` et
   `outre_mer_artisane_exoneree`, que tiennent deux tests vus rouges avant eux,
   chacun comparé à la même requête en métropole, et que le moteur Python
   refait sans écart.

**Mesuré.** Aucun des 925 témoins de simulation d'avant ne bouge ; dix-huit
rendus de page changent, ceux qui figent le formulaire entier, et la page du
simulateur. Né en 1940, à La Réunion de 1960 à 1995 au plancher de la saisie,
un dixième du salaire moyen : 118 trimestres au lieu de 104 en métropole,
1 095,58 € par an au système actuel au lieu de 1 011,68 € ; le compte
notionnel rétroactif, qui ne lit pas les trimestres, ne bouge pas. L'artisane
de La Réunion née en 1955, à 15 000 € par an de 1985 à 2014 puis à 300 € en
2015 : 120 trimestres au lieu de 122, 7 508,18 € par an au lieu de
7 597,79 € — le chiffre que l'étape 4 mesurait au modèle, que le site rend.

**Vu en chemin, non corrigé.**

- Deux tests de concordance rougissent sur `main` avant l'étape, hors de sa
  zone, la dernière suite verte de GitHub étant sur 476750c :
  `tests/test_pont.py::test_le_moteur_python_refait_chaque_temoin`, 671 écarts
  sur la pension revalorisée « aujourd'hui » (`coefficient_majoration`,
  `mensuel_decembre_2019`…), et
  `tests/test_cumul_activites.py::test_le_portage_javascript_concorde_sur_des_cumuls_tires_au_hasard`,
  sur le scénario notionnel rétroactif. Remis à l'état de `origin/main`, les
  fichiers de l'étape les laissent rouges ; les deux témoins de l'étape, eux,
  sont refaits sans écart.
- L'activité exercée après le départ ne porte pas le département : la
  chronologie ne coupe que les métiers. La seconde pension, qui en valide les
  trimestres depuis 2023, les compte au seuil de la métropole, le même depuis
  1996 ; seule l'exonération sous 390 € en dépendrait.
- Le relevé déposé en PDF n'écrit pas le département : l'assuré le dit dans le
  champ.
- Onze chiffres ancrés de `README.md`, `docs/carte_du_depot.md`,
  `docs/integration-partiliberalfrancais.md` et `docs/methodologie.md` sont
  périmés, surtout du fait d'autres sessions (le poids du paquet, les témoins,
  les sources) : la prochaine fabrique de GitHub les récrit.

**Ce qui reste.** Rien de l'étape. À la file du site, l'assurance maladie du
micro-entrepreneur, à rendre plus propre (étape 6), dans une session neuve. Au
bloc « Reprise » de l'action 177, que la file D tient : ôter l'étape 7 de ce
qui reste à la session du site.

**L'étape est faite.**
