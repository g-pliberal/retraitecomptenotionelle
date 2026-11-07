"""Les lectures de la décision 29, la dépense suivant le taux cotisé (action 186, chantier 1).

Le 7 novembre 2026, le propriétaire a décidé : « on baisse seulement de moitié
le déficit » (``docs/feuille_de_route_programme.md``, décision 29). La phrase
se lit de deux façons :

- **lecture A** : la moitié de ce que la baisse des pensions économise va au
  déficit, l'autre moitié aux cotisants, par un taux plus bas ;
- **lecture B** : le déficit du droit en vigueur est divisé par deux, tout le
  reste de l'économie va aux cotisants ;

et une référence, **tout au déficit**, le taux du droit en vigueur gardé.

CE QUE LE SCRIPT CORRIGE. Le premier chiffrage, fait à côté du modèle,
changeait les cotisations sans changer les pensions qu'elles ouvrent. Ici,
le taux cotisé est le taux crédité aux comptes du scénario 6
(``Parametres.taux_cotisation_liberal``) : ce qui est payé ouvre des droits,
rien de plus, rien de moins. La dépense de chaque taux est celle que le coût
calcule sous ce taux (``memoire.cout``), et l'économie, qui en dépend, se
partage selon la règle : un point fixe.

LES CONVENTIONS, qu'il faut dire en tête de tout chiffre qui en sort.

- Les recettes se comptent de trois façons (``CONVENTIONS``), qui changent
  tout. ``page_cout`` : celles de la proposition, comme la page Coût — ni
  impôts affectés, ni versements de l'État, ni transferts pour les droits
  non contributifs, 135 Md€ de moins qu'au droit en vigueur en 2026 —, le
  solde étant celui du régime, la garantie vieillesse à part.
  ``recettes_gardees``, le premier calcul : toutes celles du droit en
  vigueur, sauf ses cotisations ; c'est aussi la retraite et l'État comptés
  ensemble, l'État gardant ce qu'il ne verse plus et les impôts affectés.
  ``impots_supprimes`` : la même chose, ces impôts supprimés. Le droit en
  vigueur prélève ``cotisations_actuel`` (21,4 % de l'assiette de la
  proposition en 2026, 19,7 % en 2070), la variante ``taux × assiette`` ;
  ``(taux du droit en vigueur − taux) × assiette`` est ce qui est rendu aux
  cotisants.
- La dépense est celle du scénario 6 sous ce taux, pensions et garantie
  vieillesse nette des reprises sur succession, comme ``chiffrage_plf.py`` ;
  la garantie à part sur la base de la page Coût.
- Le taux est CONSTANT de 2026 à 2070, et la règle de chaque lecture tient
  EN MOYENNE sur ces années, en moyenne simple des parts de PIB, la
  convention du solde moyen du dépôt : le modèle ne sait pas faire varier le
  taux d'une année à l'autre. Année par année, la règle ne tient pas : la
  dépense ne suit le taux qu'à mesure que partent ceux qui l'ont cotisé.
  ``resoudre(lecture, annees=(2026,))`` dit le taux qui la tiendrait la
  première année, où la dépense ne dépend pas encore du taux.
- La dette refait la récurrence de ``cout.calculer_dette``, avec la
  croissance et le taux de chaque année du coût ; elle part de zéro fin 2025.

Rien d'autre ne bouge : ni comportement, ni pilier capitalisé, ni les
recettes du chantier 4, ni la décision 16 (les réversions servies gardées),
qui réduira l'économie.

Usage : ``python scripts/lectures_decision_29.py`` (une quinzaine de calculs
du coût, une demi-minute chacun sans mémoire) : les taux sous les trois
conventions, puis le détail de l'une (``--convention``, la page Coût par
défaut) ; ``--cas-types`` pour la pension de quelques cas types sous chaque
taux.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.somme import somme_ordonnee  # noqa: E402

LIBERAL = "notionnel_liberal"
DEBUT, FIN = 2026, 2070

#: Les taux calculés d'abord, entre lesquels la dépense s'interpole ; les taux
#: trouvés sont ensuite calculés eux-mêmes, et la résolution reprise.
GRILLE: tuple[float, ...] = (0.02, 0.06, 0.10, 0.14, 0.18, 0.22, 0.26, 0.30, 0.34)

LECTURES: dict[str, str] = {
    "tout": "Tout au déficit",
    "A": "Lecture A",
    "B": "Lecture B",
    "B_hors_etat": "Lecture B, hors versements de l'État",
}

#: Le taux du programme, que le scénario 6 crédite : la référence des cas types.
TAUX_PROGRAMME = 0.18

VUES: tuple[int, ...] = (2026, 2027, 2028, 2029, 2030, 2035, 2040, 2045, 2050,
                         2055, 2060, 2065, 2070)


@dataclass(frozen=True)
class Annee:
    """Ce qui, d'une année, ne dépend pas du taux. Parts de PIB, sauf ``pib``,
    en millions d'euros courants."""

    annee: int
    depense_actuel: float
    solde_actuel: float
    cotisations_actuel: float
    #: L'assiette sur laquelle la proposition prélève son taux.
    assiette: float
    #: La contribution d'équilibre de l'État et ses subventions d'équilibre.
    versements_etat: float
    pib: float
    croissance: float
    taux_dette: float
    #: Les impôts et taxes affectés au droit en vigueur (CSG, taxes).
    impots_affectes: float = 0.0
    #: Ce que la proposition encaisse hors de ses cotisations, comme la page
    #: Coût le compte : ni impôts affectés, ni versements de l'État, ni
    #: transferts pour les droits non contributifs.
    recettes_proposition: float = 0.0

    @property
    def taux_actuel(self) -> float:
        """Ce que le droit en vigueur prélève, rapporté à cette assiette."""
        return self.cotisations_actuel / self.assiette


@dataclass(frozen=True)
class Ligne:
    """Une année d'une lecture, sous un taux."""

    annee: int
    depense: float
    economie: float
    rendu: float
    rendu_md: float
    #: Ce qui est rendu, en points de cotisation : le taux du droit en
    #: vigueur moins celui de la variante.
    points: float
    solde: float
    deficit: float
    versements_etat: float
    dette: float


#: Les trois façons de compter les recettes, qui changent tout (le
#: 7 novembre 2026, après la question du propriétaire : « ce n'est pas la
#: simulation qui est déjà présente sur le site dans la page coût ») :
#:
#: - ``recettes_gardees``, le premier calcul : la retraite garde toutes les
#:   recettes du droit en vigueur, impôts affectés et versements de l'État
#:   compris, sauf ses cotisations. C'est aussi la retraite et l'État comptés
#:   ensemble, si l'État garde les impôts affectés ;
#: - ``impots_supprimes`` : la même chose, les impôts affectés supprimés ;
#: - ``page_cout`` : les recettes de la proposition, celles de la page Coût,
#:   dont le solde est celui du régime, la garantie vieillesse à part.
CONVENTIONS: dict[str, str] = {
    "page_cout": "la caisse de retraite, comme la page Coût",
    "impots_supprimes": "la retraite et l'État ensemble, impôts affectés supprimés",
    "recettes_gardees": "la retraite et l'État ensemble, impôts affectés gardés",
}


class Etude:
    """Les années communes, et la dépense de la proposition sous chaque taux
    calculé, ``{taux: {année: part de PIB}}``, garantie vieillesse nette
    comprise ; ``garanties``, de même forme, ce qu'elle en est, que la page
    Coût compte à part."""

    def __init__(self, annees: Iterable[Annee],
                 depenses: Mapping[float, Mapping[int, float]],
                 garanties: Mapping[float, Mapping[int, float]] | None = None,
                 convention: str = "recettes_gardees") -> None:
        if convention not in CONVENTIONS:
            raise KeyError(convention)
        self.annees = sorted(annees, key=lambda a: a.annee)
        self.depenses = {taux: dict(serie) for taux, serie in sorted(depenses.items())}
        self.garanties = {taux: dict(serie) for taux, serie in (garanties or {}).items()}
        self.convention = convention
        self.taux = list(self.depenses)

    def _interpolee(self, series: Mapping[float, Mapping[int, float]], annee: int,
                    taux: float) -> float:
        if taux in series:
            return series[taux][annee]
        for bas, haut in zip(self.taux, self.taux[1:]):
            if bas <= taux <= haut:
                d_bas, d_haut = series[bas][annee], series[haut][annee]
                return d_bas + (d_haut - d_bas) * (taux - bas) / (haut - bas)
        raise ValueError(f"taux {taux} hors des taux calculés ({self.taux[0]} à {self.taux[-1]})")

    def recettes(self, a: Annee, taux: float) -> float:
        if self.convention == "page_cout":
            return a.recettes_proposition + taux * a.assiette
        gardees = a.depense_actuel + a.solde_actuel - (a.taux_actuel - taux) * a.assiette
        if self.convention == "impots_supprimes":
            return gardees - a.impots_affectes
        return gardees

    def depense(self, annee: int, taux: float) -> float:
        """La dépense de l'année sous ce taux, linéaire entre deux taux calculés ;
        sans la garantie vieillesse, sur la base de la page Coût."""
        depense = self._interpolee(self.depenses, annee, taux)
        if self.convention == "page_cout" and self.garanties:
            depense -= self._interpolee(self.garanties, annee, taux)
        return depense

    def trajectoire(self, taux: float) -> list[Ligne]:
        lignes: list[Ligne] = []
        dette = 0.0
        for a in self.annees:
            depense = self.depense(a.annee, taux)
            economie = a.depense_actuel - depense
            rendu = (a.taux_actuel - taux) * a.assiette
            solde = self.recettes(a, taux) - depense
            dette = dette * (1.0 + a.taux_dette) / (1.0 + a.croissance) - solde
            lignes.append(Ligne(annee=a.annee, depense=depense, economie=economie,
                                rendu=rendu, rendu_md=rendu * a.pib / 1000.0,
                                points=a.taux_actuel - taux, solde=solde,
                                deficit=a.solde_actuel, versements_etat=a.versements_etat,
                                dette=dette))
        return lignes

    def ecart(self, lecture: str, taux: float, annees: Iterable[int] | None = None) -> float:
        """Ce dont la règle de la lecture manque, en moyenne sur ``annees``
        (toutes par défaut), en part de PIB : zéro quand elle tient."""
        retenues = None if annees is None else set(annees)
        lignes = [ligne for ligne in self.trajectoire(taux)
                  if retenues is None or ligne.annee in retenues]
        if lecture == "tout":
            ecarts = [ligne.solde - ligne.deficit - ligne.economie for ligne in lignes]
        elif lecture == "A":
            ecarts = [ligne.solde - ligne.deficit - ligne.economie / 2.0 for ligne in lignes]
        elif lecture == "B":
            ecarts = [ligne.solde - ligne.deficit / 2.0 for ligne in lignes]
        elif lecture == "B_hors_etat":
            # Le déficit compté sans les versements de l'État, divisé par
            # deux. Encaissés, ils s'y ajoutent : le solde vaut
            # (déficit − versements) / 2 + versements ; sur la base de la
            # page Coût, la retraite ne les reçoit plus.
            versements = 0.0 if self.convention == "page_cout" else 1.0
            ecarts = [ligne.solde - (ligne.deficit - ligne.versements_etat) / 2.0
                      - versements * ligne.versements_etat for ligne in lignes]
        else:
            raise KeyError(lecture)
        return somme_ordonnee(ecarts) / len(ecarts)

    def resoudre(self, lecture: str, annees: Iterable[int] | None = None) -> float:
        """Le taux constant auquel la règle de la lecture tient, par dichotomie
        entre le plus bas et le plus haut des taux calculés."""
        annees = None if annees is None else tuple(annees)
        bas, haut = self.taux[0], self.taux[-1]
        e_bas, e_haut = self.ecart(lecture, bas, annees), self.ecart(lecture, haut, annees)
        for bord, e_bord in ((bas, e_bas), (haut, e_haut)):
            if abs(e_bord) < 1e-15:
                return bord
        if e_bas * e_haut > 0:
            raise ValueError(f"{lecture} : aucun taux entre {bas} et {haut} ne tient la règle")
        for _ in range(100):
            milieu = (bas + haut) / 2.0
            e_milieu = self.ecart(lecture, milieu, annees)
            if e_bas * e_milieu <= 0:
                haut = milieu
            else:
                bas, e_bas = milieu, e_milieu
        return (bas + haut) / 2.0


# -- le modèle ----------------------------------------------------------------


def du_modele(taux: float) -> tuple[list[Annee], dict[int, float], dict[int, float]]:
    """Le coût sous ce taux crédité : les années, la dépense de la proposition,
    garantie vieillesse nette comprise, et cette garantie."""
    from retraite_notionnelle import cout as C
    from retraite_notionnelle import memoire
    from retraite_notionnelle.config import Parametres

    cout = memoire.cout(Parametres().avec(taux_cotisation_liberal=taux))
    avenir = {ligne.annee: ligne for ligne in cout.avenir.annees}
    dette = {ligne.annee: ligne for ligne in cout.dette.annees}
    annees, depenses, garanties = [], {}, {}
    for ligne in cout.solde.annees:
        if not DEBUT <= ligne.annee <= FIN:
            continue
        projetee, d = avenir[ligne.annee], dette[ligne.annee]
        actuel, liberal = ligne.postes_ressources("actuel"), ligne.postes_ressources(LIBERAL)
        annees.append(Annee(
            annee=ligne.annee,
            depense_actuel=ligne.depense("actuel"),
            solde_actuel=ligne.solde("actuel"),
            cotisations_actuel=actuel["cotisations"],
            assiette=liberal["cotisations"] / ligne.taux_liberal,
            versements_etat=actuel["contribution_equilibre_etat"] + actuel["subventions_equilibre"],
            pib=projetee.pib,
            croissance=d.croissance,
            taux_dette=d.taux,
            impots_affectes=actuel["impots_et_taxes"],
            recettes_proposition=ligne.ressources_de(LIBERAL) - liberal["cotisations"],
        ))
        garanties[ligne.annee] = (projetee.part_pib(C.COMPOSANTE_GARANTIE)
                                  - projetee.part_pib_reprises())
        depenses[ligne.annee] = ligne.depense(LIBERAL) + garanties[ligne.annee]
    return annees, depenses, garanties


def _memes_annees(unes: list[Annee], autres: list[Annee]) -> bool:
    """Les mêmes années, aux arrondis près : l'assiette se lit en divisant par
    le taux ce qu'il prélève."""
    import math

    return len(unes) == len(autres) and all(
        u.annee == v.annee and all(math.isclose(getattr(u, champ), getattr(v, champ),
                                                rel_tol=1e-9, abs_tol=1e-12)
                                   for champ in ("depense_actuel", "solde_actuel",
                                                 "cotisations_actuel", "assiette",
                                                 "versements_etat", "pib", "croissance",
                                                 "taux_dette", "impots_affectes",
                                                 "recettes_proposition"))
        for u, v in zip(unes, autres))


def etude_du_modele(grille: Iterable[float] = GRILLE, convention: str = "page_cout",
                    ) -> tuple[Etude, dict[str, float]]:
    """Les taux de chaque lecture, au modèle, sous une convention de recettes :
    résolus sur la grille, puis calculés eux-mêmes, arrondis au centième de
    point, et résolus de nouveau jusqu'à ce qu'ils ne bougent plus."""
    annees: list[Annee] | None = None
    depenses: dict[float, dict[int, float]] = {}
    garanties: dict[float, dict[int, float]] = {}

    def calculer(taux: float) -> None:
        nonlocal annees
        if taux in depenses:
            return
        lues, depenses[taux], garanties[taux] = du_modele(taux)
        if annees is None:
            annees = lues
        elif not _memes_annees(lues, annees):
            raise ValueError(f"le taux {taux} change ce qui ne devait pas en dépendre")

    for taux in grille:
        calculer(taux)
    trouves: dict[str, float] = {}
    for _ in range(4):
        etude = Etude(annees, depenses, garanties, convention)
        nouveaux = {lecture: round(etude.resoudre(lecture), 4) for lecture in LECTURES}
        if nouveaux == trouves:
            break
        trouves = nouveaux
        for taux in trouves.values():
            calculer(taux)
    calculer(TAUX_PROGRAMME)
    return Etude(annees, depenses, garanties, convention), trouves


CAS_TYPES = ("smic_carriere_complete", "salaire_moyen", "cadre")
GENERATIONS = (1975, 1990, 2005)


def pensions_des_cas_types(taux: float) -> dict[tuple[str, int], dict]:
    """La pension du scénario 6, en euros constants de 2026, de quelques cas
    types, sous ce taux crédité, et leur revenu de 2026."""
    from retraite_notionnelle.castypes import GRILLE_DU_COUT, carriere_de_la_grille
    from retraite_notionnelle.config import Parametres
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur(Parametres().avec(taux_cotisation_liberal=taux))
    sortie = {}
    for code in CAS_TYPES:
        cas = next(c for c in GRILLE_DU_COUT if c.code == code)
        for generation in GENERATIONS:
            carriere = carriere_de_la_grille(simulateur, cas, generation)
            resultat = simulateur.simuler(carriere)
            sortie[(code, generation)] = {
                "libelle": cas.libelle,
                "pension": resultat.en_euros_constants(
                    resultat.notionnel_liberal.pension_annuelle, LIBERAL),
                "actuel": resultat.en_euros_constants(resultat.actuel.pension_annuelle),
                "depart": resultat.carriere_de(LIBERAL).annee_liquidation,
                "revenu_2026": next((ligne.revenu for ligne in carriere.lignes
                                     if ligne.annee == 2026), None),
            }
    return sortie


# -- l'écriture -----------------------------------------------------------------


def _n(valeur: float, decimales: int = 2, signe: bool = True) -> str:
    texte = f"{valeur:+,.{decimales}f}" if signe else f"{valeur:,.{decimales}f}"
    return texte.replace(",", " ").replace(".", ",").replace("-", "−")


def _pourcent(taux: float) -> str:
    return _n(100 * taux, 2, signe=False) + " %"


def rapport(etude: Etude, trouves: Mapping[str, float]) -> str:
    colonnes = dict(trouves)
    colonnes["prog"] = TAUX_PROGRAMME
    titres = dict(LECTURES, prog="18 %, le taux du programme")
    trajectoires = {nom: etude.trajectoire(taux) for nom, taux in colonnes.items()}
    lignes = ["## Les taux", "",
              "| Lecture | Taux constant, la règle tenue en moyenne 2026-2070 "
              "| Écart à la règle, points de PIB | Taux de la règle tenue en 2026 seule |",
              "|---|---:|---:|---:|"]
    for nom, taux in trouves.items():
        lignes.append(f"| {titres[nom]} | {_pourcent(taux)} | {_n(100 * etude.ecart(nom, taux), 4)} "
                      f"| {_pourcent(etude.resoudre(nom, annees=(DEBUT,)))} |")
    dette_actuelle = 0.0
    for a in etude.annees:
        dette_actuelle = dette_actuelle * (1 + a.taux_dette) / (1 + a.croissance) - a.solde_actuel
    n = len(etude.annees)
    lignes += ["", "## La synthèse, en points de PIB sauf mention", "",
               "| | " + " | ".join(titres[nom] for nom in colonnes) + " | Droit en vigueur |",
               "|---|" + "---:|" * (len(colonnes) + 1)]

    def rangee(libelle: str, valeurs: list[str], actuel_: str) -> None:
        lignes.append(f"| {libelle} | " + " | ".join(valeurs) + f" | {actuel_} |")

    def a(nom: str, annee: int) -> Ligne:
        return next(ligne for ligne in trajectoires[nom] if ligne.annee == annee)

    soldes_actuels = {x.annee: x.solde_actuel for x in etude.annees}
    rangee("Taux cotisé et crédité", [_pourcent(colonnes[nom]) for nom in colonnes],
           _pourcent(etude.annees[0].taux_actuel) + " en 2026")
    for annee in (2026, 2040, 2070):
        rangee(f"Solde {annee}", [_n(100 * a(nom, annee).solde) for nom in colonnes],
               _n(100 * soldes_actuels[annee]))
    rangee("Solde moyen 2026-2070",
           [_n(100 * somme_ordonnee(x.solde for x in trajectoires[nom]) / n) for nom in colonnes],
           _n(100 * somme_ordonnee(soldes_actuels.values()) / n))
    for annee in (2030, 2050, 2070):
        rangee(f"Dette {annee} (négative : une réserve)",
               [_n(100 * a(nom, annee).dette, 1) for nom in colonnes],
               _n(100 * dette_actuelle, 1) if annee == FIN else "")
    rangee("Rendu en 2026, Md€ et points de cotisation",
           [f"{_n(a(nom, DEBUT).rendu_md, 0)} Md€, {_n(100 * a(nom, DEBUT).points, 1)}"
            for nom in colonnes], "")
    rangee("Rendu en 2070, Md€ et points de cotisation",
           [f"{_n(a(nom, FIN).rendu_md, 0)} Md€, {_n(100 * a(nom, FIN).points, 1)}"
            for nom in colonnes], "")
    rangee("Rendu cumulé 2026-2070, Md€ courants",
           [_n(somme_ordonnee(x.rendu_md for x in trajectoires[nom]), 0) for nom in colonnes], "")
    for nom, taux in colonnes.items():
        lignes += ["", f"## {titres[nom]} : {_pourcent(taux)}, année par année", "",
                   "| Année | Dépense | Économie | Rendu, Md€ | Rendu, points | Rendu / économie "
                   "| Solde | Déficit actuel | Dette |",
                   "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for x in trajectoires[nom]:
            if x.annee in VUES:
                lignes.append(
                    f"| {x.annee} | {_n(100 * x.depense, 2, False)} | {_n(100 * x.economie, 2, False)} "
                    f"| {_n(x.rendu_md, 0)} | {_n(100 * x.points, 1)} | {_n(x.rendu / x.economie, 2, False)} "
                    f"| {_n(100 * x.solde)} | {_n(100 * x.deficit)} | {_n(100 * x.dette, 1)} |")
    return "\n".join(lignes)


def rapport_cas_types(trouves: Mapping[str, float]) -> str:
    colonnes = dict(trouves)
    colonnes["prog"] = TAUX_PROGRAMME
    pensions = {nom: pensions_des_cas_types(taux) for nom, taux in colonnes.items()}
    titres = dict(LECTURES, prog="18 %")
    lignes = ["## Les cas types : la pension du scénario 6, en euros de 2026 par mois, "
              "et son écart aux 18 %", "",
              "| Cas type | Départ | Droit en vigueur | "
              + " | ".join(titres[nom] if nom == "prog" else f"{titres[nom]} ({_pourcent(taux)})"
                           for nom, taux in colonnes.items())
              + " | Revenu brut de 2026, par mois |",
              "|---|---:|---:|" + "---:|" * (len(colonnes) + 1)]
    for code in CAS_TYPES:
        for generation in GENERATIONS:
            reference = pensions["prog"][(code, generation)]
            cellules = []
            for nom in colonnes:
                p = pensions[nom][(code, generation)]["pension"]
                cellules.append(f"{_n(p / 12, 0, False)} ({_n(100 * (p / reference['pension'] - 1), 0)} %)")
            revenu = reference["revenu_2026"]
            lignes.append(f"| {reference['libelle']}, né en {generation} | {reference['depart']} "
                          f"| {_n(reference['actuel'] / 12, 0, False)} | "
                          + " | ".join(cellules)
                          + (f" | {_n(revenu / 12, 0, False)} |" if revenu else " | — |"))
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    lecteur = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    lecteur.add_argument("--cas-types", action="store_true",
                         help="la pension de quelques cas types sous chaque taux")
    lecteur.add_argument("--convention", choices=list(CONVENTIONS), default="page_cout",
                         help="les recettes du détail (la page Coût par défaut)")
    options = lecteur.parse_args(argv)
    resultats = {convention: etude_du_modele(convention=convention)
                 for convention in CONVENTIONS}
    print("## Le taux de chaque lecture, selon le déficit dont on parle\n")
    print("| Le déficit | " + " | ".join(LECTURES.values()) + " |")
    print("|---|" + "---:|" * len(LECTURES))
    for convention, (_, taux) in resultats.items():
        print(f"| {CONVENTIONS[convention]} | "
              + " | ".join(_pourcent(taux[lecture]) for lecture in LECTURES) + " |")
    etude, trouves = resultats[options.convention]
    print(f"\n# Le détail : {CONVENTIONS[options.convention]}\n")
    print(rapport(etude, trouves))
    if options.cas_types:
        print()
        print(rapport_cas_types(trouves))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
