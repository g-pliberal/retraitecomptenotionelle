"""Les deux axes du fichier de régime : la forme en quatre blocs, et la vue
ancienne que le chargeur en fabrique (note de décision 0009, amendement du
22 novembre 2026, étape 2).

Le fichier de régime range ses paramètres en quatre blocs — ``structure``,
``liquidation`` (au jour de la date d'effet), ``cotisation`` (à l'année
d'acquisition), ``servi`` — et le chargeur en refait, pendant le gel, les
``periodes`` que le moteur lit encore. Les valeurs attendues viennent du
texte des fichiers, lu à la main, et non de la vue.
"""
from __future__ import annotations

import datetime as dt

import pytest
import yaml
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.axes import BLOCS, famille, vue_ancienne
from retraite_notionnelle.donnees.regimes import fiche_de_regime, fichiers_de_regimes


DOSSIER = RACINE_DONNEES / "reference" / "regimes"
J = dt.date


def _ecrits():
    """Les fichiers de régime calculés, tels qu'écrits sur le disque."""
    for chemin in sorted(DOSSIER.glob("*.yaml")):
        if chemin.name.startswith("_"):
            continue
        brut = yaml.safe_load(chemin.read_text(encoding="utf-8"))
        if isinstance(brut, dict) and "liquidation" in brut:
            yield chemin.name, brut


def test_les_quatre_vingts_regimes_calcules_sont_ecrits_en_quatre_blocs():
    ecrits = dict(_ecrits())
    calcules = [c.name for c, f in fichiers_de_regimes(RACINE_DONNEES) if "periodes" in f]
    assert sorted(ecrits) == sorted(calcules)
    assert len(ecrits) == 80
    for nom, brut in ecrits.items():
        assert "periodes" not in brut, nom
        assert {"structure", "liquidation", "cotisation"} <= set(brut), nom


def test_chaque_ligne_ne_porte_que_les_champs_de_son_bloc():
    bornes = {"du", "au", "notes", "textes", "tranche"}
    for nom, brut in _ecrits():
        for bloc in ("liquidation", "cotisation", "servi"):
            for ligne in brut.get(bloc, ()):
                etrangers = {c for c in set(ligne) - bornes if famille(c) != bloc}
                assert not etrangers, (nom, bloc, ligne["du"], etrangers)
                for renvoi in ligne.get("textes", {}):
                    assert famille(renvoi) == bloc, (nom, bloc, renvoi)
        assert set(brut["structure"]) <= {"type_calcul", "points_de"}, nom
    assert BLOCS == ("structure", "liquidation", "cotisation", "servi")


def test_les_lignes_de_liquidation_ne_se_chevauchent_jamais():
    for nom, brut in _ecrits():
        lignes = brut["liquidation"]
        for avant, apres in zip(lignes, lignes[1:]):
            assert avant["au"] <= apres["du"], (nom, avant["du"], apres["du"])
        assert all("au" in l for l in lignes[:-1]), nom


def test_la_vue_refait_la_periode_de_2007_de_la_banque_de_france():
    """Le règlement annexé au décret n° 2007-262 vaut à compter du 1er avril
    2007 : la période de 2007 liquide depuis ce jour, à soixante ans, et
    cotise à 7,85 % (banque_de_france.yaml, lignes de liquidation du
    1er avril 2007 et de cotisation de 2007)."""
    periodes = fiche_de_regime(RACINE_DONNEES, "banque_de_france")["periodes"]
    de_2007 = [p for p in periodes if p["debut"] == 2007]
    assert len(de_2007) == 1
    p = de_2007[0]
    assert p["fin"] == 2007
    assert p["date_effet"] == [J(2007, 4, 1), J(2008, 1, 1)]
    assert p["age_ouverture"] == 60
    assert p["taux_cotisation_retraite"] == 0.0785
    assert p["textes_des_renvois"] == {
        "surcote_bareme": {"id": "LEGIARTI000006778516", "depuis": "2007-04-01"}}
    avant = [p for p in periodes if p["debut"] == 1930][0]
    assert avant["date_effet"] == [J(1930, 1, 1), J(2007, 4, 1)]
    assert avant["age_ouverture"] == 55


def test_une_borne_au_jour_va_a_l_annee_dont_la_periode_l_ouvre():
    """CARPIMKO : la période de 2015 liquide du 1er janvier au 3 octobre 2015,
    celle de 2016 depuis le 3 octobre 2015 ; celle de 2014, sans date
    d'effet, garde ses années."""
    periodes = fiche_de_regime(RACINE_DONNEES, "carpimko_complementaire")["periodes"]
    par_debut = {p["debut"]: p for p in periodes}
    assert "date_effet" not in par_debut[2014]
    assert par_debut[2015]["date_effet"] == [J(2015, 1, 1), J(2015, 10, 3)]
    assert par_debut[2016]["date_effet"] == [J(2015, 10, 3), J(2017, 1, 1)]


def test_la_vue_d_une_fiche_posee_a_la_main():
    """Deux lignes de cotisation, deux tranches la seconde année ; une
    liquidation qui change le 1er juillet 2001 : la période de 2000 liquide
    jusqu'à ce jour, celle de 2001 depuis ; un point servi."""
    fiche = {
        "code": "essai",
        "structure": {"type_calcul": "points"},
        "liquidation": [
            {"du": J(2000, 1, 1), "au": J(2001, 7, 1), "age_ouverture": 60,
             "notes": "avant"},
            {"du": J(2001, 7, 1), "age_ouverture": 62,
             "textes": {"age_ouverture": {"id": "X"}}},
        ],
        "cotisation": [
            {"du": J(2000, 1, 1), "au": J(2001, 1, 1), "assiette": "plafonnee",
             "taux_cotisation_retraite": 0.1},
            {"du": J(2001, 1, 1), "assiette": "plafonnee",
             "taux_cotisation_retraite": 0.12, "notes": "hausse"},
            {"du": J(2001, 1, 1), "tranche": 2, "assiette": "tranche_2",
             "taux_cotisation_retraite": 0.2},
        ],
        "servi": [{"du": J(2000, 1, 1), "valeur_point_euros": 1.5}],
    }
    assert vue_ancienne(fiche) == {
        "code": "essai",
        "periodes": [
            {"debut": 2000, "fin": 2000, "date_effet": [J(2000, 1, 1), J(2001, 7, 1)],
             "type_calcul": "points",
             "age_ouverture": 60, "valeur_point_euros": 1.5,
             "assiette": "plafonnee", "taux_cotisation_retraite": 0.1,
             "notes": "avant"},
            {"debut": 2001, "fin": None, "date_effet": [J(2001, 7, 1), None],
             "type_calcul": "points", "age_ouverture": 62,
             "valeur_point_euros": 1.5, "assiette": "plafonnee",
             "taux_cotisation_retraite": 0.12,
             "textes_des_renvois": {"age_ouverture": {"id": "X"}},
             "notes": "hausse"},
            {"debut": 2001, "fin": None, "date_effet": [J(2001, 7, 1), None],
             "type_calcul": "points", "age_ouverture": 62,
             "valeur_point_euros": 1.5, "assiette": "tranche_2",
             "taux_cotisation_retraite": 0.2,
             "textes_des_renvois": {"age_ouverture": {"id": "X"}}},
        ],
    }


def test_un_champ_hors_de_son_bloc_est_refuse():
    fiche = {"code": "essai", "structure": {"type_calcul": "annuites"},
             "liquidation": [{"du": J(2000, 1, 1), "taux_cotisation_retraite": 0.1}],
             "cotisation": [{"du": J(2000, 1, 1)}]}
    with pytest.raises(ValueError, match="taux_cotisation_retraite"):
        vue_ancienne(fiche)


def _fiche(**blocs):
    fiche = {"code": "essai", "structure": {"type_calcul": "annuites"},
             "liquidation": [{"du": J(2000, 1, 1), "age_ouverture": 60}],
             "cotisation": [{"du": J(2000, 1, 1), "assiette": "plafonnee"}]}
    fiche.update(blocs)
    return fiche


@pytest.mark.parametrize("blocs, message", [
    # Une liquidation qui commence après la première année cotisée : la
    # période de 2000 n'aurait aucune règle de liquidation.
    ({"liquidation": [{"du": J(2010, 1, 1), "age_ouverture": 60}]},
     "aucune ligne de liquidation|aucune frontière"),
    ({"liquidation": [{"du": J(2000, 1, 1), "au": J(2005, 1, 1), "age_ouverture": 60}],
      "cotisation": [{"du": J(2000, 1, 1), "au": J(2005, 1, 1)}, {"du": J(2005, 1, 1)}]},
     "aucune ligne de liquidation"),
    # Un trou d'un mois dans la liquidation.
    ({"liquidation": [{"du": J(2000, 1, 1), "au": J(2009, 12, 1), "age_ouverture": 60},
                      {"du": J(2010, 2, 1), "age_ouverture": 62}],
      "cotisation": [{"du": J(2000, 1, 1), "au": J(2010, 1, 1)}, {"du": J(2010, 1, 1)}]},
     "trou"),
    # Deux lignes de liquidation dans le désordre.
    ({"liquidation": [{"du": J(2005, 1, 1), "age_ouverture": 62},
                      {"du": J(2000, 1, 1), "au": J(2005, 1, 1), "age_ouverture": 60}]},
     "dans l'ordre"),
    # Deux lignes servies ouvertes ensemble.
    ({"servi": [{"du": J(2000, 1, 1), "valeur_point_euros": 1.0},
                {"du": J(2010, 1, 1), "valeur_point_euros": 2.0}]}, "se chevauchent"),
    # Une cotisation au jour, que le chargeur n'admet pas avant le passage au jour.
    ({"cotisation": [{"du": J(2000, 7, 1)}]}, "1er janvier"),
    # Deux lignes de la même tranche la même année.
    ({"cotisation": [{"du": J(2000, 1, 1)}, {"du": J(2000, 1, 1)}]}, "tranche"),
    # Une fiche qui porterait encore ses périodes à côté des blocs.
    ({"periodes": [{"debut": 2000, "fin": None}]}, "periodes"),
])
def test_la_vue_refuse_ce_qu_elle_ne_saurait_refaire(blocs, message):
    with pytest.raises(ValueError, match=message):
        vue_ancienne(_fiche(**blocs))
