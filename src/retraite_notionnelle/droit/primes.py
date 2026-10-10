"""Ce que la pension fait de la prime soumise à retenue, à sa date d'effet.

Trois fiches de ``data/reference/regles/`` (:data:`FICHES_DES_PRIMES`), une
par prime ; leur table, année par année, est
``legislation/primes_soumises_a_retenue.yaml`` (:mod:`~retraite_notionnelle.donnees.primes`).
Le régime liquide le traitement seul
(:func:`~.liquider.assiette_de_reference`) ; la version qui vaut à la date
d'effet dit ce que la pension fait de la prime :

* ``traitement`` : elle majore le traitement de référence, comme les indices
  majorés que les décrets écrivent — l'indemnité de sujétions spéciales du
  policier, « un dixième par an » de 1983 à 1992, l'indemnité de feu du
  sapeur-pompier, deux quinzièmes puis un quinzième par an de 1991 à 2003,
  « proratisée sur les seules années de service accomplies en cette qualité ».
  La pension est celle de ce traitement : pourcentage, décote, surcote,
  minimum garanti.
* ``supplement`` : elle ouvre un supplément de pension, servi après la décote
  et la surcote, hors minimum garanti et majoration pour enfants — la prime
  spéciale de sujétion de l'aide-soignant : « moyenne du montant de la prime
  de sujétion perçue les 6 derniers mois précédant la radiation des cadres x
  Pourcentage de progressivité x coefficient de proratisation » (CNRACL).

Le taux est celui de la prime en vigueur la veille de la date d'effet, la part
comptée celle de l'année de la date d'effet ; la condition, celle que la
version nomme, est lue comme celle des emplois classés
(:func:`~.compter.condition_d_un_emploi`). Action 138, étape 17, douzième
partie. Jumeau : ``moteur/js/droit/primes.js``.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..donnees.chargement import Fiabilite
from ..donnees.primes import charger_primes_soumises
from ..somme import somme_ordonnee
from . import compter, coordonner

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ScenarioActuel
    from .compter import Durees

#: Les fiches des primes, que ``FichesDatees`` porte.
FICHES_DES_PRIMES = ("indemnite_sujetions_speciales_police",
                     "prime_speciale_sujetion_aides_soignants",
                     "indemnite_de_feu_sapeurs_pompiers")

#: Ce que la pension fait de la prime.
NATURES_DES_PRIMES = ("traitement", "supplement")

#: Comment la prime se proratise : pas du tout ; sur les services accomplis
#: dans le statut, rapportés à tous les services de la liquidation ; de même,
#: sauf quand les services du statut et sa bonification atteignent seuls le
#: pourcentage maximum (décret n° 2003-1306, article 18, depuis le 2 janvier
#: 2025) ; de même, pour qui n'était pas du statut avant 2004, l'agent du
#: corps au 31 décembre 2003 ayant le supplément « à taux complet » (loi
#: n° 2003-1199, article 37, II).
PRORATAS_DES_PRIMES = ("aucun", "services_du_statut", "services_du_statut_hors_maximum",
                       "services_du_statut_depuis_2004")

#: Les conditions qu'une version peut poser : aucune, ou celle des emplois
#: classés que :func:`~.compter.condition_d_un_emploi` lit.
CONDITIONS_DES_PRIMES = ("aucune", "durees_et_age_de_l_emploi")

#: La bonification dont les services comptent, avec ceux du statut, pour
#: atteindre le pourcentage maximum sans proratisation.
BONIFICATION_DU_STATUT = "bonification_cinquieme_sapeurs_pompiers"


@dataclass(frozen=True)
class PrimeDeLaPension:
    """Ce que la prime d'une pension ajoute, et d'où."""

    fiche: str
    version: str
    texte: str | None
    #: ``traitement`` ou ``supplement``.
    nature: str
    #: Le taux de la prime, en part du traitement, plafond compris.
    taux: float
    #: La part que la date d'effet en compte.
    comptee: float
    #: Le coefficient de proratisation.
    prorata: float
    fiabilite: Fiabilite

    @property
    def part(self) -> float:
        """La part du traitement de référence que la prime ajoute, à la
        pension (``traitement``) ou au supplément (``supplement``)."""
        return self.taux * self.comptee * self.prorata

    def detail(self, montant: float | None = None) -> str:
        """Ce que la page en écrit."""
        prorata = "" if self.prorata >= 1.0 else f" × {self.prorata:.4f}"
        comptee = "" if self.comptee >= 1.0 else f" × {self.comptee:.4f}"
        if self.nature == "traitement":
            return f"+ prime de {self.taux:.2%}{comptee}{prorata}"
        return (f"supplément de {self.taux:.2%} du traitement{comptee}{prorata}"
                + ("" if montant is None else f", {montant:,.2f} €"))


def _ligne_de_reference(moteur: ScenarioActuel, code: str, carriere: Carriere,
                        annee_liquidation: int):
    """La dernière ligne cotisée au régime avant la date d'effet : celle dont
    le traitement des six derniers mois est liquidé."""
    for ligne in reversed(carriere.lignes):
        if not ligne.cotise or ligne.annee > annee_liquidation:
            continue
        regimes = moteur.affiliations.regimes(
            ligne.affiliation, ligne.annee, carriere.date_entree(ligne.affiliation))
        if code in regimes:
            return ligne
    return None


def prime_de_la_pension(moteur: ScenarioActuel, code: str, carriere: Carriere,
                        annee_liquidation: int, durees: Durees,
                        proratisation: int) -> PrimeDeLaPension | None:
    """La prime que la pension de ``code`` compte, ou ``None``.

    La ligne de référence doit être du statut qui perçoit la prime : le
    policier, l'aide-soignant, le sapeur-pompier en fonction à la radiation.
    ``proratisation`` : la durée qui ouvre le pourcentage maximum, que
    l'exception de 2025 compare aux services du statut et à sa bonification.
    """
    table = charger_primes_soumises(moteur.macro.racine)
    ligne = _ligne_de_reference(moteur, code, carriere, annee_liquidation)
    if ligne is None:
        return None
    prime = table.prime(ligne.affiliation)
    if prime is None or prime.regime != code:
        return None
    mois = carriere.date_liquidation.mois if carriere.age_liquidation is not None else 1
    effet = dt.date(annee_liquidation, mois, 1)
    version = moteur.fiches_datees.version(prime.fiche, effet.isoformat())
    if version is None or not version["parametres"].get("existe"):
        return None
    parametres = version["parametres"]
    nature = parametres["nature"]
    if nature not in NATURES_DES_PRIMES:
        raise ValueError(f"{prime.fiche}.{version['id']} : nature inconnue, {nature!r}")
    statuts = list(parametres["statuts"])
    borne = coordonner.borne_carriere(carriere)
    servies = carriere.duree_de_service(statuts, borne)
    condition = parametres["condition"]
    if condition not in CONDITIONS_DES_PRIMES:
        raise ValueError(f"{prime.fiche}.{version['id']} : condition inconnue, {condition!r}")
    fiabilite = Fiabilite.depuis_texte(parametres["fiabilite"])
    if condition != "aucune":
        ouverte = compter.condition_d_un_emploi(moteur, carriere, condition,
                                                parametres, servies)
        if ouverte is None:
            return None
        fiabilite = min(fiabilite, ouverte)
    taux = prime.taux_au(effet - dt.timedelta(days=1))
    if parametres.get("plafond") is not None:
        taux = min(taux, float(parametres["plafond"]))
    comptee = prime.part_comptee(annee_liquidation)
    if taux <= 0.0 or comptee <= 0.0:
        return None
    prorata = proratiser(moteur, carriere, code, parametres, servies, durees,
                         proratisation, borne)
    if prorata <= 0.0:
        return None
    return PrimeDeLaPension(
        fiche=prime.fiche, version=version["id"], texte=version["texte"],
        nature=nature, taux=taux, comptee=comptee, prorata=prorata,
        fiabilite=fiabilite)


def proratiser(moteur: ScenarioActuel, carriere: Carriere, code: str, parametres: dict,
               servies: float, durees: Durees, proratisation: int,
               borne: int | None) -> float:
    """Le coefficient de proratisation que la version nomme
    (:data:`PRORATAS_DES_PRIMES`) : les services du statut, en jours,
    rapportés à tous les services que la liquidation retient
    (:meth:`~.compter.Durees.jours_de_services`), un au plus."""
    regle = parametres["prorata"]
    if regle not in PRORATAS_DES_PRIMES:
        raise ValueError(f"prorata inconnu : {regle!r}")
    if regle == "aucun":
        return 1.0
    statuts = list(parametres["statuts"])
    if regle == "services_du_statut_depuis_2004":
        premiere = carriere.bornes_de_service(statuts, borne)
        if premiere is not None and premiere[0] < 2004:
            return 1.0
    if regle == "services_du_statut_hors_maximum":
        bonification = somme_ordonnee(e.services for e in durees.emplois
                                      if e.fiche == BONIFICATION_DU_STATUT
                                      and e.regime == code)
        if servies * 4.0 + bonification + 1e-9 >= proratisation:
            return 1.0
    total = durees.jours_de_services((code,)) / compter.JOURS_PAR_AN
    if total <= 0.0:
        # Avant le décompte au jour, les services en trimestres entiers.
        total = somme_ordonnee(
            durees.par_annee.get("services", {}).get(code, {}).values()) / 4.0
    if total <= 0.0:
        return 0.0
    return min(1.0, servies / total)
