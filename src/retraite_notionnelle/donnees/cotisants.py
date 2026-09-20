"""Combien de cotisants dans chaque caisse, et donc ce que chaque cas type pèse
du côté de la RECETTE.

`effectifs.py` pèse les cas types par les RETRAITÉS de leur caisse, et c'est le
bon poids pour une masse de pensions. Ce n'est pas le bon pour une masse de
cotisations : la page « Coût » fait réagir la recette du système 4 par un
rapport de cotisations calculé sur la même grille, et chaque cas type y pesait,
faute de mieux, le nombre de retraités de sa caisse. `limites.md` disait ce que
cette approximation faisait — surreprésenter les régimes qui s'éteignent, dont
les taux sont parmi les plus élevés, et pousser le rapport vers le bas — et
qu'aucune série de cotisants ne la remplaçait. C'était vrai des sources
parcourues ; le classeur par régime du COR en est une, et la seule qui donne les
treize caisses des cas types à la même maille, l'Ircantec et le RCI compris,
et qui les PROJETTE jusqu'en 2070 : la SNCF n'y a plus aucun cotisant en 2070,
la CNIEG cinquante et un, là où reconduire des retraités ferait l'inverse.

LA FONCTION PUBLIQUE D'ÉTAT EST D'UN SEUL TENANT DANS LE CLASSEUR, ET LA
GRILLE LA COUPE EN DEUX
-----------------------------------------------------------------------
Deux cas types la réclament — le fonctionnaire sédentaire et le militaire —,
et le COR ne publie qu'une ligne pour les deux. Les partager à égalité, comme
`poids_effectifs` le fait d'une caisse réclamée par plusieurs cas types, serait
faux d'un facteur cinq. Le partage est donc pris à la seule source qui le
donne, le rapport sur les pensions de retraite de la fonction publique annexé
au projet de loi de finances (« jaune budgétaire »), dont le dépôt porte déjà
la lecture sous ``sre_jaune_pensions`` : 1,63 million de civils et 0,32 million
de militaires cotisants au 1er janvier 2024. La clé est tenue CONSTANTE sur
toute la série, parce que rien ne dit comment elle évolue, et les deux lignes
qui en sortent sont marquées ``estimee`` : elles sont une déduction posée sur
une valeur publiée, pas une valeur publiée.

UN COTISANT DE CAISSE N'EST PAS UNE PERSONNE
---------------------------------------------
Un polyaffilié compte dans chacune de ses caisses, comme un polypensionné du
côté des retraités. Les poids qu'on en tire sont RELATIFS, et la masse de
cotisations les normalise de toute façon en divisant par celle des taux réels.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .chargement import Fiabilite, SerieAnnuelle, ValeurAnnuelle

#: La ligne du classeur que deux cas types se partagent.
FONCTION_PUBLIQUE_ETAT = "fonction_publique_etat"

#: Cotisants civils et militaires de l'État au 1er janvier 2024, tels que le
#: jaune « Pensions » annexé au PLF 2026 les écrit (``sre_jaune_pensions``), en
#: personnes. Seul leur rapport sert : il partage la ligne du COR entre les
#: deux cas types, et il est reconduit à l'identique sur toute la série.
COTISANTS_ETAT_2024: dict[str, float] = {
    "fonction_publique_etat_civile": 1_630_000.0,
    "fonction_publique_etat_militaire": 320_000.0,
}


def partage_fonction_publique_etat() -> dict[str, float]:
    """La part de chaque versant dans les cotisants de l'État, somme un."""
    total = sum(COTISANTS_ETAT_2024.values())
    return {caisse: valeur / total for caisse, valeur in COTISANTS_ETAT_2024.items()}


class EffectifsCotisants:
    """Effectifs de cotisants par caisse et par année, observés puis projetés.

    Même interface que :class:`~.effectifs.EffectifsRetraites`, pour que
    ``poids_effectifs`` s'en serve sans rien savoir de la différence. Chaque
    caisse est une :class:`SerieAnnuelle` : hors de la fenêtre publiée — qui
    commence en 2010 le plus souvent, en 2015 pour la fonction publique d'État,
    en 2019 pour le RCI, en 2023 pour la CNRACL —, la valeur du bord est
    reconduite et tombe au niveau ``estimee``. Avant la bascule, ce n'est pas
    grave : le rapport de recettes y vaut un par construction, et la
    pondération ne mord que de 2026 à 2070, où toutes les caisses sont
    publiées.

    Les deux versants de la fonction publique d'État sont AJOUTÉS à la lecture,
    par la clé de ``COTISANTS_ETAT_2024`` ; la ligne d'un seul tenant reste
    lisible sous ``fonction_publique_etat``.
    """

    def __init__(self, racine: Path) -> None:
        chemin = racine / "reference" / "regimes" / "cotisants.csv"
        valeurs: dict[str, dict[int, ValeurAnnuelle]] = {}
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                annee = int(ligne["annee"])
                valeurs.setdefault(ligne["caisse"], {})[annee] = ValeurAnnuelle(
                    annee=annee,
                    valeur=float(ligne["cotisants"]),
                    fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
                )
        if not valeurs:
            raise ValueError(f"aucune ligne exploitable dans {chemin}")
        etat = valeurs.get(FONCTION_PUBLIQUE_ETAT)
        if etat is None:
            raise ValueError(f"{chemin} ne porte pas {FONCTION_PUBLIQUE_ETAT!r}")
        for caisse, part in partage_fonction_publique_etat().items():
            valeurs[caisse] = {
                annee: ValeurAnnuelle(annee, point.valeur * part, Fiabilite.ESTIMEE)
                for annee, point in etat.items()
            }
        self._series = {
            caisse: SerieAnnuelle(points, nom=f"cotisants_{caisse}")
            for caisse, points in sorted(valeurs.items())
        }

    # -- accès ---------------------------------------------------------------

    def caisses(self) -> tuple[str, ...]:
        return tuple(self._series)

    def serie(self, caisse: str) -> SerieAnnuelle:
        if caisse not in self._series:
            raise KeyError(f"caisse inconnue : {caisse!r}")
        return self._series[caisse]

    def effectif(self, caisse: str, annee: int) -> float:
        return self.serie(caisse)(annee)

    def fiabilite(self, caisse: str, annee: int) -> Fiabilite:
        return self.serie(caisse).fiabilite(annee)

    @property
    def premiere_annee(self) -> int:
        return min(serie.premiere_annee for serie in self._series.values())

    @property
    def derniere_annee(self) -> int:
        return max(serie.derniere_annee for serie in self._series.values())
