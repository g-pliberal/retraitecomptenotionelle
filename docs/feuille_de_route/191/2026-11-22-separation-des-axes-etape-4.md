# Le paquet porte les quatre blocs d'un régime, et non plus ses périodes

**Reprise, au 23 novembre 2026.** L'étape 4 est finie : le paquet, le
chargeur Python, le pont, les tests, les cliquets et la page Avantages lisent
les quatre blocs de chaque régime, et aucun résultat n'a bougé. La page
Avantages compte désormais les régimes qui annoncent la réversion, 78 sur 80,
au lieu de 975 périodes (décision du propriétaire du 23 novembre). La vue en
périodes n'a plus pour lecteurs que les tests qui la gardent pendant le gel,
ceux que le témoin du droit fige, deux scripts et les contrôles Z3 des
renvois, que la note nomme : tous partent ou changent à l'étape 5, la
suivante, avant le point d'arrêt prévu. Le classement des renvois sans texte
compte encore six doublons (294 au lieu de 288), à corriger dans sa note.
Les données restent gelées. L'oracle de référence est sous
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

## Les tests en blocs (quatrième lot, 23 novembre 2026)

**Ce qui est fait.** Cinquante fichiers de tests ne lisent plus la vue des
périodes, mais les blocs. Un paramètre de liquidation se lit à la date
(`a_la_date`) : à la date d'effet de la carrière quand le test en a une
(`calendrier.date_d_effet`), au 1er janvier de l'année qu'il nomme sinon. Un
paramètre de cotisation se lit à l'année (`de_l_annee`), la première tranche
ou toutes. Une boucle sur toutes les périodes devient une boucle sur les
lignes du bloc qui porte les champs qu'elle lit, la structure lue au début de
chaque ligne quand il le faut. Les essais JavaScript du moteur, des âges, des
cultes et de la fusion font de même (`aLaDate`, `deLAnnee`). Une seule
assertion a dû changer de date : la minoration de l'Ircec, que la fiche fait
valoir depuis le 16 mai 2025, se lit ce jour-là, et non au 1er janvier 2025
(`test_simulateur.py`). Deux assertions sur la part du salarié, qu'impliquent
celles qui restent, sont parties avec la propriété qu'elles lisaient
(`test_donnees.py`).

**Ce qui reste sur la vue, à dessein.** Les tests qui gardent la vue elle-même
pendant le gel (`test_axes_des_regimes.py`, les dates d'effet de
`test_coupures_au_mois.py`, `test_jumeaux_au_bit.py`, `tests/js/axes.test.js`) ;
ceux que le témoin du droit fige, par l'argument qui nomme la période d'une
année (`test_regle_de_chacun.py`) ou par le barème des confrontations
(`test_oracle.py`, `scenario_actuel.catalogue.periodes`) ; le compte de la page
Avantages (`test_web_revues.py`), qui attend la décision sur ses 975
périodes ; le gabarit de `fusion.test.js`, qui écrit des fiches en périodes.
Tous partent ou changent à l'étape 5, avec la vue. Côté scripts, deux en
lisent encore (`calendrier_regimes.py`, `construire_donnees.py`), et
`verifier_prose.py` en nomme dans les chemins de ses exemples : hors de ce lot.

**Vérifié.** Aucune source ni donnée n'a changé : le paquet, les témoins et
l'oracle sont ceux du lot précédent. Les 55 fichiers touchés ou visés rendent
2 940 succès, 44 cas sautés et un échec attendu, comme avant ; la suite rapide
est verte ; les essais JavaScript changés passent.

**Relu sur Opus, dans un contexte neuf.** La relecture a comparé, régime par
régime et champ par champ, les valeurs que voient les lignes de chaque bloc
à celles que voyaient les périodes : aucun écart, aucun champ lu dans le
mauvais bloc, les boucles couvrent les mêmes cas. La première tranche de
l'année redonne la cotisation de la période de l'année de 1900 à 2059 ; la
lecture au 1er janvier ne diffère de la période de l'année qu'aux coupures en
cours d'année, sur lesquelles aucun test à date fixe ne tombe. Les deux tests
lus à la date d'effet qui en croisent une, la Banque de France en juin 2007
et Mayotte en février 2023, lisent la règle de leur date. Aucun défaut ; un
commentaire récrit.

## Les cliquets en blocs (cinquième lot, 23 novembre 2026)

**Ce qui est fait.** Les deux cliquets que la vue en périodes nourrissait
(`test_cliquets_du_droit_date.py`) lisent le fichier en quatre blocs
(`outils_droit_date.blocs_des_regimes`). Un renvoi se suit sur les lignes du
bloc qui porte son champ (`axes.famille`), dans l'ordre du fichier ; une
valeur de repli se compte par ligne de liquidation ; le texte cité se lit
dans les `textes` de la ligne qui ouvre le renvoi. `test_renvois_dates_au_jour.py`
lit les dix renvois cités de même : la ligne qui ouvre chacun commence le jour
de son texte, ce qui déplace l'année de trois clés (la Cavimac, 2007 → 2006 ;
l'Organic et la Cancava d'avant 1973, 2013 → 2012).

**Les valeurs.** `VALEURS_DE_REPLI` passe de 1 415 à 367 : les mêmes
170 valeurs (régime, champ, valeur), que la vue recopiait sur chaque ligne de
cotisation ; chacune des 1 415 périodes se rapporte à l'une des 367 lignes, et
à elle seule. `RENVOIS_SANS_TEXTE` passe de 294 à 288 : la vue suivait tous
les champs sur les lignes de cotisation, la tranche 1 puis la tranche 2, et
coupait en deux six renvois de la liquidation, repris à la même année sur la
tranche 2 (l'Agirc et l'Agirc des entreprises nouvelles, l'âge du taux plein
de 2011 ; l'Ircantec, la durée requise de 1983, l'âge légal et l'âge du taux
plein de 2011, la surcote de 2010). Aucun renvoi n'est perdu ni gagné ; les
13 textes cités sont les mêmes ; les 13 séries de la cotisation, identiques.
Le classement des renvois sans texte de l'étape 4 de l'action
(`2026-11-22-etape-4-classement-des-renvois.md`) en comptait 294 : ces six
doublons y figurent deux fois.

**Vérifié.** Aucune source ni donnée n'a changé : paquet, témoins et oracle
sont ceux du lot précédent. La suite rapide est verte (6 775 succès).

**Relu sur Opus, dans un contexte neuf.** La relecture a confronté l'ancien
relevé au nouveau : les 288 sont les 294 moins les six doublons, nommés
ci-dessus ; les 367 rendent exactement les 1 415 périodes rapportées à leur
ligne de liquidation ; textes et séries de la cotisation identiques. Elle a
relevé trois défauts des tests, corrigés : un commentaire faux, une docstring
qui promettait ce que le cas ne prouvait pas, un nombre de régimes écrit en
dur. Elle note un risque latent : dans l'ordre du fichier, une ligne de
tranche 1 sans le renvoi glissée entre des lignes de tranche 2 couperait un
renvoi de la cotisation (la CNAVPL, l'Agirc) ; aucun ne l'est aujourd'hui.

**Ce qui reste.** La page Avantages, dont le chiffre de 975 périodes est à
soumettre au propriétaire. Les contrôles Z3 des renvois
(`scripts/regles_z3/questions.py`, `des_renvois_des_regimes`) lisent encore
les périodes : ils partent ou changent à l'étape 5, avec la vue.

## La page Avantages (dernier lot, 23 novembre 2026)

**La décision.** Le propriétaire a choisi, le 23 novembre, que le chiffre qui
annonce la réversion compte des régimes, et non des périodes que le paquet ne
porte plus, ni les 318 lignes de liquidation : « 78 régimes sur 80
l'annoncent », compté par la page et non écrit.

**Ce qui est fait.** `avantagesDetailEtats` (`moteur/js/pages.js`) compte les
régimes dont une ligne de liquidation au moins déclare `reversion`, sur le
nombre de régimes du catalogue ; le test de `test_web_revues.py` refait le
compte de son côté, et l'a vu rouge avant le code. La page Caisses ne lisait
déjà aucune période : ses chiffres viennent des fichiers du COR
(`caisses_du_site.py`), et l'inventaire des régimes ne prend du catalogue que
le code et la fiabilité. La page Avantages n'en lisait qu'à cet endroit.
`docs/avantages_non_contributifs.md` parle encore de « 756 périodes », dans une
section de récit, gelée à sa date : laissée telle quelle.

**Vérifié.** La page toute faite `avantages/index.html` est refaite
(`construire_pages.py`) ; la suite rapide et les tests du site passent, hors
le témoin des pages (`tests/temoins/pages.json`), que GitHub refait : seule
la page Avantages y change, par cette phrase.

**Ce qui reste.** L'étape 5 : retirer la vue en périodes et ses derniers
lecteurs, nommés plus haut. Puis le point d'arrêt prévu.
