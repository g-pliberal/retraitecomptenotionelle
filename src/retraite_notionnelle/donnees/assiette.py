"""Sur quoi l'on prélève : l'assiette des revenus d'activité.

Le reste du dépôt travaille en RAPPORTS — de masses de pension, de cotisations
—, parce qu'un rapport est robuste : les erreurs de niveau se retrouvent des
deux côtés et s'annulent. Ce module porte la grandeur que le rapport ne donne
pas, et dont on ne peut pas se passer ici : le NIVEAU de ce sur quoi un taux de
cotisation s'applique.

POURQUOI IL LA FAUT
--------------------
Un rapport de taux LÉGAUX appliqué à des ressources OBSERVÉES transporte avec
lui la structure de son dénominateur, exonérations comprises : il prête au taux
de la proposition la même déperdition qu'au système actuel. Or le système
actuel n'encaisse pas son taux légal. L'allègement général de l'article
L. 241-13 du code de la sécurité sociale réduit d'un coup huit prélèvements
patronaux, dont la vieillesse de base et l'Agirc-Arrco, et l'État compense par
l'impôt : ce que la caisse perd d'un côté lui revient de l'autre, sous un autre
nom. Avec l'assiette en niveau, on n'a plus à le deviner — on le mesure. En
2024, le système encaisse 32,4 points d'assiette de ressources, dont 24,9 de
cotisations, là où le taux légal d'un salarié type est de 28 à 29 %.

LES DEUX POSTES
----------------
``salaires_bruts`` est l'assiette des salariés : c'est sur le salaire brut que
les deux parts de la cotisation sont calculées, et c'est aussi sur le traitement
que l'État verse sa contribution d'équilibre. ``revenu_mixte`` est celle des
non-salariés. Les additionner suppose que l'on tienne le revenu mixte pour un
revenu du TRAVAIL, ce qu'il n'est qu'en partie : il rémunère aussi le capital de
l'entrepreneur individuel. Le compte national ne les sépare pas, l'assiette
sociale non plus, et la convention est donc celle des deux.

CE QUE LE TAUX DE PRÉLÈVEMENT SERT À FAIRE
-------------------------------------------
Rapporter les ressources du système de retraite à cette assiette donne le taux
de prélèvement global : 32,4 % en 2024, remarquablement stable depuis 2016. Ce
taux est ce qui permet de passer d'un TAUX AFFICHÉ à une RECETTE — la
proposition prélève 18 %, et 18 % d'une assiette connue est un montant, non un
rapport.

AU-DELÀ DE LA DERNIÈRE ANNÉE PUBLIÉE, LE TAUX EST LU ET NON SUPPOSÉ
--------------------------------------------------------------------
Ce module ne sait mesurer le taux que sur une année où l'assiette existe. Ce
qu'il devient ensuite décide pourtant de tout : les ressources du COR reculent
en part de PIB sur l'horizon projeté, et ce recul se partage entre un taux qui
baisse et une assiette qui rétrécit, sans que les deux colonnes du compte
disent lequel.

Le dépôt a tranché par déduction jusqu'au 20 septembre 2026, et à l'envers. Il
reconduisait le taux du bord, faisant porter tout le recul à l'assiette : 42,5 %
du PIB en 2025, 39,3 % en 2070 — une déformation du partage de la valeur
ajoutée que `hypotheses_projection.yaml` s'interdit explicitement par ailleurs.
Il s'en justifiait en disant que « c'est le COR qui tranche ». Le COR tranche en
effet, et dans l'autre sens : sa figure des déterminants des ressources projette
un TAUX qui baisse, de 32,14 % en 2025 à 30,05 % en 2070, et une assiette qui
tient sa part de PIB. Cette série est désormais lue
(`taux_prelevement_retraite.csv`), et c'est `ComptesRetraite.profil_taux` qui
dit ce que le dépôt lui emprunte : sa FORME, jamais son niveau.
"""

from __future__ import annotations

from pathlib import Path

from .chargement import Fiabilite, SerieAnnuelle, charger_serie_annuelle

#: Les deux postes du fichier, dans l'ordre d'affichage.
POSTES_ASSIETTE: tuple[tuple[str, str], ...] = (
    ("salaires_bruts", "Salaires et traitements bruts"),
    ("revenu_mixte", "Revenu mixte des ménages"),
)


class AssietteActivite:
    """L'assiette des revenus d'activité, en euros et en part du PIB."""

    def __init__(self, racine: Path) -> None:
        macro = racine / "reference" / "macro"
        self.postes: dict[str, SerieAnnuelle] = {
            code: charger_serie_annuelle(
                macro / "assiette_activite.csv", "montant_meur",
                nom=f"assiette_{code}", filtre={"poste": code},
            )
            for code, _ in POSTES_ASSIETTE
        }
        self.pib = charger_serie_annuelle(
            macro / "pib_courant.csv", "pib_meur", nom="pib_courant"
        )

    @property
    def premiere_annee(self) -> int:
        return max(serie.premiere_annee for serie in self.postes.values())

    @property
    def derniere_annee(self) -> int:
        """Dernière année où les DEUX postes et le PIB sont publiés.

        Les trois séries ne s'arrêtent pas forcément ensemble, et une assiette
        amputée d'un de ses postes ne serait pas une assiette.
        """
        return min(
            min(serie.derniere_annee for serie in self.postes.values()),
            self.pib.derniere_annee,
        )

    def poste(self, code: str, annee: int) -> float:
        """Un poste de l'assiette, en millions d'euros courants."""
        return self.postes[code](annee)

    def montant(self, annee: int) -> float:
        """L'assiette entière, en millions d'euros courants."""
        return sum(serie(annee) for serie in self.postes.values())

    def part_pib(self, annee: int) -> float:
        """L'assiette rapportée au PIB de la même année."""
        pib = self.pib(annee)
        return self.montant(annee) / pib if pib else 0.0

    def annee_de_reference(self, annee: int) -> int:
        """L'année dont le taux de prélèvement vaut pour ``annee``.

        Elle-même tant que l'assiette est publiée, la dernière publiée ensuite.
        Ce détour existe pour une raison précise : ``SerieAnnuelle`` reconduit
        la valeur du bord, or reconduire un MONTANT en euros courants de 2025
        jusqu'en 2070 ne veut rien dire. C'est le TAUX qui est reconduit, et
        l'assiette s'en déduit.
        """
        return min(annee, self.derniere_annee)

    def taux_prelevement(self, ressources_part_pib: float, annee: int) -> float:
        """Ce que le système prélève, rapporté à l'assiette de la MÊME année.

        Les deux termes sont en part du PIB : le rapport est sans dimension, et
        c'est lui qui convertit un taux affiché en recette. ``annee`` doit être
        une année où l'assiette est publiée — voir :meth:`annee_de_reference`.

        CE QUE CETTE MÉTHODE NE FAIT PAS, ET NE DOIT PAS FAIRE. Elle ne
        projette rien. Reconduire ce taux tel quel au-delà de la fenêtre
        publiée reviendrait à supposer que tout le recul des ressources du COR
        vient de l'assiette, ce que sa propre projection dément — voir
        l'en-tête du module. Le prolongement est le travail de
        ``ComptesRetraite.profil_taux``, qui lit la trajectoire chez le
        producteur ; ici, on mesure une année, et une année seulement.
        """
        part = self.part_pib(annee)
        return ressources_part_pib / part if part else 0.0

    def fiabilite(self, annee: int) -> Fiabilite:
        niveaux = [serie.fiabilite(annee) for serie in self.postes.values()]
        niveaux.append(self.pib.fiabilite(annee))
        return min(niveaux)
