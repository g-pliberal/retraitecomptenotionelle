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
* la CRPCEN (``reversion_crpcen``) : la moitié de la pension, sous la même
  condition de mariage, que l'article 113 du décret n° 90-1215 emprunte à
  L. 39 depuis 2006, et qu'il posait dans les mêmes termes à la veuve depuis
  1990 ;
* les IEG (``reversion_ieg``) : la moitié de la pension, majoration pour
  enfants comprise, sans âge ni ressources ; depuis le 1er juillet 2008, deux
  ans de mariage au décès quand il suit la liquidation, sauf enfant de
  l'union (annexe 3 au statut national, articles 22 et 24) ;
* le RAFP (``reversion_rafp``) : la moitié de la prestation, sans âge, sans
  ressources ni durée du mariage, et rien après un droit direct versé en
  capital — l'échéancier dit lesquels (``en_capital``) ;
* l'Ircantec (``reversion_ircantec``) : la moitié, à cinquante ans ou dès le
  décès avec deux enfants de moins de vingt et un ans, sous les conditions de
  durée du mariage de l'arrêté du 30 décembre 1970 ;
* la complémentaire des indépendants (``reversion_rci``) : 60 %, à l'âge du
  régime général, réduite à due concurrence d'un plafond de ressources, deux
  plafonds annuels de la Sécurité sociale, que les réversions des régimes de
  base comptent aussi, et le ménage du survivant qui vit en couple, sous le
  même plafond ; pour un décès d'avant 2013, sa ligne dit qu'elle n'est pas
  portée.

Les autres régimes n'ont pas encore de fiche : leur ligne le dit, sans montant.

LE RÉGIME GÉNÉRAL ET LES RÉGIMES ALIGNÉS, dans l'ordre où la caisse calcule
(exposés « Montant » et « Majoration » de la retraite de réversion ; circulaire
Cnav n° 2022-26, § 3.6) : le taux de la version, appliqué à la pension du
défunt « avant comparaison au minimum et au maximum » — sans la majoration de
L. 351-10 qui la portait au minimum contributif, avec ce que le maximum des
pensions en avait retiré (exposé « Retraite de l'assuré décédé ») —,
porté au MINIMUM de D. 353-1
— entier à soixante trimestres du défunt dans le régime, en soixantièmes en
deçà, et, depuis juillet 2004, au prorata de sa durée dans le régime quand
plusieurs régimes alignés en comptent plus de soixante ; entier, sans
soixantièmes, avant décembre 1982 — ; puis réduit du dépassement du plafond de
ressources — 2 080 heures de SMIC, 1,6 fois pour le MÉNAGE du survivant qui
vit en couple, marié, pacsé ou en concubinage, depuis juillet 2004, ses
revenus d'activité abattus de 30 % à cinquante-cinq ans depuis 2005 (L. 353-1,
D. 353-1-1, R. 353-1) ; avant juillet 2004, une condition d'ouverture, ses
retraites personnelles exceptées — ; puis ramené à son MAXIMUM, le taux du maximum des pensions
« opposable à l'assuré décédé » — l'ajournement d'avant 1983 le majorant —,
au plafond de l'année des montants, que 54 % de la surcote du défunt passent
(circulaires Cnav n° 120/82, § 4, n° 105/90, § 22, et n° 2018-4, § 5) ; puis,
avant juillet 2004, réduit par le CUMUL avec ces retraites personnelles, dans
la limite de 52 % — la moitié avant décembre 1982 — de leur total et de la
pension du défunt, la limite forfaitaire au moins, quand il ne les complète
pas seulement, avant juillet 1974 (D. 355-1) ; puis
majoré de 10 % pour le survivant de trois enfants, sans
descendre sous le dixième de son minimum (R. 353-2), hors du plafond, et de la
majoration forfaitaire par enfant à charge du survivant sans retraite,
depuis 1988 (L. 353-5, fiche ``majoration_forfaitaire_reversion``), réduite
comme la réversion ; enfin,
depuis 2010, majoré de 11,1 % de la réversion réduite quand le survivant a
l'âge du taux plein et que ses retraites, réversions et majorations comprises,
restent sous le plafond de L. 353-6, la majoration étant réduite de ce qui le
dépasse (D. 353-4). Une majoration qui commence après la date d'effet de la
ligne, quand le survivant n'a pas encore l'âge du taux plein, s'écrit à part,
avec sa date, hors du montant, comme les majorations forfaitaires de 4 % et
de 3,846 % qui relèvent, en décembre 1982 et en janvier 1995, la réversion
attribuée avant elles. Avant 1973, la réversion attend soixante-cinq ans,
soixante pour l'inapte (décret n° 72-1098).

LE PARTAGE ENTRE CONJOINTS : quand l'assuré a été marié plusieurs fois, chaque
régime partage sa réversion entre le conjoint survivant et les précédents
conjoints, divorcés, « au prorata de la durée respective de chaque mariage »,
« déterminée de date à date et arrondie au nombre de mois inférieur »
(L. 353-3, R. 353-4 ; L. 43 et L. 45 du code des pensions) ; le minimum et le
maximum du régime général se réduisent de même (circulaire Cnav n° 105/90,
§ 3). Chaque version dit qui partage (``ex_conjoints``) : aucun précédent
conjoint, quand elle ne sert que le survivant ; ceux qui ne se sont pas
remariés avant le décès, comme au régime général avant juillet 2004 ; ou tous.
L'Agirc-Arrco laisse la réversion entière au conjoint marié avant le 13
janvier 1998, quand le mariage précédent du défunt a été dissous avant le 1er
juillet 1980 (``entiere_au_conjoint``). La ligne du survivant dit sa part.

LE REMARIAGE DU SURVIVANT éteint la réversion des régimes dont la fiche le dit
(``perte_au_remariage``, les formes d'union qui l'éteignent) : la fonction
publique et la CRPCEN au mariage ou au concubinage notoire (L. 46), le RAFP
de même, l'Agirc-Arrco, l'Ircantec et les IEG au mariage ; la ligne s'arrête
au mois qui suit l'union, ou n'est pas servie quand l'union la précède. Au
régime général, le ménage ne compte au plafond que s'il est formé à la date
d'effet.

CE QUI N'EST PAS ENCORE PORTÉ, et que les fiches déclarent : la durée de la
majoration pour enfant à charge, la révision de la
réversion quand le ménage ou ses ressources changent, le plafonnement du veuf
de fonctionnaire d'avant 2004,
la minoration de l'Agirc avant soixante ans, la réversion des précédents
conjoints eux-mêmes. L'Agirc-Arrco sert 60 % des points sans le coefficient
d'anticipation de l'assuré retraité, dans la limite de sa retraite, l'Ircantec
la moitié et la RCI 60 % sans lui : le moteur applique les taux à la retraite
servie, coefficient compris.

LES MONTANTS sont ceux de l'année du décès : la pension du défunt y est menée
par « faire vivre », et le plafond du régime général s'y lit, au SMIC de cette
année-là. Pour un décès à venir, l'année courante, où s'arrêtent les
revalorisations publiées.

MORT AVANT SON DÉPART, l'assuré n'a pas de pension : la réversion se calcule
sur celle qu'il « eût obtenue » (L. 353-1), que l'échéancier liquide sur sa
carrière arrêtée au décès, sans décote — au régime général, « au titre de
l'inaptitude au travail » (R. 353-6), donc au taux plein, « quel que soit
l'âge de l'assuré au moment du décès » (exposé de la Cnav, « Retraite de
l'assuré décédé ») ; ailleurs, sans « coefficient de minoration » (L. 14, I,
du code des pensions) ni coefficient d'anticipation. Ses montants sont ceux de
l'année du décès, et la cessation d'activité que lisent les conditions de
mariage de la fonction publique, des IEG et de l'Ircantec est le décès.
:attr:`Reversion.avant_le_depart` le dit.

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
from ..somme import somme_ordonnee
from .coordonner import REGIMES_ALIGNES, lura_applicable
from .liquider import maximum_des_pensions

if TYPE_CHECKING:
    from ..carriere import Carriere, Conjoint
    from ..scenarios.actuel import ScenarioActuel

#: La version du schéma que :meth:`Reversion.donnees` suit.
SCHEMA_VERSION = 1

#: Ce que dit une ligne dont le montant est nul, ou qui n'est pas servie en
#: entier.
MOTIFS = {
    "servie": "servie",
    "minimum": "portée au minimum de la réversion (D. 353-1)",
    "maximum": "ramenée au maximum de la réversion, son taux du maximum des pensions",
    "ecretee": "réduite à due concurrence du plafond de ressources",
    "ressources": "ressources au-dessus du plafond",
    "cumul": "réduite par la limite de cumul avec ses retraites personnelles (D. 355-1)",
    "mariage": "condition d'antériorité ou de durée du mariage non remplie",
    "remariage": "perdue par l'union qu'il a formée avant sa date d'effet",
    "non_portee": "la réversion de ce régime n'est pas encore portée",
}

#: Les régimes dont les durées d'assurance du défunt s'additionnent pour
#: proratiser le minimum de la réversion du régime général depuis le 1er juillet
#: 2004, quand elles dépassent ensemble soixante trimestres : le régime général,
#: les salariés et non-salariés agricoles, les indépendants, les professions
#: libérales sauf les avocats, les cultes (exposé de la Cnav, « Montant -
#: retraite de réversion » ; circulaires n° 2005-17, § 22, et n° 2008-42, § 4).
REGIMES_DU_MINIMUM = ("regime_general", "msa_salaries", "msa_non_salaries", "organic",
                      "cancava", "rsi", "cnavpl", "cavimac")

#: La majoration de L. 353-6 ne prend pas effet avant cette date.
DEBUT_DE_LA_MAJORATION = "2010-01-01"

#: Les fiches dont les réversions se chiffrent après les autres, parce que
#: celles des autres régimes de base comptent à leurs ressources : le régime
#: général et les régimes alignés, puis la complémentaire des indépendants.
APRES_LES_BASES = ("reversion", "reversion_rci")

#: Les fiches qui servent la moitié de la pension sans âge ni ressources, sous
#: la condition de mariage de L. 39 : la fonction publique, et la CRPCEN, dont
#: l'article 113 du décret n° 90-1215 rend L. 39 applicable depuis 2006, après
#: une condition de 1990 qui avait les mêmes termes.
MOITIE_SOUS_CONDITION_DE_MARIAGE = ("reversion_fonction_publique", "reversion_crpcen")

#: Les fiches des régimes de base autres que le régime général et les régimes
#: alignés : leurs réversions servies divisent, avec celles des régimes
#: alignés, les retraites personnelles du survivant que la limite de cumul
#: d'avant juillet 2004 retient, et sa limite forfaitaire (D. 171-1 ; article
#: 91 du décret n° 45-179 ; exposé de la Cnav, « Retraite de réversion
#: cumulable »).
AUTRES_BASES = MOITIE_SOUS_CONDITION_DE_MARIAGE + ("reversion_ieg",)

#: La fiche de la majoration forfaitaire pour enfant à charge (L. 353-5).
MAJORATION_FORFAITAIRE = "majoration_forfaitaire_reversion"


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
    #: Le minimum que D. 353-1 garantit à cette réversion du régime général ou
    #: d'un régime aligné, soixantièmes et prorata faits ; 0 sans lui.
    minimum: float = 0.0
    #: La majoration de 10 % du survivant de trois enfants (L. 353-1, R. 353-2),
    #: comprise dans le montant.
    majoration_trois_enfants: float = 0.0
    #: La majoration de 11,1 % du survivant aux petites retraites (L. 353-6),
    #: et le jour où elle commence : comprise dans le montant quand elle
    #: commence au plus tard à la date d'effet de la ligne, à part sinon.
    majoration_petites_retraites: float = 0.0
    majoration_petites_retraites_effet: str | None = None
    #: La part de ``base`` que le minimum contributif y ajoute (L. 351-10) :
    #: la réversion du régime général et des régimes alignés se calcule sans
    #: elle, sur ``base - minimum_contributif``.
    minimum_contributif: float = 0.0
    #: Ce que le maximum des pensions avait retiré de ``base``, que la
    #: réversion du régime général reprend, et le maximum de cette réversion :
    #: son taux du maximum des pensions de l'année, l'ajournement d'avant 1983
    #: le majorant, et de la surcote du défunt ; 0 sans lui.
    ecretement_du_maximum: float = 0.0
    maximum: float = 0.0
    #: Le plafond de ressources auquel la réversion se mesure — celui d'une
    #: personne seule ou du ménage au régime général, deux plafonds de la
    #: Sécurité sociale à la complémentaire des indépendants —, et les
    #: ressources qu'il retient à côté d'elle : celles du survivant, ses
    #: revenus d'activité abattus, celles de son nouveau conjoint s'il vit en
    #: couple, les réversions des autres régimes de base ; 0 sans plafond.
    plafond: float = 0.0
    ressources_retenues: float = 0.0
    #: La part du survivant dans la réversion du régime, partagée avec les
    #: précédents conjoints au prorata des mariages (L. 353-3) : 1 sans eux.
    part: float = 1.0
    #: Le jour où l'union nouvelle du survivant éteint la réversion
    #: (``perte_au_remariage``), quand elle suit la date d'effet ; ``None``
    #: sinon.
    fin: str | None = None
    #: La limite de cumul de la réversion d'avant juillet 2004 avec les
    #: retraites personnelles du survivant (D. 355-1) : la plus haute de la
    #: limite forfaitaire, de la limite calculée et de la réversion même ;
    #: 0 sans elle.
    limite_cumul: float = 0.0
    #: La majoration forfaitaire pour enfant à charge (L. 353-5), comprise
    #: dans le montant.
    majoration_forfaitaire_enfants: float = 0.0
    #: Les majorations forfaitaires qui relèvent la réversion après sa date
    #: d'effet — 4 % au 1er décembre 1982, 3,846 % au 1er janvier 1995 —,
    #: chacune ``(jour, montant)``, hors du montant.
    majorations_forfaitaires: tuple[tuple[str, float], ...] = ()

    def donnees(self) -> dict:
        return {"regime": self.regime, "base": self.base, "taux": self.taux,
                "montant": self.montant, "motif": self.motif,
                "date_effet": self.date_effet, "fiche": self.fiche,
                "version": self.version, "texte": self.texte,
                "fiabilite": self.fiabilite.name.lower(),
                "majoration": self.majoration, "minimum": self.minimum,
                "majoration_trois_enfants": self.majoration_trois_enfants,
                "majoration_petites_retraites": self.majoration_petites_retraites,
                "majoration_petites_retraites_effet":
                    self.majoration_petites_retraites_effet,
                "minimum_contributif": self.minimum_contributif,
                "ecretement_du_maximum": self.ecretement_du_maximum,
                "maximum": self.maximum, "plafond": self.plafond,
                "ressources_retenues": self.ressources_retenues, "part": self.part,
                "fin": self.fin, "limite_cumul": self.limite_cumul,
                "majoration_forfaitaire_enfants": self.majoration_forfaitaire_enfants,
                "majorations_forfaitaires": [
                    {"date": jour, "montant": montant}
                    for jour, montant in self.majorations_forfaitaires]}


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
    #: Le défunt est-il mort avant son départ ? La réversion porte alors sur
    #: la pension qu'il « eût obtenue » à son décès (R. 353-6).
    avant_le_depart: bool = False

    @property
    def total(self) -> float:
        return somme_ordonnee(r.montant for r in self.regimes)

    def donnees(self) -> dict:
        return {"schema_version": SCHEMA_VERSION, "personne": self.personne,
                "defunt": self.defunt, "deces": self.deces,
                "deces_suppose": self.deces_suppose,
                "avant_le_depart": self.avant_le_depart, "annee": self.annee,
                "ressources": self.ressources,
                "ressources_presumees": self.ressources_presumees,
                "total": self.total,
                "regimes": [r.donnees() for r in self.regimes]}


def mois_suivant(jour: str) -> str:
    """Le premier jour du mois qui suit ``jour`` (AAAA-MM-JJ)."""
    annee, mois = int(jour[:4]), int(jour[5:7])
    annee, mois = (annee + 1, 1) if mois == 12 else (annee, mois + 1)
    return f"{annee:04d}-{mois:02d}-01"


def mois_de_mariage(debut: str, fin: str) -> int:
    """La durée d'un mariage, en mois : « déterminée de date à date et arrondie
    au nombre de mois inférieur » (R. 353-4)."""
    mois = (int(fin[:4]) - int(debut[:4])) * 12 + int(fin[5:7]) - int(debut[5:7])
    if int(fin[8:10]) < int(debut[8:10]):
        mois -= 1
    return max(0, mois)


def _part_du_survivant(carriere: Carriere, conjoint: Conjoint, deces: str,
                       admis) -> float:
    """La part du conjoint survivant dans la réversion d'un régime : la durée
    de son mariage, jusqu'au décès, rapportée à celle de tous les mariages
    dont les conjoints y ont droit — les précédents que ``admis`` retient
    (L. 353-3, R. 353-4 ; L. 45, puis L. 43, du code des pensions). Sans
    précédent conjoint retenu, la réversion entière."""
    autres = somme_ordonnee(mois_de_mariage(ex.mariage, ex.divorce)
                            for ex in carriere.ex_conjoints if admis(ex))
    if not autres:
        return 1.0
    propre = mois_de_mariage(conjoint.mariage, deces)
    return propre / (propre + autres)


def _remarie_avant(ex, deces: str) -> bool:
    """Le précédent conjoint s'est-il remarié avant le décès de l'assuré ?"""
    return ex.remariage is not None and ex.remariage <= deces


def _admis_au_regime_general(parametres: dict, deces: str, enfants: int):
    """Les précédents conjoints qui partagent la réversion du régime général :
    tous depuis juillet 2004 (L. 353-3) ; avant, les seuls « non remariés »
    dont le mariage a duré deux ans, sauf enfant issu du mariage (R. 353-4,
    rédaction de 1985), que le modèle tient pour tout enfant déclaré."""
    if parametres.get("ex_conjoints") == "tous":
        return lambda ex: True
    annees = parametres["mariage_minimum_annees"]
    return lambda ex: (not _remarie_avant(ex, deces)
                       and (not annees or enfants > 0
                            or chrono.annees_revolues(ex.mariage, ex.divorce) >= annees))


def _admis_ailleurs(parametres: dict, deces: str):
    """Les précédents conjoints qui partagent la réversion d'un autre régime,
    selon ce que la version dit (``ex_conjoints``) : aucun, quand elle ne sert
    que le conjoint survivant ; ceux qui ne se sont pas remariés avant le
    décès ; ou tous."""
    regle = parametres.get("ex_conjoints", "aucun")
    if regle == "tous":
        return lambda ex: True
    if regle == "non_remaries":
        return lambda ex: not _remarie_avant(ex, deces)
    return lambda ex: False


def _entiere_au_conjoint(parametres: dict, carriere: Carriere, conjoint: Conjoint) -> bool:
    """La réversion entière au conjoint survivant, malgré les précédents
    conjoints, quand la version le dit (``entiere_au_conjoint``) : à
    l'Agirc-Arrco, le conjoint marié avant le 13 janvier 1998, quand le mariage
    précédent du défunt a été dissous avant le 1er juillet 1980."""
    regle = parametres.get("entiere_au_conjoint")
    if not regle or not carriere.ex_conjoints or conjoint.mariage is None:
        return False
    return (conjoint.mariage < regle["marie_avant"]
            and max(ex.divorce for ex in carriere.ex_conjoints)
            < regle["precedent_dissous_avant"])


def _fin_au_remariage(parametres: dict, conjoint: Conjoint) -> str | None:
    """Le jour où l'union nouvelle du survivant éteint la réversion d'un
    régime qui la retire à cette forme d'union (``perte_au_remariage``) : le
    premier jour du mois qui suit l'union ; ``None`` sinon."""
    if (conjoint.nouvelle_union is None or conjoint.nouvelle_union_depuis is None
            or conjoint.nouvelle_union not in (parametres.get("perte_au_remariage") or ())):
        return None
    return mois_suivant(conjoint.nouvelle_union_depuis)


def _jusqu_au_remariage(ligne_: ReversionRegime, parametres: dict,
                        conjoint: Conjoint) -> ReversionRegime:
    """La ligne, arrêtée par l'union nouvelle du survivant : sans montant quand
    l'union précède sa date d'effet, jusqu'à elle sinon."""
    fin = _fin_au_remariage(parametres, conjoint)
    if fin is None or ligne_.date_effet is None or ligne_.montant <= 0:
        return ligne_
    if fin <= ligne_.date_effet:
        return replace(ligne_, montant=0.0, motif="remariage", majoration=0.0)
    return replace(ligne_, fin=fin)


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


def _mariage_ieg(parametres: dict, conjoint: Conjoint, deces: str, depart: str,
                 enfants: int) -> bool:
    """La condition de l'article 24 de l'annexe 3 au statut national des IEG :
    aucune quand le mariage précède la liquidation de la pension — que le
    modèle tient pour le départ —, sinon deux ans de mariage au décès, « sauf
    dans les cas où un enfant est né de l'union », que le modèle tient pour
    tout enfant déclaré. Sans durée dans la version, aucune condition."""
    minimum = parametres.get("mariage_minimum_annees")
    if minimum is None or enfants > 0 or conjoint.mariage <= depart:
        return True
    return chrono.annees_revolues(conjoint.mariage, deces) >= minimum


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


def _date_d_effet_du_regime_general(parametres: dict, conjoint: Conjoint,
                                    lendemain: str) -> str:
    """La date d'effet que l'âge de la version reporte : l'âge requis, ou,
    avant 1973, soixante ans pour le survivant inapte au travail
    (``age_inaptitude``), que le modèle tient pour celui qui déclare son
    invalidité, au plus tôt le mois qui la suit."""
    date_effet = _a_l_age(conjoint.naissance, lendemain, float(parametres["age_minimum"]))
    inaptitude = parametres.get("age_inaptitude")
    if inaptitude is not None and conjoint.invalidite is not None:
        date_effet = min(date_effet, max(
            _a_l_age(conjoint.naissance, lendemain, float(inaptitude)),
            mois_suivant(conjoint.invalidite)))
    return date_effet


def _premiere_date_d_effet(table, fiche: dict, conjoint: Conjoint, lendemain: str,
                           deces: str) -> str:
    """La première date d'effet de la réversion du régime général : l'âge
    requis la reporte, et la date d'effet choisit la version, dont l'âge
    change — soixante-cinq ans avant 1973, cinquante-cinq ensuite. C'est la
    plus proche des dates que chaque version permet : au plus tôt à son début
    et à l'âge qu'elle requiert, avant sa fin. Le survivant de cinquante-cinq
    ans d'un assuré mort en 1970 la reçoit ainsi au 1er janvier 1973 (décret
    n° 72-1098, article 5)."""
    possibles = []
    for version in fiche["versions"]:
        debut, fin = version["bornes"].get("liquidation.date_effet", [None, None])
        jour = max(lendemain, debut or lendemain)
        jour = _date_d_effet_du_regime_general(version["parametres"], conjoint, jour)
        if fin is not None and jour >= fin:
            continue
        retenue = table.version(fiche, jour, deces)
        if retenue is not None and retenue["id"] == version["id"]:
            possibles.append(jour)
    return min(possibles, default=lendemain)


def _cumuler(parametres: dict, montant: float, retraites: float, principale: float,
             forfaitaire: float | None, reversions: int) -> tuple[float, float]:
    """La réversion d'avant juillet 2004 qu'il reste quand le survivant a ses
    propres retraites, et la limite de cumul : ``(montant, limite)``.

    Avant le 1er juillet 1974 (``cumul: aucun``), la réversion ne se cumule
    pas : elle complète la retraite personnelle, qu'elle dépasse. Depuis
    (``cumul: limite``), elle se cumule « dans la limite de 52 p. 100 » — la
    moitié avant décembre 1982 — « du total de ces avantages et de la pension
    principale » du défunt, prise avant le minimum et le maximum, limite qui
    ne peut être inférieure à la limite forfaitaire, ni à la réversion portée
    au minimum ou ramenée au maximum ; au-delà, la réversion « est réduite en
    conséquence » (D. 355-1 ; article 90 du décret n° 45-179 ; exposé de la
    Cnav, « Retraite de réversion cumulable »). Les retraites du survivant et
    la limite forfaitaire se divisent par le nombre de ses ``reversions`` de
    base (D. 171-1)."""
    regle = parametres.get("cumul")
    if regle is None or montant <= 0 or retraites <= 0:
        return montant, 0.0
    retenues = retraites / max(1, reversions)
    if regle == "aucun":
        return max(0.0, montant - retenues), 0.0
    limite = max(montant, float(parametres["cumul_taux"]) * (retenues + principale),
                 (forfaitaire or 0.0) / max(1, reversions))
    # Elle « n'était pas servie si le dépassement atteignait » son montant.
    return max(0.0, montant - max(0.0, montant + retenues - limite)), limite


def _majoration_forfaitaire_enfants(moteur: ScenarioActuel, carriere: Carriere,
                                    conjoint: Conjoint, retraites: float,
                                    date_effet: str, annee: int
                                    ) -> tuple[float, Fiabilite] | None:
    """La majoration forfaitaire ENTIÈRE pour enfant à charge (L. 353-5), à la
    date d'effet de la réversion : le montant annuel par enfant, par les enfants
    nés que le modèle tient pour à la charge du survivant, sous l'âge de la
    version ; ``None`` quand elle n'est pas due.

    Le survivant ne doit pas avoir de retraite personnelle d'un régime de base
    (``retraites``, ses ressources hors de ses revenus d'activité), ni l'âge
    que R. 353-9 fixe à la demande — soixante-cinq ans, puis l'âge du taux
    plein depuis le 3 juin 2011 —, ni vivre en couple avant juillet 2004."""
    table = moteur.reversions
    fiche = table.fiche(MAJORATION_FORFAITAIRE)
    if fiche is None or retraites > 0:
        return None
    version = table.version(fiche, date_effet, carriere.deces or date_effet)
    parametres = version["parametres"] if version else {}
    if not parametres.get("servie"):
        return None
    if parametres.get("age_maximum") is not None:
        if chrono.annees_revolues(conjoint.naissance, date_effet) >= int(
                parametres["age_maximum"]):
            return None
    if parametres.get("age_du_taux_plein"):
        generation = round(int(conjoint.naissance[:4])
                           + (int(conjoint.naissance[5:7]) - 1) / 12, 3)
        age = moteur.ages_annulation_decote.age(generation)
        if age is None or _atteint(conjoint.naissance, age[0]) <= date_effet:
            return None
    if (parametres.get("refusee_en_couple") and conjoint.nouvelle_union is not None
            and (conjoint.nouvelle_union_depuis or date_effet) <= date_effet):
        return None
    enfants = _enfants_de_moins_de(carriere, date_effet, int(parametres["enfant_moins_de_ans"]))
    par_enfant = table.majoration_enfant(annee)
    if enfants == 0 or par_enfant is None:
        return None
    return (enfants * par_enfant[0],
            min(par_enfant[1], Fiabilite.depuis_texte(parametres["fiabilite"])))


def _majorations_ulterieures(parametres: dict, date_effet: str, calcule: float,
                             minimum: float, maximum: float
                             ) -> tuple[tuple[str, float], ...]:
    """Les majorations forfaitaires qui relèvent la réversion attribuée avant
    leur date (``majorations_forfaitaires``) : 4 % au 1er décembre 1982, puis
    3,846 % au 1er janvier 1995, qui la portent du taux de 50 % à celui de
    52 %, puis de 54 %. Elles s'appliquent au « montant calculé » de la
    réversion, avant le minimum, après les précédentes (exposé de la Cnav,
    « Montant - retraite de réversion ») : chacune est ce qu'elle ajoute à la
    réversion portée au minimum et ramenée au maximum, ``(jour, montant)``."""
    def servie(facteur: float) -> float:
        montant = max(minimum, calcule * facteur)
        return min(montant, maximum) if maximum > 0 else montant
    ecrites, facteur = [], 1.0
    for majoration in parametres.get("majorations_forfaitaires") or ():
        if str(majoration["date"]) <= date_effet:
            continue
        nouveau = facteur * (1 + float(majoration["taux"]))
        ecrites.append((str(majoration["date"]), servie(nouveau) - servie(facteur)))
        facteur = nouveau
    return tuple(ecrites)


def _atteint(naissance: str, age: float) -> str:
    """Le jour où le survivant né le jour ``naissance`` atteint ``age``, compté
    en mois."""
    mois = round(age * 12)
    annee = int(naissance[:4]) + (int(naissance[5:7]) - 1 + mois) // 12
    numero = (int(naissance[5:7]) - 1 + mois) % 12 + 1
    return f"{annee:04d}-{numero:02d}-{naissance[8:10]}"


def _au_taux_plein(naissance: str, age: float) -> str:
    """Le jour où la majoration de L. 353-6 peut commencer : le premier jour du
    mois qui suit l'âge du taux plein, ou l'anniversaire même du survivant né
    le premier jour d'un mois (R. 353-13 ; exposé de la Cnav, « Majoration de
    la retraite de réversion »). L'âge se compte en mois : soixante-six ans et
    deux mois pour la génération 1953."""
    atteint = _atteint(naissance, age)
    return atteint if naissance[8:10] == "01" else mois_suivant(atteint)


def _part_du_minimum(parametres: dict, regime: str, durees: dict[str, int] | None,
                     lura: bool = False) -> float:
    """La part du minimum de D. 353-1 que sert la réversion de ``regime`` :
    entière avant le 1er décembre 1982 ; ensuite, autant de soixantièmes que le
    défunt a de trimestres d'assurance dans le régime, soixante au plus ;
    depuis le 1er juillet 2004, quand ses durées dans les régimes alignés
    (:data:`REGIMES_DU_MINIMUM`) dépassent ensemble soixante trimestres et
    qu'il en a dans plusieurs, sa durée dans le régime rapportée à leur total.
    Sous la liquidation unique (``lura``), la pension d'un des régimes qu'elle
    réunit est la leur : ses durées s'y additionnent, et ils ne comptent que
    pour un régime (exposé de la Cnav, « Retraite de l'assuré décédé »). Sans
    durées dites, la part entière."""
    if not parametres.get("minimum_proratise") or durees is None:
        return 1.0
    seuil = float(parametres["minimum_trimestres"])
    groupes = [(r,) for r in REGIMES_DU_MINIMUM if not (lura and r in REGIMES_ALIGNES)]
    if lura:
        groupes.insert(0, tuple(r for r in REGIMES_DU_MINIMUM if r in REGIMES_ALIGNES))
    durees_des_groupes = {groupe: somme_ordonnee(durees.get(r, 0) for r in groupe)
                          for groupe in groupes}
    propre = float(next((duree for groupe, duree in durees_des_groupes.items()
                         if regime in groupe), durees.get(regime, 0)))
    alignes = [duree for duree in durees_des_groupes.values() if duree > 0]
    total = float(somme_ordonnee(alignes))
    if parametres.get("minimum_tous_regimes") and len(alignes) > 1 and total > seuil:
        return propre / total
    return min(1.0, propre / seuil)


def _enfants_de_moins_de(carriere: Carriere, deces: str, ans: int) -> int:
    """Les enfants nés au décès qui n'ont pas encore ``ans`` ans : ceux que la
    chronologie porte, déclarés ou présumés, et que le modèle tient pour à la
    charge du survivant."""
    return somme_ordonnee(1 for _, naissance in carriere.naissances_des_enfants
               if naissance <= deces < chrono._plus_ans(naissance, ans))


def _ressources_du_plafond(parametres: dict, conjoint: Conjoint, ressources: float,
                           date_effet: str) -> tuple[float, float]:
    """Les ressources du survivant que retient le plafond de la version, et le
    facteur qui multiplie ce plafond (L. 353-1, D. 353-1-1, R. 353-1).

    Ses revenus d'activité sont abattus de 30 % quand il a cinquante-cinq ans à
    la date d'effet, « quel que soit l'âge atteint au moment où ces revenus ont
    été perçus » (circulaire Cnav n° 2006-37, § 7). Quand il vit en couple —
    marié, pacsé ou en concubinage —, les ressources de son nouveau conjoint
    s'y ajoutent, entières, sous le plafond du ménage (circulaire Cnav
    n° 2005-17, § 141 et § 145) : 1,6 fois celui d'une personne seule au
    régime général, le même à la complémentaire des indépendants. La version
    qui ne dit pas ce facteur, avant juillet 2004, ne compte que ses ressources
    personnelles."""
    taux = parametres.get("abattement_activite")
    if (taux and conjoint.revenus_d_activite
            and chrono.annees_revolues(conjoint.naissance, date_effet)
            >= int(parametres["abattement_activite_age"])):
        ressources -= float(taux) * min(ressources, float(conjoint.revenus_d_activite))
    facteur = parametres.get("facteur_menage")
    if (facteur is None or conjoint.nouvelle_union is None
            or (conjoint.nouvelle_union_depuis or date_effet) > date_effet):
        # Le ménage ne compte que formé à la date d'effet : celui qui se forme
        # après réviserait la réversion (R. 353-1-1), ce que le modèle ne fait
        # pas.
        return ressources, 1.0
    return (ressources + float(conjoint.ressources_du_nouveau_conjoint or 0.0),
            float(facteur))


def _majorer_les_petites_retraites(moteur: ScenarioActuel,
                                   lignes: dict[str, ReversionRegime],
                                   reduites: dict[str, tuple[float, dict]],
                                   conjoint: Conjoint, retraites_personnelles: float,
                                   annee: int) -> None:
    """La majoration de 11,1 % des réversions des régimes alignés (L. 353-6),
    écrite dans ``lignes``, une fois toutes les réversions chiffrées.

    Elle est due au survivant qui a l'âge du taux plein (L. 351-8, 1°) et dont
    les retraites — ``retraites_personnelles``, ses ressources déclarées hors
    de ses revenus d'activité, et toutes ses réversions, de base et
    complémentaires, majorations comprises — restent sous le plafond de
    D. 353-4, quatre fois
    le plafond trimestriel ; elle vaut 11,1 % de la réversion réduite, et se
    réduit de ce qui dépasserait le plafond, partagée entre les régimes au
    prorata de leurs réversions (R. 353-12 ; exposé de la Cnav, « Majoration à
    plusieurs régimes »). Elle commence au premier jour du mois qui suit l'âge
    du taux plein, jamais avant le 1er janvier 2010 ni avant la réversion.
    """
    eligibles = {regime: (montant, parametres) for regime, (montant, parametres)
                 in reduites.items()
                 if montant > 0 and parametres.get("majoration_taux") is not None}
    plafond = moteur.reversions.plafond_majoration(annee)
    generation = round(int(conjoint.naissance[:4]) + (int(conjoint.naissance[5:7]) - 1) / 12, 3)
    age = moteur.ages_annulation_decote.age(generation)
    if not eligibles or plafond is None or age is None:
        return
    debut = _au_taux_plein(conjoint.naissance, age[0])
    retraites = retraites_personnelles + somme_ordonnee(l.montant for l in lignes.values())
    theoriques = {regime: float(parametres["majoration_taux"]) * montant
                  for regime, (montant, parametres) in eligibles.items()}
    marge = 4 * plafond[0] - retraites
    total = somme_ordonnee(theoriques.values())
    if marge <= 0 or total <= 0:
        return
    servie = min(total, marge)
    reversions = somme_ordonnee(montant for montant, _ in eligibles.values())
    for regime, (montant, _) in eligibles.items():
        majoration = (theoriques[regime] if servie == total
                      else servie * montant / reversions)
        ligne_du_regime = lignes[regime]
        effet = max(debut, DEBUT_DE_LA_MAJORATION, ligne_du_regime.date_effet)
        comprise = effet <= ligne_du_regime.date_effet
        lignes[regime] = replace(
            ligne_du_regime,
            montant=ligne_du_regime.montant + (majoration if comprise else 0.0),
            majoration_petites_retraites=majoration,
            majoration_petites_retraites_effet=effet,
            fiabilite=min(ligne_du_regime.fiabilite, plafond[1], age[1]))


def reversion(moteur: ScenarioActuel, pensions: list[tuple[str, float, Fiabilite]],
              carriere: Carriere, annee: int,
              deces_suppose: str | None = None,
              en_capital: frozenset[str] = frozenset(),
              majorations: dict[str, float] | None = None,
              durees: dict[str, int] | None = None,
              minima: dict[str, float] | None = None,
              maxima: dict[str, tuple[float, float, float]] | None = None,
              avant_le_depart: bool = False
              ) -> Reversion | None:
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
    ``durees`` donne la durée d'assurance du défunt dans chaque régime, enfants
    compris, que le minimum du régime général proratise ; sans elle, il est
    servi entier. ``minima`` donne, régime par régime, la part de la pension
    que le minimum contributif y ajoute, aux mêmes euros : le régime général
    et les régimes alignés reversent la pension sans elle. ``maxima`` donne,
    régime par régime, ce que le maximum des pensions a retiré de la pension,
    ce que la surcote y ajoute, aux mêmes euros, et le coefficient de
    l'ajournement d'avant 1983 ou du taux acquis au 31 mars 1983, qui
    multiplie son maximum : le régime général reverse la pension d'avant son
    maximum, sous le maximum de la réversion. ``avant_le_depart`` dit que le
    défunt est mort avant son départ, et que ``pensions`` sont celles qu'il eût
    obtenues à son décès.
    """
    conjoint = carriere.conjoint
    deces = carriere.deces if deces_suppose is None else deces_suppose
    if deces is None or conjoint is None:
        return None
    lendemain = mois_suivant(deces)
    # La cessation d'activité que lisent les conditions de mariage : le départ,
    # ou le décès qui le précède.
    depart = min(deces, f"{carriere.date_liquidation.annee:04d}"
                        f"-{carriere.date_liquidation.mois:02d}-01")
    enfants = carriere.nombre_enfants
    presumees = conjoint.ressources is None
    ressources = 0.0 if presumees else float(conjoint.ressources)
    # Ses retraites personnelles : ses ressources, moins ce que son activité
    # lui rapporte ; la limite de cumul d'avant 2004, la majoration pour
    # enfant à charge et celle de 11,1 % les lisent.
    retraites_personnelles = ressources - min(ressources,
                                              float(conjoint.revenus_d_activite or 0.0))
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
        # La part du survivant, partagée avec les précédents conjoints au
        # prorata des mariages, et la ligne arrêtée par son union nouvelle.
        part = (1.0 if _entiere_au_conjoint(parametres, carriere, conjoint)
                else _part_du_survivant(carriere, conjoint, deces,
                                        _admis_ailleurs(parametres, deces)))
        if fiche["id"] in MOITIE_SOUS_CONDITION_DE_MARIAGE:
            servie = _mariage_suffit(parametres, conjoint, deces, depart, enfants)
            montant = taux * base * part if servie else 0.0
            lignes[regime] = _jusqu_au_remariage(replace(
                ligne(regime, base, montant, "servie" if servie else "mariage",
                      fiche, version, taux, lendemain, fiabilite), part=part),
                parametres, conjoint)
            autres_bases += lignes[regime].montant
            continue
        if fiche["id"] == "reversion_ieg":
            # La moitié de la pension, « majoration pour enfant comprise »
            # (annexe 3 au statut national des IEG, article 22).
            servie = _mariage_ieg(parametres, conjoint, deces, depart, enfants)
            majoration = (float(parametres.get("majoration_reversible") or 0.0)
                          * (majorations or {}).get(regime, 0.0) * part) if servie else 0.0
            montant = taux * base * part + majoration if servie else 0.0
            lignes[regime] = _jusqu_au_remariage(replace(
                ligne(regime, base, montant, "servie" if servie else "mariage", fiche,
                      version, taux, lendemain, fiabilite),
                majoration=majoration, part=part), parametres, conjoint)
            autres_bases += lignes[regime].montant
            continue
        if fiche["id"] == "reversion_rafp":
            lignes[regime] = _jusqu_au_remariage(replace(
                ligne(regime, base, taux * base * part, "servie", fiche, version, taux,
                      lendemain, fiabilite), part=part), parametres, conjoint)
            if parametres.get("compte_aux_ressources"):
                autres_bases += lignes[regime].montant
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
            lignes[regime] = _jusqu_au_remariage(replace(
                ligne(regime, base, taux * base * part if servie else 0.0,
                      "servie" if servie else "mariage", fiche, version, taux,
                      date_effet, fiabilite), part=part), parametres, conjoint)
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
                      * (majorations or {}).get(regime, 0.0) * part)
        lignes[regime] = _jusqu_au_remariage(replace(
            ligne(regime, base, taux * base * part + majoration, "servie", fiche, version,
                  taux, date_effet, fiabilite),
            majoration=majoration, part=part), parametres, conjoint)

    # Le plafond de ressources est un : les réversions des régimes alignés se
    # l'imputent l'une après l'autre, dans l'ordre de la liquidation.
    minimum_de_l_annee = table.minimum(annee)
    lura = lura_applicable(carriere)
    #: La réversion de chaque régime aligné, réduite, avant ses majorations :
    #: ce que la majoration de 11,1 % multiplie.
    reduites: dict[str, tuple[float, dict]] = {}
    #: Leur réversion entière, portée au minimum et ramenée au maximum, avant
    #: les ressources et le cumul, et leur date d'effet : la majoration pour
    #: enfant à charge se réduit dans la proportion de la réduite à l'entière.
    entieres: dict[str, float] = {}
    # Les réversions de base du survivant, qui divisent ses retraites et la
    # limite forfaitaire du cumul d'avant 2004 : celles des régimes alignés,
    # et celles des autres régimes de base servies.
    reversions_de_base = (
        somme_ordonnee(1 for regime, _, _ in pensions
                       if (table.fiche_du_regime(regime) or {}).get("id") == "reversion")
        + somme_ordonnee(1 for regime, ligne_ in lignes.items()
                         if ligne_.montant > 0 and ligne_.fiche in AUTRES_BASES))
    for regime, base, fiabilite in pensions:
        fiche = table.fiche_du_regime(regime)
        if fiche is None or fiche["id"] != "reversion":
            continue
        date_effet = _premiere_date_d_effet(table, fiche, conjoint, lendemain, deces)
        version = table.version(fiche, date_effet, deces)
        parametres = version["parametres"]
        taux = float(parametres["taux"])
        # La « pension principale » (L. 353-1), que la caisse prend « avant
        # comparaison au minimum et au maximum » : sans la majoration qui la
        # portait au minimum contributif (L. 351-10), avec ce que le maximum
        # des pensions en avait retiré (exposé de la Cnav, « Retraite de
        # l'assuré décédé » ; circulaire n° 105/90, § 22).
        contributif = min(base, (minima or {}).get(regime, 0.0))
        ecretement, surcote, coefficient = (maxima or {}).get(regime, (0.0, 0.0, 1.0))
        # Partagée avec les précédents conjoints au prorata des mariages, la
        # réversion l'est avec son minimum et son maximum (circulaire Cnav
        # n° 105/90, § 3).
        part = _part_du_survivant(carriere, conjoint, deces,
                                  _admis_au_regime_general(parametres, deces, enfants))
        montant = taux * (base - contributif + ecretement) * part
        motif = "servie"
        # Le minimum de D. 353-1, avant les ressources : la caisse porte la
        # réversion au minimum, puis la réduit du dépassement du plafond.
        minimum = 0.0
        if minimum_de_l_annee is not None and parametres.get("minimum_trimestres"):
            minimum = minimum_de_l_annee[0] * _part_du_minimum(parametres, regime, durees,
                                                               lura) * part
            if minimum > montant:
                montant, motif = minimum, "minimum"
                fiabilite = min(fiabilite, minimum_de_l_annee[1])
        # Le plafond, d'une personne seule ou du ménage, et ce qu'il retient à
        # côté de la réversion : les ressources du survivant, ou du ménage, et
        # les réversions des autres régimes de base — avant juillet 2004, ses
        # ressources personnelles « sans tenir compte des avantages de
        # réversion » (R. 353-1, rédactions de 1985 et de 1990).
        retenues, facteur = _ressources_du_plafond(parametres, conjoint, ressources,
                                                   date_effet)
        plafond_annuel = (facteur * float(parametres["plafond_smic_heures"])
                          * moteur.macro.smic_horaire(annee))
        reversions = autres_bases if parametres["ressources"] == "ecretement" else 0.0
        if parametres.get("cumul") is not None:
            # Avant juillet 2004, ses retraites personnelles « n'étaient pas
            # retenues dans les ressources » : elles se cumulaient avec la
            # réversion dans une limite (exposé de la Cnav, « Condition de
            # ressources »).
            retenues -= min(retenues, retraites_personnelles)
        disponible = plafond_annuel - retenues - reversions
        retenues += reversions
        if not _mariage_dure(conjoint, deces, enfants, parametres["mariage_minimum_annees"]):
            montant, motif = 0.0, "mariage"
        elif parametres["ressources"] == "ecretement":
            if montant > disponible:
                montant, motif = max(0.0, disponible), "ecretee"
        elif disponible < 0:
            montant, motif = 0.0, "ressources"
        # Le maximum, ensuite : la réversion « réduite pour cumul ou
        # ressources » est comparée au maximum (exposé de la Cnav), son taux du
        # maximum des pensions « qui était ou aurait été opposable à l'assuré
        # décédé » (circulaires n° 120/82, § 4, et n° 3/95, § 13) — celui de
        # sa date d'effet, au plafond de l'année des montants, l'ajournement
        # d'avant 1983 le majorant —, auquel s'ajoute son taux de la surcote,
        # que rien ne ramène (circulaire n° 2018-4, § 5).
        maximum = 0.0
        des_pensions = maximum_des_pensions(moteur, regime, date_effet, annee)
        if des_pensions is not None:
            maximum = taux * (des_pensions[0] * coefficient + surcote) * part
            if montant > maximum:
                montant, motif = maximum, "maximum"
                fiabilite = min(fiabilite, des_pensions[1])
        entieres[regime] = (min(max(taux * (base - contributif + ecretement) * part, minimum),
                                maximum) if maximum > 0
                            else max(taux * (base - contributif + ecretement) * part, minimum))
        # Le cumul d'avant juillet 2004 avec ses retraites personnelles, après
        # le maximum : la limite « ne pouvait pas être inférieure à la
        # retraite de réversion portée au minimum ou ramenée au maximum ».
        forfaitaire = table.limite_cumul(annee)
        cumulee, limite_cumul = _cumuler(
            parametres, montant, retraites_personnelles, base - contributif + ecretement,
            None if forfaitaire is None else forfaitaire[0], reversions_de_base)
        if cumulee < montant:
            montant, motif = cumulee, "cumul"
            if forfaitaire is not None and parametres.get("cumul") == "limite":
                fiabilite = min(fiabilite, forfaitaire[1])
        autres_bases += montant
        # La majoration de 10 % du survivant de trois enfants, sur la réversion
        # réduite et hors du plafond (circulaire Cnav n° 2022-26, § 3.6), au
        # moins le dixième du minimum de la réversion (R. 353-2) ; le
        # survivant est tenu pour avoir eu les enfants que déclare le défunt.
        trois_enfants = 0.0
        if montant > 0 and enfants >= 3:
            taux_enfants = float(parametres["majoration_enfants_taux"])
            trois_enfants = max(taux_enfants * montant,
                                float(parametres.get("majoration_enfants_minimum") or 0.0)
                                * minimum)
        reduites[regime] = (montant, parametres)
        lignes[regime] = replace(
            ligne(regime, base, montant + trois_enfants, motif, fiche, version, taux,
                  date_effet, fiabilite),
            minimum=minimum, majoration_trois_enfants=trois_enfants,
            minimum_contributif=contributif, ecretement_du_maximum=ecretement,
            maximum=maximum, plafond=plafond_annuel, ressources_retenues=retenues,
            part=part, limite_cumul=limite_cumul,
            majorations_forfaitaires=(
                _majorations_ulterieures(parametres, date_effet,
                                         taux * (base - contributif + ecretement) * part,
                                         minimum, maximum)
                if montant > 0 else ()))

    # La complémentaire des indépendants en dernier : ses ressources sont
    # celles de R. 353-1, « personnelles ou du ménage », que les réversions de
    # tous les régimes de base grossissent (articles 17 et 35 de son
    # règlement). Un dépassement de son plafond, le même pour un ménage,
    # réduit ses réversions à due concurrence, chacune au prorata de son
    # montant — celles d'une carrière d'artisan et d'une carrière de
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
        part = _part_du_survivant(carriere, conjoint, deces,
                                  _admis_ailleurs(version["parametres"], deces))
        independantes.append((regime, base, fiabilite, fiche, version, part))
    if independantes:
        parametres = independantes[0][4]["parametres"]
        retenues, facteur = _ressources_du_plafond(
            parametres, conjoint, ressources,
            _a_l_age(conjoint.naissance, lendemain, float(parametres["age_minimum"])))
        plafond_annuel = (facteur * float(parametres["plafond_pass"])
                          * moteur.macro.plafond_securite_sociale(annee))
        retenues += autres_bases
        brut = somme_ordonnee(float(version["parametres"]["taux"]) * base * part
                   for _, base, _, _, version, part in independantes)
        depassement = max(0.0, retenues + brut - plafond_annuel)
        for regime, base, fiabilite, fiche, version, part in independantes:
            parametres = version["parametres"]
            taux = float(parametres["taux"])
            montant = taux * base * part
            motif = "servie"
            if depassement > 0 and brut > 0:
                montant, motif = max(0.0, montant - depassement * montant / brut), "ecretee"
            date_effet = _a_l_age(conjoint.naissance, lendemain,
                                  float(parametres["age_minimum"]))
            lignes[regime] = replace(
                ligne(regime, base, montant, motif, fiche, version, taux, date_effet,
                      fiabilite),
                plafond=plafond_annuel, ressources_retenues=retenues, part=part)

    # La majoration forfaitaire pour enfant à charge, servie par un seul
    # régime : le régime général s'il sert une réversion, sinon le premier
    # régime aligné qui en sert une ; réduite dans la proportion de la
    # réversion réduite à l'entière (D. 353-2 ; exposé de la Cnav).
    servant = next((regime for regime in sorted(
        (r for r, (montant, _) in reduites.items() if montant > 0),
        key=lambda r: r != "regime_general")), None)
    if servant is not None:
        ligne_du_regime = lignes[servant]
        entiere = _majoration_forfaitaire_enfants(
            moteur, carriere, conjoint, retraites_personnelles,
            ligne_du_regime.date_effet, annee)
        if entiere is not None:
            reduite = reduites[servant][0]
            majoration = entiere[0] * (min(1.0, reduite / entieres[servant])
                                       if entieres[servant] > 0 else 0.0)
            lignes[servant] = replace(
                ligne_du_regime, montant=ligne_du_regime.montant + majoration,
                majoration_forfaitaire_enfants=majoration,
                fiabilite=min(ligne_du_regime.fiabilite, entiere[1]))

    # Ses retraites personnelles, que la majoration de 11,1 % compte.
    _majorer_les_petites_retraites(
        moteur, lignes, reduites, conjoint, retraites_personnelles, annee)

    return Reversion(
        personne=conjoint.personne, defunt=carriere.personne, deces=deces, annee=annee,
        ressources=ressources, ressources_presumees=presumees,
        regimes=tuple(lignes[regime] for regime, _, _ in pensions if regime in lignes),
        deces_suppose=deces_suppose is not None, avant_le_depart=avant_le_depart)
