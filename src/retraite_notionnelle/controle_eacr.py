"""L'âge des retraités, l'âge où ils partent et leurs conditions de départ, contrôlés sur l'EACR.

CE QUE LA PAGE COÛT NE CONTRÔLAIT PAS. Elle pèse chaque cas type par les
effectifs de sa caisse et le fait servir, en têtes, à toutes les cohortes de
la population de l'INSEE parties à son âge de liquidation (``cout._masses``) :
ni l'âge des retraités qu'elle compte, ni l'âge où ils partent, ni la part qui
part avec une décote ou une surcote ne se confrontaient à un dénombrement.
L'EACR les compte (``tests/temoins/drees_eacr_tables_2026.json``,
``scripts/fetch/drees_eacr_tables.py``) : la table C, tous régimes, les
retraités de droit direct par âge et leur pension, en stock et parmi les
nouveaux retraités de l'année ; la table H, caisse par caisse, les départs au
taux plein, avec une décote, avec une surcote.

LA MESURE. La grille de la page, sous le scénario 1, l'année
:data:`ANNEE_EACR` : chaque cohorte déjà partie, comptée en têtes comme
``grille_large.cohortes_de_l_annee`` les compte — le poids de son cas type
fois son effectif INSEE —, sa pension mensuelle prise comme
``controle_ancetre.pensions_mensuelles`` la prend, en euros de l'année ; puis
rangée par tranche d'âge (:data:`TRANCHES`), et, pour celles qui partent
l'année même, par âge de liquidation (:func:`grille_par_age`). Les cas types
partent tous au taux plein, sauf l'agent de conduite et celui des IEG, qui
partent à l'ouverture de leur statut : la grille n'a ni décote ni surcote au
régime général, à la MSA ni à l'État (:func:`conditions_publiees`).

CE QUE LA CONFRONTATION PEUT DIRE. La part d'une tranche dans le stock dit si
la grille compte ses retraités aux bons âges : chaque cohorte y est comptée
tout entière dès son départ, ce que la couverture de la page suppose
constante (limite n° 2 de ``cout.py``), et chaque cas type n'a qu'un âge de
départ. Le profil de la pension selon l'âge dit si les générations anciennes
touchent moins, comme elles le font. Les tables comptent des personnes, tous
régimes, et la grille des têtes de caisse (limite n° 1) : seules les parts et
les rapports se comparent, non les niveaux. Rien de ce module n'entre dans un
chiffre de la page.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .somme import somme_ordonnee

#: L'année que les tables du 26 mai 2026 décrivent au plus récent.
ANNEE_EACR = 2024

#: Les tranches d'âge de la confrontation : ``(premier âge, dernier âge, nom)``.
#: La table C ne détaille pas les âges au-delà de 95 ans, qu'elle réunit sous
#: « plus de 95 ».
TRANCHES: tuple[tuple[int, int, str], ...] = (
    (0, 59, "moins_60"), (60, 64, "60_64"), (65, 69, "65_69"), (70, 74, "70_74"),
    (75, 79, "75_79"), (80, 84, "80_84"), (85, 89, "85_89"), (90, 95, "90_95"),
    (96, 200, "plus_95"))

#: Le libellé de la table C pour les âges qu'elle ne détaille pas.
PLUS_DE_95 = "plus de 95"

#: Les âges de liquidation que la confrontation des nouveaux retraités
#: distingue ; les autres se réunissent en deçà et au-delà.
AGES_DE_DEPART = tuple(range(60, 68))


def tranche_de(age: int) -> str:
    """La tranche de :data:`TRANCHES` où tombe ``age``."""
    for premier, dernier, nom in TRANCHES:
        if premier <= age <= dernier:
            return nom
    raise ValueError(f"âge hors des tranches : {age}")


def cle_de_depart(age: int) -> str:
    """L'âge de liquidation sous sa clé : ``"moins_60"``, ``"60"``…, ``"68_plus"``."""
    if age < AGES_DE_DEPART[0]:
        return "moins_60"
    if age > AGES_DE_DEPART[-1]:
        return f"{AGES_DE_DEPART[-1] + 1}_plus"
    return str(age)


def _age(libelle: str) -> int | None:
    if libelle == PLUS_DE_95:
        return 96
    return int(libelle) if libelle.isdigit() else None


def _regrouper(lignes: Iterable[tuple[str, float, float | None]]
               ) -> dict[str, tuple[float, float | None]]:
    """``(clé, effectif, pension)`` réunis par clé : l'effectif, et la pension
    moyenne de ceux dont la pension est connue."""
    tetes: dict[str, list[float]] = {}
    euros: dict[str, list[tuple[float, float]]] = {}
    for cle, effectif, pension in lignes:
        tetes.setdefault(cle, []).append(effectif)
        if pension is not None:
            euros.setdefault(cle, []).append((effectif, pension))
    sortie = {}
    for cle in tetes:
        connus = euros.get(cle, [])
        poids = somme_ordonnee(e for e, _ in connus)
        sortie[cle] = (somme_ordonnee(tetes[cle]),
                       somme_ordonnee(e * p for e, p in connus) / poids if poids else None)
    return sortie


def publie_par_tranche(serie: Mapping[str, list]) -> dict[str, tuple[float, float | None]]:
    """Une série de la table C, ``{âge: [effectif, pension]}``, par tranche
    d'âge : l'effectif et la pension moyenne. La ligne « Ensemble » est
    ignorée : quelques âges secrétisés manquent au détail, moins d'un pour
    cent des retraités."""
    return _regrouper((tranche_de(age), effectif, pension)
                      for libelle, (effectif, pension) in serie.items()
                      if (age := _age(libelle)) is not None)


def publie_par_depart(serie: Mapping[str, list]) -> dict[str, tuple[float, float | None]]:
    """Les nouveaux retraités de la table C par âge de liquidation (:func:`cle_de_depart`)."""
    return _regrouper((cle_de_depart(age), effectif, pension)
                      for libelle, (effectif, pension) in serie.items()
                      if (age := _age(libelle)) is not None)


@dataclass(frozen=True)
class Cohorte:
    """Une cohorte de la grille l'année du contrôle : son cas type et la
    génération de la grille qui la porte, son âge, son âge de liquidation, ses
    têtes, sa pension mensuelle, et si elle part l'année même."""

    code: str
    generation: int
    age: int
    age_liquidation: int
    tetes: float
    pension: float
    nouvelle: bool


def cohortes(pensionnes, poids: Mapping[str, float], population, revalorisation,
             vers_euros_annee: float, annee: int = ANNEE_EACR) -> list[Cohorte]:
    """Les cohortes de la grille déjà parties en ``annee`` : cinq par génération
    de la grille, chacune pesée du poids de son cas type fois son effectif
    INSEE, sa pension revalorisée et portée à sa complétude, en euros de
    ``annee`` par mois."""
    from .cout import _DEMI_TRANCHE, coefficient_servi

    sortie = []
    for pensionne in pensionnes:
        part = poids.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            liquidation = pensionne.annee_liquidation + decalage
            if annee < liquidation:
                continue
            age = annee - pensionne.generation - decalage
            effectif = population.effectif(age, annee)
            if effectif <= 0.0:
                continue
            pension = (pensionne.pensions["actuel"] * pensionne.completude(decalage)
                       * coefficient_servi(pensionne.parts_regimes, revalorisation,
                                           liquidation, annee))
            sortie.append(Cohorte(pensionne.code, pensionne.generation, age,
                                  pensionne.annee_liquidation - pensionne.generation,
                                  part * effectif, pension * vers_euros_annee / 12.0,
                                  liquidation == annee))
    return sortie


def grille_par_tranche(lot: Iterable[Cohorte]) -> dict[str, tuple[float, float | None]]:
    """Le stock de la grille par tranche d'âge : ses têtes, sa pension moyenne."""
    return _regrouper((tranche_de(c.age), c.tetes, c.pension) for c in lot)


def grille_par_age(lot: Iterable[Cohorte]) -> dict[str, tuple[float, float | None]]:
    """Les nouveaux retraités de la grille par âge de liquidation."""
    return _regrouper((cle_de_depart(c.age_liquidation), c.tetes, c.pension)
                      for c in lot if c.nouvelle)


def parts(groupes: Mapping[str, tuple[float, float | None]]) -> dict[str, float]:
    """La part de chaque groupe dans leur total."""
    total = somme_ordonnee(e for e, _ in groupes.values())
    return {cle: effectif / total for cle, (effectif, _) in groupes.items()}


def moyenne(groupes: Mapping[str, tuple[float, float | None]]) -> float:
    """La pension moyenne de tous les groupes réunis."""
    connus = [(e, p) for e, p in groupes.values() if p is not None]
    return somme_ordonnee(e * p for e, p in connus) / somme_ordonnee(e for e, _ in connus)


def age_moyen(lot: Iterable[Cohorte]) -> float:
    """L'âge moyen de liquidation des nouveaux retraités de la grille."""
    nouvelles = [c for c in lot if c.nouvelle]
    return (somme_ordonnee(c.tetes * c.age_liquidation for c in nouvelles)
            / somme_ordonnee(c.tetes for c in nouvelles))


def age_moyen_publie(serie: Mapping[str, list]) -> float:
    """L'âge moyen de liquidation des nouveaux retraités de la table C, chacun
    à son âge au 31 décembre ; « plus de 95 » compté à 96 ans."""
    lignes = [(age, effectif) for libelle, (effectif, _) in serie.items()
              if (age := _age(libelle)) is not None]
    return somme_ordonnee(a * e for a, e in lignes) / somme_ordonnee(e for _, e in lignes)


@dataclass(frozen=True)
class Conditions:
    """Les départs d'une caisse, l'année du contrôle : la part au taux plein,
    avec une décote, avec une surcote, en flux et en stock."""

    caisse: str
    champ: str
    taux_plein: float
    decote: float
    surcote: float | None


def conditions_publiees(temoin: Mapping, annee: int = ANNEE_EACR,
                        sexe: str = "ensemble") -> list[Conditions]:
    """Chaque caisse de la table H qui porte ``annee``, en flux puis en stock,
    les parts rapportées à leur somme ; la surcote ``None`` là où la table ne
    la donne pas."""
    sortie = []
    for code, champs in sorted(temoin["conditions_liquidation"]["series"].items()):
        for champ in ("flux", "stock"):
            ligne = champs.get(champ, {}).get(sexe, {}).get(str(annee))
            if not ligne:
                continue
            surcote = ligne.get("surcote")
            total = ligne["taux_plein"] + ligne["decote"] + (surcote or 0.0)
            sortie.append(Conditions(code, champ, ligne["taux_plein"] / total,
                                     ligne["decote"] / total,
                                     None if surcote is None else surcote / total))
    return sortie


def controle(parametres=None) -> list[Cohorte]:
    """Sous ces paramètres, sur les données du dépôt : les cohortes de la
    grille de la page Coût en :data:`ANNEE_EACR`, à ses poids. La grille et
    les poids sont ceux que la mémoire des calculs garde pour la page."""
    from . import Parametres, memoire
    from . import cout as module
    from .castypes import GRILLE_DU_COUT
    from .donnees.population import Population
    from .simulateur import Simulateur

    parametres = parametres if parametres is not None else Parametres()
    simulateur = Simulateur(parametres)
    pensionnes, _ = memoire.memoriser_pour(
        parametres, ("grille_du_cout", parametres, GRILLE_DU_COUT, "droit"),
        lambda: module._pensionnes(simulateur, GRILLE_DU_COUT, "droit"))
    cout = memoire.cout(parametres)
    revalorisation = module.RevalorisationServie(
        simulateur.pour_la_projection(),
        min(p.annee_liquidation for p in pensionnes) - module._DEMI_TRANCHE,
        module.HORIZON)
    return cohortes(
        pensionnes, cout.poids,
        Population(parametres.racine_donnees, parametres.hypothese_esperance_vie),
        revalorisation,
        simulateur.macro.coefficient_prix(parametres.annee_euros_constants, ANNEE_EACR))
