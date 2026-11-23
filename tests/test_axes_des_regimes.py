"""Les deux axes du fichier de régime : la forme en quatre blocs, et ce que le
chargeur en lit (note de décision 0009, amendement du 22 novembre 2026).

Le fichier de régime range ses paramètres en quatre blocs — ``structure``,
``liquidation`` (au jour de la date d'effet), ``cotisation`` (à l'année
d'acquisition), ``servi`` — que le chargeur lit tels quels, sans plus en
refaire de périodes (étape 5). Les valeurs attendues viennent du texte des
fichiers, lu à la main.
"""
from __future__ import annotations

import datetime as dt

import pytest
import yaml
from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.axes import BLOCS, famille, verifier_les_blocs
from retraite_notionnelle.donnees.regimes import fichiers_de_regimes


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
    calcules = [c.name for c, f in fichiers_de_regimes(RACINE_DONNEES) if "liquidation" in f]
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


def test_un_champ_hors_de_son_bloc_est_refuse():
    fiche = {"code": "essai", "structure": {"type_calcul": "annuites"},
             "liquidation": [{"du": J(2000, 1, 1), "taux_cotisation_retraite": 0.1}],
             "cotisation": [{"du": J(2000, 1, 1)}]}
    with pytest.raises(ValueError, match="taux_cotisation_retraite"):
        verifier_les_blocs(fiche)


def _fiche(**blocs):
    fiche = {"code": "essai", "structure": {"type_calcul": "annuites"},
             "liquidation": [{"du": J(2000, 1, 1), "age_ouverture": 60}],
             "cotisation": [{"du": J(2000, 1, 1), "assiette": "plafonnee"}]}
    fiche.update(blocs)
    return fiche


@pytest.mark.parametrize("blocs, message", [
    # Une liquidation qui commence après la première année cotisée : 2000
    # n'aurait aucune règle de liquidation.
    ({"liquidation": [{"du": J(2010, 1, 1), "age_ouverture": 60}]},
     "aucune ligne de liquidation"),
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
    # Un servi écrit qui commence après la liquidation, ou finit avant elle :
    # une pension de 2000, ou de 2012, n'aurait aucune ligne servie.
    ({"servi": [{"du": J(2005, 1, 1), "valeur_point_euros": 1.0}]},
     "aucune ligne de servi"),
    ({"servi": [{"du": J(2000, 1, 1), "au": J(2010, 1, 1), "valeur_point_euros": 1.0}]},
     "aucune ligne de servi"),
    # Une cotisation au jour, que le chargeur n'admet pas avant le passage au jour.
    ({"cotisation": [{"du": J(2000, 7, 1)}]}, "1er janvier"),
    # Deux lignes de la même tranche la même année.
    ({"cotisation": [{"du": J(2000, 1, 1)}, {"du": J(2000, 1, 1)}]}, "tranche"),
    # Une fiche qui porterait encore ses périodes à côté des blocs.
    ({"periodes": [{"debut": 2000, "fin": None}]}, "periodes"),
])
def test_le_chargeur_refuse_des_blocs_qui_ne_tiennent_pas(blocs, message):
    with pytest.raises(ValueError, match=message):
        verifier_les_blocs(_fiche(**blocs))


# -- Le chargeur Python en blocs (étape 4) : ses lectures à la date et à l'année


@pytest.fixture(scope="module")
def catalogue():
    from retraite_notionnelle.donnees.regimes import CatalogueRegimes
    return CatalogueRegimes(RACINE_DONNEES)


def test_le_regime_porte_ses_quatre_blocs(catalogue):
    """Banque de France : une liquidation qui change le 1er avril 2007, une
    ligne de cotisation par année de 2007 à 2009 (banque_de_france.yaml)."""
    regime = catalogue["banque_de_france"]
    assert [l["du"] for l in regime.liquidation[:2]] == ["1930-01-01", "2007-04-01"]
    assert regime.liquidation[0]["au"] == "2007-04-01"
    assert regime.liquidation[0]["age_ouverture"] == 55
    assert "taux_cotisation_retraite" not in regime.liquidation[0]
    assert [l["type_calcul"] for l in regime.structure] == ["annuites"]
    de_2007 = [l for l in regime.cotisation if l["du"] == 2007]
    assert de_2007 == [{"du": 2007, "au": 2007, **{
        c: v for c, v in de_2007[0].items() if c not in ("du", "au")}}]
    assert de_2007[0]["taux_cotisation_retraite"] == 0.0785
    assert "age_ouverture" not in de_2007[0]


def test_la_liquidation_se_lit_a_sa_date(catalogue):
    """Le règlement annexé au décret n° 2007-262 vaut à compter du 1er avril
    2007 : une pension du 31 mars 2007 ouvre à 55 ans, une du 1er avril à
    60, l'une et l'autre avec la cotisation de 2007, à 7,85 %."""
    regime = catalogue["banque_de_france"]
    avant, apres = regime.a_la_date("2007-03-31"), regime.a_la_date("2007-04-01")
    assert (avant.age_ouverture, apres.age_ouverture) == (55, 60)
    assert avant.taux_cotisation_retraite == apres.taux_cotisation_retraite == 0.0785
    assert regime.a_la_date("1929-12-31") is None
    assert regime.a_la_date("2007-04-01") is regime.a_la_date("2007-06-01")


def test_une_annee_d_acquisition_lit_ses_tranches_et_la_liquidation_de_son_premier_janvier(
        catalogue):
    """L'Agirc-Arrco cotise en 2019 sur deux tranches, à 7,87 % puis 21,59 %
    (agirc_arrco.yaml) ; la Banque de France, en 2007, lit la liquidation du
    1er janvier, à 55 ans, ou celle du jour qu'on lui donne."""
    tranches = catalogue["agirc_arrco"].de_l_annee(2019)
    assert [(p.assiette, p.taux_cotisation_retraite) for p in tranches] == [
        ("tranche_1", 0.0787), ("tranche_2", 0.2159)]
    regime = catalogue["banque_de_france"]
    (de_2007,) = regime.de_l_annee(2007)
    assert (de_2007.age_ouverture, de_2007.taux_cotisation_retraite) == (55, 0.0785)
    assert regime.de_l_annee(2007, "2007-04-01")[0].age_ouverture == 60
    assert regime.de_l_annee(1900) == ()


def test_un_assemblage_sans_liquidation_ou_sans_cotisation_est_refuse(catalogue):
    """Le moteur assemblerait, sans la ligne qui manque, des paramètres où ses
    champs manquent ; des paramètres Python les portent tous : le chargeur
    refuse, plutôt que de prêter ceux d'une autre ligne. Aucun régime n'y
    tombe."""
    from dataclasses import replace
    regime = catalogue["banque_de_france"]
    (de_2007,) = [l for l in regime.cotisation if l["du"] == 2007]
    sans_tranche = replace(regime, cotisation=(de_2007,))
    with pytest.raises(ValueError, match="aucune ligne de cotisation"):
        sans_tranche.a_la_date("2010-01-01")
    sans_liquidation = replace(regime, liquidation=(
        {**regime.liquidation[-1], "du": "2008-01-01", "au": None},))
    with pytest.raises(ValueError, match="aucune ligne de liquidation"):
        sans_liquidation.de_l_annee(2007)


def _en_donnees(valeur):
    """Une valeur telle que le paquet l'écrit en JSON : tuples en listes."""
    import json
    return json.loads(json.dumps(valeur, sort_keys=True, default=str))


def test_les_blocs_du_chargeur_sont_ceux_du_paquet(catalogue):
    """Le pont désigne des paramètres par les rangs de leurs quatre lignes, que
    le Python et le portage lisent chacun dans ses blocs : ils doivent avoir les
    mêmes lignes, dans le même ordre, aux mêmes bornes, régime par régime
    (le paquet tait un champ à sa valeur par défaut)."""
    import json
    from retraite_notionnelle.config import RACINE_PROJET
    paquet = json.loads((RACINE_PROJET / "moteur" / "donnees.json").read_text(encoding="utf-8"))
    fiches = {fiche["code"]: fiche for fiche in paquet["regimes"]}
    assert set(fiches) == {regime.code for regime in catalogue}
    for regime in catalogue:
        for bloc in ("structure", "liquidation", "cotisation", "servi"):
            lignes = _en_donnees(getattr(regime, bloc))
            ecrites = fiches[regime.code][bloc]
            assert [(l["du"], l["au"]) for l in lignes] == [(l["du"], l["au"]) for l in ecrites], (
                regime.code, bloc)
            # Le paquet tait un champ à sa valeur par défaut, que le moteur pose,
            # et écrit à sa façon un champ composé : les champs simples suffisent
            # à reconnaître les lignes.
            for ligne, ecrite in zip(lignes, ecrites):
                simples = {champ: valeur for champ, valeur in ecrite.items()
                           if valeur is None or type(valeur) in (str, int, float, bool)}
                assert {champ: ligne.get(champ) for champ in simples} == simples, (
                    regime.code, bloc)


def test_des_parametres_se_designent_par_les_rangs_de_leurs_quatre_lignes(catalogue):
    """Des paramètres lus à la date ou à l'année, des lignes dont on les a
    assemblés : les rangs les redonnent."""
    for regime in catalogue:
        for annee in range(1900, 2071, 7):
            lus = regime.a_la_date(f"{annee:04d}-07-01")
            if lus is not None:
                assert regime.par_rangs(regime.rangs(lus)) is lus, (regime.code, annee)
    banque = catalogue["banque_de_france"]
    avant, apres = banque.a_la_date("2007-03-31"), banque.a_la_date("2007-04-01")
    assert banque.rangs(avant)[0] == 0 and banque.rangs(apres)[0] == 1
    assert banque.rangs(avant)[3] == banque.rangs(apres)[3]
