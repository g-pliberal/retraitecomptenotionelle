"""Le centre du coût : les données de la fabrique, et le jeu de règles sous
lequel elle calcule.

Le coût de la proposition, celui des avantages non contributifs, les bilans et
les engagements ne se calculent qu'à la fabrique
(``scripts/construire_donnees.py``, ``scripts/bilan_compte.py``), qui les fige
dans le paquet du site. Le contexte charge une fois les données coûteuses,
garde un simulateur par jeu de paramètres et les agrégats déjà calculés, et
répond à chaque demande sous le jeu de règles qu'on lui a donné.

Il vient de ``web/pages.py``, comme la saisie (``saisie.py``), quand la
phase 8 en a retiré le texte du site. Le contexte du site,
``moteur/js/contexte.js``, en porte ce qui lit les données ; la saisie — d'une
requête, la carrière — n'y a plus que cet exemplaire depuis l'action 161,
étape 6, et la fabrique la fait tourner par le pont
(:func:`~retraite_notionnelle.pont.carrieres_des_saisies`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import memoire
from .avantages import charger_avantages
from .config import Parametres
from .donnees.assiette import AssietteActivite
from .donnees.bilan import BilanFige, charger_bilan
from .donnees.depenses import DepensesRetraite
from .donnees.distribution import DistributionPensions
from .donnees.equilibre import ComptesRetraite, variante_du_scenario
from .donnees.population import Population
from .frontiere import charger_frontiere
from .restitution import Restitution
from .simulateur import Simulateur

#: Combien d'agrégats le contexte garde en mémoire, tous jeux de règles
#: confondus. Trois par jeu — la restitution, le coût et les avantages —, donc
#: deux jeux de règles : celui de référence, et le dernier demandé.
AGREGATS_MEMORISES = 6


@dataclass
class Contexte:
    """Les données de la fabrique, et le jeu de règles sous lequel on les lit.

    Un contexte, c'est deux choses : des données coûteuses à charger, et UN jeu
    de paramètres — ``base`` — sous lequel tout ce qu'on lui demande est
    calculé. ``simulateur()``, ``cout()`` et ``avantages()`` répondent tous
    trois sous ce jeu-là, sans qu'aucun appelant ait à le leur redire ; un
    autre jeu de règles se demande à un contexte dérivé par :meth:`pour`.

    Les mémoires sont des dictionnaires plutôt qu'un champ par donnée, et c'est
    ce qui fait tenir la dérivation : un dictionnaire passe par référence, si
    bien qu'un contexte dérivé PARTAGE ce que le contexte d'origine a déjà
    chargé. Le chargement des données coûte quelques dixièmes de seconde, une
    simulation en coûte dix, un agrégat deux secondes : rien de tout cela ne
    doit se refaire parce qu'on a changé une règle.
    """

    base: Parametres = field(default_factory=Parametres)
    #: Un simulateur par jeu de paramètres rencontré.
    _instances: dict[Parametres, Simulateur] = field(default_factory=dict)
    #: Ce qui ne dépend d'AUCUN paramètre : dépense observée, comptes du COR,
    #: population, distribution des pensions, assiette, inventaire des
    #: avantages. Ces séries sont lues, jamais calculées : un changement de
    #: règle ne les déplace pas.
    _donnees: dict[str, object] = field(default_factory=dict)
    #: Les agrégats, eux, dépendent des règles : un coût par jeu de paramètres.
    _agregats: dict[tuple[str, Parametres], object] = field(default_factory=dict)

    def pour(self, parametres: Parametres) -> "Contexte":
        """Le même contexte, sous un autre jeu de règles.

        Les mémoires sont partagées, pas recopiées : dériver ne coûte rien, et
        ce que l'un charge, l'autre le trouve chargé.
        """
        if parametres == self.base:
            return self
        return Contexte(base=parametres, _instances=self._instances,
                        _donnees=self._donnees, _agregats=self._agregats)

    def _donnee(self, nom: str, fabrique):
        """Une donnée indépendante des règles, chargée une fois pour toutes."""
        if nom not in self._donnees:
            self._donnees[nom] = fabrique()
        return self._donnees[nom]

    def _agregat(self, nom: str, fabrique):
        """Un agrégat, mémorisé par jeu de règles — et en nombre borné.

        Sans borne, une suite de jeux de règles — ceux qu'un test essaie l'un
        après l'autre — ferait enfler la mémoire d'un jeu à l'autre. Le plus
        ancien s'en va ; y revenir recalcule, deux secondes.
        """
        cle = (nom, self.base)
        if cle not in self._agregats:
            if len(self._agregats) >= AGREGATS_MEMORISES:
                self._agregats.pop(next(iter(self._agregats)))
            self._agregats[cle] = fabrique()
        return self._agregats[cle]

    def simulateur(self, parametres: Parametres | None = None) -> Simulateur:
        parametres = parametres or self.base
        if parametres not in self._instances:
            self._instances[parametres] = Simulateur(parametres)
        return self._instances[parametres]

    def depenses(self) -> DepensesRetraite:
        return self._donnee(
            "depenses", lambda: DepensesRetraite(self.base.racine_donnees))

    def comptes(self) -> ComptesRetraite:
        """Le second terme du bilan : ce que le système de retraite encaisse.

        SOUS LA VARIANTE DES RÈGLES DE ``base``, et c'est ce qui manquait
        jusqu'au 21 septembre 2026 : la page lisait le scénario de référence du
        COR quel que soit le scénario demandé, si bien que la croissance
        déplaçait la dépense des systèmes notionnels, qui est calculée, sans
        déplacer celle du droit en vigueur, qui est empruntée.

        La mémoire porte le nom de la variante : deux jeux de règles qui ne
        diffèrent que par leur scénario ne doivent pas se partager un compte.
        """
        racine = self.base.racine_donnees
        variante = variante_du_scenario(
            self.base.scenario_projection, racine / "reference" / "macro")
        return self._donnee(
            f"comptes:{variante}", lambda: ComptesRetraite(racine, variante=variante))

    def population(self) -> Population:
        hypothese = self.base.hypothese_esperance_vie
        return self._donnee(
            f"population:{hypothese}",
            lambda: Population(self.base.racine_donnees, hypothese))

    def distribution(self) -> DistributionPensions:
        """La distribution des pensions — elle seule chiffre un plancher.

        Celle des retraités qui résident en France : la garantie ne sert
        qu'eux, et c'est celle que le site lit dans son paquet.
        """
        return self._donnee(
            "distribution", lambda: DistributionPensions(self.base.racine_donnees,
                                                         residence="france"))

    def assiette(self) -> AssietteActivite:
        """Sur quoi l'on prélève : sans elle, un taux ne devient pas une recette."""
        return self._donnee(
            "assiette", lambda: AssietteActivite(self.base.racine_donnees))

    def restitution(self) -> Restitution:
        """Ce que la proposition rend au salaire, et ce qu'elle éteint en dette.

        Mémorisé par jeu de règles et non une fois pour toutes : le partage est
        un RÉGLAGE, et deux contextes n'ont pas forcément le même.
        """
        return self._agregat("restitution", lambda: Restitution(
            self.base.racine_donnees, self.base.part_rendue_aux_salaires))

    def bilan(self) -> BilanFige:
        """Le bilan des quatre systèmes, figé — une DONNÉE, pas un agrégat.

        La page des résultats en a besoin à chaque frappe, et le calculer
        coûte dix-huit secondes : elle lit donc la table que
        ``scripts/construire_donnees.py`` a écrite, celle-là même que le
        navigateur reçoit dans son paquet. ``donnees/bilan.py`` dit ce que ce
        figeage coûte — rien sur le système actuel, dont le coefficient est le
        compte du COR, et une dépendance aux réglages de référence sur les
        trois autres.
        """
        return self._donnee(
            "bilan", lambda: charger_bilan(self.base.racine_donnees))

    def cout(self):
        """Le coût agrégé de tous les systèmes — vingt secondes de calcul, une fois.

        Sous les règles de ``base``, et non sous celles par défaut : la
        fabrique fige celui des réglages de référence dans la table que la page
        Coût lit (``figer_cout``, ``donnees/agregats.py``). C'est un
        calcul gardé (``memoire.py``), que les tests et les scripts partagent :
        la mémoire le fait sur un simulateur et des données qu'elle bâtit des
        mêmes paramètres, ceux que ce contexte chargerait, et les comptes du COR
        du même scénario de projection.
        """
        return self._agregat("cout", lambda: memoire.cout(self.base))

    def inventaire_avantages(self):
        """L'inventaire des avantages non contributifs — une donnée, pas un calcul."""
        return self._donnee(
            "inventaire_avantages",
            lambda: charger_avantages(self.base.racine_donnees))

    def frontiere(self):
        """Le versant inverse : ce qu'on cotise sans rien acquérir. Une donnée."""
        return self._donnee(
            "frontiere", lambda: charger_frontiere(self.base.racine_donnees))

    def avantages(self):
        """Ce que les avantages non contributifs coûtent — un calcul gardé, lui
        aussi, et une fois."""
        return self._agregat("avantages", lambda: memoire.avantages(self.base))
