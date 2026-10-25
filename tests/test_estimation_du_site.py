"""Le système 1 au format de « Mon estimation retraite », sur le site.

Les départs que la synthèse officielle chiffre — au plus tôt, au taux plein, au
taux plein automatique — sont datés par le pilote du portage
(``agesDeLEstimation``, ``moteur/js/pilote.js``), liquidés étage par étage
(``departEstime``, ``moteur/js/contexte.js``), et la page les montre en brut
mensuel, étage par étage, le net en second, à côté du total que le lecteur
recopie de son estimation (``estimationOfficielle``, ``moteur/js/pages.js``).
Ils n'ont que cet exemplaire depuis l'action 161, étape 6. Ces tests tiennent
chaque âge du portage à celui que l'étape « ouvrir le droit » du Python oppose
à la carrière liquidée à cet âge, chaque départ à la liquidation que le Python
simule de cette carrière, étage par étage posé à la main sur elle — le moteur
garde ses deux exemplaires —, et la page à ce qu'elle promet. La saisie est
celle du portage, la seule : le Python simule les carrières que le portage
bâtit, par le pont. Les carrières sont fictives.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from functools import cache
from pathlib import Path

import pytest

from retraite_notionnelle.droit import ouvrir
from retraite_notionnelle.remuneration import assiette_maladie, charger_prelevements
from retraite_notionnelle.web.site import ErreurSite, module, site
from outils_pont import refus_de_la_saisie, saisie_du_portage
from outils_web import montants_du_portage, page, saisies  # noqa: F401 — les fixtures partagées

RACINE = Path(__file__).resolve().parents[1]

#: Des carrières fictives qui traversent les cas du bloc : un départ légal
#: confondu avec le taux plein, trois âges distincts, la carrière longue, le
#: régime intégré et l'additionnel, les enfants, un petit salaire, un relevé,
#: deux métiers ; puis ceux qui n'ont aucun départ à chiffrer.
REQUETES = {
    "defaut": {},
    "trois_ages": {"naissance": "1968-05-01", "debut": "1990-09", "liquidation": "2032-01"},
    "carriere_longue": {"naissance": "1966-02-01", "debut": "1984-09",
                        "liquidation": "2030-01"},
    # La même, coupée de deux ans de chômage indemnisé, dont D. 351-1-2 répute
    # cotisés quatre trimestres, sous chaque état du droit.
    "carriere_longue_chomage": {"naissance": "1966-02-01", "debut": "1984-09",
                                "liquidation": "2030-01",
                                "interruptions": "2008:2009:chomage_indemnise"},
    "fonctionnaire": {"naissance": "1975-01-01", "statut": "fonctionnaire_etat",
                      "debut": "1998-09", "primes": "0.2"},
    "cadre": {"naissance": "1976-04-01", "statut": "salarie_prive_cadre", "debut": "1999-09"},
    "mere": {"naissance": "1980-06-01", "sexe": "F", "enfants": "3", "debut": "2003-09"},
    "petit_salaire": {"naissance": "1985-01-01", "debut": "2010-01",
                      "unite_revenu": "euros_mois", "salaire": "1100"},
    "releve": {"naissance": "1975-01-01", "liquidation": "2039-01", "releve": "\n".join(
        f"{annee}:salarie_prive_non_cadre:{20_000 + 500 * (annee - 1997)}"
        for annee in range(1997, 2026))},
    # Le même relevé, prolongé jusqu'à chaque départ, mais coupé de chômage,
    # puis d'une période en Allemagne, que la prolongation respecte.
    "releve_interrompu": {"naissance": "1975-01-01", "liquidation": "2039-01",
                          "releve": "\n".join(
                              f"{annee}:salarie_prive_non_cadre:{20_000 + 500 * (annee - 1997)}"
                              for annee in range(1997, 2026)),
                          "interruptions": "2028:2029:chomage_indemnise",
                          "etranger1_pays": "DE", "etranger1_debut": "2031-01",
                          "etranger1_fin": "2033-07", "etranger1_activite": "salariee"},
    # Un relevé qui s'arrête en 2018, d'un né en 1966 : prolongé, il atteint
    # la durée requise avant 67 ans ; arrêté, il ne le faisait jamais, et le
    # taux plein attendait l'âge où il est automatique.
    "releve_ancien": {"naissance": "1966-09-01", "releve": "\n".join(
        f"{annee}:salarie_prive_cadre:{30_000 + 900 * (annee - 1990)}"
        for annee in range(1990, 2019))},
    # Le départ anticipé des assurés handicapés, une incapacité d'au moins
    # 50 % depuis le premier emploi : il ouvre le premier départ, au taux plein.
    "handicap": {"naissance": "1975-01-01", "debut": "1996-01", "handicap": "1996-01"},
    "deux_metiers": {"unite_revenu": "euros_mois", "salaire": "2900",
                     "metier2_debut": "40", "metier2_statut": "artisan",
                     "metier2_salaire": "4200"},
    "parti": {"naissance": "1955-01-01", "liquidation": "2017-01"},
    "par_pension": {"situation": "retraite", "pension": "1500"},
    # La radiation pour invalidité ouvre la pension du fonctionnaire à tout
    # âge : la saisie date elle-même ce départ.
    "radiation": {"naissance": "1975", "statut": "fonctionnaire_etat",
                  "radiation_invalidite": "2010-06", "invalidite_imputable": "oui",
                  "taux_invalidite": "60", "metier2_debut": "2010-06",
                  "metier2_statut": "salarie_prive_non_cadre"},
    # Un métier qui commence après l'âge légal : la saisie refuse la carrière à
    # cet âge, avec ses mots, et le modèle n'est pas même interrogé.
    "metier_tardif": {"naissance": "1975-01-01", "debut": "1996-01", "liquidation": "2042-01",
                      "metier2_debut": "2039-06", "metier2_statut": "salarie_prive_cadre"},
}


#: Les départs que la synthèse de « Mon estimation retraite » chiffre, dans son
#: ordre — au plus tôt, l'âge légal ou la carrière longue qui le devance ; au
#: taux plein ; au taux plein automatique —, et la règle de l'étape « ouvrir le
#: droit » qui date chacun.
REGLES = {"legal": ouvrir.age_ouverture_droit, "taux_plein": ouvrir.age_taux_plein_droit,
          "automatique": ouvrir.age_annulation_droit}

#: Le droit qui s'applique, puis les deux droits contrefactuels du scénario 1
#: (action 138, étape 10) : la loi de 2023 sans la suspension, et le droit au
#: 31 août 2023.
DROITS = (None, "loi_2023_sans_suspension", "au_31_aout_2023")


def _au_depart(requete: dict, age: float) -> dict:
    """La requête liquidée à ``age`` : la saisie lit un âge nu, comme ceux des
    adresses d'avant le calendrier, à sa valeur exacte."""
    return {**requete, "liquidation": repr(age)}


@dataclass(frozen=True)
class Depart:
    """Un départ, tel que le portage le date et le chiffre (``departEstime``,
    ``moteur/js/contexte.js``) : ses montants sont bruts, annuels, en euros
    constants de l'année de référence."""

    quoi: tuple[str, ...]
    age: float
    date: str
    etages: dict[str, float]
    total: float
    minimum_vieillesse: float
    trimestres: int
    trimestres_requis: int
    motif_ouverture: str
    assiette_maladie: float
    assiette_regime_general: float


def _departs_du_portage(requetes: list[dict], droit: str | None = None,
                        ) -> list[tuple[Depart, ...]]:
    """Les départs de chaque requête, datés et chiffrés par le portage
    (``departsDeLEstimation``, ``moteur/js/contexte.js``), sous le droit
    contrefactuel ``droit`` s'il en nomme un (``tests/js/comparer-estimation.mjs``).
    Vides où le bloc se tait : une saisie par la pension, des pensions que la
    saisie date elle-même, un départ d'une année passée, une carrière que la
    saisie ou le modèle refusent à l'un des âges."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-estimation.mjs"), chemin,
             *([droit] if droit else [])],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    lus = json.loads(execution.stdout)
    assert not [lu for lu in lus if isinstance(lu, dict)], lus
    return [tuple(Depart(**{**depart, "quoi": tuple(depart["quoi"])}) for depart in departs)
            for departs in lus]


@cache
def _estimation(droit: str | None = None) -> dict[str, tuple[Depart, ...]]:
    """Les départs de chaque requête du fichier, sous ``droit`` : un appel de
    node par état du droit."""
    return dict(zip(REQUETES, _departs_du_portage(list(REQUETES.values()), droit)))


def _departs(nom: str, droit: str | None = None) -> tuple[Depart, ...]:
    return _estimation(droit)[nom]


def _parametres(saisies, requete: dict, droit: str | None = None):
    """Les paramètres de la requête, sous le droit contrefactuel ``droit`` s'il
    en nomme un."""
    parametres = saisies.parametres(requete)
    return parametres if droit is None else parametres.avec(droit_contrefactuel=droit)


def _liquidation_du_python(saisies, requete: dict, depart: Depart,
                           droit: str | None = None) -> dict:
    """Ce que le Python simule de la carrière que le portage bâtit de la
    requête à l'âge de ``depart`` : la liquidation de son échéancier sous le
    scénario 1, posée à la main étage par étage — la pension de chaque régime,
    minima compris, et la part qu'il sert de la majoration pour enfants, à
    l'étage que le catalogue lui donne —, en euros constants de l'année de
    référence ; le minimum vieillesse, qu'aucun régime ne sert, à part ; ce
    que frappent la cotisation maladie de 1 % et, pour un non-résident, le
    taux du régime général (:func:`~retraite_notionnelle.remuneration.assiette_maladie`)."""
    parametres = _parametres(saisies, requete, droit)
    simulateur = saisies.simulateur(parametres)
    carriere = saisies.carriere(_au_depart(requete, depart.age))
    resultat = simulateur.echeancier(carriere).au_depart
    passage = simulateur.macro.coefficient_prix(carriere.annee_liquidation,
                                                parametres.annee_euros_constants)
    etages: dict[str, float] = {}

    def porter(regime: str, montant: float) -> None:
        etage = simulateur.catalogue[regime].etage
        etages[etage] = etages.get(etage, 0.0) + montant * passage

    for pension in resultat.pensions_par_regime:
        porter(pension.regime, pension.montant)
    for avantage in resultat.avantages_appliques:
        if avantage.code == "majoration_enfants":
            for regime, part in avantage.par_regime:
                porter(regime, part)
    pensions = charger_prelevements(parametres.racine_donnees).pensions
    date = carriere.date_liquidation
    return {
        "age": carriere.age_liquidation, "date": f"{date.annee:04d}-{date.mois:02d}",
        "etages": etages, "total": sum(etages.values()),
        "minimum_vieillesse": passage * sum(avantage.montant
                                            for avantage in resultat.avantages_appliques
                                            if avantage.code == "minimum_vieillesse"),
        "trimestres": resultat.trimestres_valides,
        "trimestres_requis": resultat.trimestres_requis,
        "motif_ouverture": resultat.motif_ouverture,
        "assiette_maladie": passage * assiette_maladie(pensions.regimes_maladie, resultat)[0],
        "assiette_regime_general": passage * assiette_maladie(
            pensions.regimes_generaux, resultat)[0],
    }


def _ecarts(obtenu, attendu, chemin: str, ecarts: list[str]) -> None:
    """Un milliardième au plus sur un nombre, comme les témoins ; rien ailleurs."""
    if isinstance(attendu, bool) or not isinstance(attendu, (int, float)):
        if isinstance(attendu, dict) and isinstance(obtenu, dict):
            for cle in sorted(set(attendu) | set(obtenu)):
                _ecarts(obtenu.get(cle), attendu.get(cle), f"{chemin}.{cle}", ecarts)
        elif isinstance(attendu, list) and isinstance(obtenu, list) and len(attendu) == len(obtenu):
            for rang, (o, a) in enumerate(zip(obtenu, attendu)):
                _ecarts(o, a, f"{chemin}[{rang}]", ecarts)
        elif obtenu != attendu:
            ecarts.append(f"{chemin} : python={str(attendu)[:80]} js={str(obtenu)[:80]}")
        return
    if isinstance(obtenu, bool) or not isinstance(obtenu, (int, float)):
        ecarts.append(f"{chemin} : python={attendu} js={obtenu}")
        return
    if abs(obtenu - attendu) / max(abs(attendu), 1e-300) > 1e-9 and abs(obtenu - attendu) > 1e-12:
        ecarts.append(f"{chemin} : python={attendu} js={obtenu}")


@pytest.mark.parametrize("droit", DROITS)
def test_chaque_depart_est_a_l_age_que_le_droit_oppose_a_sa_carriere(saisies, droit):
    """Le pilote du portage date chaque départ au point fixe de sa règle : l'âge
    que l'étape « ouvrir le droit » du Python oppose à la carrière que le
    portage bâtit à cet âge — au plus tôt, au taux plein, au taux plein
    automatique — est l'âge du départ, et les âges que le départ réunit, la
    page les confondant, y sont déjà atteints. Sous le droit qui s'applique et
    sous les deux droits contrefactuels."""
    for nom, requete in REQUETES.items():
        actuel = saisies.simulateur(_parametres(saisies, requete, droit)).scenario_actuel
        for depart in _departs(nom, droit):
            carriere = saisies.carriere(_au_depart(requete, depart.age))
            premier, *reunis = depart.quoi
            assert REGLES[premier](actuel, carriere) == pytest.approx(
                depart.age, abs=1e-9), (nom, premier)
            for quoi in reunis:
                assert REGLES[quoi](actuel, carriere) <= depart.age + 1e-9, (nom, quoi)


@pytest.mark.parametrize("droit", DROITS)
def test_chaque_depart_est_la_liquidation_que_le_python_simule_de_sa_carriere(
        saisies, droit):
    """Chaque départ du portage est ce que le Python simule de la carrière que
    le portage bâtit à cet âge (:func:`_liquidation_du_python`) : son mois, ses
    trimestres et ceux que le droit requiert, ce qui l'ouvre, et sa pension
    étage par étage, à un milliardième près, comme les témoins. Sous chaque
    état du droit ; et les droits contrefactuels ne datent pas comme celui qui
    s'applique le né en 1968, que les deux lois ont touché : sa première
    pension s'ouvre à soixante-quatre ans sous la loi de 2023 sans la
    suspension, à soixante-deux ans sous le droit au 31 août 2023
    (``tests/test_droits_contrefactuels.py``)."""
    ecarts: list[str] = []
    for nom, requete in REQUETES.items():
        for rang, depart in enumerate(_departs(nom, droit)):
            obtenu = {cle: valeur for cle, valeur in asdict(depart).items() if cle != "quoi"}
            _ecarts(obtenu, _liquidation_du_python(saisies, requete, depart, droit),
                    f"{nom}[{rang}]", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
    assert sum(len(_departs(nom, droit)) for nom in REQUETES) >= 15
    premier = _departs("trois_ages", droit)[0]
    assert premier.age == pytest.approx(
        {None: 63.75, "loi_2023_sans_suspension": 64.0, "au_31_aout_2023": 62.0}[droit])


def test_chaque_age_est_atteint_une_fois_dans_l_ordre_de_la_synthese():
    for droit in DROITS:
        for nom in REQUETES:
            departs = _departs(nom, droit)
            if not departs:
                continue
            reunis = [quoi for depart in departs for quoi in depart.quoi]
            assert tuple(reunis) == tuple(REGLES), (nom, droit)
            ages = [depart.age for depart in departs]
            assert ages == sorted(ages) and len(set(ages)) == len(ages), (nom, droit)


def test_les_ages_sont_ceux_que_le_droit_oppose(saisies):
    """Trois âges distincts : l'âge légal avec décote, le taux plein quand la
    durée est atteinte, soixante-sept ans ; chacun est l'âge que l'étape
    « ouvrir le droit » oppose à la carrière liquidée à cet âge."""
    requete = REQUETES["trois_ages"]
    actuel = saisies.simulateur(requete).scenario_actuel
    legal, plein, automatique = _departs("trois_ages")
    assert (legal.quoi, plein.quoi, automatique.quoi) == (
        ("legal",), ("taux_plein",), ("automatique",))

    def carriere(age):
        return saisies.carriere(_au_depart(requete, age))

    assert legal.age == pytest.approx(ouvrir.age_ouverture_droit(actuel, carriere(legal.age)))
    assert plein.age == pytest.approx(ouvrir.age_taux_plein_droit(actuel, carriere(plein.age)))
    assert automatique.age == pytest.approx(67.0)
    assert legal.trimestres < legal.trimestres_requis <= plein.trimestres
    assert legal.total < plein.total < automatique.total


def test_une_carriere_qui_ne_valide_plus_n_a_le_taux_plein_qu_a_l_age_d_annulation():
    """Née le 15 janvier 1966 et sans activité de 2026 à 2045, une carrière
    entrée en juillet 1983 a 42 × 4 + 2 = 170 trimestres — deux trimestres
    civils en 1983 —, 169 entrée en octobre, des 172 de sa génération, qui
    ouvre son droit à 63 ans et 3 mois (L. 161-17-2 et L. 161-17-3, après la
    suspension de la loi n° 2025-1403, article 105), et n'en gagne plus : elle
    n'a le taux plein qu'à l'âge d'annulation de la décote, 67 ans pour les
    nés depuis 1955 (L. 351-8, 1°), où il est aussi automatique. Le pilote
    datait sa durée comme si elle validait encore quatre trimestres par an
    (``ageTauxPleinDroit``), et s'arrêtait au bout de ses passes
    (``PASSES_LIQUIDATION``) : il la disait au taux plein, décotée, à 65 ans
    et 3 mois, et à 66 ans et 3 mois (action 138, étape 14)."""
    requetes = [{"naissance": "1966-01-15", "debut": debut,
                 "interruptions": "2026:2045:sans_activite"} for debut in ("1983-07", "1983-10")]
    for departs, trimestres in zip(_departs_du_portage(requetes), (170, 169)):
        assert [(depart.quoi, depart.age, depart.trimestres, depart.trimestres_requis)
                for depart in departs] == [
            (("legal",), pytest.approx(63.25), trimestres, 172),
            (("taux_plein", "automatique"), pytest.approx(67.0), trimestres, 172)], trimestres


def _departs_dits(requetes: list[dict], droit: str | None = None) -> list[list[tuple]]:
    """Ce que le portage dit de chaque départ de chaque requête : ce qu'il
    réunit, son âge, ses trimestres, ceux que le droit requiert, ce qui
    l'ouvre."""
    return [[(depart.quoi, depart.age, depart.trimestres, depart.trimestres_requis,
              depart.motif_ouverture) for depart in departs]
            for departs in _departs_du_portage(requetes, droit)]


def test_une_carriere_qui_ne_valide_plus_part_a_l_age_ou_la_carriere_longue_l_ouvre():
    """Né le 15 janvier 1966, entré en janvier 1982, à seize ans, et sans
    activité de 2025 à 2045, un salarié a 43 × 4 = 172 trimestres cotisés à la
    fin de 2024, ceux de sa génération. Il en a validé cinq avant la fin de
    l'année de ses dix-huit ans, non de ses seize — 1982 n'en compte que
    quatre — : la carrière longue lui ouvre son départ à 60 ans, au taux plein
    (L. 351-1-1 et D. 351-1-1, version du 1er septembre 2023), avant l'âge
    légal de 63 ans et 3 mois. Elle date sa durée cotisée comme s'il cotisait
    encore quatre trimestres par an (``CarriereLongue.agePropose``) : à tout
    âge passé 2024, elle la disait atteinte à cet âge même, et la descente du
    pilote, partie des 64 ans que la saisie demande, s'arrêtait à l'âge légal.
    Sous le droit au 31 août 2023, qui ne leur en requiert que 169, les deux
    carrières entrées en 1983 du test précédent ont de même leur durée cotisée
    à 60 ans, que leur début avant vingt ans leur ouvre (D. 351-1-1, rédaction
    du décret du 2 juillet 2012) : la descente s'arrêtait à 61 ans et 3 mois,
    au bout de ses passes, et à 62 ans, l'âge légal (action 138, étape 14)."""
    salarie = {"naissance": "1966-01-15", "debut": "1982-01",
               "interruptions": "2025:2045:sans_activite"}
    assert _departs_dits([salarie]) == [[
        (("legal", "taux_plein"), pytest.approx(60.0), 172, 172, "carriere_longue"),
        (("automatique",), pytest.approx(67.0), 172, 172, "age_legal")]]
    requetes = [{"naissance": "1966-01-15", "debut": debut,
                 "interruptions": "2026:2045:sans_activite"} for debut in ("1983-07", "1983-10")]
    assert _departs_dits(requetes, "au_31_aout_2023") == [[
        (("legal", "taux_plein"), pytest.approx(60.0), trimestres, 169, "carriere_longue"),
        (("automatique",), pytest.approx(67.0), trimestres, 169, "age_legal")]
        for trimestres in (170, 169)]


def test_un_depart_que_la_saisie_refuse_ne_tait_pas_l_estimation():
    """La saisie refuse un départ qui précède l'un de ses métiers. Chercher un
    départ plus précoce que l'âge légal ne fait pas taire le bloc d'une
    carrière qui n'en a pas : celle des trois âges, salariée cadre à compter de
    septembre 2031, six mois avant son âge légal, garde ses trois départs, aux
    mêmes âges et avec les mêmes trimestres — passer cadre ne change ni le
    régime de base ni la durée validée."""
    cadre = {**REQUETES["trois_ages"], "metier2_debut": "2031-09",
             "metier2_statut": "salarie_prive_cadre"}
    dits, attendus = _departs_dits([cadre, REQUETES["trois_ages"]])
    assert len(attendus) == 3
    assert dits == attendus


def test_la_carriere_longue_part_au_taux_plein_avant_l_age_legal(saisies):
    premier, *_ = _departs("carriere_longue")
    assert premier.quoi == ("legal", "taux_plein")
    assert premier.motif_ouverture == "carriere_longue"
    requete = REQUETES["carriere_longue"]
    actuel = saisies.simulateur(requete).scenario_actuel
    carriere = saisies.carriere(_au_depart(requete, premier.age))
    assert premier.age < min(ouvrir.age_ouverture(actuel, periode, carriere)
                             for _, periode in ouvrir.periodes_parcourues(actuel, carriere)[0])


def test_un_depart_anticipe_se_dit_par_ce_qui_l_ouvre(page):
    """La carrière longue et le handicap ouvrent le premier départ avant l'âge
    légal, au taux plein : la rangée le dit, et non « âge légal »."""
    for nom, mot in (("carriere_longue", "carrière longue"), ("handicap", "handicap")):
        premier, *_ = _departs(nom)
        assert premier.quoi == ("legal", "taux_plein"), nom
        assert premier.motif_ouverture == nom, nom
        assert f"{mot}, taux plein" in _bloc(page("/simuler", **REQUETES[nom])), nom


@pytest.mark.parametrize("nom", ["parti", "par_pension", "radiation", "metier_tardif"])
def test_sans_depart_a_choisir_le_bloc_se_tait(page, nom):
    """Qui est parti, qui saisit sa pension, dont la saisie date elle-même un
    départ, ou dont la carrière ne se bâtit pas à l'un des âges : rien à
    chiffrer, et la page calcule comme avant, sans le bloc ni un refus."""
    assert _departs(nom) == ()
    corps = page("/simuler", **REQUETES[nom])
    assert '<h2 id="estimation-officielle"' not in corps
    assert 'id="resultats"' in corps


def test_les_etages_font_la_pension_du_scenario_1_sans_le_minimum_vieillesse(saisies):
    """Chaque départ est la liquidation que la saisie ferait à cette date : ses
    étages et le minimum vieillesse font la pension du scénario 1, régimes
    provisionnés compris, en euros constants."""
    for nom in ("trois_ages", "fonctionnaire", "mere", "petit_salaire"):
        for depart in _departs(nom):
            comparaison = saisies.simuler(_au_depart(REQUETES[nom], depart.age))
            actuel = comparaison.actuel
            attendu = ((actuel.pension_annuelle + actuel.pension_hors_repartition)
                       * comparaison.coefficient_euros_constants)
            assert depart.total + depart.minimum_vieillesse == pytest.approx(attendu), nom
    fonctionnaire = _departs("fonctionnaire")
    assert all(set(d.etages) == {"integre", "additionnel"} for d in fonctionnaire)
    assert all(d.etages["additionnel"] > 0 for d in fonctionnaire)


def test_l_estimation_recopiee_voyage_dans_l_adresse_et_n_entre_dans_aucun_calcul():
    recopie = {**REQUETES["trois_ages"], "estimation_legal": "2500",
               "estimation_automatique": "3300.5"}
    saisie = saisie_du_portage(recopie)
    assert (saisie.estimation_legal, saisie.estimation_taux_plein,
            saisie.estimation_automatique) == (2500.0, None, 3300.5)
    adresse = dict(pair.split("=", 1) for pair in saisie.requete().split("&"))
    assert {nom: adresse.get(nom) for nom in module("saisie").CHAMPS_ESTIMATION} == {
        "estimation_legal": "2500", "estimation_taux_plein": None,
        "estimation_automatique": "3300.5"}
    assert _departs_du_portage([recopie]) == [_departs("trois_ages")]
    for valeur in ("0", "0.5", "-12"):
        with pytest.raises(ErreurSite, match=refus_de_la_saisie("estimation officielle")):
            saisie_du_portage({**REQUETES["trois_ages"], "estimation_taux_plein": valeur})


def _nombres(cellule: str) -> int:
    texte = re.sub(r"<[^>]+>", "", html.unescape(cellule))
    chiffres = re.sub(r"[^\d\-−]", "", texte.split("(")[0]).replace("−", "-")
    return int(chiffres)


def _bloc(corps: str) -> str:
    debut = corps.index('<h2 id="estimation-officielle"')
    return corps[debut:corps.index("</table>", debut)]


def test_la_page_montre_le_brut_par_etage_le_net_puis_l_ecart(page):
    requete = {**REQUETES["trois_ages"], "estimation_legal": "2500",
               "estimation_automatique": "3300"}
    bloc = _bloc(page("/simuler", **requete))
    departs, = _departs_du_portage([requete])
    entetes = re.findall(r'<th class="[^"]*" scope="col">([^<]*)</th>', bloc)
    assert entetes == ["Départ", "Base", "Complémentaire", "Total brut", "Net avant impôt",
                       "Votre estimation", "Écart"]
    rangees = re.findall(r'<tr><th[^>]*scope="row">(.*?)</th>(.*?)</tr>', bloc)
    assert len(rangees) == len(departs) == 3
    # Le net de chaque âge, à SA tranche : sous la présomption, son revenu
    # fiscal est fait de cette pension seule ; et 1 % de sa propre part
    # complémentaire aux deux derniers taux (action 138, étape 2).
    montants = montants_du_portage(requete, simuler=False)
    for (tete, cellules), depart, recopie in zip(rangees, departs, (2500, None, 3300)):
        valeurs = re.findall(r"<td[^>]*>(.*?)</td>", cellules)
        base, complementaire, total, net = (_nombres(v) for v in valeurs[:4])
        assert base + complementaire == total == round(depart.total / 12)
        assert 0 < depart.assiette_maladie < depart.total
        assert net == round(montants.net_d_un_depart(
            depart.total, depart.assiette_maladie, depart.minimum_vieillesse) / 12)
        assert 'form="simulateur"' in valeurs[4]
        assert f'name="estimation_{depart.quoi[0]}"' in valeurs[4]
        if recopie is None:
            assert valeurs[5] == "—"
        else:
            assert f'value="{recopie}"' in valeurs[4]
            assert _nombres(valeurs[5]) == round(depart.total / 12 - recopie)
    assert "avec décote" in rangees[0][0] and "taux plein automatique" in rangees[2][0]


def test_sans_estimation_recopiee_la_page_n_a_pas_de_colonne_d_ecart(page):
    corps = page("/simuler", **REQUETES["trois_ages"])
    assert "Écart" not in _bloc(corps)
    assert '<form class="carte" id="simulateur"' in corps
    assert '<h2 id="estimation-officielle"' not in page("/simuler", **REQUETES["parti"])


def test_chaque_depart_dit_ses_trimestres_comme_l_estimation_officielle(page):
    """« Mon estimation retraite » donne, à chaque âge, ses trimestres et son
    montant (registre, ``marel``, chantier 138.10) : chaque rangée dit la durée
    tous régimes du départ, enfants compris, et celle que sa génération
    requiert (L. 161-17-3). Le départ légal du né en mai 1968 entré à
    vingt-deux ans tombe sous la durée requise, d'où sa décote ; son taux plein
    vient au mois où la durée l'atteint (L. 351-1, R. 351-27) ; il la dépasse
    au taux plein automatique. La carrière longue part au taux plein, la durée
    atteinte ; la mère de trois enfants la dépasse dès l'âge légal."""
    for nom in ("trois_ages", "carriere_longue", "mere"):
        departs = _departs(nom)
        rangees = re.findall(r'<tr><th[^>]*scope="row">(.*?)</th>',
                             _bloc(page("/simuler", **REQUETES[nom])))
        assert len(rangees) == len(departs) >= 2, nom
        for tete, depart in zip(rangees, departs):
            texte = re.sub(r"[ \xa0]", " ", html.unescape(re.sub(r"<[^>]+>", " ", tete)))
            assert (f"{depart.trimestres} trimestres pour {depart.trimestres_requis} requis"
                    in texte), (nom, texte)
    tot, plein, automatique = _departs("trois_ages")
    assert tot.trimestres < tot.trimestres_requis == 172
    assert plein.trimestres == plein.trimestres_requis
    assert automatique.trimestres > automatique.trimestres_requis
    longue, _ = _departs("carriere_longue")
    assert longue.motif_ouverture == "carriere_longue"
    assert longue.trimestres >= longue.trimestres_requis
    mere, _ = _departs("mere")
    assert mere.trimestres > mere.trimestres_requis


def _ages_de_depart(corps: str) -> str:
    debut = corps.index("Partir plus tôt ou plus tard")
    return corps[debut:corps.index("</details>", debut)]


def test_plusieurs_ages_de_depart_cote_a_cote(saisies, page):
    """Le dépliant « Partir plus tôt ou plus tard » (action 138, étape 10) :
    la carrière de la saisie liquidée chaque année, de l'âge d'ouverture au
    taux plein automatique, et ses pensions nettes sous les quatre systèmes,
    puis après impôt (étape 5), celles que le portage tire de
    ``balayageDeLEstimation`` (``contexte.js``), sous l'impôt d'une personne
    seule que la bulle dit ; rien pour qui n'a pas de départ à chiffrer. Le
    cycle de vie et le pilote de l'estimation n'ont qu'un exemplaire, le
    portage (action 161) : le premier et le dernier âge se confrontent au
    droit du Python, l'âge d'ouverture et celui du taux plein automatique que
    l'étape « ouvrir le droit » oppose à la carrière du pont liquidée à cet
    âge. La requête date la naissance au jour : aucune présomption n'y entre,
    et la saisie du portage se lit sans leur table."""
    requete = REQUETES["trois_ages"]
    saisie = module("saisie").Saisie.depuis_requete(requete, False, None)
    balayage = site().contexte.balayage_de_l_estimation(saisie)
    departs = [un.depart for un in balayage]
    actuel = saisies.simulateur(requete).scenario_actuel
    for quoi, age in (("legal", departs[0].age), ("automatique", departs[-1].age)):
        assert REGLES[quoi](actuel, saisies.carriere(_au_depart(requete, age))) == pytest.approx(
            age, abs=1e-9), quoi
    bloc = _ages_de_depart(page("/simuler", **REQUETES["trois_ages"]))
    tableau = bloc[:bloc.index("</table>")]
    rangees = re.findall(r'<tr><th[^>]*scope="row">(.*?)</th>(.*?)</tr>', tableau)
    assert len(rangees) == len(departs) >= 2
    systemes = ("actuel", "notionnel_retroactif", "notionnel_retroactif_employeur",
                "notionnel_liberal")
    apres = bloc[bloc.index("La pension après impôt du premier mois"):]
    rangees_apres = re.findall(r'<tr><th[^>]*scope="row">(.*?)</th>(.*?)</tr>',
                               apres[:apres.index("</table>")])
    assert len(rangees_apres) == len(departs)
    for (tete, cellules), (tete_apres, cellules_apres), un in zip(
            rangees, rangees_apres, balayage):
        depart = un.depart
        assert f"en {depart.annee}" in tete and f"en {depart.annee}" in tete_apres
        for lues, pensions in ((cellules, depart.pensions_nettes),
                               (cellules_apres, depart.pensions_apres_impot)):
            valeurs = [_nombres(v) for v in re.findall(r"<td[^>]*>(.*?)</td>", lues)]
            attendus = [round(un.comparaison.en_euros_constants(
                pensions[scenario], scenario) / 12) for scenario in systemes]
            assert valeurs == attendus
    assert any(depart.pensions_apres_impot["actuel"] < depart.pensions_nettes["actuel"]
               for depart in departs)
    assert "une personne seule, sans enfant à charge" in bloc
    assert bloc.count("<table") == 4 and "rendement réel" in bloc
    assert "Partir plus tôt ou plus tard" not in page("/simuler", **REQUETES["parti"])


def _avec_ou_sans(corps: str) -> str:
    debut = corps.index("Avec ou sans la réforme de 2023")
    return corps[debut:corps.index("</details>", debut)]


def test_les_departs_sous_trois_etats_du_droit(page):
    """Le dépliant « Avec ou sans la réforme de 2023 » (action 138, étape 10) :
    au plus tôt et au taux plein, l'âge, le mois et le net du premier mois de
    la carrière saisie sous le droit qui s'applique, sous la loi de 2023 sans
    la suspension et sous le droit au 31 août 2023, avec l'écart au premier,
    et la durée requise : ceux que le portage date sous chaque droit, que le
    droit du Python confronte. Le né en mai 1968 part au plus tôt à 63 ans
    et 9 mois, 3 mois plus tard sans la suspension, 1 an et 9 mois plus tôt
    sans la réforme ; rien pour qui n'a pas de départ à chiffrer."""
    from retraite_notionnelle.calendrier import formater_age

    bloc = _avec_ou_sans(page("/simuler", **REQUETES["trois_ages"]))
    entetes = re.findall(r'<th class="[^"]*" scope="col">([^<]*)</th>', bloc)
    assert entetes == ["État du droit", "Au plus tôt", "Net au plus tôt", "Au taux plein",
                       "Net au taux plein", "Durée requise"]
    rangees = re.findall(r'<tr><th[^>]*scope="row">(.*?)</th>(.*?)</tr>', bloc)
    assert len(rangees) == 3
    montants = montants_du_portage(REQUETES["trois_ages"], simuler=False)

    def net(depart) -> int:
        return round(montants.net_d_un_depart(
            depart.total, depart.assiette_maladie, depart.minimum_vieillesse) / 12)

    for (_, cellules), droit in zip(rangees, DROITS):
        departs = _departs("trois_ages", droit)
        tot = next(depart for depart in departs if "legal" in depart.quoi)
        plein = next(depart for depart in departs if "taux_plein" in depart.quoi)
        valeurs = re.findall(r"<td[^>]*>(.*?)</td>", cellules)
        assert valeurs[0].startswith(formater_age(tot.age)), droit
        assert valeurs[2].startswith(formater_age(plein.age)), droit
        assert [_nombres(valeurs[1]), _nombres(valeurs[3]), _nombres(valeurs[4])] == [
            net(tot), net(plein), tot.trimestres_requis], droit
    premiers = [re.findall(r"<td[^>]*>(.*?)</td>", cellules)[0] for _, cellules in rangees]
    assert premiers[0].startswith("63 ans et 9 mois")
    assert premiers[1].startswith("64 ans") and "3 mois plus tard" in premiers[1]
    assert premiers[2].startswith("62 ans") and "1 an et 9 mois plus tôt" in premiers[2]
    assert [html.unescape(tete) for tete, _ in rangees] == [
        "Le droit qui s'applique", "La loi de 2023, sans la suspension",
        "Le droit du 31 août 2023"]
    assert "Avec ou sans la réforme de 2023" not in page("/simuler", **REQUETES["parti"])
