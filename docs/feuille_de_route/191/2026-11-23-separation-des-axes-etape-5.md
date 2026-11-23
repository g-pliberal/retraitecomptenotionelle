# La vue en périodes est partie : le moteur et le chargeur ne lisent que les quatre blocs

**Reprise, au 23 novembre 2026.** L'étape 5 est finie, et c'est le point
d'arrêt prévu : le propriétaire confirme que les témoins sont identiques
avant toute suite. La vue en périodes n'existe plus, ni en JavaScript ni en
Python : le moteur, le pont, le chargeur, le paquet et les tests lisent les
quatre blocs de chaque régime. Les témoins de simulation, de pages, des
servis, des sorties et des valeurs sont identiques ; le témoin du droit a
une valeur qui bouge, une fiabilité, expliquée dans la note. Restent, hors de
cette étape : les six doublons du classement des renvois sans texte (294 au
lieu de 288), et la fin du gel des données, que le propriétaire décide.

**La demande.** L'étape 5 de la séparation des axes (note de décision 0009) :
retirer l'ancienne vue en périodes, puis s'arrêter pour que le propriétaire
confirme les témoins. Sur Opus 5.5.

**Ce qui est fait.** Côté moteur, `axes.js` perd la vue (`periodesDesAxes`,
`axesDesPeriodes`) et `Regime` (`regimes.js`) ses lectures par période
(`periode`, `periodesActives`, `periodeALEffet`, `datesDEffet`) ; le taux
moyen de l'Agirc-Arrco et `sansDeclaration` travaillent sur les lignes. Le
paquet ne porte plus `dates_d_effet` et passe à la version 50. Le pont
désigne un régime par son code et un jour (`pont.Periode(code, jour)`, une
année valant son 1er janvier), lu par `aLaDate`. Côté Python, `Regime` porte
les quatre blocs, que `_blocs_de_la_fiche` lit dans le fichier ;
`lire_fiche_de_regime` rend la fiche telle qu'écrite ; `vue_ancienne` et
`blocs_des_periodes` partent, et `verifier_les_blocs` garde les refus du
chargeur. Les lecteurs restants passent aux lignes : contrôles des données
(`verifier_donnees.py`), calendrier des réformes, tableau de bord, contrôles
Z3 des renvois, mesures de la prose (23 ancres réécrites, mêmes valeurs),
cinq fiches de la carte qui nommaient `date_effet` (désormais `du`), et une
fiche qui nommait `Regime.periode`. Les tests de confrontation au droit qui
lisaient la fiche en périodes la lisent par `tests/outils_fiches.py`, qui
rend, année par année, ce que les lignes écrivent, au 1er janvier. Les
tests qui demandent la durée requise ou l'âge « à la date d'effet » passent
désormais ce jour au pont (`outils_pont.periode_a_l_effet`), comme le moteur
le fait en liquidant.

**Vérifié.** Les blocs, Python et JavaScript, au taux de la fiche et au taux
moyen, et ceux de chaque `sansDeclaration`, sont identiques à ceux d'avant ;
le paquet aussi, hors sa version et `dates_d_effet` ; les réformes non
portées, les sondes de la prose et les contrôles de la part salariale aussi.
La lecture des fiches par `outils_fiches` rend, sur les 80 régimes et toutes
les années, ce que rendait la vue, sauf les années où une ligne commence en
cours d'année : la vue y prenait tantôt l'ancienne, tantôt la nouvelle ; la
lecture prend celle du 1er janvier. Le témoin du droit garde 3 244 demandes ;
354 changent d'empreinte, parce qu'elles passent un jour au lieu d'une
année ; une seule change de valeur.

**Ce qui a bougé, sur deux exemples.** Une pension du régime général prenant
effet le 1er mars 1983 lit 150 trimestres, comme avant, mais sans la
fiabilité « haute » de la table par génération : avant le 1er avril 1983
(ordonnance n° 82-270), la durée est celle de l'article 70 du décret
n° 45-179, écrite dans la ligne d'avant, sans table. La vue lisait, pour
toute l'année 1983, la ligne d'avril. À Saint-Pierre-et-Miquelon, un départ
de février 2016 garde ses 150 trimestres : la réforme du 1er juillet 2016
(ordonnance n° 2015-896, article 4, 3°) ne s'applique pas avant sa date, ce
que la vue masquait en la lisant dès janvier ; `test_regle_de_chacun.py` le
déclare. Le tableau de bord compte 946 renvois au lieu de 2 581 : il compte
les lignes, et non plus les périodes, qui répétaient un même renvoi.

**Ce qui reste.** Le point d'arrêt : la confirmation des témoins par le
propriétaire. Puis, hors de cette étape, les six doublons du classement des
renvois sans texte, et la fin du gel des données.
