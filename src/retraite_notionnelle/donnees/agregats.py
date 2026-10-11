"""Ce que les trois pages qui agrègent lisent du modèle, fabriqué sous la référence.

POURQUOI CE FICHIER EXISTE. Coût, Carrières types et Droits non cotisés
croisent treize carrières types avec sept générations, et chiffrent ce que
chaque système coûterait, année par année jusqu'en 2070. Elles se calculaient
chez le lecteur, par le portage JavaScript du coût, sous les réglages de
l'adresse : de trois à huit secondes à la première visite. Le propriétaire a
retiré leurs réglages le 10 octobre 2026 (action 150) : elles ne montrent plus
que la référence. Ce qu'elles lisent du modèle est donc calculé une fois, par
``scripts/construire_donnees.py``, écrit dans ``data/derive/agregats.json``,
embarqué dans le paquet que le navigateur charge, et lu ici et dans
``moteur/js/agregats.js`` par les mêmes accesseurs.

CE QUI EST FIGÉ, ET CE QUI NE L'EST PAS. Tout ce qu'une règle du modèle
décide : la grille des cas types, l'âge auquel chacun part. Ce qui n'est
qu'une donnée lue — les comptes du COR, les dépenses publiées, la
distribution des pensions — reste dans le paquet, où les pages la lisent
comme avant. Les lecteurs ne calculent rien qu'une règle décide : ils rendent
ce que la table porte. Une lecture qu'elle ne porte pas lève une erreur, plutôt
que de rendre un zéro : une page qui la demanderait se tromperait sans bruit.

LE PYTHON GARDE TOUS SES RÉGLAGES. La table ne vaut que pour la référence,
celle de ``Parametres()`` ; le modèle se calcule toujours sous toute autre
règle, et c'est le simulateur, sur une carrière, qui les montre au lecteur.

Chaque partie a ses deux moitiés côte à côte : ``figer_*`` écrit la table
depuis les objets du modèle, en n'y lisant que leurs accesseurs, et le lecteur
la rend sous ces mêmes accesseurs. ``tests/test_agregats.py`` vérifie que les
deux disent la même chose que le modèle.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


def _lire(table: dict, cle, quoi: str):
    """``table[cle]``, ou une erreur qui dit ce que la table ne porte pas."""
    try:
        return table[cle]
    except KeyError:
        raise KeyError(f"{quoi} absent de la table figée : {cle!r}") from None


def _cle_grille(code: str, generation: int) -> str:
    """La clé d'une case de la grille dans la table, celle du portage."""
    return f"{code}|{generation}"


# -- les carrières types -------------------------------------------------------


@dataclass(frozen=True)
class CarriereFigee:
    """D'une carrière simulée, ce que les pages en lisent : l'année du départ."""

    annee_liquidation: int


@dataclass(frozen=True)
class ComparaisonFigee:
    """Une case de la grille : ce qu'en lisent les pages, sous les accesseurs
    de ``simulateur.Comparaison``."""

    carriere: CarriereFigee
    _carrieres: dict[str, CarriereFigee] = field(default_factory=dict)
    _variations: dict[str, float] = field(default_factory=dict)

    def carriere_de(self, scenario: str) -> CarriereFigee:
        return _lire(self._carrieres, scenario, "carrière du scénario")

    def variation_totale(self, scenario: str) -> float:
        return _lire(self._variations, scenario, "écart du scénario")


@dataclass(frozen=True)
class CasFige:
    """Un cas type, tel que les pages le nomment, et l'âge où chaque
    génération le fait partir."""

    code: str
    libelle: str
    commentaire: str
    _ages: dict[int, float] = field(default_factory=dict)

    def age_liquidation(self, generation: int) -> float:
        return _lire(self._ages, generation, "âge de départ de la génération")


@dataclass(frozen=True)
class CasTypesFiges:
    """La grille cas type × génération, sous les accesseurs de
    ``castypes.ResultatCasTypes``, et les cas qui la composent."""

    generations: tuple[int, ...]
    cas: tuple[CasFige, ...]
    resultats: dict[tuple[str, int], ComparaisonFigee]
    echecs: dict[tuple[str, int], str]

    def cas_type(self, code: str) -> CasFige:
        for cas in self.cas:
            if cas.code == code:
                return cas
        raise KeyError(f"cas type absent de la table figée : {code!r}")


def figer_cas_types(resultat, simulateur, cas_types, generations,
                    scenarios) -> dict:
    """La grille de ``castypes.calculer_cas_types``, et l'âge de départ de
    chaque case, pour les ``scenarios`` que les pages comparent."""
    return {
        "generations": list(generations),
        "cas": [
            {
                "code": cas.code,
                "libelle": cas.libelle,
                "commentaire": cas.commentaire,
                "ages": [cas.age_liquidation_pour(simulateur, generation)
                         for generation in generations],
            }
            for cas in cas_types
        ],
        "resultats": {
            _cle_grille(code, generation): {
                "annee_liquidation": comparaison.carriere.annee_liquidation,
                "annees_liquidation": {
                    scenario: comparaison.carriere_de(scenario).annee_liquidation
                    for scenario in scenarios
                },
                "variations": {scenario: comparaison.variation_totale(scenario)
                               for scenario in scenarios},
            }
            for (code, generation), comparaison in resultat.resultats.items()
        },
        "echecs": {_cle_grille(code, generation): motif
                   for (code, generation), motif in resultat.echecs.items()},
    }


def _cas_types(brut: dict) -> CasTypesFiges:
    generations = tuple(int(generation) for generation in brut["generations"])

    def case(cle: str) -> tuple[str, int]:
        code, generation = cle.split("|")
        return code, int(generation)

    return CasTypesFiges(
        generations=generations,
        cas=tuple(
            CasFige(
                code=cas["code"], libelle=cas["libelle"],
                commentaire=cas["commentaire"],
                _ages=dict(zip(generations, (float(age) for age in cas["ages"]))),
            )
            for cas in brut["cas"]
        ),
        resultats={
            case(cle): ComparaisonFigee(
                carriere=CarriereFigee(int(valeur["annee_liquidation"])),
                _carrieres={scenario: CarriereFigee(int(annee)) for scenario, annee
                            in valeur["annees_liquidation"].items()},
                _variations={scenario: float(ecart)
                             for scenario, ecart in valeur["variations"].items()},
            )
            for cle, valeur in brut["resultats"].items()
        },
        echecs={case(cle): motif for cle, motif in brut["echecs"].items()},
    )


# -- la table ------------------------------------------------------------------


@dataclass(frozen=True)
class AgregatsFiges:
    """Ce que les trois pages qui agrègent lisent, tel que la table le porte."""

    cas_types: CasTypesFiges


def depuis_dictionnaire(donnees: dict) -> AgregatsFiges:
    """Reconstruit la table, JSON du dépôt ou clé du paquet."""
    return AgregatsFiges(cas_types=_cas_types(donnees["cas_types"]))


def charger_agregats(racine: Path) -> AgregatsFiges:
    """La table du dépôt. ``scripts/construire_donnees.py`` l'écrit."""
    chemin = Path(racine) / "derive" / "agregats.json"
    with chemin.open(encoding="utf-8") as fichier:
        return depuis_dictionnaire(json.load(fichier))
