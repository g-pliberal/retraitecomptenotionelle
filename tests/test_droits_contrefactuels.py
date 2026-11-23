"""Les droits contrefactuels du scénario 1 (action 138, étape 10).

La carrière liquidée sous deux autres états du droit que celui qui s'applique :
la loi n° 2023-270 du 14 avril 2023 sans la suspension que l'article 105 de la
loi n° 2025-1403 du 30 décembre 2025 y a mise, et le droit en vigueur au
31 août 2023, avant que la première ne prenne effet. Ne changent que l'âge
légal (L. 161-17-2 et D. 161-2-1-9), la durée requise (L. 161-17-3) et les âges
de la carrière longue (D. 351-1-1), que ces deux lois ont réécrits ; le reste
du droit est celui d'aujourd'hui (``Parametres.droit_contrefactuel``).

Les valeurs attendues sont lues aux versions de ces articles que garde l'index
LEGI, relu le 19 octobre 2026, et non tirées du modèle. Les carrières sont
fictives.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.calendrier import date_d_effet

from facade import Simulateur, ouvrir
from outils_pont import Saisies

SANS_SUSPENSION = "loi_2023_sans_suspension"
AU_31_AOUT_2023 = "au_31_aout_2023"

#: L'âge légal et la durée requise, par mois de naissance, sous les trois états
#: du droit :
#:
#: - en vigueur (``None``) : L. 161-17-2 (LEGIARTI000053280889) et L. 161-17-3
#:   (LEGIARTI000053280903), versions du 31 décembre 2025 — « 3° Soixante-deux
#:   ans et neuf mois, pour les assurés nés entre le 1er janvier 1963 et le
#:   31 mars 1965 ; 4° Soixante-trois ans, pour les assurés nés entre le
#:   1er avril et le 31 décembre 1965 », « 4° 170 trimestres, pour les assurés
#:   nés entre le 1er janvier 1963 et le 31 mars 1965 ; 5° 171 trimestres […]
#:   entre le 1er avril 1965 et le 31 décembre 1965 » ;
#: - la loi de 2023 sans la suspension : D. 161-2-1-9 (LEGIARTI000047634502) et
#:   L. 161-17-3 (LEGIARTI000047452764), versions du 1er septembre 2023 — « 10°
#:   Soixante-trois ans pour les assurés nés en 1964 ; 11° Soixante-trois ans
#:   et trois mois pour les assurés nés en 1965 », « 14° Soixante-quatre ans
#:   pour les assurés nés à compter du 1er janvier 1968 », « 5° 171 trimestres,
#:   pour les assurés nés en 1964 ; 6° 172 trimestres, pour les assurés nés à
#:   partir du 1er janvier 1965 » ;
#: - au 31 août 2023 : D. 161-2-1-9 (LEGIARTI000025089933), version du
#:   31 décembre 2011 — « 6° Soixante deux ans pour les assurés nés à compter
#:   du 1er janvier 1955 » —, et L. 161-17-3 (LEGIARTI000028494794), version du
#:   22 janvier 2014 — « 3° 169 trimestres, pour les assurés nés entre le
#:   1er janvier 1964 et le 31 décembre 1966 ; 4° 170 trimestres […] entre le
#:   1er janvier 1967 et le 31 décembre 1969 ; 5° 171 trimestres […] entre le
#:   1er janvier 1970 et le 31 décembre 1972 ».
#:
#: Le né en 1958 a les mêmes sous les trois : aucune des deux lois ne l'a touché.
ATTENDUS = {
    "1958-03-01": {None: (62.0, 167), SANS_SUSPENSION: (62.0, 167), AU_31_AOUT_2023: (62.0, 167)},
    "1964-06-01": {None: (62.75, 170), SANS_SUSPENSION: (63.0, 171), AU_31_AOUT_2023: (62.0, 169)},
    "1965-08-01": {None: (63.0, 171), SANS_SUSPENSION: (63.25, 172), AU_31_AOUT_2023: (62.0, 169)},
    "1968-05-01": {None: (63.75, 172), SANS_SUSPENSION: (64.0, 172), AU_31_AOUT_2023: (62.0, 170)},
    "1971-03-01": {None: (64.0, 172), SANS_SUSPENSION: (64.0, 172), AU_31_AOUT_2023: (62.0, 171)},
}


@pytest.fixture(scope="module")
def saisies() -> Saisies:
    return Saisies()


@pytest.fixture(scope="module")
def du_portage() -> Saisies:
    """Les saisies, et un simulateur de la façade, que le portage sert."""
    return Saisies(Simulateur)


def _moteur(saisies: Saisies, parametres, droit: str | None):
    return saisies.simulateur(parametres.avec(droit_contrefactuel=droit)).scenario_actuel


@pytest.mark.parametrize("droit", [None, SANS_SUSPENSION, AU_31_AOUT_2023])
@pytest.mark.parametrize("naissance", sorted(ATTENDUS))
def test_l_age_legal_et_la_duree_de_chaque_etat_du_droit(du_portage, naissance, droit):
    """Un salarié entré à vingt-trois ans, que la carrière longue ne vise pas,
    liquidé à soixante-sept ans : le droit s'ouvre à l'âge légal de l'état du
    droit retenu, et la durée requise est la sienne."""
    annee = int(naissance[:4])
    parametres, carriere = du_portage.lire({"naissance": naissance, "debut": f"{annee + 23}-09",
                                            "liquidation": f"{annee + 67}{naissance[4:7]}"})
    moteur = _moteur(du_portage, parametres, droit)
    age, trimestres = ATTENDUS[naissance][droit]
    assert ouvrir.age_ouverture_droit(moteur, carriere) == pytest.approx(age)
    assert moteur.calculer(carriere).trimestres_requis == trimestres


#: L'âge du taux plein sans condition de durée, le même sous les trois états
#: du droit (L. 351-8, 1°, relu dans l'index LEGI le 19 novembre 2026) :
#:
#: - au 31 août 2023 : « 1° Les assurés qui atteignent l'âge prévu à l'article
#:   L. 161-17-2 augmenté de cinq années » (LEGIARTI000028498855, du 22 janvier
#:   2014 au 1er septembre 2023), cet âge étant alors « fixé à soixante-deux ans
#:   pour les assurés nés à compter du 1er janvier 1955 » (L. 161-17-2,
#:   LEGIARTI000025014605) : soixante-deux ans et cinq ;
#: - la loi de 2023, sans la suspension : « l'âge prévu au premier alinéa de
#:   l'article L. 161-17-2 augmenté de trois années » (LEGIARTI000047452736, du
#:   1er septembre 2023), ce premier alinéa disant « soixante-quatre ans pour
#:   les assurés nés à compter du 1er janvier 1968 » (LEGIARTI000047452768) :
#:   soixante-quatre ans et trois, quelle que soit la génération ;
#: - en vigueur : la même phrase (LEGIARTI000051289852), et un premier alinéa
#:   qui dit toujours soixante-quatre ans, « pour les assurés nés à compter du
#:   1er janvier 1969 » (LEGIARTI000053280889).
#:
#: La note de décision 0009 fera de cet âge un renvoi à l'âge légal. Si le
#: droit du 31 août 2023 n'y gardait que l'âge légal de 2011, le renvoi de 2023
#: y lirait soixante-deux ans et trois : soixante-cinq ans, l'erreur que ce
#: test garde (second rectificatif).
AGE_DU_TAUX_PLEIN = 67.0


@pytest.mark.parametrize("droit", [None, SANS_SUSPENSION, AU_31_AOUT_2023])
@pytest.mark.parametrize("naissance", sorted(ATTENDUS))
def test_l_age_du_taux_plein_est_le_meme_sous_les_trois_etats_du_droit(du_portage, naissance, droit):
    """Le même salarié : sous chaque état du droit, la décote s'annule à
    soixante-sept ans, que la durée soit atteinte ou non."""
    annee = int(naissance[:4])
    parametres, carriere = du_portage.lire({"naissance": naissance, "debut": f"{annee + 23}-09",
                                            "liquidation": f"{annee + 67}{naissance[4:7]}"})
    simulateur = du_portage.simulateur(parametres.avec(droit_contrefactuel=droit))
    periode = simulateur.catalogue["regime_general"].a_la_date(date_d_effet(carriere))
    age = ouvrir.age_taux_plein(simulateur.scenario_actuel, periode, carriere)
    assert age == pytest.approx(AGE_DU_TAUX_PLEIN)


def test_les_ages_de_la_carriere_longue_suivent_l_etat_du_droit(du_portage):
    """Un né en février 1966 entré à dix-neuf ans, en mars 1985 : il a ses
    cinq trimestres avant la fin de l'année de ses vingt ans, non de ses
    dix-huit. Le décret n° 2026-345 du 7 mai 2026 lui ouvre la porte des vingt
    ans à soixante ans et neuf mois ; celui du 3 juin 2023 (D. 351-1-1, II,
    version du 1er septembre 2023), à l'âge légal de sa génération, 63 ans et
    6 mois, diminué de deux ans et six mois : soixante et un ans ; celui du
    2 juillet 2012, en vigueur au 31 août 2023, à soixante ans, quelle que soit
    la génération. La durée cotisée, ici, ne manque pas."""
    parametres, carriere = du_portage.lire({"naissance": "1966-02-01", "debut": "1985-03",
                                         "liquidation": "2027-02"})
    attendus = {None: 60.75, SANS_SUSPENSION: 61.0, AU_31_AOUT_2023: 60.0}
    for droit, age in attendus.items():
        porte = _moteur(du_portage, parametres, droit).carriere_longue.age_de_depart(
            carriere, carriere.annee_liquidation, trimestres_cotises=180, requis=172)
        assert porte is not None and porte[0] == pytest.approx(age), droit


def test_au_31_aout_2023_la_porte_des_dix_sept_ans_reste_aux_nes_de_1952_et_1953(du_portage):
    """Le décret du 2 juillet 2012, que le droit au 31 août 2023 applique à
    toute date, ne donne sa porte des débuts avant dix-sept ans qu'aux nés de
    1952, à cinquante-neuf ans et quatre mois, et de 1953, à cinquante-neuf
    ans et huit mois (D. 351-1-1, II, A et B, 3°, LEGIARTI000026139949). Un né
    en février 1966 entré à seize ans, en mars 1982, n'a que quatre
    trimestres à la fin de l'année de ses seize ans : sous ce décret, il part
    à soixante ans, par la porte des vingt ans (I), et non à cinquante-neuf
    ans et huit mois, que le moteur lui ouvrait en étendant la porte de 1953
    aux générations suivantes. Sous les décrets de 2023 et de 2026, la porte
    des dix-huit ans lui donne aussi soixante ans."""
    parametres, carriere = du_portage.lire({"naissance": "1966-02-01", "debut": "1982-03",
                                         "liquidation": "2026-02"})
    for droit in (None, SANS_SUSPENSION, AU_31_AOUT_2023):
        porte = _moteur(du_portage, parametres, droit).carriere_longue.age_de_depart(
            carriere, carriere.annee_liquidation, trimestres_cotises=180, requis=172)
        assert porte is not None and porte[0] == pytest.approx(60.0), droit


def test_un_depart_d_avant_septembre_2026_a_la_duree_de_l_etat_du_droit(du_portage):
    """Un né en juin 1964 qui part en juillet 2026, par la carrière longue :
    le droit en vigueur lui oppose 171 trimestres, la durée de la loi de 2023
    que le VI de l'article 105 de la loi du 30 décembre 2025 garde aux pensions
    prenant effet avant le 1er septembre 2026 (circulaire Cnav 2026-07, point
    2.1) ; la loi de 2023 sans la suspension, de même ; le droit au 31 août
    2023, les 169 trimestres de la version de 2014 de L. 161-17-3."""
    parametres, carriere = du_portage.lire({"naissance": "1964-06-01", "debut": "1982-09",
                                            "liquidation": "2026-07"})
    attendus = {None: 171, SANS_SUSPENSION: 171, AU_31_AOUT_2023: 169}
    for droit, trimestres in attendus.items():
        assert _moteur(du_portage, parametres, droit).calculer(carriere).trimestres_requis \
            == trimestres, droit


def test_un_droit_que_le_moteur_ne_connait_pas_est_refuse(saisies):
    """Le moteur refuse ce qu'il ne sait pas calculer : un état du droit qu'il
    ne connaît pas l'arrête, au lieu de rendre le droit en vigueur. Le refus
    vient du portage, au calcul (``ScenarioActuel._sousLeDroit``)."""
    parametres, carriere = saisies.lire({})
    with pytest.raises(RuntimeError, match="droit contrefactuel inconnu : 'au_1er_janvier_2011'"):
        _moteur(saisies, parametres, "au_1er_janvier_2011").calculer(carriere)
