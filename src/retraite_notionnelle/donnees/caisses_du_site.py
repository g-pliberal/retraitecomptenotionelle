"""Les caisses de la page « Les caisses » : ce que le site montre de chacune.

Demandée par le propriétaire le 17 novembre 2026 (action 193). Le site montre,
pour chaque grande caisse de retraite, combien de cotisants paient pour un
retraité, d'où vient son argent, ses réserves et, pour une caisse en points,
le prix et la valeur du point. Ce module lit ces chiffres dans les fichiers du
dépôt qui les portent, à une année fixe chacun, et les rend au paquet du site
(``scripts/construire_donnees.py``, clé ``caisses``) ; le texte de la page,
lui, est dans ``moteur/js/pages.js``.

LES ANNÉES. Les effectifs sont ceux de 2024 et le financement celui de 2023,
tous deux des compléments du rapport du COR de juin 2024, le seul millésime
qui les ventile par caisse ; les réserves, celles de fin 2025 (rapport du COR
de juin 2026, tableau 2.3) ; le point, celui de 2026.

LES POSTES DU FINANCEMENT, regroupés en six pour un lecteur : les cotisations ;
les impôts et taxes affectés ; l'État, qu'il verse comme employeur
(contribution d'équilibre) ou comme garant (subvention) ; les autres caisses,
par les transferts et la compensation démographique ; les placements et le
reste (autres produits) ; et ce que personne ne finance (besoin de
financement). Les parts sont rendues telles que publiées, sans les ramener à un.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from ..somme import somme_ordonnee

ANNEE_EFFECTIFS = 2024
ANNEE_FINANCEMENT = 2023
ANNEE_POINT = 2026

#: Les postes du COR, et le poste du site où chacun va.
POSTES = {
    "cotisations": "cotisations",
    "impots_et_taxes": "impots",
    "contribution_equilibre_etat": "etat",
    "subventions_equilibre": "etat",
    "transferts": "autres_caisses",
    "compensation_demographique": "autres_caisses",
    "autres_produits": "placements_et_divers",
    "besoin_de_financement": "non_finance",
}


@dataclass(frozen=True)
class Caisse:
    """Une caisse de la page, et ses codes dans chacun des fichiers."""

    ident: str
    #: Ses codes dans ``cotisants.csv`` et ``retraites_projetes.csv``.
    effectifs: tuple[str, ...]
    #: Son code dans ``structure_financement.csv``.
    financement: str
    #: Ses codes dans ``reserves_regimes.csv`` ; vide, elle n'y est pas.
    reserves: tuple[str, ...] = ()
    #: Son code dans ``valeurs_point.csv``, pour une caisse dont le site
    #: chiffre le point.
    point: str | None = None


#: Les caisses, dans l'ordre de la page : par famille, la plus grande d'abord.
CAISSES: tuple[Caisse, ...] = (
    Caisse("cnav", ("cnav",), "cnav"),
    Caisse("agirc_arrco", ("agirc_arrco",), "agirc_arrco", ("agirc_arrco",), "agirc_arrco"),
    Caisse("fpe", ("fonction_publique_etat",), "fonction_publique_etat"),
    Caisse("cnracl", ("cnracl",), "cnracl", ("cnracl",)),
    Caisse("ircantec", ("ircantec",), "ircantec", ("ircantec",), "ircantec"),
    Caisse("rafp", ("erafp",), "erafp", (), "rafp"),
    Caisse("rci", ("rci_complementaire",), "rci_complementaire", ("rci_complementaire",)),
    Caisse("cnavpl", ("cnavpl",), "cnavpl", ("cnavpl", "cnavpl_complementaire")),
    Caisse("cnbf", ("cnbf",), "cnbf", ("cnbf", "cnbf_complementaire")),
    Caisse("msa_exploitants", ("msa_exploitants",), "msa_exploitants"),
    Caisse("msa_salaries", ("msa_salaries",), "msa_salaries"),
    Caisse("sncf", ("sncf",), "sncf"),
    Caisse("ratp", ("ratp",), "ratp"),
    Caisse("cnieg", ("cnieg",), "cnieg"),
    Caisse("enim", ("enim",), "enim"),
    Caisse("mines", ("canssm",), "canssm"),
    Caisse("banque_de_france", ("banque_de_france",), "banque_de_france", ("banque_de_france",)),
    Caisse("crpcen", ("crpcen",), "crpcen", ("crpcen",)),
)


def _lignes(chemin: Path):
    with chemin.open(encoding="utf-8") as fichier:
        yield from csv.DictReader(ligne for ligne in fichier if not ligne.startswith("#"))


def _effectifs(chemin: Path, colonne: str) -> dict[str, int]:
    """Les effectifs de l'année, par code ; la fonction publique d'État, que
    ``retraites_projetes.csv`` sépare en civils et militaires, d'un tenant."""
    lus: dict[str, int] = {}
    for ligne in _lignes(chemin):
        if int(ligne["annee"]) != ANNEE_EFFECTIFS:
            continue
        code = ligne["caisse"]
        if code.startswith("fonction_publique_etat"):
            code = "fonction_publique_etat"
        lus[code] = lus.get(code, 0) + int(float(ligne[colonne]))
    return lus


def _point(chemin: Path) -> dict[str, dict[str, float]]:
    """Le prix, la valeur et le taux d'appel du point de chaque code, à la
    dernière année publiée jusqu'à ``ANNEE_POINT``."""
    derniers: dict[tuple[str, str], tuple[int, float]] = {}
    for ligne in _lignes(chemin):
        annee = int(ligne["annee"])
        cle = (ligne["regime"], ligne["mesure"])
        if annee <= ANNEE_POINT and annee >= derniers.get(cle, (0, 0.0))[0]:
            derniers[cle] = (annee, float(ligne["valeur"]))
    point: dict[str, dict[str, float]] = {}
    for (code, parametre), (_, valeur) in derniers.items():
        point.setdefault(code, {})[parametre] = valeur
    return point


def lire(racine: Path) -> dict[str, dict]:
    """Chaque caisse de la page : ses effectifs, son financement regroupé,
    ses réserves (``None`` si le COR ne lui en compte pas) et son point
    (``None`` si le site ne le chiffre pas)."""
    regimes = racine / "reference" / "regimes"
    cotisants = _effectifs(regimes / "cotisants.csv", "cotisants")
    retraites = _effectifs(regimes / "retraites_projetes.csv", "retraites")

    financement: dict[str, dict[str, float]] = {}
    for ligne in _lignes(regimes / "structure_financement.csv"):
        if int(ligne["annee"]) != ANNEE_FINANCEMENT:
            continue
        poste = POSTES[ligne["poste"]]
        parts = financement.setdefault(ligne["regime"], {})
        parts[poste] = round(parts.get(poste, 0.0) + float(ligne["part"]), 6)

    reserves: dict[str, tuple[float, int | None]] = {}
    for ligne in _lignes(regimes / "reserves_regimes.csv"):
        if ligne["poste"] == "reserves":
            mois = ligne["mois_prestations"]
            reserves[ligne["regime"]] = (float(ligne["montant_md"]), int(mois) if mois else None)

    points = _point(regimes / "valeurs_point.csv")

    caisses: dict[str, dict] = {}
    for caisse in CAISSES:
        lues = [reserves[code] for code in caisse.reserves if code in reserves]
        p = points.get(caisse.point) if caisse.point else None
        caisses[caisse.ident] = {
            "cotisants": somme_ordonnee(cotisants[code] for code in caisse.effectifs),
            "retraites": somme_ordonnee(retraites[code] for code in caisse.effectifs),
            "financement": {poste: part for poste, part in financement[caisse.financement].items()
                            if part > 0},
            "reserves": None if not lues else {
                "montant_md": round(somme_ordonnee(m for m, _ in lues), 1),
                "mois": lues[0][1] if len(lues) == 1 else None,
            },
            "point": None if p is None else {
                "prix": p["salaire_reference"],
                "valeur": p["valeur_service"],
                "appel": p.get("taux_appel", 1.0),
            },
        }
    return caisses
