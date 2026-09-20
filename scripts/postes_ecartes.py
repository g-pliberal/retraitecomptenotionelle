#!/usr/bin/env python3
"""Les postes que la proposition n'encaisse pas, reconduits un par un.

    python scripts/postes_ecartes.py
    python scripts/postes_ecartes.py --json postes.json

CE QU'IL MESURE
---------------
La convention du programme écarte trois postes de recette du scénario 6 :
les impôts et taxes affectés, la contribution d'équilibre de l'État et les
subventions d'équilibre aux régimes spéciaux. ``cout.ressources_de`` dit
pourquoi, décision par décision. Ce script les reconduit UN PAR UN, sans
rien changer d'autre, et répond à une question que la page ne pose pas :

    le déficit de la proposition tient-il dans un de ces postes, tel que le
    système actuel le porte aujourd'hui — ou lui en faudrait-il davantage ?

C'est une question de niveau, pas de doctrine. La dépense ne bouge dans
aucune colonne : seule change la recette qu'on accepte de compter. Un
chiffrage qui rend l'équilibre ne dit donc pas que la proposition coûte
moins, il dit de combien de recette non contributive elle aurait besoin.

LES TROIS CHIFFRAGES, ET CE QU'ILS SUPPOSENT
--------------------------------------------
``impots`` — les impôts et taxes affectés reconduits tels quels : CSG, taxe
    sur les salaires, forfait social, C3S, taxes agricoles. **Un tiers de ce
    poste est la CSG du fonds de solidarité vieillesse**, qui sortait déjà
    par le retrait, lu du côté de ce que le fonds verse aux régimes. Elle
    rentre avec le poste, et le retrait reprend donc sa valeur pleine :
    faute de quoi la même somme rentrerait deux fois. C'est
    ``retrait_par_impot``, et c'est la seule subtilité du calcul.

``contribution`` — la contribution d'équilibre de l'État reconduite telle
    quelle : ce que l'État verse au régime de ses fonctionnaires au taux qui
    l'équilibre, 74,28 % des traitements en 2024. **Elle se superpose aux
    18 %, elle ne les remplace pas** : l'assiette des 18 % porte déjà les
    traitements de la fonction publique, si bien que ce chiffrage fait payer
    à l'État 18 % comme tout employeur PLUS le complément qu'il verse
    aujourd'hui. C'est ce qui se passerait si la réforme laissait ce poste
    intact, et c'est bien la question posée ; ce n'est pas une lecture du
    taux d'employeur de l'État sous la proposition.

``subventions`` — les subventions d'équilibre aux régimes spéciaux
    reconduites telles quelles. Le poste est petit, et son objet disparaît
    avec la fusion des régimes : il est ici pour que l'arithmétique des
    trois soit complète, pas parce qu'il serait défendable.

``tous`` — les trois ensemble, qui est la borne haute de l'exercice.

CE QU'IL EMPRUNTE
-----------------
``cout.calculer_cout`` aux paramètres par défaut, et rien d'autre : chaque
chiffrage recompose ``ressources_de`` terme à terme à partir de la même
ligne de solde, et un test tient l'identité de la recomposition. Aucun
moteur de pension n'est touché, aucune convention n'est changée.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from retraite_notionnelle import cout as C  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.donnees.assiette import AssietteActivite  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.equilibre import ComptesRetraite  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

LIBERAL = "notionnel_liberal"
ANNEES_AFFICHEES: tuple[int, ...] = (2026, 2030, 2040, 2050, 2060, 2070)

#: Les trois postes écartés, dans l'ordre où ils pèsent.
POSTE_IMPOTS = "impots"
POSTE_CONTRIBUTION = "contribution"
POSTE_SUBVENTIONS = "subventions"
POSTES: tuple[tuple[str, str], ...] = (
    (POSTE_IMPOTS, "Impôts et taxes affectés"),
    (POSTE_CONTRIBUTION, "Contribution d'équilibre de l'État"),
    (POSTE_SUBVENTIONS, "Subventions d'équilibre"),
)


def montant(ligne: C.SoldeAnnuel, poste: str) -> float:
    """Ce que le système actuel porte à ce poste, en part de PIB.

    Le poste des impôts rend son montant NET de la CSG du fonds de solidarité
    vieillesse : c'est ce que sa reconduction ajoute réellement aux ressources
    de la proposition, le reste rentrant d'une main pour ressortir de l'autre
    par le retrait. Les deux autres postes n'ont pas ce double compte.
    """
    if poste == POSTE_IMPOTS:
        return ligne.ressources * ligne.part_impots - ligne.retrait_par_impot
    if poste == POSTE_CONTRIBUTION:
        return ligne.ressources * ligne.parts.get("contribution_equilibre_etat", 0.0)
    if poste == POSTE_SUBVENTIONS:
        return ligne.ressources * ligne.part_subventions
    raise ValueError(f"poste inconnu : {poste!r}")


def montant_brut(ligne: C.SoldeAnnuel, poste: str) -> float:
    """Le même poste tel que le COR le publie, CSG du fonds comprise."""
    if poste == POSTE_IMPOTS:
        return ligne.ressources * ligne.part_impots
    return montant(ligne, poste)


@dataclass
class Chiffrage:
    """Un chiffrage : la proposition, plus les postes qu'il reconduit."""

    cle: str
    libelle: str
    #: Les postes reconduits, vide pour la référence.
    postes: tuple[str, ...]
    soldes: dict[int, float] = field(default_factory=dict)
    ressources: dict[int, float] = field(default_factory=dict)
    coefficients: dict[int, float] = field(default_factory=dict)
    solde_moyen: float = 0.0
    premiere_annee_equilibree: int | None = None
    #: Pire année de la fenêtre, et son solde.
    pire_annee: int = 0
    pire_solde: float = 0.0


def chiffrer(solde: C.Solde, cle: str, libelle: str,
             postes: tuple[str, ...]) -> Chiffrage:
    """Le solde de la proposition quand ``postes`` lui sont rendus."""
    resultat = Chiffrage(cle, libelle, postes)
    projetees = [l for l in solde.projetees() if l.annee <= C.HORIZON]
    total = 0.0
    for ligne in projetees:
        rendu = sum(montant(ligne, poste) for poste in postes)
        ressources = ligne.ressources_de(LIBERAL) + rendu
        depense = ligne.depense(LIBERAL)
        resultat.soldes[ligne.annee] = ressources - depense
        resultat.ressources[ligne.annee] = ressources
        resultat.coefficients[ligne.annee] = ressources / depense if depense > 0 else 0.0
        total += ressources - depense
        if (resultat.premiere_annee_equilibree is None
                and ressources - depense >= 0.0):
            resultat.premiere_annee_equilibree = ligne.annee
    resultat.solde_moyen = total / len(projetees) if projetees else 0.0
    pire = min(resultat.soldes.items(), key=lambda couple: couple[1])
    resultat.pire_annee, resultat.pire_solde = pire
    return resultat


@dataclass
class Besoin:
    """De combien d'un poste la proposition a besoin, et sur quelle année.

    ``brut`` compare le déficit au poste tel que le COR le publie ; ``net``
    le compare à ce que sa reconduction rapporterait vraiment. Les deux ne
    diffèrent que pour les impôts, et ils ne donnent pas la même réponse :
    voir ``montant``.
    """

    poste: str
    libelle: str
    #: Vrai si la comparaison se fait sur le poste publié, sans retrancher
    #: la CSG du fonds de solidarité vieillesse.
    brut: bool = False
    #: Part du poste qu'il faudrait pour équilibrer, année par année.
    parts: dict[int, float] = field(default_factory=dict)
    #: Moyenne 2026-2070 du besoin rapportée à la moyenne du poste.
    part_moyenne: float = 0.0
    #: Année où la part demandée est la plus grande, et cette part.
    annee_critique: int = 0
    part_critique: float = 0.0
    #: Le poste suffit-il chaque année de la fenêtre ?
    suffit_toujours: bool = False


def besoin_de(solde: C.Solde, poste: str, libelle: str,
              brut: bool = False) -> Besoin:
    """Quelle part du poste il faudrait pour que la proposition tombe juste."""
    resultat = Besoin(poste, libelle, brut)
    projetees = [l for l in solde.projetees() if l.annee <= C.HORIZON]
    mesure = montant_brut if brut else montant
    manques = 0.0
    postes = 0.0
    for ligne in projetees:
        manque = -(ligne.ressources_de(LIBERAL) - ligne.depense(LIBERAL))
        disponible = mesure(ligne, poste)
        resultat.parts[ligne.annee] = (manque / disponible if disponible > 0.0 else 0.0)
        manques += manque
        postes += disponible
    resultat.part_moyenne = manques / postes if postes > 0.0 else 0.0
    critique = max(resultat.parts.items(), key=lambda couple: couple[1])
    resultat.annee_critique, resultat.part_critique = critique
    resultat.suffit_toujours = resultat.part_critique <= 1.0
    return resultat


def calculer(parametres: Parametres) -> tuple[C.Cout, list[Chiffrage], list[Besoin]]:
    racine = parametres.racine_donnees
    cout = C.calculer_cout(
        Simulateur(parametres), DepensesRetraite(racine), Population(racine),
        ComptesRetraite(racine), assiette=AssietteActivite(racine),
    )
    solde = cout.solde
    chiffrages = [chiffrer(solde, "reference", "Proposition, convention du programme", ())]
    for poste, libelle in POSTES:
        chiffrages.append(chiffrer(solde, poste, f"+ {libelle}", (poste,)))
    chiffrages.append(chiffrer(solde, "tous", "+ les trois postes",
                               tuple(poste for poste, _ in POSTES)))
    besoins = []
    for poste, libelle in POSTES:
        besoins.append(besoin_de(solde, poste, libelle))
        # Les impôts se lisent des deux façons, et elles ne concluent pas
        # pareil : le poste publié porte une CSG qui finance des droits que la
        # proposition ne sert plus.
        if poste == POSTE_IMPOTS:
            besoins.append(besoin_de(solde, poste, f"{libelle}, poste publié",
                                     brut=True))
    return cout, chiffrages, besoins


def tableau(cout: C.Cout, chiffrages: list[Chiffrage], besoins: list[Besoin],
            annees: tuple[int, ...] = ANNEES_AFFICHEES) -> str:
    solde = cout.solde
    lignes = ["Solde en points de PIB. La DÉPENSE est la même partout : seule",
              "change la recette non contributive qu'on accepte de compter.", ""]

    entete = (f"{'chiffrage':<42}" + "".join(f"{a:>8}" for a in annees)
              + f"{'moy.':>8}{'équil.':>8}{'pire':>15}")
    lignes += [entete, "-" * len(entete)]
    actuel = ("1 système actuel", {a: solde.annee(a).solde("actuel") for a in annees},
              solde.solde_moyen("actuel", 2026, C.HORIZON))
    lignes.append(f"{actuel[0]:<42}" + "".join(f"{actuel[1][a] * 100:>+8.2f}" for a in annees)
                  + f"{actuel[2] * 100:>+8.2f}{'—':>8}{'':>13}")
    for chiffrage in chiffrages:
        equilibre = chiffrage.premiere_annee_equilibree
        pire = f"{chiffrage.pire_solde * 100:+.2f} en {chiffrage.pire_annee}"
        lignes.append(
            f"{chiffrage.libelle:<42}"
            + "".join(f"{chiffrage.soldes[a] * 100:>+8.2f}" for a in annees)
            + f"{chiffrage.solde_moyen * 100:>+8.2f}"
            + f"{str(equilibre) if equilibre else '—':>8}{pire:>15}"
        )

    lignes += ["", "Ce que le système actuel porte à chaque poste, en points de PIB.",
               "Les impôts sont donnés bruts, puis nets de la CSG du fonds de",
               "solidarité vieillesse — la part qui rentre avec le poste et ressort",
               "aussitôt par le retrait, et qui ne finance donc rien de plus.", ""]
    entete = f"{'poste':<42}" + "".join(f"{a:>8}" for a in annees)
    lignes += [entete, "-" * len(entete)]
    for poste, libelle in POSTES:
        brut = [montant_brut(solde.annee(a), poste) for a in annees]
        net = [montant(solde.annee(a), poste) for a in annees]
        lignes.append(f"{libelle:<42}" + "".join(f"{v * 100:>8.2f}" for v in brut))
        if poste == POSTE_IMPOTS:
            lignes.append(f"{'  dont net du fonds de solidarité':<42}"
                          + "".join(f"{v * 100:>8.2f}" for v in net))

    garantie = {l.annee: l.part_pib(C.COMPOSANTE_GARANTIE)
                for l in cout.avenir.projetees()}
    lignes += ["", "Et ce que la garantie vieillesse coûte, financée par l'impôt et",
               "hors du solde : c'est elle qui remplace les droits du fonds de",
               "solidarité vieillesse, et donc ce à quoi sa CSG est déjà promise.", ""]
    lignes.append(f"{'Garantie vieillesse':<42}"
                  + "".join(f"{garantie.get(a, 0.0) * 100:>8.2f}" for a in annees))

    lignes += ["", "DE COMBIEN DE CHAQUE POSTE LA PROPOSITION A-T-ELLE BESOIN ?",
               "Part du poste qu'il faudrait reconduire pour que l'année tombe",
               "juste. Au-dessus de 100 %, le poste n'y suffit pas.", ""]
    entete = (f"{'poste':<42}" + "".join(f"{a:>8}" for a in annees)
              + f"{'moy.':>8}{'pire année':>18}")
    lignes += [entete, "-" * len(entete)]
    for besoin in besoins:
        pire = f"{besoin.part_critique:.0%} en {besoin.annee_critique}"
        lignes.append(
            f"{besoin.libelle:<42}"
            + "".join(f"{besoin.parts[a]:>8.0%}" for a in annees)
            + f"{besoin.part_moyenne:>8.0%}{pire:>18}"
        )
    lignes += ["", "Verdict, sur la moyenne 2026-2070 :"]
    for besoin in besoins:
        verdict = ("MOINS que ce que le système actuel y met"
                   if besoin.part_moyenne < 1.0
                   else "PLUS que ce que le système actuel y met")
        lignes.append(f"  {besoin.libelle:<40} {verdict} "
                      f"({besoin.part_moyenne:.0%} du poste)")
        if not besoin.suffit_toujours:
            lignes.append(f"  {'':<40} mais il n'y suffit pas chaque année : "
                          f"{besoin.part_critique:.0%} en {besoin.annee_critique}")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    analyseur.add_argument("--json", type=Path)
    arguments = analyseur.parse_args(argv)
    parametres = Parametres()
    cout, chiffrages, besoins = calculer(parametres)
    print(tableau(cout, chiffrages, besoins))
    if arguments.json:
        arguments.json.write_text(json.dumps({
            "chiffrages": {
                c.cle: {"libelle": c.libelle, "postes": list(c.postes),
                        "soldes": c.soldes, "ressources": c.ressources,
                        "coefficients": c.coefficients,
                        "solde_moyen": c.solde_moyen,
                        "premiere_annee_equilibree": c.premiere_annee_equilibree,
                        "pire_annee": c.pire_annee, "pire_solde": c.pire_solde}
                for c in chiffrages
            },
            "besoins": {
                b.poste: {"libelle": b.libelle, "parts": b.parts,
                          "part_moyenne": b.part_moyenne,
                          "annee_critique": b.annee_critique,
                          "part_critique": b.part_critique,
                          "suffit_toujours": b.suffit_toujours}
                for b in besoins
            },
        }, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
