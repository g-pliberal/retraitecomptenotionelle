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

Le module retient donc, **quand l'employeur est connu**, l'incidence intégrale
au salarié, et il la calcule au lieu de la postuler : le COÛT DU TRAVAIL est
tenu fixe — c'est ce que l'employeur a budgété pour ce poste, et aucune réforme
des retraites ne le change —, et le salaire brut est celui qui l'épuise sous les
nouveaux taux. Le net s'en déduit. C'est ce que veut dire « réduire l'écart
entre le net et le brut » : la baisse du prélèvement remonte dans le brut, puis
dans le net.

C'est une HYPOTHÈSE, la plus favorable à une baisse de cotisation, et le site
l'écrit là où il affiche le chiffre. La lecture prudente — seule la part
salariale bouge, l'employeur garde son économie — donne à peu près la moitié
du gain ; c'est :data:`Incidence.ASSIETTE`, et ce n'est pas qu'une variante de
confort : c'est la SEULE lecture disponible pour les statuts dont l'employeur
ne verse pas un prix du travail. Voir « quatre profils » plus bas.

LE PARTAGE DES 18 %, ET POURQUOI IL N'EST PAS ANODIN
-----------------------------------------------------
La proposition fixe un taux unique de 18 %, « salariale et patronale
additionnées », et ne dit pas qui porte quoi. **Le programme a tranché le
20 septembre 2026 : la part PATRONALE ne bouge pas, et toute la baisse va au
salarié.** Un salarié du privé verse aujourd'hui 11,31 points sur sa fiche et
son employeur 16,67, soit 27,98 en tout ; la proposition en prélève 23, dont
l'employeur garde les mêmes 16,67 et l'assuré ne porte plus que **6,33**. Les
18 % et les 5 % capitalisés suivent la même clé : 4,95 + 1,38 pour l'assuré,
13,05 + 3,62 pour l'employeur.

Le partage a été MESURÉ avant d'être choisi — ``scripts/partage_taux_unique.py``
met les quatre partages possibles en regard, et l'action 56 de la feuille de
route en tire la décision. Ce qui l'emporte tient en trois traits. La baisse
arrive **le lendemain** de la réforme, en entier, sans rien supposer de ce
qu'un employeur rendra : +182 € par mois au salaire moyen, +91 € au SMIC. Elle
ne **fuit pas** : le brut ne bouge pas, donc ni la CSG ni les autres branches
ne grossissent avec lui, là où une baisse de la part patronale leur en laisse
le quart en remontant. Et le **coût du travail bouge peu** : au SMIC, il monte
de 66 € par mois au jour 1, parce que la part patronale du pilier capitalisé
est hors du périmètre de la réduction générale et que l'employeur la verse
pour de bon ; la hausse diminue à mesure que la réduction s'éteint — 48 € à
1,2 SMIC, 30 € à 1,5, 12 € à 2 — et devient une baisse à 3 SMIC. Ce
paragraphe disait « à tous les niveaux sauf un » jusqu'au 23 septembre 2026.

Ce qu'il ne fait pas, et qu'il faut dire : il ne fait pas monter le salaire
BRUT, donc ni le crédit au compte ni les droits assis sur le brut. Le partage
inverse — toute la baisse à l'employeur — le ferait monter de 2,9 %, au prix
d'une hypothèse d'incidence, de plusieurs années d'attente, de rien du tout au
SMIC, et de 90 € de net par mois de moins une fois le long terme atteint.

Le dépôt a partagé **moitié-moitié** jusqu'au 20 septembre 2026, faute d'avoir
mesuré : ce partage faisait MONTER la part salariale, de 11,31 à 11,50 points,
et la fiche de paie du lendemain baissait de 7 € par mois au salaire moyen.

Les cinq points de capitalisation VOLONTAIRE ne sont pas sur la fiche de paie
du tout. Personne ne les impose, donc personne ne les prélève : la fiche de la
proposition s'arrête aux 23 points imposés, et son net est le net PLEIN. Ce que
l'assuré place ensuite sur un compte à son nom est un PLACEMENT pris sur ce
net, décidé seul, porté seul — et le coût du travail ne bouge pas quand il le
fait. Le modèle le chiffre à côté (:attr:`AnneeComparee.epargne_volontaire`),
sur la même assiette que le pilier, parce que la pension du scénario 6 le
compte : c'est la convention de comparaison à 28 % cotisés, et le site doit
pouvoir écrire ce qu'elle coûte sans la faire passer pour une retenue.

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
SMIC, faire porter les 23 points imposés entièrement à l'employeur plutôt qu'au
salarié vaut plusieurs milliers d'euros de net par an — mais au long terme
seulement, et amputés de ce que la CSG et les autres branches reprennent en
chemin. ``part_salariale_taux_unique`` rend le partage réglable, et deux tests
fixent les deux mécanismes.

C'est, au passage, un résultat sur le système actuel plus que sur la
proposition : notre droit fait dépendre le salaire net de la FRONTIÈRE entre
part salariale et part patronale, alors que cette frontière ne change rien à
ce que le travail coûte ni à ce qu'il rapporte au système.

Sous :data:`Incidence.ASSIETTE`, le partage cesse d'être neutre pour une raison
plus simple encore, et plus brutale : seule la part salariale est comptée, donc
déplacer un point vers l'employeur le fait disparaître de la fiche.

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

À QUI CE MODULE S'APPLIQUE : QUATRE PROFILS
--------------------------------------------
Il n'en a longtemps décrit qu'un — le salarié du privé —, et le site n'affichait
rien aux autres statuts. Il en décrit quatre, et le découpage n'est PAS celui
des familles de statut : c'est celui de ce que l'on sait de l'employeur.

``salarie_prive``
    L'employeur verse les cotisations du régime général et de l'Agirc-Arrco, que
    la fiche du régime porte en totalité. La famille ``prive``, et les statuts de
    la famille ``special`` que la fermeture des régimes spéciaux a versés au
    régime général — l'agent SNCF, l'agent RATP, le mineur, le clerc de notaire,
    le personnel navigant.
``salarie_ircantec``
    Même chose, mais la complémentaire est l'Ircantec : la CEG, la CET et
    l'APEC, qui sont des contributions de l'Agirc-Arrco, ne sont pas dues. C'est
    l'agent non titulaire de la fonction publique.
``agent_seul``
    La fiche du régime ne porte QUE la retenue de l'agent, parce que ce que
    verse son employeur est un taux d'ÉQUILIBRE et non un prix du travail. Le
    fonctionnaire titulaire, le militaire, le marin, l'artiste de l'Opéra.
``independant``
    Pas d'employeur du tout : la cotisation est intégralement personnelle, et
    l'assiette n'est pas un salaire mais un revenu professionnel.

LA DÉCISION QUI N'EST PAS MÉCANIQUE : LE COÛT DU TRAVAIL D'UN FONCTIONNAIRE
----------------------------------------------------------------------------
La contribution de l'employeur public est un TAUX D'ÉQUILIBRE — 82,28 % du
traitement en 2026 pour l'État, 126,07 % de la solde de ses militaires,
37,65 % pour la CNRACL, voir ``legislation/contribution_employeur_public.csv``
et ``legislation/contribution_employeur_militaires.csv``. Il est fixé pour que le
compte d'affectation spéciale « Pensions » tombe juste, c'est-à-dire pour payer
les pensions d'aujourd'hui, et non parce que l'agent acquerrait 82 % de son
traitement en droits nouveaux.

L'appeler « coût du travail » et poser dessus l'incidence intégrale donnerait un
gain absurde : la baisse de 82,28 % à 11,50 % se lirait comme une augmentation
de salaire de soixante-dix points, alors que la dette de pensions que cette
contribution finance reste à payer. Tenir le traitement FIXE, à l'inverse, ne
rendrait rien du tout, comme si le taux d'équilibre n'avait jamais rien coûté à
l'employeur public : or c'est de l'argent public que la proposition libère.

Le module a longtemps retenu la seconde branche. Il retient depuis le
20 septembre 2026 la troisième, qui n'est pas un compromis mais une DÉCISION :
**la moitié de ce que l'employeur cesse de verser remonte dans le traitement,
l'autre moitié paie la dette de pensions déjà promises.** C'est
:data:`Incidence.PARTAGEE`, et ``Parametres.part_rendue_aux_salaires`` porte le
partage — à zéro, on retrouve exactement l'ancienne convention, ce qu'un test
vérifie. La ligne « coût du travail » reste absente : un taux d'équilibre n'est
toujours pas un prix du travail, et l'afficher comme tel dirait le contraire de
ce que ce partage suppose.

Le traitement d'un fonctionnaire d'État monte ainsi d'un tiers. C'est beaucoup,
et deux réserves l'accompagnent dans ``docs/limites.md`` : la pension, elle,
reste calculée sur le revenu de la carrière et non sur ce traitement-là ; et le
partage est un état d'arrivée, pas un calendrier.

``independant`` tient l'assiette fixe, et ce n'est pas une hypothèse : il n'y a
pas d'employeur, donc rien à répercuter.

``profil_de_la_fiche`` choisit le profil ; ``fiche_de_paie_possible`` dit si le
statut est couvert ; le site n'affiche rien quand il ne l'est pas, et dit
pourquoi.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path

from .donnees.chargement import Fiabilite, charger_yaml
from .donnees.regimes import ContributionsEmployeurPubliques
from .restitution import points_csg_rendus

#: Heures d'un temps plein sur une année : 35 heures sur 52 semaines. Sert à
#: convertir le SMIC horaire — la seule forme que le dépôt publie — en SMIC
#: annuel, qui est la référence de la réduction générale.
HEURES_ANNUELLES_TEMPS_PLEIN = 1820.0

#: Familles de statuts auxquelles la fiche de paie s'applique. Voir le
#: docstring du module : quatre profils, et le découpage n'est pas celui-ci.
#: Restent dehors ``agricole`` — dont les taux hors retraite sont ceux de la
#: MSA, qui ne sont pas ceux du régime général —, ``outre_mer``, dont chaque
#: collectivité a sa propre caisse, ``elus``, dont l'indemnité n'est pas un
#: salaire, et ``hors_emploi``, qui ne cotise pas.
FAMILLES_COUVERTES = frozenset({"prive", "public", "special", "independant"})


class Incidence(str, Enum):
    """Ce que le modèle tient FIXE quand il compare deux systèmes.

    * ``COUT_DU_TRAVAIL`` — l'employeur a budgété un coût pour ce poste, et ce
      qu'il ne verse plus en cotisations, il le verse en salaire. Le brut est
      recalculé par dichotomie. C'est l'incidence intégrale, la plus favorable
      à une baisse de cotisation.
    * ``ASSIETTE`` — le brut, le traitement ou le revenu professionnel ne bouge
      pas, et seule la part de l'assuré change. Lecture prudente, et la seule
      disponible quand il n'y a pas d'employeur.
    * ``PARTAGEE`` — la MOITIÉ de ce que l'employeur ne verse plus remonte dans
      l'assiette, l'autre moitié paie la dette qu'il finançait. C'est la
      décision du 20 septembre 2026 pour la contribution d'équilibre de l'État,
      et la seule des trois qui ne soit ni une hypothèse d'économiste ni un
      refus de trancher : elle dit à quoi sert l'argent.

      L'incidence intégrale prêterait au fonctionnaire les soixante-dix points
      que l'État cesse de verser, comme s'ils avaient été son salaire différé ;
      or ils payaient les pensions d'aujourd'hui, et ces pensions restent à
      payer. L'incidence sur l'assiette ne lui en rendrait aucun, comme si le
      taux d'équilibre n'avait jamais rien coûté à son employeur ; or c'est de
      l'argent public que la proposition libère. Le partage tranche entre les
      deux au lieu de choisir un bord.
    """

    COUT_DU_TRAVAIL = "cout_du_travail"
    ASSIETTE = "assiette"
    PARTAGEE = "partagee"


@dataclass(frozen=True)
class Segment:
    """Un taux, appliqué à la part du revenu comprise entre deux bornes.

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
class BaremeProgressif:
    """Un taux qui dépend du NIVEAU de l'assiette, et porte sur sa totalité.

    C'est la forme qu'a prise la loi pour les indépendants, et elle n'est pas
    celle d'un barème par tranches : « le taux de base de la cotisation
    d'assurance maladie et maternité des travailleurs indépendants fait l'objet
    d'une réduction lorsque le montant annuel de leur assiette de cotisations
    est inférieur à trois fois la valeur annuelle du plafond » (D. 621-2). Le
    taux réduit s'applique alors à TOUT le revenu, et non à la seule fraction
    comprise entre deux paliers — une modélisation par tranches marginales
    donnerait un montant tout autre.

    Entre deux paliers, le taux est interpolé linéairement, exactement comme les
    formules de l'article l'écrivent. En deçà du premier palier, c'est le taux
    de ce palier. Au-delà de ``jusqu_en_plafonds``, ce barème ne s'applique plus
    et les tranches du poste reprennent la main : la continuité au raccord est
    une propriété du droit, et un test l'exige.
    """

    jusqu_en_plafonds: float
    #: Couples (borne en plafonds, taux atteint à cette borne), triés.
    paliers: tuple[tuple[float, float], ...]

    def taux(self, assiette_en_plafonds: float) -> float:
        """Le taux applicable à la totalité de l'assiette, à ce niveau."""
        if not self.paliers:
            return 0.0
        premier_seuil, premier_taux = self.paliers[0]
        if assiette_en_plafonds <= premier_seuil:
            return premier_taux
        precedent_seuil, precedent_taux = self.paliers[0]
        for seuil, taux in self.paliers[1:]:
            if assiette_en_plafonds <= seuil:
                largeur = seuil - precedent_seuil
                if largeur <= 0:
                    return taux
                part = (assiette_en_plafonds - precedent_seuil) / largeur
                return precedent_taux + part * (taux - precedent_taux)
            precedent_seuil, precedent_taux = seuil, taux
        return precedent_taux


def _progressif(contenu) -> BaremeProgressif | None:
    if not contenu:
        return None
    paliers = tuple(
        (float(palier["en_plafonds"]), float(palier["taux"]))
        for palier in sorted(contenu["paliers"],
                             key=lambda p: float(p["en_plafonds"]))
    )
    return BaremeProgressif(
        jusqu_en_plafonds=float(contenu["jusqu_en_plafonds"]),
        paliers=paliers,
    )


@dataclass(frozen=True)
class Poste:
    """Un prélèvement, avec ses deux barèmes."""

    code: str
    libelle: str
    #: Finance-t-il la retraite ? Vrai pour la CEG et la CET, que les fiches
    #: de régime ne portent pas parce qu'elles n'acquièrent aucun droit. Faux
    #: pour l'APEC, que l'Agirc-Arrco recouvre avec elles mais qui finance le
    #: service de l'emploi des cadres : un scénario qui remplace la retraite
    #: la laisse en place.
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
    #: Réduction du taux SALARIAL en deçà d'un certain revenu, applicable à la
    #: totalité de l'assiette. Propre aux indépendants ; ``None`` ailleurs.
    progressif: BaremeProgressif | None = None
    note: str = ""

    def du(self, brut: float, plafond_annuel: float, cadre: bool) -> bool:
        if self.cadres_seulement and not cadre:
            return False
        if self.due_au_dela_de_un_plafond and brut <= plafond_annuel:
            return False
        return True

    def montant_salarie(self, assiette: float, plafond_annuel: float) -> float:
        """Ce que l'assuré supporte, barème progressif compris."""
        if (self.progressif is not None
                and assiette < self.progressif.jusqu_en_plafonds * plafond_annuel):
            return self.progressif.taux(assiette / plafond_annuel) * assiette
        return _montant(self.salarie, assiette, plafond_annuel)


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
class ProfilRemuneration:
    """Tout ce que le droit prélève sur un revenu, hors retraite acquisitive.

    Un profil par situation d'employeur, et non par famille de statut : voir le
    docstring du module. C'est l'objet que ``ConstructeurFiche`` consomme.
    """

    code: str
    libelle: str
    #: Comment la page nomme les deux montants qu'elle affiche à coup sûr.
    libelle_assiette: str
    libelle_net: str
    #: La ligne « coût du travail » a-t-elle un sens pour ce profil ? Fausse dès
    #: que ce que verse l'employeur est un taux d'équilibre, ou qu'il n'y a pas
    #: d'employeur.
    cout_du_travail: bool
    incidence: Incidence
    annee: int
    postes: tuple[Poste, ...]
    csg_deductible: float
    csg_imposable: float
    crds: float
    abattement_frais: tuple[Segment, ...]
    #: ``None`` quand l'employeur n'y a pas droit — ou qu'il n'y en a pas.
    reduction_generale: ReductionGenerale | None
    fiabilite: Fiabilite

    @property
    def csg(self) -> float:
        return self.csg_deductible + self.csg_imposable

    def taux_retraite_du_droit_en_vigueur(self) -> float:
        """Ce que le coefficient maximal compte aujourd'hui pour la retraite."""
        if self.reduction_generale is None:
            return 0.0
        return self.reduction_generale.taux_retraite_inclus


@dataclass(frozen=True)
class TrancheCsgPension:
    """Un des quatre cas de l'article L. 136-8, pour situer le lecteur."""

    libelle: str
    taux: float
    revenu_fiscal_maximum: float | None


@dataclass(frozen=True)
class PrelevementsPension:
    """Ce qu'on paie une fois retraité — et non plus en travaillant.

    Une pension n'est pas un salaire : aucune cotisation sociale, puisqu'on
    n'acquiert plus de droits ; aucun abattement pour frais professionnels ; et
    un taux de CSG propre, que la loi fait dépendre du revenu fiscal de
    référence du foyer.

    **Le dépôt retient le TAUX PLEIN pour tout le monde**, faute de connaître ce
    revenu — le simulateur ne demande ni la composition du foyer, ni les autres
    ressources. La convention surestime donc le prélèvement sur les petites
    pensions, qui seraient exonérées : le fichier de données dit de combien, et
    ``docs/limites.md`` porte la réserve. ``bareme_csg`` garde les quatre cas
    pour que la page puisse les montrer.
    """

    csg_taux_plein: float
    crds: float
    casa: float
    bareme_csg: tuple[TrancheCsgPension, ...]
    #: Les points de CSG que l'article L. 131-8, 3° e reverse à la branche
    #: vieillesse : 2,94 des 8,30 prélevés sur une pension. Ne sert à aucun
    #: calcul de pension — une pension nette ne dépend pas de qui encaisse —,
    #: mais au COMPTE : cette part de la recette est prélevée sur la dépense.
    csg_affectee_vieillesse: float = 0.0

    @property
    def taux_total(self) -> float:
        """Ce qui sépare une pension brute de sa pension nette : 9,1 %."""
        return self.csg_taux_plein + self.crds + self.casa

    def net(self, brut: float) -> float:
        return brut * (1.0 - self.taux_total)

    def brut(self, net: float) -> float:
        """L'inverse : quelle pension brute laisse ce net.

        Sert à la saisie, où l'on peut taper un montant net.
        """
        reste = 1.0 - self.taux_total
        return net / reste if reste > 0 else net


@dataclass(frozen=True)
class Prelevements:
    """Les quatre profils, tels que le fichier les écrit, et les pensions."""

    annee: int
    profils: dict[str, ProfilRemuneration]
    pensions: PrelevementsPension
    fiabilite: Fiabilite

    def profil(self, code: str) -> ProfilRemuneration:
        return self.profils[code]


def _poste(contenu) -> Poste:
    return Poste(
        code=contenu["code"],
        libelle=contenu["libelle"],
        retraite=bool(contenu.get("retraite", False)),
        dans_la_reduction_generale=bool(
            contenu.get("dans_la_reduction_generale", False)),
        salarie=_tranches(contenu.get("salarie")),
        employeur=_tranches(contenu.get("employeur")),
        taux_dans_la_reduction=(
            None if contenu.get("taux_dans_la_reduction") is None
            else float(contenu["taux_dans_la_reduction"])),
        cadres_seulement=bool(contenu.get("cadres_seulement", False)),
        due_au_dela_de_un_plafond=bool(
            contenu.get("due_au_dela_de_un_plafond", False)),
        progressif=_progressif(contenu.get("progressif")),
        note=contenu.get("note", ""),
    )


def _reduction_generale(contenu) -> ReductionGenerale | None:
    if not contenu:
        return None
    return ReductionGenerale(
        libelle=contenu["libelle"],
        plafond_en_smic=float(contenu["plafond_en_smic"]),
        puissance=float(contenu["puissance"]),
        taux_minimum=float(contenu["taux_minimum"]),
        coefficient_maximal=float(contenu["coefficient_maximal"]),
        composantes={code: float(valeur)
                     for code, valeur in contenu["composantes"].items()},
        composantes_retraite=tuple(contenu["composantes_retraite"]),
    )


@lru_cache(maxsize=4)
def _charger(chemin: str, signature: tuple) -> Prelevements:
    contenu = charger_yaml(Path(chemin))
    annee = int(contenu["annee"])
    fiabilite = Fiabilite.depuis_texte(contenu.get("fiabilite", "haute"))
    profils: dict[str, ProfilRemuneration] = {}
    for code, fiche in contenu["profils"].items():
        contributions = fiche["contributions_sociales"]
        profils[code] = ProfilRemuneration(
            code=code,
            libelle=fiche["libelle"],
            libelle_assiette=fiche["libelle_assiette"],
            libelle_net=fiche["libelle_net"],
            cout_du_travail=bool(fiche["cout_du_travail"]),
            incidence=Incidence(fiche["incidence"]),
            annee=annee,
            postes=tuple(_poste(poste) for poste in fiche.get("postes") or []),
            csg_deductible=float(contributions["csg_deductible"]),
            csg_imposable=float(contributions["csg_imposable"]),
            crds=float(contributions["crds"]),
            abattement_frais=_tranches(
                contributions.get("abattement_frais_professionnels")),
            reduction_generale=_reduction_generale(
                fiche.get("reduction_generale")),
            fiabilite=fiabilite,
        )
    pensions = contenu["pensions"]
    return Prelevements(
        annee=annee,
        profils=profils,
        pensions=PrelevementsPension(
            csg_taux_plein=float(pensions["csg_taux_plein"]),
            crds=float(pensions["crds"]),
            casa=float(pensions["casa"]),
            csg_affectee_vieillesse=float(
                pensions.get("csg_affectee_vieillesse", 0.0)),
            bareme_csg=tuple(
                TrancheCsgPension(
                    libelle=tranche["libelle"],
                    taux=float(tranche["taux"]),
                    revenu_fiscal_maximum=(
                        None if tranche.get("revenu_fiscal_maximum") is None
                        else float(tranche["revenu_fiscal_maximum"])),
                )
                for tranche in pensions["bareme_csg"]
            ),
        ),
        fiabilite=fiabilite,
    )


def charger_prelevements(racine_donnees: Path) -> Prelevements:
    """Les profils de prélèvements hors retraite, mémorisés sur la signature.

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

    Les contributions d'équilibre — CEG, CET —, qui n'acquièrent aucun
    droit et que les fiches de régime ne portent donc pas, viennent du profil
    plutôt que d'ici. Un système qui remplace le financement de la retraite les
    remplace aussi, et c'est ce que dit
    ``remplace_les_contributions_d_equilibre``.
    """

    libelle: str
    composantes: tuple[ComposanteRetraite, ...]
    remplace_les_contributions_d_equilibre: bool = False
    #: Points de CSG d'activité que le système RETIRE de la fiche, en fraction
    #: du brut abattu — 0,0112 pour 1,12 point. Nul pour le droit en vigueur.
    #: C'est la moitié des impôts affectés que la proposition rend aux
    #: salaires, une fois la taxe sur les salaires et le forfait social
    #: supprimés : voir ``restitution.py``, qui la calcule, et qui dit
    #: pourquoi cette CSG-là ne finançait aucune retraite.
    csg_rendue: float = 0.0
    #: Part de la contribution d'équilibre d'un employeur public que le système
    #: rend à l'assiette. Ne sert qu'à ``Incidence.PARTAGEE``.
    part_rendue_aux_salaires: float = 0.0
    #: Taux d'équilibre que l'employeur public verse AUJOURD'HUI, en fraction
    #: du traitement. Ne sert qu'à ``Incidence.PARTAGEE``.
    contribution_equilibre_actuelle: float = 0.0

    def taux_employeur(self, brut: float, plafond_annuel: float) -> float:
        """Ce que l'employeur verse pour la retraite, rapporté au brut."""
        return self.patronal(brut, plafond_annuel) / brut if brut else 0.0

    def salarial(self, brut: float, plafond_annuel: float) -> float:
        return sum(_montant(c.salarie, brut, plafond_annuel)
                   for c in self.composantes)

    def patronal(self, brut: float, plafond_annuel: float) -> float:
        return sum(_montant(c.employeur, brut, plafond_annuel)
                   for c in self.composantes)

    def taux_employeur_dans_la_reduction(self, profil: ProfilRemuneration) -> float:
        """Points de retraite patronale que le coefficient maximal doit compter.

        Les étages de ce bloc qui sont dans le périmètre, plus les contributions
        d'équilibre du profil quand le système les conserve : c'est exactement
        ce que le décret additionne aujourd'hui, et exactement ce qu'il
        additionnerait demain.
        """
        total = sum(c.taux_employeur_premiere_tranche()
                    for c in self.composantes if c.dans_la_reduction_generale)
        if not self.remplace_les_contributions_d_equilibre:
            for poste in profil.postes:
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

    Tous les montants sont ANNUELS et en euros courants de ``annee``. Quand le
    profil n'a pas d'employeur — ou que sa contribution n'est pas un prix du
    travail —, les barèmes patronaux sont vides : ``cout_du_travail`` vaut alors
    ``brut``, et la page n'affiche pas la ligne.
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
        """Ce que l'assuré touche, rapporté à ce que son emploi coûte.

        Quand le profil n'affiche pas de coût du travail, le dénominateur est le
        brut : la grandeur devient « ce qui reste sur cent euros de traitement »,
        et la page la nomme ainsi.
        """
        return self.net / self.cout_du_travail if self.cout_du_travail else 0.0


class ConstructeurFiche:
    """Construit une fiche de paie sous un bloc retraite donné, pour un profil."""

    def __init__(self, profil: ProfilRemuneration) -> None:
        self.profil = profil

    # -- pièces --------------------------------------------------------------

    def _lignes(self, bloc: BlocRetraite, brut: float, plafond: float,
                cadre: bool) -> tuple[Ligne, ...]:
        lignes = [
            Ligne(code=composante.code, libelle=composante.libelle, retraite=True,
                  salarie=_montant(composante.salarie, brut, plafond),
                  employeur=_montant(composante.employeur, brut, plafond))
            for composante in bloc.composantes
        ]
        for poste in self.profil.postes:
            if poste.retraite and bloc.remplace_les_contributions_d_equilibre:
                continue
            if not poste.du(brut, plafond, cadre):
                continue
            lignes.append(Ligne(
                code=poste.code, libelle=poste.libelle, retraite=poste.retraite,
                salarie=poste.montant_salarie(brut, plafond),
                employeur=_montant(poste.employeur, brut, plafond),
            ))
        contributions = self._csg_crds(bloc, brut, plafond)
        if contributions:
            lignes.append(contributions)
        return tuple(lignes)

    def _csg_crds(self, bloc: BlocRetraite, brut: float,
                  plafond: float) -> Ligne | None:
        """La CSG et la CRDS, diminuées des points que le système rend.

        Le taux ne peut pas devenir négatif : un système qui rendrait plus que
        la CSG ne prélève rien, il ne verse pas. Le libellé dit que la ligne a
        bougé, et la page dit de combien — une fiche qui afficherait « CSG et
        CRDS » au même libellé pour deux taux différents ne se relirait pas.
        """
        plein = self.profil.csg + self.profil.crds
        taux = max(0.0, plein - bloc.csg_rendue)
        if taux <= 0:
            return None
        abattement = _montant(self.profil.abattement_frais, brut, plafond)
        libelle = "CSG et CRDS allégées" if bloc.csg_rendue > 0 else "CSG et CRDS"
        return Ligne(code="csg_crds", libelle=libelle, retraite=False,
                     salarie=(brut - abattement) * taux, employeur=0.0)

    def _perimetre_reduction(self, bloc: BlocRetraite, brut: float,
                             plafond: float, cadre: bool) -> float:
        """Cotisations patronales que la réduction générale peut effacer."""
        total = sum(
            _montant(composante.employeur, brut, plafond)
            for composante in bloc.composantes
            if composante.dans_la_reduction_generale
        )
        for poste in self.profil.postes:
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
        reduction = self.profil.reduction_generale
        if reduction is None:
            return 0.0
        coefficient = reduction.coefficient(
            brut, smic_annuel, bloc.taux_employeur_dans_la_reduction(self.profil)
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
        """La fiche de paie d'une année, à revenu brut donné."""
        lignes = self._lignes(bloc, brut, plafond_annuel, cadre)
        reduction = self._reduction(bloc, brut, plafond_annuel, smic_annuel, cadre)
        salariales = sum(ligne.salarie for ligne in lignes)
        patronales = sum(ligne.employeur for ligne in lignes)
        part_retraite = 0.0
        if self.profil.reduction_generale is not None:
            taux_retraite = bloc.taux_employeur_dans_la_reduction(self.profil)
            maximal = self.profil.reduction_generale.coefficient_maximal_avec(
                taux_retraite)
            part_retraite = taux_retraite / maximal if maximal > 0 else 0.0
        return FicheDePaie(
            annee=annee,
            cout_du_travail=brut + patronales - reduction,
            brut=brut,
            net=brut - salariales,
            lignes=lignes,
            reduction_generale=reduction,
            fiabilite=self.profil.fiabilite,
            part_retraite_dans_la_reduction=min(1.0, part_retraite),
        )

    def brut_a_cout_donne(self, cout: float, plafond_annuel: float,
                          smic_annuel: float, bloc: BlocRetraite,
                          cadre: bool = False) -> float:
        """Le revenu brut qui épuise un coût du travail donné.

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

    def brut_a_net_donne(self, net: float, plafond_annuel: float,
                         smic_annuel: float, bloc: BlocRetraite,
                         cadre: bool = False) -> float:
        """Le revenu brut dont il reste ``net`` une fois tout retiré.

        L'inverse de la fiche de paie, et il sert à la SAISIE : le lecteur qui
        connaît son net — la plupart des gens — le tape tel quel, et le modèle,
        qui ne raisonne qu'en brut, remonte jusqu'à lui.

        Le net croît strictement avec le brut : chaque taux est inférieur à un,
        et ceux qui dépendent du niveau — les tranches, les barèmes progressifs
        des indépendants — ne font que changer la pente. Une dichotomie suffit
        donc, comme pour le coût du travail. La borne haute part de trois fois
        le net : aucun profil ne prélève deux tiers d'un revenu.
        """
        if net <= 0:
            return 0.0
        bas, haut = net, net * 3.0
        for _ in range(80):
            milieu = (bas + haut) / 2
            fiche = self.fiche(0, milieu, plafond_annuel, smic_annuel, bloc, cadre)
            if fiche.net < net:
                bas = milieu
            else:
                haut = milieu
        return (bas + haut) / 2

    def brut_partage(self, actuelle: FicheDePaie, plafond_annuel: float,
                     smic_annuel: float, bloc: BlocRetraite,
                     cadre: bool = False) -> float:
        """Le brut quand la MOITIÉ de ce que l'employeur libère lui revient.

        C'est ``Incidence.PARTAGEE``, et elle n'existe que pour un employeur
        public dont la contribution est un taux d'ÉQUILIBRE : 82,28 % du
        traitement pour l'État en 2026, 37,65 % pour la CNRACL. Cette
        contribution n'est pas sur la fiche de paie — elle ne figure ni dans le
        brut ni dans les cotisations patronales du profil, qui sont vides —,
        et c'est ``contribution_equilibre_actuelle`` qui la porte.

        Le calcul est celui du coût du travail, décalé d'un cran :

            dépense actuelle  = traitement × (1 + taux d'équilibre)
            dépense si rien ne bougeait = ce que la proposition prélève sur le
                                          même traitement
            libéré            = la différence
            dépense retenue   = dépense actuelle − (1 − part rendue) × libéré

        et le traitement est celui qui épuise la dépense retenue sous les
        nouveaux taux. À part rendue nulle, on retrouve l'assiette fixe ; à un,
        l'incidence intégrale.

        **Sans taux d'équilibre connu, on retombe sur l'assiette fixe.** Un
        régime dont la série employeur ne couvre pas l'année ne libère rien
        qu'on sache chiffrer, et lui appliquer la formule ferait BAISSER le
        traitement — la proposition prélèverait une part patronale que
        l'employeur ne versait pas.
        """
        if bloc.contribution_equilibre_actuelle <= 0.0:
            return actuelle.brut
        equilibre = actuelle.brut * bloc.contribution_equilibre_actuelle
        depense_actuelle = actuelle.cout_du_travail + equilibre
        a_traitement_inchange = self.fiche(
            0, actuelle.brut, plafond_annuel, smic_annuel, bloc, cadre
        ).cout_du_travail
        libere = max(0.0, depense_actuelle - a_traitement_inchange)
        retenue = depense_actuelle - (1.0 - bloc.part_rendue_aux_salaires) * libere
        return self.brut_a_cout_donne(
            retenue, plafond_annuel, smic_annuel, bloc, cadre)

    def brut_sous_la_proposition(self, actuelle: FicheDePaie, plafond_annuel: float,
                                 smic_annuel: float, bloc: BlocRetraite,
                                 cadre: bool = False) -> float:
        """Le brut à retenir sous le nouveau système, selon l'incidence du profil.

        Trois lignes, mais c'est là que se joue la décision du module : tenir le
        coût du travail fixe quand l'employeur est connu, tenir l'assiette fixe
        quand il n'y en a pas, partager quand ce qu'il verse est un taux
        d'équilibre.
        """
        if self.profil.incidence is Incidence.PARTAGEE:
            return self.brut_partage(
                actuelle, plafond_annuel, smic_annuel, bloc, cadre)
        if self.profil.incidence is Incidence.ASSIETTE:
            return actuelle.brut
        return self.brut_a_cout_donne(
            actuelle.cout_du_travail, plafond_annuel, smic_annuel, bloc, cadre)


# -- les blocs retraite des scénarios ---------------------------------------
#
# Ils sont construits ICI, mais à partir des fiches de régime : la fiche de paie
# prélève exactement ce que le compte notionnel encaisse. Écrire les taux une
# seconde fois aurait garanti qu'ils divergent un jour.


def bloc_droit_en_vigueur(catalogue, affiliations, statut: str, annee: int,
                          ) -> BlocRetraite:
    """Ce que le droit en vigueur prélève pour la retraite, par régime.

    Un étage par régime : la vieillesse de base et sa part déplafonnée d'un
    côté, la complémentaire de l'autre, chacun avec ses bornes d'assiette et
    son partage salarié/employeur, lus dans la fiche.

    **Un non-salarié paie tout.** La fiche d'un régime partagé avec des salariés
    — un artisan relève du régime général — porte la répartition 45/55 d'un
    salarié : le taux est le bon, la répartition ne le concerne pas. C'est ce
    que dit ``sans_employeur`` dans ``affiliations.yaml``, et
    ``moteur/compte.py`` en tire déjà la même conséquence pour le compte
    notionnel. Sans ce correctif, la fiche de paie d'un artisan aurait montré un
    employeur qui n'existe pas et aurait sous-estimé de moitié ce qu'il verse.

    Ce bloc vaut pour les systèmes 1, 2 et 3 du site : ils ne changent PAS ce
    qui est prélevé, seulement ce qui est porté au compte. C'est la raison pour
    laquelle la fiche de paie de ces trois systèmes est la même, au centime.
    """
    sans_employeur = affiliations.sans_employeur(statut)
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
            part = 1.0 if sans_employeur else periode.part_salariale
            taux = periode.taux_cotisation_retraite
            if taux:
                salarie.append(Segment(basse, haute, taux * part))
                employeur.append(Segment(basse, haute, taux * (1.0 - part)))
            # La part déplafonnée porte sur la totalité du salaire, par-dessus
            # la précédente : c'est un segment de plus, non une tranche.
            taux_deplafonne = periode.taux_cotisation_deplafonnee
            if taux_deplafonne:
                part_deplafonnee = (
                    1.0 if sans_employeur else periode.part_salariale_deplafonnee)
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
                     part_salariale: float = 0.0633 / 0.23,
                     libelle_repartition: str = "Retraite, compte notionnel",
                     libelle_capitalisation: str = "Retraite, part capitalisée",
                     csg_rendue: float = 0.0,
                     part_rendue_aux_salaires: float = 0.0,
                     contribution_equilibre_actuelle: float = 0.0,
                     ) -> BlocRetraite:
    """Le bloc de la proposition : un taux unique, au premier euro, sans plafond.

    ``part_salariale`` partage chaque taux entre l'assuré et son employeur. La
    proposition ne le dit pas ; le programme laisse à l'employeur les 16,67
    points qu'il verse aujourd'hui et ramène l'assuré de 11,31 à 6,33, d'où le
    défaut ``0,0633 / 0,23``. Le docstring du module dit pourquoi ce choix,
    qu'on croirait sans effet, en a un : la CSG est assise sur le brut, et la
    réduction générale n'efface que du patronal.

    Le pilier capitalisé est un étage à part, et hors du périmètre de la
    réduction générale : il n'est ni une assurance sociale, ni un régime
    complémentaire légalement obligatoire au sens de l'article L. 921-4.

    **Les cinq points VOLONTAIRES n'y sont pas.** Le bloc ne porte que ce que
    la proposition impose : une épargne que l'assuré décide seul n'est pas une
    retenue sur salaire, et la mettre ici ferait baisser un net que la
    proposition ne baisse pas. Elle est chiffrée à part, sur le net, par
    :attr:`AnneeComparee.epargne_volontaire`.
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
        csg_rendue=csg_rendue,
        part_rendue_aux_salaires=part_rendue_aux_salaires,
        contribution_equilibre_actuelle=contribution_equilibre_actuelle,
    )


def bloc_taux_unique_sans_employeur(
        taux_repartition: float, taux_capitalisation: float = 0.0,
        csg_rendue: float = 0.0,
        ) -> BlocRetraite:
    """Le même bloc pour qui n'a pas d'employeur : il porte les 18 % en entier.

    La proposition additionne « salariale et patronale ». Un indépendant est les
    deux à la fois — c'est déjà vrai aujourd'hui de ses 26 points —, et lui
    prêter un employeur pour la moitié de la charge fabriquerait un gain qui
    n'existe pas.
    """
    return bloc_taux_unique(taux_repartition, taux_capitalisation,
                            part_salariale=1.0, csg_rendue=csg_rendue)


def contribution_equilibre(racine_donnees: Path, affiliations, statut: str,
                           annee: int) -> float:
    """Ce que l'employeur public verse aujourd'hui, en fraction du traitement.

    Zéro quand aucune série ne couvre le régime cette année-là : la fiche
    retombe alors sur l'assiette fixe, et ``brut_partage`` dit pourquoi c'est
    la seule issue prudente.

    Les régimes d'un statut sont additionnés parce qu'ils le sont déjà
    ailleurs : un agent peut relever d'un régime de base et d'un régime
    additionnel, et la contribution de son employeur est la somme des deux.

    Pour un militaire, l'État verse son taux propre — 126,07 % de la solde en
    2026, quand il verse 82,28 % du traitement d'un civil —, et c'est celui-là
    qu'il cesserait de verser.
    """
    table = _contributions_publiques(racine_donnees)
    militaire = statut in affiliations.categories_militaires
    total = 0.0
    for code in affiliations.regimes(statut, annee):
        contribution = table.taux(code, annee, militaire)
        if contribution is not None:
            total += contribution.taux
    return total


@lru_cache(maxsize=4)
def _contributions_publiques(racine: Path) -> ContributionsEmployeurPubliques:
    return ContributionsEmployeurPubliques(racine)


# -- à quel profil un statut appartient --------------------------------------


def profil_de_la_fiche(affiliations, catalogue, statut: str,
                       annee: int) -> str | None:
    """Le profil de fiche de paie d'un statut, ou ``None`` si aucun ne convient.

    Le découpage est celui de ce que l'on SAIT de l'employeur, et non celui des
    familles de statut — parce que c'est cela qui décide si une ligne « coût du
    travail » veut dire quelque chose :

    1. pas d'employeur du tout (``sans_employeur``) → ``independant`` ;
    2. au moins un régime dont la fiche ne porte que la retenue de l'agent
       (``perimetre_taux == "agent_seul"``) → ``agent_seul``. C'est le
       fonctionnaire, le militaire, le marin, l'artiste de l'Opéra : la part
       employeur existe, mais c'est un taux d'équilibre ;
    3. la famille ``public`` sans régime à retenue, c'est l'agent non titulaire
       → ``salarie_ircantec``, qui ne doit ni CEG, ni CET, ni APEC ;
    4. le reste → ``salarie_prive``. Y tombent les statuts de la famille
       ``special`` que la fermeture des régimes spéciaux a versés au régime
       général et à l'Agirc-Arrco : leur fiche de paie est bel et bien celle
       d'un salarié du privé.

    La distinction (2) se lit dans les fiches de régime plutôt que dans une
    liste de statuts : c'est elle qui suivra toute seule si un régime spécial
    de plus est fermé.
    """
    try:
        famille = affiliations.famille(statut)
    except KeyError:
        return None
    if famille not in FAMILLES_COUVERTES:
        return None
    if affiliations.part_salariale_seule(statut):
        # Un auteur n'a pas de fiche de paie : voir ``fiche_de_paie_possible``.
        return None
    if famille == "independant" or affiliations.sans_employeur(statut):
        return "independant"
    for code in affiliations.regimes(statut, annee):
        if code not in catalogue:
            continue
        regime = catalogue[code]
        if regime.hors_repartition:
            continue
        for periode in regime.periodes_actives(annee):
            if periode.perimetre_taux == "agent_seul":
                return "agent_seul"
    if famille == "public":
        return "salarie_ircantec"
    return "salarie_prive"


def fiche_de_paie_possible(affiliations, statut: str) -> bool:
    """La fiche de paie sait-elle décrire ce statut ?

    Ne regarde que la famille, parce que c'est tout ce qu'un formulaire connaît
    avant d'avoir une année : le choix du profil, lui, demande le catalogue et
    une année, et c'est ``profil_de_la_fiche`` qui le fait.

    Restent dehors les salariés agricoles — la MSA a ses propres taux hors
    retraite —, l'outre-mer, dont chaque collectivité a sa caisse, les élus,
    dont l'indemnité de fonction n'est pas un salaire, et qui n'a pas d'emploi.

    Et les AUTEURS, bien qu'ils soient de la famille du privé : leur précompte
    n'est pas une fiche de paie. Ils paient la vieillesse d'un salarié, mais
    ni son assurance chômage ni sa complémentaire — la leur est le RAAP —, et
    le diffuseur ne verse qu'une contribution de 1 % là où un employeur paie
    une quarantaine de points. La fiche du salarié leur prêtait l'un et
    l'autre : mieux vaut rien qu'un net faux.
    """
    if affiliations.part_salariale_seule(statut):
        return False
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
    #: Le taux des cinq points rendus que le site suppose placés, sur
    #: l'assiette de la proposition. Il n'est PAS dans ``proposition`` : la
    #: fiche s'arrête à ce que la proposition impose, et ce placement se
    #: chiffre à côté, pris sur le net.
    taux_epargne_volontaire: float = 0.0
    #: Points de CSG d'activité que la proposition rend cette année-là, en
    #: fraction du brut abattu. Déjà retranchés de ``proposition`` ; gardés ici
    #: pour que la page puisse dire de combien la ligne a bougé.
    csg_rendue: float = 0.0
    #: Taux d'équilibre que l'employeur public verse aujourd'hui, nul pour tout
    #: autre profil. Gardé pour la même raison : la page doit pouvoir écrire
    #: d'où vient le traitement supplémentaire.
    contribution_equilibre: float = 0.0

    @property
    def gain_net(self) -> float:
        """Ce que la proposition ajoute au revenu net, en euros de l'année."""
        return self.proposition.net - self.droit_en_vigueur.net

    @property
    def gain_net_constant(self) -> float:
        return self.gain_net * self.coefficient_euros_constants

    #: Code de la ligne capitalisée de la fiche : celle que la proposition
    #: impose. La volontaire n'a pas de ligne, elle n'est pas prélevée.
    CODE_CAPITALISATION = "capitalisation"

    @property
    def epargne_a_votre_nom(self) -> float:
        """Le pilier capitalisé imposé : prélevé sur le net, mais acquis à l'assuré.

        Il n'est pas une cotisation perdue : il alimente un compte transmissible
        aux héritiers tant qu'il n'est pas liquidé. Le site l'affiche à part du
        gain, parce que le confondre avec lui serait compter deux fois, et le
        passer sous silence serait compter une fois de trop.

        Seule la cotisation OBLIGATOIRE y est : c'est la seule que la fiche
        prélève. Les cinq points volontaires sont :attr:`epargne_volontaire`.
        """
        return sum(ligne.salarie + ligne.employeur
                   for ligne in self.proposition.lignes
                   if ligne.code == self.CODE_CAPITALISATION)

    @property
    def epargne_volontaire(self) -> float:
        """Les cinq points rendus, si l'assuré les place : pris sur le net.

        Ce n'est pas une ligne de la fiche, c'est un virement que l'assuré
        décide, et le modèle le chiffre sur l'assiette de la proposition — la
        même que le pilier —, entièrement à sa charge : personne ne cofinance
        une épargne qu'on décide seul. Il ne touche ni au coût du travail, ni
        au brut, ni à la CSG, qui est assise sur le brut : il ne déplace que ce
        qui reste du net, d'exactement son montant.
        """
        return self.proposition.brut * self.taux_epargne_volontaire

    @property
    def net_apres_volontaire(self) -> float:
        """Ce qui reste du net PLEIN une fois les cinq points rendus placés.

        C'est le second net que le site écrit : celui de qui suit la
        convention de comparaison à 28 % cotisés, et dont la rente du
        scénario 6 est calculée.
        """
        return self.proposition.net - self.epargne_volontaire

    @property
    def gain_net_apres_volontaire(self) -> float:
        """Ce que la proposition ajoute au net de qui place les points rendus."""
        return self.net_apres_volontaire - self.droit_en_vigueur.net

    @property
    def brut_sous_le_smic(self) -> bool:
        """L'incidence intégrale ferait-elle passer le brut sous le SMIC ?

        Le cas se produit quand la proposition prélève PLUS que le droit en
        vigueur à coût du travail donné. Il est alors impossible en droit : le
        salaire minimum est un plancher. C'est un avertissement, et le site le
        porte. Sous l'incidence sur l'assiette, le brut ne bouge pas : la
        question ne se pose pas.
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
    #: Le profil retenu, et ce que la page doit en savoir pour écrire ses
    #: libellés et ses hypothèses.
    profil: str = "salarie_prive"
    libelle_profil: str = "Salarié"
    libelle_assiette: str = "Salaire brut"
    libelle_net: str = "Salaire net"
    affiche_cout_du_travail: bool = True
    incidence: Incidence = Incidence.COUT_DU_TRAVAIL
    #: Part de ce que l'employeur libère qui remonte dans l'assiette, sous
    #: ``Incidence.PARTAGEE``. La page en a besoin pour écrire « la moitié ».
    part_rendue_aux_salaires: float = 0.0

    @property
    def csg_rendue(self) -> float:
        """Les points de CSG d'activité rendus l'année de référence."""
        return self.reference.csg_rendue

    @property
    def contribution_equilibre(self) -> float:
        """Ce que l'employeur public verse aujourd'hui, l'année de référence."""
        return self.reference.contribution_equilibre

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
        """Ce que le pilier capitalisé imposé aura prélevé, en euros constants."""
        return sum(annee.epargne_a_votre_nom * annee.coefficient_euros_constants
                   for annee in self.annees)

    @property
    def epargne_volontaire_mensuelle(self) -> float:
        """Les cinq points rendus de l'année de référence, par mois, s'ils sont placés."""
        return self.reference.epargne_volontaire / 12.0

    @property
    def epargne_volontaire_cumulee(self) -> float:
        """Ce que les seuls points rendus auront placé, en euros constants."""
        return sum(annee.epargne_volontaire * annee.coefficient_euros_constants
                   for annee in self.annees)

    @property
    def gain_net_mensuel_apres_volontaire(self) -> float:
        """Le gain de net de qui place les points rendus, par mois."""
        return self.reference.gain_net_apres_volontaire / 12.0

    @property
    def verse_le_volontaire(self) -> bool:
        """Y a-t-il seulement des points rendus à montrer ?"""
        return any(annee.epargne_volontaire > 0 for annee in self.annees)

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
    code_profil = profil_de_la_fiche(
        affiliations, catalogue, statut, annees_actives[0])
    if code_profil is None:
        return None

    prelevements = charger_prelevements(parametres.racine_donnees)
    profil = prelevements.profil(code_profil)
    constructeur = ConstructeurFiche(profil)
    # « Cadre » n'est pas une famille d'affiliation : c'est la seule chose qui
    # sépare deux statuts du privé pour la cotisation APEC, qui vaut 0,024 %.
    cadre = "cadre" in statut and "non_cadre" not in statut
    capitalisation = (parametres.taux_capitalisation_obligatoire
                      if parametres.capitalisation_obligatoire else 0.0)
    # Les cinq points rendus ne sont pas dans le bloc : la fiche s'arrête à ce
    # que la proposition impose, et leur placement se chiffre sur chaque année,
    # pris sur le net.
    volontaire = parametres.taux_capitalisation_volontaire_applique
    sans_employeur = affiliations.sans_employeur(statut)
    rendue = parametres.part_rendue_aux_salaires
    # La contribution d'équilibre ne concerne que le profil dont l'employeur en
    # verse une : la chercher pour un salarié du privé la trouverait nulle, et
    # coûterait un chargement de série par carrière.
    partage = profil.incidence is Incidence.PARTAGEE

    def bloc_propose(annee: int) -> BlocRetraite:
        """Le bloc de la proposition l'année ``annee``.

        Il est reconstruit à chaque année parce que deux de ses trois nouveautés
        en dépendent : les points de CSG rendus suivent le poste abandonné, que
        le COR projette année par année, et le taux d'équilibre de l'employeur
        public suit sa propre série. Le coût est nul — le bloc est trois
        segments — et l'alternative aurait figé un taux sur toute une carrière.
        """
        csg = points_csg_rendus(parametres.racine_donnees, annee, rendue)
        if sans_employeur:
            return bloc_taux_unique_sans_employeur(
                parametres.taux_cotisation_liberal, capitalisation,
                csg_rendue=csg)
        return bloc_taux_unique(
            parametres.taux_cotisation_liberal, capitalisation,
            part_salariale=parametres.part_salariale_taux_unique,
            csg_rendue=csg,
            part_rendue_aux_salaires=rendue,
            contribution_equilibre_actuelle=contribution_equilibre(
                parametres.racine_donnees, affiliations, statut, annee)
            if partage else 0.0,
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
        propose = bloc_propose(annee)
        fiche_actuelle = constructeur.fiche(
            annee, brut, plafond, smic, actuel_bloc, cadre)
        brut_propose = constructeur.brut_sous_la_proposition(
            fiche_actuelle, plafond, smic, propose, cadre)
        fiche_proposee = constructeur.fiche(
            annee, brut_propose, plafond, smic, propose, cadre)
        comparees.append(AnneeComparee(
            annee=annee,
            droit_en_vigueur=fiche_actuelle,
            proposition=fiche_proposee,
            coefficient_euros_constants=macro.coefficient_prix(
                annee, parametres.annee_euros_constants),
            taux_epargne_volontaire=volontaire,
            csg_rendue=propose.csg_rendue,
            contribution_equilibre=propose.contribution_equilibre_actuelle,
            _smic=smic,
        ))

    if not comparees:
        return None
    return RemunerationActif(
        statut=statut,
        libelle_statut=affiliations.libelle(statut),
        cadre=cadre,
        annees=tuple(comparees),
        millesime_bareme=profil.annee,
        fiabilite=profil.fiabilite,
        profil=profil.code,
        libelle_profil=profil.libelle,
        libelle_assiette=profil.libelle_assiette,
        libelle_net=profil.libelle_net,
        affiche_cout_du_travail=profil.cout_du_travail,
        incidence=profil.incidence,
        part_rendue_aux_salaires=rendue,
    )


def salaire_brut_depuis_net(racine_donnees, macro, catalogue, affiliations,
                            statut: str, annee: int, net_annuel: float) -> float:
    """Le revenu brut annuel dont il reste ``net_annuel`` — ou lui-même.

    C'est l'entrée du mode « net » de la saisie : le lecteur qui connaît son
    net le tape tel quel, et le modèle, qui ne raisonne qu'en brut, remonte
    jusqu'à lui par la fiche de paie de son statut.

    Rend le net INCHANGÉ quand le statut n'a pas de fiche de paie — l'exploitant
    agricole, l'élu, l'outre-mer. Mieux vaut un brut approché par un net qu'un
    refus de calculer ; le site dit alors, sous le champ, qu'il n'a pas su
    convertir et que le nombre est lu comme un brut.
    """
    if net_annuel <= 0:
        return net_annuel
    code_profil = profil_de_la_fiche(affiliations, catalogue, statut, annee)
    if code_profil is None:
        return net_annuel
    profil = charger_prelevements(racine_donnees).profil(code_profil)
    cadre = "cadre" in statut and "non_cadre" not in statut
    return ConstructeurFiche(profil).brut_a_net_donne(
        net_annuel,
        macro.plafond_securite_sociale(annee),
        smic_annuel(macro, annee),
        bloc_droit_en_vigueur(catalogue, affiliations, statut, annee),
        cadre,
    )


def salaire_net_depuis_brut(racine_donnees, macro, catalogue, affiliations,
                            statut: str, annee: int, brut_annuel: float) -> float:
    """Le revenu net annuel que laisse ``brut_annuel`` — ou lui-même.

    Le sens direct, et il sert à la BASCULE : passer du mode brut au mode net
    doit décrire la même carrière, donc traduire le nombre saisi et non le
    relire. Même repli que son inverse pour les statuts sans fiche de paie.
    """
    if brut_annuel <= 0:
        return brut_annuel
    code_profil = profil_de_la_fiche(affiliations, catalogue, statut, annee)
    if code_profil is None:
        return brut_annuel
    profil = charger_prelevements(racine_donnees).profil(code_profil)
    cadre = "cadre" in statut and "non_cadre" not in statut
    return ConstructeurFiche(profil).fiche(
        annee, brut_annuel,
        macro.plafond_securite_sociale(annee),
        smic_annuel(macro, annee),
        bloc_droit_en_vigueur(catalogue, affiliations, statut, annee),
        cadre,
    ).net


def conversion_possible(affiliations, catalogue, statut: str, annee: int) -> bool:
    """Le modèle sait-il convertir un net en brut pour ce statut ?"""
    return profil_de_la_fiche(affiliations, catalogue, statut, annee) is not None
