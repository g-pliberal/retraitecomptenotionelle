#!/usr/bin/env python3
"""Ce que les treize cas types déplacent sur la page Coût.

    python scripts/grille_large.py                    # les grilles, et ce qu'elles déplacent
    python scripts/grille_large.py --grille salaires  # une seule
    python scripts/grille_large.py --json g.json
    python scripts/grille_large.py --processus 4      # la grille simulée sur quatre cœurs

LA QUESTION
-----------
La page Coût passe le moteur sur treize cas types, à vingt-huit générations,
pondérés par les retraités de leur caisse. Treize carrières complètes, d'un
seul régime, d'un seul niveau de salaire, et d'hommes pour douze d'entre elles.
La population qu'elles représentent compte pourtant 53 % de femmes, un tiers de
polypensionnés, près d'un retraité sur quatre à moins de trente années validées
hors majorations, et des salaires dont le centile 99 vaut sept fois le centile
10.
`cout.py` dit ce qui en découle sans le chiffrer ; l'action 136 (étape 6)
demande de le chiffrer avant de décider s'il faut une population.

LA MÉTHODE : LA MÊME PAGE, SUR UNE GRILLE PLUS LARGE
----------------------------------------------------
Chaque grille part des treize cas types et les décline ; la page Coût se
relance sur elle sans qu'une ligne de `cout.py` change. Chaque déclinaison
reçoit une PART du poids de son cas type, et ces parts se lisent dans des
distributions publiées, certifiées dans `data/` :

``personnes``      Le poids d'un cas type venait des retraités de sa caisse, et
                   un polypensionné compte dans chacune des siennes : la somme
                   des caisses dépasse d'un tiers le nombre des retraités.
                   Chaque groupe de régime principal reçoit ici sa part de
                   PERSONNES dans l'échantillon interrégimes de 2020, et les
                   contractuels, dont la pension de base est celle du régime
                   général, sortent de l'effectif de la Cnav, qui les comptait
                   aussi. Aucune carrière ne change : seuls les poids bougent.
``melees``         Sur ces personnes, les polypensionnés de deux régimes de
                   base, dans la proportion que l'EIR donne à chaque régime
                   principal : dix années de salariat du privé, puis le métier
                   du cas type.
``femmes``         Les femmes, dans la proportion que l'EIR donne à chaque
                   régime principal, avec deux enfants : la grille du dépôt
                   n'en compte qu'une, la carrière interrompue.
``interruptions``  Les femmes, puis, hors des régimes à carrière statutaire,
                   les carrières courtes, dans les proportions que l'EIR donne,
                   sexe par sexe, aux cinq tranches de durée validée hors
                   majorations — l'activité s'arrête quand la durée de la
                   tranche est validée, l'inactivité court jusqu'au départ — ;
                   et dans chacune les périodes assimilées, validées sans être
                   cotisées, dans la proportion que l'EIR mesure entre la durée
                   validée hors majorations et la durée cotisée. Le modèle
                   ajoute lui-même les trimestres des enfants.
``salaires``       Chaque niveau décliné aux sept centiles du salaire du privé
                   (INSEE, dernière année publiée), chacun pour la part de la
                   distribution qui l'entoure, la moyenne de chaque cas type
                   gardée : seule la dispersion s'ajoute.
``ensemble``       Les personnes, les carrières mêlées, les interruptions et
                   les salaires à la fois, tenus pour indépendants.
``population``     L'ensemble, son salariat privé tiré des distributions de
                   chaque sexe : voir plus bas.

La page se refait sur chacune ; le tableau dit ce que chaque grille déplace par
rapport à celle du dépôt : l'écart cumulé des années observées, la part du PIB
en 2070, le solde moyen de 2026 à 2070, le coefficient d'équilibre en 2070, et
le passé que la projection refait à rebours (``Avenir.reconstitution``, action
147), dont la composition des cas types est l'un des suspects.

L'ASPA, RETIRÉE DE TOUTES LES GRILLES
-------------------------------------
Le scénario 1 sert l'ASPA à qui n'a pas assez, et la range dans la pension qu'il
rend. Les carrières courtes la déclenchent ; la garder dans une grille
compterait le minimum vieillesse comme une pension, quand la dépense que la
page multiplie l'exclut depuis le 23 septembre 2026. La page la retire donc de
sa grille (``Simulateur.pour_la_projection``), et chaque grille de ce script
avec elle.

La mesure du 5 octobre 2026 l'avait trouvée dans la grille du dépôt, aux
non-salariés des premières générations — l'artisan né de 1885 à 1905, le
libéral jusqu'en 1915, l'exploitant agricole jusqu'en 1920 : leurs régimes,
nés après la guerre, ne leur servaient que des pensions courtes ou
forfaitaires, que le scénario 1 complète au minimum vieillesse, quand les
scénarios notionnels ne le servent pas. La page comptait donc, dans les années
observées, une économie qui n'était que le minimum vieillesse retiré, et la
mesure se comparait à la grille du dépôt sans ASPA ; depuis le 11 octobre 2026,
elle se compare à la page elle-même. Le script vérifie que la grille du dépôt,
réécrite en parts, la redonne au chiffre près.

LA DISTRIBUTION DES PENSIONS, CONTRE CELLE DE L'ENQUÊTE (action 138, étape 14)
-------------------------------------------------------------------------------
Une grille qui représente les retraités doit redonner ce qu'on sait d'eux. La
composition le dit de ses caractéristiques ; la distribution des pensions le dit
de son résultat, qui ne sert à construire aucune grille : c'est une validation,
la forme publique de celle que les microsimulations font sur les pensions
réelles de l'EIR, qui ne se lisent qu'au CASD. Chaque grille est lue l'année de
l'enquête en têtes — celles que la page compte : chaque cohorte pesée par son
effectif INSEE, chaque cas type par son poids de la page —, chaque pension de
droit direct du scénario 1 revalorisée comme la page la revalorise et ramenée
en euros de l'année ; puis confrontée, sexe par sexe, à la moyenne et aux
quantiles que l'EIR publie des résidents en France, majorations pour enfants
comprises, et à leur distribution par tranches de cent euros
(``--distribution`` : la composition et la distribution seules, sans la page).

Une grille qui a des tranches de durée est aussi rangée comme l'EIR range les
retraités par quintile de leur pension en équivalent carrière complète — la
pension divisée par la proratisation, ce qu'une carrière acquiert par année
validée : chaque cohorte de l'année de l'enquête à sa pension, divisée par sa
durée d'assurance tous régimes rapportée à la durée requise et bornée à un, en
têtes ; puis, sexe par sexe, la part de chaque tranche de durée qui tombe dans
le premier quintile, contre celle de l'EIR. Les grilles ne comptant que des
résidents, l'EIR est celui des résidents en France
(``quintiles_eqcc_residents.csv``), depuis le 12 octobre 2026 ; la population
s'y construit aussi (:data:`DUREES_DES_RESIDENTS`).

LA POPULATION (action 136, étape 6, seconde moitié)
---------------------------------------------------
La grille « ensemble » donnait aux hommes les salaires des femmes, et ses
hommes touchaient le minimum contributif deux fois plus souvent que ceux de
l'EACR (action 137) ; elle étalait chaque cas type sur toute la coupe du privé,
le Smic jusqu'à sa moitié, toute une carrière, quand les treize cas types en
couvrent déjà les niveaux. La population garde ses personnes, ses carrières
mêlées et ses interruptions, mais remplace les quatre cas types de la Cnav — le
Smic, le salaire moyen, le cadre, la carrière interrompue — par un seul
gabarit, le salarié du privé, décliné aux sept centiles de la distribution de
SON sexe (``dispersion_salaires_sexe.csv``) : sa forme, rapportée à la moyenne
du sexe, au niveau de cette moyenne l'année où la génération a quarante-cinq
ans, si bien que chaque génération garde l'écart des sexes de son temps. Les
trois centiles du haut sont cadres. Pour la part des carrières que la moyenne
de la part du temps partiel des 25-49 ans donne à son sexe
(``temps_partiel.csv``), le salarié du privé travaille à temps partiel de 25 à
49 ans, à la quotité de sa génération (``quotite_temps_partiel.csv``). Les
autres groupes gardent la dispersion de la grille élargie autour de leur
niveau, celle de leur sexe. Les poids, comme ceux de toutes les grilles, sont
ceux des retraités de 2020 pour toutes les générations : la grille ne sait
pas donner à une carrière un poids qui dépende de sa génération.

La seconde version (le 11 octobre 2026) y ajoute trois choses, chacune
débrayable pour en mesurer l'effet : une dispersion de CARRIÈRE, la coupe de
l'année resserrée de l'âge, que le profil de carrière porte déjà, et des chocs
transitoires (:data:`DISPERSION_DE_CARRIERE`) ; aucun temps complet sous le
Smic (:data:`PLANCHER_SMIC`) ; les carrières courtes à la part que l'EIR donne
à tous les retraités du sexe, et non à ceux des seuls régimes qui en ont
(:data:`COURTES_A_LA_PART_DE_TOUS`). La troisième (le même jour) y ajoute la
persistance au Smic (:data:`PERSISTANCE_SMIC`) : une part de la classe du bas
de chaque sexe, celle que la DG Trésor trouve encore au voisinage du Smic six
ans plus tard (``persistance_smic.csv``), y est payée toute la carrière, et le
reste de la classe en garde la moyenne. La quatrième y met le volume de
travail (:data:`VOLUME_DE_TRAVAIL`) : chaque année d'activité du salariat
privé est payée à la part de l'année que l'INSEE mesure à son âge
(``volume_travail.csv``), et, en variante, à son rang aussi
(:data:`VOLUME_SELON_LE_RANG`). La cinquième (le 12 octobre 2026) étale les
années validées des carrières courtes de l'entrée à soixante ans, comme
l'échantillon interrégimes de cotisants date celles de tous les affiliés
(:data:`COURTES_ETALEES`) : elles étaient les premières, celles de la jeunesse.
La sixième (le même jour) donne à chaque tranche de durée le rang de salaire
que l'EIR lui mesure (:data:`RANG_SELON_LA_DUREE`) : les carrières courtes au
bas de l'échelle, les longues au-dessus, la distribution de chaque sexe
gardée. La septième (le même jour) affine le bas de l'échelle
(:data:`SOUS_CLASSES_DU_BAS`) : le reste de la classe du bas se décline en
sous-classes de rang, que le seuil du minimum contributif ne fait plus
basculer d'un bloc. La huitième (le même jour) lit le rang des retraités que
l'EIR trouve au minimum au premier quintile, et non au leur
(:data:`MINIMUM_AU_PREMIER_QUINTILE`) : leur quintile dit le minimum, non
leur salaire. La neuvième (le même jour) embraye le volume selon le rang
(:data:`VOLUME_SELON_LE_RANG`), que la quatrième laissait en variante : les
classes du bas travaillent moins d'heures dans l'année que celles du haut. La
dixième (le même jour) compte chaque carrière statutaire dans la tranche de
sa durée, et non dans la plus longue (:data:`STATUTAIRES_A_LEUR_DUREE`) : les
autres groupes ne portent plus seuls la tranche de trente à quarante ans. La
onzième (le même jour) fait commencer les carrières pleines du salariat privé
quarante-quatre années environ avant l'âge légal de leur génération
(:data:`ENTREE_SELON_LA_GENERATION`) : à 16 ans pour les générations parties à
60 ans, à 21 ans, comme avant, pour celles qui partent à 64. La douzième (le
même jour) fait suivre leur génération aux carrières incomplètes des femmes
(:data:`DUREE_DES_FEMMES_SELON_LA_GENERATION`) : elles gagnent ou perdent, à
chaque génération, les années qui portent la durée moyenne des femmes à celle
que l'EIR mesure aux résidentes. La treizième (le même jour) garde le temps
partiel jusqu'au départ (:data:`PARTIEL_JUSQU_AU_DEPART`), et non jusqu'à 49
ans : les années d'après cinquante ans n'entrent plus entières dans le salaire
annuel moyen des carrières à temps partiel. La quatorzième (le même jour)
prend les durées des seuls résidents en France (:data:`DUREES_DES_RESIDENTS`) :
la population se mesure contre eux. La quinzième (action 138, étape 14, le
16 octobre 2026) fait partir une part des carrières incomplètes avec une
décote, à l'ouverture du droit (:data:`DEPARTS_AVEC_DECOTE`) : l'EIR en compte
8,8 % chez les résidentes, quand la population partait toute au taux plein.
La seizième (le même jour) concentre le volume de travail plus faible des
classes du bas sur une part de leurs carrières, fragmentées toute la
carrière au volume des bas revenus salariaux (:data:`EMPLOI_FRAGMENTE`) : il
abaissait toutes leurs carrières un peu, et le seuil du minimum contributif
les faisait basculer par blocs d'une génération à l'autre. La dix-septième
(le même jour) rend au salariat privé les retraités de l'Ircantec
(:data:`CONTRACTUELS_AU_SALARIAT`) : la population en faisait des
contractuels de toute une carrière, à années entières, quand l'Ircantec ne
leur sert que 161 € par mois en moyenne. La dix-huitième (le 17 octobre 2026)
donne à l'artisan la dispersion des revenus des non-salariés de son sexe
(:data:`INDEPENDANTS_A_LEUR_DISPERSION`) : il avait celle des salaires des
temps complets, et n'atteignait jamais le minimum contributif ; la mesure le
juge sur les anciens artisans et commerçants de l'EIR.

CE QUE LA MESURE N'EST PAS
---------------------------
Une population. Les axes sont tenus pour indépendants — le salaire ne dépend
ni du sexe ni de la durée —, chaque déclinaison garde l'âge d'entrée et le
profil de son cas type, et les parts sont celles des retraités de 2020,
appliquées à toutes les générations ; seules les carrières incomplètes des
femmes changent de durée avec la leur. La dispersion des salaires est celle d'une
coupe de l'année à temps complet, plus large que celle d'un salaire de
carrière ; les dix années de salariat d'un polypensionné et les deux enfants
d'une femme sont des conventions, que l'EIR ne chiffre pas. Ce que la mesure
dit : de combien la page bouge quand la grille cesse de n'avoir que treize
carrières, et si cet écart justifie une population tirée des distributions
publiées (action 136, étape 6, seconde moitié).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import multiprocessing
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from typing import Callable

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.somme import somme_ordonnee
from retraite_notionnelle import cout as C  # noqa: E402
from retraite_notionnelle import memoire  # noqa: E402
from retraite_notionnelle.carriere import (  # noqa: E402
    PROFIL_SMIC, Metier, salaire_moyen_annuel,
)
from retraite_notionnelle.castypes import (  # noqa: E402
    CAS_TYPES, GRILLE_DU_COUT, CasType, cas_type_affiche, parts_des_caisses)
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.donnees.assiette import AssietteActivite  # noqa: E402
from retraite_notionnelle.donnees.caracteristiques import CaracteristiquesRetraites  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.distribution import (  # noqa: E402
    QUANTILES_PUBLIES, DistributionPensions, ResidenceRetraites,
)
from retraite_notionnelle.donnees.equilibre import (  # noqa: E402
    ComptesRetraite, DecompositionDepense, variante_du_scenario,
)
from retraite_notionnelle.donnees.macro import DonneesMacro  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.revalorisation import RevalorisationServie  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

GRILLES = ("reference", "personnes", "melees", "femmes", "interruptions", "salaires",
           "ensemble", "population")

#: Les groupes de régime principal de l'EIR, les indicateurs qui les comptent,
#: et les cas types qui les portent. Le régime général compte les salariés
#: agricoles, que l'EIR range à part et que le droit aligne sur lui. L'artisan
#: y est aussi : l'EIR de 2020 ne nomme pas les indépendants parmi les
#: non-salariés, et leur pension de base relève du régime général depuis 2018
#: (`legislation/affiliations.yaml`). Le contractuel de même, l'Ircantec n'étant
#: qu'un régime complémentaire.
GROUPES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "regime_general": (("regime_general", "msa_salaries"),
                       ("smic_carriere_complete", "salaire_moyen", "cadre",
                        "carriere_interrompue", "contractuel_public", "artisan",
                        "salarie_prive")),
    "fonction_publique_etat_civile": (("fonction_publique_etat_civile",),
                                      ("fonctionnaire_sedentaire",)),
    "fonction_publique_etat_militaire": (("fonction_publique_etat_militaire",),
                                         ("militaire",)),
    "cnracl": (("cnracl",), ("fonctionnaire_actif",)),
    "regimes_speciaux": (("regimes_speciaux",), ("agent_sncf_conduite", "agent_ieg")),
    "msa_non_salaries": (("msa_non_salaries",), ("exploitant_agricole",)),
    "professions_liberales": (("professions_liberales",), ("profession_liberale",)),
}

#: Les groupes dont les polypensionnés se déclinent. Le militaire n'en est pas :
#: sa pension s'ouvre à une durée de services, et le salariat vient après elle,
#: avec un second départ que la grille ne sait pas dater. Le régime général
#: non plus : l'EIR ne dit pas l'autre régime de ses polypensionnés.
GROUPES_MELES = ("fonction_publique_etat_civile", "cnracl", "regimes_speciaux",
                 "msa_non_salaries", "professions_liberales")

#: L'intitulé de chaque groupe, à l'impression.
INTITULES_GROUPES = {"regime_general": "régime général",
                     "fonction_publique_etat_civile": "État, civils",
                     "fonction_publique_etat_militaire": "État, militaires",
                     "cnracl": "CNRACL", "regimes_speciaux": "régimes spéciaux",
                     "msa_non_salaries": "MSA non-salariés",
                     "professions_liberales": "professions libérales"}

#: Les groupes où une carrière peut être courte. Les autres sont des carrières
#: STATUTAIRES — une pension qui s'ouvre à une durée de services ou à un âge
#: d'emploi —, et l'EIR range leurs retraités dans les trois quintiles du haut ;
#: une carrière courte y est celle d'un polypensionné, que l'axe des carrières
#: mêlées porte.
GROUPES_INTERROMPUS = ("regime_general", "msa_non_salaries", "professions_liberales")

#: Les caisses que la Cnav compte aussi : un contractuel de droit public est
#: affilié au régime général pour sa pension de base. Les artisans n'y sont pas
#: retirés : leur effectif complémentaire compte aussi ceux qui n'ont jamais été
#: salariés, et l'EIR ne dit pas combien.
CAISSES_DANS_LA_CNAV = ("ircantec",)

#: Les années de salariat du privé d'un polypensionné, avant le métier de son
#: cas type : une convention, l'EIR ne publiant pas la durée passée dans chacun
#: des deux régimes.
ANNEES_PRIVE = 10.0

#: Le nombre d'enfants des femmes de la grille : une convention, voisine de la
#: descendance finale des générations parties à la retraite.
ENFANTS = 2

#: Les cinq tranches de durée validée hors majorations : leur indicateur dans
#: l'EIR, et la durée qu'y prend une carrière de la grille. ``None`` : la
#: carrière du cas type telle quelle.
TRANCHES: tuple[tuple[str, int | None], ...] = (
    ("40_plus", None), ("30_40", 35), ("20_30", 25), ("10_20", 15), ("moins_10", 5),
)

#: L'âge jusqu'auquel court l'inactivité d'une carrière courte : au-delà de
#: tout départ que le droit puisse dater.
AGE_FIN_INACTIVITE = 70

#: Les centiles du salaire, et la part de la distribution que chacun représente :
#: celle qui l'entoure, jusqu'aux milieux des intervalles voisins.
CENTILES: tuple[tuple[str, float], ...] = (
    ("p10", 0.175), ("p25", 0.200), ("p50", 0.250), ("p75", 0.200),
    ("p90", 0.100), ("p95", 0.045), ("p99", 0.030),
)

# -- la population (action 136, étape 6, seconde moitié) --------------------------

#: Les quatre cas types de la Cnav que la population remplace par un seul
#: gabarit : le Smic, le salaire moyen, le cadre et la carrière interrompue
#: sont des niveaux de la distribution des salaires, que le rang de chaque
#: carrière dans celle de son sexe donne désormais.
SALARIAT_PRIVE = ("smic_carriere_complete", "salaire_moyen", "cadre", "carriere_interrompue")

#: Le gabarit du salariat privé : le cas type du salaire moyen, renommé.
GABARIT = "salarie_prive"

#: L'âge auquel une génération lit sa place dans la distribution des salaires :
#: le milieu de la carrière. Le salaire moyen des femmes valait 0,65 fois
#: celui des hommes en 1955, 0,87 en 2024 : la génération 1930 n'a pas
#: l'écart de la génération 1979.
AGE_DU_RANG = 45

#: Les deux années de l'activité partielle : le centile 10 du salaire en
#: équivalent temps plein y tombe de 0,46 à 0,40 fois la moyenne des deux sexes
#: chez les femmes, de 0,52 à 0,46 chez les hommes, pour remonter ensuite. La
#: forme d'une génération ne s'y lit pas : la génération 1975, qui y lisait la
#: sienne, touchait le minimum contributif à 24,4 % quand ses voisines en
#: étaient à 19 ou 20 %.
ANNEES_ACTIVITE_PARTIELLE = (2020, 2021)

#: Les centiles dont le salariat privé est cadre : 17,5 % de sa masse. Une
#: convention : l'INSEE ne croise pas le rang de salaire et le statut de cadre.
CENTILES_CADRES = ("p90", "p95", "p99")

#: Le temps partiel : de 25 à 49 ans, la tranche où l'INSEE en publie la part,
#: tout entière, pour la part des carrières que la moyenne de cette part, de
#: 1975 à 2025, donne à leur sexe. Une convention : aucune source publique ne
#: dit combien d'années une même personne passe à temps partiel, et le salaire
#: annuel moyen ne retenant que les vingt-cinq meilleures, sa durée compte.
AGES_PARTIEL = (25.0, 50.0)

#: Le temps partiel jusqu'au départ : la carrière à temps partiel le reste de
#: 25 ans à son départ, et non plus jusqu'à 49 ans seulement. L'INSEE publie
#: aussi la part des 50 ans et plus, et elle est plus haute encore chez les
#: femmes — 33,4 % en 2020, pour 25,8 de 25 à 49 ans ; 32,3 % en moyenne de
#: 1975 à 2025, pour 25,4 (``temps_partiel.csv``). Le salaire annuel moyen ne
#: retenant que les vingt-cinq meilleures années, une carrière rendue au temps
#: complet à cinquante ans y comptait ses dernières années entières, et passait
#: au-dessus du minimum contributif : une femme née en 1950, à carrière pleine
#: et à temps partiel dans la classe médiane, touchait 964 € à son départ ; à
#: temps partiel jusqu'au bout, le minimum la relève à 911 €. La part des
#: carrières à temps partiel reste celle des 25 à 49 ans. La treizième version.
PARTIEL_JUSQU_AU_DEPART = True

#: Les durées des résidents : la population se mesure contre les seuls
#: résidents en France (``quintiles_eqcc_residents.csv``), et elle prend
#: désormais leurs durées — la part de chaque tranche de durée validée hors
#: majorations, cette durée et la durée cotisée, le rang de salaire de chaque
#: tranche et le minimum de chaque quintile (:class:`DureesDesResidents`) —, et
#: non plus celles de tous les retraités, dont ceux de l'étranger, aux carrières
#: françaises courtes : 11,5 % des hommes de tous valident moins de trente
#: années hors majorations, 7,9 % des résidents. Les parts des régimes, des
#: polypensionnés et des femmes restent celles de tous, que le dépôt ne
#: certifie pas chez les résidents ; la durée des carrières pleines aussi
#: (:func:`durees_pleines`) : l'EIR arrondit ses durées moyennes à l'année, et
#: celle des résidentes, au même arrondi, la déplacerait d'une année sans rien
#: en apprendre. La quatorzième version.
DUREES_DES_RESIDENTS = True

#: L'âge auquel une génération lit la quotité de son temps partiel, dans la
#: tranche des 25-54 ans.
AGE_DE_LA_QUOTITE = 40

#: La dispersion d'un salaire de CARRIÈRE, en écart au centre du logarithme,
#: rapportée à celle de la coupe de l'année. La coupe tous âges compte l'âge,
#: que le profil de carrière porte déjà : 23 % de la variance du logarithme du
#: salaire en 2024 (``profil_salaire_age.csv``, ``dispersion_salaires.csv``).
#: Et des chocs transitoires, qu'une carrière moyenne efface : un cinquième à
#: trois dixièmes de ce qui reste, pour le salaire journalier des hommes du
#: privé de 36 à 54 ans (Ceci-Renaud, Charnoz et Gaini, « Évolutions de la
#: volatilité des revenus salariaux du secteur privé en France depuis 1968 »,
#: Insee, document de travail G 2014/03, tableau 6). Une carrière en garde les
#: trois quarts de 77 % : 0,76 de l'écart, la racine de 0,58.
#: Le bas s'y resserre comme le milieu. Qui est payé le Smic dans la coupe a
#: pour salaire de carrière attendu la médiane, fois le Smic rapporté à elle à
#: la puissance 0,58 — 0,75 à âge donné : 1,20 Smic, 1,14 à 35-49 ans, en 2007.
#: La DG Trésor en mesure 1,20 et 1,15, la médiane, six ans plus tard, de ceux
#: payés au voisinage du Smic restés salariés du privé (``persistance_smic.csv``,
#: les bandes interpolées) : un resserrement de 0,72 à 0,75 selon le sexe et
#: l'âge.
DISPERSION_DE_CARRIERE = 0.76

#: Aucun temps complet ne se paie sous le Smic : une carrière du salariat privé
#: dont le rang tombe sous le Smic, l'année où sa génération a
#: :data:`AGE_DU_RANG` ans, est payée le Smic de chaque année. Le centile 10
#: des femmes l'était à 0,43 fois le salaire moyen pour la génération 1950,
#: quand le Smic en valait 0,535.
PLANCHER_SMIC = True

#: Les carrières courtes, à la part que l'EIR donne à TOUS les retraités de
#: chaque sexe : les régimes statutaires n'en ayant pas dans la grille, les
#: autres en portent d'autant plus. La grille élargie leur donnait la part de
#: tous, et la population de 2020 comptait 26,9 % de femmes sous trente
#: années validées, pour 33,7 % dans l'EIR.
COURTES_A_LA_PART_DE_TOUS = True

#: Les carrières statutaires à leur durée : sous
#: :data:`COURTES_A_LA_PART_DE_TOUS`, chacune compte dans la tranche de sa
#: durée — le militaire, 25 ans ; l'agent de conduite, 32 ; le fonctionnaire
#: actif, 35 ; l'agent des IEG, 36 —, et non toutes dans la plus longue ; les
#: autres groupes complètent chaque tranche jusqu'à la part que l'EIR donne à
#: tous les retraités du sexe. Tenues pour entières, elles laissaient aux
#: autres groupes la tranche de trente à quarante ans de tous : la neuvième
#: version comptait 32,8 % d'hommes de trente à quarante années, pour 22,0 %
#: dans l'EIR, et 51,5 % à quarante et plus, pour 66,5 %.
STATUTAIRES_A_LEUR_DUREE = True

#: Les carrières courtes, ÉTALÉES sur la vie active : les années validées d'une
#: tranche courte, régulièrement espacées de l'âge d'entrée du cas type à
#: :data:`AGE_FIN_ETALEMENT`, et non plus les premières. L'EIR ne les date pas ;
#: l'échantillon interrégimes de cotisants date celles de tous les affiliés
#: (DREES, « Les droits validés au cours de la carrière », EIC 2017, données
#: détaillées, trimestres validés dans l'année). Les femmes des générations
#: 1946 à 1958 en valident en moyenne 2,84 par an de 25 à 29 ans et 2,79 de 50
#: à 54, et en cotisent 2,23 puis 2,52 ; les hommes, 3,23 et 3,09 ; et de
#: même celles affiliées avant 23 ans, sans les arrivées tardives. Datées de la
#: jeunesse, les carrières courtes de la population faisaient valider de 50 à
#: 54 ans 0,70 femme pour une de 25 à 29 ans, et 0,85 homme ; étalées, 1,08 et
#: 0,98.
COURTES_ETALEES = True

#: L'âge où finit l'étalement : le premier âge de départ des générations de la
#: grille, qu'aucune année validée ne doit passer. Une tranche plus longue que
#: l'écart entre l'entrée et cet âge le prolonge d'autant.
AGE_FIN_ETALEMENT = 60

#: L'entrée des carrières pleines selon la génération : la carrière entière du
#: salariat privé, sa tranche de quarante ans et plus, commence la durée des
#: carrières pleines de sa génération (:func:`durees_pleines`) avant l'âge
#: légal d'ouverture de celle-ci (``age_ouverture_requis.csv``), et à 21 ans
#: au plus tard, l'entrée du gabarit. Elle commençait à 21 ans pour toutes :
#: les générations nées avant 1951, parties à 60 ans, n'y validaient que 39
#: années, quand les carrières pleines des retraités de 2020 en comptent 44.
ENTREE_SELON_LA_GENERATION = True

#: La durée des carrières des femmes selon la génération : les carrières
#: incomplètes des femmes, hors des régimes statutaires, gagnent ou perdent,
#: génération par génération, les mêmes années validées
#: (:func:`ecarts_des_femmes`), pour que la durée moyenne des femmes de chaque
#: génération soit celle que l'EIR mesure aux résidentes, majorations
#: comprises (``duree_assurance_generations.csv``) : 33,2 années pour la
#: génération 1940, 39,5 pour 1953, 41 environ pour les suivantes, que
#: TRAJECTOiRE projette. Les poids et les tranches restent ceux des retraitées
#: de 2020 ; une carrière incomplète garde une année au moins, et ne passe pas
#: l'âge légal de sa génération. La grille donnait à toutes les générations les
#: carrières des femmes de 2020 : 34,7 années, quand celles de l'EIR montent de
#: 33,8 autour de 1940 à 38,2 autour de 1950. Les hommes n'en reçoivent pas :
#: leur durée, dans l'EIR, ne change guère d'une génération à l'autre. Les
#: carrières incomplètes perdent 2,3 années pour les générations nées jusqu'en
#: 1940 — celles d'avant, que l'EIR ne mesure pas, gardent sa première durée —,
#: en gagnent 8,3 pour 1950, 15 à 17 pour celles nées de 1955 à 1970 : la
#: tranche de trente à quarante ans, bornée par l'âge légal, n'en prend que
#: quelques-unes, et les plus courtes portent le reste. La douzième version.
DUREE_DES_FEMMES_SELON_LA_GENERATION = True

#: La persistance au Smic : une part des carrières du salariat privé de chaque
#: sexe est payée le Smic toute la carrière. Celle de la coupe de l'année à
#: temps complet sous :data:`SEUIL_VOISINAGE` fois le Smic, en moyenne des
#: années où les centiles se publient par sexe, multipliée par la part de ceux
#: payés au voisinage du Smic qui y sont encore six ans plus tard, parmi ceux
#: restés salariés du privé (``persistance_smic.csv``) : celle des 35-49 ans,
#: l'âge où la population lit le rang, au rapport des sexes de tous âges, que
#: le document ne croise pas avec l'âge. Elle sort de la classe du bas, dont
#: le reste garde la moyenne : la masse des salaires ne bouge pas.
PERSISTANCE_SMIC = True

#: Le voisinage du Smic, en multiple de lui : celui de la DG Trésor.
SEUIL_VOISINAGE = 1.05

#: Le bas de l'échelle, plus fin : le reste de la classe du bas — hors la part
#: payée le Smic toute la carrière — se décline en autant de sous-classes de
#: rang égales, chacune au niveau que la coupe de l'année donne au milieu de ses
#: rangs, son écart resserré en carrière comme celui des classes
#: (:func:`resserrer`), la moyenne du reste gardée (:func:`ecarts_du_bas`).
#: Sous le dixième centile, la coupe se prolonge par la pente des deux premiers,
#: comme dans :func:`part_de_la_coupe_sous` ; une sous-classe qui tombe sous le
#: Smic y est payée (:data:`PLANCHER_SMIC`). La classe ne bascule plus entière
#: d'un côté du seuil du minimum contributif : abaissé d'un dixième, le reste de
#: la classe des hommes faisait passer leur part au minimum, en 2023, de 4,9 à
#: 9,9 %. Un : le reste à un seul niveau.
SOUS_CLASSES_DU_BAS = 4

#: Le volume de travail : une année travaillée ne l'est pas toute — les
#: entrées, les sorties, le chômage et les contrats courts la coupent. Chaque
#: année d'activité du salariat privé est payée à la part de l'année que
#: l'INSEE mesure à son âge (``volume_travail.csv``) : le volume de la tranche,
#: rapporté à celui de l'ensemble, fois celui d'un temps complet, 0,85 — soit
#: 0,53 avant 25 ans, 0,87 de 25 à 39, 0,93 de 40 à 49, 0,95 de 50 à 54, 0,85
#: ensuite —, et le temps partiel s'y ajoute. Le sexe n'y entre pas : le
#: volume de chacun, divisé par ce que lui retire son temps partiel
#: (``temps_partiel.csv``, ``quotite_temps_partiel.csv``), laisse la même part
#: de l'année, 0,825 pour les femmes et 0,821 pour les hommes en 2023.
VOLUME_DE_TRAVAIL = True

#: Le volume selon le rang : la classe de chaque centile du salariat privé
#: prend en outre le volume de la catégorie qu'elle représente, rapporté à
#: celui de l'ensemble — employés au dixième centile (0,88), ouvriers au
#: vingt-cinquième (0,95), professions intermédiaires au soixante-quinzième
#: (1,08), cadres au-delà (1,13) —, sans jamais dépasser l'année entière. Une
#: convention : l'INSEE ne croise pas le rang du salaire et le volume, et
#: celui des employés compte aussi leur temps partiel. Embrayée à la
#: neuvième version : elle creuse le minimum contributif, 17,2 % des
#: liquidants de 2023 au lieu de 13,6 (EACR 18,8), et rapproche de l'EIR la
#: distribution des pensions, mais abaisse encore celles des hommes.
VOLUME_SELON_LE_RANG = True

#: L'emploi fragmenté : le volume plus faible des classes du bas ne pèse pas
#: sur toutes leurs carrières un peu, mais sur une part d'entre elles
#: beaucoup. Sous :data:`VOLUME_SELON_LE_RANG`, une classe dont la catégorie
#: travaille moins que l'ensemble se scinde : une part y est fragmentée toute
#: la carrière, au volume des salariés du privé à bas revenu salarial
#: rapporté à celui de tous — 748 heures dans l'année pour 1 536 en moyenne
#: des centiles, 0,487 (``heures_salariees.csv``) —, le reste au volume de
#: l'ensemble, et la part est celle qui garde le volume de la catégorie : 22,8 %
#: des employés, 10,1 % des ouvriers. La masse des salaires ne bouge pas. Deux
#: conventions : la fragmentation dure toute la carrière, quand la moitié des
#: bas revenus salariaux de 2011 le sont encore en 2019 (le dossier de la
#: Dares qui publie les heures), et elle ne change pas d'une génération à
#: l'autre, aucune source ne le disant. Une carrière fragmentée valide moins
#: de trimestres, avant 2014 surtout.
EMPLOI_FRAGMENTE = True

#: Les catégories que le volume selon le rang prête aux classes de centiles.
CATEGORIE_DU_RANG = {"p10": "employes", "p25": "ouvriers", "p50": "ensemble",
                     "p75": "professions_intermediaires", "p90": "cadres",
                     "p95": "cadres", "p99": "cadres"}

#: Les tranches d'âge de ``volume_travail.csv``, par leur premier âge.
AGES_DU_VOLUME = {"Y_LT25": 0, "Y25T39": 25, "Y40T49": 40, "Y50T54": 50, "Y_GE55": 55}

#: Le rang de salaire selon la durée : hors des régimes statutaires, chaque
#: tranche de durée validée prend les classes de centiles de son sexe dans la
#: proportion que l'EIR mesure, et non plus dans celle de tous. L'EIR range les
#: retraités par quintile de leur pension en équivalent carrière complète — ce
#: qu'ils ont acquis par année validée — et croise ces quintiles avec les
#: tranches (``quintiles_eqcc.csv``) : 80,5 % des femmes et 74,0 % des hommes
#: de moins de dix années validées sont au premier, pour 10,1 % et 3,7 % de
#: ceux de quarante ans et plus. Chaque quintile se lit comme une bande de
#: rangs du sexe, de la largeur de sa part des retraités du sexe ; une classe
#: de centiles reçoit de chaque bande la part de ses rangs qui y tombe. Ce
#: tableau croisé de l'EIR est ensuite calé, par la méthode des marges, sur
#: les parts des tranches de la population et le poids de chaque classe : la
#: distribution des salaires de chaque sexe ne bouge pas, et l'association de
#: la durée et du rang reste celle de l'EIR. Une convention : le rang de la
#: pension par année validée est tenu pour celui du salaire, et celui de tous
#: les retraités du sexe pour celui des salariés du privé.
RANG_SELON_LA_DUREE = True

#: Les retraités au minimum, rangés au premier quintile : sous
#: :data:`RANG_SELON_LA_DUREE`, la part de chaque quintile que l'EIR trouve au
#: minimum de pension de son régime principal (``quintiles_eqcc.csv``) quitte
#: la bande de rangs de son quintile pour celle du premier, avec ses tranches
#: de durée. Leur quintile dit le minimum, non leur salaire : le minimum
#: contributif ne relève que la pension d'un salaire annuel moyen inférieur au
#: double de son montant, ce que seuls les plus bas salaires donnent. Le
#: deuxième quintile de l'EIR compte 59,9 % de femmes et 32,6 % d'hommes au
#: minimum, que la sixième version payait comme ses rangs. Une convention : au
#: minimum ou non, les retraités d'un quintile ont les mêmes tranches de durée.
MINIMUM_AU_PREMIER_QUINTILE = True

#: La quinzième version (action 138, étape 14, le 16 octobre 2026) : une part
#: des carrières incomplètes de chaque sexe part avec une décote — à l'âge où
#: le droit ouvre la liquidation (``regle_liquidation="ouverture"``), et non au
#: taux plein —, et perd avec lui le minimum contributif, qui ne relève que les
#: pensions au taux plein. La part est celle que l'EIR mesure aux résidents du
#: sexe (``part_decote`` de ``quintiles_eqcc_residents.csv`` : 8,8 % des
#: femmes, 4,5 % des hommes), rapportée au poids des carrières incomplètes du
#: salariat et des non-salariés (:func:`incomplete`), les seules à qui la
#: population en donne ; les carrières pleines y ont la durée à l'ouverture, et
#: les statutaires gardent leur départ. La mesure le juge quintile par quintile,
#: l'EIR comptant 17,5 % de départs avec décote au premier quintile des femmes,
#: 4,6 à 5,4 aux autres. Deux conventions : la décote se prend à l'âge
#: d'ouverture, et la part ne dépend ni du rang de salaire ni de la tranche.
DEPARTS_AVEC_DECOTE = True

#: La dix-septième version (action 138, étape 14, le 16 octobre 2026) : les
#: retraités de l'Ircantec sont, pour la plupart, des salariés du privé passés
#: par un contrat public, et non des contractuels de toute une carrière.
#: L'Ircantec leur a servi 3 990 M€ en 2023 (``depenses_retraite_regimes.csv``),
#: à 2 066 393 retraités (``effectifs_retraites.csv``) : 161 € par mois, réversions
#: comprises, quand le contractuel de la population, de toute sa carrière, en
#: liquide 540 € dans la génération 1950 et 630 € dans celle de 1958. Il
#: n'avait ni le volume de travail, ni l'emploi fragmenté, ni le Smic
#: persistant du salariat privé, et aucun n'atteignait le minimum contributif
#: : 9,5 % des hommes liquidants du régime général de 2022 et 2023. Sous cette
#: constante, la population n'a plus de contractuel : la Cnav garde ceux
#: qu'elle compte aussi, et le gabarit du salariat privé les porte, une
#: pension de l'Agirc-Arrco tenant lieu de la petite pension de l'Ircantec.
#: La grille « ensemble » et celles de la page gardent leur contractuel.
CONTRACTUELS_AU_SALARIAT = True

#: Les salariés agricoles, distingués dans la mesure du minimum contributif
#: (action 138, étape 14, le 16 octobre 2026). Le droit de la MSA salariés est
#: celui du régime général : une carrière du salariat privé, affiliée comme
#: salarié agricole, y liquide la même pension et le même minimum, au centime.
#: La population ne leur donne donc pas d'autres carrières, mais une part de
#: chacune de celles du salariat privé (:func:`fractions_agricoles`) : celle
#: que l'EIR donne à la MSA salariés parmi les retraités du régime général et
#: d'elle, résidents de chaque quintile de la pension en équivalent carrière
#: complète (``quintiles_eqcc_residents.csv``), lue sur la bande de rangs de
#: chaque classe de centiles comme sous :data:`RANG_SELON_LA_DUREE`, et, pour
#: les retraités de l'étranger, celle que l'EIR leur donne par différence
#: (:func:`parts_agricoles`). La mesure en tire une part au minimum des
#: salariés agricoles et une de la Cnav, que l'EACR juge chacune ; celle des
#: régimes alignés ne bouge pas.
SALARIES_AGRICOLES = True

#: Les indépendants à la dispersion de leurs revenus (action 138, étape 14, le
#: 17 octobre 2026). L'artisan — les artisans et les commerçants — prenait,
#: comme les autres groupes, la dispersion des salaires de son sexe, ceux des
#: temps complets du privé : dans la coupe de 2024, le premier décile vaut
#: 0,62 fois la médiane des femmes, 0,61 celle des hommes, et aucun artisan
#: n'atteignait le minimum contributif. Sous cette constante, il prend celle
#: des revenus des non-salariés classiques de son sexe en 2022
#: (``revenus_non_salaries.csv``, :func:`dispersion_des_independants`) : 0,23
#: et 0,22. Trois conventions. Les revenus nuls ou déficitaires de l'année, un
#: dixième des non-salariés, n'y sont pas. Le 95e et le 99e centile, que la
#: fiche par sexe ne publie pas, prolongent le neuvième décile par la queue de
#: Pareto de l'ensemble des non-salariés classiques. Et la coupe se resserre
#: en carrière comme celle des salaires (:data:`DISPERSION_DE_CARRIERE`), faute
#: d'une source sur la part passagère du revenu d'un indépendant, qui la
#: resserrerait davantage. Le champ de l'INSEE compte aussi les professions
#: libérales : celles de la population gardent la dispersion des salaires en
#: attendant leur déclinaison par section (action 152, au propriétaire), et
#: l'exploitant agricole, hors du champ, la sienne. La mesure juge l'artisan
#: sur les anciens artisans et commerçants de l'EIR
#: (:func:`confronter_non_salaries`).
INDEPENDANTS_A_LEUR_DISPERSION = True

#: Les indépendants à leur part de femmes (le même jour). La population donnait
#: à chaque cas type la part de femmes de son groupe : l'artisan, du régime
#: général, en comptait 55 %, quand les anciens artisans et commerçants de
#: l'EIR n'en comptent que 28 %, 140 milliers sur 500
#: (``pensions_non_salaries.csv``). 3,8 % des femmes de la population étaient
#: des artisanes, pour 1,7 % dans l'EIR, et 3,2 % de ses hommes des artisans,
#: pour 5,0 %. Sous cette constante, l'artisan prend la part de ses anciens
#: (:func:`femmes_des_independants`), et les hommes du reste de son groupe, le
#: salariat privé, donnent ce qui manque à celle que l'EIR mesure au groupe.
INDEPENDANTS_A_LEUR_PART_DE_FEMMES = True

#: Les cas types dont le revenu est celui d'un non-salarié classique, et le
#: régime principal sous lequel la fiche 1.11 de l'INSEE compte leurs anciens
#: (``pensions_non_salaries.csv``).
INDEPENDANTS = {"artisan": "artisans_commercants"}

#: Les quantiles que la fiche par sexe publie, et le centile de la population
#: que chacun tient.
QUANTILES_NON_SALARIES = (("d1", "p10"), ("q1", "p25"), ("mediane", "p50"),
                          ("q3", "p75"), ("d9", "p90"))

#: Les quartiles de la pension que la fiche 1.11 publie, et leur rang.
QUARTILES = (("q1", 0.25), ("mediane", 0.50), ("q3", 0.75))

#: Les quintiles de la pension en équivalent carrière complète, dans l'ordre.
QUINTILES_EQCC = ("q1", "q2", "q3", "q4", "q5")


def _par_generation(paires: tuple[tuple[int, float], ...], generation: int,
                    defaut: float) -> float:
    """La valeur de ``generation`` dans des paires ``(génération, valeur)``
    triées : celle de la dernière génération qui ne la passe pas, et la
    première avant elles."""
    if not paires:
        return defaut
    valeur = paires[0][1]
    for annee, suivante in paires:
        if annee > generation:
            break
        valeur = suivante
    return valeur


@dataclass(frozen=True)
class CasTypeLarge(CasType):
    """Un cas type de la grille élargie : celui du dépôt, décliné.

    ``avant`` : les métiers qui précèdent le sien, chacun ``(affiliation,
    années)``, au même niveau de salaire — la carrière mêlée d'un
    polypensionné. Sans eux, la carrière est celle du cas type.

    La population (:func:`population`) ajoute deux choses qu'aucun cas type du
    dépôt n'a : un niveau de salaire qui dépend de la génération (``niveaux``,
    paires ``(génération, niveau)`` triées), et le temps partiel, de l'âge
    ``ages_partiel[0]`` à l'âge ``ages_partiel[1]`` exclu, à la quotité de la
    génération (``quotites``). Les années d'interruption restent ce qu'elles
    sont. Une carrière ``persistante`` est payée le Smic de chaque année, et
    ses ``niveaux`` sont ceux du Smic. ``volumes`` — paires ``(âge, part de
    l'année)`` triées — paie chaque année d'activité à la part de l'année
    travaillée à son âge. ``entrees`` — paires ``(génération, âge)`` triées —
    fait commencer la carrière de chaque génération à son âge, les années
    d'interruption comptées de lui.
    """

    avant: tuple[tuple[str, float], ...] = ()
    niveaux: tuple[tuple[int, float], ...] = ()
    ages_partiel: tuple[float, ...] = ()
    quotites: tuple[tuple[int, float], ...] = ()
    plancher_smic: bool = False
    persistante: bool = False
    volumes: tuple[tuple[int, float], ...] = ()
    entrees: tuple[tuple[int, float], ...] = ()
    tranche_de_base: tuple = ()
    cibles: tuple[tuple[int, float], ...] = ()

    def niveau_de(self, generation: int) -> float:
        """Le niveau de salaire de cette génération."""
        return _par_generation(self.niveaux, generation, self.niveau_salaire)

    def decalages_de(self, generation: int) -> tuple[tuple[int, str], ...]:
        """Les interruptions de cette génération : celles du cas type, ou, pour
        une carrière incomplète dont la durée suit la génération (``cibles``,
        :data:`DUREE_DES_FEMMES_SELON_LA_GENERATION`), celles de ses années
        validées de cette génération (:func:`decalages_de_tranche`)."""
        if not self.cibles:
            return self.interruptions_relatives
        base, duree, assimilee, etalee = self.tranche_de_base
        cible = int(round(_par_generation(self.cibles, generation, 0.0)))
        return decalages_de_tranche(base, duree, cible, assimilee, etalee, self.age_debut)

    def debut_de(self, generation: int) -> float:
        """L'âge d'entrée de cette génération : celui des ``entrees``, paires
        ``(génération, âge)`` triées (:data:`ENTREE_SELON_LA_GENERATION`), ou
        celui du cas type."""
        return _par_generation(self.entrees, generation, self.age_debut)

    def au_smic(self, simulateur: Simulateur, generation: int) -> bool:
        """Vrai si la carrière se paie au Smic : persistante, ou, sous
        plancher, si son rang tombe sous lui l'année où sa génération a
        :data:`AGE_DU_RANG` ans."""
        if self.persistante:
            return True
        if not self.plancher_smic:
            return False
        annee = generation + AGE_DU_RANG
        macro = simulateur.macro
        return self.niveau_de(generation) < (macro.smic_annuel(annee)
                                             / salaire_moyen_annuel(macro, annee))

    def niveau_relatif(self, simulateur: Simulateur, generation: int) -> float:
        if self.niveaux:
            return self.niveau_de(generation)
        return super().niveau_relatif(simulateur, generation)

    def _temps_partiel(self, generation: int, interruptions: dict[int, str]
                       ) -> dict[int, float] | None:
        """La part de chaque année d'activité que la carrière travaille : la
        quotité de son temps partiel, fois la part de l'année à son âge."""
        if not (self.ages_partiel or self.volumes):
            return None
        quotite = _par_generation(self.quotites, generation, 1.0)
        debut, fin = self.ages_partiel or (0.0, 0.0)
        parts = {}
        for age in range(int(self.debut_de(generation)), AGE_FIN_INACTIVITE + 1):
            annee = generation + age
            if annee in interruptions:
                continue
            part = _par_generation(self.volumes, age, 1.0)
            if int(generation + debut) <= annee < int(generation + fin):
                part *= quotite
            if part != 1.0:
                parts[annee] = part
        return parts or None

    def _carriere(self, simulateur: Simulateur, generation: int, age_liquidation: float):
        if not (self.avant or self.niveaux or self.ages_partiel or self.volumes
                or self.entrees or self.cibles):
            return super()._carriere(simulateur, generation, age_liquidation)
        entree = self.debut_de(generation)
        interruptions = {
            int(generation + entree + decalage): motif
            for decalage, motif in self.decalages_de(generation)
        }
        niveau, profil = self.niveau_de(generation), self.profil_carriere
        if self.au_smic(simulateur, generation):
            niveau, profil = 1.0, PROFIL_SMIC
        metiers, age = [], entree
        for affiliation, annees in self.avant:
            metiers.append(Metier(affiliation=affiliation, age_debut=age,
                                  niveau_salaire=niveau))
            age += annees
        metiers.append(Metier(affiliation=self.affiliation, age_debut=age,
                              niveau_salaire=niveau))
        return simulateur.carriere_parcours(
            annee_naissance=generation, sexe=self.sexe, metiers=metiers,
            age_liquidation=age_liquidation, profil_carriere=profil,
            interruptions=interruptions,
            temps_partiel=self._temps_partiel(generation, interruptions),
            nombre_enfants=self.nombre_enfants, part_primes=self.part_primes,
            identifiant=f"{self.libelle} (génération {generation})")


def elargi(cas: CasType, **changements) -> CasTypeLarge:
    """Le cas type en cas type de la grille élargie, avec ces changements."""
    if not isinstance(cas, CasTypeLarge):
        cas = CasTypeLarge(**{f.name: getattr(cas, f.name) for f in fields(CasType)})
    return replace(cas, **changements)


@dataclass(frozen=True)
class Variante:
    """Une carrière de la grille élargie, et ce qu'elle pèse.

    Le poids se dit en PARTS d'effectifs de caisse, que la page lit année par
    année : ``retraites`` pour les masses de pensions, ``cotisants`` pour les
    masses de cotisations. Une part peut être négative : l'effectif d'une caisse
    que la Cnav compte aussi s'y retranche.
    """

    cas: CasType
    groupe: str
    retraites: tuple[tuple[str, float], ...]
    cotisants: tuple[tuple[str, float], ...]
    #: La durée validée hors majorations que la carrière vise, en années ;
    #: ``None`` pour celle du cas type.
    duree: int | None = None
    #: Les années assimilées : validées sans être cotisées.
    assimilees: int = 0
    poly: bool = False
    #: Le multiplicateur de salaire, la moyenne du cas type valant un.
    salaire: float = 1.0
    #: La tranche de durée de :data:`TRANCHES` où les interruptions l'ont
    #: rangée ; ``None`` hors d'elles.
    tranche: str | None = None
    #: Part-elle à l'ouverture du droit, avec une décote
    #: (:data:`DEPARTS_AVEC_DECOTE`) ?
    decote: bool = False

    def fois(self, part: float, **changements) -> "Variante":
        """La même, pour ``part`` de son poids, avec ces changements."""
        return replace(self, retraites=_echelle(self.retraites, part),
                       cotisants=_echelle(self.cotisants, part), **changements)


def _echelle(parts: tuple[tuple[str, float], ...], facteur: float):
    return tuple((caisse, part * facteur) for caisse, part in parts)


class EffectifsRepartis:
    """Les effectifs d'une caisse, et ceux des pseudo-caisses de la grille.

    Chaque variante réclame une caisse à elle, dont l'effectif est la somme de
    ses parts d'effectifs réels : ``poids_effectifs`` la lit comme une autre,
    et la page n'en sait rien. Une caisse réelle passe telle quelle.
    """

    def __init__(self, base, parts: dict[str, tuple[tuple[str, float], ...]]):
        self.base, self.parts = base, parts

    def effectif(self, caisse: str, annee: int) -> float:
        if caisse in self.parts:
            return somme_ordonnee(self.base.effectif(reelle, annee) * part
                       for reelle, part in self.parts[caisse])
        return self.base.effectif(caisse, annee)

    def fiabilite(self, caisse: str, annee: int):
        if caisse in self.parts:
            return min(self.base.fiabilite(reelle, annee)
                       for reelle, _ in self.parts[caisse])
        return self.base.fiabilite(caisse, annee)


# -- les données ------------------------------------------------------------------

def eir(racine: Path) -> CaracteristiquesRetraites:
    """Les caractéristiques des retraités de l'EIR, et, sous
    :data:`DUREES_DES_RESIDENTS`, les durées des seuls résidents en France."""
    tous = CaracteristiquesRetraites(racine)
    return DureesDesResidents(tous, racine) if DUREES_DES_RESIDENTS else tous


class DureesDesResidents:
    """Les caractéristiques de tous les retraités, leurs durées remplacées par
    celles des seuls résidents en France (:data:`DUREES_DES_RESIDENTS`) : la
    colonne « ensemble » de leurs quintiles en équivalent carrière complète
    (``quintiles_eqcc_residents.csv``). Le reste, ce qu'en dit tous."""

    INDICATEURS = ("duree_validee_hors_majoration", "duree_cotisee",
                   "part_duree_validee_hors_majoration_moins_10",
                   "part_duree_validee_hors_majoration_10_20",
                   "part_duree_validee_hors_majoration_20_30",
                   "part_duree_validee_hors_majoration_30_40",
                   "part_duree_validee_hors_majoration_40_plus")

    def __init__(self, tous: CaracteristiquesRetraites, racine: Path) -> None:
        self.tous = tous
        self.residents = quintiles_eqcc(racine, residents=True)

    def valeur(self, indicateur: str, sexe: str) -> float:
        if indicateur in self.INDICATEURS:
            return self.residents[("ensemble", indicateur, sexe)]
        return self.tous.valeur(indicateur, sexe)

    def __getattr__(self, nom: str):
        return getattr(self.tous, nom)


def centiles(racine: Path) -> tuple[int, dict[str, float]]:
    """Les sept centiles de la dernière année qui les publie tous, rapportés à
    la moyenne : ``dispersion_salaires.csv``."""
    chemin = racine / "reference" / "macro" / "dispersion_salaires.csv"
    with chemin.open(encoding="utf-8") as flux:
        lignes = list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))
    par_annee: dict[int, dict[str, float]] = {}
    for ligne in lignes:
        par_annee.setdefault(int(ligne["annee"]), {})[ligne["centile"]] = float(
            ligne["salaire_relatif"])
    noms = {nom for nom, _ in CENTILES}
    annee = max(a for a, valeurs in par_annee.items() if noms <= set(valeurs))
    return annee, par_annee[annee]


def multiplicateurs(valeurs: dict[str, float]) -> tuple[tuple[str, float, float], ...]:
    """Chaque centile, sa part, et son multiplicateur : la moyenne pondérée des
    sept vaut un, et chaque cas type garde son niveau moyen."""
    moyenne = somme_ordonnee(valeurs[nom] * part for nom, part in CENTILES)
    return tuple((nom, part, valeurs[nom] / moyenne) for nom, part in CENTILES)


def _lire_macro(racine: Path, nom: str) -> list[dict[str, str]]:
    """Les lignes d'un fichier de ``reference/macro/``, commentaires ôtés."""
    with (racine / "reference" / "macro" / nom).open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


@dataclass(frozen=True)
class DonneesPopulation:
    """Ce que la population lit des distributions publiées, sexe par sexe.

    ``niveaux`` : le niveau du salariat privé à chaque centile, génération par
    génération ; ``parts_partiel`` : la part des carrières à temps partiel ;
    ``quotites`` : la quotité de ce temps partiel, génération par génération ;
    ``points`` : les multiplicateurs que les autres groupes gardent autour de
    leur niveau, ceux de la grille élargie, mais de leur sexe ;
    ``persistants`` : la part des carrières payées le Smic toute la carrière
    (:data:`PERSISTANCE_SMIC`) ; ``smic`` : le Smic, en multiple du salaire
    moyen, l'année où chaque génération a :data:`AGE_DU_RANG` ans ;
    ``reste_du_bas`` : le niveau du reste de la classe du bas, qui en garde la
    moyenne ; ``volumes`` : la part de l'année travaillée, par âge
    (:data:`VOLUME_DE_TRAVAIL`) ; ``rangs`` : le volume relatif que chaque
    classe de centiles prend sous :data:`VOLUME_SELON_LE_RANG` ;
    ``quintiles`` : les quintiles de la pension en équivalent carrière
    complète de l'EIR (:data:`RANG_SELON_LA_DUREE`) ; ``ecarts_du_bas`` : les
    niveaux relatifs des sous-classes du reste de la classe du bas
    (:data:`SOUS_CLASSES_DU_BAS`) ; ``entrees`` : l'âge d'entrée des carrières
    pleines, génération par génération (:data:`ENTREE_SELON_LA_GENERATION`) ;
    ``fragmente`` : le volume relatif d'une carrière fragmentée
    (:data:`EMPLOI_FRAGMENTE`) ; ``independants`` : les multiplicateurs que
    les indépendants prennent au lieu des ``points``
    (:data:`INDEPENDANTS_A_LEUR_DISPERSION`).
    """

    niveaux: dict[tuple[str, str], tuple[tuple[int, float], ...]]
    parts_partiel: dict[str, float]
    quotites: dict[str, tuple[tuple[int, float], ...]]
    points: dict[str, tuple[tuple[str, float, float], ...]]
    persistants: dict[str, float]
    smic: tuple[tuple[int, float], ...]
    reste_du_bas: dict[str, tuple[tuple[int, float], ...]]
    volumes: tuple[tuple[int, float], ...]
    rangs: dict[str, float]
    quintiles: dict[tuple[str, str, str], float]
    ecarts_du_bas: dict[str, tuple[tuple[int, tuple[float, ...]], ...]]
    entrees: dict[str, tuple[tuple[int, float], ...]]
    fragmente: float
    independants: dict[str, tuple[tuple[str, float, float], ...]]


def resserrer(relatifs: dict[str, float], moyenne: float) -> dict[str, float]:
    """D'une coupe de l'année, une carrière : les écarts des sept points au
    centre du logarithme ramenés à :data:`DISPERSION_DE_CARRIERE` fois les
    leurs, et leur moyenne discrétisée portée à ``moyenne``."""
    centre = somme_ordonnee(math.log(relatifs[n]) * part for n, part in CENTILES)
    resserres = {n: math.exp(centre + DISPERSION_DE_CARRIERE
                             * (math.log(relatifs[n]) - centre))
                 for n, _ in CENTILES}
    discrete = somme_ordonnee(resserres[n] * part for n, part in CENTILES)
    return {n: valeur / discrete * moyenne for n, valeur in resserres.items()}


def niveaux_par_generation(valeurs: dict[tuple[int, str, str], float], sexe: str,
                           centile: str) -> tuple[tuple[int, float], ...]:
    """Le niveau d'un centile de ce sexe, génération par génération, en
    multiples du salaire moyen des deux sexes.

    La FORME de la distribution du sexe — ses centiles rapportés à sa moyenne,
    discrétisés en :data:`CENTILES` et resserrés en carrière (:func:`resserrer`)
    —, au niveau de cette moyenne, l'année où la génération a
    :data:`AGE_DU_RANG` ans : chaque sexe garde sa moyenne, et chaque
    génération l'écart de son temps. Les sept centiles ne se publient par sexe
    que depuis 1994 ; avant, la forme est celle de 1994, et seule la moyenne
    bouge. Elle ne se lit pas aux années de l'activité partielle
    (:data:`ANNEES_ACTIVITE_PARTIELLE`), mais à la plus proche.
    """
    moyennes = sorted(a for a, s, c in valeurs if s == sexe and c == "moyenne")
    paires = []
    for annee in moyennes:
        forme = forme_de(valeurs, sexe, annee)
        relatifs = {n: valeurs[(forme, sexe, n)] / valeurs[(forme, sexe, "moyenne")]
                    for n, _ in CENTILES}
        niveaux = resserrer(relatifs, valeurs[(annee, sexe, "moyenne")])
        paires.append((annee - AGE_DU_RANG, niveaux[centile]))
    return tuple(paires)


def forme_de(valeurs: dict[tuple[int, str, str], float], sexe: str, annee: int) -> int:
    """L'année dont la coupe donne sa forme à ``annee`` : la plus proche où
    les sept centiles du sexe se publient, hors des années de l'activité
    partielle (:data:`ANNEES_ACTIVITE_PARTIELLE`)."""
    formes = [a for a, s, c in valeurs if s == sexe and c == "moyenne"
              and a not in ANNEES_ACTIVITE_PARTIELLE
              and all((a, sexe, n) in valeurs for n, _ in CENTILES)]
    return min(formes, key=lambda candidate: (abs(candidate - annee), candidate))


def ecarts_du_bas(valeurs: dict[tuple[int, str, str], float], sexe: str,
                  persistants: float, sous_classes: int
                  ) -> tuple[tuple[int, tuple[float, ...]], ...]:
    """Les niveaux des sous-classes du reste de la classe du bas, rapportés à
    celui du reste, génération par génération : leur moyenne vaut un
    (:data:`SOUS_CLASSES_DU_BAS`).

    Le reste couvre les rangs de la coupe de ``persistants`` au haut de la
    classe ; chaque sous-classe en prend une part égale, au niveau que la coupe
    de la forme de l'année (:func:`forme_de`) donne au milieu de ses rangs —
    au logarithme, la droite des deux premiers centiles, prolongée sous le
    premier —, son écart ramené à :data:`DISPERSION_DE_CARRIERE` fois le sien.
    """
    (bas, poids_du_bas), (second, _) = CENTILES[0], CENTILES[1]
    rang_bas, rang_second = int(bas[1:]) / 100.0, int(second[1:]) / 100.0
    largeur = (poids_du_bas - persistants) / sous_classes
    milieux = [persistants + (k + 0.5) * largeur for k in range(sous_classes)]
    centre = somme_ordonnee(milieux) / sous_classes
    paires = []
    for annee in sorted(a for a, s, c in valeurs if s == sexe and c == "moyenne"):
        forme = forme_de(valeurs, sexe, annee)
        pente = (math.log(valeurs[(forme, sexe, second)] / valeurs[(forme, sexe, bas)])
                 / (rang_second - rang_bas))
        bruts = [math.exp(DISPERSION_DE_CARRIERE * pente * (milieu - centre))
                 for milieu in milieux]
        moyenne = somme_ordonnee(bruts) / sous_classes
        paires.append((annee - AGE_DU_RANG, tuple(brut / moyenne for brut in bruts)))
    return tuple(paires)


def part_de_la_coupe_sous(niveau: float, centiles: dict[str, float]) -> float:
    """La part de la coupe de l'année sous ``niveau`` : interpolée au
    logarithme entre les deux centiles publiés qui l'encadrent, prolongée sous
    le premier par la pente des deux premiers, jamais négative."""
    points = sorted((int(nom[1:]) / 100.0, valeur) for nom, valeur in centiles.items())
    (r0, v0), (r1, v1) = points[0], points[1]
    if niveau <= v1:
        return max(0.0, r0 + (r1 - r0) * math.log(niveau / v0) / math.log(v1 / v0))
    for (ra, va), (rb, vb) in zip(points[1:], points[2:]):
        if niveau <= vb:
            return ra + (rb - ra) * math.log(niveau / va) / math.log(vb / va)
    return points[-1][0]


def persistance_a_six_ans(racine: Path) -> dict[str, float]:
    """La part des salariés payés au voisinage du Smic en 2007 qui le sont
    encore en 2013, parmi ceux restés salariés du privé : celle des 35-49 ans,
    au rapport de chaque sexe à l'ensemble des âges, le document ne croisant
    pas le sexe et l'âge (``persistance_smic.csv``)."""
    parts = {(l["sexe"], l["age"], l["etat"]): float(l["part"])
             for l in _lire_macro(racine, "persistance_smic.csv")
             if l["origine"] == "voisinage" and l["annee"] == "2013"}

    def restes(sexe: str, age: str) -> float:
        voisinage = parts[(sexe, age, "voisinage")]
        return voisinage / (voisinage + parts[(sexe, age, "superieur")])

    milieu = restes("ensemble", "Y35T49") / restes("ensemble", "ensemble")
    return {sexe: restes(sexe, "ensemble") * milieu for sexe in ("F", "H")}


def volumes_de_travail(racine: Path) -> tuple[tuple[tuple[int, float], ...], dict[str, float]]:
    """La part de l'année travaillée à chaque âge, et le volume relatif de
    chaque classe de centiles : ceux de ``volume_travail.csv``, la dernière
    année publiée.

    La part de l'année d'une tranche d'âge est son volume, rapporté à celui de
    l'ensemble des salariés, fois celui d'un temps complet : la part de l'année
    qu'un temps complet travaille, que l'âge fait varier.
    """
    lignes = _lire_macro(racine, "volume_travail.csv")
    derniere = max(l["annee"] for l in lignes)
    volume = {(l["caracteristique"], l["modalite"]): float(l["volume"])
              for l in lignes if l["annee"] == derniere}
    ensemble = volume[("ensemble", "ensemble")]
    complet = volume[("quotite", "temps_complet")]
    volumes = tuple(sorted((age, volume[("age", tranche)] / ensemble * complet)
                           for tranche, age in AGES_DU_VOLUME.items()))
    rangs = {nom: (1.0 if categorie == "ensemble"
                   else volume[("categorie", categorie)] / ensemble)
             for nom, categorie in CATEGORIE_DU_RANG.items()}
    return volumes, rangs


def volume_fragmente(racine: Path) -> float:
    """Le volume relatif d'une carrière fragmentée (:data:`EMPLOI_FRAGMENTE`) :
    les heures moyennes des salariés du privé à bas revenu salarial, rapportées
    à celles de tous, en moyenne de leurs centiles publiés
    (``heures_salariees.csv``), la dernière année."""
    lignes = _lire_macro(racine, "heures_salariees.csv")
    derniere = max(l["annee"] for l in lignes)
    moyennes = {}
    for population in ("bas_revenus", "ensemble"):
        heures = [float(l["heures"]) for l in lignes
                  if l["annee"] == derniere and l["population"] == population]
        moyennes[population] = somme_ordonnee(heures) / len(heures)
    return moyennes["bas_revenus"] / moyennes["ensemble"]


def fragmentees(classes: list, relatif: float, fragmente: float,
                volumes: tuple[tuple[int, float], ...]) -> list:
    """Les classes d'une catégorie qui travaille ``relatif`` fois le volume de
    l'ensemble, scindées (:data:`EMPLOI_FRAGMENTE`) : la part fragmentée au
    volume ``fragmente``, le reste au volume de l'ensemble, la part gardant le
    volume de la catégorie. Telles quelles si elle travaille autant ou plus."""
    if relatif >= 1.0:
        return classes
    part = (1.0 - relatif) / (1.0 - fragmente)
    entiers = tuple((age, min(1.0, annee)) for age, annee in volumes)
    reduits = tuple((age, annee * fragmente) for age, annee in volumes)
    sortie = []
    for classe, poids in classes:
        sortie.append((replace(classe, volumes=entiers), poids * (1.0 - part)))
        sortie.append((replace(classe, code=f"{classe.code}~fragmente", volumes=reduits),
                       poids * part))
    return sortie


def quintiles_eqcc(racine: Path, residents: bool = False
                   ) -> dict[tuple[str, str, str], float]:
    """Les quintiles de la pension en équivalent carrière complète, tels que
    l'EIR les publie : ``(quintile, indicateur, sexe)``. Ceux de tous les
    retraités (``quintiles_eqcc.csv``), ou, sous ``residents``, ceux des seuls
    résidents en France (``quintiles_eqcc_residents.csv``), contre lesquels la
    population se mesure : elle ne compte qu'eux."""
    fichier = "quintiles_eqcc_residents.csv" if residents else "quintiles_eqcc.csv"
    return {(l["quintile"], l["indicateur"], l["sexe"]): float(l["valeur"])
            for l in _lire_macro(racine, fichier)}


def association_rang_duree(quintiles: dict, sexe: str) -> dict[str, dict[str, float]]:
    """Le tableau croisé des tranches de durée et des classes de centiles d'un
    sexe, en parts de ses retraités, que l'EIR donne (:data:`RANG_SELON_LA_DUREE`).

    Chaque quintile est une bande de rangs du sexe, de la largeur de sa part des
    retraités du sexe que les quintiles rangent ; la masse d'une tranche dans
    un quintile se répartit sur sa bande, et chaque classe de centiles en
    reçoit la part que ses rangs couvrent. Sous
    :data:`MINIMUM_AU_PREMIER_QUINTILE`, la part de chaque quintile au minimum
    passe, avec ses tranches, dans la bande du premier."""
    effectifs = [quintiles[(q, "effectifs", sexe)] for q in QUINTILES_EQCC]
    total = somme_ordonnee(effectifs)
    au_minimum = [quintiles[(q, "part_minimum_pension_regime_principal", sexe)] / 100.0
                  if MINIMUM_AU_PREMIER_QUINTILE and rang > 0 else 0.0
                  for rang, q in enumerate(QUINTILES_EQCC)]

    def au_premier(parts: list[float]) -> list[float]:
        """Des parts de quintile, celles au minimum passées au premier."""
        restes = [part * (1.0 - minimum) for part, minimum in zip(parts, au_minimum)]
        restes[0] += somme_ordonnee(part * minimum for part, minimum in zip(parts, au_minimum))
        return restes

    bandes, debut = [], 0.0
    for largeur in au_premier([effectif / total for effectif in effectifs]):
        bandes.append((debut, debut + largeur))
        debut += largeur
    classes, debut = [], 0.0
    for nom, part in CENTILES:
        classes.append((nom, debut, debut + part))
        debut += part
    tableau = {}
    for tranche, _ in TRANCHES:
        masses = au_premier([
            effectif / total
            * quintiles[(q, f"part_duree_validee_hors_majoration_{tranche}", sexe)] / 100.0
            for q, effectif in zip(QUINTILES_EQCC, effectifs)])
        tableau[tranche] = {
            nom: somme_ordonnee(masse * max(0.0, min(fin, haut) - max(bas, plancher))
                                / (haut - plancher)
                                for masse, (plancher, haut) in zip(masses, bandes))
            for nom, bas, fin in classes}
    return tableau


def caler(tableau: dict[str, dict[str, float]], lignes: dict[str, float],
          colonnes: dict[str, float], tolerance: float = 1e-12) -> dict[str, dict[str, float]]:
    """Le tableau croisé calé sur ces marges par la méthode des marges (ajustement
    proportionnel itératif) : il en prend les sommes de lignes et de colonnes,
    et garde ses rapports croisés — l'association de ses lignes et de ses
    colonnes."""
    cale = {ligne: dict(cases) for ligne, cases in tableau.items() if ligne in lignes}
    for _ in range(100_000):
        for ligne, cible in lignes.items():
            somme = somme_ordonnee(cale[ligne].values())
            cale[ligne] = {colonne: case * cible / somme
                           for colonne, case in cale[ligne].items()}
        ecart = 0.0
        for colonne, cible in colonnes.items():
            somme = somme_ordonnee(cases[colonne] for cases in cale.values())
            ecart = max(ecart, abs(somme - cible))
            for cases in cale.values():
                cases[colonne] *= cible / somme
        if ecart < tolerance:
            return cale
    raise RuntimeError("le calage du rang selon la durée ne converge pas")


def rangs_selon_la_duree(quintiles: dict, parts: dict[str, dict[str, float]]
                         ) -> dict[str, dict[str, dict[str, float]]]:
    """Les poids des classes de centiles de chaque tranche de durée, sexe par
    sexe : le tableau croisé de l'EIR (:func:`association_rang_duree`) calé
    sur ``parts``, la part de chaque tranche dans la population, et sur le
    poids de chaque classe (:data:`CENTILES`), puis lu tranche par tranche."""
    rangs = {}
    for sexe, lignes in parts.items():
        cale = caler(association_rang_duree(quintiles, sexe), lignes, dict(CENTILES))
        rangs[sexe] = {tranche: {nom: case / somme_ordonnee(cases.values())
                                 for nom, case in cases.items()}
                       for tranche, cases in cale.items()}
    return rangs


def parts_des_tranches(variantes: list[Variante]) -> dict[str, dict[str, float]]:
    """La part de chaque tranche de durée dans le salariat privé de chaque sexe,
    que les interruptions lui ont donnée ; les autres groupes qui en ont la
    partagent. Elle se lit sur la part de la Cnav, la première caisse du
    salariat privé : celle de l'Ircantec, que la Cnav compte aussi, s'y
    retranche à la même part."""
    masses: dict[str, dict[str, float]] = {}
    for v in variantes:
        if v.tranche is None or v.cas.code.split("~", 1)[0] != GABARIT:
            continue
        parts = masses.setdefault(v.cas.sexe, {})
        parts[v.tranche] = parts.get(v.tranche, 0.0) + v.retraites[0][1]
    sortie = {}
    for sexe, parts in masses.items():
        total = somme_ordonnee(parts.values())
        sortie[sexe] = {tranche: masse / total for tranche, masse in parts.items()}
    return sortie


def centiles_des_non_salaries(valeurs: dict[tuple[str, str], float],
                              sexe: str) -> dict[str, float]:
    """Les sept centiles du revenu positif des non-salariés classiques d'un
    sexe, en euros par mois : les cinq que la fiche par sexe publie
    (:data:`QUANTILES_NON_SALARIES`), puis le 95e et le 99e, que le neuvième
    décile prolonge par la queue de Pareto de l'ensemble, le rapport de son 99e
    centile à son neuvième décile. ``valeurs`` : ``(sexe, indicateur) →
    valeur``, de ``revenus_non_salaries.csv``."""
    sortie = {centile: valeurs[(sexe, code)] for code, centile in QUANTILES_NON_SALARIES}
    pente = math.log(valeurs[("ensemble", "c99")] / valeurs[("ensemble", "d9")]) / math.log(10.0)
    sortie["p95"] = sortie["p90"] * 2.0 ** pente
    sortie["p99"] = sortie["p90"] * 10.0 ** pente
    return sortie


def dispersion_des_independants(racine: Path
                                ) -> dict[str, tuple[tuple[str, float, float], ...]]:
    """Les multiplicateurs des indépendants (:data:`INDEPENDANTS_A_LEUR_DISPERSION`),
    sexe par sexe : les centiles du revenu des non-salariés classiques du sexe
    (:func:`centiles_des_non_salaries`), resserrés en carrière autour de leur
    moyenne, puis divisés par la moyenne discrétisée des deux sexes réunis,
    comme ceux des salaires (:func:`donnees_population`)."""
    valeurs = {(l["sexe"], l["indicateur"]): float(l["valeur"])
               for l in _lire_macro(racine, "revenus_non_salaries.csv")
               if l["secteur"] == "ensemble"}
    tous = centiles_des_non_salaries(valeurs, "ensemble")
    moyenne = somme_ordonnee(tous[nom] * part for nom, part in CENTILES)
    points = {}
    for sexe in ("F", "H"):
        relatifs = centiles_des_non_salaries(valeurs, sexe)
        resserres = resserrer(relatifs, somme_ordonnee(relatifs[nom] * part
                                                       for nom, part in CENTILES))
        points[sexe] = tuple((nom, part, resserres[nom] / moyenne) for nom, part in CENTILES)
    return points


def donnees_population(racine: Path) -> DonneesPopulation:
    """Les centiles du salaire par sexe, la part du temps partiel à 25-49 ans et
    sa quotité à 25-54 ans, certifiés le 11 octobre 2026, et la persistance au
    Smic, certifiée le même jour."""
    valeurs = {(int(l["annee"]), l["sexe"], l["centile"]): float(l["salaire_relatif"])
               for l in _lire_macro(racine, "dispersion_salaires_sexe.csv")}
    niveaux = {(sexe, nom): niveaux_par_generation(valeurs, sexe, nom)
               for sexe in ("F", "H") for nom, _ in CENTILES}
    partiel = _lire_macro(racine, "temps_partiel.csv")
    quotites = _lire_macro(racine, "quotite_temps_partiel.csv")
    parts, par_generation = {}, {}
    for sexe in ("F", "H"):
        lot = [float(l["part"]) for l in partiel
               if l["sexe"] == sexe and l["tranche"] == "Y25T49"]
        parts[sexe] = somme_ordonnee(lot) / len(lot) / 100.0
        par_generation[sexe] = tuple(sorted(
            (int(l["annee"]) - AGE_DE_LA_QUOTITE, float(l["quotite"]))
            for l in quotites if l["sexe"] == sexe and l["tranche"] == "Y25T54"))
    # Les autres groupes : les centiles de chaque sexe, l'année des centiles de
    # la grille élargie, resserrés en carrière autour de la moyenne du sexe,
    # puis divisés par la moyenne discrétisée des deux sexes réunis — un cas
    # type garde son niveau sur ses deux sexes, à peu près.
    annee, tous = centiles(racine)
    moyenne = somme_ordonnee(tous[nom] * part for nom, part in CENTILES)
    points = {}
    for sexe in ("F", "H"):
        relatifs = {nom: valeurs[(annee, sexe, nom)] for nom, _ in CENTILES}
        resserres = resserrer(relatifs, somme_ordonnee(relatifs[nom] * part
                                                       for nom, part in CENTILES))
        points[sexe] = tuple((nom, part, resserres[nom] / moyenne)
                             for nom, part in CENTILES)
    # La persistance au Smic : la part de la coupe au voisinage du Smic, en
    # moyenne des années où le vingt-cinquième centile se publie par sexe, hors
    # de celles de l'activité partielle, fois la part qui y reste six ans.
    macro = DonneesMacro(racine)

    def smic(annee: int) -> float:
        return macro.smic_annuel(annee) / salaire_moyen_annuel(macro, annee)

    persistance = persistance_a_six_ans(racine)
    bas, poids_du_bas = CENTILES[0]
    persistants, reste = {}, {}
    for sexe in ("F", "H"):
        annees = sorted(a for a, s, n in valeurs if s == sexe and n == "p25"
                        and a not in ANNEES_ACTIVITE_PARTIELLE)
        stocks = [part_de_la_coupe_sous(SEUIL_VOISINAGE * smic(a), {
            n: valeurs[(a, sexe, n)] for n, _ in CENTILES if (a, sexe, n) in valeurs})
            for a in annees]
        persistants[sexe] = somme_ordonnee(stocks) / len(stocks) * persistance[sexe]
        reste[sexe] = tuple(
            (g, (poids_du_bas * niveau - persistants[sexe] * smic(g + AGE_DU_RANG))
             / (poids_du_bas - persistants[sexe]))
            for g, niveau in niveaux[(sexe, bas)])
    au_smic = tuple((g, smic(g + AGE_DU_RANG)) for g, _ in niveaux[("F", bas)])
    volumes, rangs = volumes_de_travail(racine)
    ecarts = {sexe: ecarts_du_bas(valeurs, sexe,
                                  persistants[sexe] if PERSISTANCE_SMIC else 0.0,
                                  SOUS_CLASSES_DU_BAS)
              for sexe in ("F", "H")}
    return DonneesPopulation(niveaux, parts, par_generation, points, persistants,
                             au_smic, reste, volumes, rangs,
                             quintiles_eqcc(racine, residents=DUREES_DES_RESIDENTS), ecarts,
                             entrees_des_carrieres_pleines(racine), volume_fragmente(racine),
                             dispersion_des_independants(racine))


def durees_pleines(racine: Path) -> dict[str, tuple[tuple[int, float], ...]]:
    """La durée des carrières pleines, génération par génération, sexe par
    sexe (:data:`ENTREE_SELON_LA_GENERATION`). Celle des retraités de 2020 se
    déduit de l'EIR : la durée validée moyenne hors majorations, moins ce
    qu'en portent les tranches plus courtes, comptées à leur milieu, rapportée
    à la part de la tranche de quarante ans et plus — 44,1 années pour les
    hommes, 44,0 pour les femmes (``caracteristiques_retraites.csv``). D'une
    génération à l'autre, elle suit la durée d'assurance des hommes autour de
    sa moyenne des générations certifiées (``duree_assurance_generations.csv``) :
    celle des femmes monte surtout de ce que leurs carrières courtes se
    raréfient, que la grille ne sait pas faire varier. Celle de tous les
    retraités, même sous :data:`DUREES_DES_RESIDENTS`."""
    source = CaracteristiquesRetraites(racine)
    hommes = [(int(l["generation"]), float(l["trimestres"]) / 4.0, l["fiabilite"])
              for l in _lire_macro(racine, "duree_assurance_generations.csv")
              if l["sexe"] == "hommes"]
    certifiees = [duree for _, duree, fiabilite in hommes if fiabilite == "haute"]
    reference = somme_ordonnee(certifiees) / len(certifiees)
    sortie = {}
    for sexe in ("F", "H"):
        parts = parts_tranches(source, sexe)
        courtes = somme_ordonnee(parts[nom] * cible for nom, cible in TRANCHES
                                 if cible is not None)
        pleine = (source.valeur("duree_validee_hors_majoration", sexe) - courtes) / parts["40_plus"]
        sortie[sexe] = tuple(sorted((generation, pleine + duree - reference)
                                    for generation, duree, _ in hommes))
    return sortie


def entrees_des_carrieres_pleines(racine: Path) -> dict[str, tuple[tuple[int, float], ...]]:
    """L'âge d'entrée des carrières pleines du salariat privé, génération par
    génération, sexe par sexe : la durée des carrières pleines
    (:func:`durees_pleines`) avant l'âge légal de la génération, à l'année
    près, et à l'entrée du gabarit au plus tard."""
    from retraite_notionnelle.scenarios.actuel import AgesOuverture

    legaux = AgesOuverture(racine)
    gabarit = next(cas for cas in CAS_TYPES if cas.code == "salaire_moyen").age_debut
    sortie = {}
    for sexe, durees in durees_pleines(racine).items():
        entrees = []
        for generation in range(min(g for g, _ in durees) - 40, max(g for g, _ in durees) + 1):
            lu = legaux.age(generation)
            legal = lu[0] if lu is not None else 60.0
            entrees.append((generation, float(min(gabarit, round(
                legal - _par_generation(durees, generation, 0.0))))))
        sortie[sexe] = tuple(entrees)
    return sortie


def _part_eir(source: CaracteristiquesRetraites, groupe: str, sexe: str) -> float:
    """La part des retraités de ce sexe dont le régime principal est celui du
    groupe : monopensionnés et polypensionnés de deux régimes de base."""
    return somme_ordonnee(source.valeur(f"part_{statut}_{indicateur}", sexe)
               for indicateur in GROUPES[groupe][0] for statut in ("mono", "poly"))


def parts_personnes(source: CaracteristiquesRetraites) -> dict[str, float]:
    """La part de chaque groupe parmi les retraités, normalisée sur les
    groupes : le reste — trois régimes et plus, régimes que l'EIR ne nomme
    pas — se répartit au prorata."""
    brutes = {groupe: _part_eir(source, groupe, "ensemble") for groupe in GROUPES}
    total = somme_ordonnee(brutes.values())
    return {groupe: part / total for groupe, part in brutes.items()}


def parts_poly(source: CaracteristiquesRetraites) -> dict[str, float]:
    """La part des polypensionnés parmi les retraités de chaque groupe."""
    sortie = {}
    for groupe in GROUPES_MELES:
        poly = somme_ordonnee(source.valeur(f"part_poly_{i}", "ensemble") for i in GROUPES[groupe][0])
        sortie[groupe] = poly / _part_eir(source, groupe, "ensemble")
    return sortie


def parts_femmes(source: CaracteristiquesRetraites) -> dict[str, float]:
    """La part des femmes parmi les retraités de chaque groupe."""
    femmes = source.valeur("effectifs", "F")
    hommes = source.valeur("effectifs", "H")
    sortie = {}
    for groupe in GROUPES:
        f = _part_eir(source, groupe, "F") * femmes
        h = _part_eir(source, groupe, "H") * hommes
        sortie[groupe] = f / (f + h)
    return sortie


def parts_tranches(source: CaracteristiquesRetraites, sexe: str) -> dict[str, float]:
    """La part de chaque tranche de durée validée hors majorations, normalisée."""
    brutes = {nom: source.valeur(f"part_duree_validee_hors_majoration_{nom}", sexe)
              for nom, _ in TRANCHES}
    total = somme_ordonnee(brutes.values())
    return {nom: part / total for nom, part in brutes.items()}


def part_assimilee(source: CaracteristiquesRetraites, sexe: str) -> float:
    """La part de la durée validée hors majorations qui n'est pas cotisée : les
    périodes assimilées — chômage, maladie, éducation des enfants."""
    validee = source.valeur("duree_validee_hors_majoration", sexe)
    return (validee - source.valeur("duree_cotisee", sexe)) / validee


# -- les grilles -----------------------------------------------------------------

def groupe_de(code: str) -> str:
    for groupe, (_, codes) in GROUPES.items():
        if code in codes:
            return groupe
    raise KeyError(f"cas type sans groupe : {code}")


def reference() -> list[Variante]:
    """La grille du dépôt, en parts : chaque cas type de la grille de la page
    Coût, variantes comprises — l'agent sédentaire de la CNRACL —, la part de sa
    caisse que ``poids_effectifs`` lui donne : celle qu'il déclare, l'effectif
    de la caisse partagé également sinon (``parts_des_caisses``)."""
    parts_de = parts_des_caisses(GRILLE_DU_COUT)
    variantes = []
    for cas in GRILLE_DU_COUT:
        parts = tuple((caisse, parts_de[(cas.code, caisse)]) for caisse in cas.caisses)
        variantes.append(Variante(cas=cas, groupe=groupe_de(cas_type_affiche(cas.code)),
                                  retraites=parts, cotisants=parts))
    return variantes


def poids_retraites(variantes: list[Variante], effectifs, annee: int) -> list[float]:
    return [somme_ordonnee(effectifs.effectif(caisse, annee) * part for caisse, part in v.retraites)
            for v in variantes]


def personnes(variantes: list[Variante], effectifs, source: CaracteristiquesRetraites,
              retirer: tuple[str, ...] = CAISSES_DANS_LA_CNAV) -> list[Variante]:
    """Les poids de PERSONNES : chaque groupe à sa part de l'EIR, l'année de
    l'enquête ; la Cnav sans les caisses ``retirer``, les contractuels qu'elle
    comptait aussi. Les années suivent l'évolution des caisses, le rapport de
    l'enquête gardé."""
    retirees = []
    for v in variantes:
        cnav = somme_ordonnee(part for caisse, part in v.retraites if caisse == "cnav")
        if cnav and retirer:
            v = replace(v, retraites=v.retraites + tuple(
                (caisse, -cnav) for caisse in retirer))
        retirees.append(v)
    annee = source.millesime
    poids = poids_retraites(retirees, effectifs, annee)
    total = somme_ordonnee(poids)
    par_groupe: dict[str, float] = {}
    for v, p in zip(retirees, poids):
        par_groupe[v.groupe] = par_groupe.get(v.groupe, 0.0) + p / total
    cibles = parts_personnes(source)
    return [replace(v, retraites=_echelle(v.retraites, cibles[v.groupe] / par_groupe[v.groupe]))
            for v in retirees]


def affiliation_privee(cas: CasType) -> str:
    """Le salariat du privé d'un polypensionné : cadre au-delà de deux fois le
    salaire moyen, où le libéral se trouve, non cadre en deçà."""
    return "salarie_prive_cadre" if cas.niveau_salaire >= 2.0 else "salarie_prive_non_cadre"


def melees(variantes: list[Variante], source: CaracteristiquesRetraites) -> list[Variante]:
    """Les polypensionnés de deux régimes de base, dans les groupes qui en ont."""
    poly = parts_poly(source)
    sortie = []
    for v in variantes:
        s = poly.get(v.groupe)
        if not s:
            sortie.append(v)
            continue
        cas = elargi(v.cas)
        sortie.append(v.fois(1.0 - s, cas=replace(cas, code=f"{cas.code}~mono")))
        sortie.append(v.fois(s, poly=True, cas=replace(
            cas, code=f"{cas.code}~poly",
            avant=((affiliation_privee(cas), ANNEES_PRIVE),))))
    return sortie


def _placer(occupes: dict[int, str], candidates, n: int, motif: str) -> None:
    """Place ``n`` années de ``motif`` dans les premières années libres de
    ``candidates``, dans leur ordre."""
    for decalage in candidates:
        if n <= 0:
            break
        if decalage not in occupes:
            occupes[decalage] = motif
            n -= 1


def annees_etalees(cible: int, etendue: int) -> tuple[int, ...]:
    """Les décalages de ``cible`` années validées étalées sur ``etendue``
    années : chacune au milieu de sa part égale de l'étendue
    (:data:`COURTES_ETALEES`)."""
    return tuple((2 * rang + 1) * etendue // (2 * cible) for rang in range(cible))


def _interrompre(v: Variante, nom: str, cible: int | None, part: float,
                 assimilee: float, etalee: bool = False) -> Variante | None:
    """La variante dans une tranche de durée : ``cible`` années validées, dont
    une part assimilée au milieu, et l'inactivité jusqu'au départ — après elles,
    ou, sous ``etalee``, entre elles et après elles (:func:`annees_etalees`).
    ``None`` quand la carrière du cas type est déjà plus courte que la
    tranche."""
    cas = v.cas
    duree = int(round(cas.age_liquidation - cas.age_debut))
    if cible is not None and cible >= duree:
        return None
    validee = duree if cible is None else cible
    assimilees = int(round(assimilee * validee))
    nouveau = elargi(cas, code=f"{cas.code}~{nom}",
                     interruptions_relatives=decalages_de_tranche(
                         cas.interruptions_relatives, duree, cible, assimilee, etalee,
                         cas.age_debut),
                     tranche_de_base=(() if cible is None else
                                      (cas.interruptions_relatives, duree, assimilee,
                                       etalee)))
    return v.fois(part, cas=nouveau, duree=validee, assimilees=assimilees, tranche=nom)


def decalages_de_tranche(base: tuple[tuple[int, str], ...], duree: int, cible: int | None,
                         assimilee: float, etalee: bool, age_debut: float
                         ) -> tuple[tuple[int, str], ...]:
    """Les interruptions d'une carrière de ``cible`` années validées
    (:func:`_interrompre`), en décalages de son entrée : celles de ``base`` qui
    tombent dans ses années validées, une part ``assimilee`` de celles-ci au
    chômage indemnisé, au milieu, et, pour une tranche courte, l'inactivité
    ailleurs, jusqu'à :data:`AGE_FIN_INACTIVITE`."""
    validee = duree if cible is None else cible
    assimilees = int(round(assimilee * validee))
    if cible is not None and etalee:
        validees = annees_etalees(cible, max(cible, int(AGE_FIN_ETALEMENT - age_debut)))
    else:
        validees = tuple(range(validee))
    occupes = {d: m for d, m in base if d in validees}
    _placer(occupes, validees[(validee - assimilees) // 2:], assimilees, "chomage_indemnise")
    if cible is not None:
        for decalage in range(int(AGE_FIN_INACTIVITE - age_debut)):
            if decalage not in validees:
                occupes[decalage] = "inactivite"
    return tuple(sorted(occupes.items()))


def femmes(variantes: list[Variante], effectifs,
           source: CaracteristiquesRetraites,
           propres: dict[str, float] | None = None) -> list[Variante]:
    """Les femmes : dans chaque groupe, la part de l'EIR, prise sur les hommes,
    chacune avec ses enfants. Un cas type de ``propres``, par son code, prend la
    part qu'il y porte, et les autres hommes de son groupe donnent ce qui manque
    à celle du groupe."""
    propres = propres or {}
    annee = source.millesime
    poids = poids_retraites(variantes, effectifs, annee)
    femmes_cibles = parts_femmes(source)
    total: dict[str, float] = {}
    deja: dict[str, float] = {}
    hommes_propres: dict[str, float] = {}
    femmes_propres: dict[str, float] = {}
    for v, p in zip(variantes, poids):
        total[v.groupe] = total.get(v.groupe, 0.0) + p
        propre = propres.get(v.cas.code.split("~", 1)[0])
        if v.cas.sexe == "F":
            deja[v.groupe] = deja.get(v.groupe, 0.0) + p
        elif propre is not None:
            hommes_propres[v.groupe] = hommes_propres.get(v.groupe, 0.0) + p
            femmes_propres[v.groupe] = femmes_propres.get(v.groupe, 0.0) + p * propre
    sexuees = []
    for v in variantes:
        cible, libre = femmes_cibles[v.groupe], total[v.groupe]
        if v.groupe in hommes_propres:
            libre -= hommes_propres[v.groupe]
            cible = (cible * total[v.groupe] - femmes_propres[v.groupe]) / libre
        actuelle = deja.get(v.groupe, 0.0) / libre
        f = 0.0 if actuelle >= cible else (cible - actuelle) / (1.0 - actuelle)
        propre = propres.get(v.cas.code.split("~", 1)[0])
        if propre is not None and v.cas.sexe != "F":
            f = propre
        if v.cas.sexe == "F" or f == 0.0:
            sexuees.append(v)
            continue
        cas = elargi(v.cas)
        sexuees.append(v.fois(1.0 - f, cas=replace(cas, code=f"{cas.code}~h")))
        sexuees.append(v.fois(f, cas=replace(
            cas, code=f"{cas.code}~f", sexe="F",
            nombre_enfants=max(cas.nombre_enfants, ENFANTS))))
    return sexuees


def parts_tranches_de_tous(variantes: list[Variante], effectifs,
                           source: CaracteristiquesRetraites,
                           sexe: str) -> dict[str, float]:
    """Les parts des tranches de durée, hors des régimes statutaires, qui
    redonnent à TOUS les retraités du sexe celles de l'EIR : les régimes
    statutaires n'ayant pas de carrières courtes, les autres en portent
    d'autant plus. Sous :data:`STATUTAIRES_A_LEUR_DUREE`, chaque carrière
    statutaire compte dans la tranche de sa durée, et les autres groupes
    complètent chaque tranche ; sinon, elles comptent toutes dans la plus
    longue."""
    poids = poids_retraites(variantes, effectifs, source.millesime)
    siens = [(v, p) for v, p in zip(variantes, poids) if v.cas.sexe == sexe]
    total = somme_ordonnee(p for _, p in siens)
    hors = somme_ordonnee(p for v, p in siens if v.groupe not in GROUPES_INTERROMPUS)
    if STATUTAIRES_A_LEUR_DUREE:
        statutaires = {nom: 0.0 for nom, _ in TRANCHES}
        for v, p in siens:
            if v.groupe not in GROUPES_INTERROMPUS:
                statutaires[tranche_de_duree(duree_de(v))] += p
        publiees = parts_tranches(source, sexe)
        restes = {nom: max(0.0, publiees[nom] * total - statutaires[nom])
                  for nom, _ in TRANCHES}
        somme = somme_ordonnee(restes.values())
        return {nom: reste / somme for nom, reste in restes.items()}
    facteur = total / (total - hors)
    courtes = {nom: part * facteur for nom, part in parts_tranches(source, sexe).items()
               if nom != "40_plus"}
    return {"40_plus": 1.0 - somme_ordonnee(courtes.values()), **courtes}


def interruptions(variantes: list[Variante], effectifs,
                  source: CaracteristiquesRetraites,
                  de_tous: bool = False, etalees: bool = False,
                  propres: dict[str, float] | None = None) -> list[Variante]:
    """Les femmes, les cas types de ``propres`` à leur part (:func:`femmes`),
    puis, hors des régimes statutaires, les carrières courtes et les périodes
    assimilées, sexe par sexe : aux parts de l'EIR, ou, sous ``de_tous``, à
    celles qui les redonnent à tous les retraités
    (:func:`parts_tranches_de_tous`) ; leurs années validées sont les
    premières, ou, sous ``etalees``, étalées sur la vie active."""
    sexuees = femmes(variantes, effectifs, source, propres)
    parts = {sexe: (parts_tranches_de_tous(sexuees, effectifs, source, sexe) if de_tous
                    else parts_tranches(source, sexe))
             for sexe in ("F", "H")}
    sortie = []
    for v in sexuees:
        if v.groupe not in GROUPES_INTERROMPUS:
            sortie.append(v)
            continue
        tranches = parts[v.cas.sexe]
        assimilee = part_assimilee(source, v.cas.sexe)
        restes = 0.0
        declinees = []
        for nom, cible in TRANCHES:
            declinee = _interrompre(v, nom, cible, tranches[nom], assimilee, etalees)
            if declinee is None:
                restes += tranches[nom]
            else:
                declinees.append(declinee)
        # Une tranche plus longue que la carrière du cas type lui revient telle
        # quelle : la première, la carrière entière, en reçoit la part.
        if restes:
            declinees[0] = declinees[0].fois((tranches["40_plus"] + restes)
                                             / tranches["40_plus"])
        sortie.extend(declinees)
    return sortie


def salaires(variantes: list[Variante], points) -> list[Variante]:
    """Chaque variante aux sept centiles du salaire, sa moyenne gardée."""
    sortie = []
    for v in variantes:
        cas = elargi(v.cas)
        for nom, part, facteur in points:
            sortie.append(v.fois(part, salaire=v.salaire * facteur, cas=replace(
                cas, code=f"{cas.code}~{nom}",
                niveau_salaire=cas.niveau_salaire * facteur)))
    return sortie


def reference_population() -> list[Variante]:
    """La grille du dépôt, son salariat privé réduit au gabarit : les quatre cas
    types de la Cnav lui cèdent chacun sa part de la caisse ; le contractuel
    aussi sous :data:`CONTRACTUELS_AU_SALARIAT`."""
    retires = SALARIAT_PRIVE + (("contractuel_public",) if CONTRACTUELS_AU_SALARIAT else ())
    variantes = [v for v in reference() if v.cas.code not in retires]
    moyen = next(cas for cas in CAS_TYPES if cas.code == "salaire_moyen")
    gabarit = elargi(moyen, code=GABARIT, libelle="Salarié du privé")
    parts = (("cnav", 1.0),)
    return [*variantes, Variante(cas=gabarit, groupe=groupe_de(GABARIT),
                                 retraites=parts, cotisants=parts)]


def salaires_population(variantes: list[Variante],
                        donnees: DonneesPopulation) -> list[Variante]:
    """Chaque variante aux sept centiles du salaire de SON sexe.

    Le salariat privé y prend son niveau génération par génération, cadre aux
    trois centiles du haut, au Smic au moins sous :data:`PLANCHER_SMIC`, et,
    pour la part des carrières que son sexe passe à temps partiel, la quotité
    de sa génération de 25 à 49 ans. Sous :data:`PERSISTANCE_SMIC`, une part
    de sa classe du bas est payée le Smic toute la carrière, et le reste de la
    classe en garde la moyenne ; sous :data:`VOLUME_DE_TRAVAIL`, chaque année
    d'activité est payée à la part de l'année travaillée à son âge, selon son
    rang aussi sous :data:`VOLUME_SELON_LE_RANG`. Les autres groupes gardent
    la dispersion de la grille élargie autour de leur niveau, celle de leur
    sexe, resserrée en carrière, et des années entières ; les indépendants,
    celle des revenus des non-salariés de leur sexe sous
    :data:`INDEPENDANTS_A_LEUR_DISPERSION`. Sous
    :data:`RANG_SELON_LA_DUREE`, chaque tranche de durée prend les classes de
    centiles dans la proportion que l'EIR lui mesure
    (:func:`rangs_selon_la_duree`), et la part de sa classe du bas payée le
    Smic toute la carrière la suit ; sous :data:`SOUS_CLASSES_DU_BAS`, le
    reste de la classe du bas se décline en sous-classes de rang
    (:func:`sous_classes_du_bas`) ; sous :data:`EMPLOI_FRAGMENTE`, les classes
    du bas en carrières fragmentées et entières (:func:`fragmentees`).
    """
    rangs = (rangs_selon_la_duree(donnees.quintiles, parts_des_tranches(variantes))
             if RANG_SELON_LA_DUREE else {})
    sortie = []
    for v in variantes:
        cas = elargi(v.cas)
        selon = rangs.get(cas.sexe, {}).get(v.tranche, {})
        if cas.code.split("~", 1)[0] != GABARIT:
            points = (donnees.independants[cas.sexe]
                      if INDEPENDANTS_A_LEUR_DISPERSION
                      and cas.code.split("~", 1)[0] in INDEPENDANTS
                      else donnees.points[cas.sexe])
            for nom, part, facteur in points:
                sortie.append(v.fois(selon.get(nom, part), salaire=v.salaire * facteur,
                                     cas=replace(cas, code=f"{cas.code}~{nom}",
                                                 niveau_salaire=cas.niveau_salaire * facteur)))
            continue
        partiel = donnees.parts_partiel[cas.sexe]
        for nom, base in CENTILES:
            part = selon.get(nom, base)
            relatif = donnees.rangs[nom] if VOLUME_SELON_LE_RANG else 1.0
            volumes = (tuple((age, min(1.0, annee * relatif))
                             for age, annee in donnees.volumes)
                       if VOLUME_DE_TRAVAIL else ())
            rang = replace(cas, code=f"{cas.code}~{nom}",
                           affiliation=("salarie_prive_cadre" if nom in CENTILES_CADRES
                                        else "salarie_prive_non_cadre"),
                           niveaux=donnees.niveaux[(cas.sexe, nom)],
                           plancher_smic=PLANCHER_SMIC, volumes=volumes,
                           entrees=(donnees.entrees[cas.sexe]
                                    if ENTREE_SELON_LA_GENERATION and v.tranche == "40_plus"
                                    else ()))
            classes = [(rang, part)]
            if nom == CENTILES[0][0] and (PERSISTANCE_SMIC or SOUS_CLASSES_DU_BAS > 1):
                persistants = (donnees.persistants[cas.sexe] * part / base
                               if PERSISTANCE_SMIC else 0.0)
                reste = (donnees.reste_du_bas[cas.sexe] if PERSISTANCE_SMIC
                         else donnees.niveaux[(cas.sexe, nom)])
                classes = sous_classes_du_bas(rang, reste, donnees.ecarts_du_bas[cas.sexe],
                                              part - persistants)
                if PERSISTANCE_SMIC:
                    classes.append((replace(rang, code=f"{rang.code}~smic",
                                            niveaux=donnees.smic, persistante=True),
                                    persistants))
            if EMPLOI_FRAGMENTE and VOLUME_DE_TRAVAIL and VOLUME_SELON_LE_RANG:
                classes = fragmentees(classes, relatif, donnees.fragmente, donnees.volumes)
            for classe, poids in classes:
                sortie.append(v.fois(poids * (1.0 - partiel), cas=classe))
                sortie.append(v.fois(poids * partiel, cas=replace(
                    classe, code=f"{classe.code}~partiel", ages_partiel=ages_du_partiel(),
                    quotites=donnees.quotites[cas.sexe])))
    return sortie


def ages_du_partiel() -> tuple[float, float]:
    """Les âges du temps partiel d'une carrière à temps partiel : de 25 à 49
    ans (:data:`AGES_PARTIEL`), ou de 25 ans à son départ
    (:data:`PARTIEL_JUSQU_AU_DEPART`)."""
    debut, fin = AGES_PARTIEL
    return (debut, float(AGE_FIN_INACTIVITE + 1)) if PARTIEL_JUSQU_AU_DEPART else (debut, fin)


def sous_classes_du_bas(rang: CasTypeLarge, reste: tuple[tuple[int, float], ...],
                        ecarts: tuple[tuple[int, tuple[float, ...]], ...],
                        poids: float) -> list[tuple[CasTypeLarge, float]]:
    """Le reste de la classe du bas, de ce ``poids``, au niveau ``reste`` : en
    une classe, ou décliné en sous-classes de poids égal (:data:`SOUS_CLASSES_DU_BAS`),
    chacune à son écart génération par génération (:func:`ecarts_du_bas`)."""
    if SOUS_CLASSES_DU_BAS <= 1:
        return [(replace(rang, niveaux=reste), poids)]
    par_generation = dict(ecarts)
    return [(replace(rang, code=f"{rang.code}~bas{k + 1}",
                     niveaux=tuple((g, niveau * par_generation[g][k]) for g, niveau in reste)),
             poids / SOUS_CLASSES_DU_BAS)
            for k in range(SOUS_CLASSES_DU_BAS)]


def population(effectifs, source: CaracteristiquesRetraites,
               racine: Path) -> list[Variante]:
    """La population : la grille « ensemble », son salariat privé tiré des
    distributions de chaque sexe plutôt que de quatre cas types étalés sur
    celle des deux sexes réunis, et ses carrières courtes étalées sur la vie
    active sous :data:`COURTES_ETALEES`."""
    retirer = () if CONTRACTUELS_AU_SALARIAT else CAISSES_DANS_LA_CNAV
    propres = femmes_des_independants(racine) if INDEPENDANTS_A_LEUR_PART_DE_FEMMES else None
    variantes = interruptions(melees(personnes(reference_population(), effectifs, source,
                                               retirer), source), effectifs, source,
                              de_tous=COURTES_A_LA_PART_DE_TOUS, etalees=COURTES_ETALEES,
                              propres=propres)
    if DUREE_DES_FEMMES_SELON_LA_GENERATION:
        variantes = femmes_selon_la_generation(variantes, effectifs, source, racine)
    donnees = donnees_population(racine)
    if DEPARTS_AVEC_DECOTE:
        variantes = departs_avec_decote(variantes, effectifs, source, donnees.quintiles)
    return salaires_population(variantes, donnees)


def parts_avec_decote(variantes: list[Variante], effectifs,
                      source: CaracteristiquesRetraites,
                      quintiles: dict) -> dict[str, float]:
    """La part des carrières incomplètes de chaque sexe qui part avec une
    décote (:data:`DEPARTS_AVEC_DECOTE`) : celle des départs avec décote que
    l'EIR mesure à tous les retraités du sexe, divisée par le poids des
    carrières incomplètes parmi eux, l'année de l'enquête ; un au plus."""
    poids = poids_retraites(variantes, effectifs, source.millesime)
    sortie = {}
    for sexe in ("F", "H"):
        tous = somme_ordonnee(p for v, p in zip(variantes, poids) if v.cas.sexe == sexe)
        incompletes = somme_ordonnee(p for v, p in zip(variantes, poids)
                                     if v.cas.sexe == sexe and incomplete(v))
        cible = quintiles[("ensemble", "part_decote", sexe)] / 100.0
        sortie[sexe] = min(1.0, cible * tous / incompletes) if incompletes else 0.0
    return sortie


def departs_avec_decote(variantes: list[Variante], effectifs,
                        source: CaracteristiquesRetraites,
                        quintiles: dict) -> list[Variante]:
    """Chaque carrière incomplète en deux : la part de son sexe
    (:func:`parts_avec_decote`) part à l'ouverture du droit, avec une décote,
    le reste au taux plein ; les autres variantes telles quelles."""
    parts = parts_avec_decote(variantes, effectifs, source, quintiles)
    sortie = []
    for v in variantes:
        part = parts[v.cas.sexe]
        if not incomplete(v) or v.cas.regle_liquidation != "taux_plein" or not part:
            sortie.append(v)
            continue
        sortie.append(v.fois(1.0 - part))
        sortie.append(v.fois(part, decote=True, cas=replace(
            v.cas, code=f"{v.cas.code}~decote", regle_liquidation="ouverture")))
    return sortie


def non_residents(racine: Path) -> dict[str, tuple[float, dict[str, float], float]]:
    """Les retraités qui résident à l'étranger, sexe par sexe, tels que l'EIR
    les donne par différence entre tous les retraités (``quintiles_eqcc.csv``)
    et ceux qui résident en France (``quintiles_eqcc_residents.csv``) : leur
    part parmi les retraités du sexe, celle de chaque tranche de durée validée
    hors majorations parmi eux, ramenées à un, et la part d'entre eux au
    minimum de pension de leur régime principal, en pour cent. En 2020, 3,3 %
    des femmes et 7,9 % des hommes ; 28 % de ces femmes et 22 % de ces hommes
    ont moins de dix années validées, et 62 et 43 % sont au minimum. La
    population ne compte que des résidents ; l'EACR, qui compte tous les
    liquidants, et la dépense de la page, qui paie aussi les pensions servies
    à l'étranger, les comptent."""
    tous, residents = quintiles_eqcc(racine), quintiles_eqcc(racine, residents=True)
    sortie = {}
    for sexe in ("F", "H"):
        def effectif(source: dict, indicateur: str) -> float:
            return (source[("ensemble", "effectifs", sexe)]
                    * source[("ensemble", indicateur, sexe)] / 100.0)

        ailleurs = (tous[("ensemble", "effectifs", sexe)]
                    - residents[("ensemble", "effectifs", sexe)])
        tranches = {nom: max(0.0, effectif(tous, f"part_duree_validee_hors_majoration_{nom}")
                             - effectif(residents,
                                        f"part_duree_validee_hors_majoration_{nom}"))
                    for nom, _ in TRANCHES}
        total = somme_ordonnee(tranches.values())
        minimum = (effectif(tous, "part_minimum_pension_regime_principal")
                   - effectif(residents, "part_minimum_pension_regime_principal"))
        sortie[sexe] = (ailleurs / tous[("ensemble", "effectifs", sexe)],
                        {nom: masse / total for nom, masse in tranches.items()},
                        100.0 * minimum / ailleurs)
    return sortie


def poids_des_non_residents(variantes: list[Variante], poids: list[float],
                            racine: Path) -> list[float]:
    """Les poids qui font de la population celle des retraités de l'étranger
    (:func:`non_residents`) : chaque variante garde sa place dans sa tranche de
    durée et son sexe, et chaque tranche prend la part que l'EIR donne aux
    non-résidents du sexe ; une carrière hors des tranches, celle du cas type,
    compte parmi les quarante ans et plus. Le total de chaque sexe ne bouge
    pas. Une convention : à durée égale, un retraité de l'étranger a la
    carrière d'un résident — le régime, le salaire, la décote."""
    parts = non_residents(racine)

    def tranche(v: Variante) -> str:
        return v.tranche or TRANCHES[0][0]

    masses: dict[tuple[str, str], float] = {}
    sexes: dict[str, float] = {}
    for v, p in zip(variantes, poids):
        cle = (v.cas.sexe, tranche(v))
        masses[cle] = masses.get(cle, 0.0) + p
        sexes[v.cas.sexe] = sexes.get(v.cas.sexe, 0.0) + p
    return [p * sexes[v.cas.sexe] * parts[v.cas.sexe][1][tranche(v)]
            / masses[(v.cas.sexe, tranche(v))]
            if masses[(v.cas.sexe, tranche(v))] else 0.0
            for v, p in zip(variantes, poids)]


def parts_agricoles(racine: Path) -> dict[str, tuple[dict[str, float], float, float]]:
    """La part des salariés agricoles parmi les retraités du régime général et
    de la MSA salariés, sexe par sexe, telle que l'EIR de 2020 la donne à leur
    régime principal, monopensionnés et polypensionnés de deux régimes
    (:data:`SALARIES_AGRICOLES`) : celle de chaque classe de centiles parmi les
    résidents, celle de tous les résidents, et celle des retraités de
    l'étranger, par différence entre tous les retraités (``caracteristiques_retraites.csv``)
    et les résidents (``quintiles_eqcc_residents.csv``).

    Chaque quintile de la pension en équivalent carrière complète est une bande
    de rangs du sexe, de la largeur de sa part des résidents du sexe ; une classe
    de centiles prend la part des bandes que ses rangs couvrent. Les parts des
    classes, pesées comme :data:`CENTILES`, redonnent celle de tous les
    résidents. En 2020, 4,5 % des hommes résidents du groupe et 2,2 % des
    femmes, 6 à 7 % des deux premiers quintiles d'hommes ; 12,6 % des hommes
    de l'étranger. Une convention : le rang de la pension par année validée
    est tenu pour celui du salaire."""
    residents = quintiles_eqcc(racine, residents=True)
    tous = quintiles_eqcc(racine)
    source = eir(racine)
    sortie = {}
    for sexe in ("F", "H"):
        def masses(lire, quintile: str) -> tuple[float, float]:
            agricoles = somme_ordonnee(lire(f"part_{statut}_msa_salaries", quintile)
                                       for statut in ("mono", "poly"))
            generaux = somme_ordonnee(lire(f"part_{statut}_regime_general", quintile)
                                      for statut in ("mono", "poly"))
            return agricoles, agricoles + generaux

        def du_resident(indicateur: str, quintile: str) -> float:
            return residents[(quintile, indicateur, sexe)]

        effectifs = [residents[(q, "effectifs", sexe)] for q in QUINTILES_EQCC]
        total = somme_ordonnee(effectifs)
        parts_q = []
        for q in QUINTILES_EQCC:
            agricoles, groupe = masses(du_resident, q)
            parts_q.append(agricoles / groupe)
        bandes, debut = [], 0.0
        for effectif in effectifs:
            bandes.append((debut, debut + effectif / total))
            debut += effectif / total
        par_classe, debut = {}, 0.0
        for nom, largeur in CENTILES:
            fin = debut + largeur
            par_classe[nom] = somme_ordonnee(
                part * max(0.0, min(fin, haut) - max(debut, bas))
                for part, (bas, haut) in zip(parts_q, bandes)) / largeur
            debut = fin
        agricoles_r, groupe_r = masses(du_resident, "ensemble")
        cible = agricoles_r / groupe_r
        moyenne = somme_ordonnee(par_classe[nom] * largeur for nom, largeur in CENTILES)
        par_classe = {nom: part * cible / moyenne for nom, part in par_classe.items()}
        n_tous = tous[("ensemble", "effectifs", sexe)]
        n_residents = residents[("ensemble", "effectifs", sexe)]
        agricoles_t, groupe_t = masses(lambda indicateur, _: source.valeur(indicateur, sexe),
                                       "ensemble")
        ailleurs = ((agricoles_t * n_tous - agricoles_r * n_residents)
                    / (groupe_t * n_tous - groupe_r * n_residents))
        sortie[sexe] = (par_classe, cible, ailleurs)
    return sortie


def classe_de(v: Variante) -> str | None:
    """La classe de centiles d'une carrière du salariat privé de la population,
    lue dans son code ; ``None`` pour les autres."""
    morceaux = v.cas.code.split("~")
    if morceaux[0] != GABARIT:
        return None
    noms = {nom for nom, _ in CENTILES}
    return next((m for m in morceaux if m in noms), None)


def fractions_agricoles(variantes: list[Variante], racine: Path
                        ) -> tuple[list[float], list[float]]:
    """La part de chaque carrière qui est celle d'un salarié agricole
    (:data:`SALARIES_AGRICOLES`, :func:`parts_agricoles`) : parmi les
    résidents, celle de sa classe de centiles, et parmi les retraités de
    l'étranger, celle de son sexe ; zéro hors du salariat privé."""
    parts = parts_agricoles(racine)
    residents, ailleurs = [], []
    for v in variantes:
        classe = classe_de(v)
        par_classe, _, etranger = parts[v.cas.sexe]
        residents.append(par_classe[classe] if classe else 0.0)
        ailleurs.append(etranger if classe else 0.0)
    return residents, ailleurs


def femmes_ponderees(variantes: list[Variante], effectifs,
                     source: CaracteristiquesRetraites) -> list[tuple[Variante, float]]:
    """Les variantes de femmes et leur poids de retraitées, l'année de l'enquête."""
    poids = poids_retraites(variantes, effectifs, source.millesime)
    return [(v, p) for v, p in zip(variantes, poids) if v.cas.sexe == "F" and p > 0.0]


def incomplete(v: Variante) -> bool:
    """Vrai pour une carrière incomplète hors des régimes statutaires, que
    :data:`DUREE_DES_FEMMES_SELON_LA_GENERATION` allonge ou raccourcit."""
    return v.groupe in GROUPES_INTERROMPUS and v.tranche not in (None, "40_plus")


def annees_incompletes(v: Variante, ecart: float, legal: float) -> float:
    """Les années validées d'une carrière incomplète, ``ecart`` gagné ou perdu :
    une au moins, et pas au-delà de l'âge légal de sa génération."""
    return min(max(1.0, v.duree + ecart), legal - v.cas.age_debut)


def duree_moyenne_des_femmes(femmes: list[tuple[Variante, float]], ecart: float,
                             legal: float, entree: float) -> float:
    """La durée validée moyenne des femmes d'une génération, en années, comme
    :func:`ecarts_des_femmes` la compte : une carrière incomplète à ses années
    (:func:`annees_incompletes`), une carrière pleine de l'entrée à l'âge légal
    — à ``entree`` pour le salariat privé —, les deux avec les majorations de
    durée de ses enfants, huit trimestres chacun ; une carrière statutaire à sa
    durée."""
    majoration = 2.0 * ENFANTS
    somme = total = 0.0
    for v, p in femmes:
        if incomplete(v):
            annees = annees_incompletes(v, ecart, legal) + majoration
        elif v.groupe in GROUPES_INTERROMPUS:
            debut = entree if v.cas.code.split("~", 1)[0] == GABARIT else v.cas.age_debut
            annees = legal - debut + majoration
        else:
            annees = duree_de(v)
        somme += p * annees
        total += p
    return somme / total


def ecarts_des_femmes(variantes: list[Variante], effectifs,
                      source: CaracteristiquesRetraites, racine: Path) -> dict[int, float]:
    """Les années que les carrières incomplètes des femmes gagnent ou perdent,
    génération par génération (:data:`DUREE_DES_FEMMES_SELON_LA_GENERATION`) :
    celles qui portent leur durée moyenne (:func:`duree_moyenne_des_femmes`) à
    celle de l'EIR (:func:`durees_d_assurance`), par bissection."""
    from retraite_notionnelle.scenarios.actuel import AgesOuverture

    legaux = AgesOuverture(racine)
    publiees = durees_d_assurance(racine)
    serie = tuple(sorted((g, d) for (g, sexe), d in publiees.items() if sexe == "F"))
    entrees = entrees_des_carrieres_pleines(racine)["F"]
    femmes = femmes_ponderees(variantes, effectifs, source)
    sortie = {}
    for generation in range(serie[0][0] - 40, serie[-1][0] + 1):
        lu = legaux.age(generation)
        legal = lu[0] if lu is not None else 60.0
        entree = _par_generation(entrees, generation, 21.0)
        cible = _par_generation(serie, generation, 0.0)
        bas, haut = -40.0, 40.0
        for _ in range(50):
            milieu = (bas + haut) / 2.0
            if duree_moyenne_des_femmes(femmes, milieu, legal, entree) < cible:
                bas = milieu
            else:
                haut = milieu
        sortie[generation] = (bas + haut) / 2.0
    return sortie


def femmes_selon_la_generation(variantes: list[Variante], effectifs,
                               source: CaracteristiquesRetraites,
                               racine: Path) -> list[Variante]:
    """Les carrières incomplètes des femmes, chacune à ses années validées de
    chaque génération (:func:`ecarts_des_femmes`, :func:`annees_incompletes`),
    à l'année près ; les autres variantes telles quelles."""
    from retraite_notionnelle.scenarios.actuel import AgesOuverture

    legaux = AgesOuverture(racine)
    ecarts = ecarts_des_femmes(variantes, effectifs, source, racine)
    sortie = []
    for v in variantes:
        if v.cas.sexe != "F" or not incomplete(v):
            sortie.append(v)
            continue
        cibles = []
        for generation, ecart in sorted(ecarts.items()):
            lu = legaux.age(generation)
            legal = lu[0] if lu is not None else 60.0
            cibles.append((generation, float(round(annees_incompletes(v, ecart, legal)))))
        sortie.append(replace(v, cas=replace(v.cas, cibles=tuple(cibles))))
    return sortie


def grille(nom: str, effectifs, source: CaracteristiquesRetraites,
           points, racine: Path | None = None) -> list[Variante]:
    """Les variantes d'une des grilles de ``GRILLES`` ; la population lit ses
    distributions sous ``racine``, les données du dépôt par défaut."""
    if nom == "population":
        return population(effectifs, source, racine if racine is not None
                          else RACINE / "data")
    base = reference()
    if nom == "reference":
        return base
    if nom == "personnes":
        return personnes(base, effectifs, source)
    if nom == "melees":
        return melees(personnes(base, effectifs, source), source)
    if nom == "femmes":
        return femmes(base, effectifs, source)
    if nom == "interruptions":
        return interruptions(base, effectifs, source)
    if nom == "salaires":
        return salaires(base, points)
    if nom == "ensemble":
        return salaires(interruptions(melees(personnes(base, effectifs, source), source),
                                      effectifs, source), points)
    raise ValueError(f"grille inconnue : {nom!r} (attendu : {GRILLES})")


# -- le calcul -------------------------------------------------------------------

def pseudo(variantes: list[Variante]) -> tuple[tuple[CasType, ...], dict, dict]:
    """Les cas types de la grille, chacun réclamant sa pseudo-caisse, et les
    parts de chaque pseudo-caisse."""
    cas_types, retraites, cotisants = [], {}, {}
    for v in variantes:
        caisse = f"@{v.cas.code}"
        cas_types.append(replace(v.cas, caisses=(caisse,)))
        retraites[caisse] = v.retraites
        cotisants[caisse] = v.cotisants
    return tuple(cas_types), retraites, cotisants


def _simuler_morceau(parametres: Parametres, morceau: tuple[CasType, ...]):
    """La grille simulée d'un morceau, gardée comme celle de la page."""
    return memoire.memoriser_pour(
        parametres, ("grille_du_cout", parametres, morceau, "droit"),
        lambda: C._pensionnes(Simulateur(parametres), morceau, "droit"))


def simuler(parametres: Parametres, cas_types: tuple[CasType, ...], processus: int):
    """Ce que ``cout._pensionnes`` rend pour la grille, par morceaux, chacun
    gardé, et sur ``processus`` cœurs quand il y en a plusieurs."""
    taille = max(1, math.ceil(len(cas_types) / max(1, 2 * processus)))
    morceaux = [cas_types[i:i + taille] for i in range(0, len(cas_types), taille)]
    if processus <= 1 or len(morceaux) == 1:
        resultats = [_simuler_morceau(parametres, morceau) for morceau in morceaux]
    else:
        with ProcessPoolExecutor(max_workers=processus,
                                 mp_context=multiprocessing.get_context("spawn")) as pool:
            resultats = list(pool.map(_simuler_morceau, [parametres] * len(morceaux),
                                      morceaux))
    pensionnes, motifs = [], {}
    for liste, echecs in resultats:
        pensionnes.extend(liste)
        for motif, nombre in echecs.items():
            motifs[motif] = motifs.get(motif, 0) + nombre
    return pensionnes, motifs


def calculer(parametres: Parametres, variantes: list[Variante], processus: int = 1):
    """La page Coût sur cette grille : ``cout.calculer_cout`` tel quel, la grille
    simulée et les effectifs remplacés par ceux des pseudo-caisses."""
    racine = parametres.racine_donnees
    cas_types, retraites, cotisants = pseudo(variantes)
    simulee = simuler(parametres, cas_types, processus)
    simulateur = Simulateur(parametres)
    simulateur.effectifs = EffectifsRepartis(simulateur.effectifs, retraites)
    simulateur.cotisants = EffectifsRepartis(simulateur.cotisants, cotisants)
    variante = variante_du_scenario(parametres.scenario_projection,
                                    racine / "reference" / "macro")
    return C.calculer_cout(
        simulateur, DepensesRetraite(racine), Population(racine),
        ComptesRetraite(racine, variante=variante), cas_types=cas_types,
        assiette=AssietteActivite(racine), grille_simulee=simulee)


def indicateurs(cout) -> dict:
    """Ce que la page Coût affiche, système par système."""
    solde, avenir = cout.solde, cout.avenir
    horizon = avenir.annee(avenir.derniere_annee)
    sortie = {"echecs": somme_ordonnee(cout.echecs.values()), "annee_horizon": avenir.derniere_annee}
    for scenario, _ in C.SCENARIOS:
        sortie[scenario] = {
            "ecart_passe": (cout.cumul(scenario) / cout.cumul("actuel") - 1) * 100,
            "part_pib_horizon": horizon.part_pib(scenario) * 100,
            "solde_moyen": solde.solde_moyen(scenario, solde.premiere_annee_projetee,
                                             solde.derniere_annee) * 100,
            "coefficient_horizon": solde.annee(solde.derniere_annee).coefficient(scenario),
        }
    sortie["garantie_horizon"] = horizon.part_pib(C.COMPOSANTE_GARANTIE) * 100
    # Le passé refait par la projection (action 147) : l'écart, en %, de la base
    # que l'ancrage prête au modèle à la dépense observée, et le pire depuis 2000.
    passe = avenir.reconstitution()
    sortie["reconstitution"] = {annee: (rapport - 1) * 100 for annee, rapport in passe.items()}
    depuis = [abs(rapport - 1) * 100 for annee, rapport in passe.items() if annee >= 2000]
    sortie["reconstitution_pire_depuis_2000"] = max(depuis) if depuis else None
    return sortie


def composition(variantes: list[Variante], effectifs, source: CaracteristiquesRetraites,
                ) -> dict:
    """Ce que la grille dit des retraités de l'année de l'enquête, à mettre en
    regard de ce que l'EIR en publie."""
    annee = source.millesime
    poids = poids_retraites(variantes, effectifs, annee)
    total = somme_ordonnee(poids)
    femmes = somme_ordonnee(p for v, p in zip(variantes, poids) if v.cas.sexe == "F") / total
    poly = somme_ordonnee(p for v, p in zip(variantes, poids) if v.poly) / total
    duree = {}
    courtes = {}
    for sexe in ("F", "H"):
        lot = [(v, p) for v, p in zip(variantes, poids) if v.cas.sexe == sexe]
        masse = somme_ordonnee(p for _, p in lot)
        if not masse:
            continue
        duree[sexe] = somme_ordonnee(p * (v.duree if v.duree is not None
                               else v.cas.age_liquidation - v.cas.age_debut)
                          for v, p in lot) / masse
        courtes[sexe] = somme_ordonnee(p for v, p in lot if duree_de(v) < 30) / masse
    groupes = {}
    for v, p in zip(variantes, poids):
        groupes[v.groupe] = groupes.get(v.groupe, 0.0) + p / total
    return {"femmes": femmes, "polypensionnes": poly, "duree_validee": duree,
            "moins_de_30_ans": courtes, "groupes": groupes}


def composition_eir(source: CaracteristiquesRetraites) -> dict:
    femmes = source.valeur("effectifs", "F") / source.valeur("effectifs", "ensemble")
    poly = (source.valeur("part_poly_2_regimes", "ensemble")
            + source.valeur("part_poly_3_regimes", "ensemble")) / 100
    duree = {s: source.valeur("duree_validee_hors_majoration", s) for s in ("F", "H")}
    courtes = {s: somme_ordonnee(parts_tranches(source, s)[t]
                                 for t in ("moins_10", "10_20", "20_30")) for s in ("F", "H")}
    return {"femmes": femmes, "polypensionnes": poly, "duree_validee": duree,
            "moins_de_30_ans": courtes, "groupes": parts_personnes(source)}


# -- la distribution de l'année de l'enquête (action 138, étape 14) -------------

#: Les trois lectures de la distribution : tous les retraités, puis les femmes et
#: les hommes, comme l'EIR les publie.
SEXES = ("ensemble", "F", "H")
INTITULES_SEXES = {"ensemble": "Ensemble", "F": "Femmes", "H": "Hommes"}


def pensions_de_l_annee(pensionnes: list, cas_types: tuple[CasType, ...],
                        poids: dict[str, float], population: Population,
                        revalorisation: RevalorisationServie, macro: DonneesMacro,
                        annee_euros: int, annee: int) -> list[tuple[float, float, str]]:
    """Ce que la grille sert l'année ``annee``, en TÊTES : une ligne par cohorte
    liquidée, (pension mensuelle de droit direct du scénario 1 en euros de
    l'année, poids, sexe).

    Les têtes sont celles de la page (``cout._masses``) : chaque génération de
    la grille en représente cinq, chacune pesée par son effectif INSEE de
    l'année et comptée dès sa liquidation, chaque cas type par son poids de la
    page. La pension est celle de la liquidation, revalorisée comme la page la
    revalorise — le droit jusqu'au dernier barème, puis les prix, et la valeur
    de service de l'Agirc-Arrco pour sa part (``coefficient_servi``) —, ramenée des euros constants à ceux de
    l'année. Sans la complétude des cohortes (``Pensionne.completude``) : elle
    allège la MASSE d'une cohorte d'une moyenne, que la distribution ne sait
    pas répartir entre ses membres ; chaque ligne décrit une carrière.
    """
    sexes = {cas.code: cas.sexe for cas in cas_types}
    return [(montant, poids_tete, sexes[pensionne.code])
            for pensionne, montant, poids_tete in cohortes_de_l_annee(
                pensionnes, poids, population, revalorisation, macro, annee_euros, annee)]


def cohortes_de_l_annee(pensionnes: list, poids: dict[str, float], population: Population,
                        revalorisation: RevalorisationServie, macro: DonneesMacro,
                        annee_euros: int, annee: int):
    """Les cohortes de :func:`pensions_de_l_annee`, chacune avec son couple :
    ``(couple, pension mensuelle, poids en têtes)``."""
    vers_l_annee = macro.coefficient_prix(annee_euros, annee) / 12.0
    for pensionne in pensionnes:
        part = poids.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
        for decalage in range(-C._DEMI_TRANCHE, C._DEMI_TRANCHE + 1):
            liquidation = pensionne.annee_liquidation + decalage
            if annee < liquidation:
                continue
            effectif = population.effectif(annee - pensionne.generation - decalage, annee)
            if effectif <= 0.0:
                continue
            montant = pensionne.pensions["actuel"] * vers_l_annee * C.coefficient_servi(
                pensionne.parts_regimes, revalorisation, liquidation, annee)
            yield pensionne, montant, part * effectif


def quantile_pondere(lot: list[tuple[float, float]], rang: float) -> float:
    """Le plus petit montant sous lequel tombe au moins ``rang`` du poids. Une
    grille est faite d'atomes, une carrière et son montant : le quantile en est
    un."""
    tries = sorted(lot)
    total = somme_ordonnee(poids for _, poids in tries)
    cumul = 0.0
    for montant, poids in tries:
        cumul += poids
        if cumul >= rang * total:
            return montant
    return tries[-1][0]


def part_sous(lot: list[tuple[float, float]], montant: float) -> float:
    """La part du poids sous ``montant`` : ``DistributionPensions.part_sous``,
    pour la grille."""
    return (somme_ordonnee(poids for m, poids in lot if m < montant)
            / somme_ordonnee(poids for _, poids in lot))


def confronter(lignes: list[tuple[float, float, str]], residence: ResidenceRetraites,
               distributions: dict[str, DistributionPensions]) -> dict:
    """La distribution de la grille contre celle des résidents en France que
    l'EIR publie, majorations pour enfants comprises, sexe par sexe : la part
    de chacun, la moyenne et chaque quantile publié, chacun contre le sien ; le
    plus grand écart des deux fonctions de répartition aux bornes des tranches
    de cent euros de l'enquête, la distance de Kolmogorov, et la borne où il
    tombe — positif, la grille a trop de retraités sous elle, négatif, trop peu.
    """
    sortie = {}
    total = somme_ordonnee(poids for _, poids, _ in lignes)
    effectifs = residence.valeur("france", "effectifs", "ensemble")
    for sexe in SEXES:
        lot = [(montant, poids) for montant, poids, s in lignes
               if sexe == "ensemble" or s == sexe]
        if not lot:
            continue
        masse = somme_ordonnee(poids for _, poids in lot)
        distribution = distributions[sexe]
        ecarts = [(t.borne_inferieure,
                   part_sous(lot, t.borne_inferieure) - distribution.part_sous(t.borne_inferieure))
                  for t in distribution.tranches[1:]]
        borne, ecart = max(ecarts, key=lambda e: abs(e[1]))
        sortie[sexe] = {
            "part": masse / total,
            "part_eir": residence.valeur("france", "effectifs", sexe) / effectifs,
            "moyenne": somme_ordonnee(montant * poids for montant, poids in lot) / masse,
            "moyenne_eir": residence.valeur("france", "pension_droit_direct_majorations", sexe),
            "quantiles": {code: quantile_pondere(lot, rang) for code, rang in QUANTILES_PUBLIES},
            "quantiles_eir": {code: residence.valeur("france", code, sexe)
                              for code, _ in QUANTILES_PUBLIES},
            "kolmogorov": ecart,
            "borne_kolmogorov": borne,
        }
    return sortie


def pensions_non_salaries(racine: Path) -> dict[tuple[str, str, str], float]:
    """La pension des retraités de 2020 selon leur régime principal, que la
    fiche 1.11 de l'INSEE tire de l'EIR (``pensions_non_salaries.csv``) :
    ``(régime, sexe, indicateur) → valeur``."""
    return {(l["regime_principal"], l["sexe"], l["indicateur"]): float(l["valeur"])
            for l in _lire_macro(racine, "pensions_non_salaries.csv")}


def femmes_des_independants(racine: Path) -> dict[str, float]:
    """La part des femmes parmi les anciens de chaque indépendant
    (:data:`INDEPENDANTS`), au régime principal de l'EIR de 2020
    (:func:`pensions_non_salaries`) : ``{cas type: part}``."""
    publiees = pensions_non_salaries(racine)
    return {code: (publiees[(regime, "F", "effectifs")]
                   / publiees[(regime, "ensemble", "effectifs")])
            for code, regime in INDEPENDANTS.items()}


def confronter_non_salaries(lignes: list[tuple[float, float, str, str]],
                            publiees: dict[tuple[str, str, str], float]) -> dict:
    """La pension des indépendants de la grille contre celle de leurs anciens
    dans l'EIR, régime par régime (:data:`INDEPENDANTS`) et sexe par sexe :
    leur part parmi les retraités du sexe, leur moyenne et leurs quartiles,
    chacun contre le sien ; et chaque quartile rapporté à celui de tous les
    retraités du sexe, la grille contre la fiche, dont les quartiles de tous
    ne sont pas ceux de la DREES. ``lignes`` : ``(pension, poids, sexe, cas
    type)``."""
    sortie: dict[str, dict] = {}
    for code, regime in INDEPENDANTS.items():
        par_sexe = {}
        for sexe in SEXES:
            tous = [(m, p) for m, p, s, _ in lignes if sexe == "ensemble" or s == sexe]
            siens = [(m, p) for m, p, s, c in lignes
                     if c == code and (sexe == "ensemble" or s == sexe)]
            if not siens:
                continue
            masse = somme_ordonnee(p for _, p in siens)
            quantiles = {q: quantile_pondere(siens, rang) for q, rang in QUARTILES}
            de_tous = {q: quantile_pondere(tous, rang) for q, rang in QUARTILES}
            par_sexe[sexe] = {
                "part": masse / somme_ordonnee(p for _, p in tous),
                "part_eir": (publiees[(regime, sexe, "effectifs")]
                             / publiees[("ensemble", sexe, "effectifs")]),
                "moyenne": somme_ordonnee(m * p for m, p in siens) / masse,
                "moyenne_eir": publiees[(regime, sexe, "moyenne")],
                "quantiles": quantiles,
                "quantiles_eir": {q: publiees[(regime, sexe, q)] for q, _ in QUARTILES},
                "relatifs": {q: quantiles[q] / de_tous[q] for q, _ in QUARTILES},
                "relatifs_eir": {q: publiees[(regime, sexe, q)] / publiees[("ensemble", sexe, q)]
                                 for q, _ in QUARTILES},
            }
        if par_sexe:
            sortie[regime] = par_sexe
    return sortie


@dataclass(frozen=True)
class GrilleEnTetes:
    """Ce que la page pèse d'une grille : ses couples simulés, ses cas types, le
    poids de chacun année par année, la pyramide et la revalorisation ; et les
    couples que le modèle a refusé de calculer, par motif."""

    pensionnes: list
    cas_types: tuple[CasType, ...]
    poids: Callable[[int], dict[str, float]]
    population: Population
    revalorisation: RevalorisationServie
    macro: DonneesMacro
    annee_euros: int
    echecs: dict[str, int] = field(default_factory=dict)

    def pensions(self, annee: int) -> list[tuple[float, float, str]]:
        """:func:`pensions_de_l_annee`, pour cette grille."""
        return pensions_de_l_annee(self.pensionnes, self.cas_types, self.poids(annee),
                                   self.population, self.revalorisation, self.macro,
                                   self.annee_euros, annee)

    def cohortes(self, annee: int) -> list:
        """:func:`cohortes_de_l_annee`, pour cette grille."""
        return list(cohortes_de_l_annee(self.pensionnes, self.poids(annee), self.population,
                                        self.revalorisation, self.macro, self.annee_euros,
                                        annee))

    def pensions_par_cas_type(self, annee: int) -> list[tuple[float, float, str, str]]:
        """:meth:`pensions`, chaque ligne avec le cas type dont sa carrière se
        décline : ``(pension, poids, sexe, cas type)``."""
        sexes = {cas.code: cas.sexe for cas in self.cas_types}
        return [(montant, poids, sexes[pensionne.code], pensionne.code.split("~", 1)[0])
                for pensionne, montant, poids in self.cohortes(annee)]


def en_tetes(parametres: Parametres, variantes: list[Variante],
             processus: int = 1) -> GrilleEnTetes:
    """La grille de :func:`calculer`, la même simulation gardée, sous les poids
    que la page lui donne : ceux de ses caisses, recalés sur la dépense des
    groupes du COR (``cout._poids_par_groupe``)."""
    racine = parametres.racine_donnees
    cas_types, retraites, _ = pseudo(variantes)
    pensionnes, echecs = simuler(parametres, cas_types, processus)
    simulateur = Simulateur(parametres)
    simulateur.effectifs = EffectifsRepartis(simulateur.effectifs, retraites)
    population = Population(racine)
    revalorisation = RevalorisationServie(
        simulateur.pour_la_projection(),
        min(p.annee_liquidation for p in pensionnes) - C._DEMI_TRANCHE, C.HORIZON)
    poids = C._poids_par_groupe(
        C._ponderation(simulateur, "effectifs", cas_types), pensionnes, population,
        revalorisation, DecompositionDepense(racine / "reference" / "macro"))
    return GrilleEnTetes(pensionnes, cas_types, poids, population, revalorisation,
                         simulateur.macro, parametres.annee_euros_constants, echecs)


# -- la pension en équivalent carrière complète, contre l'EIR ---------------------

def tranche_de_duree(duree: float) -> str:
    """La tranche de durée validée où tombe ``duree``, en années : celles de
    l'EIR, de moins de dix ans à quarante ans et plus."""
    for borne, nom in ((10, "moins_10"), (20, "10_20"), (30, "20_30"), (40, "30_40")):
        if duree < borne:
            return nom
    return "40_plus"


def duree_de(v: Variante) -> float:
    """La durée validée hors majorations d'une carrière : celle de sa tranche,
    ou celle de son cas type."""
    return v.duree if v.duree is not None else v.cas.age_liquidation - v.cas.age_debut


#: Les minima de pension du scénario 1 que l'EIR compte : le minimum
#: contributif, le minimum garanti des fonctionnaires, la pension majorée de
#: référence des non-salariés agricoles.
MINIMA_DE_PENSION = ("minimum_contributif", "minimum_garanti", "pension_majoree_reference")


def avec_decote(simulateur: Simulateur, cas: CasType, generation: int,
                taux: float) -> bool:
    """Vrai si ce cas type, liquidé au taux ``taux``, part avec une décote :
    sous la règle ``ouverture``, avant l'âge que le pilote fixe sous
    ``taux_plein``, et à un taux plus bas que celui de ce départ-là — ou,
    quand le régime principal compte en points et ne dit pas de taux, avant
    lui seulement. Partir plus tôt n'est pas toujours partir décoté : l'agent
    de conduite né en 1958 part à cinquante ans au taux de 75 %, la décote
    des régimes spéciaux ne mordant qu'aux générations suivantes. Les autres
    règles partent au taux plein, ou à leurs services."""
    if cas.regle_liquidation != "ouverture":
        return False
    plein = replace(cas, regle_liquidation="taux_plein")
    age_plein = plein.age_liquidation_pour(simulateur, generation)
    if cas.age_liquidation_pour(simulateur, generation) >= age_plein - 1e-6:
        return False
    taux_plein = simulateur.echeancier(
        plein.carriere_a(simulateur, generation, age_plein)).au_depart.taux_liquidation
    return taux_plein == 0.0 or taux < taux_plein - 1e-9


def _proratisations(parametres: Parametres, morceau: tuple
                    ) -> list[tuple[str, int, float, bool, float, bool]]:
    """La proratisation de chaque couple du morceau, au scénario 1 de la page :
    sa durée d'assurance tous régimes, enfants compris, rapportée à la durée
    requise de sa génération, bornée à un ; si sa pension porte un minimum
    (:data:`MINIMA_DE_PENSION`) ; cette durée, en années ; et s'il part avec
    une décote (:func:`avec_decote`). Gardée sous l'empreinte du modèle et le
    code de ce script."""

    def calcul():
        simulateur = Simulateur(parametres).pour_la_projection()
        sortie = []
        for cas, generation in morceau:
            try:
                actuel = simulateur.echeancier(cas.construire(simulateur, generation)).au_depart
                decote = avec_decote(simulateur, cas, generation,
                                     actuel.taux_liquidation)
            except (ValueError, KeyError):
                continue
            requis = actuel.trimestres_requis
            minimum = any(avantage.code in MINIMA_DE_PENSION and avantage.montant > 0.0
                          for avantage in actuel.avantages_appliques)
            sortie.append((cas.code, generation,
                           min(1.0, actuel.trimestres_valides / requis) if requis else 1.0,
                           minimum, actuel.trimestres_valides / 4.0, decote))
        return sortie

    return memoire.memoriser_pour(
        parametres, ("proratisation_minimum_duree_et_decote_de_la_grille", parametres,
                     morceau),
        calcul)


def proratisations(parametres: Parametres, couples, processus: int
                   ) -> dict[tuple[str, int], tuple[float, bool, float, bool]]:
    """La proratisation de chaque couple ``(cas type, génération)``, s'il est
    au minimum, sa durée validée et s'il part avec une décote : par morceaux,
    chacun gardé, sur ``processus`` cœurs quand il y en a plusieurs."""
    couples = sorted(couples, key=lambda couple: (couple[0].code, couple[1]))
    taille = max(1, math.ceil(len(couples) / max(1, 2 * processus)))
    morceaux = [tuple(couples[i:i + taille]) for i in range(0, len(couples), taille)]
    if processus <= 1 or len(morceaux) <= 1:
        resultats = [_proratisations(parametres, morceau) for morceau in morceaux]
    else:
        with ProcessPoolExecutor(max_workers=processus,
                                 mp_context=multiprocessing.get_context("spawn")) as pool:
            resultats = list(pool.map(_proratisations, [parametres] * len(morceaux),
                                      morceaux))
    return {(code, generation): (coefficient, minimum, annees, decote)
            for resultat in resultats
            for code, generation, coefficient, minimum, annees, decote in resultat}


def quintiles_ponderes(lignes: list[tuple]) -> dict:
    """Une grille rangée comme l'EIR range les retraités : les bornes des
    quintiles de la pension en équivalent carrière complète, les deux sexes
    réunis, et, sexe par sexe, le poids de chaque tranche de durée dans chaque
    quintile, celui des retraités au minimum, et celui de leur proratisation.
    ``lignes`` : ``(pension, poids, sexe, tranche)``, et en cinquième, s'il y
    est, le minimum, en sixième la proratisation, en septième les années
    validées, en huitième le groupe, en neuvième le départ avec décote. Une
    ligne à cheval sur une borne va au quintile de son milieu."""
    tries = sorted(lignes, key=lambda ligne: ligne[0])
    total = somme_ordonnee(ligne[1] for ligne in tries)
    bornes: list[float] = []
    masses: dict[str, dict[str, list[float]]] = {}
    minima: dict[str, list[float]] = {}
    proratisees: dict[str, list[float]] = {}
    validees: dict[str, list[float]] = {}
    groupes: dict[str, dict[str, list[float]]] = {}
    decotes: dict[str, list[float]] = {}
    cumul = 0.0
    for ligne in tries:
        montant, poids, sexe, tranche = ligne[:4]
        rang = min(len(QUINTILES_EQCC) - 1, int(5.0 * (cumul + poids / 2.0) / total))
        while len(bornes) < 4 and cumul + poids >= (len(bornes) + 1) * total / 5.0:
            bornes.append(montant)
        cumul += poids
        for cle in (sexe, "ensemble"):
            masses.setdefault(cle, {}).setdefault(
                tranche, [0.0] * len(QUINTILES_EQCC))[rang] += poids
            if len(ligne) > 4 and ligne[4]:
                minima.setdefault(cle, [0.0] * len(QUINTILES_EQCC))[rang] += poids
            if len(ligne) > 5:
                proratisees.setdefault(cle, [0.0] * len(QUINTILES_EQCC))[rang] += (
                    poids * ligne[5])
            if len(ligne) > 6:
                validees.setdefault(cle, [0.0] * len(QUINTILES_EQCC))[rang] += (
                    poids * ligne[6])
            if len(ligne) > 7:
                groupes.setdefault(cle, {}).setdefault(
                    ligne[7], [0.0] * len(QUINTILES_EQCC))[rang] += poids
            if len(ligne) > 8:
                decotes.setdefault(cle, [0.0] * len(QUINTILES_EQCC))[rang] += (
                    poids if ligne[8] else 0.0)
    return {"bornes": bornes, "masses": masses, "minima": minima,
            "proratisees": proratisees, "validees": validees, "groupes": groupes,
            "decotes": decotes}


def confronter_eqcc(lignes: list[tuple], quintiles: dict) -> dict:
    """La grille contre l'EIR (:func:`quintiles_eqcc`), sexe par sexe : la part
    du sexe dans chaque quintile de la pension en équivalent carrière complète,
    celle de chaque tranche de durée qui tombe dans le premier, celle des
    retraités au minimum dans chaque quintile — l'EIR, au minimum de leur régime
    principal —, leur proratisation et, là où l'EIR les publie, leur durée
    validée, majorations comprises, la place de chaque groupe — la part de
    ses retraités dans chaque quintile, monopensionnés et polypensionnés de
    deux régimes dont c'est le régime principal —, et, là où la grille les
    compte et l'EIR les publie, les départs avec décote."""
    rangees = quintiles_ponderes(lignes)
    sortie: dict = {"bornes": rangees["bornes"]}
    for sexe in ("F", "H"):
        par_tranche = rangees["masses"].get(sexe)
        if not par_tranche:
            continue
        par_quintile = [somme_ordonnee(masses[i] for masses in par_tranche.values())
                        for i in range(len(QUINTILES_EQCC))]
        total = somme_ordonnee(par_quintile)
        effectifs = [quintiles[(q, "effectifs", sexe)] for q in QUINTILES_EQCC]
        tous = somme_ordonnee(effectifs)
        tranches = {}
        for tranche, _ in TRANCHES:
            masses = par_tranche.get(tranche, [0.0] * len(QUINTILES_EQCC))
            publiees = [effectif * quintiles[(q, f"part_duree_validee_hors_majoration_{tranche}",
                                              sexe)]
                        for q, effectif in zip(QUINTILES_EQCC, effectifs)]
            masse = somme_ordonnee(masses)
            tranches[tranche] = {
                "premier_quintile": masses[0] / masse if masse else None,
                "premier_quintile_eir": publiees[0] / somme_ordonnee(publiees),
            }
        minima = rangees["minima"].get(sexe, [0.0] * len(QUINTILES_EQCC))
        sortie[sexe] = {"quintiles": [masse / total for masse in par_quintile],
                        "quintiles_eir": [effectif / tous for effectif in effectifs],
                        "tranches": tranches,
                        "minimum": [au_minimum / masse if masse else None
                                    for au_minimum, masse in zip(minima, par_quintile)],
                        "minimum_eir": [quintiles[(q, "part_minimum_pension_regime_principal",
                                                   sexe)] / 100.0 for q in QUINTILES_EQCC],
                        "minimum_ensemble": somme_ordonnee(minima) / total,
                        "minimum_ensemble_eir": quintiles[
                            ("ensemble", "part_minimum_pension_regime_principal", sexe)] / 100.0,
                        "proratisation": [proratisee / masse if masse else None
                                          for proratisee, masse in zip(
                                              rangees["proratisees"].get(
                                                  sexe, [0.0] * len(QUINTILES_EQCC)),
                                              par_quintile)],
                        "proratisation_eir": [quintiles[(q, "coefficient_proratisation",
                                                         sexe)] / 100.0
                                              for q in QUINTILES_EQCC],
                        "duree_validee": [validee / masse if masse and validee is not None
                                          else None
                                          for validee, masse in zip(
                                              rangees["validees"].get(
                                                  sexe, [None] * len(QUINTILES_EQCC)),
                                              par_quintile)],
                        "duree_validee_eir": [quintiles.get((q, "duree_validee", sexe))
                                              for q in QUINTILES_EQCC],
                        "groupes": places_des_groupes(rangees["groupes"].get(sexe, {}),
                                                      quintiles, sexe)}
        decotes = rangees["decotes"].get(sexe)
        if decotes is not None and ("ensemble", "part_decote", sexe) in quintiles:
            sortie[sexe].update({
                "decote": [d / masse if masse else None
                           for d, masse in zip(decotes, par_quintile)],
                "decote_eir": [quintiles[(q, "part_decote", sexe)] / 100.0
                               for q in QUINTILES_EQCC],
                "decote_ensemble": somme_ordonnee(decotes) / total,
                "decote_ensemble_eir": quintiles[("ensemble", "part_decote", sexe)] / 100.0})
    return sortie


def places_des_groupes(masses: dict[str, list[float]], quintiles: dict,
                       sexe: str) -> dict[str, dict[str, list[float]]]:
    """La part des retraités de chaque groupe dans chaque quintile, celle de
    la grille et celle de l'EIR, là où il publie le régime principal
    (``quintiles_eqcc_residents.csv``) : ses monopensionnés et ses
    polypensionnés de deux régimes, aux effectifs de chaque quintile."""
    sortie = {}
    for groupe, (indicateurs, _) in GROUPES.items():
        publies = [quintiles[(q, "effectifs", sexe)] * somme_ordonnee(
                       quintiles[(q, f"part_{statut}_{indicateur}", sexe)]
                       for statut in ("mono", "poly") for indicateur in indicateurs)
                   if all((q, f"part_{statut}_{indicateur}", sexe) in quintiles
                          for statut in ("mono", "poly") for indicateur in indicateurs)
                   else None
                   for q in QUINTILES_EQCC]
        siennes = masses.get(groupe)
        if siennes is None or any(p is None for p in publies):
            continue
        total, tous = somme_ordonnee(siennes), somme_ordonnee(publies)
        if not total or not tous:
            continue
        sortie[groupe] = {"grille": [m / total for m in siennes],
                          "eir": [p / tous for p in publies]}
    return sortie


def eqcc(parametres: Parametres, variantes: list[Variante], tetes: GrilleEnTetes,
         quintiles: dict, annee: int, processus: int = 1) -> dict:
    """La grille l'année de l'enquête, chaque cohorte à sa pension divisée par
    sa proratisation (:func:`proratisations`), rangée comme l'EIR range les
    retraités (:func:`confronter_eqcc`) : ce qu'une carrière acquiert par année
    validée, selon sa durée, et qui le minimum relève ; et la durée validée de
    chaque génération (:func:`durees_par_generation`)."""
    par_code = {v.cas.code: v for v in variantes}
    cas_par_code = {cas.code: cas for cas in tetes.cas_types}
    cohortes = tetes.cohortes(annee)
    coefficients = proratisations(
        parametres, {(cas_par_code[pensionne.code], pensionne.generation)
                     for pensionne, _, _ in cohortes}, processus)
    lignes, durees = [], []
    for pensionne, montant, poids in cohortes:
        coefficient, minimum, annees, decote = coefficients.get(
            (pensionne.code, pensionne.generation), (0.0, False, 0.0, False))
        if not coefficient:
            continue
        v = par_code[pensionne.code]
        lignes.append((montant / coefficient, poids, v.cas.sexe,
                       tranche_de_duree(duree_de(v)), minimum, coefficient, annees,
                       v.groupe, decote))
        durees.append((pensionne.generation, v.cas.sexe, annees, poids))
    sortie = confronter_eqcc(lignes, quintiles)
    sortie["durees"] = durees_par_generation(
        durees, durees_d_assurance(parametres.racine_donnees))
    return sortie


def durees_d_assurance(racine: Path) -> dict[tuple[int, str], float]:
    """La durée d'assurance moyenne des retraités résidant en France, en
    années, génération par génération, sexe par sexe, majorations de durée
    comprises : l'EIR de 2020, prolongé par TRAJECTOiRE
    (``duree_assurance_generations.csv``)."""
    sexes = {"femmes": "F", "hommes": "H"}
    return {(int(l["generation"]), sexes[l["sexe"]]): float(l["trimestres"]) / 4.0
            for l in _lire_macro(racine, "duree_assurance_generations.csv")}


def durees_par_generation(lignes: list[tuple[int, str, float, float]],
                          publiees: dict[tuple[int, str], float]) -> dict:
    """La durée validée moyenne de la grille, génération simulée par génération
    simulée, sexe par sexe, contre celle que l'EIR mesure (:func:`durees_d_assurance`)
    en moyenne des générations que chacune représente, à :data:`C._DEMI_TRANCHE`
    ans près. ``lignes`` : ``(génération, sexe, années validées, poids)``."""
    masses: dict[tuple[str, int], list[float]] = {}
    for generation, sexe, annees, poids in lignes:
        masse = masses.setdefault((sexe, generation), [0.0, 0.0])
        masse[0] += poids * annees
        masse[1] += poids
    totaux: dict[str, float] = {}
    for (sexe, _), (_, poids) in masses.items():
        totaux[sexe] = totaux.get(sexe, 0.0) + poids
    sortie: dict[str, list[dict]] = {}
    for (sexe, generation), (cumul, poids) in sorted(masses.items()):
        voisines = [publiees[(g, sexe)] for g in range(generation - C._DEMI_TRANCHE,
                                                       generation + C._DEMI_TRANCHE + 1)
                    if (g, sexe) in publiees]
        sortie.setdefault(sexe, []).append({
            "generation": generation, "part": poids / totaux[sexe], "annees": cumul / poids,
            "eir": somme_ordonnee(voisines) / len(voisines) if voisines else None})
    return sortie


def processus_par_defaut() -> int:
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:       # hors de Linux
        return os.cpu_count() or 1


def mesurer(noms: tuple[str, ...] = GRILLES, processus: int = 1,
            parametres: Parametres | None = None, page: bool = True) -> dict:
    """Chaque grille, sa composition, la distribution de ses pensions l'année de
    l'enquête et ce que la page y affiche ; la page elle-même, que la grille du
    dépôt, réécrite en parts, doit redonner. ``page=False`` s'en tient à la
    composition et à la distribution, que la simulation seule donne. Une grille
    qui a des tranches de durée est en outre rangée par quintile de sa pension
    en équivalent carrière complète, contre l'EIR (:func:`eqcc`) ; une grille
    qui a des artisans les confronte aux anciens artisans et commerçants de
    l'EIR (:func:`confronter_non_salaries`)."""
    parametres = parametres if parametres is not None else Parametres()
    racine = parametres.racine_donnees
    source = eir(racine)
    publies = quintiles_eqcc(racine, residents=True)
    annee_centiles, valeurs = centiles(racine)
    points = multiplicateurs(valeurs)
    effectifs = Simulateur(parametres).effectifs
    residence = ResidenceRetraites(racine, source.millesime)
    distributions = {sexe: DistributionPensions(racine, sexe, source.millesime, "france")
                     for sexe in SEXES}
    non_salaries = pensions_non_salaries(racine)
    resultat = {
        "eir": {"millesime": source.millesime, **composition_eir(source)},
        "centiles": {"annee": annee_centiles,
                     "points": [{"centile": n, "part": p, "multiplicateur": m}
                                for n, p, m in points]},
        "grilles": {},
    }
    if page:
        resultat["page"] = indicateurs(memoire.cout(parametres))
    noms = ("reference",) + tuple(n for n in noms if n != "reference")
    for nom in noms:
        debut = time.time()
        variantes = grille(nom, effectifs, source, points)
        mesure = {"cas_types": len(variantes)}
        if page:
            mesure.update(indicateurs(calculer(parametres, variantes, processus)))
        tetes = en_tetes(parametres, variantes, processus)
        mesure["echecs"] = somme_ordonnee(tetes.echecs.values())
        mesure["composition"] = composition(variantes, effectifs, source)
        mesure["distribution"] = confronter(tetes.pensions(source.millesime),
                                            residence, distributions)
        independants = confronter_non_salaries(tetes.pensions_par_cas_type(source.millesime),
                                               non_salaries)
        if independants:
            mesure["non_salaries"] = independants
        if any(v.tranche is not None for v in variantes):
            mesure["eqcc"] = eqcc(parametres, variantes, tetes, publies, source.millesime,
                                  processus)
        mesure["secondes"] = round(time.time() - debut, 1)
        resultat["grilles"][nom] = mesure
    return resultat


# -- l'impression ----------------------------------------------------------------

NUMEROS = {scenario: str(rang) for rang, (scenario, _) in enumerate(C.SCENARIOS, 1)}


def ecart_maximal(a: dict, b: dict) -> float:
    """Le plus grand écart entre deux jeux d'indicateurs."""
    return max(abs(a[s][k] - b[s][k]) for s, _ in C.SCENARIOS for k in a[s])


def imprimer_distribution(resultat: dict) -> None:
    """La distribution de chaque grille contre celle de l'EIR, sexe par sexe."""
    grilles = resultat["grilles"]
    millesime = resultat["eir"]["millesime"]
    codes = ("d1", "d2", "d3", "mediane", "d7", "d8", "d9")
    print(f"\nLa pension de droit direct en {millesime}, contre celle de l'EIR — "
          "résidents en France, majorations pour enfants comprises, euros par mois ; "
          "Kolmogorov : le plus grand écart des répartitions, et la borne où il tombe")
    for sexe in SEXES:
        lus = [(nom, g["distribution"][sexe]) for nom, g in grilles.items()
               if sexe in g["distribution"]]
        if not lus:
            continue
        print(f"\n{INTITULES_SEXES[sexe]:16}{'part':>6}{'moyenne':>9}"
              + "".join(f"{c:>8}" for c in codes) + f"{'Kolmogorov':>14}")
        eir_ = lus[0][1]
        print(f"{'  EIR':16}{eir_['part_eir'] * 100:>5.1f}%{eir_['moyenne_eir']:>9.0f}"
              + "".join(f"{eir_['quantiles_eir'][c]:>8.0f}" for c in codes))
        for nom, d in lus:
            print(f"{'  ' + nom:16}{d['part'] * 100:>5.1f}%{d['moyenne']:>9.0f}"
                  + "".join(f"{d['quantiles'][c]:>8.0f}" for c in codes)
                  + f"{d['kolmogorov'] * 100:>+8.1f} pt à {d['borne_kolmogorov']:.0f}")


def imprimer_non_salaries(resultat: dict) -> None:
    """La pension des indépendants de chaque grille contre celle de leurs
    anciens dans l'EIR, sexe par sexe."""
    lues = [(nom, g["non_salaries"]) for nom, g in resultat["grilles"].items()
            if "non_salaries" in g]
    if not lues:
        return
    quartiles = [q for q, _ in QUARTILES]
    print(f"\nLa pension des anciens indépendants en {resultat['eir']['millesime']}, contre "
          "l'EIR (INSEE, fiche 1.11) — leur part parmi les retraités du sexe, leur moyenne "
          "et leurs quartiles, euros par mois ; chaque quartile rapporté à celui de tous")
    for regime in INDEPENDANTS.values():
        for sexe in SEXES:
            mesures = [(nom, m[regime][sexe]) for nom, m in lues
                       if regime in m and sexe in m[regime]]
            if not mesures:
                continue
            print(f"\n{regime + ', ' + INTITULES_SEXES[sexe].lower():30}{'part':>7}"
                  f"{'moyenne':>9}" + "".join(f"{q:>9}" for q in quartiles)
                  + "".join(f"{q + '/tous':>14}" for q in quartiles))
            eir_ = mesures[0][1]
            print(f"{'  EIR':30}{eir_['part_eir'] * 100:>6.1f}%{eir_['moyenne_eir']:>9.0f}"
                  + "".join(f"{eir_['quantiles_eir'][q]:>9.0f}" for q in quartiles)
                  + "".join(f"{eir_['relatifs_eir'][q]:>14.2f}" for q in quartiles))
            for nom, m in mesures:
                print(f"{'  ' + nom:30}{m['part'] * 100:>6.1f}%{m['moyenne']:>9.0f}"
                      + "".join(f"{m['quantiles'][q]:>9.0f}" for q in quartiles)
                      + "".join(f"{m['relatifs'][q]:>14.2f}" for q in quartiles))


def imprimer_eqcc(resultat: dict) -> None:
    """Les grilles qui ont des tranches de durée, rangées par quintile de leur
    pension en équivalent carrière complète, contre l'EIR des résidents."""
    lues = [(nom, g["eqcc"]) for nom, g in resultat["grilles"].items() if "eqcc" in g]
    if not lues:
        return
    millesime = resultat["eir"]["millesime"]
    print(f"\nLa pension en équivalent carrière complète en {millesime} — la pension "
          "divisée par la proratisation, ce qu'une carrière acquiert par année validée — "
          "contre l'EIR des résidents : la part de chaque tranche de durée au premier "
          "quintile, et celle du sexe")
    tranches = [nom for nom, _ in reversed(TRANCHES)]
    for sexe in ("F", "H"):
        print(f"\n{INTITULES_SEXES[sexe]:16}" + "".join(f"{t:>10}" for t in tranches)
              + f"{'sexe':>8}")
        _, premiere = lues[0]
        print(f"{'  EIR':16}" + "".join(
            f"{premiere[sexe]['tranches'][t]['premier_quintile_eir'] * 100:>9.1f}%"
            for t in tranches) + f"{premiere[sexe]['quintiles_eir'][0] * 100:>7.1f}%")
        for nom, mesure in lues:
            print(f"{'  ' + nom:16}" + "".join(
                f"{mesure[sexe]['tranches'][t]['premier_quintile'] * 100:>9.1f}%"
                if mesure[sexe]["tranches"][t]["premier_quintile"] is not None else f"{'—':>10}"
                for t in tranches) + f"{mesure[sexe]['quintiles'][0] * 100:>7.1f}%")
    print("\n" + "  ".join(f"{nom} : bornes {', '.join(f'{b:.0f}' for b in m['bornes'])} €"
                           for nom, m in lues))
    print("\nLa part au minimum de pension, quintile par quintile — l'EIR, au minimum du "
          "régime principal")
    for sexe in ("F", "H"):
        print(f"\n{INTITULES_SEXES[sexe]:16}" + "".join(f"{q:>8}" for q in QUINTILES_EQCC)
              + f"{'ensemble':>10}")
        _, premiere = lues[0]
        print(f"{'  EIR':16}" + "".join(f"{p * 100:>7.1f}%"
                                        for p in premiere[sexe]["minimum_eir"])
              + f"{premiere[sexe]['minimum_ensemble_eir'] * 100:>9.1f}%")
        for nom, mesure in lues:
            print(f"{'  ' + nom:16}" + "".join(
                f"{p * 100:>7.1f}%" if p is not None else f"{'—':>8}"
                for p in mesure[sexe]["minimum"])
                + f"{mesure[sexe]['minimum_ensemble'] * 100:>9.1f}%")
    print("\nLa proratisation moyenne, quintile par quintile — l'EIR, la somme des "
          "coefficients des régimes de base")
    for sexe in ("F", "H"):
        print(f"\n{INTITULES_SEXES[sexe]:16}" + "".join(f"{q:>8}" for q in QUINTILES_EQCC))
        _, premiere = lues[0]
        print(f"{'  EIR':16}" + "".join(f"{p * 100:>7.1f}%"
                                        for p in premiere[sexe]["proratisation_eir"]))
        for nom, mesure in lues:
            print(f"{'  ' + nom:16}" + "".join(
                f"{p * 100:>7.1f}%" if p is not None else f"{'—':>8}"
                for p in mesure[sexe]["proratisation"]))
    _, premiere = lues[0]
    if all("decote" in premiere[sexe] for sexe in ("F", "H")):
        print("\nLa part des départs avec décote, quintile par quintile")
        for sexe in ("F", "H"):
            print(f"\n{INTITULES_SEXES[sexe]:16}" + "".join(f"{q:>8}" for q in QUINTILES_EQCC)
                  + f"{'ensemble':>10}")
            print(f"{'  EIR':16}" + "".join(f"{p * 100:>7.1f}%"
                                            for p in premiere[sexe]["decote_eir"])
                  + f"{premiere[sexe]['decote_ensemble_eir'] * 100:>9.1f}%")
            for nom, mesure in lues:
                if "decote" not in mesure[sexe]:
                    continue
                print(f"{'  ' + nom:16}" + "".join(
                    f"{p * 100:>7.1f}%" if p is not None else f"{'—':>8}"
                    for p in mesure[sexe]["decote"])
                    + f"{mesure[sexe]['decote_ensemble'] * 100:>9.1f}%")
    if all(d is not None for sexe in ("F", "H") for d in premiere[sexe]["duree_validee_eir"]):
        print("\nLa durée validée, quintile par quintile, en années, majorations comprises")
        for sexe in ("F", "H"):
            print(f"\n{INTITULES_SEXES[sexe]:16}" + "".join(f"{q:>8}" for q in QUINTILES_EQCC))
            print(f"{'  EIR':16}" + "".join(f"{d:>8.1f}"
                                            for d in premiere[sexe]["duree_validee_eir"]))
            for nom, mesure in lues:
                print(f"{'  ' + nom:16}" + "".join(
                    f"{d:>8.1f}" if d is not None else f"{'—':>8}"
                    for d in mesure[sexe]["duree_validee"]))
    if all(premiere[sexe]["groupes"] for sexe in ("F", "H")):
        print("\nLa place de chaque régime, quintile par quintile — la part de ses "
              "retraités dans chaque quintile ; l'EIR, ses monopensionnés et ses "
              "polypensionnés de deux régimes")
        for sexe in ("F", "H"):
            print(f"\n{INTITULES_SEXES[sexe]:30}" + "".join(f"{q:>8}" for q in QUINTILES_EQCC))
            for nom, mesure in lues:
                for groupe, place in mesure[sexe]["groupes"].items():
                    intitule = INTITULES_GROUPES.get(groupe, groupe)
                    print(f"{'  ' + intitule + ', EIR':30}" + "".join(
                        f"{p * 100:>7.1f}%" for p in place["eir"]))
                    print(f"{'  ' + intitule + ', ' + nom:30}" + "".join(
                        f"{p * 100:>7.1f}%" for p in place["grille"]))
    print("\nLa durée validée, génération par génération, en années — l'EIR, la durée "
          "d'assurance des résidents, majorations comprises ; la part de chaque génération")
    for sexe in ("F", "H"):
        for nom, mesure in lues:
            generations = [ligne for ligne in mesure.get("durees", {}).get(sexe, [])
                           if ligne["part"] >= 0.01]
            if not generations:
                continue
            print(f"\n{INTITULES_SEXES[sexe]:16}"
                  + "".join(f"{ligne['generation']:>8}" for ligne in generations))
            print(f"{'  EIR':16}" + "".join(
                f"{ligne['eir']:>8.1f}" if ligne["eir"] is not None else f"{'—':>8}"
                for ligne in generations))
            print(f"{'  ' + nom:16}" + "".join(f"{ligne['annees']:>8.1f}"
                                               for ligne in generations))
            print(f"{'  part':16}" + "".join(f"{ligne['part'] * 100:>7.1f}%"
                                             for ligne in generations))


def imprimer(resultat: dict) -> None:
    grilles = resultat["grilles"]
    base = grilles["reference"]
    eir_ = resultat["eir"]
    print(f"Ce que les treize cas types déplacent sur la page Coût "
          f"(EIR {eir_['millesime']}, centiles {resultat['centiles']['annee']})\n")
    page = resultat.get("page")
    if page is not None:
        print(f"La grille du dépôt, réécrite en parts, redonne la page à "
              f"{ecart_maximal(base, page):.1e} près.\n")

    print("Composition, retraités de l'année de l'enquête :")
    entete = f"{'':16}{'femmes':>8}{'poly':>7}{'durée F':>9}{'durée H':>9}{'<30 F':>7}{'<30 H':>7}"
    print(entete)
    for nom, comp in [("EIR", eir_)] + [(n, g["composition"]) for n, g in grilles.items()]:
        d, c = comp["duree_validee"], comp["moins_de_30_ans"]
        print(f"{nom:16}{comp['femmes']*100:>7.1f}%{comp['polypensionnes']*100:>6.1f}%"
              f"{d.get('F', float('nan')):>9.1f}{d.get('H', float('nan')):>9.1f}"
              f"{c.get('F', float('nan'))*100:>6.1f}%{c.get('H', float('nan'))*100:>6.1f}%")
    imprimer_distribution(resultat)
    imprimer_non_salaries(resultat)
    imprimer_eqcc(resultat)

    if page is not None:
        horizon = page["annee_horizon"]
        colonnes = (("ecart_passe", "écart passé (pts)", "notionnels"),
                    ("part_pib_horizon", f"part du PIB {horizon} (pts)", "tous"),
                    ("solde_moyen", "solde moyen 2026-" + str(horizon) + " (pts)",
                     "notionnels"),
                    ("coefficient_horizon", f"coefficient {horizon}", "notionnels"))
        for cle, titre, champ in colonnes:
            print(f"\n{titre} — la grille du dépôt, puis ce que chaque grille déplace")
            scenarios = [s for s, _ in C.SCENARIOS if champ == "tous" or s != "actuel"]
            chiffres = 3 if cle == "coefficient_horizon" else 2
            print(f"{'':16}" + "".join(f"{'sc. ' + NUMEROS[s]:>9}" for s in scenarios))
            print(f"{'reference':16}" + "".join(f"{base[s][cle]:>9.{chiffres}f}"
                                                for s in scenarios))
            for nom, g in grilles.items():
                if nom == "reference":
                    continue
                print(f"{nom:16}" + "".join(f"{g[s][cle] - base[s][cle]:>+9.{chiffres}f}"
                                            for s in scenarios))
        print(f"\ngarantie vieillesse en {horizon} (pts de PIB) : reference "
              f"{base['garantie_horizon']:.3f}"
              + "".join(f" ; {n} {g['garantie_horizon'] - base['garantie_horizon']:+.3f}"
                        for n, g in grilles.items() if n != "reference"))

        annees = (1990, 2000, 2009, 2020)
        print("\nle passé refait par la projection (action 147) — écart de la base du "
              "modèle à la dépense observée, en %")
        print(f"{'':16}" + "".join(f"{a:>9}" for a in annees) + f"{'pire ≥ 2000':>13}")
        for nom, g in grilles.items():
            passe = {int(a): v for a, v in g["reconstitution"].items()}
            print(f"{nom:16}" + "".join(f"{passe[a]:>+9.1f}" if a in passe else f"{'—':>9}"
                                        for a in annees)
                  + f"{g['reconstitution_pire_depuis_2000']:>13.1f}")
    print("\n" + "  ".join(f"{n} : {g['cas_types']} cas types, {g['echecs']} échecs, "
                           f"{g['secondes']} s" for n, g in grilles.items()))


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--grille", action="append", choices=GRILLES,
                           help="une grille seulement (répétable)")
    analyseur.add_argument("--processus", type=int, default=processus_par_defaut(),
                           help="cœurs sur lesquels simuler la grille")
    analyseur.add_argument("--distribution", action="store_true",
                           help="la composition et la distribution seules, sans la page")
    analyseur.add_argument("--json", help="écrit le résultat dans ce fichier")
    arguments = analyseur.parse_args(argv)

    noms = tuple(arguments.grille) if arguments.grille else GRILLES
    resultat = mesurer(noms, arguments.processus, page=not arguments.distribution)
    imprimer(resultat)
    if arguments.json:
        Path(arguments.json).write_text(json.dumps(resultat, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
