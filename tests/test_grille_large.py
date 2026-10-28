"""La grille élargie de la page Coût : ses parts viennent des sources, et sa mécanique ne triche pas.

`scripts/grille_large.py` dit ce que les treize cas types déplacent (action
136, étape 6). La mesure entière prend plusieurs minutes et ne se rejoue pas
ici ; ce qui se tient ici est ce qui la rend lisible : chaque déclinaison
reçoit la part que l'EIR ou l'INSEE lui donne, et la grille du dépôt réécrite
en parts redonne la page. L'ASPA que la page comptait aux premières
générations, et que la mesure avait trouvée, n'y est plus depuis le
11 octobre 2026 : `test_cout.py` le tient
(`test_la_page_ne_sert_pas_le_minimum_vieillesse`).
"""

from __future__ import annotations

import math
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from retraite_notionnelle import cout as C
from retraite_notionnelle import memoire
from retraite_notionnelle.castypes import GRILLE_DU_COUT, poids_effectifs
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.simulateur import Simulateur

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import grille_large as G  # noqa: E402


@pytest.fixture(scope="module")
def parametres():
    return Parametres()


@pytest.fixture(scope="module")
def simulateur(parametres):
    return Simulateur(parametres)


@pytest.fixture(scope="module")
def source(parametres):
    return G.eir(parametres.racine_donnees)


@pytest.fixture(scope="module")
def points(parametres):
    return G.multiplicateurs(G.centiles(parametres.racine_donnees)[1])


@pytest.fixture
def sans_le_reperage_des_decotes(monkeypatch):
    """La population sans le repérage des carrières qui peuvent décoter
    (``DECOTE_DES_CARRIERES_QUI_LE_PEUVENT``), pour les tests qui la
    reconstruisent sous ``monkeypatch`` sans regarder la décote : le repérage
    demande au droit une vingtaine de secondes à chaque construction, que la
    mémoire des calculs, muette sous ``monkeypatch``, ne garde pas. Il ne
    change que les parts des jumelles, jamais une carrière ni son poids."""
    monkeypatch.setattr(G, "DECOTE_DES_CARRIERES_QUI_LE_PEUVENT", False)


def _poids(variantes, effectifs, annee):
    cas_types, retraites, _ = G.pseudo(variantes)
    return poids_effectifs(G.EffectifsRepartis(effectifs, retraites), annee, cas_types)


def _par(variantes, poids, cle):
    sortie: dict = {}
    for v in variantes:
        sortie[cle(v)] = sortie.get(cle(v), 0.0) + poids[v.cas.code]
    return sortie


def test_la_grille_du_depot_en_parts_redonne_les_poids_de_la_page(simulateur):
    """Les pseudo-caisses ne changent rien aux poids : chaque cas type reçoit,
    année par année et des deux côtés du bilan, ce que ``poids_effectifs`` lui
    donne sur ses caisses réelles."""
    variantes = G.reference()
    cas_types, retraites, cotisants = G.pseudo(variantes)
    for effectifs, parts in ((simulateur.effectifs, retraites),
                             (simulateur.cotisants, cotisants)):
        reparti = G.EffectifsRepartis(effectifs, parts)
        for annee in (1980, 2004, 2020, 2024, 2050):
            attendu = poids_effectifs(effectifs, annee, GRILLE_DU_COUT)
            obtenu = poids_effectifs(reparti, annee, cas_types)
            for cas in GRILLE_DU_COUT:
                assert obtenu[cas.code] == pytest.approx(attendu[cas.code], abs=1e-12)


def test_chaque_groupe_recoit_sa_part_de_personnes(simulateur, source):
    """L'année de l'enquête, chaque groupe de régime principal pèse la part de
    retraités que l'EIR lui donne, et la Cnav ne compte plus les contractuels
    qu'elle comptait aussi. Les cotisants, eux, ne bougent pas."""
    variantes = G.grille("personnes", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    groupes = _par(variantes, poids, lambda v: v.groupe)
    for groupe, part in G.parts_personnes(source).items():
        assert groupes[groupe] == pytest.approx(part, abs=1e-12), groupe
    moyen = next(v for v in variantes if v.cas.code == "salaire_moyen")
    assert moyen.retraites[0][0] == "cnav"
    assert ("ircantec", -moyen.retraites[0][1]) in moyen.retraites
    assert moyen.cotisants == next(v for v in G.reference()
                                   if v.cas.code == "salaire_moyen").cotisants


def test_les_polypensionnes_sont_dans_la_proportion_de_l_eir(simulateur, source):
    """Dans chaque groupe qui en a, la part des polypensionnés est celle de
    l'EIR, et leur carrière commence par dix années de salariat du privé. Le
    militaire et le régime général n'en ont pas : l'un parce que sa pension
    s'ouvre à une durée de services, l'autre parce que l'EIR ne dit pas son
    second régime."""
    variantes = G.grille("melees", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    groupes = _par(variantes, poids, lambda v: v.groupe)
    polys = _par(variantes, poids, lambda v: (v.groupe, v.poly))
    for groupe, part in G.parts_poly(source).items():
        assert polys[(groupe, True)] / groupes[groupe] == pytest.approx(part, abs=1e-12)
    for groupe in set(G.GROUPES) - set(G.GROUPES_MELES):
        assert (groupe, True) not in polys, groupe
    for v in variantes:
        if v.poly:
            assert v.cas.avant == ((G.affiliation_privee(v.cas), G.ANNEES_PRIVE),)


def test_les_femmes_et_les_carrieres_courtes_suivent_l_eir(simulateur, source):
    """Chaque groupe a la part de femmes que l'EIR lui donne ; hors des
    régimes statutaires, chaque sexe a, tranche par tranche, la part de durées
    validées hors majorations que l'EIR publie ; les régimes statutaires
    gardent leurs carrières."""
    variantes = G.grille("interruptions", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    groupes = _par(variantes, poids, lambda v: v.groupe)
    femmes = _par(variantes, poids, lambda v: (v.groupe, v.cas.sexe))
    for groupe, part in G.parts_femmes(source).items():
        assert femmes[(groupe, "F")] / groupes[groupe] == pytest.approx(part, abs=1e-12)
    tranche = {cible: nom for nom, cible in G.TRANCHES}
    for sexe in ("F", "H"):
        eligibles = [v for v in variantes
                     if v.groupe in G.GROUPES_INTERROMPUS and v.cas.sexe == sexe]
        masse = sum(poids[v.cas.code] for v in eligibles)
        for nom, part in G.parts_tranches(source, sexe).items():
            dedans = sum(poids[v.cas.code] for v in eligibles
                         if tranche.get(v.duree if v.duree in tranche else None) == nom)
            assert dedans / masse == pytest.approx(part, abs=1e-12), (sexe, nom)
    for v in variantes:
        if v.groupe not in G.GROUPES_INTERROMPUS:
            assert v.duree is None and v.assimilees == 0, v.cas.code


def test_une_carriere_courte_s_arrete_a_la_duree_de_sa_tranche(simulateur, source):
    """La carrière d'une tranche courte valide sa durée — travail et périodes
    assimilées — puis reste inactive jusqu'au départ, que le pilote date au
    taux plein."""
    variantes = G.grille("interruptions", simulateur.effectifs, source, ())
    courte = next(v for v in variantes if v.cas.code == "salaire_moyen~h~20_30")
    assert courte.duree == 25 and courte.assimilees == round(
        G.part_assimilee(source, "H") * 25)
    carriere = courte.cas.construire(simulateur, 1980)
    types = [ligne.type_periode for ligne in carriere.lignes]
    assert types.count("emploi") + types.count("chomage_indemnise") == 25
    assert types.count("chomage_indemnise") == courte.assimilees
    assert set(types[25:]) == {"inactivite"}


def test_les_salaires_gardent_la_moyenne_et_passent_la_grille_du_depot(source, simulateur,
                                                                      points):
    """Chaque cas type garde son salaire moyen, la dispersion seule s'ajoute ;
    et la grille élargie passe enfin les deux fois et demie du salaire moyen
    que la grille du dépôt ne dépassait pas (`docs/limites.md`, § 5)."""
    assert sum(part for _, part, _ in points) == pytest.approx(1.0)
    assert sum(part * facteur for _, part, facteur in points) == pytest.approx(1.0)
    variantes = G.grille("salaires", simulateur.effectifs, source, points)
    for cas in GRILLE_DU_COUT:
        siens = [v for v in variantes if v.cas.code.rsplit("~", 1)[0] == cas.code]
        assert len(siens) == len(G.CENTILES)
        poids = sum(v.retraites[0][1] for v in siens)
        moyenne = sum(v.retraites[0][1] * v.cas.niveau_salaire for v in siens) / poids
        assert moyenne == pytest.approx(cas.niveau_salaire)
    assert max(v.cas.niveau_salaire for v in variantes) > 2.5 * 3


def test_la_population_garde_les_parts_de_l_eir(simulateur, source):
    """La population remplace les quatre cas types de la Cnav par le gabarit
    du salariat privé sans rien changer aux poids : chaque groupe garde sa
    part de personnes et sa part de femmes."""
    variantes = G.grille("population", simulateur.effectifs, source, ())
    assert not any(v.cas.code.split("~", 1)[0] in G.SALARIAT_PRIVE for v in variantes)
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    groupes = _par(variantes, poids, lambda v: v.groupe)
    femmes = _par(variantes, poids, lambda v: (v.groupe, v.cas.sexe))
    for groupe, part in G.parts_personnes(source).items():
        assert groupes[groupe] == pytest.approx(part, abs=1e-12), groupe
    for groupe, part in G.parts_femmes(source).items():
        assert femmes[(groupe, "F")] / groupes[groupe] == pytest.approx(part, abs=1e-12)


def test_la_population_rend_les_contractuels_au_salariat(simulateur, source, parametres):
    """Sous ``CONTRACTUELS_AU_SALARIAT``, la population n'a plus de
    contractuel, et la Cnav garde ceux qu'elle compte aussi : l'Ircantec ne
    sert à ses retraités de 2023 que 161 € par mois en moyenne, le quart de ce
    qu'en liquide un contractuel de toute une carrière."""
    assert G.CONTRACTUELS_AU_SALARIAT
    variantes = G.grille("population", simulateur.effectifs, source, ())
    assert not any(v.cas.code.startswith("contractuel_public") for v in variantes)
    gabarit = next(v for v in variantes if v.cas.code.startswith(f"{G.GABARIT}~"))
    assert all(caisse != "ircantec" for caisse, _ in gabarit.retraites)
    depense = next(float(l["depenses_meur"]) for l in G._lire_macro(
        parametres.racine_donnees, "depenses_retraite_regimes.csv")
        if l["annee"] == "2023" and l["regime"] == "ircantec")
    mensuelle = depense * 1e6 / simulateur.effectifs.effectif("ircantec", 2023) / 12
    assert mensuelle == pytest.approx(161, abs=0.5)


def test_le_salariat_prive_a_les_salaires_de_son_sexe_et_de_son_temps(simulateur, source,
                                                                     parametres):
    """Au salariat privé, chaque sexe a, génération par génération, le salaire
    moyen que l'INSEE lui donne l'année de ses quarante-cinq ans ; les trois
    centiles du haut sont cadres ; la part du temps partiel est, sexe par
    sexe, la moyenne de celle des 25-49 ans."""
    donnees = G.donnees_population(parametres.racine_donnees)
    variantes = G.grille("population", simulateur.effectifs, source, ())
    gabarit = [v for v in variantes if v.cas.code.startswith(f"{G.GABARIT}~")]
    lignes = G._lire_macro(parametres.racine_donnees, "dispersion_salaires_sexe.csv")
    moyennes = {(int(l["annee"]), l["sexe"]): float(l["salaire_relatif"])
                for l in lignes if l["centile"] == "moyenne"}
    for sexe in ("F", "H"):
        siens = [v for v in gabarit if v.cas.sexe == sexe]
        poids = sum(v.retraites[0][1] for v in siens)
        for generation in (1906, 1955, 1979):
            moyenne = sum(v.retraites[0][1] * v.cas.niveau_de(generation)
                          for v in siens) / poids
            assert moyenne == pytest.approx(moyennes[(generation + G.AGE_DU_RANG, sexe)])
        partiels = sum(v.retraites[0][1] for v in siens if v.cas.ages_partiel) / poids
        assert partiels == pytest.approx(donnees.parts_partiel[sexe])
        cadres = sum(v.retraites[0][1] for v in siens
                     if v.cas.affiliation == "salarie_prive_cadre") / poids
        assert cadres == pytest.approx(0.175)
    assert moyennes[(2000, "F")] < moyennes[(2000, "H")]


def test_le_temps_partiel_reduit_le_revenu_de_25_ans_au_depart(simulateur, source):
    """Une carrière à temps partiel est, de 25 ans à son départ, celle de son
    jumeau à temps complet à la quotité de sa génération, et la même avant :
    sous ``PARTIEL_JUSQU_AU_DEPART``, les années d'après cinquante ans
    n'entrent plus entières dans son salaire annuel moyen."""
    assert G.PARTIEL_JUSQU_AU_DEPART
    variantes = G.grille("population", simulateur.effectifs, source, ())
    partiel = next(v for v in variantes
                   if v.cas.code == f"{G.GABARIT}~f~40_plus~p50~partiel").cas
    complet = next(v for v in variantes if v.cas.code == f"{G.GABARIT}~f~40_plus~p50").cas
    generation = 1960
    quotite = G._par_generation(partiel.quotites, generation, 1.0)
    assert 0.5 < quotite < 0.7
    ages = 62
    revenus = {ligne.annee: ligne.revenu
               for ligne in partiel.carriere_a(simulateur, generation, ages).lignes}
    pleins = {ligne.annee: ligne.revenu
              for ligne in complet.carriere_a(simulateur, generation, ages).lignes}
    for annee in (generation + 25, generation + 37, generation + 49, generation + 50,
                  generation + 61):
        assert revenus[annee] == pytest.approx(pleins[annee] * quotite)
    assert revenus[generation + 24] == pytest.approx(pleins[generation + 24])


def test_une_carriere_resserre_la_coupe_sans_toucher_a_sa_moyenne():
    """D'une coupe à une carrière, chaque écart au centre du logarithme est
    ramené à ``DISPERSION_DE_CARRIERE`` fois le sien, et la moyenne
    discrétisée reste celle qu'on demande."""
    relatifs = {"p10": 0.5, "p25": 0.65, "p50": 0.82, "p75": 1.12, "p90": 1.6,
                "p95": 2.05, "p99": 3.7}
    resserres = G.resserrer(relatifs, 0.9)
    assert sum(resserres[n] * part for n, part in G.CENTILES) == pytest.approx(0.9)
    ecart = math.log(relatifs["p99"] / relatifs["p10"])
    assert math.log(resserres["p99"] / resserres["p10"]) == pytest.approx(
        G.DISPERSION_DE_CARRIERE * ecart)


def test_l_artisan_a_la_dispersion_des_revenus_des_non_salaries(simulateur, source,
                                                               parametres):
    """Sous ``INDEPENDANTS_A_LEUR_DISPERSION``, l'artisan de la population se
    décline aux sept centiles des revenus des non-salariés classiques de son
    sexe (fiche 1.6 de l'INSEE, 2022), et non plus des salaires : son premier
    décile se tient sous sa médiane de 640 € sur 2 760 pour une femme, de 660
    sur 3 000 pour un homme, son neuvième au-dessus de 7 630 et de 10 460,
    ramenés en carrière à la puissance ``DISPERSION_DE_CARRIERE`` ; son 99e
    centile prolonge le neuvième décile de la queue de leur ensemble (fiche
    1.3 : 27 950 € sur 9 320). Sa femme gagne un cinquième de moins que lui,
    comme dans la fiche (3 470 € et 4 360 en moyenne). Le libéral garde la
    dispersion des salaires de son sexe."""
    assert G.INDEPENDANTS_A_LEUR_DISPERSION
    variantes = G.grille("population", simulateur.effectifs, source, ())
    resserrement = G.DISPERSION_DE_CARRIERE

    def niveaux(prefixe: str) -> dict[str, float]:
        return {v.cas.code.rsplit("~", 1)[1]: v.cas.niveau_salaire
                for v in variantes if v.cas.code.startswith(prefixe)
                and v.cas.code.count("~") == prefixe.count("~")}

    publies = {"f": (640.0, 2760.0, 7630.0), "h": (660.0, 3000.0, 10460.0)}
    for sexe, (d1, mediane, d9) in publies.items():
        artisan = niveaux(f"artisan~{sexe}~40_plus~")
        assert set(artisan) == {nom for nom, _ in G.CENTILES}
        assert artisan["p10"] / artisan["p50"] == pytest.approx((d1 / mediane) ** resserrement)
        assert artisan["p90"] / artisan["p50"] == pytest.approx((d9 / mediane) ** resserrement)
        assert artisan["p99"] / artisan["p90"] == pytest.approx(
            (27950.0 / 9320.0) ** resserrement)
    moyennes = {sexe: sum(niveaux(f"artisan~{sexe}~40_plus~")[nom] * part
                          for nom, part in G.CENTILES) for sexe in publies}
    assert moyennes["f"] / moyennes["h"] == pytest.approx(3470.0 / 4360.0, abs=0.03)
    annee, _ = G.centiles(parametres.racine_donnees)
    salaires = {(l["sexe"], l["centile"]): float(l["salaire_relatif"])
                for l in G._lire_macro(parametres.racine_donnees,
                                       "dispersion_salaires_sexe.csv")
                if int(l["annee"]) == annee}
    liberal = niveaux("profession_liberale~mono~h~40_plus~")
    assert liberal["p10"] / liberal["p50"] == pytest.approx(
        (salaires[("H", "p10")] / salaires[("H", "p50")]) ** resserrement)


def test_l_artisan_a_la_part_de_femmes_des_anciens_artisans(simulateur, source):
    """Sous ``INDEPENDANTS_A_LEUR_PART_DE_FEMMES``, l'artisan de la population
    compte la part de femmes des anciens artisans et commerçants de l'EIR, 140
    milliers sur 500 (fiche 1.11 de l'INSEE), et non celle de son groupe, le
    régime général, où elles sont la majorité ; le salariat privé prend le
    reste, et le groupe garde sa part de femmes."""
    assert G.INDEPENDANTS_A_LEUR_PART_DE_FEMMES
    variantes = G.grille("population", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    artisans = _par([v for v in variantes if v.cas.code.startswith("artisan~")], poids,
                    lambda v: v.cas.sexe)
    assert artisans["F"] / (artisans["F"] + artisans["H"]) == pytest.approx(140 / 500)
    groupe = _par([v for v in variantes if v.groupe == "regime_general"], poids,
                  lambda v: v.cas.sexe)
    assert groupe["F"] / (groupe["F"] + groupe["H"]) == pytest.approx(
        G.parts_femmes(source)["regime_general"], abs=1e-12)


def test_un_temps_complet_ne_se_paie_pas_sous_le_smic(simulateur, source):
    """Le salariat privé dont le rang tombe sous le Smic, l'année où sa
    génération a quarante-cinq ans, est payé le Smic de chaque année ; au-dessus,
    son rang, et l'homme de la première sous-classe du bas l'est toujours."""
    variantes = G.grille("population", simulateur.effectifs, source, ())
    femme = next(v for v in variantes
                 if v.cas.code == f"{G.GABARIT}~f~40_plus~p10~bas1").cas
    homme = next(v for v in variantes
                 if v.cas.code == f"{G.GABARIT}~h~40_plus~p10~bas1").cas
    assert femme.au_smic(simulateur, 1940)
    assert not homme.au_smic(simulateur, 1940)
    carriere = femme.carriere_a(simulateur, 1940, 62)
    revenus = {ligne.annee: ligne.revenu for ligne in carriere.lignes}
    for annee in (1970, 1985):
        part = G._par_generation(femme.volumes, annee - 1940, 1.0)
        assert revenus[annee] == pytest.approx(simulateur.macro.smic_annuel(annee) * part)


def test_la_persistance_se_lit_dans_le_fichier_certifie(parametres):
    """Six ans après, la part des salariés au voisinage du Smic qui y sont
    encore, parmi ceux restés dans le champ : celle des 35-49 ans (15,6 sur
    62,3), au rapport de chaque sexe à l'ensemble (7,8 sur 58,0 pour les
    hommes, 13,3 sur 59,5 pour les femmes, 11,1 sur 58,9 en tout)."""
    persistance = G.persistance_a_six_ans(parametres.racine_donnees)
    milieu = (15.6 / 62.3) / (11.1 / 58.9)
    assert persistance["H"] == pytest.approx(7.8 / 58.0 * milieu)
    assert persistance["F"] == pytest.approx(13.3 / 59.5 * milieu)


def test_le_reste_de_la_classe_du_bas_se_decline_en_sous_classes_de_rang(
        simulateur, source, parametres):
    """Sous ``SOUS_CLASSES_DU_BAS``, le reste de la classe du bas du salariat
    privé — hors le Smic de toute une carrière — se décline en sous-classes de
    poids égal, de plus en plus payées, dont la moyenne est celle du reste ;
    leurs écarts sont ceux de la coupe, au logarithme la droite des deux
    premiers centiles, resserrés comme les classes."""
    assert G.SOUS_CLASSES_DU_BAS > 1
    k = G.SOUS_CLASSES_DU_BAS
    donnees = G.donnees_population(parametres.racine_donnees)
    variantes = G.grille("population", simulateur.effectifs, source, ())
    racine = f"{G.GABARIT}~f~40_plus~p10"
    sous = [next(v for v in variantes if v.cas.code == f"{racine}~bas{i + 1}")
            for i in range(k)]
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    assert len({round(poids[v.cas.code], 9) for v in sous}) == 1
    reste = dict(donnees.reste_du_bas["F"])
    for generation in (1950, 1965, 1975):
        niveaux = [v.cas.niveau_de(generation) for v in sous]
        assert niveaux == sorted(niveaux)
        assert sum(niveaux) / k == pytest.approx(reste[generation], rel=1e-12)
    valeurs = {(int(l["annee"]), l["sexe"], l["centile"]): float(l["salaire_relatif"])
               for l in G._lire_macro(parametres.racine_donnees,
                                      "dispersion_salaires_sexe.csv")}
    forme = G.forme_de(valeurs, "F", 1965 + G.AGE_DU_RANG)
    pente = math.log(valeurs[(forme, "F", "p25")] / valeurs[(forme, "F", "p10")]) / 0.15
    largeur = (G.CENTILES[0][1] - donnees.persistants["F"]) / k
    niveaux = [v.cas.niveau_de(1965) for v in sous]
    assert niveaux[-1] / niveaux[0] == pytest.approx(
        math.exp(G.DISPERSION_DE_CARRIERE * pente * largeur * (k - 1)), rel=1e-9)


def test_la_coupe_s_interpole_au_logarithme_entre_ses_centiles():
    centiles = {"p10": 0.5, "p25": 0.6, "p50": 0.8}
    assert G.part_de_la_coupe_sous(0.5, centiles) == pytest.approx(0.10)
    milieu = (0.5 * 0.6) ** 0.5
    assert G.part_de_la_coupe_sous(milieu, centiles) == pytest.approx(0.175)
    assert G.part_de_la_coupe_sous(0.7, centiles) == pytest.approx(
        0.25 + 0.25 * math.log(0.7 / 0.6) / math.log(0.8 / 0.6))
    assert G.part_de_la_coupe_sous(0.45, centiles) < 0.10
    assert G.part_de_la_coupe_sous(0.1, centiles) == 0.0


def test_une_part_du_bas_reste_au_smic_toute_la_carriere(simulateur, source, parametres):
    """Sous ``PERSISTANCE_SMIC``, une part du salariat privé de chaque sexe,
    prise dans sa classe du bas, est payée le Smic de chaque année ; le reste
    de la classe, décliné en sous-classes, en garde la moyenne."""
    donnees = G.donnees_population(parametres.racine_donnees)
    variantes = G.grille("population", simulateur.effectifs, source, ())
    for sexe in ("F", "H"):
        siens = [v for v in variantes
                 if v.cas.code.startswith(f"{G.GABARIT}~") and v.cas.sexe == sexe]
        poids = sum(v.retraites[0][1] for v in siens)
        persistants = sum(v.retraites[0][1] for v in siens if v.cas.persistante) / poids
        assert persistants == pytest.approx(donnees.persistants[sexe])
        assert 0.0 < persistants < G.CENTILES[0][1]
    assert donnees.persistants["F"] > donnees.persistants["H"]
    homme = next(v for v in variantes
                 if v.cas.code == f"{G.GABARIT}~h~40_plus~p10~smic").cas
    bas = [v.cas for v in variantes
           if v.cas.code.startswith(f"{G.GABARIT}~h~40_plus~p10~bas")
           and not v.cas.code.endswith("~partiel") and "~fragmente" not in v.cas.code
           and "~entree" not in v.cas.code and "~nature" not in v.cas.code
           and not v.surcote]
    assert len(bas) == G.SOUS_CLASSES_DU_BAS
    generation = 1960
    assert not any(cas.au_smic(simulateur, generation) for cas in bas)
    revenus = {ligne.annee: ligne.revenu
               for ligne in homme.carriere_a(simulateur, generation, 62).lignes}
    # 2000 à 2003 sont les années assimilées de la variante : sans salaire.
    for annee in (1985, 1990, 2015):
        part = G._par_generation(homme.volumes, annee - generation, 1.0)
        assert revenus[annee] == pytest.approx(simulateur.macro.smic_annuel(annee) * part)
    part, poids_du_bas = donnees.persistants["H"], G.CENTILES[0][1]
    reste = sum(cas.niveau_de(generation) for cas in bas) / len(bas)
    moyenne = (part * homme.niveau_de(generation)
               + (poids_du_bas - part) * reste) / poids_du_bas
    assert moyenne == pytest.approx(G._par_generation(
        donnees.niveaux[("H", "p10")], generation, None))


def test_le_volume_se_lit_dans_le_fichier_certifie(parametres):
    """La part de l'année travaillée à un âge : le volume de sa tranche,
    rapporté à celui de l'ensemble (0,77), fois celui d'un temps complet
    (0,85) ; le rang, le volume de sa catégorie rapporté à l'ensemble."""
    volumes, rangs = G.volumes_de_travail(parametres.racine_donnees)
    attendus = {0: 0.48, 25: 0.79, 40: 0.84, 50: 0.86, 55: 0.77}
    assert [age for age, _ in volumes] == sorted(attendus)
    for age, part in volumes:
        assert part == pytest.approx(attendus[age] / 0.77 * 0.85)
    assert rangs["p10"] == pytest.approx(0.68 / 0.77)
    assert rangs["p50"] == 1.0
    assert rangs["p99"] == pytest.approx(0.87 / 0.77)


def test_une_annee_d_activite_se_paie_a_la_part_travaillee_a_son_age(simulateur, source):
    """Sous ``VOLUME_DE_TRAVAIL``, le salariat privé est payé, chaque année
    d'activité, la part de l'année travaillée à son âge : son revenu est celui
    de la même carrière sans volume, fois cette part ; et le temps partiel
    s'y ajoute."""
    variantes = G.grille("population", simulateur.effectifs, source, ())
    cas = next(v for v in variantes if v.cas.code == f"{G.GABARIT}~h~40_plus~p50").cas
    partiel = next(v for v in variantes
                   if v.cas.code == f"{G.GABARIT}~f~40_plus~p50~partiel").cas
    assert cas.volumes
    generation, age_de_depart = 1960, 62
    for carriere in (cas, partiel):
        avec = {l.annee: l.revenu
                for l in carriere.carriere_a(simulateur, generation, age_de_depart).lignes}
        sans = {l.annee: l.revenu for l in replace(carriere, volumes=()).carriere_a(
            simulateur, generation, age_de_depart).lignes}
        for age in (22, 30, 45, 52, 58):
            part = G._par_generation(carriere.volumes, age, 1.0)
            assert part < 1.0
            assert avec[generation + age] == pytest.approx(sans[generation + age] * part), age


def test_chaque_classe_travaille_le_volume_de_sa_categorie(simulateur, source, parametres):
    """Sous ``VOLUME_SELON_LE_RANG``, chaque classe de centiles du salariat
    privé travaille, à chaque âge, la part de l'année de cet âge fois le volume
    de sa catégorie rapporté à l'ensemble, sans dépasser l'année entière : les
    employés au bas, sa part au Smic toute la carrière comprise, les cadres au
    haut, la classe médiane au volume de tous. Sous ``EMPLOI_FRAGMENTE``, une
    classe du bas le travaille en moyenne de ses carrières entières et
    fragmentées, à leurs poids."""
    assert G.VOLUME_SELON_LE_RANG and G.EMPLOI_FRAGMENTE
    volumes, rangs = G.volumes_de_travail(parametres.racine_donnees)
    variantes = G.grille("population", simulateur.effectifs, source, ())
    par_code = {v.cas.code: v for v in variantes}
    for classe, nom in (("p10~bas1", "p10"), ("p10~smic", "p10"), ("p25", "p25"),
                        ("p50", "p50"), ("p99", "p99")):
        code = f"{G.GABARIT}~h~40_plus~{classe}"
        lot = [par_code[c] for c in (code, f"{code}~fragmente") if c in par_code]
        assert len(lot) == (2 if rangs[nom] < 1.0 else 1), classe
        poids = [v.retraites[0][1] for v in lot]
        for i, (age, part) in enumerate(volumes):
            moyenne = sum(p * v.cas.volumes[i][1] for p, v in zip(poids, lot)) / sum(poids)
            assert all(v.cas.volumes[i][0] == age for v in lot)
            assert moyenne == pytest.approx(min(1.0, part * rangs[nom])), classe
    assert rangs["p10"] < rangs["p25"] < 1.0 < rangs["p99"]
    assert max(part for _, part in par_code[f"{G.GABARIT}~h~40_plus~p99"].cas.volumes) == 1.0


def test_l_emploi_fragmente_pese_sur_une_part_du_bas(simulateur, source, parametres):
    """Sous ``EMPLOI_FRAGMENTE``, le volume relatif d'une carrière fragmentée
    est celui des salariés à bas revenu salarial, rapporté à celui de tous, en
    moyenne de leurs centiles (748 heures pour 1 536) ; les carrières
    fragmentées font 22,8 % de la classe des employés, 10,1 % de celle des
    ouvriers, et le reste de ces classes travaille le volume de l'ensemble."""
    fragmente = G.volume_fragmente(parametres.racine_donnees)
    assert fragmente == pytest.approx(748.09 / 1536.42, abs=1e-4)
    volumes, rangs = G.volumes_de_travail(parametres.racine_donnees)
    par_code = {v.cas.code: v for v in G.grille("population", simulateur.effectifs,
                                                 source, ())}
    for classe, part in (("p10~bas2", 0.228), ("p25", 0.101)):
        code = f"{G.GABARIT}~f~40_plus~{classe}"
        entiere, reduite = par_code[code], par_code[f"{code}~fragmente"]
        poids = reduite.retraites[0][1] / (entiere.retraites[0][1] + reduite.retraites[0][1])
        assert poids == pytest.approx(part, abs=1e-3)
        assert entiere.cas.volumes == tuple((age, min(1.0, a)) for age, a in volumes)
        assert reduite.cas.volumes == tuple((age, a * fragmente) for age, a in volumes)
    assert f"{G.GABARIT}~f~40_plus~p50~fragmente" not in par_code


def test_les_carrieres_pleines_entrent_selon_leur_generation(simulateur, source, parametres):
    """Sous ``ENTREE_SELON_LA_GENERATION``, la carrière pleine du salariat privé
    commence la durée des carrières pleines avant l'âge légal de sa génération :
    44 années pour les retraités de 2020, que l'EIR donne aux deux sexes ; à
    16 ans pour la génération 1945, partie à 60 ans ; à 21 ans, l'entrée du
    gabarit, pour celles qui partent à 64 ans. Sa part au Smic toute la
    carrière la suit ; les carrières courtes gardent l'entrée du gabarit."""
    assert G.ENTREE_SELON_LA_GENERATION
    durees = G.durees_pleines(parametres.racine_donnees)
    for sexe in ("F", "H"):
        assert G._par_generation(durees[sexe], 1950, 0.0) == pytest.approx(44.0, abs=0.2)
    par_code = {v.cas.code: v.cas for v in G.grille("population", simulateur.effectifs,
                                                     source, ())}
    pleine = par_code[f"{G.GABARIT}~h~40_plus~p50"]
    assert pleine.debut_de(1945) == 16.0
    assert pleine.debut_de(1980) == 21.0
    assert par_code[f"{G.GABARIT}~h~40_plus~p10~smic"].debut_de(1945) == 16.0
    assert par_code[f"{G.GABARIT}~h~30_40~p50"].debut_de(1945) == 21
    lignes = pleine.carriere_a(simulateur, 1945, 60).lignes
    assert min(l.annee for l in lignes if l.type_periode == "emploi") == 1945 + 16


def test_l_age_du_premier_trimestre_se_lit_dans_le_fichier_certifie(parametres):
    """L'âge où une génération cotise le premier trimestre d'un rang : le
    premier âge où la part des affiliés d'avant 23 ans qui ont cotisé un
    trimestre, rapportée à celle de 23 ans, atteint ce rang. Les hommes nés en
    1950 en ont cotisé un à 16 ans pour 38,2 sur 96,1, 39,8 % : les deux
    premiers cinquièmes, aux rangs 0,1 et 0,3 ; le troisième, au rang 0,5, à
    17 ans (50,1) ; le quatrième à 19 ans (72,3, 75,2 % ; 62,5 à 18 ans), le
    dernier à 22 (90,9, 94,6 % ; 84,8 à 21). Entre deux générations de
    l'échantillon, les parts s'interpolent : nés en 1955, la moitié des nés en
    1954 et de ceux de 1956 — 27,4 sur 96,05 à 16 ans, 50,9 à 17, 68,8 à 18,
    84,85 à 20, 89,5 à 21."""
    parts = G.premiers_trimestres(parametres.racine_donnees)
    assert parts["H"][1950][16] == 38.2
    assert parts["H"][1950][23] == 96.1
    rangs = (0.1, 0.3, 0.5, 0.7, 0.9)
    assert [G.age_du_premier_trimestre(parts["H"], 1950, rang) for rang in rangs] == [
        16, 16, 17, 19, 22]
    assert [G.age_du_premier_trimestre(parts["H"], 1955, rang) for rang in rangs] == [
        16, 17, 17, 18, 21]


@pytest.mark.usefixtures("sans_le_reperage_des_decotes")
def test_les_carrieres_pleines_entrent_au_premier_trimestre_de_leur_cinquieme(
        simulateur, source, monkeypatch):
    """Sous ``ENTREE_AU_PREMIER_TRIMESTRE``, chaque carrière pleine du
    salariat privé, hors des départs avec surcote, se décline en cinq
    cinquièmes, rangés par l'âge où leur génération cotise son premier
    trimestre ; chacun entre à cet âge, ou à celui de la onzième version s'il
    vient plus tard. Les hommes nés en 1950 entrent à 16 ans pour deux
    cinquièmes, à 17, 19 et 22 ans pour un chacun ; nés en 1955, à 17 ans pour
    trois cinquièmes — la onzième version les y faisait tous entrer —, à 18 et
    à 21 ; nés en 1980, à 21 ans, l'entrée du gabarit, pour quatre, à 22 pour
    le dernier. Les cinquièmes qui entrent au même âge à chaque génération
    n'en font qu'un, sous le code de la carrière ; ceux des hommes se
    déclinent en leurs classes de nature, « ~nature1 »
    (``NATURES_SELON_LA_GENERATION``) ; la carrière garde son poids ; les
    départs avec surcote et les carrières courtes, leur entrée."""
    assert G.ENTREE_AU_PREMIER_TRIMESTRE
    variantes = G.grille("population", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    pleine = f"{G.GABARIT}~h~40_plus~p50"

    def cinquieme(v) -> str:
        return v.cas.code.split("~nature")[0]

    classes = [v for v in variantes
               if cinquieme(v) == pleine or cinquieme(v).startswith(f"{pleine}~entree")]
    assert sorted({cinquieme(v) for v in classes}) == [
        pleine, f"{pleine}~entree3", f"{pleine}~entree4", f"{pleine}~entree5"]
    total = sum(poids[v.cas.code] for v in classes)

    def repartition(generation: int) -> dict[float, float]:
        sortie: dict[float, float] = {}
        for v in classes:
            age = v.cas.debut_de(generation)
            sortie[age] = sortie.get(age, 0.0) + poids[v.cas.code] / total
        return sortie

    assert repartition(1950) == pytest.approx({16.0: 0.4, 17.0: 0.2, 19.0: 0.2, 22.0: 0.2})
    assert repartition(1955) == pytest.approx({17.0: 0.6, 18.0: 0.2, 21.0: 0.2})
    assert repartition(1980) == pytest.approx({21.0: 0.8, 22.0: 0.2})
    par_code = {v.cas.code: v.cas for v in variantes}
    surcotee = next(code for code in par_code if code.startswith(f"{pleine}~surcote"))
    assert par_code[surcotee].debut_de(1950) == 16.0
    assert par_code[surcotee].debut_de(1955) == 17.0
    assert par_code[f"{G.GABARIT}~h~30_40~p50"].debut_de(1950) == 21
    monkeypatch.setattr(G, "ENTREE_AU_PREMIER_TRIMESTRE", False)
    avant = G.grille("population", simulateur.effectifs, source, ())
    assert _poids(avant, simulateur.effectifs, source.millesime)[pleine] == pytest.approx(total)


def test_une_carriere_pleine_entree_tard_ne_part_pas_en_carriere_longue(simulateur, source):
    """L'homme né en 1955 d'une carrière pleine du salariat privé dont le
    cinquième n'a cotisé son premier trimestre qu'à 21 ans ne remplit pas la
    condition d'entrée de la carrière longue — cinq trimestres cotisés à la
    fin de l'année de ses 20 ans (D. 351-1-1) — : son service national, à
    20 ans, est validé sans être cotisé. Il part à 62 ans, l'âge légal de sa
    génération, au taux plein : il a validé les 166 trimestres de sa
    génération à 61 ans et demi, de 20 ans à 61 ans et demi. Le premier
    cinquième, entré à 17 ans, part avant 62 ans en carrière longue."""
    variantes = G.grille("population", simulateur.effectifs, source, ())
    projection = simulateur.pour_la_projection()
    par_code = {v.cas.code: v.cas for v in variantes}
    pleine = f"{G.GABARIT}~h~40_plus~p50"
    age, condition = G.condition_au_depart(projection, par_code[pleine], 1955)
    assert condition == "carriere_longue"
    assert age < 62.0
    assert G.condition_au_depart(projection, par_code[f"{pleine}~entree5"], 1955) == (
        pytest.approx(62.0), "taux_plein_autre")


def test_le_premier_trimestre_valide_precede_le_premier_cotise(parametres):
    """La part des affiliés d'avant 23 ans qui ont VALIDÉ un trimestre à la fin
    de l'année de chaque âge (``premier_trimestre.csv``) passe celle de ceux
    qui en ont cotisé un de ce qu'un affilié valide sans cotiser : le service
    national, pour les hommes. Nés en 1950, 93,2 % avaient validé un trimestre
    à 21 ans, sur 99,2 à 23 ans, 94,0 % ; 84,8 % en avaient cotisé un, sur
    96,1, 88,2 %. Au rang 0,9 du dernier cinquième, le premier trimestre
    validé tombe donc à 21 ans (85,6 à 20 ans, 86,3 %), le premier cotisé à
    22 ; les quatre autres rangs valident et cotisent au même âge. Nés en
    1946, le dernier valide à 20 ans (91,0 sur 99,5, 91,5 %) et cotise à 22
    (83,9 sur 95,7 à 21 ans, 87,7 % ; 90,8 à 22)."""
    valides = G.premiers_trimestres(parametres.racine_donnees, "valide")
    cotises = G.premiers_trimestres(parametres.racine_donnees)
    assert valides["H"][1950][21] == 93.2
    assert valides["H"][1950][23] == 99.2
    rangs = (0.1, 0.3, 0.5, 0.7, 0.9)
    assert [G.age_du_premier_trimestre(valides["H"], 1950, rang) for rang in rangs] == [
        16, 16, 17, 19, 21]
    assert [G.age_du_premier_trimestre(cotises["H"], 1950, rang) for rang in rangs] == [
        16, 16, 17, 19, 22]
    assert G.age_du_premier_trimestre(valides["H"], 1946, 0.9) == 20
    assert G.age_du_premier_trimestre(cotises["H"], 1946, 0.9) == 22


@pytest.mark.usefixtures("sans_le_reperage_des_decotes")
def test_le_dernier_cinquieme_des_hommes_fait_son_service_avant_de_cotiser(
        simulateur, source, monkeypatch):
    """Sous ``SERVICE_AVANT_LE_PREMIER_TRIMESTRE``, le cinquième d'une
    carrière pleine d'homme dont la génération valide son premier trimestre
    avant d'en cotiser un fait son service national les années qui les
    séparent : celui de la génération 1950 qui cotise à 22 ans valide son
    service à 21 ans. Sa durée d'assurance commence un an plus tôt : il part
    à 61 ans et demi au taux plein par la durée — les 162 trimestres de sa
    génération, de 21 ans à 61 ans et demi —, et non à 62 ans et demi. Né en
    1946, il fait deux années de service, à 20 et 21 ans. Le premier
    cinquième, qui valide et cotise à 16 ans, n'en fait pas ; aucune femme
    non plus."""
    assert G.SERVICE_AVANT_LE_PREMIER_TRIMESTRE
    variantes = G.grille("population", simulateur.effectifs, source, ())
    projection = simulateur.pour_la_projection()
    par_code = {v.cas.code: v.cas for v in variantes}
    pleine = f"{G.GABARIT}~h~40_plus~p50"
    dernier = par_code[f"{pleine}~entree5"]
    assert dernier.debut_de(1950) == 22.0
    assert dernier.service_de(1950) == 1
    assert dernier.service_de(1946) == 2
    lignes = dernier.carriere_a(projection, 1950, 61.5).lignes
    assert [l.type_periode for l in lignes if l.annee == 1950 + 21] == ["service_militaire"]
    assert min(l.annee for l in lignes if l.type_periode == "emploi") == 1950 + 22
    assert G.condition_au_depart(projection, dernier, 1950) == (
        pytest.approx(61.5), "taux_plein_autre")
    assert par_code[pleine].service_de(1950) == 0
    assert not any(v.cas.service_de(generation)
                   for v in variantes if v.cas.sexe == "F" and isinstance(v.cas, G.CasTypeLarge)
                   for generation in (1942, 1946, 1950, 1970))
    monkeypatch.setattr(G, "SERVICE_AVANT_LE_PREMIER_TRIMESTRE", False)
    avant = {v.cas.code: v.cas for v in G.grille("population", simulateur.effectifs,
                                                 source, ())}
    assert G.condition_au_depart(projection, avant[f"{pleine}~entree5"], 1950) == (
        pytest.approx(62.5), "taux_plein_autre")


def test_la_part_assimilee_suit_le_quintile_de_la_classe(parametres):
    """La part de la durée validée hors majorations qui n'est pas cotisée suit
    le quintile de la pension en équivalent carrière complète : l'EIR mesure
    aux résidentes du premier quintile 23 années validées pour 17 cotisées,
    26,1 % d'assimilées ; du deuxième, 34 pour 27 ; du troisième, 38 pour 35 ;
    du quatrième, 38 pour 36 ; du cinquième, 39 pour 38, 2,6 %
    (``quintiles_eqcc_residents.csv``). Chaque classe de centiles prend la part
    des bandes de quintiles que ses rangs couvrent, comme sous
    ``RANG_SELON_LA_DUREE``, chaque retraité au minimum gardant celle de son
    quintile dans la bande du premier.

    Les classes p95 et p99 des femmes tombent toutes dans la bande du
    cinquième quintile, de 88,1 % à 100 % de leurs rangs — 1 005 milliers de
    résidentes sur 8 373, 0,9 % au minimum — : 1/39. Celles des hommes de
    même, de 70,7 % à 100 % : 4/41. La classe p10 des femmes, de 0 à 17,5 %,
    tombe dans celle du premier, de 0 à 48,3 % : dans la tranche de quarante
    années et plus, 0,0401 des résidentes du premier quintile à 6/23, 0,0457
    du deuxième au minimum à 7/34, 0,0171 du troisième à 3/38, 0,0079 du
    quatrième à 2/38, 0,0005 du cinquième à 1/39 — 19,5 %."""
    quintiles = G.quintiles_eqcc(parametres.racine_donnees, residents=True)
    femmes = G.parts_assimilees_des_classes(quintiles, "F", "40_plus")
    hommes = G.parts_assimilees_des_classes(quintiles, "H", "40_plus")
    assert femmes["p95"] == pytest.approx(1 / 39)
    assert femmes["p99"] == pytest.approx(1 / 39)
    assert hommes["p95"] == pytest.approx(4 / 41)
    assert femmes["p10"] == pytest.approx(0.1946, abs=5e-4)
    assert set(femmes) == {nom for nom, _ in G.CENTILES}


@pytest.mark.usefixtures("sans_le_reperage_des_decotes")
def test_la_carriere_pleine_d_une_femme_du_haut_part_en_carriere_longue(
        simulateur, source, monkeypatch):
    """Sous ``ASSIMILEES_SELON_LE_RANG``, la femme née en 1953 d'une carrière
    pleine du salariat privé de la classe p95, entrée à 17 ans, ne compte plus
    qu'une année assimilée sur ses 43 (1/39 de l'EIR), et non cinq (4/32) :
    ses quatre trimestres de chômage indemnisé sont réputés cotisés
    (D. 351-1-2), et elle a, à 60 ans, 172 trimestres cotisés ou réputés tels,
    pour 165 que sa génération doit : elle part à 60 ans en carrière longue.
    Avec cinq années assimilées, elle n'en avait que 156 — 172, moins seize
    trimestres de chômage non réputés —, et partait à 61 ans et deux mois,
    l'âge légal de sa génération. La carrière pleine de la classe p10 en
    compte huit (19,5 %). Le test dit la version seule : la vingt-quatrième
    (``NATURES_A_LEUR_PART``), qui donne leur nature aux années assimilées
    des femmes, en est ôtée."""
    assert G.ASSIMILEES_SELON_LE_RANG
    monkeypatch.setattr(G, "NATURES_A_LEUR_PART", False)
    variantes = {v.cas.code: v for v in G.grille("population", simulateur.effectifs,
                                                  source, ())}
    projection = simulateur.pour_la_projection()
    haute = variantes[f"{G.GABARIT}~f~40_plus~p95"]
    assert haute.duree == 43 and haute.assimilees == 1
    assert haute.cas.debut_de(1953) == 17.0
    assert G.condition_au_depart(projection, haute.cas, 1953) == (
        pytest.approx(60.0), "carriere_longue")
    assert variantes[f"{G.GABARIT}~f~40_plus~p10~bas1"].assimilees == 8
    monkeypatch.setattr(G, "ASSIMILEES_SELON_LE_RANG", False)
    avant = {v.cas.code: v for v in G.grille("population", simulateur.effectifs,
                                              source, ())}
    assert avant[f"{G.GABARIT}~f~40_plus~p95"].assimilees == 5
    assert G.condition_au_depart(projection, avant[f"{G.GABARIT}~f~40_plus~p95"].cas,
                                 1953) == (pytest.approx(61.17), "taux_plein_autre")


def test_les_natures_assimilees_se_lisent_generation_par_generation(parametres):
    """La part des hommes affiliés avant 23 ans qui ont validé un trimestre de
    service national, ou de maladie, et les années qu'en a chacun de ceux qui
    en ont, le cumul par homme sur la part (``natures_assimilees.csv``) : nés
    en 1950, 35,1 % ont servi, 1,4 trimestre par homme, quatre chacun, une
    année ; 12,6 % ont été malades, 2,2 trimestres par homme, dix-sept et demi
    chacun, quatre années. Entre deux générations de l'échantillon, la part et
    le cumul s'interpolent : 40,5 % des nés en 1952, entre 35,1 et 45,9. La
    maladie se lit à 60 ans, que l'échantillon ne voit pas après la génération
    1956 : celle de 1960 prend sa part, 14,6 %. Avant 1942, la part de 1942 ;
    nés en 1980, 0,2 % ont servi, sans cumul publié : aucune année."""
    natures = G.natures_assimilees(parametres.racine_donnees, "H")
    assert G.part_et_annees(natures["service_national"], 1950) == (pytest.approx(0.351), 1)
    assert G.part_et_annees(natures["maladie"], 1950) == (pytest.approx(0.126), 4)
    assert G.part_et_annees(natures["service_national"], 1952)[0] == pytest.approx(0.405)
    assert G.part_et_annees(natures["maladie"], 1960) == (pytest.approx(0.146), 4)
    assert G.part_et_annees(natures["service_national"], 1930) == (pytest.approx(0.497), 1)
    assert G.part_et_annees(natures["service_national"], 1980) == (pytest.approx(0.002), 0)


def test_la_population_lit_les_quatre_natures_a_60_ans_au_plus(parametres):
    """Le fichier des natures dit aussi ce que l'échantillon voit après
    60 ans — 67 ans pour les nés en 1950 — et le cumul des trimestres validés
    et cotisés, qui disent ce que compte au-delà la masse assimilée de l'EIR
    (action 138, étape 14, le 24 octobre 2026) ; la population n'en lit que
    les quatre natures, à 60 ans ou au dernier âge vu avant : 4,3 trimestres
    de chômage par homme né en 1950, et non les 4,6 de ses 67 ans."""
    for sexe in ("F", "H"):
        natures = G.natures_assimilees(parametres.racine_donnees, sexe)
        assert set(natures) == {"service_national", "maladie", "chomage", "avpf"}
    hommes = G.natures_assimilees(parametres.racine_donnees, "H")
    assert hommes["chomage"][1950] == (32.5, 4.3)
    assert hommes["service_national"][1950] == (35.1, 1.4)
    assert hommes["service_national"][1976] == (42.3, 1.4)


def test_les_classes_de_nature_rendent_les_parts_de_l_echantillon(parametres, monkeypatch):
    """Chaque cinquième d'une carrière pleine d'homme se décline en cinq classes
    de nature de poids égal, chacune au milieu de son rang. Le cinquième qui
    sert avant d'entrer (``SERVICE_AVANT_LE_PREMIER_TRIMESTRE``) a son
    service ; une classe des autres sert parmi ses années assimilées quand son
    rang passe sous la part du service qui leur reste : en 1950, 35,1 % des
    hommes ont servi, dont le dernier cinquième, 20 %, et (35,1 − 20) / 80 =
    18,9 % des autres, la première classe ; en 1955, 48,25 % entre 1954 et
    1956, (48,25 − 20) / 80 = 35,3 %, les deux premières ; en 1980, aucune.
    La dernière classe compte de la maladie quand son rang passe au-dessus de
    la part des autres : 12,6 % en 1950, quatre années. En 1950, 36 % des
    hommes ont ainsi une année de service, 20 % de la maladie ; le dernier
    cinquième ne sert pas deux fois. Le test dit la version seule : les classes
    plus fines de la vingt-sixième (``CLASSES_DE_NATURE``) en sont ôtées."""
    monkeypatch.setattr(G, "CLASSES_DE_NATURE", 5)
    racine = parametres.racine_donnees
    regle = G.entrees_des_carrieres_pleines(racine)["H"]
    entrees = G.classes_d_entree(regle, G.premiers_trimestres(racine)["H"],
                                 G.premiers_trimestres(racine, "valide")["H"])
    classes = G.classes_de_nature(entrees, G.natures_assimilees(racine, "H"))
    assert sum(poids for *_, poids in classes) == pytest.approx(1.0)

    def part(generation: int, rang: int) -> float:
        return sum(poids for _, _, services, _, natures, poids in classes
                   if G._par_generation(natures, generation, (0, 0))[rang] > 0
                   or rang == 0 and G._par_generation(services, generation, 0.0) > 0)

    assert part(1950, 0) == pytest.approx(0.2 + 0.8 * 0.2)
    assert part(1955, 0) == pytest.approx(0.2 + 0.8 * 0.4)
    assert part(1980, 0) == 0.0
    assert part(1950, 1) == pytest.approx(0.2)
    for _, _, services, _, natures, _ in classes:
        service, maladie = G._par_generation(natures, 1950, (0, 0))
        assert service in (0, 1) and maladie in (0, 4)
        assert not (service and G._par_generation(services, 1950, 0.0))
    assert sum(1 for *_, natures, _ in classes if not natures) == len(entrees)


@pytest.mark.usefixtures("sans_le_reperage_des_decotes")
def test_le_service_et_la_maladie_rendent_la_carriere_longue_aux_hommes_de_1950(
        simulateur, source, monkeypatch):
    """Sous ``NATURES_SELON_LA_GENERATION``, l'homme né en 1950 d'une carrière
    pleine du salariat privé de la classe p50, entré à 16 ans, compte trois
    années assimilées sur 43, au milieu de sa carrière, de 36 à 38 ans. Dans la
    première classe de nature, la première est son service national ; dans la
    dernière, toutes trois sont de la maladie. La rédaction de D. 351-1-2 de
    2003, qui juge un départ de 2009, en répute quatre trimestres cotisés,
    l'une et l'autre, et aucun de chômage : à 59 ans, il a validé 172
    trimestres, dont 160 cotisés et 4 réputés tels, les 162 de sa génération
    au moins (D. 351-1-1, une entrée avant 17 ans) ; il part en carrière
    longue à 59 ans. La classe sans service ni maladie garde le code de la
    carrière, son chômage entier, qui n'est pas réputé cotisé : 160 trimestres
    à 59 ans, 162 à 59 ans et demi, où elle part, comme toute la carrière sans
    la version. Le test dit la version seule : la vingt-quatrième
    (``NATURES_A_LEUR_PART``) en est ôtée, et les classes plus fines de la
    vingt-sixième (``CLASSES_DE_NATURE``)."""
    assert G.NATURES_SELON_LA_GENERATION
    monkeypatch.setattr(G, "NATURES_A_LEUR_PART", False)
    monkeypatch.setattr(G, "CLASSES_DE_NATURE", 5)
    variantes = {v.cas.code: v.cas for v in G.grille("population", simulateur.effectifs,
                                                      source, ())}
    projection = simulateur.pour_la_projection()
    pleine = f"{G.GABARIT}~h~40_plus~p50"
    service, maladie, sans = (variantes[f"{pleine}~nature1"], variantes[f"{pleine}~nature5"],
                              variantes[pleine])
    assert service.debut_de(1950) == 16.0

    def motifs(cas) -> list[str]:
        return [l.type_periode for l in cas.carriere_a(projection, 1950, 59.0).lignes
                if 1950 + 36 <= l.annee <= 1950 + 38]

    assert motifs(service) == ["service_militaire", "chomage_indemnise", "chomage_indemnise"]
    assert motifs(maladie) == ["maladie"] * 3
    assert motifs(sans) == ["chomage_indemnise"] * 3
    assert G.condition_au_depart(projection, service, 1950) == (
        pytest.approx(59.0), "carriere_longue")
    assert G.condition_au_depart(projection, maladie, 1950) == (
        pytest.approx(59.0), "carriere_longue")
    assert G.condition_au_depart(projection, sans, 1950) == (
        pytest.approx(59.5), "carriere_longue")
    monkeypatch.setattr(G, "NATURES_SELON_LA_GENERATION", False)
    avant = {v.cas.code: v.cas for v in G.grille("population", simulateur.effectifs,
                                                  source, ())}
    assert f"{pleine}~nature1" not in avant
    assert G.condition_au_depart(projection, avant[pleine], 1950) == (
        pytest.approx(59.5), "carriere_longue")


def test_le_chomage_et_l_avpf_se_lisent_generation_par_generation(parametres):
    """La part des affiliés d'avant 23 ans qui ont validé un trimestre de
    chômage, ou d'assurance vieillesse des parents au foyer, et les années
    qu'en a chacun de ceux qui en ont, sans arrondi : le cumul par affilié sur
    la part, en années de quatre trimestres (``natures_assimilees.csv``). Nés
    en 1950, 32,5 % des hommes ont validé du chômage, 4,3 trimestres par
    homme, 3,31 années chacun ; 39,8 % des femmes de l'AVPF, 10,5 trimestres
    par femme, 6,60 années chacune, et 37,6 % du chômage, 5,4 trimestres, 3,59
    années. Le chômage et l'AVPF, qui croissent avec l'âge, se lisent à 60 ans,
    comme la maladie : la génération 1960 prend la part de celle de 1956,
    41,0 % des hommes au chômage, 5,0 trimestres, 3,05 années, et 45,5 % des
    femmes à l'AVPF, 12,3 trimestres, 6,76 années."""
    racine = parametres.racine_donnees
    hommes, femmes = G.natures_assimilees(racine, "H"), G.natures_assimilees(racine, "F")
    assert G.part_et_duree(hommes["chomage"], 1950) == pytest.approx((0.325, 4.3 / 0.325 / 4))
    assert G.part_et_duree(femmes["avpf"], 1950) == pytest.approx((0.398, 10.5 / 0.398 / 4))
    assert G.part_et_duree(femmes["chomage"], 1950) == pytest.approx((0.376, 5.4 / 0.376 / 4))
    assert G.part_et_duree(hommes["chomage"], 1960) == pytest.approx((0.410, 5.0 / 0.410 / 4))
    assert G.part_et_duree(femmes["avpf"], 1960) == pytest.approx((0.455, 12.3 / 0.455 / 4))


def test_les_natures_vont_a_leur_part_et_a_leurs_annees_sous_la_masse(parametres, monkeypatch):
    """Sous ``NATURES_A_LEUR_PART``, chaque classe de nature d'un cinquième
    compte les années de ses natures, chacune à la part de sa génération — le
    service et l'AVPF du bas des rangs, le chômage et la maladie du haut — et
    aux années qu'en a chacun de ceux qui en ont, arrondies ; la classe qui
    n'en a aucune n'en compte aucune. Les années assimilées de sa classe de
    centiles, cinq fois les siennes, en sont le plafond : quand ses classes en
    demandent plus, ce que le service leur laisse se partage à proportion.
    L'homme né en 1950, trois années assimilées, du premier cinquième : la
    première classe sert, (35,1 − 20) / 80 = 18,9 % ; les deux dernières sont
    au chômage, 32,5 %, 3,31 années chacune, trois ; la dernière est malade,
    12,6 %, 4,37 années, quatre : onze années sous les quinze du cinquième. La
    femme née en 1950, huit années : les deux premières classes à l'AVPF,
    39,8 %, 6,60 années, sept ; les deux dernières au chômage, 37,6 %, 3,59,
    quatre ; la dernière malade, 19,4 %, 2,84, trois : vingt-cinq années sous
    quarante. Celle de trois années n'en a que quinze pour 23,21 : 0,65 fois
    chacune, quatre d'AVPF, deux de chômage, deux de maladie. La classe du
    milieu, sans aucune, garde le code de son cinquième. Le test dit la
    version seule : la vingt-cinquième (``MALADIE_INDEPENDANTE``) en est
    ôtée, et les classes plus fines de la vingt-sixième
    (``CLASSES_DE_NATURE``)."""
    racine = parametres.racine_donnees
    monkeypatch.setattr(G, "MALADIE_INDEPENDANTE", False)
    monkeypatch.setattr(G, "CLASSES_DE_NATURE", 5)

    def classes(sexe: str, assimilees: int) -> list:
        regle = G.entrees_des_carrieres_pleines(racine)[sexe]
        valides = G.premiers_trimestres(racine, "valide")[sexe] if sexe == "H" else None
        entrees = G.classes_d_entree(regle, G.premiers_trimestres(racine)[sexe], valides)
        return G.classes_de_nature(entrees, G.natures_assimilees(racine, sexe), assimilees)

    def premier_cinquieme_en_1950(lot: list) -> tuple[dict[tuple, float], dict[tuple, set]]:
        """Les années de chaque nature en 1950 — service, maladie, AVPF,
        chômage — des classes du premier cinquième, leur part du cinquième, et
        le rang qui fait leur code, zéro pour celui du cinquième."""
        siennes = [(G._par_generation(natures, 1950, None), poids, nature)
                   for rang, _, _, nature, natures, poids in lot if rang == 1]
        total = sum(poids for _, poids, _ in siennes)
        parts: dict[tuple, float] = {}
        codes: dict[tuple, set] = {}
        for annees, poids, nature in siennes:
            parts[annees] = parts.get(annees, 0.0) + poids / total
            codes.setdefault(annees, set()).add(nature)
        return parts, codes

    def masse(parts: dict[tuple, float]) -> float:
        return sum(sum(annees) * part for annees, part in parts.items())

    hommes, codes = premier_cinquieme_en_1950(classes("H", 3))
    assert hommes == pytest.approx(
        {(1, 0, 0, 0): 0.2, (0, 0, 0, 0): 0.4, (0, 0, 0, 3): 0.2, (0, 4, 0, 3): 0.2})
    assert codes == {(1, 0, 0, 0): {1}, (0, 0, 0, 0): {0, 2}, (0, 0, 0, 3): {4},
                     (0, 4, 0, 3): {5}}
    assert masse(hommes) == pytest.approx(2.2)
    femmes, codes = premier_cinquieme_en_1950(classes("F", 8))
    assert femmes == pytest.approx(
        {(0, 0, 7, 0): 0.4, (0, 0, 0, 0): 0.2, (0, 0, 0, 4): 0.2, (0, 3, 0, 4): 0.2})
    assert codes == {(0, 0, 7, 0): {1, 2}, (0, 0, 0, 0): {0}, (0, 0, 0, 4): {4},
                     (0, 3, 0, 4): {5}}
    assert masse(femmes) == pytest.approx(5.0)
    femmes, _ = premier_cinquieme_en_1950(classes("F", 3))
    assert femmes == pytest.approx(
        {(0, 0, 4, 0): 0.4, (0, 0, 0, 0): 0.2, (0, 0, 0, 2): 0.2, (0, 2, 0, 2): 0.2})
    assert masse(femmes) == pytest.approx(2.8)


@pytest.mark.usefixtures("sans_le_reperage_des_decotes")
def test_le_chomage_a_sa_part_rend_la_carriere_longue_aux_hommes_qui_n_en_ont_pas(
        simulateur, source, monkeypatch):
    """Sous ``NATURES_A_LEUR_PART``, l'homme né en 1950 d'une carrière pleine du
    salariat privé de la classe p50, entré à 16 ans, du premier cinquième : sa
    classe de centiles compte trois années assimilées, au milieu de sa
    carrière, de 36 à 38 ans. La classe du milieu, qui garde le code de la
    carrière, n'a en 1950 ni service, ni maladie, ni chômage : aucune année
    assimilée, 172 trimestres cotisés à 59 ans, les 162 de sa génération au
    moins ; elle part en carrière longue à 59 ans, et non plus à 59 ans et
    demi. La première sert une année, à 37 ans, réputée cotisée : elle part à
    59 ans. La quatrième est au chômage trois années, de 36 à 38 ans, que la
    rédaction de D. 351-1-2 de 2003 ne répute pas cotisées : 160 trimestres
    cotisés à 59 ans, 162 à 59 ans et demi, où elle part en carrière longue.
    La dernière en a sept, de 34 à 40 ans, quatre de maladie, réputées pour
    quatre trimestres, puis trois de chômage : 148 trimestres cotisés ou
    réputés à 59 ans ; elle part à 60 ans, l'âge légal, au taux plein. Le test
    dit la version seule : la vingt-cinquième (``MALADIE_INDEPENDANTE``) en
    est ôtée, et les classes plus fines de la vingt-sixième
    (``CLASSES_DE_NATURE``)."""
    assert G.NATURES_A_LEUR_PART
    monkeypatch.setattr(G, "MALADIE_INDEPENDANTE", False)
    monkeypatch.setattr(G, "CLASSES_DE_NATURE", 5)
    variantes = {v.cas.code: v.cas for v in G.grille("population", simulateur.effectifs,
                                                      source, ())}
    projection = simulateur.pour_la_projection()
    pleine = f"{G.GABARIT}~h~40_plus~p50"
    milieu, service, chomage, malade = (variantes[pleine], variantes[f"{pleine}~nature1"],
                                        variantes[f"{pleine}~nature4"],
                                        variantes[f"{pleine}~nature5"])
    assert milieu.debut_de(1950) == 16.0

    def motifs(cas) -> list[str]:
        return [l.type_periode for l in cas.carriere_a(projection, 1950, 59.0).lignes
                if 1950 + 32 <= l.annee <= 1950 + 41]

    assert motifs(milieu) == ["emploi"] * 10
    assert motifs(service) == ["emploi"] * 5 + ["service_militaire"] + ["emploi"] * 4
    assert motifs(chomage) == ["emploi"] * 4 + ["chomage_indemnise"] * 3 + ["emploi"] * 3
    assert motifs(malade) == (["emploi"] * 2 + ["maladie"] * 4 + ["chomage_indemnise"] * 3
                              + ["emploi"])
    for cas, attendu in ((milieu, (59.0, "carriere_longue")), (service, (59.0, "carriere_longue")),
                         (chomage, (59.5, "carriere_longue")),
                         (malade, (60.0, "taux_plein_autre"))):
        age, condition = G.condition_au_depart(projection, cas, 1950)
        assert (age, condition) == (pytest.approx(attendu[0]), attendu[1]), cas.code
    monkeypatch.setattr(G, "NATURES_A_LEUR_PART", False)
    avant = {v.cas.code: v.cas for v in G.grille("population", simulateur.effectifs,
                                                  source, ())}
    assert G.condition_au_depart(projection, avant[pleine], 1950) == (
        pytest.approx(59.5), "carriere_longue")


def test_les_malades_sont_au_chomage_a_la_part_des_autres(parametres, monkeypatch):
    """Sous ``MALADIE_INDEPENDANTE``, la maladie a son propre rang :
    l'échantillon publie la part des affiliés qui ont chaque nature, non celle
    de ceux qui en ont deux, et la vingt-quatrième version, qui mettait le
    chômage et la maladie au haut d'un même rang, mettait tous les malades au
    chômage. Chaque classe de nature d'un cinquième — le service et l'AVPF du
    bas, le chômage du haut — se décline en cinq classes de maladie de poids
    égal, dont celles dont le milieu du rang passe au-dessus de la part des
    autres sont malades : les malades ont chaque autre nature à la part de
    tous. L'homme né en 1950, trois années assimilées, du premier cinquième :
    la classe qui sert, (35,1 − 20) / 80 = 18,9 %, et les deux du chômage,
    32,5 %, trois années, gardent quatre cinquièmes de leur poids sans
    maladie, et en donnent un aux malades, 12,6 %, quatre années ; les deux
    classes du milieu de même. Des 20 % de malades, 8 sont au chômage, les
    40 % de tous, et non plus 20 ; 4 servent. Le plafond, 25 × 3 − 5 = 70
    années, passe les 5 × 4,37 + 10 × 3,31 = 54,95 que les classes demandent :
    les mêmes 2,2 années par homme du cinquième. La classe du milieu de chaque
    rang, sans aucune, garde le code de son cinquième ; les autres prennent
    celui de la première des vingt-cinq qu'elles réunissent, les mêmes natures
    à chaque génération : la deuxième classe du service, qui ne sert pas en
    1950, sert en 1955. La femme née en 1950, huit années : les mêmes
    5,0 années, l'AVPF des deux premières classes, 39,8 %, sept années, à
    trois de maladie pour un cinquième d'entre elles. Le test dit la version
    seule : les classes plus fines de la vingt-sixième (``CLASSES_DE_NATURE``)
    en sont ôtées."""
    racine = parametres.racine_donnees
    assert G.MALADIE_INDEPENDANTE
    monkeypatch.setattr(G, "CLASSES_DE_NATURE", 5)

    def premier_cinquieme_en_1950(sexe: str, assimilees: int
                                  ) -> tuple[dict[tuple, float], dict[tuple, set]]:
        """Les années de chaque nature en 1950 — service, maladie, AVPF,
        chômage — des classes du premier cinquième, leur part du cinquième, et
        le rang qui fait leur code, zéro pour celui du cinquième."""
        regle = G.entrees_des_carrieres_pleines(racine)[sexe]
        valides = G.premiers_trimestres(racine, "valide")[sexe] if sexe == "H" else None
        entrees = G.classes_d_entree(regle, G.premiers_trimestres(racine)[sexe], valides)
        lot = G.classes_de_nature(entrees, G.natures_assimilees(racine, sexe), assimilees)
        siennes = [(G._par_generation(natures, 1950, None), poids, nature)
                   for rang, _, _, nature, natures, poids in lot if rang == 1]
        total = sum(poids for _, poids, _ in siennes)
        parts: dict[tuple, float] = {}
        codes: dict[tuple, set] = {}
        for annees, poids, nature in siennes:
            parts[annees] = parts.get(annees, 0.0) + poids / total
            codes.setdefault(annees, set()).add(nature)
        return parts, codes

    def masse(parts: dict[tuple, float]) -> float:
        return sum(sum(annees) * part for annees, part in parts.items())

    hommes, codes = premier_cinquieme_en_1950("H", 3)
    assert hommes == pytest.approx(
        {(1, 0, 0, 0): 0.16, (1, 4, 0, 0): 0.04, (0, 0, 0, 0): 0.32, (0, 4, 0, 0): 0.08,
         (0, 0, 0, 3): 0.32, (0, 4, 0, 3): 0.08})
    assert codes == {(1, 0, 0, 0): {1}, (1, 4, 0, 0): {5}, (0, 0, 0, 0): {0, 6},
                     (0, 4, 0, 0): {10, 15}, (0, 0, 0, 3): {16}, (0, 4, 0, 3): {20}}
    malades = sum(part for annees, part in hommes.items() if annees[1])
    assert malades == pytest.approx(0.2)
    assert sum(part for annees, part in hommes.items()
               if annees[1] and annees[3]) / malades == pytest.approx(0.4)
    assert masse(hommes) == pytest.approx(2.2)
    femmes, _ = premier_cinquieme_en_1950("F", 8)
    assert femmes == pytest.approx(
        {(0, 0, 7, 0): 0.32, (0, 3, 7, 0): 0.08, (0, 0, 0, 0): 0.16, (0, 3, 0, 0): 0.04,
         (0, 0, 0, 4): 0.32, (0, 3, 0, 4): 0.08})
    assert masse(femmes) == pytest.approx(5.0)


@pytest.mark.usefixtures("sans_le_reperage_des_decotes")
def test_le_malade_sans_chomage_part_en_carriere_longue(simulateur, source, monkeypatch):
    """Sous ``MALADIE_INDEPENDANTE``, l'homme né en 1955 d'une carrière pleine
    du salariat privé de la classe p50, du premier cinquième, entré à 17 ans :
    sa classe de centiles compte trois années assimilées, de 37 à 39 ans. Son
    départ de 2015 est jugé par la rédaction de D. 351-1-2 d'avril 2014, qui
    répute cotisés quatre trimestres de maladie et quatre de chômage
    indemnisé, et la carrière longue à 60 ans lui demande les 166 trimestres
    cotisés ou réputés de sa génération (D. 351-1-1) ; il en a 172 à 60 ans
    sans période assimilée. La classe malade sans chômage, que la
    vingt-quatrième version n'avait pas, compte quatre années de maladie, de
    36 à 39 ans : 172 − 16 + 4 = 160 trimestres à 60 ans, 166 à 61 ans et
    demi, où elle part en carrière longue. La classe malade et au chômage,
    sept années, quatre de maladie puis trois de chômage, de 35 à 41 ans,
    huit trimestres réputés : 152 à 60 ans ; elle part à 62 ans, l'âge légal,
    au taux plein, comme tous les malades de la vingt-quatrième version. La
    classe au chômage seul, trois années, quatre trimestres réputés : 164 à
    60 ans, 166 à 60 ans et demi, où elle part en carrière longue. Le test dit
    la version seule : les classes plus fines de la vingt-sixième
    (``CLASSES_DE_NATURE``) en sont ôtées."""
    assert G.MALADIE_INDEPENDANTE
    monkeypatch.setattr(G, "CLASSES_DE_NATURE", 5)
    variantes = {v.cas.code: v.cas for v in G.grille("population", simulateur.effectifs,
                                                      source, ())}
    projection = simulateur.pour_la_projection()
    pleine = f"{G.GABARIT}~h~40_plus~p50"
    malade, malade_au_chomage, chomage = (variantes[f"{pleine}~nature15"],
                                          variantes[f"{pleine}~nature20"],
                                          variantes[f"{pleine}~nature16"])
    assert malade.debut_de(1955) == 17.0

    def motifs(cas) -> list[str]:
        return [l.type_periode for l in cas.carriere_a(projection, 1955, 60.0).lignes
                if 1955 + 34 <= l.annee <= 1955 + 42]

    assert motifs(malade) == ["emploi"] * 2 + ["maladie"] * 4 + ["emploi"] * 3
    assert motifs(malade_au_chomage) == (["emploi"] + ["maladie"] * 4
                                         + ["chomage_indemnise"] * 3 + ["emploi"])
    assert motifs(chomage) == ["emploi"] * 3 + ["chomage_indemnise"] * 3 + ["emploi"] * 3
    for cas, attendu in ((malade, (61.5, "carriere_longue")),
                         (malade_au_chomage, (62.0, "taux_plein_autre")),
                         (chomage, (60.5, "carriere_longue"))):
        age, condition = G.condition_au_depart(projection, cas, 1955)
        assert (age, condition) == (pytest.approx(attendu[0]), attendu[1]), cas.code


def test_les_classes_de_nature_plus_fines_tiennent_chaque_part_a_un_trentieme_pres(
        parametres):
    """Chaque rang de nature compte quinze classes de poids égal, et non plus
    cinq (``CLASSES_DE_NATURE``) : chaque part s'arrondissait au cinquième le
    plus proche, 40 % de chômeurs pour 30,2 à 41,0 % des hommes de 1942 à
    1956, 20 % de malades pour 10,5 à 14,6 % ; elle s'arrondit au quinzième,
    à un trentième près. L'homme né en 1950, trois années assimilées, du
    premier cinquième : trois classes du rang servent, sous les
    (35,1 − 20) / 80 = 18,9 % du service, une année chacune ; cinq sont au
    chômage, au-dessus des 67,5 % qui n'en ont pas, trois années, et non plus
    deux sur cinq ; deux classes de la maladie sont malades, au-dessus des
    87,4 %, quatre années, et non plus une sur cinq. Le tiers des malades est
    au chômage, la part de tous. Le plafond, 225 × 3 − 45 = 630 années, passe
    les 75 × 3,31 + 30 × 4,37 = 379 que les classes demandent : 26/15 = 1,73
    année par homme, et non plus 2,2. La classe du milieu des deux rangs, sans
    aucune nature, garde le code de son cinquième. Aux générations de
    l'échantillon, de 1942 à 1956, le chômage, la maladie et l'AVPF des deux
    sexes tiennent chacun leur part à un trentième près."""
    racine = parametres.racine_donnees

    def premier_cinquieme(sexe: str, assimilees: int) -> list:
        regle = G.entrees_des_carrieres_pleines(racine)[sexe]
        valides = G.premiers_trimestres(racine, "valide")[sexe] if sexe == "H" else None
        entrees = G.classes_d_entree(regle, G.premiers_trimestres(racine)[sexe], valides)
        lot = G.classes_de_nature(entrees, G.natures_assimilees(racine, sexe), assimilees)
        siennes = [(natures, poids, nature) for rang, _, _, nature, natures, poids in lot
                   if rang == 1]
        total = sum(poids for _, poids, _ in siennes)
        return [(natures, poids / total, nature) for natures, poids, nature in siennes]

    hommes = premier_cinquieme("H", 3)
    parts: dict[tuple, float] = {}
    codes: dict[tuple, set] = {}
    for natures, part, nature in hommes:
        annees = G._par_generation(natures, 1950, None)
        parts[annees] = parts.get(annees, 0.0) + part
        codes.setdefault(annees, set()).add(nature)
    assert parts == pytest.approx(
        {(1, 0, 0, 0): 39 / 225, (1, 4, 0, 0): 6 / 225, (0, 0, 0, 0): 91 / 225,
         (0, 4, 0, 0): 14 / 225, (0, 0, 0, 3): 65 / 225, (0, 4, 0, 3): 10 / 225})
    malades = sum(part for annees, part in parts.items() if annees[1])
    assert malades == pytest.approx(2 / 15)
    assert sum(part for annees, part in parts.items()
               if annees[1] and annees[3]) / malades == pytest.approx(1 / 3)
    assert sum(sum(annees) * part for annees, part in parts.items()) == pytest.approx(26 / 15)
    assert 0 in codes[(0, 0, 0, 0)]
    for sexe, assimilees in (("H", 3), ("F", 8)):
        lues = G.natures_assimilees(racine, sexe)
        classes = premier_cinquieme(sexe, assimilees)
        for rang, nom in ((1, "maladie"), (2, "avpf"), (3, "chomage")):
            for generation in sorted(lues[nom]):
                part = sum(poids for natures, poids, _ in classes
                           if G._par_generation(natures, generation, None)[rang])
                assert abs(part - lues[nom][generation][0] / 100.0) <= 1 / 30 + 1e-9, (
                    sexe, nom, generation)


def test_les_natures_des_femmes_suivent_la_masse_de_leur_rang(parametres, simulateur, source):
    """Sous ``NATURES_SELON_LE_RANG``, la part des femmes d'une carrière pleine
    qui ont de la maladie, de l'AVPF ou du chômage suit, d'une classe de
    centiles à l'autre, la masse assimilée que l'EIR mesure à ses rangs
    (``ASSIMILEES_SELON_LE_RANG``) : la part de l'échantillon, multipliée par
    le rapport de la masse de la classe à celle de toutes les carrières
    pleines des femmes, 10,82 % de leur durée validée hors majorations, leurs
    classes pesées par leurs têtes. La classe p99, qui tient du cinquième
    quintile un trente-neuvième : 0,237 fois la part de toutes ; la classe
    p10, 19,46 % : 1,80 fois. Nées en 1950, 39,8 % des femmes ont de l'AVPF,
    37,6 % du chômage, 19,4 % de la maladie : à la classe p99, 9,4, 8,9 et
    4,6 %, une classe de quinze chacune, qui garde les années de
    l'échantillon, sept, quatre et trois, sous un plafond qui ne tient plus ;
    à la classe p10, 71,6, 67,6 et 34,9 %, onze, dix et cinq classes. Aux
    générations de l'échantillon, de 1942 à 1956, chaque nature tient à
    chaque classe sa part, et sur toutes, celle de l'échantillon, à un
    trentième près. Les hommes gardent la même part à chaque rang."""
    assert G.NATURES_SELON_LE_RANG == ("F",)
    racine = parametres.racine_donnees
    variantes = G.grille("population", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    noms = {nom for nom, _ in G.CENTILES}
    masses = G.parts_assimilees_des_classes(G.quintiles_eqcc(racine, residents=True),
                                            "F", "40_plus")
    assert masses["p99"] == pytest.approx(1 / 39)

    def par_classe(sexe: str) -> dict[str, list]:
        """Les carrières pleines du sexe, par classe de centiles : les années
        de chaque nature de chacune, génération par génération, et ses têtes."""
        sortie: dict[str, list] = {}
        for v in variantes:
            if v.cas.sexe == sexe and v.cas.annees_par_nature:
                classe = next(m for m in v.cas.code.split("~") if m in noms)
                sortie.setdefault(classe, []).append((v.cas.annees_par_nature,
                                                      poids[v.cas.code]))
        return sortie

    def part(lot: list, generation: int, rang: int) -> float:
        return (sum(p for natures, p in lot if G._par_generation(natures, generation, None)[rang])
                / sum(p for _, p in lot))

    femmes = par_classe("F")
    tetes = {classe: sum(p for _, p in lot) for classe, lot in femmes.items()}
    moyenne = sum(tetes[c] * masses[c] for c in tetes) / sum(tetes.values())
    assert moyenne == pytest.approx(0.1082, abs=5e-5)
    assert masses["p99"] / moyenne == pytest.approx(0.237, abs=5e-4)
    assert masses["p10"] / moyenne == pytest.approx(1.80, abs=5e-3)
    for classe, attendues in (("p99", (1, 1, 1)), ("p10", (5, 11, 10))):
        assert tuple(round(15 * part(femmes[classe], 1950, rang)) for rang in (1, 2, 3)) == (
            attendues), classe
    siennes = [G._par_generation(natures, 1950, None) for natures, _ in femmes["p99"]]
    assert {annees[2] for annees in siennes} == {0, 7}
    assert {annees[3] for annees in siennes} == {0, 4}
    assert {annees[1] for annees in siennes} == {0, 3}
    hommes = par_classe("H")
    for rang, nom in ((1, "maladie"), (2, "avpf"), (3, "chomage")):
        lues = G.natures_assimilees(racine, "F")[nom]
        for generation in sorted(lues):
            publiee = lues[generation][0] / 100.0
            for classe, lot in femmes.items():
                attendue = min(1.0, publiee * masses[classe] / moyenne)
                assert abs(part(lot, generation, rang) - attendue) <= 1 / 30 + 1e-9, (
                    nom, generation, classe)
            ensemble = sum(tetes[c] * part(lot, generation, rang) for c, lot in femmes.items())
            assert abs(ensemble / sum(tetes.values()) - publiee) <= 1 / 30 + 1e-9, (
                nom, generation)
            parts_des_hommes = [part(lot, generation, rang) for lot in hommes.values()]
            assert max(parts_des_hommes) - min(parts_des_hommes) < 1e-9, (nom, generation)


def test_les_morceaux_de_la_grille_tiennent_dans_le_pont():
    """Le pont passe au portage la demande d'un morceau d'un seul bloc, que node
    ne lit pas au-delà de 512 Mo, et chaque cas type y porte ses carrières de
    toutes les générations, 1,4 à 1,7 Mo avec le paquet des données : les
    3 742 cas types de la population de la vingt-quatrième version, sur quatre
    cœurs, faisaient huit morceaux de 468, qui ne passaient pas. Ils en font
    trente-huit, de 100 au plus, bout à bout dans leur ordre : un morceau de
    deux cents cas types de la population de la vingt-huitième version tenait
    2,6 Go au plus, son portage compris, un de cent 1,7, et quatre cœurs
    passaient sinon les 10 Go que la mesure ne doit pas passer. Une petite
    grille garde ses deux morceaux par cœur, cent cas types en huit, de treize
    et du reste."""
    grille = tuple(range(3742))
    morceaux = G.morceaux_de(grille, 4)
    assert G.CAS_TYPES_PAR_MORCEAU == 100
    assert len(morceaux) == 38 and max(len(morceau) for morceau in morceaux) == 100
    assert tuple(cas for morceau in morceaux for cas in morceau) == grille
    assert [len(morceau) for morceau in G.morceaux_de(tuple(range(100)), 4)] == [13] * 7 + [9]


def test_les_carrieres_courtes_de_la_population_sont_celles_de_tous(simulateur, source):
    """Les régimes statutaires n'ayant pas de carrières courtes, les autres en
    portent d'autant plus : sur tous les retraités de chaque sexe, le militaire
    et ses vingt-cinq années compris, la population redonne la part que l'EIR
    donne aux carrières de moins de trente années validées."""
    variantes = G.grille("population", simulateur.effectifs, source, ())
    composition = G.composition(variantes, simulateur.effectifs, source)
    publiee = G.composition_eir(source)
    for sexe in ("F", "H"):
        assert composition["moins_de_30_ans"][sexe] == pytest.approx(
            publiee["moins_de_30_ans"][sexe], abs=1e-9), sexe


def test_les_carrieres_statutaires_comptent_a_leur_duree(simulateur, source):
    """Sous ``STATUTAIRES_A_LEUR_DUREE``, la population redonne à tous les
    retraités de chaque sexe la part de CHAQUE tranche de durée que l'EIR
    publie : les carrières statutaires dans la tranche de leur durée — le
    militaire à vingt-cinq ans, l'agent de conduite à trente-deux —, les autres
    dans celle qui leur est donnée."""
    assert G.STATUTAIRES_A_LEUR_DUREE
    variantes = G.grille("population", simulateur.effectifs, source, ())
    poids = G.poids_retraites(variantes, simulateur.effectifs, source.millesime)
    for sexe in ("F", "H"):
        lot = [(v, p) for v, p in zip(variantes, poids) if v.cas.sexe == sexe]
        total = sum(p for _, p in lot)
        publiees = G.parts_tranches(source, sexe)
        for nom, _ in G.TRANCHES:
            masse = sum(p for v, p in lot
                        if (v.tranche if v.groupe in G.GROUPES_INTERROMPUS
                            else G.tranche_de_duree(G.duree_de(v))) == nom)
            assert masse / total == pytest.approx(publiees[nom], abs=1e-9), (sexe, nom)


def test_des_annees_etalees_tombent_au_milieu_de_parts_egales():
    """Chaque année validée tombe au milieu de sa part égale de l'étendue :
    distinctes, dans l'étendue, toutes quand la tranche la remplit."""
    assert G.annees_etalees(5, 39) == (3, 11, 19, 27, 35)
    assert G.annees_etalees(39, 39) == tuple(range(39))
    for cible in (5, 15, 25, 35):
        for etendue in range(cible, 45):
            annees = G.annees_etalees(cible, etendue)
            assert len(set(annees)) == cible and 0 <= min(annees) <= max(annees) < etendue


def test_une_carriere_courte_de_la_population_s_etale_sur_la_vie_active(simulateur, source):
    """Sous ``COURTES_ETALEES``, une carrière courte de la population valide sa
    durée — travail et périodes assimilées — en années espacées de son entrée à
    soixante ans, inactive entre elles et jusqu'au départ ; la grille des
    interruptions garde les premières années
    (``test_une_carriere_courte_s_arrete_a_la_duree_de_sa_tranche``). Celle
    d'un homme : celle d'une femme change de durée avec sa génération
    (``test_les_carrieres_des_femmes_suivent_la_duree_de_leur_generation``).
    Ses périodes assimilées sont celles de sa classe
    (``test_la_part_assimilee_suit_le_quintile_de_la_classe``)."""
    assert G.COURTES_ETALEES
    variantes = G.grille("population", simulateur.effectifs, source, ())
    courte = next(v for v in variantes if v.cas.code == f"{G.GABARIT}~h~10_20~p50")
    quintiles = G.quintiles_eqcc(simulateur.parametres.racine_donnees, residents=True)
    assert courte.duree == 15 and courte.assimilees == round(
        G.parts_assimilees_des_classes(quintiles, "H", "10_20")["p50"] * 15)
    generation = 1960
    carriere = courte.cas.construire(simulateur, generation)
    validees = [ligne.annee - generation for ligne in carriere.lignes
                if ligne.type_periode in ("emploi", "chomage_indemnise")]
    attendues = [int(courte.cas.age_debut) + d for d in G.annees_etalees(
        15, G.AGE_FIN_ETALEMENT - int(courte.cas.age_debut))]
    assert validees == attendues
    assert validees[0] < 25 and validees[-1] >= 55 and validees[-1] < G.AGE_FIN_ETALEMENT
    types = {ligne.type_periode for ligne in carriere.lignes
             if ligne.annee - generation not in validees}
    assert types == {"inactivite"}


def test_les_carrieres_des_femmes_suivent_la_duree_de_leur_generation(simulateur, source,
                                                                        parametres):
    """Sous ``DUREE_DES_FEMMES_SELON_LA_GENERATION``, les carrières incomplètes
    des femmes, hors des régimes statutaires, gagnent ou perdent les mêmes
    années à chaque génération, pour que la durée moyenne des femmes, comptée
    comme le calage la compte, soit celle que l'EIR mesure aux résidentes : 38
    années pour la génération 1950, partie à 60 ans. La génération 1935 en perd,
    celles de 1950 et de 1965 en gagnent ; les carrières pleines, les carrières
    statutaires et celles des hommes ne changent pas. Simulée, une carrière de
    dix à vingt ans valide ses années de chaque génération, une au moins, sans
    passer l'âge légal."""
    assert G.DUREE_DES_FEMMES_SELON_LA_GENERATION
    racine = parametres.racine_donnees
    variantes = G.grille("population", simulateur.effectifs, source, ())
    ecarts = G.ecarts_des_femmes(variantes, simulateur.effectifs, source, racine)
    assert ecarts[1935] < 0.0 < ecarts[1950] < ecarts[1965]
    femmes = G.femmes_ponderees(variantes, simulateur.effectifs, source)
    entree = G._par_generation(G.entrees_des_carrieres_pleines(racine)["F"], 1950, 21.0)
    assert G.duree_moyenne_des_femmes(femmes, ecarts[1950], 60.0, entree) == pytest.approx(
        G.durees_d_assurance(racine)[(1950, "F")], abs=1e-6)
    for v in variantes:
        assert bool(v.cas.cibles) == (v.cas.sexe == "F" and G.incomplete(v)), v.cas.code
    courte = next(v for v in variantes if v.cas.code == f"{G.GABARIT}~f~10_20~p50")
    assert G.annees_incompletes(courte, -40.0, 60.0) == 1.0
    assert G.annees_incompletes(courte, 40.0, 60.0) == 60.0 - courte.cas.age_debut
    validees = {}
    for generation in (1935, 1965):
        carriere = courte.cas.construire(simulateur, generation)
        validees[generation] = sum(1 for ligne in carriere.lignes
                                   if ligne.type_periode in ("emploi", "chomage_indemnise"))
        assert validees[generation] == round(
            G._par_generation(courte.cas.cibles, generation, 0.0)), generation
    assert validees[1935] < courte.duree < validees[1965]


@pytest.mark.usefixtures("sans_le_reperage_des_decotes")
def test_les_carrieres_allongees_entrent_comme_les_pleines(simulateur, source, parametres,
                                                           monkeypatch):
    """Sous ``ALLONGEES_COMME_LES_PLEINES``, la carrière incomplète d'une femme
    du salariat privé dont les années de sa génération ne tiennent pas entre
    21 ans, l'entrée du gabarit, et l'âge légal entre plus tôt : à l'âge légal
    moins ses années, jamais avant l'entrée des carrières pleines de sa
    génération, qui borne ses années ; puis, cinquième par cinquième, à l'âge
    où sa génération cotise son premier trimestre s'il vient plus tard, jamais
    après 21 ans, ses années bornées par l'âge légal. Nées en 1955, parties à
    62 ans, les carrières pleines entrent à 18 ans (62 − 44,4, arrondi) : la
    carrière de trente à quarante ans, que sa génération allonge de plus de
    neuf années, en valide 44, et non 41 ; les nées en 1955 cotisent leur
    premier trimestre aux rangs 0,1 à 0,9 à 16, 17, 18, 19 et 21 ans, et ses
    cinquièmes entrent à 18 ans pour trois, à 19 et à 21, pour 44, 43 et 41
    années. Celle de la classe p95, une année assimilée sur trente-neuf, au
    chômage, entrée à 18 ans, compte à 60 ans 168 trimestres cotisés ou
    réputés tels — quarante-deux années, dont les quatre trimestres de chômage
    que D. 351-1-2 répute depuis avril 2014 —, pour les 166 de sa génération :
    elle part à 60 ans en carrière longue ; entrée à 21 ans, à 62 ans au taux
    plein, comme avant. La carrière garde son poids ; celle de dix à vingt
    ans, qui tient entre 21 ans et l'âge légal, et celles des hommes gardent
    leur entrée ; les carrières pleines, leurs cinquièmes et leurs natures, que
    la masse assimilée des seules carrières pleines règle
    (``NATURES_SELON_LE_RANG``)."""
    assert G.ALLONGEES_COMME_LES_PLEINES
    racine = parametres.racine_donnees
    assert G._par_generation(G.entrees_des_carrieres_pleines(racine)["F"], 1955, 21.0) == 18.0
    parts = G.premiers_trimestres(racine)["F"]
    assert [G.age_du_premier_trimestre(parts, 1955, rang) for rang in (0.1, 0.3, 0.5, 0.7, 0.9)
            ] == [16, 17, 18, 19, 21]
    variantes = G.grille("population", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    trente = f"{G.GABARIT}~f~30_40~p95"
    classes = [v for v in variantes
               if v.cas.code == trente or v.cas.code.startswith(f"{trente}~entree")]
    total = sum(poids[v.cas.code] for v in classes)
    repartition: dict[tuple[float, float], float] = {}
    for v in classes:
        cle = (v.cas.debut_de(1955), G._par_generation(v.cas.cibles, 1955, 0.0))
        repartition[cle] = repartition.get(cle, 0.0) + poids[v.cas.code] / total
    assert repartition == pytest.approx({(18.0, 44.0): 0.6, (19.0, 43.0): 0.2,
                                         (21.0, 41.0): 0.2})
    projection = simulateur.pour_la_projection()
    tot = next(v for v in classes if v.cas.debut_de(1955) == 18.0)
    tard = next(v for v in classes if v.cas.debut_de(1955) == 21.0)
    lignes = tot.cas.carriere_a(simulateur, 1955, 62.0).lignes
    assert [l.annee - 1955 for l in lignes if l.type_periode in (
        "emploi", "chomage_indemnise")] == list(range(18, 62))
    assert sum(1 for l in lignes if l.type_periode == "chomage_indemnise") == 1
    assert G.condition_au_depart(projection, tot.cas, 1955) == (
        pytest.approx(60.0), "carriere_longue")
    assert G.condition_au_depart(projection, tard.cas, 1955) == (
        pytest.approx(62.0), "taux_plein_autre")
    par_code = {v.cas.code: v.cas for v in variantes}
    assert par_code[f"{G.GABARIT}~f~10_20~p50"].debut_de(1955) == 21
    assert par_code[f"{G.GABARIT}~h~30_40~p95"].debut_de(1955) == 21
    monkeypatch.setattr(G, "ALLONGEES_COMME_LES_PLEINES", False)
    avant = {v.cas.code: v for v in G.grille("population", simulateur.effectifs, source, ())}
    assert avant[trente].cas.debut_de(1955) == 21
    assert G._par_generation(avant[trente].cas.cibles, 1955, 0.0) == 41.0
    assert _poids(list(avant.values()), simulateur.effectifs,
                  source.millesime)[trente] == pytest.approx(total)
    assert {v.cas.code: v.cas for v in variantes if v.tranche == "40_plus"} == {
        code: v.cas for code, v in avant.items() if v.tranche == "40_plus"}


def test_les_quintiles_eqcc_se_lisent_dans_le_fichier_certifie(parametres):
    """Les quintiles de la pension en équivalent carrière complète de l'EIR
    2020 : 23,1 % des femmes du premier ont moins de dix années validées hors
    majorations, 0,4 % de celles du dernier."""
    quintiles = G.quintiles_eqcc(parametres.racine_donnees)
    assert quintiles[("q1", "part_duree_validee_hors_majoration_moins_10", "F")] == 23.1
    assert quintiles[("q5", "part_duree_validee_hors_majoration_moins_10", "F")] == 0.4
    assert quintiles[("ensemble", "effectifs", "ensemble")] == 16552.0


def test_le_rang_selon_la_duree_tient_les_marges_et_garde_l_association_de_l_eir(parametres):
    """Le tableau croisé de l'EIR redonne, à l'arrondi de ses parts près, le
    poids de chaque classe de centiles ; calé sur d'autres parts de tranches,
    il les prend, garde le poids des classes, et ses rapports croisés — la
    façon dont la durée et le rang vont ensemble."""
    quintiles = G.quintiles_eqcc(parametres.racine_donnees)
    classes = dict(G.CENTILES)
    parts = {"F": {"moins_10": 0.105, "10_20": 0.143, "20_30": 0.174, "30_40": 0.386,
                   "40_plus": 0.192},
             "H": {"moins_10": 0.035, "10_20": 0.047, "20_30": 0.068, "30_40": 0.286,
                   "40_plus": 0.564}}
    rangs = G.rangs_selon_la_duree(quintiles, parts)
    for sexe in ("F", "H"):
        graine = G.association_rang_duree(quintiles, sexe)
        for nom, poids in classes.items():
            assert sum(cases[nom] for cases in graine.values()) == pytest.approx(poids, abs=2e-3)
            assert sum(parts[sexe][t] * rangs[sexe][t][nom] for t in parts[sexe]) == (
                pytest.approx(poids, abs=1e-9))
        for tranche, poids in rangs[sexe].items():
            assert sum(poids.values()) == pytest.approx(1.0, abs=1e-12)

        def croise(table, t1, t2, c1, c2):
            return table[t1][c1] * table[t2][c2] / (table[t1][c2] * table[t2][c1])

        for t1, t2, c1, c2 in (("moins_10", "40_plus", "p10", "p75"),
                               ("10_20", "30_40", "p25", "p90")):
            assert croise(rangs[sexe], t1, t2, c1, c2) == pytest.approx(
                croise(graine, t1, t2, c1, c2), rel=1e-6)
        assert rangs[sexe]["moins_10"]["p10"] > 2 * rangs[sexe]["40_plus"]["p10"]


def test_les_retraites_au_minimum_se_rangent_au_premier_quintile(monkeypatch):
    """Sous ``MINIMUM_AU_PREMIER_QUINTILE``, la part de chaque quintile au
    minimum rejoint, avec ses tranches, la bande du premier. Cinq quintiles
    égaux, le premier de carrières courtes, les autres de longues, la moitié
    du deuxième au minimum : la bande du bas couvre trois dixièmes des rangs,
    dont un tiers de longues carrières ; chaque classe garde son poids.
    Débrayé, les longues carrières n'ont aucun rang du premier quintile."""
    quintiles = {}
    for rang, q in enumerate(G.QUINTILES_EQCC):
        quintiles[(q, "effectifs", "F")] = 100.0
        quintiles[(q, "part_minimum_pension_regime_principal", "F")] = 50.0 if rang == 1 else 0.0
        dominante = "moins_10" if rang == 0 else "40_plus"
        for tranche, _ in G.TRANCHES:
            quintiles[(q, f"part_duree_validee_hors_majoration_{tranche}", "F")] = (
                100.0 if tranche == dominante else 0.0)
    tableau = G.association_rang_duree(quintiles, "F")
    bas = dict(G.CENTILES)["p10"]
    assert tableau["moins_10"]["p10"] == pytest.approx(0.2 * bas / 0.3)
    assert tableau["40_plus"]["p10"] == pytest.approx(0.1 * bas / 0.3)
    for nom, part in G.CENTILES:
        assert sum(cases[nom] for cases in tableau.values()) == pytest.approx(part)
    monkeypatch.setattr(G, "MINIMUM_AU_PREMIER_QUINTILE", False)
    assert G.association_rang_duree(quintiles, "F")["40_plus"]["p10"] == 0.0


def test_la_population_donne_aux_carrieres_courtes_le_rang_de_leur_duree(
        simulateur, source, parametres):
    """Sous ``RANG_SELON_LA_DUREE``, chaque tranche de durée du salariat privé
    prend les classes de centiles dans la proportion calée sur l'EIR, la part
    de sa classe du bas au Smic toute la carrière comprise ; toutes tranches
    réunies, chaque classe garde son poids."""
    assert G.RANG_SELON_LA_DUREE
    effectifs = simulateur.effectifs
    avant = G.interruptions(G.melees(G.personnes(G.reference_population(), effectifs, source),
                                     source), effectifs, source,
                            de_tous=G.COURTES_A_LA_PART_DE_TOUS, etalees=G.COURTES_ETALEES)
    rangs = G.rangs_selon_la_duree(G.quintiles_eqcc(parametres.racine_donnees,
                                                    residents=G.DUREES_DES_RESIDENTS),
                                   G.parts_des_tranches(avant))
    variantes = G.grille("population", effectifs, source, ())
    poids = _poids(variantes, effectifs, source.millesime)
    for sexe in ("F", "H"):
        par: dict = {}
        for v in variantes:
            if v.cas.sexe != sexe or not v.cas.code.startswith(f"{G.GABARIT}~"):
                continue
            classe = next(c for c in v.cas.code.split("~") if c in dict(G.CENTILES))
            par.setdefault(v.tranche, {}).setdefault(classe, 0.0)
            par[v.tranche][classe] += poids[v.cas.code]
        total = sum(sum(cases.values()) for cases in par.values())
        for nom, part in G.CENTILES:
            assert sum(cases[nom] for cases in par.values()) / total == pytest.approx(
                part, abs=1e-9), (sexe, nom)
        for tranche, cases in par.items():
            masse = sum(cases.values())
            for nom, _ in G.CENTILES:
                assert cases[nom] / masse == pytest.approx(rangs[sexe][tranche][nom],
                                                           abs=1e-9), (sexe, tranche, nom)


def test_une_grille_se_range_en_quintiles_comme_l_eir(parametres):
    """Dix carrières de même poids : les bornes tombent au deuxième, quatrième,
    sixième et huitième montant, deux carrières par quintile ; une carrière à
    cheval sur une borne va au quintile de son milieu. Contre l'EIR, une tranche
    rangée tout en bas a toute sa masse au premier quintile ; les carrières au
    minimum se comptent dans leur quintile, sexe par sexe, et la proratisation
    s'y moyenne."""
    lignes = [(float(montant), 1.0, "F" if montant % 2 else "H",
               "moins_10" if montant <= 2 else "40_plus") for montant in range(1, 11)]
    rangees = G.quintiles_ponderes(lignes)
    assert rangees["bornes"] == [2.0, 4.0, 6.0, 8.0]
    assert rangees["masses"]["ensemble"]["40_plus"] == [0.0, 2.0, 2.0, 2.0, 2.0]
    a_cheval = G.quintiles_ponderes([(1.0, 1.0, "F", "40_plus"), (2.0, 3.0, "F", "40_plus"),
                                     (3.0, 1.0, "F", "40_plus")])
    assert a_cheval["masses"]["F"]["40_plus"] == [1.0, 0.0, 3.0, 0.0, 1.0]
    confrontee = G.confronter_eqcc(lignes, G.quintiles_eqcc(parametres.racine_donnees))
    assert confrontee["F"]["tranches"]["moins_10"]["premier_quintile"] == 1.0
    assert confrontee["F"]["tranches"]["moins_10"]["premier_quintile_eir"] == pytest.approx(
        0.805, abs=1e-3)
    au_minimum = [ligne + (ligne[0] <= 3.0,) for ligne in lignes]
    assert G.quintiles_ponderes(au_minimum)["minima"]["ensemble"] == [2.0, 1.0, 0.0, 0.0, 0.0]
    confrontee = G.confronter_eqcc(au_minimum, G.quintiles_eqcc(parametres.racine_donnees))
    assert confrontee["F"]["minimum"] == [1.0, 1.0, 0.0, 0.0, 0.0]
    assert confrontee["H"]["minimum"] == [1.0, 0.0, 0.0, 0.0, 0.0]
    assert confrontee["F"]["minimum_eir"][1] == pytest.approx(0.599, abs=1e-3)
    assert confrontee["F"]["minimum_ensemble"] == pytest.approx(0.4)
    assert confrontee["H"]["minimum_ensemble"] == pytest.approx(0.2)
    assert confrontee["F"]["minimum_ensemble_eir"] == pytest.approx(0.385, abs=1e-3)
    proratisees = [ligne + (0.5 if ligne[0] <= 2.0 else 1.0,) for ligne in au_minimum]
    confrontee = G.confronter_eqcc(proratisees, G.quintiles_eqcc(parametres.racine_donnees))
    assert confrontee["F"]["proratisation"] == [0.5, 1.0, 1.0, 1.0, 1.0]
    assert confrontee["H"]["proratisation"] == [0.5, 1.0, 1.0, 1.0, 1.0]
    assert confrontee["H"]["proratisation_eir"][4] == pytest.approx(0.985, abs=1e-3)
    assert confrontee["F"]["duree_validee"] == [None] * 5
    validees = [ligne + (20.0 if ligne[0] <= 2.0 else 40.0,) for ligne in proratisees]
    residents = G.quintiles_eqcc(parametres.racine_donnees, residents=True)
    confrontee = G.confronter_eqcc(validees, residents)
    assert confrontee["F"]["duree_validee"] == [20.0, 40.0, 40.0, 40.0, 40.0]
    assert confrontee["F"]["duree_validee_eir"] == [28.0, 38.0, 41.0, 41.0, 41.0]
    assert confrontee["F"]["minimum_eir"][1] == pytest.approx(0.527, abs=1e-3)
    groupes = [ligne + ("fonction_publique_etat_militaire" if ligne[0] >= 7.0
                        else "regime_general",) for ligne in validees]
    militaires = G.confronter_eqcc(groupes, residents)["H"]["groupes"][
        "fonction_publique_etat_militaire"]
    assert militaires["grille"] == [0.0, 0.0, 0.0, 0.5, 0.5]
    assert militaires["eir"][0] == 0.0 and sum(militaires["eir"]) == pytest.approx(1.0)
    assert militaires["eir"][3] > 0.4
    assert G.confronter_eqcc(groupes, G.quintiles_eqcc(parametres.racine_donnees))["H"][
        "groupes"] == {}


def test_la_population_prend_les_durees_des_residents(simulateur, source, parametres):
    """Sous ``DUREES_DES_RESIDENTS``, la population prend les durées des seuls
    résidents en France — 1,0 % des hommes résidents valident moins de dix
    années hors majorations, 2,7 % de tous les retraités —, et le reste chez
    tous : la part des femmes, celle des régimes. Sa composition redonne la part
    des carrières de moins de trente années des résidents ; la durée des
    carrières pleines reste celle de tous."""
    assert G.DUREES_DES_RESIDENTS
    racine = parametres.racine_donnees
    tous = G.CaracteristiquesRetraites(racine)
    assert source.valeur("part_duree_validee_hors_majoration_moins_10", "H") == 1.0
    assert tous.valeur("part_duree_validee_hors_majoration_moins_10", "H") == 2.7
    assert source.valeur("effectifs", "F") == tous.valeur("effectifs", "F")
    assert source.millesime == tous.millesime
    composition = G.composition(G.grille("population", simulateur.effectifs, source, ()),
                                simulateur.effectifs, source)
    residents = G.quintiles_eqcc(racine, residents=True)
    for sexe in ("F", "H"):
        courtes = sum(residents[("ensemble", f"part_duree_validee_hors_majoration_{t}", sexe)]
                      for t in ("moins_10", "10_20", "20_30")) / sum(
            residents[("ensemble", f"part_duree_validee_hors_majoration_{t}", sexe)]
            for t, _ in G.TRANCHES)
        assert composition["moins_de_30_ans"][sexe] == pytest.approx(courtes, abs=1e-9), sexe


def test_les_quintiles_des_residents_se_lisent_dans_le_fichier_certifie(parametres):
    """Les quintiles des seuls résidents en France, contre lesquels la
    population se mesure : chacun en compte le cinquième, et ils sont moins
    nombreux que tous les retraités ; 52,7 % des résidentes du deuxième sont au
    minimum de leur régime principal, 17,5 % de celles du premier sont parties
    avec une décote, et elles y cotisent moins d'années qu'elles n'en
    valident. Les militaires monopensionnés font 5,8 % des hommes du
    quatrième, et aucun du premier : sa case vide se lit zéro."""
    residents = G.quintiles_eqcc(parametres.racine_donnees, residents=True)
    effectifs = [residents[(q, "effectifs", "ensemble")] for q in G.QUINTILES_EQCC]
    assert max(effectifs) - min(effectifs) <= 0.01 * min(effectifs)
    tous = G.quintiles_eqcc(parametres.racine_donnees)
    assert (residents[("ensemble", "effectifs", "ensemble")]
            < tous[("ensemble", "effectifs", "ensemble")])
    assert residents[("q2", "part_minimum_pension_regime_principal", "F")] == 52.7
    assert residents[("q1", "part_decote", "F")] == 17.5
    assert residents[("q1", "duree_cotisee", "F")] < residents[("q1", "duree_validee", "F")]
    assert residents[("q4", "part_mono_fonction_publique_etat_militaire", "H")] == 5.8
    assert residents[("q1", "part_mono_fonction_publique_etat_militaire", "H")] == 0.0


def test_la_duree_validee_se_lit_generation_par_generation(parametres):
    """Chaque génération simulée moyenne la durée validée de ses cohortes, à
    leur poids, et se lit contre la durée d'assurance que l'EIR mesure, en
    moyenne des générations qu'elle représente : celle des femmes nées autour
    de 1950 y monte à 38,0 années, majorations comprises."""
    publiees = G.durees_d_assurance(parametres.racine_donnees)
    assert publiees[(1953, "F")] == pytest.approx(158.0 / 4.0)
    lignes = [(1950, "F", 30.0, 1.0), (1950, "F", 40.0, 3.0), (1955, "F", 20.0, 4.0),
              (1950, "H", 41.0, 2.0)]
    durees = G.durees_par_generation(lignes, publiees)
    premiere, seconde = durees["F"]
    assert premiere["generation"] == 1950 and premiere["annees"] == pytest.approx(37.5)
    assert premiere["part"] == pytest.approx(0.5) and seconde["part"] == pytest.approx(0.5)
    voisines = [publiees[(g, "F")] for g in range(1950 - G.C._DEMI_TRANCHE,
                                                  1950 + G.C._DEMI_TRANCHE + 1)]
    assert premiere["eir"] == pytest.approx(sum(voisines) / len(voisines))
    assert premiere["eir"] == pytest.approx(38.0, abs=0.5)
    assert durees["H"][0]["annees"] == 41.0


def test_chaque_caisse_reelle_se_divise_par_les_tetes_de_ses_variantes():
    """La page divise chaque caisse par les têtes de ses cas types, pesées de
    leurs parts (action 138, étape 3) ; la grille donne à chaque variante sa
    pseudo-caisse, que ``poids_effectifs`` diviserait par ses seules têtes.
    Ses têtes sont donc celles de ses caisses RÉELLES, de quoi la diviser
    comme la page : la moyenne des têtes des variantes qui réclament chacune,
    pesées de leurs parts positives. Posé à la main, la caisse A de 300
    retraités, pour six dixièmes à X, 2 000 têtes, trois à Y, 1 000, un à W,
    500 : 1 550 têtes, comme à la page ; la caisse B de 100 retraités, à Z
    seul, 1 500 têtes, dont W retire un dixième, comme ``personnes`` retire de
    la Cnav ses contractuels : W divise 30 − 10 = 20 retraités en
    30 / 1 550 − 10 / 1 500. Sans retraités, ses propres têtes."""
    from types import SimpleNamespace

    def variante(code: str, *parts) -> SimpleNamespace:
        return SimpleNamespace(cas=SimpleNamespace(code=code), retraites=parts)

    class Effectifs:
        def effectif(self, caisse: str, annee: int) -> float:
            return {"A": 300.0, "B": 100.0, "C": 0.0}[caisse]

    variantes = [variante("X", ("A", 0.6)), variante("Y", ("A", 0.3)),
                 variante("Z", ("B", 1.0)), variante("W", ("A", 0.1), ("B", -0.1)),
                 variante("V", ("C", 1.0))]
    propres = {"X": 2_000.0, "Y": 1_000.0, "Z": 1_500.0, "W": 500.0, "V": 800.0}
    tetes = G.tetes_des_caisses_reelles(variantes, Effectifs())(lambda annee: propres)
    assert tetes(2024) == pytest.approx({"X": 1_550.0, "Y": 1_550.0, "Z": 1_500.0,
                                         "W": 20 / (30 / 1_550 - 10 / 1_500), "V": 800.0})


def test_la_grille_du_depot_reecrite_redonne_la_page(parametres):
    """Les pseudo-caisses et la grille simulée à part donnent la page au
    millième : la mesure ne mesure rien d'autre que la grille. Depuis que la
    page divise chaque caisse par les têtes de ses cas types (action 138,
    étape 3), la grille divise les siennes par celles de ses caisses réelles
    (``tetes_des_caisses_reelles``)."""
    page = G.indicateurs(memoire.cout(parametres))
    en_parts = G.indicateurs(G.calculer(parametres, G.reference()))
    assert G.ecart_maximal(en_parts, page) < 1e-6


# -- la distribution de l'année de l'enquête (action 138, étape 14) -------------

def test_le_quantile_d_une_grille_est_l_un_de_ses_montants():
    """Une grille est faite d'atomes, une carrière et son montant : son quantile
    est le plus petit montant sous lequel tombe au moins le rang du poids."""
    lot = [(300.0, 2.0), (100.0, 1.0), (200.0, 1.0)]
    assert G.quantile_pondere(lot, 0.25) == 100.0
    assert G.quantile_pondere(lot, 0.5) == 200.0
    assert G.quantile_pondere(lot, 0.51) == 300.0
    assert G.part_sous(lot, 200.0) == pytest.approx(0.25)
    assert G.part_sous(lot, 250.0) == pytest.approx(0.5)


def test_les_artisans_se_confrontent_aux_anciens_artisans_de_l_eir(parametres):
    """La pension des artisans d'une grille contre celle des anciens artisans
    et commerçants de l'EIR (fiche 1.11 de l'INSEE) : leur part parmi les
    retraités de leur sexe, leur moyenne et leurs quartiles, chacun contre le
    sien ; et chaque quartile rapporté à celui de tous les retraités du sexe,
    dans la grille comme dans la fiche, dont les quartiles de tous ne sont
    pas ceux de la DREES."""
    publiees = G.pensions_non_salaries(parametres.racine_donnees)
    assert publiees[("artisans_commercants", "H", "mediane")] == 1440.0
    lignes = [(600.0, 1.0, "F", "artisan"), (900.0, 1.0, "F", "artisan"),
              (1200.0, 2.0, "F", "artisan"), (1000.0, 6.0, "F", G.GABARIT),
              (1500.0, 1.0, "H", "artisan"), (2000.0, 9.0, "H", G.GABARIT)]
    mesure = G.confronter_non_salaries(lignes, publiees)["artisans_commercants"]
    femmes = mesure["F"]
    assert femmes["part"] == pytest.approx(4 / 10)
    assert femmes["part_eir"] == pytest.approx(140 / 8450)
    assert femmes["moyenne"] == pytest.approx((600 + 900 + 2 * 1200) / 4)
    assert femmes["moyenne_eir"] == 820.0
    assert femmes["quantiles"] == {"q1": 600.0, "mediane": 900.0, "q3": 1200.0}
    assert femmes["quantiles_eir"] == {"q1": 520.0, "mediane": 870.0, "q3": 1230.0}
    assert femmes["relatifs"]["mediane"] == pytest.approx(900 / 1000)
    assert femmes["relatifs_eir"]["mediane"] == pytest.approx(870 / 1140)
    assert mesure["ensemble"]["part"] == pytest.approx(5 / 20)
    assert mesure["ensemble"]["part_eir"] == pytest.approx(500 / 15650)


def test_la_distribution_compte_les_tetes_et_les_euros_de_la_page(parametres):
    """La distribution de l'année est la population de la page, en têtes : ses
    poids somment les têtes que ``cout._masses`` compte, et ses montants, la
    complétude des cohortes ôtée, la masse du scénario 1, des euros constants
    à ceux de l'année et au mois près."""
    from dataclasses import replace

    grille = G.en_tetes(parametres, G.reference())
    annee = 2020
    lignes = grille.pensions(annee)
    entieres = [replace(p, completudes=()) for p in grille.pensionnes]
    masses, _, tetes = C._masses(entieres, grille.population, annee,
                                 grille.poids(annee), grille.revalorisation)
    vers = grille.macro.coefficient_prix(parametres.annee_euros_constants, annee) / 12
    assert sum(p for _, p, _ in lignes) == pytest.approx(tetes[C.TETES_TOUTES], rel=1e-12)
    assert sum(m * p for m, p, _ in lignes) == pytest.approx(masses["actuel"] * vers,
                                                             rel=1e-12)
    assert {s for _, _, s in lignes} == {"F", "H"}


def test_les_tetes_se_lisent_sur_des_couples_alleges(parametres):
    """La mesure garde tous les couples simulés de sa grille : la population de
    la vingt-sixième version, 11 188 cas types de 28 générations, en 56
    morceaux de 177 Mo chacun en mémoire, passait les 15 Go du conteneur, ses
    quatre workers et leurs portages en sus. Les têtes ne lisent d'un couple
    que son code, sa génération, ses départs, sa pension du scénario 1, les
    parts de ses régimes, sa complétude et sa survie : ``alleges`` les leur
    donne sans la proposition, son autre côté ni ses cotisations, et leurs
    survies en tableaux de flottants (``alleger``), 36 Mo le morceau. La
    grille du dépôt en tire les mêmes poids, les mêmes pensions et les mêmes
    départs."""
    from array import array

    entiers = G.en_tetes(parametres, G.reference())
    alleges = G.en_tetes(parametres, G.reference(), alleges=True)
    for entier, allege in zip(entiers.pensionnes, alleges.pensionnes, strict=True):
        assert (allege.propre, allege.autre, allege.cotisations) == (None, None, None)
        assert all(isinstance(courbe, array) for courbe in allege.survies)
        assert [list(courbe) for courbe in allege.survies] == [
            list(courbe) for courbe in entier.survies]
        assert (allege.code, allege.generation, allege.annee_liquidation, allege.pensions,
                allege.parts_regimes, allege.completudes, allege.departs) == (
            entier.code, entier.generation, entier.annee_liquidation, entier.pensions,
            entier.parts_regimes, entier.completudes, entier.departs)
    for annee in (2020, 2030):
        assert alleges.poids(annee) == entiers.poids(annee)
        assert alleges.pensions(annee) == entiers.pensions(annee)
    publies = G.departs_publies(parametres.racine_donnees)
    assert G.departs(parametres, alleges, publies) == G.departs(parametres, entiers, publies)


def test_la_mesure_pese_chaque_cohorte_de_la_part_de_sa_generation(parametres):
    """La mesure pèse chaque cohorte de la part que sa génération donne à sa
    carrière (``GrilleEnTetes.parts``, :data:`DECOTE_SELON_LA_GENERATION`),
    la cohorte comptée à son année de naissance : les pensions de l'année,
    et les départs des générations qu'elle confronte à l'EIR. Sans part,
    une ; la grille du dépôt n'en a pas."""
    grille = G.en_tetes(parametres, G.reference())
    assert grille.parts == {}
    code = grille.cas_types[0].code
    generations = sorted({p.generation for p in grille.pensionnes if p.code == code})
    coupure = generations[len(generations) // 2]
    pesee = replace(grille, parts={code: ((0, 3.0), (coupure - C._DEMI_TRANCHE, 0.5))})
    for annee in (2020, 2040):
        for (p, m, w), (q, n, x) in zip(grille.cohortes(annee), pesee.cohortes(annee),
                                        strict=True):
            assert (p.code, p.generation, m) == (q.code, q.generation, n)
            facteur = 1.0 if p.code != code else (3.0 if p.generation < coupure else 0.5)
            assert x == pytest.approx(facteur * w, rel=1e-12)
    publies = G.departs_publies(parametres.racine_donnees)
    hommes = {cas.code for cas in grille.cas_types if cas.sexe == "H"}
    sans_les_hommes_d_apres_1952 = replace(
        grille, parts={c: ((0, 1.0), (1953, 0.0)) for c in hommes})
    base = G.departs(parametres, grille, publies)
    mesure = G.departs(parametres, sans_les_hommes_d_apres_1952, publies)
    assert mesure["1950"] == base["1950"]
    assert "H" in base["1955"] and "H" not in mesure["1955"]
    assert mesure["1955"]["F"] == base["1955"]["F"]


def test_la_mesure_appliquee_a_l_enquete_redonne_l_enquete(parametres):
    """L'enquête, mise en atomes au milieu de ses tranches de cent euros, se
    confronte à elle-même sans écart aux bornes des tranches, et ses quantiles
    redonnent ceux que la DREES publie à une tranche près — l'atome est au
    milieu de la sienne, et la soustraction des résidents à l'étranger
    (``DistributionPensions``) n'est exacte qu'à quelques dizaines d'euros :
    la mesure ne mesure que la grille."""
    from retraite_notionnelle.donnees.distribution import (DistributionPensions,
                                                           ResidenceRetraites)

    racine = parametres.racine_donnees
    residence = ResidenceRetraites(racine, 2020)
    distributions = {sexe: DistributionPensions(racine, sexe, 2020, "france")
                     for sexe in G.SEXES}
    lignes = []
    for sexe in ("F", "H"):
        effectif = residence.valeur("france", "effectifs", sexe)
        for tranche in distributions[sexe].tranches:
            milieu = (tranche.borne_inferieure + 50.0 if not tranche.ouverte
                      else tranche.borne_inferieure + 1000.0)
            lignes.append((milieu, tranche.part * effectif, sexe))
    mesure = G.confronter(lignes, residence, distributions)
    for sexe in ("F", "H"):
        lue = mesure[sexe]
        assert abs(lue["kolmogorov"]) < 1e-9, sexe
        # Les effectifs publiés sont arrondis au millier : 15 647 milliers de
        # résidents, quand les deux sexes en font 15 648.
        assert lue["part"] == pytest.approx(lue["part_eir"], rel=1e-4)
        for code, publie in lue["quantiles_eir"].items():
            assert abs(lue["quantiles"][code] - publie) < 100.0, (sexe, code)
    # L'ensemble n'est pas le mélange des deux sexes au poids des effectifs à
    # mieux que quelques dixièmes de point : les parts publiées sont arrondies.
    assert abs(mesure["ensemble"]["kolmogorov"]) < 5e-3


def test_une_part_des_carrieres_incompletes_part_avec_une_decote(simulateur, source,
                                                                  parametres):
    """Sous ``DEPARTS_AVEC_DECOTE``, chaque carrière incomplète du salariat et
    des non-salariés se dédouble : une part, la même pour tout le sexe, part à
    l'ouverture du droit. Ses départs pèsent, parmi tous les retraités du sexe,
    la part des départs avec décote que l'EIR mesure aux résidents — 8,8 % des
    femmes, 4,5 % des hommes. Un tel départ part avec une décote, une carrière
    pleine ou statutaire garde son départ, et partir plus tôt que le taux plein
    n'est pas partir décoté : l'agent de conduite né en 1958 part à cinquante
    ans à 75 %, celui né en 1962 en dessous."""
    assert G.DEPARTS_AVEC_DECOTE
    residents = G.quintiles_eqcc(parametres.racine_donnees, residents=True)
    variantes = G.grille("population", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    for sexe in ("F", "H"):
        du_sexe = [v for v in variantes if v.cas.sexe == sexe]
        part = (sum(poids[v.cas.code] for v in du_sexe if v.decote)
                / sum(poids[v.cas.code] for v in du_sexe))
        assert part == pytest.approx(residents[("ensemble", "part_decote", sexe)] / 100.0,
                                     abs=1e-9), sexe
    assert all(G.incomplete(v) and v.cas.regle_liquidation == "ouverture"
               for v in variantes if v.decote)
    assert not any(v.decote for v in variantes if v.tranche == "40_plus"
                   or v.groupe not in G.GROUPES_INTERROMPUS)
    projection = simulateur.pour_la_projection()

    def decotee(cas, generation):
        taux = projection.echeancier(cas.construire(projection, generation)
                                     ).au_depart.taux_liquidation
        return G.avec_decote(projection, cas, generation, taux)

    courte = next(v for v in variantes if v.decote and v.cas.sexe == "F"
                  and v.tranche == "20_30" and v.groupe == "regime_general")
    assert decotee(courte.cas, 1950)
    pleine = next(v for v in variantes if not v.decote and v.tranche == "40_plus")
    assert not decotee(pleine.cas, 1950)
    conduite = next(v for v in variantes if v.cas.code.startswith("agent_sncf_conduite"))
    assert conduite.cas.regle_liquidation == "ouverture"
    assert not decotee(conduite.cas, 1958) and decotee(conduite.cas, 1962)


def _decotes_attendues(racine: Path, generations: tuple[int, ...]) -> dict[str, dict[int, float]]:
    """La part des départs avec décote de chacune de ces ``generations`` parmi
    tous les retraités du sexe (``DECOTE_SELON_LA_GENERATION``), refaite à la
    main des fichiers certifiés de l'EIR, du témoin de l'EACR et de la
    pyramide de l'INSEE."""
    import json

    from retraite_notionnelle.donnees.population import Population

    publies = G.departs_publies(racine)
    residents = G.quintiles_eqcc(racine, residents=True)
    temoin = Path(__file__).resolve().parent / "temoins" / "drees_eacr_tables_2026.json"
    flux = json.loads(temoin.read_text(encoding="utf-8"))[
        "conditions_liquidation"]["series"]["0015"]["flux"]
    pyramide = Population(racine)
    parties = {g: pyramide.effectif(2020 - g, 2020) for g in range(1900, 1954)}
    attendues: dict[str, dict[int, float]] = {}
    for sexe in ("F", "H"):
        de_1950 = publies[(1950, "condition", "decote", sexe, "part")] / 100.0
        de_1953 = publies[(1953, "condition", "decote", sexe, "part")] / 100.0
        ligne = flux[sexe]["2024"]
        du_flux = ligne["decote"] / (ligne["decote"] + ligne["taux_plein"] + ligne["surcote"])

        def part(g: int, avant: float) -> float:
            if g < 1950:
                return avant
            if g <= 1953:
                return de_1950 + (de_1953 - de_1950) * (g - 1950) / 3
            if g >= 1960:
                return du_flux
            return de_1953 + (du_flux - de_1953) * (g - 1953) / 7

        stock = residents[("ensemble", "part_decote", sexe)] / 100.0
        anciennes = sum(e for g, e in parties.items() if g < 1950)
        avant = (stock * sum(parties.values())
                 - sum(e * part(g, 0.0) for g, e in parties.items() if g >= 1950)) / anciennes
        attendues[sexe] = {g: part(g, avant) for g in generations}
    return attendues


def test_la_part_des_departs_avec_decote_suit_la_generation(simulateur, source, parametres,
                                                           monkeypatch):
    """Sous ``DECOTE_SELON_LA_GENERATION``, la part des départs avec décote suit
    la génération, sexe par sexe, parmi tous les retraités du sexe : celle que
    l'EIR mesure aux nés en 1950 — 7,9 % des femmes, 5,6 % des hommes — et aux
    nés en 1953 — 12,4 et 8,6 % —, en droite ligne entre les deux ; celle des
    liquidants de la Cnav de 2024 (EACR, table H) — 13,7 et 13,0 % —, depuis la
    génération 1960, en droite ligne depuis 1953, comme la grille du coût ;
    avant 1950, celle qui garde aux générations que 2020 voit toutes parties,
    jusqu'à celle de 1953, pesées de leur effectif INSEE de 2020, la part que
    l'EIR mesure aux résidents, 8,8 et 4,5 % : 8,3 et 3,6 %. Les deux jumelles
    de chaque carrière incomplète gardent leur poids, celui de la quinzième
    version ; chacune porte la part que chaque génération donne à ce poids :
    génération par génération, les départs avec décote pèsent parmi tous les
    retraités du sexe la part de leur génération, et chaque carrière ce
    qu'elle pèse. Sans la version, une part partout, et la décote de 2020 à
    toutes les générations. La version seule, rapportée à toutes les carrières
    incomplètes : la trentième, qui la rapporte à celles qui peuvent décoter,
    a son test."""
    racine = parametres.racine_donnees
    residents = G.quintiles_eqcc(racine, residents=True)
    attendues = _decotes_attendues(racine, (1925, 1949, 1950, 1952, 1953, 1955, 1958, 1960,
                                            1980))
    assert attendues["F"][1950] == pytest.approx(0.079)
    assert attendues["H"][1953] == pytest.approx(0.086)
    assert attendues["F"][1960] == pytest.approx(46637 / (46637 + 226331 + 66672))
    assert attendues["H"][1980] == pytest.approx(40139 / (40139 + 212871 + 55696))
    assert attendues["F"][1925] == pytest.approx(0.083, abs=5e-4)
    assert attendues["H"][1925] == pytest.approx(0.036, abs=5e-4)
    decotes = G.decotes_des_generations(racine)
    for sexe, parts in attendues.items():
        for g, attendue in parts.items():
            assert G._par_generation(decotes[sexe], g, 0.0) == pytest.approx(
                attendue, rel=1e-9), (sexe, g)

    def pesees(variantes, poids, generation: int, sexe: str) -> tuple[float, float, float]:
        du_sexe = [v for v in variantes if v.cas.sexe == sexe]
        siennes = {v.cas.code: poids[v.cas.code] * v.part_de_la_generation(generation)
                   for v in du_sexe}
        return (sum(siennes[v.cas.code] for v in du_sexe if v.decote),
                sum(siennes.values()), sum(poids[v.cas.code] for v in du_sexe))

    assert G.DECOTE_SELON_LA_GENERATION
    monkeypatch.setattr(G, "DECOTE_DES_CARRIERES_QUI_LE_PEUVENT", False)
    variantes = G.grille("population", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    for sexe, parts in attendues.items():
        for g, attendue in parts.items():
            decotees, toutes, sans_part = pesees(variantes, poids, g, sexe)
            assert decotees / toutes == pytest.approx(attendue, rel=1e-6), (sexe, g)
            assert toutes == pytest.approx(sans_part, rel=1e-9), (sexe, g)
    assert all(v.part_de_la_generation(1952) == 1.0 for v in variantes if not G.incomplete(v))
    monkeypatch.setattr(G, "DECOTE_SELON_LA_GENERATION", False)
    sans = G.grille("population", simulateur.effectifs, source, ())
    assert all(v.part_de_la_generation(g) == 1.0 for v in sans for g in (1925, 1955, 1980))
    poids = _poids(sans, simulateur.effectifs, source.millesime)
    for sexe in ("F", "H"):
        decotees, toutes, _ = pesees(sans, poids, 1955, sexe)
        assert decotees / toutes == pytest.approx(
            residents[("ensemble", "part_decote", sexe)] / 100.0, abs=1e-9)


def test_une_carriere_decote_a_l_ouverture_quand_le_droit_l_y_ouvre_avant_son_taux_plein(
        simulateur, source):
    """Une carrière qui part au taux plein décoterait à l'ouverture du droit
    (``decote_a_l_ouverture``) quand le droit de sa génération l'y ouvre avant
    son taux plein. Né en 1955, l'homme d'une carrière de vingt-cinq années a
    100 des 166 trimestres de sa génération à 62 ans, l'âge légal (L. 161-17-2),
    et n'a le taux plein qu'à 67 ans (L. 351-8, 1°) : il décoterait. Née en
    1955, la femme d'une carrière de trente à quarante ans, que sa génération
    porte à 44 années validées (``DUREE_DES_FEMMES_SELON_LA_GENERATION``), en a
    176, et les huit trimestres de chacun de ses deux enfants (L. 351-4) la
    mènent à 192 : elle a le taux plein dès 62 ans, et ne décoterait pas. Née
    en 1925, la même carrière n'a que 32 années, 144 trimestres avec ses
    enfants, des 150 que le taux plein demande à 60 ans depuis 1983 : elle
    décoterait. Une carrière qui part à l'ouverture de son statut y décote
    quand elle y prend un taux plus bas que son taux plein (``avec_decote``) :
    l'agent des IEG né en 1955 part à 55 ans, en 2010, au taux de 75 %, la
    décote des régimes spéciaux ne mordant pas encore ; né en 1965, il part à
    56 ans et 4 mois, au taux de 60 %."""
    variantes = G.grille("population", simulateur.effectifs, source, ())
    par_code = {v.cas.code: v.cas for v in variantes}
    projection = simulateur.pour_la_projection()
    homme = par_code[f"{G.GABARIT}~h~20_30~p50"]
    femme = par_code[f"{G.GABARIT}~f~30_40~p50"]
    assert G._par_generation(femme.cibles, 1955, 0.0) == 44.0
    assert G._par_generation(femme.cibles, 1925, 0.0) == 32.0
    assert G.decote_a_l_ouverture(projection, homme, 1955)
    assert not G.decote_a_l_ouverture(projection, femme, 1955)
    assert G.decote_a_l_ouverture(projection, femme, 1925)
    agent = par_code["agent_ieg~mono~h~p50"]
    assert agent.regle_liquidation == "ouverture"
    assert not G.decote_a_l_ouverture(projection, agent, 1955)
    assert G.decote_a_l_ouverture(projection, agent, 1965)


def test_la_part_des_departs_avec_decote_se_rapporte_aux_carrieres_qui_peuvent_decoter(
        simulateur, source, parametres):
    """Sous ``DECOTE_DES_CARRIERES_QUI_LE_PEUVENT``, la part des départs avec
    décote de chaque génération se rapporte aux seules carrières incomplètes
    qui peuvent décoter à l'ouverture du droit (``decote_a_l_ouverture``),
    comme la grille du coût (``facteurs_depense.part_avec_decote``), et non à
    toutes ; elle se prend sans ce que les carrières qui partent à l'ouverture
    de leur statut, les agents des IEG et de la conduite, y décotent déjà —
    aucun des nés de 1953 à 1957, tous ceux de 1963 à 1967. Génération par
    génération, les départs avec décote, des jumelles et des agents, pèsent
    parmi tous les retraités du sexe la part de leur génération, refaite à la
    main ; une jumelle qui ne peut pas décoter ne pèse rien — celle de la femme
    née en 1955 d'une carrière de trente à quarante ans, qui a sa durée à
    62 ans —, sa carrière gardant son poids."""
    assert G.DECOTE_DES_CARRIERES_QUI_LE_PEUVENT
    generations = (1955, 1965)
    naissances = {g: range(g - C._DEMI_TRANCHE, g + C._DEMI_TRANCHE + 1) for g in generations}
    attendues = _decotes_attendues(parametres.racine_donnees,
                                   tuple(n for g in generations for n in naissances[g]))
    variantes = G.grille("population", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    projection = simulateur.pour_la_projection()
    jumelles = [v for v in variantes if v.decote]
    agents = [v for v in variantes if v.cas.regle_liquidation == "ouverture" and not v.decote]
    assert {v.cas.code.split("~")[0] for v in agents} == {"agent_ieg", "agent_sncf_conduite"}
    for generation in generations:
        decotent = set()
        for v in agents:
            depart = projection.echeancier(v.cas.construire(projection, generation)).au_depart
            if G.avec_decote(projection, v.cas, generation, depart.taux_liquidation):
                decotent.add(v.cas.code)
        assert decotent == (set() if generation == 1955 else {v.cas.code for v in agents})
        for v in jumelles:
            if any(v.part_de_la_generation(n) > 0.0 for n in naissances[generation]):
                assert G.decote_a_l_ouverture(
                    projection, replace(v.cas, regle_liquidation="taux_plein"), generation
                ), (v.cas.code, generation)
        for sexe in ("F", "H"):
            du_sexe = [v for v in variantes if v.cas.sexe == sexe]
            for n in naissances[generation]:
                toutes = sum(poids[v.cas.code] * v.part_de_la_generation(n) for v in du_sexe)
                decotees = sum(poids[v.cas.code] * v.part_de_la_generation(n) for v in du_sexe
                               if v.decote or v.cas.code in decotent)
                assert toutes == pytest.approx(sum(poids[v.cas.code] for v in du_sexe),
                                               rel=1e-9), (sexe, n)
                assert decotees / toutes == pytest.approx(attendues[sexe][n], rel=1e-6), (
                    sexe, n)
    femme = next(v for v in jumelles if v.cas.code == f"{G.GABARIT}~f~30_40~decote~p50")
    assert femme.part_de_la_generation(1955) == 0.0
    assert femme.part_de_la_generation(1925) > 0.0


def test_les_departs_avec_decote_se_comptent_quintile_par_quintile(parametres):
    """Les départs avec décote se rangent dans leur quintile, sexe par sexe,
    contre ceux de l'EIR des résidents : 17,5 % des femmes du premier
    quintile."""
    lignes = [(float(montant), 1.0, "F" if montant % 2 else "H", "40_plus", False, 1.0,
               40.0, "regime_general", montant <= 3) for montant in range(1, 11)]
    confrontee = G.confronter_eqcc(lignes, G.quintiles_eqcc(parametres.racine_donnees,
                                                            residents=True))
    assert confrontee["F"]["decote"] == [1.0, 1.0, 0.0, 0.0, 0.0]
    assert confrontee["H"]["decote"] == [1.0, 0.0, 0.0, 0.0, 0.0]
    assert confrontee["F"]["decote_ensemble"] == pytest.approx(0.4)
    assert confrontee["F"]["decote_eir"][0] == pytest.approx(0.175)
    assert confrontee["H"]["decote_ensemble_eir"] == pytest.approx(0.045)
    assert "decote" not in G.confronter_eqcc([ligne[:8] for ligne in lignes],
                                             G.quintiles_eqcc(parametres.racine_donnees,
                                                              residents=True))["F"]


def test_l_attente_des_departs_avec_decote_se_lit_dans_l_eir(parametres):
    """Les départs avec décote des nés en 1953 après leur âge légal, 61 ans et
    2 mois, en trois attentes. Ceux de l'âge légal même n'attendent pas :
    37,5 % des femmes y partent, dont 15,4 % avec une décote. Ceux des deux
    premières années, 61 et 62 ans, et les autres, de 63 ans à l'âge
    d'annulation, 66 ans et 2 mois, attendent jusqu'au milieu de leur âge :
    42,1 % des femmes partent à 61 ans, dont 14,8 % avec une décote, ceux de
    l'âge légal compris, qui n'en sont pas, au milieu de ce qui reste de
    l'année ; 14,9 % à 66 ans, dont 1,9 % avec une décote, au milieu des deux
    mois d'avant l'âge d'annulation. Chaque attente au milieu de ses âges,
    pondéré, et pesant leur part : la moitié des femmes décotées partent à
    l'âge légal, un gros tiers des hommes. Nul ne décote après l'âge
    d'annulation ; ceux d'avant l'âge légal, des statuts qui ouvrent plus tôt,
    ne comptent pas."""
    publies = G.departs_publies(parametres.racine_donnees)
    lues = G.attentes_des_decotes(publies, parametres.racine_donnees)
    legal, annulation = 61.17, 66.17
    for sexe, a_l_age_legal, par_age in (
            ("F", 37.5 * 15.4, {61: 42.1 * 14.8, 62: 8.9 * 19.6, 63: 5.0 * 20.6,
                                64: 5.7 * 20.3, 65: 2.9 * 27.6, 66: 14.9 * 1.9}),
            ("H", 24.4 * 11.0, {61: 29.7 * 10.3, 62: 8.2 * 14.9, 63: 5.2 * 14.5,
                                64: 6.1 * 17.1, 65: 3.1 * 29.7, 66: 9.1 * 3.9})):
        par_age[61] -= a_l_age_legal
        attentes = {age: ((legal + 62.0) / 2 if age == 61 else (66.0 + annulation) / 2
                          if age == 66 else age + 0.5) - legal for age in par_age}
        total = a_l_age_legal + sum(par_age.values())
        attendues = [(0.0, a_l_age_legal / total)] + [
            (sum(par_age[a] * attentes[a] for a in ages) / sum(par_age[a] for a in ages),
             sum(par_age[a] for a in ages) / total)
            for ages in ((61, 62), (63, 64, 65, 66))]
        assert [attente for attente, _ in lues[sexe]] == pytest.approx(
            [attente for attente, _ in attendues]), sexe
        assert [part for _, part in lues[sexe]] == pytest.approx(
            [part for _, part in attendues]), sexe
    assert lues["F"][0][1] == pytest.approx(0.51, abs=0.01)
    assert lues["H"][0][1] == pytest.approx(0.37, abs=0.01)


def test_les_departs_avec_decote_attendent_comme_ceux_des_nes_en_1953(
        simulateur, source, parametres):
    """Sous ``DECOTE_ENTRE_LES_DEUX_AGES``, la jumelle qui décote de chaque
    carrière incomplète se décline comme les départs avec décote des nés en
    1953 (``attentes_des_decotes``) : la part de son poids qu'ils prennent à
    l'âge légal y part, à l'ouverture du droit, sous son code ; le reste
    attend après lui, en deux attentes, à l'ouverture encore. Les trois pèsent
    ensemble ce que pesait la jumelle, chacune de la part de sa génération
    (``test_la_part_des_departs_avec_decote_se_rapporte_aux_carrieres_qui_peuvent_decoter``)."""
    assert G.DECOTE_ENTRE_LES_DEUX_AGES
    attentes = G.attentes_des_decotes(G.departs_publies(parametres.racine_donnees),
                                      parametres.racine_donnees)
    variantes = G.grille("population", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    jumelles = {v.cas.code: v for v in variantes if v.decote}
    attendantes: dict[str, set[float]] = {}
    for v in jumelles.values():
        assert v.cas.regle_liquidation == "ouverture"
        if not v.cas.attente:
            continue
        immobile = jumelles[v.cas.code.replace(f"~decote{v.cas.attente:.2f}", "~decote")]
        assert immobile.cas.attente == 0.0
        assert v.parts_des_generations == immobile.parts_des_generations
        parts = dict(attentes[v.cas.sexe])
        assert poids[v.cas.code] / poids[immobile.cas.code] == pytest.approx(
            parts[v.cas.attente] / parts[0.0])
        attendantes.setdefault(immobile.cas.code, set()).add(v.cas.attente)
    assert {code for code, v in jumelles.items() if not v.cas.attente} == set(attendantes)
    for code, siennes in attendantes.items():
        assert siennes == {a for a, _ in attentes[jumelles[code].cas.sexe] if a}, code


def test_un_depart_avec_decote_qui_attend_decote_moins(simulateur, source, parametres):
    """Née en 1955, la femme d'une carrière de dix à vingt ans du salariat
    privé, de la classe médiane, a moins de 146 trimestres à 62 ans, ses
    enfants compris, des 166 de sa génération : c'est l'âge qui borne sa
    décote (R. 351-27). Partie à l'âge légal, il lui manque vingt trimestres
    jusqu'à 67 ans, l'âge d'annulation des nés depuis 1955 (L. 351-8, 1°) :
    elle liquide au taux de 50 − 20 × 0,625 = 37,5 %. Ses jumelles qui
    attendent partent plus tard, décotées encore, d'autant de trimestres que
    leur attente en laisse jusqu'à 67 ans, arrondis au trimestre supérieur :
    seize, au taux de 40 %, après un an et deux mois ; sept, au taux de
    45,625 %, après trois ans et cinq mois. Elles ne valident rien en
    attendant. La surcote, née en 2004, n'attend qu'aux générations qui la
    connaissent ; la décote baissait déjà avec l'âge : la même femme, née en
    1940, attend autant après 60 ans."""
    variantes = G.grille("population", simulateur.effectifs, source, ())
    projection = simulateur.pour_la_projection()
    attentes = G.attentes_des_decotes(G.departs_publies(parametres.racine_donnees),
                                      parametres.racine_donnees)["F"]
    par_code = {v.cas.code: v for v in variantes}
    code = f"{G.GABARIT}~f~10_20~decote~p50"
    valides = set()
    for attente, _ in attentes:
        jumelle = par_code[code.replace("~decote", f"~decote{attente:.2f}") if attente
                           else code]
        assert G.condition_au_depart(projection, jumelle.cas, 1955) == (
            pytest.approx(62.0 + attente), "decote")
        depart = projection.echeancier(jumelle.cas.construire(projection, 1955)).au_depart
        valides.add(depart.trimestres_valides)
        assert depart.taux_liquidation == pytest.approx(
            0.5 - 0.00625 * math.ceil(4.0 * (5.0 - attente)))
        assert jumelle.cas.age_liquidation_pour(projection, 1940) == pytest.approx(
            60.0 + attente)
    assert len(valides) == 1 and valides.pop() < 146
    assert [round(a, 2) for a, _ in attentes] == [0.0, 1.14, 3.4]


# -- les départs d'une génération, contre l'EIR (action 138, étape 14) ----------

def test_les_departs_publies_se_lisent_dans_le_fichier_certifie(parametres):
    """Les départs des nés en 1950 et en 1953 que l'EIR compte, tels que le
    fichier certifié les donne ; la grille 1950 se juge sur les nés en 1950,
    celle de 1955 sur les nés en 1953, la génération la plus proche que
    l'enquête voie presque toute partie."""
    publies = G.departs_publies(parametres.racine_donnees)
    assert publies[(1953, "condition", "surcote", "F", "part")] == 14.2
    assert publies[(1950, "position", "age_legal", "ensemble", "part")] == 40.0
    assert publies[(1950, "age_liquidation", "60", "H", "part")] == 41.3
    assert G.GENERATIONS_DES_DEPARTS == {1950: 1950, 1955: 1953}


def test_un_depart_se_range_par_sa_place_et_son_age():
    """La place d'un départ par rapport à l'âge légal et à l'âge d'annulation
    de la décote, chacun à un mois et demi près, et son âge en années
    révolues, comme l'EIR les range."""
    places = [G.position_du_depart(age, 60.0, 65.0)
              for age in (58.5, 60.0, 60.1, 62.5, 64.95, 65.0, 66.0)]
    assert places == ["avant_age_legal", "age_legal", "age_legal", "entre",
                      "age_annulation", "age_annulation", "apres_annulation"]
    assert [G.age_du_depart(age) for age in (58.5, 60.0, 64.75, 67.0, 68.5)] == [
        "avant_60", "60", "64", "67_plus", "67_plus"]


def test_les_departs_d_une_generation_se_confrontent_a_l_eir(parametres):
    """Les départs d'une génération de la grille, sexe par sexe, contre ceux
    de la génération de l'EIR qui la juge : la part de chaque place et de
    chaque condition — carrière longue, décote, surcote, taux plein par l'âge,
    et le reste du taux plein, par la durée ou pour un autre motif —, et,
    quand la génération est la même, de chaque âge. Les conditions de l'EIR
    se lisent parmi les départs dont la condition est connue : 11,2 % des
    femmes nées en 1950 surcotent, sur 99,6 % de conditions connues."""
    publies = G.departs_publies(parametres.racine_donnees)
    lignes = [(1950, "F", 1.0, "age_legal", "taux_plein_autre", "60"),
              (1950, "F", 3.0, "entre", "surcote", "62"),
              (1950, "H", 2.0, "avant_age_legal", "carriere_longue", "avant_60"),
              (1955, "F", 1.0, "age_annulation", "taux_plein_age", "67_plus")]
    mesure = G.confronter_departs(lignes, publies)
    femmes = mesure["1950"]["F"]
    assert femmes["positions"]["entre"] == [pytest.approx(0.75), pytest.approx(0.224)]
    assert femmes["conditions"]["surcote"] == [pytest.approx(0.75),
                                               pytest.approx(11.2 / 99.6)]
    assert femmes["conditions"]["taux_plein_autre"][1] == pytest.approx(
        (4.7 + 7.1 + 8.9 + 1.5 + 34.4) / 99.6)
    assert femmes["ages"]["62"] == [pytest.approx(0.75), pytest.approx(0.038)]
    assert mesure["1950"]["ensemble"]["positions"]["avant_age_legal"][0] == pytest.approx(
        2.0 / 6.0)
    assert mesure["1950"]["eir"] == 1950 and mesure["1955"]["eir"] == 1953
    assert mesure["1955"]["F"]["conditions"]["taux_plein_age"] == [
        pytest.approx(1.0), pytest.approx(12.2 / 99.2)]
    assert "ages" not in mesure["1955"]["F"]
    assert "H" not in mesure["1955"]


def test_la_condition_d_un_depart_se_lit_dans_sa_liquidation(simulateur, source):
    """La condition d'un départ de la population, telle que l'EIR la range :
    l'homme né en 1950 d'une carrière pleine du salariat privé de la classe
    médiane, entré à 16 ans, part en carrière longue ; la femme d'une carrière
    courte part au taux plein par l'âge, à 65 ans, ou avec une décote si elle
    part à l'ouverture du droit ; l'agent de conduite né en 1950 part à
    cinquante ans au taux plein de son statut, sans décote."""
    variantes = G.grille("population", simulateur.effectifs, source, ())
    projection = simulateur.pour_la_projection()

    def condition(v, generation=1950):
        return G.condition_au_depart(projection, v.cas, generation)

    pleine = next(v for v in variantes if v.cas.code == f"{G.GABARIT}~h~40_plus~p50")
    assert condition(pleine)[1] == "carriere_longue"
    courte = next(v for v in variantes if v.tranche == "moins_10" and v.cas.sexe == "F"
                  and v.groupe == "regime_general" and not v.decote)
    assert condition(courte) == (pytest.approx(65.0), "taux_plein_age")
    decotee = next(v for v in variantes if v.tranche == "moins_10" and v.cas.sexe == "F"
                   and v.groupe == "regime_general" and v.decote)
    assert condition(decotee) == (pytest.approx(60.0), "decote")
    conduite = next(v for v in variantes if v.cas.code.startswith("agent_sncf_conduite"))
    assert condition(conduite) == (pytest.approx(50.0), "taux_plein_autre")


def test_la_part_et_l_attente_des_departs_avec_surcote_se_lisent_dans_l_eir(parametres):
    """La part des carrières complètes qui partent avec une surcote parmi les
    nés en 1953, sexe par sexe : 14,2 % des femmes surcotent, dont 87,4 % à
    carrière complète, quand 57,3 % de toutes en ont une. Et l'attente de ces
    départs après l'âge légal, 61 ans et 2 mois, au milieu de chaque âge de
    liquidation — 1 an et 4 mois pour les départs de 62 ans, qui pèsent 8,9 %
    des femmes, dont 46,8 % en surcote, 5 mois pour ceux de l'année de l'âge
    légal —, en trois attentes : les départs de ses deux premières années, 61
    et 62 ans, ceux d'avant l'année où s'annule la décote, à 66 ans et 2 mois,
    et ceux de cette année-là et d'après. Nul ne surcote avant l'âge légal."""
    publies = G.departs_publies(parametres.racine_donnees)
    parts = G.parts_avec_surcote(publies)
    assert parts["F"] == pytest.approx(0.142 * 87.4 / 57.3)
    assert parts["H"] == pytest.approx(0.145 * 85.6 / 70.0)
    lues = G.attentes_des_surcotes(publies, parametres.racine_donnees)["F"]
    femmes = {61: 42.1 * 1.5, 62: 8.9 * 46.8, 63: 5.0 * 53.3, 64: 5.7 * 51.7,
              65: 2.9 * 39.8, 66: 14.9 * 15.8, 67: 0.8 * 29.1}
    attentes = {age: (61.17 + 62.0) / 2 - 61.17 if age == 61 else age + 0.5 - 61.17
                for age in femmes}
    total = sum(femmes.values())
    groupes = [(61, 62), (63, 64, 65), (66, 67)]
    attendues = [(sum(femmes[a] * attentes[a] for a in ages) / sum(femmes[a] for a in ages),
                  sum(femmes[a] for a in ages) / total) for ages in groupes]
    assert [attente for attente, _ in lues] == pytest.approx(
        [attente for attente, _ in attendues])
    assert [part for _, part in lues] == pytest.approx([part for _, part in attendues])


def test_une_part_des_carrieres_de_trente_ans_et_plus_part_avec_une_surcote(
        simulateur, source, parametres):
    """Sous ``DEPARTS_AVEC_SURCOTE``, chaque carrière du salariat et des
    non-salariés de trente années validées et plus, qui part au taux plein, se
    décline : la part de son sexe que l'EIR voit surcoter parmi les carrières
    complètes attend, après l'âge légal, autant que les départs avec surcote
    des nés en 1953, âge par âge ; le reste part au taux plein. Les carrières
    plus courtes, les départs avec décote et les statutaires gardent leur
    départ."""
    assert G.DEPARTS_AVEC_SURCOTE
    publies = G.departs_publies(parametres.racine_donnees)
    parts = G.parts_avec_surcote(publies)
    attentes = G.attentes_des_surcotes(publies, parametres.racine_donnees)
    variantes = G.grille("population", simulateur.effectifs, source, ())
    poids = _poids(variantes, simulateur.effectifs, source.millesime)
    for sexe in ("F", "H"):
        du_sexe = [v for v in variantes if v.cas.sexe == sexe
                   and (v.surcote or G.peut_surcoter(v))]
        avec = [v for v in du_sexe if v.surcote]
        assert (sum(poids[v.cas.code] for v in avec)
                / sum(poids[v.cas.code] for v in du_sexe)) == pytest.approx(parts[sexe],
                                                                            abs=1e-9)
        par_attente: dict[float, float] = {}
        for v in avec:
            par_attente[v.surcote] = par_attente.get(v.surcote, 0.0) + poids[v.cas.code]
        total = sum(par_attente.values())
        assert {a: p / total for a, p in par_attente.items()} == pytest.approx(
            dict(attentes[sexe])), sexe
    assert all(v.tranche in ("30_40", "40_plus") and v.groupe in G.GROUPES_INTERROMPUS
               and v.cas.regle_liquidation == "taux_plein" and not v.decote
               and v.cas.attente == v.surcote for v in variantes if v.surcote)
    assert not any(G.peut_surcoter(v) for v in variantes
                   if v.tranche not in ("30_40", "40_plus") or v.decote
                   or v.groupe not in G.GROUPES_INTERROMPUS)


def test_un_depart_avec_surcote_attend_apres_l_age_legal(simulateur, source):
    """L'homme d'une carrière pleine du salariat privé de la classe médiane né
    en 1955, que la carrière longue ferait partir avant 62 ans, part, s'il
    surcote, sa première attente après lui, avec une surcote ; la femme née en
    1955 d'une carrière de trente à quarante années de la même classe, au taux
    plein dès 62 ans, de même. Avant 2004, la loi ne servait aucune surcote :
    le même homme, né en 1940, part comme s'il n'en attendait pas."""
    variantes = G.grille("population", simulateur.effectifs, source, ())
    projection = simulateur.pour_la_projection()
    attentes = G.attentes_des_surcotes(G.departs_publies(simulateur.parametres.racine_donnees),
                                       simulateur.parametres.racine_donnees)

    def surcotee(sexe: str, tranche: str) -> G.Variante:
        return next(v for v in variantes if v.cas.code.startswith(G.GABARIT)
                    and v.cas.sexe == sexe and v.tranche == tranche
                    and G.classe_de(v) == "p50"
                    and v.surcote == pytest.approx(attentes[sexe][0][0]))

    homme = surcotee("H", "40_plus")
    sans = next(v for v in variantes if v.cas.code == homme.cas.code.split("~surcote")[0])
    assert G.condition_au_depart(projection, sans.cas, 1955)[1] == "carriere_longue"
    assert G.condition_au_depart(projection, homme.cas, 1955) == (
        pytest.approx(62.0 + attentes["H"][0][0]), "surcote")
    femme = surcotee("F", "30_40")
    assert G.condition_au_depart(projection, femme.cas, 1955) == (
        pytest.approx(62.0 + attentes["F"][0][0]), "surcote")
    assert (homme.cas.age_liquidation_pour(projection, 1940)
            == sans.cas.age_liquidation_pour(projection, 1940))
