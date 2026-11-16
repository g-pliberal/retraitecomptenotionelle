"""Les types du journal de l'échéancier que le pont échange (action 161,
étape 1 du retrait des règles Python) : l'événement (contrat C.7), l'entrée et
le journal (contrat C.8, ``docs/architecture.md``, § 7.4), que ``journal.py``
et ``echeancier.py`` réimportent le temps du retrait. Leur jumeau est
``moteur/js/journal.js``.
"""

from __future__ import annotations

from dataclasses import dataclass

#: La version du contrat C.7 que :meth:`Evenement.donnees` suit.
SCHEMA_DE_L_EVENEMENT = 1

#: La version du contrat C.8 que :meth:`Entree.donnees` suit.
SCHEMA_DE_L_ENTREE = 1



@dataclass(frozen=True)
class Evenement:
    """Un événement (contrat C.7)."""

    id: str
    #: Sa date (AAAA-MM-JJ).
    date: str
    #: Les personnes concernées.
    personnes: tuple[str, ...]
    #: Ce qu'il vise : un régime, une liquidation, une allocation.
    vise: dict
    sorte: str = "depart"
    #: ``acte``, ``simule``, ``observe``, ``induit`` ou ``publication``.
    origine: str = "acte"
    condition: object | None = None
    #: L'ordre dans la journée.
    rang: int = 0

    def donnees(self) -> dict:
        """L'événement, tel que le contrat C.7 le décrit."""
        donnee = {"schema_version": SCHEMA_DE_L_EVENEMENT, "id": self.id, "date": self.date,
                  "sorte": self.sorte, "personnes": list(self.personnes),
                  "vise": self.vise, "origine": self.origine, "rang": self.rang}
        if self.condition is not None:
            donnee["condition"] = self.condition
        return donnee


@dataclass(frozen=True)
class Entree:
    """Une entrée du journal (contrat C.8)."""

    id: str
    #: L'événement qui l'a écrite, et sa date (AAAA-MM-JJ).
    evenement: str
    inscrite_le: str
    #: Sa période d'effet, [début, fin) ; une fin ``None`` ne borne rien.
    debut: str | None
    fin: str | None
    #: Ce qu'elle contient : sa sorte (``evenement``, ``liquidation``,
    #: ``composante``, ``revalorisation``, ``foyer``, ``reversion``,
    #: ``decision``) et sa donnée.
    sorte: str
    contenu: object
    #: L'entrée qu'elle révise : sa lignée est celle de cette entrée.
    remplace: str | None = None
    #: L'événement en attente qu'elle annule.
    annule: str | None = None

    def couvre(self, debut: str, fin: str | None) -> bool:
        """Son effet couvre-t-il la période [debut, fin) ?"""
        if self.debut is not None and self.debut > debut:
            return False
        if self.fin is None:
            return True
        return fin is not None and fin <= self.fin

    def donnees(self) -> dict:
        """L'entrée, telle que le contrat C.8 la décrit ; son contenu est la
        donnée qu'elle porte, décrite par son propre contrat ou schéma."""
        contenu = self.contenu.donnees() if hasattr(self.contenu, "donnees") else self.contenu
        donnee = {
            "schema_version": SCHEMA_DE_L_ENTREE,
            "id": self.id,
            "inscrite": {"evenement": self.evenement, "date": self.inscrite_le},
            "effet": [self.debut, self.fin],
            "contenu": {"sorte": self.sorte, "donnee": contenu},
        }
        if self.remplace is not None:
            donnee["remplace"] = self.remplace
        if self.annule is not None:
            donnee["annule"] = self.annule
        return donnee


class Journal:
    """Le journal : une liste d'entrées où l'on ajoute sans jamais effacer."""

    def __init__(self) -> None:
        self._entrees: list[Entree] = []
        self._par_id: dict[str, Entree] = {}
        #: Pour chaque entrée, la racine de sa lignée.
        self._lignee: dict[str, str] = {}

    def inscrire(self, entree: Entree) -> Entree:
        """Ajoute ``entree``. Un identifiant déjà pris, ou une révision d'une
        entrée inconnue, est refusé : le journal ne se corrige pas en place."""
        if entree.id in self._par_id:
            raise ValueError(f"entrée déjà inscrite : {entree.id}")
        if entree.remplace is not None and entree.remplace not in self._par_id:
            raise ValueError(f"{entree.id} remplace une entrée inconnue : {entree.remplace}")
        self._entrees.append(entree)
        self._par_id[entree.id] = entree
        self._lignee[entree.id] = (self._lignee[entree.remplace]
                                   if entree.remplace is not None else entree.id)
        return entree

    def __iter__(self):
        return iter(self._entrees)

    def __len__(self) -> int:
        return len(self._entrees)

    def entree(self, ident: str) -> Entree:
        return self._par_id[ident]

    def etat_au(self, date: str) -> list[Entree]:
        """L'état à ``date`` : tout ce qui a été inscrit au plus tard ce jour-là."""
        return [e for e in self._entrees if e.inscrite_le <= date]

    def servi(self, debut: str, fin: str | None = None,
              sorte: str | None = None) -> list[Entree]:
        """Ce qui est servi pour la période [debut, fin) : pour chaque lignée,
        la dernière entrée inscrite dont l'effet la couvre — une entrée sans
        montant, qui éteint sa composante, compte comme les autres."""
        retenues: dict[str, Entree] = {}
        for entree in self._entrees:
            if sorte is not None and entree.sorte != sorte:
                continue
            if entree.couvre(debut, fin):
                retenues[self._lignee[entree.id]] = entree
        return list(retenues.values())

    def donnees(self) -> list[dict]:
        return [e.donnees() for e in self._entrees]
