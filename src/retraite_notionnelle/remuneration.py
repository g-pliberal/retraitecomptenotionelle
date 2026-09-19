"""La fiche de paie : coût du travail, salaire brut, salaire net.

Tout le reste du dépôt calcule des PENSIONS. Ce module calcule ce qui se passe
AVANT — ce qu'un actif touche pendant qu'il cotise —, et il n'existe que pour
une raison : une réforme qui change le taux de cotisation retraite change le
salaire net, et personne ne le chiffre jamais.

LES TROIS MONTANTS, ET CE QUI LES SÉPARE
----------------------------------------
    coût du travail = brut + cotisations patronales − réduction générale
    salaire net     = brut − cotisations salariales − CSG − CRDS

Le premier est ce que l'emploi coûte à l'employeur ; le dernier est ce qui
tombe sur le compte du salarié. Entre les deux, l'écart vaut aujourd'hui près
de la moitié du coût du travail, et la retraite en est le premier poste.

CE QUE CE MODULE NE DÉCIDE PAS, ET QUI EST ÉCRIT DANS LES DONNÉES
------------------------------------------------------------------
Les taux sont dans ``legislation/prelevements_remuneration.yaml`` pour tout ce
qui n'est pas la retraite, et dans les fiches de régime pour ce qui l'est :
la fiche de paie et le compte notionnel lisent donc la même grandeur au même
endroit, et ne peuvent pas diverger.

L'INCIDENCE : CE QUE L'EMPLOYEUR NE VERSE PLUS, LE SALARIÉ LE REÇOIT
--------------------------------------------------------------------
Une cotisation patronale n'apparaît pas sur la fiche de paie, et pourtant elle
est prélevée sur le travail du salarié : c'est du salaire différé, versé à une
caisse plutôt qu'à lui. La question — qui la supporte vraiment ? — a une
réponse à peu près consensuelle en économie du travail à long terme : le
salarié, par un salaire brut plus bas que ce que l'employeur aurait consenti.

Le module retient donc **l'incidence intégrale au salarié**, et il la calcule
au lieu de la postuler : le COÛT DU TRAVAIL est tenu fixe — c'est ce que
l'employeur a budgété pour ce poste, et aucune réforme des retraites ne le
change —, et le salaire brut est celui qui l'épuise sous les nouveaux taux.
Le net s'en déduit. C'est ce que veut dire « réduire l'écart entre le net et le
brut » : la baisse du prélèvement remonte dans le brut, puis dans le net.

C'est une HYPOTHÈSE, la plus favorable à une baisse de cotisation, et le site
l'écrit là où il affiche le chiffre. La lecture prudente — seule la part
salariale bouge, l'employeur garde son économie — donne à peu près la moitié
du gain ; elle est disponible par ``incidence="salariale"``.

LE PARTAGE DES 18 %, ET POURQUOI IL N'EST PAS ANODIN
-----------------------------------------------------
La proposition fixe un taux unique de 18 %, « salariale et patronale
additionnées », et ne dit pas qui porte quoi. Le modèle partage **moitié-moitié**
— 9 % et 9 % —, et de même pour les 5 % capitalisés.

On attendrait ce partage sans effet sous l'incidence intégrale : à coût du
travail donné, ce qui n'est pas versé à une caisse est versé au salarié, quel
que soit le nom de la ligne. C'est FAUX, et les tests l'ont montré. Le partage
déplace le salaire net, pour deux raisons qui n'ont rien à voir l'une avec
l'autre :

1. **La CSG et la CRDS sont assises sur le BRUT**, non sur le coût du travail.
   Faire porter un point à l'employeur plutôt qu'au salarié rétrécit le brut,
   donc leur assiette, donc leur montant. Dix points déplacés valent un point
   de net. L'algèbre est courte : à coût C fixé, le net vaut
   ``C − brut × (taux total + autres patronaux + CSG-CRDS)``, et le brut, lui,
   décroît quand la part patronale grossit.
2. **La réduction générale n'efface que des cotisations PATRONALES.** En deçà
   de trois SMIC, plus la part patronale est grosse, plus l'allègement l'est,
   plus il reste de coût du travail à verser en salaire.

Les deux jouent dans le même sens, et fort : au salaire moyen comme à quatre
SMIC, faire porter les 23 points entièrement à l'employeur plutôt que
moitié-moitié vaut plusieurs milliers d'euros de net par an. Le partage retenu
est donc le choix MÉDIAN d'un paramètre que la proposition laisse ouvert, et pas
une commodité d'écriture. ``part_salariale_taux_unique`` le rend réglable, et
deux tests fixent les deux mécanismes.

C'est, au passage, un résultat sur le système actuel plus que sur la
proposition : notre droit fait dépendre le salaire net de la FRONTIÈRE entre
part salariale et part patronale, alors que cette frontière ne change rien à
ce que le travail coûte ni à ce qu'il rapporte au système.

LA RÉDUCTION GÉNÉRALE, ET POURQUOI ELLE NE PEUT PAS ÊTRE IGNORÉE
-----------------------------------------------------------------
Depuis le 1er janvier 2026, la réduction générale dégressive unique annule au
niveau du SMIC la TOTALITÉ des cotisations patronales de son périmètre — son
coefficient maximal, 40,21 %, est exactement la somme de ces taux — et
s'éteint à trois SMIC. Deux conséquences, et la seconde est un résultat :

1. Sans elle, le coût du travail d'un salarié au SMIC serait surestimé de plus
   d'un quart.
2. **Au voisinage du SMIC, baisser la cotisation retraite de l'employeur ne
   rend rien**, parce qu'il n'en versait déjà plus. La loi le dit : le
   coefficient maximal est fixé « dans la limite de la somme des taux des
   cotisations et contributions incluses dans le périmètre ». Le modèle refait
   donc l'addition au lieu de figer le chiffre — un allègement ne peut pas
   alléger une cotisation qui n'existe plus. Le gain d'une baisse de cotisation
   est ainsi nul au SMIC, et croît jusqu'à trois SMIC.

   C'est l'inverse de ce qu'un tract dirait, et c'est le genre de chose qu'un
   modèle sert à trouver.

À QUI CE MODULE S'APPLIQUE
--------------------------
Aux salariés du SECTEUR PRIVÉ, et à eux seuls : les taux ci-dessus sont ceux du
régime général. Un agent public, un artisan, un agent d'un régime spécial n'ont
ni les mêmes branches ni les mêmes assiettes, et leur « employeur » est l'État.
``fiche_de_paie_possible`` dit si le statut est couvert ; le site n'affiche rien
quand il ne l'est pas, et dit pourquoi.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .donnees.chargement import Fiabilite, charger_yaml

#: Heures d'un temps plein sur une année : 35 heures sur 52 semaines. Sert à
#: convertir le SMIC horaire — la seule forme que le dépôt publie — en SMIC
#: annuel, qui est la référence de la réduction générale.
HEURES_ANNUELLES_TEMPS_PLEIN = 1820.0

#: Familles de statuts auxquelles la fiche de paie s'applique. Voir le
#: docstring du module : les taux hors retraite sont ceux du régime général.
FAMILLES_COUVERTES = frozenset({"prive"})


@dataclass(frozen=True)
class Segment:
    """Un taux, appliqué à la part du salaire comprise entre deux bornes.

    Les bornes sont exprimées en PLAFONDS ANNUELS de la Sécurité sociale, comme
    les fiches de régime les écrivent ; ``haut_en_plafonds`` à ``None`` signifie
    « sans limite ».

    Des segments peuvent se RECOUVRIR, et c'est voulu : la cotisation vieillesse
    déplafonnée porte sur la totalité du salaire par-dessus la cotisation
    plafonnée, comme la contribution d'équilibre technique. Une forme cumulative
    — « jusqu'à tant de plafonds » — ne saurait pas les représenter, et c'est
    pour cela que celle-ci est explicite.
    """

    bas_en_plafonds: float
    haut_en_plafonds: float | None
    taux: float


def _montant(segments: tuple[Segment, ...], assiette: float,
             plafond_annuel: float) -> float:
    """Somme des taux appliqués segment par segment à une assiette."""
    total = 0.0
    for segment in segments:
        if segment.taux == 0.0:
            continue
        bas = segment.bas_en_plafonds * plafond_annuel
        haut = (assiette if segment.haut_en_plafonds is None
                else min(assiette, segment.haut_en_plafonds * plafond_annuel))
        if haut > bas:
            total += (haut - bas) * segment.taux
    return total


def _tranches(lignes) -> tuple[Segment, ...]:
    """Convertit la forme CUMULATIVE des données — commode à écrire — en segments.

    ``[{jusqu_en_plafonds: 1, taux: a}, {jusqu_en_plafonds: null, taux: b}]``
    devient ``[(0 → 1, a), (1 → ∞, b)]``.
    """
    segments: list[Segment] = []
    bas = 0.0
    for ligne in lignes or []:
        haut = (None if ligne.get("jusqu_en_plafonds") is None
                else float(ligne["jusqu_en_plafonds"]))
        segments.append(Segment(bas, haut, float(ligne["taux"])))
        if haut is None:
            break
        bas = haut
    return tuple(segments)


@dataclass(frozen=True)
class Poste:
    """Un prélèvement, avec ses deux barèmes."""

    code: str
    libelle: str
    #: Finance-t-il la retraite ? Vrai pour la CEG, la CET et l'APEC, que les
    #: fiches de régime ne portent pas parce qu'elles n'acquièrent aucun droit.
    retraite: bool
    #: Entre-t-il dans le périmètre de la réduction générale (L. 241-13) ?
    dans_la_reduction_generale: bool
    salarie: tuple[Segment, ...]
    employeur: tuple[Segment, ...]
    #: Taux patronal retenu DANS le périmètre de la réduction générale quand il
    #: diffère du taux appelé : l'AT-MP n'y entre qu'à hauteur de l'arrêté que
    #: vise le I de l'article L. 241-13. ``None`` = le taux appelé lui-même.
    taux_dans_la_reduction: float | None = None
    #: Dû par les seuls cadres (APEC).
    cadres_seulement: bool = False
    #: Dû seulement si la rémunération dépasse un plafond, mais assis alors sur
    #: la totalité du salaire (CET).
    due_au_dela_de_un_plafond: bool = False
    note: str = ""

    def du(self, brut: float, plafond_annuel: float, cadre: bool) -> bool:
        if self.cadres_seulement and not cadre:
            return False
        if self.due_au_dela_de_un_plafond and brut <= plafond_annuel:
            return False
        return True


@dataclass(frozen=True)
class ReductionGenerale:
    """La réduction générale dégressive unique, et de quoi la recalculer."""

    libelle: str
    plafond_en_smic: float
    puissance: float
    #: Plancher du coefficient, quel que soit le salaire sous le plafond.
    taux_minimum: float
    #: Valeur maximale du coefficient — celle qu'atteint un salaire au SMIC —,
    #: et somme exacte des taux du périmètre : au SMIC, la réduction efface la
    #: TOTALITÉ des cotisations patronales qu'elle vise.
    coefficient_maximal: float
    #: Ces taux, poste par poste. Leur somme est ``coefficient_maximal``, et un
    #: test l'exige : c'est ce qui relie le coefficient aux barèmes.
    composantes: dict[str, float]
    #: Celles de ces composantes qui financent la retraite, et qu'un scénario
    #: remplace donc par les siennes.
    composantes_retraite: tuple[str, ...]

    @property
    def taux_retraite_inclus(self) -> float:
        """Points de cotisation retraite patronale compris dans le coefficient."""
        return sum(self.composantes[code] for code in self.composantes_retraite)

    def coefficient_maximal_avec(self, taux_retraite_employeur: float) -> float:
        """Le coefficient maximal quand la retraite patronale change de taux.

        La loi le plafonne à la somme des taux du périmètre : on retire la
        retraite d'aujourd'hui et on ajoute celle du scénario. Le résultat ne
        descend jamais sous le plancher.
        """
        return max(
            self.taux_minimum,
            self.coefficient_maximal - self.taux_retraite_inclus
            + taux_retraite_employeur,
        )

    def coefficient(self, brut: float, smic_annuel: float,
                    taux_retraite_employeur: float) -> float:
        """Coefficient applicable à ce salaire, entre zéro et son maximum."""
        if brut <= 0 or smic_annuel <= 0:
            return 0.0
        if brut >= self.plafond_en_smic * smic_annuel:
            return 0.0
        maximal = self.coefficient_maximal_avec(taux_retraite_employeur)
        delta = maximal - self.taux_minimum
        rapport = max(0.0, 0.5 * (self.plafond_en_smic * smic_annuel / brut - 1.0))
        coefficient = self.taux_minimum + round(delta * rapport ** self.puissance, 4)
        return min(maximal, coefficient)


@dataclass(frozen=True)
class BaremePrelevements:
    """Tout ce que le droit prélève sur un salaire, hors retraite acquisitive."""

    annee: int
    postes: tuple[Poste, ...]
    csg_deductible: float
    csg_imposable: float
    crds: float
    abattement_frais: tuple[Segment, ...]
    reduction_generale: ReductionGenerale
    fiabilite: Fiabilite

    @property
    def csg(self) -> float:
        return self.csg_deductible + self.csg_imposable

    def taux_retraite_du_droit_en_vigueur(self) -> float:
        """Ce que le coefficient maximal compte aujourd'hui pour la retraite."""
        return self.reduction_generale.taux_retraite_inclus


@lru_cache(maxsize=4)
def _charger(chemin: str, signature: tuple) -> BaremePrelevements:
    contenu = charger_yaml(Path(chemin))
    postes = tuple(
        Poste(
            code=poste["code"],
            libelle=poste["libelle"],
            retraite=bool(poste.get("retraite", False)),
            dans_la_reduction_generale=bool(
                poste.get("dans_la_reduction_generale", False)),
            salarie=_tranches(poste.get("salarie")),
            employeur=_tranches(poste.get("employeur")),
            taux_dans_la_reduction=(
                None if poste.get("taux_dans_la_reduction") is None
                else float(poste["taux_dans_la_reduction"])),
            cadres_seulement=bool(poste.get("cadres_seulement", False)),
            due_au_dela_de_un_plafond=bool(
                poste.get("due_au_dela_de_un_plafond", False)),
            note=poste.get("note", ""),
        )
        for poste in contenu["postes"]
    )
    contributions = contenu["contributions_sociales"]
    reduction = contenu["reduction_generale"]
    return BaremePrelevements(
        annee=int(contenu["annee"]),
        postes=postes,
        csg_deductible=float(contributions["csg_deductible"]),
        csg_imposable=float(contributions["csg_imposable"]),
        crds=float(contributions["crds"]),
        abattement_frais=_tranches(
            contributions["abattement_frais_professionnels"]),
        reduction_generale=ReductionGenerale(
            libelle=reduction["libelle"],
            plafond_en_smic=float(reduction["plafond_en_smic"]),
            puissance=float(reduction["puissance"]),
            taux_minimum=float(reduction["taux_minimum"]),
            coefficient_maximal=float(reduction["coefficient_maximal"]),
            composantes={code: float(valeur)
                         for code, valeur in reduction["composantes"].items()},
            composantes_retraite=tuple(reduction["composantes_retraite"]),
        ),
        fiabilite=Fiabilite.depuis_texte(contenu.get("fiabilite", "haute")),
    )


def charger_prelevements(racine_donnees: Path) -> BaremePrelevements:
    """Le barème des prélèvements hors retraite, mémorisé sur la signature.

    Même convention que ``charger_yaml`` et ``charger_serie_annuelle`` : un
    fichier modifié est relu sans qu'on ait à vider quoi que ce soit.
    """
    chemin = racine_donnees / "reference" / "legislation" / "prelevements_remuneration.yaml"
    try:
        etat = chemin.stat()
        signature = (etat.st_mtime_ns, etat.st_size)
    except OSError:
        signature = ()
    return _charger(str(chemin), signature)


@dataclass(frozen=True)
class ComposanteRetraite:
    """Un étage du financement de la retraite, avec ses deux barèmes."""

    code: str
    libelle: str
    salarie: tuple[Segment, ...]
    employeur: tuple[Segment, ...]
    #: Entre-t-il dans le périmètre de la réduction générale ? Vrai de la
    #: vieillesse de base et de la complémentaire légalement obligatoire, que
    #: le I de l'article L. 241-13 nomme l'une et l'autre. Faux du pilier
    #: capitalisé de la proposition, qui n'est ni l'une ni l'autre.
    dans_la_reduction_generale: bool = True

    def taux_employeur_premiere_tranche(self) -> float:
        """Taux patronal sur la première tranche — celui qu'un décret additionne.

        Le décret qui fixe le coefficient maximal de la réduction générale
        additionne des taux de PREMIÈRE TRANCHE : 8,55 % de vieillesse
        plafonnée, 4,72 % d'Agirc-Arrco. C'est cette grandeur qu'un scénario
        déplace, et c'est donc elle qu'on additionne ici.
        """
        return sum(segment.taux for segment in self.employeur
                   if segment.bas_en_plafonds < 1.0)


@dataclass(frozen=True)
class BlocRetraite:
    """Ce qu'un système prélève pour la retraite, étage par étage.

    Les contributions d'équilibre — CEG, CET, APEC —, qui n'acquièrent aucun
    droit et que les fiches de régime ne portent donc pas, viennent du barème
    plutôt que d'ici. Un système qui remplace le financement de la retraite les
    remplace aussi, et c'est ce que dit
    ``remplace_les_contributions_d_equilibre``.
    """

    libelle: str
    composantes: tuple[ComposanteRetraite, ...]
    remplace_les_contributions_d_equilibre: bool = False

    def salarial(self, brut: float, plafond_annuel: float) -> float:
        return sum(_montant(c.salarie, brut, plafond_annuel)
                   for c in self.composantes)

    def patronal(self, brut: float, plafond_annuel: float) -> float:
        return sum(_montant(c.employeur, brut, plafond_annuel)
                   for c in self.composantes)

    def taux_employeur_dans_la_reduction(self, bareme: "BaremePrelevements") -> float:
        """Points de retraite patronale que le coefficient maximal doit compter.

        Les étages de ce bloc qui sont dans le périmètre, plus les contributions
        d'équilibre du barème quand le système les conserve : c'est exactement
        ce que le décret additionne aujourd'hui, et exactement ce qu'il
        additionnerait demain.
        """
        total = sum(c.taux_employeur_premiere_tranche()
                    for c in self.composantes if c.dans_la_reduction_generale)
        if not self.remplace_les_contributions_d_equilibre:
            for poste in bareme.postes:
                if poste.retraite and poste.dans_la_reduction_generale:
                    total += sum(segment.taux for segment in poste.employeur
                                 if segment.bas_en_plafonds < 1.0)
        return total


@dataclass(frozen=True)
class Ligne:
    """Une ligne de la fiche de paie."""

    code: str
    libelle: str
    retraite: bool
    salarie: float
    employeur: float


@dataclass(frozen=True)
class FicheDePaie:
    """Une année de rémunération, décomposée.

    Tous les montants sont ANNUELS et en euros courants de ``annee``.
    """

    annee: int
    cout_du_travail: float
    brut: float
    net: float
    lignes: tuple[Ligne, ...]
    #: Montant de la réduction générale, déjà retranché du coût du travail.
    reduction_generale: float
    fiabilite: Fiabilite
    #: Part de la retraite dans le coefficient maximal de la réduction
    #: générale, posée à la construction : c'est la clé par laquelle la loi
    #: répartit la réduction entre les organismes qui l'encaissent.
    part_retraite_dans_la_reduction: float = 0.0

    @property
    def cotisations_salariales(self) -> float:
        return self.brut - self.net

    @property
    def cotisations_patronales(self) -> float:
        return self.cout_du_travail - self.brut

    @property
    def retraite_salarie(self) -> float:
        return sum(ligne.salarie for ligne in self.lignes if ligne.retraite)

    @property
    def retraite_employeur(self) -> float:
        return sum(ligne.employeur for ligne in self.lignes if ligne.retraite)

    @property
    def retraite_totale(self) -> float:
        """Ce qui est prélevé pour la retraite, les deux parts réunies.

        Nette de la réduction générale : au voisinage du SMIC, l'employeur ne
        verse pas ce que le barème affiche. Sans cette correction, le
        prélèvement retraite d'un salarié au SMIC serait surestimé de seize
        points, et le gain d'une baisse de taux avec lui.
        """
        return max(0.0, self.retraite_salarie + self.retraite_employeur
                   - self._reduction_imputee_a_la_retraite())

    def _reduction_imputee_a_la_retraite(self) -> float:
        """Part de la réduction générale qui porte sur la retraite.

        La loi répartit la réduction entre les organismes « en fonction de la
        part que représente le taux de ces cotisations dans la valeur maximale
        fixée par le décret ». Le modèle applique la même clé.
        """
        return self.reduction_generale * self.part_retraite_dans_la_reduction

    @property
    def taux_retraite(self) -> float:
        """Prélèvement retraite rapporté au coût du travail."""
        return self.retraite_totale / self.cout_du_travail if self.cout_du_travail else 0.0

    @property
    def ecart_brut_net(self) -> float:
        """La part du brut qui n'arrive pas sur le compte du salarié."""
        return self.cotisations_salariales / self.brut if self.brut else 0.0

    @property
    def part_qui_arrive(self) -> float:
        """Ce que le salarié touche, rapporté à ce que son emploi coûte."""
        return self.net / self.cout_du_travail if self.cout_du_travail else 0.0


class ConstructeurFiche:
    """Construit une fiche de paie sous un bloc retraite donné."""

    def __init__(self, bareme: BaremePrelevements) -> None:
        self.bareme = bareme

    # -- pièces --------------------------------------------------------------

    def _lignes(self, bloc: BlocRetraite, brut: float, plafond: float,
                cadre: bool) -> tuple[Ligne, ...]:
        lignes = [
            Ligne(code=composante.code, libelle=composante.libelle, retraite=True,
                  salarie=_montant(composante.salarie, brut, plafond),
                  employeur=_montant(composante.employeur, brut, plafond))
            for composante in bloc.composantes
        ]
        for poste in self.bareme.postes:
            if poste.retraite and bloc.remplace_les_contributions_d_equilibre:
                continue
            if not poste.du(brut, plafond, cadre):
                continue
            assiette = brut
            lignes.append(Ligne(
                code=poste.code, libelle=poste.libelle, retraite=poste.retraite,
                salarie=_montant(poste.salarie, assiette, plafond),
                employeur=_montant(poste.employeur, assiette, plafond),
            ))
        contributions = self._csg_crds(brut, plafond)
        if contributions:
            lignes.append(contributions)
        return tuple(lignes)

    def _csg_crds(self, brut: float, plafond: float) -> Ligne | None:
        taux = self.bareme.csg + self.bareme.crds
        if taux <= 0:
            return None
        abattement = _montant(self.bareme.abattement_frais, brut, plafond)
        return Ligne(code="csg_crds", libelle="CSG et CRDS", retraite=False,
                     salarie=(brut - abattement) * taux, employeur=0.0)

    def _perimetre_reduction(self, bloc: BlocRetraite, brut: float,
                             plafond: float, cadre: bool) -> float:
        """Cotisations patronales que la réduction générale peut effacer."""
        total = sum(
            _montant(composante.employeur, brut, plafond)
            for composante in bloc.composantes
            if composante.dans_la_reduction_generale
        )
        for poste in self.bareme.postes:
            if not poste.dans_la_reduction_generale:
                continue
            if poste.retraite and bloc.remplace_les_contributions_d_equilibre:
                continue
            if not poste.du(brut, plafond, cadre):
                continue
            if poste.taux_dans_la_reduction is not None:
                total += brut * poste.taux_dans_la_reduction
            else:
                total += _montant(poste.employeur, brut, plafond)
        return total

    def _reduction(self, bloc: BlocRetraite, brut: float, plafond: float,
                   smic_annuel: float, cadre: bool) -> float:
        coefficient = self.bareme.reduction_generale.coefficient(
            brut, smic_annuel, bloc.taux_employeur_dans_la_reduction(self.bareme)
        )
        if coefficient <= 0:
            return 0.0
        # Une réduction ne peut pas excéder ce qui est dû : c'est la règle, et
        # c'est aussi ce qui empêche le coût du travail de devenir négatif.
        return min(coefficient * brut,
                   self._perimetre_reduction(bloc, brut, plafond, cadre))

    # -- la fiche ------------------------------------------------------------

    def fiche(self, annee: int, brut: float, plafond_annuel: float,
              smic_annuel: float, bloc: BlocRetraite,
              cadre: bool = False) -> FicheDePaie:
        """La fiche de paie d'une année, à salaire brut donné."""
        lignes = self._lignes(bloc, brut, plafond_annuel, cadre)
        reduction = self._reduction(bloc, brut, plafond_annuel, smic_annuel, cadre)
        salariales = sum(ligne.salarie for ligne in lignes)
        patronales = sum(ligne.employeur for ligne in lignes)
        taux_retraite = bloc.taux_employeur_dans_la_reduction(self.bareme)
        maximal = self.bareme.reduction_generale.coefficient_maximal_avec(
            taux_retraite)
        part_retraite = taux_retraite / maximal if maximal > 0 else 0.0
        return FicheDePaie(
            annee=annee,
            cout_du_travail=brut + patronales - reduction,
            brut=brut,
            net=brut - salariales,
            lignes=lignes,
            reduction_generale=reduction,
            fiabilite=self.bareme.fiabilite,
            part_retraite_dans_la_reduction=min(1.0, part_retraite),
        )

    def brut_a_cout_donne(self, cout: float, plafond_annuel: float,
                          smic_annuel: float, bloc: BlocRetraite,
                          cadre: bool = False) -> float:
        """Le salaire brut qui épuise un coût du travail donné.

        C'est l'incidence intégrale : l'employeur a budgété ``cout`` pour ce
        poste, et ce qu'il ne verse plus en cotisations, il le verse en salaire.
        Le coût du travail croît strictement avec le brut — chaque taux est
        positif et la réduction générale décroît —, si bien qu'une dichotomie
        converge sans hypothèse supplémentaire.
        """
        if cout <= 0:
            return 0.0
        bas, haut = 0.0, cout
        for _ in range(80):
            milieu = (bas + haut) / 2
            fiche = self.fiche(0, milieu, plafond_annuel, smic_annuel, bloc, cadre)
            if fiche.cout_du_travail < cout:
                bas = milieu
            else:
                haut = milieu
        return (bas + haut) / 2


# -- les blocs retraite des scénarios ---------------------------------------
#
# Ils sont construits ICI, mais à partir des fiches de régime : la fiche de paie
# prélève exactement ce que le compte notionnel encaisse. Écrire les taux une
# seconde fois aurait garanti qu'ils divergent un jour.


def bloc_droit_en_vigueur(catalogue, affiliations, statut: str,
                          annee: int) -> BlocRetraite:
    """Ce que le droit en vigueur prélève pour la retraite, par régime.

    Un étage par régime : la vieillesse de base et sa part déplafonnée d'un
    côté, la complémentaire de l'autre, chacun avec ses bornes d'assiette et
    son partage salarié/employeur, lus dans la fiche.

    Ce bloc vaut pour les systèmes 1, 2 et 3 du site : ils ne changent PAS ce
    qui est prélevé, seulement ce qui est porté au compte. C'est la raison pour
    laquelle la fiche de paie de ces trois systèmes est la même, au centime.
    """
    composantes: list[ComposanteRetraite] = []
    for code in affiliations.regimes(statut, annee):
        if code not in catalogue:
            continue
        regime = catalogue[code]
        if regime.hors_repartition:
            continue
        salarie: list[Segment] = []
        employeur: list[Segment] = []
        for periode in regime.periodes_actives(annee):
            basse, haute = periode.bornes_assiette_en_pass()
            part = periode.part_salariale
            taux = periode.taux_cotisation_retraite
            if taux:
                salarie.append(Segment(basse, haute, taux * part))
                employeur.append(Segment(basse, haute, taux * (1.0 - part)))
            # La part déplafonnée porte sur la totalité du salaire, par-dessus
            # la précédente : c'est un segment de plus, non une tranche.
            taux_deplafonne = periode.taux_cotisation_deplafonnee
            if taux_deplafonne:
                part_deplafonnee = periode.part_salariale_deplafonnee
                salarie.append(
                    Segment(0.0, None, taux_deplafonne * part_deplafonnee))
                employeur.append(
                    Segment(0.0, None, taux_deplafonne * (1.0 - part_deplafonnee)))
        if not salarie and not employeur:
            continue
        composantes.append(ComposanteRetraite(
            code=code, libelle=regime.nom, salarie=tuple(salarie),
            employeur=tuple(employeur), dans_la_reduction_generale=True,
        ))
    return BlocRetraite(
        libelle="Retraite (droit en vigueur)",
        composantes=tuple(composantes),
        remplace_les_contributions_d_equilibre=False,
    )


def bloc_taux_unique(taux_repartition: float, taux_capitalisation: float = 0.0,
                     part_salariale: float = 0.5,
                     libelle_repartition: str = "Retraite, compte notionnel",
                     libelle_capitalisation: str = "Retraite, part capitalisée",
                     ) -> BlocRetraite:
    """Le bloc de la proposition : un taux unique, au premier euro, sans plafond.

    ``part_salariale`` partage chaque taux entre l'assuré et son employeur. La
    proposition ne le dit pas ; le dépôt partage moitié-moitié, et le docstring
    du module dit pourquoi ce choix, qu'on croirait sans effet, en a un : la
    CSG est assise sur le brut, et la réduction générale n'efface que du
    patronal.

    Le pilier capitalisé est un étage à part, et hors du périmètre de la
    réduction générale : il n'est ni une assurance sociale, ni un régime
    complémentaire légalement obligatoire au sens de l'article L. 921-4.
    """
    composantes = [ComposanteRetraite(
        code="regime_unifie", libelle=libelle_repartition,
        salarie=(Segment(0.0, None, taux_repartition * part_salariale),),
        employeur=(Segment(0.0, None, taux_repartition * (1.0 - part_salariale)),),
        dans_la_reduction_generale=True,
    )]
    if taux_capitalisation:
        composantes.append(ComposanteRetraite(
            code="capitalisation", libelle=libelle_capitalisation,
            salarie=(Segment(0.0, None, taux_capitalisation * part_salariale),),
            employeur=(Segment(0.0, None,
                               taux_capitalisation * (1.0 - part_salariale)),),
            dans_la_reduction_generale=False,
        ))
    return BlocRetraite(
        libelle="Retraite (proposition)",
        composantes=tuple(composantes),
        remplace_les_contributions_d_equilibre=True,
    )


def fiche_de_paie_possible(affiliations, statut: str) -> bool:
    """La fiche de paie sait-elle décrire ce statut ?

    Les taux hors retraite de ce module sont ceux du régime général. Les
    opposer au traitement d'un fonctionnaire ou au revenu d'un artisan
    produirait un net faux sans que rien ne le dise.
    """
    try:
        return affiliations.famille(statut) in FAMILLES_COUVERTES
    except KeyError:
        return False


def smic_annuel(macro, annee: int) -> float:
    """SMIC annuel d'un temps plein, en euros courants de l'année."""
    return macro.smic_horaire(annee) * HEURES_ANNUELLES_TEMPS_PLEIN


# -- ce qu'un actif touche, système par système ------------------------------


@dataclass(frozen=True)
class AnneeComparee:
    """Une année d'activité, sous le droit en vigueur et sous la proposition."""

    annee: int
    droit_en_vigueur: FicheDePaie
    proposition: FicheDePaie
    #: Coefficient de passage aux euros constants de l'année de référence.
    coefficient_euros_constants: float = 1.0

    @property
    def gain_net(self) -> float:
        """Ce que la proposition ajoute au salaire net, en euros de l'année."""
        return self.proposition.net - self.droit_en_vigueur.net

    @property
    def gain_net_constant(self) -> float:
        return self.gain_net * self.coefficient_euros_constants

    @property
    def epargne_a_votre_nom(self) -> float:
        """Le pilier capitalisé : prélevé sur le net, mais acquis à l'assuré.

        Il n'est pas une cotisation perdue : il alimente un compte transmissible
        aux héritiers tant qu'il n'est pas liquidé. Le site l'affiche à part du
        gain, parce que le confondre avec lui serait compter deux fois, et le
        passer sous silence serait compter une fois de trop.
        """
        return sum(ligne.salarie + ligne.employeur
                   for ligne in self.proposition.lignes
                   if ligne.code == "capitalisation")

    @property
    def brut_sous_le_smic(self) -> bool:
        """L'incidence intégrale ferait-elle passer le brut sous le SMIC ?

        Le cas se produit quand la proposition prélève PLUS que le droit en
        vigueur à coût du travail donné. Il est alors impossible en droit : le
        salaire minimum est un plancher. C'est un avertissement, et le site le
        porte.
        """
        return self.proposition.brut < self.droit_en_vigueur.brut and (
            self.proposition.brut < self._smic)

    _smic: float = 0.0


@dataclass(frozen=True)
class RemunerationActif:
    """Ce qu'un actif touche entre la bascule et son départ, dans les deux systèmes.

    Vide — donc absente du site — pour qui a déjà liquidé, et pour tout statut
    que la fiche de paie ne sait pas décrire.
    """

    statut: str
    libelle_statut: str
    cadre: bool
    annees: tuple[AnneeComparee, ...]
    #: Millésime des taux hors retraite. Ils sont appliqués tels quels aux
    #: années à venir : le modèle ne prétend pas prévoir la prochaine LFSS.
    millesime_bareme: int
    fiabilite: Fiabilite

    @property
    def reference(self) -> AnneeComparee:
        """La première année pleine sous le nouveau système : celle qu'on affiche."""
        return self.annees[0]

    @property
    def gain_net_mensuel(self) -> float:
        return self.reference.gain_net / 12.0

    @property
    def gain_net_cumule(self) -> float:
        """Somme des gains jusqu'au départ, en euros constants de la référence."""
        return sum(annee.gain_net_constant for annee in self.annees)

    @property
    def epargne_cumulee(self) -> float:
        """Ce que le pilier capitalisé aura prélevé, en euros constants."""
        return sum(annee.epargne_a_votre_nom * annee.coefficient_euros_constants
                   for annee in self.annees)

    @property
    def bute_sur_le_smic(self) -> bool:
        return any(annee.brut_sous_le_smic for annee in self.annees)


def remuneration_de_la_carriere(carriere, macro, catalogue, affiliations,
                                parametres) -> RemunerationActif | None:
    """Les fiches de paie d'une carrière, de la bascule au départ.

    ``None`` quand il n'y a rien à montrer : aucune année d'activité après la
    bascule — la personne a déjà liquidé, et sa pension ne dépend plus d'aucune
    cotisation —, ou un statut que ce module ne sait pas décrire.
    """
    debut = max(parametres.annee_bascule, carriere.premiere_annee)
    annees_actives = [
        annee for annee in range(debut, carriere.annee_liquidation + 1)
        if (ligne := carriere.ligne(annee)) is not None and ligne.cotise
        and ligne.revenu > 0
    ]
    if not annees_actives:
        return None

    statut = carriere.ligne(annees_actives[0]).affiliation
    if not fiche_de_paie_possible(affiliations, statut):
        return None

    bareme = charger_prelevements(parametres.racine_donnees)
    constructeur = ConstructeurFiche(bareme)
    # « Cadre » n'est pas une famille d'affiliation : c'est la seule chose qui
    # sépare deux statuts du privé pour la cotisation APEC, qui vaut 0,024 %.
    cadre = "cadre" in statut and "non_cadre" not in statut
    propose = bloc_taux_unique(
        parametres.taux_cotisation_liberal,
        (parametres.taux_capitalisation_obligatoire
         if parametres.capitalisation_obligatoire else 0.0),
        part_salariale=parametres.part_salariale_taux_unique,
    )

    comparees: list[AnneeComparee] = []
    for annee in annees_actives:
        ligne = carriere.ligne(annee)
        part = carriere.part_retenue(annee)
        if part <= 0:
            continue
        # Une année incomplète ne se compare pas à une année pleine : on
        # annualise le revenu, et le plafond comme le SMIC restent annuels.
        brut = ligne.revenu / part if part < 1.0 else ligne.revenu
        plafond = macro.plafond_securite_sociale(annee)
        smic = smic_annuel(macro, annee)
        actuel_bloc = bloc_droit_en_vigueur(catalogue, affiliations, statut, annee)
        fiche_actuelle = constructeur.fiche(
            annee, brut, plafond, smic, actuel_bloc, cadre)
        brut_propose = constructeur.brut_a_cout_donne(
            fiche_actuelle.cout_du_travail, plafond, smic, propose, cadre)
        fiche_proposee = constructeur.fiche(
            annee, brut_propose, plafond, smic, propose, cadre)
        comparees.append(AnneeComparee(
            annee=annee,
            droit_en_vigueur=fiche_actuelle,
            proposition=fiche_proposee,
            coefficient_euros_constants=macro.coefficient_prix(
                annee, parametres.annee_euros_constants),
            _smic=smic,
        ))

    if not comparees:
        return None
    return RemunerationActif(
        statut=statut,
        libelle_statut=affiliations.libelle(statut),
        cadre=cadre,
        annees=tuple(comparees),
        millesime_bareme=bareme.annee,
        fiabilite=bareme.fiabilite,
    )
