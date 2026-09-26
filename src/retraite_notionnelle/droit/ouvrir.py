"""Ouvrir le droit (docs/architecture.md, § 7.3).

À quel âge le droit ouvre-t-il la liquidation demandée, et à quelle durée la
sert-il au taux plein ? Trois droits se superposent, du plus particulier au
plus général : l'âge qu'un régime spécial a en propre, celui que la
catégorie active ou la jouissance militaire ouvrent, et l'âge légal de la
génération (:func:`age_ouverture`) ; la durée requise suit la génération, le
calendrier du régime ou l'année d'ouverture des droits
(:func:`duree_requise`). Quand l'âge demandé précède tous les autres, la
carrière longue peut encore l'ouvrir.

:func:`ouvrir` écrit ce que l'étape dit d'une demande — son schéma est
``data/reference/etapes/ouvrir_le_droit.yaml`` ; :func:`age_ouverture_droit`
et :func:`age_taux_plein_droit` sont ce que le pilote en lit quand il ne lui
faut qu'un âge, sans rien liquider (§ 7.7).

Les tables sont celles que le moteur du scénario 1 tient (``moteur``, un
:class:`~retraite_notionnelle.scenarios.actuel.ScenarioActuel`), jusqu'aux
fiches (phase 6). Son jumeau est ``moteur/js/droit/ouvrir.js``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..calendrier import DateMois, en_mois
from ..donnees.chargement import Fiabilite
from . import compter, coordonner
from .commun import date_d_effet, derniere_annee

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..donnees.regimes import PeriodeRegime
    from ..scenarios.actuel import DerogationActive, ScenarioActuel
    from .releve import Releve

#: La version du schéma de l'étape que :meth:`Ouverture.donnees` suit.
SCHEMA_VERSION = 1

#: Première date d'effet, (année, mois), où la table de la suspension vaut, et
#: les générations qu'elle a changées : avant, la table de 2023 demeure.
SUSPENSION_2026_EFFET = (2026, 9)
GENERATIONS_SUSPENSION = (1964.0, 1966.0)


#: Première date d'effet où la table de 2023 vaut, et la première génération
#: qu'elle a changée — le 1er septembre 1961 : avant, la version de 2014 de
#: L. 161-17-3 demeure.
REFORME_2023_EFFET = (2023, 9)
GENERATION_REFORME_2023 = 1961.667

#: Durée minimale de services qui ouvre une pension militaire, même différée :
#: « lorsqu'ils ont accompli […] moins de quinze ans de services effectifs »,
#: dit le 5° de l'article L. 25, la pension n'est due qu'à l'âge légal.
SERVICES_MINIMAUX_MILITAIRES = 15.0

#: Trimestres de services que le II de l'article L. 14 ajoute à la durée
#: d'ouverture pour borner la décote militaire, et plafond de celle-ci.
TRIMESTRES_DECOTE_MILITAIRE = 10

#: Surcote de l'emploi classé de la fonction publique (loi n° 2023-270, article
#: 10, XXIV, D ; décret n° 2023-435, article 13, II, D) : première génération
#: des marches de 2023 — nés à compter du 1er septembre 1966 pour l'active, du
#: 1er septembre 1971 pour la super-active —, et années ajoutées à l'âge
#: anticipé ou minoré pour obtenir l'âge de la surcote.
SURCOTE_EMPLOIS_CLASSES = {
    "active": (1966 + 8 / 12, 5.0),
    "super_active": (1971 + 8 / 12, 10.0),
}

#: Âge de la surcote « applicable avant l'entrée en vigueur » de la réforme de
#: 2023, que le même D laisse aux générations classées d'avant ces marches :
#: l'âge de L. 161-17-2 pour les générations nées depuis 1955.
AGE_SURCOTE_AVANT_2023 = 62.0


@dataclass(frozen=True)
class DroitMilitaire:
    """Ce que la pension militaire oppose à un assuré, une fois sa carrière lue."""

    #: Âge auquel la pension s'ouvre : celui où la durée est atteinte, ou l'âge
    #: de jouissance différée de l'article L. 25.
    age_ouverture: float
    #: Trimestres de services militaires accomplis à la liquidation.
    trimestres_servis: int
    #: Durée d'ouverture majorée des dix trimestres du II de l'article L. 14 :
    #: c'est elle, et non l'âge, qui borne la décote d'un militaire.
    trimestres_cible: int
    #: Vrai quand la pension n'est due qu'à l'âge différé, faute de la durée.
    jouissance_differee: bool
    fiabilite: Fiabilite


@dataclass(frozen=True)
class Ouverture:
    """Ce que l'étape « ouvrir le droit » dit d'une demande."""

    #: La carrière de la demande, rétablissement fait.
    carriere: Carriere
    #: La durée d'assurance requise que les régimes de base opposent : celle
    #: qui commande le taux plein, et l'abattement des complémentaires.
    requis: int
    #: L'âge le plus précoce auquel le droit ouvre cette liquidation, tous
    #: dispositifs compris, carrière longue comprise ; ``None`` quand aucun
    #: régime n'en fixe.
    age: float | None
    #: ``age_legal``, ``carriere_longue`` ou ``non_ouverte`` (vocabulaire,
    #: liste ``ouvertures``).
    motif: str
    #: Les trimestres cotisés tous régimes, qui commandent la carrière longue
    #: et la majoration du minimum contributif.
    trimestres_cotises: int
    fiabilite: Fiabilite

    @property
    def ouverte(self) -> bool:
        """Le droit ouvre-t-il la liquidation à cet âge ? Quand il ne l'ouvre
        pas, le montant reste calculé — il faut bien comparer les scénarios
        sur la même carrière —, mais il ne décrit aucune pension servie."""
        return self.motif != "non_ouverte"

    def donnees(self) -> dict:
        """L'ouverture, telle que le schéma de l'étape la décrit."""
        return {
            "schema_version": SCHEMA_VERSION,
            "personne": self.carriere.personne,
            "date_effet": date_d_effet(self.carriere),
            "requis": self.requis,
            "age": self.age,
            "motif": self.motif,
            "trimestres_cotises": self.trimestres_cotises,
            "fiabilite": self.fiabilite.name.lower(),
        }


def ouvrir(moteur: ScenarioActuel, releve: Releve) -> Ouverture:
    """Ce que le droit ouvre à la demande dont ``releve`` est le relevé.

    La durée requise de référence est la plus longue de celles des régimes de
    base en annuités ; l'âge d'ouverture, le plus précoce des leurs. Une
    carrière qui n'a que des points les lit sur ses régimes en points, dans
    une seconde passe. Quand l'âge demandé précède cet âge, la carrière
    longue peut encore ouvrir le droit ; sinon, la liquidation n'est pas
    ouverte, et le dit.
    """
    carriere = releve.carriere
    durees, droits = releve.durees, releve.droits
    annee_liquidation = carriere.annee_liquidation
    age_liquidation = carriere.age_liquidation or 0.0
    majoration_enfants = durees.enfants
    fiabilite = Fiabilite.CERTIFIEE

    # Durée requise de référence : celle du régime de base. C'est elle qui
    # commande le taux plein, donc aussi l'abattement des complémentaires —
    # un assuré au taux plein liquide sa complémentaire sans abattement,
    # quel que soit son âge.
    requis_reference = 0
    #: Âge d'ouverture des droits le plus précoce parmi les régimes de base
    #: de la carrière. Un polypensionné liquide en réalité chaque pension à
    #: l'âge de son régime ; le modèle liquide tout à la fois, et retient
    #: donc l'âge du régime le plus précoce — celui d'un régime spécial,
    #: quand il y en a un.
    age_ouverture_reference: float | None = None
    codes = droits.codes
    # Un régime et celui qui lui succède liquident ensemble, sous les règles
    # de la caisse qui aurait le dossier : les autres membres du groupe
    # sont sautés partout où un régime liquide.
    groupes = releve.groupes
    # DEUX PASSES, ET LA SECONDE NE SERT QU'À QUI N'A QUE DES POINTS.
    # Les régimes en ANNUITÉS commandent, comme partout ailleurs. Mais une
    # carrière entière en points n'en a aucun, et la boucle laissait alors
    # `age_ouverture_reference` à ``None`` : aucun âge ne lui était opposé,
    # et un chef d'exploitation pouvait liquider à cinquante ans sans que
    # rien ne le refuse, quand l'artisan de la grille se le voyait refuser
    # à la même page. `requis_reference` retombait de son côté sur 160,
    # c'est-à-dire sur une durée que plus aucune génération ne doit — et
    # c'est cette durée-là que l'abattement du régime en points opposait.
    #
    # La seconde passe ne s'ouvre donc que si la première n'a rien trouvé,
    # et les comportements des carrières en annuités ne bougent pas d'un
    # trimestre. L'Agirc-Arrco et l'Ircantec en sont écartées comme
    # ailleurs : elles n'opposent pas la durée du régime de base, et ne
    # sont jamais seules sur une carrière.
    for calculs in (("annuites",), ("points", "mixte")):
        for code in codes:
            if groupes.get(code, (code,))[0] != code:
                continue
            regime = moteur.catalogue[code]
            periode = regime.periode(
                min(annee_liquidation, derniere_annee(regime)))
            if periode is None or periode.type_calcul not in calculs:
                continue
            if periode.abattement_points in ("agirc_arrco", "ircantec"):
                continue
            # Une complémentaire qui a SES âges — la CAVOM ouvre la sienne
            # à soixante ans aux nés avant 1956 — ne dit pas quand le droit
            # s'ouvre : c'est le régime de base qu'elle accompagne toujours
            # qui le dit, et elle suit. Un régime de base en annuités qui
            # a les siens — la SNCF, la RATP, les IEG — le dit, lui.
            if periode.age_table and periode.type_calcul != "annuites":
                continue
            requis_reference = max(
                requis_reference, duree_requise(moteur, periode, carriere)[0]
            )
            age_regime = age_ouverture(moteur, periode, carriere)
            age_ouverture_reference = (
                age_regime if age_ouverture_reference is None
                else min(age_ouverture_reference, age_regime)
            )
        if age_ouverture_reference is not None:
            break
    requis_reference = requis_reference or 160

    # Trimestres réellement COTISÉS, tous régimes : ils commandent la
    # carrière longue et la majoration du minimum contributif.
    trimestres_cotises = carriere.trimestres_cumules(
        ligne for ligne in carriere.lignes
        if ligne.cotise and ligne.annee <= annee_liquidation
    )

    # Le droit ouvre-t-il cette liquidation à cet âge ? La question n'était
    # pas posée : le modèle servait une pension décotée à qui ne pouvait
    # pas encore liquider, ce qui n'est ni le droit ni un contrefactuel
    # utile. Elle l'est maintenant, et la réponse accompagne le montant.
    motif_ouverture = "age_legal"
    if age_ouverture_reference is not None and age_liquidation < age_ouverture_reference:
        anticipe = moteur.carriere_longue.age_de_depart(
            carriere, annee_liquidation,
            moteur.carriere_longue.cotises_reputes(
                carriere, trimestres_cotises,
                majoration_enfants.trimestres if majoration_enfants is not None else 0,
            ),
            requis_reference,
        )
        if anticipe is not None and age_liquidation >= anticipe[0]:
            motif_ouverture = "carriere_longue"
            age_ouverture_reference = anticipe[0]
            fiabilite = min(fiabilite, anticipe[1])
        else:
            motif_ouverture = "non_ouverte"


    return Ouverture(
        carriere=carriere,
        requis=requis_reference,
        age=age_ouverture_reference,
        motif=motif_ouverture,
        trimestres_cotises=trimestres_cotises,
        fiabilite=fiabilite,
    )


def duree_requise(moteur, periode: PeriodeRegime,
                   carriere: Carriere) -> tuple[int, Fiabilite | None]:
    """Durée requise opposable à cet assuré dans ce régime.

    La fonction publique a sa propre montée en charge, 2004-2008, lue à
    l'année d'ouverture du droit ; elle passe avant la table par
    génération, qui ne vaut pour elle qu'à compter de 2009.

    ET UN EMPLOI CLASSÉ N'A PAS LA DURÉE DE SA GÉNÉRATION. Le XXIV, B de
    l'article 10 de la loi du 14 avril 2023 pour l'État, et le II, B de
    l'article 13 du décret n° 2023-435 pour la CNRACL et le FSPOEIE, fixent
    « par dérogation à l'article L. 13 » une durée propre aux catégories
    active et super-active — 169 trimestres des nés de septembre 1966 à
    1967, 172 dès 1971, et les mêmes marches cinq ans plus tard pour la
    super-active. Le modèle leur opposait celle des sédentaires, soit
    jusqu'à trois trimestres de trop.

    UN RÉGIME SPÉCIAL QUI ÉCRIT SES TABLES PASSE AVANT LA TABLE COMMUNE : la
    SNCF, la RATP et les IEG. Leurs tables par génération ne valent qu'à
    compter de la date où l'assuré réunit les conditions
    (`legislation/duree_requise_regimes_speciaux.csv`) ; avant, c'est le
    calendrier de la réforme de 2008, lu à cette même date
    (`legislation/duree_requise_calendriers.csv`). C'est ce qui donne à un
    cheminot parti en 2010 les 154 trimestres de son droit, et non les 167
    de sa génération au régime général.

    Et ceux que ces marches ne visent pas — l'emploi classé né avant elles,
    le militaire — n'ont pas davantage la durée de leur génération : voir
    :func:`duree_requise_avant_soixante_ans`.
    """
    requis = periode.duree_requise_trimestres or 160
    propre = duree_propre(moteur, periode, carriere)
    if propre is not None:
        return propre[0], propre[2]
    if periode.bareme_decote == "fonction_publique":
        transitoire = moteur.durees_requises_fonction_publique.trimestres(
            annee_ouverture_des_droits(moteur, 
                periode, carriere,
                carriere.annee_liquidation
                if carriere.age_liquidation is not None else 9999,
            )
        )
        if transitoire is not None:
            return transitoire
    derogation = derogation_active(moteur, periode, carriere)
    if derogation is not None and derogation.duree_requise is not None:
        return derogation.duree_requise, derogation.fiabilite
    avant_soixante_ans = duree_requise_avant_soixante_ans(moteur, 
        periode, carriere, derogation)
    if avant_soixante_ans is not None:
        return avant_soixante_ans
    if periode.duree_requise_par_generation:
        # LA RÉFORME DE 2023 NE VAUT QU'À COMPTER DU 1er SEPTEMBRE 2023 : le
        # B du XXX de son article 10 la réserve aux pensions prenant effet à
        # cette date. Avant, les nés à compter du 1er septembre 1961 — partis
        # par un départ anticipé — doivent la durée de la version de 2014 de
        # L. 161-17-3 : 168 trimestres au né en 1962 parti en carrière
        # longue en janvier 2022, à qui le module en opposait 169.
        if (carriere.age_liquidation is not None
                and carriere.generation >= GENERATION_REFORME_2023
                and (carriere.annee_liquidation, carriere.mois_liquidation)
                < REFORME_2023_EFFET):
            avant = moteur.durees_requises_avant_reforme_2023.trimestres(
                carriere.generation)
            if avant is not None:
                return avant
        # LA SUSPENSION NE VAUT QU'À COMPTER DU 1er SEPTEMBRE 2026 : avant,
        # les nés en 1964 et 1965 doivent la durée de la loi de 2023, que
        # le module ne leur opposait plus.
        if (carriere.age_liquidation is not None
                and GENERATIONS_SUSPENSION[0] <= carriere.generation
                < GENERATIONS_SUSPENSION[1]
                and (carriere.annee_liquidation, carriere.mois_liquidation)
                < SUSPENSION_2026_EFFET):
            avant = moteur.durees_requises_avant_suspension.trimestres(
                carriere.generation)
            if avant is not None:
                return avant
        par_generation = moteur.durees_requises.trimestres(carriere.generation)
        if par_generation is not None:
            return par_generation
    return requis, None


def duree_requise_avant_soixante_ans(
        moteur, periode: PeriodeRegime, carriere: Carriere,
        derogation: DerogationActive | None,
) -> tuple[int, Fiabilite | None] | None:
    """La durée d'un droit qui s'ouvre avant soixante ans, ou ``None``.

    Le militaire qui réunit ses services, l'emploi classé qui atteint son
    âge anticipé ou minoré ne se voient pas opposer la durée de leur
    génération, mais « celle exigée des fonctionnaires atteignant [soixante
    ans] l'année à compter de laquelle la liquidation peut intervenir » —
    article 5, VI, de la loi du 21 août 2003, puis L. 13, III, du code des
    pensions, que le XXIV de la loi du 14 avril 2023 garde en vigueur pour
    l'emploi classé né avant ses propres marches et pour le militaire qui
    pouvait liquider avant le 1er septembre 2023. Un super-actif né en 1965
    dont le droit s'ouvre à cinquante-deux ans, en 2017, se voit donc
    opposer la durée de la génération 1957, 166 trimestres, et non les 169
    de la sienne ; c'est ce que publie la Cour des comptes (tableau n° 20
    de son rapport de septembre 2026).

    Le militaire qui peut liquider à compter du 1er septembre 2023 relève du
    C, 2°, du même XXIV : 169 trimestres, un de plus en 2025 et en 2027,
    172 à compter de 2028.

    ET LE FONCTIONNAIRE SÉDENTAIRE DONT LA CARRIÈRE LONGUE OUVRE LE DROIT
    AVANT SOIXANTE ANS AUSSI. Le C vise « les fonctionnaires civils, autres
    que ceux mentionnés aux A et B du présent XXIV, et les militaires
    remplissant les conditions de liquidation de la pension avant l'âge de
    soixante ans » : le A ne porte que les générations d'avant septembre
    1961, le B les emplois classés. Et L. 13, III, que le C, 1°, garde pour
    qui pouvait liquider avant septembre 2023, disait déjà « les
    fonctionnaires », sans restriction. La CNRACL l'écrit pour la carrière
    longue, l'invalidité, le handicap et les parents de trois enfants :
    « un fonctionnaire né en 1967 qui a un droit ouvert à 58 ans au titre
    des carrières longues en 2025 aura une durée d'assurance requise de
    170 trimestres (au lieu de 172 trimestres en fonction de sa
    génération) ». Le modèle ne l'opposait qu'au militaire ; de ces
    départs, il ne connaît que la carrière longue.

    Avant 2009 la table ne répond pas : de 2004 à 2008, celle de la loi de
    2003 a déjà répondu (:func:`duree_requise` la lit d'abord, à la même
    clé), et avant 2004 c'est la durée que la fiche portait l'année
    d'ouverture — 150 trimestres, et non celle de la liquidation.

    ``derogation`` est celle que :func:`duree_requise` vient de lire, pour
    ne pas refaire le décompte des services classés.
    """
    if periode.bareme_decote != "fonction_publique":
        return None
    militaire = droit_militaire(moteur, periode, carriere)
    carriere_longue = False
    if militaire is not None:
        age = militaire.age_ouverture
    elif derogation is not None:
        age = derogation.age_ouverture
    elif periode.regime in coordonner.REGIMES_CODE_DES_PENSIONS:
        age = ouverture_carriere_longue(moteur, periode, carriere)
        if age is None:
            return None
        carriere_longue = True
    else:
        return None
    if age >= moteur.AGE_DUREE_A_L_OUVERTURE:
        return None
    ouverture = carriere.date_naissance.plus_mois(en_mois(age))
    if carriere.age_liquidation is not None:
        ouverture = DateMois.depuis_rang(min(
            ouverture.rang,
            carriere.date_naissance.plus_mois(
                en_mois(carriere.age_liquidation)).rang,
        ))
    if ((militaire is not None or carriere_longue)
            and ouverture.rang >= moteur.DUREE_XXIV_C_DEPUIS.rang):
        return moteur.durees_requises_avant_soixante_ans.depuis_2023(ouverture)
    for table in (moteur.durees_requises_fonction_publique.trimestres,
                  moteur.durees_requises_avant_soixante_ans.par_annee):
        lue = table(ouverture.annee)
        if lue is not None:
            return lue
    en_vigueur = moteur.catalogue[periode.regime].periode(ouverture.annee)
    if en_vigueur is None or en_vigueur.duree_requise_trimestres is None:
        return None
    return en_vigueur.duree_requise_trimestres, None


def ouverture_carriere_longue(moteur, periode: PeriodeRegime,
                               carriere: Carriere) -> float | None:
    """L'âge où la carrière longue ouvre le droit de ce fonctionnaire, s'il
    l'ouvre au plus tard à la liquidation ; ``None`` sinon.

    La condition de durée est celle de la génération : « au moins égale à
    la durée mentionnée à l'article L. 161-17-3 du code de la sécurité
    sociale » (D. 16-1 du code des pensions, rédaction du décret
    n° 2026-345). Pendant qu'on la lit, :func:`duree_requise` ne doit donc
    pas rendre la durée que ce droit fait opposer ensuite au taux plein —
    ce serait la condition qui se lirait elle-même.
    """
    if moteur._ouverture_carriere_longue_en_cours or carriere.age_liquidation is None:
        return None
    moteur._ouverture_carriere_longue_en_cours = True
    try:
        age = age_carriere_longue(moteur, carriere, [(periode.regime, periode)])
    finally:
        moteur._ouverture_carriere_longue_en_cours = False
    if age is None or age > carriere.age_liquidation + 1e-9:
        return None
    return age


def statut_dominant(moteur, carriere: Carriere,
                     classements: dict[str, str]) -> str | None:
    """Le classement que la carrière a exercé le plus longtemps.

    La règle est celle du code : quand plusieurs emplois classés se
    succèdent, « la catégorie applicable pour bénéficier de l'âge de départ
    minoré est celle associée à l'emploi que le fonctionnaire a occupé le
    plus longtemps » (L. 24, I, 1°). À égalité, le classement le plus
    favorable — la super-active — l'emporte, parce que la durée qu'elle
    exige est la plus longue : l'assuré qui la remplit remplit l'autre.
    """
    durees: dict[str, float] = {}
    borne = coordonner.borne_carriere(carriere)
    for statut, classement in classements.items():
        duree = carriere.duree_de_service((statut,), borne)
        if duree > 0:
            durees[classement] = durees.get(classement, 0.0) + duree
    if not durees:
        return None
    return max(durees, key=lambda cle: (durees[cle], cle == "super_active",
                                        cle == "officier"))


def derogation_active(moteur, periode: PeriodeRegime,
                       carriere: Carriere) -> DerogationActive | None:
    """L'âge anticipé que le classement de l'emploi ouvre, ou ``None``.

    Quatre conditions, et la fiche en porte une : le régime doit servir la
    catégorie active — l'avoir dans ses ``avantages_non_contributifs`` ; le
    statut déclaré doit être classé ; le régime doit être l'un de ceux que
    ce statut route, sans quoi la dérogation déborderait sur un régime
    spécial que la même carrière traverserait (cf.
    :func:`~retraite_notionnelle.droit.coordonner.regimes_routes`) ;
    et la carrière doit porter la durée de services classés que l'article
    L. 24 exige — dix-sept ans, vingt-sept pour la super-active. Sans cette
    dernière, l'assuré reste au droit commun, ce qui est exactement ce que
    le texte dit : la faculté « est ouverte à la condition que le
    fonctionnaire puisse se prévaloir, au total, d'au moins dix-sept ans de
    services accomplis […] dits services actifs ».
    """
    if "categorie_active" not in periode.avantages_non_contributifs:
        return None
    classements = moteur.affiliations.classements_actifs
    if not classements:
        return None
    classement = statut_dominant(moteur, carriere, classements)
    if classement is None:
        return None
    derogation = moteur.ages_categorie_active.derogation(
        classement, carriere.generation
    )
    if derogation is None:
        return None
    statuts = [code for code, valeur in classements.items()
               if valeur == classement]
    if periode.regime not in coordonner.regimes_routes(moteur, statuts):
        return None
    servies = carriere.duree_de_service(statuts, coordonner.borne_carriere(carriere))
    if servies + 1e-9 < derogation.services_requis:
        return None
    return derogation


def droit_militaire(moteur, periode: PeriodeRegime,
                     carriere: Carriere) -> "DroitMilitaire | None":
    """Ce que la pension militaire oppose à cet assuré, ou ``None``.

    Elle ne s'ouvre pas à un âge mais à une DURÉE — dix-sept ans de services
    effectifs pour un non-officier, vingt-sept pour un officier (L. 24, II).
    Qui la réunit liquide aussitôt, à trente-cinq ans s'il s'est engagé à
    dix-huit ; qui ne la réunit pas mais a quinze ans de services attend
    l'âge de jouissance différée de l'article L. 25 ; qui a moins de quinze
    ans n'a pas de pension militaire, et c'est l'âge légal qui vaut.

    La durée opposée dépend de l'ANNÉE où l'ancienne durée — quinze ou
    vingt-cinq ans — a été atteinte, et non de la génération : c'est la clé
    que le décret n° 2011-2103 a choisie.
    """
    if "categorie_active" not in periode.avantages_non_contributifs:
        return None
    categories = moteur.affiliations.categories_militaires
    if not categories:
        return None
    categorie = statut_dominant(moteur, carriere, categories)
    if categorie is None:
        return None
    statuts = [code for code, valeur in categories.items()
               if valeur == categorie]
    if periode.regime not in coordonner.regimes_routes(moteur, statuts):
        return None
    base = moteur.durees_services_militaires.duree_de_base(categorie)
    if base is None:
        return None
    date_base = carriere.date_de_service(statuts, base)
    annee_base = (9999.0 if date_base is None
                  else date_base.annee + (date_base.mois - 1) / 12)
    requises = moteur.durees_services_militaires.annees_requises(
        categorie, annee_base
    )
    if requises is None:
        return None
    annees_requises, fiabilite = requises
    servies = carriere.duree_de_service(statuts, coordonner.borne_carriere(carriere))
    age_requis = carriere.age_de_service(statuts, annees_requises)
    if servies + 1e-9 >= annees_requises and age_requis is not None:
        age_ouverture, differee = age_requis, False
    elif servies + 1e-9 >= SERVICES_MINIMAUX_MILITAIRES:
        par_generation = moteur.ages_jouissance_militaire.age(carriere.generation)
        if par_generation is None:
            return None
        age_ouverture, differee = par_generation[0], True
        fiabilite = min(fiabilite, par_generation[1])
    else:
        return None
    return DroitMilitaire(
        age_ouverture=age_ouverture,
        trimestres_servis=round(servies * 4),
        trimestres_cible=round(annees_requises * 4) + TRIMESTRES_DECOTE_MILITAIRE,
        jouissance_differee=differee,
        fiabilite=fiabilite,
    )


def age_ouverture(moteur, periode: PeriodeRegime, carriere: Carriere) -> float:
    """Âge légal opposable à cet assuré dans ce régime.

    Trois droits se superposent, du plus particulier au plus général : la
    pension militaire, qui s'ouvre à une durée de services ; la catégorie
    active, qui avance l'âge de cinq ou de dix années ; le droit commun,
    lu à la génération ou dans la fiche.
    """
    militaire = droit_militaire(moteur, periode, carriere)
    if militaire is not None:
        return militaire.age_ouverture
    derogation = derogation_active(moteur, periode, carriere)
    if derogation is not None:
        return derogation.age_ouverture
    commun = age_ouverture_commun(moteur, periode, carriere)
    speciale = ouverture_pension_speciale(moteur, periode, carriere)
    if speciale is not None:
        return speciale
    par_services = ouverture_par_services(moteur, periode, carriere)
    if par_services is not None and par_services < commun:
        return par_services
    return commun


def services_dans_le_regime(moteur, periode: PeriodeRegime,
                             carriere: Carriere) -> tuple[list[str], float]:
    """Les statuts que le régime route, et les années servies dans ceux-ci
    jusqu'à la liquidation."""
    statuts = [code for code in moteur.affiliations.codes
               if periode.regime in coordonner.regimes_routes(moteur, [code])]
    return statuts, carriere.duree_de_service(
        statuts, coordonner.borne_carriere(carriere))


def ouverture_pension_speciale(moteur, periode: PeriodeRegime,
                                carriere: Carriere) -> float | None:
    """L'âge de la pension SPÉCIALE des marins, ou ``None`` si l'assuré a
    les quinze ans de services qui ouvrent une autre pension.

    Moins de quinze ans de services n'ouvrent ni la pension d'ancienneté
    ni la proportionnelle, mais une pension spéciale (L. 5552-11 du code
    des transports), dont « la concession et l'entrée en jouissance […]
    interviennent au moment de l'entrée en jouissance de la pension de
    retraite servie par l'Etat ou un régime légal de sécurité sociale,
    sous réserve que l'intéressé ait atteint » cinquante-cinq ans, et à
    défaut d'une telle pension à soixante ans (L. 5552-12 ; R. 5 du code
    des pensions de retraite des marins).

    Le modèle liquide tous les régimes à la même date : la pension
    spéciale suit donc le plus précoce des AUTRES régimes de base que la
    carrière traverse, jamais avant l'âge de la fiche ; sans autre régime
    de base, c'est l'âge de la fiche sans autre pension. La page de l'ENIM
    écrit « l'âge légal […] du régime général » dans son texte et
    « 60 ans » dans son exemple : c'est R. 5 qui fait foi.
    """
    seuil = periode.pension_speciale_services_annees
    isole = periode.pension_speciale_age_sans_autre_pension
    if seuil is None or isole is None:
        return None
    _, servies = services_dans_le_regime(moteur, periode, carriere)
    if servies + 1e-9 >= seuil:
        return None
    annuites, autres = periodes_parcourues(moteur, carriere)
    bases = [p for code, p in annuites + periodes_opposant_une_duree(autres)
             if code != periode.regime]
    if not bases:
        return isole
    return max(periode.age_ouverture,
               min(age_ouverture(moteur, p, carriere) for p in bases))


def ouverture_par_services(moteur, periode: PeriodeRegime,
                            carriere: Carriere) -> float | None:
    """L'âge que la durée de services dans le régime ouvre, ou ``None``.

    Les marins acquièrent la pension d'ancienneté « lorsque se trouve
    remplie la double condition de cinquante ans d'âge et de vingt-cinq
    années de services » (R. 2 de leur code). Les cinquante-cinq ans que
    le même article fixe ensuite ne sont que la borne de l'entrée en
    jouissance de celui qui CONTINUE à naviguer (L. 5552-5 du code des
    transports) : qui cesse à cinquante ans avec vingt-cinq ans de mer
    liquide, et l'ENIM l'écrit — « Gaspard, marin, a 50 ans et réunit
    25 ans de services […] Il peut prétendre au versement d'une pension
    d'ancienneté ». Le plafond de vingt-cinq annuités de R. 13 n'avait
    pas d'autre objet que ce départ-là.

    Les services sont ceux des statuts que le régime route, comptés
    jusqu'à la liquidation ; l'âge est le plus tardif de l'âge écrit et de
    celui où la durée est atteinte.
    """
    if (periode.age_ouverture_services is None
            or periode.services_ouverture_annees is None):
        return None
    statuts, servies = services_dans_le_regime(moteur, periode, carriere)
    requis = periode.services_ouverture_annees
    if servies + 1e-9 < requis:
        return None
    atteint = carriere.age_de_service(statuts, requis)
    if atteint is None:
        return None
    return max(periode.age_ouverture_services, atteint)


def age_ouverture_commun(moteur, periode: PeriodeRegime,
                          carriere: Carriere) -> float:
    """L'âge légal de droit commun, sans égard au classement de l'emploi.

    C'est lui, et non l'âge anticipé, qui commande la SURCOTE : le III de
    l'article L. 14 ne la donne qu'« au-delà de l'âge mentionné à l'article
    L. 161-17-2 ». Compter la surcote depuis cinquante-sept ans aurait payé
    deux fois l'avantage du classement. Mais l'emploi classé n'attend pas
    l'âge légal de SA génération : le D du XXIV de l'article 10 de la loi
    du 14 avril 2023 lui donne l'âge anticipé majoré de cinq années, qui
    est l'âge légal de la génération née cinq ans plus tôt — voir
    :func:`age_surcote`. Cette docstring disait « l'âge légal dans les deux
    cas », et c'était faux de toute la montée en charge.
    """
    if periode.age_table:
        propres = moteur.ages_regimes.ages(periode.age_table, carriere.generation)
        if propres is not None and propres[0] is not None:
            return propres[0]
    if periode.age_ouverture_par_generation:
        par_generation = moteur.ages_ouverture.age(carriere.generation)
        if par_generation is not None:
            return par_generation[0]
    return periode.age_ouverture


def age_surcote(moteur, periode: PeriodeRegime, carriere: Carriere) -> float:
    """Âge au-delà duquel les trimestres cotisés ouvrent la surcote.

    L'âge légal de droit commun, sauf pour la SNCF et la RATP, dont les
    décrets écrivent leur propre calendrier : le compter depuis leur âge
    d'ouverture payait la surcote dix ans trop tôt à un agent de conduite.

    **Et sauf pour l'emploi classé de la fonction publique.** Le D du XXIV
    de l'article 10 de la loi du 14 avril 2023 déroge au III de L. 14 :
    l'âge de la surcote est l'âge anticipé majoré de cinq années pour les
    actifs nés à compter du 1er septembre 1966, l'âge minoré majoré de dix
    pour les super-actifs nés à compter du 1er septembre 1971, et, avant ces
    dates, « celui applicable avant l'entrée en vigueur » de la réforme —
    soixante-deux ans. Le II, D, de l'article 13 du décret n° 2023-435 dit
    la même chose pour la CNRACL et le FSPOEIE, et le décret n° 2026-344
    l'écrit en toutes lettres : soixante-deux ans et neuf mois pour les
    actifs nés de 1968 à mars 1970, soixante-quatre ans à partir de 1974.
    Le modèle leur opposait l'âge légal de LEUR génération, en croyant que
    l'âge anticipé majoré de cinq ans y revenait ; il revient à celui de la
    génération née cinq ans plus tôt, et un fonctionnaire actif né en 1969
    attendait soixante-quatre ans une surcote que la loi lui ouvre à
    soixante-deux ans et neuf mois.
    """
    if periode.age_surcote_regimes_speciaux:
        propre = moteur.ages_surcote_regimes_speciaux.age(carriere.generation)
        if propre is not None:
            return propre[0]
    commun = age_ouverture_commun(moteur, periode, carriere)
    if moteur.catalogue[periode.regime].famille != "fonction_publique":
        return commun
    derogation = derogation_active(moteur, periode, carriere)
    if derogation is None:
        return commun
    classement = statut_dominant(moteur, carriere, moteur.affiliations.classements_actifs)
    marche = SURCOTE_EMPLOIS_CLASSES.get(classement or "")
    if marche is None:
        return commun
    premiere_generation, majoration = marche
    if carriere.generation + 1e-9 >= premiere_generation:
        return derogation.age_ouverture + majoration
    return min(commun, AGE_SURCOTE_AVANT_2023)


def periodes_parcourues(
        moteur, carriere: Carriere
) -> tuple[list[tuple[str, PeriodeRegime]], list[tuple[str, PeriodeRegime]]]:
    """Les régimes que cette carrière traverse, séparés en deux paquets.

    Le premier est celui des régimes en ANNUITÉS, qui commandent le taux
    plein et l'ouverture du droit ; le second recueille les autres. C'est
    la même énumération que celle de :func:`ouvrir`, mais tirée de la
    seule carrière : elle répond donc AVANT que la pension ne soit
    calculée, ce qu'il faut pour dater un départ. Chaque entrée porte le
    code du régime avec sa période, parce que la majoration pour enfants
    se demande à un régime nommé.
    """
    annee_liquidation = carriere.annee_liquidation
    codes: set[str] = set()
    for ligne in carriere.lignes:
        if ligne.annee > annee_liquidation:
            continue
        codes.update(coordonner.regimes_de(moteur, 
            ligne, ligne.annee,
            carriere.date_entree(ligne.affiliation),
            revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
            plafond=moteur.macro.plafond_securite_sociale(ligne.annee),
        ))
    annuites: list[tuple[str, PeriodeRegime]] = []
    autres: list[tuple[str, PeriodeRegime]] = []
    for code in sorted(codes):
        if code not in moteur.catalogue:
            continue
        regime = moteur.catalogue[code]
        periode = regime.periode(min(annee_liquidation, derniere_annee(regime)))
        if periode is None:
            continue
        (annuites if periode.type_calcul == "annuites" else autres).append(
            (code, periode)
        )
    return annuites, autres


def age_ouverture_droit(moteur, carriere: Carriere) -> float | None:
    """L'âge auquel le droit OUVRE la liquidation de cette carrière.

    C'est la même question que celle posée dans :func:`ouvrir` — le plus
    précoce des régimes de base parcourus, chacun lisant l'âge que sa
    génération lui oppose —, mais posée AVANT la pension et sans la
    calculer. Elle a un usage propre : dater le départ d'un cas type. Une
    grille qui fait partir toutes les générations au même âge fait partir
    celle de 1940 à un âge que la loi de 2023 lui opposera soixante ans
    plus tard ; c'est par cette méthode-ci qu'elle cesse de le faire.

    Ce sont les régimes en ANNUITÉS qui commandent, comme dans la
    liquidation. Quand la carrière n'en a aucun — le libéral, dont le
    régime de base est en points —, les autres répondent : sans cela la
    question resterait sans réponse pour lui seul, et il serait le seul à
    garder un âge écrit à la main.

    ``None`` quand aucun régime connu n'est parcouru, ce qui arrive avant
    que le premier ne soit créé. L'appelant décide alors : il n'y a pas
    d'âge à proposer, et non un âge de zéro.
    """
    carriere = coordonner.retablir(moteur, carriere)
    annuites, autres = periodes_parcourues(moteur, carriere)
    autres = sans_ages_propres(autres)
    retenues = annuites or autres
    if not retenues:
        return None
    ouverture = min(age_ouverture(moteur, periode, carriere)
                    for _, periode in retenues)
    anticipe = age_carriere_longue(moteur, 
        carriere, annuites or periodes_opposant_une_duree(autres))
    if anticipe is not None and anticipe < ouverture:
        return anticipe
    return ouverture


def sans_ages_propres(
        periodes: list[tuple[str, PeriodeRegime]],
) -> list[tuple[str, PeriodeRegime]]:
    """Les périodes en points, moins les complémentaires qui ont leurs âges.

    Une complémentaire qui a SES âges — la CAVOM, la CARPIMKO et la CAVP
    ouvraient la leur à soixante ans aux générations d'avant 1956 et la
    servaient au taux plein à soixante-cinq — ne dit pas quand le droit
    s'ouvre ni quand il est entier : c'est le régime de base qu'elle
    accompagne toujours qui le dit, et :func:`ouvrir` l'écarte déjà. Les
    deux règles d'âge des cas types la gardaient, et proposaient soixante
    ans à un officier ministériel né en 1955 que le calcul refusait à cet
    âge. Si rien d'autre ne reste, on la garde.
    """
    communes = [(code, periode) for code, periode in periodes
                if not periode.age_table]
    return communes or periodes


def age_carriere_longue(moteur, carriere: Carriere,
                         periodes: list[tuple[str, PeriodeRegime]]
                         ) -> float | None:
    """L'âge que le départ anticipé pour carrière longue proposerait à
    cette carrière, ou ``None`` s'il ne lui ouvre rien.

    C'est la seule porte avant l'âge légal qui se déduise de la carrière
    elle-même, et :func:`ouvrir` la connaissait déjà — mais comme une
    dérogation qu'on lui demande à un âge donné, pas comme un âge qu'il
    propose. Un salarié entré à dix-huit ans et né en 1965 partait donc, en
    cas type, à soixante-trois ans et trois mois, quand le droit lui ouvre
    soixante-deux ans au taux plein : la grille faisait attendre l'âge
    légal à ceux-là mêmes que la loi en dispense. La durée requise et les
    trimestres cotisés sont ceux que :func:`ouvrir` oppose au même
    départ.

    ``periodes`` sont celles qui OPPOSENT une durée, et non les seules
    périodes en annuités : **les deux régimes de base en points ouvrent la
    carrière longue**, et le lire ailleurs serait une lecture de travers.
    L'article L. 732-18-1 du code rural la donne aux non-salariés agricoles
    — « l'âge prévu à l'article L. 732-18 est abaissé pour les personnes
    ayant exercé une activité non salariée agricole qui ont commencé leur
    activité avant un des quatre âges, dont le plus élevé ne peut excéder
    vingt et un ans » —, et le II de l'article L. 643-3 du code de la
    sécurité sociale la donne aux professions libérales par renvoi à
    L. 351-1-1, « les références au régime général […] étant remplacées par
    celles au régime d'assurance vieillesse de base des professions
    libérales ».

    Les deux règles d'âge doivent la lire sur la MÊME liste. Ne l'ouvrir
    qu'au taux plein faisait rendre à celui-ci un âge antérieur à celui que
    :func:`age_ouverture_droit` accordait — soixante-trois ans contre
    soixante-quatre pour un chef d'exploitation né en 2000 —, c'est-à-dire
    deux règles du même droit qui se contredisent.
    """
    if not periodes:
        return None
    requis = max(duree_requise(moteur, periode, carriere)[0]
                 for _, periode in periodes) or 160
    annee_liquidation = carriere.annee_liquidation
    cotises = carriere.trimestres_cumules(
        ligne for ligne in carriere.lignes
        if ligne.cotise and ligne.annee <= annee_liquidation
    )
    majoration = compter.majoration_pour_enfants(moteur, 
        carriere, {code: cotises for code, _ in periodes}, annee_liquidation
    )
    cotises = moteur.carriere_longue.cotises_reputes(
        carriere, cotises, majoration.trimestres if majoration is not None else 0
    )
    return moteur.carriere_longue.age_propose(
        carriere, annee_liquidation, cotises, requis, carriere.age_liquidation
    )


def age_taux_plein_droit(moteur, carriere: Carriere) -> float | None:
    """L'âge auquel cette carrière obtient le TAUX PLEIN, et non seulement
    le droit de partir.

    Les deux âges ne se confondent pas, et l'écart entre eux est l'un des
    ressorts du système : la loi ouvre le droit à soixante-quatre ans, mais
    elle ne le sert entier qu'à qui a la durée requise — cent soixante-douze
    trimestres pour les générations d'après 1964. Un cadre entré à
    vingt-trois ans ne les a pas à soixante-quatre : partir là serait partir
    avec une décote de huit trimestres, ce que personne ne fait. Les cas
    types partent donc au taux plein, comme ceux du Conseil d'orientation
    des retraites.

    Trois termes, et le plus tardif des deux premiers l'emporte, sous le
    plafond du troisième :

    * l'âge d'ouverture, qui n'ouvre rien avant lui ;
    * l'âge auquel la DURÉE requise est atteinte. Il se déduit sans
      simuler : il manque à cette carrière ``requis - acquis`` trimestres,
      et une année pleine en rend quatre. La soustraction est signée — une
      carrière qui a déjà trop de trimestres l'avait donc atteinte plus
      tôt, et la règle le lit dans le même calcul ;
    * l'âge d'annulation de la décote, qui donne le taux plein sans
      condition de durée. C'est lui qui borne : au-delà, attendre ne
      rapporte plus de taux, et les cas types ne surcotent pas.

    La durée acquise compte les trimestres que le droit accorde au titre
    des enfants — majoration de durée d'assurance du régime général,
    bonification de la fonction publique —, lus au régime qui les porte
    comme :func:`~retraite_notionnelle.droit.liquidation.liquider` le fait. Sans eux, une mère de deux enfants
    était datée trois ans après l'âge où sa pension est entière, et partait
    en surcote quand le droit la servait déjà en entier.

    Et le départ anticipé pour carrière longue passe avant les trois
    termes : il n'ouvre qu'à qui a sa durée COTISÉE, donc au taux plein.

    ``None`` dans le même cas que :func:`age_ouverture_droit`.
    """
    carriere = coordonner.retablir(moteur, carriere)
    annuites, autres = periodes_parcourues(moteur, carriere)
    autres = sans_ages_propres(autres)
    retenues = annuites or autres
    if not retenues:
        return None
    ouverture = min(age_ouverture(moteur, periode, carriere)
                    for _, periode in retenues)
    opposent = annuites or periodes_opposant_une_duree(autres)
    if not opposent:
        return ouverture
    annulation = min(age_taux_plein(moteur, periode, carriere)
                     for _, periode in retenues)
    requis = max(duree_requise(moteur, periode, carriere)[0]
                 for _, periode in opposent)
    if not requis:
        return ouverture
    annee_liquidation = carriere.annee_liquidation
    acquis = carriere.trimestres_cumules(
        ligne for ligne in carriere.lignes
        if ligne.annee <= annee_liquidation
    )
    majoration = compter.majoration_pour_enfants(moteur, 
        carriere, {code: acquis for code, _ in opposent}, annee_liquidation
    )
    if majoration is not None:
        acquis += majoration.trimestres
    duree = carriere.age_liquidation + (requis - acquis) / 4.0
    taux_plein = min(annulation, max(ouverture, duree))
    anticipe = age_carriere_longue(moteur, carriere, opposent)
    if anticipe is not None and anticipe < taux_plein:
        return anticipe
    return taux_plein


def periodes_opposant_une_duree(
        periodes: list[tuple[str, PeriodeRegime]],
) -> list[tuple[str, PeriodeRegime]]:
    """Parmi des périodes NON annuitaires, celles qui opposent une durée.

    Une carrière entière en points n'a aucune période en annuités, et la
    règle du taux plein rendait alors l'âge d'OUVERTURE — c'est-à-dire
    qu'elle faisait liquider au premier âge permis, sans regarder la durée.
    La pension, elle, était bien abattue : ``_abattement_points`` lit la
    décote de la fiche. Le modèle faisait donc partir au taux plein des
    carrières que le même modèle servait minorées. Le libéral né en 1955
    partait à soixante-quatre ans avec cent quarante-huit trimestres sur
    cent soixante-six requis, soit dix-huit trimestres de réduction que la
    règle disait inexistants.

    Le droit oppose bien cette durée aux régimes en points : l'article
    L. 643-3 du code de la sécurité sociale la pose pour les professions
    libérales — « lorsque l'intéressé a accompli la durée d'assurance fixée
    en application du deuxième alinéa de l'article L. 351-1 dans le présent
    régime et dans un ou plusieurs autres régimes », sinon « coefficients de
    réduction […] en fonction de l'âge […] et de la durée d'assurance » —,
    et le II de l'article L. 732-24 du code rural pour les non-salariés
    agricoles.

    Deux familles sont écartées, et c'est le sens de cette fonction.
    L'Agirc-Arrco et l'Ircantec n'opposent PAS la durée du régime de base :
    elles ont leurs propres coefficients d'anticipation, en deux tables
    dont ``_abattement_points`` retient la plus avantageuse. Elles ne sont
    de toute façon jamais seules — ce sont des complémentaires, et la
    carrière qui les porte a des périodes en annuités.
    """
    return [(code, periode) for code, periode in periodes
            if periode.abattement_points not in ("agirc_arrco", "ircantec")]


def age_taux_plein(moteur, periode: PeriodeRegime, carriere: Carriere) -> float:
    """Âge d'annulation de la décote opposable à cet assuré.

    Pour un emploi classé, ce n'est pas soixante-sept ans mais la limite
    d'âge du grade — soixante-deux ans en catégorie active, cinquante-sept
    en super-active — puis, depuis la réforme de 2023, l'âge que l'article
    L. 14 bis attache au classement. Le barème de la fonction publique en
    retranche ensuite les trimestres de sa propre montée en charge.
    """
    derogation = derogation_active(moteur, periode, carriere)
    if derogation is not None:
        return derogation.age_annulation
    if periode.age_table:
        propres = moteur.ages_regimes.ages(periode.age_table, carriere.generation)
        if propres is not None and propres[1] is not None:
            return propres[1]
    if periode.age_taux_plein_par_generation:
        par_generation = moteur.ages_annulation_decote.age(carriere.generation)
        if par_generation is not None:
            return par_generation[0]
    return periode.age_taux_plein


def annee_ouverture_des_droits(moteur, periode: PeriodeRegime,
                                carriere: Carriere,
                                annee_liquidation: int) -> int:
    """Année où les conditions d'ouverture du droit sont réunies.

    C'est le millésime auquel se lisent les barèmes de décote en table —
    celui de la fonction publique (loi du 21 août 2003, article 66 III)
    comme celui des régimes spéciaux (décrets de 2008). L'assuré les réunit
    quand il atteint l'âge d'ouverture de son régime, au mois près ; s'il
    liquide avant — carrière longue, catégorie active —, il les réunit au
    plus tôt à la liquidation, et c'est cette année-là qui vaut.
    """
    ouverture = carriere.date_naissance.plus_mois(
        en_mois(age_ouverture(moteur, periode, carriere))
    ).annee
    return min(annee_liquidation, ouverture)


def mois_ouverture_des_droits(moteur, periode: PeriodeRegime,
                               carriere: Carriere) -> int:
    """Rang du mois où l'assuré réunit les conditions d'ouverture.

    L'âge d'ouverture atteint, ou la liquidation si elle vient avant —
    carrière longue, départ anticipé : c'est le mois que les décrets des
    régimes spéciaux visent, « les personnes remplissant les conditions ».
    """
    rang = carriere.date_naissance.plus_mois(
        en_mois(age_ouverture(moteur, periode, carriere))
    ).rang
    if carriere.age_liquidation is not None:
        rang = min(rang, carriere.date_liquidation.rang)
    return rang


def duree_propre(moteur, periode: PeriodeRegime, carriere: Carriere
                  ) -> tuple[int, int, Fiabilite | None] | None:
    """Durée requise propre au régime : trimestres, retranchés, fiabilité.

    Les tables nommées par la fiche, dans l'ordre, puis son calendrier ;
    ``None`` pour une fiche qui n'en nomme aucun.
    """
    if not periode.duree_requise_table and not periode.duree_requise_calendrier:
        return None
    ouverture = mois_ouverture_des_droits(moteur, periode, carriere)
    for table in periode.duree_requise_table:
        ligne = moteur.durees_requises_regimes.ligne(
            table, carriere.generation, ouverture
        )
        if ligne is not None:
            return ligne
    if periode.duree_requise_calendrier:
        lu = moteur.calendriers_duree_requise.trimestres(
            periode.duree_requise_calendrier, ouverture
        )
        if lu is not None:
            return lu[0], 0, lu[1]
    return None
