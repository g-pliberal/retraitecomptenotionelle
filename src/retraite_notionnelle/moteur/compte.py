"""Compte notionnel : accumulation des cotisations et liquidation.

Le compte notionnel est un compte virtuel. On y inscrit chaque année les
cotisations retraite réellement versées, on le revalorise au taux d'indexation
retenu, et on divise le solde final par un coefficient de conversion actuariel.
Aucun capital n'est placé : le système reste intégralement en répartition.

Trois principes tiennent tout le reste :

1. **Seules les cotisations comptent.** Une année sans cotisation n'ajoute rien
   au compte, quelle qu'en soit la cause. Les trimestres gratuits, majorations,
   bonifications et minima n'existent pas ici.
2. **L'année du versement fixe la valeur du droit.** Une cotisation de 1975 est
   revalorisée par le produit des taux annuels de 1976 à la liquidation.
3. **L'âge de liquidation fixe le partage.** Plus on liquide tôt, moins on a
   cotisé et plus longtemps on percevra : la double sanction est automatique.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property

from ..carriere import Affiliations, Carriere, salaire_moyen_annuel
from ..config import ContributionEtat, Parametres, PartCotisation, SourceCotisations
from ..donnees.chargement import Fiabilite
from ..donnees.macro import DonneesMacro
from ..donnees.regimes import (CatalogueRegimes, ClassesCotisation,
                              ContributionsEmployeurPubliques, PartRetraiteSeuleEtat,
                              SalairesForfaitaires)
from .fusion import RegimeFusionne
from .indexation import Indexation


#: Le seul régime dont la contribution employeur est un taux d'équilibre.
REGIME_ETAT = "fonction_publique_etat"


@dataclass(frozen=True)
class CotisationAnnuelle:
    """Détail des cotisations d'une année, régime par régime."""

    annee: int
    revenu: float
    assiette_retenue: float
    cotisation: float
    regimes: tuple[str, ...]
    taux_effectif: float
    hors_repartition: float
    fiabilite: Fiabilite
    #: D'où vient la part employeur PUBLIQUE, cette année-là — celle des
    #: régimes à ``perimetre_taux: agent_seul``, qu'aucune fiche ne porte. Vide
    #: si l'année n'en compte aucun ;
    #: ``appelee`` ou ``implicite`` si la contribution réellement versée a été
    #: trouvée ; ``repli`` si elle ne l'a pas été et que le taux du statut pivot
    #: privé lui a été substitué ; ``retraite_seule`` si c'est la part du taux
    #: de l'État que la Cour des comptes rattache à la retraite de l'agent
    #: (``ContributionEtat.RETRAITE_SEULE``). Ne vaut que dans les scénarios 4
    #: et 5 — ailleurs, la question ne se pose pas.
    origine_part_employeur: str = ""
    #: Part de ``cotisation`` versée par l'employeur, en euros. Nulle sous
    #: ``SALARIALE``, qui ne porte rien de lui au compte, et pour un
    #: non-salarié, qui n'en a pas.
    part_employeur: float = 0.0

    @property
    def nulle(self) -> bool:
        return self.cotisation <= 0


@dataclass
class CompteNotionnel:
    """Résultat de l'accumulation sur une carrière."""

    capital: float
    capital_hors_repartition: float
    annee_liquidation: int
    cotisations: list[CotisationAnnuelle] = field(default_factory=list)
    fiabilite: Fiabilite = Fiabilite.ESTIMEE

    @property
    def cotisations_versees(self) -> float:
        """Somme des cotisations en euros courants, sans revalorisation."""
        return sum(c.cotisation for c in self.cotisations)

    @property
    def annees_cotisees(self) -> int:
        return sum(1 for c in self.cotisations if not c.nulle)

    @property
    def rendement_cumule(self) -> float:
        """Rapport entre capital revalorisé et cotisations versées."""
        versees = self.cotisations_versees
        return self.capital / versees if versees else 0.0

    @property
    def cotisations_employeur(self) -> float:
        """Part des cotisations versée par l'employeur, en euros courants."""
        return sum(c.part_employeur for c in self.cotisations)

    @property
    def annees_part_employeur(self) -> dict[str, int]:
        """Nombre d'années par origine de la part employeur publique.

        Ce que les scénarios 4 et 5 doivent dire d'eux-mêmes : sur combien
        d'années la contribution réellement versée a été trouvée, et sur combien
        il a fallu l'estimer, faute de série.
        """
        decompte: dict[str, int] = {}
        for cotisation in self.cotisations:
            if cotisation.origine_part_employeur and not cotisation.nulle:
                origine = cotisation.origine_part_employeur
                decompte[origine] = decompte.get(origine, 0) + 1
        return decompte


class ConstructeurCompte:
    """Construit un compte notionnel à partir d'une carrière."""

    def __init__(
        self,
        macro: DonneesMacro,
        catalogue: CatalogueRegimes,
        affiliations: Affiliations,
        indexation: Indexation,
        parametres: Parametres,
    ) -> None:
        self.macro = macro
        self.catalogue = catalogue
        self.affiliations = affiliations
        self.indexation = indexation
        self.parametres = parametres
        self._taux_pivot: dict[int, float] = {}
        self.contributions_publiques = ContributionsEmployeurPubliques(
            parametres.racine_donnees
        )
        self.classes = ClassesCotisation(parametres.racine_donnees)
        self.grilles = SalairesForfaitaires(parametres.racine_donnees)

    # -- taux ----------------------------------------------------------------

    @cached_property
    def statuts_militaires(self) -> frozenset[str]:
        """Les statuts dont l'État paie la pension au titre des militaires."""
        return frozenset(self.affiliations.categories_militaires)

    @cached_property
    def parts_retraite_seule(self) -> dict[tuple[bool, bool], float]:
        """Part du taux de l'État que la Cour rattache à la retraite de l'agent.

        Indexée par (l'agent est-il militaire ?, le taux est-il celui des
        militaires ?). C'est le taux « retraite seule » que la Cour a mesuré
        pour sa population, rapporté à ce que valait la même année la série
        dont le taux vient : 44,1 / 78,28 pour un civil, 51,2 / 126,07 pour un
        militaire sur son propre taux. Chacun reçoit ainsi exactement le taux
        de la Cour l'année qu'elle a mesurée, et la même proportion de sa série
        les autres années.

        Avant 2006, le militaire n'a pas de taux propre : il reçoit le taux
        implicite de tout l'État, dont la part est 51,2 / 78,28 — rapportée au
        taux civil, ce qui garde entre militaire et civil le rapport que la
        Cour mesure entre leurs deux parts.
        """
        table = PartRetraiteSeuleEtat(self.parametres.racine_donnees)
        civil = self.contributions_publiques.taux(REGIME_ETAT, table.annee).taux
        militaire = self.contributions_publiques.taux(
            REGIME_ETAT, table.annee, militaire=True).taux
        return {(False, False): table.taux("civils") / civil,
                (True, True): table.taux("militaires") / militaire,
                (True, False): table.taux("militaires") / civil}

    @cached_property
    def annee_retraite_seule(self) -> int:
        """L'année que la Cour a mesurée — la seule où la part n'est pas supposée."""
        return PartRetraiteSeuleEtat(self.parametres.racine_donnees).annee

    def taux_pivot_prive(self, annee: int) -> float:
        """Taux total salarié + employeur du statut pivot privé, cette année-là.

        Sert de référence aux régimes dont la fiche ne stocke que la retenue de
        l'agent. On somme les régimes du statut pivot dont l'assiette commence
        au premier euro, pour ne pas compter deux fois les tranches hautes.
        """
        if annee in self._taux_pivot:
            return self._taux_pivot[annee]
        total = 0.0
        codes = self.affiliations.regimes(
            self.parametres.statut_pivot_cotisations, annee
        )
        for code in codes:
            if code not in self.catalogue:
                continue
            regime = self.catalogue[code]
            if regime.hors_repartition:
                continue
            for periode in regime.periodes_actives(annee):
                borne_basse, _ = periode.bornes_assiette_en_pass()
                if borne_basse > 0:
                    continue
                # La cotisation déplafonnée en fait partie : elle est prélevée
                # sur le salarié du privé comme le reste, et un régime qui
                # emprunte ce taux de référence doit emprunter le même effort.
                # L'omettre désalignait `TOTALE_ALIGNEE`, dont c'est justement
                # la raison d'être : prêter au public le taux du privé.
                total += (periode.taux_cotisation_retraite
                          + periode.taux_cotisation_deplafonnee)
        self._taux_pivot[annee] = total
        return total

    def _cotisation_forfaitaire(self, periode, annee: int) -> float:
        """Part forfaitaire de la cotisation, en euros de l'année demandée.

        La fiche la porte dans les euros d'une année de référence ; elle est
        ramenée à l'année courante par l'indice des prix, faute d'une série
        publiée sur toute la durée. C'est la convention déjà retenue pour
        ``pension_forfaitaire_annuelle``.
        """
        if periode.cotisation_forfaitaire_euros is None:
            return 0.0
        reference = periode.cotisation_forfaitaire_annee or annee
        return periode.cotisation_forfaitaire_euros * self.macro.coefficient_prix(
            reference, annee
        )

    def _cotisation_par_classes(self, code: str, periode, revenu: float,
                                annee: int) -> tuple[float, Fiabilite] | None:
        """Montant du palier où tombe ce revenu, ``None`` hors de cette forme.

        La grille est celle du millésime publié ; pour les autres exercices
        elle est ramenée par le RAPPORT DES PLAFONDS, bornes et montants
        ensemble — n'indexer que les montants ferait glisser tout le monde
        d'une classe à chaque revalorisation.

        Le plafond, et non les prix comme le fait ``_cotisation_forfaitaire``,
        parce que la grille est écrite en plafonds : rapportées à celui de
        2022, les sept bornes de la Cipav valent 0,65, 1,2, 1,4, 1,6, 2, 2,5 et
        3 plafonds, et ses huit montants sont 1, 2, 3, 5, 7, 11, 12 et 13 fois
        une unité qui vaut 3,71 % du plafond. L'indexer sur les prix la
        déformerait : le plafond a crû plus vite qu'eux, et une grille reportée
        vers l'amont en euros constants rangerait presque tout le monde dans la
        première classe.
        """
        if not periode.cotisation_par_classes:
            return None
        millesime = self.classes.annee_grille(code, annee)
        if millesime is None:
            return None
        reference = self.macro.plafond_securite_sociale(millesime)
        if reference <= 0:
            return None
        return self.classes.cotisation(
            code, annee, revenu,
            self.macro.plafond_securite_sociale(annee) / reference,
        )

    def taux_effectif(self, regime: str, periode, annee: int,
                      sans_employeur: bool = False,
                      part_salariale_seule: bool = False,
                      militaire: bool = False,
                      ) -> tuple[float, float, str, Fiabilite]:
        """Taux à porter au compte, sa part employeur, d'où elle vient et ce
        qu'elle vaut.

        Le deuxième terme est la part employeur EN POINTS DE TAUX, nulle sous
        ``SALARIALE`` et pour un non-salarié. Le troisième ne concerne que les
        régimes dont la fiche s'arrête à la retenue de l'agent : il dit si la
        contribution réellement versée par l'employeur public a été trouvée pour
        cette année-là (``appelee``, ``implicite``) ou s'il a fallu lui
        substituer le taux du statut pivot privé (``repli``), ou si c'est la
        part « retraite seule » du taux de l'État (``retraite_seule``). Le
        quatrième qualifie le résultat : la fiabilité de la série employeur
        quand elle a servi, ``estimee`` quand il a fallu s'en passer — ou la
        supposer, hors de l'année que la Cour a mesurée.
        """
        part = self.parametres.part_cotisation
        taux = periode.taux_cotisation_retraite

        if sans_employeur:
            # Un non-salarié paie tout : la répartition de la fiche est celle
            # d'un salarié du même régime, elle ne le concerne pas.
            return taux, 0.0, "", Fiabilite.CERTIFIEE

        if part_salariale_seule:
            # Un auteur paie la part du salarié, et personne l'autre : le
            # compte porte cette part sous TOUTES les conventions, parce
            # qu'elle est tout ce qui a été versé. Les scénarios 4 et 5 lui
            # prêtaient la part patronale d'un salarié, que le diffuseur ne
            # verse pas.
            return periode.taux_cotisation_salarie, 0.0, "", Fiabilite.CERTIFIEE

        if part is PartCotisation.SALARIALE:
            # La même grandeur des deux côtés : ce que l'assuré supporte. Pour
            # une période `agent_seul`, la retenue de l'agent est déjà cela, et
            # `part_salariale` y vaut un.
            return periode.taux_cotisation_salarie, 0.0, "", Fiabilite.CERTIFIEE

        if periode.perimetre_taux != "agent_seul":
            # Le privé : la fiche porte le total, et sa part salariale dit
            # combien l'employeur y met.
            return (taux, taux - periode.taux_cotisation_salarie, "",
                    Fiabilite.CERTIFIEE)

        if part is PartCotisation.TOTALE:
            # La retenue de l'agent, plus ce que l'employeur public a versé —
            # pour un militaire de l'État, le taux propre aux militaires.
            contribution = self.contributions_publiques.taux(regime, annee, militaire)
            if contribution is not None:
                if (regime == REGIME_ETAT and self.parametres.contribution_etat
                        is ContributionEtat.RETRAITE_SEULE):
                    # Ce que l'État a versé paie aussi ce qui n'est pas la
                    # retraite de l'agent : n'en porter que la part que la Cour
                    # lui rattache. Mesurée pour une année, supposée ailleurs,
                    # et prise sur la série dont le taux vient.
                    employeur = contribution.taux * self.parts_retraite_seule[
                        militaire, contribution.militaire]
                    fiabilite = min(contribution.fiabilite, Fiabilite.HAUTE
                                    if annee == self.annee_retraite_seule
                                    else Fiabilite.ESTIMEE)
                    return taux + employeur, employeur, "retraite_seule", fiabilite
                return (taux + contribution.taux, contribution.taux,
                        contribution.nature, contribution.fiabilite)
            # Aucune série pour ce régime cette année-là : plutôt que de laisser
            # le taux à la seule retenue de l'agent — ce qui ferait retomber les
            # scénarios 4 et 5 sur les scénarios 2 et 3 sans le dire — on
            # retombe sur l'effort total d'un salarié du privé de la même année.
            # L'écart avec la retenue est alors porté à la part employeur : c'est
            # une ESTIMATION de ce que l'employeur public aurait versé, pas une
            # somme retrouvée, et le résultat le dit — `repli`, fiabilité
            # `estimee`, et le décompte des années affiché sous la simulation.
            pivot = self.taux_pivot_prive(annee)
            if pivot <= taux:
                return taux, 0.0, "repli", Fiabilite.ESTIMEE
            return pivot, pivot - taux, "repli", Fiabilite.ESTIMEE

        # TOTALE_ALIGNEE : l'ancienne convention, conservée comme contrefactuel.
        pivot = self.taux_pivot_prive(annee)
        if pivot > 0:
            return pivot, 0.0, "", Fiabilite.CERTIFIEE
        return taux, 0.0, "", Fiabilite.CERTIFIEE

    def a_un_employeur(self, ligne, annee: int) -> bool:
        """Un employeur verse-t-il quelque chose pour cet assuré, cette année-là ?

        Non pour un artisan, un commerçant, un libéral, un exploitant agricole :
        ils cotisent seuls, et leur cotisation est intégralement personnelle.
        Oui pour un salarié, dont la fiche porte une part salariale inférieure à
        un, et pour un agent public, dont la fiche s'arrête à sa retenue.
        """
        if self.affiliations.sans_employeur(ligne.affiliation):
            return False
        # L'année d'entrée n'est pas connue ici, et elle ne change rien : la
        # question posée est celle de l'EXISTENCE d'un employeur, et un régime
        # fermé aux nouveaux entrants est remplacé par un autre régime de
        # salariés, jamais par un statut sans employeur.
        for code in self.affiliations.regimes(ligne.affiliation, annee):
            if code not in self.catalogue:
                continue
            regime = self.catalogue[code]
            if regime.hors_repartition:
                continue
            for periode in regime.periodes_actives(annee):
                if periode.perimetre_taux == "agent_seul":
                    return True
                if periode.part_salariale < 1.0:
                    return True
        return False

    def taux_unifie(self, ligne, annee: int,
                    regime_fusionne: RegimeFusionne
                    ) -> tuple[float, float, str, Fiabilite]:
        """Taux du régime unique, après la bascule — et ce que l'employeur y met.

        Le régime unique remplace tous les régimes : il n'y a plus, après la
        bascule, ni fonction publique ni régimes spéciaux, donc plus de
        contribution d'un employeur public à retrouver décret par décret. Son
        taux est celui du statut pivot privé, et il en hérite la répartition
        salarié/employeur — c'est elle qui sépare ici les scénarios 2 et 3 des
        scénarios 4 et 5.

        Une exception, et une seule : un assuré qui n'avait pas d'employeur
        n'en gagne pas un en changeant de régime. Un artisan cotise seul avant
        la bascule ; il cotise seul après, à un taux plus élevé — c'est déjà ce
        que dit le modèle, et la répartition doit le suivre.
        """
        # Un taux d'acquisition commun s'applique ici qu'il ait couvert toute la
        # carrière (``TAUX_UNIFORME``) ou qu'il ne commence qu'à la bascule
        # (``TAUX_HISTORIQUES_PUIS_UNIFORME``, le scénario 6) : après la
        # bascule, les deux sources se confondent.
        if self.parametres.source_cotisations is not SourceCotisations.TAUX_HISTORIQUES:
            return self.parametres.taux_cotisation_uniforme, 0.0, "", Fiabilite.CERTIFIEE

        unifie = regime_fusionne.taux_cotisation_retraite
        salarie = (regime_fusionne.taux_cotisation_salarie
                   if self.a_un_employeur(ligne, annee) else unifie)

        if (self.parametres.part_cotisation is PartCotisation.SALARIALE
                or self.affiliations.part_salariale_seule(ligne.affiliation)):
            # Même exception, dans l'autre sens : un auteur qui ne payait que
            # la part du salarié n'en gagne pas un employeur non plus.
            return salarie, 0.0, "", Fiabilite.CERTIFIEE
        return unifie, unifie - salarie, "", Fiabilite.CERTIFIEE

    # -- assiette ------------------------------------------------------------

    def _assiette(self, revenu: float, annee: int, plancher: float,
                  plafond_periode: float | None, fraction: float = 1.0) -> float:
        """Part du revenu comprise entre deux bornes, exprimées EN EUROS.

        Le plafond global du modèle, lui, reste en plafonds de la Sécurité
        sociale : c'est un paramètre de simulation, pas une règle de régime.

        ``fraction`` proratise le plafond sur les mois réellement travaillés :
        l'article R. 242-2 le calcule par mois, et une demi-année de travail
        n'ouvre qu'un demi-plafond. Sans ce prorata, l'année d'entrée et celle
        de la liquidation cotiseraient sous un plafond de douze mois.
        """
        pass_annuel = self.macro.plafond_securite_sociale(annee) * fraction
        plafond_global = self.parametres.plafond_assiette_en_pass
        if plafond_periode is None:
            plafond = revenu if plafond_global is None else plafond_global * pass_annuel
        else:
            plafond = plafond_periode
            if plafond_global is not None:
                plafond = min(plafond, plafond_global * pass_annuel)
        return max(0.0, min(revenu, plafond) - plancher)

    def _bornes_proratisees(self, periode, annee: int, fraction: float
                            ) -> tuple[float, float | None]:
        """Bornes d'assiette d'une période, ramenées aux mois travaillés.

        Les deux formes de bornes s'y plient : celles exprimées en plafonds de
        la Sécurité sociale, et celles que la fiche fixe en euros — les unes
        comme les autres sont des bornes ANNUELLES, et une année incomplète ne
        les atteint qu'à proportion.
        """
        basse, haute = periode.bornes_assiette_en_euros(
            self.macro.plafond_securite_sociale(annee)
        )
        if fraction >= 1.0:
            return basse, haute
        return basse * fraction, None if haute is None else haute * fraction

    @staticmethod
    def _fusionner(bornes: list[tuple[float, float | None]]
                   ) -> list[tuple[float, float | None]]:
        """Réunion d'intervalles d'assiette, sans recouvrement.

        Un taux d'acquisition COMMUN s'applique une fois à la rémunération, et
        non une fois par régime. Or les régimes se recouvrent : un cadre cotise
        au régime général et à l'Arrco sur la même première tranche, puis à
        l'Agirc sur la seconde. Sommer leurs assiettes conviendrait à des taux
        distincts, chacun n'ouvrant droit que dans son régime ; appliquer un taux
        unique à cette somme le compterait deux fois. On réunit donc les
        intervalles avant de prélever. ``None`` en borne haute vaut « sans
        plafond de régime » — le plafond global du modèle s'applique ensuite.
        """
        ordonnees = sorted(bornes, key=lambda b: (b[0], b[1] is None, b[1] or 0.0))
        fusionnees: list[tuple[float, float | None]] = []
        for basse, haute in ordonnees:
            if not fusionnees:
                fusionnees.append((basse, haute))
                continue
            precedente_basse, precedente_haute = fusionnees[-1]
            if precedente_haute is not None and basse > precedente_haute:
                fusionnees.append((basse, haute))
                continue
            if precedente_haute is None or haute is None:
                fusionnees[-1] = (precedente_basse, None)
            else:
                fusionnees[-1] = (precedente_basse, max(precedente_haute, haute))
        return fusionnees

    def _base_selon_assiette(self, assiette: str, base_ligne: float,
                             part_primes: float) -> float:
        """La part de la rémunération qu'un GROUPE d'assiettes découpe.

        Sert au seul taux uniforme, qui réunit les assiettes par leur point de
        départ — traitement, primes, rémunération entière — avant de prélever.
        Le plafond des primes du RAFP n'y a pas cours : c'est une règle du
        RAFP, et un taux unique porte sur toute la rémunération. Le groupe des
        primes ne s'y forme d'ailleurs que si `isoler_capitalisation` vaut
        faux ; sinon le RAFP garde son taux, son plafond et son compartiment.
        Les cotisations d'un régime passent par `PeriodeRegime.part_du_revenu`.
        """
        if assiette == "primes_uniquement":
            return base_ligne * part_primes
        if assiette == "hors_primes":
            return base_ligne * (1.0 - part_primes)
        return base_ligne

    # -- cotisation d'une année ---------------------------------------------

    def cotisation_annuelle(self, carriere: Carriere, annee: int,
                            regime_fusionne: RegimeFusionne | None = None) -> CotisationAnnuelle:
        """Les cotisations de l'année, TOUTES ACTIVITÉS RÉUNIES.

        Deux activités cumulées cotisent chacune à son régime, sur son revenu
        et sous ses propres bornes, et le compte porte ce qui a été versé :
        la somme des deux. Une année d'une seule activité est cette activité.
        """
        lignes = carriere.lignes_de(annee)
        if len(lignes) <= 1:
            return self._cotisation_ligne(
                carriere, lignes[0] if lignes else None, annee, regime_fusionne
            )
        details = [self._cotisation_ligne(carriere, ligne, annee, regime_fusionne)
                   for ligne in lignes]
        revenu = sum(d.revenu for d in details)
        cotisation = sum(d.cotisation for d in details)
        origines = [d.origine_part_employeur for d in details
                    if d.origine_part_employeur]
        return CotisationAnnuelle(
            annee=annee,
            revenu=revenu,
            assiette_retenue=sum(d.assiette_retenue for d in details),
            cotisation=cotisation,
            regimes=tuple(dict.fromkeys(
                code for d in details for code in d.regimes)),
            taux_effectif=cotisation / revenu if revenu else 0.0,
            hors_repartition=sum(d.hors_repartition for d in details),
            fiabilite=min(d.fiabilite for d in details),
            origine_part_employeur=(
                "repli" if "repli" in origines else (origines[0] if origines else "")
            ),
            part_employeur=sum(d.part_employeur for d in details),
        )

    def _cotisation_ligne(self, carriere: Carriere, ligne, annee: int,
                          regime_fusionne: RegimeFusionne | None
                          ) -> CotisationAnnuelle:
        """Les cotisations d'UNE activité de l'année."""
        # Une année non travaillée ne porte au compte que ce qu'un tiers a
        # VERSÉ pour elle : les cotisations complémentaires que l'Unédic paie
        # pendant un chômage indemnisé. Les points que l'Agirc-Arrco donne
        # pour la maladie, sans contrepartie, n'y entrent pas.
        if ligne is None or (not ligne.cotise and not ligne.familles_financees):
            return CotisationAnnuelle(
                annee=annee, revenu=0.0, assiette_retenue=0.0, cotisation=0.0,
                regimes=(), taux_effectif=0.0, hors_repartition=0.0,
                fiabilite=Fiabilite.CERTIFIEE,
            )

        # Aux deux bords de la carrière, l'année n'est pas pleine : le revenu
        # ne porte que les mois travaillés, et les plafonds se proratisent sur
        # les mêmes mois. L'année du départ est en outre tronquée au point de
        # départ, y compris quand la ligne, elle, déclare douze mois.
        part = carriere.part_retenue_ligne(ligne)
        if part <= 0:
            return CotisationAnnuelle(
                annee=annee, revenu=0.0, assiette_retenue=0.0, cotisation=0.0,
                regimes=(), taux_effectif=0.0, hors_repartition=0.0,
                fiabilite=Fiabilite.CERTIFIEE,
            )

        # Pendant une période indemnisée, l'assiette est le salaire d'AVANT
        # l'interruption : c'est sur lui que l'Unédic verse ses cotisations.
        base_ligne = ligne.revenu if ligne.cotise else ligne.revenu_reference
        if part < ligne.fraction_annee:
            # La ligne déclare plus de mois que le départ n'en laisse : on ne
            # porte au compte que ceux qui l'ont précédé.
            base_ligne *= part / ligne.fraction_annee

        # Après la bascule, un seul régime : le régime fusionné, pour ce que
        # l'assuré et son employeur versent. Une année indemnisée n'est pas de
        # celles-là : l'Unédic y verse ce qu'elle versait avant la bascule, et
        # c'est cela que le compte porte, par la branche des régimes. Elle
        # prenait jusqu'au 23 septembre 2026 le taux unifié entier sur le
        # salaire d'avant — et le pilier capitalisé avec —, que personne ne
        # versait : trois ans de chômage y valaient trois ans de travail.
        if (regime_fusionne is not None and annee >= regime_fusionne.annee_bascule
                and ligne.cotise):
            assiette = self._assiette(base_ligne, annee, 0.0, None, part)
            taux, taux_employeur, origine, fiabilite_taux = self.taux_unifie(
                ligne, annee, regime_fusionne
            )
            fiabilite = regime_fusionne.fiabilite
            if origine:
                fiabilite = min(fiabilite, fiabilite_taux)
            return CotisationAnnuelle(
                annee=annee, revenu=base_ligne, assiette_retenue=assiette,
                cotisation=assiette * taux, regimes=("regime_unifie",),
                taux_effectif=taux, hors_repartition=0.0,
                fiabilite=fiabilite,
                origine_part_employeur=origine,
                part_employeur=assiette * taux_employeur,
            )

        # Pendant une période indemnisée, seuls les régimes complémentaires
        # que quelqu'un paie encaissent, et sur le salaire d'avant
        # l'interruption.
        familles_admises = None if ligne.cotise else set(ligne.familles_financees)

        codes = self.affiliations.regimes(
            ligne.affiliation, annee, carriere.date_entree(ligne.affiliation),
            revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
            plafond=self.macro.plafond_securite_sociale(annee),
        )
        sans_employeur = self.affiliations.sans_employeur(ligne.affiliation)
        part_salariale_seule = self.affiliations.part_salariale_seule(
            ligne.affiliation)
        militaire = ligne.affiliation in self.statuts_militaires
        cotisation = 0.0
        assiette_totale = 0.0
        hors_repartition = 0.0
        fiabilite = Fiabilite.CERTIFIEE
        retenus: list[str] = []
        origines: list[str] = []
        part_employeur = 0.0

        # Taux d'acquisition commun (``source_cotisations = taux_uniforme``) :
        # un seul taux, prélevé une fois sur la rémunération. Les régimes en
        # répartition n'y servent plus qu'à délimiter l'assiette, qu'on réunit
        # avant de prélever. Le compartiment de capitalisation, lui, garde ses
        # taux propres : il n'est pas un compte notionnel. La source « taux
        # historiques puis uniforme » ne passe pas par ici : avant la bascule,
        # elle est exactement les taux historiques.
        acquisition_commune = (
            self.parametres.source_cotisations is SourceCotisations.TAUX_UNIFORME
        )
        intervalles: dict[str, list[tuple[float, float | None]]] = {}

        for code in codes:
            if code not in self.catalogue:
                continue
            regime = self.catalogue[code]
            if familles_admises is not None and regime.famille not in familles_admises:
                continue
            fiabilite = min(fiabilite, regime.fiabilite)
            en_repartition = not (
                regime.hors_repartition and self.parametres.isoler_capitalisation
            )
            for periode in regime.periodes_actives(annee):
                borne_basse, borne_haute = self._bornes_proratisees(
                    periode, annee, part
                )

                # Traitement seul ou primes seules, celles du RAFP dans la
                # limite de 20 % du traitement : `PeriodeRegime.part_du_revenu`,
                # le découpage même du scénario 1.
                base = periode.part_du_revenu(base_ligne, ligne.part_primes)
                # L'ASSIETTE N'EST PAS TOUJOURS LE REVENU. La CAVAMAC prélève
                # sur les commissions que les compagnies versent à l'agent
                # général, la CPRN sur les produits de l'office du notaire :
                # deux grandeurs que la carrière ne porte pas et qui valent
                # plusieurs fois le revenu. Le facteur les reconstitue AVANT
                # les bornes — c'est bien l'assiette qui est plafonnée, pas le
                # revenu.
                if periode.assiette_facteur_revenu is not None:
                    base *= periode.assiette_facteur_revenu
                # L'ASSIETTE PAR GRILLE : le marin cotise sur le salaire
                # forfaitaire de sa catégorie, non sur sa rémunération. La
                # catégorie est celle dont le forfait approche le plus le
                # revenu annualisé ; le forfait est proratisé sur les mois
                # retenus, comme l'était le revenu.
                if periode.assiette_grille:
                    forfait_grille = self.grilles.forfait(
                        periode.assiette_grille, annee, ligne.revenu_annualise,
                        lambda a: salaire_moyen_annuel(self.macro, a),
                    )
                    if forfait_grille is not None:
                        base = forfait_grille[0] * part
                        fiabilite = min(fiabilite, forfait_grille[2])

                if acquisition_commune and en_repartition:
                    # Regroupées par ASSIETTE DE DÉPART — traitement indiciaire,
                    # primes, rémunération entière — et non par régime : c'est
                    # la même rémunération qu'on découpe, et deux régimes qui la
                    # découpent différemment doivent se réunir, pas s'ajouter.
                    # Les planchers d'assiette propres à un régime — les 1 820
                    # SMIC de la complémentaire agricole — ne survivent pas non
                    # plus : un taux unique porte sur la rémunération réelle.
                    if self._assiette(base, annee, borne_basse, borne_haute, part) > 0:
                        groupe = (
                            periode.assiette
                            if periode.assiette in ("primes_uniquement", "hors_primes")
                            else "total"
                        )
                        intervalles.setdefault(groupe, []).append(
                            (borne_basse, borne_haute)
                        )
                        retenus.append(code)
                    continue

                assiette = self._assiette(base, annee, borne_basse, borne_haute, part)
                repere = periode.repere_assiette(
                    self.macro.plafond_securite_sociale(annee),
                    self.macro.smic_horaire(annee),
                ) * part
                if periode.assiette_forfaitaire:
                    # Assiette FORFAITAIRE : le régime des cultes ne prélève pas
                    # une fraction d'un revenu, il prélève sur un forfait égal au
                    # SMIC mensuel (R. 382-89 et R. 382-90), que l'assuré
                    # perçoive davantage, moins, ou rien. Le remplacement est
                    # donc inconditionnel, là où `assiette_plancher` ne relève
                    # que les assiettes trop basses.
                    assiette = repere
                elif periode.assiette_plancher and assiette < repere:
                    # Assiette minimale : la complémentaire agricole prélève sur
                    # 1 820 SMIC même quand le revenu est en dessous. Ce qui a
                    # été prélevé ouvre des droits, ici comme dans le scénario 1.
                    assiette = repere
                if not periode.assiette_forfaitaire:
                    # Assiette minimale en plafonds : celle de la CARPIMKO
                    # depuis 2026, comme dans le scénario 1.
                    assiette = max(assiette, periode.assiette_minimale(
                        self.macro.plafond_securite_sociale(annee)) * part)
                # LA COTISATION FORFAITAIRE. Certains complémentaires libéraux
                # ne sont ni proportionnels ni forfaitaires mais LES DEUX : le
                # régime des chirurgiens-dentistes appelle 3 210,60 € en 2026,
                # qui ouvrent six points, PLUS 11,35 % du revenu. Le forfait est
                # dû quel que soit le revenu : il ne dépend pas de l'assiette et
                # ne s'annule donc pas avec elle.
                forfait = self._cotisation_forfaitaire(periode, annee) * part

                # LA COTISATION PAR CLASSES. La Cipav, avant 2023, ne prélevait
                # ni un taux ni un forfait : elle rangeait l'assuré dans un des
                # huit paliers de son barème et appelait le montant du palier.
                # Ni l'assiette ni le taux n'ont alors de rôle — c'est la
                # grille qui décide, sur le revenu ENTIER de l'année, et le
                # montant est proratisé comme un forfait pour une année
                # incomplète.
                classe = self._cotisation_par_classes(code, periode, base, annee)
                if classe is not None:
                    montant_classe, fiabilite_classe = classe
                    montant_classe *= part
                    fiabilite = min(fiabilite, fiabilite_classe)
                elif assiette <= 0 and forfait <= 0:
                    continue

                taux, taux_employeur, origine, fiabilite_taux = self.taux_effectif(
                    code, periode, annee, sans_employeur, part_salariale_seule,
                    militaire,
                )
                if origine:
                    origines.append(origine)
                    fiabilite = min(fiabilite, fiabilite_taux)
                montant = (montant_classe if classe is not None
                           else assiette * taux + forfait)

                # LA COTISATION DÉPLAFONNÉE. Le régime général prélève, en
                # plus de la cotisation plafonnée, un taux sur la TOTALITÉ du
                # salaire — 2,42 % en 2024 et 2025, 2,51 % en 2026, lus année
                # par année ; la fiche en porte la moyenne de période, 2,41 % —,
                # et cette part n'ouvre aucun droit : elle finance la
                # solidarité. Le scénario 1 a donc
                # raison de l'ignorer.
                #
                # Un compte notionnel, lui, porte au compte ce qui a été VERSÉ.
                # La fiche portait auparavant les deux taux confondus en un
                # seul, appliqué à l'assiette PLAFONNÉE : la déplafonnée
                # s'arrêtait donc au plafond, alors que la loi la lève sur tout
                # le salaire. En dessous du plafond les deux écritures donnent
                # le même chiffre au centime près ; au-dessus, ce qui avait été
                # réellement payé manquait au compte — jusqu'à 122 643 € de
                # capital, soit 4,5 %, sur le témoin `salaire_8` part
                # employeur comprise.
                deplafonnee = base * periode.taux_cotisation_deplafonnee
                if deplafonnee > 0:
                    part_agent = periode.part_salariale_deplafonnee
                    if sans_employeur:
                        part_agent = 1.0
                    montant += (deplafonnee * part_agent
                                if self.parametres.part_cotisation
                                is PartCotisation.SALARIALE
                                or part_salariale_seule else deplafonnee)

                if regime.hors_repartition and self.parametres.isoler_capitalisation:
                    # RAFP, assurances sociales d'avant-guerre : ces droits sont
                    # provisionnés, ils ne rejoignent pas le compte notionnel.
                    hors_repartition += montant
                else:
                    cotisation += montant
                    assiette_totale += assiette
                    part_employeur += assiette * taux_employeur
                    if (deplafonnee > 0 and not sans_employeur
                            and not part_salariale_seule
                            and self.parametres.part_cotisation
                            is not PartCotisation.SALARIALE):
                        # Même règle que pour `taux_employeur` ci-dessus : sous
                        # `salariale`, le compte ne porte que la part de
                        # l'assuré, et la mesure de l'effort patronal est nulle.
                        part_employeur += deplafonnee * (
                            1.0 - periode.part_salariale_deplafonnee
                        )
                retenus.append(code)

        if acquisition_commune:
            taux_commun = self.parametres.taux_cotisation_uniforme
            for groupe, bornes in intervalles.items():
                base = self._base_selon_assiette(groupe, base_ligne, ligne.part_primes)
                for borne_basse, borne_haute in self._fusionner(bornes):
                    assiette = self._assiette(
                        base, annee, borne_basse, borne_haute, part
                    )
                    if assiette <= 0:
                        continue
                    assiette_totale += assiette
                    cotisation += assiette * taux_commun

        taux_effectif = cotisation / base_ligne if base_ligne else 0.0
        return CotisationAnnuelle(
            annee=annee,
            revenu=base_ligne,
            assiette_retenue=assiette_totale,
            cotisation=cotisation,
            regimes=tuple(dict.fromkeys(retenus)),
            taux_effectif=taux_effectif,
            hors_repartition=hors_repartition,
            fiabilite=fiabilite,
            # Un même agent ne relève que d'un régime en répartition à la fois ;
            # si deux périodes se recouvraient, le repli l'emporte, parce que
            # c'est lui qui qualifie le résultat.
            origine_part_employeur=(
                "repli" if "repli" in origines else (origines[0] if origines else "")
            ),
            part_employeur=part_employeur,
        )

    # -- accumulation --------------------------------------------------------

    def construire(
        self,
        carriere: Carriere,
        annee_liquidation: int,
        annee_debut: int | None = None,
        regime_fusionne: RegimeFusionne | None = None,
    ) -> CompteNotionnel:
        """Accumule les cotisations de ``annee_debut`` à la liquidation.

        ``annee_debut`` permet de n'ouvrir le compte qu'à partir d'une date —
        c'est ce qui distingue le scénario notionnel prospectif (compte ouvert à
        l'année de bascule) du scénario rétroactif (compte ouvert à l'entrée
        dans la vie active).
        """
        debut = max(
            annee_debut if annee_debut is not None else carriere.premiere_annee,
            self.parametres.annee_debut_repartition,
        )
        # L'année de la liquidation est INCLUSE. Elle ne l'était pas, et les
        # mois cotisés avant le point de départ n'allaient nulle part : partir
        # en décembre revenait à travailler onze mois pour rien. La ligne de
        # cette année-là ne porte que ces mois-là — voir
        # ``Carriere.depuis_profil`` —, et la revalorisation de l'année lui est
        # acquise puisque le compte est crédité au 1er janvier.
        fin = min(annee_liquidation, carriere.derniere_annee)

        capital = 0.0
        capital_hors = 0.0
        cotisations: list[CotisationAnnuelle] = []
        fiabilite = Fiabilite.CERTIFIEE

        for annee in range(debut, fin + 1):
            detail = self.cotisation_annuelle(carriere, annee, regime_fusionne)
            cotisations.append(detail)
            if detail.nulle and detail.hors_repartition == 0:
                continue
            fiabilite = min(fiabilite, detail.fiabilite)
            coefficient = self.indexation.coefficient(annee, annee_liquidation)
            capital += detail.cotisation * coefficient
            capital_hors += detail.hors_repartition * coefficient

        if cotisations:
            fiabilite = min(
                fiabilite,
                self.indexation.fiabilite_sur(debut, annee_liquidation),
            )

        return CompteNotionnel(
            capital=capital,
            capital_hors_repartition=capital_hors,
            annee_liquidation=annee_liquidation,
            cotisations=cotisations,
            fiabilite=fiabilite,
        )
