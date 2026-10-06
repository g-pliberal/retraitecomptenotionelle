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

La page se refait sur chacune ; le tableau dit ce que chaque grille déplace par
rapport à celle du dépôt : l'écart cumulé des années observées, la part du PIB
en 2070, le solde moyen de 2026 à 2070, le coefficient d'équilibre en 2070, et
le passé que la projection refait à rebours (``Avenir.reconstitution``, action
147), dont la composition des cas types est l'un des suspects.

L'ASPA, RETIRÉE DE TOUTES LES GRILLES
-------------------------------------
Le scénario 1 sert l'ASPA à qui n'a pas assez, et la range dans la pension qu'il
rend. Les carrières courtes la déclenchent ; la garder dans la grille élargie
compterait le minimum vieillesse comme une pension, quand la dépense que la
page multiplie l'exclut depuis le 23 septembre 2026. Toutes les grilles se
calculent donc sans elle (``minimum_vieillesse_dans_le_scenario_actuel``), et
c'est à la grille du dépôt SANS ASPA que chacune se compare.

La mesure a trouvé en chemin que la grille du dépôt la déclenche aussi, aux
non-salariés des premières générations — l'artisan né de 1885 à 1905, le
libéral jusqu'en 1915, l'exploitant agricole jusqu'en 1920 : leurs régimes,
nés après la guerre, ne leur servaient que des pensions courtes ou
forfaitaires, que le scénario 1 complète au minimum vieillesse, quand les
scénarios notionnels ne le servent pas. La page compte donc, dans les années
observées, une économie qui n'est que le minimum vieillesse retiré ; le script
la chiffre à part. Il vérifie aussi que la grille du dépôt, réécrite en parts
et avec l'ASPA, redonne la page au chiffre près.

CE QUE LA MESURE N'EST PAS
---------------------------
Une population. Les axes sont tenus pour indépendants — le salaire ne dépend
ni du sexe ni de la durée —, chaque déclinaison garde l'âge d'entrée et le
profil de son cas type, et les parts sont celles des retraités de 2020,
appliquées à toutes les générations. La dispersion des salaires est celle d'une
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
from dataclasses import dataclass, fields, replace
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.somme import somme_ordonnee
from retraite_notionnelle import cout as C  # noqa: E402
from retraite_notionnelle import memoire  # noqa: E402
from retraite_notionnelle.carriere import Metier  # noqa: E402
from retraite_notionnelle.castypes import CAS_TYPES, CasType  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.donnees.assiette import AssietteActivite  # noqa: E402
from retraite_notionnelle.donnees.caracteristiques import CaracteristiquesRetraites  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.equilibre import (  # noqa: E402
    ComptesRetraite, variante_du_scenario,
)
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

GRILLES = ("reference", "personnes", "melees", "femmes", "interruptions", "salaires",
           "ensemble")

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
                        "carriere_interrompue", "contractuel_public", "artisan")),
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


@dataclass(frozen=True)
class CasTypeLarge(CasType):
    """Un cas type de la grille élargie : celui du dépôt, décliné.

    ``avant`` : les métiers qui précèdent le sien, chacun ``(affiliation,
    années)``, au même niveau de salaire — la carrière mêlée d'un
    polypensionné. Sans eux, la carrière est celle du cas type.
    """

    avant: tuple[tuple[str, float], ...] = ()

    def _carriere(self, simulateur: Simulateur, generation: int, age_liquidation: float):
        if not self.avant:
            return super()._carriere(simulateur, generation, age_liquidation)
        interruptions = {
            int(generation + self.age_debut + decalage): motif
            for decalage, motif in self.interruptions_relatives
        }
        metiers, age = [], self.age_debut
        for affiliation, annees in self.avant:
            metiers.append(Metier(affiliation=affiliation, age_debut=age,
                                  niveau_salaire=self.niveau_salaire))
            age += annees
        metiers.append(Metier(affiliation=self.affiliation, age_debut=age,
                              niveau_salaire=self.niveau_salaire))
        return simulateur.carriere_parcours(
            annee_naissance=generation, sexe=self.sexe, metiers=metiers,
            age_liquidation=age_liquidation, profil_carriere=self.profil_carriere,
            interruptions=interruptions, nombre_enfants=self.nombre_enfants,
            part_primes=self.part_primes,
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
    return CaracteristiquesRetraites(racine)


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
    """La grille du dépôt, en parts : chaque cas type, la part de sa caisse que
    ``poids_effectifs`` lui donne — l'effectif de la caisse partagé également
    entre les cas types qui la réclament."""
    reclamants: dict[str, int] = {}
    for cas in CAS_TYPES:
        for caisse in cas.caisses:
            reclamants[caisse] = reclamants.get(caisse, 0) + 1
    variantes = []
    for cas in CAS_TYPES:
        parts = tuple((caisse, 1.0 / reclamants[caisse]) for caisse in cas.caisses)
        variantes.append(Variante(cas=cas, groupe=groupe_de(cas.code),
                                  retraites=parts, cotisants=parts))
    return variantes


def poids_retraites(variantes: list[Variante], effectifs, annee: int) -> list[float]:
    return [somme_ordonnee(effectifs.effectif(caisse, annee) * part for caisse, part in v.retraites)
            for v in variantes]


def personnes(variantes: list[Variante], effectifs, source: CaracteristiquesRetraites,
              ) -> list[Variante]:
    """Les poids de PERSONNES : chaque groupe à sa part de l'EIR, l'année de
    l'enquête ; la Cnav sans les contractuels, qu'elle comptait aussi. Les
    années suivent l'évolution des caisses, le rapport de l'enquête gardé."""
    retirees = []
    for v in variantes:
        cnav = somme_ordonnee(part for caisse, part in v.retraites if caisse == "cnav")
        if cnav:
            v = replace(v, retraites=v.retraites + tuple(
                (caisse, -cnav) for caisse in CAISSES_DANS_LA_CNAV))
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


def _placer(occupes: dict[int, str], debut: int, n: int, motif: str, fin: int) -> None:
    """Place ``n`` années de ``motif`` dans les premières années libres à partir
    de ``debut``, sans passer ``fin``."""
    decalage = max(0, debut)
    while n > 0 and decalage < fin:
        if decalage not in occupes:
            occupes[decalage] = motif
            n -= 1
        decalage += 1


def _interrompre(v: Variante, nom: str, cible: int | None, part: float,
                 assimilee: float) -> Variante | None:
    """La variante dans une tranche de durée : ``cible`` années validées, dont
    une part assimilée, puis l'inactivité jusqu'au départ. ``None`` quand la
    carrière du cas type est déjà plus courte que la tranche."""
    cas = v.cas
    duree = int(round(cas.age_liquidation - cas.age_debut))
    if cible is not None and cible >= duree:
        return None
    validee = duree if cible is None else cible
    assimilees = int(round(assimilee * validee))
    occupes = {d: m for d, m in cas.interruptions_relatives if d < validee}
    _placer(occupes, (validee - assimilees) // 2, assimilees, "chomage_indemnise", validee)
    if cible is not None:
        for decalage in range(validee, int(AGE_FIN_INACTIVITE - cas.age_debut)):
            occupes[decalage] = "inactivite"
    nouveau = elargi(cas, code=f"{cas.code}~{nom}",
                     interruptions_relatives=tuple(sorted(occupes.items())))
    return v.fois(part, cas=nouveau, duree=validee, assimilees=assimilees)


def femmes(variantes: list[Variante], effectifs,
           source: CaracteristiquesRetraites) -> list[Variante]:
    """Les femmes : dans chaque groupe, la part de l'EIR, prise sur les hommes,
    chacune avec ses enfants."""
    annee = source.millesime
    poids = poids_retraites(variantes, effectifs, annee)
    femmes_cibles = parts_femmes(source)
    total: dict[str, float] = {}
    deja: dict[str, float] = {}
    for v, p in zip(variantes, poids):
        total[v.groupe] = total.get(v.groupe, 0.0) + p
        if v.cas.sexe == "F":
            deja[v.groupe] = deja.get(v.groupe, 0.0) + p
    sexuees = []
    for v in variantes:
        actuelle = deja.get(v.groupe, 0.0) / total[v.groupe]
        cible = femmes_cibles[v.groupe]
        f = 0.0 if actuelle >= cible else (cible - actuelle) / (1.0 - actuelle)
        if v.cas.sexe == "F" or f == 0.0:
            sexuees.append(v)
            continue
        cas = elargi(v.cas)
        sexuees.append(v.fois(1.0 - f, cas=replace(cas, code=f"{cas.code}~h")))
        sexuees.append(v.fois(f, cas=replace(
            cas, code=f"{cas.code}~f", sexe="F",
            nombre_enfants=max(cas.nombre_enfants, ENFANTS))))
    return sexuees


def interruptions(variantes: list[Variante], effectifs,
                  source: CaracteristiquesRetraites) -> list[Variante]:
    """Les femmes, puis, hors des régimes statutaires, les carrières courtes et
    les périodes assimilées, sexe par sexe."""
    sortie = []
    for v in femmes(variantes, effectifs, source):
        if v.groupe not in GROUPES_INTERROMPUS:
            sortie.append(v)
            continue
        tranches = parts_tranches(source, v.cas.sexe)
        assimilee = part_assimilee(source, v.cas.sexe)
        restes = 0.0
        declinees = []
        for nom, cible in TRANCHES:
            declinee = _interrompre(v, nom, cible, tranches[nom], assimilee)
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


def grille(nom: str, effectifs, source: CaracteristiquesRetraites,
           points) -> list[Variante]:
    """Les variantes d'une des grilles de ``GRILLES``."""
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

def parametres_de_la_grille(parametres: Parametres) -> Parametres:
    """Les paramètres de la page, l'ASPA retirée du scénario 1."""
    return replace(parametres, minimum_vieillesse_dans_le_scenario_actuel=False)


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
        courtes[sexe] = somme_ordonnee(p for v, p in lot if v.duree is not None and v.duree < 30) / masse
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
    courtes = {s: somme_ordonnee(source.valeur(f"part_duree_validee_hors_majoration_{t}", s)
                      for t in ("moins_10", "10_20", "20_30")) / 100 for s in ("F", "H")}
    return {"femmes": femmes, "polypensionnes": poly, "duree_validee": duree,
            "moins_de_30_ans": courtes, "groupes": parts_personnes(source)}


def processus_par_defaut() -> int:
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:       # hors de Linux
        return os.cpu_count() or 1


def mesurer(noms: tuple[str, ...] = GRILLES, processus: int = 1,
            parametres: Parametres | None = None) -> dict:
    """Chaque grille, sa composition et ce que la page y affiche, sans ASPA ;
    la page elle-même, et la grille du dépôt réécrite en parts avec l'ASPA,
    qui doit la redonner."""
    parametres = parametres if parametres is not None else Parametres()
    racine = parametres.racine_donnees
    source = eir(racine)
    annee_centiles, valeurs = centiles(racine)
    points = multiplicateurs(valeurs)
    sans_aspa = parametres_de_la_grille(parametres)
    effectifs = Simulateur(parametres).effectifs
    resultat = {
        "page": indicateurs(memoire.cout(parametres)),
        "page_en_parts": indicateurs(calculer(parametres, reference(), processus)),
        "eir": {"millesime": source.millesime, **composition_eir(source)},
        "centiles": {"annee": annee_centiles,
                     "points": [{"centile": n, "part": p, "multiplicateur": m}
                                for n, p, m in points]},
        "grilles": {},
    }
    noms = ("reference",) + tuple(n for n in noms if n != "reference")
    for nom in noms:
        debut = time.time()
        variantes = grille(nom, effectifs, source, points)
        cout = calculer(sans_aspa, variantes, processus)
        resultat["grilles"][nom] = {
            "cas_types": len(variantes),
            "secondes": round(time.time() - debut, 1),
            "composition": composition(variantes, effectifs, source),
            **indicateurs(cout),
        }
    return resultat


# -- l'impression ----------------------------------------------------------------

NUMEROS = {scenario: str(rang) for rang, (scenario, _) in enumerate(C.SCENARIOS, 1)}


def ecart_maximal(a: dict, b: dict) -> float:
    """Le plus grand écart entre deux jeux d'indicateurs."""
    return max(abs(a[s][k] - b[s][k]) for s, _ in C.SCENARIOS for k in a[s])


def imprimer(resultat: dict) -> None:
    page = resultat["page"]
    grilles = resultat["grilles"]
    base = grilles["reference"]
    eir_ = resultat["eir"]
    print(f"Ce que les treize cas types déplacent sur la page Coût "
          f"(EIR {eir_['millesime']}, centiles {resultat['centiles']['annee']})\n")
    print(f"La grille du dépôt, réécrite en parts, redonne la page à "
          f"{ecart_maximal(resultat['page_en_parts'], page):.1e} près.")
    print("Sans l'ASPA que le scénario 1 sert aux premières générations de "
          "non-salariés, l'écart passé devient :")
    print("  " + " ; ".join(
        f"sc. {NUMEROS[s]} {page[s]['ecart_passe']:.2f} → {base[s]['ecart_passe']:.2f}"
        for s, _ in C.SCENARIOS if abs(base[s]['ecart_passe'] - page[s]['ecart_passe']) > 5e-3))
    autres = max(abs(base[s][k] - page[s][k]) for s, _ in C.SCENARIOS
                 for k in page[s] if k != "ecart_passe")
    print(f"  et rien d'autre ne bouge de plus de {autres:.1e}. Les grilles se "
          "comparent à celle du dépôt sans ASPA.\n")

    print("Composition, retraités de l'année de l'enquête :")
    entete = f"{'':16}{'femmes':>8}{'poly':>7}{'durée F':>9}{'durée H':>9}{'<30 F':>7}{'<30 H':>7}"
    print(entete)
    for nom, comp in [("EIR", eir_)] + [(n, g["composition"]) for n, g in grilles.items()]:
        d, c = comp["duree_validee"], comp["moins_de_30_ans"]
        print(f"{nom:16}{comp['femmes']*100:>7.1f}%{comp['polypensionnes']*100:>6.1f}%"
              f"{d.get('F', float('nan')):>9.1f}{d.get('H', float('nan')):>9.1f}"
              f"{c.get('F', float('nan'))*100:>6.1f}%{c.get('H', float('nan'))*100:>6.1f}%")

    horizon = page["annee_horizon"]
    colonnes = (("ecart_passe", "écart passé (pts)", "notionnels"),
                ("part_pib_horizon", f"part du PIB {horizon} (pts)", "tous"),
                ("solde_moyen", "solde moyen 2026-" + str(horizon) + " (pts)", "notionnels"),
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
    analyseur.add_argument("--json", help="écrit le résultat dans ce fichier")
    arguments = analyseur.parse_args(argv)

    noms = tuple(arguments.grille) if arguments.grille else GRILLES
    resultat = mesurer(noms, arguments.processus)
    imprimer(resultat)
    if arguments.json:
        Path(arguments.json).write_text(json.dumps(resultat, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
