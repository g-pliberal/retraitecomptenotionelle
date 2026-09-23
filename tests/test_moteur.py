"""Tests du moteur : indexation, âge de référence, conversion, fusion, compte."""

from __future__ import annotations

import pytest

from retraite_notionnelle.config import (
    ModeAgeReference,
    ModeIndexation,
    Parametres,
    RACINE_DONNEES,
    TableConversion,
)
from retraite_notionnelle.donnees.macro import DonneesMacro
from retraite_notionnelle.donnees.mortalite import DonneesMortalite
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.moteur.age_reference import AgeReference
from retraite_notionnelle.moteur.conversion import Convertisseur
from retraite_notionnelle.moteur.fusion import CritereTaux, RegleFusion, fusionner
from retraite_notionnelle.carriere import (
    ANNEE_FORME_CATEGORIE,
    _facteur_secteur,
    TRANCHES_CATEGORIE,
    TRANCHES_SERIE,
    profil_salaire,
)
from retraite_notionnelle.moteur.indexation import Indexation
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def macro() -> DonneesMacro:
    return DonneesMacro(RACINE_DONNEES)


@pytest.fixture(scope="module")
def mortalite() -> DonneesMortalite:
    return DonneesMortalite(RACINE_DONNEES, cache_disque=False)


@pytest.fixture(scope="module")
def catalogue() -> CatalogueRegimes:
    return CatalogueRegimes(RACINE_DONNEES)


# -- indexation --------------------------------------------------------------


def test_triple_lock_inverse_retient_bien_le_minimum(macro):
    # Le mode est nommé : ce n'est plus le défaut du modèle depuis que celui-ci
    # est la règle d'équilibre. Un test sur la règle demandée doit la demander.
    indexation = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.TRIPLE_LOCK_INVERSE)
    )
    for annee in (1975, 1990, 2005, 2020):
        taux = indexation.taux(annee)
        assert taux.taux == min(taux.inflation, taux.salaire_moyen, taux.productivite)


def test_triple_lock_inverse_est_domine_par_la_productivite_en_forte_inflation(macro):
    """Le mélange réel/nominal fait gagner la productivité dès que l'inflation monte."""
    indexation = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.TRIPLE_LOCK_INVERSE)
    )
    for annee in (1974, 1980, 1981):
        assert indexation.taux(annee).terme_retenu == "productivite_reelle"


def test_regle_litterale_detruit_le_pouvoir_d_achat_des_comptes_anciens(macro):
    """Constat central du modèle, à ne pas perdre de vue en lisant les résultats.

    Sur 1941-2025, la règle littérale revalorise les comptes d'un facteur voisin
    de 5 quand les prix sont multipliés par plus de 300 : une cotisation de
    l'immédiat après-guerre ne conserve que quelques pour cent de sa valeur
    réelle. La variante nominale, qui ramène la productivité en termes nominaux
    avant de prendre le minimum, en conserve l'essentiel.
    """
    litterale = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.TRIPLE_LOCK_INVERSE)
    )
    nominale = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.TRIPLE_LOCK_INVERSE_NOMINAL)
    )
    prix = macro.coefficient_prix(1941, 2025)
    cumul_litteral = litterale.coefficient(1941, 2025)
    cumul_nominal = nominale.coefficient(1941, 2025)

    assert cumul_litteral / prix < 0.05, "la règle littérale devrait tout écraser"
    assert cumul_nominal / prix > 0.50, "la variante nominale devrait préserver l'essentiel"
    assert cumul_nominal > 10 * cumul_litteral


def test_mediane_retient_le_terme_du_milieu(macro):
    """La médiane est l'un des trois taux, celui du milieu — jamais un calcul."""
    indexation = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.MEDIANE_TROIS_TAUX)
    )
    for annee in range(1941, 2026):
        taux = indexation.taux(annee)
        trois = sorted((taux.inflation, taux.salaire_moyen, taux.productivite))
        assert taux.taux == trois[1]
        assert taux.terme_retenu in {"inflation", "salaire_moyen", "productivite_reelle"}


def test_moyenne_est_la_moyenne_arithmetique_des_trois(macro):
    indexation = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.MOYENNE_TROIS_TAUX)
    )
    for annee in range(1941, 2026):
        taux = indexation.taux(annee)
        assert taux.taux == pytest.approx(
            (taux.inflation + taux.salaire_moyen + taux.productivite) / 3
        )
        assert taux.terme_retenu == "moyenne"


def test_mediane_et_moyenne_adoucissent_la_regle_annee_par_annee(macro):
    """Même carrière, mêmes trois séries : seule la statistique change.

    Le minimum est par construction le plus bas des trois ; la médiane et la
    moyenne lui sont donc supérieures ou égales chaque année, et la médiane
    reste sous le maximum. C'est tout ce que la théorie garantit — le reste,
    ce sont les données qui le disent (test suivant).
    """
    minimum = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.TRIPLE_LOCK_INVERSE)
    )
    mediane = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.MEDIANE_TROIS_TAUX)
    )
    moyenne = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.MOYENNE_TROIS_TAUX)
    )
    for annee in range(1941, 2026):
        bas = minimum.taux(annee)
        haut = max(bas.inflation, bas.salaire_moyen, bas.productivite)
        assert bas.taux <= mediane.taux(annee).taux <= haut
        assert bas.taux <= moyenne.taux(annee).taux <= haut


def test_la_mediane_depasse_les_prix_quand_la_moyenne_reste_dessous(macro):
    """Le résultat le moins intuitif des deux variantes, sur 1941-2025.

    La médiane est presque toujours l'inflation ou le salaire moyen — deux taux
    NOMINAUX : elle suit donc les prix, et les dépasse même un peu (le salaire
    moyen l'emporte quand la productivité est forte). La moyenne, elle, incorpore
    un tiers de productivité RÉELLE chaque année, y compris pendant les années à
    dix ou vingt points d'inflation : elle reste durablement sous les prix. La
    moyenne est donc plus sévère que la médiane, ce qui ne se lit pas dans
    l'ordre des trois statistiques mais dans le mélange nominal/réel.
    """
    prix = macro.coefficient_prix(1941, 2025)
    mediane = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.MEDIANE_TROIS_TAUX)
    ).coefficient(1941, 2025)
    moyenne = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.MOYENNE_TROIS_TAUX)
    ).coefficient(1941, 2025)
    litteral = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.TRIPLE_LOCK_INVERSE)
    ).coefficient(1941, 2025)

    assert mediane > prix > moyenne > litteral


def test_revalorisation_portee_au_compte_sert_les_coefficients_des_arretes(macro):
    """Le mode lit les arrêtés, il ne les approche pas.

    Année par année, le taux est le rapport de deux années consécutives dans la
    colonne publiée par la caisse — la grandeur même dont le scénario 1 se sert
    pour revaloriser les salaires de son salaire de référence.
    """
    indexation = Indexation(
        macro,
        Parametres(mode_indexation=ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE),
    )
    for annee in (1955, 1975, 1986, 1987, 2000, 2024, 2025):
        taux = indexation.taux(annee)
        attendu = macro.coefficient_revalorisation_portee_au_compte(annee - 1, annee) - 1
        assert taux.taux == pytest.approx(attendu)
        assert taux.terme_retenu == "revalorisation_legale"


def test_la_composition_annuelle_ne_derive_pas_des_colonnes_publiees(macro):
    """Le moteur compose ce mode année par année, la caisse arrondit à trois
    décimales : les deux chemins doivent rester à distance négligeable.

    0,04 % sur quatre-vingt-quatre ans — deux ordres de grandeur sous les écarts
    que ce mode sert à mesurer. Si la borne saute, c'est que la table a changé
    de forme et que le mode ne peut plus se composer comme les autres.
    """
    indexation = Indexation(
        macro,
        Parametres(mode_indexation=ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE),
    )
    compose = indexation.coefficient(1941, 2025)
    publie = macro.coefficient_revalorisation_portee_au_compte(1941, 2025)
    assert compose == pytest.approx(publie, rel=0.001)


def test_l_indexation_sur_les_prix_n_est_pas_la_regle_du_droit_positif(macro):
    """La régression que ce mode corrige, et qui valait un facteur cinq.

    Le README, la documentation et le site ont longtemps présenté
    ``--indexation prix`` comme la règle neutralisant l'indexation, donc comme
    celle du système actuel. Le régime général ne revalorise sur les prix que
    depuis 1987 : avant, les arrêtés suivaient les salaires. Confondre les deux
    imputait aux comptes notionnels un écart qui venait encore de l'indexation.
    """
    legale = Indexation(
        macro,
        Parametres(mode_indexation=ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE),
    ).coefficient(1941, 2025)
    prix = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.PRIX)
    ).coefficient(1941, 2025)
    salaires = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.SALAIRES)
    ).coefficient(1941, 2025)

    # ×3,9 les prix sur 1942-2025 (le tableau du README annonce ×4,8 : il
    # cumule aussi l'année 1941, première année de la période qu'il couvre).
    assert legale > 3.5 * prix, "les arrêtés ont suivi les salaires jusqu'en 1986"
    assert legale < salaires, "et les prix depuis 1987"

    # Depuis la bascule de 1987, en revanche, les deux règles se rejoignent :
    # c'est bien la même règle, mais seulement sur cette portion-là.
    depuis_1987 = Indexation(
        macro,
        Parametres(mode_indexation=ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE),
    ).coefficient(1990, 2025)
    prix_depuis_1987 = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.PRIX)
    ).coefficient(1990, 2025)
    assert depuis_1987 == pytest.approx(prix_depuis_1987, rel=0.10)


def test_masse_salariale_est_le_salaire_moyen_plus_l_emploi(macro):
    """La masse salariale se décompose exactement en salaire moyen × emploi.

    Le contrôle ne dispose pas d'une série d'emploi — le modèle n'en charge pas —
    mais l'identité impose au moins ceci : sur la période où l'emploi salarié a
    crû, la masse salariale doit croître plus vite que le salaire moyen, et
    l'écart cumulé doit valoir le doublement de l'emploi salarié observé par
    l'INSEE entre 1950 et 2025 (×2,14).
    """
    masse = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.MASSE_SALARIALE)
    ).coefficient(1950, 2025)
    salaires = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.SALAIRES)
    ).coefficient(1950, 2025)
    assert masse / salaires == pytest.approx(2.14, abs=0.05)


def test_la_masse_salariale_est_la_regle_la_plus_genereuse(macro):
    """Le taux d'équilibre de la répartition n'est pas une règle d'austérité.

    C'est le point que le modèle doit rendre visible : la règle que la théorie
    désigne — le rendement que l'assiette peut servir — est très au-dessus de
    toutes celles qui ont été discutées, y compris de l'indexation sur les
    salaires, parce qu'elle y ajoute la croissance de l'emploi.
    """
    coefficients = {
        mode: Indexation(macro, Parametres(mode_indexation=mode)).coefficient(1941, 2025)
        for mode in ModeIndexation
    }
    masse = coefficients[ModeIndexation.MASSE_SALARIALE]
    assert masse == max(coefficients.values())
    assert masse > coefficients[ModeIndexation.SALAIRES]
    assert masse > 10 * macro.coefficient_prix(1941, 2025)


def test_le_cumul_du_pib_lisse_doit_son_avance_a_la_moyenne_mobile(macro):
    """Un lissage n'est pas neutre sur un cumul de quatre-vingts ans.

    Le PIB nominal croît MOINS vite que la masse salariale sur la période. Son
    cumul lissé sur cinq ans la dépasse pourtant : c'est la moyenne mobile qui
    recule la base de référence, pas l'assiette qui serait plus dynamique. Sur
    une carrière réelle, l'écart retombe à deux ou trois points.
    """
    masse = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.MASSE_SALARIALE)
    ).coefficient(1941, 2025)
    brut = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.PIB_NOMINAL)
    ).coefficient(1941, 2025)
    lisse = Indexation(
        macro,
        Parametres(mode_indexation=ModeIndexation.PIB_NOMINAL, lissage_indexation=5),
    ).coefficient(1941, 2025)

    assert brut < masse < lisse


def test_la_masse_salariale_est_certifiee_depuis_1950(macro):
    """Une règle par défaut ne peut pas reposer sur une série non sourcée.

    1930-1949 reste estimé — les comptes nationaux ne remontent pas plus haut,
    et ces vingt années supposent l'emploi salarié constant — mais la fiabilité
    le dit, et elle se propage jusqu'au résultat.
    """
    from retraite_notionnelle.donnees.chargement import Fiabilite

    assert macro.masse_salariale.fiabilite_minimale_sur(1950, 2025) == Fiabilite.CERTIFIEE
    assert macro.masse_salariale.fiabilite(1935) == Fiabilite.ESTIMEE


def test_le_lissage_est_la_moyenne_geometrique_de_la_fenetre(macro):
    """Un lissage se vérifie sur sa fenêtre, et sur n'importe quelle règle."""
    for mode in (ModeIndexation.PIB_NOMINAL, ModeIndexation.MASSE_SALARIALE,
                 ModeIndexation.TRIPLE_LOCK_INVERSE):
        brut = Indexation(macro, Parametres(mode_indexation=mode))
        lisse = Indexation(
            macro, Parametres(mode_indexation=mode, lissage_indexation=5)
        )
        for annee in (1975, 2000, 2020, 2025):
            produit = 1.0
            for a in range(annee - 4, annee + 1):
                produit *= 1 + brut.taux(a).taux
            assert lisse.taux(annee).taux == pytest.approx(produit ** (1 / 5) - 1), (
                f"{mode.value} en {annee}"
            )


def test_le_lissage_absorbe_le_trou_de_2020(macro):
    """Ce que le lissage sert à faire, sur l'année qui le montre le mieux.

    Le PIB nominal recule de plusieurs points en 2020. Sans lissage, les comptes
    d'une génération liquidée cette année-là en porteraient la trace entière ;
    avec, l'année est absorbée par les quatre qui l'entourent — et le taux reste
    positif. C'est la loterie de cohorte que le lissage vise, pas le niveau.
    """
    brut = macro.pib_nominal(2020)
    lisse = Indexation(
        macro,
        Parametres(mode_indexation=ModeIndexation.PIB_NOMINAL, lissage_indexation=5),
    ).taux(2020).taux
    assert brut < 0 < lisse


def test_le_lissage_ne_change_rien_a_une_fenetre_d_un_an(macro):
    """Le défaut est l'absence de lissage, et l'absence de lissage est neutre."""
    for mode in ModeIndexation:
        sans = Indexation(macro, Parametres(mode_indexation=mode))
        avec_un = Indexation(
            macro, Parametres(mode_indexation=mode, lissage_indexation=1)
        )
        assert sans.coefficient(1941, 2025) == avec_un.coefficient(1941, 2025), mode


def test_la_fenetre_de_lissage_est_tronquee_au_debut_des_series(macro):
    """Aux premières années, la fenêtre est plus courte — jamais indisponible.

    En deçà, ``SerieAnnuelle`` répète sa première valeur : une moyenne glissante
    qui l'avalerait ferait passer une extrapolation pour une observation.
    """
    indexation = Indexation(
        macro,
        Parametres(mode_indexation=ModeIndexation.PIB_NOMINAL, lissage_indexation=5),
    )
    premiere = macro.inflation.premiere_annee
    assert indexation.taux(premiere).taux == pytest.approx(macro.pib_nominal(premiere))
    # et une carrière ancienne se calcule sans lever
    assert indexation.coefficient(premiere, 2025) > 1.0


def test_le_plancher_s_applique_apres_le_lissage(macro):
    """Un plancher qu'une moyenne pourrait repasser sous le seuil n'en est pas un."""
    indexation = Indexation(
        macro,
        Parametres(mode_indexation=ModeIndexation.TRIPLE_LOCK_INVERSE,
                   lissage_indexation=5, plancher_indexation=0.0),
    )
    for annee in range(1941, 2026):
        assert indexation.taux(annee).taux >= 0.0


def test_le_lissage_supprime_les_annees_ou_attendre_fait_perdre(macro):
    """La loterie de cohorte, sous sa forme la plus nette.

    Une cotisation de 1950 vaut, à la liquidation, son coefficient cumulé. Sur
    le PIB nominal brut, il existe des années où ce coefficient RECULE : partir
    un an plus tard rapporte moins, parce que l'année traversée s'est mal
    passée. Rien dans la carrière ne le justifie — c'est le calendrier qui
    tranche. Le lissage retire ce pouvoir au calendrier.
    """
    def reculs(lissage: int) -> int:
        indexation = Indexation(
            macro,
            Parametres(mode_indexation=ModeIndexation.PIB_NOMINAL,
                       lissage_indexation=lissage),
        )
        return sum(
            1 for liquidation in range(1951, 2026)
            if indexation.coefficient(1950, liquidation)
            > indexation.coefficient(1950, liquidation + 1)
        )

    assert reculs(1) > 0
    assert reculs(3) == 0
    assert reculs(5) == 0


def test_le_lissage_gonfle_les_cumuls_longs_sans_toucher_a_l_assiette(macro):
    """La réserve à connaître avant de lire un cumul lissé sur quatre-vingts ans.

    Le produit des moyennes glissantes revient à mesurer la croissance depuis
    une base reculée d'environ la moitié de la fenêtre. Sur 1941-2025 cela vaut
    une vingtaine de pour cent à cinq ans — sans qu'aucune série ait changé.
    """
    brut = Indexation(
        macro, Parametres(mode_indexation=ModeIndexation.PIB_NOMINAL)
    ).coefficient(1941, 2025)
    lisse = Indexation(
        macro,
        Parametres(mode_indexation=ModeIndexation.PIB_NOMINAL, lissage_indexation=5),
    ).coefficient(1941, 2025)
    assert 1.15 < lisse / brut < 1.30


def test_indexation_prix_reproduit_l_inflation(macro):
    indexation = Indexation(macro, Parametres(mode_indexation=ModeIndexation.PRIX))
    assert indexation.coefficient(1980, 2020) == pytest.approx(
        macro.coefficient_prix(1980, 2020)
    )


def test_plancher_d_indexation_est_respecte(macro):
    indexation = Indexation(macro, Parametres(plancher_indexation=0.0))
    for annee in range(1941, 2026):
        assert indexation.taux(annee).taux >= 0.0


def test_coefficient_ne_revalorise_pas_l_annee_du_versement(macro):
    indexation = Indexation(macro, Parametres())
    assert indexation.coefficient(2000, 2000) == 1.0
    assert indexation.coefficient(2000, 2001) == pytest.approx(
        1 + indexation.taux(2001).taux
    )


# -- profil de rémunération ---------------------------------------------------


def test_le_passe_ne_depend_pas_de_l_age_de_depart():
    """Travailler plus longtemps ne doit pas réécrire les salaires d'avant.

    L'étalon de la déformation salariale a longtemps été la carrière de
    l'assuré, si bien qu'une même année civile se trouvait moins « avancée »
    dans une carrière plus longue, donc moins payée. Allonger sa carrière
    rabaissait alors son propre passé — de 5,2 % entre 60 et 67 ans en profil
    ascendant, de 8,4 % en fortement ascendant —, ce qui surestimait de quatre
    points le gain à travailler plus longtemps dans le système actuel, dont le
    salaire de référence ne retient que les meilleures années.

    L'étalon est désormais la carrière complète de la GÉNÉRATION, que l'assuré
    ne choisit pas. Le passé est donc strictement invariant, et ce test le dit
    sur les trois profils, y compris pour un départ au-delà du taux plein, où
    l'avancement plafonne.
    """
    simulateur = Simulateur(Parametres())
    for profil in ("plat", "ascendant", "fortement_ascendant"):
        passes = []
        for age in (58, 60, 64, 67, 70):
            carriere = simulateur.carriere_simple(
                annee_naissance=1975, sexe="H",
                affiliation="salarie_prive_non_cadre",
                age_debut=21, age_liquidation=age, profil_carriere=profil,
            )
            passes.append(sum(l.revenu for l in carriere.lignes if l.annee < 2026))
        assert passes[0] == pytest.approx(passes[-1]), profil
        assert all(p == pytest.approx(passes[0]) for p in passes), profil


def test_le_profil_salarial_suit_la_generation():
    """Chaque génération a vécu sa propre pente, et le modèle la lit.

    La prime à l'âge n'a pas été la même à toutes les époques : l'INSEE la
    mesure à 1,19 entre les 51-60 ans et les 26-30 ans en 1962, 1,47 en 2000,
    1,35 en 2024. Celui qui est né en 1940 est entré dans la vie active au
    salaire moyen de son temps, celui qui est né en 1960 à 86 % du sien.

    Le modèle appliquait auparavant la MÊME droite à toutes les générations.
    Il lit maintenant la série longue, et retrouve les pentes observées à
    quelques centièmes près : ×1,23 contre ×1,25 pour la génération 1940,
    ×1,37 contre ×1,38 pour celle de 1960.
    """
    def pente(generation, profil="ascendant"):
        jeune = profil_salaire(RACINE_DONNEES, profil, 26, generation + 26)
        agee = profil_salaire(RACINE_DONNEES, profil, 55, generation + 55)
        return agee / jeune

    assert pente(1940) < pente(1950) < pente(1960)
    assert pente(1940) == pytest.approx(1.25, abs=0.05)
    assert pente(1960) == pytest.approx(1.38, abs=0.05)
    # Le profil plat ne doit RIEN à la génération : c'est la convention qui ne
    # suppose rien, et elle doit le rester.
    assert pente(1940, "plat") == pytest.approx(1.0)
    assert pente(1975, "plat") == pytest.approx(1.0)


def test_le_profil_salarial_ne_doit_rien_a_une_droite_inventee():
    """Les pentes servies sont celles de l'INSEE, catégorie par catégorie.

    Le modèle appliquait ×1,69 de 26 à 55 ans en profil ascendant et ×2,42 en
    fortement ascendant, sans source. L'INSEE observe ×1,30 pour un employé et
    ×1,86 pour un cadre en 2024 — un tiers de moins dans les deux cas. Ce test
    tient l'année de référence, la seule où la modulation vaut un et où la
    forme lue doit donc se retrouver telle quelle.
    """
    def pente(profil):
        jeune = profil_salaire(RACINE_DONNEES, profil, 26, ANNEE_FORME_CATEGORIE)
        agee = profil_salaire(RACINE_DONNEES, profil, 54.5, ANNEE_FORME_CATEGORIE)
        return agee / jeune

    assert pente("ascendant") == pytest.approx(1.30, abs=0.02)
    assert pente("fortement_ascendant") == pytest.approx(1.86, abs=0.03)


def test_le_facteur_de_secteur_ne_touche_que_les_regimes_speciaux():
    """L'hypothèse la plus forte du profil salarial, tenue à sa place.

    Aucune source française ne ventile le salaire par âge pour les régimes
    spéciaux. L'enquête européenne le fait par SECTION d'activité, et deux
    sections tombent sur un périmètre de régime : l'électricité-gaz est le champ
    du statut des IEG, les transports celui où sont la SNCF et la RATP. Mais
    elle est agrégée, donc le modèle n'en prend qu'un rapport de pentes — ce qui
    suppose ce rapport identique en intra-catégorie et en agrégé.

    Ce test garde les deux bornes de cette hypothèse : elle ne touche QUE les
    affiliations nommées, et elle n'est pas retenue là où elle ne tient pas
    d'une vague à l'autre — les mines et les spectacles.
    """
    assert _facteur_secteur(RACINE_DONNEES, "agent_ieg") == pytest.approx(1.38, abs=0.03)
    assert _facteur_secteur(RACINE_DONNEES, "agent_sncf") == pytest.approx(0.93, abs=0.02)

    # Tout le reste est à un : le facteur ne déborde pas sur le privé, ni sur le
    # public, ni sur les régimes dont le secteur n'est que du bruit.
    for affiliation in ("salarie_prive_non_cadre", "salarie_prive_cadre",
                        "fonctionnaire_etat", "contractuel_public", "artisan",
                        "mineur", "personnel_opera", "personnel_comedie_francaise"):
        assert _facteur_secteur(RACINE_DONNEES, affiliation) == 1.0, affiliation


# -- âge de référence --------------------------------------------------------


def test_cliquet_ne_redescend_jamais(mortalite):
    """Le mode est nommé : le défaut, lui, abaisse la référence à la bascule."""
    reference = AgeReference(
        RACINE_DONNEES,
        Parametres(mode_age_reference=ModeAgeReference.CLIQUET_LEGAL),
        mortalite,
    )
    precedent = 0.0
    for annee in range(1945, 2031):
        courant = reference.age(annee)
        assert courant >= precedent, f"l'âge de référence recule en {annee}"
        precedent = courant


def test_le_defaut_tient_le_cliquet_puis_fixe_soixante_quatre(mortalite):
    """Le défaut coupe en deux à la bascule, qu'il inclut.

    Avant elle, le cliquet, parce que 64 ans n'existait dans aucun droit et
    qu'une liquidation de 1990 se mesure à son époque. À partir d'elle, l'âge
    légal d'ouverture des droits. La bascule elle-même est du second côté : les
    droits acquis y sont convertis, et c'est le seul calcul où l'âge de
    référence pèse sur une pension.
    """
    parametres = Parametres()
    assert parametres.mode_age_reference is ModeAgeReference.FIXE_APRES_BASCULE
    reference = AgeReference(RACINE_DONNEES, parametres, mortalite)

    assert reference.age(1990) == 65.0
    assert reference.age(parametres.annee_bascule - 1) == 67.0
    assert reference.age(parametres.annee_bascule) == 64.0
    assert reference.age(2070) == 64.0


def test_abaissement_de_1982_ne_baisse_pas_la_reference(mortalite):
    """Cœur du cahier des charges : partir à 60 ans en 1990 = 5 ans d'anticipation."""
    reference = AgeReference(RACINE_DONNEES, Parametres(), mortalite)
    assert reference.age(1990) == 65.0
    ecart = reference.ecart(60.0, 1990)
    assert ecart.ecart == pytest.approx(5.0)
    assert ecart.anticipe


def test_sans_cliquet_la_reference_suit_le_droit_positif(mortalite):
    reference = AgeReference(
        RACINE_DONNEES,
        Parametres(mode_age_reference=ModeAgeReference.LEGAL_SANS_CLIQUET),
        mortalite,
    )
    assert reference.age(1990) == 60.0
    assert reference.ecart(60.0, 1990).ecart == pytest.approx(0.0)


def test_depart_de_regime_special_a_50_ans(mortalite):
    """Un agent de conduite parti à 50 ans en 1990 anticipe de 15 ans."""
    reference = AgeReference(RACINE_DONNEES, Parametres(), mortalite)
    assert reference.ecart(50.0, 1990).ecart == pytest.approx(15.0)


def test_report_est_compte_negativement(mortalite):
    reference = AgeReference(RACINE_DONNEES, Parametres(), mortalite)
    ecart = reference.ecart(69.0, 2026)
    assert ecart.ecart < 0
    assert not ecart.anticipe


# -- conversion --------------------------------------------------------------


def test_diviseur_decroit_avec_l_age_de_liquidation(mortalite):
    convertisseur = Convertisseur(mortalite, Parametres())
    precedent = None
    for age in (55, 60, 62, 64, 67, 70):
        diviseur = convertisseur.coefficient(age, 2026).diviseur
        if precedent is not None:
            assert diviseur < precedent, f"le diviseur ne baisse pas à {age} ans"
        precedent = diviseur


def test_anticipation_reduit_la_pension_sans_decote_administrative(mortalite):
    """La sanction du départ anticipé est produite par le seul diviseur."""
    convertisseur = Convertisseur(mortalite, Parametres())
    rapport = convertisseur.effet_anticipation(59.0, 64.0, 2026)
    assert rapport < 1.0
    # Cinq ans d'anticipation coûtent de l'ordre de 15 % de pension annuelle,
    # avant même de compter les cotisations non versées.
    assert 0.75 < rapport < 0.92


def test_diviseur_nul_de_taux_anticipe_vaut_esperance_de_vie(mortalite):
    convertisseur = Convertisseur(mortalite, Parametres(taux_anticipe_conversion=0.0))
    coefficient = convertisseur.coefficient(64, 2026)
    assert coefficient.diviseur == pytest.approx(coefficient.esperance_residuelle, rel=1e-6)


def test_taux_anticipe_positif_reduit_le_diviseur(mortalite):
    sans = Convertisseur(mortalite, Parametres()).coefficient(64, 2026)
    avec = Convertisseur(
        mortalite, Parametres(taux_anticipe_conversion=0.015)
    ).coefficient(64, 2026)
    assert avec.diviseur < sans.diviseur


def test_table_par_sexe_penalise_les_femmes(mortalite):
    """Justification du choix unisexe par défaut : l'écart est loin d'être marginal."""
    convertisseur = Convertisseur(
        mortalite, Parametres(table_conversion=TableConversion.PAR_SEXE)
    )
    homme = convertisseur.coefficient(64, 2026, "H").diviseur
    femme = convertisseur.coefficient(64, 2026, "F").diviseur
    assert femme > homme
    assert (femme / homme - 1) > 0.05


def test_table_par_sexe_exige_le_sexe(mortalite):
    convertisseur = Convertisseur(
        mortalite, Parametres(table_conversion=TableConversion.PAR_SEXE)
    )
    with pytest.raises(ValueError, match="sexe non renseigné"):
        convertisseur.coefficient(64, 2026, None)


def test_la_table_d_une_population_allonge_le_diviseur(mortalite):
    """Ce que le diviseur commun transfère (action 14) : à 64 ans, un
    fonctionnaire civil de l'État a entre un et deux ans de rente de plus que
    la population générale, et une table qui le saurait lui servirait 4 à 8 %
    de moins par an à capital égal. La table commune reste le défaut."""
    commun = Convertisseur(mortalite, Parametres()).coefficient(64, 2026)
    corrige = Convertisseur(
        mortalite, Parametres(population_conversion="fonctionnaires_civils_etat")
    ).coefficient(64, 2026)
    ecart = corrige.esperance_residuelle - commun.esperance_residuelle
    assert 1.0 < ecart < 2.0
    assert 0.04 < corrige.diviseur / commun.diviseur - 1 < 0.08
    assert commun.table == "unisexe_generation"
    assert corrige.table == "unisexe_generation_fonctionnaires_civils_etat"


def test_la_population_ne_change_rien_au_scenario_1_et_baisse_les_notionnels():
    """Le garde-fou de l'action 14 : le défaut n'appartient pas au notionnel.
    Le scénario 1 sert la même pension quelle que soit la longévité — aucun
    diviseur ne l'a calculée —, et c'est pourquoi le transfert y est du même
    ordre. Les scénarios notionnels, eux, voient leur pension baisser sous la
    table de la population, de l'ordre de l'écart de diviseur."""
    from retraite_notionnelle.castypes import CAS_TYPES
    from retraite_notionnelle.simulateur import Simulateur

    cas = next(c for c in CAS_TYPES if c.code == "fonctionnaire_sedentaire")
    commun = Simulateur(Parametres(population_conversion=None))
    corrige = Simulateur(Parametres(population_conversion="fonctionnaires_civils_etat"))
    carriere = cas.construire(commun, 1975)
    avec, sans = commun.simuler(carriere), corrige.simuler(carriere)
    assert sans.actuel.pension_annuelle == avec.actuel.pension_annuelle
    rapport = (sans.notionnel_retroactif.pension_annuelle
               / avec.notionnel_retroactif.pension_annuelle)
    assert 0.92 < rapport < 0.97


def test_le_rattachement_par_la_pension_est_un_point_fixe():
    """Par la pension, le vingtile dépend de la pension qui dépend du diviseur.
    `Convertisseur.resoudre` itère jusqu'à ce que le vingtile de la pension
    servie soit celui qui l'a servie — ou, s'il oscille entre deux voisins,
    s'arrête au sixième tour, ce qui rend le résultat déterministe. Ce test
    tient le point fixe là où il existe, et vérifie que le rang parmi les
    retraités n'est pas le rang par le salaire : le SMIC à carrière
    complète, quatrième vingtile par le salaire, est au cinquième par sa
    pension. Le rang se lit parmi les retraités qui résident en France,
    ceux que décrivent les vingtiles de niveau de vie de l'INSEE : 57 %
    d'entre eux touchent moins de 1 500 € par mois, contre 59 % en comptant
    ceux qui vivent à l'étranger, dont la pension française est petite —
    c'est ce qui le faisait classer au sixième jusqu'au 23 septembre 2026."""
    from retraite_notionnelle.castypes import CAS_TYPES
    from retraite_notionnelle.simulateur import Simulateur

    par_salaire = Simulateur(Parametres())
    par_pension = Simulateur(Parametres(rattachement_niveau_de_vie="pension"))
    assert par_pension.convertisseur.rattache_par_pension
    assert not par_salaire.convertisseur.rattache_par_pension
    cas = next(c for c in CAS_TYPES if c.code == "smic_carriere_complete")
    carriere = cas.construire(par_salaire, 1975)
    resultat = par_pension.simuler(carriere).notionnel_retroactif_employeur
    retenue = resultat.conversion.table.split("_generation_")[1]
    attendue = par_pension.convertisseur.population_par_pension(
        resultat.pension_annuelle, carriere.annee_liquidation)
    # Le point fixe peut osciller entre deux vingtiles voisins — la pension
    # du sixième retombe au cinquième, qui la renvoie au sixième — ; le
    # dernier tour est alors retenu. Ici il est atteint : le vingtile de la
    # pension servie est celui qui l'a servie.
    assert retenue == "niveau_de_vie_v05"
    assert attendue == retenue
    assert par_pension.distribution.part_sous(1500.0) == pytest.approx(0.573, abs=0.005)
    salaire = par_salaire.simuler(carriere).notionnel_retroactif_employeur
    assert salaire.conversion.table.endswith("niveau_de_vie_v04")
    assert resultat.pension_annuelle < salaire.pension_annuelle


def test_le_diviseur_commun_transfere_des_modestes_vers_les_aises(mortalite):
    """L'axe du revenu : à 64 ans en 2026, la table des 5 % les plus modestes
    donne trois ans de rente de MOINS que la table commune, celle des 5 % les
    plus aisés trois ans de PLUS. Un diviseur commun sert donc au premier une
    pension calculée pour une vie qu'il n'aura pas, et au second l'inverse —
    ce que mesure `scripts/mortalite_population.py --niveau-de-vie`."""
    commun = Convertisseur(mortalite, Parametres()).coefficient(64, 2026)
    modeste = Convertisseur(
        mortalite, Parametres(population_conversion="niveau_de_vie_v01")
    ).coefficient(64, 2026)
    aise = Convertisseur(
        mortalite, Parametres(population_conversion="niveau_de_vie_v20")
    ).coefficient(64, 2026)
    assert -4.5 < modeste.esperance_residuelle - commun.esperance_residuelle < -2.0
    assert 2.0 < aise.esperance_residuelle - commun.esperance_residuelle < 4.5
    assert modeste.diviseur < commun.diviseur < aise.diviseur


# -- fusion ------------------------------------------------------------------


def test_fusion_retient_les_ages_les_plus_eleves(catalogue):
    fusionne = fusionner(catalogue, 2026)
    for regime in catalogue:
        if regime.hors_repartition or not regime.vivant(2026):
            continue
        for periode in regime.periodes_actives(2026):
            assert periode.age_ouverture <= fusionne.age_ouverture
            assert periode.age_taux_plein <= fusionne.age_taux_plein


def test_fusion_supprime_tous_les_avantages_non_contributifs(catalogue):
    assert fusionner(catalogue, 2026).avantages_non_contributifs == ()


def test_fusion_retient_le_salaire_de_reference_le_moins_avantageux(catalogue):
    assert fusionner(catalogue, 2026).salaire_reference == "carriere_entiere"


def test_fusion_deplafonne_l_assiette(catalogue):
    assert fusionner(catalogue, 2026).assiette == "deplafonnee"


def test_fusion_somme_les_taux_du_statut_pivot(catalogue):
    """Et la cotisation DÉPLAFONNÉE en fait partie.

    L'assiette du régime unifié est déplafonnée : ce que le régime général
    prélève sur la totalité du salaire — 2,41 % en moyenne sur la période de
    la fiche, 2,51 % en 2026 — y porte donc sur la même base
    que la part plafonnée, et s'y ajoute. L'omettre faisait perdre au compte
    notionnel, après la bascule, exactement ce que la séparation des deux taux
    venait d'y porter avant elle.
    """
    fusionne = fusionner(catalogue, 2026)
    base = catalogue["regime_general"].periode(2026)
    complementaire = min(catalogue["agirc_arrco"].periodes_actives(2026),
                         key=lambda p: p.bornes_assiette_en_pass()[0])
    attendu = (
        base.taux_cotisation_retraite + base.taux_cotisation_deplafonnee
        + complementaire.taux_cotisation_retraite
        + complementaire.taux_cotisation_deplafonnee
    )
    assert fusionne.taux_cotisation_retraite == pytest.approx(attendu)
    assert base.taux_cotisation_deplafonnee > 0, (
        "sans déplafonnée au régime général, ce test ne prouve plus rien"
    )


def test_fusion_exclut_la_capitalisation(catalogue):
    assert "rafp" not in fusionner(catalogue, 2026).regimes_fusionnes


def test_fusion_variante_taux_le_plus_eleve(catalogue):
    fusionne = fusionner(
        catalogue, 2026, RegleFusion(critere_taux=CritereTaux.LE_PLUS_ELEVE)
    )
    maxima = max(
        periode.taux_cotisation_retraite + periode.taux_cotisation_deplafonnee
        for regime in catalogue if regime.vivant(2026) and not regime.hors_repartition
        for periode in regime.periodes_actives(2026)
    )
    assert fusionne.taux_cotisation_retraite == pytest.approx(maxima)


# -- le mois -----------------------------------------------------------------


def test_la_liquidation_est_datee_au_mois_et_non_arrondie_a_l_annee():
    """« Soixante-quatre ans et six mois » n'est pas « soixante-cinq ans ».

    Le modèle arrondissait ``naissance + âge`` à l'année civile la plus proche,
    et Python arrondit les demis AU PAIR : deux assurés déclarant le même âge
    étaient traités différemment selon la parité de leur millésime. La date se
    lit désormais en mois depuis la date de naissance.
    """
    from retraite_notionnelle.carriere import Carriere

    def date(naissance, mois, age):
        carriere = Carriere(annee_naissance=naissance, sexe="H",
                            mois_naissance=mois, age_liquidation=age,
                            lignes=[])
        return (carriere.date_liquidation.annee, carriere.date_liquidation.mois)

    # Né en mars 1962, parti à 64 ans et 6 mois : septembre 2026, et rien d'autre.
    assert date(1962, 3, 64.5) == (2026, 9)
    assert date(1962, 1, 64.5) == (2026, 7)
    # La parité du millésime ne décide plus de rien : deux générations
    # consécutives, même âge, même mois de départ dans l'année.
    assert date(1961, 1, 64.5)[1] == date(1962, 1, 64.5)[1] == 7
    # Un âge entier et une naissance en janvier tombent au 1er janvier, comme
    # avant : c'est la convention qui laisse les cas types inchangés.
    assert date(1975, 1, 64) == (2039, 1)


def test_l_annee_de_liquidation_est_portee_au_compte_au_prorata(macro):
    """Partir en décembre, ce n'est pas travailler onze mois pour rien.

    L'accumulation s'arrêtait à l'année PRÉCÉDANT la liquidation : les mois
    cotisés de l'année du départ n'allaient nulle part. Ils y vont, à
    proportion, et le compte croît donc de mois en mois.
    """
    from retraite_notionnelle.carriere import Carriere

    capitaux = []
    for mois in range(12):
        carriere = Carriere.depuis_profil(
            1962, "H", "salarie_prive_non_cadre", 22, 64 + mois / 12, macro,
        )
        ligne = carriere.ligne(carriere.annee_liquidation)
        if mois == 0:
            # Départ au 1er janvier : aucun mois de l'année n'est travaillé.
            assert ligne is None or carriere.part_retenue(2026) == 0
        else:
            assert ligne.fraction_annee == pytest.approx(mois / 12)
            assert ligne.revenu > 0
        capitaux.append(sum(l.revenu for l in carriere.lignes))
    assert capitaux == sorted(capitaux)
    assert capitaux[-1] > capitaux[0]


def test_les_trimestres_de_l_annee_du_depart_sont_bornes_aux_trimestres_civils(macro):
    """On ne valide pas quatre trimestres en sept mois.

    Le montant cotisé commande le nombre de trimestres, les mois en commandent
    le plafond : c'est la règle de l'article R. 351-9 pour l'année du point de
    départ, et elle vaut aussi pour l'année d'entrée dans la vie active.
    """
    from retraite_notionnelle.carriere import Carriere

    attendus = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]
    for mois, attendu in enumerate(attendus):
        carriere = Carriere.depuis_profil(
            1962, "H", "salarie_prive_non_cadre", 22, 64 + mois / 12, macro,
            niveau_salaire=3.0,
        )
        ligne = carriere.ligne(carriere.annee_liquidation)
        obtenu = 0 if ligne is None else carriere.trimestres_retenus(ligne)
        assert obtenu == attendu, mois


def test_un_releve_declarant_douze_mois_est_tronque_au_point_de_depart(macro):
    """Une ligne de carrière dit l'année ; la liquidation dit jusqu'où.

    Un relevé de carrière déclare des années pleines. Qui liquide au 1er juillet
    n'a pourtant travaillé que six mois de son année de départ, et c'est la plus
    courte des deux durées qui compte — sans quoi l'année du départ vaudrait
    douze mois de cotisations à qui n'en a fait aucun.
    """
    from retraite_notionnelle.carriere import AnneeCarriere, Carriere

    lignes = [AnneeCarriere(annee=a, revenu=40_000.0,
                            affiliation="salarie_prive_non_cadre")
              for a in range(1985, 2027)]
    carriere = Carriere(annee_naissance=1962, sexe="H", lignes=lignes,
                        age_liquidation=64.5)
    assert carriere.annee_liquidation == 2026
    assert carriere.part_retenue(2026) == pytest.approx(0.5)
    assert carriere.trimestres_retenus(carriere.ligne(2026)) == 2
    # Une année postérieure au départ ne compte pas, pleine ou non.
    assert carriere.part_retenue(2027) == 0.0

    # Départ au 1er janvier : l'année du départ ne compte pour rien.
    janvier = Carriere(annee_naissance=1962, sexe="H", lignes=list(lignes),
                       age_liquidation=64.0)
    assert janvier.part_retenue(2026) == 0.0


def test_le_diviseur_ne_fait_plus_de_marche_a_l_anniversaire(mortalite):
    """Le mois de départ déplace le diviseur, et régulièrement.

    ``survie_annuelle`` lisait ``quotients[int(age)]`` : la part OBSERVÉE de la
    table était aveugle aux mois, et le diviseur d'un départ à 60 ans et onze
    mois était celui d'un départ à 60 ans tout rond — puis tombait d'un coup à
    l'anniversaire. La force de mortalité étant supposée constante entre deux
    âges entiers, la décroissance est désormais lisse.
    """
    parametres = Parametres(racine_donnees=RACINE_DONNEES)
    convertisseur = Convertisseur(mortalite, parametres)
    # 2005 : les quotients observés couvrent la première moitié de la courbe,
    # et c'est là que la marche se produisait.
    diviseurs = [convertisseur.coefficient(60 + m / 12, 2005, "H").diviseur
                 for m in range(13)]
    ecarts = [avant - apres for avant, apres in zip(diviseurs, diviseurs[1:])]

    assert diviseurs == sorted(diviseurs, reverse=True)
    # Aucun pas ne pèse plus du double du plus petit : la marche d'un an valait
    # près de la moitié de la baisse annuelle à elle seule.
    assert max(ecarts) < 2 * min(ecarts)
    # Et le douzième mois retombe exactement sur l'âge entier suivant.
    assert diviseurs[12] == pytest.approx(
        convertisseur.coefficient(61.0, 2005, "H").diviseur
    )


def test_le_diviseur_decroit_aussi_au_passage_du_1er_janvier(mortalite):
    """Le millésime de la table ne doit pas sauter quand l'âge, lui, glisse.

    L'âge avançait mois par mois et l'année civile d'un bloc au 1er janvier :
    le diviseur REMONTAIT à cette date, et partir un mois plus tard rallongeait
    la durée de service attendue. Le trajet d'une année de rente est désormais
    découpé à ses deux franchissements — l'anniversaire, puis le 1er janvier —,
    chaque tronçon recevant la force de mortalité de la cellule qu'il traverse.
    """
    parametres = Parametres(racine_donnees=RACINE_DONNEES)
    convertisseur = Convertisseur(mortalite, parametres)

    # Vingt-quatre mois consécutifs, à cheval sur deux 1er janvier.
    diviseurs = []
    for k in range(25):
        annee, mois = 2037 + k // 12, k % 12 + 1
        diviseurs.append(
            convertisseur.coefficient(62 + k / 12, annee, "H", mois).diviseur
        )
    ecarts = [avant - apres for avant, apres in zip(diviseurs, diviseurs[1:])]

    assert all(ecart > 0 for ecart in ecarts), diviseurs
    # Le pas de janvier ne se distingue pas des autres : c'était le symptôme.
    assert max(ecarts) < 2 * min(ecarts), ecarts

    # Et douze mois de mois valent exactement un an d'âge, au même mois.
    assert diviseurs[12] == pytest.approx(
        convertisseur.coefficient(63.0, 2038, "H", 1).diviseur
    )


def test_le_taux_de_remplacement_rapporte_un_revenu_annualise(macro):
    """L'année du départ ne porte que ses mois ; le taux compare des années.

    Le dernier revenu servait de dénominateur tel quel. L'année du départ étant
    devenue incomplète, six mois de salaire y répondaient d'une pension
    annuelle : le taux de remplacement doublait pour qui liquidait en juillet.
    """
    from retraite_notionnelle.simulateur import Simulateur
    from retraite_notionnelle.carriere import Carriere

    simulateur = Simulateur(Parametres(racine_donnees=RACINE_DONNEES))
    taux = []
    for mois in range(12):
        carriere = Carriere.depuis_profil(
            1962, "H", "salarie_prive_non_cadre", 22, 64 + mois / 12,
            simulateur.macro, profil_carriere="plat",
        )
        taux.append(simulateur.simuler(carriere).taux_remplacement_actuel)

    # Aucun mois ne fait bondir le taux : il suit la pension, pas la troncature
    # de la dernière année.
    for avant, apres in zip(taux, taux[1:]):
        assert abs(apres / avant - 1) < 0.03, taux
    assert all(0.2 < t < 1.2 for t in taux), taux


def test_le_mois_de_liquidation_designe_la_circulaire_de_revalorisation(macro):
    """Deux circulaires portent l'année 2022, et elles diffèrent de 3,9 %.

    La revalorisation exceptionnelle du 1er juillet 2022 n'était opposée à
    personne : le modèle ne retenait que les colonnes prenant effet au
    1er janvier, si bien qu'une liquidation de septembre 2022 lisait celle de
    janvier et sous-revalorisait tout son salaire annuel moyen.
    """
    lu = macro.coefficient_revalorisation_portee_au_compte
    janvier = lu(2015, 2022, 1)
    juillet = lu(2015, 2022, 7)
    assert juillet > janvier
    assert juillet / janvier == pytest.approx(1.039, abs=0.002)
    # La colonne ne s'applique qu'à compter de sa date d'effet.
    assert lu(2015, 2022, 6) == pytest.approx(janvier)
    assert lu(2015, 2022, 12) == pytest.approx(juillet)
