"""Foyer et net (docs/architecture.md, § 7.4).

Ce que le droit sert en regardant toutes les ressources du bénéficiaire, et
non une pension : l'ASPA. Elle vient en DERNIER, et pour cause : elle est
différentielle. Elle complète tout le reste, majorations comprises, jusqu'au
montant du barème — c'est la seule prestation du système actuel qui ne suppose
aucune cotisation, et donc celle qui creuse le plus l'écart avec un compte
notionnel. Elle s'ouvre à 65 ans, à qui réside en France, et se revoit à
chaque échéance : l'échéancier l'applique après les liquidations du jour, et
après « faire vivre ». Les pensions qu'un autre État sert comptent dans ses
ressources, servies à part.

LE BARÈME EST CELUI DU FOYER. Une personne seule a le sien. Qui déclare un
conjoint, et l'a épousé à cette date, a celui du couple : le plafond du couple,
que ses ressources et celles du conjoint ne doivent pas dépasser (L. 815-9 ;
D. 815-2) ; la moitié de ce qui manque quand le conjoint a lui aussi l'âge de
l'allocation, chacun des deux en recevant autant (D. 815-1, b ; R. 815-28) ;
tout ce qui manque sinon, au plus le montant d'une personne seule
(D. 815-1, a). Le conjoint qui ne dit pas ses ressources n'en a aucune
(présomption ``ressources_du_conjoint``) ; fiche ``minimum_vieillesse``.

Ce que l'étape écrit, :class:`Foyer`, suit son schéma,
``data/reference/etapes/foyer_et_net.yaml``. Son jumeau est
``moteur/js/droit/foyer.js``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from ..donnees.chargement import Fiabilite
from .commun import AvantageApplique
from .etranger import pensions_etrangeres_servies
from .invalidite import AGE_DE_L_ASPA

if TYPE_CHECKING:
    from ..carriere import Carriere, Conjoint
    from ..scenarios.actuel import DeuxEtages, ScenarioActuel
    from .liquidation import Contexte

#: La version du schéma de l'étape que :meth:`Foyer.donnees` suit.
SCHEMA_VERSION = 1

#: Les trois barèmes de l'allocation : une personne seule ; un couple dont la
#: personne est seule allocataire, au plus le montant d'une personne seule
#: (D. 815-1, a) ; un couple dont les deux membres le sont, qui se partagent
#: le montant du couple par moitié (D. 815-1, b).
PERSONNE_SEULE = "personne_seule"
COUPLE = "couple"
DEUX_ALLOCATAIRES = "deux_allocataires"

#: Ce que la cascade des avantages dit de chacun.
DETAILS = {
    PERSONNE_SEULE: "allocation différentielle, barème d'une personne seule",
    COUPLE: ("allocation différentielle, plafond du couple, au plus le montant "
             "d'une personne seule"),
    DEUX_ALLOCATAIRES: ("allocation différentielle, barème d'un couple "
                        "d'allocataires, servie par moitié"),
}

#: Ce qu'elle en dit avant 2007, quand le minimum tient en deux étages.
DETAILS_DEUX_ETAGES = {
    PERSONNE_SEULE: ("allocation aux vieux travailleurs salariés et allocation "
                     "supplémentaire, sous le plafond d'une personne seule"),
    COUPLE: ("allocation aux vieux travailleurs salariés et allocation "
             "supplémentaire, sous le plafond du couple"),
    DEUX_ALLOCATAIRES: ("allocation aux vieux travailleurs salariés et allocation "
                        "supplémentaire du ménage, sous le plafond du couple, "
                        "servie par moitié"),
}


@dataclass(frozen=True)
class Foyer:
    """Ce que l'étape « foyer et net » écrit, à une date."""

    personne: str
    #: La date à laquelle les ressources sont lues : l'effet de la
    #: liquidation, ou l'échéance (AAAA-MM-JJ).
    date: str | None
    #: Toutes les pensions que le bénéficiaire reçoit, régimes provisionnés,
    #: majorations et pensions étrangères compris.
    ressources: float
    #: L'ASPA : le complément jusqu'au barème, nul quand les ressources
    #: l'atteignent — pour un couple d'allocataires, la part de la personne.
    minimum_vieillesse: float
    #: Le barème lu, quand l'allocation est ouverte : celui d'une personne
    #: seule, ou le plafond du couple.
    plafond: float | None
    fiabilite: Fiabilite
    #: Celles des ressources qu'un autre État sert, à part des pensions
    #: françaises : l'allocation ne complète que ce qu'elles laissent.
    etrangeres: float = 0.0
    #: Le barème du foyer : :data:`PERSONNE_SEULE`, :data:`COUPLE` ou
    #: :data:`DEUX_ALLOCATAIRES`.
    bareme: str = PERSONNE_SEULE
    #: Les ressources du conjoint, que le plafond du couple compte avec les
    #: siennes : déclarées, nulles sinon ; nulles sans conjoint.
    ressources_conjoint: float = 0.0
    #: Avant 2007, le minimum à deux étages (:func:`avant_l_aspa`) : il ne
    #: porte pas les ressources au plafond, qu'il ne fait que borner.
    deux_etages: bool = False

    def avantage(self) -> AvantageApplique:
        """L'ASPA, sous la forme où la cascade des avantages la dit."""
        return AvantageApplique(
            code="minimum_vieillesse",
            libelle="Minimum vieillesse (ASPA)",
            montant=self.minimum_vieillesse,
            detail=(DETAILS_DEUX_ETAGES if self.deux_etages else DETAILS)[self.bareme],
        )

    def servie_avec(self, pensions: float) -> float:
        """Les pensions françaises de la personne et l'allocation, ensemble :
        le barème d'une personne seule, moins ce que les pensions étrangères,
        servies à part, en remplissent ; dans un couple, ses pensions et sa
        part de l'allocation, que le barème ne dit plus ; avant 2007, ses
        pensions et les deux étages, que le plafond borne sans les y porter."""
        if self.bareme == PERSONNE_SEULE and not self.deux_etages:
            return self.plafond - self.etrangeres
        return pensions + self.minimum_vieillesse

    def donnees(self) -> dict:
        """Le foyer, tel que le schéma de l'étape le décrit."""
        return {"schema_version": SCHEMA_VERSION, "personne": self.personne,
                "date": self.date, "ressources": self.ressources,
                "etrangeres": self.etrangeres, "bareme": self.bareme,
                "ressources_conjoint": self.ressources_conjoint,
                "minimum_vieillesse": self.minimum_vieillesse,
                "fiabilite": self.fiabilite.name.lower()}


def condition_de_residence(moteur: ScenarioActuel, residence: str | None, date: str,
                           mois_en_france: int | None = None) -> bool:
    """La condition de résidence de l'allocation à cette date (fiche
    ``residence_et_minimum_vieillesse``) : elle n'est servie qu'en France, à
    qui y séjourne plus de six mois de l'année civile, plus de neuf depuis le
    1er septembre 2023, et supprimée au départ hors de France. ``residence``
    est l'État où le bénéficiaire réside hors de France, ``None`` pour qui
    n'en déclare pas (présomption ``residence_en_france``) ; ``mois_en_france``
    les mois qu'il y passe chaque année, ``None`` pour toute l'année."""
    if residence is None and mois_en_france is None:
        return True
    version = moteur.carrieres_hors_de_france.version(
        "residence", {"liquidation.date_effet": date})
    if version is None or not version["parametres"].get("residence_requise"):
        return True
    if residence is not None:
        return False
    seuil = version["parametres"].get("mois_de_residence_plus_de")
    return seuil is None or mois_en_france > seuil


def conjoint_au_foyer(carriere: Carriere | None, jour: str) -> Conjoint | None:
    """Le conjoint avec qui la personne vit à cette date, dont les ressources
    comptent au plafond du couple (L. 815-9) : celui que la saisie déclare,
    une fois le mariage célébré ; ``None`` sinon. Le modèle ne connaît ni
    divorce, ni décès du conjoint."""
    conjoint = None if carriere is None else carriere.conjoint
    if conjoint is None or conjoint.mariage > jour:
        return None
    return conjoint


def conjoint_allocataire(conjoint: Conjoint, jour: str) -> bool:
    """Si le conjoint peut lui aussi prétendre à l'allocation à cette date : il
    en a l'âge, soixante-cinq ans. L'âge abaissé de l'inapte et de l'ex-invalide
    (R. 815-1) ne se lit que pour l'assuré, et le conjoint réside avec lui."""
    naissance = conjoint.naissance
    anniversaire = f"{int(naissance[:4]) + int(AGE_DE_L_ASPA):04d}{naissance[4:]}"
    return anniversaire <= jour


def avant_l_aspa(etages: DeuxEtages, bareme: str, ressources: float,
                 du_conjoint: float) -> tuple[float, float | None]:
    """Le minimum vieillesse d'avant 2007, et le plafond qui le borne.

    Le premier étage porte la pension au montant de l'allocation aux vieux
    travailleurs salariés (L. 814-2). Le second, l'allocation supplémentaire,
    « n'est due que si le total de cette allocation et des ressources
    personnelles de l'intéressé et du conjoint » n'excède pas le plafond, et
    se réduit « à due concurrence » sinon (L. 815-8) : au-dessus du montant
    des deux étages, que le plafond dépassait de moitié en 1970, une pension en
    recevait encore une part. Deux allocataires se partagent par moitié le
    montant du ménage, le double de celui d'un seul avant juillet 1982 ; le
    conjoint qui l'est a lui aussi son premier étage, qui compte dans les
    ressources du ménage. Le premier étage n'est servi que sous le plafond
    (L. 814-2), que les ressources du conjoint peuvent atteindre. Avant 1956,
    le premier étage seul, sans plafond lu.
    """
    if bareme == PERSONNE_SEULE:
        plafond, total = etages.plafond, ressources
    else:
        plafond, total = etages.plafond_couple, ressources + du_conjoint
    premier = max(0.0, etages.avts - ressources)
    if plafond is None:
        return premier, None
    premier = max(0.0, min(premier, plafond - total))
    total += premier
    maximum, part = etages.supplementaire, 1.0
    if bareme == DEUX_ALLOCATAIRES:
        total += max(0.0, min(etages.avts - du_conjoint, plafond - total))
        maximum = (2 * etages.supplementaire if etages.supplementaire_menage is None
                   else etages.supplementaire_menage)
        part = 0.5
    return premier + part * max(0.0, min(maximum, plafond - total)), plafond


def foyer_et_net(moteur: ScenarioActuel, personne: str, date: str | None, annee: int,
                 ressources: float, age_atteint: bool,
                 contexte: Contexte | None = None, carriere: Carriere | None = None) -> Foyer:
    """L'ASPA qu'appellent ``ressources``, les pensions françaises, en ``annee``.

    ``age_atteint`` dit si l'âge de l'allocation l'est : à la date d'effet
    pour une liquidation, dans l'année pour une échéance. La ``carriere`` dit
    les faits que l'allocation lit : les pensions qu'un autre État sert à
    cette date, qui s'ajoutent aux ressources (R. 815-22) ; l'État où le
    bénéficiaire réside hors de France, s'il le déclare : elle n'y est pas
    servie, ni à qui ne passe pas assez de mois en France ; et le conjoint,
    qui donne au foyer le barème du couple. Le contexte peut neutraliser les
    avantages non contributifs, et l'allocation avec eux ; le paramètre
    ``minimum_vieillesse_dans_le_scenario_actuel`` la retire aussi.
    """
    jour = date or f"{annee:04d}-12-31"
    residence = None if carriere is None else carriere.residence
    mois_en_france = None if carriere is None else carriere.mois_en_france
    etrangeres = (0.0 if carriere is None else pensions_etrangeres_servies(
        moteur.macro, carriere, DateMois(int(jour[:4]), int(jour[5:7])), annee))
    ressources += etrangeres
    conjoint = conjoint_au_foyer(carriere, jour)
    du_conjoint = (0.0 if conjoint is None or conjoint.ressources is None
                   else float(conjoint.ressources))
    bareme = (PERSONNE_SEULE if conjoint is None
              else DEUX_ALLOCATAIRES if conjoint_allocataire(conjoint, jour) else COUPLE)
    montant, plafond, fiabilite = 0.0, None, Fiabilite.CERTIFIEE
    servie = (age_atteint and moteur.parametres.minimum_vieillesse_dans_le_scenario_actuel
              and condition_de_residence(moteur, residence, jour, mois_en_france)
              and not (contexte is not None
                       and contexte.neutralise("avantages_non_contributifs")))
    etages = moteur.minimum_vieillesse.deux_etages(annee) if servie else None
    if etages is not None:
        # AVANT L'ASPA, DEUX ÉTAGES. Le modèle servait le montant de 2006 ramené
        # sur les prix, 1 195 € en 1970 au lieu de 457 € (action 138, étape 6).
        montant, plafond = avant_l_aspa(etages, bareme, ressources, du_conjoint)
        if montant > 0:
            fiabilite = etages.fiabilite
    elif servie:
        seule = moteur.minimum_vieillesse.plafond(annee)
        couple = (None if bareme == PERSONNE_SEULE
                  else moteur.minimum_vieillesse.plafond_couple(annee))
        if bareme == PERSONNE_SEULE and seule is not None:
            plafond = seule[0]
            montant = max(0.0, seule[0] - ressources)
            if montant > 0:
                fiabilite = seule[1]
        elif seule is not None and couple is not None:
            # Ce qui manque au couple pour atteindre son plafond : partagé
            # entre deux allocataires, borné au montant d'une personne seule
            # pour un seul.
            plafond = couple[0]
            manque = max(0.0, couple[0] - ressources - du_conjoint)
            montant = manque / 2.0 if bareme == DEUX_ALLOCATAIRES else min(seule[0], manque)
            if montant > 0:
                fiabilite = (couple[1] if bareme == DEUX_ALLOCATAIRES
                             else min(couple[1], seule[1]))
    return Foyer(personne=personne, date=date, ressources=ressources,
                 minimum_vieillesse=montant, plafond=plafond, fiabilite=fiabilite,
                 etrangeres=etrangeres, bareme=bareme, ressources_conjoint=du_conjoint,
                 deux_etages=etages is not None)
