"""La réversion : la pension du survivant, dans les régimes du défunt (§ 7.3).

« La réversion n'est pas une étape. C'est ``liquider`` pour le survivant, de
motif « réversion », dans les régimes du défunt. » Elle lit la liquidation du
défunt — ici son départ, menée jusqu'à son décès par « faire vivre » — et
applique à chaque régime la version de sa fiche que les dates choisissent :

* le régime général et les régimes alignés (fiche ``reversion``) : un taux de
  la pension, à partir d'un âge, sous un plafond de ressources — condition
  d'ouverture avant juillet 2004, écrêtement depuis — ; les points d'avant
  1973 des artisans et des commerçants de même, au même taux, sans les
  majorations pour enfants (décret n° 73-937, article 9) ;
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
* la SNCF (``reversion_sncf``) : la moitié de la pension, majorée pour enfants
  comme elle, sans âge ni ressources, au conjoint marié deux ans le jour de la
  cessation des fonctions, ou quatre ans au décès, deux avec un enfant du
  mariage, sans durée quand un enfant est né avant la cessation ; rien au
  survivant en concubinage au décès, et l'union qu'il forme après ne l'éteint
  pas ; quand la pension de l'agent atteint le minimum de pension, 54 % de ce
  minimum au moins, 51,3 % et 52,7 % avant juillet 2010 (décret n° 2008-639,
  articles 15, 18 à 20 et 31) ;
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
soixantièmes, avant décembre 1982 ; le régime étant celui qui succède aux
caisses du défunt, la CANCAVA et l'ORGANIC le RSI, et leurs droits d'avant
1973 avec elles, dont le minimum borne avec la réversion alignée « le montant
cumulé » (D. 634-14 ; décret n° 73-937, article 7-2) — ; puis réduit du
dépassement du plafond de ressources — 2 080 heures de SMIC, 1,6 fois pour le
MÉNAGE du survivant qui
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
pas seulement, avant juillet 1974 (D. 355-1), à sa date d'effet, ou au jour
où sa propre retraite, qu'il date, la suit, aux règles de ce jour. Une
retraite qu'il prend depuis juillet 2004 la RECALCULE aux règles de ressources
de 2004, à sa date d'effet ; attribuée depuis, ou ainsi recalculée, la
réversion se RÉVISE le mois qui suit chaque changement que la chronologie
date — sa retraite, le ménage qu'il forme, ses cinquante-cinq ans qui abattent
ses revenus d'activité — (R. 353-1-1), sous le plafond de ce jour, ses
ressources des trois mois qui la précèdent comptées telles que perçues, puis
une fois encore quand ces trois mois ne portent plus que ce qui suit le
changement, jusqu'à la DERNIÈRE révision : trois mois après sa retraite ; sa
date d'effet quand il a ses retraites sans la dater ; le mois qui suit son âge
légal quand il n'a ni retraite ni activité. Puis
majoré de 10 % pour le survivant de trois enfants, sans
descendre sous le dixième de son minimum (R. 353-2), hors du plafond, et de la
majoration forfaitaire par enfant à charge du survivant sans retraite,
depuis 1988 (L. 353-5, fiche ``majoration_forfaitaire_reversion``), réduite
comme la réversion, tant que chaque enfant est à charge et que le survivant
n'a pas sa propre retraite ; enfin,
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
régime général, le ménage compte au plafond formé à la date d'effet, ou à la
révision qu'il ouvre le mois qui suit. La SNCF ne l'éteint pas, elle la fige ;
mais le survivant qui vit en concubinage au décès n'en jouit pas
(``sans_jouissance_au_deces``).

CE QUI N'EST PAS ENCORE PORTÉ, et que les fiches déclarent : la révision de la
réversion quand le ménage se défait ou que les ressources varient sans que la
chronologie le date, le plafonnement du veuf
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
from datetime import date
from typing import TYPE_CHECKING

from .. import chronologie as chrono
from ..donnees.chargement import Fiabilite
from ..somme import somme_ordonnee
from .coordonner import (REGIMES_ALIGNES, REGIMES_ALIGNES_TETE, lura_applicable, regimes_de,
                         tete_de_succession)
from .liquider import maximum_des_pensions

if TYPE_CHECKING:
    from collections.abc import Callable

    from ..carriere import Carriere, Conjoint
    from ..scenarios.actuel import ScenarioActuel

#: La version du schéma que :meth:`Reversion.donnees` suit.
SCHEMA_VERSION = 1

#: Ce que dit une ligne dont le montant est nul, ou qui n'est pas servie en
#: entier.
MOTIFS = {
    "servie": "servie",
    "minimum": "portée au minimum de la réversion (D. 353-1 ; décret n° 2008-639, article 18)",
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
#: Chacun sous sa tête de succession : voir :func:`_groupes_du_minimum`.
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
AUTRES_BASES = MOITIE_SOUS_CONDITION_DE_MARIAGE + ("reversion_ieg", "reversion_sncf")

#: Les fiches qui reversent la moitié de la majoration pour enfants du défunt
#: avec la moitié de sa pension : les IEG, « majoration pour enfant comprise »,
#: et la SNCF, dont la réversion est « majorée dans les conditions fixées à
#: l'article 16 ».
MOITIE_MAJORATION_COMPRISE = ("reversion_ieg", "reversion_sncf")

#: Les lignes de la cascade dont :func:`reversion` lit la part dans chaque
#: pension (``minima``) : le minimum contributif, sans lequel le régime général
#: reverse la pension, et le minimum de pension de la SNCF, dont la pension
#: relevée se reverse au minimum de l'article 18.
MINIMA_REVERSES = ("minimum_contributif", "minimum_pension_sncf")

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
    #: d'un régime aligné, soixantièmes et prorata faits, ou l'article 18 du
    #: décret n° 2008-639 à celle de la SNCF, sa part faite ; 0 sans lui.
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
    #: dans le montant, et ce qu'elle devient ensuite : depuis chaque jour où
    #: le nombre des enfants à charge change, ``(jour, montant)``, la dernière
    #: étape nulle — le dernier enfant n'est plus à charge, ou le survivant a
    #: sa propre retraite.
    majoration_forfaitaire_enfants: float = 0.0
    majoration_forfaitaire_enfants_etapes: tuple[tuple[str, float], ...] = ()
    #: Les majorations forfaitaires qui relèvent la réversion après sa date
    #: d'effet — 4 % au 1er décembre 1982, 3,846 % au 1er janvier 1995 —,
    #: chacune ``(jour, montant)``, hors du montant.
    majorations_forfaitaires: tuple[tuple[str, float], ...] = ()
    #: Le jour où la retraite personnelle du survivant, qui suit la date
    #: d'effet, revoit la réversion d'avant juillet 2004 par la limite de cumul
    #: de ce jour (D. 355-1), et ce qu'elle en retire alors, majoration de 10 %
    #: comprise, hors du montant : ``None`` et 0 sans elle. ``limite_cumul``
    #: est alors la limite de ce jour.
    cumul_effet: str | None = None
    reduction_du_cumul: float = 0.0
    #: Le jour de la dernière révision de la réversion sous le plafond de
    #: ressources (R. 353-1-1) — le recalcul aux règles de 2004 qu'ouvre la
    #: retraite du survivant quand elle les précède, la révision qui suit sa
    #: retraite, le ménage qu'il forme ou ses cinquante-cinq ans sinon —, et ce
    #: qu'elle en retire alors, majoration de 10 % comprise, négatif quand elle
    #: y ajoute, hors du montant : ``None`` et 0 sans révision. ``revisions``
    #: les dit toutes, ``(jour, ce qu'elle retire)``, dans l'ordre.
    revision_effet: str | None = None
    reduction_de_la_revision: float = 0.0
    revisions: tuple[tuple[str, float], ...] = ()
    #: Les ressources que chaque révision retient à côté de la réversion, par
    #: an, ``(jour, ressources)`` dans l'ordre de ``revisions`` : celles des
    #: trois mois qui la précèdent (:func:`_ressources_des_trois_mois`), et les
    #: réversions des autres régimes de base ce jour-là.
    ressources_des_revisions: tuple[tuple[str, float], ...] = ()
    #: Le jour d'où la réversion soumise aux règles de ressources n'est plus
    #: révisable (R. 353-1-1) : trois mois après la retraite que le survivant
    #: date ; sa date d'effet quand il a, sans la dater, des retraites ; le
    #: mois qui suit son âge légal quand il n'a ni retraite ni activité ;
    #: ``None`` quand il travaille sans retraite datée, et pour la réversion
    #: d'avant juillet 2004 qu'aucune retraite n'a recalculée.
    derniere_revision: str | None = None

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
                "majoration_forfaitaire_enfants_etapes": [
                    {"date": jour, "montant": montant}
                    for jour, montant in self.majoration_forfaitaire_enfants_etapes],
                "majorations_forfaitaires": [
                    {"date": jour, "montant": montant}
                    for jour, montant in self.majorations_forfaitaires],
                "cumul_effet": self.cumul_effet,
                "reduction_du_cumul": self.reduction_du_cumul,
                "revision_effet": self.revision_effet,
                "reduction_de_la_revision": self.reduction_de_la_revision,
                "revisions": [{"date": jour, "reduction": reduction,
                               "ressources": dict(self.ressources_des_revisions).get(jour)}
                              for jour, reduction in self.revisions],
                "derniere_revision": self.derniere_revision}


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


def _sans_jouissance_au_deces(ligne_: ReversionRegime, parametres: dict,
                              conjoint: Conjoint, deces: str) -> ReversionRegime:
    """La ligne sans montant quand le survivant vit, au décès, dans une union
    que la version dit sans jouissance (``sans_jouissance_au_deces``) : à la
    SNCF, « Le conjoint survivant vivant en concubinage au moment du décès de
    l'agent ou du retraité ne peut entrer en jouissance de sa pension »
    (décret n° 2008-639, article 19, I). L'union dont la saisie ne dit pas le
    début commence au décès."""
    if (ligne_.montant > 0
            and conjoint.nouvelle_union in (parametres.get("sans_jouissance_au_deces") or ())
            and conjoint.nouvelle_union_depuis is not None
            and conjoint.nouvelle_union_depuis <= deces):
        return replace(ligne_, montant=0.0, motif="remariage", majoration=0.0)
    return ligne_


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


def _mariage_sncf(parametres: dict, conjoint: Conjoint, deces: str, depart: str,
                  naissances: list[str]) -> bool:
    """La condition de l'article 19, I, du décret n° 2008-639 : deux ans de
    mariage le jour de la cessation des fonctions — que le modèle tient pour
    le départ —, ou quatre ans au décès, deux s'il existe un enfant issu du
    mariage ; aucune durée quand un enfant est né avant la cessation. Le
    modèle tient tout enfant déclaré, né aux jours ``naissances``, pour un
    enfant des conjoints."""
    if any(naissance < depart for naissance in naissances):
        return True
    if (chrono.annees_revolues(conjoint.mariage, depart)
            >= parametres["mariage_cessation_minimum_annees"]):
        return True
    minimum = parametres["mariage_minimum_annees_avec_enfant" if naissances
                         else "mariage_minimum_annees"]
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


def _retraites_au(conjoint: Conjoint, retraites: float, jour: str) -> float:
    """Les retraites personnelles du survivant servies le jour ``jour`` :
    toutes, sauf quand sa propre retraite, qu'il date, ne prend effet
    qu'après (présomption ``retraites_du_survivant_servies`` sinon)."""
    return 0.0 if conjoint.retraite is not None and conjoint.retraite > jour else retraites


#: Avant cette date, la limite de cumul revue à l'attribution des droits
#: personnels du survivant, quand ils suivent la réversion, tenait la pension du
#: défunt pour « 100/52èmes de la pension de réversion effectivement servie à
#: la date à laquelle les droits personnels sont attribués », le double avant
#: le 1er décembre 1982 (circulaire Cnav n° 31/75, § 2521) ; depuis, pour celle
#: qui a servi de base à la réversion, revalorisée jusque-là (circulaire Cnav
#: n° 105/90 du 15 novembre 1990, § 12 et 13).
PRINCIPALE_REVALORISEE_DEPUIS = "1990-11-15"


def _cumul_a_la_retraite(moteur: ScenarioActuel, fiche: dict, conjoint: Conjoint,
                         deces: str, annee: int, date_effet: str, servie: float,
                         ulterieures: tuple[tuple[str, float], ...], retraites: float,
                         principale: float, reversions: int,
                         personnelles: tuple[tuple[str, float], ...] = ()
                         ) -> tuple[str, float, float, float, Fiabilite] | None:
    """La réversion d'avant juillet 2004 revue à l'attribution de la retraite
    personnelle du survivant, quand elle suit sa date d'effet : ``(jour,
    servie, ce qu'il en reste, limite, fiabilité)``, ou ``None`` sans elle.

    « Les règles de cumul s'appliquaient à la date d'attribution du 2e
    avantage : soit au point de départ de l'avantage personnel s'il était
    attribué après la retraite de réversion » (exposé de la Cnav, « Retraite de
    réversion cumulable ») — celles de ce jour, que la version en vigueur alors
    dit : sa limite forfaitaire, le taux de sa limite calculée, ou, avant
    juillet 1974, la réversion qui complète la retraite (D. 355-1). La
    réversion servie ce jour-là, ``servie`` et les majorations forfaitaires
    ``ulterieures`` déjà venues, s'y cumule avec ses ``retraites`` ; la pension
    du défunt est ``principale``, celle qui a servi de base à la réversion, que
    les montants de l'année tiennent revalorisée jusque-là (circulaire Cnav
    n° 105/90, § 13), et que les majorations forfaitaires venues depuis la
    date d'effet relèvent (``personnelles``), ou, avant le 15 novembre 1990,
    la réversion servie rapportée au taux de la limite
    (:data:`PRINCIPALE_REVALORISEE_DEPUIS`). La
    limite forfaitaire de l'année de ce jour se ramène aux euros de ``annee``
    par les coefficients qui revalorisent les pensions. Une retraite
    attribuée depuis le 1er juillet 2004 recalcule la réversion « compte tenu
    des règles de ressources applicables » alors : :func:`_revisions`."""
    jour = conjoint.retraite
    if jour is None or jour <= date_effet or servie <= 0 or retraites <= 0:
        return None
    alors = moteur.reversions.version(fiche, jour, deces)
    parametres = alors["parametres"] if alors is not None else {}
    if parametres.get("cumul") is None:
        return None
    servie += somme_ordonnee(montant for quand, montant in ulterieures if quand <= jour)
    for quand, taux in personnelles:
        if date_effet < quand <= jour:
            principale *= 1 + taux
    if jour < PRINCIPALE_REVALORISEE_DEPUIS and parametres.get("cumul_taux"):
        principale = servie / float(parametres["cumul_taux"])
    fiabilite = Fiabilite.depuis_texte(parametres["fiabilite"])
    forfaitaire = moteur.reversions.limite_cumul(int(jour[:4]))
    en_euros = None
    if forfaitaire is not None:
        coefficient, fiabilite_coefficient = moteur.revalorisations_pensions.generale(
            date(annee, 12, 31), date(int(jour[:4]), 12, 31), False, None)
        en_euros = forfaitaire[0] / coefficient
        fiabilite = min(fiabilite, forfaitaire[1], fiabilite_coefficient)
    reste, limite = _cumuler(parametres, servie, retraites, principale, en_euros, reversions)
    return jour, servie, reste, limite, fiabilite


def _annee_du_plafond(moteur: ScenarioActuel, annee: int, jour: str) -> int:
    """L'année dont le SMIC fait le plafond d'une révision du jour ``jour`` :
    la sienne, ou, quand le barème ne la publie pas encore, la dernière qu'il
    publie — les montants d'une réversion s'arrêtent à l'année courante, et un
    SMIC projeté n'en est pas un —, jamais avant l'année des montants."""
    alors = int(jour[:4])
    while alors > annee and moteur.macro.smic_horaire.fiabilite(alors) <= Fiabilite.ESTIMEE:
        alors -= 1
    return alors


def _servie_au(montant: float, etapes: tuple[tuple[str, float], ...], jour: str) -> float:
    """Ce qu'une réversion sert le jour ``jour`` : ``montant``, ou ce qu'en a
    fait la dernière de ses ``etapes``, ``(jour, montant)``, venue ce jour-là."""
    servie = montant
    for quand, revue in etapes:
        if quand <= jour:
            servie = revue
    return servie


def _revisions(moteur: ScenarioActuel, fiche: dict, parametres: dict, conjoint: Conjoint,
               deces: str, annee: int, date_effet: str, servie: float, entiere: float,
               ulterieures: tuple[tuple[str, float], ...], ressources: float,
               retraites: float, bases: Callable[[str], float], derniere: str | None,
               regime: str) -> tuple[tuple[str, float, float, Fiabilite, float], ...]:
    """Les révisions de la réversion du régime ``regime`` sous le plafond de
    ressources, dans l'ordre de leurs jours : ``(jour, servie, revue,
    fiabilité, ressources)`` chacune.

    Attribuée avant juillet 2004 (``cumul``), la réversion n'est revue que par
    une retraite personnelle prise depuis, que le survivant date : elle est
    alors « recalculée compte tenu des règles de ressources applicables depuis
    le 01/07/2004 » (exposé de la Cnav, « Retraite de réversion cumulable »),
    « à compter de la date d'effet de l'avantage personnel » (circulaire Cnav
    n° 2005-17, § 31), les règles de cumul supprimées avec elles (lettre
    ministérielle du 22 mars 2005, § 1) ; « dans tous les autres cas », elle
    « continue d'être servie selon les règles applicables avant cette date »
    (exposé « Condition de ressources »), et c'est :func:`_cumul_a_la_retraite`
    qui la revoit. Attribuée depuis (``ecretement``), ou ainsi recalculée, elle
    « est révisable en cas de variation dans le montant des ressources »
    (R. 353-1-1), « à partir du 1er jour du mois qui suit la date de
    modification des ressources » (circulaire Cnav n° 2010/58, § 21), ou de
    l'attribution d'une retraite (§ 22) — que le modèle tient pour constatée le
    mois même avant le 30 juin 2010 (circulaire Cnav n° 2006-37, § 6). Les
    changements que la chronologie date : sa retraite ; le ménage qu'il forme,
    car « le remariage du bénéficiaire entraîne la révision de la retraite de
    réversion pour tenir compte des ressources du nouveau ménage » (exposé
    « Condition de ressources »), et celui qui se défait — « décès du
    conjoint, du concubin, du partenaire pacsé », « divorce », « résiliation
    d'un Pacs », « fin du concubinage », autant de changements de la
    situation familiale qui changent « le plafond de ressources à retenir
    (personne seule ou ménage) » et « le montant des ressources elles-mêmes »
    (lettre de la Cnav du 18 avril 2007) ; la fin de son activité, comme dans
    l'exemple de la circulaire n° 2010/58, § 21 (cessée le 15 février 2008,
    révisée le 1er mars) ; « la variation des revenus professionnels du
    conjoint survivant (ou du ménage) » (circulaire Cnav n° 2006-6, § 12) — un
    salaire qui change, une activité reprise, les ressources de son nouveau
    conjoint qui changent —, révisée de même ; ses cinquante-cinq ans, quand
    ils abattent les revenus de l'activité qu'il exerce alors, la caisse
    l'interrogeant « pour appliquer cette mesure aux pensions de réversion en
    cours de service » (circulaire Cnav n° 2007-35, § 221). Le survivant est
    tenu pour déclarer chacun (R. 815-38), et pour demander le rétablissement
    de la réversion que ses ressources avaient réduite à rien (circulaire Cnav
    n° 2005-17, § 321). Aucune révision après ``derniere`` : « A partir de
    cette date de dernière révision, aucun changement de ressources ou de
    situation familiale n'est pris en compte » (:func:`_derniere_revision`).

    Chaque révision lit le plafond de la version de son jour, au SMIC de son
    année (:func:`_annee_du_plafond`), ramené aux euros de ``annee`` par les
    coefficients qui revalorisent les pensions, en 2020 ceux des pensions de
    2 000 € par mois au plus, que ne passent pas les ressources d'un survivant
    sous le plafond ; à côté de la réversion, les ressources « des 3 mois qui
    précèdent cette date de révision » (:func:`_ressources_des_trois_mois`),
    qui portent encore, le mois qui suit un changement, celles d'avant lui —
    un changement du jour même ne compte qu'à la révision du mois qui suit —,
    et ``bases(jour)``, les réversions des autres régimes de base ce jour-là.
    Le modèle la révise encore le premier mois dont les trois mois ne portent
    plus que ce qui suit chaque changement compté tel que perçu
    (:func:`_apres_les_trois_mois`) — pour sa retraite, quand la révision
    qu'elle ouvre ne la compte que pour ce qu'elle sert, c'est la dernière
    révision, trois mois après elle, comme dans l'exemple de la circulaire
    n° 2010/58, § 24 (retraites au 1er janvier 2008, révision au 1er février,
    « dernière révision (cristallisation) » au 1er avril) —, sauf quand elle
    n'y change rien : les textes ne disent pas ce que la caisse fait de ces
    trois mois après la première révision, et sans elle les revenus d'avant le
    changement pèseraient jusqu'au suivant. Le recalcul aux règles de 2004
    compte, comme une date d'effet, ses ressources de ce jour, l'année
    entière, sa retraite et son ménage du jour même
    (:func:`_ressources_du_plafond`). La réversion revue est ``entiere``,
    d'avant les ressources et le cumul, avec les majorations forfaitaires
    ``ulterieures`` venues, réduite du dépassement ; ``servie``, avec elles,
    celle qu'elle remplace ; ``ressources``, ce que le plafond retient à côté
    d'elle."""
    retraite = conjoint.retraite
    # Chaque jour de révision, et s'il est celui du recalcul aux règles de 2004.
    jours: dict[str, bool] = {}
    if parametres.get("cumul") is not None:
        if retraite is None or retraite <= date_effet or retraites <= 0 or servie <= 0:
            return ()
        depuis = retraite
        jours[retraite] = True
    elif parametres.get("ressources") == "ecretement":
        depuis = date_effet
        if retraite is not None and retraite > date_effet and retraites > 0:
            jours[mois_suivant(retraite)] = False
    else:
        return ()
    # Les changements de ses ressources, comptés tels que perçus : la fin de son
    # activité, ses revenus qui varient, ce qu'apporte son nouveau conjoint, qui
    # varie ; et le ménage qu'il forme ou qui se défait, dont les ressources
    # se transposent.
    percus = [conjoint.fin_d_activite] if conjoint.revenus_d_activite else []
    percus += [quand for quand, _ in conjoint.variations_d_activite]
    familiaux = []
    if conjoint.nouvelle_union is not None:
        familiaux = [conjoint.nouvelle_union_depuis, conjoint.nouvelle_union_fin]
        percus += [quand for quand, _ in conjoint.variations_du_nouveau_conjoint]
    for change in percus + familiaux:
        if change is not None and change > depuis:
            jours.setdefault(mois_suivant(change), False)
    alors = moteur.reversions.version(fiche, depuis, deces)
    regles = alors["parametres"] if alors is not None else {}
    if regles.get("abattement_activite"):
        abattement = chrono._plus_ans(conjoint.naissance,
                                      int(regles["abattement_activite_age"]))
        if abattement > depuis and _activite_au(conjoint, abattement, True):
            jours.setdefault(mois_suivant(abattement), False)
    # Le premier mois dont les trois mois ne portent plus que ce qui suit chaque
    # changement compté tel que perçu, sa retraite comprise quand la révision
    # qu'elle ouvre ne la compte que pour ce qu'elle sert.
    if (parametres.get("cumul") is None and retraite is not None and retraite > date_effet
            and retraites > 0):
        premiere = moteur.reversions.version(fiche, mois_suivant(retraite), deces)
        if not _retraites_entieres(premiere["parametres"] if premiere is not None else {},
                                   regime, mois_suivant(retraite)):
            percus.append(retraite)
    apres: set[str] = set()
    for change in percus:
        if change is not None and change > depuis and _apres_les_trois_mois(change) not in jours:
            jours[_apres_les_trois_mois(change)] = False
            apres.add(_apres_les_trois_mois(change))
    revisions = []
    for jour in sorted(jours):
        if derniere is not None and jour > derniere:
            break
        alors = moteur.reversions.version(fiche, jour, deces)
        regles = alors["parametres"] if alors is not None else {}
        if regles.get("ressources") != "ecretement":
            continue
        recalcul = jours[jour]
        venues = somme_ordonnee(montant for quand, montant in ulterieures if quand <= jour)
        if recalcul:
            commencees = retraite is None or retraite <= jour
            retenues, facteur = _ressources_du_plafond(
                regles, conjoint, ressources - (0.0 if commencees else retraites), jour)
        else:
            retenues, facteur = _ressources_des_trois_mois(
                regles, conjoint, retraites, jour, _retraites_entieres(regles, regime, jour))
        an = _annee_du_plafond(moteur, annee, jour)
        coefficient, fiabilite_coefficient = moteur.revalorisations_pensions.generale(
            date(annee, 12, 31), date(an, 12, 31), False, 0.0)
        plafond = (facteur * float(regles["plafond_smic_heures"])
                   * moteur.macro.smic_horaire(an) / coefficient)
        autres = bases(jour)
        revue = max(0.0, min(entiere + venues, plafond - retenues - autres))
        if jour in apres and revue == (revisions[-1][2] if revisions else servie + venues):
            # Les trois mois d'après le changement n'y changent rien.
            continue
        fiabilite = min(Fiabilite.depuis_texte(regles["fiabilite"]), fiabilite_coefficient)
        revisions.append((jour, servie + venues, revue, fiabilite, retenues + autres))
    return tuple(revisions)


def _retraites_entieres(parametres: dict, regime: str, jour: str) -> bool:
    """La révision du jour ``jour`` compte-t-elle les retraites du survivant
    entières, dès qu'elles ont commencé, et non pour ce qu'elles servent dans
    les trois mois qui la précèdent ? Au régime général avant le 30 juin 2010,
    « ce qui revient à prendre en compte 3 mois de DP alors qu'un seul mois est
    servi (ce qui correspond à la méthode retenue par le régime général mais
    non par le RSI, la MSA et la CNAVPL) » (circulaire RSI n° 2007/061,
    annexe 3, § 6.2), jusqu'à ce que la circulaire Cnav n° 2010/58 (§ 22) lui
    fasse compter « les sommes réellement perçues au titre du nouvel
    avantage » : la version le dit, régime par régime, par le jour d'où les
    révisions les comptent telles que perçues
    (``retraites_entieres_a_la_revision``)."""
    jusqu_au = (parametres.get("retraites_entieres_a_la_revision") or {}).get(regime)
    return jusqu_au is not None and jour < str(jusqu_au)


def _en_mois(jour: str) -> float:
    """Le jour ``jour`` compté en mois, chaque mois de trente jours, comme la
    caisse transpose les ressources : « Tous les mois sont considérés comme
    valant 30 jours », et un changement « le 31 d'un mois » n'y laisse qu'un
    jour (circulaire RSI n° 2007/061, annexe 3, § 7)."""
    quantieme = min(int(jour[8:10]), 30)
    return 12 * int(jour[:4]) + int(jour[5:7]) - 1 + (quantieme - 1) / 30


def _percu(montant: float, changements, debut: float, fin: float) -> float:
    """Ce qu'une ressource de ``montant`` par an rapporte par an, en moyenne
    sur la période de ``debut`` à ``fin`` (en mois, :func:`_en_mois`), chacun
    de ses ``changements``, ``(jour, montant)``, la portant à son montant à
    partir de son jour : ce montant même quand aucun ne tombe dans la
    période."""
    total, depuis = 0.0, debut
    for jour, nouveau in sorted(changements):
        quand = _en_mois(jour)
        if quand >= fin:
            break
        if quand > depuis:
            total += montant * (quand - depuis)
            depuis = quand
        montant = nouveau
    if depuis == debut:
        return montant
    return (total + montant * (fin - depuis)) / (fin - debut)


def _ressources_des_trois_mois(parametres: dict, conjoint: Conjoint, retraites: float,
                               jour: str, entieres: bool) -> tuple[float, float]:
    """Les ressources du survivant qu'une révision du jour ``jour`` retient
    sous le plafond de la version, par an, et le facteur qui multiplie ce
    plafond (R. 353-1-1).

    « Les ressources sont examinées sur les 3 mois qui précèdent cette date de
    révision » (exposé de la Cnav, « Condition de ressources »), « les 3 mois
    civils précédant la date d'effet de la révision » (circulaire RSI
    n° 2007/061, annexe 3, § 5.2), en mois de trente jours (:func:`_en_mois`) :
    ses revenus d'activité « pour leur montant réellement perçu au cours de la
    période de référence » (§ 6.1), et de même ce qu'apporte son nouveau
    conjoint ; ses ``retraites`` personnelles pour ce qu'elles servent dans
    ces trois mois, depuis le jour où elles prennent effet, « les sommes
    réellement perçues au titre du nouvel avantage » (circulaire Cnav
    n° 2010/58, § 22), ou ``entieres`` dès qu'elles ont commencé
    (:func:`_retraites_entieres`). Quand sa situation familiale change dans ces
    trois mois — le ménage formé ou défait —, les ressources d'après le
    changement « sont ensuite transposées sur la période de référence
    entière » (exposé « Condition de ressources » ; circulaire Cnav
    n° 2005/17, § 146 ; circulaire RSI n° 2007/061, annexe 3, § 7). Ses revenus
    d'activité sont abattus quand il a l'âge de l'abattement ce jour-là,
    « quel que soit l'âge atteint au moment où ces revenus ont été perçus »
    (circulaire Cnav n° 2006-37, § 7) ; le plafond est celui du ménage quand il
    vit en couple ce jour-là, comme à la date d'effet
    (:func:`_ressources_du_plafond`)."""
    fin = _en_mois(jour)
    debut = fin - 3
    if conjoint.nouvelle_union is not None:
        for change in (conjoint.nouvelle_union_depuis, conjoint.nouvelle_union_fin):
            if change is not None and change < jour:
                debut = max(debut, _en_mois(change))
    changements = list(conjoint.variations_d_activite)
    if conjoint.fin_d_activite is not None:
        changements.append((conjoint.fin_d_activite, 0.0))
    activite = _percu(float(conjoint.revenus_d_activite or 0.0), changements, debut, fin)
    taux = parametres.get("abattement_activite")
    if (taux and activite
            and chrono.annees_revolues(conjoint.naissance, jour)
            >= int(parametres["abattement_activite_age"])):
        activite -= float(taux) * activite
    retraite = conjoint.retraite
    if retraite is None:
        servies = retraites
    elif entieres:
        servies = retraites if retraite < jour else 0.0
    else:
        servies = _percu(0.0, [(retraite, retraites)], debut, fin)
    ressources = activite + servies
    facteur = parametres.get("facteur_menage")
    union = conjoint.nouvelle_union_depuis
    if (facteur is None or conjoint.nouvelle_union is None
            or not (union is None or union < jour)
            or _venu(conjoint.nouvelle_union_fin, jour, False)):
        return ressources, 1.0
    apport = _percu(float(conjoint.ressources_du_nouveau_conjoint or 0.0),
                    conjoint.variations_du_nouveau_conjoint, debut, fin)
    return ressources + apport, float(facteur)


def _trois_mois_apres(jour: str) -> str:
    """Le premier jour du troisième mois qui suit celui de ``jour``."""
    return mois_suivant(mois_suivant(mois_suivant(jour)))


def _apres_les_trois_mois(jour: str) -> str:
    """Le premier jour du premier mois dont les trois mois qui précèdent
    suivent tous le jour ``jour`` : le troisième mois qui suit le sien quand
    ``jour`` est le premier d'un mois, le quatrième sinon."""
    trois = _trois_mois_apres(jour)
    return trois if jour[8:10] == "01" else mois_suivant(trois)


def _generation(naissance: str) -> float:
    """La génération de qui est né le jour ``naissance``, comme les tables par
    génération la lisent : l'année, et la part écoulée avant son mois."""
    return round(int(naissance[:4]) + (int(naissance[5:7]) - 1) / 12, 3)


def _derniere_revision(moteur: ScenarioActuel, conjoint: Conjoint, date_effet: str,
                       retraites: float) -> str | None:
    """Le jour d'où la réversion soumise aux règles de ressources n'est plus
    révisable (R. 353-1-1).

    a) « Un délai de trois mois après la date à laquelle le conjoint survivant
    est entré en jouissance de l'ensemble des avantages personnels de retraite
    de base et complémentaire », que le modèle lui sert tous au jour qu'il
    date, ou sa date d'effet quand il en jouit depuis plus longtemps : elle
    « n'est plus révisable dès son point de départ » (circulaire Cnav
    n° 2010/58, § 24) — c'est le cas, sans retraite datée, de ses
    ``retraites``, servies depuis plus de trois mois (présomption
    ``retraites_du_survivant_servies``). Qui travaille sans les avoir
    liquidées garde une réversion « révisable jusqu'à ce que ces droits soient
    liquidés » (circulaire Cnav n° 2007-35, § 222) : ``None``.

    b) « Lorsque le conjoint survivant ne peut prétendre à de tels
    avantages », que le modèle présume de qui n'a ni retraite ni activité, au
    décès ou commencée avant ce jour (présomption
    ``survivant_sans_droit_propre``), « à compter du 1er jour du
    mois qui suit l'âge légal de la retraite du demandeur » (exposé
    « Condition de ressources ») : l'âge de L. 161-17-2 de sa génération,
    depuis le 3 juin 2011, soixante ans avant, que la table donne aux
    générations qui l'atteignaient alors (circulaire Cnav n° 2012/25, § 1 et
    annexe 1) ; sa date d'effet, quand il l'a déjà. ``None`` quand la table ne
    connaît pas sa génération."""
    if conjoint.retraite is not None:
        return max(date_effet, _trois_mois_apres(conjoint.retraite))
    if retraites > 0:
        return date_effet
    if conjoint.revenus_d_activite:
        return None
    age = moteur.ages_ouverture.age(_generation(conjoint.naissance))
    if age is None:
        return None
    fige = max(date_effet, mois_suivant(_atteint(conjoint.naissance, age[0])))
    if any(montant > 0 and quand < fige for quand, montant in conjoint.variations_d_activite):
        # Une activité commencée avant : il a travaillé, et la garde révisable
        # jusqu'à ce qu'il liquide ses droits (circulaire Cnav n° 2007-35, § 222).
        return None
    return fige


def _versions_de_la_charge(fiche: dict) -> list[tuple[str | None, str | None, dict]]:
    """Les versions de la majoration forfaitaire pour enfant, dans l'ordre de
    leurs dates : ``(début, fin, paramètres)``, la fin exclue."""
    bornees = [(*version["bornes"].get("liquidation.date_effet", [None, None]),
                version["parametres"]) for version in fiche["versions"]]
    return sorted(bornees, key=lambda element: element[0] or "")


def _reunir(periodes: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Des périodes ``[début, fin)``, réunies quand elles se chevauchent ou se
    touchent, dans l'ordre."""
    reunies: list[tuple[str, str]] = []
    for debut, fin in sorted(periodes):
        if reunies and debut <= reunies[-1][1]:
            reunies[-1] = (reunies[-1][0], max(reunies[-1][1], fin))
        else:
            reunies.append((debut, fin))
    return reunies


def _jours_a_charge(fiche: dict, naissance: str, depuis: str,
                    prolongations: list[tuple[str, str | None]]) -> list[tuple[str, str]]:
    """Les jours, depuis ``depuis``, où l'enfant né le ``naissance`` est à la
    charge du survivant, en périodes ``[début, fin)`` : sous l'âge de la
    version en vigueur chaque jour — seize ans, puis la majorité depuis le 1er
    janvier 2016 (R. 353-9, R. 313-12, R. 161-4) —, l'enfant « n'est plus à
    charge le jour de son » anniversaire (circulaire Cnav n° 76/88, fiche
    n° 4) ; pendant ses ``prolongations``, ses études, son apprentissage, son
    infirmité (:func:`~retraite_notionnelle.chronologie.prolongations_de_la_charge`),
    sous l'âge où la version les arrête, vingt ans. Rien sous une version qui
    ne dit pas d'âge, avant que la majoration n'existe. L'enfant de seize ans
    à la fin de 2015 redevient à charge le 1er janvier 2016, jusqu'à sa
    majorité."""
    periodes = []
    for debut, fin, parametres in _versions_de_la_charge(fiche):
        ans = parametres.get("enfant_moins_de_ans")
        if ans is None:
            continue
        de = max(debut or depuis, depuis, naissance)
        if fin is not None and de >= fin:
            continue
        limites = [(de, chrono._plus_ans(naissance, int(ans)))]
        prolonge = parametres.get("enfant_prolonge_moins_de_ans")
        if prolonge is not None:
            vingt_ans = chrono._plus_ans(naissance, int(prolonge))
            limites += [(max(de, depuis_le), vingt_ans if jusqu_au is None
                         else min(vingt_ans, jusqu_au))
                        for depuis_le, jusqu_au in prolongations]
        for de_, jusqu_a in limites:
            if fin is not None:
                jusqu_a = min(jusqu_a, fin)
            if de_ < jusqu_a:
                periodes.append((de_, jusqu_a))
    return _reunir(periodes)


def _parts_de_l_enfant(jours: list[tuple[str, str]], date_effet: str,
                       creation: str | None) -> list[tuple[str, str]]:
    """Les périodes ``[début, fin)`` où la part d'un enfant est servie : dès
    la date d'effet s'il est alors à charge, dès le 1er janvier 1988 quand la
    majoration naît après elle (« attribuée au plus tôt le 1er janvier 1988 »,
    circulaire Cnav n° 76/88, § 3), et sinon « à compter du premier jour du
    mois suivant la date à laquelle ces conditions sont satisfaites »
    (R. 353-10) — l'enfant né après la date d'effet, l'enfant qui redevient à
    charge (§ 6) ; jusqu'au « premier jour du mois suivant celui au cours
    duquel l'assuré cesse d'y avoir droit »."""
    parts = []
    for de, jusqu_a in jours:
        debut = de if de in (date_effet, creation) else mois_suivant(de)
        fin = mois_suivant(jusqu_a)
        if debut < fin:
            parts.append((debut, fin))
    return parts


def _majoration_forfaitaire_enfants(moteur: ScenarioActuel, carriere: Carriere,
                                    conjoint: Conjoint, retraites_personnelles: float,
                                    date_effet: str, annee: int
                                    ) -> tuple[float, Fiabilite,
                                               tuple[tuple[str, str], ...]] | None:
    """La majoration forfaitaire ENTIÈRE pour enfant à charge (L. 353-5) : le
    montant annuel PAR ENFANT, aux euros de ``annee``, sa fiabilité, et les
    périodes ``[début, fin)`` où la part de chacun des enfants nés que le
    modèle tient pour à la charge du survivant est servie
    (:func:`_parts_de_l_enfant`), dans l'ordre ; ``None`` quand elle n'est
    jamais due.

    Elle s'attribue le jour où la première part commence : la date d'effet de
    la réversion, ou plus tard (R. 353-10). Ce jour-là, le survivant ne doit
    pas avoir de retraite personnelle d'un régime de base (ses
    ``retraites_personnelles``, ses ressources hors de ses revenus
    d'activité, quand elles sont servies), ni l'âge que R. 353-9 fixe à la
    demande — soixante-cinq ans, puis l'âge du taux plein depuis le 3 juin
    2011 —, ni vivre en couple avant juillet 2004 : l'union défaite avant ce
    jour ne compte plus (lettre de la Cnav du 18 avril 2007). Une part qui
    revient ensuite ne revoit pas l'âge : « La condition d'âge est exigée
    uniquement au moment de l'attribution » (exposé de la Cnav).

    La majoration cesse avec la charge de chaque enfant, et toute entière le
    premier jour du mois qui suit celui où le survivant « perçoit [...] une
    retraite personnelle » (``conjoint.retraite``, quand elle suit
    l'attribution), ou, avant juillet 2004, celui où il « se remarie » ou
    « vit maritalement » (circulaire Cnav n° 76/88, fiche n° 9) ; jamais quand
    il atteint l'âge de R. 353-9, que la fiche n° 9 excepte. Née le 1er janvier
    1988 (R. 353-11), son montant de cette année-là se ramène aux euros d'une
    année des montants antérieure par les coefficients des pensions."""
    table = moteur.reversions
    fiche = table.fiche(MAJORATION_FORFAITAIRE)
    if fiche is None:
        return None
    deces = carriere.deces or date_effet
    creation = min((debut for debut, _, parametres in _versions_de_la_charge(fiche)
                    if parametres.get("servie") and debut is not None), default=None)
    parts = [part for enfant, naissance in carriere.naissances_des_enfants
             for part in _parts_de_l_enfant(_jours_a_charge(
                 fiche, naissance, date_effet,
                 chrono.prolongations_de_la_charge(carriere.chronologie, enfant)),
                 date_effet, creation)]
    if not parts:
        return None
    attribution = min(debut for debut, _ in parts)
    if _retraites_au(conjoint, retraites_personnelles, attribution) > 0:
        return None
    version = table.version(fiche, attribution, deces)
    parametres = version["parametres"] if version else {}
    if not parametres.get("servie"):
        return None
    if parametres.get("age_maximum") is not None:
        if chrono.annees_revolues(conjoint.naissance, attribution) >= int(
                parametres["age_maximum"]):
            return None
    if parametres.get("age_du_taux_plein"):
        age = moteur.ages_annulation_decote.age(_generation(conjoint.naissance))
        if age is None or _atteint(conjoint.naissance, age[0]) <= attribution:
            return None
    if (parametres.get("refusee_en_couple") and conjoint.nouvelle_union is not None
            and (conjoint.nouvelle_union_depuis or date_effet) <= attribution
            and not _venu(conjoint.nouvelle_union_fin, attribution, True)):
        return None
    par_enfant = table.majoration_enfant(annee)
    if par_enfant is None:
        premiere = table.majoration_enfant(int(attribution[:4]))
        if premiere is None:
            return None
        coefficient, fiabilite_coefficient = moteur.revalorisations_pensions.generale(
            date(annee, 12, 31), date(int(attribution[:4]), 12, 31), False, None)
        par_enfant = (premiere[0] / coefficient, min(premiere[1], fiabilite_coefficient))
    # Ce qui l'arrête toute entière : sa propre retraite, puis, avant juillet
    # 2004, l'union où il entre après l'attribution.
    arrets = []
    if conjoint.retraite is not None and conjoint.retraite > attribution:
        arrets.append(mois_suivant(conjoint.retraite))
    union = conjoint.nouvelle_union_depuis
    if conjoint.nouvelle_union is not None and union is not None and union > attribution:
        alors = table.version(fiche, union, deces)
        if alors is not None and alors["parametres"].get("refusee_en_couple"):
            arrets.append(mois_suivant(union))
    arret = min(arrets, default=None)
    servies = sorted((debut, fin if arret is None else min(fin, arret))
                     for debut, fin in parts if arret is None or debut < arret)
    return (par_enfant[0], min(par_enfant[1], Fiabilite.depuis_texte(parametres["fiabilite"])),
            tuple(servies))


def _dernieres_affiliations(moteur: ScenarioActuel, carriere: Carriere,
                            jusqu_a: int) -> dict[str, int]:
    """La dernière année cotisée de l'assuré dans chaque régime, jusqu'à
    l'année ``jusqu_a`` : celle de sa dernière affiliation, que lit le choix
    du régime qui sert la majoration pour enfant
    (:func:`_regime_de_la_majoration`)."""
    plafond = moteur.macro.plafond_securite_sociale
    dernieres: dict[str, int] = {}
    for ligne in carriere.lignes:
        if not ligne.cotise or ligne.annee > jusqu_a:
            continue
        for code in regimes_de(moteur, ligne, ligne.annee, carriere.date_entree(ligne.affiliation),
                               revenu=ligne.revenu, plafond=plafond(ligne.annee)):
            dernieres[code] = max(dernieres.get(code, 0), ligne.annee)
    return dernieres


def _regime_de_la_majoration(moteur: ScenarioActuel, carriere: Carriere,
                             candidats: list[str], jusqu_a: int,
                             durees: dict[str, int] | None,
                             reduites: dict[str, tuple[float, dict]]) -> str | None:
    """Le régime qui sert la majoration pour enfant, parmi les ``candidats``,
    les régimes alignés qui servent une réversion : « par priorité, [...] le
    régime auquel l'assuré a été affilié en dernier lieu si ce régime sert la
    majoration » ; quand il relevait de plusieurs à la fois, « le régime qui
    verse la pension de réversion rémunérant la plus longue durée
    d'assurance » (D. 173-21-1 jusqu'au 30 juin 2017, D. 173-21-7 jusqu'en
    2025, R. 173-17-3 depuis) ; « en cas d'égalité de durée d'assurance », la
    réversion « dont le montant est le plus élevé » (circulaire Cnav n° 76/88,
    fiche n° 7) ; le régime général enfin. La dernière affiliation se lit à
    l'année (:func:`_dernieres_affiliations`). La liquidation unique ne laisse
    qu'une réversion des régimes qu'elle réunit, celle du régime qui la
    liquide, que la règle désigne aussi (« le régime compétent pour la
    liquidation unique sert la majoration », exposé de la Cnav)."""
    if len(candidats) < 2:
        return candidats[0] if candidats else None
    dernieres = _dernieres_affiliations(moteur, carriere, jusqu_a)
    return max(candidats, key=lambda regime: (
        dernieres.get(regime, 0), (durees or {}).get(regime, 0), reduites[regime][0],
        regime == "regime_general"))


def _majorations_ulterieures(parametres: dict, date_effet: str, calcule: float,
                             minimum: float, maximum: float,
                             personnelles: tuple[tuple[str, float], ...] = (),
                             autres: float = 0.0) -> tuple[tuple[str, float], ...]:
    """Les majorations forfaitaires qui relèvent la réversion attribuée avant
    leur date (``majorations_forfaitaires``) : 4 % au 1er décembre 1982, puis
    3,846 % au 1er janvier 1995, qui la portent du taux de 50 % à celui de
    52 %, puis de 54 %. Elles s'appliquent au « montant calculé » de la
    réversion, avant le minimum, « après application éventuelle des
    majorations forfaitaires précédentes » (exposé de la Cnav, « Montant -
    retraite de réversion ») — celles aussi de la pension du défunt, que la
    réversion suit (``personnelles``, ``(jour, taux)``, fiche
    ``majorations_forfaitaires_1972_1982``), et qui passent, le même jour,
    avant la sienne. Chaque jour, ce qu'elles ajoutent ensemble à la
    réversion portée au minimum et ramenée au maximum, ``(jour, montant)``.
    ``autres`` est le montant calculé des réversions que le minimum compte
    avec elle (D. 634-14), que les majorations de la réversion relèvent aussi,
    et que la réversion portée au minimum laisse sous lui."""
    def servie(facteur: float, propre: float) -> float:
        montant = max(minimum - autres * propre, calcule * facteur)
        return min(montant, maximum) if maximum > 0 else montant
    datees = sorted([(jour, 0, taux) for jour, taux in personnelles if jour > date_effet]
                    + [(str(majoration["date"]), 1, float(majoration["taux"]))
                       for majoration in parametres.get("majorations_forfaitaires") or ()
                       if str(majoration["date"]) > date_effet])
    ecrites, facteur, propre = [], 1.0, 1.0
    for jour in dict.fromkeys(jour for jour, _, _ in datees):
        nouveau, nouveau_propre = facteur, propre
        for _, sorte, taux in (datee for datee in datees if datee[0] == jour):
            nouveau *= 1 + taux
            if sorte == 1:
                nouveau_propre *= 1 + taux
        ecrites.append((jour, servie(nouveau, nouveau_propre) - servie(facteur, propre)))
        facteur, propre = nouveau, nouveau_propre
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


def _groupes_du_minimum(moteur: ScenarioActuel, parametres: dict, lura: bool,
                        annee: int) -> dict[str, str]:
    """Le régime de chacun des régimes du minimum (:data:`REGIMES_DU_MINIMUM`)
    pour la liquidation de l'année ``annee`` : sa tête de succession, la
    CANCAVA et l'ORGANIC étant le RSI qui leur succède en 2006, le RSI le
    régime général en 2020 (:func:`~.coordonner.tete_de_succession`), dont la
    pension sert leurs années et dont chacun des régimes « retient [le
    minimum] au prorata de la durée d'assurance accomplie en son sein »
    (D. 353-1) ; sous la liquidation unique (``lura``), les régimes alignés,
    dont « la pension d'un des régimes qu'elle réunit est la leur » (exposé de
    la Cnav, « Retraite de l'assuré décédé »). Les droits d'avant 1973 de
    chaque caisse (``droits_d_avant_1973``) sont du régime qui leur succède
    quand la version compte leur réversion avec la sienne pour le minimum
    (``minimum_avec_les_droits_d_avant_1973`` : D. 634-14 ; décret n° 73-937,
    article 7-2) ; sinon, ils n'ont pas de minimum."""
    groupes: dict[str, str] = {}
    for code in REGIMES_DU_MINIMUM:
        if lura and code in REGIMES_ALIGNES:
            groupes[code] = REGIMES_ALIGNES_TETE
        else:
            groupes[code] = (tete_de_succession(moteur, code, annee)
                             if code in moteur.catalogue else code)
    if parametres.get("minimum_avec_les_droits_d_avant_1973"):
        for code, successeur in (parametres.get("droits_d_avant_1973") or {}).items():
            groupes[code] = groupes.get(successeur, successeur)
    return groupes


def _part_du_minimum(parametres: dict, regime: str, durees: dict[str, int] | None,
                     groupes: dict[str, str]) -> float:
    """La part du minimum de D. 353-1 que sert la réversion de ``regime`` :
    entière avant le 1er décembre 1982 ; ensuite, autant de soixantièmes que le
    défunt a de trimestres d'assurance dans le régime, soixante au plus ;
    depuis le 1er juillet 2004, quand ses durées dans les régimes alignés
    dépassent ensemble soixante trimestres et qu'il en a dans plusieurs, sa
    durée dans le régime rapportée à leur total. Le régime est celui de
    ``groupes`` (:func:`_groupes_du_minimum`) : les durées de ses membres s'y
    additionnent, et ils ne comptent que pour un. Sans durées dites, la part
    entière."""
    if not parametres.get("minimum_proratise") or durees is None:
        return 1.0
    seuil = float(parametres["minimum_trimestres"])
    durees_des_groupes: dict[str, int] = {}
    for code, groupe in groupes.items():
        durees_des_groupes[groupe] = durees_des_groupes.get(groupe, 0) + durees.get(code, 0)
    propre = float(durees_des_groupes[groupes[regime]] if regime in groupes
                   else durees.get(regime, 0))
    alignes = [duree for duree in durees_des_groupes.values() if duree > 0]
    total = float(somme_ordonnee(alignes))
    if parametres.get("minimum_tous_regimes") and len(alignes) > 1 and total > seuil:
        return propre / total
    return min(1.0, propre / seuil)


def _minimum_de_pension(moteur: ScenarioActuel, parametres: dict, base: float,
                        annee: int, portee: bool = False
                        ) -> tuple[float, Fiabilite] | None:
    """Ce que garde au moins la réversion entière de la SNCF, aux euros de
    ``annee``, et sa fiabilité : la part ``part_du_minimum_de_pension`` du
    minimum de pension de l'article 15, IV, quand la pension de l'agent,
    ``base``, a été « portée au montant du minimum » à sa liquidation —
    ``portee`` —, ou lui est « supérieure » (décret n° 2008-639, article 18) ;
    ``None`` sans lui. Le minimum suit les pensions de son ancre à l'année des
    montants (article 30), en 2020 au taux des pensions de 2 000 € par mois au
    plus, qu'il ne dépasse pas ; la pension portée au minimum avant octobre
    2014, revalorisée comme les pensions, reste 0,3 % sous celui que le décret
    de 2015 écrit, et n'en est pas moins portée au minimum."""
    part = parametres.get("part_du_minimum_de_pension")
    ancre = moteur.reversions.minimum_pension_sncf(annee)
    if part is None or ancre is None:
        return None
    depuis, montant, fiabilite = ancre
    coefficient, fiabilite_du_coefficient = moteur.revalorisations_pensions.generale(
        date(depuis, 12, 31), date(annee, 12, 31), False, montant / 12)
    if not portee and base < montant * coefficient:
        return None
    return float(part) * montant * coefficient, min(fiabilite, fiabilite_du_coefficient)


def _enfants_de_moins_de(carriere: Carriere, deces: str, ans: int) -> int:
    """Les enfants nés au décès qui n'ont pas encore ``ans`` ans : ceux que la
    chronologie porte, déclarés ou présumés, et que le modèle tient pour à la
    charge du survivant."""
    return somme_ordonnee(1 for _, naissance in carriere.naissances_des_enfants
               if naissance <= deces < chrono._plus_ans(naissance, ans))


def _venu(jour: str | None, date_: str, le_jour_meme: bool) -> bool:
    """Le changement du jour ``jour`` — le ménage formé ou défait, l'activité
    cessée, des ressources qui varient — compte-t-il le jour ``date_`` ? Venu
    avant, oui ; ce jour même, seulement quand ``le_jour_meme``."""
    return jour is not None and (jour < date_ or (le_jour_meme and jour == date_))


def _activite_au(conjoint: Conjoint, date_: str, le_jour_meme: bool) -> float:
    """Ce que son activité rapporte par an au survivant le jour ``date_`` : les
    revenus qu'il déclare au décès, rien une fois qu'elle a cessé, ou ceux de
    la dernière de ses variations venue (:func:`_venu`) — un salaire qui
    change, une activité reprise."""
    activite = float(conjoint.revenus_d_activite or 0.0)
    changements = list(conjoint.variations_d_activite)
    if conjoint.fin_d_activite is not None:
        changements.append((conjoint.fin_d_activite, 0.0))
    for quand, montant in sorted(changements):
        if _venu(quand, date_, le_jour_meme):
            activite = montant
    return activite


def _apport_au(conjoint: Conjoint, date_: str, le_jour_meme: bool) -> float:
    """Ce que son nouveau conjoint apporte par an au ménage du survivant le
    jour ``date_`` : ce qu'il déclare à leur union, ou la dernière de ses
    variations venue (:func:`_venu`)."""
    apport = float(conjoint.ressources_du_nouveau_conjoint or 0.0)
    for quand, montant in conjoint.variations_du_nouveau_conjoint:
        if _venu(quand, date_, le_jour_meme):
            apport = montant
    return apport


def _ressources_du_plafond(parametres: dict, conjoint: Conjoint, ressources: float,
                           date_effet: str, le_jour_meme: bool = True) -> tuple[float, float]:
    """Les ressources du survivant que retient le plafond de la version, et le
    facteur qui multiplie ce plafond (L. 353-1, D. 353-1-1, R. 353-1).

    Ses revenus d'activité sont ceux de ce jour (:func:`_activite_au`) : ceux
    qu'il déclare au décès, rien une fois son activité cessée, ceux qu'une
    variation leur substitue — un salaire qui change, une activité reprise. Ils
    sont abattus de 30 % quand il a cinquante-cinq ans à la date d'effet,
    « quel que soit l'âge atteint au moment où ces revenus ont été perçus »
    (circulaire Cnav n° 2006-37, § 7). Quand il vit en couple — marié, pacsé
    ou en concubinage —, les ressources de son nouveau conjoint s'y ajoutent,
    entières, celles de ce jour (:func:`_apport_au`), sous le plafond du ménage
    (circulaire Cnav n° 2005-17, § 141 et § 145) : 1,6 fois celui d'une
    personne seule au régime général, le même à la complémentaire des
    indépendants. Le ménage défait, « le salaire du conjoint doit être ignoré,
    et le décompte doit s'effectuer en retenant le plafond de ressources
    personne seule » (§ 146), comme pour le survivant « séparé de fait avec
    résidence distincte » (R. 815-27 ; circulaire Cnav n° 2009/11, § 31). La
    version qui ne dit pas ce facteur, avant juillet 2004, ne compte que ses
    ressources personnelles. Chaque changement compte venu avant la date
    d'effet, ou ce jour même quand ``le_jour_meme`` ; à une révision, celui du
    jour même révise au mois qui suit (:func:`_revisions`)."""
    declares = float(conjoint.revenus_d_activite or 0.0)
    activite = _activite_au(conjoint, date_effet, le_jour_meme)
    if activite != declares:
        # Ses revenus d'activité de ce jour remplacent, dans ses ressources,
        # ceux qu'il déclare au décès.
        ressources = ressources - min(ressources, declares) + activite
    taux = parametres.get("abattement_activite")
    if (taux and activite
            and chrono.annees_revolues(conjoint.naissance, date_effet)
            >= int(parametres["abattement_activite_age"])):
        ressources -= float(taux) * min(ressources, activite)
    facteur = parametres.get("facteur_menage")
    union = conjoint.nouvelle_union_depuis
    formee = union is None or _venu(union, date_effet, le_jour_meme)
    if (facteur is None or conjoint.nouvelle_union is None or not formee
            or _venu(conjoint.nouvelle_union_fin, date_effet, le_jour_meme)):
        return ressources, 1.0
    return ressources + _apport_au(conjoint, date_effet, le_jour_meme), float(facteur)


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
    age = moteur.ages_annulation_decote.age(_generation(conjoint.naissance))
    if not eligibles or plafond is None or age is None:
        return
    debut = _au_taux_plein(conjoint.naissance, age[0])
    # Ses réversions, revues par la limite de cumul quand sa retraite les
    # suit, ou à leur dernière révision sous le plafond de ressources.
    retraites = retraites_personnelles + somme_ordonnee(
        l.montant - l.reduction_du_cumul - l.reduction_de_la_revision
        for l in lignes.values())
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
              avant_le_depart: bool = False,
              majorations_des_pensions: dict[str, tuple[tuple[str, float], ...]] | None = None
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
    et les régimes alignés reversent la pension sans elle ; ou celle que le
    minimum de pension de la SNCF y ajoute, qui la dit portée au minimum
    (:data:`MINIMA_REVERSES`). ``maxima`` donne,
    régime par régime, ce que le maximum des pensions a retiré de la pension,
    ce que la surcote y ajoute, aux mêmes euros, et le coefficient de
    l'ajournement d'avant 1983 ou du taux acquis au 31 mars 1983, qui
    multiplie son maximum : le régime général reverse la pension d'avant son
    maximum, sous le maximum de la réversion. ``avant_le_depart`` dit que le
    défunt est mort avant son départ, et que ``pensions`` sont celles qu'il eût
    obtenues à son décès. ``majorations_des_pensions`` donne, régime par
    régime, les majorations forfaitaires de 1972 à 1982 que sa pension reçoit
    après l'année des montants, ``(jour, taux)`` : la réversion du régime
    général les suit, comprises dans son montant calculé jusqu'à sa date
    d'effet, à leur date ensuite.
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
        if fiche["id"] in MOITIE_MAJORATION_COMPRISE:
            # La moitié de la pension, « majoration pour enfant comprise » aux
            # IEG (annexe 3 au statut national, article 22), « majorée dans les
            # conditions fixées à l'article 16 » à la SNCF (décret n° 2008-639,
            # article 18).
            servie = (_mariage_sncf(parametres, conjoint, deces, depart,
                                    [jour for _, jour in carriere.naissances_des_enfants])
                      if fiche["id"] == "reversion_sncf"
                      else _mariage_ieg(parametres, conjoint, deces, depart, enfants))
            # La réversion entière, portée au minimum de la SNCF, que le
            # survivant partage comme elle (article 20) ; sa majoration est
            # celle de l'agent au même taux de son montant (article 16).
            entiere = taux * base
            minimum, motif, releve = 0.0, "servie", 1.0
            garanti = (_minimum_de_pension(moteur, parametres, base, annee,
                                           bool((minima or {}).get(regime)))
                       if servie else None)
            if garanti is not None:
                minimum = garanti[0]
                if minimum > entiere:
                    entiere, motif, releve = minimum, "minimum", minimum / entiere
                    fiabilite = min(fiabilite, garanti[1])
            majoration = (float(parametres.get("majoration_reversible") or 0.0)
                          * (majorations or {}).get(regime, 0.0) * part
                          * releve) if servie else 0.0
            montant = entiere * part + majoration if servie else 0.0
            lignes[regime] = _sans_jouissance_au_deces(_jusqu_au_remariage(replace(
                ligne(regime, base, montant, motif if servie else "mariage", fiche,
                      version, taux, lendemain, fiabilite),
                majoration=majoration, part=part, minimum=minimum * part),
                parametres, conjoint), parametres, conjoint, deces)
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
    # L'année de la liquidation dont viennent les pensions, qui dit quelle
    # caisse succède aux autres : celle du décès pour l'assuré mort avant son
    # départ, que l'échéancier liquide alors.
    annee_de_liquidation = int(deces[:4]) if avant_le_depart else carriere.annee_liquidation
    #: Les droits d'avant 1973 que nomment les versions : leur réversion ne
    #: porte pas les majorations pour enfants (décret n° 73-937, article 9).
    d_avant_1973: set[str] = set()

    def principale_de(regime_: str, base_: float, date_effet_: str) -> float:
        # La « pension principale » (L. 353-1), que la caisse prend « avant
        # comparaison au minimum et au maximum » : sans la majoration qui la
        # portait au minimum contributif (L. 351-10), avec ce que le maximum
        # des pensions en avait retiré (exposé de la Cnav, « Retraite de
        # l'assuré décédé » ; circulaire n° 105/90, § 22). Les majorations
        # forfaitaires de sa pension venues entre l'année des montants et la
        # date d'effet relèvent la pension que la réversion lit.
        principale_ = (base_ - min(base_, (minima or {}).get(regime_, 0.0))
                       + (maxima or {}).get(regime_, (0.0, 0.0, 1.0))[0])
        for jour, taux_majoration in (majorations_des_pensions or {}).get(regime_, ()):
            if jour <= date_effet_:
                principale_ *= 1 + taux_majoration
        return principale_

    #: La réversion de chaque régime aligné, réduite, avant ses majorations :
    #: ce que la majoration de 11,1 % multiplie.
    reduites: dict[str, tuple[float, dict]] = {}
    #: Leur réversion entière, portée au minimum et ramenée au maximum, avant
    #: les ressources et le cumul, et leur date d'effet : la majoration pour
    #: enfant à charge se réduit dans la proportion de la réduite à l'entière.
    entieres: dict[str, float] = {}
    #: Leur réversion réduite, revue par la limite de cumul quand la retraite
    #: du survivant la suit : celle que la majoration de 11,1 %, qui commence
    #: plus tard, multiplie.
    revues: dict[str, tuple[float, dict]] = {}
    # Les réversions de base du survivant, qui divisent ses retraites et la
    # limite forfaitaire du cumul d'avant 2004 : celles des régimes alignés,
    # et celles des autres régimes de base servies.
    reversions_de_base = (
        somme_ordonnee(1 for regime, _, _ in pensions
                       if (table.fiche_du_regime(regime) or {}).get("id") == "reversion")
        + somme_ordonnee(1 for regime, ligne_ in lignes.items()
                         if ligne_.montant > 0 and ligne_.fiche in AUTRES_BASES))
    # Les réversions des autres régimes de base que retient une révision, et
    # celles des régimes alignés déjà chiffrés, avec ce que leurs révisions en
    # font : ce qu'elles servent chaque jour (:func:`_servie_au`).
    bases_des_autres = autres_bases
    alignees: list[tuple[float, tuple[tuple[str, float], ...]]] = []

    def bases_au(jour: str) -> float:
        return somme_ordonnee((_servie_au(montant_, etapes_, jour)
                               for montant_, etapes_ in alignees), bases_des_autres)

    for regime, base, fiabilite in pensions:
        fiche = table.fiche_du_regime(regime)
        if fiche is None or fiche["id"] != "reversion":
            continue
        date_effet = _premiere_date_d_effet(table, fiche, conjoint, lendemain, deces)
        version = table.version(fiche, date_effet, deces)
        parametres = version["parametres"]
        taux = float(parametres["taux"])
        # Ses retraites personnelles, servies dès la date d'effet, ou seulement
        # quand sa propre retraite, qu'il date après elle, commence : ses
        # ressources n'en ont pas d'autres à la date d'effet.
        retraites = _retraites_au(conjoint, retraites_personnelles, date_effet)
        contributif = min(base, (minima or {}).get(regime, 0.0))
        ecretement, surcote, coefficient = (maxima or {}).get(regime, (0.0, 0.0, 1.0))
        personnelles = (majorations_des_pensions or {}).get(regime, ())
        principale = principale_de(regime, base, date_effet)
        # Partagée avec les précédents conjoints au prorata des mariages, la
        # réversion l'est avec son minimum et son maximum (circulaire Cnav
        # n° 105/90, § 3).
        part = _part_du_survivant(carriere, conjoint, deces,
                                  _admis_au_regime_general(parametres, deces, enfants))
        montant = taux * principale * part
        motif = "servie"
        # Le minimum de D. 353-1, avant les ressources : la caisse porte la
        # réversion au minimum, puis la réduit du dépassement du plafond. Les
        # réversions d'un même régime (:func:`_groupes_du_minimum`) n'en ont
        # qu'un, que la première de leurs lignes qui n'est pas d'avant 1973 sert
        # en complément des autres : « il est tenu compte, le cas échéant, du
        # montant cumulé » (D. 634-14 ; décret n° 73-937, article 7-2).
        avant_1973 = parametres.get("droits_d_avant_1973") or {}
        d_avant_1973.update(avant_1973)
        groupes = _groupes_du_minimum(moteur, parametres, lura, annee_de_liquidation)
        membres = [(autre, base_autre) for autre, base_autre, _ in pensions
                   if regime in groupes and groupes.get(autre) == groupes[regime]
                   and (table.fiche_du_regime(autre) or {}).get("id") == "reversion"]
        tete = next((autre for autre, _ in membres if autre not in avant_1973),
                    membres[0][0] if membres else regime)
        autres = 0.0
        minimum = 0.0
        if (minimum_de_l_annee is not None and parametres.get("minimum_trimestres")
                and tete == regime and (regime not in avant_1973 or regime in groupes)):
            autres = somme_ordonnee(taux * principale_de(autre, base_autre, date_effet) * part
                                    for autre, base_autre in membres if autre != regime)
            minimum = minimum_de_l_annee[0] * _part_du_minimum(parametres, regime, durees,
                                                               groupes) * part
            if minimum - autres > montant:
                montant, motif = minimum - autres, "minimum"
                fiabilite = min(fiabilite, minimum_de_l_annee[1])
        # Le plafond, d'une personne seule ou du ménage, et ce qu'il retient à
        # côté de la réversion : les ressources du survivant, ou du ménage, et
        # les réversions des autres régimes de base — avant juillet 2004, ses
        # ressources personnelles « sans tenir compte des avantages de
        # réversion » (R. 353-1, rédactions de 1985 et de 1990).
        retenues, facteur = _ressources_du_plafond(
            parametres, conjoint, ressources - (retraites_personnelles - retraites), date_effet)
        plafond_annuel = (facteur * float(parametres["plafond_smic_heures"])
                          * moteur.macro.smic_horaire(annee))
        reversions = autres_bases if parametres["ressources"] == "ecretement" else 0.0
        if parametres.get("cumul") is not None:
            # Avant juillet 2004, ses retraites personnelles « n'étaient pas
            # retenues dans les ressources » : elles se cumulaient avec la
            # réversion dans une limite (exposé de la Cnav, « Condition de
            # ressources »).
            retenues -= min(retenues, retraites)
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
        calcule = taux * principale * part
        entieres[regime] = (min(max(calcule, minimum - autres), maximum) if maximum > 0
                            else max(calcule, minimum - autres))
        # Le cumul d'avant juillet 2004 avec ses retraites personnelles, après
        # le maximum : la limite « ne pouvait pas être inférieure à la
        # retraite de réversion portée au minimum ou ramenée au maximum ».
        forfaitaire = table.limite_cumul(annee)
        cumulee, limite_cumul = _cumuler(
            parametres, montant, retraites, principale,
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
        # Pas sur les points d'avant 1973, dont l'article 9 du décret
        # n° 73-937 ne cite pas la majoration.
        def des_trois_enfants(reversion_: float) -> float:
            if reversion_ <= 0 or enfants < 3 or regime in avant_1973:
                return 0.0
            return max(float(parametres["majoration_enfants_taux"]) * reversion_,
                       float(parametres.get("majoration_enfants_minimum") or 0.0) * minimum)

        trois_enfants = des_trois_enfants(montant)
        ulterieures = (_majorations_ulterieures(parametres, date_effet, calcule, minimum,
                                                maximum, personnelles, autres)
                       if montant > 0 else ())
        # La limite revue quand sa propre retraite suit la date d'effet : ce
        # qu'elle retire alors, la majoration de 10 % suivant la réversion.
        cumul_effet, reduction_du_cumul, revue_a = None, 0.0, montant
        etapes: list[tuple[str, float]] = []
        revue = _cumul_a_la_retraite(moteur, fiche, conjoint, deces, annee, date_effet,
                                     montant, ulterieures, retraites_personnelles,
                                     principale, reversions_de_base, personnelles)
        if revue is not None:
            cumul_effet, servie_alors, revue_a, limite_cumul, fiabilite_revue = revue
            reduction_du_cumul = (servie_alors + des_trois_enfants(servie_alors)
                                  - revue_a - des_trois_enfants(revue_a))
            fiabilite = min(fiabilite, fiabilite_revue)
            etapes.append((cumul_effet, revue_a))
        # Ou révisée sous le plafond de ressources, jusqu'à sa dernière
        # révision : de même, à chaque révision.
        derniere = _derniere_revision(moteur, conjoint, date_effet, retraites_personnelles)
        revisions = []
        ressources_revisees = []
        for jour, servie_alors, revue_a, fiabilite_revisee, retenues_alors in _revisions(
                moteur, fiche, parametres, conjoint, deces, annee, date_effet, montant,
                entieres[regime], ulterieures, ressources, retraites_personnelles, bases_au,
                derniere, regime):
            revisions.append((jour, servie_alors + des_trois_enfants(servie_alors)
                              - revue_a - des_trois_enfants(revue_a)))
            ressources_revisees.append((jour, retenues_alors))
            fiabilite = min(fiabilite, fiabilite_revisee)
            etapes.append((jour, revue_a))
        revision_effet, reduction_de_la_revision = revisions[-1] if revisions else (None, 0.0)
        alignees.append((montant, tuple(etapes)))
        reduites[regime] = (montant, parametres)
        revues[regime] = (revue_a, parametres)
        lignes[regime] = replace(
            ligne(regime, base, montant + trois_enfants, motif, fiche, version, taux,
                  date_effet, fiabilite),
            minimum=minimum, majoration_trois_enfants=trois_enfants,
            minimum_contributif=contributif, ecretement_du_maximum=ecretement,
            maximum=maximum, plafond=plafond_annuel, ressources_retenues=retenues,
            part=part, limite_cumul=limite_cumul, majorations_forfaitaires=ulterieures,
            cumul_effet=cumul_effet, reduction_du_cumul=reduction_du_cumul,
            revision_effet=revision_effet, reduction_de_la_revision=reduction_de_la_revision,
            revisions=tuple(revisions), ressources_des_revisions=tuple(ressources_revisees),
            derniere_revision=(derniere if parametres["ressources"] == "ecretement"
                               or revisions else None))

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
        if version["parametres"].get("rien_apres_un_capital") and regime in en_capital:
            # Le versement forfaitaire unique de l'assuré « fait obstacle à
            # l'attribution d'une pension de réversion » (règlement, article
            # 41, II) : la ligne ne s'écrit pas.
            continue
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
    # régime, celui de la dernière affiliation parmi ceux qui servent une
    # réversion (:func:`_regime_de_la_majoration`) ; réduite dans la
    # proportion de la réversion réduite à l'entière (D. 353-2 ; exposé de la
    # Cnav). Jamais celle des points d'avant 1973, dont l'article 9 du décret
    # n° 73-937 ne cite pas L. 353-5.
    servant = _regime_de_la_majoration(
        moteur, carriere,
        [r for r, (montant, _) in reduites.items() if montant > 0 and r not in d_avant_1973],
        min(annee_de_liquidation, int(deces[:4])), durees, reduites)
    if servant is not None:
        ligne_du_regime = lignes[servant]
        entiere = _majoration_forfaitaire_enfants(
            moteur, carriere, conjoint, retraites_personnelles,
            ligne_du_regime.date_effet, annee)
        if entiere is not None:
            par_enfant, fiabilite_enfant, parts = entiere
            reduite = reduites[servant][0]
            facteur = (min(1.0, reduite / entieres[servant])
                       if entieres[servant] > 0 else 0.0)

            def servie_au(jour: str) -> float:
                # Chaque enfant compte pendant que sa part est servie.
                servies = len([1 for debut, fin in parts if debut <= jour < fin])
                return servies * par_enfant * facteur

            majoration = servie_au(ligne_du_regime.date_effet)
            etapes = []
            for jour in sorted({jour for part in parts for jour in part
                                if jour > ligne_du_regime.date_effet}):
                montant = servie_au(jour)
                if montant != (etapes[-1][1] if etapes else majoration):
                    etapes.append((jour, montant))
            etapes = tuple(etapes)
            lignes[servant] = replace(
                ligne_du_regime, montant=ligne_du_regime.montant + majoration,
                majoration_forfaitaire_enfants=majoration,
                majoration_forfaitaire_enfants_etapes=etapes,
                fiabilite=min(ligne_du_regime.fiabilite, fiabilite_enfant))

    # Ses retraites personnelles, que la majoration de 11,1 % compte.
    _majorer_les_petites_retraites(
        moteur, lignes, revues, conjoint, retraites_personnelles, annee)

    return Reversion(
        personne=conjoint.personne, defunt=carriere.personne, deces=deces, annee=annee,
        ressources=ressources, ressources_presumees=presumees,
        regimes=tuple(lignes[regime] for regime, _, _ in pensions if regime in lignes),
        deces_suppose=deces_suppose is not None, avant_le_depart=avant_le_depart)
