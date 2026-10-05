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
  la date du décès choisit, ou dès l'invalidité du survivant ou deux enfants à
  sa charge au décès ; depuis 2019, la majoration pour enfants du défunt en
  plus, reversée en entier (accord du 17 novembre 2017, articles 109 à 111) ;
* le RAFP (``reversion_rafp``) : la moitié de la prestation, sans âge, sans
  ressources ni durée du mariage, et rien après un droit direct versé en
  capital — l'échéancier dit lesquels (``en_capital``) ;
* l'Ircantec (``reversion_ircantec``) : la moitié, à cinquante ans ou dès le
  décès avec deux enfants de moins de vingt et un ans, sous les conditions de
  durée du mariage de l'arrêté du 30 décembre 1970 ;
* la complémentaire des indépendants (``reversion_rci``) : 60 %, à l'âge du
  régime général, réduite à due concurrence d'un plafond de ressources, deux
  plafonds annuels de la Sécurité sociale, que les réversions des régimes de
  base comptent aussi ; pour un décès d'avant 2013, sa ligne dit qu'elle n'est
  pas portée.

Les autres régimes n'ont pas encore de fiche : leur ligne le dit, sans montant.

CE QUI N'EST PAS ENCORE PORTÉ, et que les fiches déclarent : le minimum de
réversion et la majoration de 11,1 % du régime général, la majoration pour
enfants du survivant, le plafonnement du veuf de fonctionnaire d'avant 2004,
la minoration de l'Agirc avant soixante ans, le partage entre ex-conjoints, le
remariage. L'Agirc-Arrco sert 60 % des points sans le coefficient
d'anticipation de l'assuré retraité, dans la limite de sa retraite, l'Ircantec
la moitié et la RCI 60 % sans lui : le moteur applique les taux à la retraite
servie, coefficient compris.

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

from dataclasses import dataclass, replace
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

#: Les fiches dont les réversions se chiffrent après les autres, parce que
#: celles des autres régimes de base comptent à leurs ressources : le régime
#: général et les régimes alignés, puis la complémentaire des indépendants.
APRES_LES_BASES = ("reversion", "reversion_rci")


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
    #: La part du montant qui reverse la majoration pour enfants du défunt,
    #: hors du taux : l'Agirc-Arrco la reverse en entier depuis 2019.
    majoration: float = 0.0

    def donnees(self) -> dict:
        return {"regime": self.regime, "base": self.base, "taux": self.taux,
                "montant": self.montant, "motif": self.motif,
                "date_effet": self.date_effet, "fiche": self.fiche,
                "version": self.version, "texte": self.texte,
                "fiabilite": self.fiabilite.name.lower(),
                "majoration": self.majoration}


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


def _age_ircantec(parametres: dict, sexe: str) -> float:
    """L'âge requis à l'Ircantec : celui du conjoint depuis 2004 ; avant, celui
    de la veuve ou du veuf. Le veuf d'avant 1976, que l'arrêté ne servait pas,
    attend l'âge de la veuve : une approximation que la fiche déclare."""
    if parametres.get("age_minimum") is not None:
        return float(parametres["age_minimum"])
    veuf = parametres.get("age_minimum_veuf")
    if sexe == "H" and veuf is not None:
        return float(veuf)
    return float(parametres["age_minimum_veuve"])


def _mariage_ircantec(parametres: dict, conjoint: Conjoint, naissance: str, deces: str,
                      depart: str, enfants: int) -> bool:
    """La condition de l'article 20 de l'arrêté du 30 décembre 1970 : quatre ans
    de mariage au décès, ou un mariage contracté deux ans au moins avant les
    cinquante-cinq ans de l'agent né le jour ``naissance``, ou avant la
    cessation de ses fonctions — que le modèle tient pour son départ ; depuis
    1994, aucune durée quand un enfant est issu du mariage, que le modèle tient
    pour tout enfant déclaré."""
    if parametres.get("mariage_leve_par_enfant") and enfants > 0:
        return True
    avant = parametres["mariage_avant_annees"]
    limite = chrono._plus_ans(naissance, int(parametres["mariage_avant_age"]))
    return (chrono.annees_revolues(conjoint.mariage, deces)
            >= parametres["mariage_minimum_annees"]
            or chrono.annees_revolues(conjoint.mariage, limite) >= avant
            or chrono.annees_revolues(conjoint.mariage, depart) >= avant)


def _enfants_de_moins_de(carriere: Carriere, deces: str, ans: int) -> int:
    """Les enfants nés au décès qui n'ont pas encore ``ans`` ans : ceux que la
    chronologie porte, déclarés ou présumés, et que le modèle tient pour à la
    charge du survivant."""
    return sum(1 for _, naissance in carriere.naissances_des_enfants
               if naissance <= deces < chrono._plus_ans(naissance, ans))


def reversion(moteur: ScenarioActuel, pensions: list[tuple[str, float, Fiabilite]],
              carriere: Carriere, annee: int,
              deces_suppose: str | None = None,
              en_capital: frozenset[str] = frozenset(),
              majorations: dict[str, float] | None = None) -> Reversion | None:
    """La réversion que le décès de la personne de ``carriere`` ouvre à son
    conjoint, régime par régime ; ``None`` sans décès ou sans conjoint.

    ``pensions`` sont les pensions du défunt à l'année ``annee``, où les
    montants se chiffrent : ``(régime, montant, fiabilité)``, dans l'ordre de
    sa liquidation. Un régime qui ne lui sert rien n'a rien à reverser, ni
    celui qui lui a versé son droit en capital, quand la fiche le dit :
    ``en_capital`` nomme ces régimes. ``deces_suppose`` date le décès que la
    présomption ``deces_apres_le_depart`` suppose, quand la chronologie n'en
    dit pas. ``majorations`` donne, régime par régime, la majoration pour
    enfants du défunt aux mêmes euros que sa pension, hors d'elle : la version
    qui la dit réversible (``majoration_reversible``) en ajoute cette part.
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
    # La fonction publique, le RAFP, l'Ircantec et l'Agirc-Arrco d'abord : la
    # réversion d'un autre régime de base compte aux ressources du régime
    # général ; celle des complémentaires du régime général et des
    # indépendants, non (R. 353-1, 2°), et le RAFP, complémentaire de la
    # fonction publique, le dit dans sa fiche (``compte_aux_ressources``).
    autres_bases = 0.0
    for regime, base, fiabilite in pensions:
        fiche = table.fiche_du_regime(regime)
        if fiche is None:
            lignes[regime] = ReversionRegime(regime, base, 0.0, "non_portee")
            continue
        if fiche["id"] in APRES_LES_BASES:
            continue
        version = table.version(fiche, lendemain, deces)
        parametres = version["parametres"]
        if parametres.get("rien_apres_un_capital") and regime in en_capital:
            # Un droit direct versé en capital ne laisse rien à reverser : la
            # ligne ne s'écrit pas, comme celle d'un régime qui ne sert rien.
            continue
        taux = float(parametres["taux"])
        if fiche["id"] == "reversion_fonction_publique":
            servie = _mariage_suffit(parametres, conjoint, deces, depart, enfants)
            montant = taux * base if servie else 0.0
            autres_bases += montant
            lignes[regime] = ligne(regime, base, montant, "servie" if servie else "mariage",
                                   fiche, version, taux, lendemain, fiabilite)
            continue
        if fiche["id"] == "reversion_rafp":
            montant = taux * base
            if parametres.get("compte_aux_ressources"):
                autres_bases += montant
            lignes[regime] = ligne(regime, base, montant, "servie", fiche, version, taux,
                                   lendemain, fiabilite)
            continue
        if fiche["id"] == "reversion_ircantec":
            naissance = chrono.naissance(carriere.chronologie, carriere.personne)["debut"]
            servie = _mariage_ircantec(parametres, conjoint, naissance, deces, depart, enfants)
            date_effet = _a_l_age(conjoint.naissance, lendemain,
                                  _age_ircantec(parametres, conjoint.sexe))
            if (conjoint.sexe in (parametres.get("deux_enfants_sans_age") or ())
                    and _enfants_de_moins_de(
                        carriere, deces, int(parametres["deux_enfants_moins_de_ans"])) >= 2):
                # Deux enfants de moins de vingt et un ans à sa charge au décès
                # lèvent l'âge (article 21) : la réversion part au mois qui
                # suit le décès.
                date_effet = lendemain
            lignes[regime] = ligne(regime, base, taux * base if servie else 0.0,
                                   "servie" if servie else "mariage", fiche, version, taux,
                                   date_effet, fiabilite)
            continue
        date_effet = _a_l_age(conjoint.naissance, lendemain,
                              _age_agirc_arrco(parametres, regime, conjoint.sexe))
        if conjoint.invalidite is not None and parametres.get("invalidite_sans_age"):
            # L'invalidité du survivant, au décès ou plus tard, lève l'âge :
            # la réversion part au premier jour du mois qui la suit.
            date_effet = min(date_effet, max(lendemain, mois_suivant(conjoint.invalidite)))
        enfants_a_charge = parametres.get("deux_enfants_a_charge_moins_de_ans")
        if (enfants_a_charge is not None
                and _enfants_de_moins_de(carriere, deces, int(enfants_a_charge)) >= 2):
            # Deux enfants à charge du survivant au décès lèvent l'âge
            # (article 110), et la réversion reste servie quand ils cessent de
            # l'être (article 111) : elle part au mois qui suit le décès.
            date_effet = lendemain
        # La majoration pour enfants du défunt « réversible au taux de 100 % »
        # (article 109) : en plus des 60 %, qui ne la comptent pas.
        majoration = (float(parametres.get("majoration_reversible") or 0.0)
                      * (majorations or {}).get(regime, 0.0))
        lignes[regime] = replace(
            ligne(regime, base, taux * base + majoration, "servie", fiche, version, taux,
                  date_effet, fiabilite),
            majoration=majoration)

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

    # La complémentaire des indépendants en dernier : ses ressources sont
    # celles de R. 353-1, que les réversions de tous les régimes de base
    # grossissent (articles 17 et 35 de son règlement). Un dépassement de son
    # plafond réduit ses réversions à due concurrence, chacune au prorata de
    # son montant — celles d'une carrière d'artisan et d'une carrière de
    # commerçant d'avant 2013 comme une seule.
    independantes = []
    for regime, base, fiabilite in pensions:
        fiche = table.fiche_du_regime(regime)
        if fiche is None or fiche["id"] != "reversion_rci":
            continue
        version = table.version(fiche, lendemain, deces)
        if not version["parametres"].get("portee", True):
            lignes[regime] = ReversionRegime(regime, base, 0.0, "non_portee")
            continue
        independantes.append((regime, base, fiabilite, fiche, version))
    if independantes:
        parametres = independantes[0][4]["parametres"]
        plafond_annuel = (float(parametres["plafond_pass"])
                          * moteur.macro.plafond_securite_sociale(annee))
        brut = sum(float(version["parametres"]["taux"]) * base
                   for _, base, _, _, version in independantes)
        depassement = max(0.0, ressources + autres_bases + brut - plafond_annuel)
        for regime, base, fiabilite, fiche, version in independantes:
            parametres = version["parametres"]
            taux = float(parametres["taux"])
            montant = taux * base
            motif = "servie"
            if depassement > 0:
                montant, motif = max(0.0, montant - depassement * montant / brut), "ecretee"
            date_effet = _a_l_age(conjoint.naissance, lendemain,
                                  float(parametres["age_minimum"]))
            lignes[regime] = ligne(regime, base, montant, motif, fiche, version, taux,
                                   date_effet, fiabilite)

    return Reversion(
        personne=conjoint.personne, defunt=carriere.personne, deces=deces, annee=annee,
        ressources=ressources, ressources_presumees=presumees,
        regimes=tuple(lignes[regime] for regime, _, _ in pensions if regime in lignes),
        deces_suppose=deces_suppose is not None)
