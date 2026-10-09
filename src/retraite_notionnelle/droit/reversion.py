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
D. 353-1-1, R. 353-1) — ; puis ramené à son MAXIMUM, le taux du maximum des pensions
« opposable à l'assuré décédé » — l'ajournement d'avant 1983 le majorant —,
au plafond de l'année des montants, que 54 % de la surcote du défunt passent
(circulaires Cnav n° 120/82, § 4, n° 105/90, § 22, et n° 2018-4, § 5) ; puis
majoré de 10 % pour le survivant de trois enfants, sans
descendre sous le dixième de son minimum (R. 353-2), hors du plafond ; enfin,
depuis 2010, majoré de 11,1 % de la réversion réduite quand le survivant a
l'âge du taux plein et que ses retraites, réversions et majorations comprises,
restent sous le plafond de L. 353-6, la majoration étant réduite de ce qui le
dépasse (D. 353-4). Une majoration qui commence après la date d'effet de la
ligne, quand le survivant n'a pas encore l'âge du taux plein, s'écrit à part,
avec sa date, hors du montant.

CE QUI N'EST PAS ENCORE PORTÉ, et que les fiches déclarent : la majoration
forfaitaire pour enfant à charge du régime général, la révision de la
réversion quand le ménage ou ses ressources changent, le plafonnement du veuf
de fonctionnaire d'avant 2004,
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
    "mariage": "condition d'antériorité ou de durée du mariage non remplie",
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
                "ressources_retenues": self.ressources_retenues}


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
        return somme_ordonnee(r.montant for r in self.regimes)

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


def _au_taux_plein(naissance: str, age: float) -> str:
    """Le jour où la majoration de L. 353-6 peut commencer : le premier jour du
    mois qui suit l'âge du taux plein, ou l'anniversaire même du survivant né
    le premier jour d'un mois (R. 353-13 ; exposé de la Cnav, « Majoration de
    la retraite de réversion »). L'âge se compte en mois : soixante-six ans et
    deux mois pour la génération 1953."""
    mois = round(age * 12)
    annee = int(naissance[:4]) + (int(naissance[5:7]) - 1 + mois) // 12
    numero = (int(naissance[5:7]) - 1 + mois) % 12 + 1
    atteint = f"{annee:04d}-{numero:02d}-{naissance[8:10]}"
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
    if facteur is None or conjoint.nouvelle_union is None:
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
              maxima: dict[str, tuple[float, float, float]] | None = None
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
    maximum, sous le maximum de la réversion.
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
        if fiche["id"] in MOITIE_SOUS_CONDITION_DE_MARIAGE:
            servie = _mariage_suffit(parametres, conjoint, deces, depart, enfants)
            montant = taux * base if servie else 0.0
            autres_bases += montant
            lignes[regime] = ligne(regime, base, montant, "servie" if servie else "mariage",
                                   fiche, version, taux, lendemain, fiabilite)
            continue
        if fiche["id"] == "reversion_ieg":
            # La moitié de la pension, « majoration pour enfant comprise »
            # (annexe 3 au statut national des IEG, article 22).
            servie = _mariage_ieg(parametres, conjoint, deces, depart, enfants)
            majoration = (float(parametres.get("majoration_reversible") or 0.0)
                          * (majorations or {}).get(regime, 0.0)) if servie else 0.0
            montant = taux * base + majoration if servie else 0.0
            autres_bases += montant
            lignes[regime] = replace(
                ligne(regime, base, montant, "servie" if servie else "mariage", fiche,
                      version, taux, lendemain, fiabilite),
                majoration=majoration)
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
    minimum_de_l_annee = table.minimum(annee)
    lura = lura_applicable(carriere)
    #: La réversion de chaque régime aligné, réduite, avant ses majorations :
    #: ce que la majoration de 11,1 % multiplie.
    reduites: dict[str, tuple[float, dict]] = {}
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
        # La « pension principale » (L. 353-1), que la caisse prend « avant
        # comparaison au minimum et au maximum » : sans la majoration qui la
        # portait au minimum contributif (L. 351-10), avec ce que le maximum
        # des pensions en avait retiré (exposé de la Cnav, « Retraite de
        # l'assuré décédé » ; circulaire n° 105/90, § 22).
        contributif = min(base, (minima or {}).get(regime, 0.0))
        ecretement, surcote, coefficient = (maxima or {}).get(regime, (0.0, 0.0, 1.0))
        montant = taux * (base - contributif + ecretement)
        motif = "servie"
        # Le minimum de D. 353-1, avant les ressources : la caisse porte la
        # réversion au minimum, puis la réduit du dépassement du plafond.
        minimum = 0.0
        if minimum_de_l_annee is not None and parametres.get("minimum_trimestres"):
            minimum = minimum_de_l_annee[0] * _part_du_minimum(parametres, regime, durees,
                                                               lura)
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
            maximum = taux * (des_pensions[0] * coefficient + surcote)
            if montant > maximum:
                montant, motif = maximum, "maximum"
                fiabilite = min(fiabilite, des_pensions[1])
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
            maximum=maximum, plafond=plafond_annuel, ressources_retenues=retenues)

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
        independantes.append((regime, base, fiabilite, fiche, version))
    if independantes:
        parametres = independantes[0][4]["parametres"]
        retenues, facteur = _ressources_du_plafond(
            parametres, conjoint, ressources,
            _a_l_age(conjoint.naissance, lendemain, float(parametres["age_minimum"])))
        plafond_annuel = (facteur * float(parametres["plafond_pass"])
                          * moteur.macro.plafond_securite_sociale(annee))
        retenues += autres_bases
        brut = somme_ordonnee(float(version["parametres"]["taux"]) * base
                   for _, base, _, _, version in independantes)
        depassement = max(0.0, retenues + brut - plafond_annuel)
        for regime, base, fiabilite, fiche, version in independantes:
            parametres = version["parametres"]
            taux = float(parametres["taux"])
            montant = taux * base
            motif = "servie"
            if depassement > 0:
                montant, motif = max(0.0, montant - depassement * montant / brut), "ecretee"
            date_effet = _a_l_age(conjoint.naissance, lendemain,
                                  float(parametres["age_minimum"]))
            lignes[regime] = replace(
                ligne(regime, base, montant, motif, fiche, version, taux, date_effet,
                      fiabilite),
                plafond=plafond_annuel, ressources_retenues=retenues)

    # Ses retraites personnelles, que la majoration de 11,1 % compte : ses
    # ressources, moins ce que son activité lui rapporte.
    _majorer_les_petites_retraites(
        moteur, lignes, reduites, conjoint,
        ressources - min(ressources, float(conjoint.revenus_d_activite or 0.0)), annee)

    return Reversion(
        personne=conjoint.personne, defunt=carriere.personne, deces=deces, annee=annee,
        ressources=ressources, ressources_presumees=presumees,
        regimes=tuple(lignes[regime] for regime, _, _ in pensions if regime in lignes),
        deces_suppose=deces_suppose is not None)
