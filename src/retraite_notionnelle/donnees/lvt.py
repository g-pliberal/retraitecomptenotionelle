"""Ce que rapporte une taxe sur la valeur du terrain (LVT), capitalisation comprise.

LA DÉCISION. Le programme remplace la taxe foncière par une taxe annuelle sur
la valeur du terrain, à 2 %, dont un point va aux retraites et l'autre aux
communes, à la place de la taxe foncière (décisions 9 et 80 de
``docs/feuille_de_route_programme.md``, action 186). Elle entre en vigueur
dans les mois qui suivent le vote (décision 81) : le coût la compte dès la
bascule. L'étude est ``docs/feuille_de_route/186/2026-11-07-recettes-tva-lvt.md``.

L'ASSIETTE
-----------
Les terrains bâtis des ménages et des sociétés, 6 091 Md€ fin 2025 (Insee,
patrimoine national, ``patrimoine_immobilier.csv``). Ceux des administrations
publiques, qui ne paient pas la taxe foncière, n'en sont pas ; les terres
agricoles non plus, que l'Insee ne publie pas à part.

LE CALCUL
----------
Une taxe annuelle sur le terrain se capitalise : l'offre de terrain ne bouge
pas, et l'acheteur déduit du prix la taxe qu'il paiera à jamais. Avec un loyer
du terrain R, avant taxe foncière, et un prix P₀ d'aujourd'hui, le rendement
locatif est y = R / P₀. Ce prix contient déjà la taxe foncière, τ₀ : son
produit rapporté à tout l'immobilier privé, terrains et bâti, 0,32 %.
Remplacer τ₀ par une LVT au taux t porte le prix à

    P₁ = P₀ × y / (y − τ₀ + t),

et le produit de la taxe est t × P₁ : 78 Md€ à 2 % pour un rendement de 3 %,
quand 2 % de l'assiette d'aujourd'hui feraient 122 Md€.

LA CONVENTION DE PROJECTION
----------------------------
Le produit garde sa part de PIB de l'année des terrains : la convention du
dépôt pour ce qu'il ne sait pas projeter. Elle suppose que le prix des
terrains suit la production, quand il a baissé de 11 % de 2022 à 2024.

CE QUE CE CHIFFRAGE NE COMPTE PAS
----------------------------------
* le RENDEMENT LOCATIF du terrain n'est pas mesuré : l'étude le prend de
  2,5 à 4 %, et le coût à 3 % (``Parametres.rendement_locatif_terrain``) ; le
  point des retraites vaut 1,2 à 1,4 point de PIB selon lui ;
* la capitalisation est supposée COMPLÈTE ET IMMÉDIATE, et la valeur du bâti,
  qui n'est plus taxé, n'est pas recalculée ;
* AUCUN ABATTEMENT sur la résidence principale, aucune exonération, aucun
  plafonnement au revenu, que le Conseil constitutionnel exigerait
  (décision 2012-654 DC), et un recouvrement complet : le propriétaire a remis
  l'abattement et le plafonnement à plus tard, et tous deux baisseraient le
  produit ;
* la taxe foncière retranchée comprend le non-bâti, quand les terres
  agricoles ne sont pas dans l'assiette.
"""

from __future__ import annotations

from pathlib import Path

from .chargement import Fiabilite, charger_serie_annuelle, charger_table_csv
from ..somme import somme_ordonnee

#: Les secteurs dont les terrains paient la taxe : tous, hors administrations
#: publiques.
SECTEURS_TAXES: tuple[str, ...] = (
    "menages", "societes_non_financieres", "societes_financieres",
)
#: Ce qui fait l'immobilier : le bâti, et le terrain qui le porte.
ACTIFS_IMMOBILIERS: tuple[str, ...] = ("logements", "autres_batiments", "terrains_batis")
ACTIF_TERRAIN = "terrains_batis"


class TaxeTerrain:
    """L'assiette d'une taxe sur la valeur du terrain, et ce qu'elle rapporte."""

    def __init__(self, racine: Path) -> None:
        macro = racine / "reference" / "macro"
        valeurs, fiabilites = charger_table_csv(
            macro / "patrimoine_immobilier.csv", ("annee", "secteur", "actif"), "valeur_mdeur")
        #: L'année du patrimoine, en fin d'année : la dernière publiée.
        self.annee = max((int(annee) for annee, _, _ in valeurs), default=0)
        #: Valeur de chaque actif de chaque secteur, en millions d'euros.
        self._valeurs: dict[tuple[str, str], float] = {
            (secteur, actif): 1000.0 * valeur
            for (annee, secteur, actif), valeur in valeurs.items() if int(annee) == self.annee
        }
        taxes, fiabilites_taxes = charger_table_csv(
            macro / "taxes_foncieres.csv", ("annee", "payeur"), "montant_meur")
        #: L'année de la taxe foncière : la dernière publiée.
        self.annee_taxe_fonciere = max((int(annee) for annee, _ in taxes), default=0)
        self._taxes: dict[str, float] = {
            payeur: montant for (annee, payeur), montant in taxes.items()
            if int(annee) == self.annee_taxe_fonciere
        }
        self._fiabilite = min(fiabilites + fiabilites_taxes, default=Fiabilite.ESTIMEE)
        self.pib = charger_serie_annuelle(
            macro / "pib_courant.csv", "pib_meur", nom="pib_courant"
        )

    def __bool__(self) -> bool:
        return bool(self._valeurs) and bool(self._taxes)

    def valeur(self, actif: str, secteur: str | None = None) -> float:
        """La valeur d'un actif, en millions d'euros de fin ``annee`` : celle
        d'un secteur, ou de l'économie nationale."""
        return somme_ordonnee(valeur for (s, a), valeur in self._valeurs.items()
                              if a == actif and secteur in (None, s))

    def assiette(self) -> float:
        """Les terrains bâtis des ménages et des sociétés, en millions d'euros."""
        return somme_ordonnee(self.valeur(ACTIF_TERRAIN, secteur) for secteur in SECTEURS_TAXES)

    def immobilier(self) -> float:
        """Tout l'immobilier des mêmes secteurs, terrains et bâti, en millions d'euros."""
        return somme_ordonnee(self.valeur(actif, secteur)
                              for secteur in SECTEURS_TAXES for actif in ACTIFS_IMMOBILIERS)

    def taxe_fonciere(self, payeur: str | None = None) -> float:
        """Le produit des taxes foncières, en millions d'euros de
        ``annee_taxe_fonciere`` : celui d'un payeur, ou de tous."""
        return somme_ordonnee(montant for p, montant in self._taxes.items()
                              if payeur in (None, p))

    def taux_actuel(self) -> float:
        """La taxe foncière rapportée à l'immobilier privé : le taux que les
        prix d'aujourd'hui contiennent déjà."""
        immobilier = self.immobilier()
        return self.taxe_fonciere() / immobilier if immobilier else 0.0

    def facteur_prix(self, taux: float, rendement: float) -> float:
        """Ce que le prix du terrain devient quand une LVT au taux ``taux``
        remplace la taxe foncière, pour un rendement locatif ``rendement`` : un
        sans LVT, moins de un dès qu'elle dépasse la taxe d'aujourd'hui."""
        if taux <= 0.0 or not self:
            return 1.0
        return rendement / (rendement - self.taux_actuel() + taux)

    def produit(self, taux: float, rendement: float) -> float:
        """Ce que la LVT rapporte, en millions d'euros de ``annee``, sur des
        terrains dont elle a fait baisser le prix. Zéro sans LVT."""
        if taux <= 0.0 or not self:
            return 0.0
        return taux * self.assiette() * self.facteur_prix(taux, rendement)

    def part_pib(self, taux_affecte: float, taux: float, rendement: float) -> float:
        """Ce que ``taux_affecte`` points d'une LVT au taux ``taux`` rapportent,
        en part du PIB de ``annee``, tenue à ce niveau ensuite : le point des
        retraites, sur les deux de la proposition."""
        pib = self.pib(self.annee) if self else 0.0
        if taux <= 0.0 or not pib:
            return 0.0
        return self.produit(taux, rendement) * (taux_affecte / taux) / pib

    @property
    def fiabilite(self) -> Fiabilite:
        return min(self._fiabilite, self.pib.fiabilite(self.annee)) if self else Fiabilite.ESTIMEE
