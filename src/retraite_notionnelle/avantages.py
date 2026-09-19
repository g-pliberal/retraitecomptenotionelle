"""Les avantages non contributifs du scénario 1 : lesquels, depuis quand, combien.

Le scénario 1 est le droit en vigueur. Un compte notionnel ne sert que ce qui a
été cotisé. Tout ce qui sépare les deux est inventorié dans
``data/reference/legislation/avantages_non_contributifs.yaml`` ; ce module lit
cet inventaire et en tire deux grandeurs que la page « Avantages » montre.

CE QUE L'INVENTAIRE PORTE, ET QUE LE MODÈLE NE CALCULE PAS
-----------------------------------------------------------
Trente-neuf dispositifs, chacun avec sa date de création, sa date de fin quand
il est éteint, sa base légale et l'état du modèle à son égard. C'est une
DONNÉE, pas un résultat : la frise que la page trace ne suppose aucun calcul, et
c'est ce qui la rend sûre là où les masses ci-dessous sont fragiles.

LES DEUX SÉRIES DE COÛT, ET POURQUOI ELLES NE DISENT PAS LA MÊME CHOSE
------------------------------------------------------------------------
1. **Ce que l'avantage ajoute au MONTANT de la pension.** La cascade du
   scénario 1 en isole huit ; deux autres — les périodes assimilées et la
   catégorie active — sont servies sans être isolées, leur effet passant par un
   trimestre ou par un âge, et se mesurent par RECALCUL : on refait la pension
   sans l'avantage, à date de liquidation inchangée, et l'écart est la ligne.
   Les dix masses sont ensuite portées de l'individu au collectif par la méthode
   de :mod:`cout` — part de la masse × dépense observée —, sans en changer une
   ligne.

2. **Ce qu'un avantage d'ÂGE coûte en ANNÉES DE SERVICE.** C'est le second
   effet, et il est treize fois plus lourd que le premier. Une pension servie de
   cinquante-deux à soixante-quatre ans est douze annuités que personne n'a
   cotisées et qu'aucune décote ne rattrape : l'article L. 14 la plafonne à vingt
   trimestres, si bien que l'agent classé et l'agent sédentaire partis le même
   jour butent sur le même plafond. Une décote plafonnée ne sait pas dire qui
   part cinq ans trop tôt. :func:`masses_anticipees` compte ces annuités à l'âge
   légal de chaque génération, et les ventile par ce qui les ouvre.

CE QUE CES SÉRIES VALENT, ET IL FAUT LE DIRE AVANT DE LES LIRE
----------------------------------------------------------------
La grille de cas types n'est pas une population. Un seul de ses treize cas types
a des enfants, un seul porte des interruptions, aucun ne connaît le chômage. Les
masses qui en sortent sont donc des PLANCHERS, et très bas : 3 % de la dépense
là où le COR chiffre les droits de solidarité à « de l'ordre d'un cinquième ».
Vingt-neuf des trente-neuf dispositifs n'y sont d'ailleurs pas — la réversion en
tête, première dépense non contributive du système, qu'un modèle décrivant une
carrière et non un ménage ne peut pas voir.

C'est pourquoi la page mène par la FRISE, qui est exacte, et ne donne les masses
qu'ensuite, sous leur réserve.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .castypes import CAS_TYPES, CasType
from .cout import _DEMI_TRANCHE, _ponderation, generations
from .donnees.chargement import charger_yaml
from .donnees.depenses import DepensesRetraite
from .donnees.population import Population
from .simulateur import Simulateur

#: Les quatre états possibles du modèle à l'égard d'un avantage. Vocabulaire
#: fermé : un cinquième état inventé au fil de l'eau rendrait l'inventaire
#: illisible, et un test le refuse.
ETATS: frozenset[str] = frozenset({"chiffre", "integre", "declare", "absent"})

#: Les trois façons d'en mesurer le coût.
MESURES: frozenset[str] = frozenset({"modele", "serie_publiee", "aucune"})

#: La part contributive, sous une clé qui ne peut être celle d'aucun avantage.
CONTRIBUTIF = "_contributif"

#: Les avantages que le scénario 1 sert mais que la cascade N'ISOLE PAS, et
#: qu'on mesure donc par recalcul. Leur montant est PRIS SUR la part
#: contributive, où la cascade les avait laissés faute de savoir les séparer :
#: la somme des parts vaut donc toujours la pension entière.
RECALCULS: tuple[str, ...] = (
    "periodes_assimilees",
    "categorie_active",
    "age_jouissance_militaire",
)

#: Pour chaque statut CLASSÉ, le statut sédentaire de mêmes régimes.
#:
#: Le classement tient à l'emploi et non à la personne : la contrefactuelle d'un
#: agent de catégorie active est le même agent, même caisse, même traitement,
#: dont l'emploi ne serait pas classé. Les régimes sont identiques des deux
#: côtés — un test l'exige —, si bien que l'écart ne porte que sur l'âge opposé
#: et sur ce qui en découle.
#:
#: Les militaires y figurent sous leur propre ligne : ce n'est pas un classement
#: d'emploi, c'est une pension qui s'ouvre à une DURÉE DE SERVICES et non à un
#: âge. Leur contrefactuelle est le fonctionnaire d'État, qui relève des mêmes
#: régimes qu'eux — et elle est refusée, voir :func:`recalculer`.
SEDENTAIRE: dict[str, tuple[str, str]] = {
    "fonctionnaire_etat_actif": ("fonctionnaire_etat", "categorie_active"),
    "fonctionnaire_etat_super_actif": ("fonctionnaire_etat", "categorie_active"),
    "fonctionnaire_territorial_hospitalier_actif": (
        "fonctionnaire_territorial_hospitalier", "categorie_active"),
    "fonctionnaire_territorial_hospitalier_super_actif": (
        "fonctionnaire_territorial_hospitalier", "categorie_active"),
    "ouvrier_etat_actif": ("ouvrier_etat", "categorie_active"),
    "militaire": ("fonctionnaire_etat", "age_jouissance_militaire"),
    "militaire_officier": ("fonctionnaire_etat", "age_jouissance_militaire"),
}

#: Les trois familles de départ anticipé. Elles ne se recouvrent pas : un départ
#: est ouvert par un motif et un seul.
#:
#: Les confondre est la meilleure manière de se tromper de réforme. La CARRIÈRE
#: LONGUE regarde la durée cotisée, donc est la moins éloignée d'un principe
#: contributif ; le CLASSEMENT de l'emploi ne regarde ni la durée ni la
#: pénibilité réelle, mais le corps d'appartenance ; l'âge propre d'un RÉGIME
#: SPÉCIAL ne regarde que le régime.
MOTIFS: tuple[str, ...] = ("carriere_longue", "classement", "regime_special")

#: Le libellé de chaque motif, pour la légende du graphique.
LIBELLES_MOTIFS: dict[str, str] = {
    "carriere_longue": "Carrière longue",
    "classement": "Catégorie active",
    "regime_special": "Régimes spéciaux",
}


@dataclass(frozen=True)
class Avantage:
    """Une ligne de l'inventaire."""

    code: str
    libelle: str
    famille: str
    quoi: str
    base_legale: tuple[str, ...]
    #: Année de création du dispositif, et année de sa fin quand il est éteint.
    #: ``fin`` à ``None`` veut dire « en vigueur », et c'est ce que la frise
    #: trace jusqu'au bord droit.
    creation: int
    fin: int | None
    regimes: str
    etat_modele: str
    #: Code de la ligne de cascade qui l'isole, quand elle existe.
    ligne_cascade: str | None
    mesurable_par: str

    @property
    def chiffre(self) -> bool:
        """Le modèle sait-il dire ce que cette ligne coûte ?"""
        return self.ligne_cascade is not None or self.code in RECALCULS

    def dictionnaire(self) -> dict:
        """Ce que le paquet de données transporte, et que le portage relit."""
        return {
            "code": self.code,
            "libelle": self.libelle,
            "famille": self.famille,
            "quoi": self.quoi,
            "base_legale": list(self.base_legale),
            "creation": self.creation,
            "fin": self.fin,
            "regimes": self.regimes,
            "etat_modele": self.etat_modele,
            "ligne_cascade": self.ligne_cascade,
            "mesurable_par": self.mesurable_par,
        }


@dataclass(frozen=True)
class Famille:
    """Un groupe de l'inventaire, dans l'ordre où la frise les empile."""

    code: str
    libelle: str
    quoi: str


@dataclass(frozen=True)
class Inventaire:
    """Les trente-neuf dispositifs, et les familles qui les rangent."""

    familles: tuple[Famille, ...]
    avantages: tuple[Avantage, ...]

    def par_famille(self, code: str) -> tuple[Avantage, ...]:
        return tuple(a for a in self.avantages if a.famille == code)

    def compte(self, etat: str) -> int:
        return sum(1 for a in self.avantages if a.etat_modele == etat)

    @property
    def chiffres(self) -> tuple[Avantage, ...]:
        return tuple(a for a in self.avantages if a.chiffre)

    def libelle_de_ligne(self, ligne: str) -> str:
        """Le nom d'une ligne de coût, qui peut porter deux dispositifs.

        La MDA et la bonification pour enfants de la fonction publique partagent
        une ligne de cascade : le même trimestre gratuit, sous deux textes. La
        légende du graphique doit donc les nommer toutes les deux.
        """
        portes = [a.libelle for a in self.avantages
                  if a.ligne_cascade == ligne or a.code == ligne]
        return " / ".join(sorted(portes)) if portes else ligne


def charger_avantages(racine: Path) -> Inventaire:
    """L'inventaire, dans l'ordre du fichier, validé champ par champ."""
    chemin = racine / "reference" / "legislation" / "avantages_non_contributifs.yaml"
    contenu = charger_yaml(chemin)
    familles = tuple(
        Famille(code=code, libelle=fiche["libelle"], quoi=fiche["quoi"])
        for code, fiche in contenu["familles"].items()
    )
    connues = {famille.code for famille in familles}
    avantages: list[Avantage] = []
    codes: set[str] = set()
    for fiche in contenu["avantages"]:
        code = str(fiche["code"])
        if code in codes:
            raise ValueError(f"{chemin.name} : code dupliqué {code}")
        codes.add(code)
        if fiche["famille"] not in connues:
            raise ValueError(
                f"{chemin.name} / {code} : famille inconnue {fiche['famille']!r}"
            )
        if fiche["etat_modele"] not in ETATS:
            raise ValueError(
                f"{chemin.name} / {code} : état inconnu {fiche['etat_modele']!r}"
            )
        mesure = fiche["cout"]["mesurable_par"]
        if mesure not in MESURES:
            raise ValueError(f"{chemin.name} / {code} : mesure inconnue {mesure!r}")
        avantages.append(Avantage(
            code=code,
            libelle=fiche["libelle"],
            famille=fiche["famille"],
            quoi=" ".join(fiche["quoi"].split()),
            base_legale=tuple(fiche.get("base_legale") or ()),
            creation=int(fiche["creation"]),
            fin=None if fiche.get("fin") is None else int(fiche["fin"]),
            regimes=fiche["regimes"],
            etat_modele=fiche["etat_modele"],
            ligne_cascade=fiche["ligne_cascade"],
            mesurable_par=mesure,
        ))
    return Inventaire(familles=familles, avantages=tuple(avantages))


def inventaire_depuis_paquet(lignes: dict) -> Inventaire:
    """L'inventaire relu depuis le paquet de données, tel que le site le charge."""
    return Inventaire(
        familles=tuple(Famille(**famille) for famille in lignes["familles"]),
        avantages=tuple(Avantage(**avantage) for avantage in lignes["avantages"]),
    )


# ---------------------------------------------------------------------------
# Le chiffrage
# ---------------------------------------------------------------------------


def carriere_variante(simulateur: Simulateur, cas: CasType, generation: int,
                      age: float, affiliation: str | None = None,
                      interruptions: dict[int, str] | None = None):
    """La carrière d'un cas type, avec une variante possible.

    Reprend ``CasType._carriere`` à deux libertés près, qui sont exactement les
    deux contrefactuelles : le statut d'affiliation, et le motif des périodes
    non travaillées. L'âge de liquidation est PASSÉ et non recalculé — c'est ce
    qui tient les deux pensions comparables.
    """
    reelles = {
        int(generation + cas.age_debut + decalage): motif
        for decalage, motif in cas.interruptions_relatives
    }
    return simulateur.carriere_simple(
        annee_naissance=generation,
        sexe=cas.sexe,
        affiliation=affiliation or cas.affiliation,
        age_debut=cas.age_debut,
        age_liquidation=age,
        niveau_salaire=cas.niveau_salaire,
        profil_carriere=cas.profil_carriere,
        interruptions=reelles if interruptions is None else interruptions,
        nombre_enfants=cas.nombre_enfants,
        part_primes=cas.part_primes,
        identifiant=f"{cas.libelle} (génération {generation})",
    )


def recalculer(simulateur: Simulateur, cas: CasType, generation: int,
               age: float, reelle) -> tuple[dict[str, float], dict[str, str]]:
    """Les avantages non isolés par la cascade, mesurés par recalcul.

    Rend un dictionnaire VIDE quand la carrière n'en porte aucun, plutôt qu'un
    zéro : la plupart des cas types sont dans ce cas, et un zéro écrit
    laisserait croire à une mesure là où il n'y a rien à mesurer.

    DEUX PRÉCAUTIONS ET UN GARDE-FOU.

    La première précaution évite un double compte. Neutraliser les périodes non
    travaillées retire les trimestres assimilés ET l'AVPF, que la cascade
    chiffre déjà sous sa propre ligne. On la retranche donc de l'écart brut.

    La seconde est une interaction qu'on ne mesure pas. Retirer deux avantages
    d'âge à la fois n'est pas la somme de deux retraits — la décote est
    plafonnée, et deux pénalités qui butent sur le même plafond ne s'additionnent
    pas. Aucun cas type de la grille ne porte les deux (les interruptions sont
    sur une carrière du privé, le classement sur des carrières publiques), et un
    test l'exige ; si cela changeait, ce calcul devrait changer aussi.

    LE GARDE-FOU refuse plutôt que de rendre un chiffre faux. Un changement de
    statut ne vaut comme contrefactuelle que s'il ne déplace QUE l'âge opposé.
    Quand il déplace aussi la DURÉE REQUISE, le rapport de proratisation change
    avec lui et l'écart ne mesure plus l'avantage : c'est le cas du militaire,
    dont la pension exige 172 trimestres là où le fonctionnaire civil en exige
    160, si bien que la contrefactuelle civile rend une pension PLUS FORTE et
    l'avantage un montant négatif. L'appelant reçoit le refus et sa raison. Ce
    que la jouissance militaire coûte est une affaire d'annuités servies, que
    :func:`masses_anticipees` mesure et que celle-ci ne mesurera jamais.
    """
    parts: dict[str, float] = {}
    refus: dict[str, str] = {}
    if cas.interruptions_relatives:
        sans = simulateur.scenario_actuel.calculer(carriere_variante(
            simulateur, cas, generation, age,
            interruptions={
                int(generation + cas.age_debut + decalage): "sans_activite"
                for decalage, _ in cas.interruptions_relatives
            },
        ))
        avpf = sum(a.montant for a in reelle.avantages_appliques if a.code == "avpf")
        ecart = reelle.pension_annuelle - sans.pension_annuelle - avpf
        if ecart > 0.0:
            parts["periodes_assimilees"] = ecart
    if cas.affiliation in SEDENTAIRE:
        temoin, ligne = SEDENTAIRE[cas.affiliation]
        sans = simulateur.scenario_actuel.calculer(
            carriere_variante(simulateur, cas, generation, age, affiliation=temoin)
        )
        if sans.trimestres_requis != reelle.trimestres_requis:
            refus[ligne] = (
                f"{cas.code} : la contrefactuelle {temoin} exige "
                f"{sans.trimestres_requis} trimestres contre "
                f"{reelle.trimestres_requis} — la proratisation change avec le "
                f"statut, l'écart ne mesure plus l'âge"
            )
        else:
            ecart = reelle.pension_annuelle - sans.pension_annuelle
            if ecart > 0.0:
                parts[ligne] = ecart
    return parts, refus


def motif_de_depart(cas: CasType, actuel) -> str:
    """Ce qui ouvre ce départ, quand il est anticipé.

    Le modèle nomme la carrière longue lui-même (``motif_ouverture``) ; les deux
    autres se lisent au statut, le classement étant celui des sept affiliations
    que ``legislation/affiliations.yaml`` marque.
    """
    if actuel.motif_ouverture == "carriere_longue":
        return "carriere_longue"
    if cas.affiliation in SEDENTAIRE:
        return "classement"
    return "regime_special"


@dataclass(frozen=True)
class Pensionne:
    """Un couple (cas type, génération), et sa pension décomposée."""

    code: str
    generation: int
    annee_liquidation: int
    age_liquidation: float
    #: Part contributive et avantages, en euros CONSTANTS de l'année de
    #: référence. Les clés sont les lignes de coût ; leur somme vaut la pension.
    parts: dict[str, float]
    motif: str


@dataclass
class AnneeAvantages:
    """Une année de la décomposition."""

    annee: int
    #: Dépense observée, en millions d'euros courants.
    observee: float
    #: Coût de chaque ligne, en millions d'euros courants de l'année.
    lignes: dict[str, float]
    #: Coût des pensions servies avant l'âge légal, par motif d'ouverture.
    anticipees: dict[str, float]

    @property
    def gratuit(self) -> float:
        return sum(self.lignes.values())

    @property
    def anticipee(self) -> float:
        return sum(self.anticipees.values())


@dataclass
class CoutAvantages:
    """Ce que les avantages non contributifs coûtent, année par année."""

    annees: tuple[AnneeAvantages, ...] = ()
    #: Les lignes effectivement chiffrées, par coût décroissant de la dernière
    #: année : c'est l'ordre de la légende et celui des bandes empilées.
    lignes: tuple[str, ...] = ()
    #: Ce que le garde-fou a refusé de mesurer, et pourquoi. Un refus est un
    #: résultat : la page l'affiche au lieu de le taire.
    refus: dict[str, str] = field(default_factory=dict)
    ponderation: str = "effectifs"

    @property
    def derniere(self) -> AnneeAvantages | None:
        return self.annees[-1] if self.annees else None


def decomposer(simulateur: Simulateur, liquidation: str = "droit"
               ) -> tuple[list[Pensionne], dict[str, str]]:
    """La pension de chaque couple (cas type, génération), part par part.

    LE SCÉNARIO 1 SEUL EST CALCULÉ, et c'est ce qui rend la page tenable.
    ``calculer_cas_types`` rend les six scénarios — trente-cinq millisecondes
    par couple —, alors que cette décomposition n'a besoin que de l'étalon, qui
    en coûte trois. Sur les trois cent quarante-deux couples de la grille, la
    différence est celle d'une page qui s'ouvre et d'une page qui fait attendre.
    Les deux garde-fous de ``calculer_cas_types`` sont repris tels quels : une
    liquidation antérieure à la répartition et une carrière dont aucun régime
    n'était actif sont écartées plutôt que de faire échouer l'ensemble.

    LE REFUS EST CONTAGIEUX, et il doit l'être. La durée requise d'un statut
    varie par génération : une contrefactuelle peut être propre pour les unes et
    faussée pour les autres. Garder les premières donnerait une série qui ne
    porte qu'un morceau de sa population — un agrégat biaisé, et dont le biais
    serait invisible. Une ligne refusée quelque part est donc retirée PARTOUT,
    et son montant rendu à la part contributive d'où il venait.
    """
    macro = simulateur.macro
    annee_euros = simulateur.parametres.annee_euros_constants
    debut = simulateur.parametres.annee_debut_repartition
    pensionnes: list[Pensionne] = []
    refus: dict[str, str] = {}
    for cas in CAS_TYPES:
        for generation in generations():
            try:
                age = cas.age_liquidation_pour(simulateur, generation, liquidation)
                carriere = carriere_variante(simulateur, cas, generation, age)
                if carriere.annee_liquidation <= debut:
                    continue
                if not any(simulateur.affiliations.regimes(cas.affiliation, ligne.annee)
                           for ligne in carriere.lignes):
                    continue
                actuel = simulateur.scenario_actuel.calculer(carriere)
            except (ValueError, KeyError):
                continue
            parts = {CONTRIBUTIF: actuel.total_contributif}
            for avantage in actuel.avantages_appliques:
                parts[avantage.code] = parts.get(avantage.code, 0.0) + avantage.montant
            mesures, refuses = recalculer(simulateur, cas, generation, age, actuel)
            refus.update(refuses)
            for ligne, montant in mesures.items():
                parts[ligne] = parts.get(ligne, 0.0) + montant
                parts[CONTRIBUTIF] -= montant
            coefficient = macro.coefficient_prix(carriere.annee_liquidation, annee_euros)
            pensionnes.append(Pensionne(
                code=cas.code,
                generation=generation,
                annee_liquidation=carriere.annee_liquidation,
                age_liquidation=age,
                parts={cle: valeur * coefficient for cle, valeur in parts.items()},
                motif=motif_de_depart(cas, actuel),
            ))
    for pensionne in pensionnes:
        for ligne in refus:
            montant = pensionne.parts.pop(ligne, 0.0)
            pensionne.parts[CONTRIBUTIF] += montant
    return pensionnes, refus


def masses(pensionnes: list[Pensionne], population: Population, annee: int,
           poids_cas: dict[str, float]) -> dict[str, float]:
    """La masse de chaque part une année donnée.

    Copie fidèle de la pondération de :func:`cout._masses` pour le scénario 1 :
    chaque génération de la grille en représente cinq, parcourues une à une,
    chacune liquidant sa propre année. Le scénario 1 n'est pas revalorisé — le
    droit l'indexe sur les prix et les masses sont déjà en euros constants —, si
    bien qu'un seul poids suffit, celui des têtes.
    """
    total: dict[str, float] = {}
    for pensionne in pensionnes:
        part_cas = poids_cas.get(pensionne.code, 0.0)
        if part_cas <= 0.0:
            continue
        poids = 0.0
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            if annee < pensionne.annee_liquidation + decalage:
                continue
            poids += population.effectif(annee - pensionne.generation - decalage, annee)
        if poids <= 0.0:
            continue
        for cle, montant in pensionne.parts.items():
            total[cle] = total.get(cle, 0.0) + part_cas * poids * montant
    return total


def masses_anticipees(pensionnes: list[Pensionne], simulateur: Simulateur,
                      population: Population, annee: int,
                      poids_cas: dict[str, float]
                      ) -> tuple[float, dict[str, float]]:
    """La masse servie AVANT l'âge légal de droit commun, ventilée par motif.

    La comparaison se fait à l'âge légal de la GÉNÉRATION, lu dans
    ``legislation/age_ouverture_requis.csv``, et non à un âge fixe : opposer
    soixante-quatre ans à une génération qui relevait de soixante compterait
    comme anticipé un départ que le droit de l'époque disait à l'heure.

    La ventilation par motif est l'essentiel du résultat. Le coût des départs
    anticipés n'a pas la même origine selon l'époque : il vient des statuts
    classés et des régimes spéciaux tant que ceux-ci pèsent, puis de la carrière
    longue à mesure que l'âge légal monte au-dessus de l'âge auquel les
    carrières commencées tôt réunissent leur durée.
    """
    ages = simulateur.scenario_actuel.ages_ouverture
    totale = 0.0
    par_motif = {motif: 0.0 for motif in MOTIFS}
    for pensionne in pensionnes:
        part_cas = poids_cas.get(pensionne.code, 0.0)
        if part_cas <= 0.0:
            continue
        pension = sum(pensionne.parts.values())
        # L'ÂGE LÉGAL EST CELUI DE LA GÉNÉRATION DE LA GRILLE, et il est lu une
        # seule fois — non celui de chacune des cinq cohortes que la tranche
        # représente. La nuance n'est pas un raffinement.
        #
        # L'âge de DÉPART a été calculé une fois, pour la génération de la
        # grille, et les cinq cohortes le portent tel quel : c'est la convention
        # de `cout._masses`, qui décale l'année de liquidation et garde l'âge.
        # Opposer cet âge-là à l'âge légal d'une cohorte plus jeune revenait
        # donc à déclarer anticipé un départ que rien n'avançait, et la réforme
        # de 2023 — un trimestre d'âge légal par génération — faisait tripler la
        # série sur ses deux dernières années par ce seul effet de bord. Un
        # départ est anticipé ou il ne l'est pas ; il ne l'est pas à moitié
        # parce que la tranche est large de cinq ans.
        legal = ages.age(pensionne.generation)
        seuil = None if legal is None else legal[0]
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            cohorte = pensionne.generation + decalage
            if annee < pensionne.annee_liquidation + decalage:
                continue
            age_atteint = annee - cohorte
            effectif = population.effectif(age_atteint, annee)
            if effectif <= 0.0:
                continue
            masse = part_cas * effectif * pension
            totale += masse
            # Et seules les ANNÉES précoces comptent, non toute la retraite de
            # qui est parti tôt : la grandeur cherchée est l'annuité servie
            # avant l'âge légal, qui s'éteint le jour où l'assuré l'atteint.
            if seuil is not None and age_atteint < seuil:
                par_motif[pensionne.motif] += masse
    return totale, par_motif


def calculer_avantages(simulateur: Simulateur, depenses: DepensesRetraite,
                       population: Population, ponderation: str = "effectifs",
                       liquidation: str = "droit") -> CoutAvantages:
    """Les deux séries, année par année, sur la fenêtre des dépenses publiées.

    Les années où le modèle ne sert AUCUNE pension — celles d'avant la première
    liquidation possible — sont écartées : une part y serait une division par
    zéro, et non un résultat.
    """
    pensionnes, refus = decomposer(simulateur, liquidation)
    poids = _ponderation(simulateur, ponderation, CAS_TYPES)
    annees: list[AnneeAvantages] = []
    for annee in depenses.annees():
        poids_annee = poids(annee)
        parts = masses(pensionnes, population, annee, poids_annee)
        totale = sum(parts.values())
        if totale <= 0.0:
            continue
        observee = depenses.depense(annee)
        masse, par_motif = masses_anticipees(
            pensionnes, simulateur, population, annee, poids_annee)
        annees.append(AnneeAvantages(
            annee=annee,
            observee=observee,
            lignes={cle: observee * valeur / totale
                    for cle, valeur in parts.items() if cle != CONTRIBUTIF},
            anticipees={motif: observee * valeur / masse if masse > 0.0 else 0.0
                        for motif, valeur in par_motif.items()},
        ))
    derniere = annees[-1].lignes if annees else {}
    # Le code départage les ex aequo : sans lui, l'ordre viendrait d'un
    # ensemble, donc du hasard du hachage, et la légende du graphique changerait
    # d'une exécution à l'autre — ce qu'un témoin figé ne pardonne pas.
    lignes = tuple(sorted(
        {cle for annee in annees for cle in annee.lignes},
        key=lambda cle: (-derniere.get(cle, 0.0), cle),
    ))
    return CoutAvantages(annees=tuple(annees), lignes=lignes, refus=refus,
                         ponderation=ponderation)
