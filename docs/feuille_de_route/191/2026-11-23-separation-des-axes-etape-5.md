# La vue en périodes est partie : le moteur et le chargeur ne lisent que les quatre blocs

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

**Relu sur Fable 5.2, dans un contexte neuf.** La relecture a comparé
l'avant et l'après sur les 80 régimes : paquet, blocs, lectures à la date et
à l'année, en Python et en JavaScript, au taux de la fiche et au taux moyen,
identiques ; une seule valeur du témoin du droit bouge, celle de mars 1983.
Elle a relevé quatre défauts mineurs, corrigés le même jour après la
validation des témoins par le propriétaire. Le chargeur refuse de nouveau un
bloc `servi` écrit qui ne couvre pas toute la liquidation, ce que la vue
refusait et que `verifier_les_blocs` avait perdu ; son test le dit. Le
contrôle de la carte n'admet `du` que pour un régime dont une ligne de
liquidation commence hors d'un 1er janvier, comme `date_effet` avant lui. Le
test de la sonde `partout` dit le refus qu'il attend. Le schéma des fichiers
de régime décrit les quatre blocs, `PeriodeRegime.couvre`, sans appelant,
part, et deux commentaires de tests sont remis à jour.

**Ce qui reste.** Hors de cette étape : les six doublons du classement des
renvois sans texte, et la fin du gel des données.
