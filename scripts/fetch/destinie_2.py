#!/usr/bin/env python3
"""Témoin de Destinie 2 (INSEE), exécuté à part, sur des carrières écrites des deux côtés.

    python scripts/fetch/destinie_2.py            # refait tests/temoins/destinie_2.json
    python scripts/fetch/destinie_2.py --lister   # les cas, sans rien exécuter

À quoi il sert. Destinie 2 est le modèle de microsimulation de l'INSEE, celui
qui projette la France pour le Conseil d'orientation des retraites et pour
l'Ageing Report : une seconde implémentation du droit, écrite par d'autres, et
la seule du registre (`data/reference/referents.yaml`, `destinie_2`) qui porte
la réversion du régime général entière et l'allocation de solidarité du
ménage. Ce n'est PAS une source officielle : un désaccord ne désigne pas
d'office le coupable, et le registre en a déjà tranché onze contre lui.

Ce qu'il fait. Il décrit des cas — une carrière année par année, ses enfants,
un conjoint, un décès —, et les écrit DEUX FOIS : en requête du simulateur du
dépôt (le relevé de carrière du formulaire, en euros de chaque année), et en
tables de Destinie (`ech`, `emp`, `fam`, `union_base`, `union`). Il lance
`destinie_2.R` dans R, deux fois — Destinie tel quel, puis sans les
majorations de pension pour trois enfants (NoBonif), dont l'écart dit ce
qu'elles valent dans chaque régime —, et fige ses sorties dans
`tests/temoins/destinie_2.json`, avec la version, le commit, la date et la
législation retenue. `tests/test_destinie.py` y confronte le scénario 1, sans R.

Ce qu'il ne fait pas. Le code de Destinie 2 n'entre jamais au dépôt : il est
sous GPL-3.0 (paramètres sous ODbL et DbCL), et le copier ferait passer le
dépôt sous sa licence (`docs/architecture.md`, § 3.4). Il s'installe à part —
dans la distribution Ubuntu de la WSL sur le poste du propriétaire —, et seules
ses sorties entrent ici, leur origine et leur licence dites dans le témoin.

LA POPULATION N'EST PAS SIMULÉE. Ni naissances, ni décès tirés au hasard, ni
transitions sur le marché du travail, ni salaires imputés : `destinieSim` ne
fait que liquider ce que les tables écrites ici décrivent. Chacun part au taux
plein (le comportement par défaut de Destinie), que chaque carrière atteint à
son âge d'ouverture des droits : c'est la date de la requête du dépôt.

LES CARRIÈRES S'ARRÊTENT D'ORDINAIRE AU 31 DÉCEMBRE QUI PRÉCÈDE LE DÉPART.
L'année du départ n'est alors travaillée dans aucun des deux modèles — le dépôt
la prolongerait au rythme du salaire moyen : l'interruption « sans_activite »
de cette année-là le lui interdit —, pour que la confrontation porte sur les
règles, pas sur deux conventions de l'année incomplète. Seuls les deux cas de
la loi de 2023 travaillent jusqu'au départ, faute de quoi il leur manquerait
le 169e trimestre ; leur relevé porte ce qui est gagné avant lui.

Installation de Destinie 2, sur le poste, une fois (voir le témoin pour le
commit) : télécharger l'archive du dépôt de l'INSEE au commit voulu dans
`~/modeles/Destinie-2`, puis `R CMD INSTALL` dans la bibliothèque de
l'utilisateur, après `install.packages("xlsx")` (qui exige Java et rJava).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.carriere import salaire_moyen_annuel  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

SORTIE = RACINE / "tests" / "temoins" / "destinie_2.json"
SCRIPT_R = Path(__file__).resolve().with_suffix(".R")

#: Le modèle, tel qu'il a été téléchargé et installé (voir l'en-tête).
DEPOT_DESTINIE = "https://github.com/InseeFr/Destinie-2"
COMMIT = "4c1d34ba2d2f26a99cfd08a883850cad5af18bc0"
LICENCE = "GPL-3.0 ou ultérieure ; paramètres sous ODbL et DbCL"

#: La législation : la plus récente que Destinie 2 porte, la loi du 14 avril
#: 2023 (`an_leg >= 2023` dans `src/Legislation.cpp`). Il n'a pas la loi du 30
#: décembre 2025, qui suspend la réforme à partir de la génération 1964 : aucun
#: cas n'en est.
AN_LEG = 2023
#: Le comportement de départ : `comp_tp` (0), le départ au taux plein, celui
#: de la démonstration du paquet. Chaque cas atteint le taux plein à son âge
#: d'ouverture des droits, et c'est la date de sa requête. `comp_exo` (3), qui
#: semblerait plus direct, ne liquide pas : sa branche de `TestLiq` rend vrai
#: sans appeler `Liq()` (`src/OutilsComp.cpp`), et la pension attend une
#: « seconde liquidation » d'un trimestre, ou ne vient jamais sous décote.
COMPORTEMENT = 0
#: La fin de la simulation : les départs sont de 2015 à 2024, les réversions
#: de 2023.
AN_MAX = 2025
#: Les hypothèses du COR que le paquet livre (COR_2023), scénario central de
#: productivité et de chômage. Elles ne jouent qu'au-delà des séries observées.
SCENARIO = {"scenario_productivite": "1,0%", "scenario_chomage": "7%"}
#: Les deux exécutions, et l'option de Destinie que chacune neutralise. La
#: majoration de durée d'assurance se lit sans relancer : Destinie écrit les
#: durées avec et sans elle (`duree_tot`, `duree_tot_maj`) ; la neutraliser
#: déplacerait le départ au taux plein, et la pension ne se comparerait plus.
VARIANTES = {"base": [], "sans_majoration": ["NoBonif"]}
#: Les paramètres que le témoin recopie, pour expliquer un écart de montant
#: sans relancer R.
PARAMETRES = (
    "PlafondSS", "SMIC", "SMPT", "Prix", "PointFP", "RevaloRG", "RevaloFP", "RevaloSPC",
    "TauxARRCO_1", "TauxARRCO_2", "TauxAGIRC_B", "TauxAGIRC_ARRCO_1", "TauxAGIRC_ARRCO_2",
    "SalRefARRCO", "SalRefAGIRC", "SalRefAGIRC_ARRCO",
    "ValPtARRCO", "ValPtAGIRC", "ValPtAGIRC_ARRCO",
    "Mincont1", "Mincont2", "MinVieil1", "MinVieil2", "TauxRevRG", "MinRevRG",
    "MaxRevRG", "PlafRevRG", "PlafMajoRevRG", "TauxRevARRCO", "TauxRevFP",
    "CoefMdaRG", "CoefMdaFP", "SalValid",
)
#: Les années des carrières, de dix en dix, et chacune des dernières : de quoi
#: lire les taux d'acquisition des points et les revalorisations récentes.
ANNEES_PARAMETRES = (1970, 1976, 1980, 1985, 1990, 1995, 1999, 2005, 2010,
                     *range(2014, AN_MAX + 1))

#: Les statuts de Destinie (`src/Constantes.h`) des statuts du dépôt.
STATUTS = {
    "salarie_prive_non_cadre": 1,      # S_NC
    "salarie_prive_cadre": 2,          # S_CAD
    "fonctionnaire_etat": 321,         # S_FPSE, fonction publique d'État sédentaire
    "fonctionnaire_territorial_hospitalier": 322,  # S_FPSTH
}
SCOLARITE, INACTIF = 63, 6
#: `typeFP` de Destinie : 0 État, 1 territoriale ou hospitalière, 2 hors de la
#: fonction publique.
TYPE_FP = {"fonctionnaire_etat": 0, "fonctionnaire_territorial_hospitalier": 1}
CELIBATAIRE, MARIE, VEUF = 1, 2, 3
#: L'année de base de l'échantillon de Destinie (`AN_BASE`, 2017) : les états
#: familiaux antérieurs y sont lus.
ANNEE_BASE = 2017


@dataclass(frozen=True)
class Periode:
    """Des années civiles d'un même statut, à un niveau de revenu : un multiple
    du salaire moyen de chaque année, que le témoin recopie en euros."""

    debut: int
    fin: int
    statut: str
    niveau: float


@dataclass(frozen=True)
class Personne:
    sexe: str
    naissance: str                   # AAAA-MM-JJ
    periodes: tuple[Periode, ...] = ()
    deces: str | None = None         # AAAA-MM-JJ
    #: Part des primes dans la rémunération d'un fonctionnaire.
    primes: float = 0.0

    @property
    def annee(self) -> int:
        return int(self.naissance[:4])

    @property
    def mois(self) -> int:
        return int(self.naissance[5:7])


@dataclass(frozen=True)
class Cas:
    code: str
    objet: str
    assure: Personne
    #: Le départ de l'assuré (AAAA-MM) : le premier jour du mois qui suit son
    #: âge d'ouverture des droits, où il a le taux plein.
    depart: str
    enfants: tuple[str, ...] = ()
    conjoint: Personne | None = None
    mariage: str | None = None
    #: Travaille-t-il jusqu'à son départ ? Sinon, sa carrière s'arrête au 31
    #: décembre qui le précède.
    travaille_l_annee_du_depart: bool = False


def _prive(debut: int, fin: int, niveau: float, cadre: bool = False) -> Periode:
    return Periode(debut, fin, "salarie_prive_cadre" if cadre else "salarie_prive_non_cadre",
                   niveau)


def _etat(debut: int, fin: int, niveau: float = 1.1) -> Periode:
    return Periode(debut, fin, "fonctionnaire_etat", niveau)


# Tous sont nés un 15 JANVIER, sauf un. Destinie compte la surcote de l'année
# civile où tombe l'âge d'ouverture sans regarder le mois de naissance
# (`DroitsRetr::DecoteSurcote`) : né en octobre 1961, il prête trois trimestres
# de surcote à qui part à 62 ans et 3 mois en février 2024 sans avoir travaillé
# un jour après cet âge. Né en janvier, l'âge d'ouverture tombe au début de
# l'année civile, et l'approximation ne joue plus ; le cas `rg_ne_en_octobre`
# la montre, seul.

# Les survivantes ont liquidé leur propre pension avant le décès : sans quoi
# Destinie compte deux fois la réversion du régime général dans leurs
# ressources (écart du registre), et la confrontation mesurerait cela.

#: Une femme née en 1953, dix années d'emploi, partie à l'âge d'annulation de la
#: décote (66 ans et 2 mois) en 2019 : des ressources faibles, sous le plafond de
#: la réversion même quand Destinie y compte celle de l'Agirc-Arrco.
SURVIVANTE_AGEE = Personne("F", "1953-01-15", (_prive(1973, 1982, 0.5),))
#: Une femme née en 1960, quarante-deux années au tiers du salaire moyen, partie
#: à 62 ans en février 2022 : sa pension, au minimum contributif, approche le
#: plafond de la réversion.
SURVIVANTE = Personne("F", "1960-01-15", (_prive(1980, 2021, 0.3),))
#: Une femme née en 1975, sans activité, mère de deux enfants à charge au décès.
SURVIVANTE_JEUNE = Personne("F", "1975-01-15")
#: Le défunt type : un salarié né en 1956, quarante-deux années au salaire
#: moyen, parti à 62 ans en février 2018 — avant le coefficient de solidarité de
#: l'Agirc-Arrco, né pour les départs de 2019 —, mort en janvier 2023.
DEFUNT_PRIVE = Personne("H", "1956-01-15", (_prive(1976, 2017, 1.0),), deces="2023-01-15")
#: La petite pension : un salarié né en 1950, vingt années à 0,4 salaire moyen,
#: parti au taux plein à 65 ans en février 2015, mort en janvier 2023.
DEFUNT_PETITE_PENSION = Personne("H", "1950-01-15", (_prive(1970, 1989, 0.4),),
                                 deces="2023-01-15")
DEFUNT_FONCTIONNAIRE = Personne("H", "1956-01-15", (_etat(1976, 2017),),
                                deces="2023-01-15", primes=0.2)
ENFANTS_1956 = ("1981-03-15", "1984-06-15", "1987-09-15")

CAS: tuple[Cas, ...] = (
    # Le droit direct, parti en février 2018 à 62 ans : les séries de 2018 sont
    # observées des deux côtés, les points de l'Arrco et de l'Agirc gelés.
    Cas("rg_salaire_moyen",
        "droit direct : régime général et Arrco, taux plein à l'âge d'ouverture",
        Personne("H", "1956-01-15", (_prive(1976, 2017, 1.0),)), "2018-02"),
    Cas("rg_cadre",
        "droit direct : salaire au-dessus du plafond, Arrco et Agirc",
        Personne("H", "1956-01-15", (_prive(1976, 2017, 2.2, cadre=True),)), "2018-02"),
    Cas("rg_bas_salaire",
        "droit direct : le minimum contributif",
        Personne("H", "1956-01-15", (_prive(1976, 2017, 0.4),)), "2018-02"),
    Cas("rg_mere_trois_enfants",
        "majorations pour enfants : la durée d'assurance de la mère, qui lui donne le "
        "taux plein ; 10 % au régime général, à l'Arrco et à l'Agirc",
        Personne("F", "1956-01-15", (_prive(1976, 1983, 0.8), _prive(1990, 2017, 0.8))),
        "2018-02", enfants=ENFANTS_1956),
    Cas("rg_pere_trois_enfants",
        "majorations pour enfants : le père, 10 % au régime général et à l'Arrco",
        Personne("H", "1956-01-15", (_prive(1976, 2017, 1.0),)), "2018-02",
        enfants=ENFANTS_1956),
    Cas("fp_etat",
        "droit direct : pension civile d'un sédentaire de l'État",
        Personne("H", "1956-01-15", (_etat(1976, 2017),), primes=0.2), "2018-02"),
    Cas("fp_mere_deux_enfants",
        "majorations pour enfants : la bonification de la mère fonctionnaire, qui "
        "compte à la liquidation",
        Personne("F", "1956-01-15", (_etat(1978, 2017),), primes=0.2), "2018-02",
        enfants=("1982-03-15", "1985-06-15")),
    Cas("fp_pere_trois_enfants",
        "majorations pour enfants : 10 % de la pension civile",
        Personne("H", "1956-01-15", (_etat(1976, 2017),), primes=0.2), "2018-02",
        enfants=ENFANTS_1956),
    # Le seul né en octobre : l'âge d'ouverture de 62 ans et 3 mois tombe en
    # janvier 2024, et Destinie compte trois trimestres de surcote sur 2023.
    Cas("rg_ne_en_octobre",
        "droit direct : né en octobre 1961, aucun trimestre après l'âge d'ouverture",
        Personne("H", "1961-10-15", (_prive(1981, 2023, 1.0),)), "2024-02"),
    # La loi du 14 avril 2023 : né en janvier 1962, 62 ans et 6 mois et 169
    # trimestres ; il travaille jusqu'à son départ, en août 2024, pour les avoir.
    Cas("loi_2023_salaire_moyen",
        "droit direct sous la loi du 14 avril 2023 : 62 ans et 6 mois, 169 trimestres",
        Personne("H", "1962-01-15", (_prive(1982, 2024, 1.0),)), "2024-08",
        travaille_l_annee_du_depart=True),
    Cas("loi_2023_fp_etat",
        "pension civile sous la loi du 14 avril 2023",
        Personne("H", "1962-01-15", (_etat(1982, 2024),), primes=0.2), "2024-08",
        travaille_l_annee_du_depart=True),
    # Les réversions d'un décès de janvier 2023 : montants de 2023.
    Cas("reversion_rg",
        "réversion : 54 % au régime général, 60 % à l'Agirc-Arrco",
        DEFUNT_PRIVE, "2018-02", enfants=("1978-04-15", "1981-07-15"),
        conjoint=SURVIVANTE_AGEE, mariage="1976-06-15"),
    Cas("reversion_trois_enfants",
        "réversion : la survivante de trois enfants",
        DEFUNT_PRIVE, "2018-02", enfants=("1978-04-15", "1981-07-15", "1984-10-15"),
        conjoint=SURVIVANTE_AGEE, mariage="1976-06-15"),
    Cas("reversion_plafond",
        "réversion : des ressources près du plafond, et ce qui y compte",
        DEFUNT_PRIVE, "2018-02", enfants=("1982-04-15", "1985-07-15"),
        conjoint=SURVIVANTE, mariage="1980-06-15"),
    Cas("reversion_jeune_deux_enfants",
        "réversion : une survivante de 48 ans, deux enfants à charge",
        DEFUNT_PRIVE, "2018-02", enfants=("2005-03-15", "2008-06-15"),
        conjoint=SURVIVANTE_JEUNE, mariage="2003-06-15"),
    Cas("reversion_minimum",
        "réversion : une petite pension, sous le minimum de réversion",
        DEFUNT_PETITE_PENSION, "2015-02", enfants=("1982-04-15", "1985-07-15"),
        conjoint=SURVIVANTE, mariage="1980-06-15"),
    Cas("reversion_minimum_age",
        "réversion : la même, à une survivante passée l'âge d'annulation de la décote",
        DEFUNT_PETITE_PENSION, "2015-02", enfants=("1975-04-15", "1978-07-15"),
        conjoint=SURVIVANTE_AGEE, mariage="1974-06-15"),
    Cas("reversion_fonctionnaire",
        "réversion : la moitié de la pension civile",
        DEFUNT_FONCTIONNAIRE, "2018-02", enfants=("1982-04-15", "1985-07-15"),
        conjoint=SURVIVANTE, mariage="1980-06-15"),
)


# ---------------------------------------------------------------------------
# Les revenus, en euros de chaque année
# ---------------------------------------------------------------------------

def revenus(personne: Personne, macro) -> dict[int, tuple[str, int]]:
    """Le statut et le revenu brut de chaque année travaillée, en euros de
    l'année : le niveau de la période fois le salaire moyen du dépôt."""
    annees: dict[int, tuple[str, int]] = {}
    for periode in personne.periodes:
        for annee in range(periode.debut, periode.fin + 1):
            if annee in annees:
                raise ValueError(f"{annee} : deux périodes la couvrent")
            annees[annee] = (periode.statut,
                             round(periode.niveau * salaire_moyen_annuel(macro, annee)))
    return dict(sorted(annees.items()))


def requete(cas: Cas, macro, ressources_conjoint: float | None = None) -> dict[str, str]:
    """La requête du simulateur du dépôt : le relevé de carrière du formulaire,
    les enfants, le conjoint et le décès.

    L'année du départ : travaillée, le relevé en porte ce qui est gagné avant
    lui, au prorata de ses mois — Destinie, qui lit le salaire de l'année
    entière, en compte de même les trimestres et les points jusqu'à la date ;
    non travaillée, elle est déclarée sans activité, sans quoi le dépôt
    prolongerait le relevé jusqu'au départ."""
    assure = cas.assure
    annees = revenus(assure, macro)
    annee_depart, mois_depart = int(cas.depart[:4]), int(cas.depart[5:7])
    lignes = []
    for annee, (statut, montant) in annees.items():
        if annee == annee_depart:
            if not cas.travaille_l_annee_du_depart:
                raise ValueError(f"{cas.code} : {annee} est travaillée, le départ y tombe")
            montant = round(montant * (mois_depart - 1) / 12)
        lignes.append(f"{annee}:{statut}:{montant}")
    demande = {
        "naissance": assure.naissance,
        "sexe": assure.sexe,
        "liquidation": cas.depart,
        "releve": ",".join(lignes),
    }
    if mois_depart > 1 and not cas.travaille_l_annee_du_depart:
        demande["interruptions"] = f"{annee_depart}:{annee_depart}:sans_activite"
    if assure.primes:
        demande["primes"] = f"{assure.primes:g}"
    if cas.enfants:
        demande["enfants"] = str(len(cas.enfants))
        demande["naissances"] = ",".join(cas.enfants)
    if cas.conjoint is not None:
        demande["conjoint"] = cas.conjoint.naissance
        demande["conjoint_sexe"] = cas.conjoint.sexe
        if cas.mariage:
            demande["mariage"] = cas.mariage
        if ressources_conjoint is not None:
            demande["ressources_conjoint"] = f"{round(ressources_conjoint)}"
    if assure.deces:
        demande["deces"] = assure.deces
    return demande


# ---------------------------------------------------------------------------
# Les tables de Destinie
# ---------------------------------------------------------------------------

@dataclass
class Individu:
    ident: int
    personne: Personne
    role: str
    cas: str
    pere: int = 0
    mere: int = 0
    enfants: list[int] = field(default_factory=list)
    conjoint: int = 0


def _derniere_annee(personne: Personne) -> int:
    """La dernière année où la personne est présente : celle qui précède son
    décès, la fin de la simulation sinon."""
    if personne.deces:
        return int(personne.deces[:4]) - 1
    return AN_MAX + 1


def population(cas_: tuple[Cas, ...]) -> tuple[list[Individu], dict[str, dict[str, int]]]:
    """Les individus, numérotés de 1 sans trou comme Destinie l'exige, et, cas
    par cas, l'identifiant de chaque rôle."""
    individus: list[Individu] = []
    roles: dict[str, dict[str, int]] = {}

    def ajouter(personne: Personne, role: str, code: str) -> Individu:
        individu = Individu(len(individus) + 1, personne, role, code)
        individus.append(individu)
        roles.setdefault(code, {})[role] = individu.ident
        return individu

    for cas in cas_:
        assure = ajouter(cas.assure, "assure", cas.code)
        conjoint = ajouter(cas.conjoint, "conjoint", cas.code) if cas.conjoint else None
        if conjoint is not None:
            assure.conjoint, conjoint.conjoint = conjoint.ident, assure.ident
        for rang, naissance in enumerate(cas.enfants, start=1):
            sexe = "H" if rang % 2 else "F"
            enfant = ajouter(Personne(sexe, naissance), f"enfant{rang}", cas.code)
            # Les enfants d'un couple sont les siens : c'est la seule
            # configuration que la requête du dépôt sait dire.
            parents = [assure] + ([conjoint] if conjoint is not None else [])
            for parent in parents:
                parent.enfants.append(enfant.ident)
                if parent.personne.sexe == "H":
                    enfant.pere = parent.ident
                else:
                    enfant.mere = parent.ident
    return individus, roles


def tables(individus: list[Individu], cas_: tuple[Cas, ...], macro) -> dict[str, list[dict]]:
    """ech, emp, fam, union_base et union, triées comme Destinie les lit."""
    par_code = {cas.code: cas for cas in cas_}
    ech, emp, fam, union_base, union = [], [], [], [], []
    for individu in individus:
        personne = individu.personne
        annees = revenus(personne, macro)
        debut = min(annees) if annees else None
        findet = (debut - personne.annee) if debut else 20
        primes = personne.primes
        statut_fp = next((s for s, _ in annees.values() if s in TYPE_FP), None)
        ech.append({
            "Id": individu.ident, "sexe": 1 if personne.sexe == "H" else 2,
            "anaiss": personne.annee, "moisnaiss": personne.mois - 1, "findet": findet,
            "neFrance": 1, "emigrant": 0,
            "typeFP": TYPE_FP.get(statut_fp, 2), "peudip": 0, "tresdip": 0, "dipl": 3,
            # Destinie divise la rémunération par (1 + taux_prim) : un taux de
            # primes rapporté au traitement, quand le dépôt en dit la part.
            "taux_prim": primes / (1 - primes) if primes else 0.0, "k": 0.0,
        })
        for age in range(0, _derniere_annee(personne) - personne.annee + 1):
            annee = personne.annee + age
            if annee in annees:
                statut, montant = annees[annee]
                emp.append({"Id": individu.ident, "age": age, "statut": STATUTS[statut],
                            "salaire": float(montant)})
            else:
                emp.append({"Id": individu.ident, "age": age,
                            "statut": SCOLARITE if age < findet else INACTIF,
                            "salaire": 0.0})
        enfants = individu.enfants + [0] * (6 - len(individu.enfants))
        ligne = {"Id": individu.ident, "annee": ANNEE_BASE, "pere": individu.pere,
                 "mere": individu.mere,
                 "matri": MARIE if individu.conjoint else CELIBATAIRE,
                 "conjoint": individu.conjoint,
                 **{f"enf{rang}": ident for rang, ident in enumerate(enfants, start=1)}}
        fam.append(ligne)
        cas = par_code[individu.cas]
        # Le survivant devient veuf l'année du décès, son conjoint gardé : c'est
        # ce que la démographie de Destinie écrit (`src/Mortalite.cpp`).
        if individu.role == "conjoint" and cas.assure.deces:
            fam.append({**ligne, "annee": int(cas.assure.deces[:4]), "matri": VEUF})
        if individu.role == "assure" and individu.conjoint:
            mariage = int(cas.mariage[:4])
            union_base.append({"Id1": individu.ident, "Id2": individu.conjoint,
                               "annee_union": mariage})
            fin_assure = int(personne.deces[:4]) if personne.deces else 9999
            fin_conjoint = int(cas.conjoint.deces[:4]) if cas.conjoint.deces else 9999
            union.append({"Id1": individu.ident, "Id2": individu.conjoint,
                          "t_ageMax1": fin_assure, "t_ageMax2": fin_conjoint,
                          "annee_union": mariage,
                          "duree_union": min(fin_assure, fin_conjoint, AN_MAX) - mariage,
                          "nb_enf": len(individu.enfants)})
    return {"ech": ech, "emp": emp, "fam": fam, "union_base": union_base, "union": union}


def _ecrire_csv(chemin: Path, lignes: list[dict], colonnes: list[str]) -> None:
    with chemin.open("w", newline="", encoding="utf-8") as flux:
        ecrivain = csv.DictWriter(flux, fieldnames=colonnes, lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


COLONNES = {
    "ech": ["Id", "sexe", "anaiss", "moisnaiss", "findet", "neFrance", "emigrant",
            "typeFP", "peudip", "tresdip", "dipl", "taux_prim", "k"],
    "emp": ["Id", "age", "statut", "salaire"],
    "fam": ["Id", "annee", "pere", "mere", "matri", "conjoint",
            "enf1", "enf2", "enf3", "enf4", "enf5", "enf6"],
    "union_base": ["Id1", "Id2", "annee_union"],
    "union": ["Id1", "Id2", "t_ageMax1", "t_ageMax2", "annee_union", "duree_union", "nb_enf"],
}


# ---------------------------------------------------------------------------
# L'exécution, dans R
# ---------------------------------------------------------------------------

def chemin_wsl(chemin: Path) -> str:
    """Le chemin d'un fichier Windows vu de la WSL (`/mnt/c/…`)."""
    absolu = chemin.resolve()
    lecteur = absolu.drive.rstrip(":").lower()
    return f"/mnt/{lecteur}" + absolu.as_posix()[len(absolu.drive):]


def commande_r(distribution: str | None) -> tuple[list[str], callable]:
    """Rscript, directement ou par la WSL, et la façon d'y écrire un chemin."""
    if distribution:
        return ["wsl", "-d", distribution, "--exec", "Rscript"], chemin_wsl
    return ["Rscript"], lambda chemin: str(chemin)


def executer(dossier: Path, distribution: str | None) -> dict[str, dict]:
    """Les trois exécutions, chacune dans son processus ; leurs sorties lues."""
    rscript, chemin = commande_r(distribution)
    sorties = {}
    for variante in VARIANTES:
        sortie = dossier / f"sorties_{variante}"
        commande = rscript + [chemin(SCRIPT_R), chemin(dossier), chemin(sortie), variante]
        print(f"Destinie 2, variante « {variante} »…", flush=True)
        fini = subprocess.run(commande, capture_output=True, text=True, encoding="utf-8",
                              errors="replace")
        if fini.returncode != 0:
            raise RuntimeError(f"Destinie 2 a échoué (variante {variante}) :\n"
                               f"{fini.stdout[-3000:]}\n{fini.stderr[-3000:]}")
        sorties[variante] = {
            "liquidations": _lire_csv(sortie / "liquidations.csv"),
            "retraites": _lire_csv(sortie / "retraites.csv"),
            "parametres": _lire_csv(sortie / "parametres.csv"),
            "versions": json.loads((sortie / "versions.json").read_text(encoding="utf-8")),
        }
    return sorties


def _nombre(texte: str):
    if texte in ("", "NA"):
        return None
    if texte in ("TRUE", "FALSE"):
        return texte == "TRUE"
    valeur = float(texte)
    return int(valeur) if valeur.is_integer() else valeur


def _lire_csv(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as flux:
        return [{cle: _nombre(valeur) for cle, valeur in ligne.items()}
                for ligne in csv.DictReader(flux)]


# ---------------------------------------------------------------------------
# Le témoin
# ---------------------------------------------------------------------------

#: Ce que le témoin garde de la liquidation : durées en années (le trimestre
#: vaut 0,25), taux, salaires de référence, points, pensions annuelles brutes
#: en euros de l'année du départ.
LIQUIDATION = (
    "annee", "agetest", "ageliq", "t", "type_liq", "duree_rg", "duree_fp", "duree_tot",
    "duree_rg_maj", "duree_fp_maj", "duree_tot_maj", "durdecote_rg", "dursurcote_rg",
    "durdecote_fp", "dursurcote_fp", "tauxliq_rg", "tauxliq_fp", "tauxliq_ar",
    "taux_prorat_rg", "taux_prorat_fp", "sam_rg", "sam_rgin", "sr_fp", "points_arrco",
    "points_agirc", "points_agirc_arrco", "coeffTemp", "min_cont", "min_garanti",
    "majo_min_rg", "majo_min_fp", "majo_3enf_rg", "majo_3enf_ar", "majo_3enf_ag",
    "majo_3enf_fp", "pension_rg", "pension_ar", "pension_ag", "pension_ag_ar",
    "pension_fp", "pension",
)
#: Ce qu'il garde des pensions servies, l'année d'une réversion.
SERVIES = ("annee", "age", "pension", "pension_rg", "pension_fp", "pension_ar",
           "pension_ag", "pension_ag_ar", "rev", "rev_rg", "rev_fp", "rev_ar", "rev_ag",
           "min_vieil")


def _par_id(lignes: list[dict]) -> dict[int, list[dict]]:
    groupes: dict[int, list[dict]] = {}
    for ligne in lignes:
        groupes.setdefault(int(ligne["Id"]), []).append(ligne)
    return groupes


def _liquidation(lignes: list[dict]) -> dict | None:
    if not lignes:
        return None
    ligne, = lignes
    return {cle: ligne[cle] for cle in LIQUIDATION}


def _servie(lignes: list[dict], annee: int) -> dict | None:
    for ligne in lignes:
        if ligne["annee"] == annee:
            servie = {cle: ligne[cle] for cle in SERVIES}
            # Destinie n'écrit pas la réversion de l'Agirc-Arrco unifiée à
            # part : elle est le reste du total.
            servie["rev_ag_ar"] = round(ligne["rev"] - sum(
                ligne[c] for c in ("rev_rg", "rev_fp", "rev_in", "rev_ar", "rev_ag")), 6)
            return servie
    return None


def temoin(sorties: dict[str, dict], roles: dict[str, dict[str, int]], macro) -> dict:
    base = sorties["base"]
    liquidations = {v: _par_id(s["liquidations"]) for v, s in sorties.items()}
    retraites = {v: _par_id(s["retraites"]) for v, s in sorties.items()}
    cas_temoins = {}
    for cas in CAS:
        ids = roles[cas.code]
        assure = ids["assure"]
        resultat = {
            "objet": cas.objet,
            "destinie": {
                "liquidation": _liquidation(liquidations["base"].get(assure, [])),
                "sans_majoration": _liquidation(
                    liquidations["sans_majoration"].get(assure, [])),
            },
        }
        ressources = None
        if cas.assure.deces and cas.conjoint is not None:
            annee = int(cas.assure.deces[:4])
            survivant = ids["conjoint"]
            servie = _servie(retraites["base"].get(survivant, []), annee)
            resultat["destinie"]["survivant"] = servie
            resultat["destinie"]["survivant_sans_majoration"] = _servie(
                retraites["sans_majoration"].get(survivant, []), annee)
            resultat["destinie"]["defunt_servi_l_annee_d_avant"] = _servie(
                retraites["base"].get(assure, []), annee - 1)
            # Les ressources du survivant, dans le dépôt : ses propres pensions,
            # celles que Destinie lui sert cette année-là.
            ressources = servie["pension"] if servie else 0.0
        resultat["requete"] = requete(cas, macro, ressources)
        cas_temoins[cas.code] = resultat
    parametres = {str(ligne["annee"]): {cle: valeur for cle, valeur in ligne.items()
                                         if cle != "annee"}
                  for ligne in base["parametres"]}
    return {
        "modele": "Destinie 2",
        "auteur": "INSEE",
        "code": DEPOT_DESTINIE,
        "commit": COMMIT,
        "version": base["versions"]["destinie"],
        "licence": LICENCE,
        "origine": (
            "Sorties de Destinie 2, exécuté à part par scripts/fetch/destinie_2.py et "
            "destinie_2.R ; le code de Destinie n'entre pas au dépôt. Les chiffres "
            "ci-dessous sont ses résultats, publiés sous sa licence, avec leur origine."
        ),
        "execute_le": dt.date.today().isoformat(),
        "environnement": base["versions"],
        "legislation": {
            "anLeg": AN_LEG,
            "dit": ("la plus récente que Destinie 2 porte : la loi du 14 avril 2023, sans "
                    "la loi du 30 décembre 2025"),
        },
        "options": {"AN_MAX": AN_MAX, "comp": COMPORTEMENT,
                    "NoRegUniqAgircArrco": False, "SecondLiq": False,
                    "hypotheses_cor": "COR_2023", **SCENARIO,
                    "variantes": VARIANTES},
        "conventions": {
            "durees": "en années ; le trimestre vaut 0,25",
            "montants": ("pensions annuelles brutes, en euros de l'année de la liquidation ; "
                         "servies et réversions, en euros de l'année dite"),
            "revenus": ("relevé de la requête : niveau de la période fois le salaire moyen "
                        "annuel du dépôt, arrondi à l'euro, écrit tel quel dans les deux "
                        "modèles"),
        },
        "parametres_destinie": parametres,
        "cas": cas_temoins,
    }


def _ecrire(document: dict) -> None:
    texte = json.dumps(document, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_bytes(texte.encode("utf-8"))


def main(arguments: list[str] | None = None) -> int:
    lecteur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    lecteur.add_argument("--wsl", default="Ubuntu", metavar="DISTRIBUTION",
                         help="la distribution de la WSL où R est installé ; "
                              "« aucune » pour lancer Rscript directement")
    lecteur.add_argument("--lister", action="store_true",
                         help="imprime les cas et leurs requêtes, sans rien exécuter")
    lecteur.add_argument("--garder", action="store_true",
                         help="garde le dossier des tables et des sorties de R")
    options = lecteur.parse_args(arguments)
    macro = Simulateur().macro
    if options.lister:
        for cas in CAS:
            print(f"{cas.code} : {cas.objet}")
            print(f"    {json.dumps(requete(cas, macro), ensure_ascii=False)[:300]}…")
        return 0
    distribution = None if options.wsl in ("", "aucune") else options.wsl
    if distribution is None and shutil.which("Rscript") is None:
        print("Rscript est introuvable : installer R et Destinie 2 (voir l'en-tête).",
              file=sys.stderr)
        return 1
    individus, roles = population(CAS)
    dossier = Path(tempfile.mkdtemp(prefix="destinie_2_"))
    try:
        for nom, lignes in tables(individus, CAS, macro).items():
            _ecrire_csv(dossier / f"{nom}.csv", lignes, COLONNES[nom])
        (dossier / "options.json").write_bytes(json.dumps({
            "anLeg": AN_LEG, "AN_MAX": AN_MAX, "comp": COMPORTEMENT,
            "variantes": VARIANTES, "parametres": list(PARAMETRES),
            "annees_parametres": list(ANNEES_PARAMETRES), **SCENARIO,
        }, ensure_ascii=False).encode("utf-8"))
        sorties = executer(dossier, distribution)
    finally:
        if options.garder:
            print(f"Tables et sorties gardées dans {dossier}")
        else:
            shutil.rmtree(dossier, ignore_errors=True)
    document = temoin(sorties, roles, macro)
    _ecrire(document)
    print(f"{SORTIE} : {len(document['cas'])} cas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
