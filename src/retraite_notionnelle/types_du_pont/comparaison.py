"""La comparaison que le pont relit (action 161, étape 1 bis du retrait des
règles Python) : les résultats des scénarios d'une même carrière, côte à côte,
et qui a payé le compte notionnel, sous leurs types, et leur présentation,
sans aucun corps de règle. ``simulateur.py`` les réimporte le temps du
retrait.

Le résumé de la carrière (:meth:`Comparaison.dictionnaire`) lit encore ses
trimestres validés (``trimestres_actuels``), une règle que seule la carrière
de ``carriere.py`` porte : le pont, qui la bâtit, la sert ; la carrière nue
n'en a pas.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..calendrier import formater_age
from ..config import Parametres
from ..donnees.chargement import Fiabilite
from ..donnees.simulateur import SCENARIOS_NOTIONNELS
from ..remuneration import RemunerationActif
from ..somme import somme_ordonnee
from .carriere import Carriere
from .droit import Reversion
from .journal import Journal
from .moteur import RegimeFusionne
from .resultats import ResultatActuel, ResultatNotionnel
from .revalorisation import PensionAujourdhui


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
        return somme_ordonnee(nombre for origine, nombre in self.annees_par_origine.items()
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
    #: Renseigné par le portage quand la carrière n'a pas été saisie mais
    #: DÉDUITE d'une pension : ce que l'inversion a trouvé (``NiveauInverse``,
    #: ``moteur/js/simulateur.js``). Le pont ne le transmet pas : ``None`` ici.
    niveau_inverse: dict | None = None
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
    #: La carrière sur laquelle la PROPOSITION est calculée, quand son âge
    #: légal de 65 ans reporte le départ : la même, poursuivie jusqu'à cet âge
    #: (voir :meth:`Simulateur.carriere_proposition`). ``None`` quand le
    #: départ n'est pas reporté — le scénario 6 part alors avec les autres.
    carriere_liberal: Carriere | None = None
    #: Les deux grandeurs qui dépendent de la DATE du départ, prises à celle du
    #: scénario 6 quand elle est reportée : le passage aux euros constants, et
    #: le dernier revenu du taux de remplacement.
    coefficient_euros_constants_liberal: float | None = None
    dernier_revenu_annualise_liberal: float | None = None
    #: Le journal de l'échéancier du scénario 1 (docs/architecture.md, § 7.4) :
    #: le départ, sa liquidation et ses composantes, l'ASPA du jour et, pour
    #: qui a déjà liquidé, ce que l'échéance en a fait. Il n'entre dans aucune
    #: sortie.
    journal: Journal | None = None
    #: La réversion que le décès déclaré de l'assuré ouvre à son conjoint,
    #: sous le droit en vigueur (docs/architecture.md, § 7.3) : ``None`` sans
    #: décès ni conjoint déclarés.
    reversion: Reversion | None = None

    # -- indicateurs ---------------------------------------------------------

    @property
    def depart_reporte(self) -> bool:
        """L'âge légal de la proposition reporte-t-il le départ du scénario 6 ?"""
        return self.carriere_liberal is not None

    def _reporte(self, scenario: str | None) -> bool:
        return scenario == "notionnel_liberal" and self.depart_reporte

    def carriere_de(self, scenario: str) -> Carriere:
        """La carrière sur laquelle ce scénario est calculé."""
        return self.carriere_liberal if self._reporte(scenario) else self.carriere

    def coefficient_de(self, scenario: str | None) -> float:
        """Le passage aux euros constants des montants de ce scénario.

        Chaque montant est en euros courants de SON année de liquidation. Le
        scénario 6, quand son départ est reporté, liquide plus tard que les
        autres : ses montants ne se comparent aux leurs qu'une fois ramenés,
        chacun par son propre coefficient, aux euros de la même année.
        """
        if self._reporte(scenario):
            return self.coefficient_euros_constants_liberal
        return self.coefficient_euros_constants

    def en_euros_constants(self, montant: float, scenario: str | None = None) -> float:
        """Un montant de ``scenario`` en euros constants — l'étalon et les
        scénarios 2 à 5 si ``scenario`` est omis."""
        return montant * self.coefficient_de(scenario)

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
        """Écart relatif d'un scénario notionnel au système actuel.

        En euros constants quand le scénario liquide à une autre date que
        l'étalon : deux montants courants d'années différentes ne se divisent
        pas l'un par l'autre.
        """
        return self._ecart(getattr(self, scenario).pension_annuelle, scenario)

    def _ecart(self, montant: float, scenario: str) -> float:
        reference = self.actuel.pension_annuelle
        if reference <= 0:
            return float("nan")
        if not self._reporte(scenario):
            return montant / reference - 1.0
        return (self.en_euros_constants(montant, scenario)
                / self.en_euros_constants(reference) - 1.0)

    @property
    def taux_remplacement_actuel(self) -> float:
        return self._taux(self.actuel.pension_annuelle)

    @property
    def taux_remplacement_retroactif(self) -> float:
        return self._taux(self.notionnel_retroactif.pension_annuelle)

    @property
    def taux_remplacement_prospectif(self) -> float:
        return self._taux(self.notionnel_prospectif.pension_annuelle)

    def _taux(self, pension: float, scenario: str | None = None) -> float:
        """Pension rapportée au dernier revenu d'activité, à la date du départ.

        À la date du départ DU SCÉNARIO : le scénario 6 reporté se rapporte au
        dernier revenu de la carrière prolongée, ramené à son année.
        """
        revenu = (self.dernier_revenu_annualise_liberal if self._reporte(scenario)
                  else self.dernier_revenu_annualise)
        if pension <= 0 or revenu <= 0:
            return 0.0
        return pension / revenu

    def taux_remplacement(self, scenario: str) -> float:
        """Taux de remplacement de n'importe lequel des scénarios notionnels."""
        return self._taux(getattr(self, scenario).pension_annuelle, scenario)

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
        return self._ecart(self.pension_totale(scenario), scenario)

    def taux_remplacement_total(self, scenario: str) -> float:
        return self._taux(self.pension_totale(scenario), scenario)

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
                  ecart_relatif: float | str | None,
                  scenario: str | None = None) -> str:
            # Trois cas, et le troisième compte : l'étalon porte « réf. », un
            # scénario porte son écart, et une ligne qui ne se compare à rien —
            # un compartiment servi à part — ne porte rien du tout. Elle
            # portait « réf. », ce qui la donnait pour la référence des autres.
            if isinstance(ecart_relatif, str):
                variation = ecart_relatif
            else:
                variation = ("réf." if ecart_relatif is None
                             else f"{ecart_relatif:+.1%}")
            constant = self.en_euros_constants(montant, scenario)
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
                cle,
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
                          rente_capitalisee - volontaire, "", "notionnel_liberal"),
                    ligne("   + rente capitalisée volontaire, les 5 points rendus",
                          volontaire, "", "notionnel_liberal"),
                ]
            else:
                lignes += [
                    ligne(f"   + rente du pilier capitalisé, scénario {numero} seul",
                          rente_capitalisee, "", "notionnel_liberal"),
                ]
            lignes += [
                ligne(f"   = total servi par le scénario {numero}",
                      self.notionnel_liberal.pension_totale,
                      self.variation_totale("notionnel_liberal"),
                      "notionnel_liberal"),
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

        if self.depart_reporte:
            reporte = self.carriere_liberal
            lignes.append(
                f"Âge légal de la proposition : le scénario 6 liquide à "
                f"{formater_age(reporte.age_liquidation)}, en "
                f"{reporte.date_liquidation}, et non à "
                f"{formater_age(self.carriere.age_liquidation)} : la carrière est "
                "prolongée jusque-là, et son montant courant est en euros de "
                f"{reporte.annee_liquidation}."
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
                        {"regime": p.regime, "montant": p.montant, "detail": p.detail,
                         # La date d'une pension n'est dite que quand les
                         # régimes liquident à des dates différentes.
                         **({"date_effet": p.date_effet,
                             "montant_a_l_effet": p.montant_a_l_effet}
                            if p.date_effet is not None else {})}
                        for p in self.actuel.pensions_par_regime
                    ],
                    **({"departs": [d.donnees() for d in self.actuel.departs]}
                       if self.actuel.departs else {}),
                    **({"demandes": [d.donnees() for d in self.actuel.demandes]}
                       if self.actuel.demandes else {}),
                    **({"retraite_progressive": self.actuel.retraite_progressive.donnees()}
                       if self.actuel.retraite_progressive is not None else {}),
                    **({"cumul": self.actuel.cumul.donnees()}
                       if self.actuel.cumul is not None else {}),
                    **({"droits_apres_depart": self.actuel.droits_apres_depart.donnees()}
                       if self.actuel.droits_apres_depart is not None else {}),
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
                        self.variation(cle), self.coefficient_de(cle),
                    )
                    for cle, _, _ in SCENARIOS_NOTIONNELS
                },
            },
            # Le départ de la proposition, qui n'est celui des autres que tant
            # que son âge légal ne le reporte pas.
            "liquidation_liberal": {
                "reportee": self.depart_reporte,
                "age_legal": self.parametres.age_legal_liberal,
                "age_liquidation": self.carriere_de("notionnel_liberal").age_liquidation,
                "annee_liquidation": self.carriere_de("notionnel_liberal").annee_liquidation,
                "mois_liquidation": self.carriere_de("notionnel_liberal").mois_liquidation,
                "coefficient_euros_constants": self.coefficient_de("notionnel_liberal"),
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
                "hypothese_esperance_vie": self.parametres.hypothese_esperance_vie,
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
            # La réversion n'a de clé que déclarée : les sorties d'avant ne
            # changent pas.
            **({"reversion": self.reversion.donnees()}
               if self.reversion is not None else {}),
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
        # Le capital du COMPTE par origine des cotisations : celui des
        # scénarios rétroactifs tout entier ; en prospectif, sa part cotisée
        # depuis la bascule, les droits acquis étant à part.
        "capital_par_regime": dict(sorted(resultat.compte.capital_par_regime.items())),
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
                 "majoration_exceptionnelle": r.majoration,
                 "relevement_des_exploitants": r.relevement,
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
