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

CE QUE LA VENTILATION DES TRANSFERTS SERT À DIRE
-------------------------------------------------
Le poste « transferts d'organismes extérieurs » est un agrégat, et ce qu'il
contient importe au compte notionnel plus qu'aucun autre : la CNAF y paie les
droits liés aux enfants — les cotisations d'assurance vieillesse des parents au
foyer et les majorations de pension pour trois enfants —, que les scénarios
notionnels du dépôt SUPPRIMENT. Compter cette recette comme acquise à un
système qui ne sert plus ces droits, c'est lui prêter dix milliards par an qui
ne lui reviennent pas. La série ``transferts_retraite.csv`` dit ce que la CNAF
et l'Unédic versent, année par année, lue chez celui qui paie (rapports à la
Commission des comptes de la Sécurité sociale), et ``ORGANISMES`` dit lequel
des deux finance un droit que le compte notionnel supprime.

CE QUE LA STRUCTURE DES RESSOURCES SERT À DIRE
-----------------------------------------------
Deux tiers des ressources sont des cotisations assises sur des revenus
d'activité. Le reste ne l'est pas, et il faut le savoir avant de lire un
coefficient d'équilibre : la contribution que l'État verse au régime de ses
fonctionnaires est fixée pour ÉQUILIBRER ce régime et non pour acquérir des
droits, les impôts affectés n'ouvrent de droit à personne, les subventions
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
        "modèle la porte au compte du système 3, et elle est comptée "
        "ici comme contributive pour cette raison.",
        True,
    ),
    PosteRessources(
        "impots_et_taxes", "Impôts et taxes affectés",
        "CSG, taxe sur les salaires, forfait social, contribution sociale de "
        "solidarité des sociétés, taxes des régimes agricoles. "
        "38 % en financent le fonds de solidarité vieillesse. Ce n'est PAS la "
        "compensation des allègements généraux de cotisations patronales : "
        "celle-là passe par la TVA, qui finance la branche maladie, et le "
        "compte de la Cnav n'en porte aucune ligne.",
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
        "CSG, taxe sur les salaires, forfait social. Des recettes fiscales "
        "affectées à la retraite, qui n'ouvrent de droit à personne : plus du "
        "tiers finance le fonds de solidarité vieillesse.",
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
        "Ce que l'État comble à la SNCF, aux mines, aux marins (des régimes dont les cotisants ont disparu avant les retraités), plus les "
        "produits financiers et les recettes diverses des caisses.",
        ("subventions_equilibre", "autres_produits"),
        "var(--serie-9)",
    ),
)


@dataclass(frozen=True)
class PosteTransfert:
    """Une ligne de ce qu'un organisme extérieur verse à la retraite.

    Au découpage des rapports à la Commission des comptes de la Sécurité
    sociale, du côté de celui qui paie : la fiche de la CNAF distingue l'AVPF
    des majorations, les fiches de l'Agirc-Arrco et de l'Ircantec portent
    chacune ce que l'Unédic leur verse.
    """

    code: str
    organisme: str
    libelle: str
    glose: str


@dataclass(frozen=True)
class Organisme:
    """Qui paie, et si le compte notionnel du dépôt supprime ce qu'il finance."""

    code: str
    libelle: str
    explication: str
    #: Le compte notionnel du dépôt supprime-t-il les droits que ce transfert
    #: paie ? Oui pour la branche famille : ni AVPF ni majorations dans les
    #: scénarios 2 à 6. Oui aussi pour l'assurance chômage, mais pour une autre
    #: raison : une année de chômage indemnisé ne verse rien au compte
    #: (``carriere.PERIODES_NON_COTISEES``), alors qu'un système notionnel réel
    #: pourrait créditer ce que l'Unédic paie, qui est une cotisation assise
    #: sur l'allocation. Tant que le modèle ne le fait pas, la recette suit le
    #: droit.
    droit_supprime: bool
    #: Sa recette arrive-t-elle par l'impôt plutôt que par un transfert ? Vrai
    #: du seul fonds de solidarité vieillesse : ce qu'il verse aux régimes est
    #: financé par la CSG, et cette CSG est DÉJÀ dans le poste « impôts et
    #: taxes affectés » des ressources. Retirer le poste en entier et retirer
    #: ce versement retirerait donc la même somme deux fois ; ``cout.py`` s'en
    #: sert pour ne la retirer qu'une.
    recette_par_impot: bool = False


POSTES_TRANSFERTS: tuple[PosteTransfert, ...] = (
    PosteTransfert(
        "cnaf_avpf", "famille", "Assurance vieillesse des parents au foyer",
        "Les cotisations que la branche famille verse à la Cnav pour les "
        "parents qui ont réduit ou cessé leur activité pour élever un enfant : "
        "des trimestres et un salaire portés au compte, sans cotisation de "
        "l'assuré.",
    ),
    PosteTransfert(
        "cnaf_majorations", "famille", "Majorations de pension pour enfants",
        "Les 10 % de pension en plus des parents de trois enfants, que la "
        "branche famille rembourse en totalité aux régimes depuis 2011.",
    ),
    PosteTransfert(
        "unedic_agirc_arrco", "chomage", "Points Agirc-Arrco des chômeurs",
        "Ce que l'assurance chômage verse à l'Agirc-Arrco pour que les "
        "périodes de chômage indemnisé ouvrent des points de retraite "
        "complémentaire (l'Agirc et l'Arrco séparément avant 2019).",
    ),
    PosteTransfert(
        "unedic_ircantec", "chomage", "Points Ircantec des chômeurs",
        "La même chose, pour les contractuels de la fonction publique.",
    ),
    PosteTransfert(
        "fsv_cotisations", "solidarite",
        "Cotisations prises en charge pour des périodes non travaillées",
        "Ce que le fonds de solidarité vieillesse verse aux régimes pour que "
        "le chômage indemnisé, la maladie, l'apprentissage, le service "
        "national et les stages de formation ouvrent des trimestres : des "
        "droits acquis sans qu'aucune cotisation ait été prélevée sur un "
        "revenu.",
    ),
    PosteTransfert(
        "fsv_prestations", "solidarite",
        "Minimum vieillesse, et le minimum contributif jusqu'en 2015",
        "Ce que le même fonds verse pour les prestations qui ne dépendent pas "
        "de ce qui a été cotisé : le minimum vieillesse, et le minimum "
        "contributif de 2011 à 2015. C'est ce second financement, éteint "
        "depuis, qui fait doubler cette ligne avant 2016.",
    ),
)

CODES_TRANSFERTS = tuple(poste.code for poste in POSTES_TRANSFERTS)

ORGANISMES: tuple[Organisme, ...] = (
    Organisme(
        "famille", "Branche famille",
        "La CNAF paie les droits à retraite liés aux enfants. Le compte "
        "notionnel du dépôt ne sert plus ces droits : il ne peut pas compter "
        "cette recette comme la sienne.",
        True,
    ),
    Organisme(
        "chomage", "Assurance chômage",
        "L'Unédic paie les points de retraite complémentaire des chômeurs "
        "indemnisés. Le compte notionnel du dépôt ne porte rien au compte "
        "pendant une année de chômage : cette recette non plus n'est pas la "
        "sienne, tant qu'il ne crédite pas ce que l'Unédic verse.",
        True,
    ),
    Organisme(
        "solidarite", "Fonds de solidarité vieillesse",
        "Le fonds finance par la CSG deux choses, et deux seulement : des "
        "trimestres pour des périodes non travaillées, et le minimum "
        "vieillesse. Aucun scénario notionnel ne sert l'un ni l'autre — la "
        "garantie vieillesse qui remplace le second est financée à part, hors "
        "du compte des cotisants. Ce fonds échappait à la règle parce que sa "
        "recette n'arrive pas par un transfert mais par l'impôt : elle est "
        "dans le poste « impôts et taxes affectés », dont elle fait 38 % en "
        "2024. Il est supprimé au 1er janvier 2026, ses missions et son "
        "financement passant à la CNAV ; la série s'arrête donc à 2025, et la "
        "part constante prend le relais, ce qui est exact puisque les "
        "missions, elles, continuent.",
        True,
        recette_par_impot=True,
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
        # En MILLIONS d'euros, l'unité des rapports à la CCSS : c'est le PIB
        # qui les ramène à l'unité du reste du compte.
        self.transferts: dict[str, SerieAnnuelle] = {
            poste.code: charger_serie_annuelle(
                macro / "transferts_retraite.csv", "montant_meur",
                nom=f"transferts_{poste.code}", filtre={"poste": poste.code},
            )
            for poste in POSTES_TRANSFERTS
        }
        self.pib = charger_serie_annuelle(
            macro / "pib_courant.csv", "pib_meur", nom="pib_courant")
        # La dette de TOUTES les administrations publiques, au sens de
        # Maastricht, en part de PIB : ce que le pays porte déjà. Elle ne sert
        # à aucun calcul ; la page Coût pose dessus le stock que chaque système
        # accumule, pour qu'il se lise à l'échelle.
        self.dette_publique = charger_serie_annuelle(
            macro / "dette_publique.csv", "part_pib", nom="dette_publique")

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

    # -- ce que d'autres caisses versent ----------------------------------------

    def transfert(self, code: str, annee: int) -> float:
        """Ce qu'une ligne de transfert a rapporté, en millions d'euros."""
        return self.transferts[code](annee)

    def transfert_organisme(self, organisme: str, annee: int) -> float:
        """Ce qu'un organisme a versé, en millions d'euros."""
        return sum(self.transfert(poste.code, annee)
                   for poste in POSTES_TRANSFERTS if poste.organisme == organisme)

    def transfert_part_pib(self, organisme: str, annee: int) -> float:
        """Le même versement, en part du PIB — l'unité du reste du compte."""
        return self.transfert_organisme(organisme, annee) / self.pib(annee)

    def transfert_part_ressources(self, organisme: str, annee: int) -> float:
        """Le même versement, en part des ressources de l'année.

        C'est l'unité de la structure des ressources, et ce qui permet de dire
        quelle fraction du poste « transferts » un organisme explique.
        """
        return self.transfert_part_pib(organisme, annee) / self.ressource(annee)

    def transfert_supprime_part_pib(self, annee: int,
                                    *, par_impot: bool | None = None,
                                    organisme: str | None = None) -> float:
        """Ce que le compte notionnel ne peut pas compter, en part du PIB.

        La somme des versements qui financent un droit que les scénarios
        notionnels ne servent pas. C'est ce qu'il faudrait retirer des
        ressources avant de lire leur coefficient d'équilibre.

        ``par_impot`` sépare les deux façons dont cette recette arrive : par un
        transfert d'organisme, qui est dans le poste « transferts » des
        ressources (la CNAF, l'Unédic), ou par l'impôt, qui est dans le poste
        « impôts et taxes affectés » (le fonds de solidarité vieillesse). Qui
        retire un de ces deux postes en entier doit cesser de retirer la ligne
        correspondante, sous peine de retirer la même somme deux fois.

        ``organisme`` ne garde qu'un seul payeur : c'est ce qui permet au
        tableau des postes de la page Coût d'écrire « dont branche famille »
        et « dont assurance chômage » sur la ligne des transferts, comme le
        COR le fait dans le sien.
        """
        return sum(self.transfert_part_pib(payeur.code, annee)
                   for payeur in ORGANISMES
                   if payeur.droit_supprime
                   and (par_impot is None or payeur.recette_par_impot is par_impot)
                   and (organisme is None or payeur.code == organisme))

    def recette_non_acquise(self, annee: int, *, par_impot: bool | None = None,
                            organisme: str | None = None) -> float:
        """Ce qu'un scénario notionnel doit retirer de ses ressources, en part du PIB.

        Dans la fenêtre où les quatre lignes sont connues, c'est ce que la
        branche famille et l'assurance chômage ont réellement versé. En dehors
        — avant 2013, et sur tout l'horizon projeté du COR —, c'est la même
        chose à PART CONSTANTE des ressources, celle de l'année connue la plus
        proche : personne ne projette ce que la CNAF versera en 2070, et une
        part constante est l'hypothèse qui n'en ajoute aucune autre.

        ``par_impot`` et ``organisme`` passent à ``transfert_supprime_part_pib``
        et y disent lesquels des payeurs compter.
        """
        premiere, derniere = self.premiere_annee_transferts, self.derniere_annee_transferts
        if premiere <= annee <= derniere:
            return self.transfert_supprime_part_pib(
                annee, par_impot=par_impot, organisme=organisme)
        reference = min(max(annee, premiere), derniere)
        part = (self.transfert_supprime_part_pib(
                    reference, par_impot=par_impot, organisme=organisme)
                / self.ressource(reference))
        return part * self.ressource(annee)

    # -- fenêtre des transferts --------------------------------------------------
    #
    # Les quatre lignes ne commencent ni ne finissent la même année : les
    # rapports à la CCSS ne détaillent l'Ircantec que depuis 2013, et le rapport
    # de printemps qui arrête la dernière année ne porte pas les fiches des
    # régimes complémentaires. La fenêtre commune est celle où les QUATRE sont
    # connues, et elle se lit dans les séries.

    @property
    def premiere_annee_transferts(self) -> int:
        return max(serie.premiere_annee for serie in self.transferts.values())

    @property
    def derniere_annee_transferts(self) -> int:
        return min(serie.derniere_annee for serie in self.transferts.values())

    def annees_transferts(self) -> list[int]:
        return list(range(self.premiere_annee_transferts,
                          self.derniere_annee_transferts + 1))

    def fiabilite(self, annee: int) -> Fiabilite:
        return min(self.depenses.fiabilite(annee), self.ressources.fiabilite(annee))
