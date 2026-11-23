# Le paquet porte les quatre blocs d'un régime, et non plus ses périodes

**Reprise, au 22 novembre 2026.** L'étape 4 avance : le paquet porte les
quatre blocs de chaque régime, que le moteur lit tels quels ; le chargeur
Python les porte aussi, avec ses lectures à la date et à l'année ; le pont
désigne des paramètres par les rangs de leurs quatre lignes. Aucun résultat
n'a bougé. Seuls les tests et l'oracle lisent encore la vue des périodes ;
le pont n'en garde qu'une trace, l'argument qui nomme la période d'une
année, que le témoin du droit fige. Reste, une session chacun : les tests
qui lisent des périodes ; les cliquets recomptés à valeur égale ; la page
Avantages. Par quoi commencer : les tests, dont la note dit les sites. Les
données restent gelées. L'oracle de référence est sous
`architecture/separation-des-axes/oracle/`, dans les fichiers du projet.

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

## Le chargeur Python en blocs (deuxième lot, 22 novembre 2026)

**Ce qui est fait.** `Regime` (`donnees/regimes.py`) porte les quatre blocs,
`structure`, `liquidation`, `cotisation` et `servi`, et les lit comme le
moteur : `a_la_date(jour)` rend ce qui liquide une pension prenant effet ce
jour, `de_l_annee(annee, jour)` les tranches d'une année d'acquisition, avec
la liquidation du 1er janvier ou du jour donné. Ce sont les jumeaux de
`aLaDate` et `deLAnnee`, confrontés au bit près sur chaque régime, au taux
de la fiche et au taux moyen (`test_jumeaux_au_bit.py`) ; `_assembler` l'est
par eux. Pendant le gel, les blocs se refont des périodes, par la même
fonction que la fabrique du paquet (`blocs_des_periodes`, `donnees/axes.py`),
où `_blocs_du_paquet` n'est plus qu'un appel. Les lecteurs Python d'une
période passent par eux : la paie et ses composantes (`remuneration.py`,
trois sites), le forfait des cultes (`contributions_equilibre.py`), les
barèmes de la fusion (`solde_fusion.py`), la règle de revalorisation d'une
pension servie (`revalorisation_servie.py`, à la date, comme le moteur).
`periode` et `periodes_actives` n'ont plus de lecteur Python hors des tests
et de l'oracle : la liste des jumeaux les range au moteur.

**Vérifié.** Le paquet, refait, est identique au caractère près ; l'oracle,
identique à celui du gel ; les six familles de témoins, identiques. Une année
d'acquisition lit les mêmes lignes de cotisation que les périodes qui la
couvrent, dans le même ordre, sur chaque régime de 1900 à 2070. Aucun régime
n'a, de 1850 à 2100, une année cotisée sans ligne de liquidation au
1er janvier, ni une date liquidée sans ligne de cotisation dans son année.

**Relu sur Opus, dans un contexte neuf.** La relecture a relevé chaque champ
que les lecteurs basculés lisent, méthodes comprises : tous de la cotisation,
et la structure seule pour la revalorisation ; sur tout le catalogue, au taux
de la fiche et au taux moyen, de 1800 à 2100, les lectures à l'année ne
diffèrent des périodes que par des champs de liquidation, qu'aucun d'eux ne
lit. Elle a trouvé deux écarts latents avec le moteur, qu'aucune donnée
n'atteint : un assemblage sans ligne de liquidation, ou sans ligne de
cotisation, prêtait les champs d'une autre ligne. Le chargeur le refuse
désormais, un test posé à la main le dit.

**Ce qui reste.** Le pont passe une période par son rang
(`commun.periode_de_liquidation`, la marque `periode` de la façade et
l'argument `Periode` du droit, `scenario_actuel.catalogue.periodes`), et la
fusion lit `periodesActives` (`fusion.taux_total.tranche_1`, `pont.mjs`) : il
passera les lectures à la date et à l'année. Une piste relevée en finissant :
la façade des tests (`tests/facade.py`, `_periode_du_catalogue`) peut
transmettre des paramètres assemblés par les rangs de leurs quatre lignes :
les blocs du chargeur ont, dans les 80 régimes, les mêmes lignes, aux mêmes
bornes, que ceux du paquet ; un test le gardera. Viennent ensuite les tests, les
cliquets et la page Avantages, comme au premier lot.

## Le pont en blocs (troisième lot, 22 novembre 2026)

**Ce qui est fait.** Le pont ne lit plus la vue des périodes du moteur
(`tests/test_pont.py` le garde). Des paramètres d'un régime, en argument
d'une règle ou d'une table de la façade, passent par les rangs de leurs
quatre lignes (`pont.ParametresDuCatalogue`, marque `parametres`), que
`Regime.rangs` relève en Python — ceux d'un assemblage lu à la date ou à
l'année, ou, pour une période de la vue, sa ligne de cotisation et les
lignes en vigueur au premier jour de sa date d'effet — et que le moteur
assemble (`_assembler`). `commun.periode_de_liquidation` rend les rangs de
ce que le moteur lit à la date (`periodeDeLiquidation`), que le Python
assemble (`Regime.par_rangs`) : ce sont désormais les paramètres du moteur,
et non la période de la vue qui liquide le jour, qui n'en différait que par
des champs de cotisation (65 dates de 12 régimes, de 1900 à 2070). Deux
assertions sur la vue le suivent (`test_coupures_au_mois.py`,
`test_facade.py`). Le barème des confrontations lit les lignes de
cotisation, et la fusion, la lecture à l'année.

**Ce qui reste de la vue au pont.** L'argument `pont.Periode(code, annee)` du
droit nomme la période de la vue qui couvre l'année, que le témoin du droit
fige ; la lecture à l'année en diffère par sa liquidation, prise au
1er janvier, dans 13 couples régime-année (le régime général et les salariés
agricoles en 1983, la Banque de France en 2007, Mayotte en 2023…) : deux
preuves de la durée requise de 1983 bougeraient. Le pont la refait des blocs
(`parametresDeLaVue`), avec les dates d'effet des périodes, que le régime du
moteur garde à cette seule fin (`datesDEffet`). À l'étape 5, quand la vue
part, ces appels (`test_oracle.py`, `test_justesse.py` par ses preuves,
`test_cnav_exposes.py`, `test_regle_de_chacun.py`,
`test_taux_plein_a_soixante_cinq_ans.py`, `test_exploitants_agricoles_1986.py`)
devront dire leur date d'effet, et le témoin du droit se refaire.

**Vérifié.** L'oracle est identique à celui de la fin de l'étape 3 ; les six
familles de témoins, refaites, sont identiques ; la suite rapide et les
confrontations légères sont vertes. `test_axes_des_regimes.py` dit que les
blocs du chargeur ont, régime par régime, les mêmes lignes aux mêmes bornes
que ceux du paquet, et que les rangs de chaque période de la vue, et de
paramètres lus à la date, les redonnent.

**Relu sur Opus, dans un contexte neuf.** La relecture a confronté, sur les
80 régimes, au taux de la fiche, au taux moyen et après chaque retrait d'un
avantage : la période refaite des blocs à celle de la vue, année par année
de 1900 à 2070 ; l'assemblage par les rangs à la période de l'ancienne
marque, et à la lecture à la date ou à l'année, au même objet près ; le
barème de cotisation et le taux de la fusion à leurs anciennes valeurs.
Aucun écart, et aucune règle du moteur ne lit les bornes de paramètres
reçus. Elle note un piège : ce que `commun.periode_de_liquidation` rend en
Python garde les années de sa ligne de cotisation, sur lesquelles aucun
appelant ne doit se fonder.

**Ce qui reste.** Les tests qui lisent des périodes ; les cliquets recomptés
à valeur égale ; la page Avantages, dont le chiffre de 975 périodes est à
soumettre au propriétaire.
