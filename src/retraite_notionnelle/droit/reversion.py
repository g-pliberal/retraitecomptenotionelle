"""La réversion : la pension du survivant, dans les régimes du défunt (§ 7.3).

« La réversion n'est pas une étape. C'est ``liquider`` pour le survivant, de
motif « réversion », dans les régimes du défunt. » Elle lit la liquidation du
défunt — ici son départ, menée jusqu'à son décès par « faire vivre » — et
applique à chaque régime la version de sa fiche que les dates choisissent :

* le régime général et les régimes alignés (fiche ``reversion``) : un taux de
  la pension, à partir d'un âge, sous un plafond de ressources — condition
  d'ouverture avant juillet 2004, écrêtement depuis ;
* la fonction publique et la CNRACL (``reversion_fonction_publique``) : la
  moitié de la pension, sans âge ni ressources, sous la condition
  d'antériorité ou de durée du mariage de L. 39 ;
* l'Agirc-Arrco (``reversion_agirc_arrco``) : 60 % de la retraite, à l'âge que
  la date du décès choisit.

Les autres régimes n'ont pas encore de fiche : leur ligne le dit, sans montant.

CE QUI N'EST PAS ENCORE PORTÉ, et que les fiches déclarent : le minimum de
réversion et la majoration de 11,1 % du régime général, la majoration pour
enfants du survivant, le plafonnement du veuf de fonctionnaire d'avant 2004,
la minoration de l'Agirc avant soixante ans, le partage entre ex-conjoints, le
remariage. L'Agirc-Arrco sert 60 % des points sans le coefficient
d'anticipation de l'assuré retraité, dans la limite de sa retraite : le moteur
applique les 60 % à la retraite servie, coefficient compris.

LES MONTANTS sont ceux de l'année du décès : la pension du défunt y est menée
par « faire vivre », et le plafond du régime général s'y lit, au SMIC de cette
année-là. Pour un décès à venir, l'année courante, où s'arrêtent les
revalorisations publiées.

SANS DÉCÈS DÉCLARÉ, l'échéancier liquide une réversion d'essai pour un décès
supposé juste après le départ, ou au 1er janvier de l'année courante pour qui
est déjà parti (présomption ``deces_apres_le_depart``) : ce que le conjoint
recevrait. :attr:`Reversion.deces_suppose` le dit.

Ce qu'elle écrit, :class:`Reversion`, se porte au journal. Son jumeau est
``moteur/js/droit/reversion.js``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .. import chronologie as chrono
from ..donnees.chargement import Fiabilite

if TYPE_CHECKING:
    from ..carriere import Carriere, Conjoint
    from ..scenarios.actuel import ScenarioActuel

#: La version du schéma que :meth:`Reversion.donnees` suit.
SCHEMA_VERSION = 1

#: Ce que dit une ligne dont le montant est nul, ou qui n'est pas servie en
#: entier.
MOTIFS = {
    "servie": "servie",
    "ecretee": "réduite à due concurrence du plafond de ressources",
    "ressources": "ressources au-dessus du plafond",
    "mariage": "condition d'antériorité ou de durée du mariage non remplie",
    "non_portee": "la réversion de ce régime n'est pas encore portée",
}


@dataclass(frozen=True)
class ReversionRegime:
    """La réversion d'un régime du défunt."""

    regime: str
    #: La pension du défunt dans ce régime, à l'année des montants.
    base: float
    montant: float
    motif: str
    fiche: str | None = None
    version: str | None = None
    texte: str | None = None
    taux: float = 0.0
    #: La date d'effet (AAAA-MM-JJ) : le premier jour du mois qui suit le
    #: décès, ou qui suit l'âge requis.
    date_effet: str | None = None
    fiabilite: Fiabilite = Fiabilite.ESTIMEE

    def donnees(self) -> dict:
        return {"regime": self.regime, "base": self.base, "taux": self.taux,
                "montant": self.montant, "motif": self.motif,
                "date_effet": self.date_effet, "fiche": self.fiche,
                "version": self.version, "texte": self.texte,
                "fiabilite": self.fiabilite.name.lower()}


@dataclass(frozen=True)
class Reversion:
    """Ce que la liquidation d'une réversion écrit : régime par régime."""

    #: Le survivant, et le défunt dont les régimes servent la réversion.
    personne: str
    defunt: str
    #: Le décès (AAAA-MM-JJ), et l'année dont les montants sont les euros.
    deces: str
    annee: int
    #: Les ressources du survivant hors réversions, et si elles sont présumées.
    ressources: float
    ressources_presumees: bool
    regimes: tuple[ReversionRegime, ...]
    #: Le décès est-il supposé (présomption ``deces_apres_le_depart``) plutôt
    #: que déclaré ?
    deces_suppose: bool = False

    @property
    def total(self) -> float:
        return sum(r.montant for r in self.regimes)

    def donnees(self) -> dict:
        return {"schema_version": SCHEMA_VERSION, "personne": self.personne,
                "defunt": self.defunt, "deces": self.deces,
                "deces_suppose": self.deces_suppose, "annee": self.annee,
                "ressources": self.ressources,
                "ressources_presumees": self.ressources_presumees,
                "total": self.total,
                "regimes": [r.donnees() for r in self.regimes]}


def mois_suivant(jour: str) -> str:
    """Le premier jour du mois qui suit ``jour`` (AAAA-MM-JJ)."""
    annee, mois = int(jour[:4]), int(jour[5:7])
    annee, mois = (annee + 1, 1) if mois == 12 else (annee, mois + 1)
    return f"{annee:04d}-{mois:02d}-01"


def _apres_l_age(naissance: str, age: float) -> str:
    """Le premier jour du mois qui suit celui où ``age`` est atteint (R. 353-7) :
    un anniversaire le 1er du mois ouvre le mois suivant, comme les autres."""
    ans = int(age)
    return mois_suivant(chrono._plus_ans(naissance, ans))


def _a_l_age(naissance: str, date_effet: str, age: float | None) -> str:
    """La date d'effet, reportée s'il le faut au mois qui suit l'âge requis."""
    if age is None:
        return date_effet
    return max(date_effet, _apres_l_age(naissance, age))


def _age_agirc_arrco(parametres: dict, regime: str, sexe: str) -> float:
    """L'âge requis à l'Agirc-Arrco : celui de l'accord de 2017, ou, pour un
    décès d'avant 2019, celui de l'Agirc ou de l'Arrco, et du veuf ou de la
    veuve quand la version les distingue."""
    if parametres.get("age_minimum") is not None:
        return float(parametres["age_minimum"])
    agirc = regime.startswith("agirc") and regime != "agirc_arrco"
    propre = parametres.get("age_minimum_agirc" if agirc else "age_minimum_arrco")
    if propre is not None:
        return float(propre)
    return float(parametres["age_minimum_veuf" if sexe == "H" else "age_minimum_veuve"])


def _mariage_dure(conjoint: Conjoint, deces: str, enfants: int, annees: float) -> bool:
    """La condition de durée du mariage du régime général d'avant juillet 2004 :
    ``annees`` de mariage au décès, sauf enfant issu du mariage — que le
    modèle tient pour tout enfant déclaré."""
    return (not annees or enfants > 0
            or chrono.annees_revolues(conjoint.mariage, deces) >= annees)


def _mariage_suffit(parametres: dict, conjoint: Conjoint, deces: str, depart: str,
                    enfants: int) -> bool:
    """La condition de L. 39 : un enfant issu du mariage, quatre ans de
    mariage, ou deux ans de services entre le mariage et la cessation
    d'activité — lue au départ, que le modèle tient pour la cessation."""
    if enfants > 0:
        return True
    return (chrono.annees_revolues(conjoint.mariage, deces)
            >= parametres["mariage_minimum_annees"]
            or chrono.annees_revolues(conjoint.mariage, depart)
            >= parametres["mariage_services_minimum_annees"])


def reversion(moteur: ScenarioActuel, pensions: list[tuple[str, float, Fiabilite]],
              carriere: Carriere, annee: int,
              deces_suppose: str | None = None) -> Reversion | None:
    """La réversion que le décès de la personne de ``carriere`` ouvre à son
    conjoint, régime par régime ; ``None`` sans décès ou sans conjoint.

    ``pensions`` sont les pensions du défunt à l'année ``annee``, où les
    montants se chiffrent : ``(régime, montant, fiabilité)``, dans l'ordre de
    sa liquidation. Un régime qui ne lui sert rien n'a rien à reverser.
    ``deces_suppose`` date le décès que la présomption
    ``deces_apres_le_depart`` suppose, quand la chronologie n'en dit pas.
    """
    conjoint = carriere.conjoint
    deces = carriere.deces if deces_suppose is None else deces_suppose
    if deces is None or conjoint is None:
        return None
    lendemain = mois_suivant(deces)
    depart = f"{carriere.date_liquidation.annee:04d}-{carriere.date_liquidation.mois:02d}-01"
    enfants = carriere.nombre_enfants
    presumees = conjoint.ressources is None
    ressources = 0.0 if presumees else float(conjoint.ressources)
    table = moteur.reversions
    pensions = [(regime, base, fiabilite) for regime, base, fiabilite in pensions if base > 0]

    def ligne(regime, base, montant, motif, fiche, version, taux, date_effet, fiabilite):
        return ReversionRegime(
            regime, base, montant, motif, fiche["id"], version["id"], version["texte"],
            taux, date_effet,
            min(fiabilite, Fiabilite.depuis_texte(version["parametres"]["fiabilite"])))

    lignes: dict[str, ReversionRegime] = {}
    # La fonction publique et l'Agirc-Arrco d'abord : la réversion d'un autre
    # régime de base compte aux ressources du régime général ; celle des
    # complémentaires, non (R. 353-1, 2°).
    autres_bases = 0.0
    for regime, base, fiabilite in pensions:
        fiche = table.fiche_du_regime(regime)
        if fiche is None:
            lignes[regime] = ReversionRegime(regime, base, 0.0, "non_portee")
            continue
        if fiche["id"] == "reversion":
            continue
        if fiche["id"] == "reversion_fonction_publique":
            version = table.version(fiche, lendemain, deces)
            parametres = version["parametres"]
            taux = float(parametres["taux"])
            servie = _mariage_suffit(parametres, conjoint, deces, depart, enfants)
            montant = taux * base if servie else 0.0
            autres_bases += montant
            lignes[regime] = ligne(regime, base, montant, "servie" if servie else "mariage",
                                   fiche, version, taux, lendemain, fiabilite)
            continue
        version = table.version(fiche, lendemain, deces)
        parametres = version["parametres"]
        date_effet = _a_l_age(conjoint.naissance, lendemain,
                              _age_agirc_arrco(parametres, regime, conjoint.sexe))
        taux = float(parametres["taux"])
        lignes[regime] = ligne(regime, base, taux * base, "servie", fiche, version, taux,
                               date_effet, fiabilite)

    # Le plafond de ressources est un : les réversions des régimes alignés se
    # l'imputent l'une après l'autre, dans l'ordre de la liquidation.
    for regime, base, fiabilite in pensions:
        fiche = table.fiche_du_regime(regime)
        if fiche is None or fiche["id"] != "reversion":
            continue
        # L'âge requis reporte la date d'effet, et la date d'effet choisit la
        # version, dont l'âge peut changer : deux tours suffisent au plus.
        date_effet = lendemain
        for _ in range(3):
            version = table.version(fiche, date_effet, deces)
            reportee = _a_l_age(conjoint.naissance, lendemain,
                                float(version["parametres"]["age_minimum"]))
            if reportee == date_effet:
                break
            date_effet = reportee
        parametres = version["parametres"]
        taux = float(parametres["taux"])
        montant = taux * base
        plafond_annuel = (float(parametres["plafond_smic_heures"])
                          * moteur.macro.smic_horaire(annee))
        disponible = plafond_annuel - ressources - autres_bases
        motif = "servie"
        if not _mariage_dure(conjoint, deces, enfants, parametres["mariage_minimum_annees"]):
            montant, motif = 0.0, "mariage"
        elif parametres["ressources"] == "ecretement":
            if montant > disponible:
                montant, motif = max(0.0, disponible), "ecretee"
        elif disponible < 0:
            montant, motif = 0.0, "ressources"
        autres_bases += montant
        lignes[regime] = ligne(regime, base, montant, motif, fiche, version, taux,
                               date_effet, fiabilite)

    return Reversion(
        personne=conjoint.personne, defunt=carriere.personne, deces=deces, annee=annee,
        ressources=ressources, ressources_presumees=presumees,
        regimes=tuple(lignes[regime] for regime, _, _ in pensions),
        deces_suppose=deces_suppose is not None)
