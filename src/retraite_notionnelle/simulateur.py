"""Simulateur : assemble les données, le moteur et les six scénarios.

C'est le point d'entrée unique. Une seule instance charge les données une fois
et peut ensuite simuler autant de carrières que voulu :

    >>> from retraite_notionnelle import Parametres
    >>> from retraite_notionnelle.simulateur import Simulateur
    >>> simulateur = Simulateur(Parametres())
    >>> carriere = simulateur.carriere_simple(
    ...     annee_naissance=1960, sexe="H",
    ...     affiliation="salarie_prive_non_cadre",
    ...     age_debut=20, age_liquidation=60)
    >>> comparaison = simulateur.simuler(carriere)
    >>> print(comparaison.tableau())     # doctest: +SKIP
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from .calendrier import formater_age
from .carriere import (
    Affiliations,
    Carriere,
    LigneRelevee,
    Metier,
    salaire_moyen_annuel,
)
from .config import Parametres, PartCotisation, SourceCotisations
from .donnees.chargement import DonneeInsuffisante, Fiabilite
from .donnees.cotisants import EffectifsCotisants
from .donnees.caracteristiques import CaracteristiquesRetraites
from .donnees.distribution import DistributionPensions
from .donnees.patrimoine import PatrimoineMenages
from .donnees.vie_en_couple import VieEnCouple
from .donnees.effectifs import EffectifsRetraites
from .donnees.financement_regimes import StructureFinancement
from .donnees.macro import DonneesMacro
from .donnees.mortalite import DonneesMortalite
from .donnees.regimes import CatalogueRegimes
from .donnees.taux import CourbeTauxSansRisque
from .moteur.age_reference import AgeReference
from .moteur.capitalisation import ConstructeurCapitalisation
from .moteur.compte import ConstructeurCompte
from .moteur.conversion import Convertisseur
from .moteur.fusion import RegimeFusionne, fusionner
from .moteur.indexation import Indexation
from .remuneration import RemunerationActif, remuneration_de_la_carriere
from .revalorisation import (
    PensionAujourdhui,
    RevalorisationServie,
    RevalorisationsPensions,
    actuel_aujourd_hui,
    pension_aujourd_hui,
)
from .scenarios.actuel import ResultatActuel, ScenarioActuel
from .scenarios.notionnel import ResultatNotionnel, ScenarioNotionnel


#: Les cinq scénarios notionnels, dans l'ordre où ils s'affichent, avec le
#: numéro et le titre sous lesquels le tableau, la page et l'API les citent.
#:
#: Deux paires, puis un sixième. 2 et 3 ne portent au compte que la part
#: SALARIALE de la cotisation, 4 et 5 y ajoutent la part PATRONALE. À
#: l'intérieur de chaque paire, l'un est rétroactif et l'autre prospectif. Rien
#: d'autre ne les sépare, et c'est ce qui les rend comparables deux à deux : 4
#: se lit contre 2, 5 contre 3, et l'écart mesure exactement ce que l'employeur
#: verse. Le 6 se lit contre le 4 : même compte rétroactif, cotisation entière
#: aux taux réels jusqu'à la bascule, puis un taux unique de 18 % pour tous à
#: compter d'elle, et une garantie vieillesse individualisée, financée par
#: l'impôt, par-dessus.
SCENARIOS_NOTIONNELS = (
    ("notionnel_retroactif", 2, "Notionnel rétroactif, part salariale"),
    ("notionnel_prospectif", 3, "Notionnel dès {bascule}, part salariale"),
    ("notionnel_retroactif_employeur", 4,
     "Notionnel rétroactif, salariale + patronale"),
    ("notionnel_prospectif_employeur", 5,
     "Notionnel dès {bascule}, salariale + patronale"),
    ("notionnel_liberal", 6,
     "Notionnel rétroactif, 18 % dès {bascule}, garantie vieillesse"),
)


@dataclass(frozen=True)
class ContributionEmployeur:
    """Qui a payé le compte notionnel, et sur quelles années.

    En euros courants cumulés, sans revalorisation : la somme de ce qui a
    effectivement transité, et non un capital notionnel. C'est la mesure directe
    de ce qui sépare les scénarios 2 et 3 des scénarios 4 et 5 — le premier
    couple ne porte au compte que ``agent``, le second ``total``.

    Un non-salarié n'a pas d'employeur : ``employeur`` y est nul et les quatre
    scénarios se réduisent à deux.
    """

    #: Cotisations portées au compte par le scénario 4, agent et employeur
    #: confondus.
    total: float
    #: Part de ce total versée par l'employeur.
    employeur: float
    #: Nombre d'années où la contribution employeur PUBLIQUE réelle a été
    #: trouvée, par nature (``appelee``, ``implicite``), et où il a fallu s'en
    #: passer (``repli``). Vide pour un salarié du privé, dont la fiche porte
    #: la répartition : la question ne s'y pose pas.
    annees_par_origine: dict[str, int]

    @property
    def agent(self) -> float:
        """Ce qui reste : la cotisation que l'assuré supporte lui-même."""
        return self.total - self.employeur

    @property
    def part(self) -> float:
        """Part de l'employeur dans le total versé, entre 0 et 1."""
        return self.employeur / self.total if self.total else 0.0

    @property
    def a_un_employeur(self) -> bool:
        return self.employeur > 0

    @property
    def concerne_un_regime_public(self) -> bool:
        return bool(self.annees_par_origine)

    @property
    def annees_trouvees(self) -> int:
        return sum(nombre for origine, nombre in self.annees_par_origine.items()
                   if origine != "repli")

    @property
    def annees_repli(self) -> int:
        return self.annees_par_origine.get("repli", 0)


@dataclass
class Comparaison:
    """Les six résultats, côte à côte, pour une même carrière."""

    carriere: Carriere
    actuel: ResultatActuel
    notionnel_retroactif: ResultatNotionnel
    notionnel_prospectif: ResultatNotionnel
    notionnel_retroactif_employeur: ResultatNotionnel
    notionnel_prospectif_employeur: ResultatNotionnel
    notionnel_liberal: ResultatNotionnel
    regime_fusionne: RegimeFusionne
    parametres: Parametres
    #: Coefficient de passage des euros de l'année de liquidation aux euros
    #: constants de ``parametres.annee_euros_constants``.
    coefficient_euros_constants: float = 1.0
    #: Ce qu'un actif touche entre la bascule et son départ, sous le droit en
    #: vigueur et sous la proposition : coût du travail, brut, net. ``None``
    #: pour qui a déjà liquidé — il ne cotise plus — et pour tout statut dont
    #: ``remuneration.py`` ne sait pas écrire la fiche de paie.
    remuneration: RemunerationActif | None = None
    #: Dernier revenu d'activité, annualisé ET ramené à l'année de liquidation.
    #: Dénominateur du taux de remplacement. Calculé par le simulateur, qui
    #: seul dispose des séries : voir :meth:`Simulateur._dernier_revenu`.
    dernier_revenu_annualise: float = 0.0
    #: Renseigné quand la carrière n'a pas été saisie mais DÉDUITE d'une
    #: pension : ce que l'inversion a trouvé, et ce qu'elle a dû écarter. Voir
    #: :func:`niveau_pour_pension`. ``None`` partout ailleurs, c'est-à-dire
    #: chaque fois que le revenu est celui qu'on a donné.
    niveau_inverse: "NiveauInverse | None" = None
    #: Pour qui a DÉJÀ liquidé — avant l'année courante —, ce que les six
    #: systèmes lui servent aujourd'hui, en euros courants de l'année
    #: courante : le système 1 revalorisé comme le droit l'a fait, les autres
    #: comme leur règle le veut. ``None`` pour qui part cette année ou plus
    #: tard, dont la pension du départ est la seule qu'il y ait à dire. Voir
    #: :mod:`retraite_notionnelle.revalorisation`.
    aujourd_hui: PensionAujourdhui | None = None
    #: Passage des euros de l'année courante aux euros constants de
    #: ``parametres.annee_euros_constants`` : le pendant, pour les montants
    #: d'aujourd'hui, de :attr:`coefficient_euros_constants`.
    coefficient_euros_aujourd_hui: float = 1.0

    # -- indicateurs ---------------------------------------------------------

    def en_euros_constants(self, montant: float) -> float:
        return montant * self.coefficient_euros_constants

    def aujourd_hui_en_euros_constants(self, montant: float) -> float:
        """Un montant d'aujourd'hui, dans les euros constants de la page."""
        return montant * self.coefficient_euros_aujourd_hui

    @property
    def fiabilite(self) -> Fiabilite:
        """Fiabilité de l'ÉTALON et des deux scénarios de référence.

        Les scénarios 4 à 6 en sont exclus à dessein : ils reposent sur une
        série employeur qui n'existe pas pour tous les régimes ni sur toutes les
        années. Les laisser qualifier l'ensemble ferait retomber toute
        simulation publique à « estimée » alors que les trois premiers
        scénarios, eux, ne se sont pas dégradés. Chacun porte sa propre
        fiabilité, et la sortie JSON les donne une à une.
        """
        return min(
            self.actuel.fiabilite,
            self.notionnel_retroactif.fiabilite,
            self.notionnel_prospectif.fiabilite,
        )

    @property
    def contribution_employeur(self) -> ContributionEmployeur:
        """Agent, employeur, total — la décomposition du scénario 4."""
        compte = self.notionnel_retroactif_employeur.compte
        return ContributionEmployeur(
            total=compte.cotisations_versees,
            employeur=compte.cotisations_employeur,
            annees_par_origine=compte.annees_part_employeur,
        )

    def variation(self, scenario: str) -> float:
        """Écart relatif d'un scénario notionnel au système actuel."""
        reference = self.actuel.pension_annuelle
        if reference <= 0:
            return float("nan")
        cible = getattr(self, scenario).pension_annuelle
        return cible / reference - 1.0

    @property
    def taux_remplacement_actuel(self) -> float:
        return self._taux(self.actuel.pension_annuelle)

    @property
    def taux_remplacement_retroactif(self) -> float:
        return self._taux(self.notionnel_retroactif.pension_annuelle)

    @property
    def taux_remplacement_prospectif(self) -> float:
        return self._taux(self.notionnel_prospectif.pension_annuelle)

    def _taux(self, pension: float) -> float:
        """Pension rapportée au dernier revenu d'activité, à la date du départ."""
        revenu = self.dernier_revenu_annualise
        if pension <= 0 or revenu <= 0:
            return 0.0
        return pension / revenu

    def taux_remplacement(self, scenario: str) -> float:
        """Taux de remplacement de n'importe lequel des scénarios notionnels."""
        return self._taux(getattr(self, scenario).pension_annuelle)

    # -- avec le pilier capitalisé ------------------------------------------
    #
    # Trois méthodes, et elles ne servent qu'à la PROPOSITION : elle seule
    # porte un pilier capitalisé, et pour tous les autres scénarios ces trois
    # valeurs sont, au centime près, celles d'au-dessus. Les séparer n'est pas
    # une précaution de style : une pension de répartition et une rente issue
    # d'un capital ne se revalorisent pas de la même façon, ne se transmettent
    # pas de la même façon, et ne sont pas exposées aux mêmes risques. Le site
    # affiche le total, mais jamais sans dire de quoi il est fait.

    def rente_capitalisee(self, scenario: str) -> float:
        """Ce que le pilier capitalisé sert, en plus de la répartition."""
        return getattr(self, scenario).rente_capitalisation_obligatoire

    def rente_capitalisee_volontaire(self, scenario: str) -> float:
        """La part de cette rente qui vient des cinq points volontaires."""
        return getattr(self, scenario).rente_capitalisation_volontaire

    def pension_totale(self, scenario: str) -> float:
        """Répartition et capitalisation réunies."""
        return getattr(self, scenario).pension_totale

    def variation_totale(self, scenario: str) -> float:
        """Écart au système actuel, pilier capitalisé compris."""
        reference = self.actuel.pension_annuelle
        if reference <= 0:
            return float("nan")
        return self.pension_totale(scenario) / reference - 1.0

    def taux_remplacement_total(self, scenario: str) -> float:
        return self._taux(self.pension_totale(scenario))

    # -- restitution ---------------------------------------------------------

    def tableau(self) -> str:
        c = self.carriere
        ecart = self.notionnel_retroactif.ecart_age
        conversion = self.notionnel_retroactif.conversion

        lignes = [
            f"Assuré : {c.identifiant} — né(e) en {c.date_naissance}, sexe {c.sexe}",
            f"Carrière : {c.premiere_annee}-{c.derniere_annee}, "
            f"{len(c.annees_cotisees)} années cotisées, "
            f"{c.trimestres_actuels} trimestres au sens actuel",
            f"Liquidation : {formater_age(c.age_liquidation)}, "
            f"en {c.date_liquidation}",
            f"Âge de référence : {ecart.age_reference:g} ans -> {ecart}",
            f"Coefficient de conversion : {conversion.diviseur:.2f} "
            f"(espérance de vie résiduelle {conversion.esperance_residuelle:.2f} ans, "
            f"table {conversion.table})",
            "",
            f"Montants bruts annuels. La colonne « constants » convertit en euros "
            f"de {self.parametres.annee_euros_constants},",
            "seule unité permettant de comparer des liquidations d'années différentes.",
            "",
            f"{'Scénario':<62} {'Courants':>11} {'Constants':>11} "
            f"{'Mensuel':>9} {'Écart':>8}",
            "-" * 104,
        ]

        def ligne(nom: str, montant: float,
                  ecart_relatif: float | str | None) -> str:
            # Trois cas, et le troisième compte : l'étalon porte « réf. », un
            # scénario porte son écart, et une ligne qui ne se compare à rien —
            # un compartiment servi à part — ne porte rien du tout. Elle
            # portait « réf. », ce qui la donnait pour la référence des autres.
            if isinstance(ecart_relatif, str):
                variation = ecart_relatif
            else:
                variation = ("réf." if ecart_relatif is None
                             else f"{ecart_relatif:+.1%}")
            constant = self.en_euros_constants(montant)
            return (
                f"{nom:<62} {montant:>10,.0f}€ {constant:>10,.0f}€ "
                f"{constant/12:>8,.0f}€ {variation:>8}"
            )

        lignes.append(ligne("1. Système actuel", self.actuel.pension_annuelle, None))
        for cle, numero, titre in SCENARIOS_NOTIONNELS:
            lignes.append(ligne(
                f"{numero}. " + titre.format(bascule=self.parametres.annee_bascule),
                getattr(self, cle).pension_annuelle,
                self.variation(cle),
            ))

        # Ce qui n'est pas de la répartition est servi À L'IDENTIQUE dans les
        # six scénarios : un régime provisionné n'est pas atteint par une
        # réforme de la répartition. Il est donc sorti des cinq totaux, et
        # affiché une seule fois — à son propre barème, celui du scénario 1, et
        # non converti en rente notionnelle.
        hors_repartition = self.actuel.pension_hors_repartition
        if hors_repartition > 0:
            lignes += [
                "-" * 104,
                ligne("   hors répartition (RAFP), servi à part, identique aux 6",
                      hors_repartition, ""),
            ]

        # Le pilier capitalisé, en dessous et à part. Il n'appartient qu'au
        # dernier scénario, il ne sort pas de la répartition, et l'additionner
        # en silence à une pension notionnelle ferait passer pour un rendement
        # de la répartition ce qui vient d'un marché obligataire. Ses deux
        # cotisations sont distinguées, parce que l'une est imposée et l'autre
        # non : c'est la seconde qui ramène l'effort au taux d'aujourd'hui.
        rente_capitalisee = self.notionnel_liberal.rente_capitalisation_obligatoire
        if rente_capitalisee > 0:
            numero = SCENARIOS_NOTIONNELS[-1][1]
            volontaire = self.notionnel_liberal.rente_capitalisation_volontaire
            lignes += ["-" * 104]
            if volontaire > 0:
                lignes += [
                    ligne(f"   + rente capitalisée obligatoire, scénario {numero}",
                          rente_capitalisee - volontaire, ""),
                    ligne("   + rente capitalisée volontaire, les 5 points rendus",
                          volontaire, ""),
                ]
            else:
                lignes += [
                    ligne(f"   + rente du pilier capitalisé, scénario {numero} seul",
                          rente_capitalisee, ""),
                ]
            lignes += [
                ligne(f"   = total servi par le scénario {numero}",
                      self.notionnel_liberal.pension_totale,
                      self.variation_totale("notionnel_liberal")),
            ]

        lignes += [
            "",
            f"Taux de remplacement — actuel {self.taux_remplacement_actuel:.1%}, "
            f"rétroactif {self.taux_remplacement_retroactif:.1%}, "
            f"prospectif {self.taux_remplacement_prospectif:.1%}",
            f"Capital notionnel rétroactif : "
            f"{self.notionnel_retroactif.capital_notionnel:,.0f} € "
            f"(cotisations versées {self.notionnel_retroactif.compte.cotisations_versees:,.0f} €, "
            f"rendement cumulé ×{self.notionnel_retroactif.compte.rendement_cumule:.2f})",
            f"Fiabilité du résultat : {self.fiabilite} "
            f"— voir docs/limites.md avant toute interprétation",
        ]

        employeur = self.contribution_employeur
        if employeur.a_un_employeur or employeur.concerne_un_regime_public:
            lignes += ["", "Qui verse la cotisation, en euros courants cumulés :"]
            if employeur.a_un_employeur:
                lignes += [
                    f"  part salariale     {employeur.agent:>13,.0f} €"
                    f"   scénarios 2 et 3",
                    f"  part patronale     {employeur.employeur:>13,.0f} €"
                    f"   soit {employeur.part:.0%} du total",
                    f"  total              {employeur.total:>13,.0f} €"
                    f"   scénarios 4 et 5",
                ]
            if employeur.concerne_un_regime_public:
                lignes.append(
                    f"  contribution employeur publique trouvée sur "
                    f"{employeur.annees_trouvees} année(s)"
                    + (f", inconnue sur {employeur.annees_repli} — le taux du "
                       "privé y tient lieu d'étalon"
                       if employeur.annees_repli else "")
                )

        if self.actuel.minimum_applique:
            lignes.append(
                "Note : le minimum contributif s'applique dans le scénario 1 ; "
                "il est supprimé dans les scénarios 2 à 6."
            )
        garantie = self.notionnel_liberal.garantie_vieillesse
        if garantie is not None and garantie.servie:
            quand = (
                "" if garantie.age_atteint
                else f", à compter de {garantie.annee_ouverture} (65 ans)"
            )
            lignes.append(
                f"Garantie vieillesse du scénario 6{quand} : "
                f"{garantie.complement:,.0f} € par an, financés par l'impôt, "
                f"portent la pension obligatoire de "
                f"{garantie.ressources:,.0f} € au plancher de "
                f"{garantie.plancher_annuel:,.0f} € ({garantie.situation})."
            )
        if not self.actuel.liquidation_ouverte:
            age = self.actuel.age_ouverture_opposable
            lignes.append(
                "ATTENTION : le droit en vigueur N'OUVRE PAS cette liquidation à "
                f"{formater_age(self.carriere.age_liquidation)}"
                + (f" — il faut attendre {age:g} ans" if age is not None else "")
                + ". Le montant du scénario 1 est un contrefactuel, pas une "
                "pension que le système actuel servirait."
            )
        return "\n".join(lignes)

    def dictionnaire(self) -> dict:
        """Forme sérialisable, pour une API ou un export."""
        return {
            "assure": {
                "identifiant": self.carriere.identifiant,
                "annee_naissance": self.carriere.annee_naissance,
                "mois_naissance": self.carriere.mois_naissance,
                "sexe": self.carriere.sexe,
                "age_liquidation": self.carriere.age_liquidation,
                "annee_liquidation": self.carriere.annee_liquidation,
                "mois_liquidation": self.carriere.mois_liquidation,
                "annees_cotisees": len(self.carriere.annees_cotisees),
                "trimestres_actuels": self.carriere.trimestres_actuels,
                "affiliations": list(self.carriere.affiliations_utilisees()),
            },
            "age_reference": {
                "age": self.notionnel_retroactif.ecart_age.age_reference,
                "ecart_annees": self.notionnel_retroactif.ecart_age.ecart,
                "anticipe": self.notionnel_retroactif.ecart_age.anticipe,
            },
            "conversion": {
                "diviseur": self.notionnel_retroactif.conversion.diviseur,
                "esperance_residuelle": self.notionnel_retroactif.conversion.esperance_residuelle,
                "table": self.notionnel_retroactif.conversion.table,
            },
            "scenarios": {
                "actuel": {
                    "pension_annuelle": self.actuel.pension_annuelle,
                    "pension_annuelle_euros_constants": self.en_euros_constants(
                        self.actuel.pension_annuelle
                    ),
                    "pension_mensuelle": self.actuel.pension_mensuelle,
                    "taux_remplacement": self.taux_remplacement_actuel,
                    "par_regime": [
                        {"regime": p.regime, "montant": p.montant, "detail": p.detail}
                        for p in self.actuel.pensions_par_regime
                    ],
                    "minimum_applique": self.actuel.minimum_applique,
                    "liquidation_ouverte": self.actuel.liquidation_ouverte,
                    "motif_ouverture": self.actuel.motif_ouverture,
                    "age_ouverture_opposable": self.actuel.age_ouverture_opposable,
                    "total_contributif": self.actuel.total_contributif,
                    "pension_hors_repartition": (
                        self.actuel.pension_hors_repartition
                    ),
                    "avantages_appliques": [
                        {"code": a.code, "libelle": a.libelle,
                         "montant": a.montant, "detail": a.detail}
                        for a in self.actuel.avantages_appliques
                    ],
                },
                **{
                    cle: _resume_notionnel(
                        getattr(self, cle), self.taux_remplacement(cle),
                        self.variation(cle), self.coefficient_euros_constants,
                    )
                    for cle, _, _ in SCENARIOS_NOTIONNELS
                },
            },
            "contribution_employeur": {
                "total": self.contribution_employeur.total,
                "employeur": self.contribution_employeur.employeur,
                "agent": self.contribution_employeur.agent,
                "part": self.contribution_employeur.part,
                "annees_par_origine": dict(
                    sorted(self.contribution_employeur.annees_par_origine.items())
                ),
            },
            "unite": {
                "euros_constants_de": self.parametres.annee_euros_constants,
                "coefficient": self.coefficient_euros_constants,
                "scenario_projection": self.parametres.scenario_projection,
                "trajectoire_emploi": self.parametres.trajectoire_emploi,
            },
            "regime_fusionne": {
                "annee_bascule": self.regime_fusionne.annee_bascule,
                "age_ouverture": self.regime_fusionne.age_ouverture,
                "age_taux_plein": self.regime_fusionne.age_taux_plein,
                "duree_requise_trimestres": self.regime_fusionne.duree_requise_trimestres,
                "taux_cotisation": self.regime_fusionne.taux_cotisation_retraite,
                "regimes_fusionnes": list(self.regime_fusionne.regimes_fusionnes),
                "origines": dict(self.regime_fusionne.origines),
            },
            "aujourd_hui": _resume_aujourd_hui(self.aujourd_hui),
            "fiabilite": str(self.fiabilite),
        }


def _resume_notionnel(resultat: ResultatNotionnel, taux_remplacement: float,
                      variation: float, coefficient: float = 1.0) -> dict:
    return {
        "pension_annuelle": resultat.pension_annuelle,
        "pension_annuelle_euros_constants": resultat.pension_annuelle * coefficient,
        "pension_mensuelle": resultat.pension_mensuelle,
        "taux_remplacement": taux_remplacement,
        "variation_vs_actuel": variation,
        "capital_notionnel": resultat.capital_notionnel,
        "capital_droits_acquis": resultat.capital_droits_acquis,
        "droits_acquis": None if resultat.droits_acquis is None else {
            "pension_figee": resultat.droits_acquis.pension_figee,
            "age_conversion": resultat.droits_acquis.age_conversion,
            "diviseur": resultat.droits_acquis.diviseur,
            "capital_a_la_bascule": resultat.droits_acquis.capital_a_la_bascule,
            "coefficient_revalorisation": resultat.droits_acquis.coefficient_revalorisation,
            "capital": resultat.droits_acquis.capital,
        },
        "cotisations_versees": resultat.compte.cotisations_versees,
        "rendement_cumule": resultat.compte.rendement_cumule,
        "cotisations_employeur": resultat.compte.cotisations_employeur,
        "annees_part_employeur": dict(
            sorted(resultat.compte.annees_part_employeur.items())
        ),
        "rente_capitalisation": resultat.rente_capitalisation_annuelle,
        "capitalisation": None if resultat.capitalisation is None else {
            "annee_ouverture": resultat.capitalisation.annee_ouverture,
            "taux_cotisation": resultat.capitalisation.taux_cotisation,
            "annees_cotisees": resultat.capitalisation.annees_cotisees,
            "versements": resultat.capitalisation.versements,
            "interets": resultat.capitalisation.interets,
            "frais_preleves": resultat.capitalisation.frais_preleves,
            "cout_des_frais": resultat.capitalisation.cout_des_frais,
            "capital": resultat.capitalisation.capital,
            "capital_hors_frais": resultat.capitalisation.capital_hors_frais,
            "diviseur": resultat.capitalisation.conversion.diviseur,
            "frais_arrerages": resultat.capitalisation.frais_arrerages,
            "frais_encours_rente": resultat.capitalisation.frais_encours_rente,
            "facteur_encours_rente": resultat.capitalisation.facteur_encours_rente,
            "rente_annuelle": resultat.capitalisation.rente_annuelle,
            "rente_mensuelle": resultat.capitalisation.rente_mensuelle,
            "taux_cotisation_volontaire":
                resultat.capitalisation.taux_cotisation_volontaire,
            "rente_volontaire": resultat.capitalisation.rente_volontaire,
            "capital_volontaire": resultat.capitalisation.capital_volontaire,
            "taux_rendement_annuel": resultat.capitalisation.taux_rendement_annuel,
            "rendement_cumule": resultat.capitalisation.rendement_cumule,
            "probabilite_deces_avant_liquidation": (
                resultat.capitalisation.probabilite_deces_avant_liquidation
            ),
            "esperance_capital_transmis": (
                resultat.capitalisation.esperance_capital_transmis
            ),
            "fiabilite": str(resultat.capitalisation.fiabilite),
        },
        "rente_capitalisation_obligatoire": resultat.rente_capitalisation_obligatoire,
        "rente_capitalisation_volontaire": resultat.rente_capitalisation_volontaire,
        "pension_totale": resultat.pension_totale,
        "pension_totale_euros_constants": resultat.pension_totale * coefficient,
        "pension_totale_mensuelle": resultat.pension_totale_mensuelle,
        "garantie_vieillesse": None if resultat.garantie_vieillesse is None else {
            "situation": resultat.garantie_vieillesse.situation,
            "age_atteint": resultat.garantie_vieillesse.age_atteint,
            "annee_ouverture": resultat.garantie_vieillesse.annee_ouverture,
            "coefficient_prix": resultat.garantie_vieillesse.coefficient_prix,
            "base_annuelle": resultat.garantie_vieillesse.base_annuelle,
            "isolement_annuel": resultat.garantie_vieillesse.isolement_annuel,
            "plancher_annuel": resultat.garantie_vieillesse.plancher_annuel,
            "pension_contributive": resultat.garantie_vieillesse.pension_contributive,
            "rente_capitalisee": resultat.garantie_vieillesse.rente_capitalisee,
            "ressources": resultat.garantie_vieillesse.ressources,
            "complement": resultat.garantie_vieillesse.complement,
            "differee": resultat.garantie_vieillesse.differee,
        },
        "fiabilite": str(resultat.fiabilite),
    }


def _resume_aujourd_hui(aujourd_hui: PensionAujourdhui | None) -> dict | None:
    """La pension d'aujourd'hui, pour la sortie JSON — ``None`` pour qui n'a
    pas encore liquidé."""
    if aujourd_hui is None:
        return None
    actuel = aujourd_hui.actuel
    return {
        "annee": aujourd_hui.annee,
        "actuel": {
            "pension_annuelle": actuel.pension_annuelle,
            "pension_hors_repartition": actuel.pension_hors_repartition,
            "par_regime": [
                {"regime": r.regime, "au_depart": r.au_depart,
                 "coefficient": r.coefficient, "aujourd_hui": r.aujourd_hui,
                 "regle": r.regle, "fiabilite": str(r.fiabilite)}
                for r in actuel.regimes
            ],
            "majoration_enfants": actuel.majoration_enfants,
            "coefficient_majoration": actuel.coefficient_majoration,
            "minimum_vieillesse": actuel.minimum_vieillesse,
            "mensuel_decembre_2019": actuel.mensuel_decembre_2019,
            "fiabilite": str(actuel.fiabilite),
        },
        "notionnels": dict(aujourd_hui.notionnels),
        "coefficients_notionnels": dict(aujourd_hui.coefficients_notionnels),
        "garantie_vieillesse": aujourd_hui.garantie_vieillesse,
        "rente_capitalisee": aujourd_hui.rente_capitalisee,
        "rente_capitalisee_volontaire": aujourd_hui.rente_capitalisee_volontaire,
        "garantie_ouverte": aujourd_hui.garantie_ouverte,
        "plancher_garantie": aujourd_hui.plancher_garantie,
        "ressources_garantie": aujourd_hui.ressources_garantie,
    }


def _dernier_revenu_annualise(carriere: Carriere, macro: DonneesMacro) -> float:
    """Dénominateur du taux de remplacement, à la DATE du départ.

    Deux corrections y sont faites, chacune pour une raison distincte.

    L'année du départ est incomplète — six mois de salaire pour qui liquide au
    1er juillet —, et la rapporter telle quelle doublait le taux. Le revenu est
    donc ramené à l'année pleine.

    Il est ensuite ramené à l'ANNÉE DE LIQUIDATION. Qui part le 1er janvier n'a
    travaillé aucun mois de cette année-là : sa dernière année cotisée est la
    précédente, et le taux rapportait alors une pension en euros de l'année du
    départ à un salaire en euros de l'année d'avant. Deux millésimes pour un
    seul rapport, et un décrochement de 1,84 point entre un départ en janvier
    et un départ en février — la marche la plus grosse de toute l'année, alors
    qu'un mois seulement les sépare. Le salaire est donc avancé jusqu'à l'année
    du départ par l'indice du salaire moyen, celui-là même dont la carrière est
    tirée. Il reste une marche de 0,58 point, du même ordre que celles des
    frontières de trimestre : celle-là mesure un mois de cotisation en moins,
    et non un changement d'unité.
    """
    derniers = [l for l in carriere.lignes if l.cotise]
    if not derniers:
        return 0.0
    dernier = derniers[-1]
    reference = salaire_moyen_annuel(macro, dernier.annee)
    if reference <= 0:
        return dernier.revenu_annualise
    facteur = salaire_moyen_annuel(macro, carriere.annee_liquidation) / reference
    return dernier.revenu_annualise * facteur


class Simulateur:
    """Façade : charge les données une fois, simule autant de carrières que voulu."""

    def __init__(self, parametres: Parametres | None = None) -> None:
        self.parametres = parametres or Parametres()
        racine = self.parametres.racine_donnees
        if not racine.exists():
            raise FileNotFoundError(
                f"répertoire de données introuvable : {racine}. "
                "Lancer le simulateur depuis la racine du dépôt, ou renseigner "
                "Parametres(racine_donnees=...)."
            )

    # -- données -------------------------------------------------------------

    @cached_property
    def macro(self) -> DonneesMacro:
        return DonneesMacro(
            self.parametres.racine_donnees,
            scenario_projection=self.parametres.scenario_projection,
            trajectoire_emploi=self.parametres.trajectoire_emploi,
        )

    @cached_property
    def mortalite(self) -> DonneesMortalite:
        return DonneesMortalite(self.parametres.racine_donnees)

    @cached_property
    def courbe_taux(self) -> CourbeTauxSansRisque:
        """La courbe sans risque telle que la BCE la publie, sans retouche.

        C'est elle que lit le TAUX D'EMPRUNT du chiffrage : la dette de la page
        Coût se finance au forward à un an, déflaté. Elle ne porte donc aucune
        prime de terme, quel que soit le réglage — voir
        :attr:`courbe_taux_pilier`, qui dit pourquoi les deux sont séparées.
        """
        return CourbeTauxSansRisque(self.parametres.racine_donnees)

    @cached_property
    def courbe_taux_pilier(self) -> CourbeTauxSansRisque:
        """La même courbe, sous le réglage des taux du PILIER capitalisé.

        ``prime_terme_trente_ans`` ne traverse que celle-ci. La séparation est
        volontaire, et elle corrige une erreur : la prime portée sur la courbe
        commune déplaçait aussi le taux d'emprunt de la dette, donc le stock
        accumulé par TOUS les systèmes — jusqu'à dix points de PIB sur le
        système actuel, qui n'a pas de pilier capitalisé et que le réglage
        annonçait pourtant ne pas toucher.

        Le coût de rouler une dette courte est une question réelle, et elle se
        pose dans les mêmes termes ; mais c'est une AUTRE question, qui a ses
        propres réserves dans ``docs/limites.md``, et un réglage nommé « taux
        futurs du pilier capitalisé » n'est pas l'endroit d'où la trancher.
        À zéro, le réglage publié, les deux courbes sont le même objet à un
        identifiant près.
        """
        return CourbeTauxSansRisque(
            self.parametres.racine_donnees,
            self.parametres.prime_terme_trente_ans,
        )

    @cached_property
    def catalogue(self) -> CatalogueRegimes:
        return CatalogueRegimes(self.parametres.racine_donnees)

    @cached_property
    def effectifs(self) -> EffectifsRetraites:
        """Effectifs de retraités par caisse — la pondération des cas types.

        Aucune pension n'en dépend : ils ne servent qu'aux AGRÉGATS, où ils
        disent ce que chaque configuration de carrière pèse réellement.
        """
        return EffectifsRetraites(self.parametres.racine_donnees)

    @cached_property
    def cotisants(self) -> EffectifsCotisants:
        """Effectifs de cotisants par caisse — la pondération côté RECETTE.

        Le pendant de ``effectifs`` pour une masse de cotisations : un cas type
        y pèse les cotisants de sa caisse, et non plus ses retraités. Aucune
        pension n'en dépend davantage.
        """
        return EffectifsCotisants(self.parametres.racine_donnees)

    @cached_property
    def distribution(self) -> DistributionPensions:
        """La distribution des pensions — elle seule chiffre un plancher.

        Aucune pension n'en dépend. Elle ne sert qu'à la garantie vieillesse de
        la page « Coût », qui est une allocation différentielle et ne se lit
        pas sur treize carrières. Celle des retraités qui RÉSIDENT en France :
        la garantie, comme l'ASPA qu'elle remplace, ne sert qu'eux.
        """
        return DistributionPensions(self.parametres.racine_donnees, residence="france")

    @cached_property
    def distributions_par_sexe(self) -> dict[str, DistributionPensions]:
        """La même distribution, femmes et hommes à part.

        L'enquête les publie séparément, et c'est ce qui permet de déplacer
        chaque sexe de son propre facteur au lieu de déplacer l'ensemble du
        même : le scénario 6 retire des droits non cotisés que les femmes
        détiennent plus souvent.
        """
        return {
            sexe: DistributionPensions(self.parametres.racine_donnees, sexe=sexe,
                                       residence="france")
            for sexe in ("F", "H")
        }

    @cached_property
    def caracteristiques(self) -> CaracteristiquesRetraites:
        """Ce que les carrières doivent aux droits non cotisés, par sexe.

        Elle ne sert, elle non plus, qu'à la garantie : c'est d'elle que vient
        le rapport des deux facteurs de déplacement, et le poids des deux sexes
        parmi les retraités.
        """
        return CaracteristiquesRetraites(self.parametres.racine_donnees)

    @cached_property
    def patrimoine(self) -> PatrimoineMenages:
        """Le patrimoine des ménages retraités — ce qu'une succession couvre.

        Aucune pension n'en dépend. Il ne sert qu'à la reprise sur succession
        de la garantie vieillesse, sur la page « Coût ».
        """
        return PatrimoineMenages(self.parametres.racine_donnees)

    @cached_property
    def vie_en_couple(self) -> VieEnCouple:
        """Qui vit en couple après 65 ans — ce qui regroupe deux avances sur
        une succession. Aucune pension n'en dépend."""
        return VieEnCouple(self.parametres.racine_donnees)

    @cached_property
    def financement_regimes(self) -> StructureFinancement:
        """Qui finance chaque régime : ses cotisants, l'État, ou personne.

        Aucune pension n'en dépend non plus. Elle sert à dire ce qu'une réforme
        déplace ENTRE FINANCEURS, ce que le coefficient d'équilibre agrégé ne
        distingue pas : 86 % de la fonction publique d'État viennent de la
        contribution de l'État, et 49 % de la CNRACL de 2070 ne viennent de
        personne.
        """
        return StructureFinancement(self.parametres.racine_donnees)

    @cached_property
    def affiliations(self) -> Affiliations:
        return Affiliations(self.parametres.racine_donnees)

    # -- moteur --------------------------------------------------------------

    @cached_property
    def indexation(self) -> Indexation:
        return Indexation(self.macro, self.parametres)

    @cached_property
    def revalorisations(self) -> RevalorisationsPensions:
        """Ce que le droit a servi aux pensions liquidées, date d'effet par date d'effet."""
        return RevalorisationsPensions(self.parametres.racine_donnees)

    @cached_property
    def revalorisation_servie(self) -> RevalorisationServie:
        """La règle que les systèmes notionnels prêtent aux pensions servies.

        La même que celle de la page Coût, de la première année de la
        répartition à l'année courante : le simulateur n'en lit que ce qui va
        du départ à aujourd'hui.
        """
        return RevalorisationServie(self, self.parametres.annee_debut_repartition,
                                    self.parametres.annee_courante)

    def pension_actuelle_aujourd_hui(self, carriere: Carriere) -> float:
        """Le système 1 servi l'année courante, en euros de cette année.

        La grandeur que l'inversion cherche pour un retraité : la pension qu'il
        lit sur son relevé, et non celle de son premier mois. Pour qui liquide
        cette année ou plus tard, c'est la pension du départ, dans ses euros.
        """
        resultat = self.scenario_actuel.calculer(carriere)
        if carriere.annee_liquidation >= self.parametres.annee_courante:
            return resultat.pension_annuelle
        return actuel_aujourd_hui(self, carriere, resultat).pension_annuelle

    @cached_property
    def convertisseur(self) -> Convertisseur:
        return Convertisseur(self.mortalite, self.parametres, self.macro,
                             self.distribution)

    @cached_property
    def age_reference(self) -> AgeReference:
        return AgeReference(self.parametres.racine_donnees, self.parametres, self.mortalite)

    @cached_property
    def constructeur(self) -> ConstructeurCompte:
        return ConstructeurCompte(
            self.macro, self.catalogue, self.affiliations,
            self.indexation, self.parametres,
        )

    def _constructeur_variante(self, **modifications) -> ConstructeurCompte:
        """Constructeur identique, sauf sur ce qui alimente le compte.

        Les scénarios 4 et 5 ne diffèrent du scénario 2 que par leur flux de
        cotisations : mêmes données, même indexation, même liquidation. Ils se
        construisent donc en dérivant les paramètres, ce qui garantit qu'aucune
        autre différence ne peut s'y glisser à l'insu du lecteur.
        """
        return ConstructeurCompte(
            self.macro, self.catalogue, self.affiliations,
            self.indexation, self.parametres.avec(**modifications),
        )

    @cached_property
    def constructeur_employeur(self) -> ConstructeurCompte:
        """Le constructeur des scénarios 4 et 5 : un seul, pour les deux.

        Il ne diffère de celui des scénarios 2 et 3 que par un paramètre : la
        part de la cotisation portée au compte.
        """
        return self._constructeur_variante(
            part_cotisation=PartCotisation.TOTALE,
        )

    @cached_property
    def constructeur_liberal(self) -> ConstructeurCompte:
        """Le constructeur du scénario 6 : le scénario 4 jusqu'à la bascule,
        le taux unique de la proposition ensuite.

        Il ne diffère de celui du scénario 4 que par ce qui alimente le compte
        À COMPTER DE LA BASCULE : un taux d'acquisition commun, prélevé une
        fois sur la rémunération, à la place des taux du régime unique. Avant
        la bascule, ce qui a été cotisé sous le système actuel est porté tel
        qu'il a été prélevé, aux taux réels de chaque régime, salariale et
        patronale confondues — exactement le scénario 4. La part de cotisation
        reste donc ``TOTALE``.
        """
        return self._constructeur_variante(
            part_cotisation=PartCotisation.TOTALE,
            source_cotisations=SourceCotisations.TAUX_HISTORIQUES_PUIS_UNIFORME,
            taux_cotisation_uniforme=self.parametres.taux_cotisation_liberal,
        )

    @cached_property
    def scenario_actuel(self) -> ScenarioActuel:
        return ScenarioActuel(
            self.macro, self.catalogue, self.affiliations, self.parametres
        )

    @cached_property
    def scenario_notionnel(self) -> ScenarioNotionnel:
        return ScenarioNotionnel(
            self.constructeur, self.convertisseur, self.age_reference,
            self.scenario_actuel, self.parametres,
        )

    @cached_property
    def scenario_employeur(self) -> ScenarioNotionnel:
        """Scénarios 4 et 5 : le scénario notionnel, part patronale comprise.

        Le même objet sert aux deux, comme :attr:`scenario_notionnel` sert aux
        scénarios 2 et 3 : c'est le point de départ du compte — origine de la
        répartition ou année de bascule — qui les distingue, pas le calcul.
        """
        return ScenarioNotionnel(
            self.constructeur_employeur, self.convertisseur,
            self.age_reference, self.scenario_actuel, self.parametres,
        )

    @cached_property
    def convertisseur_rente_capitalisee(self) -> Convertisseur:
        """Le convertisseur de la rente du PER : même table, taux technique propre.

        Il ne diffère de celui de la pension notionnelle que par le taux
        d'actualisation incorporé au diviseur — nul de part et d'autre au
        réglage par défaut, si bien que les deux diviseurs sont alors le même
        nombre. Les séparer coûte une ligne et garantit qu'un taux technique
        donné au PER ne déplacera jamais la pension de répartition.
        """
        return Convertisseur(
            self.mortalite,
            self.parametres.avec(
                taux_anticipe_conversion=(
                    self.parametres.taux_technique_rente_capitalisation
                )
            ),
            self.macro,
            self.distribution,
        )

    @cached_property
    def constructeur_capitalisation(self) -> ConstructeurCapitalisation:
        """Le pilier obligatoire de la proposition — et d'elle seule."""
        return ConstructeurCapitalisation(
            self.courbe_taux_pilier, self.mortalite,
            self.convertisseur_rente_capitalisee, self.parametres,
        )

    @cached_property
    def scenario_liberal(self) -> ScenarioNotionnel:
        """Scénario 6 : le scénario 4 jusqu'à la bascule, 18 % pour tous ensuite,
        la garantie vieillesse et le pilier de capitalisation obligatoire."""
        return ScenarioNotionnel(
            self.constructeur_liberal, self.convertisseur,
            self.age_reference, self.scenario_actuel, self.parametres,
            capitalisation=self.constructeur_capitalisation,
        )

    @cached_property
    def regime_fusionne(self) -> RegimeFusionne:
        return fusionner(self.catalogue, self.parametres.annee_bascule)

    # -- usage ---------------------------------------------------------------

    def carriere_simple(self, annee_naissance: int, sexe: str, affiliation: str,
                        age_debut: float, age_liquidation: float, **kwargs) -> Carriere:
        """Construit une carrière d'un seul métier, à partir de cinq informations.

        C'est le chemin le plus court pour qu'un assuré se simule sans rien
        connaître de la mécanique des régimes. Pour une carrière qui en compte
        plusieurs, voir :meth:`carriere_parcours`.
        """
        self._verifier_affiliation(affiliation)
        return Carriere.depuis_profil(
            annee_naissance=annee_naissance,
            sexe=sexe,
            affiliation=affiliation,
            age_debut=age_debut,
            age_liquidation=age_liquidation,
            macro=self.macro,
            **kwargs,
        )

    def carriere_parcours(self, annee_naissance: int, sexe: str,
                          metiers: list[Metier], age_liquidation: float,
                          **kwargs) -> Carriere:
        """Construit une carrière à partir de la suite des métiers exercés.

        Un métier après l'autre, chacun avec son statut et son niveau de revenu :
        c'est la forme générale, dont :meth:`carriere_simple` est le cas à un
        métier.
        """
        for metier in metiers:
            self._verifier_affiliation(metier.affiliation)
        return Carriere.depuis_parcours(
            annee_naissance=annee_naissance,
            sexe=sexe,
            metiers=list(metiers),
            age_liquidation=age_liquidation,
            macro=self.macro,
            **kwargs,
        )

    def carriere_releve(self, annee_naissance: int, sexe: str,
                        releve: list[LigneRelevee], age_liquidation: float,
                        **kwargs) -> Carriere:
        """Construit une carrière lue sur un relevé, année par année.

        La forme la plus exacte : rien n'y est reconstitué, ni le revenu de
        chaque année ni les trimestres qu'elle a validés — l'assuré les recopie
        de son relevé.
        """
        for ligne in releve:
            self._verifier_affiliation(ligne.affiliation)
        return Carriere.depuis_releve(
            annee_naissance=annee_naissance,
            sexe=sexe,
            releve=list(releve),
            age_liquidation=age_liquidation,
            macro=self.macro,
            **kwargs,
        )

    def _verifier_affiliation(self, affiliation: str) -> None:
        if affiliation not in self.affiliations:
            raise KeyError(
                f"affiliation inconnue : {affiliation!r}. Disponibles : "
                + ", ".join(self.affiliations.codes)
            )

    def simuler(self, carriere: Carriere) -> Comparaison:
        """Calcule les six scénarios pour une carrière."""
        self._verifier_fiabilite(carriere)

        fusionne = self.regime_fusionne if self.parametres.fusion_au_plus_defavorable else None

        actuel = self.scenario_actuel.calculer(carriere)
        retroactif = self.scenario_notionnel.retroactif(carriere, fusionne)
        prospectif = self.scenario_notionnel.prospectif(carriere, self.regime_fusionne)
        retroactif_employeur = self.scenario_employeur.retroactif(
            carriere, fusionne,
            libelle="Comptes notionnels rétroactifs, cotisation salariale et patronale",
        )
        prospectif_employeur = self.scenario_employeur.prospectif(
            carriere, self.regime_fusionne,
            libelle="Comptes notionnels à compter de la bascule, "
                    "cotisation salariale et patronale",
        )
        liberal = self.scenario_liberal.liberal(carriere, fusionne)

        # La mémoire des calibrations n'est plus écrite ici : c'est un fichier
        # versionné, dont `scripts/construire_donnees.py` est le seul écrivain.
        comparaison = Comparaison(
            carriere=carriere,
            actuel=actuel,
            notionnel_retroactif=retroactif,
            notionnel_prospectif=prospectif,
            notionnel_retroactif_employeur=retroactif_employeur,
            notionnel_prospectif_employeur=prospectif_employeur,
            notionnel_liberal=liberal,
            regime_fusionne=self.regime_fusionne,
            parametres=self.parametres,
            coefficient_euros_constants=self.macro.coefficient_prix(
                carriere.annee_liquidation, self.parametres.annee_euros_constants
            ),
            dernier_revenu_annualise=_dernier_revenu_annualise(carriere, self.macro),
            remuneration=remuneration_de_la_carriere(
                carriere, self.macro, self.catalogue, self.affiliations,
                self.parametres,
            ),
        )
        if carriere.annee_liquidation < self.parametres.annee_courante:
            comparaison.aujourd_hui = pension_aujourd_hui(self, comparaison)
            comparaison.coefficient_euros_aujourd_hui = self.macro.coefficient_prix(
                self.parametres.annee_courante, self.parametres.annee_euros_constants
            )
        return comparaison

    def _verifier_fiabilite(self, carriere: Carriere) -> None:
        exigee = Fiabilite.depuis_texte(self.parametres.fiabilite_minimale)
        if exigee == Fiabilite.ESTIMEE:
            return
        disponible = self.macro.fiabilite_sur(
            carriere.premiere_annee, carriere.annee_liquidation
        )
        if disponible < exigee:
            raise DonneeInsuffisante(
                f"les séries macroéconomiques couvrant "
                f"{carriere.premiere_annee}-{carriere.annee_liquidation} sont de "
                f"fiabilité « {disponible} », inférieure au minimum exigé "
                f"« {exigee} ». Certifier les données ou abaisser "
                "Parametres.fiabilite_minimale."
            )


# -- l'inversion : de la pension au revenu -----------------------------------
#
# Le simulateur va du revenu à la pension. Un retraité, lui, connaît sa pension
# au centime et ne se souvient pas de ce qu'il gagnait il y a trente ans : ce
# qui suit fait le chemin inverse, en cherchant le niveau de revenu dont le
# SCÉNARIO 1 — le droit en vigueur, le seul qui ait un sens à inverser — tire
# la pension saisie.

#: Nombre de coupes de la dichotomie. Fixe, et non un arrêt sur un écart :
#: les deux moteurs doivent rendre le MÊME niveau au bit près, et une boucle
#: qui s'arrête sur une condition de convergence n'offre pas cette garantie
#: aussi simplement qu'un compte de tours. Dix-huit coupes sur [0,1 ; 10]
#: laissent 3,8 · 10⁻⁵ de niveau, soit treize centimes de revenu mensuel :
#: bien en deçà de l'euro que la page affiche.
COUPES_INVERSION = 18

#: Les niveaux sur lesquels ``tests/test_simulateur.py`` balaie la croissance
#: de la pension. Ils sont ici, et non dans le test, parce que c'est la
#: PROPRIÉTÉ dont la dichotomie dépend : le jour où l'on doutera d'elle, c'est
#: à côté d'elle qu'on cherchera ce qui l'établit.
NIVEAUX_BALAYAGE = tuple(
    round(0.1 + rang * (10.0 - 0.1) / 29, 4) for rang in range(30)
)

#: Ce qui sépare une pension atteinte d'une pension manquée : un euro par mois,
#: la maille de ce que la page écrit. La dichotomie, elle, resserre à moins d'un
#: euro par AN dans la partie continue de la courbe — cet écart ne se franchit
#: donc que sur un saut de la fonction, jamais par défaut de convergence.
TOLERANCE_INVERSION = 12.0


@dataclass(frozen=True)
class NiveauInverse:
    """Le niveau de revenu qu'une pension suppose, et ce qu'il ne dit pas.

    La pension n'est pas une fonction bijective du revenu, et les trois cas où
    elle ne l'est pas ne sont pas des détails de calcul : ils sont le droit.

    ELLE PLAFONNE. Au-delà du plafond de la tranche la plus haute du statut,
    cotiser davantage n'acquiert plus rien : toutes les carrières mieux payées
    que ce plafond servent la même pension, et aucune ne sert davantage.

    ELLE SAUTE. Une année ne valide quatre trimestres qu'à partir de 150 heures
    de SMIC ; au-dessous, la carrière est comptée pour moins qu'elle n'a duré,
    le minimum contributif est proratisé d'autant, et la pension fait un bond
    dès que le seuil est franchi. Entre les deux, il existe des pensions que
    NULLE carrière de cette forme ne sert.

    ELLE A UN PLANCHER. Le minimum contributif et l'ASPA servent un montant
    qu'aucun revenu, si petit soit-il, ne fait descendre.

    Le champ ``pension`` porte donc ce que le niveau trouvé donne RÉELLEMENT,
    et l'appelant doit le comparer à ce qui était demandé — c'est à quoi sert
    :attr:`atteinte`.
    """

    #: Le niveau trouvé, en multiples du salaire moyen.
    niveau: float
    #: La pension annuelle que ce niveau sert, en euros de l'année de
    #: liquidation. C'est elle, et non la cible, qui dit la vérité.
    pension: float
    #: La pension demandée, dans la même unité.
    cible: float
    #: Ce que sert le plus grand niveau dont la pension reste EN DESSOUS de la
    #: cible. Avec :attr:`pension`, il borne le saut : entre les deux, aucune
    #: carrière de cette forme ne sert quoi que ce soit, et c'est ce couple que
    #: le refus montre plutôt qu'un chiffre approché.
    pension_dessous: float
    #: Ce que sert le niveau le plus bas accepté : le plancher du droit.
    plancher: float
    #: Ce que sert le niveau le plus haut accepté : le plafond du statut.
    plafond: float
    #: Le nombre de fois que le scénario 1 a été calculé. Sert aux tests et à
    #: la mesure, jamais à l'affichage.
    evaluations: int

    @property
    def atteinte(self) -> bool:
        """La pension demandée est-elle servie par le niveau trouvé ?"""
        return abs(self.pension - self.cible) <= TOLERANCE_INVERSION

    @property
    def sous_le_plancher(self) -> bool:
        """La pension demandée est plus petite que ce que le droit garantit."""
        return self.cible < self.plancher - TOLERANCE_INVERSION

    @property
    def au_dessus_du_plafond(self) -> bool:
        """La pension demandée dépasse ce que ce statut peut acquérir."""
        return self.cible > self.plafond + TOLERANCE_INVERSION


def niveau_pour_pension(pension_de_niveau, cible: float, mini: float,
                        maxi: float) -> NiveauInverse:
    """Le plus petit niveau de revenu dont le scénario 1 tire ``cible``.

    ``pension_de_niveau`` calcule une pension annuelle à partir d'un niveau ;
    c'est l'appelant qui décide ce qu'il y met — la carrière, ses métiers, ses
    interruptions —, et cette fonction ne connaît que le nombre qui en sort.

    LA DICHOTOMIE CHERCHE UNE BORNE, PAS UNE RACINE. Elle resserre l'encadrement
    du plus petit niveau dont la pension ATTEINT la cible, ce qui reste défini
    quand la fonction saute : sur un saut, elle converge vers le bord du saut,
    et la pension rendue est celle d'après — plus grande que la cible, et c'est
    ainsi qu'on sait que la cible n'est servie par personne. Chercher une racine
    aurait rendu, dans ce cas, un niveau dont la pension n'est pas celle qu'on
    demandait, sans que rien ne le signale.

    La fonction est supposée croissante, ce que le droit assure : cotiser plus
    n'a jamais acquis moins. Rien ici ne le vérifie — le contrôle est dans
    ``tests/test_simulateur.py``, qui balaie la courbe statut par statut.
    """
    plancher = pension_de_niveau(mini)
    plafond = pension_de_niveau(maxi)
    evaluations = 2
    if cible <= plancher:
        return NiveauInverse(mini, plancher, cible, plancher, plancher,
                             plafond, evaluations)
    if cible > plafond:
        return NiveauInverse(maxi, plafond, cible, plafond, plancher,
                             plafond, evaluations)

    bas, haut = mini, maxi
    pension_bas, pension_haut = plancher, plafond
    for _ in range(COUPES_INVERSION):
        milieu = (bas + haut) / 2.0
        servie = pension_de_niveau(milieu)
        evaluations += 1
        if servie >= cible:
            haut, pension_haut = milieu, servie
        else:
            bas, pension_bas = milieu, servie
    return NiveauInverse(haut, pension_haut, cible, pension_bas, plancher,
                         plafond, evaluations)
