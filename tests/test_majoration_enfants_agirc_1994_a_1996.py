"""La majoration pour enfants de l'Agirc de 1994 à 1996 : le pourcentage de
service de l'accord du 9 février 1994 (action 130, file M3).

« Les majorations pour charges de famille visées à l'article 6 bis de l'annexe
1 à la convention collective nationale du 14 mars 1947 sont affectées, à
compter du 1er janvier 1995, d'un pourcentage de service égal à : - 96 % à
compter du 1er janvier 1995 - 85 % à compter du 1er janvier 1996 - 80 % à
compter du 1er janvier 1997 » (accord du 9 février 1994 relatif au régime de
retraite des cadres, article 2, recueil de la caisse « Accords nationaux des
partenaires sociaux », page imprimée 16). L'avenant A-159 l'a porté à
l'article 6 bis « avec effet du 1er mars 1994, en affectant d'un " pourcentage
de service " les majorations de points pour charges de famille » ; ces
modifications « sont illicites en tant qu'elles s'appliquent aux participants
dont la retraite a été liquidée avant l'entrée en vigueur de l'accord de
révision » (Cass. soc., 23 novembre 1999, n° 97-18.980, publié au bulletin) ;
la date du 1er janvier 1995 « concerne la prise d'effet de ce mode de calcul
et non la catégorie de retraites visée » (CA Lyon, 18 novembre 2004,
RG 03/03980, pour une retraite liquidée le 1er juillet 1994). La majoration
qu'il réduit, « 10% pour 3 enfants », « 30% pour 7 enfants et + », n'est lue
que dans une source secondaire (COR, séance du 25 mai 2011, document n° 7,
page 3) : la rédaction de l'article 6 bis d'alors n'est pas publiée en ligne.

D'où, pour trois enfants : 10 % à la date d'effet d'avant 1995, et pour
toujours si la retraite a pris effet avant le 1er mars 1994 ; 9,6 % en 1995 ;
8,5 % en 1996 ; 8 % depuis 1997. Une retraite liquidée du 1er mars 1994 au
31 décembre 1996 suit, après sa date d'effet, le pourcentage de chaque année :
les étapes de la majoration (``a_charge``) le disent, et sa part de 1997 est
celle que le modèle servait déjà. Chaque cas part de la requête du
simulateur, servi par le portage et refait par le moteur Python
(``servi_et_refait``) : un cadre de trois enfants, parti à 65 ans, au taux
plein. Les calculs, posés à la main, sont dans la note
docs/feuille_de_route/130/2026-11-03-majoration-enfants-agirc-1995-1996.md.
"""

from __future__ import annotations

import re

import pytest

from outils_pont import servi_et_refait

REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "22", "emploi": "cor_2026",
    "enfants": "3", "euros": "2026", "indexation": "triple_lock_inverse",
    "liquidation": "65", "primes": "0", "profil": "plat",
    "projection": "cor_reference", "salaire": "2", "sexe": "H",
    "statut": "salarie_prive_cadre", "stock": "prix", "table": "unisexe",
}

#: « 10% pour 3 enfants, 15% pour 4 enfants, 20% pour 5 enfants, 25% pour 6
#: enfants, 30% pour 7 enfants et + » (COR, document n° 7 du 25 mai 2011,
#: page 3) : la majoration de l'article 6 bis avant le pourcentage.
AVANT_LE_POURCENTAGE = (0.10, 0.15, 0.20, 0.25, 0.30)
#: Le pourcentage de service de chaque année de service (accord du 9 février
#: 1994, article 2) ; 100 % avant 1995.
POURCENTAGE = {1994: 1.00, 1995: 0.96, 1996: 0.85, 1997: 0.80}

#: Le cas, sa naissance, sa date d'effet (le premier jour du mois qui suit ses
#: 65 ans), le taux de trois enfants à cette date, et les étapes que la
#: majoration de l'Agirc suit ensuite : (date, taux servi).
CAS = {
    # Liquidée avant le 1er mars 1994 : rien ne la réduit (Cass. 1999).
    "avant_l_avenant": ("1928-12-15", "1994-01-01", 0.10, ()),
    # Liquidée le 1er juin 1994 : 10 % en 1994, puis le pourcentage de chaque
    # année (CA Lyon 2004).
    "juin_1994": ("1929-05-15", "1994-06-01", 0.10,
                  (("1995-01-01", 0.096), ("1996-01-01", 0.085), ("1997-01-01", 0.08))),
    "avril_1995": ("1930-03-15", "1995-04-01", 0.096,
                   (("1996-01-01", 0.085), ("1997-01-01", 0.08))),
    "avril_1996": ("1931-03-15", "1996-04-01", 0.085, (("1997-01-01", 0.08),)),
    # Depuis 1997, 80 % de 10 % : les 8 % que le modèle servait.
    "avril_1997": ("1932-03-15", "1997-04-01", 0.08, ()),
}
#: Le taux de 1997, que la part de l'Agirc garde une fois les étapes passées.
DEPUIS_1997 = 0.08

#: « 19,323.91 points × valeur de service 0.35109 € » : les points et la valeur
#: que le détail de la pension affiche.
POINTS_ET_VALEUR = re.compile(r"([\d,]+\.\d+) points × valeur de service ([\d.]+) €")


@pytest.fixture(scope="module")
def servis():
    cas = [{"cle": cle, "requete": {**REQUETE, "naissance": naissance}}
           for cle, (naissance, *_reste) in CAS.items()]
    servis, refus = servi_et_refait(cas)
    assert refus == {}, refus
    return {cle: servi["actuel"] for cle, servi in servis.items()}


def _droits_agirc(actuel: dict) -> float:
    """Les points de l'Agirc × la valeur de service : l'allocation, au taux
    plein, telle que le détail de la pension l'affiche."""
    pension = next(p for p in actuel["pensions_par_regime"] if p["regime"] == "agirc")
    trouve = POINTS_ET_VALEUR.search(pension["detail"])
    assert trouve, pension["detail"]
    assert "coefficient d'anticipation" not in pension["detail"], pension["detail"]
    return float(trouve.group(1).replace(",", "")) * float(trouve.group(2))


def _majoration(actuel: dict) -> dict:
    return next(a for a in actuel["avantages_appliques"] if a["code"] == "majoration_enfants")


def _part(parts, regime: str) -> float:
    return sum(part for code, part in parts if code == regime)


def test_le_bareme_servi_est_celui_de_l_accord_annee_par_annee():
    """La table du moteur sert aux points de l'Agirc d'avant 2012, pour trois à
    sept enfants et plus, la majoration de l'article 6 bis affectée du
    pourcentage de l'année de service : 100 % jusqu'en 1994, 96 % en 1995,
    85 % en 1996, 80 % depuis 1997 ; aux points de l'Arrco, le même barème à
    toute année de service."""
    from retraite_notionnelle.config import RACINE_DONNEES
    from retraite_notionnelle.scenarios.actuel import MajorationsEnfantsPoints

    table = MajorationsEnfantsPoints(RACINE_DONNEES)
    for service, pourcentage in POURCENTAGE.items():
        for enfants, base in enumerate(AVANT_LE_POURCENTAGE, start=3):
            for code in ("agirc", "agirc_entreprises_nouvelles"):
                assert table.taux(code, 1990, enfants, service) == pytest.approx(
                    base * pourcentage, abs=1e-12), (code, service, enfants)
        assert table.taux("agirc", 1990, 2, service) == 0.0
        assert table.taux("arrco", 1990, 3, service) == 0.10
    # Une année de service qui vient après 1997 garde 80 %.
    assert table.taux("agirc", 2005, 3, 2010) == 0.08
    assert table.taux("agirc", 2005, 3) == 0.08


@pytest.mark.parametrize("cle", CAS)
def test_la_majoration_de_l_agirc_a_la_date_d_effet(servis, cle):
    """Points × valeur × taux de l'année de la date d'effet."""
    _naissance, _effet, taux, _etapes = CAS[cle]
    actuel = servis[cle]
    droits = _droits_agirc(actuel)
    servie = _part(_majoration(actuel)["par_regime"], "agirc")
    assert servie == pytest.approx(droits * taux, abs=0.01), (cle, servie, droits)


@pytest.mark.parametrize("cle", CAS)
def test_la_majoration_suit_le_pourcentage_de_chaque_annee(servis, cle):
    """Les étapes de la majoration : ce que l'Agirc sert au-delà de ses 8 %
    depuis la date d'effet, puis depuis chaque 1er janvier jusqu'en 1997 ;
    aucune pour une retraite liquidée avant le 1er mars 1994, ni depuis 1997."""
    _naissance, effet, taux, etapes = CAS[cle]
    actuel = servis[cle]
    droits = _droits_agirc(actuel)
    lues = _majoration(actuel).get("a_charge") or []
    if not etapes:
        assert lues == [], (cle, lues)
        return
    attendues = [(effet, taux), *etapes]
    assert [depuis for depuis, _parts in lues] == [depuis for depuis, _ in attendues], lues
    for (depuis, parts), (_, servi) in zip(lues, attendues):
        assert _part(parts, "agirc") == pytest.approx(
            droits * (servi - DEPUIS_1997), abs=0.01), (cle, depuis)
    # Les étapes passées, l'Agirc sert ses 8 %.
    majoration = _majoration(actuel)
    finale = (_part(majoration["par_regime"], "agirc") - _part(lues[0][1], "agirc")
              + _part(lues[-1][1], "agirc"))
    assert finale == pytest.approx(droits * DEPUIS_1997, abs=0.01), cle


@pytest.mark.parametrize("cle", CAS)
def test_la_reversion_reprend_la_majoration_de_1997(servis, cle):
    """La part que la réversion reprend depuis 2019, sans le coefficient
    (``par_regime_sans_anticipation``) : celle que la majoration sert depuis
    1997, 8 % ; 10 % si la retraite a pris effet avant le 1er mars 1994."""
    _naissance, _effet, taux, etapes = CAS[cle]
    actuel = servis[cle]
    reprise = _part(_majoration(actuel)["par_regime_sans_anticipation"], "agirc")
    attendu = DEPUIS_1997 if etapes else taux
    assert reprise == pytest.approx(_droits_agirc(actuel) * attendu, abs=0.01), cle
