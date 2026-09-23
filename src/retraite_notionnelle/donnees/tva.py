"""Ce que rapporte une TVA à taux unique : l'assiette de la TVA, taux par taux.

Le Parti libéral affecte au scénario 6, depuis le 23 septembre 2026, une TVA à
TAUX UNIQUE : les quatre taux d'aujourd'hui — 20, 10, 5,5 et 2,1 % — cèdent la
place à un seul, et ce qu'il rapporte de plus va à la retraite. Ce module dit
combien, et il ne sait le dire qu'avec une donnée que personne d'autre ne
publie : l'ASSIETTE de chaque taux.

D'OÙ VIENT L'ASSIETTE
----------------------
Du modèle de la TVA théorique de la DG Trésor (Trésor-Éco n° 371, septembre
2025), qui publie ce que rapporterait en 2025 un point de plus sur chaque taux.
Un point étant un centième, l'assiette en est le centuple. Le Trésor donne le
point BRUT et le point NET ; le net retire la TVA que les administrations
publiques paient sur leurs propres achats — hôpitaux, collectivités,
médicaments remboursés —, qu'une hausse de taux leur ferait payer d'autant.
C'est le gain des finances publiques prises ensemble, et c'est lui que le
dépôt emploie : une TVA qui comblerait la retraite en creusant l'hôpital ne
comblerait rien.

CE QUE LE MODULE EN TIRE
-------------------------
Deux nombres, et tout le reste en découle :

* le TAUX MOYEN d'aujourd'hui sur l'assiette nette, Σ taux × assiette ÷ Σ
  assiette, soit 15,46 %. C'est aussi le taux unique qui rapporterait
  exactement ce que rapportent les quatre : un taux unique n'a donc pas besoin
  d'atteindre 20 % pour rapporter plus, parce qu'il supprime les taux réduits,
  qui coûtent 52 Md€ nets ;
* la PART DE PIB de cette assiette, 38,4 % en 2025.

Ce qu'un taux unique ``t`` rapporte DE PLUS est alors ``(t − taux moyen) ×
part de PIB`` : 1,63 point de PIB à 19,7 %.

LA CONVENTION DE PROJECTION
----------------------------
L'assiette garde sa part de PIB de 2025, et le taux moyen des quatre taux
d'aujourd'hui ne bouge pas. C'est la convention du reste du dépôt pour ce qu'il
ne sait pas projeter — une part de PIB, jamais un montant en euros courants —,
et elle suppose que la consommation taxée suit la production.

CE QUE CE CHIFFRAGE NE COMPTE PAS
----------------------------------
Il est STATIQUE, et le Trésor le dit de ses propres points : « hors effets
induits sur les comportements de consommation ». Quatre omissions, qu'il faut
avoir en tête avant de citer un chiffre :

* aucun effet de volume : les achats ne baissent pas quand les prix montent ;
* une répercussion intégrale et symétrique, alors que les baisses de TVA
  passent moins dans les prix que les hausses ;
* aucun effet de prix sur les dépenses indexées : à 19,7 %, l'alimentation
  prend 13,5 %, les médicaments remboursables 17,2 %, et les pensions et
  prestations qui suivent l'indice des prix suivraient ;
* les arrondis du Trésor, au dixième de milliard par taux, laissent le taux
  moyen entre 15,3 et 15,6 %.
"""

from __future__ import annotations

from pathlib import Path

from .chargement import (
    Fiabilite, charger_serie_annuelle, charger_table_csv,
)


class AssietteTva:
    """L'assiette de chaque taux de TVA, et ce qu'un taux unique en tirerait."""

    def __init__(self, racine: Path) -> None:
        macro = racine / "reference" / "macro"
        chemin = macro / "assiette_tva.csv"
        brut, fiabilites = charger_table_csv(chemin, ("annee", "taux"), "point_brut_meur")
        net, _ = charger_table_csv(chemin, ("annee", "taux"), "point_net_meur")
        annees = {int(annee) for annee, _ in net}
        #: L'année des points publiés. Une seule : le Trésor ne publie qu'un
        #: millésime, et un point ne se reconduit pas en euros courants.
        self.annee = max(annees) if annees else 0
        #: Assiette de chaque taux, en millions d'euros de ``annee`` — le
        #: centuple du point.
        self.assiettes_brutes: dict[float, float] = {
            float(taux): 100.0 * point
            for (annee, taux), point in brut.items() if int(annee) == self.annee
        }
        self.assiettes_nettes: dict[float, float] = {
            float(taux): 100.0 * point
            for (annee, taux), point in net.items() if int(annee) == self.annee
        }
        self._fiabilite = min(fiabilites, default=Fiabilite.ESTIMEE)
        self.pib = charger_serie_annuelle(
            macro / "pib_courant.csv", "pib_meur", nom="pib_courant"
        )

    def __bool__(self) -> bool:
        return bool(self.assiettes_nettes) and self.annee > 0

    def assiettes(self, nette: bool = True) -> dict[float, float]:
        """L'assiette de chaque taux, en millions d'euros de ``annee``."""
        return self.assiettes_nettes if nette else self.assiettes_brutes

    def montant(self, nette: bool = True) -> float:
        """L'assiette de tous les taux, en millions d'euros de ``annee``."""
        return sum(self.assiettes(nette).values())

    def recette(self, nette: bool = True) -> float:
        """Ce que les taux d'aujourd'hui en tirent, en millions d'euros."""
        return sum(taux * assiette for taux, assiette in self.assiettes(nette).items())

    def taux_moyen(self, nette: bool = True) -> float:
        """Le taux unique qui rapporterait exactement ce que rapportent les quatre."""
        montant = self.montant(nette)
        return self.recette(nette) / montant if montant else 0.0

    def part_pib(self, nette: bool = True) -> float:
        """L'assiette rapportée au PIB de ``annee``, et tenue à ce niveau ensuite."""
        pib = self.pib(self.annee) if self else 0.0
        return self.montant(nette) / pib if pib else 0.0

    def recette_supplementaire(self, taux_unique: float, nette: bool = True) -> float:
        """Ce qu'un taux unique rapporte DE PLUS que les quatre, en part de PIB.

        Négatif sous le taux moyen : un taux unique plus bas coûte. Zéro quand
        ``taux_unique`` est nul, qui veut dire « la TVA n'est pas réformée »
        et non « une TVA à zéro » — c'est ainsi que
        ``Parametres.taux_tva_liberal`` rend l'ancienne convention.
        """
        if taux_unique <= 0.0 or not self:
            return 0.0
        return (taux_unique - self.taux_moyen(nette)) * self.part_pib(nette)

    def variation_prix(self, taux_unique: float, taux_actuel: float) -> float:
        """Ce que le passage au taux unique fait au prix TTC, répercussion intégrale."""
        return (1.0 + taux_unique) / (1.0 + taux_actuel) - 1.0

    @property
    def fiabilite(self) -> Fiabilite:
        return min(self._fiabilite, self.pib.fiabilite(self.annee)) if self else Fiabilite.ESTIMEE
