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
juge sur les anciens artisans et commerçants de l'EIR. La dix-neuvième (le
18 octobre 2026) fait partir une part des carrières de trente années validées
et plus après l'âge légal et le taux plein, avec une surcote
(:data:`DEPARTS_AVEC_SURCOTE`) : 14,3 % des nés en 1953 sont partis ainsi,
quand la population ne surcotait jamais ; la mesure juge les départs des
générations 1950 et 1955 sur ceux des nés en 1950 et en 1953 (:func:`departs`).
La vingtième (le même jour) fait entrer les carrières pleines du salariat
privé à l'âge où leur génération cotise son premier trimestre, cinquième par
cinquième, que l'échantillon interrégimes de cotisants publie
(:data:`ENTREE_AU_PREMIER_TRIMESTRE`) : toutes entraient assez tôt pour la
carrière longue, quand 22,3 % des hommes nés en 1954 et affiliés avant 23 ans
n'avaient cotisé aucun trimestre à la fin de l'année de leurs 19 ans. La
vingt et unième (le 19 octobre 2026) fait précéder du service national le
cinquième d'homme dont la génération valide un trimestre avant d'en cotiser
un (:data:`SERVICE_AVANT_LE_PREMIER_TRIMESTRE`) : le dernier de la génération
1950 valide son service à 21 ans, cotise à 22, et part à 61 ans et demi au lieu
de 62 ans et demi. La vingt-deuxième (le même jour) donne à chaque classe de
centiles la part de périodes assimilées des quintiles de la pension que ses
rangs couvrent (:data:`ASSIMILEES_SELON_LE_RANG`) : huit années de la carrière
pleine d'une femme de la classe p10, une de celle des classes p95 et p99, au
lieu de cinq pour toutes ; aucune femme ne partait en carrière longue. La
vingt-troisième (le 22 octobre 2026) donne leur nature aux périodes assimilées
des carrières pleines des hommes, le service national et la maladie, aux parts
que l'échantillon interrégimes de cotisants publie génération par génération
(:data:`NATURES_SELON_LA_GENERATION`) : toutes étaient du chômage, que la
carrière longue ne répute pas cotisé avant novembre 2012, quand elle répute le
service et la maladie dans toutes ses rédactions. La vingt-quatrième (le
23 octobre 2026) donne aux carrières pleines des deux sexes leurs natures à
leur part et à leurs années, le chômage et l'AVPF compris
(:data:`NATURES_A_LEUR_PART`) : la population mettait du chômage à tous les
hommes qui n'étaient pas malades, et à toutes les femmes ; chaque classe a
désormais les années de ses natures que l'échantillon donne, sous celles de sa
classe de centiles, et celle qui n'en a aucune n'en compte plus. La
vingt-cinquième (le 24 octobre 2026) donne à la maladie son propre rang
(:data:`MALADIE_INDEPENDANTE`) : la vingt-quatrième mettait le chômage et la
maladie au haut d'un même rang, et tous les malades au chômage, quand
l'échantillon ne publie que la part de chaque nature ; les malades ont
désormais les autres natures à la part de tous. La vingt-sixième (le même
jour) compte quinze classes de nature par rang, et non plus cinq
(:data:`CLASSES_DE_NATURE`) : cinq arrondissaient chaque part au cinquième,
40 % de chômeurs pour 30,2 à 41,0 % des hommes, 20 % de malades pour 10,5 à
14,6 % ; quinze l'arrondissent à un trentième près. La vingt-septième (le
même jour) donne aux femmes leurs natures selon leur rang
(:data:`NATURES_SELON_LE_RANG`) : chaque classe de centiles les avait à la
même part, quand la masse assimilée de l'EIR qui les plafonne va au bas des
rangs ; la part de chaque nature y suit désormais la masse de sa classe,
1,80 fois celle de l'échantillon aux classes p10 et p25, 0,24 fois aux classes
p95 et p99, et les femmes nées en 1950 comptent 4,60 années de maladie,
d'AVPF et de chômage, et non plus 3,42, pour 4,53 que l'échantillon leur
trouve. La vingt-huitième (le 25 octobre 2026) fait entrer plus tôt les
carrières incomplètes des femmes du salariat privé que leur génération allonge
au-delà de 21 ans avant l'âge légal (:data:`ALLONGEES_COMME_LES_PLEINES`) :
elles entraient toutes à 21 ans, l'entrée du gabarit, et la condition d'entrée
de la carrière longue leur était fermée ; elles entrent désormais comme les
carrières pleines, à l'âge légal moins leurs années, puis cinquième par
cinquième au premier trimestre cotisé de leur génération. La vingt-neuvième
(le même jour) fait suivre leur génération aux départs avec décote
(:data:`DECOTE_SELON_LA_GENERATION`) : la quinzième donnait à toutes la part
des retraités de 2020, 8,8 % des femmes et 4,5 % des hommes, quand l'EIR en
compte 7,9 et 5,6 % chez les nés en 1950, 12,4 et 8,6 % chez les nés en 1953 ;
chaque génération a désormais la sienne, dont la mesure pèse ses cohortes. La
trentième (le même jour) rapporte cette part aux seules carrières incomplètes
qui peuvent décoter à l'ouverture du droit, comme la grille du coût, et la
prend sans ce que les agents des IEG et de la conduite décotent déjà à
l'ouverture de leur statut (:data:`DECOTE_DES_CARRIERES_QUI_LE_PEUVENT`) : née
en 1955, la femme d'une carrière de trente à quarante ans a sa durée dès
62 ans avec ses enfants, et sa jumelle « décotée » partait au taux plein. La
trente et unième (le 28 octobre 2026) fait partir les départs avec décote
entre l'âge légal et l'âge d'annulation de la décote aussi, comme ceux des nés
en 1953 (:data:`DECOTE_ENTRE_LES_DEUX_AGES`) : l'EIR en voit la moitié chez
les femmes, un gros tiers chez les hommes, partir à l'âge légal, où la
population les faisait tous partir.

CE QUE LA MESURE N'EST PAS
---------------------------
Une population. Les axes sont tenus pour indépendants — le salaire ne dépend
ni du sexe ni de la durée —, chaque déclinaison garde l'âge d'entrée et le
profil de son cas type, et les parts sont celles des retraités de 2020,
appliquées à toutes les générations ; seules les carrières incomplètes des
femmes changent de durée avec la leur, et la part des départs avec décote avec
la sienne. La dispersion des salaires est celle d'une
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
from array import array
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
from retraite_notionnelle.controle_eacr import conditions_publiees  # noqa: E402
from retraite_notionnelle.donnees.assiette import AssietteActivite  # noqa: E402
from retraite_notionnelle.donnees.caracteristiques import CaracteristiquesRetraites  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.distribution import (  # noqa: E402
    QUANTILES_PUBLIES, DistributionPensions, ResidenceRetraites,
)
from retraite_notionnelle.donnees.equilibre import (  # noqa: E402
    ComptesRetraite, DecompositionDepense, variante_du_scenario,
)
from retraite_notionnelle.donnees.macro import ANNEE_CREATION_AVPF, DonneesMacro  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.facteurs_depense import (  # noqa: E402
    ANNEE_DU_FLUX, CAISSE_DU_FLUX, GENERATION_DES_DECOTES, GENERATION_DU_FLUX,
    part_decotee_de_la_generation,
)
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

#: L'entrée des carrières pleines au premier trimestre cotisé : chaque
#: carrière pleine qui entre selon sa génération (:data:`ENTREE_SELON_LA_GENERATION`),
#: hors des départs avec surcote, se décline en :data:`CLASSES_D_ENTREE`
#: classes de poids égal, rangées par l'âge où leur génération cotise son
#: premier trimestre parmi les affiliés d'avant 23 ans de leur sexe
#: (``premier_trimestre.csv``, EIC 2017, :func:`classes_d_entree`) ; chacune
#: entre à cet âge, ou à celui de la onzième version s'il vient plus tard. La
#: condition d'entrée de la carrière longue se lit sur les trimestres cotisés
#: à la fin de l'année des 16, 17 ou 20 ans (D. 351-1-1) : toutes les
#: carrières pleines y satisfaisaient, quand 38,2 % des hommes nés en 1950
#: avaient cotisé un trimestre à 16 ans, et 77,7 % de ceux nés en 1954 à
#: 19 ans ; les hommes partaient en carrière longue deux fois plus que dans
#: l'EIR. Les départs avec surcote gardent leur entrée : ils renoncent à la
#: carrière longue, et la page pèse ses carrières à un coût qui croît comme
#: leur carré. La vingtième version.
ENTREE_AU_PREMIER_TRIMESTRE = True

#: Les classes de l'entrée au premier trimestre : des cinquièmes, chacun
#: entrant à l'âge du milieu de son rang ; ceux qui entrent au même âge à
#: chaque génération n'en font qu'un — les deux premiers des hommes.
CLASSES_D_ENTREE = 5

#: La vingt et unième version (action 138, étape 14, le 19 octobre 2026) : le
#: service national avant le premier trimestre cotisé. Sous
#: :data:`ENTREE_AU_PREMIER_TRIMESTRE`, chaque cinquième d'une carrière pleine
#: entre à l'âge où sa génération COTISE son premier trimestre ; elle en VALIDE
#: un plus tôt, de ce qu'un affilié valide sans cotiser — chez les hommes, le
#: service national : 93,2 % des hommes nés en 1950 et affiliés avant 23 ans
#: avaient validé un trimestre à la fin de l'année de leurs 21 ans, 84,8 % en
#: avaient cotisé un (``premier_trimestre.csv``, la série des trimestres
#: validés). Le cinquième d'homme dont le rang valide avant de cotiser fait son
#: service (``service_militaire``) les années qui séparent les deux âges, avant
#: d'entrer (:func:`classes_d_entree`) : le dernier, à 21 ans quand il cotise à
#: 22 dans la génération 1950, à 20 et 21 ans dans celle de 1946. Sa durée
#: d'assurance commence plus tôt, et son service est réputé cotisé pour la
#: carrière longue dans la limite de quatre trimestres (D. 351-1-2) ; la
#: condition d'entrée, qui ne lit que les trimestres cotisés, ne change pas.
#: Les femmes gardent leur entrée : un cinquième de trois de leurs générations
#: valide un an avant de cotiser, d'une nature que l'échantillon ne dit pas.
SERVICE_AVANT_LE_PREMIER_TRIMESTRE = True

#: La vingt-deuxième version (le même jour) : les périodes assimilées selon le
#: rang. Chaque carrière du salariat et des non-salariés en comptait la même
#: part, celle que l'EIR mesure à tous les résidents de son sexe — 12,5 % de la
#: durée validée hors majorations des femmes (32 années, dont 28 cotisées),
#: 10 % de celle des hommes (40, dont 36) —, toutes au chômage indemnisé : cinq
#: années de la carrière pleine d'une femme, quatre de celle d'un homme, dont
#: quatre trimestres seulement sont réputés cotisés pour la carrière longue
#: (D. 351-1-2). Aucune femme n'y partait, quand l'EIR en compte 13,0 % des
#: nées en 1953. La part suit pourtant la pension : l'EIR mesure aux résidentes
#: du premier quintile de la pension en équivalent carrière complète 23 années
#: validées pour 17 cotisées, 26,1 % d'assimilées, à celles du cinquième 39
#: pour 38, 2,6 % ; aux résidents, 12,5 % au premier et au deuxième, de 4,9 à
#: 9,8 % aux autres (``quintiles_eqcc_residents.csv``). Sous cette constante,
#: chaque classe de centiles prend, dans chaque tranche de durée, la part des
#: bandes de quintiles que ses rangs couvrent, comme sous
#: :data:`RANG_SELON_LA_DUREE`, les retraités au minimum portant celle de leur
#: quintile dans la bande du premier (:func:`parts_assimilees_des_classes`) : la
#: carrière pleine d'une femme compte huit années assimilées dans la classe p10,
#: une dans les classes p95 et p99. Deux conventions : la part d'un quintile vaut
#: pour toutes ses tranches de durée, et l'EIR arrondissant ses durées à
#: l'année, elle se lit à une année près.
ASSIMILEES_SELON_LE_RANG = True

#: La vingt-troisième version (action 138, étape 14, le 22 octobre 2026) : la
#: nature des périodes assimilées des hommes. Toutes étaient du chômage
#: indemnisé, que la carrière longue ne répute pas cotisé avant novembre 2012,
#: puis dans la limite de deux trimestres, de quatre depuis avril 2014
#: (D. 351-1-2, daté) ; or l'échantillon interrégimes de cotisants en trouve
#: d'autres aux hommes affiliés avant 23 ans (``natures_assimilees.csv``) :
#: nés en 1950, 35,1 % ont validé un trimestre de service national, quatre
#: chacun, et 12,6 % un de maladie, dix-sept chacun, que toutes les rédactions
#: réputent cotisés dans la limite de quatre trimestres. Sous cette
#: constante, chaque cinquième d'une carrière pleine d'homme
#: (:data:`ENTREE_AU_PREMIER_TRIMESTRE`) se décline en
#: :data:`CLASSES_DE_NATURE` classes de poids égal (:func:`classes_de_nature`) :
#: une classe sert — sa première année assimilée est son service national —
#: quand le milieu de son rang passe sous la part du service qui reste aux
#: cinquièmes qui ne servent pas avant d'entrer
#: (:data:`SERVICE_AVANT_LE_PREMIER_TRIMESTRE`) ; une classe est malade —
#: autant de ses années assimilées que chacun de ceux qui le sont en compte —
#: quand le milieu de son rang passe au-dessus de la part des autres. En 1950,
#: la première classe sert et la dernière est malade : 36 % des hommes ont une
#: année de service, 20 % quatre de maladie. Les années gardent leur place, au
#: milieu de la carrière ; les autres carrières des hommes, et celles des
#: femmes, gardent leur chômage.
NATURES_SELON_LA_GENERATION = True

#: Les classes de nature de chaque rang, de poids égal, chacune au milieu de
#: son rang ; celles qui ont les mêmes natures à chaque génération n'en font
#: qu'une. Sous :data:`MALADIE_INDEPENDANTE`, chacune se décline en autant de
#: classes du rang de la maladie (:func:`rangs_de_nature`). La vingt-sixième
#: version (action 138, étape 14, le 24 octobre 2026) en compte quinze, et
#: non plus cinq : une classe a une nature quand le milieu de son rang passe
#: la part qu'en publie l'échantillon, qui s'arrondit ainsi au nombre de
#: classes le plus proche ; cinq classes donnaient 40 % de chômeurs pour 30,2
#: à 41,0 % des hommes des générations 1942 à 1956, 20 % de malades pour 10,5
#: à 14,6 %, quinze arrondissent chaque part au quinzième, à un trentième
#: près. Chaque classe de cinq se coupe en trois ; le nombre impair garde une
#: classe au milieu de chaque rang, qui garde le code de son cinquième. Ce
#: que les versions précédentes disent de leurs classes vaut sous cinq.
CLASSES_DE_NATURE = 15

#: La vingt-quatrième version (action 138, étape 14, le 23 octobre 2026) : les
#: natures à leur part et à leurs années. Sous la vingt-troisième, les années
#: assimilées qui n'étaient ni service ni maladie restaient du chômage, à tous
#: les hommes, et toutes celles des femmes : la carrière longue en réputait
#: quatre trimestres à chacun depuis avril 2014 (D. 351-1-2, daté), quand
#: l'échantillon interrégimes de cotisants ne trouve du chômage qu'à 32,5 %
#: des hommes nés en 1950, et que l'AVPF, qu'elle ne répute cotisée que depuis
#: septembre 2023, fait plus de la moitié des trimestres que les femmes
#: valident sans les cotiser (``natures_assimilees.csv``). Sous cette
#: constante, les cinquièmes des carrières pleines des deux sexes se déclinent
#: en :data:`CLASSES_DE_NATURE` classes, chacune avec les natures que sa
#: génération donne à son rang, à la part des affiliés qui en ont : le
#: service et l'AVPF du bas des rangs, le chômage et la maladie du haut
#: (:func:`classes_de_nature`), chacune aux années qu'en a chacun de ceux qui
#: en ont, arrondies, une au moins. La classe qui n'en a aucune n'en compte
#: aucune : ses années sont cotisées. Les années assimilées que la classe de
#: centiles tient de l'EIR (:data:`ASSIMILEES_SELON_LE_RANG`), cinq fois les
#: siennes pour un cinquième, en sont le plafond : quand ses classes en
#: demandent plus, ce que le service leur laisse se partage à proportion. Les
#: répartir toutes entre les seules classes qui ont une nature, quand elles
#: passent celles de l'échantillon, multipliait celles-ci par 1,3 à 2,9 : dix
#: années de chômage et de maladie à l'homme de la classe p50 né en 1950 qui
#: est l'un et l'autre, quand l'échantillon en donne sept, et la carrière
#: longue des hommes de 1955 tombait de 25,8 à 19,6 % (EIR 28,6). Chaque
#: classe refait le bloc de ses années assimilées au milieu de sa carrière
#: (:func:`refaire_le_bloc`) ; l'AVPF d'avant 1972, qui n'existait pas, y reste
#: du chômage.
NATURES_A_LEUR_PART = True

#: La vingt-cinquième version (action 138, étape 14, le 24 octobre 2026) : la
#: maladie indépendante des autres natures. L'échantillon interrégimes de
#: cotisants publie la part des affiliés qui ont validé chaque nature, non
#: celle de ceux qui en ont deux ; sous la vingt-quatrième, le chômage et la
#: maladie se donnaient au haut d'un même rang, et tous les malades étaient au
#: chômage : la classe malade et au chômage de la génération 1955, sept années
#: assimilées dont huit trimestres réputés cotisés, perdait la carrière
#: longue. Or la note de la Cnav au COR sur la génération 1944 (séance du
#: 25 mai 2011, document n° 10, tableau 11) donne, avec la part de ses
#: retraités qui ont eu chaque période assimilée, celle de ceux qui en ont eu
#: au moins une : 76,7 % des hommes, pour 49,9 % au chômage, 38,1 % malades,
#: 8,1 % invalides et 2,9 % à l'AVPF. De 29,7 à 58,5 % de ses malades ont donc
#: été au chômage, et non tous ; la part de tous, 49,9 %, celle de
#: l'indépendance, y tombe. Sous cette constante, la maladie a son propre rang
#: (:func:`rangs_de_nature`) : chaque classe de nature se décline en
#: :data:`CLASSES_DE_NATURE` classes de la maladie, dont celles du haut sont
#: malades, et les malades ont le service, l'AVPF et le chômage à la part de
#: tous.
MALADIE_INDEPENDANTE = True

#: La vingt-septième version (action 138, étape 14, le 24 octobre 2026) : les
#: natures des femmes selon leur rang. Sous la vingt-quatrième, chaque classe
#: de centiles donnait ses natures à la même part, quand la masse assimilée
#: de l'EIR qui les plafonne (:data:`NATURES_A_LEUR_PART`) va au bas des
#: rangs : l'EIR ne cotise pas 26,1 % de la durée validée hors majorations
#: des résidentes du premier quintile, 2,6 % de celle du cinquième
#: (``quintiles_eqcc_residents.csv``). Le haut était plafonné, le bas gardait
#: des années cotisées. Sous cette constante, la part des femmes d'une classe
#: qui ont de la maladie, de l'AVPF ou du chômage est celle de l'échantillon
#: interrégimes de cotisants, multipliée par le rapport de la masse de sa
#: classe (:data:`ASSIMILEES_SELON_LE_RANG`) à celle de toutes les carrières
#: pleines des femmes, leurs classes pesées par leur poids
#: (:func:`masses_moyennes`) : 0,24 fois aux classes p95 et p99, 1,80 fois aux
#: classes p10 et p25 ; chacune de celles qui en ont garde les années de
#: l'échantillon (:func:`natures_au_rang`). Les hommes gardent la même part à
#: chaque rang : la masse du stock de 2020 remonte au haut des leurs, 4,9 % au
#: troisième quintile, 9,8 % au cinquième, que ses générations anciennes
#: portent et que les classeurs des nés en 1950 et en 1953, non certifiés, ne
#: trouvent pas (note de la treizième partie).
NATURES_SELON_LE_RANG = ("F",)

#: Les natures qui croissent avec l'âge, que :func:`natures_assimilees` ne lit
#: qu'à 60 ans : les générations que l'échantillon ne voit pas jusque-là
#: prennent celles de la dernière qu'il y voit, 1956.
NATURES_LUES_A_60_ANS = ("maladie", "chomage", "avpf")

#: Les natures que la population lit, à 60 ans au plus. Le fichier dit aussi
#: ce que l'échantillon voit après, et le cumul des trimestres validés et
#: cotisés : ce que compte au-delà la masse assimilée de l'EIR qui les
#: plafonne (:data:`NATURES_A_LEUR_PART`).
NATURES_DE_L_ECHANTILLON = ("service_national", *NATURES_LUES_A_60_ANS)

#: Les motifs du bloc des années assimilées que :func:`refaire_le_bloc` refait,
#: dans leur ordre : le service national, la maladie, l'AVPF, le chômage.
MOTIFS_DES_NATURES = ("service_militaire", "maladie", "education_enfant", "chomage_indemnise")

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

#: La vingt-huitième version (action 138, étape 14, le 25 octobre 2026) : les
#: carrières allongées entrent comme les pleines. Sous
#: :data:`DUREE_DES_FEMMES_SELON_LA_GENERATION`, une carrière incomplète de
#: femme gagne les années de sa génération sans passer l'âge légal, depuis
#: l'entrée du gabarit, 21 ans : celle de trente à quarante ans, qui en gagne
#: six en 1950 et douze en 1955, y butait, 39 années de 21 à 60 ans, 41 de 21
#: à 62, et la condition d'entrée de la carrière longue, des trimestres cotisés
#: à la fin de l'année des 16, 17 ou 20 ans (D. 351-1-1), lui était fermée :
#: 37 % des femmes du régime général de la population, quand l'EIR compte
#: 13,0 % des nées en 1953 parties en carrière longue. Sous cette constante, la
#: carrière incomplète d'une femme du salariat privé dont les années ne
#: tiennent pas entre 21 ans et l'âge légal entre à l'âge légal moins ses
#: années, jamais avant l'entrée des carrières pleines de sa génération
#: (:data:`ENTREE_SELON_LA_GENERATION`), qui borne ses années
#: (:func:`debut_des_annees`) ; puis, comme elles
#: (:data:`ENTREE_AU_PREMIER_TRIMESTRE`), elle se décline en cinquièmes, chacun
#: entrant à l'âge où sa génération cotise son premier trimestre s'il vient
#: plus tard, jamais après 21 ans, et validant d'autant moins d'années
#: (:func:`allongees_au_premier_trimestre`) : la carrière finit où elle
#: finissait. Elle garde ses années assimilées, au chômage, comme toute
#: carrière incomplète ; le calage de la durée des femmes la compte à l'entrée
#: de sa génération, comme il compte les carrières pleines.
ALLONGEES_COMME_LES_PLEINES = True

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

#: La vingt-neuvième version (action 138, étape 14, le 25 octobre 2026) : la
#: part des départs avec décote suit la génération (:func:`decotes_des_generations`),
#: quand la quinzième donnait à toutes celle des retraités de 2020. L'EIR
#: compte 7,9 % de femmes et 5,6 % d'hommes partis avec une décote chez les nés
#: en 1950, 12,4 et 8,6 % chez les nés en 1953 (``departs_generations.csv``) ;
#: la Cnav en décote 13,7 et 13,0 % de ses liquidants de 2024 (EACR, table H),
#: que la grille du coût prête à la génération 1960
#: (``facteurs_depense.part_decotee_de_la_generation``). Chaque génération a la
#: sienne, en droite ligne entre ces trois-là ; celles d'avant 1950, celle qui
#: garde au stock de 2020 la part que l'EIR mesure aux résidents, 8,3 et 3,6 %.
#: Les deux jumelles de chaque carrière incomplète gardent le poids de la
#: quinzième version ; chacune porte ce que chaque génération y change
#: (:func:`parts_des_jumelles`), et la mesure pèse chaque cohorte de la part de
#: sa génération (:meth:`GrilleEnTetes.part_de`). Trois conventions : les parts
#: des nés en 1950 et en 1953 sont celles de tous les retraités, résidents ou
#: non, quand la population et le stock de 2020 ne comptent que des résidents ;
#: les générations d'avant 1950 ont toutes la même ; la page, et la pesée qui
#: recale chaque groupe sur sa dépense, voient la population sans elles, au
#: poids de la quinzième version.
DECOTE_SELON_LA_GENERATION = True

#: La trentième version (action 138, étape 14, le 25 octobre 2026) : la part
#: des départs avec décote de chaque génération se rapporte aux seules
#: carrières incomplètes qui peuvent décoter à l'ouverture du droit — celles
#: que le droit de leur génération y ouvre avant leur taux plein
#: (:func:`decote_a_l_ouverture`) —, comme la grille du coût
#: (``facteurs_depense.part_avec_decote``), et non à toutes ; et elle se prend
#: sans ce que les carrières qui partent à l'ouverture de leur statut, les
#: agents des IEG et de la conduite, y décotent déjà, la part de l'EIR les
#: comptant. Nées en 1955, les femmes d'une carrière de trente à quarante ans
#: ont leur durée dès 62 ans, les huit trimestres de chacun de leurs deux
#: enfants compris : leur jumelle partait au taux plein, et un peu plus de la
#: moitié seulement des jumelles de leur génération partaient décotées. Aux
#: générations où sa carrière ne peut pas décoter, une jumelle ne pèse plus
#: rien, celle qui part au taux plein portant tout le poids de la carrière
#: (:func:`parts_des_jumelles`). Une convention : une carrière peut décoter
#: quand elle le peut au salaire de son cas type, avant sa déclinaison par le
#: rang ; ses déclinaisons du bas, fragmentées ou à temps partiel, qui
#: valident moins, ne décotent pas quand elle ne le peut pas.
DECOTE_DES_CARRIERES_QUI_LE_PEUVENT = True

#: La trente et unième version (action 138, étape 14, le 28 octobre 2026) : les
#: départs avec décote se prennent aussi entre l'âge légal et l'âge
#: d'annulation de la décote, comme ceux des nés en 1953
#: (:func:`attentes_des_decotes`), et non tous à l'âge légal. Étalées jusqu'à
#: 60 ans (:data:`AGE_FIN_ETALEMENT`), les carrières incomplètes ne valident
#: plus rien à l'âge légal : leur jumelle qui décote y partait, celle du taux
#: plein à l'âge d'annulation, jamais entre les deux ; les femmes de la
#: génération 1955 y partaient pour 8,5 %, quand l'EIR compte 26,7 % des nées
#: en 1953 entre les deux âges, dont 20,4 % avec une décote, et pour 53,9 % à
#: l'âge légal (37,5). La jumelle qui décote se décline en trois : la part des
#: départs avec décote des nés en 1953 que l'EIR range à l'âge légal y part, à
#: l'ouverture du droit — la moitié chez les femmes, un gros tiers chez les
#: hommes — ; le reste attend après lui, en deux attentes, un an et deux mois
#: et trois ans et cinq mois chez les femmes. Deux conventions : la jumelle qui
#: attend ne valide rien de plus, sa carrière restant celle de sa tranche, si
#: bien que sa décote ne baisse que de l'âge, quand la durée ne la borne pas ;
#: les attentes sont celles des nés en 1953 à toutes les générations, comptées
#: de l'âge légal de chacune, et ne dépendent pas du rang.
DECOTE_ENTRE_LES_DEUX_AGES = True

#: Le témoin des tables de l'EACR, dont la table H dit la part décotée des
#: liquidants de la Cnav (:func:`decote_du_flux`).
TEMOIN_EACR = RACINE / "tests" / "temoins" / "drees_eacr_tables_2026.json"

#: La dix-neuvième version (action 138, étape 14, le 18 octobre 2026) : une part
#: des carrières qui ont le taux plein part après lui, avec une surcote — 14,2 %
#: des femmes et 14,5 % des hommes nés en 1953 (``departs_generations.csv``),
#: quand la population partait toute au taux plein ou avant lui. Chaque carrière
#: du salariat et des non-salariés de trente années validées et plus, qui part
#: au taux plein (:func:`peut_surcoter`), se décline : la part de son sexe que
#: l'EIR voit surcoter parmi les carrières complètes des nés en 1953 — 21,7 %
#: des femmes, 17,7 % des hommes (:func:`parts_avec_surcote`) — attend après
#: l'âge légal de sa génération ce qu'attendent leurs départs avec surcote, en
#: trois attentes (:func:`attentes_des_surcotes`) ; le reste part au taux plein.
#: Quatre conventions : l'attente se compte de l'âge légal, au milieu de chaque
#: âge de liquidation, et jamais avant le taux plein ; les âges se regroupent en
#: trois attentes (:data:`PREMIERES_ANNEES`), chaque attente de plus multipliant
#: les carrières que la page pèse une à une, à un coût qui croît comme leur
#: carré ; la part ne dépend ni du rang de salaire, ni de la génération, sinon
#: qu'aucune n'attend avant 2004 (:data:`ANNEE_DE_LA_SURCOTE`) ; les carrières
#: statutaires gardent leur départ, quand l'État surcote deux fois plus que la
#: Cnav (38,9 % de ses liquidants civils de 2024, pour 18,9 % ; EACR, table H).
DEPARTS_AVEC_SURCOTE = True

#: L'année où naît la surcote du régime général (L. 351-1-2 du code de la
#: sécurité sociale ; D. 351-1-4 dans sa version de 2004, fiche
#: ``surcote_regime_general``) : une génération qui atteint son âge légal avant
#: elle n'attend pas, la loi ne servant rien à l'attente.
ANNEE_DE_LA_SURCOTE = 2004

#: La génération de l'EIR dont les départs avec surcote donnent leur part et
#: leurs attentes à la population : les nés en 1953, les plus récents que
#: l'enquête voie presque tous partis.
GENERATION_DES_SURCOTES = 1953

#: Les tranches de durée des carrières qui peuvent surcoter : celles de trente
#: années validées et plus, que les enfants complètent, chez les femmes, dès
#: l'âge légal.
TRANCHES_DES_SURCOTES = ("30_40", "40_plus")

#: Les trois attentes d'un départ avec surcote réunissent les âges de
#: liquidation des :data:`PREMIERES_ANNEES` premières années de l'âge légal,
#: ceux d'avant l'année où s'annule la décote, et ceux de cette année-là et
#: d'après : l'âge d'annulation, où beaucoup partent, ne se partage pas entre
#: deux attentes, ni ne reçoit celle des départs d'avant lui.
PREMIERES_ANNEES = 2

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
    d'interruption comptées de lui ; ``services`` — paires ``(génération,
    années)`` triées — la fait précéder d'autant d'années de service national
    (:data:`SERVICE_AVANT_LE_PREMIER_TRIMESTRE`) ; ``natures`` — paires
    ``(génération, (service, maladie))`` triées — fait de ses premières années
    de chômage indemnisé autant d'années de service national, puis de maladie
    (:data:`NATURES_SELON_LA_GENERATION`) ; ``annees_par_nature`` — paires
    ``(génération, (service, maladie, avpf, chômage))`` triées — refait le bloc
    de ses années assimilées de ces années-là (:data:`NATURES_A_LEUR_PART`,
    :func:`refaire_le_bloc`).
    """

    avant: tuple[tuple[str, float], ...] = ()
    niveaux: tuple[tuple[int, float], ...] = ()
    ages_partiel: tuple[float, ...] = ()
    quotites: tuple[tuple[int, float], ...] = ()
    plancher_smic: bool = False
    persistante: bool = False
    volumes: tuple[tuple[int, float], ...] = ()
    entrees: tuple[tuple[int, float], ...] = ()
    services: tuple[tuple[int, float], ...] = ()
    natures: tuple[tuple[int, tuple[int, int]], ...] = ()
    annees_par_nature: tuple[tuple[int, tuple[int, int, int, int]], ...] = ()
    tranche_de_base: tuple = ()
    cibles: tuple[tuple[int, float], ...] = ()
    #: Les années qu'un départ avec surcote, ou avec décote, attend après l'âge
    #: légal de sa génération (:data:`DEPARTS_AVEC_SURCOTE`,
    #: :data:`DECOTE_ENTRE_LES_DEUX_AGES`), et ces âges légaux, paires
    #: ``(génération, âge)`` triées.
    attente: float = 0.0
    legaux: tuple[tuple[int, float], ...] = ()

    def age_liquidation_pour(self, simulateur: Simulateur, generation: int,
                             variante: str = "droit") -> float:
        """L'âge que le pilote fixe, ou, pour un départ qui attend,
        :attr:`attente` années après l'âge légal de sa génération, jamais
        avant celui que le pilote fixe : un départ avec décote, qui part à
        l'ouverture du droit, à toute génération ; un départ avec surcote, au
        taux plein, seulement si la génération atteint son âge légal depuis
        que la surcote existe (:data:`ANNEE_DE_LA_SURCOTE`)."""
        age = super().age_liquidation_pour(simulateur, generation, variante)
        if not self.attente or variante == "absolu":
            return age
        legal = _par_generation(self.legaux, generation, 0.0)
        if self.regle_liquidation == "taux_plein" and generation + legal < ANNEE_DE_LA_SURCOTE:
            return age
        return max(age, legal + self.attente)

    def niveau_de(self, generation: int) -> float:
        """Le niveau de salaire de cette génération."""
        return _par_generation(self.niveaux, generation, self.niveau_salaire)

    def decalages_de(self, generation: int) -> tuple[tuple[int, str], ...]:
        """Les interruptions de cette génération : celles du cas type, ou, pour
        une carrière incomplète dont la durée suit la génération (``cibles``,
        :data:`DUREE_DES_FEMMES_SELON_LA_GENERATION`), celles de ses années
        validées de cette génération, comptées de son entrée
        (:func:`decalages_de_tranche`)."""
        if not self.cibles:
            return self.interruptions_relatives
        base, duree, assimilee, etalee = self.tranche_de_base
        cible = int(round(_par_generation(self.cibles, generation, 0.0)))
        return decalages_de_tranche(base, duree, cible, assimilee, etalee,
                                    self.debut_de(generation))

    def debut_de(self, generation: int) -> float:
        """L'âge d'entrée de cette génération : celui des ``entrees``, paires
        ``(génération, âge)`` triées (:data:`ENTREE_SELON_LA_GENERATION`), ou
        celui du cas type."""
        return _par_generation(self.entrees, generation, self.age_debut)

    def service_de(self, generation: int) -> int:
        """Les années de service national que cette génération fait avant son
        entrée (:data:`SERVICE_AVANT_LE_PREMIER_TRIMESTRE`) ; zéro sans elles."""
        return int(round(_par_generation(self.services, generation, 0.0)))

    def natures_de(self, generation: int) -> tuple[int, int]:
        """Les années de service national et de maladie que cette génération
        compte parmi ses années assimilées (:data:`NATURES_SELON_LA_GENERATION`) ;
        aucune sans elles."""
        return _par_generation(self.natures, generation, (0, 0))

    def annees_par_nature_de(self, generation: int) -> tuple[int, int, int, int] | None:
        """Les années de service national, de maladie, d'AVPF et de chômage que
        cette génération compte dans son bloc d'années assimilées
        (:data:`NATURES_A_LEUR_PART`) ; ``None`` sans elles, le bloc tel quel."""
        return _par_generation(self.annees_par_nature, generation, None)

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
                or self.entrees or self.services or self.natures or self.annees_par_nature
                or self.cibles):
            return super()._carriere(simulateur, generation, age_liquidation)
        entree = self.debut_de(generation)
        interruptions = {
            int(generation + entree + decalage): motif
            for decalage, motif in self.decalages_de(generation)
        }
        par_nature = self.annees_par_nature_de(generation)
        if par_nature is not None:
            refaire_le_bloc(interruptions, par_nature)
        en_service, en_maladie = self.natures_de(generation)
        chomage = sorted(annee for annee, motif in interruptions.items()
                         if motif == "chomage_indemnise")
        for annee in chomage[:en_service]:
            interruptions[annee] = "service_militaire"
        for annee in chomage[en_service:en_service + en_maladie]:
            interruptions[annee] = "maladie"
        service = self.service_de(generation)
        for annee in range(int(generation + entree) - service, int(generation + entree)):
            interruptions[annee] = "service_militaire"
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
        if service:
            # Le service se fait sous le premier métier, les années d'avant l'entrée.
            metiers[0] = replace(metiers[0], age_debut=entree - service)
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
    #: Les années qu'elle attend après l'âge légal, avec une surcote
    #: (:data:`DEPARTS_AVEC_SURCOTE`) ; zéro sans elle.
    surcote: float = 0.0
    #: Ce que chaque génération donne à son poids, paires ``(génération,
    #: part)`` triées : la part des départs avec décote de sa génération,
    #: rapportée à celle que son poids porte (:data:`DECOTE_SELON_LA_GENERATION`) ;
    #: vide, une partout. La mesure en pèse chaque cohorte, à son année de
    #: naissance (:meth:`GrilleEnTetes.part_de`).
    parts_des_generations: tuple[tuple[int, float], ...] = ()

    def fois(self, part: float, **changements) -> "Variante":
        """La même, pour ``part`` de son poids, avec ces changements."""
        return replace(self, retraites=_echelle(self.retraites, part),
                       cotisants=_echelle(self.cotisants, part), **changements)

    def part_de_la_generation(self, generation: int) -> float:
        """Ce que la génération ``generation`` donne à son poids : une, sans
        :attr:`parts_des_generations`."""
        return _par_generation(self.parts_des_generations, generation, 1.0)


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
    bandes = BandesDesQuintiles(quintiles, sexe)
    tableau = {}
    for tranche, _ in TRANCHES:
        masses = bandes.au_premier(bandes.masses(tranche))
        tableau[tranche] = {nom: bandes.sur_la_classe(masses, bas, fin)
                            for nom, bas, fin in bandes.classes}
    return tableau


class BandesDesQuintiles:
    """Les quintiles de la pension en équivalent carrière complète d'un sexe
    lus comme des bandes de ses rangs (:func:`association_rang_duree`) :
    ``parts``, la part de chaque quintile parmi les retraités du sexe ;
    ``au_minimum``, celle de ses retraités au minimum, que
    :data:`MINIMUM_AU_PREMIER_QUINTILE` fait passer dans la bande du premier,
    nulle pour celui-ci ; ``bandes``, la bande de rangs de chacun ;
    ``classes``, celle de chaque classe de centiles, ``(nom, bas, fin)``."""

    def __init__(self, quintiles: dict, sexe: str) -> None:
        self.quintiles, self.sexe = quintiles, sexe
        effectifs = [quintiles[(q, "effectifs", sexe)] for q in QUINTILES_EQCC]
        total = somme_ordonnee(effectifs)
        self.parts = [effectif / total for effectif in effectifs]
        self.au_minimum = [quintiles[(q, "part_minimum_pension_regime_principal", sexe)] / 100.0
                           if MINIMUM_AU_PREMIER_QUINTILE and rang > 0 else 0.0
                           for rang, q in enumerate(QUINTILES_EQCC)]
        self.bandes, debut = [], 0.0
        for largeur in self.au_premier(self.parts):
            self.bandes.append((debut, debut + largeur))
            debut += largeur
        self.classes, debut = [], 0.0
        for nom, part in CENTILES:
            self.classes.append((nom, debut, debut + part))
            debut += part

    def au_premier(self, parts: list[float]) -> list[float]:
        """Des parts de quintile, celles au minimum passées au premier."""
        restes = [part * (1.0 - minimum) for part, minimum in zip(parts, self.au_minimum)]
        restes[0] += somme_ordonnee(part * minimum
                                    for part, minimum in zip(parts, self.au_minimum))
        return restes

    def masses(self, tranche: str) -> list[float]:
        """La masse de la tranche de durée dans chaque quintile, en parts des
        retraités du sexe."""
        return [part * self.quintiles[(q, f"part_duree_validee_hors_majoration_{tranche}",
                                       self.sexe)] / 100.0
                for q, part in zip(QUINTILES_EQCC, self.parts)]

    def sur_la_classe(self, masses: list[float], bas: float, fin: float) -> float:
        """Ce que la classe des rangs de ``bas`` à ``fin`` reçoit de masses
        réparties chacune sur sa bande."""
        return somme_ordonnee(masse * max(0.0, min(fin, haut) - max(bas, plancher))
                              / (haut - plancher)
                              for masse, (plancher, haut) in zip(masses, self.bandes))


def parts_assimilees_des_classes(quintiles: dict, sexe: str, tranche: str
                                 ) -> dict[str, float]:
    """La part assimilée de la durée validée hors majorations de chaque classe
    de centiles d'une tranche de durée, pour un sexe
    (:data:`ASSIMILEES_SELON_LE_RANG`) : celle des bandes de quintiles que ses
    rangs couvrent (:class:`BandesDesQuintiles`), chacune pesée par la masse
    de la tranche qui y tombe. Celle d'un quintile est la part de sa durée
    validée hors majorations qui n'est pas cotisée ; ses retraités au minimum
    la portent dans la bande du premier. Une classe où la tranche n'a pas de
    masse prend la part de la tranche."""
    bandes = BandesDesQuintiles(quintiles, sexe)
    assimilees = [1.0 - quintiles[(q, "duree_cotisee", sexe)]
                  / quintiles[(q, "duree_validee_hors_majoration", sexe)]
                  for q in QUINTILES_EQCC]
    masses = bandes.masses(tranche)
    dans_les_bandes = bandes.au_premier(masses)
    portees = bandes.au_premier([masse * part for masse, part in zip(masses, assimilees)])
    moyenne = somme_ordonnee(portees) / somme_ordonnee(dans_les_bandes)
    sortie = {}
    for nom, bas, fin in bandes.classes:
        masse = bandes.sur_la_classe(dans_les_bandes, bas, fin)
        sortie[nom] = bandes.sur_la_classe(portees, bas, fin) / masse if masse else moyenne
    return sortie


def assimilees_selon_le_rang(variantes: list[Variante], quintiles: dict) -> list[Variante]:
    """Chaque carrière d'une tranche de durée à la part assimilée de sa classe
    de centiles (:func:`parts_assimilees_des_classes`), ses années validées
    redécoupées comme à la tranche (:func:`decalages_de_tranche`), celles d'une
    femme qui suit sa génération comprises ; les autres variantes telles
    quelles (:data:`ASSIMILEES_SELON_LE_RANG`)."""
    noms = {nom for nom, _ in CENTILES}
    parts: dict[tuple[str, str], dict[str, float]] = {}
    sortie = []
    for v in variantes:
        classe = next((m for m in v.cas.code.split("~") if m in noms), None)
        if v.tranche is None or classe is None:
            sortie.append(v)
            continue
        if (v.cas.sexe, v.tranche) not in parts:
            parts[(v.cas.sexe, v.tranche)] = parts_assimilees_des_classes(
                quintiles, v.cas.sexe, v.tranche)
        part = parts[(v.cas.sexe, v.tranche)][classe]
        base, duree, _, etalee = v.cas.tranche_de_base
        cible = None if v.tranche == "40_plus" else v.duree
        cas = replace(v.cas, tranche_de_base=(base, duree, part, etalee),
                      interruptions_relatives=decalages_de_tranche(
                          base, duree, cible, part, etalee, v.cas.age_debut))
        sortie.append(replace(v, cas=cas, assimilees=int(round(part * v.duree))))
    return sortie


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


def premiers_trimestres(racine: Path, trimestre: str = "cotise"
                        ) -> dict[str, dict[int, dict[int, float]]]:
    """La part des affiliés d'avant 23 ans qui ont cotisé un trimestre à la
    fin de l'année de chaque âge, de 16 à 23 ans, génération par génération de
    l'échantillon interrégimes de cotisants, sexe par sexe :
    ``{sexe: {génération: {âge: part}}}``, en pour cent
    (``premier_trimestre.csv``, :data:`ENTREE_AU_PREMIER_TRIMESTRE`) ; ou,
    ``trimestre`` valant ``"valide"``, qui en ont validé un, de quelque nature
    qu'il soit (:data:`SERVICE_AVANT_LE_PREMIER_TRIMESTRE`)."""
    sortie: dict[str, dict[int, dict[int, float]]] = {}
    for ligne in _lire_macro(racine, "premier_trimestre.csv"):
        if ligne["trimestre"] == trimestre:
            sortie.setdefault(ligne["sexe"], {}).setdefault(
                int(ligne["generation"]), {})[int(ligne["age"])] = float(ligne["part"])
    return sortie


def age_du_premier_trimestre(parts: dict[int, dict[int, float]], generation: int,
                             rang: float) -> int:
    """L'âge où ``generation`` cotise le premier trimestre de ce ``rang``,
    entre zéro et un : le premier âge où la part de ses affiliés d'avant 23 ans
    qui ont cotisé un trimestre, rapportée à celle du dernier âge, l'atteint.
    Entre deux générations de l'échantillon (:func:`premiers_trimestres`), les
    parts s'interpolent ; avant la première et après la dernière, elles sont
    les leurs."""
    lues = sorted(parts)
    if generation <= lues[0] or generation >= lues[-1]:
        par_age = parts[lues[0] if generation <= lues[0] else lues[-1]]
    else:
        bas = max(g for g in lues if g <= generation)
        haut = min(g for g in lues if g >= generation)
        poids = (generation - bas) / (haut - bas) if haut > bas else 0.0
        par_age = {age: (1.0 - poids) * part + poids * parts[haut][age]
                   for age, part in parts[bas].items()}
    ages = sorted(par_age)
    return next(age for age in ages if par_age[age] >= rang * par_age[ages[-1]])


def classes_d_entree(regle: tuple[tuple[int, float], ...], parts: dict[int, dict[int, float]],
                     valides: dict[int, dict[int, float]] | None = None,
                     au_plus_tard: float | None = None
                     ) -> list[tuple[int, tuple[tuple[int, float], ...],
                                     tuple[tuple[int, float], ...], float]]:
    """Les cinquièmes d'une carrière pleine (:data:`ENTREE_AU_PREMIER_TRIMESTRE`),
    ``(rang, entrées, services, poids)`` : chacun entre, génération par
    génération, à l'âge où sa génération cotise le premier trimestre du milieu
    de son cinquième (:func:`age_du_premier_trimestre`), ou à celui de
    ``regle`` s'il vient plus tard, et à ``au_plus_tard`` au plus tard s'il est
    donné. Sous ``valides``, la part des affiliés qui ont validé un trimestre,
    il fait son service national les années d'avant, depuis l'âge où sa
    génération valide ce premier trimestre, jamais avant celui de ``regle``
    (:data:`SERVICE_AVANT_LE_PREMIER_TRIMESTRE`) ; sans elles, ``services`` est
    vide. Ceux qui entrent au même âge et servent les mêmes années à chaque
    génération n'en font qu'un, sous le rang du premier."""
    borne = math.inf if au_plus_tard is None else au_plus_tard
    classes: dict[tuple, list] = {}
    for rang in range(CLASSES_D_ENTREE):
        milieu = (2 * rang + 1) / (2 * CLASSES_D_ENTREE)
        entrees = tuple((generation, min(borne, max(age, float(age_du_premier_trimestre(
            parts, generation, milieu))))) for generation, age in regle)
        services: tuple[tuple[int, float], ...] = ()
        if valides is not None:
            services = tuple(
                (generation, max(0.0, entree - max(age, float(age_du_premier_trimestre(
                    valides, generation, milieu)))))
                for (generation, age), (_, entree) in zip(regle, entrees))
            if not any(annees for _, annees in services):
                services = ()
        classes.setdefault((entrees, services), [rang + 1, 0.0])[1] += 1.0 / CLASSES_D_ENTREE
    return [(premier, entrees, services, poids)
            for (entrees, services), (premier, poids) in classes.items()]


def natures_assimilees(racine: Path, sexe: str) -> dict[str, dict[int, tuple[float, float]]]:
    """La part des affiliés d'avant 23 ans de ce sexe qui ont validé un
    trimestre de chaque nature, en pour cent, et le cumul de ces trimestres par
    affilié, génération par génération de l'échantillon interrégimes de
    cotisants : ``{nature: {génération: (part, cumul)}}``
    (``natures_assimilees.csv``, :data:`NATURES_SELON_LA_GENERATION`). Le
    service national, fait au dernier âge où l'échantillon voit chaque
    génération, se lit à cet âge ; la maladie, le chômage et l'AVPF, qui
    croissent avec l'âge, à 60 ans seulement (:data:`NATURES_LUES_A_60_ANS`).
    Ni ce que l'échantillon voit après 60 ans, ni les totaux des trimestres
    validés et cotisés ne se lisent (:data:`NATURES_DE_L_ECHANTILLON`)."""
    lues: dict[str, dict[int, dict[str, float]]] = {}
    for ligne in _lire_macro(racine, "natures_assimilees.csv"):
        if (ligne["sexe"] != sexe or ligne["nature"] not in NATURES_DE_L_ECHANTILLON
                or int(ligne["age"]) > 60
                or (ligne["nature"] in NATURES_LUES_A_60_ANS and ligne["age"] != "60")):
            continue
        lues.setdefault(ligne["nature"], {}).setdefault(int(ligne["generation"]), {})[
            ligne["indicateur"]] = float(ligne["valeur"])
    return {nature: {generation: (valeurs["part"], valeurs["cumul"])
                     for generation, valeurs in par_generation.items()}
            for nature, par_generation in lues.items()}


def _interpolee(valeurs: dict[int, float], generation: int) -> float:
    """La valeur de ``generation`` parmi celles des générations de
    l'échantillon : interpolée entre deux d'entre elles ; avant la première et
    après la dernière, la leur."""
    lues = sorted(valeurs)
    if generation <= lues[0] or generation >= lues[-1]:
        return valeurs[lues[0] if generation <= lues[0] else lues[-1]]
    bas = max(g for g in lues if g <= generation)
    haut = min(g for g in lues if g >= generation)
    poids = (generation - bas) / (haut - bas) if haut > bas else 0.0
    return (1.0 - poids) * valeurs[bas] + poids * valeurs[haut]


def part_et_duree(lues: dict[int, tuple[float, float]], generation: int
                  ) -> tuple[float, float]:
    """La part des affiliés de ``generation`` qui ont validé un trimestre d'une
    nature (:func:`natures_assimilees`), en fraction, et les années qu'en
    compte chacun d'eux : le cumul par affilié sur la part, en années de quatre
    trimestres. La part et le cumul s'interpolent entre deux générations de
    l'échantillon ; avant la première et après la dernière, ce sont les
    leurs."""
    part = _interpolee({g: p for g, (p, _) in lues.items()}, generation) / 100.0
    cumul = _interpolee({g: c for g, (_, c) in lues.items()}, generation)
    return part, (cumul / part / 4.0 if part > 0.0 else 0.0)


def part_et_annees(lues: dict[int, tuple[float, float]], generation: int
                   ) -> tuple[float, int]:
    """La part et les années de :func:`part_et_duree`, les années arrondies."""
    part, duree = part_et_duree(lues, generation)
    return part, int(round(duree))


def classes_de_nature(classes: list[tuple[int, tuple[tuple[int, float], ...],
                                          tuple[tuple[int, float], ...], float]],
                      parts: dict[str, dict[int, tuple[float, float]]],
                      assimilees: int | None = None
                      ) -> list[tuple[int, tuple, tuple, int, tuple, float]]:
    """Les cinquièmes d'une carrière pleine (:func:`classes_d_entree`), chacun
    décliné en :data:`CLASSES_DE_NATURE` classes de poids égal, ``(rang,
    entrées, services, nature, natures, poids)`` : ``natures``, paires
    ``(génération, (service, maladie))`` triées, dit les années de service
    national et de maladie que la classe compte parmi ses années assimilées,
    génération par génération (:data:`NATURES_SELON_LA_GENERATION`). Une classe
    sert quand le milieu de son rang passe sous la part des affiliés de sa
    génération qui ont servi (:func:`part_et_annees`), moins celle des
    cinquièmes qui servent avant d'entrer, rapportée aux autres, et dans ceux-ci
    seulement ; elle est malade quand il passe au-dessus de la part des autres.
    Les classes qui ont les mêmes natures à chaque génération n'en font qu'une,
    sous le rang de la première, ``nature`` ; celle qui n'en a aucune,
    ``natures`` vide, a le rang zéro, et garde le code de son cinquième. Avec
    ``assimilees``, les années assimilées de la carrière, les classes sont
    celles de :data:`NATURES_A_LEUR_PART` (:func:`natures_a_leur_part`)."""
    generations = [generation for generation, _ in classes[0][1]]
    servent = {generation: somme_ordonnee(poids for _, _, services, poids in classes
                                          if _par_generation(services, generation, 0.0))
               for generation in generations}
    service = {g: part_et_annees(parts["service_national"], g) for g in generations}
    if assimilees is not None:
        return natures_a_leur_part(classes, parts, assimilees, servent, service)
    maladie = {g: part_et_annees(parts["maladie"], g) for g in generations}
    sortie = []
    for rang, entrees, services, poids in classes:
        natures: dict[tuple, list] = {}
        for nature in range(CLASSES_DE_NATURE):
            milieu = (2 * nature + 1) / (2 * CLASSES_DE_NATURE)
            annees = []
            for generation in generations:
                (servis, en_service), (malades, en_maladie) = service[generation], maladie[generation]
                reste = ((servis - servent[generation]) / (1.0 - servent[generation])
                         if servent[generation] < 1.0 else 0.0)
                sert = milieu < reste and not _par_generation(services, generation, 0.0)
                annees.append((generation, (en_service if sert else 0,
                                            en_maladie if milieu > 1.0 - malades else 0)))
            cle = tuple(annees) if any(any(paire) for _, paire in annees) else ()
            natures.setdefault(cle, [nature + 1, 0.0])[1] += poids / CLASSES_DE_NATURE
        sortie.extend((rang, entrees, services, premier if cle else 0, cle, part)
                      for cle, (premier, part) in natures.items())
    return sortie


def rangs_de_nature() -> list[tuple[float, float]]:
    """Le milieu du rang de chaque classe de nature d'un cinquième, ``(rang du
    service, de l'AVPF et du chômage, rang de la maladie)`` : les
    :data:`CLASSES_DE_NATURE` classes d'un seul rang, le même ; sous
    :data:`MALADIE_INDEPENDANTE`, chacune déclinée en autant de classes de la
    maladie, classe par classe."""
    milieux = [(2 * nature + 1) / (2 * CLASSES_DE_NATURE) for nature in range(CLASSES_DE_NATURE)]
    if not MALADIE_INDEPENDANTE:
        return [(milieu, milieu) for milieu in milieux]
    return [(milieu, maladie) for milieu in milieux for maladie in milieux]


def natures_a_leur_part(classes: list[tuple[int, tuple[tuple[int, float], ...],
                                            tuple[tuple[int, float], ...], float]],
                        parts: dict[str, dict[int, tuple[float, float]]], assimilees: int,
                        servent: dict[int, float], service: dict[int, tuple[float, int]]
                        ) -> list[tuple[int, tuple, tuple, int, tuple, float]]:
    """Les classes de nature de :func:`classes_de_nature` sous
    :data:`NATURES_A_LEUR_PART` : ``natures``, paires ``(génération, (service,
    maladie, avpf, chômage))`` triées, dit les années de chaque nature que la
    classe compte, génération par génération ; leur somme est son bloc
    d'années assimilées (:func:`refaire_le_bloc`).

    Le service se donne comme sous :func:`classes_de_nature`, une classe
    servant son année ; une classe a de l'AVPF quand le milieu de son rang passe
    sous la part des affiliés de sa génération qui en ont, du chômage ou de la
    maladie quand il passe au-dessus de la part des autres — celui de la
    maladie, son propre rang sous :data:`MALADIE_INDEPENDANTE`
    (:func:`rangs_de_nature`). Chacune de ces natures y compte les années qu'a
    chacun de ceux qui en ont (:func:`part_et_duree`), arrondies, une au
    moins ; ``assimilees`` années par classe en sont le plafond : quand les
    classes du cinquième en demandent plus, ce que le service leur laisse se
    partage entre elles à proportion. Une classe sans nature n'en compte
    aucune. Les classes qui ont les mêmes natures à chaque génération n'en font
    qu'une, sous le rang de la première ; celle qui porte le milieu du rang du
    cinquième a le rang zéro, et garde le code de son cinquième."""
    generations = list(servent)
    lues = {generation: {nature: part_et_duree(parts[nature], generation)
                         for nature in ("maladie", "avpf", "chomage") if nature in parts}
            for generation in generations}
    rangs = rangs_de_nature()
    milieu_du_rang = len(rangs) // 2
    sortie = []
    for rang, entrees, services, poids in classes:
        par_classe: list[list] = [[] for _ in rangs]
        for generation in generations:
            servis, en_service = service[generation]
            reste = ((servis - servent[generation]) / (1.0 - servent[generation])
                     if servent[generation] < 1.0 else 0.0)
            avant = bool(_par_generation(services, generation, 0.0))
            demandes = []
            for milieu, de_la_maladie in rangs:
                sert = en_service if milieu < reste and not avant else 0
                siennes = {nom: duree for nom, (part, duree) in lues[generation].items()
                           if duree > 0.0
                           and (milieu < part if nom == "avpf"
                                else (de_la_maladie if nom == "maladie" else milieu)
                                > 1.0 - part)}
                demandes.append((sert, siennes))
            masse = len(rangs) * assimilees - somme_ordonnee(sert for sert, _ in demandes)
            total = somme_ordonnee(duree for _, siennes in demandes
                                   for duree in siennes.values())
            echelle = min(1.0, max(0.0, masse) / total) if total > 0.0 else 0.0
            for nature, (sert, siennes) in enumerate(demandes):
                annees = {nom: max(1, int(round(echelle * duree)))
                          for nom, duree in siennes.items()}
                par_classe[nature].append((generation, (
                    sert, annees.get("maladie", 0), annees.get("avpf", 0),
                    annees.get("chomage", 0))))
        groupes: dict[tuple, list] = {}
        for nature, annees in enumerate(par_classe):
            groupe = groupes.setdefault(tuple(annees), [nature + 1, 0.0, False])
            groupe[1] += poids / len(rangs)
            groupe[2] = groupe[2] or nature == milieu_du_rang
        sortie.extend((rang, entrees, services, 0 if du_milieu else premier, cle, part)
                      for cle, (premier, part, du_milieu) in groupes.items())
    return sortie


def masses_moyennes(variantes: list[Variante]) -> dict[str, float]:
    """La part assimilée moyenne des carrières pleines qui entrent selon leur
    génération, hors des départs avec surcote et des carrières incomplètes
    allongées (:data:`ALLONGEES_COMME_LES_PLEINES`), de chaque sexe de
    :data:`NATURES_SELON_LE_RANG` : celle de chaque carrière, que sa classe de
    centiles tient de l'EIR (:data:`ASSIMILEES_SELON_LE_RANG`), pesée par sa
    part de la Cnav, comme sous :func:`parts_des_tranches`."""
    masses: dict[str, list[float]] = {}
    for v in variantes:
        if (v.cas.sexe in NATURES_SELON_LE_RANG and v.cas.entrees and not v.cas.cibles
                and not v.surcote):
            somme = masses.setdefault(v.cas.sexe, [0.0, 0.0])
            somme[0] += v.retraites[0][1] * v.cas.tranche_de_base[2]
            somme[1] += v.retraites[0][1]
    return {sexe: masse / poids for sexe, (masse, poids) in masses.items()}


def natures_au_rang(parts: dict[str, dict[int, tuple[float, float]]], facteur: float
                    ) -> dict[str, dict[int, tuple[float, float]]]:
    """Les natures de l'échantillon (:func:`natures_assimilees`) à une classe
    de centiles dont la masse fait ``facteur`` fois la moyenne
    (:data:`NATURES_SELON_LE_RANG`) : la part et le cumul de la maladie, de
    l'AVPF et du chômage multipliés par lui, les années de chacun de ceux qui
    en ont restant les mêmes ; le service tel quel."""
    return {nature: ({generation: (part * facteur, cumul * facteur)
                      for generation, (part, cumul) in lues.items()}
                     if nature in NATURES_LUES_A_60_ANS else lues)
            for nature, lues in parts.items()}


def refaire_le_bloc(interruptions: dict[int, str], annees: tuple[int, int, int, int]) -> None:
    """Refait le bloc des années assimilées d'une carrière pleine
    (:data:`NATURES_A_LEUR_PART`) : ses années de chômage indemnisé, contiguës
    au milieu de la carrière, deviennent ``annees`` de service national, de
    maladie, d'AVPF et de chômage, dans cet ordre (:data:`MOTIFS_DES_NATURES`),
    centrées sur le même milieu ; celles qu'elles ne prennent pas sont
    cotisées. L'AVPF d'avant sa création (:data:`ANNEE_CREATION_AVPF`) reste du
    chômage."""
    bloc = sorted(annee for annee, motif in interruptions.items()
                  if motif == "chomage_indemnise")
    if not bloc:
        return
    for annee in bloc:
        del interruptions[annee]
    debut = bloc[0] + (len(bloc) - somme_ordonnee(annees)) // 2
    motifs = [motif for motif, nombre in zip(MOTIFS_DES_NATURES, annees) for _ in range(nombre)]
    for decalage, motif in enumerate(motifs):
        annee = debut + decalage
        if motif == "education_enfant" and annee < ANNEE_CREATION_AVPF:
            motif = "chomage_indemnise"
        interruptions[annee] = motif


def allongees_au_premier_trimestre(v: Variante, parts: dict[int, dict[int, float]]
                                   ) -> list[Variante]:
    """Une carrière incomplète allongée (:data:`ALLONGEES_COMME_LES_PLEINES`)
    en ses cinquièmes (:func:`classes_d_entree`) : chacun entre, génération par
    génération, à l'âge où sa génération cotise le premier trimestre de son
    rang s'il vient après celui de la carrière, jamais après l'entrée de son
    cas type, et valide d'autant moins d'années, sa carrière finissant où elle
    finissait ; il garde sa part assimilée. Le premier cinquième garde son
    code, les autres prennent leur rang, « ~entree4 »."""
    sortie = []
    for rang, entrees, _, poids in classes_d_entree(v.cas.entrees, parts,
                                                    au_plus_tard=float(v.cas.age_debut)):
        cibles = tuple((generation, cible - (siennes - entree))
                       for (generation, cible), (_, entree), (_, siennes)
                       in zip(v.cas.cibles, v.cas.entrees, entrees))
        code = v.cas.code if rang == 1 else f"{v.cas.code}~entree{rang}"
        sortie.append(v.fois(poids, cas=replace(v.cas, code=code, entrees=entrees,
                                                cibles=cibles)))
    return sortie


def entrees_au_premier_trimestre(variantes: list[Variante], racine: Path) -> list[Variante]:
    """Chaque carrière pleine qui entre selon sa génération, hors des départs
    avec surcote, en ses cinquièmes (:func:`classes_d_entree`), ceux des hommes
    précédés de leur service national sous
    :data:`SERVICE_AVANT_LE_PREMIER_TRIMESTRE`, et déclinés en leurs classes de
    nature sous :data:`NATURES_SELON_LA_GENERATION` (:func:`classes_de_nature`),
    ceux des deux sexes, à leurs années assimilées, sous
    :data:`NATURES_A_LEUR_PART`, et ceux des femmes à la part de leur rang sous
    :data:`NATURES_SELON_LE_RANG` (:func:`natures_au_rang`) : le premier
    cinquième garde son code, les autres prennent leur rang, « ~entree3 » ; la
    classe de nature de rang zéro garde celui de son cinquième, les autres
    prennent leur rang, « ~nature1 ». Une carrière incomplète allongée
    (:data:`ALLONGEES_COMME_LES_PLEINES`) se décline en ses seuls cinquièmes
    (:func:`allongees_au_premier_trimestre`) ; les autres variantes telles
    quelles."""
    parts = premiers_trimestres(racine)
    valides = ({"H": premiers_trimestres(racine, "valide")["H"]}
               if SERVICE_AVANT_LE_PREMIER_TRIMESTRE else {})
    a_leur_part = NATURES_SELON_LA_GENERATION and NATURES_A_LEUR_PART
    sexes = ("F", "H") if a_leur_part else ("H",) if NATURES_SELON_LA_GENERATION else ()
    parts_des_natures = {sexe: natures_assimilees(racine, sexe) for sexe in sexes}
    moyennes = masses_moyennes(variantes) if a_leur_part else {}
    classes: dict[tuple, list] = {}
    sortie = []
    for v in variantes:
        if not v.cas.entrees or v.surcote:
            sortie.append(v)
            continue
        if v.cas.cibles:
            sortie.extend(allongees_au_premier_trimestre(v, parts[v.cas.sexe]))
            continue
        assimilees = v.assimilees if a_leur_part else None
        facteur = (v.cas.tranche_de_base[2] / moyennes[v.cas.sexe]
                   if v.cas.sexe in moyennes else 1.0)
        cle = (v.cas.sexe, v.cas.entrees, assimilees, facteur)
        if cle not in classes:
            cinquiemes = classes_d_entree(v.cas.entrees, parts[v.cas.sexe],
                                          valides.get(v.cas.sexe))
            classes[cle] = (classes_de_nature(cinquiemes,
                                              natures_au_rang(parts_des_natures[v.cas.sexe],
                                                              facteur),
                                              assimilees)
                            if v.cas.sexe in parts_des_natures
                            else [(rang, entrees, services, 0, (), poids)
                                  for rang, entrees, services, poids in cinquiemes])
        champ = "natures" if assimilees is None else "annees_par_nature"
        for rang, entrees, services, nature, natures, poids in classes[cle]:
            code = v.cas.code if rang == 1 else f"{v.cas.code}~entree{rang}"
            if nature:
                code = f"{code}~nature{nature}"
            sortie.append(v.fois(poids, cas=replace(v.cas, code=code, entrees=entrees,
                                                    services=services, **{champ: natures})))
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
                     tranche_de_base=(cas.interruptions_relatives, duree, assimilee,
                                      etalee))
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
    types de la Cnav lui cèdent chacun sa part de la caisse, et l'inapte et
    l'ex-invalide de la grille du coût, leurs variantes, la leur ; le
    contractuel aussi sous :data:`CONTRACTUELS_AU_SALARIAT`."""
    retires = SALARIAT_PRIVE + (("contractuel_public",) if CONTRACTUELS_AU_SALARIAT else ())
    variantes = [v for v in reference() if cas_type_affiche(v.cas.code) not in retires]
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
                                    else cas.entrees))
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
        decotes = decotes_des_generations(racine) if DECOTE_SELON_LA_GENERATION else None
        ouvertures = (ouvertures_decotees(variantes, racine)
                      if decotes and DECOTE_DES_CARRIERES_QUI_LE_PEUVENT else None)
        attentes = (attentes_des_decotes(departs_publies(racine), racine)
                    if DECOTE_ENTRE_LES_DEUX_AGES else None)
        variantes = departs_avec_decote(variantes, effectifs, source, donnees.quintiles,
                                        decotes, ouvertures, attentes, ages_legaux(racine))
    variantes = salaires_population(variantes, donnees)
    if ASSIMILEES_SELON_LE_RANG:
        variantes = assimilees_selon_le_rang(variantes, donnees.quintiles)
    if DEPARTS_AVEC_SURCOTE:
        variantes = departs_avec_surcote(variantes, departs_publies(racine), racine)
    if ENTREE_AU_PREMIER_TRIMESTRE:
        variantes = entrees_au_premier_trimestre(variantes, racine)
    return variantes


def poids_des_incompletes(variantes: list[Variante], effectifs,
                          source: CaracteristiquesRetraites
                          ) -> dict[str, tuple[float, float]]:
    """Le poids de tous les retraités de chaque sexe, et celui de ses carrières
    incomplètes (:func:`incomplete`), l'année de l'enquête."""
    poids = poids_retraites(variantes, effectifs, source.millesime)
    return {sexe: (somme_ordonnee(p for v, p in zip(variantes, poids) if v.cas.sexe == sexe),
                   somme_ordonnee(p for v, p in zip(variantes, poids)
                                  if v.cas.sexe == sexe and incomplete(v)))
            for sexe in ("F", "H")}


def part_des_incompletes(decote: float, tous: float, incompletes: float) -> float:
    """La part des carrières incomplètes qui part avec une décote pour que ses
    départs pèsent ``decote`` parmi tous les retraités du sexe, ``tous`` et
    ``incompletes`` les poids de :func:`poids_des_incompletes` ; un au plus."""
    return min(1.0, decote * tous / incompletes) if incompletes else 0.0


def parts_avec_decote(variantes: list[Variante], effectifs,
                      source: CaracteristiquesRetraites,
                      quintiles: dict) -> dict[str, float]:
    """La part des carrières incomplètes de chaque sexe qui part avec une
    décote (:data:`DEPARTS_AVEC_DECOTE`) : celle des départs avec décote que
    l'EIR mesure à tous les retraités du sexe, divisée par le poids des
    carrières incomplètes parmi eux, l'année de l'enquête ; un au plus."""
    return {sexe: part_des_incompletes(quintiles[("ensemble", "part_decote", sexe)] / 100.0,
                                       tous, incompletes)
            for sexe, (tous, incompletes)
            in poids_des_incompletes(variantes, effectifs, source).items()}


def decote_du_flux(sexe: str) -> float:
    """La part des liquidants de la Cnav de :data:`ANNEE_DU_FLUX` partis avec
    une décote, ``sexe`` par sexe, parmi ceux partis au taux plein, avec une
    décote ou avec une surcote (EACR, table H,
    ``controle_eacr.conditions_publiees``) : 13,7 % des femmes, 13,0 % des
    hommes, que ``facteurs_depense.part_decotee_du_flux`` réunit."""
    temoin = json.loads(TEMOIN_EACR.read_text(encoding="utf-8"))
    return next(conditions.decote
                for conditions in conditions_publiees(temoin, ANNEE_DU_FLUX, sexe)
                if conditions.caisse == CAISSE_DU_FLUX and conditions.champ == "flux")


def decotes_des_generations(racine: Path) -> dict[str, tuple[tuple[int, float], ...]]:
    """La part des départs avec décote de chaque génération parmi tous ses
    retraités, sexe par sexe, en paires ``(génération, part)`` triées
    (:data:`DECOTE_SELON_LA_GENERATION`) : celle que l'EIR compte aux nés en
    1950 et en 1953 (``departs_generations.csv``), en droite ligne entre eux ;
    celle des liquidants de la Cnav de :data:`ANNEE_DU_FLUX`
    (:func:`decote_du_flux`) depuis la génération :data:`GENERATION_DU_FLUX`,
    en droite ligne depuis 1953, comme la grille du coût
    (``facteurs_depense.part_decotee_de_la_generation``) ; avant 1950, celle
    qui donne aux générations que l'enquête de 2020 voit toutes parties,
    jusqu'à celle de 1953, chacune pesée de son effectif INSEE de 2020, la part
    que l'EIR mesure aux résidents (``part_decote`` de
    ``quintiles_eqcc_residents.csv``)."""
    publies = departs_publies(racine)
    residents = quintiles_eqcc(racine, residents=True)
    premiere, derniere = min(ENQUETES_DES_DEPARTS), GENERATION_DES_DECOTES
    annee = ENQUETES_DES_DEPARTS[derniere]
    pyramide = Population(racine)
    recentes = {generation: pyramide.effectif(annee - generation, annee)
                for generation in range(premiere, derniere + 1)}
    anciennes = pyramide.effectif_tranche(annee - premiere + 1, pyramide.age_maximal, annee)
    sortie = {}
    for sexe in ("F", "H"):
        de_la_premiere, de_la_derniere = (
            publies[(generation, "condition", "decote", sexe, "part")] / 100.0
            for generation in (premiere, derniere))
        du_flux = decote_du_flux(sexe)

        def part(generation: int) -> float:
            if generation >= derniere:
                return part_decotee_de_la_generation(generation, de_la_derniere, du_flux)
            return de_la_premiere + ((de_la_derniere - de_la_premiere)
                                     * (generation - premiere) / (derniere - premiere))

        stock = residents[("ensemble", "part_decote", sexe)] / 100.0
        avant = (stock * (anciennes + somme_ordonnee(recentes.values()))
                 - somme_ordonnee(effectif * part(generation)
                                  for generation, effectif in recentes.items())) / anciennes
        sortie[sexe] = ((premiere - 1, avant),) + tuple(
            (generation, part(generation))
            for generation in range(premiere, GENERATION_DU_FLUX + 1))
    return sortie


def decote_a_l_ouverture(simulateur: Simulateur, cas: CasType, generation: int) -> bool:
    """Vrai si ce cas type part, ou partirait, avec une décote à l'ouverture
    de son droit (:data:`DECOTE_DES_CARRIERES_QUI_LE_PEUVENT`). Sous la règle
    ``taux_plein``, quand le droit de sa génération l'ouvre avant l'âge de son
    taux plein, que le pilote fixe : le critère d'âge de :func:`avec_decote`,
    sans le taux, que seule la liquidation dirait, comme la grille du coût
    (``facteurs_depense.dates_a_l_age_legal``). Sous la règle ``ouverture``,
    celle des agents qui partent à l'ouverture de leur statut, quand ils y
    prennent un taux plus bas que celui de leur taux plein
    (:func:`avec_decote`) : l'agent de conduite né en 1958 part à cinquante ans
    au taux de 75 %."""
    if cas.regle_liquidation == "ouverture":
        depart = simulateur.echeancier(cas.construire(simulateur, generation)).au_depart
        return avec_decote(simulateur, cas, generation, depart.taux_liquidation)
    ouverte = replace(cas, regle_liquidation="ouverture")
    return (ouverte.age_liquidation_pour(simulateur, generation)
            < cas.age_liquidation_pour(simulateur, generation) - 1e-6)


def ouvertures_decotees(variantes: list[Variante], racine: Path) -> dict[str, frozenset[int]]:
    """Les générations de la grille (``cout.generations``) où chaque carrière
    incomplète qui part au taux plein, et chaque carrière qui part à
    l'ouverture de son statut, partirait avec une décote à l'ouverture de son
    droit (:func:`decote_a_l_ouverture`), par code ; une génération que le
    modèle refuse de calculer n'en est pas. Gardées sous l'empreinte du modèle
    et le code de ce script."""
    parametres = Parametres(racine_donnees=racine)
    cas_types = tuple(v.cas for v in variantes
                      if v.cas.regle_liquidation == "ouverture"
                      or (incomplete(v) and v.cas.regle_liquidation == "taux_plein"))
    generations = C.generations()

    def calcul() -> dict[str, frozenset[int]]:
        simulateur = Simulateur(parametres).pour_la_projection()
        sortie = {}
        for cas in cas_types:
            siennes = []
            for generation in generations:
                try:
                    if decote_a_l_ouverture(simulateur, cas, generation):
                        siennes.append(generation)
                except (ValueError, KeyError):
                    continue
            sortie[cas.code] = frozenset(siennes)
        return sortie

    return memoire.memoriser_pour(
        parametres, ("decote_a_l_ouverture_de_la_population", parametres, cas_types,
                     generations), calcul)


def _en_paires(valeurs: list[tuple[int, float]]) -> tuple[tuple[int, float], ...]:
    """Des paires ``(génération, valeur)`` triées, une là où la valeur change."""
    sortie: list[tuple[int, float]] = []
    for generation, valeur in valeurs:
        if not sortie or sortie[-1][1] != valeur:
            sortie.append((generation, valeur))
    return tuple(sortie)


def parts_des_jumelles(variantes: list[Variante], effectifs,
                       source: CaracteristiquesRetraites, parts: dict[str, float],
                       decotes: dict[str, tuple[tuple[int, float], ...]],
                       ouvertures: dict[str, frozenset[int]] | None = None
                       ) -> dict[str, tuple[tuple[tuple[int, float], ...], ...]]:
    """Ce que chaque génération donne au poids des deux jumelles de chaque
    carrière incomplète (:data:`DECOTE_SELON_LA_GENERATION`), par code de la
    carrière : celle qui part au taux plein, puis celle qui décote, en paires
    ``(génération, part)`` triées. La jumelle qui décote pèse la part
    ``parts`` de la carrière (:func:`parts_avec_decote`) ; sa génération en
    fait partir la part ``decotes`` parmi tous les retraités du sexe
    (:func:`decotes_des_generations`), rapportée aux carrières incomplètes
    comme ``parts`` (:func:`part_des_incompletes`). Sous ``ouvertures``
    (:func:`ouvertures_decotees`, :data:`DECOTE_DES_CARRIERES_QUI_LE_PEUVENT`),
    elle se rapporte aux seules carrières qui peuvent décoter à la génération
    simulée dont chaque année de naissance est une cohorte, et se prend sans
    ce que les carrières qui partent à l'ouverture de leur statut y décotent ;
    la jumelle qui décote d'une carrière qui ne le peut pas ne pèse rien.
    Ensemble, les deux gardent à chaque génération le poids de la carrière."""
    poids = poids_retraites(variantes, effectifs, source.millesime)
    simulees = [(naissance, generation) for generation in C.generations()
                for naissance in range(generation - C._DEMI_TRANCHE,
                                       generation + C._DEMI_TRANCHE + 1)]
    sortie = {}
    for sexe in ("F", "H"):
        base = parts[sexe]
        if not base:
            continue
        du_sexe = [(v, p) for v, p in zip(variantes, poids) if v.cas.sexe == sexe]
        tous = somme_ordonnee(p for _, p in du_sexe)
        carrieres = [v for v, _ in du_sexe
                     if incomplete(v) and v.cas.regle_liquidation == "taux_plein"]
        codes = {v.cas.code for v in carrieres}

        def jumelles(part: float) -> tuple[float, float]:
            return ((1.0 - part) / (1.0 - base) if base < 1.0 else 1.0), part / base

        if ouvertures is None:
            incompletes = somme_ordonnee(p for v, p in du_sexe if incomplete(v))
            pleine, decotee = [], []
            for generation, decote in decotes[sexe]:
                au_taux_plein, avec = jumelles(part_des_incompletes(decote, tous, incompletes))
                pleine.append((generation, au_taux_plein))
                decotee.append((generation, avec))
            for v in carrieres:
                sortie[v.cas.code] = (tuple(pleine), tuple(decotee))
            continue
        eligibles = {generation: somme_ordonnee(
            p for v, p in du_sexe if v.cas.code in codes
            and generation in ouvertures.get(v.cas.code, ()))
            for generation in C.generations()}
        statutaires = {generation: somme_ordonnee(
            p for v, p in du_sexe if v.cas.regle_liquidation == "ouverture"
            and generation in ouvertures.get(v.cas.code, ()))
            for generation in C.generations()}

        def part(naissance: int, generation: int) -> float:
            if not eligibles[generation]:
                return 0.0
            cible = (_par_generation(decotes[sexe], naissance, 0.0) * tous
                     - statutaires[generation])
            return min(1.0, max(0.0, cible / eligibles[generation]))

        for v in carrieres:
            siennes = ouvertures.get(v.cas.code, frozenset())
            valeurs = [(naissance, jumelles(part(naissance, generation)
                                            if generation in siennes else 0.0))
                       for naissance, generation in simulees]
            sortie[v.cas.code] = (_en_paires([(n, j[0]) for n, j in valeurs]),
                                  _en_paires([(n, j[1]) for n, j in valeurs]))
    return sortie


def attentes_des_decotes(publies: dict, racine: Path) -> dict[str, list[tuple[float, float]]]:
    """Les départs avec décote des nés en 1953 (``GENERATION_DES_DECOTES``),
    sexe par sexe, en trois attentes après l'âge légal de la génération,
    ``(attente, part)`` triés (:data:`DECOTE_ENTRE_LES_DEUX_AGES`) : ceux de
    l'âge légal même, qui n'attendent pas ; ceux des :data:`PREMIERES_ANNEES`
    premières années de l'âge légal ; les autres, jusqu'à l'âge d'annulation
    de la décote. L'âge légal pèse sa part dans la génération, fois celle de
    ses départs qui décotent, que le tableau des places de l'EIR donne ;
    chaque âge de liquidation de même, au tableau des âges — l'année de l'âge
    légal sans ses départs de l'âge légal même —, et attend jusqu'au milieu de
    l'âge : de l'âge légal à l'anniversaire qui le suit pour l'année de l'âge
    légal, de l'anniversaire à l'âge d'annulation pour l'année de celui-ci,
    l'âge et demi ensuite ; chaque attente au milieu de ses âges, pondéré, et
    pesant leur part. Nul ne décote à l'âge d'annulation ni après lui ; les
    départs avec décote d'avant l'âge légal, des statuts qui ouvrent plus tôt,
    ne comptent pas."""
    from retraite_notionnelle.scenarios.actuel import AgesAnnulationDecote, AgesOuverture

    generation = GENERATION_DES_DECOTES
    legal = AgesOuverture(racine).age(generation)[0]
    annulation = AgesAnnulationDecote(racine).age(generation)[0]
    sortie = {}
    for sexe in ("F", "H"):
        def decotes(tableau: str, colonne: str) -> float:
            return (publies[(generation, tableau, colonne, sexe, "part")]
                    * publies[(generation, tableau, colonne, sexe, "condition_decote")])

        a_l_age_legal = decotes("position", "age_legal")
        groupes = {0: [0.0, a_l_age_legal]}
        for (lue, tableau, colonne, cle, indicateur) in publies:
            if ((lue, tableau, cle, indicateur) != (generation, "age_liquidation", sexe, "part")
                    or not colonne[0].isdigit()):
                continue
            age = float(colonne.split("_")[0])
            if age + 1.0 <= legal or age >= annulation:
                continue
            masse = decotes(tableau, colonne)
            if age == math.floor(legal):
                masse = max(0.0, masse - a_l_age_legal)
            milieu = (max(age, legal) + min(age + 1.0, annulation)) / 2.0
            groupe = groupes.setdefault(
                1 if age - math.floor(legal) < PREMIERES_ANNEES else 2, [0.0, 0.0])
            groupe[0] += masse * (milieu - legal)
            groupe[1] += masse
        total = somme_ordonnee(masse for _, masse in groupes.values())
        sortie[sexe] = sorted((attendue / masse, masse / total)
                              for attendue, masse in groupes.values())
    return sortie


def ages_legaux(racine: Path) -> tuple[tuple[int, float], ...]:
    """L'âge légal de chaque génération de la grille (``cout.generations``) qui
    en a un, paires ``(génération, âge)`` triées : celui d'où se compte
    l'attente d'un départ (:attr:`CasTypeLarge.attente`)."""
    from retraite_notionnelle.scenarios.actuel import AgesOuverture

    lus = AgesOuverture(racine)
    return tuple((generation, lu[0]) for generation in C.generations()
                 if (lu := lus.age(generation)) is not None)


def departs_avec_decote(variantes: list[Variante], effectifs,
                        source: CaracteristiquesRetraites, quintiles: dict,
                        decotes: dict[str, tuple[tuple[int, float], ...]] | None = None,
                        ouvertures: dict[str, frozenset[int]] | None = None,
                        attentes: dict[str, list[tuple[float, float]]] | None = None,
                        legaux: tuple[tuple[int, float], ...] = ()
                        ) -> list[Variante]:
    """Chaque carrière incomplète en deux : la part de son sexe
    (:func:`parts_avec_decote`) part à l'ouverture du droit, avec une décote,
    le reste au taux plein ; les autres variantes telles quelles. Sous
    ``decotes``, la part des départs avec décote de chaque génération
    (:func:`decotes_des_generations`), chaque jumelle porte ce que chaque
    génération donne à son poids (:func:`parts_des_jumelles`), rapporté sous
    ``ouvertures`` aux carrières qui peuvent décoter (:func:`ouvertures_decotees`).
    Sous ``attentes`` (:func:`attentes_des_decotes`), la jumelle qui décote se
    décline à son tour : chaque attente prend sa part du poids de la jumelle,
    et part autant d'années après l'âge légal de sa génération, ``legaux``
    (:func:`ages_legaux`), à l'ouverture du droit encore ; celle qui n'attend
    pas garde le code de la jumelle."""
    parts = parts_avec_decote(variantes, effectifs, source, quintiles)
    jumelles = (parts_des_jumelles(variantes, effectifs, source, parts, decotes, ouvertures)
                if decotes else {})
    sortie = []
    for v in variantes:
        part = parts[v.cas.sexe]
        if not incomplete(v) or v.cas.regle_liquidation != "taux_plein" or not part:
            sortie.append(v)
            continue
        pleine, decotee = jumelles.get(v.cas.code, ((), ()))
        sortie.append(v.fois(1.0 - part, parts_des_generations=pleine))
        cas = replace(v.cas, code=f"{v.cas.code}~decote", regle_liquidation="ouverture")
        for attente, poids in (attentes[v.cas.sexe] if attentes else ((0.0, 1.0),)):
            sienne = (elargi(cas, code=f"{cas.code}{attente:.2f}", attente=attente,
                             legaux=legaux) if attente else cas)
            sortie.append(v.fois(part * poids, decote=True, parts_des_generations=decotee,
                                 cas=sienne))
    return sortie


def peut_surcoter(v: Variante) -> bool:
    """Vrai pour une carrière que :data:`DEPARTS_AVEC_SURCOTE` décline : du
    salariat ou des non-salariés, de trente années validées et plus
    (:data:`TRANCHES_DES_SURCOTES`), qui part au taux plein, ni décotée ni
    déjà déclinée."""
    return (v.groupe in GROUPES_INTERROMPUS and v.tranche in TRANCHES_DES_SURCOTES
            and v.cas.regle_liquidation == "taux_plein" and not v.decote and not v.surcote)


def parts_avec_surcote(publies: dict) -> dict[str, float]:
    """La part des carrières complètes de chaque sexe qui partent avec une
    surcote parmi les nés en 1953 (:data:`GENERATION_DES_SURCOTES`) : la part
    des départs avec surcote, fois celle des carrières complètes parmi eux,
    divisée par celle des carrières complètes parmi tous."""
    generation = GENERATION_DES_SURCOTES
    return {sexe: (publies[(generation, "condition", "surcote", sexe, "part")] / 100.0
                   * publies[(generation, "condition", "surcote", sexe, "carriere_complete")]
                   / publies[(generation, "condition", "ensemble", sexe, "carriere_complete")])
            for sexe in ("F", "H")}


def attentes_des_surcotes(publies: dict, racine: Path) -> dict[str, list[tuple[float, float]]]:
    """Les départs avec surcote des nés en 1953, sexe par sexe, en trois
    attentes après l'âge légal de la génération (:data:`PREMIERES_ANNEES`),
    ``(attente, part)`` triés. Chaque âge de liquidation pèse la part de l'âge
    dans la génération, fois celle de ses départs qui surcotent, et attend
    jusqu'au milieu de l'âge — de l'âge légal à l'anniversaire qui le suit pour
    l'année de l'âge légal, l'âge et demi ensuite, « 67 ans et plus » pris pour
    67 ans, le dernier que l'enquête voie ; chaque attente au milieu de ses
    âges, pondéré, et pesant leur part. Nul ne surcote avant l'âge légal."""
    from retraite_notionnelle.scenarios.actuel import AgesAnnulationDecote, AgesOuverture

    generation = GENERATION_DES_SURCOTES
    legal = AgesOuverture(racine).age(generation)[0]
    annulation = AgesAnnulationDecote(racine).age(generation)[0]
    sortie = {}
    for sexe in ("F", "H"):
        groupes: dict[int, list[float]] = {}
        for (lue, tableau, colonne, cle, indicateur), part in publies.items():
            if ((lue, tableau, cle, indicateur) != (generation, "age_liquidation", sexe, "part")
                    or not colonne[0].isdigit()):
                continue
            age = float(colonne.split("_")[0])
            if age + 1.0 <= legal:
                continue
            masse = part * publies[(generation, tableau, colonne, sexe, "condition_surcote")]
            if age >= math.floor(annulation):
                rang = 2
            else:
                rang = 0 if age - math.floor(legal) < PREMIERES_ANNEES else 1
            groupe = groupes.setdefault(rang, [0.0, 0.0])
            groupe[0] += masse * ((max(age, legal) + age + 1.0) / 2.0 - legal)
            groupe[1] += masse
        total = somme_ordonnee(masse for _, masse in groupes.values())
        sortie[sexe] = sorted((attendue / masse, masse / total)
                              for attendue, masse in groupes.values())
    return sortie


def departs_avec_surcote(variantes: list[Variante], publies: dict,
                         racine: Path) -> list[Variante]:
    """Chaque carrière qui peut surcoter (:func:`peut_surcoter`) se décline :
    la part de son sexe (:func:`parts_avec_surcote`) attend après l'âge légal,
    répartie comme les départs avec surcote des nés en 1953
    (:func:`attentes_des_surcotes`), le reste part au taux plein ; les autres
    variantes telles quelles."""
    from retraite_notionnelle.scenarios.actuel import AgesOuverture

    parts = parts_avec_surcote(publies)
    attentes = attentes_des_surcotes(publies, racine)
    lus = AgesOuverture(racine)
    legaux = tuple((generation, lu[0]) for generation in C.generations()
                   if (lu := lus.age(generation)) is not None)
    sortie = []
    for v in variantes:
        part = parts[v.cas.sexe]
        if not peut_surcoter(v) or not part:
            sortie.append(v)
            continue
        sortie.append(v.fois(1.0 - part))
        for attente, poids in attentes[v.cas.sexe]:
            sortie.append(v.fois(part * poids, surcote=attente, cas=elargi(
                v.cas, code=f"{v.cas.code}~surcote{attente:.2f}", attente=attente,
                legaux=legaux)))
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


def annees_incompletes(v: Variante, ecart: float, legal: float,
                       debut: float | None = None) -> float:
    """Les années validées d'une carrière incomplète, ``ecart`` gagné ou perdu :
    une au moins, et pas plus que de ``debut``, son entrée par défaut, à l'âge
    légal de sa génération."""
    return min(max(1.0, v.duree + ecart), legal - (v.cas.age_debut if debut is None else debut))


def debut_des_annees(v: Variante, entree: float) -> float:
    """L'âge d'où une carrière incomplète de femme compte les années qu'elle
    peut valider avant l'âge légal : sous :data:`ALLONGEES_COMME_LES_PLEINES`,
    pour une carrière du salariat privé, ``entree``, celle des carrières pleines
    de sa génération ; la sienne, sinon."""
    if ALLONGEES_COMME_LES_PLEINES and v.cas.code.split("~", 1)[0] == GABARIT:
        return entree
    return v.cas.age_debut


def duree_moyenne_des_femmes(femmes: list[tuple[Variante, float]], ecart: float,
                             legal: float, entree: float) -> float:
    """La durée validée moyenne des femmes d'une génération, en années, comme
    :func:`ecarts_des_femmes` la compte : une carrière incomplète à ses années
    (:func:`annees_incompletes`), bornées depuis ``entree`` sous
    :data:`ALLONGEES_COMME_LES_PLEINES` pour le salariat privé
    (:func:`debut_des_annees`), une carrière pleine de l'entrée à l'âge légal —
    à ``entree`` pour le salariat privé —, les deux avec les majorations de
    durée de ses enfants, huit trimestres chacun ; une carrière statutaire à sa
    durée."""
    majoration = 2.0 * ENFANTS
    somme = total = 0.0
    for v, p in femmes:
        if incomplete(v):
            annees = annees_incompletes(v, ecart, legal, debut_des_annees(v, entree)) + majoration
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
    à l'année près ; sous :data:`ALLONGEES_COMME_LES_PLEINES`, celle du
    salariat privé dont les années ne tiennent pas entre son entrée et l'âge
    légal entre à l'âge légal moins ses années, à l'année près, chaque
    génération ; les autres variantes telles quelles."""
    from retraite_notionnelle.scenarios.actuel import AgesOuverture

    legaux = AgesOuverture(racine)
    ecarts = ecarts_des_femmes(variantes, effectifs, source, racine)
    pleines = entrees_des_carrieres_pleines(racine)["F"]
    sortie = []
    for v in variantes:
        if v.cas.sexe != "F" or not incomplete(v):
            sortie.append(v)
            continue
        cibles, entrees = [], []
        for generation, ecart in sorted(ecarts.items()):
            lu = legaux.age(generation)
            legal = lu[0] if lu is not None else 60.0
            debut = debut_des_annees(v, _par_generation(pleines, generation, v.cas.age_debut))
            cible = float(round(annees_incompletes(v, ecart, legal, debut)))
            cibles.append((generation, cible))
            entrees.append((generation, min(float(v.cas.age_debut),
                                            max(debut, float(round(legal - cible))))))
        allongee = any(age < v.cas.age_debut for _, age in entrees)
        sortie.append(replace(v, cas=replace(v.cas, cibles=tuple(cibles),
                                             entrees=tuple(entrees) if allongee else ())))
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


def tetes_des_caisses_reelles(variantes: list[Variante], base):
    """Ce qui rend aux têtes propres de chaque variante (``cout._tetes_par_poids``)
    celles de ses caisses réelles, dont ``poids_effectifs`` divise sa
    pseudo-caisse.

    La page divise chaque caisse par les têtes de ses cas types, pesées de
    leurs parts (action 138, étape 3) : un cas type qui part tôt compterait
    sinon plus de retraités que sa caisse n'en a. Chaque variante réclame ici
    sa pseudo-caisse, et ses seules têtes la diviseraient : celles d'une caisse
    réelle sont la moyenne des têtes des variantes qui la réclament, pesées de
    leurs parts positives — celles que ``personnes`` retire, des contractuels
    de la Cnav, se divisent comme la caisse qu'elles retirent. La variante
    divise ses retraités comme la page diviserait les siens, et la grille du
    dépôt redonne la page. Sans retraités, ses propres têtes."""
    def diviser(propres: Callable[[int], dict[str, float]]) -> Callable[[int], dict[str, float]]:
        memoire: dict[int, dict[str, float]] = {}

        def tetes(annee: int) -> dict[str, float]:
            if annee not in memoire:
                siennes = propres(annee)
                pesees: dict[str, list[float]] = {}
                parts: dict[str, list[float]] = {}
                for v in variantes:
                    for reelle, part in v.retraites:
                        if part > 0.0:
                            pesees.setdefault(reelle, []).append(
                                part * siennes.get(v.cas.code, 0.0))
                            parts.setdefault(reelle, []).append(part)
                moyennes = {reelle: somme_ordonnee(pesees[reelle]) / somme_ordonnee(parts[reelle])
                            for reelle in pesees}
                sortie = {}
                for v in variantes:
                    retraites = somme_ordonnee(base.effectif(reelle, annee) * part
                                               for reelle, part in v.retraites)
                    divises = somme_ordonnee(base.effectif(reelle, annee) * part / moyennes[reelle]
                                             for reelle, part in v.retraites
                                             if moyennes.get(reelle, 0.0) > 0.0)
                    sortie[v.cas.code] = (retraites / divises if retraites > 0.0 and divises > 0.0
                                          else siennes.get(v.cas.code, 0.0))
                memoire[annee] = sortie
            return memoire[annee]

        return tetes

    return diviser


def _simuler_morceau(parametres: Parametres, morceau: tuple[CasType, ...]):
    """La grille simulée d'un morceau, gardée comme celle de la page."""
    return memoire.memoriser_pour(
        parametres, ("grille_du_cout", parametres, morceau, "droit"),
        lambda: C._pensionnes(Simulateur(parametres), morceau, "droit"))


#: Le plus de cas types qu'un morceau de :func:`simuler` envoie au portage :
#: le pont lui passe sa demande d'un seul bloc, que node ne lit pas au-delà de
#: 512 Mo, et chaque cas type y porte ses carrières de toutes les générations,
#: 1,4 à 1,7 Mo avec le paquet des données. Les morceaux de 468 cas types de
#: la population de la vingt-quatrième version, sur quatre cœurs, ne passaient
#: pas ; ceux de 383, de la vingt-troisième, passaient de peu. Cent, et non plus
#: deux cents (le 25 octobre 2026) : le morceau de deux cents cas types de la
#: population de la vingt-huitième version tenait 2,6 Go au plus, le worker et
#: son portage réunis, celui de cent 1,7, pour 1,54 et 1,65 seconde par cas
#: type ; quatre workers passaient sinon les 10 Go.
CAS_TYPES_PAR_MORCEAU = 100


def morceaux_de(cas_types: tuple[CasType, ...], processus: int) -> list[tuple[CasType, ...]]:
    """La grille en morceaux bout à bout, deux par cœur, de
    :data:`CAS_TYPES_PAR_MORCEAU` cas types au plus."""
    taille = max(1, min(CAS_TYPES_PAR_MORCEAU,
                        math.ceil(len(cas_types) / max(1, 2 * processus))))
    return [cas_types[i:i + taille] for i in range(0, len(cas_types), taille)]


def alleger(pensionne: C.Pensionne) -> C.Pensionne:
    """Un couple tel que les têtes le lisent (:func:`en_tetes`) : sans la
    proposition, son autre côté ni ses cotisations, que seule la page lit, et
    ses survies en tableaux de flottants, quatre fois plus légers que des
    n-uplets. Le morceau de deux cents cas types de la population passe de 177
    à 36 Mo en mémoire."""
    return replace(pensionne, propre=None, autre=None, cotisations=None,
                   survies=tuple(array("d", courbe) for courbe in pensionne.survies))


def _simuler_morceau_allege(parametres: Parametres, morceau: tuple[CasType, ...]):
    """:func:`_simuler_morceau`, chaque couple allégé (:func:`alleger`) avant de
    rejoindre le processus qui mesure ; la mémoire garde le morceau entier."""
    pensionnes, echecs = _simuler_morceau(parametres, morceau)
    return [alleger(pensionne) for pensionne in pensionnes], echecs


def simuler(parametres: Parametres, cas_types: tuple[CasType, ...], processus: int,
            alleges: bool = False):
    """Ce que ``cout._pensionnes`` rend pour la grille, par morceaux
    (:func:`morceaux_de`), chacun gardé, et sur ``processus`` cœurs quand il y
    en a plusieurs ; chaque couple allégé sous ``alleges``
    (:func:`_simuler_morceau_allege`)."""
    simuler_un = _simuler_morceau_allege if alleges else _simuler_morceau
    morceaux = morceaux_de(cas_types, processus)
    if processus <= 1 or len(morceaux) == 1:
        resultats = [simuler_un(parametres, morceau) for morceau in morceaux]
    else:
        with ProcessPoolExecutor(max_workers=processus,
                                 mp_context=multiprocessing.get_context("spawn")) as pool:
            resultats = list(pool.map(simuler_un, [parametres] * len(morceaux), morceaux))
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
    diviser = tetes_des_caisses_reelles(variantes, simulateur.effectifs)
    simulateur.effectifs = EffectifsRepartis(simulateur.effectifs, retraites)
    simulateur.cotisants = EffectifsRepartis(simulateur.cotisants, cotisants)
    variante = variante_du_scenario(parametres.scenario_projection,
                                    racine / "reference" / "macro")
    return C.calculer_cout(
        simulateur, DepensesRetraite(racine), Population(racine),
        ComptesRetraite(racine, variante=variante), cas_types=cas_types,
        assiette=AssietteActivite(racine), grille_simulee=simulee,
        tetes_par_poids=lambda pensionnes, population: diviser(
            C._tetes_par_poids(pensionnes, population)))


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
                        annee_euros: int, annee: int,
                        parts: dict[str, tuple[tuple[int, float], ...]] | None = None,
                        ) -> list[tuple[float, float, str]]:
    """Ce que la grille sert l'année ``annee``, en TÊTES : une ligne par cohorte
    liquidée, (pension mensuelle de droit direct du scénario 1 en euros de
    l'année, poids, sexe).

    Les têtes sont celles de la page (``cout._masses``) : chaque génération de
    la grille en représente cinq, chacune pesée par son effectif INSEE de
    l'année et comptée dès sa liquidation, chaque cas type par son poids de la
    page et par sa survie propre, à nombre de décès égal
    (``cout._survies_alignees``). La pension est celle de la liquidation,
    revalorisée comme la page la revalorise — le droit jusqu'au dernier
    barème, puis les prix, et la valeur de service de l'Agirc-Arrco pour sa
    part (``coefficient_servi``) —, ramenée des euros constants à ceux de
    l'année. Sans la complétude des cohortes (``Pensionne.completude``) : elle
    allège la MASSE d'une cohorte d'une moyenne, que la distribution ne sait
    pas répartir entre ses membres ; chaque ligne décrit une carrière. Chaque
    cohorte pèse enfin ce que son année de naissance donne au poids de son cas
    type, ``parts`` par code (:attr:`GrilleEnTetes.parts`) ; une, sans elles.
    """
    sexes = {cas.code: cas.sexe for cas in cas_types}
    return [(montant, poids_tete, sexes[pensionne.code])
            for pensionne, montant, poids_tete in cohortes_de_l_annee(
                pensionnes, poids, population, revalorisation, macro, annee_euros, annee,
                parts)]


def cohortes_de_l_annee(pensionnes: list, poids: dict[str, float], population: Population,
                        revalorisation: RevalorisationServie, macro: DonneesMacro,
                        annee_euros: int, annee: int,
                        parts: dict[str, tuple[tuple[int, float], ...]] | None = None):
    """Les cohortes de :func:`pensions_de_l_annee`, chacune avec son couple :
    ``(couple, pension mensuelle, poids en têtes)``."""
    parts = parts or {}
    vers_l_annee = macro.coefficient_prix(annee_euros, annee) / 12.0
    alignees = C._survies_alignees(pensionnes, poids, annee)
    for pensionne in pensionnes:
        part = poids.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
        siennes = parts.get(pensionne.code, ())
        for decalage in range(-C._DEMI_TRANCHE, C._DEMI_TRANCHE + 1):
            liquidation = pensionne.liquidation(decalage)
            if annee < liquidation:
                continue
            effectif = (population.effectif(annee - pensionne.generation - decalage, annee)
                        * alignees.get((pensionne.code, pensionne.generation, decalage), 1.0)
                        * _par_generation(siennes, pensionne.generation + decalage, 1.0))
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
    #: Ce que chaque génération donne au poids de chaque cas type, par code :
    #: les :attr:`Variante.parts_des_generations` de ses variantes qui en ont.
    parts: dict[str, tuple[tuple[int, float], ...]] = field(default_factory=dict)

    def part_de(self, code: str, naissance: int) -> float:
        """Ce que l'année de naissance ``naissance`` donne au poids du cas type
        ``code`` (:data:`DECOTE_SELON_LA_GENERATION`) : une, sans part."""
        return _par_generation(self.parts.get(code, ()), naissance, 1.0)

    def pensions(self, annee: int) -> list[tuple[float, float, str]]:
        """:func:`pensions_de_l_annee`, pour cette grille."""
        return pensions_de_l_annee(self.pensionnes, self.cas_types, self.poids(annee),
                                   self.population, self.revalorisation, self.macro,
                                   self.annee_euros, annee, self.parts)

    def cohortes(self, annee: int) -> list:
        """:func:`cohortes_de_l_annee`, pour cette grille."""
        return list(cohortes_de_l_annee(self.pensionnes, self.poids(annee), self.population,
                                        self.revalorisation, self.macro, self.annee_euros,
                                        annee, self.parts))

    def pensions_par_cas_type(self, annee: int) -> list[tuple[float, float, str, str]]:
        """:meth:`pensions`, chaque ligne avec le cas type dont sa carrière se
        décline : ``(pension, poids, sexe, cas type)``."""
        sexes = {cas.code: cas.sexe for cas in self.cas_types}
        return [(montant, poids, sexes[pensionne.code], pensionne.code.split("~", 1)[0])
                for pensionne, montant, poids in self.cohortes(annee)]


def en_tetes(parametres: Parametres, variantes: list[Variante],
             processus: int = 1, alleges: bool = False) -> GrilleEnTetes:
    """La grille de :func:`calculer`, la même simulation gardée, sous les poids
    que la page lui donne : ceux de ses caisses, recalés sur la dépense des
    groupes du COR (``cout._poids_par_groupe``). Sous ``alleges``, ses couples
    n'ont que ce que les têtes en lisent (:func:`alleger`) : la mesure les
    demande, sans quoi la population de la vingt-sixième version ne tient pas
    dans la mémoire du conteneur."""
    racine = parametres.racine_donnees
    cas_types, retraites, _ = pseudo(variantes)
    pensionnes, echecs = simuler(parametres, cas_types, processus, alleges)
    simulateur = Simulateur(parametres)
    simulateur.effectifs = EffectifsRepartis(simulateur.effectifs, retraites)
    population = Population(racine)
    revalorisation = RevalorisationServie(
        simulateur.pour_la_projection(),
        min(p.annee_liquidation for p in pensionnes) - C._DEMI_TRANCHE, C.HORIZON)
    tetes = tetes_des_caisses_reelles(variantes, simulateur.effectifs.base)(
        C._tetes_par_poids(pensionnes, population))
    poids = C._poids_par_groupe(
        C._ponderation(simulateur, "effectifs", cas_types, tetes=tetes),
        pensionnes, population,
        revalorisation, DecompositionDepense(racine / "reference" / "macro"))
    return GrilleEnTetes(pensionnes, cas_types, poids, population, revalorisation,
                         simulateur.macro, parametres.annee_euros_constants, echecs,
                         {v.cas.code: v.parts_des_generations for v in variantes
                          if v.parts_des_generations})


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


def _par_morceaux(fonction: Callable[[Parametres, tuple], list], parametres: Parametres,
                  couples, processus: int) -> list:
    """``fonction(parametres, morceau)`` sur les couples ``(cas type,
    génération)``, triés, par morceaux, chacun gardé par elle, sur
    ``processus`` cœurs quand il y en a plusieurs : ses lignes, bout à bout."""
    couples = sorted(couples, key=lambda couple: (couple[0].code, couple[1]))
    taille = max(1, math.ceil(len(couples) / max(1, 2 * processus)))
    morceaux = [tuple(couples[i:i + taille]) for i in range(0, len(couples), taille)]
    if processus <= 1 or len(morceaux) <= 1:
        resultats = [fonction(parametres, morceau) for morceau in morceaux]
    else:
        with ProcessPoolExecutor(max_workers=processus,
                                 mp_context=multiprocessing.get_context("spawn")) as pool:
            resultats = list(pool.map(fonction, [parametres] * len(morceaux), morceaux))
    return [ligne for resultat in resultats for ligne in resultat]


def proratisations(parametres: Parametres, couples, processus: int
                   ) -> dict[tuple[str, int], tuple[float, bool, float, bool]]:
    """La proratisation de chaque couple ``(cas type, génération)``, s'il est
    au minimum, sa durée validée et s'il part avec une décote : par morceaux,
    chacun gardé, sur ``processus`` cœurs quand il y en a plusieurs."""
    return {(code, generation): (coefficient, minimum, annees, decote)
            for code, generation, coefficient, minimum, annees, decote
            in _par_morceaux(_proratisations, parametres, couples, processus)}


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


# -- les départs d'une génération, contre l'EIR ----------------------------------

#: Les générations de la grille dont les départs se confrontent à l'EIR, et la
#: génération de l'enquête qui juge chacune (``departs_generations.csv``) :
#: celle de 1950 à elle-même ; celle de 1955 aux nés en 1953, la plus proche
#: que l'enquête voie presque toute partie. Leurs places par rapport à l'âge
#: légal se comparent, et leurs conditions de départ ; leurs âges quand la
#: génération est la même — l'âge légal des nés en 1953, 61 ans et 2 mois,
#: n'est pas celui de la grille 1955, 62 ans.
GENERATIONS_DES_DEPARTS = {1950: 1950, 1955: 1953}

#: L'année où l'EIR voit chacune de ses générations : les classeurs « nés en
#: 1950 (EIR 2016) » et « nés en 1953 (EIR 2020) ».
ENQUETES_DES_DEPARTS = {1950: 2016, 1953: 2020}

#: Les places d'un départ, dans l'ordre de l'EIR.
PLACES_DES_DEPARTS = ("avant_age_legal", "age_legal", "entre", "age_annulation",
                      "apres_annulation")

#: Les classes de conditions de départ que la population sait faire, et les
#: conditions de l'EIR que chacune réunit : la population n'a ni invalides ni
#: inaptes, ni de motif propre au taux plein ; ce qu'elle fait partir au taux
#: plein d'un statut, sans décote, l'EIR le dit « décote inapplicable ».
CLASSES_DE_CONDITIONS: dict[str, tuple[str, ...]] = {
    "carriere_longue": ("carriere_longue",),
    "decote": ("decote",),
    "surcote": ("surcote",),
    "taux_plein_age": ("taux_plein_age",),
    "taux_plein_autre": ("decote_inapplicable", "invalidite", "inaptitude",
                         "autres_motifs", "taux_plein_duree"),
}

#: L'écart à l'âge légal ou à l'âge d'annulation de la décote en deçà duquel un
#: départ est pris à cet âge : un mois et demi.
TOLERANCE_DE_PLACE = 0.125


def departs_publies(racine: Path) -> dict[tuple[int, str, str, str, str], float]:
    """Les départs des nés en 1950 et en 1953 que l'EIR compte
    (``departs_generations.csv``), clé ``(génération, tableau, colonne, sexe,
    indicateur)``."""
    return {(int(l["generation"]), l["tableau"], l["colonne"], l["sexe"], l["indicateur"]):
            float(l["valeur"]) for l in _lire_macro(racine, "departs_generations.csv")}


def position_du_depart(age: float, legal: float, annulation: float) -> str:
    """La place d'un départ à ``age``, comme l'EIR la range : avant l'âge
    légal, à lui, entre lui et l'âge d'annulation de la décote, à ce dernier,
    après lui, chacun à :data:`TOLERANCE_DE_PLACE` près."""
    if abs(age - legal) <= TOLERANCE_DE_PLACE:
        return "age_legal"
    if age < legal:
        return "avant_age_legal"
    if abs(age - annulation) <= TOLERANCE_DE_PLACE:
        return "age_annulation"
    return "entre" if age < annulation else "apres_annulation"


def age_du_depart(age: float) -> str:
    """L'âge d'un départ en années révolues, comme l'EIR le range : avant
    60 ans, de 60 à 66 ans, 67 ans et plus."""
    if age < 60.0 - 1e-9:
        return "avant_60"
    if age >= 67.0 - 1e-9:
        return "67_plus"
    return str(int(age + 1e-9))


def au_taux_plein(cas: CasType) -> CasType:
    """Ce cas type sous la règle ``taux_plein``, sans l'attente d'un départ
    avec surcote : celui dont le pilote fixe l'âge du taux plein."""
    if isinstance(cas, CasTypeLarge):
        return replace(cas, regle_liquidation="taux_plein", attente=0.0)
    return replace(cas, regle_liquidation="taux_plein")


def condition_au_depart(simulateur: Simulateur, cas: CasType, generation: int
                        ) -> tuple[float, str]:
    """L'âge où ce cas type part, étant né en ``generation``, et la classe de
    :data:`CLASSES_DE_CONDITIONS` de son départ : en carrière longue quand le
    droit l'ouvre par elle ; avec une décote (:func:`avec_decote`) ; avec une
    surcote quand il part après l'âge légal de sa génération et après l'âge de
    son taux plein ; au taux plein par l'âge quand il part à l'âge
    d'annulation de la décote, ou après lui, sans la durée requise ; au taux
    plein, autrement. Les générations que la mesure lit partent après 2004 :
    la loi leur sert la surcote de tout trimestre qui passe l'un et l'autre."""
    from retraite_notionnelle.scenarios.actuel import AgesAnnulationDecote, AgesOuverture

    racine = simulateur.parametres.racine_donnees
    age = cas.age_liquidation_pour(simulateur, generation)
    actuel = simulateur.echeancier(cas.carriere_a(simulateur, generation, age)).au_depart
    if actuel.motif_ouverture == "carriere_longue":
        return age, "carriere_longue"
    if avec_decote(simulateur, cas, generation, actuel.taux_liquidation):
        return age, "decote"
    legal = AgesOuverture(racine).age(generation)[0]
    annulation = AgesAnnulationDecote(racine).age(generation)[0]
    if cas.regle_liquidation != "services" and age > legal + TOLERANCE_DE_PLACE:
        if age > au_taux_plein(cas).age_liquidation_pour(simulateur, generation) + 1e-6:
            return age, "surcote"
    if (age >= annulation - TOLERANCE_DE_PLACE
            and actuel.trimestres_valides < actuel.trimestres_requis):
        return age, "taux_plein_age"
    return age, "taux_plein_autre"


def _conditions(parametres: Parametres, morceau: tuple) -> list[tuple[str, int, float, str]]:
    """L'âge et la condition du départ de chaque couple du morceau
    (:func:`condition_au_depart`), au scénario 1 de la page. Gardés sous
    l'empreinte du modèle et le code de ce script."""

    def calcul():
        simulateur = Simulateur(parametres).pour_la_projection()
        sortie = []
        for cas, generation in morceau:
            try:
                age, condition = condition_au_depart(simulateur, cas, generation)
            except (ValueError, KeyError):
                continue
            sortie.append((cas.code, generation, age, condition))
        return sortie

    return memoire.memoriser_pour(
        parametres, ("age_et_condition_de_depart_de_la_grille", parametres, morceau), calcul)


def confronter_departs(lignes: list[tuple], publies: dict) -> dict:
    """Les départs de chaque génération de la grille, sexe par sexe, contre
    ceux de la génération de l'EIR qui la juge (:data:`GENERATIONS_DES_DEPARTS`) :
    la part de chaque place, de chaque classe de conditions et, quand la
    génération est la même, de chaque âge, ``[grille, EIR]``. Les conditions
    de l'EIR se lisent parmi les départs dont la condition est connue.
    ``lignes`` : ``(génération, sexe, poids, place, classe, âge)``."""
    masses: dict[tuple[int, str], dict[str, dict[str, float]]] = {}
    for generation, sexe, poids, place, classe, age in lignes:
        for cle in (sexe, "ensemble"):
            masse = masses.setdefault((generation, cle),
                                      {"places": {}, "classes": {}, "ages": {}})
            for champ, valeur in (("places", place), ("classes", classe), ("ages", age)):
                masse[champ][valeur] = masse[champ].get(valeur, 0.0) + poids
    sortie: dict = {}
    for (generation, sexe), masse in sorted(masses.items()):
        eir_ = GENERATIONS_DES_DEPARTS[generation]
        total = somme_ordonnee(masse["places"].values())

        def publie(tableau: str, colonne: str) -> float:
            return publies.get((eir_, tableau, colonne, sexe, "part"), 0.0)

        connues = somme_ordonnee(publie("condition", condition)
                                 for conditions in CLASSES_DE_CONDITIONS.values()
                                 for condition in conditions)
        mesure = {
            "positions": {place: [masse["places"].get(place, 0.0) / total,
                                  publie("position", place) / 100.0]
                          for place in PLACES_DES_DEPARTS},
            "conditions": {classe: [masse["classes"].get(classe, 0.0) / total,
                                    somme_ordonnee(publie("condition", c) for c in conditions)
                                    / connues]
                           for classe, conditions in CLASSES_DE_CONDITIONS.items()},
        }
        if eir_ == generation:
            ages = {a for (g, t, a, _, _) in publies if (g, t) == (eir_, "age_liquidation")
                    and a != "ensemble"} | set(masse["ages"])
            mesure["ages"] = {age: [masse["ages"].get(age, 0.0) / total,
                                    publie("age_liquidation", age) / 100.0]
                              for age in sorted(ages, key=_rang_d_age)}
        sortie.setdefault(str(generation), {"eir": eir_})[sexe] = mesure
    return sortie


def _rang_d_age(age: str) -> float:
    """Le rang d'un âge de :func:`age_du_depart`, pour les ranger."""
    if age == "avant_60":
        return 0.0
    return float(age.split("_")[0]) + (0.5 if age.endswith("_plus") else 0.0)


def departs(parametres: Parametres, tetes: GrilleEnTetes, publies: dict,
            processus: int = 1) -> dict:
    """Les départs de chaque génération de :data:`GENERATIONS_DES_DEPARTS`,
    contre ceux de la génération de l'EIR qui la juge
    (:func:`confronter_departs`). Chaque génération se compte à l'âge où
    l'enquête voit la sienne — 66 ans pour les nés en 1950, 67 pour les nés en
    1953 —, ses seuls départs déjà pris à cet âge, chaque cas type du poids
    que la page lui donne cette année-là et de sa survie propre, à nombre de
    décès égal (``cout._survies_alignees``), et de ce que la génération donne à
    son poids (:meth:`GrilleEnTetes.part_de`)."""
    from retraite_notionnelle.scenarios.actuel import AgesAnnulationDecote, AgesOuverture

    racine = parametres.racine_donnees
    legaux, annulations = AgesOuverture(racine), AgesAnnulationDecote(racine)
    cas_par_code = {cas.code: cas for cas in tetes.cas_types}
    couples = {(cas_par_code[pensionne.code], pensionne.generation)
               for pensionne in tetes.pensionnes
               if pensionne.generation in GENERATIONS_DES_DEPARTS}
    lus = {(code, generation): (age, condition) for code, generation, age, condition
           in _par_morceaux(_conditions, parametres, couples, processus)}
    lignes = []
    for generation, eir_ in GENERATIONS_DES_DEPARTS.items():
        vu = ENQUETES_DES_DEPARTS[eir_] - eir_
        poids = tetes.poids(generation + vu)
        alignees = C._survies_alignees(tetes.pensionnes, poids, generation + vu)
        legal = legaux.age(generation)[0]
        annulation = annulations.age(generation)[0]
        for pensionne in tetes.pensionnes:
            lu = lus.get((pensionne.code, pensionne.generation))
            if pensionne.generation != generation or lu is None or lu[0] >= vu + 1.0:
                continue
            part = (poids.get(pensionne.code, 0.0)
                    * alignees.get((pensionne.code, generation, 0), 1.0)
                    * tetes.part_de(pensionne.code, generation))
            if part > 0.0:
                lignes.append((generation, cas_par_code[pensionne.code].sexe, part,
                               position_du_depart(lu[0], legal, annulation), lu[1],
                               age_du_depart(lu[0])))
    return confronter_departs(lignes, publies)


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
    l'EIR (:func:`confronter_non_salaries`). Chaque grille confronte enfin les
    départs de deux de ses générations à ceux des nés en 1950 et en 1953
    (:func:`departs`)."""
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
    publies_departs = departs_publies(racine)
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
        tetes = en_tetes(parametres, variantes, processus, alleges=True)
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
        mesure["departs"] = departs(parametres, tetes, publies_departs, processus)
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


#: Les intitulés des places, des classes de conditions et des âges d'un départ.
INTITULES_DES_DEPARTS = {
    "avant_age_legal": "avant l'âge légal", "age_legal": "à l'âge légal",
    "entre": "entre les deux", "age_annulation": "à l'âge d'annulation",
    "apres_annulation": "après lui", "carriere_longue": "carrière longue",
    "decote": "décote", "surcote": "surcote", "taux_plein_age": "taux plein par l'âge",
    "taux_plein_autre": "taux plein, autrement", "avant_60": "avant 60 ans",
    "67_plus": "67 ans et plus",
}

#: Les intitulés des trois rubriques de la mesure des départs.
RUBRIQUES_DES_DEPARTS = {"positions": "la place du départ", "conditions": "sa condition",
                         "ages": "son âge"}


def imprimer_departs(resultat: dict) -> None:
    """Les départs de deux générations de chaque grille, contre ceux des nés
    en 1950 et en 1953 que l'EIR compte : la part de chaque place, de chaque
    classe de conditions et, à génération égale, de chaque âge."""
    lues = [(nom, g["departs"]) for nom, g in resultat["grilles"].items() if "departs" in g]
    if not lues:
        return
    print("\nLes départs d'une génération, contre l'EIR — la grille 1950 contre les nés "
          "en 1950 (EIR 2016), la grille 1955 contre les nés en 1953 (EIR 2020) ; part "
          "des départs déjà pris à l'âge où l'enquête voit la génération, en %")
    for generation in sorted({g for _, d in lues for g in d}):
        for rubrique in ("positions", "conditions", "ages"):
            cles = []
            for _, d in lues:
                for sexe in SEXES:
                    for cle in d.get(generation, {}).get(sexe, {}).get(rubrique, {}):
                        if cle not in cles:
                            cles.append(cle)
            if not cles:
                continue
            eir_ = lues[0][1][generation]["eir"]
            titre = f"grille {generation}, nés en {eir_} : {RUBRIQUES_DES_DEPARTS[rubrique]}"
            print(f"\n{titre:38}" + "".join(f"{INTITULES_SEXES[s]:>18}" for s in SEXES))
            for cle in cles:
                ligne = f"  {INTITULES_DES_DEPARTS.get(cle, cle + ' ans'):24}"
                print(f"{ligne}{'EIR':>12}" + "".join(
                    f"{lues[0][1][generation].get(s, {}).get(rubrique, {}).get(cle, [0, 0])[1] * 100:>18.1f}"
                    for s in SEXES))
                for nom, d in lues:
                    print(f"{'':26}{nom[:12]:>12}" + "".join(
                        f"{d[generation].get(s, {}).get(rubrique, {}).get(cle, [0, 0])[0] * 100:>18.1f}"
                        for s in SEXES))


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
    imprimer_departs(resultat)

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
