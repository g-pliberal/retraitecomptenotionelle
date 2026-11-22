# Le paquet porte les quatre blocs d'un régime, et non plus ses périodes

**Reprise, au 22 novembre 2026.** L'étape 4 avance : le paquet porte les
quatre blocs de chaque régime, que le moteur lit tels quels, et le chargeur
Python les porte aussi, avec ses lectures à la date et à l'année. Aucun
résultat n'a bougé. Les lecteurs Python d'une période passent par ces
lectures ; seuls le pont, les tests et l'oracle lisent encore la vue des
périodes, que le chargeur et le moteur refont des blocs. Reste, une session
chacun : le pont, qui passe une période par son rang ; les tests qui lisent
des périodes ; les cliquets recomptés à valeur égale ; la page Avantages.
Par quoi commencer : le pont, dont la note dit les quatre sites. Les données
restent gelées. L'oracle de référence est sous
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
passera les lectures à la date et à l'année. Viennent ensuite les tests, les
cliquets et la page Avantages, comme au premier lot.
