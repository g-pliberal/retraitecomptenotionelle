# Étape 1 : le champ `gestionnaire`, et le référentiel des organismes

**Ce qui est fait.** Chaque fichier de régime de `data/reference/regimes/`
porte, dans sa ligne d'inventaire, `gestionnaire` : un code du référentiel
`_gestionnaires.yaml`, ou une liste de codes. Le chargeur
(`charger_inventaire`, `lignes_d_inventaire`) le reprend sous
`RegimeInventaire.gestionnaires`, l'inventaire le recopie, le paquet le porte
(`dictionnaire()`), et `docs/regimes.md` gagne un bloc produit, « Les
organismes qui les gèrent », que `scripts/construire_regimes_md.py` écrit :
le compte, puis deux tableaux, les gestionnaires des régimes encore en vie et
ceux qui ont disparu. `charger_gestionnaires` lit le référentiel ; le
schéma des fiches décrit le champ.

**La règle retenue.** Le gestionnaire est l'organisme qui tient les comptes
du régime et en sert les pensions : aujourd'hui, ou le dernier qui l'a géré
en propre quand le régime s'est éteint ou fondu dans un autre. La CANCAVA
reste celle du régime des artisans d'avant 2006 ; qui en sert les droits
aujourd'hui, la chaîne des `integre_dans` le dit (le RSI, puis le régime
général). Deux champs du référentiel disent le reste : `operateur`,
l'organisme à qui un autre confie sa gestion — la Caisse des dépôts pour la
CNRACL, l'Ircantec, le FSPOEIE, l'ERAFP, la CNRV et deux caisses fermées, la
Cnav pour le régime complémentaire des indépendants, que le CPSTI pilote ; et
`collectif`, quand un code nomme un ensemble — les caisses communales d'avant
1945, celles des deux assemblées, celles des ports autonomes.

**Les comptes.** 76 organismes : 53 gèrent les 83 lignes encore en vie, ni
éteintes ni intégrées, et 23 ont disparu avec leurs régimes, ou les ont
laissés à un autre. Le chiffre de 53 dépasse la trentaine de caisses
nationales qu'on cite d'ordinaire : il compte l'outre-mer (Mayotte,
Saint-Pierre-et-Miquelon, la Polynésie, la Nouvelle-Calédonie,
Wallis-et-Futuna), l'État, l'Urssaf du micro-social, les caisses des petits
régimes fermés et les ensembles.

**D'où viennent les valeurs.** Des fiches elles-mêmes, de leurs textes et de
`data/sources.yaml` : vingt-cinq d'entre elles, chacune sous la phrase qui la
dit, sont recoupées par `test_les_gestionnaires_sont_ceux_que_les_sources_nomment`
— la Caisse des dépôts « gestionnaire du régime » de l'Ircantec et des mines,
sa carte des régimes, fonds et mandats de février 2026 pour l'ATC-ICNA, la
SUDAC et les élus locaux d'avant 1992, « une gestion distincte confiée à la
Mutualité sociale agricole », « géré par la CAFAT »… Les autres sont celles
que le nom du régime porte (la CARMF, la CNIEG, l'ENIM…), ou l'histoire
générale des régimes : les caisses des retraites ouvrières et paysannes,
celles des assurances sociales de 1930, l'institution de Strasbourg du
régime local d'Alsace-Moselle. Pour la prestation des sapeurs-pompiers
volontaires, une recherche du 7 novembre 2026 nomme l'association nationale
(APFR), qui en confiait la gestion à la CNP pour dix ans ; le contrat en
cours n'est pas lu, et l'opérateur n'est pas écrit.

**Ce qui reste.** Trois régimes n'ont pas de gestionnaire, déclarés un à un
dans `A_IDENTIFIER` : l'allocation aux vieux travailleurs salariés de 1941,
le régime additionnel des enseignants du privé (le décret de 2005 qui
l'organise n'est pas lu) et la SEITA (l'État la finance, mais qui en sert les
pensions depuis la privatisation de 1995, aucune source du dépôt ne le dit).
Puis la page Données, qui lit le paquet : une session du site.
