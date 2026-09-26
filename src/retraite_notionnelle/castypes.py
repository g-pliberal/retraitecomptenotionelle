"""Cas types — le « cas général », par opposition au cas particulier.

Une simulation individuelle répond à « et moi ? ». Les cas types répondent à
« et globalement ? ». On croise un jeu de carrières représentatives avec un jeu
de générations, et l'on regarde comment la réforme déplace chacune d'elles.

Les carrières retenues suivent l'esprit des cas types du Conseil d'orientation
des retraites : elles ne prétendent pas décrire un individu réel, mais isoler
l'effet des règles à comportement donné. Elles couvrent volontairement les cas
extrêmes du système — le régime spécial à départ précoce et la carrière
interrompue — parce que ce sont eux que la réforme simulée déplace le plus.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from typing import TYPE_CHECKING

from .carriere import PROFIL_AUTOMATIQUE, Carriere
from .simulateur import Comparaison, Simulateur
from . import pilote
from .pilote import VARIANTES_LIQUIDATION

if TYPE_CHECKING:  # pragma: no cover - annotation seulement
    from .donnees.effectifs import EffectifsRetraites


@dataclass(frozen=True)
class CasType:
    """Une carrière de référence, indépendante de la génération."""

    code: str
    libelle: str
    affiliation: str
    age_debut: float
    #: L'âge de départ ÉCRIT. Il ne commande plus les résultats affichés : la
    #: règle ci-dessous le fait. Il reste parce que la variante ``absolu`` le
    #: lit, et parce qu'il est le point de départ de la recherche du point
    #: fixe — ce qui n'engage rien, la recherche ne s'arrêtant que sur un âge
    #: que le droit de la génération confirme.
    age_liquidation: float
    niveau_salaire: float
    #: Le défaut RÉSOUT le profil sur l'affiliation, et les fiches ci-dessous ne
    #: le nomment que là où elles en savent plus que l'affiliation : le
    #: sédentaire est de catégorie B et l'actif de catégorie C, ce que leur
    #: commentaire disait déjà sans que le modèle le lise.
    profil_carriere: str = PROFIL_AUTOMATIQUE
    sexe: str = "H"
    nombre_enfants: int = 0
    part_primes: float = 0.0
    interruptions_relatives: tuple[tuple[int, str], ...] = ()
    #: Caisses de ``effectifs_retraites.csv`` dont ce cas type porte les
    #: retraités. C'est par elles qu'il reçoit son POIDS dans les agrégats :
    #: voir :func:`poids_effectifs`. Une caisse réclamée par plusieurs cas types
    #: se partage entre eux.
    caisses: tuple[str, ...] = ()
    #: Ce qui DATE le départ, quand ce n'est pas un nombre. Trois règles, et
    #: chacune répond à la question « qu'est-ce qui, pour cette carrière-là,
    #: commande le départ ? ».
    #:
    #: ``taux_plein`` — le premier âge auquel la pension est SERVIE ENTIÈRE :
    #: l'âge d'ouverture si la durée requise y est atteinte, l'âge auquel elle
    #: l'est sinon, et de toute façon pas au-delà de l'âge d'annulation de la
    #: décote. C'est la règle du plus grand nombre, et celle des cas types du
    #: Conseil d'orientation des retraites : personne ne liquide volontairement
    #: avec huit trimestres de décote.
    #:
    #: ``ouverture`` — l'âge auquel le droit OUVRE la liquidation, sans égard
    #: à la durée. C'est celle des carrières dont un STATUT commande le départ :
    #: la catégorie active, l'agent de conduite, l'agent des IEG. Leur cas type
    #: existe pour montrer ce départ-là ; les faire attendre le taux plein
    #: reviendrait à les calculer en sédentaires, ce dont le dépôt vient de
    #: sortir. Elle suit tout ce que le droit fait varier — l'âge légal par
    #: génération, l'anticipation du classement, l'âge propre d'un régime
    #: spécial, et jusqu'à sa FERMETURE : l'agent de conduite né en 2000 est
    #: embauché après 2020, relève du régime général, et liquide donc à l'âge
    #: de celui-ci et non à cinquante-deux ans.
    #:
    #: ``services`` — l'âge d'entrée augmenté de :attr:`ecart_liquidation`
    #: années de services. La pension militaire ne s'ouvre pas à un âge mais à
    #: une durée : lui opposer un âge légal serait lui opposer ce que le droit
    #: ne lui oppose pas.
    regle_liquidation: str = "taux_plein"
    #: Le décalage que la règle applique à son âge de référence. Il ne sert
    #: plus qu'au militaire, où il porte la durée de services elle-même : le
    #: libéral l'a porté jusqu'au 22 septembre 2026 pour contourner un défaut du
    #: moteur, et l'a rendu avec lui.
    ecart_liquidation: float = 0.0
    commentaire: str = ""

    def age_liquidation_pour(self, simulateur: Simulateur, generation: int,
                             variante: str = "droit") -> float:
        """L'âge auquel ce cas type liquide, étant né en ``generation`` : le
        pilote le fixe (:func:`~retraite_notionnelle.pilote.age_de_depart`)."""
        return pilote.age_de_depart(simulateur, self, generation, variante)

    def construire(self, simulateur: Simulateur, generation: int,
                   variante: str = "droit") -> Carriere:
        return self._carriere(
            simulateur, generation,
            self.age_liquidation_pour(simulateur, generation, variante),
        )

    def _carriere(self, simulateur: Simulateur, generation: int,
                  age_liquidation: float) -> Carriere:
        interruptions = {
            int(generation + self.age_debut + decalage): motif
            for decalage, motif in self.interruptions_relatives
        }
        return simulateur.carriere_simple(
            annee_naissance=generation,
            sexe=self.sexe,
            affiliation=self.affiliation,
            age_debut=self.age_debut,
            age_liquidation=age_liquidation,
            niveau_salaire=self.niveau_salaire,
            profil_carriere=self.profil_carriere,
            interruptions=interruptions,
            nombre_enfants=self.nombre_enfants,
            part_primes=self.part_primes,
            identifiant=f"{self.libelle} (génération {generation})",
        )


#: Jeu de cas types couvrant les principales configurations du système.
CAS_TYPES: tuple[CasType, ...] = (
    CasType(
        code="smic_carriere_complete",
        libelle="Salarié au niveau du SMIC, carrière complète",
        affiliation="salarie_prive_non_cadre",
        age_debut=18, age_liquidation=64, niveau_salaire=0.55,
        profil_carriere="plat",
        caisses=("cnav",),
        commentaire="Carrière longue à bas salaire : le cas où les minima pèsent le plus.",
    ),
    CasType(
        code="salaire_moyen",
        libelle="Salarié au salaire moyen",
        affiliation="salarie_prive_non_cadre",
        age_debut=21, age_liquidation=64, niveau_salaire=1.0,
        caisses=("cnav",),
        commentaire="Référence centrale.",
    ),
    CasType(
        code="cadre",
        libelle="Cadre du privé",
        affiliation="salarie_prive_cadre",
        age_debut=23, age_liquidation=64, niveau_salaire=2.2,
        caisses=("cnav",),
        commentaire="Forte part de rémunération au-dessus du plafond.",
    ),
    CasType(
        code="carriere_interrompue",
        libelle="Carrière interrompue (5 ans hors emploi)",
        affiliation="salarie_prive_non_cadre",
        age_debut=21, age_liquidation=64, niveau_salaire=0.9,
        sexe="F", nombre_enfants=2,
        caisses=("cnav",),
        interruptions_relatives=tuple((decalage, "education_enfant") for decalage in range(8, 13)),
        commentaire=(
            "Cinq années sans cotisation. Le système actuel les couvre par des "
            "trimestres assimilés, par l'AVPF (qui porte au compte un salaire au SMIC) et par la majoration de durée d'assurance ; le compte "
            "notionnel ne couvre rien. Les deux premiers ne se voient guère ici : "
            "sur une carrière de plus de vingt-cinq années portées au compte, "
            "les années au SMIC n'entrent pas dans les vingt-cinq meilleures, et "
            "les trimestres assimilés ne servent que si la durée requise n'est "
            "pas atteinte. C'est un résultat, pas une omission."
        ),
    ),
    CasType(
        code="fonctionnaire_sedentaire",
        libelle="Fonctionnaire sédentaire (catégorie B)",
        affiliation="fonctionnaire_etat",
        age_debut=22, age_liquidation=64, niveau_salaire=1.2,
        part_primes=0.18,
        profil_carriere="public_categorie_b",
        caisses=("fonction_publique_etat_civile",),
        commentaire="Traitement indiciaire hors primes ; les primes relèvent du RAFP.",
    ),
    CasType(
        code="fonctionnaire_actif",
        libelle="Fonctionnaire de catégorie active (départ anticipé)",
        affiliation="fonctionnaire_territorial_hospitalier_actif",
        age_debut=22, age_liquidation=57, niveau_salaire=1.1,
        part_primes=0.22,
        profil_carriere="public_categorie_c",
        caisses=("cnracl",),
        regle_liquidation="ouverture",
        commentaire=(
            "Aide-soignant, agent technique territorial : l'emploi est classé, "
            "et le départ anticipé de cinq années est celui que l'article L. 24 "
            "lui ouvre, non une anticipation sanctionnée. Le cas type était "
            "calculé comme un sédentaire tant qu'aucun statut ne portait le "
            "classement. L'âge suit sa génération : cinquante-cinq ans jusqu'à "
            "celle de 1956, cinquante-sept ensuite, cinquante-neuf pour celles "
            "que la réforme de 2023 atteint."
        ),
    ),
    CasType(
        code="militaire",
        libelle="Militaire non officier (radiation après vingt-cinq ans de services)",
        affiliation="militaire",
        age_debut=19, age_liquidation=44, niveau_salaire=0.95,
        part_primes=0.25,
        caisses=("fonction_publique_etat_militaire",),
        regle_liquidation="services", ecart_liquidation=25,
        commentaire=(
            "La pension militaire ne s'ouvre pas à un âge mais à une durée : "
            "dix-sept ans de services pour un non-officier. C'est le départ le "
            "plus précoce du système, et celui qu'un compte notionnel déplace le plus : quarante ans de rente pour vingt-cinq ans de cotisations. "
            "La solde indiciaire seule ouvre des droits ; les indemnités, plus "
            "lourdes que les primes de la fonction publique civile, relèvent du "
            "RAFP."
        ),
    ),
    CasType(
        code="agent_sncf_conduite",
        libelle="Agent de conduite SNCF",
        affiliation="agent_sncf",
        age_debut=20, age_liquidation=52, niveau_salaire=1.1,
        caisses=("sncf",),
        regle_liquidation="ouverture",
        commentaire=(
            "Écart à l'âge de référence parmi les plus élevés du système : "
            "cinquante ans jusqu'aux départs de 2016, cinquante-quatre au terme "
            "de la montée en charge. Le régime est fermé aux embauches depuis "
            "2020, et la règle en tire la conséquence : la génération 2000, "
            "entrée après la fermeture, relève du régime général et liquide à "
            "l'âge de celui-ci."
        ),
    ),
    CasType(
        code="agent_ieg",
        libelle="Agent des industries électriques et gazières",
        affiliation="agent_ieg",
        age_debut=21, age_liquidation=57, niveau_salaire=1.4,
        caisses=("cnieg",),
        regle_liquidation="ouverture",
        commentaire=(
            "Régime spécial fermé aux embauches depuis 2023. L'âge d'ouverture "
            "y est celui du millésime de départ : cinquante-cinq ans jusqu'en "
            "2016, cinquante-neuf à compter de 2027."
        ),
    ),
    CasType(
        code="artisan",
        libelle="Artisan",
        affiliation="artisan",
        age_debut=24, age_liquidation=64, niveau_salaire=0.9,
        caisses=("rci_complementaire",),
        commentaire="Assiette de cotisation plus faible que celle d'un salarié.",
    ),
    CasType(
        code="exploitant_agricole",
        libelle="Chef d'exploitation agricole",
        affiliation="exploitant_agricole",
        age_debut=20, age_liquidation=64, niveau_salaire=0.5,
        caisses=("msa_exploitants",),
        commentaire=(
            "Retraite majoritairement forfaitaire aujourd'hui : la part non "
            "contributive disparaît intégralement dans les scénarios notionnels."
        ),
    ),
    CasType(
        code="profession_liberale",
        libelle="Profession libérale",
        affiliation="profession_liberale",
        age_debut=27, age_liquidation=66, niveau_salaire=2.5,
        caisses=("cnavpl",),
        commentaire="Régime de base CNAVPL et complémentaire Cipav, la section par "
                    "défaut. Un libéral d'une section spécialisée — auxiliaires "
                    "médicaux, pharmaciens, notaires — aurait un complémentaire "
                    "différent, et celui-là n'est pas paramétré. Il a porté "
                    "jusqu'au 22 septembre 2026 une règle à lui, « ouverture plus "
                    "deux ans », qui n'était qu'un contournement : le moteur ne "
                    "savait pas opposer de durée à une carrière tout en points, et "
                    "le taux plein lui rendait donc l'âge d'ouverture. Le défaut "
                    "corrigé, la règle ordinaire le date comme les autres, et le "
                    "COR la confirme — son cas type n° 13, un médecin libéral de "
                    "secteur 1 né en 1960, « peut prétendre à un départ à 62 ans » "
                    "et « atteint le taux plein à 66 ans et 9 mois », quand cette "
                    "fiche donne 62,00 et 67,00 pour la même génération."),
    CasType(
        code="contractuel_public",
        libelle="Agent contractuel de la fonction publique",
        affiliation="contractuel_public",
        age_debut=24, age_liquidation=64, niveau_salaire=0.85,
        caisses=("ircantec",),
        commentaire="Régime général + Ircantec.",
    ),
)

#: Générations couvertes par défaut : de la première génération entièrement
#: couverte par la Sécurité sociale aux actifs entrés récemment.
GENERATIONS = (1940, 1950, 1960, 1970, 1980, 1990, 2000)


def poids_effectifs(effectifs: "EffectifsRetraites", annee: int,
                    cas_types: tuple[CasType, ...] = CAS_TYPES) -> dict[str, float]:
    """Poids de chaque cas type une année donnée, tirés des effectifs de caisse.

    La grille des cas types n'est pas un échantillon : elle couvre les
    configurations du système, pas sa population. Rien ne s'oppose à ce qu'on
    l'utilise pour un AGRÉGAT, à condition de rendre à chaque configuration son
    poids réel — et c'est ce que les effectifs de la DREES donnent.

    **La règle.** Chaque cas type reçoit l'effectif de ses caisses. Une caisse
    réclamée par plusieurs cas types se partage ÉGALEMENT entre eux : la Cnav
    est la caisse des quatre carrières du privé, et rien ne dit combien de ses
    retraités ont été cadres, combien ont été au SMIC. C'est la seule part de
    convention égalitaire qui subsiste, et elle ne joue plus qu'à l'intérieur du
    salariat privé — non plus entre un agent de conduite et un salarié moyen.

    **Les poids sont normalisés** : leur somme vaut un. Seul leur rapport
    importe — la masse de pensions est de toute façon divisée par celle du
    scénario actuel — et la normalisation rend le résultat lisible.

    Un cas type sans caisse reçoit un poids nul et disparaît de l'agrégat ; ce
    serait une erreur silencieuse, et le contrôle qui l'interdit est dans les
    tests.
    """
    reclamants: dict[str, int] = {}
    for cas in cas_types:
        for caisse in cas.caisses:
            reclamants[caisse] = reclamants.get(caisse, 0) + 1

    bruts = {
        cas.code: sum(
            effectifs.effectif(caisse, annee) / reclamants[caisse]
            for caisse in cas.caisses
        )
        for cas in cas_types
    }
    total = sum(bruts.values())
    if total <= 0:
        raise ValueError(f"aucun effectif connu en {annee} pour pondérer les cas types")
    return {code: poids / total for code, poids in bruts.items()}


def poids_egaux(cas_types: tuple[CasType, ...] = CAS_TYPES) -> dict[str, float]:
    """L'ANCIENNE convention, gardée comme variante et non comme repli.

    Elle ne sert plus à calculer les résultats affichés ; elle sert à dire de
    combien elle les déplaçait, ce qu'aucun argument ne remplace.
    """
    return {cas.code: 1.0 / len(cas_types) for cas in cas_types}


@dataclass
class ResultatCasTypes:
    """Grille cas type × génération."""

    resultats: dict[tuple[str, int], Comparaison] = field(default_factory=dict)
    echecs: dict[tuple[str, int], str] = field(default_factory=dict)

    #: Les cinq grilles, dans l'ordre, avec le titre qui les introduit.
    GRILLES = (
        ("notionnel_retroactif",
         "scénario 2, notionnel RÉTROACTIF, part salariale seule"),
        ("notionnel_prospectif",
         "scénario 3, notionnel PROSPECTIF, part salariale seule"),
        ("notionnel_retroactif_employeur",
         "scénario 4, notionnel RÉTROACTIF, part patronale comprise"),
        ("notionnel_prospectif_employeur",
         "scénario 5, notionnel PROSPECTIF, part patronale comprise"),
        ("notionnel_liberal",
         "scénario 6, notionnel RÉTROACTIF, 18 % dès la bascule, garantie vieillesse"),
    )

    def tableau(self, cas_types=CAS_TYPES, generations=GENERATIONS) -> str:
        lignes = [
            "Écart de pension par rapport au système actuel, par scénario",
            "(en euros constants ; négatif = pension plus faible qu'aujourd'hui)",
        ]
        for scenario, titre in self.GRILLES:
            lignes += [
                "",
                f"Écart de pension — {titre}",
                "",
                f"{'Cas type':<46} " + " ".join(f"{g:>7}" for g in generations),
                "-" * (46 + 8 * len(generations)),
            ]
            for cas in cas_types:
                cellules = []
                for generation in generations:
                    comparaison = self.resultats.get((cas.code, generation))
                    if comparaison is None:
                        cellules.append(f"{'—':>7}")
                    else:
                        cellules.append(f"{comparaison.variation(scenario):>+7.0%}")
                lignes.append(f"{cas.libelle[:45]:<46} " + " ".join(cellules))

        if self.echecs:
            lignes += ["", "Cas non calculés :"]
            for (code, generation), motif in sorted(self.echecs.items()):
                lignes.append(f"  {code} / {generation} : {motif}")
        return "\n".join(lignes)

    def dictionnaire(self) -> dict:
        return {
            f"{code}|{generation}": comparaison.dictionnaire()
            for (code, generation), comparaison in self.resultats.items()
        }


def calculer_cas_types(
    simulateur: Simulateur,
    cas_types: tuple[CasType, ...] = CAS_TYPES,
    generations: tuple[int, ...] = GENERATIONS,
    liquidation: str = "droit",
) -> ResultatCasTypes:
    """Calcule la grille complète cas type × génération.

    Les combinaisons impossibles — un régime qui n'existait pas encore, une
    liquidation avant l'origine de la répartition — sont écartées avec leur
    motif plutôt que de faire échouer l'ensemble.

    ``liquidation`` choisit à quel âge chaque cas type part : ``droit``, celui
    que le droit de sa génération lui ouvre, ou ``absolu``, l'âge écrit dans la
    grille. Le second n'existe que pour mesurer ce que le premier a déplacé.
    """
    if liquidation not in VARIANTES_LIQUIDATION:
        raise ValueError(
            f"variante de liquidation inconnue : {liquidation!r} "
            f"(attendu : {VARIANTES_LIQUIDATION})"
        )
    resultat = ResultatCasTypes()
    for cas in cas_types:
        for generation in generations:
            cle = (cas.code, generation)
            try:
                carriere = cas.construire(simulateur, generation, liquidation)
                if carriere.annee_liquidation <= simulateur.parametres.annee_debut_repartition:
                    resultat.echecs[cle] = "liquidation antérieure à la répartition"
                    continue
                regimes_connus = any(
                    simulateur.affiliations.regimes(cas.affiliation, ligne.annee)
                    for ligne in carriere.lignes
                )
                if not regimes_connus:
                    resultat.echecs[cle] = "aucun régime actif sur la période"
                    continue
                resultat.resultats[cle] = simulateur.simuler(carriere)
            except (ValueError, KeyError) as erreur:
                resultat.echecs[cle] = str(erreur)
    return resultat


@dataclass(frozen=True)
class EcartsMedians:
    """L'ordre de grandeur de ce que la proposition change, lu sur la grille.

    La grille dit carrière par carrière ce que la proposition sert, rapporté à
    ce que le système actuel promet. La question qu'on lui pose d'abord est
    plus courte — « de combien ma retraite baisse-t-elle ? » — et elle appelle
    trois nombres, parce qu'elle a trois lecteurs.

    - Qui n'est PAS ENCORE à la retraite, et ne place rien : la répartition et
      les cinq points capitalisés obligatoires, la rente des cinq points rendus
      retirée. C'est ce qu'il touche sans rien ajouter.
    - Le même, les cinq points rendus placés : l'écart que la grille affiche,
      le « jusqu'à » du simulateur.
    - Qui est DÉJÀ à la retraite : sa pension d'AUJOURD'HUI, recalculée et
      garantie vieillesse comprise, rapportée à celle qu'il touche. Pas celle
      du départ, que la grille affiche : la garantie ne s'ouvre qu'à
      soixante-cinq ans, les deux pensions n'ont pas été revalorisées de la
      même façon depuis, et c'est la pension d'aujourd'hui que la bascule
      recalculerait.

    DES MÉDIANES, parce qu'un ordre de grandeur doit dire la carrière du
    milieu, pas celle que la moyenne tire vers les régimes à départ précoce.
    Médiane basse — l'élément de rang ``n // 2`` des écarts rangés par ordre
    croissant —, la convention de ``_deplacement_des_ecarts``. Les cases
    pèsent chacune autant, comme sur la page qui affiche la grille ; l'action
    113 de la feuille de route dit ce qu'une pondération par les effectifs y
    changerait.

    Des nombres signés : négatifs quand la proposition sert moins.
    """

    a_venir: float
    a_venir_volontaire: float
    deja_liquidees: float
    cases_a_venir: int
    cases_deja_liquidees: int


def _mediane_basse(valeurs: list[float]) -> float:
    rangees = sorted(valeurs)
    return rangees[len(rangees) // 2]


def ecarts_medians(resultat: ResultatCasTypes,
                   scenario: str = "notionnel_liberal") -> EcartsMedians:
    """Les trois écarts médians de ``scenario`` au système actuel.

    Une carrière est déjà à la retraite si le simulateur lui a calculé une
    pension d'aujourd'hui, c'est-à-dire si elle a liquidé avant l'année
    courante ; les autres sont à venir. Un groupe vide est une erreur, et non
    une médiane qui vaudrait zéro : l'accueil l'écrirait.
    """
    a_venir: list[float] = []
    a_venir_volontaire: list[float] = []
    deja_liquidees: list[float] = []
    for comparaison in resultat.resultats.values():
        aujourd_hui = comparaison.aujourd_hui
        if aujourd_hui is None:
            reference = comparaison.actuel.pension_annuelle
            if reference <= 0.0:
                continue
            totale = comparaison.pension_totale(scenario)
            volontaire = comparaison.rente_capitalisee_volontaire(scenario)
            a_venir.append((totale - volontaire) / reference - 1.0)
            a_venir_volontaire.append(totale / reference - 1.0)
        else:
            reference = aujourd_hui.pension("actuel")
            if reference <= 0.0:
                continue
            servie = (aujourd_hui.pension_totale(scenario)
                      - (aujourd_hui.rente_capitalisee_volontaire
                         if scenario == "notionnel_liberal" else 0.0))
            deja_liquidees.append(servie / reference - 1.0)
    if not a_venir or not deja_liquidees:
        raise ValueError(
            "écarts médians : aucune carrière "
            + ("à venir" if not a_venir else "déjà liquidée")
            + " dans la grille"
        )
    return EcartsMedians(
        a_venir=_mediane_basse(a_venir),
        a_venir_volontaire=_mediane_basse(a_venir_volontaire),
        deja_liquidees=_mediane_basse(deja_liquidees),
        cases_a_venir=len(a_venir),
        cases_deja_liquidees=len(deja_liquidees),
    )
