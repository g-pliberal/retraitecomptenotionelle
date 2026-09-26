"""Compléter tous régimes (docs/architecture.md, § 7.3).

Ce que le droit ajoute aux pensions de régime en les regardant toutes
ensemble, dans l'ordre où il l'applique — et l'ordre commande le résultat :

* LE MINIMUM CONTRIBUTIF, qui ne relève que les pensions liquidées au taux
  plein, au prorata de la durée acquise dans chaque régime, et que
  l'article L. 173-2 écrête tous régimes confondus (:func:`complement_minimum`) ;
* LE MINIMUM GARANTI de la fonction publique, un barème sur la durée des
  services, qui se substitue à la pension quand il lui est supérieur ;
* LA SURCOTE PARENTALE, sur la pension relevée, pour les trimestres de
  l'année qui précède l'âge légal ;
* LA MAJORATION POUR ENFANTS enfin, sur ce plancher, plafonnée en euros à la
  complémentaire (:func:`plafond_majoration`).

L'ASPA n'en est pas : elle regarde toutes les ressources, c'est l'étape
« foyer et net » (:mod:`.foyer`).

Ce que l'étape écrit, :class:`Complements`, suit son schéma,
``data/reference/etapes/completer_tous_regimes.yaml``. Son jumeau est
``moteur/js/droit/completer.js``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from ..calendrier import DateMois, en_mois
from ..donnees.chargement import Fiabilite
from . import liquider, ouvrir
from .commun import AvantageApplique, PensionRegime, derniere_annee
from .compter import trimestres_de_la_ligne_entre as _trimestres_de_la_ligne_entre

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..donnees.regimes import PeriodeRegime
    from ..scenarios.actuel import ScenarioActuel
    from .liquidation import Contexte
    from .liquider import Pensions
    from .ouvrir import Ouverture
    from .releve import Releve

#: La version du schéma de l'étape que :meth:`Complements.donnees` suit.
SCHEMA_VERSION = 1

#: La fiche de la carte que chaque dispositif applique.
FICHES = {
    "minimum_contributif": "minimum_contributif",
    "minimum_garanti": "minimum_garanti",
    "surcote_parentale": "surcote_parentale",
    "majoration_enfants": "majoration_dix_pour_cent",
}

#: Durée cotisée, tous régimes, qui ouvre la majoration du minimum contributif
#: au titre des périodes cotisées (article L. 351-10 du code de la sécurité
#: sociale). En deçà, seul le montant de base est dû.
TRIMESTRES_COTISES_MINIMUM_MAJORE = 120

#: Première date d'effet, (année, mois), où la surcote s'AJOUTE au minimum
#: contributif au lieu d'entrer dans la pension qu'on lui compare : décret
#: n° 2008-1509 du 30 décembre 2008, dernier alinéa de D. 351-2-1.
SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS = (2009, 4)


def complement_minimum(nue: float, plancher: float, coefficient_surcote: float,
                       date_effet: tuple[int, int]) -> float:
    """Ce que le minimum contributif ajoute à une pension, surcote comprise.

    ``nue`` est la pension calculée avant surcote, ``plancher`` le minimum
    dû au régime, ``coefficient_surcote`` le facteur de la surcote (1,025 pour
    deux trimestres à 1,25 %). La règle dépend de la date d'effet :

    - depuis le 1er avril 2009, la surcote « est calculée sur la base du
      montant de pension avant qu'il ne soit porté au montant minimum »
      (D. 351-2-1) et s'ajoute au minimum : la pension servie vaut
      ``plancher + nue × (coefficient − 1)``, et le complément ``plancher −
      nue``. Circulaire Cnav 2018-04, 3.4.2 : 621 + (645,07 − 621) + 15,52 =
      660,59 € ;
    - jusqu'au 1er mars 2009, la surcote entrait dans la pension comparée au
      minimum : ``max(nue × coefficient, plancher)``. Même circulaire, 3.4.1 :
      621 × 1,015 = 630,31 € < 633,61 €, portés à 633,61 €.

    Le module servait ``plancher × coefficient`` : il surcotait le minimum
    lui-même, ce qu'aucune des deux règles ne fait.
    """
    if nue <= 0.0:
        return 0.0
    if date_effet >= SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS:
        return max(0.0, plancher - nue)
    return max(0.0, plancher - nue * coefficient_surcote)


@dataclass(frozen=True)
class Complements:
    """Ce que l'étape « compléter tous régimes » écrit."""

    #: La personne dont les pensions sont complétées.
    personne: str
    #: Les pensions de régime une fois les minima et la surcote parentale
    #: faits, chacune avec la formule qui le dit.
    regimes: tuple[PensionRegime, ...]
    #: Ce que chaque dispositif ajoute, dans l'ordre où le droit l'applique.
    avantages: tuple[AvantageApplique, ...]
    #: Le total des pensions, complété : minima, surcote parentale et
    #: majoration pour enfants compris.
    total: float
    #: Un des deux minima a-t-il relevé une pension ?
    minimum_applique: bool
    fiabilite: Fiabilite

    def donnees(self) -> dict:
        """Les compléments, tels que le schéma de l'étape les décrit."""
        return {
            "schema_version": SCHEMA_VERSION,
            "personne": self.personne,
            "dispositifs": [
                {"code": a.code, "fiche": FICHES[a.code], "montant": a.montant,
                 "parts": [{"regime": code, "montant": part} for code, part in a.par_regime]}
                for a in self.avantages],
            "fiabilite": self.fiabilite.name.lower(),
        }


def completer(moteur: ScenarioActuel, releve: Releve, ouverture: Ouverture,
              liquidees: Pensions, contexte: Contexte | None = None) -> Complements:
    """Les pensions de ``liquidees``, complétées de ce que le droit y ajoute.

    Le contexte dit ce que le calcul neutralise : les avantages non
    contributifs, que la cascade retire pour en mesurer l'apport ; la décote
    et la surcote, pour valoriser des droits acquis — la surcote parentale
    part avec elles.
    """
    carriere = releve.carriere
    durees, droits = releve.durees, releve.droits
    annee_liquidation = carriere.annee_liquidation
    avantages_non_contributifs = (contexte is None
                                  or not contexte.neutralise("avantages_non_contributifs"))
    ignorer_penalite_age = contexte is not None and contexte.neutralise("decote_surcote")
    trimestres_cotises = ouverture.trimestres_cotises
    majoration_enfants = durees.enfants
    points_acquis = droits.points_acquis
    majoration_points = droits.majoration_points
    points_majores = droits.points_majores
    pensions = list(liquidees.regimes)
    eligibles_minimum = liquidees.minimum
    eligibles_garanti = liquidees.garanti
    total = sum(p.montant for p in pensions)
    avantages: list[AvantageApplique] = []
    fiabilite_globale = Fiabilite.CERTIFIEE
    minimum_applique = False

    if avantages_non_contributifs and eligibles_minimum:
        # Le minimum contributif ne relève que les pensions liquidées AU
        # TAUX PLEIN (L. 351-10). Sa majoration au titre des périodes
        # cotisées demande en outre 120 trimestres cotisés tous régimes ;
        # elle se proratise sur la durée COTISÉE dans le régime, quand le
        # montant de base se proratise sur sa durée d'assurance
        # (D. 351-2-2). Ce n'est pas la même fraction : une carrière
        # entrecoupée de chômage indemnisé valide sa durée d'assurance
        # sans cotiser, et n'a donc droit qu'à une part de la majoration.
        montant_base, montant_majore, plafond, fiabilite_minimum = (
            moteur.minimum_contributif.valeurs(annee_liquidation)
        )
        majoration_ouverte = (
            trimestres_cotises >= TRIMESTRES_COTISES_MINIMUM_MAJORE
        )
        #: Complément dû à chaque régime, avant écrêtement.
        complements: dict[int, float] = {}
        for eligible in eligibles_minimum:
            if not eligible.taux_plein:
                continue
            pension = pensions[eligible.indice]
            # Le minimum se compare à la pension AVANT surcote, et la
            # surcote, calculée sur cette pension nue, s'ajoute au minimum
            # (D. 351-2-1) : voir :func:`complement_minimum`, qui porte
            # aussi la règle d'avant avril 2009.
            nue = pension.montant / eligible.surcote
            plancher = montant_base * min(1.0, eligible.prorata_assurance)
            if majoration_ouverte:
                plancher += (montant_majore - montant_base) * min(
                    1.0, eligible.prorata_cotise
                )
            complement = complement_minimum(
                nue, plancher, eligible.surcote,
                (annee_liquidation, carriere.mois_liquidation),
            )
            if complement > 0:
                complements[eligible.indice] = complement
        releve_minimum = sum(complements.values())
        if releve_minimum > 0:
            # Écrêtement de l'article L. 173-2 : le complément est rogné de
            # ce qui dépasse le plafond, tous régimes confondus, et jamais
            # au-delà. La comparaison porte sur les pensions PERSONNELLES,
            # majorations pour enfants exclues — raison de plus pour que
            # celles-ci se calculent après, sur le montant relevé.
            admissible = max(0.0, min(releve_minimum, plafond - total))
            if admissible < releve_minimum:
                facteur = admissible / releve_minimum
                complements = {
                    indice: complement * facteur
                    for indice, complement in complements.items()
                }
            releve_minimum = admissible
        if releve_minimum > 0:
            for indice, complement in complements.items():
                # Le complément est DIT, pas seulement annoncé : sans lui,
                # refaire la formule donnait la pension d'avant le minimum
                # et l'écart restait inexpliqué — deux mille euros par an
                # sur une petite retraite, ce qui n'est pas un détail.
                pensions[indice] = replace(
                    pensions[indice],
                    montant=pensions[indice].montant + complement,
                    detail=(
                        f"{pensions[indice].detail} = "
                        f"{pensions[indice].montant:,.2f} €, porté au minimum "
                        f"contributif par + {complement:,.2f} €"
                    ),
                )
            total += releve_minimum
            minimum_applique = True
            fiabilite_globale = min(fiabilite_globale, fiabilite_minimum)
            avantages.append(AvantageApplique(
                code="minimum_contributif",
                libelle="Minimum contributif",
                montant=releve_minimum,
                detail=(
                    "porté au plancher, au prorata de la durée acquise"
                    + (", majoration des périodes cotisées comprise"
                       if majoration_ouverte else "")
                ),
            ))

    if avantages_non_contributifs and eligibles_garanti:
        # Le minimum garanti n'est pas un minimum proratisé mais un BARÈME
        # sur la durée de services : quinze ans en ouvrent 57,5 % de la
        # référence, trente ans 95 %, quarante ans la totalité. Il ne
        # s'ajoute pas à la pension, il s'y substitue quand il lui est
        # supérieur.
        releve_garanti = 0.0
        for eligible in eligibles_garanti:
            if not eligible.ouvert:
                continue
            plancher = moteur.minimum_garanti.montant(
                annee_liquidation, eligible.trimestres_services,
                eligible.duree_maximum,
            )
            if plancher is None:
                continue
            pension = pensions[eligible.indice]
            if 0 < pension.montant < plancher[0]:
                complement = plancher[0] - pension.montant
                releve_garanti += complement
                fiabilite_globale = min(fiabilite_globale, plancher[1])
                # Le complément est DIT, comme pour le minimum contributif :
                # sans lui, refaire la formule donnait la pension d'avant le
                # plancher, et l'écart restait sans explication.
                pensions[eligible.indice] = replace(
                    pension,
                    montant=plancher[0],
                    detail=(f"{pension.detail} = {pension.montant:,.2f} €, "
                            f"porté au minimum garanti par + {complement:,.2f} €"),
                )
        if releve_garanti > 0:
            total += releve_garanti
            avantages.append(AvantageApplique(
                code="minimum_garanti",
                libelle="Minimum garanti de la fonction publique",
                montant=releve_garanti,
                detail="barème de l'article L. 17, sur la durée de services",
            ))

    # Surcote parentale (L. 351-1-2-1) : elle vient APRÈS les minima,
    # comme la surcote ordinaire, et AVANT la majoration pour enfants, qui
    # se calcule sur la pension surcotée. Elle ne récompense pas les mêmes
    # trimestres que la surcote ordinaire — celle-ci ne compte qu'au-delà
    # de l'âge légal, celle-là dans l'année qui le précède — et les deux se
    # cumulent donc sans se recouvrir.
    parametres_parentale = (
        moteur.surcote_parentale.parametres(annee_liquidation)
        if (avantages_non_contributifs and majoration_enfants is not None
            and not ignorer_penalite_age)
        else None
    )
    if parametres_parentale is not None:
        age_legal_minimal, taux_parental, maximum, fiabilite_parentale = (
            parametres_parentale
        )
        gain_parental = 0.0
        trimestres_parentaux = 0
        for indice, pension in enumerate(pensions):
            regime = moteur.catalogue[pension.regime]
            periode = regime.periode(
                min(annee_liquidation, derniere_annee(regime))
            )
            if (periode is None or "surcote_parentale"
                    not in periode.avantages_non_contributifs):
                continue
            age_legal = ouvrir.age_ouverture(moteur, periode, carriere)
            requis = ouvrir.duree_requise(moteur, periode, carriere)[0]
            # LA FENÊTRE EST L'ANNÉE QUI PRÉCÈDE L'ÂGE LÉGAL, dès que cet
            # âge atteint 63 ans : « accomplie l'année précédant l'âge
            # mentionné à l'article L. 161-17-2, lorsque celui-ci est égal
            # ou supérieur à soixante-trois ans » (L. 351-1-2-1, 2023) ;
            # l'âge de la surcote « est abaissé d'un an » (version de 2025).
            # Le module la faisait courir de 63 ans à l'âge légal : la
            # génération 1966, âge légal 63 ans et trois mois, n'y trouvait
            # qu'un trimestre là où le texte en ouvre quatre, et la
            # génération 1965 d'avril, âge légal 63 ans, aucun.
            if age_legal < age_legal_minimal:
                continue
            # Au MOIS près : l'âge légal tombe en cours d'année depuis la
            # suspension de 2026, et une fenêtre lue à l'année entière n'y
            # trouvait qu'un trimestre pour la génération 1966.
            date_legale = carriere.date_naissance.plus_mois(en_mois(age_legal))
            debut_fenetre = date_legale.plus_mois(-12)
            # Ne comptent que les trimestres cotisés de la fenêtre
            # accomplis « au delà de la limite » de durée (L. 351-1-2-1) :
            # tous, si la durée requise est atteinte à l'ouverture de la
            # fenêtre, trimestres pour enfants compris ; ceux d'après la
            # limite, si elle l'est en cours de fenêtre ; aucun sinon.
            if requis <= 0:
                continue
            avant = majoration_enfants.trimestres + _trimestres_entre_dates(
                carriere, DateMois(carriere.annee_naissance, 1), debut_fenetre,
                cotises_seulement=False,
            )
            valides_fenetre = _trimestres_entre_dates(
                carriere, debut_fenetre, date_legale, cotises_seulement=False,
            )
            # Surtout pas `trimestres` : c'est la durée d'assurance tous
            # régimes, et l'écraser ici la faisait tomber à quatre.
            acquis_parentaux = min(
                maximum,
                _trimestres_entre_dates(carriere, debut_fenetre, date_legale,
                                        cotises_seulement=True),
                max(0, avant + valides_fenetre - requis),
            )
            if acquis_parentaux <= 0:
                continue
            supplement = pension.montant * taux_parental * acquis_parentaux
            pensions[indice] = replace(
                pension,
                montant=pension.montant + supplement,
                detail=(pension.detail + ", surcote parentale "
                        f"{taux_parental * acquis_parentaux:.2%}"),
            )
            gain_parental += supplement
            trimestres_parentaux = max(trimestres_parentaux, acquis_parentaux)
        if gain_parental > 0:
            total += gain_parental
            fiabilite_globale = min(fiabilite_globale, fiabilite_parentale)
            avantages.append(AvantageApplique(
                code="surcote_parentale",
                libelle="Surcote parentale",
                montant=gain_parental,
                detail=(f"{taux_parental * trimestres_parentaux:.2%} pour "
                        f"{trimestres_parentaux} trimestre"
                        f"{'s' if trimestres_parentaux > 1 else ''} dans "
                        "l'année qui précède l'âge légal"),
            ))

    if avantages_non_contributifs and carriere.nombre_enfants >= 2:
        majoration = 0.0
        taux_cite = 0.0
        # Le plafond de l'Agirc-Arrco s'oppose à la majoration de LA
        # complémentaire, pas à celle de chacune de ses fiches : les points
        # d'un salarié du privé sont répartis entre l'Agirc, l'Arrco et le
        # régime unifié, et plafonner chacun séparément reviendrait à
        # tripler le plafond. On les met donc dans un même seau.
        majoration_plafonnee = 0.0
        plafond_commun: float | None = None
        #: (régime, part, soumise au plafond), dans l'ordre des pensions.
        parts: list[tuple[str, float, bool]] = []
        for pension in pensions:
            if pension.montant <= 0.0:
                continue
            regime = moteur.catalogue[pension.regime]
            periode = regime.periode(min(annee_liquidation, derniere_annee(regime)))
            if periode is None:
                continue
            if "majoration_enfants" not in periode.avantages_non_contributifs:
                continue
            taux = _taux_majoration_enfants(regime, carriere.nombre_enfants,
                                            periode)
            points = points_acquis.get(pension.regime, 0.0)
            majores = points_majores.get(pension.regime, 0.0)
            if majores > 0.0 and points > 0.0:
                # CHAQUE POINT À SON TAUX, celui de son année d'acquisition
                # (`MajorationsEnfantsPoints`) : le module servait 10 % aux
                # points Arrco de 1999 à 2011, que l'accord majore de 5 %,
                # et aux points Agirc d'avant 2012, qu'il majore de 8 à
                # 24 % selon le nombre d'enfants.
                taux = (majoration_points[pension.regime]
                        + taux * (points - majores)) / points
            if taux <= 0:
                continue
            part = pension.montant * taux
            plafond = plafond_majoration(moteur, 
                pension.regime, periode, carriere, annee_liquidation
            )
            if plafond is None:
                majoration += part
            else:
                majoration_plafonnee += part
                plafond_commun = (plafond if plafond_commun is None
                                  else max(plafond_commun, plafond))
            parts.append((pension.regime, part, plafond is not None))
            taux_cite = max(taux_cite, taux)
        plafonnee = plafond_commun is not None
        retenue_plafonnee = 1.0
        if plafond_commun is not None:
            majoration += min(majoration_plafonnee, plafond_commun)
            if majoration_plafonnee > plafond_commun:
                retenue_plafonnee = plafond_commun / majoration_plafonnee
        if majoration > 0:
            total += majoration
            detail = f"jusqu'à {taux_cite:.0%} selon le régime"
            if plafonnee:
                detail += ", plafonnée en euros à la complémentaire"
            avantages.append(AvantageApplique(
                code="majoration_enfants",
                libelle=("Majoration pour trois enfants et plus"
                         if carriere.nombre_enfants >= 3
                         else "Bonification pour deux enfants"),
                montant=majoration,
                detail=detail,
                par_regime=tuple(
                    (code, part * (retenue_plafonnee if soumise else 1.0))
                    for code, part, soumise in parts
                ),
            ))


    return Complements(
        personne=carriere.personne,
        regimes=tuple(pensions),
        avantages=tuple(avantages),
        total=total,
        minimum_applique=minimum_applique,
        fiabilite=fiabilite_globale,
    )


def plafond_majoration(moteur, code: str, periode: PeriodeRegime,
                        carriere: Carriere,
                        annee_liquidation: int) -> float | None:
    """Plafond en euros de la majoration pour enfants, ou ``None``.

    Les régimes de base servent 10 % sans plafond ; l'Agirc-Arrco, elle,
    borne la majoration en euros — 2 367 € par an pour les pensions servies
    depuis le 1er novembre 2025 — et le plafond est revalorisé comme la
    valeur de service du point, à laquelle il est donc rapporté ici. Sans
    lui, les familles très nombreuses de salariés du privé étaient
    surestimées.

    Le plafond ne s'oppose qu'aux assurés nés à compter du 2 août 1951 : le
    modèle ne connaît que l'année de naissance et retient les générations à
    partir de 1952, comme il le fait des autres bornes coupées en cours
    d'année.
    """
    if periode.plafond_majoration_enfants is None:
        return None
    if carriere.annee_naissance < 1952:
        return None
    plafond = periode.plafond_majoration_enfants
    annee_reference = periode.plafond_majoration_annee
    if annee_reference is None or annee_reference == annee_liquidation:
        return plafond
    servie = liquider.valeur_du_point(moteur, code, annee_liquidation)
    publiee = liquider.valeur_du_point(moteur, code, annee_reference)
    if servie is None or publiee is None or publiee[0] <= 0:
        return plafond * moteur.macro.coefficient_prix(
            annee_reference, annee_liquidation
        )
    return plafond * servie[0] / publiee[0]


def _taux_majoration_enfants(regime, nombre_enfants: int,
                             periode: PeriodeRegime | None = None) -> float:
    """Taux de majoration pour enfants, régime par régime.

    Le régime général sert 10 % à partir de trois enfants. La fonction
    publique y ajoute 5 % par enfant au-delà du troisième. Une fiche qui porte
    son propre barème l'emporte : les régimes spéciaux, dont la plupart suivent
    la fonction publique et la Banque de France sert 8,5 % puis 4,25 % par
    enfant, les marins, qui bonifient dès deux enfants. Les points de
    l'Agirc-Arrco ont un taux par année d'acquisition, que
    :class:`~retraite_notionnelle.scenarios.actuel.MajorationsEnfantsPoints`
    porte et que l'appelant substitue à celui-ci ; leur plafond en euros est
    :func:`plafond_majoration`.
    """
    if periode is not None and periode.taux_majoration_enfants:
        bareme = periode.taux_majoration_enfants
        return bareme[min(nombre_enfants, len(bareme) - 1)]
    if nombre_enfants < 3:
        return 0.0
    if regime.famille == "fonction_publique":
        return 0.10 + 0.05 * (nombre_enfants - 3)
    return 0.10


def _trimestres_entre_dates(carriere: Carriere, debut: DateMois, fin: DateMois,
                            cotises_seulement: bool) -> int:
    """Trimestres acquis entre deux DATES, au mois près — ``fin`` exclue.

    Le pas du moteur est l'année, et les deux aides voisines comparent l'âge
    atteint dans l'année à un seuil. C'est juste quand le seuil tombe sur un
    âge entier ; c'est faux quand il tombe en cours d'année, ce qui est
    devenu la règle depuis que l'âge légal compte des mois. Chaque ligne voit
    ici ses trimestres répartis sur ses mois — les premiers de l'année pour
    celle du départ, les derniers pour celle de l'entrée —, et seuls comptent
    ceux de la plage ; la somme est arrondie au trimestre inférieur.
    """
    total = 0.0
    for ligne in carriere.lignes:
        if cotises_seulement and not ligne.cotise:
            continue
        total += _trimestres_de_la_ligne_entre(carriere, ligne, debut, fin)
    return int(total + 1e-9)
