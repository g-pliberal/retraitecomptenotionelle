"""Catalogue des régimes de retraite, de 1930 à aujourd'hui."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field, replace
from functools import cached_property
from pathlib import Path

from .chargement import Fiabilite, charger_yaml

#: Familles de régimes reconnues.
FAMILLES = {
    "base_prive",
    "complementaire_prive",
    "fonction_publique",
    "special",
    "non_salarie",
    "agricole",
    "liberal",
    "additionnel_capitalise",
}

#: Assiettes reconnues et leur borne exprimée en plafonds de la Sécurité sociale.
#: ``None`` signifie « pas de borne supérieure ».
BORNES_ASSIETTE: dict[str, tuple[float, float | None]] = {
    "plafonnee": (0.0, 1.0),
    "deplafonnee": (0.0, None),
    "tranche_1": (0.0, 1.0),
    "tranche_a": (0.0, 1.0),
    "tranche_2": (1.0, 8.0),
    # Tranche 2 de l'Arrco d'AVANT la fusion : elle s'arrêtait à trois plafonds,
    # là où celle de l'Agirc-Arrco va jusqu'à huit. Les confondre donnait à un
    # non-cadre des droits sur une assiette que son régime n'a jamais couverte.
    "tranche_2_arrco": (1.0, 3.0),
    # Tranche B de l'Ircantec, et de l'IPACTE avant elle : l'article 7 du
    # décret n° 70-1277 limite l'assiette à « 4,75 fois le plafond fixé pour
    # les cotisations de retraite du régime général », et le décret
    # n° 2008-996 du 23 septembre 2008 la porte à huit — elle prend alors la
    # borne commune. Lui prêter huit plafonds dès 1971 donnait des points sur
    # une assiette que le régime n'appelait pas.
    "tranche_2_ircantec": (1.0, 4.75),
    "tranche_b": (1.0, 4.0),
    "tranche_c": (4.0, 8.0),
    # Tranches propres au régime de base des professions libérales : la
    # première s'arrêtait à 0,85 plafond avant 2015, la seconde part de zéro
    # depuis — les deux se recouvrent donc, et c'est bien la règle du régime.
    "plafonnee_085_pass": (0.0, 0.85),
    "tranche_085_5_pass": (0.85, 5.0),
    "plafonnee_5_pass": (0.0, 5.0),
    # Complémentaires des indépendants : le revenu y est plafonné à trois
    # plafonds jusqu'en 2004 (D. 635-4), à quatre pour les artisans ensuite
    # (D. 635-7), et la réforme de 2008 y découpe deux tranches — l'article
    # fixe la borne de la première à 33 276 € pour 2008, qui est le plafond
    # de cette année-là.
    "plafonnee_3_pass": (0.0, 3.0),
    "plafonnee_4_pass": (0.0, 4.0),
    "tranche_1_4_pass": (1.0, 4.0),
    # Cipav depuis 2023 : 9 % jusqu'au plafond, 22 % du plafond au triple.
    "tranche_1_3_pass": (1.0, 3.0),
    # Cipav en 2024 : la seconde tranche va jusqu'à trois plafonds et demi,
    # puis jusqu'à quatre depuis 2025 (article 2 du décret n° 79-262).
    "tranche_1_3_5_pass": (1.0, 3.5),
    # CARPIMKO depuis 2026 : 8,70 % entre un demi et trois plafonds.
    "tranche_05_3_pass": (0.5, 3.0),
    # CAVOM depuis 2016 : 12,5 % du revenu, jusqu'à huit plafonds. C'est la
    # borne la plus haute du catalogue libéral, et le décret la fixe en
    # plafonds — 384 480 € en 2026. Le décret n° 2015-1875 y montait par
    # marches : quatre plafonds en 2016, cinq, six, sept, huit en 2020.
    "plafonnee_6_pass": (0.0, 6.0),
    "plafonnee_7_pass": (0.0, 7.0),
    "plafonnee_8_pass": (0.0, 8.0),
    # Tranche B de la CPS polynésienne : entre 269 000 et 525 000 FCFP par
    # mois, soit 0,69 à 1,35 plafond national — la borne la plus proche.
    "tranche_1_2_pass": (1.0, 2.0),
    # Régime des conjoints de commerçants (D. 635-36, 1985-2003) : un taux
    # « des revenus ou de la part des revenus qui n'excèdent pas le tiers du
    # plafond », un autre « de la part des revenus comprise entre le tiers
    # et le montant dudit plafond ».
    "plafonnee_033_pass": (0.0, 1.0 / 3.0),
    "tranche_033_1_pass": (1.0 / 3.0, 1.0),
    # CAVAMAC : le plafond des commissions, que la caisse indexe sur la
    # commission MOYENNE et non sur celui de la Sécurité sociale — 625 777 €
    # en 2026, quand treize plafonds en valent 624 780. C'est la meilleure
    # approximation indexable ; l'écart atteint 6 % en 2024.
    "plafonnee_13_pass": (0.0, 13.0),
    # Complémentaires des sections libérales : la CARMF prélève jusqu'à
    # trois plafonds et demi, le RAAP des artistes-auteurs jusqu'à trois.
    "plafonnee_3_5_pass": (0.0, 3.5),
    # Complémentaire des chirurgiens-dentistes : sa tranche part de
    # 0,85 plafond jusqu'en 2025, de 0,65 depuis la réforme de
    # l'assiette sociale de 2026.
    "tranche_065_5_pass": (0.65, 5.0),
    "hors_primes": (0.0, None),
    "primes_uniquement": (0.0, None),
    "forfaitaire": (0.0, None),
    "sans_objet": (0.0, None),
}


@dataclass(frozen=True)
class PointsGratuits:
    """Points attribués à la liquidation, sans cotisation, pour des années
    antérieures à la création du régime.

    C'est la RCO des non-salariés agricoles : créée en 2003, elle attribue au
    chef d'exploitation qui liquide depuis « 100 points de retraite
    complémentaire pour chacune des années de chef d'exploitation [...]
    accomplies avant le 1er janvier 2003 », dans la limite de « la différence
    entre trente-sept années et demie et le nombre d'années ayant donné lieu à
    affiliation » à la RCO (D. 732-154 du code rural), s'il réunit dix-sept
    ans et demi comme chef (D. 732-151) et le taux plein de son régime de base
    (L. 732-56, II, 2°, auquel renvoie le III).
    """

    #: Le régime de BASE dont les années ouvrent les points, celui où se
    #: comptent les dix-sept ans et demi, et dont le taux plein est la
    #: condition : le régime des non-salariés agricoles.
    regime: str
    #: Seules comptent les années accomplies AVANT le 1er janvier de cette
    #: année-là — celle où le régime qui attribue les points a été créé.
    avant: int
    points_par_annee: float
    #: Années validées dans ``regime`` à la date d'effet, toute la carrière,
    #: sans lesquelles rien n'est attribué.
    annees_minimum: float
    #: Plafond des années retenues, diminué des années d'affiliation au régime
    #: qui attribue les points.
    annees_maximum: float
    #: Date d'effet, (année, mois), à compter de laquelle la condition est
    #: d'avoir LIQUIDÉ au taux plein, par la durée ou par l'âge ; avant elle,
    #: il fallait réunir la durée requise pour ce taux (L. 732-56, II, 2°, dans
    #: sa version antérieure à la loi n° 2023-270 du 14 avril 2023).
    taux_plein_depuis: tuple[int, int]


def _points_gratuits(fiche: dict | None) -> PointsGratuits | None:
    """La règle écrite dans une fiche, dates « AAAA-MM » comprises."""
    if not fiche:
        return None
    annee, mois = str(fiche["taux_plein_depuis"]).split("-")
    return PointsGratuits(
        regime=str(fiche["regime"]),
        avant=int(fiche["avant"]),
        points_par_annee=float(fiche["points_par_annee"]),
        annees_minimum=float(fiche["annees_minimum"]),
        annees_maximum=float(fiche["annees_maximum"]),
        taux_plein_depuis=(int(annee), int(mois)),
    )


@dataclass(frozen=True)
class PeriodeRegime:
    """Jeu de paramètres d'un régime sur une plage d'années."""

    #: Code du régime dont cette période vient. Une période circule seule dans
    #: le moteur — `ouvrir.age_ouverture(moteur, periode, carriere)` ne reçoit
    #: qu'elle —, et
    #: certaines règles ont besoin de savoir DE QUEL RÉGIME elle est : la
    #: catégorie active et la pension militaire n'avancent l'âge que dans les
    #: régimes que leur statut route, non dans un régime spécial que la même
    #: carrière traverserait par ailleurs.
    regime: str
    debut: int
    fin: int | None
    type_calcul: str
    age_ouverture: float
    age_taux_plein: float
    duree_requise_trimestres: int | None
    #: La durée requise suit-elle la génération plutôt que l'année de
    #: liquidation ? Vrai depuis la loi Balladur pour les régimes alignés, la
    #: loi Fillon pour la fonction publique, leurs réformes propres pour les
    #: régimes spéciaux. La valeur ci-dessus sert alors de repli.
    duree_requise_par_generation: bool
    #: La table de durée requise PROPRE au régime, par génération, qui passe
    #: avant la table commune : `sncf_conduite`, `ratp`, `ieg_actif_*`
    #: (`legislation/duree_requise_regimes_speciaux.csv`). Leurs décrets
    #: écrivent chacun la sienne, et la suspension de 2026 ne les a pas touchés.
    duree_requise_table: tuple[str, ...]
    #: Le calendrier de durée requise lu à la DATE où l'assuré réunit les
    #: conditions, quand aucune table par génération ne répond :
    #: `regimes_speciaux_2008` (`legislation/duree_requise_calendriers.csv`).
    duree_requise_calendrier: str | None
    #: La surcote se compte-t-elle depuis l'âge du calendrier propre à la SNCF
    #: et à la RATP (`legislation/age_surcote_regimes_speciaux.csv`), et non
    #: depuis l'âge d'ouverture de la fiche ?
    age_surcote_regimes_speciaux: bool
    #: L'âge d'ouverture suit-il la génération plutôt que l'année de
    #: liquidation ? Vrai pour les régimes alignés sur l'âge légal général.
    age_ouverture_par_generation: bool
    #: L'âge d'annulation de la décote suit-il la génération ? Vrai depuis la
    #: loi du 9 novembre 2010 pour les régimes alignés (65 -> 67 ans).
    age_taux_plein_par_generation: bool
    #: Table d'âges PROPRE au régime, lue à la génération dans
    #: ``legislation/ages_regimes.csv`` : l'âge d'ouverture et l'âge du taux
    #: plein que le règlement d'une section écrit lui-même, et qui ne sont pas
    #: ceux du régime général. Elle passe avant les deux drapeaux ci-dessus ;
    #: ``None`` les laisse faire.
    age_table: str | None
    #: Le coefficient de minoration suit-il la génération ? Vrai pour les
    #: régimes alignés : la table de l'article R. 351-27 vaut aussi bien pour
    #: l'ancien droit (2,5 %) que pour la montée en charge de la loi Fillon.
    decote_par_generation: bool
    #: Le dénominateur de la PRORATISATION suit-il la table de l'article
    #: R. 351-6 plutôt que la durée requise pour le taux plein ? Ce sont deux
    #: paramètres distincts, et le moteur les confondait. Réservé aux régimes
    #: alignés sur le code de la sécurité sociale : la fonction publique et les
    #: régimes spéciaux ont la leur, calendaire, non modélisée.
    duree_proratisation_par_generation: bool
    #: Le nombre d'années retenues au salaire de référence suit-il la
    #: génération ? Vrai depuis la loi Balladur (dix à vingt-cinq années).
    salaire_reference_par_generation: bool
    #: Âge en deçà duquel la durée liquidable est PLAFONNÉE, et ce plafond en
    #: trimestres. Les marins sont seuls à porter cette règle : l'article R. 13
    #: de leur code fixe « le maximum des annuités liquidables dans les pensions
    #: d'ancienneté dont la liquidation est demandée avant cinquante-cinq ans
    #: […] à vingt-cinq annuités », là où la pension liquidée à cinquante-cinq
    #: ans en compte trente-sept et demie. Un marin parti à cinquante ans avec
    #: trente ans de mer ne touche donc pas 60 % du salaire forfaitaire, mais
    #: 50 %.
    duree_maximum_avant_age: float | None
    duree_maximum_avant_age_trimestres: int | None
    #: Le même article R. 13 lève ce plafond « au profit d'un marin âgé d'au
    #: moins cinquante-deux ans et demi, réunissant trente-sept annuités et
    #: demie de services » : l'âge, et la durée en trimestres.
    duree_maximum_levee_age: float | None
    duree_maximum_levee_trimestres: int | None
    #: Âge d'ouverture ABAISSÉ pour qui réunit une durée de services dans le
    #: régime : « la double condition de cinquante ans d'âge et de vingt-cinq
    #: années de services » de l'article R. 2 du code des pensions de retraite
    #: des marins. Sans cette durée, c'est `age_ouverture` qui vaut.
    age_ouverture_services: float | None
    services_ouverture_annees: float | None
    #: En deçà de cette durée de services, la pension est SPÉCIALE : elle suit
    #: l'entrée en jouissance d'une autre pension de base, jamais avant
    #: `age_ouverture`, et s'ouvre à défaut à l'âge ci-dessous (R. 5 et
    #: L. 5552-12 du code des transports pour les marins : quinze ans, soixante).
    pension_speciale_services_annees: float | None
    pension_speciale_age_sans_autre_pension: float | None
    taux_plein: float | None
    #: Taux de liquidation que les BONIFICATIONS peuvent porter au-delà de
    #: ``taux_plein`` : « Le pourcentage maximum fixé à l'article L 13 peut-être
    #: augmenté de cinq points du chef des bonifications » (L. 12 CPCMR), soit
    #: 80 % pour un maximum de 75 %. Les services seuls ne le dépassent jamais.
    #: ``None`` : aucune bonification ne passe le maximum.
    taux_maximum_bonifie: float | None
    salaire_reference: str
    assiette: str
    taux_cotisation_retraite: float
    #: Périmètre du taux ci-dessus : ``total`` (salarié + employeur, cas du
    #: privé) ou ``agent_seul`` (retenue de l'agent seule, cas de la fonction
    #: publique et des régimes spéciaux).
    perimetre_taux: str
    #: Fraction du taux ci-dessus supportée par l'assuré lui-même ; le
    #: complément est la part de l'employeur. ``1.0`` couvre les non-salariés,
    #: qui n'ont pas d'employeur, et les périodes ``agent_seul``, dont le taux
    #: est déjà la seule retenue de l'agent.
    part_salariale: float
    decote_par_trimestre: float | None
    #: Barème de décote applicable. ``regime_aligne`` (défaut) applique le
    #: coefficient ci-dessus, éventuellement lu à la génération ;
    #: ``fonction_publique`` applique celui de l'article L. 14 du code des
    #: pensions, dont le coefficient ET l'âge d'annulation montent en charge de
    #: 2006 à 2020 (``legislation/decote_fonction_publique.csv``) ;
    #: ``regimes_speciaux`` applique le même barème avec QUATRE ANS DE RETARD,
    #: celui que la réforme de 2008 a donné aux régimes spéciaux — rien avant
    #: le 1er juillet 2010, un dixième du taux plein ensuite, 1,25 % seulement
    #: en 2019 (``legislation/decote_regimes_speciaux.csv``) ;
    #: ``regimes_speciaux_age_fixe`` en prend le coefficient mais garde l'âge
    #: d'annulation de la fiche, comme le V de l'article 14 le fait pour les
    #: catégories d'âge atypique — artistes du ballet, musiciens de l'orchestre.
    bareme_decote: str
    #: La durée d'assurance annule-t-elle la décote ? Vrai depuis l'ordonnance
    #: du 26 mars 1982, qui ouvre le taux plein à 60 ans à qui a la durée
    #: requise. Avant elle, le taux ne dépendait QUE de l'âge : 20 % à 60 ans
    #: majorés de 4 points par année différée jusqu'en 1971, 50 % à 65 ans
    #: diminués de 5 points par année anticipée ensuite. Une carrière longue
    #: n'y changeait rien.
    decote_annulee_par_la_duree: bool
    #: La décote se compte-t-elle sur la SEULE durée, l'âge ne faisant que
    #: l'annuler une fois atteint ? C'est la CRPN depuis le 1er janvier 2022 :
    #: « une décote égale à 5 % par annuité manquante » sous trente annuités
    #: (R. 6527-22 du code des transports), qui tombe à l'âge du premier alinéa
    #: de L. 6521-4, soixante ans (R. 6527-23). Le plus petit des deux manques,
    #: que le moteur prend partout ailleurs, retirait moins que le droit dès
    #: que l'âge était proche et la carrière courte.
    decote_par_la_duree_seule: bool
    #: Nombre maximal de trimestres de décote opposables. Vingt dans tous les
    #: régimes qui en appliquent une : au-delà, le taux ne descend plus.
    #: ``None`` lève le plafond.
    decote_trimestres_maximum: int | None
    #: Décote à DEUX PENTES d'un régime en points : les trimestres manquants
    #: au-delà de cet âge se comptent au second taux. La CAVP minore de 1,25 %
    #: par trimestre jusqu'à 65 ans et de 0,5 % de 65 ans à l'âge du taux
    #: plein. ``None`` : un seul taux.
    decote_palier_age: float | None
    decote_par_trimestre_apres_palier: float | None
    #: Taux plein ANTICIPÉ d'une affiliée, par enfant : d'autant d'années
    #: avant l'âge du taux plein, dans la limite du maximum. La CARCDSF l'ouvre
    #: « à raison d'une année d'anticipation par enfant mis au monde, dans la
    #: limite de 5 années ». ``None`` : aucun.
    taux_plein_anticipe_par_enfant_annees: float | None
    taux_plein_anticipe_maximum_annees: float | None
    surcote_par_trimestre: float | None
    #: Barème DATÉ de la surcote — ``regime_general`` ou ``fonction_publique`` —,
    #: lu dans ``legislation/surcote_baremes.csv`` trimestre par trimestre ;
    #: ``None`` applique le taux plat ci-dessus à tous les trimestres.
    surcote_bareme: str | None
    #: Barème d'abattement des régimes en points. ``decote_du_regime_de_base``
    #: applique le coefficient de minoration ci-dessus ; ``agirc_arrco``
    #: applique les coefficients d'anticipation propres à ce régime.
    abattement_points: str
    #: Barème de MAJORATION des régimes en points liquidés APRÈS le taux
    #: plein. ``aucune`` quand la fiche n'en écrit pas ; ``regime_general``
    #: compte les trimestres COTISÉS après l'âge légal et au-delà de la durée
    #: requise, comme la branche en annuités (CNAVPL, MSA des non-salariés) ;
    #: ``par_age_seul`` compte les trimestres civils ENTIERS écoulés depuis
    #: ``surcote_age_debut`` — l'âge du taux plein à défaut —, sans condition
    #: de durée, comme l'écrivent les statuts des sections libérales ;
    #: ``ircantec`` applique le IV de l'article 16 de l'arrêté du 30 décembre
    #: 1970 — 0,75 % par trimestre écoulé au-delà de l'âge du taux plein,
    #: 0,625 % par trimestre cotisé au-delà de la durée requise en deçà.
    surcote_points: str
    #: Bornes du décompte ``par_age_seul`` : âge de départ (``None`` : l'âge
    #: du taux plein), âge au-delà duquel plus rien ne compte, nombre maximal
    #: de trimestres, pas du décompte (4 : années pleines seulement), âge
    #: d'un second taux et ce taux, durée d'affiliation au régime exigée.
    surcote_age_debut: float | None
    surcote_age_maximum: float | None
    surcote_trimestres_maximum: int | None
    surcote_pas_trimestres: int
    surcote_palier_age: float | None
    surcote_par_trimestre_apres_palier: float | None
    surcote_affiliation_minimale_trimestres: int | None
    #: ``par_age_seul`` ne compte que les trimestres COTISÉS depuis l'âge de
    #: départ du décompte, et non le temps écoulé : la CAVAMAC majore depuis
    #: 2024 « pour chaque année pleine cotisée dans le présent régime ».
    surcote_trimestres_cotises: bool
    #: Plafond en euros de la majoration pour enfants, et année à laquelle il
    #: est publié. Le plafond suit ensuite la valeur de service du point.
    plafond_majoration_enfants: float | None
    plafond_majoration_annee: int | None
    #: Barème PROPRE de la majoration pour enfants, indexé par le nombre
    #: d'enfants — le dernier taux vaut au-delà. ``None`` : le barème commun
    #: de ``_taux_majoration_enfants``. Les marins bonifient dès DEUX enfants,
    #: 5 %, puis 10 % pour trois et 15 % au-delà (R. 14 de leur code).
    taux_majoration_enfants: tuple[float, ...] | None
    #: Nombre de points attribués quand l'assiette atteint le repère
    #: ci-dessous. Sert aux régimes dont le barème est écrit en POINTS et non
    #: en prix d'achat — le régime de base des libéraux, la complémentaire
    #: agricole. ``None`` : les points s'achètent, cf. ``valeurs_point.csv``.
    points_maximum: float | None
    #: Bornes de l'assiette exprimées EN EUROS plutôt qu'en plafonds de la
    #: Sécurité sociale. La plupart des régimes découpent leur assiette en
    #: multiples du plafond, qui suit les salaires ; d'autres la fixent en
    #: euros et ne l'indexent pas. C'est le cas des tranches de la
    #: complémentaire des avocats : 42 507 € en 2023, en 2025 et en 2026, alors
    #: que le plafond passait de 43 992 à 48 060 € sur la même période. Les
    #: exprimer en plafonds les ferait donc dériver. ``None`` : les bornes en
    #: plafonds ci-dessus s'appliquent.
    borne_basse_euros: float | None
    borne_haute_euros: float | None
    #: Pension annuelle servie à taux plein par un régime FORFAITAIRE, dans les
    #: euros de ``pension_forfaitaire_annee``, proratisée par la durée. Elle ne
    #: dépend pas du revenu : c'est tout l'objet d'un régime forfaitaire, et
    #: c'est ce qu'un compte notionnel supprime le plus radicalement.
    pension_forfaitaire_annuelle: float | None
    pension_forfaitaire_annee: int | None
    #: Nombre de points garantis chaque année à qui cotise au régime, quelle
    #: que soit son assiette. C'est la garantie minimale de points de l'Agirc :
    #: 120 points par an de 1989 à 2018, y compris pour un cadre dont la
    #: tranche B est nulle. Droit GRATUIT, sans contrepartie de cotisation.
    points_minimum_annuels: float | None
    #: Points attribués par TRIMESTRE VALIDÉ, sans égard au montant cotisé.
    #: C'est la règle du régime de base des professions libérales pour tout ce
    #: qui précède la réforme de 2004 : « les trimestres validés avant le
    #: 1er janvier 2004 sont convertis en points à raison de cent points par
    #: trimestre » (D. 643-1). Le droit d'avant 2004 n'était pas contributif —
    #: l'allocation vieillesse valait un quinzième de l'AVTS par année cotisée,
    #: la même pour tous —, et c'est pourquoi sa conversion ignore l'assiette.
    #: Le nombre de trimestres, lui, reste celui que le revenu a validés.
    points_par_trimestre_valide: float | None
    #: POINTS D'AJUSTEMENT, qui s'ajoutent aux points par trimestre : leur
    #: nombre vaut ``points_ajustement_par_forfait`` fois la cotisation
    #: proportionnelle divisée par la cotisation forfaitaire, dans la limite
    #: de ``points_ajustement_maximum`` par an. C'est l'ASV des médecins depuis
    #: 2012 : 27 points pour le forfait, et « dans la limite de neuf points par
    #: an », l'ajustement multiplié par « les deux tiers » des 27 points et
    #: divisé par le forfait (décret n° 2011-1644, art. 3).
    points_ajustement_par_forfait: float | None
    #: SEUIL DU CAPITAL : en deçà de ce nombre de points, le régime verse un
    #: capital une fois au lieu d'une rente. C'est le RAFP, « servie sous forme
    #: de capital lorsque le nombre de points acquis est inférieur à 5 125 »
    #: (décret n° 2004-569, art. 9).
    capital_seuil_points: float | None
    points_ajustement_maximum: float | None
    #: BARÈME DE POINTS NOMMÉ, dont la formule vit dans le moteur parce qu'elle
    #: ne se laisse pas écrire en colonnes. Une seule valeur pour l'instant :
    #: ``msa_proportionnelle``, la retraite proportionnelle des non-salariés
    #: agricoles (R. 732-70 et R. 732-71 du code rural). Le nombre de points
    #: y dépend du revenu par quatre paliers — 15 points jusqu'à 400 SMIC
    #: horaires, une pente jusqu'à 800, un plateau à 30 jusqu'à deux fois le
    #: minimum contributif, puis une pente jusqu'au maximum M de l'année —, et
    #: la pension multiplie les points par 37,5 / la durée requise en années.
    bareme_points: str | None
    #: BARÈME D'UN AUTRE RÉGIME. Le prix d'achat et la valeur de service du
    #: point sont ceux du régime nommé ici, et non ceux du code de la fiche.
    #: Une seule situation l'exige : une TRANCHE que tous les affiliés d'un
    #: régime ne cotisent pas. La tranche 2 de l'Arrco n'est due que par les
    #: non-cadres — les cadres cotisent l'Agirc au-dessus du plafond —, et elle
    #: forme donc une fiche à part, que l'affiliation donne aux uns et pas aux
    #: autres ; ses points restent des points Arrco.
    points_de: str | None
    #: VALEUR DE SERVICE DU POINT écrite dans la fiche, en euros de
    #: ``valeur_point_annee``, pour les régimes dont la caisse est seule à la
    #: publier et dont `valeurs_point.csv` ne porte donc rien de certifiable.
    #: Revalorisée sur les prix, comme la loi le prescrit (L. 161-23-1).
    valeur_point_euros: float | None
    valeur_point_annee: int | None
    #: BARÈME DU TRIMESTRE : le nom d'une table ``legislation/bareme_trimestre_
    #: <nom>.csv`` qui donne, par date d'effet, la valeur du trimestre et le
    #: coefficient de majoration de la durée. La pension minière est « le
    #: produit de la durée de services par la valeur du trimestre de services
    #: de l'année de leur prise d'effet » (article 131 du décret n° 46-2769),
    #: durée affectée d'un coefficient de majoration (article 131-1) ; la table
    #: prime alors sur ``valeur_point_euros``.
    bareme_trimestre: str | None
    #: PLAFOND DE LA DURÉE LIQUIDÉE, levé pour les trimestres accomplis avant un
    #: âge : « le nombre maximum de trimestres susceptibles d'être pris en
    #: compte pour le calcul de la pension est de cent-vingt ; toutefois, pour
    #: les affiliés qui ont réalisé cette durée avant l'âge de cinquante-cinq
    #: ans, les trimestres accomplis postérieurement sont pris en compte
    #: jusqu'à ce que cet âge soit atteint » (article 136 du même décret).
    trimestres_maximum: int | None
    trimestres_maximum_leve_avant_age: float | None
    #: Repère d'assiette, exprimé en heures de SMIC. ``None`` : le repère est
    #: la borne haute de l'assiette, en plafonds de la Sécurité sociale.
    assiette_repere_smic: float | None
    #: L'assiette est-elle relevée au repère quand elle lui est inférieure ?
    #: C'est l'assiette minimale de la complémentaire agricole.
    assiette_plancher: bool
    #: L'assiette EST le repère, quel que soit le revenu — et non un
    #: plancher. C'est la base forfaitaire du régime des cultes : les
    #: articles R. 382-89 et R. 382-90 l'égalent au SMIC mensuel, que
    #: l'assuré perçoive davantage, moins, ou rien du tout. Un ministre
    #: du culte n'a pas de salaire dont on prélèverait une fraction ; la
    #: congrégation et lui cotisent sur un forfait.
    assiette_forfaitaire: bool
    #: ASSIETTE MINIMALE, en plafonds annuels de la Sécurité sociale : la
    #: cotisation est due sur au moins cette assiette, quel que soit le
    #: revenu. C'est la forme de la CARPIMKO depuis 2026 — « l'assiette de
    #: cette cotisation est comprise entre un minimum et un maximum »,
    #: 50 % et 300 % du plafond (décret n° 2025-1076, art. 7 et 14). Un
    #: seuil qui relève l'assiette, et non un abattement qui la retranche.
    assiette_minimale_pass: float | None
    #: PLAFOND DES PRIMES, en fraction du TRAITEMENT INDICIAIRE — la part du
    #: revenu que les primes ne sont pas. Le RAFP cotise sur les primes « dans
    #: la limite de 20 % du traitement indiciaire brut total [...] perçu au
    #: cours de l'année considérée » (décret n° 2004-569, art. 2, dans toutes
    #: ses versions depuis 2004) : des primes qui font 25 % de la rémunération
    #: valent un tiers du traitement, et n'en cotisent que 15 %. Voir
    #: :meth:`part_du_revenu`.
    plafond_primes_traitement: float | None
    #: COTISATION PAR CLASSES : le régime ne prélève ni un taux ni un forfait
    #: mais un MONTANT par palier de revenu, lu dans `classes_cotisation.csv`.
    #: C'est la forme de la Cipav d'avant 2023.
    cotisation_par_classes: bool
    #: ASSIETTE PAR GRILLE : le régime cotise et liquide sur un SALAIRE
    #: FORFAITAIRE par catégorie, lu dans `salaires_forfaitaires.csv` sous ce
    #: code, et non sur la rémunération réelle. C'est le régime des marins :
    #: vingt catégories de fonction à bord, dont le montant est fixé par
    #: arrêté chaque année. Une carrière saisie porte un revenu, pas une
    #: fonction : le moteur range l'assuré, chaque année, dans la catégorie
    #: dont le forfait est le plus proche de son revenu annualisé.
    assiette_grille: str | None
    #: L'ASSIETTE N'EST PAS LE REVENU, mais une grandeur qui lui est
    #: proportionnelle et que la carrière saisie ne porte pas. Deux sections
    #: libérales sont dans ce cas, et c'est ce qui les tenait hors du
    #: catalogue : la CAVAMAC prélève sur les COMMISSIONS BRUTES que les
    #: compagnies versent à l'agent général, la CPRN sur les PRODUITS DE
    #: L'OFFICE du notaire. L'une et l'autre valent plusieurs fois le revenu
    #: professionnel qui reste à l'assuré une fois ses charges payées.
    #:
    #: Le facteur reconstitue cette grandeur : assiette = revenu × facteur,
    #: avant application des bornes. C'est une MOYENNE DE SECTION, prise dans
    #: les statistiques de la caisse, et elle ne décrit aucun assuré en
    #: particulier — deux agents généraux à même revenu n'ont pas les mêmes
    #: commissions. Le taux, lui, reste celui du texte : la fiche ne maquille
    #: pas le facteur en taux, elle le nomme.
    assiette_facteur_revenu: float | None
    #: COTISATION FORFAITAIRE, en euros de `cotisation_forfaitaire_annee`,
    #: qui s'AJOUTE à la cotisation proportionnelle. C'est la forme du
    #: complémentaire des chirurgiens-dentistes : 3 210,60 € en 2026,
    #: attribuant six points, PLUS 11,35 % du revenu. Ni un taux ni un
    #: forfait pur — les deux à la fois, et le modèle ne savait exprimer
    #: que le premier. Indexée sur les prix, comme la pension
    #: forfaitaire, faute d'une série publiée pour les années anciennes.
    cotisation_forfaitaire_euros: float | None
    cotisation_forfaitaire_annee: int | None
    avantages_non_contributifs: tuple[str, ...]
    #: Taux prélevé sur la TOTALITÉ de la rémunération, en plus du taux
    #: ci-dessus, et qui n'ouvre AUCUN droit — la cotisation « déplafonnée » du
    #: régime général, créée en 1991 pour l'employeur et 2004 pour le salarié.
    #:
    #: Le scénario 1 l'ignore, et c'est le droit : elle finance la solidarité
    #: sans rien acquérir. Les comptes notionnels la portent au compte, parce
    #: que leur principe est d'y inscrire ce qui a été VERSÉ. Elle est donc lue
    #: par le seul constructeur de compte, jamais par le calcul de la pension
    #: actuelle : la séparer d'un champ plutôt que d'une seconde période garantit
    #: qu'elle ne peut pas déplacer l'étalon par inadvertance.
    taux_cotisation_deplafonnee: float = 0.0
    #: Fraction de ce taux supportée par l'assuré. Elle n'a rien à voir avec
    #: celle du taux plafonné : en 2025, le salarié porte 0,40 point sur 2,42,
    #: soit 16,6 %, contre 44,7 % sur la part plafonnée.
    part_salariale_deplafonnee: float = 0.0
    #: POINTS GRATUITS attribués à la liquidation pour les années d'avant la
    #: création du régime : voir :class:`PointsGratuits`. ``None`` partout
    #: ailleurs qu'à la RCO des non-salariés agricoles.
    points_gratuits: PointsGratuits | None = None
    notes: str = ""

    @property
    def taux_cotisation_salarie(self) -> float:
        """Part du taux que l'assuré supporte lui-même."""
        return self.taux_cotisation_retraite * self.part_salariale

    def repere_assiette(self, pass_annuel: float, smic_horaire: float) -> float:
        """Assiette qui ouvre droit à ``points_maximum`` points."""
        if self.assiette_repere_smic is not None:
            return self.assiette_repere_smic * smic_horaire
        borne_basse, borne_haute = self.bornes_assiette_en_pass()
        if borne_haute is None:
            return 0.0
        return (borne_haute - borne_basse) * pass_annuel

    def assiette_minimale(self, pass_annuel: float) -> float:
        """Assiette en deçà de laquelle la cotisation n'est pas appelée."""
        if self.assiette_minimale_pass is None:
            return 0.0
        return self.assiette_minimale_pass * pass_annuel

    def part_du_revenu(self, revenu: float, part_primes: float) -> float:
        """Part de la rémunération que ce régime prend en compte.

        Un fonctionnaire cotise à la pension civile sur son seul traitement
        indiciaire, au RAFP sur ses seules primes, et les primes n'y entrent
        que jusqu'à ``plafond_primes_traitement`` du traitement. Les autres
        régimes prennent la rémunération entière. Le scénario 1 et le compte
        notionnel découpent tous deux par ici, pour ne pas diverger.
        """
        if self.assiette == "primes_uniquement":
            primes = revenu * part_primes
            if self.plafond_primes_traitement is None:
                return primes
            return min(primes, self.plafond_primes_traitement
                       * revenu * (1.0 - part_primes))
        if self.assiette == "hors_primes":
            return revenu * (1.0 - part_primes)
        return revenu

    def couvre(self, annee: int) -> bool:
        return self.debut <= annee and (self.fin is None or annee <= self.fin)

    def bornes_assiette_en_pass(self) -> tuple[float, float | None]:
        return BORNES_ASSIETTE.get(self.assiette, (0.0, None))

    def bornes_assiette_en_euros(
        self, pass_annuel: float
    ) -> tuple[float, float | None]:
        """Bornes de l'assiette en euros de l'année, quelle que soit leur forme.

        Les bornes en euros priment quand la fiche en porte : un régime qui fixe
        ses tranches en euros et ne les indexe pas ne peut pas être décrit en
        multiples d'un plafond qui, lui, suit les salaires.
        """
        if (self.borne_basse_euros is not None
                or self.borne_haute_euros is not None):
            return self.borne_basse_euros or 0.0, self.borne_haute_euros
        borne_basse, borne_haute = self.bornes_assiette_en_pass()
        return (borne_basse * pass_annuel,
                None if borne_haute is None else borne_haute * pass_annuel)


@dataclass
class Regime:
    code: str
    nom: str
    famille: str
    source_id: str
    fiabilite: Fiabilite
    creation: int
    fermeture: int | None
    extinction: int | None
    succede_a: tuple[str, ...]
    integre_dans: str | None
    population: str
    hors_repartition: bool
    periodes: tuple[PeriodeRegime, ...] = field(default_factory=tuple)

    def periode(self, annee: int) -> PeriodeRegime | None:
        """Paramètres applicables une année donnée.

        Quand plusieurs périodes couvrent la même année — cas des régimes à
        tranches, où deux fiches coexistent pour la tranche 1 et la tranche 2 —
        la première est retournée ; utiliser :meth:`periodes_actives` pour les
        obtenir toutes.
        """
        for p in self.periodes:
            if p.couvre(annee):
                return p
        return None

    def periodes_actives(self, annee: int) -> tuple[PeriodeRegime, ...]:
        return tuple(p for p in self.periodes if p.couvre(annee))

    def ouvert(self, annee: int) -> bool:
        """Le régime accepte-t-il de nouveaux affiliés cette année-là ?"""
        if annee < self.creation:
            return False
        if self.fermeture is not None and annee >= self.fermeture:
            return False
        return True

    def vivant(self, annee: int) -> bool:
        """Le régime sert-il encore des droits cette année-là ?"""
        if annee < self.creation:
            return False
        return self.extinction is None or annee < self.extinction


@dataclass(frozen=True)
class ContributionEmployeur:
    """Ce que l'employeur public a versé, une année, pour un régime."""

    taux: float
    #: ``appelee`` — taux fixé par décret ou par arrêté, effectivement prélevé.
    #: ``implicite`` — taux reconstitué a posteriori, l'État n'appelant aucune
    #: cotisation avant 2006.
    nature: str
    fiabilite: Fiabilite
    #: Vrai si la valeur prolonge la dernière année connue au-delà de la série.
    projetee: bool = False
    #: Vrai si c'est le taux que l'État verse pour ses MILITAIRES, et non celui
    #: de ses civils : le 1° de l'article L. 61 du code des pensions en fixe deux.
    militaire: bool = False


class ContributionsEmployeurPubliques:
    """Contribution employeur des régimes publics, année par année.

    Les fiches de régime ne portent, pour la fonction publique et les régimes
    spéciaux, que la retenue de l'agent. Cette table porte l'autre moitié, pour
    les trois régimes dont elle est publiée : l'État (reconstituée de 1995 à
    2005, appelée depuis 2006), la CNRACL (appelée depuis 1948) et la SNCF
    (T1 + T2, de 2007 à 2018).

    Deux bornes, traitées différemment, et c'est délibéré :

    * **avant** la première année d'un régime, la table ne rend rien. Il n'y a
      rien à extrapoler : l'État ne versait aucune cotisation en 1960, et lui en
      prêter une inventerait la donnée que tout ce fichier existe pour éviter.
      L'appelant estime alors la part patronale par l'effort d'un salarié du
      privé de la même année, et le résultat le dit.
    * **après** la dernière année connue, le dernier taux est prolongé, comme
      toute projection du modèle et avec la même conséquence : la fiabilité
      retombe à ``estimee``. Sans cela, une carrière qui se poursuit jusqu'en
      2060 basculerait au milieu sur une autre convention de calcul.

    L'État a DEUX taux, un pour ses civils et un pour ses militaires — 82,28 %
    et 126,07 % en 2026. Le second est dans un fichier à part,
    ``contribution_employeur_militaires.csv``, parce que ce n'est pas un régime
    de plus ; ``taux(..., militaire=True)`` le sert à partir de 2006, première
    année où l'État a versé une contribution. Avant, il n'y a qu'un taux
    implicite pour tout l'État, et le militaire le reçoit comme le civil.
    """

    #: Le régime dont les militaires ont leur propre taux.
    REGIME_DES_MILITAIRES = "fonction_publique_etat"

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, dict[int, ContributionEmployeur]] = {}
        self._militaires: dict[int, ContributionEmployeur] = {}
        dossier = racine / "reference" / "legislation"
        chemin = dossier / "contribution_employeur_public.csv"
        if chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    self._table.setdefault(ligne["regime"], {})[int(ligne["annee"])] = (
                        ContributionEmployeur(
                            taux=float(ligne["taux"]),
                            nature=ligne["nature"],
                            fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
                        )
                    )
        chemin = dossier / "contribution_employeur_militaires.csv"
        if chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                lignes = (l for l in flux if not l.lstrip().startswith("#"))
                for ligne in csv.DictReader(lignes):
                    self._militaires[int(ligne["annee"])] = ContributionEmployeur(
                        taux=float(ligne["taux"]),
                        nature=ligne.get("nature") or "appelee",
                        fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
                        militaire=True,
                    )

    def __bool__(self) -> bool:
        return bool(self._table)

    @property
    def regimes(self) -> tuple[str, ...]:
        return tuple(sorted(self._table))

    def couverture(self, regime: str) -> tuple[int, int] | None:
        """Première et dernière année publiées, ``None`` si le régime est absent."""
        annees = self._table.get(regime)
        return (min(annees), max(annees)) if annees else None

    def couverture_militaires(self) -> tuple[int, int] | None:
        """Première et dernière année du taux propre aux militaires."""
        annees = self._militaires
        return (min(annees), max(annees)) if annees else None

    def taux(self, regime: str, annee: int,
             militaire: bool = False) -> ContributionEmployeur | None:
        """Contribution employeur du régime cette année-là, ``None`` si inconnue.

        ``militaire`` : l'agent est un militaire. Pour l'État, et à partir de la
        première année de son taux propre, c'est ce taux qui est rendu ; il
        porte alors ``militaire=True``.
        """
        if (militaire and regime == self.REGIME_DES_MILITAIRES and self._militaires
                and annee >= min(self._militaires)):
            return self._en_vigueur(self._militaires, annee)
        return self._en_vigueur(self._table.get(regime), annee)

    @staticmethod
    def _en_vigueur(annees: dict[int, ContributionEmployeur] | None,
                    annee: int) -> ContributionEmployeur | None:
        if not annees:
            return None
        if annee in annees:
            return annees[annee]
        premiere, derniere = min(annees), max(annees)
        if annee < premiere:
            return None
        if annee > derniere:
            base = annees[derniere]
            return ContributionEmployeur(base.taux, base.nature, Fiabilite.ESTIMEE,
                                         projetee=True, militaire=base.militaire)
        # Trou interne : le taux reste en vigueur jusqu'à sa modification.
        precedente = max(a for a in annees if a < annee)
        return annees[precedente]


@dataclass(frozen=True)
class PosteContributionEtat:
    """Une ligne du tableau de la Cour : un poste, ce qu'il coûte, ce qu'il pèse."""

    population: str
    poste: str
    #: Milliards d'euros de l'année mesurée ; négatif pour une déduction.
    montant: float
    #: En points de l'assiette de la retenue, cotisation de l'agent déduite.
    taux: float


class PartRetraiteSeuleEtat:
    """Ce que paie la contribution de l'État employeur, poste par poste.

    Le taux que l'État verse au compte d'affectation spéciale « Pensions » est
    un taux d'ÉQUILIBRE : il paie toutes les pensions de l'année. La Cour des
    comptes l'a décomposé pour 2025 et n'en rattache à la retraite de l'agent
    lui-même que 44,1 % du traitement pour un civil et 51,2 % pour un
    militaire ; le reste paie l'invalidité avant 62 ans, les majorations pour
    enfants, les départs anticipés et un rapport démographique plus
    défavorable que celui de l'ensemble des régimes.

    Une seule année est mesurée : ``annee``. Deux postes servent, chacun en
    proportion du taux versé cette année-là : ``retraite_stricto_sensu``, ce
    que le compte reçoit sous ``ContributionEtat.RETRAITE_SEULE``, et
    ``avantages_professionnels``, les départs anticipés, que l'État garde en
    entier sur la fiche de paie de la proposition (``remuneration.py``).
    """

    def __init__(self, racine: Path) -> None:
        self.annee: int | None = None
        self.postes: tuple[PosteContributionEtat, ...] = ()
        chemin = (racine / "reference" / "legislation"
                  / "contribution_etat_retraite_seule.csv")
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = list(csv.DictReader(
                l for l in flux if not l.lstrip().startswith("#")))
        annees = {int(ligne["annee"]) for ligne in lignes}
        if len(annees) != 1:
            raise ValueError(f"{chemin.name} : une seule année attendue, {sorted(annees)}")
        self.annee = annees.pop()
        self.postes = tuple(
            PosteContributionEtat(ligne["population"], ligne["poste"],
                                  float(ligne["montant"]), float(ligne["taux"]))
            for ligne in lignes
        )

    def __bool__(self) -> bool:
        return bool(self.postes)

    def taux(self, population: str, poste: str = "retraite_stricto_sensu") -> float:
        """Taux d'un poste l'année mesurée : ``civils`` ou ``militaires``.

        Le taux « retraite seule » par défaut. Un poste que la Cour RETIRE est
        négatif, comme elle l'imprime : les départs anticipés d'un militaire
        valent −0,338.
        """
        for ligne in self.postes:
            if ligne.population == population and ligne.poste == poste:
                return ligne.taux
        raise KeyError((population, poste))


@dataclass(frozen=True)
class ClasseCotisation:
    """Un palier : jusqu'à ce revenu, ce montant."""

    #: Borne haute du palier, incluse. ``None`` pour le dernier, qui n'en a pas.
    revenu_maximum: float | None
    #: Montant dû, en euros de l'année de la grille.
    cotisation: float
    fiabilite: Fiabilite


class ClassesCotisation:
    """Cotisations par CLASSES, pour les régimes qui prélèvent un montant.

    Une fiche sait porter un taux et un forfait. Plusieurs complémentaires
    libéraux ne prélèvent ni l'un ni l'autre : ils rangent l'assuré dans une
    classe selon son revenu, et chaque classe a son montant. C'est une fonction
    en escalier, et c'était la seule forme que le catalogue ne savait pas
    exprimer.

    La classe est SUBIE, pas choisie, et c'est ce qui la rend modélisable : la
    fiche pratique 2022 de la Cipav écrit du complémentaire que « son montant
    est DÉTERMINÉ selon ce tableau », quand elle écrit de l'invalidité-décès,
    juste à côté, que l'assuré « a la possibilité de CHOISIR sa classe ». Seule
    la première forme entre ici.

    ANNÉES SANS GRILLE PUBLIÉE : c'est la grille la plus récente qui précède
    l'exercice qui s'applique, bornes et montants indexés sur les prix par
    l'appelant — la convention déjà retenue pour la cotisation forfaitaire. Un
    exercice antérieur à toute grille connue prend la plus ancienne, indexée de
    la même façon.
    """

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, dict[int, list[ClasseCotisation]]] = {}
        chemin = racine / "reference" / "regimes" / "classes_cotisation.csv"
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                borne = ligne["revenu_maximum"].strip()
                self._table.setdefault(ligne["regime"], {}).setdefault(
                    int(ligne["annee"]), []
                ).append(ClasseCotisation(
                    revenu_maximum=float(borne) if borne else None,
                    cotisation=float(ligne["cotisation"]),
                    fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
                ))
        for grilles in self._table.values():
            for classes in grilles.values():
                # Les paliers sans borne ferment la grille : ils passent en fin.
                classes.sort(key=lambda c: (c.revenu_maximum is None,
                                            c.revenu_maximum or 0.0))

    def __bool__(self) -> bool:
        return bool(self._table)

    @property
    def regimes(self) -> tuple[str, ...]:
        return tuple(sorted(self._table))

    def annee_grille(self, regime: str, annee: int) -> int | None:
        """Millésime de la grille qui s'applique à cet exercice."""
        grilles = self._table.get(regime)
        if not grilles:
            return None
        anterieures = [a for a in grilles if a <= annee]
        return max(anterieures) if anterieures else min(grilles)

    def grille(self, regime: str, annee: int
               ) -> tuple[ClasseCotisation, ...] | None:
        millesime = self.annee_grille(regime, annee)
        if millesime is None:
            return None
        return tuple(self._table[regime][millesime])

    def cotisation(self, regime: str, annee: int, revenu: float,
                   coefficient: float = 1.0
                   ) -> tuple[float, Fiabilite] | None:
        """Montant dû pour ce revenu, ``None`` si le régime n'a pas de grille.

        ``coefficient`` ramène la grille de son millésime à l'exercice demandé :
        il multiplie les bornes ET les montants, faute de quoi l'indexation
        ferait glisser tout le monde d'une classe.
        """
        classes = self.grille(regime, annee)
        if not classes:
            return None
        for classe in classes:
            borne = classe.revenu_maximum
            if borne is None or revenu <= borne * coefficient:
                return classe.cotisation * coefficient, classe.fiabilite
        dernier = classes[-1]
        return dernier.cotisation * coefficient, dernier.fiabilite


@dataclass(frozen=True)
class SalaireForfaitaire:
    categorie: int
    montant: float
    fiabilite: Fiabilite


class SalairesForfaitaires:
    """Grilles de salaires forfaitaires par catégorie, régime par régime.

    Le régime des marins ne cotise ni ne liquide sur le salaire réel mais sur
    un forfait par catégorie de fonction à bord, publié chaque année par
    arrêté ; `salaires_forfaitaires.csv` les porte depuis 2008, lus au
    Journal officiel. Une carrière saisie porte un revenu, pas une fonction :
    :meth:`forfait` range l'assuré dans la catégorie dont le montant est le
    plus proche de son revenu annualisé — convention nommée, la seule qui
    rende la grille applicable à une carrière décrite par un revenu.

    Hors des années publiées, la grille la plus proche est ramenée par le
    salaire moyen de l'économie, et le résultat le dit : fiabilité
    ``estimee``.
    """

    def __init__(self, racine: Path) -> None:
        self._table: dict[str, dict[int, list[SalaireForfaitaire]]] = {}
        chemin = racine / "reference" / "regimes" / "salaires_forfaitaires.csv"
        if not chemin.exists():
            return
        with chemin.open(encoding="utf-8") as flux:
            lignes = (l for l in flux if not l.lstrip().startswith("#"))
            for ligne in csv.DictReader(lignes):
                self._table.setdefault(ligne["regime"], {}).setdefault(
                    int(ligne["annee"]), []
                ).append(SalaireForfaitaire(
                    categorie=int(ligne["categorie"]),
                    montant=float(ligne["montant_annuel"]),
                    fiabilite=Fiabilite.depuis_texte(ligne["fiabilite"]),
                ))
        for grilles in self._table.values():
            for grille in grilles.values():
                grille.sort(key=lambda c: c.montant)

    def __bool__(self) -> bool:
        return bool(self._table)

    @property
    def regimes(self) -> tuple[str, ...]:
        return tuple(sorted(self._table))

    def annees(self, regime: str) -> tuple[int, ...]:
        return tuple(sorted(self._table.get(regime, {})))

    def forfait(self, regime: str, annee: int, revenu_annuel: float,
                indice_salaire) -> tuple[float, int, Fiabilite] | None:
        """Le forfait de la catégorie la plus proche du revenu, sa catégorie,
        et ce qu'il vaut.

        ``indice_salaire`` est une fonction année -> salaire moyen, qui sert
        à ramener la grille la plus proche aux années qu'aucun arrêté ne
        couvre. À égalité de distance, la catégorie la plus basse.
        """
        grilles = self._table.get(regime)
        if not grilles:
            return None
        if annee in grilles:
            grille, coefficient, hors_grille = grilles[annee], 1.0, False
        else:
            proche = min(grilles, key=lambda a: (abs(a - annee), a))
            grille = grilles[proche]
            coefficient = indice_salaire(annee) / indice_salaire(proche)
            hors_grille = True
        meilleur = min(
            grille,
            key=lambda c: (abs(c.montant * coefficient - revenu_annuel), c.categorie),
        )
        fiabilite = Fiabilite.ESTIMEE if hors_grille else meilleur.fiabilite
        return meilleur.montant * coefficient, meilleur.categorie, fiabilite


#: Champ de la période que chaque mesure de `taux_cotisation_annuels.csv`
#: remplace.
_MESURES_TAUX_ANNUELS = {
    "taux_plafonne": "taux_cotisation_retraite",
    "part_salariale": "part_salariale",
    "taux_deplafonne": "taux_cotisation_deplafonnee",
    "part_salariale_deplafonnee": "part_salariale_deplafonnee",
}


def charger_taux_annuels(racine: Path) -> dict[str, dict[int, dict[str, float]]]:
    """``taux_cotisation_annuels.csv`` : régime -> année -> champ -> valeur.

    Absent, le fichier ne change rien : les fiches gardent leurs moyennes.
    """
    chemin = racine / "reference" / "regimes" / "taux_cotisation_annuels.csv"
    if not chemin.exists():
        return {}
    table: dict[str, dict[int, dict[str, float]]] = {}
    with chemin.open(encoding="utf-8") as flux:
        lignes = list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))
    for ligne in lignes:
        champ = _MESURES_TAUX_ANNUELS.get(ligne["mesure"])
        if champ is None:
            raise ValueError(
                f"{chemin.name} : mesure inconnue {ligne['mesure']!r} "
                f"({ligne['regime']}, {ligne['annee']})"
            )
        table.setdefault(ligne["regime"], {}).setdefault(int(ligne["annee"]), {})[
            champ
        ] = float(ligne["valeur"])
    return table


def dater_les_taux(periodes: tuple[PeriodeRegime, ...],
                   annuels: dict[int, dict[str, float]],
                   ) -> tuple[PeriodeRegime, ...]:
    """Découpe les périodes ``plafonnee`` d'un régime selon ses taux annuels.

    Une fiche porte un taux par PÉRIODE LÉGISLATIVE — huit périodes de 1945 à
    aujourd'hui pour le régime général, et un taux moyen dans chacune, écrit
    comme tel dans ses notes : « une moyenne de période, à affiner ». Le
    droit a changé ce taux presque chaque année, et c'est lui qui alimente le
    compte notionnel : la moyenne 1972-1982 prêtait à 1972 les 12,9 % de 1979,
    quand il cotisait 8,75 %.

    Chaque période dont l'assiette est ``plafonnee`` — celle que la table
    décrit — est donc réécrite année par année : le taux, sa part salariale,
    la cotisation déplafonnée et sa part sont ceux de la table quand elle a
    l'année, ceux de la fiche sinon ; les années consécutives identiques sont
    refondues en une période, et la dernière garde la borne de la fiche — une
    période ouverte reste ouverte, au dernier taux connu. Tout le reste de la
    période — âges, durées, barème de liquidation — est recopié tel quel : la
    liquidation ne change pas, seule la cotisation se date.
    """
    if not annuels:
        return periodes
    derniere_annee = max(annuels)
    resultat: list[PeriodeRegime] = []
    for periode in periodes:
        if periode.assiette != "plafonnee" or periode.perimetre_taux == "agent_seul":
            resultat.append(periode)
            continue
        fin = derniere_annee if periode.fin is None else min(periode.fin, derniere_annee)
        annees = [a for a in range(periode.debut, fin + 1) if a in annuels]
        if not annees:
            resultat.append(periode)
            continue
        # Les valeurs de chaque année de la période, table puis fiche.
        valeurs = []
        for annee in range(periode.debut, fin + 1):
            champs = {
                champ: getattr(periode, champ) for champ in _MESURES_TAUX_ANNUELS.values()
            }
            champs.update(annuels.get(annee, {}))
            valeurs.append((annee, champs))
        # Refonte des années consécutives identiques.
        tranches: list[tuple[int, int, dict[str, float]]] = []
        for annee, champs in valeurs:
            if tranches and tranches[-1][2] == champs:
                tranches[-1] = (tranches[-1][0], annee, champs)
            else:
                tranches.append((annee, annee, champs))
        for rang, (debut, fin_tranche, champs) in enumerate(tranches):
            derniere = rang == len(tranches) - 1
            resultat.append(replace(
                periode, debut=debut,
                fin=periode.fin if derniere else fin_tranche,
                **champs,
            ))
    return tuple(resultat)


class CatalogueRegimes:
    """Ensemble des régimes chargés depuis ``data/reference/regimes/*.yaml``.

    Les taux de cotisation des régimes que `taux_cotisation_annuels.csv`
    couvre sont datés année par année au chargement : voir
    :func:`dater_les_taux`. Le portage JavaScript reçoit les périodes ainsi
    découpées dans le paquet de données, et n'a rien à refaire.
    """

    def __init__(self, racine: Path) -> None:
        self.racine = racine
        self._regimes: dict[str, Regime] = {}
        self.taux_annuels = charger_taux_annuels(racine)
        dossier = racine / "reference" / "regimes"
        for chemin in sorted(dossier.glob("*.yaml")):
            if chemin.name.startswith("_"):
                continue
            contenu = charger_yaml(chemin)
            for fiche in contenu.get("regimes", []):
                regime = self._construire(fiche, chemin)
                if regime.code in self._regimes:
                    raise ValueError(f"code de régime dupliqué : {regime.code}")
                if regime.code in self.taux_annuels:
                    regime = replace(regime, periodes=dater_les_taux(
                        regime.periodes, self.taux_annuels[regime.code]))
                self._regimes[regime.code] = regime
        if not self._regimes:
            raise ValueError(f"aucun régime chargé depuis {dossier}")
        inconnus = set(self.taux_annuels) - set(self._regimes)
        if inconnus:
            raise ValueError(
                "taux_cotisation_annuels.csv nomme des régimes sans fiche : "
                + ", ".join(sorted(inconnus))
            )

    @staticmethod
    def _construire(fiche: dict, chemin: Path) -> Regime:
        manquants = {"code", "nom", "famille", "fiabilite"} - set(fiche)
        if manquants:
            raise ValueError(f"{chemin.name} : champs manquants {sorted(manquants)}")
        if fiche["famille"] not in FAMILLES:
            raise ValueError(
                f"{chemin.name} / {fiche['code']} : famille inconnue {fiche['famille']!r}"
            )
        periodes = tuple(
            PeriodeRegime(
                regime=fiche["code"],
                debut=int(p["debut"]),
                fin=None if p.get("fin") is None else int(p["fin"]),
                type_calcul=p["type_calcul"],
                age_ouverture=float(p["age_ouverture"]),
                age_taux_plein=float(p["age_taux_plein"]),
                duree_requise_trimestres=(
                    None if p.get("duree_requise_trimestres") is None
                    else int(p["duree_requise_trimestres"])
                ),
                duree_requise_par_generation=bool(
                    p.get("duree_requise_par_generation", False)
                ),
                duree_requise_table=(
                    (p["duree_requise_table"],)
                    if isinstance(p.get("duree_requise_table"), str)
                    else tuple(p.get("duree_requise_table") or ())
                ),
                duree_requise_calendrier=p.get("duree_requise_calendrier"),
                age_surcote_regimes_speciaux=bool(
                    p.get("age_surcote_regimes_speciaux", False)
                ),
                age_ouverture_par_generation=bool(
                    p.get("age_ouverture_par_generation", False)
                ),
                age_taux_plein_par_generation=bool(
                    p.get("age_taux_plein_par_generation", False)
                ),
                age_table=p.get("age_table"),
                decote_par_generation=bool(p.get("decote_par_generation", False)),
                duree_proratisation_par_generation=bool(
                    p.get("duree_proratisation_par_generation", False)
                ),
                salaire_reference_par_generation=bool(
                    p.get("salaire_reference_par_generation", False)
                ),
                duree_maximum_avant_age=(
                    None if p.get("duree_maximum_avant_age") is None
                    else float(p["duree_maximum_avant_age"])
                ),
                duree_maximum_avant_age_trimestres=(
                    None if p.get("duree_maximum_avant_age_trimestres") is None
                    else int(p["duree_maximum_avant_age_trimestres"])
                ),
                duree_maximum_levee_age=(
                    None if p.get("duree_maximum_levee_age") is None
                    else float(p["duree_maximum_levee_age"])
                ),
                duree_maximum_levee_trimestres=(
                    None if p.get("duree_maximum_levee_trimestres") is None
                    else int(p["duree_maximum_levee_trimestres"])
                ),
                age_ouverture_services=(
                    None if p.get("age_ouverture_services") is None
                    else float(p["age_ouverture_services"])
                ),
                services_ouverture_annees=(
                    None if p.get("services_ouverture_annees") is None
                    else float(p["services_ouverture_annees"])
                ),
                pension_speciale_services_annees=(
                    None if p.get("pension_speciale_services_annees") is None
                    else float(p["pension_speciale_services_annees"])
                ),
                pension_speciale_age_sans_autre_pension=(
                    None if p.get("pension_speciale_age_sans_autre_pension") is None
                    else float(p["pension_speciale_age_sans_autre_pension"])
                ),
                taux_plein=None if p.get("taux_plein") is None else float(p["taux_plein"]),
                taux_maximum_bonifie=(
                    None if p.get("taux_maximum_bonifie") is None
                    else float(p["taux_maximum_bonifie"])
                ),
                salaire_reference=p.get("salaire_reference", "sans_objet"),
                assiette=p.get("assiette", "deplafonnee"),
                taux_cotisation_retraite=float(p["taux_cotisation_retraite"]),
                perimetre_taux=p.get("perimetre_taux", "total"),
                part_salariale=float(p.get("part_salariale", 1.0)),
                taux_cotisation_deplafonnee=float(
                    p.get("taux_cotisation_deplafonnee", 0.0)
                ),
                part_salariale_deplafonnee=float(
                    p.get("part_salariale_deplafonnee", 0.0)
                ),
                decote_par_trimestre=(
                    None if p.get("decote_par_trimestre") is None
                    else float(p["decote_par_trimestre"])
                ),
                bareme_decote=p.get("bareme_decote", "regime_aligne"),
                decote_annulee_par_la_duree=bool(
                    p.get("decote_annulee_par_la_duree", True)
                ),
                decote_par_la_duree_seule=bool(
                    p.get("decote_par_la_duree_seule", False)
                ),
                decote_trimestres_maximum=(
                    None if "decote_trimestres_maximum" in p
                    and p["decote_trimestres_maximum"] is None
                    else int(p.get("decote_trimestres_maximum", 20))
                ),
                decote_palier_age=(
                    None if p.get("decote_palier_age") is None
                    else float(p["decote_palier_age"])
                ),
                decote_par_trimestre_apres_palier=(
                    None if p.get("decote_par_trimestre_apres_palier") is None
                    else float(p["decote_par_trimestre_apres_palier"])
                ),
                taux_plein_anticipe_par_enfant_annees=(
                    None if p.get("taux_plein_anticipe_par_enfant_annees") is None
                    else float(p["taux_plein_anticipe_par_enfant_annees"])
                ),
                taux_plein_anticipe_maximum_annees=(
                    None if p.get("taux_plein_anticipe_maximum_annees") is None
                    else float(p["taux_plein_anticipe_maximum_annees"])
                ),
                surcote_par_trimestre=(
                    None if p.get("surcote_par_trimestre") is None
                    else float(p["surcote_par_trimestre"])
                ),
                surcote_bareme=p.get("surcote_bareme"),
                abattement_points=p.get("abattement_points", "decote_du_regime_de_base"),
                surcote_points=p.get("surcote_points", "aucune"),
                surcote_age_debut=(
                    None if p.get("surcote_age_debut") is None
                    else float(p["surcote_age_debut"])
                ),
                surcote_age_maximum=(
                    None if p.get("surcote_age_maximum") is None
                    else float(p["surcote_age_maximum"])
                ),
                surcote_trimestres_maximum=(
                    None if p.get("surcote_trimestres_maximum") is None
                    else int(p["surcote_trimestres_maximum"])
                ),
                surcote_pas_trimestres=int(p.get("surcote_pas_trimestres") or 1),
                surcote_palier_age=(
                    None if p.get("surcote_palier_age") is None
                    else float(p["surcote_palier_age"])
                ),
                surcote_par_trimestre_apres_palier=(
                    None if p.get("surcote_par_trimestre_apres_palier") is None
                    else float(p["surcote_par_trimestre_apres_palier"])
                ),
                surcote_affiliation_minimale_trimestres=(
                    None if p.get("surcote_affiliation_minimale_trimestres") is None
                    else int(p["surcote_affiliation_minimale_trimestres"])
                ),
                surcote_trimestres_cotises=bool(p.get("surcote_trimestres_cotises", False)),
                plafond_majoration_enfants=(
                    None if p.get("plafond_majoration_enfants") is None
                    else float(p["plafond_majoration_enfants"])
                ),
                taux_majoration_enfants=(
                    None if p.get("taux_majoration_enfants") is None
                    else tuple(float(t) for t in p["taux_majoration_enfants"])
                ),
                plafond_majoration_annee=(
                    None if p.get("plafond_majoration_annee") is None
                    else int(p["plafond_majoration_annee"])
                ),
                points_maximum=(
                    None if p.get("points_maximum") is None
                    else float(p["points_maximum"])
                ),
                borne_basse_euros=(
                    None if p.get("borne_basse_euros") is None
                    else float(p["borne_basse_euros"])
                ),
                borne_haute_euros=(
                    None if p.get("borne_haute_euros") is None
                    else float(p["borne_haute_euros"])
                ),
                pension_forfaitaire_annuelle=(
                    None if p.get("pension_forfaitaire_annuelle") is None
                    else float(p["pension_forfaitaire_annuelle"])
                ),
                pension_forfaitaire_annee=(
                    None if p.get("pension_forfaitaire_annee") is None
                    else int(p["pension_forfaitaire_annee"])
                ),
                points_minimum_annuels=(
                    None if p.get("points_minimum_annuels") is None
                    else float(p["points_minimum_annuels"])
                ),
                capital_seuil_points=(
                    None if p.get("capital_seuil_points") is None
                    else float(p["capital_seuil_points"])
                ),
                points_ajustement_par_forfait=(
                    None if p.get("points_ajustement_par_forfait") is None
                    else float(p["points_ajustement_par_forfait"])
                ),
                points_ajustement_maximum=(
                    None if p.get("points_ajustement_maximum") is None
                    else float(p["points_ajustement_maximum"])
                ),
                points_par_trimestre_valide=(
                    None if p.get("points_par_trimestre_valide") is None
                    else float(p["points_par_trimestre_valide"])
                ),
                bareme_points=p.get("bareme_points"),
                points_de=p.get("points_de"),
                valeur_point_euros=(
                    None if p.get("valeur_point_euros") is None
                    else float(p["valeur_point_euros"])
                ),
                valeur_point_annee=(
                    None if p.get("valeur_point_annee") is None
                    else int(p["valeur_point_annee"])
                ),
                bareme_trimestre=p.get("bareme_trimestre"),
                trimestres_maximum=(
                    None if p.get("trimestres_maximum") is None
                    else int(p["trimestres_maximum"])
                ),
                trimestres_maximum_leve_avant_age=(
                    None if p.get("trimestres_maximum_leve_avant_age") is None
                    else float(p["trimestres_maximum_leve_avant_age"])
                ),
                assiette_repere_smic=(
                    None if p.get("assiette_repere_smic") is None
                    else float(p["assiette_repere_smic"])
                ),
                assiette_plancher=bool(p.get("assiette_plancher", False)),
                assiette_forfaitaire=bool(p.get("assiette_forfaitaire", False)),
                assiette_minimale_pass=(
                    None if p.get("assiette_minimale_pass") is None
                    else float(p["assiette_minimale_pass"])
                ),
                plafond_primes_traitement=(
                    None if p.get("plafond_primes_traitement") is None
                    else float(p["plafond_primes_traitement"])
                ),
                cotisation_par_classes=bool(
                    p.get("cotisation_par_classes", False)
                ),
                assiette_grille=p.get("assiette_grille"),
                assiette_facteur_revenu=(
                    None if p.get("assiette_facteur_revenu") is None
                    else float(p["assiette_facteur_revenu"])
                ),
                cotisation_forfaitaire_euros=(
                    None if p.get("cotisation_forfaitaire_euros") is None
                    else float(p["cotisation_forfaitaire_euros"])
                ),
                cotisation_forfaitaire_annee=(
                    None if p.get("cotisation_forfaitaire_annee") is None
                    else int(p["cotisation_forfaitaire_annee"])
                ),
                avantages_non_contributifs=tuple(p.get("avantages_non_contributifs") or ()),
                points_gratuits=_points_gratuits(p.get("points_gratuits")),
                notes=(p.get("notes") or "").strip(),
            )
            for p in fiche.get("periodes", [])
        )
        return Regime(
            code=fiche["code"],
            nom=fiche["nom"],
            famille=fiche["famille"],
            source_id=fiche.get("source_id", ""),
            fiabilite=Fiabilite.depuis_texte(fiche["fiabilite"]),
            creation=int(fiche["creation"]),
            fermeture=None if fiche.get("fermeture") is None else int(fiche["fermeture"]),
            extinction=None if fiche.get("extinction") is None else int(fiche["extinction"]),
            succede_a=tuple(fiche.get("succede_a") or ()),
            integre_dans=fiche.get("integre_dans"),
            population=(fiche.get("population") or "").strip(),
            hors_repartition=bool(fiche.get("hors_repartition", False)),
            periodes=periodes,
        )

    # -- accès ---------------------------------------------------------------

    def __getitem__(self, code: str) -> Regime:
        if code not in self._regimes:
            raise KeyError(
                f"régime inconnu : {code!r}. Régimes disponibles : "
                + ", ".join(sorted(self._regimes))
            )
        return self._regimes[code]

    def __contains__(self, code: str) -> bool:
        return code in self._regimes

    def __iter__(self):
        return iter(self._regimes.values())

    def __len__(self) -> int:
        return len(self._regimes)

    @cached_property
    def codes(self) -> tuple[str, ...]:
        return tuple(sorted(self._regimes))

    def en_repartition(self) -> tuple[Regime, ...]:
        return tuple(r for r in self if not r.hors_repartition)

    def ouverts(self, annee: int) -> tuple[Regime, ...]:
        return tuple(r for r in self if r.ouvert(annee))

    def resoudre_succession(self, code: str, annee: int) -> str:
        """Suit la chaîne d'absorption jusqu'au régime réellement compétent.

        Exemple : ``organic`` en 2010 renvoie ``rsi`` ; en 2020, ``regime_general``.
        """
        vu = {code}
        courant = self[code]
        while courant.extinction is not None and annee >= courant.extinction:
            suivant = courant.integre_dans
            if suivant is None or suivant in vu:
                break
            vu.add(suivant)
            courant = self[suivant]
        return courant.code


# ---------------------------------------------------------------------------
# L'inventaire : tous les régimes, calculés ou non
# ---------------------------------------------------------------------------

#: Ce que le dépôt sait faire d'un régime de l'inventaire.
COUVERTURES = ("modelise", "partiel", "a_modeliser", "routage", "hors_champ")


@dataclass(frozen=True)
class RegimeInventaire:
    """Une ligne de ``data/reference/regimes/inventaire.yaml``.

    Le catalogue ne connaît que les régimes qu'il calcule ; l'inventaire les
    nomme tous — vivants, disparus, et ceux qu'on ne calculera pas — avec,
    pour chacun, ce qui manque au dépôt. Un régime ``modelise`` ou ``partiel``
    a une fiche au catalogue sous le même code ; ``a_modeliser`` et
    ``hors_champ`` n'en ont pas, et disent pourquoi. ``routage`` est la ligne
    qui n'est pas un régime mais une AFFILIATION — l'élu local à l'Ircantec,
    le micro-social — : un statut du catalogue la porte, et ``manque`` dit
    ce que ce statut ne lit pas encore.
    """

    code: str
    nom: str
    famille: str
    population: str
    creation: int | None
    fermeture: int | None
    extinction: int | None
    succede_a: tuple[str, ...]
    integre_dans: str | None
    couverture: str
    statuts: tuple[str, ...]
    textes: tuple[dict, ...]
    manque: str
    raison_hors_champ: str

    @property
    def au_catalogue(self) -> bool:
        return self.couverture in ("modelise", "partiel")

    def dictionnaire(self) -> dict:
        return {
            "code": self.code,
            "nom": self.nom,
            "famille": self.famille,
            "population": self.population,
            "creation": self.creation,
            "fermeture": self.fermeture,
            "extinction": self.extinction,
            "succede_a": list(self.succede_a),
            "integre_dans": self.integre_dans,
            "couverture": self.couverture,
            "statuts": list(self.statuts),
            "textes": [dict(t) for t in self.textes],
            "manque": self.manque,
            "raison_hors_champ": self.raison_hors_champ,
        }


def _annee(valeur) -> int | None:
    return None if valeur is None else int(valeur)


def charger_inventaire(racine: Path) -> tuple[RegimeInventaire, ...]:
    """L'inventaire, dans l'ordre du fichier, validé champ par champ."""
    chemin = racine / "reference" / "regimes" / "inventaire.yaml"
    contenu = charger_yaml(chemin)
    lignes: list[RegimeInventaire] = []
    codes: set[str] = set()
    for fiche in contenu.get("inventaire", []):
        manquants = {"code", "nom", "famille", "population", "couverture",
                     "statuts", "textes"} - set(fiche)
        if manquants:
            raise ValueError(
                f"{chemin.name} / {fiche.get('code', '?')} : champs manquants "
                f"{sorted(manquants)}"
            )
        code = str(fiche["code"])
        if code in codes:
            raise ValueError(f"{chemin.name} : code dupliqué {code}")
        codes.add(code)
        if fiche["famille"] not in FAMILLES:
            raise ValueError(f"{chemin.name} / {code} : famille inconnue {fiche['famille']!r}")
        if fiche["couverture"] not in COUVERTURES:
            raise ValueError(
                f"{chemin.name} / {code} : couverture inconnue {fiche['couverture']!r}"
            )
        if fiche["couverture"] == "routage" and not fiche.get("statuts"):
            raise ValueError(
                f"{chemin.name} / {code} : une ligne `routage` doit nommer son statut"
            )
        textes = tuple(
            {"reference": str(t["reference"]), "id": t.get("id")}
            for t in fiche["textes"] or ()
        )
        if not textes:
            raise ValueError(f"{chemin.name} / {code} : aucun texte de référence")
        lignes.append(RegimeInventaire(
            code=code,
            nom=str(fiche["nom"]),
            famille=str(fiche["famille"]),
            population=" ".join(str(fiche["population"]).split()),
            creation=_annee(fiche.get("creation")),
            fermeture=_annee(fiche.get("fermeture")),
            extinction=_annee(fiche.get("extinction")),
            succede_a=tuple(fiche.get("succede_a") or ()),
            integre_dans=fiche.get("integre_dans"),
            couverture=str(fiche["couverture"]),
            statuts=tuple(fiche["statuts"] or ()),
            textes=textes,
            manque=" ".join(str(fiche.get("manque") or "").split()),
            raison_hors_champ=" ".join(str(fiche.get("raison_hors_champ") or "").split()),
        ))
    if not lignes:
        raise ValueError(f"aucun régime dans {chemin}")
    return tuple(lignes)


# ---------------------------------------------------------------------------
# Le calendrier des réformes et les articles pivots
# ---------------------------------------------------------------------------

#: Drapeaux d'une période qui lisent un paramètre à la génération plutôt
#: qu'à l'année : ce sont eux qui peuvent « absorber » une réforme sans
#: qu'une période nouvelle commence.
DRAPEAUX_PAR_GENERATION = (
    "duree_requise_par_generation",
    "age_ouverture_par_generation",
    "age_taux_plein_par_generation",
    # La table d'âges d'une section se lit à la génération, comme les deux
    # drapeaux qui précèdent.
    "age_table",
    "decote_par_generation",
    "duree_proratisation_par_generation",
    "salaire_reference_par_generation",
    # Pas un drapeau par génération, mais un barème DATÉ : une période qui le
    # porte lit le taux de chaque trimestre de surcote à sa date, et absorbe
    # donc les changements de taux sans coupure.
    "surcote_bareme",
)


@dataclass(frozen=True)
class Reforme:
    """Une ligne de ``data/reference/legislation/reformes.yaml``."""

    code: str
    date: str
    annee: int
    texte: dict
    parametres: tuple[str, ...]
    regimes: tuple[str, ...]
    absorbee_par: tuple[str, ...]
    non_appliquee: dict[str, str]


def charger_reformes(racine: Path) -> tuple[Reforme, ...]:
    chemin = racine / "reference" / "legislation" / "reformes.yaml"
    contenu = charger_yaml(chemin)
    reformes: list[Reforme] = []
    codes: set[str] = set()
    for fiche in contenu.get("reformes", []):
        manquants = {"code", "date", "texte", "parametres", "regimes"} - set(fiche)
        if manquants:
            raise ValueError(f"{chemin.name} / {fiche.get('code', '?')} : {sorted(manquants)}")
        code = str(fiche["code"])
        if code in codes:
            raise ValueError(f"{chemin.name} : réforme dupliquée {code}")
        codes.add(code)
        date = str(fiche["date"])
        if len(date) < 4 or not date[:4].isdigit():
            raise ValueError(f"{chemin.name} / {code} : date illisible {date!r}")
        absorbee = tuple(fiche.get("absorbee_par") or ())
        inconnus = set(absorbee) - set(DRAPEAUX_PAR_GENERATION)
        if inconnus:
            raise ValueError(f"{chemin.name} / {code} : drapeaux inconnus {sorted(inconnus)}")
        reformes.append(Reforme(
            code=code,
            date=date,
            annee=int(date[:4]),
            texte={"reference": str(fiche["texte"]["reference"]),
                   "id": fiche["texte"].get("id")},
            parametres=tuple(fiche["parametres"] or ()),
            regimes=tuple(fiche["regimes"] or ()),
            absorbee_par=absorbee,
            non_appliquee={
                str(k): " ".join(str(v).split())
                for k, v in (fiche.get("non_appliquee") or {}).items()
            },
        ))
    if not reformes:
        raise ValueError(f"aucune réforme dans {chemin}")
    return tuple(sorted(reformes, key=lambda r: r.date))


@dataclass(frozen=True)
class Pivot:
    """Un article de code ou de décret qui porte un paramètre d'une fiche."""

    texte: str
    num: str
    parametres: tuple[str, ...]


def charger_pivots(racine: Path) -> tuple[dict[str, tuple[Pivot, ...]], dict[str, str]]:
    """Rend (pivots par régime, raison ``hors_legi`` par régime)."""
    chemin = racine / "reference" / "regimes" / "pivots.yaml"
    contenu = charger_yaml(chemin)
    pivots: dict[str, tuple[Pivot, ...]] = {}
    hors_legi: dict[str, str] = {}
    for code, valeur in (contenu.get("pivots") or {}).items():
        if isinstance(valeur, dict) and "hors_legi" in valeur:
            hors_legi[str(code)] = " ".join(str(valeur["hors_legi"]).split())
            pivots[str(code)] = ()
            continue
        if not isinstance(valeur, list) or not valeur:
            raise ValueError(f"{chemin.name} / {code} : ni pivots ni raison hors_legi")
        pivots[str(code)] = tuple(
            Pivot(texte=str(p["texte"]), num=str(p.get("num") or ""),
                  parametres=tuple(p.get("parametres") or ()))
            for p in valeur
        )
    return pivots, hors_legi


def reformes_non_portees(catalogue: "CatalogueRegimes",
                         reformes: tuple[Reforme, ...],
                         tolerance: int = 1) -> list[tuple[str, str, str]]:
    """Les couples (réforme, régime) que la fiche ne porte ni ne déclare.

    Une réforme est PORTÉE par une fiche si une période commence l'année
    d'effet à ``tolerance`` près, ou si une période active cette année-là
    lève un des drapeaux qui l'absorbent, ou si le régime est déclaré dans
    ``non_appliquee`` avec sa raison. Un régime sans période active à la date
    — pas encore créé, déjà éteint — n'est pas concerné. Rend une liste de
    (code réforme, code régime, diagnostic).
    """
    manques: list[tuple[str, str, str]] = []
    for reforme in reformes:
        for code in reforme.regimes:
            if code not in catalogue:
                continue
            if code in reforme.non_appliquee:
                continue
            regime = catalogue[code]
            actives = [p for p in regime.periodes
                       if p.debut <= reforme.annee <= (p.fin if p.fin is not None else 9999)]
            if not actives:
                continue
            coupee = any(abs(p.debut - reforme.annee) <= tolerance for p in regime.periodes)
            if coupee:
                continue
            absorbee = any(getattr(p, drapeau, False)
                           for p in actives for drapeau in reforme.absorbee_par)
            if absorbee:
                continue
            debuts = sorted({p.debut for p in actives})
            manques.append((reforme.code, code,
                            f"période(s) active(s) depuis {debuts} sans coupure en "
                            f"{reforme.annee} ni drapeau {list(reforme.absorbee_par) or '—'}"))
    return manques
