# Étape 2, le barème : l'indice majoré de chaque indice brut, version par version depuis 1983

**Le 3 novembre 2026 : le barème du décret n° 82-1105, qui fait de l'indice
brut d'une grille l'indice majoré sur lequel se calcule le traitement, est
entré dans le dépôt pour ses vingt-neuf versions, du 1er janvier 1983 au
1er janvier 2024 : 12 122 périodes, sous `data/reference/grilles/bareme/`. Le
Noyau RH n'en avait qu'une ligne avant novembre 2006, fausse au bas de
l'échelle jusqu'en juin 2009. La source est une transcription tierce, celle
d'Épicycle sur data.gouv.fr ; elle redonne sans un écart les treize tableaux
que le LEGI reproduit depuis 2007 et les 86 couples que les textes écrivent
pour les barèmes de 1983 à 2008. La version du 1er juillet 1999, qu'elle omet,
est déduite ; huit valeurs recopiées de la ligne voisine sont corrigées.**

Demande : la session d'orchestration du 3 novembre 2026, file B, troisième
vague : « le barème qui convertit l'indice en traitement avant 2006, fixé par
le décret n° 82-1105 et ses versions » ; pas de site ; la question de la durée
des échelons, posée au propriétaire, à ne pas trancher.

- *Où sont les tableaux.* Le LEGI date chaque version — l'article 1er du
  décret n° 82-1105 dit « à compter du » — mais ne reproduit ses tableaux qu'à
  partir du 1er juillet 2007 ; avant, « tableau non reproduit ». Au JORF, les
  décrets de 1986 à 2006 qui les annexent renvoient au Journal officiel imprimé
  (« Vous pouvez consulter le tableau dans le JO n° 136 du 14/06/1998 page
  9063 à 9068 »), que Légifrance ne sert qu'au navigateur d'un poste, derrière
  un contrôle (action 138, étape 17) ; Internet Archive et Gallica refusent le
  mandataire de la session.
- *La source.* Épicycle publie sur data.gouv.fr, sous licence CC BY-SA,
  « Correspondances entre indices bruts et indices majorés de la fonction
  publique en fonction du temps » (jeu 61c26e0a8b4b58472b8d0907, fichier du
  14 novembre 2023) : une colonne par version, de 1972 à 2024. Le récupérateur
  (`scripts/fetch/epicycle_bareme.py`, test `tests/test_bareme_indices.py`) la
  télécharge — data.gouv.fr coupe une connexion sur deux à travers le
  mandataire : il retente — et vérifie l'empreinte SHA-1 que la notice publie.
  Le fichier de référence garde la licence de sa source.
- *Le recoupement.*
  - Au LEGI : les treize colonnes de 2007 à 2024 sont ses tableaux, 11 484
    couples, aucun écart. Le récupérateur le refait quand l'index est là, et
    refuse d'écrire sur un écart.
  - Aux textes : les articles 7 à 10 bis du décret n° 85-1148, version par
    version au LEGI, écrivent « l'indice majoré X (indice brut Y) » — le
    traitement de l'indice 100, le minimum de traitement, les bornes de
    l'indemnité de résidence et du supplément familial ; avec l'article 2 du
    n° 91-1191, 86 couples, tous redonnés. La rédaction d'origine du
    n° 85-1148 (JO du 5 novembre 1985) écrit les indices du barème de 1983, que
    le n° 86-166 n'a remplacé qu'en février 1986, rétroactivement au
    1er janvier 1985. Quatre mentions du LEGI, restées à leur ancienne valeur
    quand le reste de l'article changeait, sont écartées ; le test les nomme.
  - Aux titres : sept décrets attribuent des points « aux personnels » ou « à
    l'ensemble des personnels » (octobre 1988, février 1989, 1990, août 1991,
    avril et décembre 1999, novembre 2006) ; chacun de leurs barèmes ajoute
    exactement ce nombre à chaque indice majoré du précédent. Les autres
    versions ne touchent que le bas de l'échelle, jusqu'à l'indice brut 479 au
    plus, sauf celles de 1985 et de 2024, qui ajoutent deux et cinq points à
    tous sans que leur titre le dise ; celles de 2017 et 2018 n'ajoutent que
    les indices bruts 1016 à 1027.
- *Ce que le récupérateur ajoute.*
  - Les dates, du texte et non de l'intitulé de la colonne : celle qu'Épicycle
    date du 1er septembre 1979 est le barème du n° 82-1105, appliqué au
    1er janvier 1983 ; sa notice attribue au n° 88-1067 la version de février
    1989, qui est du n° 89-64. Le LEGI intervertit les dates de ses deux
    versions de 1999 (avril et juillet), et fait commencer le 7 juillet 2012 le
    tableau que l'article 1er dit du 1er juillet.
  - La version du 1er juillet 1999 (décret n° 99-491, des points « à certains
    personnels »), que la source omet : celle du 1er décembre 1999, moins le
    point uniforme du n° 99-943. Ses six couples des textes la confirment ; elle
    change les indices bruts 100 à 427 (328 périodes, lecture `deduite`).
  - Huit valeurs recopiées de l'indice brut suivant : un saut de deux points
    que le barème ne fait nulle part ailleurs au-dessus de l'indice brut 400, à
    contre-courant des points uniformes qui les entourent — l'indice brut 621
    en 1983 (509 au lieu de 510), 467 et 792 en février 1989, 554, 567, 607 et
    633 en 1990, 457 en 2004 (398, quand 2001 et 2005 disent 399). Chacune
    prend la valeur que les versions voisines donnent ensemble (`CORRECTIONS`,
    lecture `corrigee`) ; le récupérateur refuse une correction que la source
    ne justifierait plus.
- *Ce qu'il écrit*, sous `data/reference/grilles/bareme/` : `versions.csv`,
  les 29 versions, leur décret, leur texte au JORF, l'article du LEGI qui les
  date ou reproduit leur tableau, leurs points uniformes ; `indices.csv`,
  12 122 périodes, pour 916 indices bruts (100 à 1015) jusqu'en 2016, 923 en
  2017, 928 depuis 2018 (jusqu'à 1027).
- *La certification.* `scripts/verifier_donnees.py` relit
  `data/brut/epicycle_bareme.json` : 12 115 valeurs au niveau `haute` — une
  transcription tierce ne va pas au-delà —, les 7 périodes corrigées au niveau
  `estimee` (la huitième correction, en 2004, rend à l'indice brut 457 la
  valeur de 2001, et ne coupe pas sa période). Le journal ne reçoit que ces
  deux traces.
- *Ce que cela dit du Noyau RH* (`grilles/etat/indices.csv`). Son barème
  redonne celui du décret indice pour indice de juillet 2009 à 2023. Avant, il
  prolonge jusqu'au 1er janvier 1900 les valeurs de mai 2008 des indices bruts
  100 à 302 — l'indice brut 244, premier échelon de la catégorie C, y vaut
  l'indice majoré 288 jusqu'en juin 2009, quand le barème dit 280 en novembre
  2006, 283 en juillet 2007, 290 en juillet 2008 — et donne 466 à l'indice
  brut 500 avant novembre 2006, au lieu de 430 ; sa ligne d'avant novembre 2006
  est, pour le reste, le barème de juillet 2006. Depuis 2024, il mêle à son
  barème le minimum de traitement (l'indice majoré 366). Le test le dit, pour
  qu'une correction de l'un ou de l'autre se voie. La carrière (étape 3)
  prendra le barème du décret, et le minimum de traitement à part.
- *Ce que la donnée ne dit pas.* Le minimum de traitement de l'article 8 du
  décret n° 85-1148, sous lequel le traitement ne descend pas : ses valeurs
  sont aux versions de cet article au LEGI, à mettre en table. La hors-échelle
  (lettres A à G), payée par l'article 6. Avant 1983, les indices nouveaux
  majorés, que la source donne depuis 1972 et que le fichier ne reprend pas.
  Et la preuve imprimée des huit corrections et de la version de juillet 1999 :
  les tableaux des JO du 28 décembre 1982, du 7 février 1986, du 29 novembre
  1988, du 5 février 1989, du 11 avril 1990, du 27 novembre 1991, du 14 juin
  1998, des 20 mars, 13 juin et 14 novembre 1999, des 28 avril et 29 juin 2001,
  du 10 juillet 2004 (et son rectificatif du 7 août), des 30 juin 2005 et 2006,
  et du 20 octobre 2006, qu'un poste lirait sur Légifrance.

*Ce que cette tâche change à la question des durées d'échelon.* Le barème
n'arrête plus rien : de 1983 à aujourd'hui, l'indice brut de chaque échelon des
grilles du dépôt se convertit en indice majoré, donc en traitement. Ce qui
manque pour dérouler une carrière sur ces grilles, c'est le temps passé dans
chaque échelon — les durées, dans les statuts. Les grilles d'avant le Noyau RH
et les reclassements, que la file fait d'abord, étendent la couverture vers le
passé ; les durées d'abord donneraient plus vite une première carrière chiffrée
de bout en bout, sur les grilles déjà entrées.

*Pour les autres files.* Rien pour le site. Des fichiers partagés ont reçu des
lignes : `scripts/verifier_donnees.py` (une source, deux certifications),
`tests/test_donnees.py` (les deux séries et leur fichier),
`data/derive/certification.json` (deux traces), `data/sources.yaml` (l'entrée
`epicycle_bareme_indices`, sous un producteur neuf, `epicycle`).

*Ce qui reste de l'action 158, étape 2.* Les grilles de l'État d'avant le
noyau, puis le chaînage et les reclassements, dans l'ordre de la file ; les
durées d'échelon, dans les statuts des trois versants et des militaires ; les
tableaux que l'index aplatit ; le minimum de traitement, à mettre en table ; les
tableaux imprimés du barème de 1982 à 2006, d'un poste ; le traitement mensuel
d'une grille militaire publiée.
