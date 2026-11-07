"""Les réversions déjà servies à la bascule, gardées jusqu'à extinction.

LA DÉCISION. Le 7 novembre 2026, le programme garde « les réversions déjà
servies jusqu'à extinction » (décision 16 de
``docs/feuille_de_route_programme.md``), au seul scénario 6 (décision 28) :
les scénarios 2 à 5, qui montrent ce que l'on a cotisé, n'en servent aucune.
Le propriétaire a précisé, le même jour, deux lectures
(``docs/feuille_de_route/186/2026-11-07-reversion-scenario-6-plan.md``) :

- la règle se lit « décès avant la bascule : réversion du droit actuel ».
  Le scénario 6, rétroactif, sert donc toute la réversion avant la bascule,
  puisque tous ceux qui la touchent alors ont perdu leur conjoint avant elle ;
- ces réversions se revalorisent sur les prix, comme aujourd'hui.

CE QUE LE MODÈLE EN SAIT. Il ne simule pas de ménages : la réversion du droit
actuel est une masse, la dépense du COR multipliée par la part des droits
dérivés qu'il projette (``cout.masse_du_scenario``). Le stock est la masse
servie l'année qui précède la bascule ; il suit les prix, et ses
bénéficiaires meurent. Ce module dit quelle part de cette masse, en euros
constants, reste servie chaque année : la SURVIE DU STOCK, pondérée par ce
que chacun touche.

LES HYPOTHÈSES, celles du calcul de l'étude du 7 novembre (H1 à H4 de
``docs/feuille_de_route/186/2026-11-07-reversion-etude-et-couts.md``), à
une près :

- le stock a le profil par âge et par sexe des veufs de 60 ans ou plus que
  l'INSEE compte au 1er janvier (``etat_matrimonial.csv``), celui de la
  dernière année publiée — 2020 —, pris pour celui de la bascule ; les 90 ans
  ou plus, que l'INSEE ne détaille pas, s'y étalent comme les survivants
  d'une génération soumise à la mortalité de l'année du profil ;
- il meurt comme la population générale (``DonneesMortalite``), sous
  l'hypothèse d'espérance de vie du calcul ;
- les femmes touchent 91,5 % de la masse (COR, rapport de novembre 2025), là
  où l'étude posait, sans source, qu'un veuf touche 40 % de ce que touche une
  veuve ; dans chaque sexe, chacun touche autant.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .somme import somme_ordonnee

#: La part de la réversion versée à des femmes : « 38,7 Md€, soit 9,9 % des
#: pensions et 1,3 % du PIB, versés à 91,5 % à des femmes » (COR, rapport de
#: novembre 2025, cité par l'étude du 7 novembre 2026).
PART_DES_FEMMES = 0.915

#: Le fichier de l'INSEE : la population au 1er janvier par sexe, âge et état
#: matrimonial légal, de 60 à 89 ans puis 90 ans ou plus.
FICHIER_ETAT_MATRIMONIAL = Path("reference") / "macro" / "etat_matrimonial.csv"

#: La tranche ouverte de l'INSEE, et l'âge au-delà duquel plus personne ne
#: survit : le stock s'y étale, puis s'y éteint.
TRANCHE_OUVERTE = "90_plus"
AGE_DE_LA_TRANCHE_OUVERTE = 90
AGE_LIMITE = 120

SEXES = ("F", "H")


def _veufs(racine: Path, annee_au_plus: int) -> tuple[int, dict[str, dict[str, float]]]:
    """Les veufs de la dernière année publiée au plus tard ``annee_au_plus`` :
    ``(annee, sexe -> age -> effectif)``, l'âge écrit comme l'INSEE l'écrit."""
    lignes: dict[int, dict[str, dict[str, float]]] = {}
    with (racine / FICHIER_ETAT_MATRIMONIAL).open(encoding="utf-8") as flux:
        donnees = (ligne for ligne in flux if not ligne.lstrip().startswith("#"))
        for ligne in csv.DictReader(donnees):
            if ligne["etat"] != "veuf":
                continue
            annee = int(ligne["annee"])
            lignes.setdefault(annee, {}).setdefault(ligne["sexe"], {})[ligne["age"]] = (
                float(ligne["effectif"]))
    annees = [annee for annee in lignes if annee <= annee_au_plus]
    if not annees:
        raise ValueError(f"aucun veuf publié avant {annee_au_plus} dans "
                         f"{FICHIER_ETAT_MATRIMONIAL}")
    annee = max(annees)
    return annee, lignes[annee]


class StockDeReversion:
    """Ce qui reste servi, chaque année, des réversions servies à la bascule.

    ``survie(annee)`` est la part de la masse du stock, en euros constants,
    servie dans l'année : un avant la bascule, où toute réversion est encore
    du stock, puis de moins en moins. Le stock suivant les prix, c'est aussi
    la part de sa masse de départ, revalorisée sur les prix, qu'on sert.
    """

    def __init__(self, racine: Path, mortalite, annee_bascule: int) -> None:
        self.annee_bascule = annee_bascule
        self._mortalite = mortalite
        self.annee_du_profil, veufs = _veufs(racine, annee_bascule)
        #: ``(sexe, age au 1er janvier de la bascule) -> effectif``.
        self._effectifs: dict[tuple[str, int], float] = {}
        for sexe in SEXES:
            for age, effectif in veufs[sexe].items():
                if age == TRANCHE_OUVERTE:
                    for exact, part in self._etalement(sexe):
                        self._effectifs[(sexe, exact)] = effectif * part
                else:
                    self._effectifs[(sexe, int(age))] = effectif
        totaux = {sexe: somme_ordonnee(n for (s, _), n in self._effectifs.items() if s == sexe)
                  for sexe in SEXES}
        #: ``(sexe, age) -> part de la masse du stock``, qui somme à un.
        self._poids = {
            (sexe, age): self.part_du_sexe(sexe) * effectif / totaux[sexe]
            for (sexe, age), effectif in self._effectifs.items()
        }
        #: ``(sexe, age) -> survies au 1er janvier de la bascule, de
        #: l'année suivante, etc.``, prolongées à la demande.
        self._survies: dict[tuple[str, int], list[float]] = {
            cellule: [1.0] for cellule in self._poids}

    def _etalement(self, sexe: str) -> list[tuple[int, float]]:
        """Les 90 ans ou plus, étalés de 90 ans à l'âge limite comme les
        survivants d'une génération à la mortalité de l'année du profil."""
        survivants = [1.0]
        for age in range(AGE_DE_LA_TRANCHE_OUVERTE, AGE_LIMITE - 1):
            survivants.append(survivants[-1] * self._mortalite.survie_annuelle(
                float(age), self.annee_du_profil, sexe))
        total = somme_ordonnee(survivants)
        return [(AGE_DE_LA_TRANCHE_OUVERTE + rang, n / total)
                for rang, n in enumerate(survivants)]

    @staticmethod
    def part_du_sexe(sexe: str) -> float:
        """La part de la masse du stock que touchent les survivants d'un sexe."""
        if sexe not in SEXES:
            raise ValueError(f"sexe inconnu : {sexe!r} (attendu : {SEXES})")
        return PART_DES_FEMMES if sexe == "F" else 1.0 - PART_DES_FEMMES

    @property
    def age_moyen(self) -> float:
        """L'âge moyen des bénéficiaires du stock à la bascule, par tête : un
        âge révolu au 1er janvier vaut, en moyenne, cet âge et demi."""
        total = somme_ordonnee(self._effectifs.values())
        return somme_ordonnee((age + 0.5) * n for (_, age), n in self._effectifs.items()) / total

    def _survie_au_1er_janvier(self, cellule: tuple[str, int], rang: int) -> float:
        """La survie d'une cellule du 1er janvier de la bascule à celui de la
        ``rang``-ième année suivante."""
        survies = self._survies[cellule]
        sexe, age = cellule
        while len(survies) <= rang:
            ecoule = len(survies) - 1
            atteint = age + ecoule
            annuelle = (0.0 if atteint >= AGE_LIMITE
                        else self._mortalite.survie_annuelle(
                            float(atteint), self.annee_bascule + ecoule, sexe))
            survies.append(survies[-1] * annuelle)
        return survies[rang]

    def survie(self, annee: int) -> float:
        """La part de la masse du stock servie dans l'année, en euros constants.

        Un avant la bascule. Ensuite, la moyenne des survies au 1er janvier de
        l'année et du suivant : on touche sa réversion tant qu'on vit, et l'on
        meurt, en moyenne, au milieu de l'année.
        """
        if annee < self.annee_bascule:
            return 1.0
        rang = annee - self.annee_bascule
        return somme_ordonnee(
            poids * 0.5 * (self._survie_au_1er_janvier(cellule, rang)
                           + self._survie_au_1er_janvier(cellule, rang + 1))
            for cellule, poids in self._poids.items()
        )
