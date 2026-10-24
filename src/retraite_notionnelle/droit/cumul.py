"""Le cumul emploi-retraite (docs/architecture.md, § 7.4 ; fiches
``cumul_emploi_retraite_et_retraite_progressive``,
``cumul_emploi_retraite_fonction_publique``,
``cumul_emploi_retraite_complementaire_des_independants``,
``cumul_emploi_retraite_ircantec``, ``cumul_emploi_retraite_rco_agricole`` et
``cumul_emploi_retraite_complementaires_des_liberaux``).

Le retraité qui travaille garde sa pension, entière ou non, selon le droit du
MOIS où il travaille, la date de sa pension et celle de sa première pension de
base. Ce module dit, mois par mois de l'activité exercée après le départ
(:attr:`~retraite_notionnelle.carriere.Carriere.emploi_retraite`), ce que
chaque pension en garde.

Le salarié — régime général, salariés agricoles, régimes spéciaux (L. 161-22) :

* la pension prise avant le 1er avril 1983 se cumule librement ; de 1983 à
  2003, son service suppose « la rupture définitive de tout lien professionnel
  avec l'employeur » : le modèle lit le DERNIER employeur, la reprise chez un
  autre restant libre ;
* pour la pension de 2004, la reprise chez le dernier employeur dans les six
  mois fait perdre la pension du mois de la reprise au sixième mois
  (D. 161-2-15) ; ensuite, les pensions et le revenu ne dépassent pas le
  dernier salaire — la moyenne des trois derniers mois soumis à la CSG
  (D. 161-2-7), au moins le SMIC mensuel (D. 161-2-9) —, ou la pension est
  suspendue pour le mois (D. 161-2-16) ;
* depuis 2009, le plafond est au moins 160 % du SMIC, le dernier salaire est
  revalorisé comme les pensions depuis 2010 (D. 161-2-8), et la pension se
  cumule entièrement à qui a liquidé toutes ses pensions, à l'âge du taux
  plein automatique ou à l'âge légal avec la durée requise ; ni le plafond ni
  le délai de six mois ne le touchent alors ;
* la première pension de 2015 relève du nouvel article : chacune de ses
  pensions de base est RÉDUITE du dépassement (D. 161-2-16, II), et n'est plus
  suspendue, pour les activités exercées depuis le 1er avril 2017, date du
  décret de la réduction ; la première pension d'avant 2015 garde la
  suspension, que sa rédaction de L. 161-22 écrit ;
* la première pension de 2027 a trois régimes selon l'âge : avant l'âge
  légal, la pension est réduite de tout le revenu ; de l'âge légal à l'âge du
  taux plein automatique, de la moitié de ce qui dépasse un seuil qu'aucun
  décret n'a encore fixé — le modèle la sert entière, et le dit ; au-delà,
  elle se cumule entièrement.

L'artisan et le commerçant (L. 634-6) : la pension prise depuis juillet 1984
est suspendue quand il reprend dans l'entreprise qu'il exploitait ; depuis
2004, son revenu ne dépasse pas la moitié du plafond de la sécurité sociale,
rapportée à la durée de l'activité (D. 634-11-2), ou la pension est suspendue,
puis, pour la première pension de 2015 et les activités de 2017, réduite du
dépassement. Le libéral (L. 643-6), de même, sous le plafond entier
(D. 643-10), depuis 2004.

Le fonctionnaire (L. 84 à L. 86 du code des pensions) : L. 161-22 ne
s'applique pas à lui avant 2027. Payé par un employeur public — puis, civil
et parti depuis 2015, par tout employeur —, il ne touche dans l'année que le
tiers de sa pension et la moitié du minimum garanti sans que l'excédent soit
déduit de sa pension (L. 85) ; avant 2004, il ne touchait d'un employeur
public que l'excédent de sa pension sur sa rémunération, jusqu'à sa limite
d'âge (L. 86).

L'Agirc-Arrco suspend sa retraite complémentaire au-delà de son propre
plafond, le plus haut de 160 % du SMIC, du dernier salaire revalorisé et du
salaire moyen revalorisé des dix dernières années.

La complémentaire de l'artisan et du commerçant — le RCI, et les points du RCO
et du NRCO qu'il sert depuis 2013 — suit leur pension de base, que leurs
règlements lui imposent : suspendue avec elle depuis 2009, servie entière en
cumul intégral et quand la base n'est que réduite ; réduite du dépassement
comme elle depuis le 26 juin 2024 ; pour la première pension de 2027, réduite
de ce que la base n'absorbe pas (fiche
``cumul_emploi_retraite_complementaire_des_independants``).

L'Ircantec suit L. 161-22 pour l'activité qui y cotise, depuis 2004, sans la
réduction du dépassement depuis décembre 2020 ; la RCO agricole suit la règle
de la base de l'exploitant ; la complémentaire d'une section libérale, ce que
ses statuts écrivent — suspendue avec la base, réduite de ce que la base
n'absorbe pas ou du dépassement entier, incompatible avec le notariat
libéral. Pour la première pension de 2027, L. 161-22 réduit toutes ces
complémentaires de ce que les pensions de base n'absorbent pas, au prorata.

CHAQUE RÉGIME NE RÉDUIT QUE SES PENSIONS, pour l'activité qui relève de lui :
le salarié qui se fait artisan ne perd rien de sa pension du régime général ;
l'artisan qui se fait salarié ne perd rien de celle des artisans. Les
régimes dont le modèle n'a pas lu la règle — avocats, exploitants agricoles,
outre-mer, élus, les autres complémentaires — servent leur pension entière,
et le résultat le dit.

Le jumeau de ce module est ``moteur/js/droit/cumul.js``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Callable

from ..calendrier import DateMois
from . import departs as _departs
from ..somme import somme_ordonnee

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ResultatActuel, ScenarioActuel

#: Ce que le droit fait d'une pension, pour un mois d'activité.
LIBRE = "libre"
INTEGRAL = "integral"
PLAFONNEE = "plafonnee"
NON_DUE = "non_due"
SUSPENDUE = "suspendue"
REDUITE = "reduite"
SEUIL_NON_PUBLIE = "seuil_non_publie"
NON_CALCULE = "non_calcule"

#: L'ordre où se dit le statut d'un mois : celui de la pension la plus
#: touchée.
PRIORITE = (NON_DUE, SUSPENDUE, REDUITE, SEUIL_NON_PUBLIE, NON_CALCULE, PLAFONNEE,
            INTEGRAL, LIBRE)

#: Les versions des deux fiches.
AVANT_1983 = "sans_condition_avant_1983"
RUPTURE_1983 = "rupture_avec_l_employeur_1983"
PLAFOND_2004 = "plafond_du_dernier_salaire_2004"
LIBERALISE_2009 = "cumul_liberalise_2009"
PREMIERES_2015 = "premieres_pensions_de_2015"
REDUCTION_2015 = "reduction_du_depassement_2015"
AGES_2027 = "trois_regimes_selon_l_age_2027"
FP_1970 = "limite_d_age_1970"
FP_2004 = "tiers_de_la_pension_2004"
FP_2009 = "cumul_integral_2009"
FP_2015 = "tout_employeur_2015"
FP_2027 = "regles_communes_2027"
RCI_AVANT_2009 = "servie_entiere_avant_2009"
RCI_2009 = "suspendue_avec_la_base_2009"
RCI_2024 = "reduite_comme_la_base_2024"
#: La version de 2027 de chaque complémentaire que L. 161-22, III, A, réduit
#: après les bases : celle du RCI, de l'Ircantec, de la RCO agricole et des
#: sections libérales porte ce même nom dans sa fiche.
RCI_2027 = "imputee_apres_les_bases_2027"
#: Les versions des fiches de l'Ircantec, de la RCO agricole et des sections
#: libérales.
IRCANTEC_AVANT_2004 = "servie_entiere_avant_2004"
IRCANTEC_2004 = "l_161_22_2004"
IRCANTEC_2020 = "sans_le_troisieme_alinea_2020"
RCO_AGRICOLE_2003 = "suit_la_base_2003"
SECTIONS_STATUTS = "statuts_des_sections"

#: Les dates qui découpent la règle.
LOI_1983 = DateMois(1983, 4)
ARTISANS_1984 = DateMois(1984, 7)
LOI_2004 = DateMois(2004, 1)
LOI_2009 = DateMois(2009, 1)
#: D. 161-2-8 : le dernier salaire se revalorise pour les périodes d'après 2009.
REVALORISATION_2010 = DateMois(2010, 1)
#: Loi n° 2014-40, article 20, III : la pension d'un régime qui ouvre après
#: l'âge légal n'est pas attendue pour le cumul intégral.
ORDRE_DES_AGES = DateMois(2014, 2)
PREMIERE_2015 = DateMois(2015, 1)
#: Décret n° 2017-416 : la réduction du dépassement, pour les activités
#: exercées depuis le 1er avril 2017 (D. 161-2-16), et depuis le 1er janvier
#: pour les non-salariés (D. 634-11-2).
REDUCTION_SALARIES = DateMois(2017, 4)
REDUCTION_NON_SALARIES = DateMois(2017, 1)
PREMIERE_2027 = DateMois(2027, 1)
#: Les règlements du RCO et du NRCO approuvés le 7 juillet 2009 suspendent la
#: complémentaire avec la base (articles 23, II, et 10) ; la caisse les
#: applique depuis le 1er janvier 2009 (circulaire RSI n° 2009-044, § 2.4).
COMPLEMENTAIRES_2009 = DateMois(2009, 1)
#: L'arrêté du 19 juin 2024 applique la section 3 du code au service de la
#: pension du RCI, du 26 juin : le premier mois entier de sa rédaction.
SECTION_3_RCI = DateMois(2024, 7)
#: L'article 14 de l'arrêté du 30 décembre 1970 soumet l'allocation de
#: l'Ircantec à L. 161-22 depuis 2004 ; sans son troisième alinéa depuis
#: l'arrêté du 16 décembre 2020, en vigueur le 19 : le premier mois entier de
#: sa rédaction.
IRCANTEC_L_161_22 = DateMois(2004, 1)
IRCANTEC_SANS_REDUCTION = DateMois(2021, 1)

#: Les règles des statuts des sections libérales pour leur complémentaire,
#: pendant l'activité : suspendue dès la reprise de la profession ; suspendue
#: pour la même durée que la base (L. 643-6) ; suspendue ou réduite comme
#: elle ; réduite de ce que la base n'absorbe pas du dépassement ; réduite du
#: dépassement entier ; servie sans suspension ; incompatible avec le notariat
#: libéral.
A_LA_REPRISE = "suspendue_a_la_reprise"
AVEC_LA_BASE = "suspendue_avec_la_base"
COMME_LA_BASE = "reduite_comme_la_base"
APRES_LA_BASE = "reduite_apres_la_base"
DEPASSEMENT_ENTIER = "reduite_du_depassement"
SANS_SUSPENSION = "sans_suspension"
NOTAIRE_LIBERAL = "incompatible_avec_le_notariat_liberal"
#: Chaque section dont les statuts sont lus, la règle de chacune de leurs
#: rédactions et le premier mois entier où elle vaut (fiche
#: ``cumul_emploi_retraite_complementaires_des_liberaux``) ; une section ou un
#: mois qui n'y figure pas sert sa complémentaire entière.
REGLES_DES_SECTIONS = {
    "carcdsf_complementaire": ((DateMois(2007, 11), A_LA_REPRISE),
                               (DateMois(2011, 2), AVEC_LA_BASE)),
    "carmf_complementaire": ((DateMois(2011, 10), APRES_LA_BASE),),
    "carpv_complementaire": ((DateMois(2011, 2), DEPASSEMENT_ENTIER),
                             (DateMois(2022, 1), SANS_SUSPENSION)),
    "cavamac_complementaire": ((DateMois(2011, 7), AVEC_LA_BASE),
                               (DateMois(2026, 8), COMME_LA_BASE)),
    "cavom_complementaire": ((DateMois(2020, 10), APRES_LA_BASE),
                             (DateMois(2026, 8), DEPASSEMENT_ENTIER)),
    "cprn_complementaire": ((DateMois(2017, 7), NOTAIRE_LIBERAL),),
}
#: Les professions que visent les statuts de 2007 de la CARCDSF — « la
#: profession de chirurgien-dentiste » — et ceux de la CPRN — « la profession de
#: notaire libéral » —, par leur statut.
PROFESSIONS_DES_STATUTS = {A_LA_REPRISE: "chirurgien_dentiste_ou_sage_femme",
                           NOTAIRE_LIBERAL: "notaire"}

#: D. 161-2-15 : la reprise chez le dernier employeur, dans les six mois.
SIX_MOIS = 6
#: D. 161-2-9 : le SMIC mensuel, sur 1 820 heures par an ; 160 % depuis 2009.
HEURES_SMIC = 1820
PART_SMIC_2004 = 1.0
PART_SMIC_2009 = 1.6
#: L'assiette de la CSG sur les salaires, que D. 161-2-7 et D. 161-2-10
#: retiennent : l'abattement pour frais professionnels, 5 % de 1991 à 2004,
#: 3 % jusqu'en 2011, 1,75 % depuis. Avant 1991, les cotisations familiales,
#: sur le salaire entier.
ASSIETTES_CSG = ((1991, 0.95), (2005, 0.97), (2012, 0.9825))
#: D. 634-11-2 et D. 643-10 : le seuil des non-salariés, en plafond annuel de
#: la sécurité sociale.
SEUILS_NON_SALARIES = {"independants": 0.5, "liberaux": 1.0}
#: L. 85 : le tiers de la pension, et la moitié du minimum garanti du a de
#: L. 17 ; L. 86 de 1970 : le quart de la pension.
PART_DE_LA_PENSION = 1.0 / 3.0
ABATTEMENT_MINIMUM_GARANTI = 0.5
FRANCHISE_1970 = 0.25

#: Les pensions du code des pensions civiles et militaires, et des régimes
#: qui le suivent.
FONCTION_PUBLIQUE = frozenset({"fonction_publique_etat", "cnracl", "fspoeie",
                               "pensions_civiles_1853"})
#: Les régimes des collectivités d'outre-mer, dont le modèle n'a pas lu la
#: règle.
OUTRE_MER = frozenset({"cafat_nouvelle_caledonie", "cps_polynesie", "cps_polynesie_tranche_b",
                       "cps_saint_pierre_et_miquelon", "cssm_mayotte", "wallis_et_futuna",
                       "fonctionnaires_pacifique", "crfm_mayotte", "elus_pacifique"})
#: L'Agirc-Arrco et les caisses qu'elle a reprises.
AGIRC_ARRCO = frozenset({"agirc", "agirc_arrco", "agirc_entreprises_nouvelles", "arrco",
                         "arrco_cultes", "arrco_tranche_2",
                         "arrco_tranche_2_entreprises_nouvelles", "igrante", "ipacte",
                         "regimes_professionnels_integres", "unirs"})
#: Les statuts des artisans et des commerçants (L. 634-6).
INDEPENDANTS = frozenset({"artisan", "commercant", "micro_entrepreneur",
                          "liberal_non_reglemente", "gerant_debit_tabac"})
#: Le RCI et les complémentaires qu'il a reprises en 2013, dont il sert les
#: points : la pension complémentaire de l'artisan et du commerçant.
COMPLEMENTAIRES_DES_INDEPENDANTS = frozenset({"rci", "rco_artisans", "nric"})
#: Les régimes complémentaires des dix sections professionnelles des libéraux.
COMPLEMENTAIRES_DES_LIBERAUX = frozenset({
    "carcdsf_complementaire", "carmf_complementaire", "carpimko_complementaire",
    "carpv_complementaire", "cavamac_complementaire", "cavec_complementaire",
    "cavom_complementaire", "cavp_complementaire", "cipav_complementaire",
    "cprn_complementaire"})
#: Les groupes de complémentaires que la première pension de 2027 réduit après
#: les pensions de base (L. 161-22, III, A), au prorata de leurs montants.
GROUPES_COMPLEMENTAIRES_2027 = frozenset({"rci", "ircantec", "rco_agricole", "liberales"})
#: Le régime qui liquide la pension des régimes alignés (liquidation unique,
#: depuis 2017) et sert celle des artisans et des commerçants depuis 2020 :
#: celle d'un ancien indépendant suit aussi la règle de L. 634-6.
ALIGNES = frozenset({"regime_general"})
#: La limite d'âge de l'emploi quitté, avant 2004, selon son classement.
LIMITES_D_AGE_1970 = {None: 65.0, "active": 60.0, "super_active": 55.0}
#: Les groupes de pensions de base, que la règle de 2027 réunit.
GROUPES_DE_BASE = frozenset({"salaries", "independants", "liberaux", "avocats",
                             "exploitants", "fonction_publique"})
#: Les groupes dont le modèle a lu la règle, pour l'activité qui relève d'eux.
GROUPES_LUS = frozenset({"salaries", "independants", "liberaux"})


def assiette_csg(annee: int) -> float:
    """La part du salaire brut que la CSG retient, cette année-là."""
    part = 1.0
    for debut, valeur in ASSIETTES_CSG:
        if annee >= debut:
            part = valeur
    return part


def groupe_de_l_activite(moteur: ScenarioActuel, affiliation: str,
                         annee: int) -> str | None:
    """Le groupe de régimes dont relève l'activité : ``salaries``,
    ``independants``, ``liberaux``, ``avocats``, ``exploitants``,
    ``fonctionnaires`` ; ``None`` pour une activité dont le modèle n'a pas lu
    la règle (outre-mer, élus)."""
    if affiliation in INDEPENDANTS:
        return "independants"
    regimes = moteur.affiliations.regimes(affiliation, annee)
    if "cnavpl" in regimes:
        return "liberaux"
    if "cnbf" in regimes:
        return "avocats"
    if "msa_non_salaries" in regimes:
        return "exploitants"
    famille = moteur.affiliations.famille(affiliation)
    if famille in ("prive", "special", "agricole") or affiliation == "contractuel_public":
        return "salaries"
    if famille == "public":
        return "fonctionnaires"
    return None


def groupe_de_la_pension(moteur: ScenarioActuel, regime: str) -> str:
    """Le groupe d'une pension : celui de l'activité qui la réduit."""
    if regime in FONCTION_PUBLIQUE:
        return "fonction_publique"
    if regime in OUTRE_MER:
        return "outre_mer"
    if regime in AGIRC_ARRCO:
        return "agirc_arrco"
    if regime in COMPLEMENTAIRES_DES_INDEPENDANTS:
        return "rci"
    if regime == "ircantec":
        return "ircantec"
    if regime == "msa_rco":
        return "rco_agricole"
    if regime in COMPLEMENTAIRES_DES_LIBERAUX:
        return "liberales"
    fiche = moteur.catalogue[regime]
    if fiche.etage not in _departs.ETAGES_DES_UNITES:
        return "complementaires"
    if regime == "cnavpl":
        return "liberaux"
    if regime == "cnbf":
        return "avocats"
    if regime == "msa_non_salaries":
        return "exploitants"
    if fiche.famille == "non_salarie":
        return "independants"
    if fiche.famille in ("base_prive", "agricole", "special"):
        return "salaries"
    return "autres"


def fonction_publique_quittee(moteur: ScenarioActuel, carriere: Carriere) -> tuple[bool, float]:
    """La pension de l'État est-elle militaire, et la limite d'âge de l'emploi
    quitté, avant 2004 : celles de la dernière ligne de fonctionnaire avant le
    départ — soixante-cinq ans, soixante en catégorie active, cinquante-cinq en
    catégorie super-active."""
    affiliations = moteur.affiliations
    for ligne in reversed(carriere.lignes):
        if ligne.annee > carriere.annee_liquidation:
            continue
        regimes = affiliations.regimes(ligne.affiliation, ligne.annee)
        if not FONCTION_PUBLIQUE & set(regimes):
            continue
        categorie = affiliations.categorie_active(ligne.affiliation)
        limite = LIMITES_D_AGE_1970.get(categorie, LIMITES_D_AGE_1970[None])
        return affiliations.pension_militaire(ligne.affiliation) is not None, limite
    return False, LIMITES_D_AGE_1970[None]


@dataclass(frozen=True)
class PensionEnCumul:
    """Ce que le droit fait d'une pension, des mois d'une tranche."""

    regime: str
    #: :data:`LIBRE`, :data:`INTEGRAL`, :data:`PLAFONNEE`, :data:`NON_DUE`,
    #: :data:`SUSPENDUE`, :data:`REDUITE`, :data:`SEUIL_NON_PUBLIE` ou
    #: :data:`NON_CALCULE`.
    statut: str
    #: La version de la fiche qui le dit, et pourquoi.
    regle: str
    motif: str
    #: La pension du mois, et ce qui n'en est pas servi, en euros de l'année.
    montant: float
    reduction: float
    #: Le plafond mensuel de la règle qui la touche, ou ``None``.
    plafond: float | None = None

    def donnees(self) -> dict:
        return {"regime": self.regime, "statut": self.statut, "regle": self.regle,
                "motif": self.motif, "montant": self.montant, "reduction": self.reduction,
                "plafond": self.plafond}


@dataclass(frozen=True)
class TrancheDeCumul:
    """Des mois consécutifs d'une même année, où le droit traite chaque pension
    de la même façon. Les montants sont mensuels, en euros de l'année."""

    debut: DateMois
    #: Le premier mois qui n'en est plus.
    fin: DateMois
    #: Le revenu brut de l'activité, et toutes les pensions servies, avant
    #: réduction.
    revenu: float
    pensions: float
    #: Le plafond de la règle qui touche la pension, ou ``None``.
    plafond: float | None
    par_regime: tuple[PensionEnCumul, ...]

    @property
    def mois(self) -> int:
        return self.fin.rang - self.debut.rang

    @property
    def reduction(self) -> float:
        """Ce qui n'est pas servi, par mois."""
        return somme_ordonnee(p.reduction for p in self.par_regime)

    @property
    def principale(self) -> PensionEnCumul | None:
        """La pension qui dit le statut de la tranche : la plus touchée."""
        return min(self.par_regime, key=lambda p: PRIORITE.index(p.statut), default=None)

    @property
    def statut(self) -> str:
        principale = self.principale
        return principale.statut if principale is not None else LIBRE

    def donnees(self) -> dict:
        principale = self.principale
        return {"debut": jour(self.debut), "fin": jour(self.fin), "mois": self.mois,
                "statut": self.statut,
                "regle": principale.regle if principale is not None else None,
                "motif": principale.motif if principale is not None else None,
                "revenu": self.revenu, "pensions": self.pensions, "plafond": self.plafond,
                "reduction": self.reduction,
                "par_regime": [p.donnees() for p in self.par_regime]}


@dataclass(frozen=True)
class Cumul:
    """L'activité exercée après le départ, et ce que chaque pension en garde."""

    debut: DateMois
    fin: DateMois
    affiliation: str
    #: ``dernier`` ou ``autre``.
    employeur: str
    #: Le groupe de régimes dont relève l'activité (:func:`groupe_de_l_activite`).
    groupe: str | None
    #: Le mois où le cumul devient intégral, s'il le devient pendant l'activité.
    integral_depuis: DateMois | None
    tranches: tuple[TrancheDeCumul, ...]

    @property
    def non_servi(self) -> float:
        """Ce que l'activité fait perdre de pension, en tout, en euros de
        chaque année."""
        return somme_ordonnee(t.reduction * t.mois for t in self.tranches)

    def donnees(self) -> dict:
        return {"debut": jour(self.debut), "fin": jour(self.fin),
                "affiliation": self.affiliation, "employeur": self.employeur,
                "groupe": self.groupe,
                "integral_depuis": (jour(self.integral_depuis)
                                    if self.integral_depuis is not None else None),
                "non_servi": self.non_servi,
                "tranches": [t.donnees() for t in self.tranches]}


def jour(date_mois: DateMois) -> str:
    return f"{date_mois.annee:04d}-{date_mois.mois:02d}-01"


def _mois_de(jour: str) -> DateMois:
    return DateMois(int(jour[:4]), int(jour[5:7]))


@dataclass(frozen=True)
class _Annee:
    """Ce qu'une année de l'activité fournit à ses mois."""

    #: La pension annuelle de chaque régime, à l'échéance de l'année, et la
    #: majoration pour enfants.
    pensions: dict
    majoration: float
    #: Les mois d'activité de l'année, et le revenu brut mensuel.
    mois: int
    revenu: float
    #: Le SMIC mensuel sur 1 820 heures, le plafond de la sécurité sociale, le
    #: minimum garanti du a de L. 17.
    smic: float
    plafond_securite_sociale: float
    minimum_garanti: float


class _Calcul:
    """Le calcul, mois par mois, d'une activité après le départ."""

    def __init__(self, moteur: ScenarioActuel, carriere: Carriere, resultat: ResultatActuel,
                 pensions_de: Callable[[int], tuple[dict, float]], annee_courante: int) -> None:
        emploi = carriere.emploi_retraite
        self.moteur = moteur
        self.carriere = carriere
        self.pensions_de = pensions_de
        self.debut, self.fin = emploi["debut"], emploi["fin"]
        self.affiliation, self.employeur = emploi["affiliation"], emploi["employeur"]
        self.groupe = groupe_de_l_activite(moteur, self.affiliation, self.debut.annee)
        self.public = moteur.affiliations.famille(self.affiliation) == "public"
        self.declare = carriere.date_liquidation
        #: La dernière année dont les revalorisations sont publiées : au-delà,
        #: les pensions et le dernier salaire suivent les prix, comme la loi
        #: les revalorise (L. 161-25), à la rencontre des revenus que la
        #: carrière projette en euros courants.
        self.ancre = max(annee_courante, self.declare.annee)
        #: La première pension de base : celle du départ déclaré. Une pension
        #: militaire servie depuis la sortie de l'armée n'y compte pas : L. 84
        #: la soustrait à L. 161-22.
        self.premiere = self.declare
        self.pensions = tuple(
            (p.regime, _mois_de(p.date_effet) if p.date_effet else self.declare,
             groupe_de_la_pension(moteur, p.regime))
            for p in resultat.pensions_par_regime)
        self.age_legal = _departs.age_legal(moteur, carriere)
        automatique = moteur.ages_annulation_decote.age(carriere.generation)
        self.age_automatique = automatique[0] if automatique is not None else 65.0
        self.duree = resultat.trimestres_valides >= resultat.trimestres_requis
        self.militaire, self.limite_d_age = fonction_publique_quittee(moteur, carriere)
        #: L'assuré a-t-il été artisan ou commerçant avant son départ ?
        self.independant = any(ligne.affiliation in INDEPENDANTS
                               for ligne in carriere.lignes
                               if ligne.annee <= self.declare.annee)
        self.dernier = self._dernier_salaire()
        self.moyen = self._salaire_moyen()
        self.lignes = {}
        for ligne in carriere.lignes_apres_depart:
            self.lignes[ligne.annee] = self.lignes.get(ligne.annee, 0.0) + ligne.revenu
        self._annees: dict[int, _Annee] = {}
        self._revalorisations: dict[DateMois, float] = {}
        self._deductions: dict[tuple[str, int], float] = {}

    # -- la carrière d'avant le départ ------------------------------------------------

    def _dernier_salaire(self) -> tuple[float, int] | None:
        """Le dernier salaire mensuel brut avant le départ, en temps plein
        (D. 161-2-7, II), et son année : les lignes de la dernière année
        d'emploi, rapportées à ses mois."""
        emplois = [l for l in self.carriere.lignes
                   if l.type_periode == "emploi" and l.revenu > 0
                   and l.annee <= self.declare.annee]
        if not emplois:
            return None
        annee = max(l.annee for l in emplois)
        derniere = [l for l in emplois if l.annee == annee]
        mois = max(1, round(max(l.fraction_annee for l in derniere) * 12))
        brut = somme_ordonnee(l.revenu / (l.quotite if 0 < l.quotite < 1 else 1.0) for l in derniere)
        return brut / mois, annee

    def _salaire_moyen(self) -> tuple[float, int] | None:
        """Le salaire mensuel moyen des dix dernières années d'emploi, en euros
        de l'année du départ : le troisième terme du plafond de l'Agirc-Arrco."""
        emplois = [l for l in self.carriere.lignes
                   if l.type_periode == "emploi" and l.revenu > 0
                   and l.annee <= self.declare.annee]
        annees = sorted({l.annee for l in emplois})[-10:]
        if not annees:
            return None
        macro = self.moteur.macro
        total = mois = 0.0
        for annee in annees:
            lignes = [l for l in emplois if l.annee == annee]
            total += somme_ordonnee(l.revenu for l in lignes) * macro.coefficient_prix(
                annee, self.declare.annee)
            mois += max(l.fraction_annee for l in lignes) * 12
        return (total / mois if mois else 0.0), self.declare.annee

    # -- l'année et le mois -----------------------------------------------------------

    def annee(self, annee: int) -> _Annee:
        if annee not in self._annees:
            pensions, majoration = self.pensions_de(min(annee, self.ancre))
            if annee > self.ancre:
                prix = self.moteur.macro.coefficient_prix(self.ancre, annee)
                pensions = {regime: montant * prix for regime, montant in pensions.items()}
                majoration *= prix
            mois = somme_ordonnee(1 for rang in range(self.debut.rang, self.fin.rang)
                       if DateMois.depuis_rang(rang).annee == annee)
            macro = self.moteur.macro
            reference = self.moteur.minimum_garanti.reference(annee)
            self._annees[annee] = _Annee(
                pensions=pensions, majoration=majoration, mois=mois,
                revenu=self.lignes.get(annee, 0.0) / mois if mois else 0.0,
                smic=macro.smic_horaire(annee) * HEURES_SMIC / 12.0,
                plafond_securite_sociale=macro.plafond_securite_sociale(annee),
                minimum_garanti=reference[0] if reference is not None else 0.0)
        return self._annees[annee]

    def age(self, mois: DateMois) -> float:
        return self.carriere.age_au(mois)

    def integral(self, mois: DateMois) -> bool:
        """Le cumul intégral : toutes les pensions liquidées, à l'âge du taux
        plein automatique, ou à l'âge légal avec la durée requise ; pour la
        première pension de 2027, à l'âge du taux plein automatique seul."""
        if mois < LOI_2009:
            return False
        for regime, date_effet, _ in self.pensions:
            if date_effet <= mois:
                continue
            # Depuis la loi de 2014, la pension d'un régime qui ouvre après
            # l'âge légal n'est pas attendue.
            if (mois >= ORDRE_DES_AGES
                    and self.carriere.age_au(date_effet) > self.age_legal + 1e-9):
                continue
            return False
        age = self.age(mois)
        if self.premiere >= PREMIERE_2027:
            # La première pension de 2027 ne se cumule entièrement qu'à l'âge
            # du taux plein automatique (L. 161-22, III, A, 3°).
            return age >= self.age_automatique - 1e-9
        return (age >= self.age_automatique - 1e-9
                or (age >= self.age_legal - 1e-9 and self.duree))

    def _revalorisation(self, mois: DateMois) -> float:
        """Ce qui mène le dernier salaire au mois : les revalorisations des
        pensions depuis le départ (D. 161-2-8), pour les mois d'après 2009."""
        if mois < REVALORISATION_2010:
            return 1.0
        if mois not in self._revalorisations:
            depuis = date(self.declare.annee, self.declare.mois, 1)
            jusqu_a = (date(mois.annee, mois.mois, 1) if mois.annee <= self.ancre
                       else date(self.ancre, 12, 31))
            coefficient = (self.moteur.revalorisations_pensions.generale(
                depuis, jusqu_a, False, None)[0] if jusqu_a > depuis else 1.0)
            if mois.annee > self.ancre:
                coefficient *= self.moteur.macro.coefficient_prix(self.ancre, mois.annee)
            self._revalorisations[mois] = coefficient
        return self._revalorisations[mois]

    def plafond_salarie(self, mois: DateMois, annee: _Annee) -> float:
        """Le plafond de L. 161-22 : le dernier salaire, à son assiette de CSG
        et revalorisé, au moins le SMIC, puis 160 % du SMIC depuis 2009."""
        dernier = 0.0
        if self.dernier is not None:
            mensuel, son_annee = self.dernier
            dernier = mensuel * assiette_csg(son_annee) * self._revalorisation(mois)
        part = PART_SMIC_2009 if mois >= LOI_2009 else PART_SMIC_2004
        return max(dernier, part * annee.smic)

    def plafond_agirc_arrco(self, mois: DateMois, annee: _Annee) -> float:
        """Le plafond de l'Agirc-Arrco : celui du régime de base, ou le salaire
        moyen des dix dernières années, revalorisé, s'il est plus haut."""
        plafond = self.plafond_salarie(mois, annee)
        if self.moyen is not None and mois >= LOI_2009:
            mensuel, son_annee = self.moyen
            plafond = max(plafond, mensuel * assiette_csg(son_annee)
                          * self._revalorisation(mois))
        return plafond

    def version(self, mois: DateMois, date_effet: DateMois) -> str:
        """La version de L. 161-22 qui vaut pour ce mois et cette pension."""
        if date_effet < LOI_1983:
            return AVANT_1983
        if self.premiere >= PREMIERE_2027:
            return AGES_2027
        if mois < LOI_2009:
            return RUPTURE_1983 if date_effet < LOI_2004 else PLAFOND_2004
        if self.premiere < PREMIERE_2015:
            return LIBERALISE_2009
        return PREMIERES_2015 if mois < REDUCTION_SALARIES else REDUCTION_2015

    def _dans_les_six_mois(self, mois: DateMois, date_effet: DateMois) -> bool:
        """La reprise chez le dernier employeur dans les six mois de la pension
        (D. 161-2-15) : la pension n'est pas due jusqu'au sixième mois."""
        limite = date_effet.plus_mois(SIX_MOIS)
        return self.employeur == "dernier" and self.debut < limite and mois < limite

    # -- la règle de chaque pension ---------------------------------------------------

    def mois(self, mois: DateMois) -> tuple[list[PensionEnCumul], float | None]:
        """Ce que chaque pension servie ce mois-là en garde, et le plafond de
        la règle qui touche la plus touchée."""
        annee = self.annee(mois.annee)
        servies = [(regime, date_effet, groupe) for regime, date_effet, groupe
                   in self.pensions
                   if date_effet <= mois and annee.pensions.get(regime, 0.0) > 0]
        montants = {regime: annee.pensions.get(regime, 0.0) / 12.0
                    for regime, _, _ in servies}
        total = somme_ordonnee(montants.values()) + (annee.majoration / 12.0 if servies else 0.0)
        integral = self.integral(mois)
        resultats: list[PensionEnCumul] = []
        # La règle de 2027 réunit les pensions de base : la réduction des
        # revenus s'y répartit au prorata.
        base_2027 = somme_ordonnee(montants[regime] for regime, _, groupe in servies
                        if groupe in GROUPES_DE_BASE)
        # Les points du RCI, du RCO et du NRCO font une seule pension.
        complementaire = somme_ordonnee(montants[regime] for regime, _, groupe in servies
                                        if groupe == "rci")
        # Les complémentaires que la règle de 2027 réduit après les bases.
        complementaires_2027 = somme_ordonnee(montants[regime] for regime, _, groupe in servies
                                              if groupe in GROUPES_COMPLEMENTAIRES_2027)
        for regime, date_effet, groupe in servies:
            montant = montants[regime]
            if self.premiere >= PREMIERE_2027 and groupe in GROUPES_DE_BASE:
                decision = self._regle_2027(mois, date_effet, groupe, montant, annee,
                                            base_2027)
            elif self.premiere >= PREMIERE_2027 and groupe in GROUPES_COMPLEMENTAIRES_2027:
                decision = self._complementaire_2027(mois, date_effet, montant,
                                                     montant / complementaires_2027, annee,
                                                     base_2027)
            elif groupe == "fonction_publique":
                decision = self._fonctionnaire(mois, regime, date_effet, montant, annee,
                                               integral)
            elif groupe == "agirc_arrco":
                decision = self._agirc_arrco(mois, date_effet, montant, annee, total,
                                             integral)
            elif groupe == "rci":
                decision = self._complementaire_des_independants(
                    mois, date_effet, montant, montant / complementaire, annee, integral,
                    servies, montants)
            elif groupe == "ircantec":
                decision = self._ircantec(mois, date_effet, montant, annee, total, integral)
            elif groupe == "rco_agricole":
                decision = self._rco_agricole()
            elif groupe == "liberales":
                decision = self._complementaire_des_liberaux(mois, regime, date_effet, montant,
                                                             annee, integral, servies,
                                                             montants)
            elif groupe in ("complementaires", "autres"):
                decision = (LIBRE, "", "non_lue", 0.0, None)
            elif not self._concerne(regime, groupe):
                decision = (LIBRE, "", "autre_regime", 0.0, None)
            elif self.groupe == "salaries":
                decision = self._salarie(mois, date_effet, montant, annee, total, integral)
            elif self.groupe in SEUILS_NON_SALARIES:
                decision = self._non_salarie(mois, date_effet, self.groupe, montant, annee,
                                             integral, servies, montants)
            else:
                decision = (NON_CALCULE, "", "regle_non_lue", 0.0, None)
            statut, regle, motif, reduction, plafond = decision
            resultats.append(PensionEnCumul(regime, statut, regle, motif, montant,
                                            min(montant, max(0.0, reduction)), plafond))
        principale = min(resultats, key=lambda p: PRIORITE.index(p.statut), default=None)
        return resultats, principale.plafond if principale is not None else None

    def _concerne(self, regime: str, groupe: str) -> bool:
        """L'activité touche-t-elle cette pension ? Celle de son groupe, et,
        pour l'ancien artisan ou commerçant qui le redevient, la pension des
        régimes alignés que le régime général sert."""
        if groupe == self.groupe:
            return True
        return self.groupe == "independants" and self.independant and regime in ALIGNES

    def _salarie(self, mois: DateMois, date_effet: DateMois, montant: float, annee: _Annee,
                 total: float, integral: bool) -> tuple:
        """L. 161-22, pour une pension de salarié et une activité salariée."""
        regle = self.version(mois, date_effet)
        if regle == AVANT_1983:
            return LIBRE, regle, "avant_1983", 0.0, None
        if regle == RUPTURE_1983:
            if self.employeur == "dernier":
                return NON_DUE, regle, "dernier_employeur", montant, None
            return LIBRE, regle, "autre_employeur", 0.0, None
        if integral:
            return INTEGRAL, regle, "taux_plein", 0.0, None
        if self._dans_les_six_mois(mois, date_effet):
            return NON_DUE, regle, "six_mois", montant, None
        plafond = self.plafond_salarie(mois, annee)
        depassement = total + annee.revenu * assiette_csg(mois.annee) - plafond
        if depassement <= 0:
            return PLAFONNEE, regle, "sous_le_plafond", 0.0, plafond
        if regle == REDUCTION_2015:
            return REDUITE, regle, "depassement", depassement, plafond
        return SUSPENDUE, regle, "depassement", montant, plafond

    def _agirc_arrco(self, mois: DateMois, date_effet: DateMois, montant: float,
                     annee: _Annee, total: float, integral: bool) -> tuple:
        """La retraite complémentaire, suspendue au-delà de son plafond, pour
        une activité salariée qui cotise à l'Agirc-Arrco."""
        regimes = self.moteur.affiliations.regimes(self.affiliation, mois.annee)
        if not AGIRC_ARRCO & set(regimes):
            return LIBRE, "", "autre_regime", 0.0, None
        regle = self.version(mois, date_effet)
        if regle == AVANT_1983:
            return LIBRE, regle, "avant_1983", 0.0, None
        if regle == RUPTURE_1983:
            if self.employeur == "dernier":
                return NON_DUE, regle, "dernier_employeur", montant, None
            return LIBRE, regle, "autre_employeur", 0.0, None
        if integral:
            return INTEGRAL, regle, "taux_plein", 0.0, None
        if self._dans_les_six_mois(mois, date_effet):
            return NON_DUE, regle, "six_mois", montant, None
        plafond = self.plafond_agirc_arrco(mois, annee)
        if total + annee.revenu * assiette_csg(mois.annee) <= plafond:
            return PLAFONNEE, regle, "sous_le_plafond", 0.0, plafond
        return SUSPENDUE, regle, "depassement", montant, plafond

    def _non_salarie(self, mois: DateMois, date_effet: DateMois, groupe: str,
                     montant: float, annee: _Annee, integral: bool, servies,
                     montants: dict) -> tuple:
        """L. 634-6 et L. 643-6 : l'artisan, le commerçant et le libéral."""
        if groupe == "independants" and date_effet < LOI_2004:
            if date_effet < ARTISANS_1984:
                return LIBRE, AVANT_1983, "avant_1984", 0.0, None
            if mois < LOI_2009:
                if self.employeur == "dernier":
                    return NON_DUE, RUPTURE_1983, "meme_entreprise", montant, None
                return LIBRE, RUPTURE_1983, "autre_entreprise", 0.0, None
        if date_effet < LOI_2004 and mois < LOI_2009:
            return NON_CALCULE, "", "regle_non_lue", 0.0, None
        if mois < LOI_2009:
            regle = PLAFOND_2004
        elif self.premiere < PREMIERE_2015:
            regle = LIBERALISE_2009
        elif mois < REDUCTION_NON_SALARIES:
            regle = PREMIERES_2015
        else:
            regle = REDUCTION_2015
        if integral:
            return INTEGRAL, regle, "taux_plein", 0.0, None
        # Le seuil est annuel, rapporté aux mois d'activité : le dépassement de
        # l'année se répartit sur ses mois, et entre les pensions du régime.
        seuil = SEUILS_NON_SALARIES[groupe] * annee.plafond_securite_sociale / 12.0
        depassement = annee.revenu - seuil
        if depassement <= 0:
            return PLAFONNEE, regle, "sous_le_plafond", 0.0, seuil
        if regle != REDUCTION_2015:
            return SUSPENDUE, regle, "depassement", montant, seuil
        du_groupe = somme_ordonnee(montants[code] for code, _, g in servies if self._concerne(code, g))
        part = montant / du_groupe if du_groupe > 0 else 0.0
        return REDUITE, regle, "depassement", depassement * part, seuil

    def _complementaire_des_independants(self, mois: DateMois, date_effet: DateMois,
                                         montant: float, part: float, annee: _Annee,
                                         integral: bool, servies, montants: dict) -> tuple:
        """La complémentaire de l'artisan et du commerçant, que leurs
        règlements soumettent aux règles de cumul de la pension de base ;
        ``part`` est celle de ses points du RCI, du RCO ou du NRCO dans la
        pension qu'ils font ensemble.

        * Avant 2009, la règle n'est pas lue : le modèle la sert entière.
        * Depuis 2009, « Lorsque l'assuré est soumis à une suspension dans le
          régime de base en application des alinéas 2 et 3 de l'article
          L. 634-6 [...], le service de la pension de vieillesse complémentaire
          est suspendu pour la même durée », et l'assuré a droit à son « service
          intégral » en cumul intégral (règlements du RCO et du NRCO de 2009,
          articles 23, II, et 10 ; du RCI, article 27, jusqu'au 25 juin 2024) :
          la base que le dépassement ne fait que réduire, depuis 2017, ne la
          touche pas.
        * Depuis, « Les dispositions de la section 3 du chapitre 4 du titre III
          du livre VI du code de la sécurité sociale sont applicables au service
          de la pension » (article 27, arrêté du 19 juin 2024) : réduite du
          dépassement entier, comme la base, ou suspendue avec elle.
        * Pour la première pension de 2027, L. 161-22, que l'article 27 lui
          applique depuis le 1er janvier 2027 (:meth:`_complementaire_2027`).

        Hors de la première pension de 2027, seule l'activité de l'artisan ou
        du commerçant la touche : l'article 27 vise « les activités relevant
        des régimes des professions artisanales, industrielles et
        commerciales », L. 634-6 l'activité indépendante.
        """
        if mois < COMPLEMENTAIRES_2009:
            return LIBRE, RCI_AVANT_2009, "non_lue", 0.0, None
        if self.groupe != "independants":
            return LIBRE, "", "autre_regime", 0.0, None
        statut, _, motif, _, seuil = self._non_salarie(
            mois, date_effet, "independants", montant, annee, integral, servies, montants)
        regle = RCI_2009 if mois < SECTION_3_RCI else RCI_2024
        if statut == SUSPENDUE:
            return SUSPENDUE, regle, motif, montant, seuil
        if statut != REDUITE:
            return statut, regle, motif, 0.0, seuil
        if regle == RCI_2009:
            return PLAFONNEE, regle, "base_reduite", 0.0, seuil
        return REDUITE, regle, motif, (annee.revenu - seuil) * part, seuil

    def _complementaire_2027(self, mois: DateMois, date_effet: DateMois, montant: float,
                             part: float, annee: _Annee, base_2027: float) -> tuple:
        """L. 161-22, III, A, de 2027, pour la première pension de base de
        cette date : « Une pension de vieillesse personnelle servie au titre
        d'un régime légal ou rendu légalement obligatoire, de base ou
        complémentaire » est réduite de tout le revenu avant l'âge légal ; la
        réduction « est appliquée, par priorité, sur les pensions versées par
        les régimes de retraite de base », et « La somme des réductions imputée
        sur chaque pension ne peut excéder la réduction ». La complémentaire —
        le RCI, que son règlement y soumet depuis le 1er janvier 2027,
        l'Ircantec, la RCO agricole, les sections libérales — perd ce que les
        pensions de base n'absorbent pas, au prorata (``part``) de celles
        qu'elle réduit. L'Agirc-Arrco garde sa règle."""
        statut, _, motif, reduction, plafond = self._regle_2027(
            mois, date_effet, "complementaires", montant, annee, base_2027)
        if statut != REDUITE:
            return statut, RCI_2027, motif, reduction, plafond
        reste = annee.revenu * assiette_csg(mois.annee) - base_2027
        if reste <= 0:
            return PLAFONNEE, RCI_2027, "imputee_sur_la_base", 0.0, None
        return REDUITE, RCI_2027, motif, reste * part, None

    def _ircantec(self, mois: DateMois, date_effet: DateMois, montant: float, annee: _Annee,
                  total: float, integral: bool) -> tuple:
        """L'allocation de l'Ircantec, que l'article 14 de l'arrêté du 30
        décembre 1970 soumet aux conditions de L. 161-22 pour l'activité qui y
        cotise (fiche ``cumul_emploi_retraite_ircantec``).

        * Avant 2004, l'article ne dit que la cessation de tout emploi qui
          ouvre le droit : le modèle la sert entière.
        * Depuis 2004, « La reprise d'activité est autorisée dans les
          conditions prévues à l'article L. 161-22 », puis, depuis 2011, « Le
          cumul d'une allocation de retraite avec l'exercice d'une activité
          professionnelle entraînant un assujettissement à l'IRCANTEC » : la
          règle de la pension de base du salarié — la rupture, les six mois, le
          plafond, la suspension, puis la réduction du dépassement.
        * Depuis l'arrêté du 16 décembre 2020, en vigueur le 19, « à
          l'exception de son troisième alinéa », celui qui réduit « chacune
          des pensions » : au-delà du plafond, l'allocation est servie entière,
          l'Ircantec « continue de vous verser la totalité » (sa page du cumul
          emploi-retraite).
        """
        if mois < IRCANTEC_L_161_22:
            return LIBRE, IRCANTEC_AVANT_2004, "non_lue", 0.0, None
        if "ircantec" not in self.moteur.affiliations.regimes(self.affiliation, mois.annee):
            return LIBRE, "", "autre_regime", 0.0, None
        statut, _, motif, reduction, plafond = self._salarie(mois, date_effet, montant, annee,
                                                             total, integral)
        if mois < IRCANTEC_SANS_REDUCTION:
            return statut, IRCANTEC_2004, motif, reduction, plafond
        if motif == "depassement":
            return PLAFONNEE, IRCANTEC_2020, "sans_le_troisieme_alinea", 0.0, plafond
        return statut, IRCANTEC_2020, motif, reduction, plafond

    def _rco_agricole(self) -> tuple:
        """La retraite complémentaire obligatoire des non-salariés agricoles :
        « Les dispositions des articles L. 732-39 et L. 732-40 sont applicables
        à la pension de retraite complémentaire obligatoire » (D. 732-157,
        depuis 2003). Elle suit la règle de la base de l'exploitant, que le
        modèle n'a pas lue pour l'activité agricole non salariée, et que
        l'activité d'un autre régime ne touche pas (fiche
        ``cumul_emploi_retraite_rco_agricole``)."""
        if self.groupe != "exploitants":
            return LIBRE, "", "autre_regime", 0.0, None
        return NON_CALCULE, RCO_AGRICOLE_2003, "regle_non_lue", 0.0, None

    def _complementaire_des_liberaux(self, mois: DateMois, regime: str, date_effet: DateMois,
                                     montant: float, annee: _Annee, integral: bool, servies,
                                     montants: dict) -> tuple:
        """La complémentaire d'une section libérale, selon la règle que ses
        statuts écrivent ce mois-là (:data:`REGLES_DES_SECTIONS` ; fiche
        ``cumul_emploi_retraite_complementaires_des_liberaux``).

        * La CARCDSF de 2007 et la CPRN visent une profession : « Le versement
          de la retraite complémentaire est suspendu pour tout allocataire qui
          reprend l'exercice de la profession de chirurgien-dentiste » ; le
          droit aux allocations « est incompatible avec l'exercice de la
          profession de notaire libéral ».
        * Les autres règles suivent le seuil de la base (L. 643-6, D. 643-10),
          pour l'activité libérale, et cèdent au cumul intégral : la CARCDSF
          depuis 2011 et la CAVAMAC suspendent la complémentaire « pour la même
          durée » que la base ; la CAVAMAC depuis 2026, « dans les mêmes
          conditions que pour le régime de base » ; la CARMF « conjointement à
          celui des autres pensions [...] versées par la caisse et à concurrence
          du montant du dépassement », la CAVOM de 2020 quand « le revenu
          dépasse le seuil après cette diminution » de la base : ce que la base
          n'absorbe pas ; la CARPV de 2011, « pendant la durée qui aurait procuré
          [...] un montant brut d'allocations [...] égal au montant du
          dépassement », la CAVOM de 2026 « à due concurrence du montant du
          dépassement » : le dépassement entier ; la CARPV depuis 2022, aucune.
        """
        regle_des_statuts = None
        for debut, regle in REGLES_DES_SECTIONS.get(regime, ()):
            if mois >= debut:
                regle_des_statuts = regle
        if regle_des_statuts is None:
            return LIBRE, SECTIONS_STATUTS, "non_lue", 0.0, None
        if regle_des_statuts == SANS_SUSPENSION:
            return LIBRE, SECTIONS_STATUTS, "sans_suspension", 0.0, None
        if regle_des_statuts in PROFESSIONS_DES_STATUTS:
            if self.affiliation != PROFESSIONS_DES_STATUTS[regle_des_statuts]:
                return LIBRE, "", "autre_regime", 0.0, None
            if regle_des_statuts == A_LA_REPRISE:
                return SUSPENDUE, SECTIONS_STATUTS, "reprise", montant, None
            return NON_DUE, SECTIONS_STATUTS, "notaire_liberal", montant, None
        if self.groupe != "liberaux":
            return LIBRE, "", "autre_regime", 0.0, None
        statut, _, motif, _, seuil = self._non_salarie(mois, date_effet, "liberaux", montant,
                                                       annee, integral, servies, montants)
        if statut not in (SUSPENDUE, REDUITE):
            return statut, SECTIONS_STATUTS, motif, 0.0, seuil
        depassement = annee.revenu - seuil
        if regle_des_statuts == DEPASSEMENT_ENTIER:
            return REDUITE, SECTIONS_STATUTS, motif, depassement, seuil
        if regle_des_statuts == APRES_LA_BASE:
            base = somme_ordonnee(montants[code] for code, _, groupe in servies
                                  if groupe == "liberaux")
            if depassement <= base:
                return PLAFONNEE, SECTIONS_STATUTS, "imputee_sur_la_base", 0.0, seuil
            return REDUITE, SECTIONS_STATUTS, motif, depassement - base, seuil
        if statut == SUSPENDUE:
            return SUSPENDUE, SECTIONS_STATUTS, motif, montant, seuil
        if regle_des_statuts == AVEC_LA_BASE:
            return PLAFONNEE, SECTIONS_STATUTS, "base_reduite", 0.0, seuil
        return REDUITE, SECTIONS_STATUTS, motif, depassement, seuil

    def _fonctionnaire(self, mois: DateMois, regime: str, date_effet: DateMois,
                       montant: float, annee: _Annee, integral: bool) -> tuple:
        """L. 84 à L. 86 du code des pensions."""
        if date_effet < LOI_2004:
            if not self.public:
                return LIBRE, FP_1970, "employeur_prive", 0.0, None
            if self.militaire:
                return NON_CALCULE, FP_1970, "militaire", 0.0, None
            if self.age(mois) >= self.limite_d_age - 1e-9:
                return LIBRE, FP_1970, "limite_d_age", 0.0, None
            if annee.revenu <= FRANCHISE_1970 * montant:
                return PLAFONNEE, FP_1970, "quart_de_la_pension", 0.0, FRANCHISE_1970 * montant
            return REDUITE, FP_1970, "remuneration", annee.revenu, None
        if mois < LOI_2009:
            regle = FP_2004
        elif self.premiere < PREMIERE_2015:
            regle = FP_2009
        else:
            regle = FP_2015
        if mois >= LOI_2009 and integral:
            return INTEGRAL, regle, "taux_plein", 0.0, None
        tout_employeur = self.premiere >= PREMIERE_2015 and not self.militaire
        if not (self.public or tout_employeur):
            return LIBRE, regle, "employeur_prive", 0.0, None
        deduction, plafond = self._deduction_fonction_publique(regime, date_effet, mois.annee)
        if deduction <= 0:
            return PLAFONNEE, regle, "sous_le_plafond", 0.0, plafond
        return REDUITE, regle, "depassement", deduction, plafond

    def _deduction_fonction_publique(self, regime: str, date_effet: DateMois,
                                     annee_civile: int) -> tuple[float, float]:
        """L. 85 : l'excédent des revenus de l'année sur le tiers de la pension
        de l'année et la moitié du minimum garanti, réparti sur les mois
        d'activité où la règle vaut ; et ce plafond, par mois."""
        annee = self.annee(annee_civile)
        mois = [DateMois.depuis_rang(rang) for rang in range(self.debut.rang, self.fin.rang)
                if DateMois.depuis_rang(rang).annee == annee_civile]
        couverts = [m for m in mois if not (m >= LOI_2009 and self.integral(m))]
        annuelle = annee.pensions.get(regime, 0.0)
        servis = somme_ordonnee(1 for m in range(1, 13)
                     if DateMois(annee_civile, m) >= date_effet)
        pension_de_l_annee = annuelle * servis / 12.0
        plafond = (PART_DE_LA_PENSION * pension_de_l_annee
                   + ABATTEMENT_MINIMUM_GARANTI * annee.minimum_garanti)
        cle = (regime, annee_civile)
        if cle not in self._deductions:
            revenus = annee.revenu * len(couverts)
            excedent = max(0.0, revenus - plafond)
            self._deductions[cle] = excedent / len(couverts) if couverts else 0.0
        return self._deductions[cle], plafond / 12.0

    def _regle_2027(self, mois: DateMois, date_effet: DateMois, groupe: str,
                    montant: float, annee: _Annee, base: float) -> tuple:
        """L. 161-22 pour les premières pensions de 2027, que L. 84 du code
        des pensions étend au fonctionnaire."""
        regle = FP_2027 if groupe == "fonction_publique" else AGES_2027
        age = self.age(mois)
        if age >= self.age_automatique - 1e-9:
            return INTEGRAL, regle, "age_du_taux_plein", 0.0, None
        if self._dans_les_six_mois(mois, date_effet):
            return NON_DUE, regle, "six_mois", montant, None
        if age >= self.age_legal - 1e-9:
            return SEUIL_NON_PUBLIE, regle, "seuil_non_publie", 0.0, None
        revenu = annee.revenu * assiette_csg(mois.annee)
        part = montant / base if base > 0 else 0.0
        if revenu <= 0:
            return PLAFONNEE, regle, "sans_revenu", 0.0, None
        return REDUITE, regle, "avant_l_age_legal", revenu * part, None


def cumuler(moteur: ScenarioActuel, carriere: Carriere, resultat: ResultatActuel,
            pensions_de: Callable[[int], tuple[dict, float]],
            annee_courante: int) -> Cumul | None:
    """Le cumul de l'activité que ``carriere`` exerce après son départ, ou
    ``None`` sans elle.

    ``resultat`` est le scénario 1 au départ ; ``pensions_de(annee)`` rend la
    pension annuelle de chaque régime menée à cette année — l'étape « faire
    vivre » —, et la majoration pour enfants ; au-delà de ``annee_courante``,
    le module les mène par les prix. Les mois se regroupent en tranches, dans
    l'année, tant que chaque pension y garde le même sort.
    """
    if carriere.emploi_retraite is None or resultat is None:
        return None
    calcul = _Calcul(moteur, carriere, resultat, pensions_de, annee_courante)
    tranches: list[TrancheDeCumul] = []
    integral_depuis = None
    courante = None
    for rang in range(calcul.debut.rang, calcul.fin.rang):
        mois = DateMois.depuis_rang(rang)
        if integral_depuis is None and calcul.integral(mois):
            integral_depuis = mois
        par_regime, plafond = calcul.mois(mois)
        annee = calcul.annee(mois.annee)
        pensions = (somme_ordonnee(p.montant for p in par_regime)
                    + (annee.majoration / 12.0 if par_regime else 0.0))
        cle = (mois.annee, tuple((p.regime, p.statut, p.regle, p.motif, p.reduction,
                                  p.plafond) for p in par_regime))
        if courante is not None and courante[0] == cle:
            courante[2] = rang + 1
            continue
        if courante is not None:
            tranches.append(_tranche(*courante[1:]))
        courante = [cle, rang, rang + 1, annee.revenu, pensions, plafond, tuple(par_regime)]
    if courante is not None:
        tranches.append(_tranche(*courante[1:]))
    return Cumul(debut=calcul.debut, fin=calcul.fin, affiliation=calcul.affiliation,
                 employeur=calcul.employeur, groupe=calcul.groupe,
                 integral_depuis=integral_depuis, tranches=tuple(tranches))


def _tranche(debut: int, fin: int, revenu: float, pensions: float, plafond: float | None,
             par_regime: tuple[PensionEnCumul, ...]) -> TrancheDeCumul:
    return TrancheDeCumul(debut=DateMois.depuis_rang(debut), fin=DateMois.depuis_rang(fin),
                          revenu=revenu, pensions=pensions, plafond=plafond,
                          par_regime=par_regime)
