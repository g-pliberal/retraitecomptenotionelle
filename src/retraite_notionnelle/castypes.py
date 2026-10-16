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

from dataclasses import dataclass, field, replace

from typing import TYPE_CHECKING

from .carriere import PROFIL_AUTOMATIQUE, PROFIL_SMIC, Carriere, Metier
from .donnees.chargement import dans_un_instantane
from .simulateur import Comparaison, Simulateur
from . import pilote
from .pilote import VARIANTES_LIQUIDATION
from .somme import somme_ordonnee

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
    #: se partage entre eux, également sauf si chacun déclare la sienne.
    caisses: tuple[str, ...] = ()
    #: La part de ses caisses partagées que ce cas type porte, quand le
    #: partage n'est pas égal : ``(("cnracl", 0.2),)``. Ce que la caisse compte
    #: n'est pas une population homogène, et la part de chaque départ se
    #: publie (action 138, étape 3). Ou tous les cas types qui réclament une
    #: caisse dans la grille déclarent leur part, ou aucun : les parts déclarées
    #: sont ramenées à leur somme, si bien qu'un cas type seul de sa caisse,
    #: dans une grille réduite, la porte entière.
    parts_caisses: tuple[tuple[str, float], ...] = ()
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
    #: l'agent de conduite, l'agent des IEG. Leur cas type existe pour montrer
    #: ce départ-là. Elle suit tout ce que le droit fait varier — l'âge légal
    #: par génération, l'âge propre d'un régime spécial, et jusqu'à sa
    #: FERMETURE : l'agent de conduite né en 2000 est embauché après 2020,
    #: relève du régime général, et liquide donc à l'âge de celui-ci et non à
    #: cinquante-deux ans. La catégorie active l'a portée jusqu'au 14 octobre
    #: 2026 : le jaune pensions annexé au PLF 2027 a montré que ses agents n'en
    #: usent pas — les actifs de la CNRACL partent à 61,0 ans en 2025, trois
    #: ans et quart après l'ouverture du cas type, et 7,8 % seulement avec une
    #: décote (tableau B-5) —, et elle part depuis au taux plein, que le
    #: classement lui ouvre plus tôt qu'aux sédentaires (action 159, étape 5).
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
    #: Sous les conventions de projection du COR seulement — la page Coût — :
    #: le statut des premières années, avant l'entrée dans le régime de
    #: l'affiliation, pendant
    #: :meth:`~retraite_notionnelle.donnees.macro.DonneesMacro.delai_entree_fonction_publique`
    #: années (action 147, étape 11 ; les deux fonctionnaires civils, au délai
    #: que mesurent les services du jaune pensions, depuis l'action 159,
    #: étape 5). Vide, la carrière n'a qu'un statut, et la page Cas types
    #: montre toujours celle-là : le droit d'une carrière, non une projection.
    affiliation_avant_entree: str = ""
    #: La série de ``macro/hypotheses_projection.yaml`` qui donne ce délai,
    #: génération par génération (:meth:`~retraite_notionnelle.donnees.macro.DonneesMacro.delai_entree`) :
    #: celle de l'État, que le COR fait croître de six ans d'ici la génération
    #: 2000, ou celle de la CNRACL, que rien ne fait varier.
    serie_entree: str = "entree_fonction_publique"

    def niveau_relatif(self, simulateur: Simulateur, generation: int) -> float:
        """Son salaire en multiples du salaire moyen : ce qui le RATTACHE à un
        vingtile de niveau de vie hors du simulateur
        (``DonneesMortalite.population_niveau_de_vie``).

        Le niveau écrit, sauf sous :data:`~retraite_notionnelle.carriere.PROFIL_SMIC`,
        dont le niveau est un multiple du SMIC : c'est alors celui de la
        carrière construite, tel que le simulateur le lit
        (:func:`~retraite_notionnelle.moteur.conversion.niveau_relatif`).
        """
        if self.profil_carriere != PROFIL_SMIC:
            return self.niveau_salaire
        from .moteur.conversion import niveau_relatif

        return niveau_relatif(self.construire(simulateur, generation), simulateur.macro)

    def age_liquidation_pour(self, simulateur: Simulateur, generation: int,
                             variante: str = "droit") -> float:
        """L'âge auquel ce cas type liquide, étant né en ``generation`` : le
        pilote le fixe (:func:`~retraite_notionnelle.pilote.age_de_depart`)."""
        return pilote.age_de_depart(simulateur, self, generation, variante)

    def construire(self, simulateur: Simulateur, generation: int,
                   variante: str = "droit") -> Carriere:
        return self.carriere_a(simulateur, generation,
                               self.age_liquidation_pour(simulateur, generation, variante))

    def carriere_a(self, simulateur: Simulateur, generation: int, age: float) -> Carriere:
        """La carrière de ce cas type liquidée à ``age``, et non à l'âge que
        le pilote fixe : celle que les indicateurs à chaque âge de départ
        balaient (``scripts/cycle_de_vie.py --ages``)."""
        if self.affiliation_avant_entree and simulateur.parametres.conventions_cor:
            delai = simulateur.macro.delai_entree(self.serie_entree, generation)
            if delai > 0.0:
                return self._carriere_entree_tardive(simulateur, generation, age, delai)
        return self._carriere(simulateur, generation, age)

    def _carriere_entree_tardive(self, simulateur: Simulateur, generation: int,
                                 age_liquidation: float, delai: float) -> Carriere:
        """La carrière d'un fonctionnaire entré tard dans son régime : ses
        ``delai`` premières années sous :attr:`affiliation_avant_entree`, au
        même niveau de salaire, le reste dans le régime.

        L'âge de départ est celui que le pilote a fixé sur la carrière d'un
        seul statut : l'entrée tardive ne fait partir personne plus tard. Le
        pilote attendrait sinon que la petite pension du régime général soit
        elle aussi au taux plein — deux ans de plus pour la génération 1945,
        que le régime de l'État servait entière dès soixante ans —, ce
        qu'aucun fonctionnaire ne fait pour quelques euros.
        Le COR fait partir de même ses cas types au taux plein de leur régime
        principal.
        """
        interruptions = {
            int(generation + self.age_debut + decalage): motif
            for decalage, motif in self.interruptions_relatives
        }
        carriere = simulateur.carriere_parcours(
            annee_naissance=generation,
            sexe=self.sexe,
            metiers=[Metier(self.affiliation_avant_entree, self.age_debut,
                            self.niveau_salaire),
                     Metier(self.affiliation, self.age_debut + delai,
                            self.niveau_salaire)],
            age_liquidation=age_liquidation,
            profil_carriere=self.profil_carriere,
            interruptions=interruptions,
            nombre_enfants=self.nombre_enfants,
            part_primes=self.part_primes,
            identifiant=f"{self.libelle} (génération {generation})",
        )
        return primes_projetees(carriere, simulateur.macro)

    def options(self, generation: int, age_liquidation: float) -> dict:
        """Les options de la carrière d'un seul statut de ce cas type, né en
        ``generation`` et liquidé à ``age_liquidation`` : celles de
        ``carriere_simple``, du simulateur et de son portage, que
        ``scripts/cycle_de_vie.py`` passe au portage (action 161, étape 5)."""
        return {
            "annee_naissance": generation,
            "sexe": self.sexe,
            "affiliation": self.affiliation,
            "age_debut": self.age_debut,
            "age_liquidation": age_liquidation,
            "niveau_salaire": self.niveau_salaire,
            "profil_carriere": self.profil_carriere,
            "interruptions": {
                int(generation + self.age_debut + decalage): motif
                for decalage, motif in self.interruptions_relatives
            },
            "nombre_enfants": self.nombre_enfants,
            "part_primes": self.part_primes,
            "identifiant": f"{self.libelle} (génération {generation})",
        }

    def _carriere(self, simulateur: Simulateur, generation: int,
                  age_liquidation: float) -> Carriere:
        carriere = simulateur.carriere_simple(**self.options(generation, age_liquidation))
        if not simulateur.parametres.conventions_cor:
            return carriere
        return primes_projetees(carriere, simulateur.macro)


def primes_projetees(carriere: Carriere, macro) -> Carriere:
    """La carrière d'un cas type de fonctionnaire, sa part des primes portée
    comme le COR la projette.

    Le COR fait décrocher le traitement indiciaire du salaire moyen jusqu'en
    2037 (annexe méthodologique du rapport de juin 2026, note 40), et monter
    d'autant la part des primes de ses cas types de fonctionnaires, au fil des
    générations : à rémunération totale égale, le traitement d'une année vaut
    ce qu'il valait, fois le traitement relatif
    (:meth:`~retraite_notionnelle.donnees.macro.DonneesMacro.traitement_indiciaire_relatif`).
    Avant 2025, le même rapport porte le décrochage déjà fait, de 2019 à 2024 :
    la part des primes y est plus basse, et la pension des générations parties
    plus haute (action 147, étape 9).
    Le cas type tenait sa part constante, et la pension de la fonction
    publique, liquidée sur le traitement, en suivait le salaire moyen ; celle
    des systèmes notionnels, qui cotisent sur la rémunération entière, ne
    bouge pas. Seuls les cas types la suivent, et sous
    ``Parametres.conventions_cor`` seulement, que la page Coût allume : une
    personne qui saisit sa part des primes dit la sienne, et la page Cas types
    montre le droit des carrières, non une projection du COR.
    """
    lignes = [
        replace(ligne, part_primes=1.0 - (1.0 - ligne.part_primes)
                * macro.traitement_indiciaire_relatif(ligne.annee))
        if ligne.part_primes > 0.0 and macro.traitement_indiciaire_relatif(ligne.annee) != 1.0
        else ligne
        for ligne in carriere.lignes
    ]
    if all(nouvelle is ancienne for nouvelle, ancienne in zip(lignes, carriere.lignes)):
        return carriere
    return carriere.avec_lignes(lignes)


#: Les départs pour ancienneté de la CNRACL en 2025, au jaune pensions annexé
#: au PLF 2027 (tableau B-5, ``macro/caracteristiques_fonction_publique.csv``) :
#: en catégorie active, sédentaires, en carrière longue — ceux-ci sédentaires
#: aussi, le tableau B-3bis ne comptant d'actifs que les 10 597 premiers. Un
#: départ sur cinq est actif, et la grille n'en avait qu'un : la caisse entière
#: partait au taux plein de la catégorie active (action 138, étape 3). Le flux,
#: non le stock, que le jaune ne partage pas : ses retraités les plus âgés
#: comptaient plus d'actifs — les infirmiers l'étaient tous avant 2010 —, mais
#: la page Coût se joue dans la projection, que le flux d'aujourd'hui fait.
DEPARTS_CNRACL_2025 = {"active": 10_597, "sedentaire": 27_477, "carriere_longue": 15_054}
PART_ACTIVE_CNRACL = (DEPARTS_CNRACL_2025["active"]
                      / somme_ordonnee(DEPARTS_CNRACL_2025.values()))

#: Les départs pour ancienneté des civils de l'État en 2025, au même jaune
#: (tableau B-4, La Poste et Orange compris, comme la caisse que la DREES
#: compte) : sédentaires hors carrières longues, actifs ouverts à cinquante-sept
#: ans et à cinquante-deux, en carrière longue — ceux-ci sédentaires, les
#: actifs du tableau B-3 n'étant que les 8 899 des deux catégories actives. Le
#: sédentaire de catégorie B portait la caisse entière : un départ sur cinq est
#: actif (action 138, étape 3).
DEPARTS_ETAT_CIVILS_2025 = {"sedentaire": 28_209, "active_57": 5_552,
                            "active_52": 3_347, "carriere_longue": 4_704}
PART_ACTIVE_ETAT = (DEPARTS_ETAT_CIVILS_2025["active_57"]
                    / somme_ordonnee(DEPARTS_ETAT_CIVILS_2025.values()))
PART_SUPER_ACTIVE_ETAT = (DEPARTS_ETAT_CIVILS_2025["active_52"]
                          / somme_ordonnee(DEPARTS_ETAT_CIVILS_2025.values()))

#: Jeu de cas types couvrant les principales configurations du système.
CAS_TYPES: tuple[CasType, ...] = (
    CasType(
        code="smic_carriere_complete",
        libelle="Salarié au niveau du SMIC, carrière complète",
        affiliation="salarie_prive_non_cadre",
        # Le SMIC de chaque année, à temps complet, et non une part fixe du
        # salaire moyen : 0,55 l'arrondissait, quand il en a valu 0,40 en 1970
        # et 0,52 en 2024 (action 147, étape 16).
        age_debut=18, age_liquidation=64, niveau_salaire=1.0,
        profil_carriere=PROFIL_SMIC,
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
        parts_caisses=(("fonction_publique_etat_civile",
                        1.0 - PART_ACTIVE_ETAT - PART_SUPER_ACTIVE_ETAT),),
        affiliation_avant_entree="contractuel_public",
        commentaire="Traitement indiciaire hors primes ; les primes relèvent du RAFP.",
    ),
    CasType(
        code="fonctionnaire_actif",
        libelle="Fonctionnaire de catégorie active (départ anticipé)",
        affiliation="fonctionnaire_territorial_hospitalier_actif",
        # L'agent actif moyen des départs de 2025 à la CNRACL, au jaune pensions
        # annexé au PLF 2027 (tableau B-5 ; action 159, étape 5) : mis en
        # paiement à 61,0 ans, à l'indice 508, après 127,6 trimestres de
        # services, 7,8 % seulement avec une décote. Le cas type partait à
        # l'âge d'ouverture, au niveau de 1,1 salaire moyen : trois ans et
        # quart trop tôt, sur un traitement d'un cinquième trop haut, deux
        # erreurs qui se compensaient. Le taux plein rend le départ, à
        # soixante-deux ans pour la génération qui part en 2025 ; le niveau de
        # 0,9, l'indice ; l'entrée tardive de la page Coût, les services.
        age_debut=22, age_liquidation=62, niveau_salaire=0.9,
        part_primes=0.22,
        profil_carriere="public_categorie_c",
        caisses=("cnracl",),
        parts_caisses=(("cnracl", PART_ACTIVE_CNRACL),),
        affiliation_avant_entree="contractuel_public",
        serie_entree="entree_cnracl",
        commentaire=(
            "Aide-soignant, agent technique territorial : l'emploi est classé, "
            "et l'article L. 24 lui ouvre la pension cinq ans avant les "
            "sédentaires — cinquante-cinq ans jusqu'à la génération 1956, "
            "cinquante-sept ensuite, cinquante-neuf pour celles que la réforme "
            "de 2023 atteint. Il ne part pas pour autant à cet âge : comme les "
            "actifs de la CNRACL, mis en paiement à 61 ans en 2025 et presque "
            "tous sans décote, il attend le taux plein, que le classement lui "
            "ouvre plus tôt qu'aux sédentaires."
        ),
    ),
    CasType(
        code="militaire",
        libelle="Militaire non officier (radiation après vingt-sept ans et demi de services)",
        affiliation="militaire",
        # Le militaire moyen des départs pour ancienneté du jaune budgétaire
        # (annexe au PLF 2026, action 152) : 110,1 trimestres de services et
        # une radiation à 48,7 ans en 2024 (tableau B-3) ; un indice de
        # liquidation qui vaut de 0,83 à 0,98 salaire moyen de 2003 à 2024,
        # 0,90 en moyenne (tableau 98), soit 1,15 salaire moyen primes
        # comprises, le profil de l'État portant la solde de la radiation à
        # 1,05 fois sa moyenne. Le cas type partait à quarante-quatre ans
        # après vingt-cinq ans de services, au niveau de 0,95 salaire moyen :
        # un non-officier des armées parti tôt, quand il porte le poids de tous.
        age_debut=21, age_liquidation=48.5, niveau_salaire=1.15,
        part_primes=0.25,
        caisses=("fonction_publique_etat_militaire",),
        regle_liquidation="services", ecart_liquidation=27.5,
        commentaire=(
            "La pension militaire ne s'ouvre pas à un âge mais à une durée : "
            "dix-sept ans de services pour un non-officier. C'est le départ le "
            "plus précoce du système, et celui qu'un compte notionnel déplace le plus : plus de trente ans de rente pour vingt-sept ans et demi de cotisations. "
            "Le cas type est le militaire moyen des départs de 2024, radié à "
            "quarante-huit ans et demi, à la solde moyenne de tous, officiers "
            "compris. Il lui manque les bénéfices de campagne et les "
            "bonifications de service aérien, que le simulateur ne saisit pas. "
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
            "2016, cinquante-neuf à compter de 2034."
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

def _cas(code: str) -> CasType:
    return next(cas for cas in CAS_TYPES if cas.code == code)


#: L'agent SÉDENTAIRE de la CNRACL, que la page Coût pèse avec l'actif et que
#: la page Cas types ne montre pas : la même carrière de catégorie C, hors de
#: l'emploi classé. Il part au taux plein des sédentaires — les sédentaires de
#: la CNRACL sont mis en paiement à 64,0 ans en 2025, trois ans après les
#: actifs (tableau B-5) —, à l'indice 489,5 contre 508, d'où son niveau, et
#: avec un quart de services en moins : il entre tard à la caisse
#: (``entree_cnracl_sedentaire``). Les
#: deux portent la caisse dans la proportion de leurs départs
#: (:data:`PART_ACTIVE_CNRACL`). Son code dit de quel cas type il est la
#: variante : les poids que la page affiche l'y rapportent
#: (:func:`cas_type_affiche`).
AGENT_SEDENTAIRE_CNRACL = replace(
    _cas("fonctionnaire_actif"),
    code="fonctionnaire_actif~sedentaire",
    libelle="Agent sédentaire de la fonction publique territoriale ou hospitalière",
    affiliation="fonctionnaire_territorial_hospitalier",
    age_liquidation=64,
    niveau_salaire=round(0.9 * 489.5 / 508, 2),
    parts_caisses=(("cnracl", 1.0 - PART_ACTIVE_CNRACL),),
    serie_entree="entree_cnracl_sedentaire",
    commentaire=(
        "Agent technique, adjoint administratif territorial ou hospitalier, "
        "hors catégorie active : quatre départs sur cinq de la CNRACL. La "
        "pension ne s'ouvre qu'à l'âge légal, et il part au taux plein."
    ),
)

#: Les deux fonctionnaires ACTIFS de l'État, que la page Coût pèse avec le
#: sédentaire de catégorie B et que la page Cas types ne montre pas : la même
#: carrière, dans un emploi classé. Les actifs ouverts à cinquante-sept ans —
#: douaniers de la surveillance, instituteurs d'hier — sont mis en paiement à
#: 61,9 ans en 2025, à l'indice 757,9 contre 735,3 aux sédentaires ; ceux
#: ouverts à cinquante-deux — policiers, surveillants pénitentiaires —, à 58,3
#: ans, à l'indice 768,2, avec 22,9 trimestres de bonification du cinquième
#: (tableau B-4). Chacun part au
#: taux plein de sa catégorie, et porte la caisse dans la proportion de ses
#: départs (:data:`PART_ACTIVE_ETAT`, :data:`PART_SUPER_ACTIVE_ETAT`).
FONCTIONNAIRE_ACTIF_ETAT = replace(
    _cas("fonctionnaire_sedentaire"),
    code="fonctionnaire_sedentaire~actif",
    libelle="Fonctionnaire de l'État de catégorie active",
    affiliation="fonctionnaire_etat_actif",
    age_liquidation=62,
    niveau_salaire=round(1.2 * 757.9 / 735.3, 2),
    parts_caisses=(("fonction_publique_etat_civile", PART_ACTIVE_ETAT),),
    commentaire=(
        "Douanier de la surveillance, instituteur d'avant le corps des "
        "professeurs des écoles : "
        "l'emploi classé ouvre la pension cinq ans avant les sédentaires, et "
        "il part au taux plein de sa catégorie."
    ),
)
FONCTIONNAIRE_SUPER_ACTIF_ETAT = replace(
    _cas("fonctionnaire_sedentaire"),
    code="fonctionnaire_sedentaire~super_actif",
    libelle="Fonctionnaire de l'État de catégorie super-active",
    affiliation="fonctionnaire_etat_super_actif",
    age_liquidation=57,
    niveau_salaire=round(1.2 * 768.2 / 735.3, 2),
    parts_caisses=(("fonction_publique_etat_civile", PART_SUPER_ACTIVE_ETAT),),
    commentaire=(
        "Policier, surveillant pénitentiaire : la pension s'ouvre dix ans "
        "avant les sédentaires, la bonification du cinquième s'ajoute aux "
        "services, et il part au taux plein de sa catégorie."
    ),
)

#: La grille de la page Coût : les cas types de la page Cas types, et les
#: variantes qui partagent leur caisse avec eux.
GRILLE_DU_COUT: tuple[CasType, ...] = CAS_TYPES + (
    AGENT_SEDENTAIRE_CNRACL, FONCTIONNAIRE_ACTIF_ETAT, FONCTIONNAIRE_SUPER_ACTIF_ETAT)


def cas_type_affiche(code: str) -> str:
    """Le cas type de la page dont ``code`` est la variante, lui-même sinon."""
    return code.split("~", 1)[0]


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
    réclamée par plusieurs cas types se partage entre eux selon la part que
    chacun déclare (:attr:`CasType.parts_caisses`) quand elle se publie — la
    CNRACL entre ses départs actifs et sédentaires, au jaune pensions —, et
    ÉGALEMENT sinon : la Cnav est la caisse des quatre carrières du privé, et
    rien ne dit combien de ses retraités ont été cadres, combien ont été au
    SMIC. C'est la seule part de convention égalitaire qui subsiste, et elle ne
    joue plus qu'à l'intérieur du salariat privé — non plus entre un agent de
    conduite et un salarié moyen.

    **Les poids sont normalisés** : leur somme vaut un. Seul leur rapport
    importe — la masse de pensions est de toute façon divisée par celle du
    scénario actuel — et la normalisation rend le résultat lisible.

    Un cas type sans caisse reçoit un poids nul et disparaît de l'agrégat ; ce
    serait une erreur silencieuse, et le contrôle qui l'interdit est dans les
    tests.
    """
    parts = parts_des_caisses(cas_types)
    bruts = {
        cas.code: somme_ordonnee(
            effectifs.effectif(caisse, annee) * parts[(cas.code, caisse)]
            for caisse in cas.caisses
        )
        for cas in cas_types
    }
    total = somme_ordonnee(bruts.values())
    if total <= 0:
        raise ValueError(f"aucun effectif connu en {annee} pour pondérer les cas types")
    return {code: poids / total for code, poids in bruts.items()}


def parts_des_caisses(cas_types: tuple[CasType, ...] = CAS_TYPES
                      ) -> dict[tuple[str, str], float]:
    """La part de chaque caisse que chaque cas type porte, ``(code, caisse)``.

    Égale entre les cas types qui la réclament, sauf s'ils déclarent tous la
    leur, ramenée alors à la somme des parts déclarées. Un partage où les uns
    déclarent et les autres non lève : il n'y a pas de bonne façon de le lire.
    """
    reclamants: dict[str, list[CasType]] = {}
    for cas in cas_types:
        for caisse in cas.caisses:
            reclamants.setdefault(caisse, []).append(cas)
    parts: dict[tuple[str, str], float] = {}
    for caisse, cas_de_la_caisse in reclamants.items():
        declarees = [dict(cas.parts_caisses).get(caisse) for cas in cas_de_la_caisse]
        if all(part is None for part in declarees):
            for cas in cas_de_la_caisse:
                parts[(cas.code, caisse)] = 1.0 / len(cas_de_la_caisse)
            continue
        if any(part is None for part in declarees) or any(part <= 0.0 for part in declarees):
            raise ValueError(f"la caisse {caisse!r} : parts déclarées par les uns, "
                             f"non par les autres, ou nulles")
        total = somme_ordonnee(declarees)
        for cas, part in zip(cas_de_la_caisse, declarees):
            parts[(cas.code, caisse)] = part / total
    return parts


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


@dans_un_instantane
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
                carriere = carriere_de_la_grille(simulateur, cas, generation, liquidation)
                resultat.resultats[cle] = simulateur.simuler(carriere)
            except (ValueError, KeyError) as erreur:
                resultat.echecs[cle] = str(erreur)
    return resultat


def carriere_de_la_grille(simulateur: Simulateur, cas: CasType, generation: int,
                          liquidation: str = "droit") -> Carriere:
    """La carrière d'une case de la grille, ou ``ValueError`` portant le motif
    qui l'écarte : une liquidation avant l'origine de la répartition, un
    régime qui n'existait pas encore (:func:`calculer_cas_types`)."""
    carriere = cas.construire(simulateur, generation, liquidation)
    if carriere.annee_liquidation <= simulateur.parametres.annee_debut_repartition:
        raise ValueError("liquidation antérieure à la répartition")
    if not any(simulateur.affiliations.regimes(cas.affiliation, ligne.annee)
               for ligne in carriere.lignes):
        raise ValueError("aucun régime actif sur la période")
    return carriere


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
