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
from retraite_notionnelle.castypes import CAS_TYPES, poids_effectifs
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
            attendu = poids_effectifs(effectifs, annee, CAS_TYPES)
            obtenu = poids_effectifs(reparti, annee, cas_types)
            for cas in CAS_TYPES:
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
    for cas in CAS_TYPES:
        siens = [v for v in variantes if v.cas.code.startswith(f"{cas.code}~")]
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
           and not v.cas.code.endswith("~partiel")]
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
    haut, la classe médiane au volume de tous."""
    assert G.VOLUME_SELON_LE_RANG
    volumes, rangs = G.volumes_de_travail(parametres.racine_donnees)
    par_code = {v.cas.code: v.cas for v in G.grille("population", simulateur.effectifs,
                                                     source, ())}
    for classe, nom in (("p10~bas1", "p10"), ("p10~smic", "p10"), ("p50", "p50"),
                        ("p99", "p99")):
        cas = par_code[f"{G.GABARIT}~h~40_plus~{classe}"]
        assert cas.volumes == tuple((age, min(1.0, part * rangs[nom]))
                                    for age, part in volumes), classe
    assert rangs["p10"] < 1.0 < rangs["p99"]
    assert max(part for _, part in par_code[f"{G.GABARIT}~h~40_plus~p99"].volumes) == 1.0


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
    (``test_les_carrieres_des_femmes_suivent_la_duree_de_leur_generation``)."""
    assert G.COURTES_ETALEES
    variantes = G.grille("population", simulateur.effectifs, source, ())
    courte = next(v for v in variantes if v.cas.code == f"{G.GABARIT}~h~10_20~p50")
    assert courte.duree == 15 and courte.assimilees == round(
        G.part_assimilee(source, "H") * 15)
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


def test_la_grille_du_depot_reecrite_redonne_la_page(parametres):
    """Les pseudo-caisses et la grille simulée à part donnent la page au
    millième : la mesure ne mesure rien d'autre que la grille."""
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
