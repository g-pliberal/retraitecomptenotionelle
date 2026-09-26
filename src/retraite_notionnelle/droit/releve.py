"""Le relevé des droits (docs/architecture.md, § 7.2 et 7.6).

Pour une demande, les quatre étapes de l'acquisition construisent le relevé
des droits qu'elle fait valoir : :func:`construire` les enchaîne — la
chronologie arrive préparée, puisque la carrière qui en est la vue ne se
construit qu'après (:mod:`.preparer`) —, puis réunit en groupes les régimes où
un droit est acquis. La liquidation du scénario 1 lit ce qu'il rend.

Le relevé se publie en lignes, que le contrat C.5 décrit
(``data/reference/contrats/ligne_releve.yaml``) : :meth:`Releve.lignes`.
Chaque ligne dit la personne qui en bénéficie, le fait de la chronologie qui
l'ouvre et sa date, le droit — une quantité, son unité, son régime et, pour
une durée, son compte —, sa face, et les présomptions qu'elle emploie. Les
lignes sont les crédits, année par année : le plafond d'une année — ses
trimestres civils, toutes activités d'un régime ou d'un groupe réunies — et
celui de la durée qu'un régime rémunère s'appliquent quand on les lit. Une
ligne cite la fiche de la carte qui l'écrit quand la règle en a une ; sa
version et le texte appliqué attendent que les fiches soient découpées en
versions : ce sont des manques, que le tableau de bord compte.

Son jumeau est ``moteur/js/droit/releve.js``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .. import chronologie as chrono
from . import acquerir as _acquerir
from . import compter as _compter
from . import coordonner as _coordonner
from .commun import date_d_effet as _date_d_effet

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ScenarioActuel
    from .acquerir import Droits
    from .compter import Durees
    from .coordonner import Coordination

#: La version du contrat C.5 que les lignes et l'enveloppe suivent.
SCHEMA_VERSION = 1

#: Les fiches de la carte que certaines lignes appliquent (data/reference/regles/).
FICHE_RETABLISSEMENT = "retablissement_fonction_publique"
FICHE_SERVICES = "services_et_duree_fonction_publique"
FICHE_ENFANTS = "majoration_duree_assurance_enfants"
FICHE_POINTS_GRATUITS = "rco_points_gratuits"

#: Les présomptions que chaque dispositif pour enfants applique dans le code
#: (data/reference/vocabulaire/valeurs.yaml, liste `presomptions`).
PRESOMPTIONS_ENFANTS = {
    "mda": ("pas_d_accord_des_parents", "enfant_eleve_neuf_ans"),
    "bonifications": ("interruption_d_activite_par_la_mere",),
}


@dataclass(frozen=True, eq=False)
class Releve:
    """Le relevé des droits d'une demande : ce que chaque étape a écrit, et
    les régimes que la coordination fait liquider ensemble."""

    coordination: Coordination
    durees: Durees
    droits: Droits
    #: Pour chaque régime d'un groupe d'au moins deux, les membres du groupe,
    #: le premier étant celui qui liquide.
    groupes: dict[str, tuple[str, ...]]
    #: Les régimes dont la liquidation lit les services : ceux de la fonction
    #: publique. Le compte des services se tient pour toute année d'emploi,
    #: mais seules leurs lignes se publient.
    services_lus: frozenset[str] = frozenset()

    @property
    def carriere(self) -> Carriere:
        """La carrière que la liquidation lit, rétablissement fait."""
        return self.coordination.carriere

    def donnees(self) -> dict:
        """Le relevé, tel que l'enveloppe du contrat C.5 le décrit."""
        carriere = self.carriere
        groupes = list(dict.fromkeys(self.groupes.values()))
        return {
            "schema_version": SCHEMA_VERSION,
            "personne": carriere.personne,
            "date": _date_d_effet(carriere),
            "lignes": self.lignes(),
            "groupes": [{"regimes": list(membres)} for membres in groupes],
        }

    def lignes(self) -> list[dict]:
        """Les lignes du relevé (contrat C.5), dans l'ordre des étapes : les
        durées, compte par compte ; les trimestres des enfants ; les points ;
        les cotisations ; les points gratuits."""
        carriere = self.carriere
        faits = _Faits(carriere)
        lignes: list[dict] = []
        cotisees: set[tuple[str, int]] = set()
        retablies: set[tuple[str, int]] = set()
        for ligne, regimes in zip(carriere.lignes, self.coordination.regimes):
            for code in regimes:
                if ligne.cotise:
                    cotisees.add((code, ligne.annee))
                if ligne.revenu_retabli > 0:
                    retablies.add((code, ligne.annee))
        for compte in _compter.COMPTES:
            for code, annees in self.durees.par_annee[compte].items():
                if compte == "services" and code not in self.services_lus:
                    continue
                for annee, trimestres in annees.items():
                    fait = faits.de_l_annee(annee, code, self.coordination)
                    fiche = (FICHE_SERVICES if compte == "services"
                             else FICHE_RETABLISSEMENT if (code, annee) in retablies
                             else None)
                    lignes.append(_ligne(
                        f"{compte}_{code}_{annee}", carriere.personne, fait,
                        f"{annee:04d}-01-01",
                        {"quantite": trimestres, "unite": "trimestre", "regime": code,
                         "compte": compte},
                        fiche=fiche,
                        contributive=(code, annee) in cotisees,
                        origine="observee" if faits.observe(fait) else "calculee",
                        presomptions=faits.presomptions(fait),
                        fiabilite=faits.fiabilite(fait)))
        enfants = self.durees.enfants
        if enfants is not None and carriere.nombre_enfants > 0:
            par_enfant = {"assurance": enfants.trimestres // carriere.nombre_enfants,
                          "services": enfants.services // carriere.nombre_enfants}
            for rang in range(1, carriere.nombre_enfants + 1):
                naissance = faits.naissance(f"enfant_{rang}")
                presomptions = sorted(
                    ([naissance["presomption"]] if naissance and naissance.get("presomption")
                     else [])
                    + list(PRESOMPTIONS_ENFANTS.get(enfants.dispositif, ())))
                for compte, trimestres in par_enfant.items():
                    if trimestres <= 0 or (compte == "services"
                                           and enfants.regime not in self.services_lus):
                        continue
                    lignes.append(_ligne(
                        f"enfants_{compte}_{enfants.regime}_{rang}", carriere.personne,
                        naissance["id"] if naissance else None,
                        naissance["debut"] if naissance else None,
                        {"quantite": trimestres, "unite": "trimestre",
                         "regime": enfants.regime, "compte": compte},
                        fiche=FICHE_ENFANTS, contributive=False,
                        presomptions=presomptions,
                        fiabilite=enfants.fiabilite.name.lower()))
        droits = self.droits
        vus: dict[str, int] = {}
        for code, annee, points, _ in droits.points:
            cle = f"points_{code}_{annee}"
            vus[cle] = vus.get(cle, 0) + 1
            lignes.append(_ligne(
                cle if vus[cle] == 1 else f"{cle}_{vus[cle]}", carriere.personne,
                faits.de_l_annee(annee, code, self.coordination), f"{annee:04d}-01-01",
                {"quantite": points, "unite": "point", "regime": code},
                fiabilite=droits.fiabilite_points[code].name.lower()))
        for code, annee, montant in droits.cotisations:
            cle = f"cotisations_{code}_{annee}"
            vus[cle] = vus.get(cle, 0) + 1
            lignes.append(_ligne(
                cle if vus[cle] == 1 else f"{cle}_{vus[cle]}", carriere.personne,
                faits.de_l_annee(annee, code, self.coordination), f"{annee:04d}-01-01",
                {"quantite": montant, "unite": "euro", "regime": code},
                face="cotisation", fiabilite=None))
        date_d_effet = _date_d_effet(carriere)
        for code, (points, _) in droits.gratuits.items():
            lignes.append(_ligne(
                f"gratuits_{code}", carriere.personne, faits.depart(), date_d_effet,
                {"quantite": points, "unite": "point", "regime": code},
                fiche=FICHE_POINTS_GRATUITS, contributive=False,
                fiabilite=droits.fiabilite_points[code].name.lower()))
        return lignes


def construire(moteur: ScenarioActuel, carriere: Carriere, *,
               avantages_non_contributifs: bool = True,
               points_gratuits: bool = True,
               liquider_successions: bool = True) -> Releve:
    """Le relevé des droits que la demande portée par ``carriere`` fait
    valoir : coordonner les affiliations, compter les durées, acquérir les
    droits, puis réunir les régimes que le droit fait liquider ensemble.

    Les trois drapeaux sont ceux de :meth:`ScenarioActuel.calculer`, qui les
    documente : les trimestres des enfants, les points gratuits, et la
    liquidation ensemble des régimes qui se succèdent.
    """
    coordination = _coordonner.coordonner(moteur, carriere)
    durees = _compter.compter(moteur, coordination, avantages_non_contributifs)
    droits = _acquerir.acquerir(moteur, coordination, durees, points_gratuits)
    # Un régime et celui qui lui succède liquident ensemble, sous les règles
    # de la caisse qui aurait le dossier : les autres membres du groupe
    # sont sautés partout où un régime liquide.
    groupes = (
        _coordonner.groupes_de_succession(
            moteur, droits.codes, coordination.carriere.annee_liquidation,
            droits.derniere_annee_par_regime, coordination.carriere,
        ) if liquider_successions else {}
    )
    services_lus = frozenset(
        code for code in durees.par_annee["services"]
        if moteur.catalogue[code].famille == "fonction_publique")
    return Releve(coordination, durees, droits, groupes, services_lus)


def _ligne(ident: str, personne: str, fait: str | None, date: str | None,
           droit: dict, *, fiche: str | None = None, face: str = "droit",
           contributive: bool = True, origine: str = "calculee",
           presomptions: list[str] | None = None,
           fiabilite: str | None = None) -> dict:
    """Une ligne du contrat C.5. Ce qui n'est pas encore su — la version de
    la fiche, le texte appliqué, une fiche que la règle n'a pas encore — n'y
    figure pas : c'est un manque, pas une erreur."""
    ligne = {"schema_version": SCHEMA_VERSION, "id": ident, "personne": personne}
    if fait is not None:
        ligne["fait"] = fait
    if date is not None:
        ligne["date"] = date
    if fiche is not None:
        ligne["fiche"] = fiche
    ligne |= {"droit": droit, "face": face, "contributive": contributive,
              "nature": "ferme", "origine": origine,
              "presomptions": presomptions or []}
    if fiabilite is not None:
        ligne["fiabilite"] = fiabilite
    return ligne


class _Faits:
    """Les faits de la chronologie qu'une ligne du relevé cite."""

    def __init__(self, carriere: Carriere) -> None:
        chronologie = carriere.chronologie or {"faits": []}
        self.personne = carriere.personne
        self.par_id = {f["id"]: f for f in chronologie.get("faits") or []}
        self.periodes = [f for f in chrono.faits_de(chronologie, carriere.personne)
                         if f["sorte"] in (chrono.EMPLOI, chrono.INTERRUPTION)]
        self.naissances = {f["personne"]: f for f in chronologie.get("faits") or []
                           if f["sorte"] == "naissance"}

    def de_l_annee(self, annee: int, code: str,
                   coordination: Coordination) -> str | None:
        """Le fait qui ouvre ce que ``code`` reçoit en ``annee`` : la période
        qui couvre l'année sous un statut que la coordination y route — une
        interruption, quand l'année en est une —, la première dans l'ordre de
        la chronologie."""
        debut, fin = f"{annee:04d}-01-01", f"{annee + 1:04d}-01-01"
        statuts = {ligne.affiliation
                   for ligne, regimes in zip(coordination.carriere.lignes,
                                             coordination.regimes)
                   if ligne.annee == annee and code in regimes}
        couvrent = [f for f in self.periodes
                    if f["debut"] < fin and (f.get("fin") is None or f["fin"] > debut)]
        for fait in couvrent:
            if fait["sorte"] == chrono.INTERRUPTION and "affiliation" not in fait["attributs"]:
                return fait["id"]
        for fait in couvrent:
            if fait["attributs"].get("affiliation") in statuts:
                return fait["id"]
        return None

    def observe(self, fait: str | None) -> bool:
        """Un fait d'un relevé de carrière déposé fait foi : ses trimestres
        sont observés, non calculés."""
        return fait is not None and fait.startswith("releve_")

    def presomptions(self, fait: str | None) -> list[str]:
        element = self.par_id.get(fait) if fait else None
        return [element["presomption"]] if element and element.get("presomption") else []

    def fiabilite(self, fait: str | None) -> str | None:
        element = self.par_id.get(fait) if fait else None
        return element.get("fiabilite") if element else None

    def naissance(self, personne: str) -> dict | None:
        return self.naissances.get(personne)

    def depart(self) -> str | None:
        fait = f"depart_{self.personne}"
        return fait if fait in self.par_id else None
