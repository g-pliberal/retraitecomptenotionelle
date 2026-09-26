"""Liquider chaque régime (docs/architecture.md, § 7.3).

Chaque régime liquide sa pension sous ses propres règles, sur ce que le
relevé lui a acquis :

* EN ANNUITÉS : un salaire de référence (:func:`salaire_de_reference`) ou un
  forfait, un taux — le taux plein, décote et surcote faites
  (:func:`decote_opposable`, :func:`trimestres_de_decote`,
  :func:`coefficient_surcote_datee`) —, et une durée proratisée
  (:func:`duree_proratisation`), plafonnée au taux maximum ;
* EN POINTS : les points à la valeur de service de la liquidation
  (:func:`valeur_du_point`), le rendement pour les années sans prix d'achat,
  le forfait d'un régime mixte ; l'abattement avant le taux plein et la
  majoration après (:func:`abattement_points`, :func:`surcote_points`) ; le
  capital du RAFP sous son seuil.

Un régime que la coordination réunit à celui qui lui succède est liquidé par
lui, sur leurs années réunies. L'étape dit aussi ce que l'étape suivante lit
pour compléter : pour chaque régime qui porte le minimum contributif ou le
minimum garanti, les durées et la condition qui les ouvrent.

Ce qu'elle écrit, :class:`Pensions`, suit son schéma,
``data/reference/etapes/liquider_chaque_regime.yaml``. Les tables sont celles
que le moteur du scénario 1 tient, jusqu'aux fiches (phase 6). Son jumeau est
``moteur/js/droit/liquider.js``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from ..calendrier import DateMois, en_mois
from ..carriere import salaire_moyen_annuel
from ..donnees.chargement import Fiabilite
from .. import revalorisation
from . import acquerir, coordonner, ouvrir
from .commun import PensionRegime, derniere_annee
from .ouvrir import TRIMESTRES_DECOTE_MILITAIRE

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..donnees.regimes import PeriodeRegime
    from ..scenarios.actuel import ScenarioActuel
    from .liquidation import Contexte
    from .ouvrir import Ouverture
    from .releve import Releve

#: La version du schéma de l'étape que :meth:`Pensions.donnees` suit.
SCHEMA_VERSION = 1

#: Trimestres dont l'âge d'annulation de la décote est minoré, pour ouvrir le
#: minimum garanti à qui n'a pas la durée, selon l'année où l'âge d'ouverture
#: du droit est atteint : tableau de l'article 3 du décret n° 2010-1744 du
#: 30 décembre 2010, pris pour le IV de l'article 45 de la loi n° 2010-1330.
#: Aucun à partir de 2016.
MINORATION_AGE_MINIMUM_GARANTI = {2011: 9, 2012: 7, 2013: 5, 2014: 3, 2015: 1}

#: Coefficients d'anticipation de l'Agirc-Arrco, sous leur forme de barème.
#: Le régime n'applique pas la décote du régime de base : il a ses propres
#: coefficients, publiés en deux tables — l'une indexée sur les trimestres
#: manquants, l'autre sur l'âge — dont il retient la plus favorable.
#:
#: Les deux tables descendent par paliers réguliers, et c'est cette régularité
#: qu'on écrit ici plutôt que quarante lignes de barème : un point de
#: pourcentage par trimestre jusqu'à douze, un point et quart jusqu'à vingt,
#: un point trois quarts au-delà — ce dernier palier n'existant que dans la
#: table des âges, qui descend jusqu'à 0,43 pour dix ans d'anticipation.
_PALIERS_ANTICIPATION: tuple[tuple[int, float], ...] = (
    (12, 0.01), (20, 0.0125), (40, 0.0175),
)

#: Les barèmes de minoration qui comptent des ANNÉES manquantes et non des
#: trimestres : les deux de l'IRCEC (RAAP, RACD, RACL) et celui de la CAVOM,
#: qui est le second sous un autre nom. Voir ``_abattement_ircec``.
_ABATTEMENTS_IRCEC = ("ircec", "ircec_age_seul", "cavom")

#: Ceux des précédents que seul l'âge annule : la durée d'assurance n'y ouvre
#: pas le taux plein.
_ABATTEMENTS_PAR_ANNEE_AGE_SEUL = ("ircec_age_seul", "cavom")

#: Dernière ligne de la table des âges : dix ans d'anticipation. Au-delà, le
#: barème ne descend plus.
_COEFFICIENT_ANTICIPATION_PLANCHER = 0.43

#: Majoration par trimestre ENTIER écoulé entre l'âge du taux plein et la
#: liquidation — le 1° du IV de l'article 16 de l'arrêté du 30 décembre 1970,
#: « 0,75 % par trimestre entier écoulé entre le soixante-cinquième
#: anniversaire de l'assuré et la date d'entrée en jouissance de la pension ».
#: Aucune condition de durée ne s'y attache : c'est le temps qui compte.
_SURCOTE_IRCANTEC_AGE = 0.0075

#: Majoration par trimestre COTISÉ au-delà de la durée requise, entre l'âge
#: légal et l'âge du taux plein — le 2° du même IV, « 0,625 % par trimestre
#: accompli ». Son assiette est celle de la surcote du régime général, bornée
#: en haut par l'âge où le 1° prend le relais : « en aucun cas une même période
#: ne peut donner lieu à la fois à l'attribution de la majoration prévue au 1°
#: et à celle prévue au 2° ».
_SURCOTE_IRCANTEC_DUREE = 0.00625


def _sans_zeros_inutiles(valeur: float, decimales: int) -> str:
    """Un nombre à ``decimales`` chiffres au plus, sans les zéros de fin.

    Certaines valeurs de service sont des barèmes PUBLIÉS à quatre décimales —
    1,8026 € à l'Agirc-Arrco —, d'autres sont CALCULÉES et en portent bien
    davantage. Les tronquer toutes à quatre inventait un écart de vingt-huit
    centimes entre la formule affichée et le montant de la ligne ; les afficher
    toutes à six aurait inventé, à l'inverse, une précision que le barème n'a
    pas. Chacune est donc écrite à la précision qu'elle porte.
    """
    return f"{valeur:.{decimales}f}".rstrip("0").rstrip(".")


def _formule_points(termes: list[str], coefficient: float) -> str:
    """La formule d'un régime en points, telle qu'on doit pouvoir la refaire.

    Le coefficient multiplie la SOMME des termes, il ne s'y ajoute pas : il
    vient donc après, et la somme prend ses parenthèses dès qu'elle en compte
    plusieurs. Sans lui, la formule affichée ne retrouvait pas le montant de la
    ligne — à dix ans d'anticipation elle en donnait 2,3 fois trop, sans que
    rien à l'écran ne dise pourquoi.

    Il se nomme par ce qu'il fait : « coefficient d'anticipation » quand il
    retire, « coefficient de majoration » quand il ajoute. Un seul régime
    ajoute — l'Ircantec, dont le IV de l'article 16 de l'arrêté du 30 décembre
    1970 majore les points d'une liquidation tardive —, et l'appeler
    « anticipation » aurait écrit le contraire de ce qu'il vaut.
    """
    formule = " + ".join(termes) or "aucun droit"
    if coefficient == 1.0 or not termes:
        return formule
    if len(termes) > 1:
        formule = f"({formule})"
    nom = "de majoration" if coefficient > 1.0 else "d'anticipation"
    return f"{formule} × coefficient {nom} {coefficient:.4f}"


def _au_trimestre_superieur(trimestres: float) -> int:
    """Nombre de trimestres arrondi à l'entier supérieur, jamais négatif.

    C'est la règle de l'article R. 351-27 pour la décote, et celle que la
    caisse illustre dans son exemple pour les coefficients d'anticipation : un
    assuré à qui il manque trois ans et dix mois se voit opposer seize
    trimestres, pas quinze. La tolérance de 10⁻³ évite qu'un flottant tout juste
    au-dessus d'un entier n'en fasse compter un de plus.
    """
    return max(0, -(-int(round(trimestres * 1000)) // 1000))


#: RAFP — barème actuariel de modulation de la valeur de service, par âge
#: ENTIER à la date d'effet : « la valeur de service du point est modulée en
#: fonction de l'âge de liquidation de la retraite additionnelle » (décret
#: n° 2004-569, art. 8). Tableau publié par l'ERAFP, « Valeurs des
#: coefficients de majoration » ; 1,00 jusqu'à 62 ans, 1,80 dès 75.
_MAJORATION_RAFP = {
    62: 1.00, 63: 1.04, 64: 1.08, 65: 1.12, 66: 1.17, 67: 1.22, 68: 1.28,
    69: 1.33, 70: 1.40, 71: 1.47, 72: 1.54, 73: 1.62, 74: 1.71, 75: 1.80,
}

#: RAFP — coefficients de conversion en capital, par âge à la date d'effet,
#: pour les prestations servies depuis le 1er janvier 2022 (barème de l'ERAFP).
#: Le document les interpole au MOIS entre deux âges entiers : 62 ans et 7
#: mois valent 27,11 + (26,34 − 27,11) × 7 / 12.
_CONVERSION_CAPITAL_RAFP = {
    62: 27.11, 63: 26.34, 64: 25.57, 65: 24.79, 66: 24.02, 67: 23.25,
    68: 22.47, 69: 21.70, 70: 20.92, 71: 20.15, 72: 19.37, 73: 18.61,
    74: 17.84, 75: 17.07,
}


def _majoration_rafp(age_liquidation: float) -> float:
    """Coefficient de majoration du RAFP à l'âge de liquidation."""
    return _MAJORATION_RAFP[min(75, max(62, int(age_liquidation + 1e-9)))]


def _conversion_capital_rafp(age_liquidation: float) -> float:
    """Coefficient de conversion en capital du RAFP, interpolé au mois."""
    age = min(75.0, max(62.0, age_liquidation))
    ans = int(age + 1e-9)
    if ans >= 75:
        return _CONVERSION_CAPITAL_RAFP[75]
    mois = int((age - ans) * 12 + 1e-6)
    bas = _CONVERSION_CAPITAL_RAFP[ans]
    return bas + (_CONVERSION_CAPITAL_RAFP[ans + 1] - bas) * mois / 12


def _coefficient_anticipation(trimestres_manquants: float,
                              maximum: int) -> float | None:
    """Coefficient d'anticipation Agirc-Arrco pour un nombre de trimestres.

    ``maximum`` est la dernière ligne du barème : vingt trimestres pour la
    table des trimestres manquants, quarante pour celle des âges. Au-delà, la
    table ne dit rien et ``None`` est renvoyé — la prolonger reviendrait à
    inventer un coefficient plus favorable que celui de l'autre table, alors
    que le régime retient la plus avantageuse des deux.

    Les trimestres sont comptés en ENTIERS ARRONDIS AU SUPÉRIEUR : le barème
    est un escalier, et un assuré à qui il manque trois ans et dix mois se voit
    opposer seize trimestres, pas quinze. C'est la lecture que la caisse
    illustre elle-même dans son exemple.
    """
    manquants = _au_trimestre_superieur(trimestres_manquants)
    if manquants <= 0:
        return 1.0
    if manquants > maximum:
        return None
    coefficient = 1.0
    precedent = 0
    for borne, pas in _PALIERS_ANTICIPATION:
        tranche = min(manquants, borne) - precedent
        if tranche > 0:
            coefficient -= tranche * pas
        precedent = borne
        if manquants <= borne:
            break
    return max(0.0, coefficient)

#: Barèmes de décote lus dans une table, et non dans la fiche du régime : le
#: coefficient et l'âge d'annulation y montent en charge à l'année de
#: liquidation. ``regimes_speciaux_age_fixe`` prend le coefficient de la table
#: des régimes spéciaux mais garde l'âge d'annulation écrit dans la fiche.
_BAREMES_DECOTE_EN_TABLE = frozenset(
    {"fonction_publique", "regimes_speciaux", "regimes_speciaux_age_fixe"}
)


@dataclass(frozen=True)
class EligibleMinimum:
    """Régime de base susceptible d'être porté au minimum contributif.

    Quatre grandeurs, et pas une seule, parce que le droit en demande quatre :
    la pension à relever, les deux fractions de durée qui proratisent le
    montant de base et sa majoration, la condition de taux plein qui ouvre le
    droit, et le coefficient de surcote qu'il faut retirer avant de comparer
    au plancher puis rendre après.
    """

    #: Indice de la pension dans :attr:`Pensions.regimes`.
    indice: int
    #: Durée d'assurance acquise dans le régime / durée requise, bornée à 1.
    prorata_assurance: float
    #: Durée COTISÉE acquise dans le régime / durée requise, bornée à 1.
    prorata_cotise: float
    #: La pension est-elle liquidée au taux plein dans ce régime ?
    taux_plein: bool
    #: Coefficient de surcote déjà incorporé au montant de la pension.
    surcote: float = 1.0


@dataclass(frozen=True)
class EligibleMinimumGaranti:
    """Régime de la fonction publique susceptible d'atteindre son plancher."""

    #: Indice de la pension dans :attr:`Pensions.regimes`.
    indice: int
    #: Durée de services acquise dans le régime, en trimestres.
    trimestres_services: int
    #: La pension est-elle liquidée au taux plein, ou l'assuré atteignait-il
    #: l'âge d'ouverture de ses droits avant 2011 ?
    ouvert: bool
    #: Durée des services et bonifications qui ouvre le pourcentage maximum :
    #: le d de L. 17 y rapporte le minimum d'une pension de moins de quinze
    #: ans. ``None`` garde le c, un quinzième de 57,5 % par année.
    duree_maximum: int | None = None


@dataclass(frozen=True)
class Pensions:
    """Ce que l'étape « liquider chaque régime » écrit."""

    #: La personne dont les pensions sont liquidées.
    personne: str
    #: La pension de chaque régime qui liquide, dans l'ordre du relevé.
    regimes: tuple[PensionRegime, ...]
    #: Les régimes de base qui portent le minimum contributif.
    minimum: tuple[EligibleMinimum, ...]
    #: Les régimes de la fonction publique qui portent le minimum garanti.
    garanti: tuple[EligibleMinimumGaranti, ...]
    #: La plus longue des durées requises des régimes en annuités.
    requis: int
    #: Le plus haut des taux de liquidation des régimes en annuités.
    taux: float
    fiabilite: Fiabilite

    def donnees(self) -> dict:
        """Les pensions, telles que le schéma de l'étape les décrit."""
        regimes = [{"regime": p.regime, "montant": p.montant, "calcul": p.type_calcul,
                    "detail": p.detail, "fiabilite": p.fiabilite.name.lower()}
                   for p in self.regimes]
        for eligible in self.minimum:
            regimes[eligible.indice]["minimum"] = {
                "prorata_assurance": eligible.prorata_assurance,
                "prorata_cotise": eligible.prorata_cotise,
                "taux_plein": eligible.taux_plein,
                "surcote": eligible.surcote,
            }
        for eligible in self.garanti:
            regimes[eligible.indice]["garanti"] = {
                "trimestres_services": eligible.trimestres_services,
                "ouvert": eligible.ouvert,
                "duree_maximum": eligible.duree_maximum,
            }
        return {"schema_version": SCHEMA_VERSION, "personne": self.personne,
                "regimes": regimes, "requis": self.requis, "taux": self.taux,
                "fiabilite": self.fiabilite.name.lower()}


def liquider_chaque_regime(moteur: ScenarioActuel, releve: Releve, ouverture: Ouverture,
                           contexte: Contexte | None = None) -> Pensions:
    """La pension de chaque régime où le relevé porte un droit.

    La durée requise de référence, que l'étape « ouvrir le droit » a lue, est
    celle que l'abattement des complémentaires oppose. Le contexte dit ce que
    le calcul neutralise : la décote, la surcote et l'abattement liés à l'âge
    pour valoriser des droits acquis ; l'AVPF pour en mesurer l'apport.
    """
    carriere = releve.carriere
    durees, droits = releve.durees, releve.droits
    annee_liquidation = carriere.annee_liquidation
    age_liquidation = carriere.age_liquidation or 0.0
    trimestres = durees.trimestres
    requis_reference = ouverture.requis
    ignorer_penalite_age = contexte is not None and contexte.neutralise("decote_surcote")
    avpf = contexte is None or not contexte.neutralise("avpf")
    codes = droits.codes
    groupes = releve.groupes

    pensions: list[PensionRegime] = []
    fiabilite_globale = Fiabilite.CERTIFIEE
    trimestres_requis = 0
    taux_retenu = 0.0
    #: Régimes de base qui portent le minimum contributif : indice dans
    #: ``pensions``, prorata de durée d'assurance, prorata de durée
    #: COTISÉE, et condition de taux plein remplie ou non.
    eligibles_minimum: list[EligibleMinimum] = []
    #: Régimes de la fonction publique qui portent le minimum garanti.
    eligibles_garanti: list[EligibleMinimumGaranti] = []

    # Ce que les étapes de l'acquisition ont écrit, sous les noms que la
    # liquidation lit.
    cumul_cotisations = droits.cumul_cotisations
    points_acquis = droits.points_acquis
    fiabilite_points = droits.fiabilite_points
    gratuits_attribues = droits.gratuits
    trimestres_par_regime = durees.trimestres_par_regime
    bonifications_par_regime = durees.bonifications_par_regime
    cumul_plafonne = durees.cumul_plafonne
    majoration_enfants = durees.enfants

    for code in codes:
        cumul = cumul_cotisations.get(code, 0.0)
        regime = moteur.catalogue[code]
        periode = regime.periode(min(annee_liquidation, derniere_annee(regime)))
        if periode is None:
            continue
        fiabilite_globale = min(fiabilite_globale, regime.fiabilite)
        membres = groupes.get(code, (code,))
        if membres[0] != code:
            # Liquidé par le régime qui lui a succédé.
            continue

        if periode.type_calcul in ("points", "mixte"):
            montant = 0.0
            fiabilite_regime = regime.fiabilite
            details = []

            points = points_acquis.get(code, 0.0)
            # BARÈME DU TRIMESTRE : la pension minière est la durée, majorée
            # du coefficient de l'article 131-1, multipliée par la valeur du
            # trimestre de la date d'effet — l'une et l'autre lues dans
            # `bareme_trimestre_<nom>.csv`. La fiche ne portait que la
            # seconde, et par les prix.
            trimestre = (
                moteur.baremes_trimestre.valeurs(
                    periode.bareme_trimestre, carriere.date_liquidation)
                if points and periode.bareme_trimestre else None
            )
            if trimestre is not None:
                valeur_trimestre, coefficient_duree, fiabilite_trimestre = trimestre
                montant += points * coefficient_duree * valeur_trimestre
                fiabilite_regime = min(
                    fiabilite_regime, fiabilite_trimestre, fiabilite_points[code]
                )
                details.append(
                    f"{points:,.2f} trimestres × coefficient de majoration de "
                    f"la durée {coefficient_duree:.3f} × valeur du trimestre "
                    f"{_sans_zeros_inutiles(valeur_trimestre, 2)} €"
                )
            elif points:
                valeur = valeur_du_point(moteur, 
                    periode.points_de or code, annee_liquidation
                )
                if valeur is None and periode.valeur_point_euros is not None:
                    # Valeur de service écrite dans la fiche : le régime
                    # dont la caisse est seule à la publier n'a rien de
                    # certifiable dans `valeurs_point.csv`, et retombait
                    # donc sur le rendement instantané.
                    valeur = (
                        valeur_point_fiche(moteur, periode, annee_liquidation),
                        Fiabilite.MOYENNE,
                    )
                if valeur is not None:
                    service, fiabilite_service = valeur
                    # COEFFICIENT DE DURÉE de la proportionnelle agricole :
                    # la pension vaut « points × valeur du point × 37,5 /
                    # durée requise en années ». Il est neutre pour les
                    # générations qui devaient 37,5 ans, et retire un
                    # huitième à celles qui en doivent 43 — sans lui, le
                    # maximum du barème cesse de valoir ce que le code lui
                    # fait valoir.
                    coefficient_duree = 1.0
                    if periode.bareme_points == "msa_proportionnelle":
                        requis, fiabilite_duree = ouvrir.duree_requise(moteur, 
                            periode, carriere
                        )
                        if fiabilite_duree is not None:
                            fiabilite_regime = min(
                                fiabilite_regime, fiabilite_duree
                            )
                        if requis > 0:
                            coefficient_duree = 37.5 / (requis / 4.0)
                    montant += points * service * coefficient_duree
                    fiabilite_regime = min(
                        fiabilite_regime, fiabilite_service, fiabilite_points[code]
                    )
                    gratuits = gratuits_attribues.get(code, (0.0, 0))[0]
                    details.append(
                        f"{points:,.2f} points × valeur de service "
                        f"{_sans_zeros_inutiles(service, 6)} €"
                        + ("" if coefficient_duree == 1.0
                           else f" × {coefficient_duree:.4f}")
                        # Les points gratuits sont DANS le compte : la
                        # formule se refait sur le total, et le lecteur
                        # voit d'où vient ce qu'il n'a pas cotisé.
                        + ("" if not gratuits
                           else f" (dont {gratuits:,.2f} points gratuits)")
                    )

            # RÉGIME MIXTE : une part forfaitaire s'ajoute aux points. Le
            # régime agricole en est le seul exemple — sa retraite
            # forfaitaire vaut l'allocation aux vieux travailleurs salariés
            # pour une carrière complète, et se proratise sur la durée
            # (L. 732-24). Le moteur traitait `mixte` comme un synonyme de
            # `points` et ne la servait pas du tout.
            if (periode.type_calcul == "mixte"
                    and periode.pension_forfaitaire_annuelle is not None):
                requis, _ = ouvrir.duree_requise(moteur, periode, carriere)
                proratisation, fiabilite_prorata = duree_proratisation(moteur, 
                    periode, carriere, requis
                )
                if fiabilite_prorata is not None:
                    fiabilite_regime = min(fiabilite_regime, fiabilite_prorata)
                acquis = min(trimestres_par_regime.get(code, 0), proratisation)
                if proratisation > 0 and acquis > 0:
                    forfait = (
                        periode.pension_forfaitaire_annuelle
                        * moteur.macro.coefficient_prix(
                            periode.pension_forfaitaire_annee or annee_liquidation,
                            annee_liquidation,
                        )
                        * acquis / proratisation
                    )
                    montant += forfait
                    details.append(
                        f"forfait {forfait:,.2f} € ({acquis}/{proratisation})"
                    )

            # Années sans prix d'achat connu : le rendement instantané prend
            # le relais, régime par régime et année par année. Il fait
            # partie du barème du point — c'est le rapport de la valeur de
            # service au prix d'achat —, et une fiche qui emprunte ce barème
            # (`points_de`) emprunte donc aussi le rendement : sans quoi elle
            # ne trouvait aucune ligne sous son propre code, et sa pension
            # tombait à zéro sans rien dire.
            if cumul:
                rendement, fiabilite_rendement = moteur.rendements.rendement(
                    periode.points_de or code,
                    min(annee_liquidation, derniere_annee(regime)),
                )
                montant += cumul * rendement
                fiabilite_regime = min(fiabilite_regime, fiabilite_rendement)
                details.append(
                    f"cotisations revalorisées {cumul:,.0f} € "
                    f"× rendement {rendement:.2%}"
                )

            fiabilite_globale = min(fiabilite_globale, fiabilite_regime)
            montant_brut = montant
            abattement = 1.0
            if not ignorer_penalite_age:
                # Le coefficient d'anticipation multiplie le montant : sans
                # lui, la formule affichée ne le retrouve pas — à dix ans
                # d'anticipation elle en donnait deux fois trop, sans que
                # rien à l'écran ne dise pourquoi.
                abattement = abattement_points(moteur, 
                    periode, carriere, trimestres, requis_reference,
                    age_liquidation, annee_liquidation,
                    trimestres_par_regime.get(code, 0),
                )
                montant *= abattement
            detail = _formule_points(details, abattement)
            # Les années qu'aucun prix d'achat ne couvre encore passent par
            # le rendement : le seuil se compare donc aux points que vaut
            # TOUT le montant, à la valeur de service de la liquidation.
            points_totaux = points
            if periode.capital_seuil_points is not None:
                valeur = valeur_du_point(moteur, 
                    periode.points_de or code, annee_liquidation)
                if valeur is not None and valeur[0] > 0:
                    points_totaux = montant_brut / valeur[0]
            if (periode.capital_seuil_points is not None
                    and 0 < points_totaux < periode.capital_seuil_points):
                # SOUS LE SEUIL, UN CAPITAL. Le RAFP ne sert de rente qu'à
                # partir de 5 125 points ; en deçà, il verse une fois
                # « points × coefficient de majoration × valeur de service ×
                # coefficient de conversion en capital » (décret
                # n° 2004-569, art. 9). Le montant annuel reste celui de la
                # rente dont le capital est l'équivalent actuariel : c'est
                # lui que les comparaisons annuelles savent lire.
                capital = montant * _conversion_capital_rafp(age_liquidation)
                detail += (
                    f" ; versé en capital, {capital:,.0f} € en une fois "
                    f"(moins de {periode.capital_seuil_points:,.0f} points)"
                )
            pensions.append(PensionRegime(
                regime=code, montant=montant, type_calcul=periode.type_calcul,
                detail=detail,
                fiabilite=fiabilite_regime,
            ))
            continue

        # Régimes en annuités — et régimes FORFAITAIRES, dont la pension ne
        # dépend pas du revenu mais de la seule durée. Le second cas se
        # traite comme le premier en remplaçant le salaire de référence par
        # le montant forfaitaire : c'est bien un `montant × taux × durée /
        # durée requise`, à ceci près que le montant est le même pour tous.
        # Faute de ce montant, la fiche retombait sur la moyenne des
        # revenus, c'est-à-dire sur un taux de remplacement de 100 %.
        plafonner = periode.assiette in ("plafonnee", "tranche_1", "tranche_a")
        if periode.pension_forfaitaire_annuelle is not None:
            salaire_reference = (
                periode.pension_forfaitaire_annuelle
                * moteur.macro.coefficient_prix(
                    periode.pension_forfaitaire_annee or annee_liquidation,
                    annee_liquidation,
                )
            )
        else:
            salaire_reference = salaire_de_reference(moteur, 
                code, carriere, periode, annee_liquidation, plafonner,
                carriere.annee_naissance, avpf, membres,
                enfants_majores=(carriere.nombre_enfants
                                 if majoration_enfants is not None else 0),
            )
        requis, fiabilite_duree = ouvrir.duree_requise(moteur, periode, carriere)
        if fiabilite_duree is not None:
            fiabilite_globale = min(fiabilite_globale, fiabilite_duree)
        trimestres_requis = max(trimestres_requis, requis)
        # Le dénominateur de la PRORATISATION n'est pas la durée requise :
        # l'article R. 351-6 en fixe une autre, plus courte pour les
        # générations d'avant 1949. Confondre les deux retirait à un assuré
        # né en 1945 avec 156 trimestres les 2,5 % que 156/160 lui coûte,
        # là où 156/154 lui donne le coefficient plein.
        proratisation, fiabilite_proratisation = duree_proratisation(moteur, 
            periode, carriere, requis
        )
        if fiabilite_proratisation is not None:
            fiabilite_globale = min(fiabilite_globale, fiabilite_proratisation)
        # Le numérateur n'est pas le même selon le régime : services et
        # bonifications dans la fonction publique (L. 13), durée
        # d'assurance partout ailleurs (R. 351-1).
        # Le plafond est la durée requise, que les BONIFICATIONS seules
        # peuvent dépasser, et dans la limite d'un taux : « Le pourcentage
        # maximum fixé à l'article L 13 peut-être augmenté de cinq points du
        # chef des bonifications » (L. 12 CPCMR). Le module plafonnait
        # services et bonifications ensemble à la durée requise, et servait
        # 75 % à une mère de trois enfants à qui le droit en doit près de 80.
        bonifications = (
            sum(bonifications_par_regime.get(m, 0) for m in membres)
            if periode.taux_maximum_bonifie and periode.taux_plein else 0
        )
        # Les membres d'un groupe liquidé ensemble se somment ANNÉE PAR
        # ANNÉE : deux activités cumulées dans deux régimes alignés ne
        # valident pas huit trimestres la même année.
        trimestres_regime = min(
            cumul_plafonne(
                "services"
                if moteur.catalogue[code].famille == "fonction_publique"
                else "assurance",
                membres,
            ),
            proratisation + bonifications,
        )
        #: Rapport des trimestres liquidables à la durée requise, borné au
        #: taux maximum — 80/75 avec des bonifications, un sans elles.
        rapport_maximum = (periode.taux_maximum_bonifie / periode.taux_plein
                           if bonifications else 1.0)
        if (periode.duree_maximum_avant_age is not None
                and periode.duree_maximum_avant_age_trimestres is not None
                and age_liquidation < periode.duree_maximum_avant_age):
            # DURÉE LIQUIDABLE PLAFONNÉE PAR L'ÂGE. L'article R. 13 du code
            # des pensions de retraite des marins : « le maximum des
            # annuités liquidables dans les pensions d'ancienneté dont la
            # liquidation est demandée avant cinquante-cinq ans est fixé à
            # vingt-cinq annuités ». Un marin parti à cinquante ans avec
            # trente ans de mer touche 50 % du salaire forfaitaire, non
            # 60 %. C'est la seule règle du catalogue où l'ÂGE borne la
            # durée, et non l'inverse.
            # Levé « au profit d'un marin âgé d'au moins cinquante-deux ans
            # et demi, réunissant trente-sept annuités et demie de
            # services » : le même alinéa, b).
            levee = (periode.duree_maximum_levee_age is not None
                     and periode.duree_maximum_levee_trimestres is not None
                     and age_liquidation >= periode.duree_maximum_levee_age
                     and trimestres_regime
                     >= periode.duree_maximum_levee_trimestres)
            if not levee:
                trimestres_regime = min(
                    trimestres_regime,
                    periode.duree_maximum_avant_age_trimestres,
                )

        taux = periode.taux_plein or 0.5
        #: Part du taux qui vient de la surcote. Le minimum contributif se
        #: compare à la pension AVANT surcote : il faut donc pouvoir la
        #: retirer, puis la rendre.
        coefficient_surcote = 1.0
        #: Trimestres de décote effectivement retenus : la condition
        #: d'ouverture du minimum garanti en dépend.
        trimestres_decote = 0.0
        #: Âge d'annulation de la décote, que l'ouverture transitoire du
        #: minimum garanti minore.
        age_annulation: float | None = None
        if not ignorer_penalite_age:
            decote, age_annulation, fiabilite_decote = decote_opposable(moteur, 
                periode, carriere, annee_liquidation
            )
            trimestres_decote = trimestres_de_decote(moteur, 
                periode, carriere, trimestres, requis, age_liquidation,
                age_annulation
            )
            if decote and trimestres_decote > 0:
                # Les régimes sans décote (fonction publique avant 2004,
                # régimes spéciaux avant 2008) ne subissent que la
                # proratisation : leur `decote_par_trimestre` est nul.
                if fiabilite_decote is not None:
                    fiabilite_globale = min(fiabilite_globale, fiabilite_decote)
                taux *= max(0.0, 1.0 - decote * trimestres_decote)
            # La surcote ne récompense que les trimestres COTISÉS APRÈS
            # l'âge légal ET au-delà de la durée requise. Les compter tous
            # majorait la pension de qui a commencé tôt sans jamais
            # travailler au-delà de l'âge d'ouverture.
            supplementaires = max(0, trimestres - requis)
            # La surcote se compte depuis l'âge légal DE DROIT COMMUN, même
            # pour un emploi classé, et le militaire n'en a aucune : le III
            # de l'article L. 14 ne la donne qu'au « fonctionnaire civil ».
            age_ouverture = ouvrir.age_surcote(moteur, periode, carriere)
            if (periode.surcote_par_trimestre and supplementaires > 0
                    and age_liquidation >= age_ouverture
                    and ouvrir.droit_militaire(moteur, periode, carriere) is None):
                if periode.surcote_bareme:
                    # Barème DATÉ : chaque trimestre civil de surcote au
                    # taux en vigueur quand il a été accompli, depuis le
                    # trimestre qui suit l'âge légal (D. 351-1-4).
                    coefficient_surcote, fiabilite_surcote = (
                        coefficient_surcote_datee(moteur, 
                            periode, carriere, trimestres, requis,
                            supplementaires, age_ouverture,
                        )
                    )
                    if fiabilite_surcote is not None:
                        fiabilite_globale = min(fiabilite_globale, fiabilite_surcote)
                else:
                    supplementaires = min(
                        supplementaires,
                        _trimestres_cotises_apres(
                            carriere, age_ouverture, annee_liquidation
                        ),
                    )
                    if supplementaires > 0:
                        coefficient_surcote = (
                            1.0 + periode.surcote_par_trimestre * supplementaires
                        )
                taux *= coefficient_surcote

        taux_retenu = max(taux_retenu, taux)
        prorata = min(trimestres_regime / proratisation, rapport_maximum)
        montant = salaire_reference * taux * prorata
        if "minimum_contributif" in periode.avantages_non_contributifs:
            # Le minimum ne relève que les régimes de base qui le portent,
            # et au prorata de la durée acquise DANS CE régime — durée
            # d'assurance pour le montant de base, durée COTISÉE pour la
            # majoration au titre des périodes cotisées.
            #
            # Et il ne relève que les pensions LIQUIDÉES AU TAUX PLEIN
            # (L. 351-10) : durée requise atteinte, ou âge d'annulation de
            # la décote atteint. Le servir à un assuré décoté, comme le
            # faisait ce module, revenait à faire garantir par le système
            # actuel un départ que le droit sanctionne — et gonflait
            # l'étalon de 20 % sur les petites pensions parties tôt.
            # Le minimum se proratise « dans les mêmes conditions que la
            # pension » : c'est donc la durée de proratisation, et non la
            # durée requise, qui fait office ici aussi.
            cotises_regime = min(
                cumul_plafonne("cotises", membres),
                proratisation,
            )
            eligibles_minimum.append(EligibleMinimum(
                indice=len(pensions),
                prorata_assurance=prorata,
                prorata_cotise=cotises_regime / proratisation,
                taux_plein=(
                    trimestres >= requis
                    or age_liquidation >= ouvrir.age_taux_plein(moteur, periode, carriere)
                ),
                surcote=coefficient_surcote,
            ))
        if "minimum_garanti" in periode.avantages_non_contributifs:
            # Depuis la loi du 9 novembre 2010, le minimum garanti n'est dû
            # qu'au taux plein — décote nulle, ou durée requise atteinte.
            # Les assurés qui atteignaient l'âge d'ouverture de leurs
            # droits avant 2011 gardent le droit inconditionnel, et le c
            # de L. 17 sous quinze ans de services ; les autres ont le d,
            # que la même loi a créé (voir `MinimumGaranti.montant`).
            age_ouverture = ouvrir.age_ouverture(moteur, periode, carriere)
            ancien_droit = carriere.annee_naissance + age_ouverture < 2011
            # L'âge qui ouvre le minimum sans la durée est l'âge
            # d'annulation de la décote, MINORÉ à titre transitoire selon
            # l'année où l'âge d'ouverture est atteint (IV de l'article 45
            # de la loi, article 3 du décret n° 2010-1744) : le modèle le
            # refusait neuf trimestres trop longtemps à qui ouvrait ses
            # droits en 2011.
            fonction_publique = moteur.catalogue[code].famille == "fonction_publique"
            minoration = MINORATION_AGE_MINIMUM_GARANTI.get(
                carriere.date_naissance.plus_mois(en_mois(age_ouverture)).annee, 0
            ) if fonction_publique else 0
            eligibles_garanti.append(EligibleMinimumGaranti(
                indice=len(pensions),
                trimestres_services=cumul_plafonne("services", membres),
                ouvert=(
                    ancien_droit
                    or trimestres_decote <= 0
                    or trimestres >= requis
                    or (minoration > 0 and age_annulation is not None
                        and age_liquidation + 1e-9
                        >= age_annulation - minoration / 4.0)
                ),
                # Le d et la minoration ne valent que pour la fonction
                # publique : la Banque de France a les siens depuis son
                # décret de 2012, que sa fiche ne date pas.
                duree_maximum=(
                    proratisation if fonction_publique and not ancien_droit
                    else None
                ),
            ))
        pensions.append(PensionRegime(
            regime=code, montant=montant, type_calcul="annuites",
            detail=(
                f"{'forfait' if periode.pension_forfaitaire_annuelle is not None else 'SR'} "
                # Salaire de référence au centime et taux au millième : à
                # l'euro et au centième, refaire « SR × taux × durée »
                # ratait le montant de 1,20 € sur un régime spécial, le
                # taux arrondi pesant à lui seul 0,89 €.
                f"{salaire_reference:,.2f} € × taux {taux:.3%} "
                f"× {trimestres_regime}/{proratisation}"
                + (f", taux maximum {periode.taux_maximum_bonifie:.0%} atteint"
                   if trimestres_regime / proratisation > rapport_maximum else "")
                # La succession est DITE : sans elle, le lecteur cherche
                # la ligne de la CANCAVA et ne la trouve pas.
                + ("" if len(membres) == 1 else
                   f", {len(membres)} caisses liquidées ensemble "
                   f"({', '.join(membres[1:])} puis {membres[0]})")
            ),
            fiabilite=min(moteur.catalogue[m].fiabilite for m in membres),
        ))

    return Pensions(
        personne=carriere.personne,
        regimes=tuple(pensions),
        minimum=tuple(eligibles_minimum),
        garanti=tuple(eligibles_garanti),
        requis=trimestres_requis,
        taux=taux_retenu,
        fiabilite=fiabilite_globale,
    )


def valeur_du_point(moteur, code: str,
                    annee_liquidation: int) -> tuple[float, Fiabilite] | None:
    """Ce que vaut, à la liquidation, un point acquis dans ``code``.

    Un régime fermé ne sert plus ses points : ils ont été convertis dans son
    successeur, au coefficient que l'accord de fusion a fixé. La méthode
    remonte la chaîne des successions (UNIRS -> Arrco -> Agirc-Arrco,
    Agirc -> Agirc-Arrco, IPACTE et IGRANTE -> Ircantec) en cumulant ces
    coefficients, qui sont LUS dans ``regimes/conversions_points.csv`` et
    non plus déduits d'un rapport de valeurs de service.

    **Les déduire coûtait cher.** Le rapport était pris entre la dernière
    valeur publiée du régime d'origine et la PREMIÈRE du successeur ; or les
    séries ``arrco`` et ``ircantec`` sont rétro-remplies bien avant leur
    fusion, si bien qu'on comparait deux valeurs distantes de quarante ou
    soixante-dix ans. Le point UNIRS ressortait quinze fois trop cher pour
    toute liquidation postérieure à 1998, le point IPACTE cinquante fois
    trop cher au-delà de 2022. Et là même où les deux bornes tombaient
    juste, la valeur du successeur était celle du 31 décembre quand la
    conversion s'opère au 1er janvier : un pour cent de trop peu sur tous
    les points d'avant 2019.

    Quand la chaîne s'arrête — plus de successeur, ou aucun coefficient
    déclaré — la dernière valeur publiée est ramenée en euros de la
    liquidation par l'indice des prix, pris un an plus tôt comme la
    revalorisation du 1er janvier le prend. C'est une approximation, signalée
    comme telle par la fiabilité renvoyée ; c'est surtout un aveu
    d'ignorance, préférable à un coefficient inventé.
    """
    conversion = 1.0
    courant = code
    fiabilite = Fiabilite.CERTIFIEE
    for _ in range(len(moteur.catalogue) + 1):  # garde-fou : jamais de boucle
        derniere = moteur.valeurs_point.derniere_annee_servie(courant)
        if derniere is None:
            return None
        if annee_liquidation <= derniere:
            valeur = moteur.valeurs_point.service(courant, annee_liquidation)
            if valeur is None:
                # Liquidation antérieure au premier barème publié. Symétrique
                # du cas ci-dessous : la première valeur connue est ramenée
                # en euros de la liquidation par l'indice des prix, et la
                # fiabilité tombe pour le dire.
                premiere_connue = moteur.valeurs_point.premiere_annee_servie(courant)
                ancienne = moteur.valeurs_point.service(courant, premiere_connue)
                return (
                    conversion * ancienne[0]
                    * moteur.macro.coefficient_prix(premiere_connue, annee_liquidation),
                    min(fiabilite, ancienne[1], Fiabilite.MOYENNE),
                )
            return conversion * valeur[0], min(fiabilite, valeur[1])

        successeur = (moteur.catalogue[courant].integre_dans
                      if courant in moteur.catalogue else None)
        reprise = (moteur.conversions_points.fusion(courant, successeur)
                   if successeur else None)
        if reprise is None:
            # AVEC UN AN DE RETARD : une valeur revalorisée au 1er janvier
            # l'est des prix de l'année écoulée (L. 161-25, moyenne des
            # douze derniers indices mensuels). La prolonger par les prix de
            # l'année même donnait à la valeur 2026 du point RCO et de la
            # CNAVPL les +1,75 % de l'hypothèse d'inflation, là où la
            # revalorisation de 2026 est de 0,9 %.
            ancienne = moteur.valeurs_point.service(courant, derniere)
            return (
                conversion * ancienne[0]
                * moteur.macro.coefficient_prix(derniere - 1, annee_liquidation - 1),
                min(fiabilite, ancienne[1], Fiabilite.MOYENNE),
            )

        conversion *= reprise.coefficient
        fiabilite = min(fiabilite, reprise.fiabilite)
        courant = successeur
    return None  # pragma: no cover - chaîne de successions cyclique


def assiette_de_reference(moteur, periode: PeriodeRegime, ligne) -> float:
    """La rémunération que ce régime liquide : voir la fonction du même
    nom, et, pour un régime à grille, le salaire forfaitaire de la
    catégorie — le marin liquide « sur le salaire forfaitaire de la
    catégorie dans laquelle il a été classé » (R. 11), non sur sa paie.
    Le forfait est proratisé sur les mois de l'année, comme le revenu.

    Une année RÉTABLIE porte au compte le dernier traitement de l'agent,
    non ce qu'il a perçu cette année-là (voir
    :func:`~retraite_notionnelle.droit.coordonner.retablir`).
    """
    if ligne.revenu_retabli > 0 and periode.assiette != "primes_uniquement":
        return ligne.revenu_retabli
    if periode.assiette_grille:
        forfait_grille = moteur.grilles.forfait(
            periode.assiette_grille, ligne.annee, ligne.revenu_annualise,
            lambda a: salaire_moyen_annuel(moteur.macro, a),
        )
        if forfait_grille is not None:
            return forfait_grille[0] * ligne.fraction_annee
    if periode.assiette_forfaitaire:
        # L'ASSIETTE FORFAITAIRE EST AUSSI LE SALAIRE PORTÉ AU COMPTE. Le
        # régime des cultes liquide aux règles du régime général (L. 382-27),
        # dont le salaire annuel moyen est fait des salaires qui ont porté
        # cotisation — ici le forfait de R. 382-89. La CAVIMAC l'écrit :
        # « Ces salaires correspondent à une base SMIC pour tous les assurés
        # cultuels. » Le moteur prenait le revenu saisi, et servait au
        # ministre déclaré à une fois et demie le salaire moyen une pension
        # de base plus de deux fois trop haute. Le forfait
        # est celui de l'année — 169 heures mensuelles avant 2002, 151,67
        # ensuite —, proratisé sur ses mois.
        annuelle = moteur.catalogue[periode.regime].periode(ligne.annee) or periode
        if annuelle.assiette_repere_smic is not None:
            return (annuelle.assiette_repere_smic
                    * moteur.macro.smic_horaire(ligne.annee) * ligne.fraction_annee)
    return _assiette_de_reference(periode, ligne)


def salaire_de_reference(moteur, code: str, carriere: Carriere,
                         periode: PeriodeRegime,
                         annee_liquidation: int, plafonner: bool,
                         generation: int | None = None,
                         avpf: bool = True,
                         membres: tuple[str, ...] | None = None,
                         enfants_majores: int = 0) -> float:
    """Salaire de référence, exprimé en euros de l'année de liquidation.

    **Il porte sur les seules années passées DANS CE régime** — ou dans
    l'un des ``membres`` de sa chaîne de succession, quand ``code`` liquide
    pour un régime qu'il a absorbé : les années CANCAVA d'un artisan sont
    des années du RSI, puis du régime général, et n'entrent qu'une fois
    dans un seul salaire annuel moyen. Voir
    :func:`~retraite_notionnelle.droit.coordonner.groupes_de_succession`.

    Un régime ne
    liquide que ce qui lui a été déclaré : la pension civile se calcule sur
    le traitement des six derniers mois de service, pas sur le dernier
    salaire d'une carrière poursuivie ailleurs, et le salaire annuel moyen
    du régime général ne retient que les salaires portés à son compte. Sans
    cette condition, un polypensionné passé de la fonction publique au privé
    liquidait sa pension civile sur son salaire privé de fin de carrière —
    et le prorata de durée, lui, restait celui du régime : le modèle
    rapportait une part de carrière publique à une assiette qui ne l'était
    pas.

    Trois autres règles de droit commandent ce calcul, et le modèle les
    applique toutes.

    La première est la **revalorisation des salaires portés au compte** :
    les salaires anciens sont réévalués par les coefficients annuels que
    fixe l'arrêté, et le modèle les LIT au lieu de les reconstituer. Il les
    approchait par « les salaires jusqu'en 1986, les prix depuis », ce qui
    décrit les arrêtés dans les grandes lignes mais ignore leurs
    revalorisations semestrielles, leurs gels, leurs revalorisations
    exceptionnelles et leurs changements de DÉLAI d'application : cette
    approximation sur-revalorisait les salaires anciens de 12 % sur
    quarante ans. La grandeur commande le salaire de référence deux fois
    plutôt qu'une, puisque la moyenne porte sur les N MEILLEURES années et
    que « meilleures » se juge sur des salaires revalorisés.

    La seconde est le **nombre d'années retenues**, que la loi du 22 juillet
    1993 fait passer de dix à vingt-cinq à raison d'une par génération. Le
    lire à l'année de liquidation opposait vingt-cinq années à des assurés
    auxquels la loi n'en a jamais demandé plus de dix — et étendre la
    moyenne aux années les plus faibles ne peut que l'abaisser.

    Le salaire retenu est celui de l'assiette du régime, et pas la
    rémunération entière : la pension civile porte sur le seul traitement
    indiciaire, primes exclues. C'est le paramètre qui commande le taux de
    remplacement d'un fonctionnaire, puisque les primes n'ouvrent de droit
    qu'au RAFP.
    """
    avpf_ouvert = (
        avpf and "avpf" in periode.avantages_non_contributifs
    )
    # Les coefficients des arrêtés ne valent que pour un salaire PORTÉ AU
    # COMPTE. Un régime qui liquide sur le dernier traitement ne porte rien
    # à un compte : lui appliquer les coefficients du régime général serait
    # une erreur de catégorie. Le traitement d'un FONCTIONNAIRE suit le
    # point d'indice — l'agent garde son indice, et c'est le point de
    # l'année du départ qui dit ce que vaut son traitement de l'année
    # d'avant — ; les autres régimes à dernier salaire restent sur les
    # prix, avec la réserve que `docs/limites.md` leur attache.
    porte_au_compte = periode.salaire_reference not in (
        "derniers_6_mois", "dernier_salaire"
    )
    suit_le_point = (
        not porte_au_compte
        and moteur.catalogue[code].famille == "fonction_publique"
    )
    # Le MOIS de la liquidation désigne la circulaire applicable : les
    # arrêtés ne prennent pas tous effet au 1er janvier, et deux d'entre
    # eux portent l'année 2022. Le mois ne vaut que si l'année passée est
    # bien celle de la liquidation — certains appels bornent l'année à la
    # dernière que porte la fiche du régime.
    mois_liquidation = (
        carriere.mois_liquidation
        if (carriere.age_liquidation is not None
            and annee_liquidation == carriere.annee_liquidation)
        else 1
    )

    def revaloriser(perception: int, arrivee: int) -> float:
        if not porte_au_compte:
            if suit_le_point:
                ratio = moteur.minimum_garanti.ratio_point_indice(perception, arrivee)
                if ratio is not None:
                    return ratio
            return moteur.macro.coefficient_revalorisation_salaires(
                perception, arrivee
            )
        return moteur.macro.coefficient_revalorisation_portee_au_compte(
            perception, arrivee, mois_liquidation
        )
    codes_admis = frozenset(membres) if membres else frozenset((code,))
    # LE REVENU D'UNE ANNÉE, TOUTES ACTIVITÉS DU RÉGIME RÉUNIES. Deux
    # activités cumulées qui versent au même régime — ou à deux régimes
    # alignés que la liquidation unique réunit — forment un seul revenu
    # annuel, écrêté UNE fois au plafond : c'est la somme des salaires et
    # revenus d'une même année que la LURA écrête (R. 173-4-4-1, 1°).
    # Une année d'une seule activité n'a qu'un terme, et rien ne bouge.
    par_annee: dict[int, list[float]] = {}
    for ligne in carriere.lignes:
        if ligne.annee >= annee_liquidation:
            continue
        if codes_admis.isdisjoint(coordonner.regimes_de(moteur, 
                ligne, ligne.annee,
                carriere.date_entree(ligne.affiliation),
                revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
                plafond=moteur.macro.plafond_securite_sociale(ligne.annee))):
            continue
        if not ligne.cotise:
            # Assurance vieillesse des parents au foyer : la CNAF cotise
            # sur une assiette forfaitaire égale au SMIC, et ce salaire est
            # PORTÉ AU COMPTE. C'est ce qui la distingue d'une période
            # assimilée, laquelle valide des trimestres sans jamais ajouter
            # de salaire — et c'est ce que le modèle ne faisait pas, alors
            # que le cas type « carrière interrompue » l'annonçait.
            if not (avpf_ouvert and ligne.revenu_avpf > 0):
                continue
            revenu = ligne.revenu_avpf
        else:
            revenu = max(assiette_de_reference(moteur, periode, ligne),
                         acquerir.assiette_minimale(moteur, codes_admis, ligne))
        # TRANCHE DE SALAIRE. Un régime qui liquide TRANCHE PAR TRANCHE —
        # le personnel navigant, dont l'article R. 426-16-1 attribue
        # 1,85 % par annuité à la première et 1,4 % à la seconde — a
        # besoin que son salaire de référence soit celui de SA tranche, et
        # non le salaire entier. Sans quoi les deux périodes simultanées
        # calculeraient le même salaire moyen et la seconde paierait une
        # deuxième fois sur la première.
        #
        # Le découpage ne s'applique qu'aux assiettes dont la borne basse
        # n'est pas nulle : `plafonnee`, `tranche_1` et `tranche_a` partent
        # de zéro et continuent de passer par `plafonner` ci-dessous,
        # exactement comme avant. Aucun régime en annuités du catalogue
        # n'utilisait de tranche à borne basse avant celui-ci : ce bloc ne
        # déplace donc aucun chiffre existant.
        borne_basse, borne_haute = periode.bornes_assiette_en_euros(
            moteur.macro.plafond_securite_sociale(ligne.annee)
            * ligne.fraction_annee
        )
        if borne_basse > 0:
            revenu = max(0.0, min(revenu, borne_haute or revenu) - borne_basse)
        cumul = par_annee.setdefault(ligne.annee, [0.0, 0.0])
        cumul[0] += revenu
        cumul[1] = max(cumul[1], ligne.fraction_annee)

    revenus: list[float] = []
    # Le dernier revenu avant revalorisation, et son année : ce qu'une
    # pension différée revalorise autrement (voir plus bas).
    dernier_brut: tuple[int, float] | None = None
    for annee in sorted(par_annee):
        revenu, fraction = par_annee[annee]
        if plafonner:
            # Le plafond se proratise sur les mois travaillés : l'année
            # d'entrée dans la vie active n'est pas pleine, et un plafond
            # de douze mois y laisserait passer un salaire qu'il aurait
            # écrêté.
            revenu = min(
                revenu,
                moteur.macro.plafond_securite_sociale(annee) * fraction,
            )
        dernier_brut = (annee, revenu)
        revenus.append(revenu * revaloriser(annee, annee_liquidation))

    if not revenus:
        return 0.0

    reference = periode.salaire_reference
    if reference in ("25_meilleures_annees", "10_meilleures_annees"):
        annees = 25 if reference == "25_meilleures_annees" else 10
        if periode.salaire_reference_par_generation and generation is not None:
            par_generation = moteur.annees_salaire_reference.annees(generation)
            if par_generation is not None:
                annees = par_generation[0]
            # LES PARENTS : vingt-quatre années pour qui bénéficie d'une
            # majoration ou d'une bonification au titre d'un enfant,
            # vingt-trois pour deux enfants et plus, pour les pensions
            # prenant effet à compter du 1er septembre 2026 (article
            # R. 173-3-2, décret n° 2026-699 du 29 juillet 2026, pris pour
            # l'article 103 de la loi de financement pour 2026). La moyenne
            # porte sur moins d'années, donc sur de meilleures : c'est la
            # mesure « mères de famille » de cette loi, et elle vaut à qui
            # détient les trimestres, la mère par défaut dans ce modèle.
            if (enfants_majores > 0 and carriere.age_liquidation is not None
                    and carriere.date_liquidation.rang
                    >= moteur.PARENTS_MEILLEURES_ANNEES_DEPUIS.rang):
                annees = max(1, annees - (1 if enfants_majores == 1 else 2))
        retenus = sorted(revenus, reverse=True)[:annees]
    elif reference in ("derniers_6_mois", "dernier_salaire"):
        # Le traitement des six derniers mois est celui EN VIGUEUR au
        # départ. L'année de la liquidation est incomplète — l'assuré n'y a
        # travaillé que quelques mois —, mais c'est bien son traitement que
        # liquide le régime : on l'annualise plutôt que de reculer d'un an.
        # La ligne du régime, et non l'activité principale : un
        # fonctionnaire qui cumule une activité libérale liquide son
        # traitement, quel que soit le rang de la ligne.
        derniere = next((
            ligne for ligne in carriere.lignes_de(annee_liquidation)
            if not codes_admis.isdisjoint(coordonner.regimes_de(moteur, 
                ligne, annee_liquidation,
                carriere.date_entree(ligne.affiliation),
                revenu=ligne.revenu,
                plafond=moteur.macro.plafond_securite_sociale(annee_liquidation)))
        ), None)
        if (derniere is not None and derniere.cotise
                and derniere.fraction_annee > 0
                and not codes_admis.isdisjoint(coordonner.regimes_de(moteur, 
                    derniere, annee_liquidation,
                    carriere.date_entree(derniere.affiliation),
                    revenu=derniere.revenu,
                    plafond=moteur.macro.plafond_securite_sociale(annee_liquidation)))):
            traitement = (assiette_de_reference(moteur, periode, derniere)
                          / derniere.fraction_annee)
            if plafonner:
                traitement = min(
                    traitement,
                    moteur.macro.plafond_securite_sociale(annee_liquidation),
                )
            return traitement
        # LA PENSION DIFFÉRÉE. L'agent n'est plus en service l'année de la
        # liquidation : il a été radié des cadres au plus tard à la fin de
        # sa dernière année de service, et sa pension attend l'âge. Le
        # traitement qu'il détenait suit alors les revalorisations des
        # PENSIONS, de la radiation à la mise en paiement (L. 25 du code
        # des pensions, article 26 du décret n° 2003-1306, article 22 du
        # décret n° 2004-1056), et non le point d'indice des actifs, que
        # le moteur lui appliquait : +6,3 % de 2011 à 2026, quand les
        # pensions prenaient près d'un quart. Avant 2004, la péréquation
        # faisait suivre le point à toute pension : rien ne change.
        if (dernier_brut is not None
                and code in coordonner.REGIMES_CODE_DES_PENSIONS):
            derniere_annee, brut = dernier_brut
            radiation = date(derniere_annee + 1, 1, 1)
            paiement = date(annee_liquidation, mois_liquidation, 1)
            if radiation < paiement and paiement >= revalorisation.FIN_PEREQUATION:
                coefficient = revalorisation.coefficient_traitement_differe(
                    moteur.revalorisations_pensions,
                    moteur.minimum_garanti.ratio_point_indice,
                    derniere_annee, radiation, paiement)
                if coefficient is not None:
                    return brut * coefficient
        return revenus[-1]
    elif reference == "carriere_entiere":
        retenus = revenus
    else:
        retenus = revenus
    return sum(retenus) / len(retenus)


def duree_proratisation(moteur, periode: PeriodeRegime, carriere: Carriere,
                         requis: int) -> tuple[int, Fiabilite | None]:
    """Dénominateur du coefficient de proratisation, dans ce régime.

    Il vaut la durée requise partout, sauf pour les générations 1944 à 1948
    et celles qui les précèdent, auxquelles l'article R. 351-6 oppose une
    durée maximale plus courte — 150 trimestres avant 1944, puis 152, 154,
    156, 158 et 160. La table ne répond que là ; ailleurs, c'est la durée
    requise qui fait office, comme le droit le veut depuis 1949.

    **La table est celle du code de la sécurité sociale**, et la fiche dit
    qui la suit : le régime général et les régimes alignés. La fonction
    publique et les régimes spéciaux ont la leur, calendaire et non
    générationnelle (article L. 13 du code des pensions) ; elle n'est pas
    modélisée, et leur durée requise continue d'y faire office. Leur
    appliquer la table du privé remplacerait une approximation par une
    autre, sans que rien ne l'établisse.

    Et la durée de proratisation ne dépasse jamais la durée requise : les
    périodes anciennes, dont la durée maximale est plus courte que
    150 trimestres — 120 sous les ordonnances de 1945 —, gardent la leur.
    """
    if not periode.duree_proratisation_par_generation:
        return requis, None
    par_generation = moteur.durees_proratisation.trimestres(carriere.generation)
    if par_generation is None:
        return requis, None
    return min(par_generation[0], requis), par_generation[1]


def decote_opposable(moteur, periode: PeriodeRegime, carriere: Carriere,
            annee_liquidation: int
            ) -> tuple[float | None, float, Fiabilite | None]:
    """Décote opposable : coefficient, âge d'annulation, fiabilité.

    Un régime sans décote — fonction publique avant 2006, régimes spéciaux
    avant 2008 — n'en acquiert pas une parce que la table en porte une :
    ``None`` dans la fiche reste ``None`` ici, et le coefficient renvoyé
    est ``None``.

    **Les barèmes en table se lisent à l'année d'ouverture du droit, pas à
    celle de la liquidation.** Le III de l'article 66 de la loi du 21 août
    2003 titre sa colonne « Année au cours de laquelle sont réunies les
    conditions mentionnées au I et au II de l'article L. 24 », et les
    décrets de 2008 des régimes spéciaux visent « les personnes remplissant
    les conditions définies à l'article 6 » entre deux dates. Un
    fonctionnaire dont le droit s'ouvre en 2008 garde donc 0,375 % et
    « limite d'âge moins douze trimestres » quelle que soit l'année de son
    départ ; qui part avant l'âge d'ouverture réunit les conditions à la
    liquidation, et c'est ce millésime-là qui vaut. Le modèle lisait le
    barème à l'année de liquidation, et c'est la confrontation à
    OpenFisca-France-Pension qui l'a fait voir : deux trimestres de décote
    de trop pour un sédentaire né en 1948 parti à soixante-deux ans.

    **La fonction publique n'a pas la décote du régime général.** L'article
    L. 14 du code des pensions lui donne la sienne, montée en charge de
    2006 à 2020, et surtout un âge d'annulation qui n'est pas un âge en
    propre : c'est la LIMITE D'ÂGE du grade, diminuée d'un nombre de
    trimestres décroissant. Un sédentaire liquidant en 2012 voyait sa
    décote s'annuler à 63 ans, pas à 67 — et chaque trimestre manquant lui
    coûtait 0,875 %, pas 1,25 %. Lui opposer le barème du privé retirait
    jusqu'à un sixième de sa pension.

    **Et les régimes spéciaux ont ce barème avec quatre ans de retard.**
    La réforme de 2008 ne leur applique aucune décote avant le 1er juillet
    2010, puis un dixième du taux plein, un dixième de plus chaque année
    jusqu'à 1,25 % en 2019 : un cheminot parti en 2011 décotait de 0,125 %
    par trimestre manquant, non de 1,25 %.
    """
    age_annulation = ouvrir.age_taux_plein(moteur, periode, carriere)
    if periode.bareme_decote in _BAREMES_DECOTE_EN_TABLE:
        table = (moteur.decote_fonction_publique
                 if periode.bareme_decote == "fonction_publique"
                 else moteur.decote_regimes_speciaux)
        parametres = table.parametres(
            ouvrir.annee_ouverture_des_droits(moteur, periode, carriere, annee_liquidation)
        )
        if parametres is None:
            return None, age_annulation, None
        trimestres_avant, coefficient, fiabilite = parametres
        if periode.bareme_decote == "regimes_speciaux_age_fixe":
            # Les catégories d'âge atypique — artistes du ballet, musiciens
            # de l'orchestre — n'ont pas l'âge de référence de droit
            # commun : le V de l'article 14 leur donne « l'âge minimum
            # d'ouverture du droit à pension qui leur est applicable majoré
            # de […] huit trimestres », un âge fixe que la montée en charge
            # ne recule pas. La fiche le porte tel quel.
            return coefficient, age_annulation, fiabilite
        return coefficient, age_annulation - trimestres_avant / 4.0, fiabilite
    if periode.decote_par_trimestre is None:
        return None, age_annulation, None
    if periode.age_table:
        # Le taux que le règlement de la section écrit pour la génération,
        # quand il en écrit un : la CARCDSF de 2011 à 2023.
        propre = moteur.ages_regimes.decote(periode.age_table, carriere.generation)
        if propre is not None:
            return propre[0], age_annulation, propre[1]
    if periode.decote_par_generation:
        par_generation = moteur.coefficients_minoration.coefficient(
            carriere.generation
        )
        if par_generation is not None:
            return par_generation[0], age_annulation, par_generation[1]
    return periode.decote_par_trimestre, age_annulation, None


def trimestres_de_decote(moteur, periode: PeriodeRegime, carriere: Carriere,
                          trimestres: int,
                          requis: int, age_liquidation: float,
                          age_annulation: float) -> float:
    """Trimestres de décote opposables, plafond compris.

    **Le militaire a le sien, et il ne compte pas des âges.** Le II de
    l'article L. 14 lui oppose, non la distance à un âge d'annulation, mais
    « le nombre de trimestres manquants […] pour atteindre […] la durée de
    services militaires effectifs nécessaire pour pouvoir bénéficier d'une
    liquidation de la pension […] augmentée d'une durée de services
    effectifs de dix trimestres » — dans la limite de dix trimestres, et non
    de vingt. Un sous-officier parti à quarante ans avec dix-sept ans de
    services ne perd donc que les deux trimestres et demi qui le séparent de
    dix-neuf ans et demi, quand le barème des civils lui aurait retiré le
    quart de sa pension pour être parti vingt-deux ans avant l'âge légal.

    Le décompte retient le plus favorable des deux : trimestres manquants
    pour la durée requise, ou trimestres manquants jusqu'à l'âge
    d'annulation de la décote.

    **Le plafond de vingt trimestres n'est pas une règle de plus : c'est
    l'arithmétique des deux âges.** Il est écrit là où le droit a voulu
    l'écrire — R. 643-7 pour les professions libérales, R. 723-38 pour les
    avocats, le I de L. 14 pour la fonction publique — et absent de
    R. 351-27 2° comme de R. 732-61, qui ne s'en sont jamais souciés. La
    raison est mesurable dans les tables du dépôt : l'écart entre l'âge
    d'ouverture et l'âge d'annulation vaut EXACTEMENT vingt trimestres pour
    les générations 1930 à 1961, puis descend à dix-huit, quinze, treize et
    douze à mesure que les réformes relèvent le premier sans toucher au
    second. Sur toute liquidation que le droit ouvre, le décompte par l'âge
    est donc au plus de vingt par construction, et le plafond ne mord
    jamais — ``tests/test_moteur.py`` le vérifie sur toute la grille.

    Il ne mordrait que sur une liquidation ANTÉRIEURE à l'âge d'ouverture,
    que le modèle refuse depuis qu'il sait opposer un âge à toutes les
    carrières. Le garder ne coûte donc rien et protège d'un changement
    d'âges qui casserait l'identité ; le retirer demanderait de vérifier
    les trois textes qui l'écrivent. On le garde, et cette phrase dit
    pourquoi il ne se voit pas.

    Le décompte par l'ÂGE est arrondi à l'entier supérieur, comme le veut
    l'article R. 351-27. Les âges d'annulation des générations 1951 à 1954
    valent 65,33, 65,75, 66,17 et 66,58 ans : sans cet arrondi, on opposait
    13,32 trimestres à un assuré né en 1951 parti à 62 ans, quand le droit
    lui en oppose 14. Le barème d'anticipation de l'Agirc-Arrco, lui,
    arrondissait déjà — les deux décomptes suivent maintenant la même règle.
    """
    militaire = ouvrir.droit_militaire(moteur, periode, carriere)
    if militaire is not None:
        manquants_services = max(
            0, militaire.trimestres_cible - militaire.trimestres_servis
        )
        manquants_duree = max(0, requis - trimestres)
        return float(min(manquants_services, manquants_duree,
                         TRIMESTRES_DECOTE_MILITAIRE))
    manquants_age = float(_au_trimestre_superieur(
        (age_annulation - age_liquidation) * 4
    ))
    if periode.decote_par_la_duree_seule:
        # La CRPN depuis 2022 : la durée seule compte, et l'âge d'annulation
        # ne fait qu'effacer la décote une fois atteint (R. 6527-22 et
        # R. 6527-23 du code des transports).
        trimestres_decote = (
            0.0 if manquants_age <= 0 else float(max(0, requis - trimestres))
        )
    elif periode.decote_annulee_par_la_duree:
        # La SNCF compte la décote par la durée sur une cible abaissée de
        # deux à dix trimestres selon la génération (décret n° 2008-639,
        # article 35, II) ; partout ailleurs, rien n'est retranché.
        cible = requis - retranche_decote(moteur, periode, carriere)
        trimestres_decote = min(max(0, cible - trimestres), manquants_age)
    else:
        # Avant l'ordonnance du 26 mars 1982, le taux ne dépendait QUE de
        # l'âge : le régime général servait 20 % à 60 ans, majorés de
        # 4 points par année différée, puis — loi Boulin — 50 % à 65 ans,
        # diminués de 5 points par année anticipée. Aucune durée, si longue
        # fût-elle, n'ouvrait le taux plein avant l'âge. Annuler la décote
        # par la durée, comme le fait le droit d'après 1982, servait le taux
        # plein à 60 ans à des générations auxquelles la loi ne l'a jamais
        # donné.
        trimestres_decote = manquants_age
    if trimestres_decote <= 0:
        return 0.0
    if periode.decote_trimestres_maximum is not None:
        trimestres_decote = min(trimestres_decote, periode.decote_trimestres_maximum)
    return trimestres_decote


def retranche_decote(moteur, periode: PeriodeRegime, carriere: Carriere) -> int:
    """Trimestres retranchés à la durée requise pour compter la décote."""
    propre = ouvrir.duree_propre(moteur, periode, carriere)
    return 0 if propre is None else propre[1]


def valeur_point_fiche(moteur, periode: PeriodeRegime, annee: int) -> float:
    """Valeur de service du point écrite dans la fiche, à l'année demandée.

    La MSA est seule à publier celle de sa retraite proportionnelle — ni le
    code rural, ni les barèmes IPP, ni OpenFisca ne la portent —, et elle le
    fait dans un communiqué annuel. Une ancre datée suffit : la loi
    (L. 161-23-1) revalorise cette valeur sur les prix, et c'est donc l'index
    des prix qui la porte d'une année à l'autre.
    """
    if periode.valeur_point_euros is None:
        return 0.0
    return periode.valeur_point_euros * moteur.macro.coefficient_prix(
        periode.valeur_point_annee or annee, annee
    )


def abattement_points(moteur, periode: PeriodeRegime, carriere: Carriere,
                       trimestres: int, requis: int,
                       age_liquidation: float,
                       annee_liquidation: int,
                       trimestres_regime: int = 0) -> float:
    """Coefficient d'un régime en points : abattu avant le taux plein,
    majoré après.

    Il ne dépassait jamais un, et c'était un droit manquant : voir
    :func:`surcote_points`, qui rend la majoration que la fiche écrit
    quand l'abattement est revenu à un. ``trimestres_regime`` est la durée
    d'affiliation à ce régime-là, que la CIPAV oppose à sa surcote.

    « Avant le taux plein » est une condition de DURÉE autant que d'âge :
    une complémentaire est servie sans abattement dès que l'assuré a le
    taux plein au régime de base, même s'il liquide avant l'âge d'annulation
    de la décote.

    L'Agirc-Arrco ne reprend pas la décote du régime de base : elle publie
    ses propres COEFFICIENTS D'ANTICIPATION, en deux tables — l'une indexée
    sur les trimestres manquants, l'autre sur l'âge — et retient la plus
    avantageuse pour l'assuré. Les deux ne se recoupent pas : douze
    trimestres manquants valent 0,88, quand la décote du régime de base
    n'en donnerait que 0,85 ; mais dix ans d'anticipation valent 0,43, là
    où elle en donnerait 0,50.

    **L'Ircantec a le même barème, et son texte l'écrit.** L'article 16 de
    l'arrêté du 30 décembre 1970 donne le coefficient 0,43 dix ans avant
    l'âge normal, « majoré de 0,017 5 par trimestre » jusqu'à cinq ans
    avant, de 0,012 5 par trimestre sur les deux suivantes et de 0,01 par
    trimestre sur les trois dernières : ce sont, marche pour marche, les
    paliers de l'Agirc-Arrco. Son paragraphe 2 est la seconde table —
    l'assuré qui n'a pas la durée requise se voit appliquer le même
    escalier « en assimilant à l'âge de soixante-cinq ans l'âge auquel
    [il] aurait effectivement accompli la durée d'assurance », sans
    pouvoir descendre sous le coefficient de son âge, ce qui est
    exactement « la plus avantageuse des deux ». Le modèle lui opposait
    1,1 % par trimestre, taux moyen qui tombe juste aux deux extrémités du
    barème — 0,78 à cinq ans, 1,00 à zéro — et nulle part entre les deux :
    à douze trimestres il retirait 13,2 % là où l'arrêté en retire 12.
    """
    if periode.abattement_points in ("agirc_arrco", "ircantec"):
        # AVANT L'ASF, L'ÂGE SEUL. Jusqu'à l'accord du 4 février 1983,
        # l'Agirc et l'Arrco servaient le taux plein à soixante-cinq ans et
        # abattaient toute anticipation, quelle que soit la durée : c'est
        # l'ASF qui a financé la retraite à soixante ans sans abattement
        # pour qui avait le taux plein au régime de base. Une période sans
        # durée requise — ni en dur, ni lue à la génération — porte ce
        # droit-là, et la table par durée ne s'y consulte pas.
        par_age_seul = (
            periode.duree_requise_trimestres is None
            and not periode.duree_requise_par_generation
        )
        if not par_age_seul and trimestres >= requis:
            abattement = 1.0
        else:
            par_duree = (
                None if par_age_seul
                else _coefficient_anticipation(requis - trimestres, 20)
            )
            ecart_age = max(
                0.0,
                (ouvrir.age_taux_plein(moteur, periode, carriere) - age_liquidation) * 4,
            )
            par_age = _coefficient_anticipation(ecart_age, 40)
            if par_age is None:
                par_age = _COEFFICIENT_ANTICIPATION_PLANCHER
            candidats = [c for c in (par_duree, par_age) if c is not None]
            abattement = max(candidats) if candidats else 1.0
    elif periode.abattement_points in _ABATTEMENTS_IRCEC:
        abattement = abattement_ircec(moteur, 
            periode, carriere, trimestres, requis,
            age_liquidation, annee_liquidation,
        )
    else:
        abattement = abattement_regime_de_base(moteur, 
            periode, carriere, trimestres, requis,
            age_liquidation, annee_liquidation,
        )
    if abattement < 1.0 and taux_plein_anticipe(moteur, 
            periode, carriere, age_liquidation):
        abattement = 1.0

    if abattement < 1.0:
        # ABATTU ET MAJORÉ NE SE RENCONTRENT PAS. Les deux majorations de
        # l'arrêté supposent l'une l'âge du taux plein dépassé, l'autre la
        # durée requise dépassée — c'est-à-dire, dans les deux cas, un
        # coefficient d'anticipation déjà revenu à 1. L'écrire coûte une
        # ligne et dispense de s'en convaincre à chaque lecture.
        return abattement
    return surcote_points(moteur, 
        periode, carriere, trimestres, requis,
        age_liquidation, annee_liquidation, trimestres_regime,
    )


def taux_plein_anticipe(moteur, periode: PeriodeRegime, carriere: Carriere,
                         age_liquidation: float) -> bool:
    """Le taux plein qu'une section ouvre aux mères avant son âge.

    La CARCDSF permet « un départ anticipé à la retraite sans qu'il soit
    fait application du taux de minoration […] aux affiliées
    chirurgiens-dentistes ou sages-femmes, au titre de l'incidence sur leur
    vie professionnelle de la maternité […] à raison d'une année
    d'anticipation par enfant mis au monde, dans la limite de 5 années
    maximum » (statuts approuvés le 13 avril 2011, article 19 II, puis
    règlement du 10 juillet 2026, article 3 II) ; ses statuts de 2007
    l'écrivaient déjà, de 64 ans pour un enfant à 60 ans pour cinq.

    Les dispositions générales et particulières « sont exclusives les unes
    des autres » (article 4) : l'anticipation n'abaisse pas l'âge dont se
    compte la minoration, elle ouvre le taux plein à un âge. Une mère de
    deux enfants partie à 65 ans n'en perd rien ; partie à 64, elle est
    minorée comme tout affilié, depuis 67 ans.
    """
    if (periode.taux_plein_anticipe_par_enfant_annees is None
            or carriere.sexe != "F" or carriere.nombre_enfants <= 0):
        return False
    anticipation = (carriere.nombre_enfants
                    * periode.taux_plein_anticipe_par_enfant_annees)
    if periode.taux_plein_anticipe_maximum_annees is not None:
        anticipation = min(anticipation,
                           periode.taux_plein_anticipe_maximum_annees)
    return (age_liquidation
            >= ouvrir.age_taux_plein(moteur, periode, carriere) - anticipation - 1e-9)


def abattement_regime_de_base(moteur, periode: PeriodeRegime,
                               carriere: Carriere, trimestres: int,
                               requis: int, age_liquidation: float,
                               annee_liquidation: int) -> float:
    """Coefficient qui reprend la décote du régime de base : un taux par
    trimestre manquant, au plus favorable de l'âge et de la durée.

    **Deux pentes, quand la fiche en écrit deux.** La CAVP minore « de
    1,25 % par trimestre d'anticipation entre l'âge d'ouverture des droits
    et 65 ans ; 0,5 % par trimestre d'anticipation entre 65 ans et l'âge
    fixé au 1° de l'article L. 351-8 » (règlement approuvé le 10 juillet
    2026, article 12, déjà dans ses statuts depuis l'arrêté du 23 juin
    2011). Les trimestres d'avant le palier se comptent au premier taux,
    les autres au second : un pharmacien parti à soixante-quatre ans en
    perd quatre à 1,25 % et huit à 0,5 %, soit 9 %.
    """
    decote, age_annulation, _ = decote_opposable(moteur, 
        periode, carriere, annee_liquidation
    )
    if decote is None:
        return 1.0
    trimestres_decote = trimestres_de_decote(moteur, 
        periode, carriere, trimestres, requis, age_liquidation,
        age_annulation
    )
    if (periode.decote_palier_age is not None
            and periode.decote_par_trimestre_apres_palier is not None
            and trimestres_decote > 0):
        avant = min(trimestres_decote, max(0, _au_trimestre_superieur(
            (periode.decote_palier_age - age_liquidation) * 4)))
        apres = trimestres_decote - avant
        return max(0.0, 1.0 - decote * avant
                   - periode.decote_par_trimestre_apres_palier * apres)
    return max(0.0, 1.0 - decote * trimestres_decote)


def abattement_ircec(moteur, periode: PeriodeRegime, carriere: Carriere,
                      trimestres: int, requis: int,
                      age_liquidation: float,
                      annee_liquidation: int) -> float:
    """Coefficient de minoration des trois régimes de l'IRCEC.

    Les règlements du RAAP (art. 27), du RACD (art. 21) et du RACL
    (art. 21) ne reprennent pas la décote du régime de base : ils comptent
    des ANNÉES manquantes jusqu'à l'âge du taux plein — celui du 1° de
    l'article L. 351-8 —, « 2,5 % par année pour chacune des deux premières
    années manquantes ; 5 % par année manquante supplémentaire ». Une
    année entamée compte entière : l'annexe de l'arrêté du 21 novembre
    2013 le chiffre trimestre par trimestre, un à quatre trimestres
    d'anticipation valant 2,5 %, cinq à huit 5 %, neuf à douze 10 %.

    « Toutefois, si cela est plus favorable à l'adhérent », les mêmes
    coefficients que ceux du régime de base : c'est la décote de la fiche,
    et le coefficient retenu est le plus haut des deux. La pension est
    servie sans minoration dès l'âge légal si celle du régime de base
    l'est au taux plein, c'est-à-dire dès que la durée requise est réunie.

    ``ircec_age_seul`` est le RACL de 2014 à 2024 : « 5 % par année
    manquante », sans marche à 2,5 %, sans renvoi au régime de base, et un
    taux plein que la durée n'ouvrait pas — il fallait l'âge. L'arrêté du
    13 mai 2025 l'a aligné sur les deux autres. Le modèle leur opposait à
    tous trois 1,25 % par trimestre depuis soixante-sept ans : vingt-cinq
    pour cent à soixante-deux ans pour qui n'a pas sa durée, là où l'IRCEC
    en retire vingt.

    ``cavom`` est la même règle, écrite par un autre règlement : « 5 % par
    année manquante entre l'âge auquel est demandée la liquidation […] et
    l'âge prévu au 2° », et « ce coefficient n'est pas susceptible de
    fractionnement » (règlement du régime complémentaire de la CAVOM,
    article 1er, I, 3°, approuvé par l'arrêté du 10 juillet 2026, déjà dans
    ses statuts depuis l'arrêté du 12 décembre 2024). Le texte ne dit pas
    si l'année entamée compte ; le modèle la compte, comme l'IRCEC l'écrit
    en toutes lettres. La durée d'assurance n'y ouvre pas le taux plein :
    la fiche lui opposait la décote du régime de base, que la durée
    annule, et un officier ministériel parti à l'âge légal avec sa durée
    ne perdait rien de sa complémentaire.
    """
    age_taux_plein = ouvrir.age_taux_plein(moteur, periode, carriere)
    age_seul = periode.abattement_points in _ABATTEMENTS_PAR_ANNEE_AGE_SEUL
    if age_liquidation >= age_taux_plein - 1e-9:
        return 1.0
    if not age_seul and trimestres >= requis:
        return 1.0
    annees = -(-_au_trimestre_superieur(
        (age_taux_plein - age_liquidation) * 4) // 4)
    if age_seul:
        propre = 1.0 - 0.05 * annees
    else:
        propre = 1.0 - 0.025 * min(annees, 2) - 0.05 * max(0, annees - 2)
    propre = max(0.0, propre)
    if age_seul:
        return propre
    return max(propre, abattement_regime_de_base(moteur, 
        periode, carriere, trimestres, requis,
        age_liquidation, annee_liquidation,
    ))


def coefficient_surcote_datee(moteur, periode: PeriodeRegime, carriere: Carriere,
                               trimestres: int, requis: int,
                               supplementaires: int, age_ouverture: float
                               ) -> tuple[float, Fiabilite | None]:
    """Coefficient de surcote, trimestre civil par trimestre civil.

    La règle est celle de la circulaire Cnav 2018-04 (point 2), que le
    modèle suivait à l'année près : la PÉRIODE DE RÉFÉRENCE commence au
    plus tard des trois — le premier jour du trimestre civil qui suit
    l'âge légal, le premier jour du mois qui suit l'acquisition de la
    durée requise, le 1er janvier 2004 — et s'achève au dernier jour du
    trimestre civil qui précède la date d'effet. Chaque trimestre civil de
    cette période compte, dans la limite des trimestres cotisés reportés
    au compte pour l'année, et au plus ``supplementaires`` en tout ; puis
    chacun prend le taux du barème à sa date. Un assuré né le 15 avril, à
    l'âge légal en avril, ne surcote qu'à partir de juillet : le modèle
    comptait avril, et servait un trimestre de trop.

    La durée acquise se lit dans l'ordre des années. Les trimestres qui ne
    tiennent à aucune année — la majoration pour enfants — sont réputés
    acquis d'emblée : ils sont dus quelle que soit la date du départ, et la
    caisse ne les date pas davantage.

    LA FONCTION PUBLIQUE COMPTE DES DURÉES, ET NON DES TRIMESTRES CIVILS.
    L. 14, III, du code des pensions retient « le nombre de trimestres
    d'assurance effectués après le 1er janvier 2004, au-delà de l'âge
    [légal] et en sus du nombre de trimestres nécessaire » : la période
    s'ouvre le jour où les conditions sont réunies, et se découpe en
    trimestres de durée dont seuls les entiers comptent. La CNRACL en donne
    l'exemple : l'agent né le 1er janvier 1962, à l'âge légal le 1er juillet
    2024, qui travaille jusqu'au 31 décembre 2025, a « effectué 6
    trimestres supplémentaires de services effectifs à partir du
    01/07/2024 ». La règle du régime général, que le modèle lui appliquait,
    n'ouvre la période qu'au trimestre civil suivant : partie en février
    2026 après un âge légal atteint à la mi-octobre 2024, une fonctionnaire
    a quinze mois de services au-delà, cinq trimestres entiers, et le
    modèle lui en comptait quatre.

    Le modèle datant au mois, la période s'ouvre le premier du mois qui
    suit celui où l'âge est atteint. C'est exact pour qui est né après le
    premier du mois — service-public.gouv.fr l'écrit ainsi pour un
    fonctionnaire né le 9 octobre 1964, « taux plein à 62 ans et 9 mois
    (1er août 2027) » —, et l'agent de la CNRACL, né un 1er janvier, a un
    trimestre de plus que le modèle ne lui en compte.
    """
    annee_liquidation = carriere.annee_liquidation
    date_legal = carriere.date_naissance.plus_mois(en_mois(age_ouverture))
    en_duree = periode.regime in coordonner.REGIMES_CODE_DES_PENSIONS
    trimestre_legal = (date_legal.mois - 1) // 3
    debut_age = (date_legal.plus_mois(1) if en_duree
                 else DateMois(date_legal.annee, 1).plus_mois(3 * (trimestre_legal + 1)))

    par_annee = carriere.trimestres_par_annee(
        ligne for ligne in carriere.lignes if ligne.annee <= annee_liquidation
    )
    cotises_par_annee = carriere.trimestres_par_annee(
        ligne for ligne in carriere.lignes
        if ligne.cotise and ligne.annee <= annee_liquidation
    )
    acquis = trimestres - sum(par_annee.values())
    debut_duree = None
    if acquis >= requis:
        debut_duree = moteur.SURCOTE_DEPUIS
    for annee in sorted(par_annee):
        if debut_duree is not None:
            break
        valides = par_annee[annee]
        if acquis + valides >= requis:
            manquants = requis - acquis
            debut_duree = DateMois(annee, 1).plus_mois(3 * manquants)
        acquis += valides
    if debut_duree is None:
        return 1.0, None
    debut = DateMois.depuis_rang(max(
        debut_age.rang, debut_duree.rang, moteur.SURCOTE_DEPUIS.rang
    ))
    # Le trimestre de départ est ramené au trimestre civil qui le
    # contient s'il commence en cours de trimestre : la durée acquise au
    # 30 juin ouvre la période au 1er juillet, celle acquise au 31 mai
    # l'ouvre au 1er juin, mais un trimestre civil ne se compte qu'entier.
    # La fonction publique, qui compte des durées, n'arrondit pas.
    if (debut.mois - 1) % 3 and not en_duree:
        debut = DateMois(debut.annee, 1).plus_mois(3 * ((debut.mois - 1) // 3 + 1))
    fin = carriere.date_liquidation
    date_65 = carriere.date_naissance.plus_mois(12 * moteur.SURCOTE_AGE_MAJORE)
    trimestre_65 = (date_65.annee, (date_65.mois - 1) // 3)

    dates: list[tuple[DateMois, bool]] = []
    restants_par_annee = dict(cotises_par_annee)
    courant = debut
    while courant.rang + 2 < fin.rang and len(dates) < supplementaires:
        if restants_par_annee.get(courant.annee, 0) > 0:
            restants_par_annee[courant.annee] -= 1
            apres_65 = (courant.annee, (courant.mois - 1) // 3) > trimestre_65
            # Un trimestre de durée est accompli à son dernier mois, et
            # c'est le taux de ce mois-là qu'il prend : celui de novembre
            # 2008 à janvier 2009 est au 1,25 % de la LFSS pour 2009.
            dates.append((courant.plus_mois(2) if en_duree else courant, apres_65))
        courant = courant.plus_mois(3)
    if not dates:
        return 1.0, None
    if not moteur.surcote_baremes.connait(periode.surcote_bareme or ""):
        return 1.0 + (periode.surcote_par_trimestre or 0.0) * len(dates), None
    return moteur.surcote_baremes.coefficient(periode.surcote_bareme, dates)


def surcote_points(moteur, periode: PeriodeRegime, carriere: Carriere,
                    trimestres: int, requis: int,
                    age_liquidation: float,
                    annee_liquidation: int,
                    trimestres_regime: int = 0) -> float:
    """Majoration d'un régime en points liquidé APRÈS le taux plein.

    Trois façons de compter, parce que les textes en écrivent trois, et la
    fiche dit laquelle par ``surcote_points`` :

    ``regime_general`` — la règle de l'article L. 351-1-2, mot pour mot
    celle que la branche en annuités sert : trimestres COTISÉS « après
    l'âge prévu au premier alinéa de l'article L. 351-1 et au-delà de la
    limite mentionnée au deuxième alinéa du même article ». C'est celle du
    régime de base des professions libérales — R. 643-8, 0,75 % par
    trimestre depuis 2004, 1,25 % pour les trimestres accomplis à compter
    du 1er septembre 2023 — et celle des exploitants agricoles (D. 732-42).
    Le militaire n'en a aucune, et le décompte part de l'âge légal de droit
    commun, comme là-bas.

    ``par_age_seul`` — les statuts des sections libérales ne comptent ni
    durée ni cotisation, seulement le TEMPS : « 1,25 % par trimestre
    séparant le premier jour du trimestre civil suivant celui où le médecin
    atteint cet âge de la date d'effet de la retraite » (CARMF, art. 15),
    « par trimestre civil entier d'ajournement postérieur à l'âge du taux
    plein dans la limite de vingt trimestres » (CARPIMKO, art. 12 ter),
    « par trimestre plein de prorogation au-delà de cet âge, dans la limite
    maximale de 25 % » (CAVEC, art. 13). Le décompte part de
    ``surcote_age_debut``, ou de l'âge du taux plein lu à la génération ;
    il s'arrête à ``surcote_age_maximum`` — le soixante-dixième
    anniversaire, chez les médecins et les notaires — et à
    ``surcote_trimestres_maximum`` ; il ne retient que des multiples de
    ``surcote_pas_trimestres`` quand le texte dit « par année pleine » ;
    il change de taux à ``surcote_palier_age`` — 0,75 % au lieu de 1,25 %
    après soixante-cinq ans, à la CARMF et à l'ASV — ; et il n'est dû
    qu'au-delà de ``surcote_affiliation_minimale_trimestres`` d'affiliation
    au régime, « si, à 67 ans, vous réunissez 30 années d'affiliation à la
    Cipav ».

    ``ircantec`` — le IV de l'article 16 de l'arrêté du 30 décembre 1970,
    paragraphe 4 dans la version que le décret du 23 septembre 2008 a
    introduite « à compter du 1er janvier 2010 », majore le total des
    points de DEUX façons qui ne se recouvrent pas : 1° « 0,75 % par
    trimestre entier écoulé entre le soixante-cinquième anniversaire de
    l'assuré et la date d'entrée en jouissance de la pension » — du temps
    écoulé, comme ``par_age_seul`` ; 2° « 0,625 % par trimestre accompli »
    de durée cotisée au-delà de l'âge légal et de la durée requise, en deçà
    de ce même âge — l'assiette de ``regime_general``, bornée en haut par
    l'âge où le 1° prend le relais, car « en aucun cas une même période ne
    peut donner lieu à la fois » aux deux.

    Le modèle ne servait que la troisième : la branche en points ne lisait
    pas ``surcote_par_trimestre``, et neuf fiches de non-salariés en
    écrivaient une pour rien.
    """
    mode = periode.surcote_points
    if mode == "aucune":
        return 1.0
    if mode == "rafp":
        # Le RAFP module sa valeur de service par un barème d'âge, sans
        # taux par trimestre : 1,08 à 64 ans, 1,22 à 67, 1,40 à 70.
        return _majoration_rafp(age_liquidation)
    if mode == "ircantec":
        return surcote_ircantec(moteur, 
            periode, carriere, trimestres, requis,
            age_liquidation, annee_liquidation,
        )
    taux = periode.surcote_par_trimestre
    if not taux:
        return 1.0
    if mode == "regime_general":
        supplementaires = max(0, trimestres - requis)
        age_ouverture = ouvrir.age_ouverture_commun(moteur, periode, carriere)
        if (supplementaires <= 0 or age_liquidation < age_ouverture
                or ouvrir.droit_militaire(moteur, periode, carriere) is not None):
            return 1.0
        supplementaires = min(
            supplementaires,
            _trimestres_cotises_apres(carriere, age_ouverture, annee_liquidation),
        )
        return 1.0 + taux * supplementaires
    if mode != "par_age_seul":
        raise ValueError(f"surcote_points inconnu : {mode!r}")

    minimum = periode.surcote_affiliation_minimale_trimestres
    if minimum is not None and trimestres_regime < minimum:
        return 1.0
    debut = periode.surcote_age_debut
    if debut is None:
        debut = ouvrir.age_taux_plein(moteur, periode, carriere)
    fin = age_liquidation
    if periode.surcote_age_maximum is not None:
        fin = min(fin, periode.surcote_age_maximum)
    # Des trimestres civils ENTIERS : deux mois de plus ne valent rien.
    ecoules = int((max(0.0, fin - debut) + 1e-9) * 4)
    if periode.surcote_trimestres_cotises:
        # « Pour chaque année pleine COTISÉE dans le présent régime »
        # (CAVAMAC, statuts dans la rédaction de l'arrêté du 4 août 2023,
        # article 16) : le temps écoulé sans cotiser ne compte plus.
        ecoules = min(ecoules, _trimestres_cotises_apres(
            carriere, debut, annee_liquidation))
    if periode.surcote_trimestres_maximum is not None:
        ecoules = min(ecoules, periode.surcote_trimestres_maximum)
    pas = max(1, periode.surcote_pas_trimestres)
    ecoules -= ecoules % pas
    if ecoules <= 0:
        return 1.0
    palier = periode.surcote_palier_age
    if palier is None or periode.surcote_par_trimestre_apres_palier is None:
        return 1.0 + taux * ecoules
    avant_palier = min(ecoules, max(0, int((palier - debut + 1e-9) * 4)))
    return (1.0
            + taux * avant_palier
            + periode.surcote_par_trimestre_apres_palier
            * (ecoules - avant_palier))


def surcote_ircantec(moteur, periode: PeriodeRegime, carriere: Carriere,
                      trimestres: int, requis: int,
                      age_liquidation: float,
                      annee_liquidation: int) -> float:
    """Les deux taux du IV de l'article 16 — voir :func:`surcote_points`."""
    age_taux_plein = ouvrir.age_taux_plein(moteur, periode, carriere)

    # 1° — LE TEMPS ÉCOULÉ, en trimestres ENTIERS : l'arrêté le dit, et
    # deux mois de plus ne valent rien.
    ecoules = int((max(0.0, age_liquidation - age_taux_plein) + 1e-9) * 4)

    # 2° — LA DURÉE COTISÉE EN DEÇÀ. Les trimestres au-delà de la durée
    # requise sont les DERNIERS de la carrière : les compter ici suppose
    # donc que la durée requise était déjà atteinte avant l'âge du taux
    # plein, sans quoi ils tombent dans la fenêtre du 1° et y sont déjà
    # payés.
    supplementaires = 0
    age_ouverture = ouvrir.age_ouverture_commun(moteur, periode, carriere)
    if age_liquidation >= age_ouverture:
        avant = min(
            trimestres,
            _trimestres_valides_avant(
                carriere, age_taux_plein, annee_liquidation
            ),
        )
        supplementaires = max(0, avant - requis)
        if supplementaires > 0:
            supplementaires = min(
                supplementaires,
                _trimestres_cotises_entre(
                    carriere, age_ouverture, age_taux_plein,
                    annee_liquidation,
                ),
            )
    return (1.0
            + _SURCOTE_IRCANTEC_AGE * ecoules
            + _SURCOTE_IRCANTEC_DUREE * supplementaires)


def _trimestres_cotises_apres(carriere: Carriere, age: float,
                              annee_liquidation: int) -> int:
    """Trimestres cotisés à partir de l'année où l'assuré atteint ``age``.

    Seuls ceux-là ouvrent droit à la surcote : c'est une récompense du travail
    prolongé, pas de l'entrée précoce dans la vie active.
    """
    return carriere.trimestres_cumules(
        ligne
        for ligne in carriere.lignes
        if ligne.cotise
        and ligne.annee <= annee_liquidation
        and ligne.annee - carriere.annee_naissance >= age
    )


def _trimestres_valides_avant(carriere: Carriere, age: float,
                              annee_liquidation: int) -> int:
    """Durée d'assurance acquise avant l'année où l'assuré atteint ``age``.

    Périodes assimilées comprises : c'est la durée d'assurance qu'oppose la
    condition de taux plein, et non la seule durée cotisée.
    """
    return carriere.trimestres_cumules(
        ligne
        for ligne in carriere.lignes
        if ligne.annee <= annee_liquidation
        and ligne.annee - carriere.annee_naissance < age
    )


def _trimestres_cotises_entre(carriere: Carriere, age_bas: float, age_haut: float,
                              annee_liquidation: int) -> int:
    """Trimestres cotisés entre deux âges — bas inclus, haut exclu.

    C'est la fenêtre de la surcote de l'Ircantec à la durée, entre l'âge
    d'ouverture et l'âge du taux plein, lue à l'âge atteint dans l'année. La
    surcote parentale, dont la fenêtre tombe en cours d'année, se compte au
    mois près : :func:`_trimestres_entre_dates`.
    """
    return carriere.trimestres_cumules(
        ligne
        for ligne in carriere.lignes
        if ligne.cotise
        and ligne.annee <= annee_liquidation
        and age_bas <= ligne.annee - carriere.annee_naissance < age_haut
    )


def _assiette_de_reference(periode: PeriodeRegime, ligne) -> float:
    """Part de la rémunération que ce régime prend en compte.

    Même découpage que dans la boucle de cotisation : un régime qui ne cotise
    que sur le traitement indiciaire ne peut pas liquider sur la rémunération
    primes comprises, sans quoi les primes ouvriraient deux fois des droits —
    au RAFP et à la pension civile — alors qu'elles n'en ouvrent qu'au RAFP.
    """
    return periode.part_du_revenu(ligne.revenu, ligne.part_primes)
