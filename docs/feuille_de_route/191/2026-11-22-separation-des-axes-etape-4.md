# Le paquet porte les quatre blocs d'un régime, et non plus ses périodes

**Reprise, au 22 novembre 2026.** L'étape 4 est commencée : le paquet porte
les quatre blocs de chaque régime, et le moteur les lit tels quels. Aucun
résultat n'a bougé. Le chargeur Python lit encore des périodes, et la
fabrique du paquet en refait les blocs. Le moteur refait de ces blocs une vue
des périodes, que lisent encore le pont, les tests, le taux moyen de
l'Agirc-Arrco et la page Avantages. Reste, une session chacun : le chargeur
Python en blocs, avec ses lectures à la date et à l'année ; le pont, qui
passe une période par son rang ; les tests qui lisent des périodes ; les
cliquets recomptés à valeur égale ; la page Avantages. Par quoi commencer :
le chargeur Python. Les données restent gelées. L'oracle de référence est
sous `architecture/separation-des-axes/oracle/`, dans les fichiers du projet.

**La demande.** L'étape 4 de la séparation des axes, décidée le 22 novembre
2026 : le chargeur Python, le paquet, le pont, les tests, les cliquets et la
page Avantages passent à la nouvelle forme, sans qu'aucun résultat bouge.
Cette session en mène le premier lot, par où la note de l'étape 3 disait de
commencer : faire porter au paquet les quatre blocs au lieu des périodes. Sur
Opus 5.5 ; Fable 5.2 étant indisponible jusqu'au 25 novembre, la relecture
s'est faite sur Opus, dans un contexte neuf.

**Ce qui est fait.** `_blocs_du_paquet` (`scripts/construire_donnees.py`)
refait, des périodes que le chargeur rend, les quatre blocs comme le moteur
les refaisait au chargement (`axesDesPeriodes`) : la cotisation, une ligne
par période, bornée à ses années ; la liquidation, la structure et le servi,
des lignes au jour, chaque intervalle prenant la première période qui le
liquide. Le paquet ne porte plus de périodes ; `dates_d_effet` garde, au rang
de sa ligne de cotisation, la date d'effet qu'une période déclarait. Le
paquet passe de 6,4 à 4,3 Mo, et à la version 49. `Regime` (`regimes.js`)
lit les blocs du paquet tels quels, et `periodesDesAxes` (`axes.js`) en
refait la vue des périodes : une par ligne de cotisation, avec la
liquidation, la structure et le servi en vigueur au premier jour de sa date
d'effet. Une fiche en périodes, celles que le taux moyen redate, que
`sansDeclaration` retouche ou que les tests écrivent, passe encore par
`axesDesPeriodes`. Les deux fonctions partent à l'étape 5, avec la vue. Les
deux taux propres du non-salarié, que le chargeur date depuis
`taux_cotisation_annuels.csv`, sont rangés en cotisation du côté Python
aussi.

**Vérifié.** Les 977 périodes de la vue refaite rendent, champ par champ,
celles de l'ancien paquet, hors leur note, que rien ne lit. Les témoins de
simulation, de pages, des servis, des sorties, des valeurs et du droit,
refaits, sont identiques ; l'oracle est identique à celui du gel.
`tests/js/axes.test.js` dit que le paquet ne porte plus de périodes, et que
la vue refaite redonne les blocs du paquet. Deux tests qui retouchaient les
périodes du paquet retouchent ses lignes : la décote plafonnée
(`test_cout_age_depart.py`) et le poids des annuités du CESE.

**Relu sur Opus, dans un contexte neuf.** La relecture a refait l'ancien
paquet en périodes et comparé les deux catalogues, au taux minimal et au taux
moyen : mêmes blocs, mêmes périodes dans le même ordre, donc les mêmes rangs
au pont, et `sansDeclaration` redonne les mêmes blocs. Aucun défaut. Elle
note que le premier test d'`axes.test.js` compare désormais le moteur à une
vue refaite des mêmes blocs : le gel de ce lot tient par les témoins.

**Ce qui reste.** Le chargeur Python (`donnees/regimes.py`) range encore les
périodes de la vue ancienne, et 67 fichiers de tests et de scripts en lisent
quelque 320 sites. Le pont passe une période par son rang
(`commun.periode_de_liquidation`, la marque `periode`, `periodesActives`
pour la fusion, `scenario_actuel.catalogue.periodes`). Le taux moyen de
l'Agirc-Arrco redate des périodes, des deux côtés
(`daterLesTauxMoyens`, `dater_les_taux_moyens`) : il redatera les lignes de
cotisation. La page Avantages compte 975 périodes qui annoncent la
réversion ; compter les lignes de liquidation donnerait 318, et les régimes
78 sur 80 : le chiffre affiché changera, à soumettre au propriétaire avec
les autres décisions de la fin du gel.
