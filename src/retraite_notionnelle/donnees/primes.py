"""Les primes que la loi assujettit à la retenue pour pension, année par année
(``legislation/primes_soumises_a_retenue.yaml``) : l'indemnité de sujétions
spéciales des policiers, la prime spéciale de sujétion des aides-soignants,
l'indemnité de feu des sapeurs-pompiers professionnels.

La part de primes d'une ligne reste l'assiette du RAFP, les primes que la
pension ne compte pas (décret n° 2004-569, article 2). Le reste de la
rémunération est le traitement et la part soumise à retenue de la prime, qui se
partagent au taux de la prime et à la part que l'année en compte
(:meth:`PrimesSoumises.parts`) : l'assiette de la retenue ordinaire n'en change
pas, celle des retenues et contributions supplémentaires du statut s'y lit
(:meth:`PrimesSoumises.taux_supplementaires`), et le RAFP plafonne ses primes
au traitement seul. Ce que la pension fait de la prime, à sa date d'effet, est
dans les fiches que ``droit/primes.py`` lit.

Action 138, étape 17, douzième partie. Jumeau : ``moteur/js/primes.js``.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path

from ..somme import somme_ordonnee
from .chargement import charger_yaml, une_fois_par_instantane

#: Les assiettes d'une retenue ou d'une contribution supplémentaire.
ASSIETTES = ("remuneration_soumise", "traitement_et_prime", "traitement", "prime_soumise")


@dataclass(frozen=True)
class Parts:
    """Ce que la rémunération d'une ligne porte, en parts d'elle."""

    #: Le traitement indiciaire.
    traitement: float
    #: La prime perçue, entière.
    prime: float = 0.0
    #: Sa part soumise à retenue : celle que l'assiette et la pension comptent.
    soumise: float = 0.0

    def assiette(self, nom: str) -> float:
        """La part de la rémunération qu'une assiette supplémentaire prend."""
        if nom == "remuneration_soumise":
            return self.traitement + self.soumise
        if nom == "traitement_et_prime":
            return self.traitement + self.prime
        if nom == "traitement":
            return self.traitement
        if nom == "prime_soumise":
            return self.soumise
        raise ValueError(f"assiette inconnue : {nom!r}")


def _jour(valeur) -> dt.date:
    return valeur if isinstance(valeur, dt.date) else dt.date.fromisoformat(str(valeur))


def _premiers_du_mois(annee: int) -> tuple[dt.date, ...]:
    return tuple(dt.date(annee, mois, 1) for mois in range(1, 13))


@dataclass(frozen=True)
class Prime:
    """Une prime soumise à retenue : les statuts qui la perçoivent, le régime
    qui la compte, son taux en part du traitement, et la part que chaque année
    en compte."""

    code: str
    fiche: str
    statuts: frozenset[str]
    regime: str
    taux: tuple[tuple[dt.date, float], ...]
    integration: tuple[tuple[int, float], ...]

    def taux_au(self, jour: dt.date) -> float:
        """Le taux en vigueur ce jour ; nul avant le premier."""
        valeur = 0.0
        for depuis, taux in self.taux:
            if depuis <= jour:
                valeur = taux
        return valeur

    def taux_annuel(self, annee: int) -> float:
        """La moyenne des taux en vigueur au premier de chaque mois de l'année."""
        return somme_ordonnee(self.taux_au(jour) for jour in _premiers_du_mois(annee)) / 12.0

    def part_comptee(self, annee: int) -> float:
        """La part de la prime que l'année compte ; nulle avant l'intégration."""
        part = 0.0
        for depuis, valeur in self.integration:
            if depuis <= annee:
                part = valeur
        return part


@dataclass(frozen=True)
class Supplementaire:
    """Une retenue, ou une contribution, supplémentaire du statut."""

    statuts: frozenset[str]
    regime: str
    motif: str
    assiette: str
    #: (depuis, taux salarié, taux employeur), un taux valant jusqu'au suivant.
    taux: tuple[tuple[dt.date, float, float], ...]

    def taux_au(self, jour: dt.date) -> tuple[float, float]:
        valeur = (0.0, 0.0)
        for depuis, salarie, employeur in self.taux:
            if depuis <= jour:
                valeur = (salarie, employeur)
        return valeur

    def taux_annuels(self, annee: int) -> tuple[float, float]:
        """Les taux salarié et employeur, en moyenne des mois de l'année."""
        mois = [self.taux_au(jour) for jour in _premiers_du_mois(annee)]
        return (somme_ordonnee(s for s, _ in mois) / 12.0,
                somme_ordonnee(e for _, e in mois) / 12.0)


@dataclass(frozen=True)
class PrimesSoumises:
    """La table des primes soumises à retenue et des retenues supplémentaires."""

    primes: tuple[Prime, ...] = ()
    supplementaires: tuple[Supplementaire, ...] = ()

    def prime(self, statut: str) -> Prime | None:
        """La prime soumise à retenue que ce statut perçoit, s'il en perçoit une."""
        return next((p for p in self.primes if statut in p.statuts), None)

    def parts(self, statut: str, annee: int, part_primes: float) -> Parts:
        """Le partage de la rémunération d'une année : le traitement t,
        (1 − part de primes) / (1 + taux × part comptée), la prime taux × t et
        sa part soumise taux × part comptée × t. Sans prime cette année-là —
        avant son intégration, ou pour un autre statut —, le reste est le
        traitement."""
        reste = 1.0 - part_primes
        prime = self.prime(statut)
        if prime is None:
            return Parts(traitement=reste)
        taux = prime.taux_annuel(annee)
        comptee = prime.part_comptee(annee)
        if taux <= 0.0 or comptee <= 0.0:
            return Parts(traitement=reste)
        traitement = reste / (1.0 + taux * comptee)
        return Parts(traitement=traitement, prime=taux * traitement,
                     soumise=taux * comptee * traitement)

    def taux_supplementaires(self, statut: str, regime: str, annee: int,
                             part_primes: float) -> tuple[float, float]:
        """Ce que les retenues et contributions supplémentaires du statut
        prélèvent pour ce régime, en taux salarié et employeur de la
        rémunération entière."""
        salarie = employeur = 0.0
        parts = None
        for supplement in self.supplementaires:
            if statut not in supplement.statuts or supplement.regime != regime:
                continue
            taux_salarie, taux_employeur = supplement.taux_annuels(annee)
            if not (taux_salarie or taux_employeur):
                continue
            if parts is None:
                parts = self.parts(statut, annee, part_primes)
            assiette = parts.assiette(supplement.assiette)
            salarie += taux_salarie * assiette
            employeur += taux_employeur * assiette
        return salarie, employeur


_PRIMES: dict[tuple, PrimesSoumises] = {}


@une_fois_par_instantane
def charger_primes_soumises(racine: Path) -> PrimesSoumises:
    """La table, gardée sur la signature du fichier ; vide sans lui."""
    chemin = racine / "reference" / "legislation" / "primes_soumises_a_retenue.yaml"
    if not chemin.exists():
        return PrimesSoumises()
    etat = chemin.stat()
    cle = (str(chemin), etat.st_mtime_ns, etat.st_size)
    if cle in _PRIMES:
        return _PRIMES[cle]
    contenu = charger_yaml(chemin)
    primes = tuple(
        Prime(
            code=entree["code"], fiche=entree["fiche"],
            statuts=frozenset(entree["statuts"]), regime=entree["regime"],
            taux=tuple(sorted((_jour(t["depuis"]), float(t["taux"]))
                              for t in entree["taux"])),
            integration=tuple(sorted((int(i["depuis"]), float(i["part"]))
                                     for i in entree["integration"])),
        )
        for entree in contenu.get("primes") or ())
    supplementaires = []
    for entree in contenu.get("supplementaires") or ():
        if entree["assiette"] not in ASSIETTES:
            raise ValueError(f"primes soumises à retenue : assiette inconnue, "
                             f"{entree['assiette']!r}")
        supplementaires.append(Supplementaire(
            statuts=frozenset(entree["statuts"]), regime=entree["regime"],
            motif=entree["motif"], assiette=entree["assiette"],
            taux=tuple(sorted((_jour(t["depuis"]), float(t["salarie"]),
                               float(t["employeur"])) for t in entree["taux"]))))
    table = PrimesSoumises(primes=primes, supplementaires=tuple(supplementaires))
    _PRIMES[cle] = table
    return table
