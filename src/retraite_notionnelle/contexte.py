"""Le contexte du site : ses données, et le jeu de règles sous lequel il calcule.

Une page du site demande une simulation, le coût de la proposition, les
avantages non contributifs. Le contexte charge une fois les données coûteuses,
garde un simulateur par jeu de paramètres et les agrégats déjà calculés, et
répond à chaque demande sous le jeu de règles qu'on lui a donné.

Il vient de ``web/pages.py``, comme la saisie (``saisie.py``), quand la
phase 8 en a retiré le texte du site. Sa copie JavaScript est
``moteur/js/contexte.js``.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from . import memoire
from .avantages import charger_avantages
from .calendrier import MOIS_PAR_AN, DateMois
from .carriere import Affiliations, Metier, formater_borne, salaire_moyen_annuel
from .config import Parametres
from .donnees.assiette import AssietteActivite
from .donnees.bilan import BilanFige, charger_bilan
from .donnees.chargement import charger_periodes_non_travaillees
from .donnees.depenses import DepensesRetraite
from .donnees.distribution import DistributionPensions
from .donnees.equilibre import ComptesRetraite, variante_du_scenario
from .donnees.population import Population
from .frontiere import charger_frontiere
from .remuneration import (
    charger_prelevements,
    salaire_brut_depuis_net,
    salaire_net_depuis_brut,
)
from .restitution import Restitution
from .saisie import (
    HEURES_SMIC_PAR_MOIS,
    NIVEAU_MAXIMAL,
    NIVEAU_MINIMAL,
    Echelle,
    ErreurSaisie,
    Saisie,
    _refus,
    euros,
)
from .simulateur import Comparaison, NiveauInverse, Simulateur, niveau_pour_pension


def _refus_de_pension(trouve: "NiveauInverse", saisie: Saisie,
                      montants: "Montants", constants: float) -> str:
    """Pourquoi aucune carrière ne sert la pension saisie, et ce qui la sert.

    Les trois refus disent une règle du droit, jamais une limite du calcul, et
    c'est ce qui les rend utiles : celui qui les lit apprend pourquoi sa
    pension ne se déduit pas d'un revenu, et ce qu'il faut changer — le
    montant, ou la carrière décrite au-dessus.

    Les montants sont rendus dans la langue du formulaire — mensuels, nets si
    la page est en net, en euros de l'année de référence —, faute de quoi le
    refus opposerait des annuels bruts à quelqu'un qui vient de taper un net
    mensuel.
    """
    def afficher(annuel: float) -> str:
        return euros(montants.pension(annuel * constants / MOIS_PAR_AN))

    if trouve.sous_le_plancher:
        return (
            "Aucune carrière de cette forme ne sert une pension si petite : "
            f"au revenu le plus bas que le formulaire accepte, elle sert déjà "
            f"{afficher(trouve.plancher)} par mois — le minimum contributif et "
            "l'ASPA font ce plancher. Saisissez au moins ce montant, ou "
            "décrivez une carrière plus courte ou plus interrompue."
        )
    if trouve.au_dessus_du_plafond:
        return (
            "Aucune carrière de cette forme ne sert une pension si grande : "
            f"le système actuel plafonne à {afficher(trouve.plafond)} par "
            "mois. Au-delà du plafond de la tranche la plus haute de ce "
            "statut, cotiser davantage n'acquiert plus rien, et toutes les "
            "carrières mieux payées servent la même pension."
        )
    return (
        "Aucune carrière de cette forme ne sert exactement cette pension : "
        f"entre {afficher(trouve.pension_dessous)} et "
        f"{afficher(trouve.pension)} par mois, il n'y a rien. Une année ne "
        "valide quatre trimestres qu'à partir de 150 heures de SMIC ; "
        "au-dessous, la carrière compte pour moins qu'elle n'a duré et le "
        "minimum contributif est proratisé d'autant, si bien que la pension "
        "saute dès que le seuil est franchi. Saisissez l'un de ces deux "
        "montants, ou décrivez la carrière — sa durée, ses interruptions — "
        "telle qu'elle a été."
    )


#: Combien d'agrégats le contexte garde en mémoire, tous jeux de règles
#: confondus. Deux par jeu — le coût et les avantages —, donc trois jeux de
#: règles : celui par défaut, et les deux derniers essayés.
AGREGATS_MEMORISES = 6


@dataclass
class Contexte:
    """Les données du site, et le jeu de règles sous lequel on les lit.

    Un contexte, c'est deux choses : des données coûteuses à charger, et UN jeu
    de paramètres — ``base`` — sous lequel tout ce que la page demande est
    calculé. ``simulateur()``, ``cout()`` et ``avantages()`` répondent tous
    trois sous ce jeu-là, sans qu'aucune page ait à le leur redire.

    Les trois pages qui AGRÈGENT — Cas types, Coût, Avantages — se rendent donc
    sous un contexte dérivé par :meth:`pour`, portant les réglages que l'adresse
    demande. Le corps des pages n'en sait rien : il lit ``contexte.base`` comme
    il l'a toujours fait, et y trouve les règles en vigueur au lieu des règles
    par défaut. C'est ce qui évite de faire passer un jeu de paramètres à la
    main dans la trentaine d'endroits qui les lisent.

    Les mémoires sont des dictionnaires plutôt qu'un champ par donnée, et c'est
    ce qui fait tenir la dérivation : un dictionnaire passe par référence, si
    bien qu'un contexte dérivé PARTAGE ce que le contexte d'origine a déjà
    chargé. Le chargement des données coûte quelques dixièmes de seconde, une
    simulation en coûte dix, un agrégat deux secondes : rien de tout cela ne
    doit se refaire parce qu'on a changé une règle.
    """

    base: Parametres = field(default_factory=Parametres)
    #: Un simulateur par jeu de paramètres rencontré.
    _instances: dict[Parametres, Simulateur] = field(default_factory=dict)
    #: Ce qui ne dépend d'AUCUN paramètre : dépense observée, comptes du COR,
    #: population, distribution des pensions, assiette, inventaire des
    #: avantages. Ces séries sont lues, jamais calculées : un changement de
    #: règle ne les déplace pas.
    _donnees: dict[str, object] = field(default_factory=dict)
    #: Les agrégats, eux, dépendent des règles : un coût par jeu de paramètres.
    _agregats: dict[tuple[str, Parametres], object] = field(default_factory=dict)

    def pour(self, parametres: Parametres) -> "Contexte":
        """Le même contexte, sous un autre jeu de règles.

        Les mémoires sont partagées, pas recopiées : dériver ne coûte rien, et
        ce que l'un charge, l'autre le trouve chargé.
        """
        if parametres == self.base:
            return self
        return Contexte(base=parametres, _instances=self._instances,
                        _donnees=self._donnees, _agregats=self._agregats)

    def _donnee(self, nom: str, fabrique):
        """Une donnée indépendante des règles, chargée une fois pour toutes."""
        if nom not in self._donnees:
            self._donnees[nom] = fabrique()
        return self._donnees[nom]

    def _agregat(self, nom: str, fabrique):
        """Un agrégat, mémorisé par jeu de règles — et en nombre borné.

        Sans borne, une adresse suffirait à faire enfler la mémoire de l'onglet
        d'un jeu de règles à l'autre : le calcul se fait chez le lecteur, et
        l'adresse EST la saisie. Le plus ancien s'en va ; revenir aux réglages
        par défaut après en avoir essayé trois recalcule, deux secondes.
        """
        cle = (nom, self.base)
        if cle not in self._agregats:
            if len(self._agregats) >= AGREGATS_MEMORISES:
                self._agregats.pop(next(iter(self._agregats)))
            self._agregats[cle] = fabrique()
        return self._agregats[cle]

    def simulateur(self, parametres: Parametres | None = None) -> Simulateur:
        parametres = parametres or self.base
        if parametres not in self._instances:
            self._instances[parametres] = Simulateur(parametres)
        return self._instances[parametres]

    def depenses(self) -> DepensesRetraite:
        return self._donnee(
            "depenses", lambda: DepensesRetraite(self.base.racine_donnees))

    def comptes(self) -> ComptesRetraite:
        """Le second terme du bilan : ce que le système de retraite encaisse.

        SOUS LA VARIANTE DES RÈGLES DE ``base``, et c'est ce qui manquait
        jusqu'au 21 septembre 2026 : la page lisait le scénario de référence du
        COR quel que soit le scénario demandé, si bien que la croissance
        déplaçait la dépense des systèmes notionnels, qui est calculée, sans
        déplacer celle du droit en vigueur, qui est empruntée.

        La mémoire porte le nom de la variante : deux jeux de règles qui ne
        diffèrent que par leur scénario ne doivent pas se partager un compte.
        """
        racine = self.base.racine_donnees
        variante = variante_du_scenario(
            self.base.scenario_projection, racine / "reference" / "macro")
        return self._donnee(
            f"comptes:{variante}", lambda: ComptesRetraite(racine, variante=variante))

    def population(self) -> Population:
        return self._donnee(
            "population", lambda: Population(self.base.racine_donnees))

    def distribution(self) -> DistributionPensions:
        """La distribution des pensions — elle seule chiffre un plancher.

        Celle des retraités qui résident en France : la garantie ne sert
        qu'eux, et c'est celle que le site lit dans son paquet.
        """
        return self._donnee(
            "distribution", lambda: DistributionPensions(self.base.racine_donnees,
                                                         residence="france"))

    def assiette(self) -> AssietteActivite:
        """Sur quoi l'on prélève : sans elle, un taux ne devient pas une recette."""
        return self._donnee(
            "assiette", lambda: AssietteActivite(self.base.racine_donnees))

    def restitution(self) -> Restitution:
        """Ce que la proposition rend au salaire, et ce qu'elle éteint en dette.

        Mémorisé par jeu de règles et non une fois pour toutes : le partage est
        un RÉGLAGE, et deux contextes n'ont pas forcément le même.
        """
        return self._agregat("restitution", lambda: Restitution(
            self.base.racine_donnees, self.base.part_rendue_aux_salaires))

    def bilan(self) -> BilanFige:
        """Le bilan des quatre systèmes, figé — une DONNÉE, pas un agrégat.

        La page des résultats en a besoin à chaque frappe, et le calculer
        coûte dix-huit secondes : elle lit donc la table que
        ``scripts/construire_donnees.py`` a écrite, celle-là même que le
        navigateur reçoit dans son paquet. ``donnees/bilan.py`` dit ce que ce
        figeage coûte — rien sur le système actuel, dont le coefficient est le
        compte du COR, et une dépendance aux réglages de référence sur les
        trois autres.
        """
        return self._donnee(
            "bilan", lambda: charger_bilan(self.base.racine_donnees))

    def cout(self):
        """Le coût agrégé de tous les systèmes — vingt secondes de calcul, une fois.

        Sous les règles de ``base``, et non sous celles par défaut : c'est ce
        qui fait que la page Coût chiffre ce que le simulateur calcule. C'est un
        calcul gardé (``memoire.py``), que les tests et les scripts partagent :
        la mémoire le fait sur un simulateur et des données qu'elle bâtit des
        mêmes paramètres, ceux que ce contexte chargerait, et les comptes du COR
        du même scénario de projection.
        """
        return self._agregat("cout", lambda: memoire.cout(self.base))

    def inventaire_avantages(self):
        """L'inventaire des avantages non contributifs — une donnée, pas un calcul."""
        return self._donnee(
            "inventaire_avantages",
            lambda: charger_avantages(self.base.racine_donnees))

    def frontiere(self):
        """Le versant inverse : ce qu'on cotise sans rien acquérir. Une donnée."""
        return self._donnee(
            "frontiere", lambda: charger_frontiere(self.base.racine_donnees))

    def avantages(self):
        """Ce que les avantages non contributifs coûtent — un calcul gardé, lui
        aussi, et une fois."""
        return self._agregat("avantages", lambda: memoire.avantages(self.base))

    def echelle(self, saisie: Saisie) -> Echelle:
        """L'échelle des salaires de l'année courante, pour cette saisie.

        L'année est celle du modèle — on saisit un salaire d'aujourd'hui —, et
        les séries sont CELLES DE LA SAISIE : au-delà de la dernière année
        observée, le salaire moyen dépend du scénario de projection choisi.
        """
        parametres = saisie.parametres(self.base)
        macro = self.simulateur(parametres).macro
        annee = parametres.annee_courante
        simulateur = self.simulateur(parametres)

        def vers_brut(net_mensuel: float, statut: str) -> float:
            return salaire_brut_depuis_net(
                parametres.racine_donnees, macro, simulateur.catalogue,
                simulateur.affiliations, statut, annee,
                net_mensuel * MOIS_PAR_AN,
            ) / MOIS_PAR_AN

        def vers_net(brut_mensuel: float, statut: str) -> float:
            return salaire_net_depuis_brut(
                parametres.racine_donnees, macro, simulateur.catalogue,
                simulateur.affiliations, statut, annee,
                brut_mensuel * MOIS_PAR_AN,
            ) / MOIS_PAR_AN

        return Echelle(
            moyen=salaire_moyen_annuel(macro, annee),
            smic=HEURES_SMIC_PAR_MOIS * macro.smic_horaire(annee),
            plafond=macro.plafond_securite_sociale(annee) / MOIS_PAR_AN,
            vers_brut=vers_brut if saisie.saisie_en_net else None,
            vers_net=vers_net,
            vers_brut_direct=vers_brut,
        )

    def simuler(self, saisie: Saisie) -> Comparaison:
        simulateur = self.simulateur(saisie.parametres(self.base))
        # Les motifs viennent des données, pas d'une liste écrite ici : le
        # moteur y lit ce que chaque période ouvre, et une saisie refusée doit
        # l'être sur la même table que celle qui calcule.
        motifs = charger_periodes_non_travaillees(simulateur.macro.racine)
        if saisie.releve_actif:
            return simulateur.simuler(self._carriere_relevee(
                simulateur, saisie, motifs))
        parcours = saisie.parcours(self.echelle(saisie))
        for metier in parcours:
            if metier.affiliation not in simulateur.affiliations:
                raise ErreurSaisie(
                    f"Statut d'affiliation inconnu : « {metier.affiliation} »."
                )

        def batir(niveaux: list[float]) -> "Carriere":
            return simulateur.carriere_parcours(
                annee_naissance=saisie.naissance,
                sexe=saisie.sexe,
                metiers=[
                    replace(metier, niveau_salaire=niveau)
                    for metier, niveau in zip(parcours, niveaux)
                ],
                mois_naissance=saisie.naissance_mois,
                jour_naissance=saisie.jour_declare,
                age_liquidation=saisie.liquidation,
                profil_carriere=saisie.profil,
                interruptions=saisie.interruptions_de_carriere(motifs),
                nombre_enfants=saisie.enfants,
                naissances_enfants=saisie.naissances_enfants(),
                conjoint=saisie.conjoint_declare(),
                deces=saisie.deces_declare(),
                part_primes=saisie.primes,
                identifiant="assuré",
            )

        if saisie.par_pension:
            return self._simuler_par_pension(simulateur, saisie, batir,
                                             len(parcours), parcours)
        carriere = batir([metier.niveau_salaire for metier in parcours])
        _verifier_statuts_ouverts(simulateur.affiliations, carriere, parcours)
        return simulateur.simuler(carriere)

    def _simuler_par_pension(self, simulateur: Simulateur, saisie: Saisie,
                             batir, combien: int, parcours) -> Comparaison:
        """La carrière que la pension suppose, puis les quatre systèmes dessus.

        UN SEUL NIVEAU POUR TOUTE LA CARRIÈRE. Inverser une pension ne donne
        qu'un nombre, et une carrière en compte autant qu'elle a de métiers :
        il faut donc une convention, et la plus simple est la seule qui
        n'invente rien — le même niveau partout, que le profil de carrière
        déforme ensuite comme il le fait toujours. Qui veut un revenu par
        métier le saisit, ou dépose son relevé.

        LA CIBLE EST RAMENÉE À CE QUE LE MODÈLE CALCULE, et dans cet ordre : la
        pension saisie est mensuelle, nette peut-être, en euros constants de
        l'année de référence ; le scénario 1 rend une pension annuelle, brute,
        en euros de l'année de liquidation. Le coefficient des euros constants
        ne dépend que de l'année de liquidation, jamais du niveau de revenu :
        il se calcule une fois, avant la dichotomie, et non à chaque tour.

        POUR UN RETRAITÉ, LA CIBLE EST LA PENSION D'AUJOURD'HUI. Il saisit ce
        qu'il touche, pas ce qu'il touchait le premier mois : la dichotomie
        compare donc au montant saisi la pension du départ revalorisée comme
        le droit l'a fait depuis — :meth:`Simulateur.pension_actuelle_aujourd_hui`
        —, en euros de l'année courante. Ce coefficient-là dépend du niveau,
        par la tranche de 2020 et par le poids de la complémentaire : il se
        refait à chaque tour, et c'est le prix de l'exactitude.
        """
        montants = Montants.depuis(saisie, self.base)
        parametres = simulateur.parametres
        retraite = saisie.date_de(saisie.liquidation).annee < parametres.annee_courante
        constants = simulateur.macro.coefficient_prix(
            parametres.annee_courante if retraite
            else saisie.date_de(saisie.liquidation).annee,
            parametres.annee_euros_constants,
        )
        brute = (saisie.pension / (1.0 - montants.taux_pension)
                 if saisie.en_net else saisie.pension)
        cible = brute * MOIS_PAR_AN / constants

        def pension_de_niveau(niveau: float) -> float:
            carriere = batir([niveau] * combien)
            if retraite:
                return simulateur.pension_actuelle_aujourd_hui(carriere)
            return simulateur.scenario_actuel.calculer(carriere).pension_annuelle

        trouve = niveau_pour_pension(pension_de_niveau, cible,
                                     NIVEAU_MINIMAL, NIVEAU_MAXIMAL)
        if not trouve.atteinte:
            raise ErreurSaisie(_refus_de_pension(trouve, saisie, montants,
                                                 constants))
        carriere = batir([trouve.niveau] * combien)
        _verifier_statuts_ouverts(simulateur.affiliations, carriere, parcours)
        comparaison = simulateur.simuler(carriere)
        return replace(comparaison, niveau_inverse=trouve)

    def _carriere_relevee(self, simulateur: Simulateur, saisie: Saisie,
                          motifs) -> "Carriere":
        """La carrière telle que le relevé la donne, sans rien reconstituer.

        Aucune échelle des salaires n'intervient : le relevé est déjà en euros
        de chaque année, quand le formulaire paramétrique saisit un revenu
        d'aujourd'hui que le modèle promène ensuite le long du salaire moyen.
        C'est ce qui fait de ce chemin le plus exact — et le seul où l'euro
        n'est pas converti.
        """
        releve = saisie.releve_analyse(motifs)
        for ligne in releve:
            if ligne.affiliation not in simulateur.affiliations:
                raise ErreurSaisie(
                    f"Relevé, année {ligne.annee} : statut d'affiliation "
                    f"inconnu « {ligne.affiliation} »."
                )
        carriere = simulateur.carriere_releve(
            annee_naissance=saisie.naissance,
            sexe=saisie.sexe,
            releve=releve,
            mois_naissance=saisie.naissance_mois,
            jour_naissance=saisie.jour_declare,
            age_liquidation=saisie.liquidation,
            nombre_enfants=saisie.enfants,
            naissances_enfants=saisie.naissances_enfants(),
            conjoint=saisie.conjoint_declare(),
            deces=saisie.deces_declare(),
            part_primes=saisie.primes,
            identifiant="assuré",
        )
        _verifier_statuts_releve(simulateur.affiliations, carriere)
        return carriere


def _verifier_statuts_ouverts(affiliations: Affiliations, carriere,
                              parcours: list[Metier]) -> None:
    """Un statut ne se déclare qu'aux dates où son régime recrutait.

    Un jeune d'aujourd'hui ne peut pas se déclarer mineur : le régime des
    mines est fermé aux recrutés depuis septembre 2010. Le routage le savait
    déjà — il envoyait ce mineur-là au régime général, en silence, et la page
    affichait « Mineur » au-dessus d'une pension de salarié du privé. Le refus
    dit la date, et le statut de droit commun qui porte le même calcul.

    La date opposée est celle de l'ENTRÉE dans le statut, au mois près,
    telle que le parcours l'a datée : un agent entré à la RATP en octobre
    2022 n'y a sa première ligne qu'en 2023, et n'est pas recruté après la
    fermeture pour autant.
    """
    for rang, metier in enumerate(parcours, start=1):
        ferme = _statut_ferme(affiliations, carriere, metier.affiliation)
        if ferme is None:
            continue
        fermeture, entree = ferme
        raise _refus(rang, _phrase_statut_ferme(
            affiliations, metier.affiliation, fermeture,
            f"ce métier commence en {entree}",
        ))


def _verifier_statuts_releve(affiliations: Affiliations, carriere) -> None:
    """Le même refus, opposé à un relevé de carrière.

    Le relevé ne compte pas de métiers : il porte des ANNÉES, dont chacune
    nomme son statut. La date opposée à la fermeture est donc la première
    année déclarée sous ce statut — janvier, faute d'un mois que le relevé ne
    donne pas —, et la phrase le dit plutôt que de parler d'un « métier n° 2 »
    qui n'existe nulle part sur la page.
    """
    for code in carriere.affiliations_utilisees():
        ferme = _statut_ferme(affiliations, carriere, code)
        if ferme is None:
            continue
        fermeture, entree = ferme
        raise ErreurSaisie(_phrase_statut_ferme(
            affiliations, code, fermeture,
            f"la première année déclarée sous ce statut est {entree.annee}",
        ))


def _statut_ferme(affiliations: Affiliations, carriere,
                  code: str) -> tuple[DateMois, DateMois] | None:
    """``(fermeture, entrée)`` si ce statut se déclare trop tard, sinon ``None``."""
    fermeture = affiliations.fermeture_entrants(code)
    if fermeture is None:
        return None
    entree = carriere.date_entree(code)
    if entree is None or entree.rang < fermeture.rang:
        return None
    return fermeture, entree


def _phrase_statut_ferme(affiliations: Affiliations, code: str,
                         fermeture: DateMois, quand: str) -> str:
    """Le refus, écrit une fois pour les deux formes de saisie.

    ``quand`` est la seule chose qui les sépare : un métier commence à un mois,
    une ligne de relevé n'a qu'une année. Écrire les deux phrases en entier les
    laisserait diverger — c'est la raison d'être de ``_refus`` juste au-dessus.
    """
    releve = affiliations.releve_par(code)
    return (
        f"Le statut « {affiliations.libelle(code)} » est fermé aux recrutés "
        f"depuis {formater_borne(fermeture)} ; {quand}. Depuis cette date, "
        f"il relève des mêmes régimes que « {affiliations.libelle(releve)} » : "
        "choisir ce statut."
    )


@dataclass(frozen=True)
class Montants:
    """Le mode net/brut, et ce qu'il fait à chaque montant affiché.

    Un seul objet, construit une fois par rendu, pour que la bascule n'existe
    qu'à un endroit. Deux grandeurs n'ont pas le même barème — un salaire
    supporte des cotisations, une pension n'en supporte plus — et deux autres
    n'ont pas de net du tout : un CAPITAL notionnel et une ASSIETTE de
    cotisation sont bruts par nature, et le site les laisse tels quels.
    """

    net: bool
    #: Ce qui sépare une pension brute de sa nette : CSG 8,30 %, CRDS 0,50 %,
    #: CASA 0,30 %. Voir ``remuneration.PrelevementsPension``.
    taux_pension: float

    @classmethod
    def depuis(cls, saisie: Saisie, base: Parametres,
               comparaison: Comparaison | None = None) -> "Montants":
        pensions = charger_prelevements(base.racine_donnees).pensions
        # Le rapport net/brut du salaire se lit sur la DERNIÈRE fiche de paie
        # de la carrière, celle de l'année du départ : c'est l'année dont le
        # revenu sert de dénominateur au taux de remplacement.
        # La proposition a SA fiche de paie : elle prélève moins sur le même
        # brut, et le dernier salaire net auquel sa pension se compare est le
        # sien — celui que la ligne affiche à côté de sa pension.
        rapport = rapport_proposition = 0.0
        remuneration = getattr(comparaison, "remuneration", None)
        if remuneration is not None:
            derniere = remuneration.annees[-1]
            if derniere.droit_en_vigueur.brut > 0:
                rapport = derniere.droit_en_vigueur.net / derniere.droit_en_vigueur.brut
            if derniere.proposition.brut > 0:
                rapport_proposition = derniere.proposition.net / derniere.proposition.brut
        return cls(net=saisie.en_net, taux_pension=pensions.taux_total,
                   rapport_net_brut_salaire=rapport,
                   rapport_net_brut_proposition=rapport_proposition)

    def pension(self, brut: float) -> float:
        """Une pension, une rente, une garantie : tout ce qui se sert après."""
        return brut * (1.0 - self.taux_pension) if self.net else brut

    def salaire(self, fiche) -> float:
        """Un salaire, lu sur la fiche de paie qui porte déjà les deux."""
        return fiche.net if self.net else fiche.brut

    def taux_remplacement(self, taux_brut: float, proposition: bool = False) -> float:
        """Le taux de remplacement, dans la langue du mode.

        Le modèle le calcule brut sur brut : une pension brute rapportée au
        dernier revenu d'activité brut. Affiché à côté de montants NETS, il
        deviendrait le seul chiffre de la page à parler l'autre langue — et il
        mentirait dans un sens précis, car un même écart de brut se traduit par
        un écart de net PLUS GRAND : une pension est moins prélevée qu'un
        salaire, 9,1 % contre une vingtaine de points.

        Le taux net vaut donc le taux brut multiplié par le rapport des deux
        prélèvements. C'est un fait connu, et rarement montré : en France, le
        taux de remplacement net dépasse le taux brut de plusieurs points.

        ``proposition`` prend le rapport de SA fiche de paie : le même brut y
        laisse un net plus élevé, et le taux de la proposition se comparait
        jusqu'au 22 septembre 2026 au net du droit en vigueur, qu'elle ne
        prélève pas.
        """
        rapport = (self.rapport_net_brut_proposition if proposition
                   else self.rapport_net_brut_salaire)
        if not self.net or rapport <= 0:
            return taux_brut
        return taux_brut * (1.0 - self.taux_pension) / rapport

    #: Ce qu'un euro de salaire brut laisse en net, au DERNIER revenu
    #: d'activité — le dénominateur du taux de remplacement. Zéro quand le
    #: statut n'a pas de fiche de paie : le taux reste alors brut, faute de
    #: pouvoir le netter honnêtement.
    rapport_net_brut_salaire: float = 0.0
    #: Le même, sur la fiche de paie de la PROPOSITION.
    rapport_net_brut_proposition: float = 0.0

    @property
    def mot(self) -> str:
        return "net" if self.net else "brut"

    @property
    def unite_salaire(self) -> str:
        return "€ net/mois" if self.net else "€ brut/mois"

    @property
    def unite_pension(self) -> str:
        return "€ net/mois" if self.net else "€ brut/mois"
