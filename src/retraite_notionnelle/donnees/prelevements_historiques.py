"""L'histoire des prélèvements sur les pensions et sur les salaires.

La fiche de paie du site et la pension nette qu'il affiche sont aux taux de
l'année courante (``prelevements_remuneration.yaml``). Les indicateurs de cycle
de vie nets (:mod:`~retraite_notionnelle.cycle_de_vie`) suivent une carrière et
une retraite sur des décennies : la CSG n'existait pas avant 1991, la
cotisation maladie des pensions a valu jusqu'à 3,8 % sur les complémentaires,
le salarié du privé payait 6,8 % de maladie en 1992. Ce module lit ces taux,
marche par marche, dans ``data/reference/legislation/prelevements_historiques.yaml``,
qu'écrit ``scripts/fetch/ipp_prelevements_sociaux.py`` depuis les barèmes de
l'IPP.

Une année qui change de taux prélève la moyenne de ses douze mois, comme les
contributions d'équilibre (:mod:`~retraite_notionnelle.contributions_equilibre`).

L'indépendant a ses barèmes : la maladie des artisans et commerçants ou celle
des professions libérales, la cotisation d'allocations familiales des
travailleurs indépendants, et la CSG et la CRDS de l'activité, sans abattement,
sur son revenu augmenté de ses cotisations jusqu'en 2024. Un barème
d'indépendant s'écrit en tranches qui s'ajoutent (:data:`TRANCHES`) et, depuis
2015, en paliers : en deçà d'un certain revenu, un taux réduit sur tout le
revenu, interpolé comme :class:`~retraite_notionnelle.remuneration.BaremeProgressif`
l'interpole pour la fiche de paie.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from ..somme import somme_ordonnee
from .chargement import charger_yaml

CHEMIN = Path("reference") / "legislation" / "prelevements_historiques.yaml"

#: Les familles de la fiche de paie que l'histoire couvre, par le profil de la
#: fiche (``prelevements_remuneration.yaml``, ``profils``) : le salarié du privé,
#: l'agent non titulaire, salarié du régime général pour sa maladie et agent
#: public pour la solidarité, et l'agent à retenue — fonctionnaire ou agent d'un
#: régime spécial, dont les taux de maladie sont ceux des agents de l'État.
#: L'indépendant a la sienne selon ses régimes de base (:func:`famille_de_la_fiche`).
FAMILLES = {"salarie_prive": "prive", "salarie_ircantec": "contractuel",
            "agent_seul": "agent"}

#: Les familles d'indépendants : l'artisan et le commerçant, sous la maladie
#: des artisans et commerçants, que l'indemnité journalière de 1995 à 2000 sépare ;
#: le libéral de la CNAVPL (L. 640-1) et l'avocat (L. 651-1), sous celle des
#: professions libérales, que l'indemnité journalière de 2021 sépare.
FAMILLES_INDEPENDANTES = ("artisan", "commercant", "liberal", "avocat")

#: Les régimes de base qui font d'un indépendant un avocat, un libéral, un
#: artisan ; les autres sont commerçants — l'Organic, le RSI, et depuis 2018 la
#: sécurité sociale des indépendants au régime général.
REGIMES_AVOCATS = frozenset({"cnbf"})
REGIMES_LIBERAUX = frozenset({"cnavpl"})
REGIMES_ARTISANS = frozenset({"cancava"})

#: Les tranches d'un barème d'indépendant, par la colonne qui porte leur taux :
#: leurs bornes, en plafonds de l'année, ``None`` pour l'infini. Elles
#: s'ajoutent : 3,10 % sous le plafond et 8,45 % sous cinq plafonds font
#: 11,55 % sous le plafond, 8,45 % au-dessus.
TRANCHES = {
    "tout_revenu": (0.0, None), "sous_plafond": (0.0, 1.0),
    "sous_trois_plafonds": (0.0, 3.0), "sous_quatre_plafonds": (0.0, 4.0),
    "sous_cinq_plafonds": (0.0, 5.0), "au_dela_de_trois_plafonds": (3.0, None),
    "au_dela_de_cinq_plafonds": (5.0, None),
}

#: L'indemnité journalière, que le taux réduit ne touche pas : ses bornes, et
#: les familles qui la paient.
INDEMNITES = {
    "ij_sous_cinq_plafonds": ((0.0, 5.0), ("artisan", "commercant")),
    "ij_artisans_sous_cinq_plafonds": ((0.0, 5.0), ("artisan",)),
    "ij_sous_trois_plafonds": ((0.0, 3.0), ("liberal",)),
}


def famille_de_la_fiche(profil: str | None, regimes) -> str | None:
    """La famille dont l'histoire prélève une fiche de paie : celle du profil
    (:data:`FAMILLES`), ou, pour un indépendant, celle de ses régimes de base de
    l'année (:data:`FAMILLES_INDEPENDANTES`). ``None`` hors de l'histoire."""
    if profil != "independant":
        return FAMILLES.get(profil)
    regimes = frozenset(regimes)
    if regimes & REGIMES_AVOCATS:
        return "avocat"
    if regimes & REGIMES_LIBERAUX:
        return "liberal"
    if regimes & REGIMES_ARTISANS:
        return "artisan"
    return "commercant"


def _tranche(revenu: float, plafond: float, bas: float, haut: float | None) -> float:
    plus_haut = revenu if haut is None else min(revenu, haut * plafond)
    return max(plus_haut - bas * plafond, 0.0)


def _taux_progressif(paliers, en_plafonds: float) -> float:
    """Le taux réduit, sur tout le revenu, à ce niveau : interpolé entre deux
    paliers, celui du premier en deçà, celui du dernier au-delà — la règle de
    :meth:`~retraite_notionnelle.remuneration.BaremeProgressif.taux`."""
    precedent_seuil, precedent_taux = paliers[0]
    if en_plafonds <= precedent_seuil:
        return precedent_taux
    for seuil, taux in paliers[1:]:
        if en_plafonds <= seuil:
            largeur = seuil - precedent_seuil
            if largeur <= 0:
                return taux
            part = (en_plafonds - precedent_seuil) / largeur
            return precedent_taux + part * (taux - precedent_taux)
        precedent_seuil, precedent_taux = seuil, taux
    return precedent_taux


def bareme_independant(valeurs: dict, revenu: float, plafond: float) -> float:
    """Ce qu'un barème d'indépendant prélève d'un revenu annuel, indemnité
    journalière à part : son taux réduit sur tout le revenu en deçà de
    ``progressif_jusqu_a`` plafonds (partout sans lui), ses tranches au-delà,
    et le seuil en euros de la cotisation familiale de 1974 à 1982."""
    paliers = valeurs.get("paliers")
    jusqu_a = valeurs.get("progressif_jusqu_a")
    if paliers and (not jusqu_a or revenu < jusqu_a * plafond):
        return _taux_progressif(paliers, revenu / plafond) * revenu
    total = somme_ordonnee(valeurs.get(cle, 0.0) * _tranche(revenu, plafond, bas, haut)
                           for cle, (bas, haut) in TRANCHES.items())
    seuil = valeurs.get("seuil_euros", 0.0)
    return (total + valeurs.get("sous_seuil", 0.0) * min(revenu, seuil)
            + valeurs.get("du_seuil_au_plafond", 0.0) * max(min(revenu, plafond) - seuil, 0.0))


@dataclass(frozen=True)
class Serie:
    """Les marches d'un prélèvement, de la plus ancienne à la plus récente."""

    nom: str
    #: Chaque marche : sa date, et ses taux — ses ``paliers`` en couples.
    marches: tuple[tuple[dt.date, dict[str, float | tuple]], ...]
    #: La première marche vaut-elle en deçà d'elle ? Vrai pour la maladie, que
    #: les barèmes de l'IPP ne prennent qu'en 1967 ; faux pour ce qui est né à
    #: sa première marche.
    tenue_avant: bool = False

    def en_vigueur(self, jour: dt.date) -> dict[str, float]:
        retenues: dict[str, float] = {}
        for debut, valeurs in self.marches:
            if debut > jour:
                break
            retenues = valeurs
        if not retenues and self.tenue_avant and self.marches:
            return self.marches[0][1]
        return retenues

    def valeur(self, jour: dt.date, cle: str = "taux") -> float:
        return self.en_vigueur(jour).get(cle, 0.0)


def _serie(nom: str, marches, tenue_avant: bool) -> Serie:
    lues = []
    for marche in marches:
        valeurs = {cle: (tuple((float(seuil), float(taux)) for seuil, taux in valeur)
                         if cle == "paliers" else float(valeur))
                   for cle, valeur in marche.items() if cle not in ("depuis", "texte")}
        lues.append((dt.date.fromisoformat(str(marche["depuis"])), valeurs))
    return Serie(nom=nom, marches=tuple(sorted(lues, key=lambda m: m[0])),
                 tenue_avant=tenue_avant)


def _mois(annee: int) -> tuple[dt.date, ...]:
    return tuple(dt.date(annee, rang, 1) for rang in range(1, 13))


@dataclass(frozen=True)
class PrelevementsHistoriques:
    """Les prélèvements des pensions et des salaires, date par date."""

    pensions: dict[str, Serie]
    salaires: dict[str, Serie]
    lu_le: str
    independants: dict[str, Serie] = field(default_factory=dict)

    # -- les pensions ------------------------------------------------------

    def taux_pension(self, jour: dt.date, part_regime_general: float,
                     part_complementaires: float) -> float:
        """Ce que les prélèvements du ``jour`` retirent à une pension, en part
        du brut, au taux plein de CSG : la CSG, la CRDS, la CASA, la maladie
        du régime général sur sa part de la pension, celle des complémentaires
        sur la leur."""
        p = self.pensions
        return (p["csg_taux_plein"].valeur(jour) + p["crds"].valeur(jour)
                + p["casa"].valeur(jour)
                + p["maladie_regime_general"].valeur(jour) * part_regime_general
                + p["maladie_complementaires"].valeur(jour) * part_complementaires)

    def taux_pension_annuel(self, annee: int, part_regime_general: float,
                            part_complementaires: float) -> float:
        """La moyenne des douze mois de l'année."""
        return somme_ordonnee(self.taux_pension(jour, part_regime_general, part_complementaires)
                              for jour in _mois(annee)) / 12.0

    def taux_csg_pension(self, jour: dt.date, taux: str) -> float:
        """La CSG d'une pension, au taux ``plein``, ``median`` ou ``reduit`` ;
        zéro pour un taux qui n'existe pas encore."""
        return self.pensions[f"csg_taux_{taux}"].valeur(jour)

    # -- les salaires ------------------------------------------------------

    def _assiette_csg(self, jour: dt.date, brut: float, plafond: float) -> float:
        csg = self.salaires["csg"].en_vigueur(jour)
        abattement = (csg.get("abattement", 0.0) * brut
                      + csg.get("abattement_jusqu_a_quatre_plafonds", 0.0)
                      * min(brut, 4.0 * plafond))
        return brut - abattement

    def _maladie(self, jour: dt.date, serie: str, brut: float, plafond: float) -> float:
        taux = self.salaires[serie].en_vigueur(jour)
        return (taux.get("tout_salaire", 0.0) * brut
                + taux.get("sous_plafond", 0.0) * min(brut, plafond)
                + taux.get("au_dela_du_plafond", 0.0) * max(brut - plafond, 0.0))

    def _chomage(self, jour: dt.date, brut: float, plafond: float) -> float:
        taux = self.salaires["chomage_prive"].en_vigueur(jour)
        return (taux.get("tout_salaire", 0.0) * brut
                + taux.get("sous_plafond", 0.0) * min(brut, plafond)
                + taux.get("de_un_a_quatre_plafonds", 0.0)
                * min(max(brut - plafond, 0.0), 3.0 * plafond))

    def _solidarite(self, jour: dt.date, brut: float, plafond: float,
                    cotisations: float) -> float:
        """La contribution exceptionnelle de solidarité des agents publics :
        son taux sur la rémunération nette des cotisations, dans la limite de
        quatre plafonds, quand le mois dépasse le seuil d'assujettissement."""
        taux = self.salaires["solidarite_public"].en_vigueur(jour)
        if not taux.get("taux") or brut / 12.0 <= taux.get("seuil_mensuel", 0.0):
            return 0.0
        return taux["taux"] * min(max(brut - cotisations, 0.0), 4.0 * plafond)

    # -- les indépendants --------------------------------------------------

    def maladie_independant(self, famille: str, jour: dt.date, revenu: float,
                            plafond: float) -> float:
        """La cotisation maladie du ``jour`` d'un revenu annuel d'indépendant,
        indemnité journalière comprise : celle des artisans et commerçants, ou
        celle des professions libérales pour le libéral et l'avocat."""
        nom = ("maladie_professions_liberales" if famille in ("liberal", "avocat")
               else "maladie_artisans_commercants")
        valeurs = self.independants[nom].en_vigueur(jour)
        indemnites = somme_ordonnee(
            valeurs.get(cle, 0.0) * _tranche(revenu, plafond, bas, haut)
            for cle, ((bas, haut), familles) in INDEMNITES.items() if famille in familles)
        return bareme_independant(valeurs, revenu, plafond) + indemnites

    def famille_independant(self, jour: dt.date, revenu: float, plafond: float) -> float:
        """La cotisation d'allocations familiales du ``jour`` d'un revenu annuel
        d'indépendant."""
        return bareme_independant(self.independants["famille"].en_vigueur(jour), revenu,
                                  plafond)

    def _independant(self, famille: str, jour: dt.date, revenu: float, plafond: float,
                     cotisations: float) -> float:
        """La maladie, les allocations familiales, et la CSG et la CRDS de
        l'activité sans abattement, sur le revenu augmenté, jusqu'en 2024, des
        cotisations personnelles de l'année (L. 136-3)."""
        maladie = self.maladie_independant(famille, jour, revenu, plafond)
        allocations = self.famille_independant(jour, revenu, plafond)
        assiette = revenu
        if self.independants["assiette_csg"].valeur(jour, "cotisations_ajoutees"):
            assiette += cotisations + maladie + allocations
        taux = self.salaires["csg"].valeur(jour) + self.salaires["crds"].valeur(jour)
        return maladie + allocations + taux * assiette

    def hors_retraite(self, famille: str, jour: dt.date, brut: float, plafond: float,
                      retraite_salarie: float = 0.0) -> float:
        """Ce que les prélèvements salariaux hors retraite du ``jour`` retirent
        d'un brut annuel, sous un plafond annuel : la CSG et la CRDS sur le
        brut abattu, et selon la famille (:data:`FAMILLES`) la maladie, le
        veuvage, l'assurance chômage, la contribution de solidarité.

        Pour un indépendant (:data:`FAMILLES_INDEPENDANTES`), ``brut`` est son
        revenu, et ``retraite_salarie`` ses cotisations que l'histoire ne refait
        pas — la retraite, l'invalidité-décès —, que sa CSG d'avant 2025 ajoute
        à son assiette."""
        if famille in FAMILLES_INDEPENDANTES:
            return self._independant(famille, jour, brut, plafond, retraite_salarie)
        assiette = self._assiette_csg(jour, brut, plafond)
        total = (self.salaires["csg"].valeur(jour) + self.salaires["crds"].valeur(jour)) * assiette
        if famille in ("prive", "contractuel"):
            maladie = self._maladie(jour, "maladie_prive", brut, plafond)
            total += maladie + self._maladie(jour, "veuvage_prive", brut, plafond)
        else:
            maladie = self._maladie(jour, "maladie_etat", brut, plafond)
            total += maladie
        if famille == "prive":
            total += self._chomage(jour, brut, plafond)
        else:
            total += self._solidarite(jour, brut, plafond, retraite_salarie + maladie)
        return total

    def hors_retraite_annuel(self, famille: str, annee: int, brut: float, plafond: float,
                             retraite_salarie: float = 0.0) -> float:
        """La moyenne des douze mois de l'année."""
        return somme_ordonnee(self.hors_retraite(famille, jour, brut, plafond, retraite_salarie)
                              for jour in _mois(annee)) / 12.0


@lru_cache(maxsize=4)
def _charger(chemin: str, signature: tuple) -> PrelevementsHistoriques:
    contenu = charger_yaml(Path(chemin))
    tenues = set(contenu.get("tenues_avant_leur_premiere_marche") or ())
    return PrelevementsHistoriques(
        pensions={nom: _serie(nom, marches, nom in tenues)
                  for nom, marches in contenu["pensions"].items()},
        salaires={nom: _serie(nom, marches, nom in tenues)
                  for nom, marches in contenu["salaires"].items()},
        lu_le=str(contenu.get("lu_le", "")),
        independants={nom: _serie(nom, marches, nom in tenues)
                      for nom, marches in (contenu.get("independants") or {}).items()},
    )


def charger_prelevements_historiques(racine_donnees: Path) -> PrelevementsHistoriques:
    """L'histoire des prélèvements, gardée tant que le fichier ne change pas."""
    chemin = Path(racine_donnees) / CHEMIN
    etat = chemin.stat()
    return _charger(str(chemin), (etat.st_mtime_ns, etat.st_size))
