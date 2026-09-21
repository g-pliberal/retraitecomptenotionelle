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

CE QUE LE TAUX DE PRÉLÈVEMENT SERT À DIRE
------------------------------------------
Les ressources reculent en part de PIB sur l'horizon projeté — 13,95 % en 2025,
12,91 % en 2070. Les deux colonnes du compte ne disent pas POURQUOI, et la
réponse décide de ce qu'un taux unique rapporterait : la proposition prélève
18 % d'une assiette, et cette assiette est le quotient des ressources par le
taux. Tout ce que le taux ne porte pas, l'assiette le porte.

Le dépôt gelait ce taux au-delà de sa fenêtre de mesure, et faisait donc
tomber son assiette de 42,5 % du PIB à 39,3 %. Le COR publie la série, dans la
figure des déterminants de ses ressources, et elle dit l'inverse : le TAUX
baisse, de 32,14 % à 30,05 %, et l'assiette tient sa part de PIB. ``profil_taux``
dit ce que le dépôt lui emprunte — la forme, jamais le niveau, les deux
définitions d'assiette ne coïncidant pas à 2 % près.
"""

from __future__ import annotations

import csv
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


def variantes_disponibles(macro: Path) -> tuple[str, ...]:
    """Les variantes que ``comptes_retraite_variantes.csv`` porte, dans l'ordre.

    Lues dans le fichier et jamais écrites ici : le rapport suivant du COR peut
    en ajouter une, et une liste en dur la rendrait invisible. Le fichier est
    produit par ``scripts/verifier_donnees.py`` depuis les noms que
    ``hypotheses_projection.yaml`` déclare.
    """
    chemin = macro / "comptes_retraite_variantes.csv"
    if not chemin.exists():
        return ()
    vues: dict[str, None] = {}
    with chemin.open(encoding="utf-8") as flux:
        lignes = (ligne for ligne in flux if not ligne.lstrip().startswith("#"))
        for enregistrement in csv.DictReader(lignes):
            nom = enregistrement.get("variante")
            if nom:
                vues[nom] = None
    return tuple(sorted(vues))


#: Le nom du scénario de référence du COR, sous lequel le compte principal est
#: publié. Ce n'est pas une variante : c'est le fichier ``comptes_retraite.csv``
#: lui-même, et ``comptes_retraite_variantes.csv`` ne le porte pas.
VARIANTE_REFERENCE = "reference"


def variante_du_scenario(scenario: str | None, macro: Path) -> str:
    """La variante de compte que réclame un scénario de projection.

    LE RAPPROCHEMENT SE LIT DANS LE FICHIER, ET NON DANS UNE TABLE. Les noms
    de variantes de ``comptes_retraite_variantes.csv`` SONT les noms de
    scénarios de ``hypotheses_projection.yaml`` — c'est
    ``scripts/verifier_donnees.py`` qui les y écrit. Un scénario qui n'y figure
    pas est donc, par construction, celui sous lequel le compte principal est
    publié : le scénario de référence, qui n'a pas de variante parce qu'il est
    le fichier.

    Elle tolère qu'aucune variante ne soit disponible — le fichier peut ne pas
    avoir encore été produit — et rend alors la référence : le dépôt retrouve
    exactement le comportement qu'il avait avant ce fichier, plutôt que de
    refuser de calculer.
    """
    if scenario and scenario in variantes_disponibles(macro):
        return scenario
    return VARIANTE_REFERENCE


class ComptesRetraite:
    """Le compte du système de retraite : dépenses, ressources, solde, structure.

    Tout y est en PART DE PIB, parce que c'est ainsi que le COR le publie et
    que c'est la seule unité où une dépense de 2002 et une projection de 2070
    se comparent sans convention d'actualisation. Les euros s'en déduisent en
    multipliant par le PIB de l'année — ce que la page ne fait que sur les
    années où le PIB est publié, faute de quoi elle afficherait des milliards
    de 2070 qui ne seraient qu'une hypothèse de croissance déguisée.
    """

    def __init__(self, racine: Path,
                 variante: str = VARIANTE_REFERENCE) -> None:
        macro = racine / "reference" / "macro"
        chemin = macro / "comptes_retraite.csv"
        #: La variante du COR sous laquelle ce compte est lu. Voir
        #: ``_charger_variante`` pour ce qu'elle déplace, et ce qu'elle ne
        #: déplace pas.
        self.variante = variante
        self.depenses = charger_serie_annuelle(
            chemin, "part_pib", nom="comptes_retraite_depenses",
            filtre={"poste": "depenses"},
        )
        self.ressources = charger_serie_annuelle(
            chemin, "part_pib", nom="comptes_retraite_ressources",
            filtre={"poste": "ressources"},
        )
        self.depenses_variante, self.ressources_variante = self._charger_variante(macro)
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
        # Le taux de prélèvement du système, en part des REVENUS D'ACTIVITÉ et
        # non du PIB. C'est la seule série du compte qui dise pourquoi les
        # ressources reculent en part de PIB : parce que le taux baisse, et non
        # parce que l'assiette rétrécit. ``profil_taux`` dit ce qu'on en prend.
        self.taux_prelevement = charger_serie_annuelle(
            macro / "taux_prelevement_retraite.csv", "taux",
            nom="taux_prelevement_retraite")
        # Les mêmes ressources sous l'AUTRE convention comptable du COR, toutes
        # années au niveau projeté : ``ressource_eec`` dit ce qu'elle est.
        self.ressources_eec = charger_serie_annuelle(
            macro / "ressources_eec_retraite.csv", "part_pib",
            nom="ressources_eec_retraite")
        # Les droits à pension ACQUIS À DATE, en part de PIB : le stock, là où
        # tout le reste de ce module est un flux. Trois transmissions, tous les
        # trois ans ; ``engagements`` dit ce qu'on en retient.
        self.engagements_acquis: dict[str, SerieAnnuelle] = {
            regime: charger_serie_annuelle(
                macro / "engagements_retraite.csv", "part_pib",
                nom=f"engagements_{regime}", filtre={"regime": regime},
                # PONCTUELLE, et la raison est dans la périodicité : le tableau
                # supplémentaire est transmis tous les TROIS ANS, si bien que
                # deux années sur trois n'ont pas été mesurées. Les dire au
                # niveau du producteur ferait de 2016 une transmission.
                interpolation="ponctuelle",
            )
            for regime in ("tous_regimes", "repartition")
        }
        self.pib = charger_serie_annuelle(
            macro / "pib_courant.csv", "pib_meur", nom="pib_courant")
        # La dette de TOUTES les administrations publiques, au sens de
        # Maastricht, en part de PIB : ce que le pays porte déjà. Elle ne sert
        # à aucun calcul ; la page Coût pose dessus le stock que chaque système
        # accumule, pour qu'il se lise à l'échelle.
        self.dette_publique = charger_serie_annuelle(
            macro / "dette_publique.csv", "part_pib", nom="dette_publique")

    # -- la variante ------------------------------------------------------------

    def _charger_variante(
        self, macro: Path,
    ) -> tuple[SerieAnnuelle | None, SerieAnnuelle | None]:
        """Les deux séries de la variante demandée, ou deux ``None``.

        CE QU'UNE VARIANTE DÉPLACE. La DÉPENSE et la RESSOURCE du système, sur
        les seules années projetées, telles que le COR les republie dans ses
        figures de sensibilité — même convention, même champ que le compte
        principal. C'est ce qui manquait : le dépôt lisait le scénario de
        référence quel que soit le scénario demandé, si bien que la croissance
        déplaçait la dépense de ses systèmes notionnels, qui est calculée, sans
        déplacer celle du droit en vigueur, qui est empruntée.

        CE QU'ELLE NE DÉPLACE PAS, ET IL FAUT LE SAVOIR AVANT DE LIRE UN
        COEFFICIENT. Le taux de prélèvement, que le COR ne projette que dans
        son scénario de référence : ``profil_taux`` garde donc la même forme
        sous toutes les variantes. La structure des ressources, publiée elle
        aussi pour la seule référence, donc la part contributive et les parts
        de postes. Les ressources sous convention EEC, dont le bloc ne porte
        que la dimension de productivité. Et les transferts, que personne ne
        projette dans aucun scénario. Ces quatre réserves empruntent à la
        référence des FORMES et jamais des niveaux : ce sont des rapports, et
        c'est ce qui les rend transportables.

        LES ANNÉES OBSERVÉES NE SONT JAMAIS CELLES D'UNE VARIANTE. Le fichier
        n'en porte aucune, et ``depense``/``ressource`` retombent donc sur le
        compte principal partout avant la première année projetée : ce que le
        passé a été ne dépend d'aucune hypothèse.
        """
        if self.variante == VARIANTE_REFERENCE:
            return None, None
        chemin = macro / "comptes_retraite_variantes.csv"
        try:
            return tuple(
                charger_serie_annuelle(
                    chemin, "part_pib",
                    nom=f"comptes_variante_{self.variante}_{poste}",
                    filtre={"poste": poste, "variante": self.variante},
                )
                for poste in ("depenses", "ressources")
            )
        except ValueError as erreur:
            # Un nom de variante inconnu ne doit pas retomber en silence sur la
            # référence : il rendrait deux courbes identiques sans que rien ne
            # le dise, ce qui est exactement le défaut qu'on répare ici. Le
            # chargeur refuse déjà ; on ne fait que nommer les variantes que le
            # fichier porte, pour que le message dise quoi écrire à la place.
            raise ValueError(
                f"variante de compte inconnue : {self.variante!r} — "
                f"{chemin.name} porte {', '.join(variantes_disponibles(macro))}"
            ) from erreur

    def _sous_variante(self, serie: SerieAnnuelle | None, annee: int) -> float | None:
        """La valeur de la variante pour ``annee``, ou ``None`` hors de sa fenêtre.

        La borne est lue dans la série et non écrite ici : le rapport suivant
        décalera d'un an la frontière entre l'observé et le projeté, et le
        fichier le dira tout seul.
        """
        if serie is None or not (serie.premiere_annee <= annee <= serie.derniere_annee):
            return None
        return serie(annee)

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
        variante = self._sous_variante(self.depenses_variante, annee)
        return self.depenses(annee) if variante is None else variante

    def ressource(self, annee: int) -> float:
        variante = self._sous_variante(self.ressources_variante, annee)
        return self.ressources(annee) if variante is None else variante

    def solde(self, annee: int) -> float:
        """Ressources moins dépenses, en part de PIB. Négatif : besoin de financement.

        Le solde n'est pas stocké : il est la différence de deux séries écrites,
        et ``scripts/verifier_donnees.py`` confronte cette différence au solde
        que le COR publie séparément.

        Il passe par ``ressource`` et ``depense``, et non par les deux séries :
        sous une variante, c'est le seul chemin qui rende le solde de CETTE
        variante. Le prendre aux séries redonnerait celui de la référence.
        """
        return self.ressource(annee) - self.depense(annee)

    @property
    def premiere_annee_eec(self) -> int:
        return self.ressources_eec.premiere_annee

    @property
    def derniere_annee_eec(self) -> int:
        return self.ressources_eec.derniere_annee

    def ressource_eec(self, annee: int) -> float:
        """Les ressources sous la convention EEC, en part de PIB.

        CE QU'UNE CONVENTION DÉCIDE, ET QUE LE RESTE DU DÉPÔT TAIT. Tout ce que
        ce module porte est sous convention **EPR** : les contributions et
        subventions d'équilibre y « évoluent de manière à équilibrer chaque
        année le solde » des régimes de fonctionnaires et des régimes spéciaux.
        L'État y verse exactement ce qu'il faut, ces régimes ne montrent jamais
        de déficit, et le solde publié est donc celui des AUTRES régimes — un
        déficit d'après bouclage, et non d'avant.

        Sous **EEC**, l'effort de l'État est figé en part de PIB. Le COR publie
        les deux ; le dépôt calcule sous la première, qui est celle de son
        objectif de pérennité financière, et lit la seconde pour dire ce que le
        choix vaut.

        IL VAUT JUSQU'À 0,67 POINT DE PIB, ET IL CHANGE DE SIGNE. EEC donne
        moins de ressources à court terme — l'effort figé est sous le besoin
        tant que les régimes de fonctionnaires pèsent —, passe au-dessus en
        2047, et rend 0,49 point de plus en 2069. Sur toute la fenêtre
        projetée, les deux moyennes ne diffèrent pas de deux centièmes de
        point : aucune des deux conventions ne flatte, elles déplacent le
        déficit dans le temps.
        """
        return self.ressources_eec(annee)

    def solde_eec(self, annee: int) -> float:
        """Le solde sous la convention EEC : les mêmes dépenses, l'autre recette.

        La convention ne touche qu'aux ressources — ce que l'État verse —, et
        jamais aux pensions servies. Retrancher les dépenses du compte
        principal est donc exact, et non un mélange de deux périmètres.
        """
        return self.ressources_eec(annee) - self.depenses(annee)

    def annees_engagements(self) -> list[int]:
        """Les années transmises, et elles seules : une tous les trois ans.

        ``annees()`` ne rend que les années ÉCRITES, et c'est ce qu'il faut :
        la série n'en porte que trois, et balayer de la première à la dernière
        en inventerait quatre, chacune reconduisant la transmission
        précédente — un engagement de 2021 n'est pas celui de 2022. Le filtre
        sur la fiabilité ne retire donc rien aujourd'hui ; il est là pour le
        jour où une valeur estimée s'y glisserait, et le portage JavaScript
        fait exactement le même geste sur le même tableau d'années.
        """
        serie = self.engagements_acquis["tous_regimes"]
        return [annee for annee in serie.annees()
                if serie.fiabilite(annee) > Fiabilite.ESTIMEE]

    def engagements(self, annee: int, regime: str = "tous_regimes") -> float:
        """Les droits à pension acquis à date, en part de PIB.

        LE STOCK, ET NON LE FLUX. Tout le reste de ce module dit ce qui rentre
        et ce qui sort dans l'année. Ceci dit ce que le système DOIT DÉJÀ, au
        titre des droits que les vivants ont acquis : près de quatre années de
        production, contre quatorze pour-cent de PIB de dépense annuelle.

        CE QU'ON EN RETIENT EST L'ORDRE DE GRANDEUR, ET RIEN DE PLUS. Les trois
        transmissions donnent 368 %, 431 % puis 397 % du PIB. Un droit acquis à
        date est une somme actualisée, et soixante-trois points de PIB en trois
        ans ne sont pas des droits qui apparaissent : c'est un taux
        d'actualisation qui bouge. Le dépôt le montre pour dire que le stock
        existe et qu'il est grand, jamais comme une dette.
        """
        return self.engagements_acquis[regime](annee)

    def profil_taux(self, annee: int, reference: int) -> float:
        """Ce que le taux de prélèvement de ``annee`` vaut, rapporté à celui de
        ``reference``.

        LE PROFIL, ET JAMAIS LE NIVEAU. Le COR projette son taux de prélèvement
        sur les revenus d'activité ; le dépôt mesure le sien sur l'assiette
        qu'il certifie — salaires et traitements bruts plus revenu mixte —, et
        les deux définitions ne coïncident pas : 32,14 % contre 32,84 % en
        2025, soit 2 % d'écart. Emprunter le NIVEAU du COR déplacerait la
        recette de la proposition de 2 % sans que rien ne le dise ; emprunter
        son RAPPORT d'une année à l'autre n'emprunte que ce que lui seul sait,
        c'est-à-dire la FORME de la trajectoire.

        Vaut un quand les deux années sont la même, ce qui est le cas de toutes
        les années où l'assiette est publiée : rien ne change alors sur les
        années observées, et c'est voulu — elles sont mesurées, pas projetées.
        """
        base = self.taux_prelevement(reference)
        return self.taux_prelevement(annee) / base if base else 1.0

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
