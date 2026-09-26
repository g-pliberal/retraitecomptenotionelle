"""Coordonner les affiliations (docs/architecture.md, § 7.2).

Une carrière qui a traversé plusieurs régimes ne se liquide pas régime par
régime comme s'ils s'ignoraient. Cette étape dit ce que chacun reçoit :

* LE RÉTABLISSEMENT : l'agent parti de la fonction publique sans droit à
  pension est rétabli au régime général et à l'Ircantec (:func:`retablir`) ;
* LE ROUTAGE : chaque ligne de la carrière va aux régimes de son statut,
  rétablissement fait (:func:`regimes_de`) ;
* LES GROUPES : les régimes où un droit est acquis se réunissent quand le
  droit les fait liquider ensemble — un régime et celui qui lui succède, les
  régimes alignés depuis la liquidation unique, les trois régimes
  interpénétrés du code des pensions (:func:`groupes_de_succession`). Ils se
  lisent sur les droits : le relevé les écrit, une fois les droits acquis.

Ce que l'étape écrit, :class:`Coordination`, suit son schéma,
``data/reference/etapes/coordonner_les_affiliations.yaml``. Son jumeau est
``moteur/js/droit/coordonner.js``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from ..donnees.chargement import Fiabilite
from .commun import derniere_annee

if TYPE_CHECKING:
    from ..carriere import AnneeCarriere, Carriere
    from ..scenarios.actuel import ScenarioActuel

#: La version du schéma de l'étape.
SCHEMA_VERSION = 1

#: Les régimes que L. 13 du code des pensions et le XXIV visent : l'État,
#: et par renvoi la CNRACL et le FSPOEIE. La Banque de France, qui emprunte
#: le barème de leur décote, a son propre règlement. Ce sont aussi les trois
#: que L. 5 et L. 11 interpénètrent (:func:`regimes_interpenetres`).
REGIMES_CODE_DES_PENSIONS = frozenset({"fonction_publique_etat", "cnracl", "fspoeie"})

#: Les trois régimes que la liquidation unique des régimes alignés réunit
#: — le régime général, les salariés agricoles et la sécurité sociale des
#: indépendants, sous ses trois noms successifs. Les exploitants agricoles
#: n'en sont pas : la LURA ne vise que les SALARIÉS agricoles.
REGIMES_ALIGNES = frozenset({
    "regime_general", "msa_salaries", "cancava", "organic", "rsi",
})
#: La LURA ne vaut que pour les assurés nés à compter de 1953 (article 51
#: de la loi n° 2015-1702 de financement pour 2016) et pour les pensions
#: prenant effet à compter du 1er juillet 2017 (article 4 du décret
#: n° 2017-737 du 3 mai 2017).
LURA_PREMIERE_GENERATION = 1953
LURA_DATE_EFFET = DateMois(2017, 7)
#: La clé sous laquelle les régimes alignés se réunissent quand la LURA
#: s'applique : ce n'est pas un régime, c'est un groupe.
REGIMES_ALIGNES_TETE = "regimes_alignes"
#: LES TROIS RÉGIMES DU CODE DES PENSIONS SONT INTERPÉNÉTRÉS. Chacun compte
#: et liquide les services des deux autres — L. 5 et L. 11 du code des
#: pensions, articles 8 et 13 du décret n° 2003-1306, articles 4 et 10 du
#: décret n° 2004-1056 —, et c'est le régime de la dernière affiliation
#: qui sert une PENSION UNIQUE. Ils se réunissent sous cette clé comme les
#: régimes alignés sous la leur.
REGIMES_INTERPENETRES_TETE = "regimes_interpenetres"

#: LE RÉTABLISSEMENT. L'agent qui part sans droit à pension est « rétabli,
#: en ce qui concerne l'assurance vieillesse, dans la situation qu'il
#: aurait eue s'il avait été affilié au régime général [...] et à
#: l'Ircantec » (L. 65 du code des pensions, article 64 du décret
#: n° 2003-1306). Les régimes que D. 173-15 du code de la sécurité sociale
#: y soumet et que le catalogue porte : l'État, pensions civiles d'avant
#: 1948 comprises, la CNRACL, le FSPOEIE et la SEITA.
REGIMES_RETABLIS = frozenset({
    "fonction_publique_etat", "pensions_civiles_1853", "cnracl", "fspoeie", "seita",
})
#: Pour qui a quitté son régime après le 28 janvier 1950 (décret
#: n° 50-133 ; circulaire Cnav 2011/38). Le droit d'avant n'a pas été lu :
#: l'agent parti plus tôt garde la pension au prorata que le modèle sert.
RETABLISSEMENT_DEPUIS = "1950-01-29"
#: Où vont ses années : là où le statut de contractuel du public les route
#: — le régime général et l'Ircantec, ou ses devancières de 1951 et de
#: 1959, que l'article 9 du décret n° 70-1277 nomme — et, avant 1945, aux
#: assurances sociales du salarié.
STATUTS_DU_RETABLISSEMENT = ("contractuel_public", "salarie_prive_non_cadre")


@dataclass(frozen=True)
class DroitPension:
    """Ce qu'un régime spécial doit à un agent : la durée qui ouvre une pension,
    et ce qu'il en a servi. Voir :func:`droit_a_pension`."""

    #: Les régimes dont les services se comptent ensemble — les trois
    #: régimes interpénétrés, ou le seul régime demandé.
    regimes: frozenset[str]
    #: Les années servies, une par année civile, dans l'ordre.
    lignes: tuple[AnneeCarriere, ...]
    #: Services effectifs, en années.
    servies: float
    #: Durée exigée à la radiation, et fiabilité de la ligne qui la donne.
    exigees: float
    fiabilite: Fiabilite
    #: Date de la radiation, ISO : le 1er janvier qui suit la dernière année
    #: de services, ou le départ quand l'agent part en fonctions.
    radiation: str

    @property
    def pension(self) -> bool:
        return self.servies + 1e-9 >= self.exigees

    @property
    def recrutement(self) -> int:
        return self.lignes[0].annee

    @property
    def derniere(self) -> int:
        return self.lignes[-1].annee


def borne_carriere(carriere: Carriere) -> int | None:
    """Dernière année à compter dans les services, ``None`` si sans objet."""
    return (carriere.annee_liquidation
            if carriere.age_liquidation is not None else None)


def regimes_routes(moteur: ScenarioActuel, statuts: list[str]) -> frozenset[str]:
    """Les régimes que ces statuts atteignent, une année au moins.

    C'est la seconde garde du droit dérogatoire, et elle n'est pas de
    confort. Plusieurs régimes SPÉCIAUX servent eux aussi une catégorie
    active — leur fiche le déclare, et c'est exact : la SNCF a ses agents
    de conduite. Mais la catégorie active de la fonction publique n'a rien
    à y voir : sans cette garde, un assuré ayant fait vingt ans d'emploi
    classé après une carrière à la SNCF aurait vu son régime SNCF liquidé à
    l'âge de la fonction publique, et décoté sur la limite d'âge d'un grade
    qu'il n'a jamais eu.
    """
    return frozenset(
        code
        for statut in statuts
        for periode in moteur.affiliations.periodes(statut)
        for code in (periode.get("regimes") or ())
    )


def regimes_interpenetres(moteur: ScenarioActuel, carriere: Carriere) -> frozenset[str]:
    """Les régimes du code des pensions que cette carrière réunit en une
    pension unique.

    Les trois, sauf l'État quand l'assuré n'y a servi que sous l'uniforme :
    le militaire garde sa pension militaire, et n'y renonce pour une
    pension unique que par un choix exprès (L. 77 du code des pensions,
    article 57 du décret n° 2003-1306). Le modèle suit ce défaut. Les
    services militaires d'un fonctionnaire civil de l'État restent, eux,
    dans la pension de l'État, que le catalogue ne scinde pas.
    """
    militaires = moteur.affiliations.categories_militaires
    etat = ("fonction_publique_etat", "pensions_civiles_1853")
    civil = any(
        ligne.cotise and ligne.affiliation not in militaires
        and not regimes_routes(moteur, [ligne.affiliation]).isdisjoint(etat)
        for ligne in carriere.lignes
    )
    if civil:
        return REGIMES_CODE_DES_PENSIONS
    return REGIMES_CODE_DES_PENSIONS - {"fonction_publique_etat"}


def droit_a_pension(moteur: ScenarioActuel, code: str, carriere: Carriere,
                    annee_liquidation: int) -> DroitPension | None:
    """Ce régime peut-il pensionner cet agent ? ``None`` s'il n'y a pas servi.

    La durée qui ouvre une pension (:class:`ServicesOuvrantPension`) se
    compte sur les années que le régime a effectivement reçues — celles
    des trois régimes interpénétrés ensemble, puisque chacun compte les
    services des deux autres —, et se lit à la radiation : au 1er janvier
    qui suit la dernière année de services, comme pour la pension
    différée, ou au départ quand l'agent part en fonctions. Une carrière
    d'État seulement militaire se lit à la règle des militaires (L. 6), et
    à son premier engagement : les deux ans de R. 4-1 ne valent que pour
    le militaire engagé depuis le 1er janvier 2014 (article 42, II, de la
    loi n° 2014-40).
    """
    # Les pensions civiles d'avant 1948 sont celles de l'État.
    if code == "pensions_civiles_1853":
        code = "fonction_publique_etat"
    interpenetres = regimes_interpenetres(moteur, carriere)
    if code in interpenetres:
        regimes, cle = set(interpenetres), code
    elif code == "fonction_publique_etat":
        regimes, cle = {code}, "militaires"
    else:
        regimes, cle = {code}, code
    if "fonction_publique_etat" in regimes:
        regimes.add("pensions_civiles_1853")
    borne = borne_carriere(carriere)
    par_annee: dict[int, AnneeCarriere] = {}
    for ligne in carriere.lignes:
        if not ligne.cotise or (borne is not None and ligne.annee > borne):
            continue
        if regimes.isdisjoint(moteur.affiliations.regimes(
                ligne.affiliation, ligne.annee,
                carriere.date_entree(ligne.affiliation))):
            continue
        retenue = par_annee.get(ligne.annee)
        if retenue is None or ligne.fraction_annee > retenue.fraction_annee:
            par_annee[ligne.annee] = ligne
    if not par_annee:
        return None
    lignes = tuple(par_annee[annee] for annee in sorted(par_annee))
    mois = (carriere.date_liquidation.mois
            if carriere.age_liquidation is not None else 1)
    depart = f"{annee_liquidation:04d}-{mois:02d}-01"
    radiation = f"{lignes[-1].annee + 1:04d}-01-01"
    en_fonctions = radiation >= depart
    if en_fonctions:
        radiation = depart
    lue_le = f"{lignes[0].annee:04d}-01-01" if cle == "militaires" else radiation
    regle = moteur.services_ouvrant_pension.annees(cle, lue_le, en_fonctions)
    exigees, fiabilite = regle if regle is not None else (0.0, Fiabilite.ESTIMEE)
    return DroitPension(
        regimes=frozenset(regimes), lignes=lignes,
        servies=sum(ligne.fraction_annee for ligne in lignes),
        exigees=exigees, fiabilite=fiabilite, radiation=radiation,
    )


def retablir(moteur: ScenarioActuel, carriere: Carriere) -> Carriere:
    """La carrière que le scénario 1 liquide, RÉTABLISSEMENT fait.

    Le fonctionnaire qui part sans la durée qui ouvre une pension — deux
    ans depuis 2011, quinze avant ; les trois régimes interpénétrés comptés
    ensemble, de sorte qu'un retour dans l'un d'eux annule le
    rétablissement (article 64, II, du décret n° 2003-1306) — n'a pas de
    pension de son régime : ses années passent au régime général et à
    l'Ircantec, comme s'il y avait été affilié. Le modèle les pensionnait
    au prorata dans le régime spécial.

    Deux assiettes, et les textes les séparent. Le régime général porte au
    compte « des salaires reconstitués à partir des cotisations
    rétroactives calculées sur la base des derniers émoluments ou de la
    dernière solde soumis à retenues pour pension [...], dans la limite du
    plafond en vigueur » chaque année (D. 173-16 ; circulaire Cnav
    2011/38) : le dernier traitement, pour toutes les années, et la
    période « entre en compte, quel qu'ait été le montant de sa
    rémunération ». L'Ircantec, elle, valide « suivant sa propre
    réglementation » (article 9 du décret n° 70-1277) : le traitement de
    chaque année. Les primes restent au RAFP, que le rétablissement ne
    touche pas.

    Les années rétablies gardent leur statut : c'est leur champ
    ``revenu_retabli`` qui les désigne, et :func:`regimes_de` qui les
    route. La carrière est rendue telle quelle quand rien n'est rétabli.
    """
    return _retablir(moteur, carriere)[0]


def _retablir(moteur: ScenarioActuel, carriere: Carriere
              ) -> tuple[Carriere, tuple[tuple[DroitPension, float], ...]]:
    """:func:`retablir`, et les rétablissements faits : pour chacun, le
    droit que l'agent n'a pas, et le dernier traitement que le régime général
    porte au compte de ses années."""
    if carriere.age_liquidation is None:
        return carriere, ()
    annee_liquidation = carriere.annee_liquidation
    vus: set[frozenset[str]] = set()
    retablies: dict[int, float] = {}
    faits: list[tuple[DroitPension, float]] = []
    for code in sorted(REGIMES_RETABLIS):
        droit = droit_a_pension(moteur, code, carriere, annee_liquidation)
        if droit is None or droit.regimes in vus:
            continue
        vus.add(droit.regimes)
        if droit.pension or droit.radiation < RETABLISSEMENT_DEPUIS:
            continue
        derniere = droit.lignes[-1]
        traitement = derniere.revenu_annualise * (1.0 - derniere.part_primes)
        faits.append((droit, traitement))
        for ligne in carriere.lignes:
            if (ligne.cotise and ligne.annee <= annee_liquidation
                    and not droit.regimes.isdisjoint(moteur.affiliations.regimes(
                        ligne.affiliation, ligne.annee,
                        carriere.date_entree(ligne.affiliation)))):
                retablies[id(ligne)] = traitement * ligne.fraction_annee
    if not retablies:
        return carriere, ()
    return carriere.avec_lignes([
        replace(ligne, revenu_retabli=retablies[id(ligne)])
        if id(ligne) in retablies else ligne
        for ligne in carriere.lignes
    ]), tuple(faits)


def regimes_de(moteur: ScenarioActuel, ligne: AnneeCarriere, annee: int,
               annee_entree: int | DateMois | None = None,
               revenu: float | None = None,
               plafond: float | None = None) -> tuple[str, ...]:
    """Les régimes auxquels cette ligne cotise cette année-là.

    Ceux de son statut, sauf pour une année RÉTABLIE : elle quitte son
    régime spécial pour le régime général et l'Ircantec — là où le
    contractuel du public est routé —, et garde le RAFP. Voir
    :func:`retablir`.
    """
    regimes = moteur.affiliations.regimes(
        ligne.affiliation, annee, annee_entree, revenu=revenu, plafond=plafond)
    if ligne.revenu_retabli <= 0:
        return regimes
    cibles: tuple[str, ...] = ()
    for statut in STATUTS_DU_RETABLISSEMENT:
        cibles = tuple(moteur.affiliations.regimes(statut, annee))
        if cibles:
            break
    return cibles + tuple(code for code in regimes
                          if code not in REGIMES_RETABLIS)


@dataclass(frozen=True, eq=False)
class Coordination:
    """Ce que l'étape écrit : la carrière, rétablissement fait, et les
    régimes qui reçoivent chacune de ses lignes. Son schéma :
    ``data/reference/etapes/coordonner_les_affiliations.yaml``."""

    #: La vue de la chronologie que les étapes suivantes lisent,
    #: rétablissement fait.
    carriere: Carriere
    #: Pour chaque ligne de ``carriere``, dans son ordre, ses régimes.
    regimes: tuple[tuple[str, ...], ...]
    #: Les rétablissements faits : le droit que l'agent n'a pas, et le
    #: traitement que le régime général porte au compte.
    retablissements: tuple[tuple[DroitPension, float], ...] = ()

    def donnees(self) -> dict:
        """La coordination, telle que son schéma la décrit."""
        return {
            "schema_version": SCHEMA_VERSION,
            "personne": self.carriere.personne,
            "retablissements": [
                {"regimes": sorted(droit.regimes), "radiation": droit.radiation,
                 "traitement": traitement}
                for droit, traitement in self.retablissements],
            "lignes": [
                {"annee": ligne.annee, "affiliation": ligne.affiliation,
                 "regimes": list(regimes), "revenu_retabli": ligne.revenu_retabli}
                for ligne, regimes in zip(self.carriere.lignes, self.regimes)],
        }


def coordonner(moteur: ScenarioActuel, carriere: Carriere) -> Coordination:
    """L'étape : rétablir, puis router chaque ligne vers ses régimes.

    Le routage est celui que toute l'acquisition lit : les régimes du statut
    de la ligne, l'année de la ligne, à la date d'entrée dans le statut, pour
    le revenu de l'année — le salaire de référence d'une année indemnisée,
    que les complémentaires continuent de recevoir.
    """
    carriere, retablissements = _retablir(moteur, carriere)
    plafond = moteur.macro.plafond_securite_sociale
    regimes = tuple(
        regimes_de(moteur, ligne, ligne.annee,
                   carriere.date_entree(ligne.affiliation),
                   revenu=ligne.revenu if ligne.cotise else ligne.revenu_reference,
                   plafond=plafond(ligne.annee))
        for ligne in carriere.lignes)
    return Coordination(carriere, regimes, retablissements)


def lura_applicable(carriere: Carriere) -> bool:
    """La liquidation unique vaut-elle pour cette carrière ?

    Deux conditions, et le modèle les porte toutes les deux : la
    génération, et la date d'effet au mois près. Une troisième reste hors
    du modèle — la LURA ne s'applique pas à qui avait déjà obtenu, avant
    le 1er juillet 2017, une retraite de même nature dans l'un des trois
    régimes —, parce qu'une carrière du dépôt liquide tout à la fois.
    """
    return (carriere.generation >= LURA_PREMIERE_GENERATION
            and carriere.date_liquidation.rang >= LURA_DATE_EFFET.rang)


def tete_de_succession(moteur: ScenarioActuel, code: str, annee_liquidation: int) -> str:
    """Le régime au bout de la chaîne d'absorption de ``code``, tant que
    la chaîne reste en annuités : ``cancava`` et ``rsi`` rendent
    ``regime_general``, ``pensions_civiles_1853`` rend
    ``fonction_publique_etat``. Un régime en points au bout de la chaîne
    l'arrête — les annuités des régimes professionnels intégrés ne se
    fondent pas dans les points de l'Agirc-Arrco —, et un régime en points
    n'y entre jamais : ses points se convertissent et s'additionnent déjà
    (voir :func:`~retraite_notionnelle.droit.liquider.valeur_du_point`).

    L'absorption ne se suit qu'à partir de l'année où le régime FERME à
    ses affiliés — celle où l'absorbant commence à recevoir leurs années.
    Avant, ce sont deux régimes distincts, et un polypensionné en a deux :
    un salarié devenu artisan qui liquide en 2010 a une pension du régime
    général et une du RSI, comme le droit d'alors ; s'il liquide en 2020,
    le RSI est le régime général, et il n'en a qu'une.
    """
    vu = {code}
    courant = code
    while True:
        regime = moteur.catalogue[courant]
        suivant = regime.integre_dans
        borne = (regime.fermeture if regime.fermeture is not None
                 else regime.extinction)
        if (suivant is None or borne is None or annee_liquidation < borne
                or suivant not in moteur.catalogue or suivant in vu):
            return courant
        absorbant = moteur.catalogue[suivant]
        periode = absorbant.periode(
            min(annee_liquidation, derniere_annee(absorbant))
        )
        if periode is None or periode.type_calcul != "annuites":
            return courant
        vu.add(suivant)
        courant = suivant


def chaine_depuis(moteur: ScenarioActuel, membres: list[str]) -> list[str]:
    """Les membres dans l'ordre de la chaîne, du plus ancien à l'absorbant."""
    restants = set(membres)
    ordre: list[str] = []
    for depart in sorted(membres):
        courant = depart
        chaine = []
        while courant in restants and courant not in ordre:
            chaine.append(courant)
            courant = moteur.catalogue[courant].integre_dans
        if len(chaine) > len(ordre):
            ordre = chaine
    return ordre + sorted(restants - set(ordre))


def groupes_de_succession(
        moteur: ScenarioActuel, codes: list[str], annee_liquidation: int,
        derniere_annee_par_regime: dict[str, int],
        carriere: Carriere | None = None,
) -> dict[str, tuple[str, ...]]:
    """Les régimes d'annuités que la carrière a traversés, groupés par
    chaîne de succession : pour chaque code d'un groupe d'au moins deux,
    les membres du groupe, LE PREMIER ÉTANT CELUI QUI LIQUIDE.

    **Un régime et celui qui lui succède ne sont pas deux régimes.** La
    CANCAVA, le RSI et le régime général sont trois NOMS du même droit
    pour un artisan : sa caisse calcule un seul salaire annuel moyen sur
    toute la carrière et un seul coefficient de proratisation, et le
    catalogue le sait, puisqu'il porte ``succede_a`` et ``integre_dans``.
    Liquider chaque nom sur ses seules années — ce que le modèle faisait,
    et qui est juste d'un polypensionné passé d'un régime à un AUTRE —
    calculait deux salaires de référence là où la caisse n'en calcule
    qu'un : un artisan payé 60 000 € de 1976 à 2015 recevait
    « 30 077 € × 120/165 » plus « 36 778 € × 40/165 » au lieu de
    « 34 152 € × 160/165 ». Mesuré contre l'oracle du régime général,
    l'écart allait de −7,2 % à +0,3 %, dans les deux sens, les meilleures
    années de chaque morceau pouvant être meilleures que celles de la
    carrière entière.

    Le groupe est liquidé par le membre de la DERNIÈRE période active de
    la carrière — à égalité, par l'absorbant —, dont la fiche donne les
    règles : c'est la caisse qui aurait le dossier, et c'est aussi ce que
    la LURA prescrit (« le montant de la retraite unique est déterminé en
    fonction des règles applicables au régime liquidateur »). Un assuré
    qui n'a connu qu'un seul nom n'est pas touché.

    **ET LES RÉGIMES ALIGNÉS DISTINCTS SE RÉUNISSENT AUSSI, DEPUIS 2017.**
    La liquidation unique des régimes alignés (`L. 173-1-2` CSS) donne une
    seule retraite à qui a cotisé à deux des trois régimes alignés : un
    revenu annuel moyen formé de la somme des salaires et revenus d'une
    même année, écrêtée au plafond, sur les vingt-cinq meilleures années,
    et une proratisation qui tient compte de tous les trimestres des trois
    régimes (`R. 173-4-4-1`, 1° et 4°, circulaire Cnav 2017/27). Le modèle
    y arrivait déjà pour le couple régime général / indépendants, mais par
    la chaîne d'absorption, qui ne ferme le RSI qu'en 2018 : une carrière
    liquidée entre juillet 2017 et l'absorption était coupée en deux. Et
    il ne le faisait pas du tout pour les salariés agricoles, dont le
    régime existe toujours — « SR 41 499 € × 88/167 » plus
    « SR 29 069 € × 80/167 » là où la caisse calcule un seul salaire de
    référence. Les deux conditions de la loi sont opposées :
    :func:`lura_applicable`.

    **ET LES TROIS RÉGIMES DU CODE DES PENSIONS SONT INTERPÉNÉTRÉS.** L'État,
    la CNRACL et le FSPOEIE comptent et liquident chacun les services des
    deux autres, et le régime de la dernière affiliation sert une pension
    unique : un traitement, celui des six derniers mois de la carrière
    publique entière, et une proratisation sur tous ses services. Le modèle
    liquidait chaque régime sur ses seules années : un fonctionnaire de
    l'État devenu territorial touchait une pension de l'État sur son
    traitement de départ, revalorisé comme une pension, et une de la CNRACL
    au prorata de ses dernières années. Voir :func:`regimes_interpenetres`.
    """
    par_tete: dict[str, list[str]] = {}
    lura = carriere is not None and lura_applicable(carriere)
    interpenetres = (regimes_interpenetres(moteur, carriere)
                     if carriere is not None else frozenset())
    for code in codes:
        regime = moteur.catalogue[code]
        periode = regime.periode(min(annee_liquidation, derniere_annee(regime)))
        if periode is None or periode.type_calcul != "annuites":
            continue
        tete = (REGIMES_ALIGNES_TETE if lura and code in REGIMES_ALIGNES
                else tete_de_succession(moteur, code, annee_liquidation))
        if tete in interpenetres:
            tete = REGIMES_INTERPENETRES_TETE
        par_tete.setdefault(tete, []).append(code)
    groupes: dict[str, tuple[str, ...]] = {}
    for membres in par_tete.values():
        if len(membres) < 2:
            continue
        rang = {code: i for i, code in enumerate(chaine_depuis(moteur, membres))}
        liquidateur = max(
            membres,
            key=lambda code: (derniere_annee_par_regime.get(code, 0), rang[code]),
        )
        ordonnes = (liquidateur,) + tuple(
            code for code in sorted(membres, key=rang.get) if code != liquidateur
        )
        for code in membres:
            groupes[code] = ordonnes
    return groupes
