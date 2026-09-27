"""Ce que le moteur fait d'un univers de la proposition.

La pile se résout quand on fabrique les données (``docs/architecture.md``,
§ 4.8 et 13.5) : le moteur ne lit pas les couches une à une, il lit ce que
:func:`calcul_notionnel` en tire — le compte, rétroactif ou ouvert à la bascule
par une transition, les paramètres que les couches lui changent, le pilier
capitalisé, la garantie vieillesse, l'âge légal, et ce que la liquidation
fictive de la transition neutralise.

Il refuse ce qu'il ne sait pas faire (§ 6.7) : une fiche de la proposition qu'il
ne connaît pas, ou qu'une couche ajoute depuis une autre date que celle où il
l'applique ; un paramètre qu'il ne sait pas changer ; une neutralisation
qu'aucune liquidation ne connaît ; une combinaison que ses méthodes ne
calculent pas. Une valeur qu'il ne connaît pas l'arrête : c'est ce qui rend
l'ajout d'un univers sans risque.
"""

from __future__ import annotations

import typing
from dataclasses import dataclass
from enum import Enum

from ..config import Parametres
from ..noyau.univers import ORIGINE, Univers

#: La transition qui ouvre le compte à la bascule.
_A_LA_BASCULE_DU_REVENU = {"date": "revenu.annee", "valeur": {"parametre": "annee_bascule"}}
_A_LA_BASCULE_DU_DEPART = {"date": "liquidation.date_effet", "valeur": {"parametre": "annee_bascule"}}

#: Les fiches de la proposition que le moteur sait appliquer, et le ``depuis``
#: où il les applique : la couche qui les ajoute doit dire le même.
FICHES_DU_MOTEUR: dict[str, object] = {
    "compte_notionnel": ORIGINE,
    "indexation_du_compte": ORIGINE,
    "coefficient_de_conversion": ORIGINE,
    "age_de_reference": ORIGINE,
    "fusion_des_regimes": ORIGINE,
    "valorisation_des_droits_acquis": _A_LA_BASCULE_DU_REVENU,
    "capitalisation_obligatoire": _A_LA_BASCULE_DU_REVENU,
    "garantie_vieillesse": ORIGINE,
    "age_legal_de_la_proposition": _A_LA_BASCULE_DU_DEPART,
}
#: Le compte, sans lequel le moteur ne calcule aucun univers de la proposition.
COMPTE = "compte_notionnel"
TRANSITION = "valorisation_des_droits_acquis"
#: Les paramètres du compte qu'une couche sait changer : ce qui l'alimente.
PARAMETRES_DU_COMPTE = ("part_cotisation", "source_cotisations", "taux_cotisation_uniforme")
#: Ce qu'une couche d'un seul calcul sait neutraliser, et la neutralisation du
#: contexte de la liquidation qui l'applique (liste ``neutralisations``).
NEUTRALISATIONS_DU_CALCUL: dict[tuple[str, str], str] = {
    ("contributivite", "avantages_non_contributifs"): "avantages_non_contributifs",
    ("contributivite", "avpf"): "avpf",
    ("contributivite", "points_gratuits"): "points_gratuits",
    ("domaine", "decote_surcote"): "decote_surcote",
}


@dataclass(frozen=True)
class CalculNotionnel:
    """Ce que le moteur fait d'un univers de la proposition."""

    univers: str
    #: L'intitulé que porte le résultat.
    libelle: str
    #: Une transition : le droit réel jusqu'à la bascule, les droits acquis
    #: valorisés, puis le compte ; sinon, le compte depuis l'origine.
    prospectif: bool
    #: Les paramètres du compte que les couches changent, résolus, par nom.
    modifications: tuple[tuple[str, object], ...]
    capitalisation: bool
    garantie: bool
    age_legal: bool
    #: Ce que la liquidation fictive de la transition neutralise.
    neutralisations: frozenset[str]

    def donnees(self) -> dict:
        """Ce que le paquet du site porte : le portage ne résout pas les
        couches, la fabrication l'a fait (§ 13.5). Tiré sans paramètres, un
        paramètre qui se lit dans un autre y reste un renvoi,
        ``{"parametre": "taux_cotisation_liberal"}``, que le site lit sous ses
        propres réglages."""
        return {
            "univers": self.univers, "libelle": self.libelle,
            "prospectif": self.prospectif,
            "modifications": {nom: (valeur.value if isinstance(valeur, Enum) else valeur)
                              for nom, valeur in self.modifications},
            "capitalisation": self.capitalisation, "garantie": self.garantie,
            "age_legal": self.age_legal,
            "neutralisations": sorted(self.neutralisations),
        }


def calcul_notionnel(univers: Univers, parametres: Parametres | None) -> CalculNotionnel:
    """Ce que le moteur fait de ``univers``, sous ``parametres`` ; ce qu'il ne
    sait pas faire l'arrête. Sans paramètres, les valeurs restent telles que
    les couches les écrivent : c'est la forme que le paquet du site porte."""
    nom = univers.id
    if univers.est_le_droit_reel:
        raise ValueError(f"univers {nom} : le droit réel se calcule par l'échéancier")
    for couche in univers.de_l_univers:
        for operation in couche.operations:
            if operation.operation in ("ajouter", "ajouter_une_transition"):
                attendu = FICHES_DU_MOTEUR.get(operation.fiche)
                if operation.fiche not in FICHES_DU_MOTEUR:
                    raise ValueError(f"univers {nom} : le moteur ne sait pas appliquer "
                                     f"la fiche {operation.fiche}")
                if couche.depuis != attendu:
                    raise ValueError(f"univers {nom} : le moteur applique {operation.fiche} "
                                     f"depuis {attendu}, la couche {couche.id} dit {couche.depuis}")
            if operation.operation == "changer_un_parametre" and couche.depuis != ORIGINE:
                raise ValueError(f"univers {nom} : le moteur ne change un paramètre que depuis "
                                 f"l'origine, la couche {couche.id} dit {couche.depuis}")
    if not univers.ajoute(COMPTE):
        raise ValueError(f"univers {nom} : le moteur ne calcule la proposition que sur "
                         "le compte notionnel, qu'aucune couche n'ajoute")

    types = typing.get_type_hints(Parametres)
    modifications = {}
    for fiche, parametre, valeur in univers.changements:
        if fiche != COMPTE or parametre not in PARAMETRES_DU_COMPTE:
            raise ValueError(f"univers {nom} : le moteur ne sait pas changer "
                             f"{fiche}.{parametre}")
        if parametres is None:
            pass                        # la forme du paquet, que le site résout
        elif isinstance(valeur, dict):
            valeur = getattr(parametres, valeur["parametre"])
        elif isinstance(types[parametre], type) and issubclass(types[parametre], Enum):
            valeur = types[parametre](valeur)
        modifications[parametre] = valeur

    neutralisations = set()
    for operation in univers.calcul:
        cle = operation.selecteur
        if operation.operation != "neutraliser" or cle not in NEUTRALISATIONS_DU_CALCUL:
            raise ValueError(f"univers {nom} : aucune liquidation ne sait « {operation} »")
        neutralisations.add(NEUTRALISATIONS_DU_CALCUL[cle])

    prospectif = univers.transition is not None
    if prospectif and univers.transition.transition != TRANSITION:
        raise ValueError(f"univers {nom} : le moteur ne connaît que la transition {TRANSITION}")
    capitalisation = univers.ajoute("capitalisation_obligatoire")
    garantie = univers.ajoute("garantie_vieillesse")
    if prospectif and (capitalisation or garantie):
        raise ValueError(f"univers {nom} : le moteur ne sert ni le pilier ni la garantie sur "
                         "un compte ouvert à la bascule (scripts/proposition_prospective.py "
                         "le fait à part)")
    if capitalisation and not garantie:
        raise ValueError(f"univers {nom} : le pilier se sert avec la garantie, qui le regarde")
    return CalculNotionnel(
        univers=nom,
        libelle=univers.libelle or univers.nom,
        prospectif=prospectif,
        modifications=tuple(sorted(modifications.items())),
        capitalisation=capitalisation,
        garantie=garantie,
        age_legal=univers.ajoute("age_legal_de_la_proposition"),
        neutralisations=frozenset(neutralisations),
    )
