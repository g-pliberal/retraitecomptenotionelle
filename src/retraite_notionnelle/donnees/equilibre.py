"""Ce que la retraite encaisse, et non plus seulement ce qu'elle verse.

``depenses.py`` porte la dépense observée : les Comptes de la protection
sociale de la DREES, risque vieillesse-survie, depuis 1959. Ce module porte
l'autre moitié du bilan — les RESSOURCES —, et avec elle le solde, qui est la
seule grandeur par laquelle un système de répartition se juge soutenable.

POURQUOI UNE AUTRE SOURCE, ET UN AUTRE PÉRIMÈTRE
-------------------------------------------------
On aurait voulu les ressources du même producteur, sur le même périmètre, pour
les retrancher ligne à ligne. Elles n'existent pas : **les Comptes de la
protection sociale ne ventilent pas leurs ressources par risque.** Ils publient
la dépense risque par risque et le financement de l'ensemble — maladie, vieux,
famille, logement confondus. Une « recette du risque vieillesse » n'est pas une
donnée que quiconque a manqué de produire : c'est une donnée qui n'a pas de
définition comptable, les cotisations d'un régime polyvalent n'étant pas
affectées à un risque.

Ce qui existe, en revanche, c'est le compte du SYSTÈME DE RETRAITE : dépenses,
ressources et solde du même ensemble de régimes, sous la même convention. Le
COR l'établit chaque année dans son rapport, en consolidant les rapports à la
Commission des comptes de la Sécurité sociale, et personne d'autre ne
l'établit. On prend donc les DEUX colonnes chez lui — pas seulement les
ressources —, parce qu'un solde ne se fabrique pas en soustrayant deux
périmètres différents.

Ce périmètre n'est pas celui de ``depenses.py`` :

* champ : ensemble des régimes légalement obligatoires, FSV compris, RAFP
  exclu. Ni dépendance, ni capitalisation, ni aide sociale des départements ;
* ordre de grandeur : 13,86 % du PIB en 2024, contre 13,59 % pour la
  « répartition obligatoire » de la DREES et 14,54 % pour le risque
  vieillesse-survie entier. L'écart entre les deux premiers — moins de trois
  dixièmes de point — est le meilleur recoupement dont ces deux séries
  disposent, et c'est le test ``test_les_deux_perimetres_se_recoupent`` qui le
  tient.

CE QUE LA STRUCTURE DES RESSOURCES SERT À DIRE
-----------------------------------------------
Deux tiers des ressources sont des cotisations assises sur des revenus
d'activité. Le reste ne l'est pas, et il faut le savoir avant de lire un
coefficient d'équilibre : la contribution que l'État verse au régime de ses
fonctionnaires est fixée pour ÉQUILIBRER ce régime et non pour acquérir des
droits, les impôts affectés compensent des exonérations, les subventions
d'équilibre comblent des régimes en extinction. Un système en comptes
notionnels ne sait créditer que la première catégorie ; ``contributive`` dit
laquelle c'est.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .chargement import Fiabilite, SerieAnnuelle, charger_serie_annuelle


@dataclass(frozen=True)
class PosteRessources:
    """Un poste du financement, au découpage du rapport annuel du COR.

    ``contributive`` dit si le poste est une cotisation assise sur un revenu
    d'activité — la seule ressource qu'un compte notionnel sache porter au
    crédit de quelqu'un. La contribution d'équilibre de l'État à ses propres
    fonctionnaires en est une malgré son nom : elle est prélevée sur les
    traitements, à un taux publié, et le modèle la porte déjà au compte des
    scénarios 4 et 5. Un impôt affecté, non.
    """

    code: str
    libelle: str
    glose: str
    contributive: bool


#: Les six postes, dans l'ordre d'affichage : ce qui est cotisé d'abord, puis
#: ce qui ne l'est pas, par masse décroissante en fin de série. Les codes sont
#: ceux qu'écrit ``scripts/verifier_donnees.py`` depuis les libellés du COR ; un
#: test vérifie que les deux listes ne divergent pas.
POSTES: tuple[PosteRessources, ...] = (
    PosteRessources(
        "cotisations", "Cotisations sociales",
        "Salariales, patronales et de non-salariés, hors contribution "
        "d'équilibre. Les deux tiers du financement, et la seule part qu'un "
        "compte notionnel sache créditer telle quelle.",
        True,
    ),
    PosteRessources(
        "contribution_equilibre_etat", "Contribution d'équilibre de l'État",
        "Ce que l'État verse au régime de ses propres fonctionnaires, au taux "
        "qui équilibre ce régime — 74,28 % des traitements en 2024. C'est une "
        "cotisation d'employeur par son assiette, un solde par son taux : le "
        "modèle la porte au compte des scénarios 4 et 5, et elle est comptée "
        "ici comme contributive pour cette raison.",
        True,
    ),
    PosteRessources(
        "impots_et_taxes", "Impôts et taxes affectés",
        "CSG, forfait social, taxe sur les salaires, transferts de TVA. Pour "
        "l'essentiel, la compensation des allègements généraux de cotisations "
        "patronales : l'État a exonéré, puis remboursé par l'impôt.",
        False,
    ),
    PosteRessources(
        "transferts", "Transferts d'organismes extérieurs",
        "Branche famille pour les majorations de pension et l'assurance "
        "vieillesse des parents au foyer, Unédic pour les périodes de chômage. "
        "Des droits sont acquis sans cotisation de l'assuré, et quelqu'un paie.",
        False,
    ),
    PosteRessources(
        "subventions_equilibre", "Subventions d'équilibre aux régimes spéciaux",
        "Ce que le budget de l'État comble à la SNCF, à la RATP, aux marins, "
        "aux mines : des régimes dont les cotisants ont disparu avant les "
        "pensionnés.",
        False,
    ),
    PosteRessources(
        "autres_produits", "Autres produits",
        "Reprises de provisions, produits de gestion, recettes diverses des "
        "caisses.",
        False,
    ),
)

CODES_POSTES = tuple(poste.code for poste in POSTES)


@dataclass(frozen=True)
class GroupeRessources:
    """Un regroupement de postes, dit dans les mots de tout le monde.

    Les six postes du COR sont ceux d'un comptable. « Contribution d'équilibre
    de l'État », « impôts et taxes affectés », « transferts d'organismes
    extérieurs » ne disent rien à qui n'a pas fait d'économie, et un graphique à
    six bandes est de toute façon illisible. Quatre groupes suffisent à porter
    la seule chose que cette ventilation a à dire : les trois quarts de l'argent
    viennent des salaires, le reste vient d'ailleurs.

    Le découpage détaillé n'est pas perdu pour autant — la page le montre en
    entier, poste par poste, dans son dépliant.
    """

    code: str
    libelle: str
    #: Une phrase, sans jargon, qui dit ce que le groupe contient.
    explication: str
    postes: tuple[str, ...]
    #: Couleur de la bande dans le graphique empilé.
    couleur: str


#: Les quatre groupes, du plus cotisé au moins cotisé. L'ordre est celui des
#: bandes du graphique, de bas en haut : le socle des salaires d'abord.
GROUPES: tuple[GroupeRessources, ...] = (
    GroupeRessources(
        "salaires", "Cotisations sur les salaires",
        "Prélevées sur chaque fiche de paie, une part par le salarié, une part "
        "par l'employeur. C'est la seule ressource qu'un compte notionnel sache "
        "porter au crédit de quelqu'un.",
        ("cotisations", "contribution_equilibre_etat"),
        "var(--serie-5)",
    ),
    GroupeRessources(
        "impots", "Impôts",
        "CSG, TVA, taxe sur les salaires. L'État a allégé les cotisations des "
        "employeurs pour baisser le coût du travail, puis remboursé la retraite "
        "par l'impôt.",
        ("impots_et_taxes",),
        "var(--serie-6)",
    ),
    GroupeRessources(
        "transferts", "Versements d'autres caisses",
        "La branche famille paie les droits liés aux enfants, l'assurance "
        "chômage ceux des périodes sans emploi : des droits acquis sans "
        "cotisation de l'assuré, que quelqu'un paie quand même.",
        ("transferts",),
        "var(--serie-7)",
    ),
    GroupeRessources(
        "reste", "Le reste",
        "Ce que l'État comble à la SNCF, aux mines, aux marins — des régimes "
        "dont les cotisants ont disparu avant les retraités —, plus les "
        "produits financiers et les recettes diverses des caisses.",
        ("subventions_equilibre", "autres_produits"),
        "var(--serie-9)",
    ),
)


class ComptesRetraite:
    """Le compte du système de retraite : dépenses, ressources, solde, structure.

    Tout y est en PART DE PIB, parce que c'est ainsi que le COR le publie et
    que c'est la seule unité où une dépense de 2002 et une projection de 2070
    se comparent sans convention d'actualisation. Les euros s'en déduisent en
    multipliant par le PIB de l'année — ce que la page ne fait que sur les
    années où le PIB est publié, faute de quoi elle afficherait des milliards
    de 2070 qui ne seraient qu'une hypothèse de croissance déguisée.
    """

    def __init__(self, racine: Path) -> None:
        macro = racine / "reference" / "macro"
        chemin = macro / "comptes_retraite.csv"
        self.depenses = charger_serie_annuelle(
            chemin, "part_pib", nom="comptes_retraite_depenses",
            filtre={"poste": "depenses"},
        )
        self.ressources = charger_serie_annuelle(
            chemin, "part_pib", nom="comptes_retraite_ressources",
            filtre={"poste": "ressources"},
        )
        self.structure: dict[str, SerieAnnuelle] = {
            poste.code: charger_serie_annuelle(
                macro / "structure_ressources_retraite.csv", "part",
                nom=f"structure_{poste.code}", filtre={"poste": poste.code},
            )
            for poste in POSTES
        }

    # -- bornes --------------------------------------------------------------

    @property
    def premiere_annee(self) -> int:
        return self.depenses.premiere_annee

    @property
    def derniere_annee(self) -> int:
        return self.depenses.derniere_annee

    @property
    def derniere_annee_observee(self) -> int:
        """Dernière année que le COR marque « Obs » plutôt que « Sc. Ref ».

        Elle se lit dans la fiabilité et non dans une constante : le rapport
        suivant décalera la frontière d'un an, et le fichier de référence le
        dira tout seul.
        """
        observees = [
            annee for annee in self.depenses.annees()
            if self.depenses.fiabilite(annee) > Fiabilite.ESTIMEE
        ]
        return observees[-1] if observees else self.premiere_annee

    def annees(self) -> list[int]:
        return list(range(self.premiere_annee, self.derniere_annee + 1))

    # -- lectures ------------------------------------------------------------

    def depense(self, annee: int) -> float:
        """Dépenses du système de retraite, en part du PIB de la même année."""
        return self.depenses(annee)

    def ressource(self, annee: int) -> float:
        return self.ressources(annee)

    def solde(self, annee: int) -> float:
        """Ressources moins dépenses, en part de PIB. Négatif : besoin de financement.

        Le solde n'est pas stocké : il est la différence de deux séries écrites,
        et ``scripts/verifier_donnees.py`` confronte cette différence au solde
        que le COR publie séparément.
        """
        return self.ressources(annee) - self.depenses(annee)

    def part(self, code: str, annee: int) -> float:
        """Part d'un poste dans les ressources de l'année."""
        return self.structure[code](annee)

    def part_contributive(self, annee: int) -> float:
        """Part des ressources qui est une cotisation sur un revenu d'activité."""
        return sum(self.part(poste.code, annee)
                   for poste in POSTES if poste.contributive)

    def part_groupe(self, code: str, annee: int) -> float:
        """Part d'un groupe de postes dans les ressources de l'année."""
        groupe = next(g for g in GROUPES if g.code == code)
        return sum(self.part(poste, annee) for poste in groupe.postes)

    def ressource_groupe(self, code: str, annee: int) -> float:
        """Ce qu'un groupe rapporte, en part du PIB.

        C'est la grandeur que le graphique empile : les parts d'un même total
        ne se lisent qu'en pourcentages les unes des autres, alors que les
        parts de PIB se lisent aussi dans le temps — et c'est le temps qui dit
        que l'impôt a doublé pendant que les cotisations ne bougeaient pas.
        """
        return self.part_groupe(code, annee) * self.ressource(annee)

    # -- fenêtre de la ventilation -------------------------------------------
    #
    # Le total des ressources remonte à 2002 et va jusqu'à l'horizon du COR ; sa
    # VENTILATION ne couvre que les années où le COR l'a publiée. Les deux
    # bornes se lisent donc dans les séries, jamais dans une constante écrite
    # ici : le rapport suivant les décalera d'un an.

    @property
    def premiere_annee_ventilee(self) -> int:
        return max(serie.premiere_annee for serie in self.structure.values())

    @property
    def derniere_annee_ventilee(self) -> int:
        return min(serie.derniere_annee for serie in self.structure.values())

    def annees_ventilees(self) -> list[int]:
        return list(range(self.premiere_annee_ventilee,
                          self.derniere_annee_ventilee + 1))

    def fiabilite(self, annee: int) -> Fiabilite:
        return min(self.depenses.fiabilite(annee), self.ressources.fiabilite(annee))
