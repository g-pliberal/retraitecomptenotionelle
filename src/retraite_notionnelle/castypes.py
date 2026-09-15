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

from .carriere import Carriere
from .simulateur import Comparaison, Simulateur

if TYPE_CHECKING:  # pragma: no cover - annotation seulement
    from .donnees.effectifs import EffectifsRetraites


@dataclass(frozen=True)
class CasType:
    """Une carrière de référence, indépendante de la génération."""

    code: str
    libelle: str
    affiliation: str
    age_debut: float
    age_liquidation: float
    niveau_salaire: float
    profil_carriere: str = "ascendant"
    sexe: str = "H"
    nombre_enfants: int = 0
    part_primes: float = 0.0
    interruptions_relatives: tuple[tuple[int, str], ...] = ()
    #: Caisses de ``effectifs_retraites.csv`` dont ce cas type porte les
    #: retraités. C'est par elles qu'il reçoit son POIDS dans les agrégats :
    #: voir :func:`poids_effectifs`. Une caisse réclamée par plusieurs cas types
    #: se partage entre eux.
    caisses: tuple[str, ...] = ()
    commentaire: str = ""

    def construire(self, simulateur: Simulateur, generation: int) -> Carriere:
        interruptions = {
            int(generation + self.age_debut + decalage): motif
            for decalage, motif in self.interruptions_relatives
        }
        return simulateur.carriere_simple(
            annee_naissance=generation,
            sexe=self.sexe,
            affiliation=self.affiliation,
            age_debut=self.age_debut,
            age_liquidation=self.age_liquidation,
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
        profil_carriere="fortement_ascendant",
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
            "trimestres assimilés, par l'AVPF — qui porte au compte un salaire "
            "au SMIC — et par la majoration de durée d'assurance ; le compte "
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
        caisses=("fonction_publique_etat_civile",),
        commentaire="Traitement indiciaire hors primes ; les primes relèvent du RAFP.",
    ),
    CasType(
        code="fonctionnaire_actif",
        libelle="Fonctionnaire de catégorie active (départ à 57 ans)",
        affiliation="fonctionnaire_territorial_hospitalier_actif",
        age_debut=22, age_liquidation=57, niveau_salaire=1.1,
        part_primes=0.22,
        caisses=("cnracl",),
        commentaire=(
            "Aide-soignant, agent technique territorial : l'emploi est classé, "
            "et le départ à cinquante-sept ans est celui que l'article L. 24 lui "
            "ouvre, non une anticipation sanctionnée. Le cas type était calculé "
            "comme un sédentaire tant qu'aucun statut ne portait le classement."
        ),
    ),
    CasType(
        code="militaire",
        libelle="Militaire non officier (radiation après vingt-cinq ans de services)",
        affiliation="militaire",
        age_debut=19, age_liquidation=44, niveau_salaire=0.95,
        part_primes=0.25,
        caisses=("fonction_publique_etat_militaire",),
        commentaire=(
            "La pension militaire ne s'ouvre pas à un âge mais à une durée : "
            "dix-sept ans de services pour un non-officier. C'est le départ le "
            "plus précoce du système, et celui qu'un compte notionnel déplace le "
            "plus — quarante ans de rente pour vingt-cinq ans de cotisations. "
            "La solde indiciaire seule ouvre des droits ; les indemnités, plus "
            "lourdes que les primes de la fonction publique civile, relèvent du "
            "RAFP."
        ),
    ),
    CasType(
        code="agent_sncf_conduite",
        libelle="Agent de conduite SNCF (départ à 52 ans)",
        affiliation="agent_sncf",
        age_debut=20, age_liquidation=52, niveau_salaire=1.1,
        caisses=("sncf",),
        commentaire="Écart à l'âge de référence parmi les plus élevés du système.",
    ),
    CasType(
        code="agent_ieg",
        libelle="Agent des industries électriques et gazières",
        affiliation="agent_ieg",
        age_debut=21, age_liquidation=57, niveau_salaire=1.4,
        caisses=("cnieg",),
        commentaire="Régime spécial fermé aux embauches depuis 2023.",
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
        profil_carriere="fortement_ascendant",
        caisses=("cnavpl",),
        commentaire="Régime de base CNAVPL et complémentaire Cipav, la section par "
                    "défaut. Un libéral d'une section spécialisée — auxiliaires "
                    "médicaux, pharmaciens, notaires — aurait un complémentaire "
                    "différent, et celui-là n'est pas paramétré.",
    ),
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
) -> ResultatCasTypes:
    """Calcule la grille complète cas type × génération.

    Les combinaisons impossibles — un régime qui n'existait pas encore, une
    liquidation avant l'origine de la répartition — sont écartées avec leur
    motif plutôt que de faire échouer l'ensemble.
    """
    resultat = ResultatCasTypes()
    for cas in cas_types:
        for generation in generations:
            cle = (cas.code, generation)
            try:
                carriere = cas.construire(simulateur, generation)
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
