"""La fraction de TVA que l'Agirc-Arrco reçoit pour la réduction générale.

La réduction générale de cotisations patronales efface, au voisinage du SMIC,
les cotisations de retraite complémentaire comme celles des régimes de base.
L'Urssaf en compense l'Agirc-Arrco « à l'euro près », par une fraction de TVA
qui lui est affectée pour cela (rapport à la Commission des comptes de la
sécurité sociale d'octobre 2026, synthèse, p. 15). C'est « la part existante »
de TVA que la décision 79 du programme garde aux retraites
(``docs/feuille_de_route_programme.md``) ; le régime général n'en reçoit
aucune pour la retraite.

AUCUNE SOURCE LUE N'EN PUBLIE LE MONTANT pour l'Agirc-Arrco seule. Le rapport
publie ce que la réduction efface hors des régimes de base — assurance
chômage, retraite complémentaire, FNAL — (fiche 1.6, tableau 2, p. 67 :
``allegements_hors_regimes_de_base.csv``). La part de l'Agirc-Arrco s'en
déduit par les taux que la réduction efface : c'est un CALCUL, que
:meth:`CompensationAgircArrco.montant` pose, et non une lecture.

CE QUE LE CALCUL NE SAIT PAS. Les 10,2 points sont ceux d'une entreprise de
moins de cinquante salariés, où le FNAL vaut 0,10 point ; il en vaut 0,50
au-delà, et la part de l'Agirc-Arrco tombe alors de 0,59 à 0,57. Le même
rapport publie l'effet de la réduction unique de 2026 sur ses cotisations,
3,8 Md€, que le saut de la série recoupe à 0,1 près
(``tests/test_compensation_agirc_arrco.py``). Et la TVA ne paie pas toute la
compensation : le régime général a complété de 1,0 Md€ en 2025, Unédic
comprise.

Rien du coût ne lit encore cette série : la porter au scénario 6 est l'étape
suivante du chantier (note ``docs/feuille_de_route/186/2026-11-09-recettes-au-modele.md``).
"""

from __future__ import annotations

from pathlib import Path

from .chargement import SerieAnnuelle, charger_serie_annuelle

#: Ce que l'employeur doit à l'Agirc-Arrco sous le plafond de la sécurité
#: sociale, et que la réduction générale efface : 4,72 points de cotisation
#: (60 % des 7,87 points de la tranche 1) et 1,29 de contribution d'équilibre
#: général (60 % de 2,15).
POINTS_AGIRC_ARRCO: float = 4.72 + 1.29

#: Ce que la réduction générale efface hors des régimes de base : les 6,01
#: points de l'Agirc-Arrco, la contribution patronale d'assurance chômage
#: (4,05 points, 4,00 depuis le 1er mai 2025) et le FNAL (0,10 point sous
#: cinquante salariés). La convention de la note du 9 novembre 2026.
POINTS_HORS_REGIMES_DE_BASE: float = 10.2

#: Les trois lignes du tableau publié.
POSTES: tuple[str, ...] = ("regimes_de_base", "hors_regimes_de_base", "ensemble")


class CompensationAgircArrco:
    """Ce que la réduction générale efface, et ce que l'Agirc-Arrco en reçoit.

    En millions d'euros courants, sur les seules années que le rapport
    publie : une année hors de la fenêtre lève ``KeyError``, et qui projette
    la série dit sa convention.
    """

    def __init__(self, racine: Path) -> None:
        chemin = racine / "reference" / "macro" / "allegements_hors_regimes_de_base.csv"
        self._series: dict[str, SerieAnnuelle] = {
            poste: charger_serie_annuelle(
                chemin, "montant_meur", nom=f"allegements_{poste}",
                interpolation="ponctuelle", filtre={"poste": poste},
            )
            for poste in POSTES
        }

    @property
    def premiere_annee(self) -> int:
        return self._series["hors_regimes_de_base"].premiere_annee

    @property
    def derniere_annee(self) -> int:
        return self._series["hors_regimes_de_base"].derniere_annee

    def allegements(self, annee: int, poste: str = "hors_regimes_de_base") -> float:
        """Ce que la réduction générale efface, tel que le rapport le publie."""
        if not self.premiere_annee <= annee <= self.derniere_annee:
            raise KeyError(f"le rapport ne publie pas les allègements de {annee}")
        return self._series[poste](annee)

    def montant(self, annee: int) -> float:
        """La compensation de l'Agirc-Arrco, que la TVA paie : un calcul.

        La part de ses taux dans ce que la réduction efface hors des régimes
        de base, appliquée au montant publié.
        """
        return (self.allegements(annee) * POINTS_AGIRC_ARRCO
                / POINTS_HORS_REGIMES_DE_BASE)
